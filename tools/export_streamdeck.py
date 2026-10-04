"""Exporta los iconos aprobados (catalog.json + renders de Icon Composer) a Stream Deck.

Escribe:
  - la biblioteca del plugin Liquid Deck: library/<id>-<variante>.png + library/library.js
  - el paquete de iconos "Liquid Glass" para la biblioteca de iconos de Stream Deck

Comprueba todos los renders antes de tocar nada: si falta uno o no está en sRGB de 8 bits,
la biblioteca y el paquete que usa Stream Deck se quedan como estaban.

Uso:  python tools/export_streamdeck.py [carpeta-de-renders]
"""
import json
import shutil
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent           # liquid-icons/
WORKSPACE = ROOT.parent                                 # streamdeck/
PLUGIN = WORKSPACE / "com.ricca.liquiddeck.sdPlugin"
PACK = WORKSPACE / "com.ricca.liquidglass.sdIconPack"

KEY_PX = 144  # 72 pt @2x
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def png_info(path: Path) -> dict:
    """Lee la cabecera y los fragmentos de color de un PNG (sin dependencias)."""
    data = path.read_bytes()
    if data[:8] != PNG_SIGNATURE:
        raise ValueError(f"{path.name} no es un PNG")
    chunks, pos = {}, 8
    while pos + 8 <= len(data):
        length, tag = struct.unpack(">I4s", data[pos:pos + 8])
        chunks.setdefault(tag, data[pos + 8:pos + 8 + length])
        pos += 12 + length
        if tag == b"IEND":
            break
    width, height, depth, color_type = struct.unpack(">IIBB", chunks[b"IHDR"][:10])
    icc = chunks.get(b"iCCP", b"").split(b"\x00")[0].decode("latin-1")
    cicp = chunks.get(b"cICP")
    return {"size": (width, height), "depth": depth, "color_type": color_type,
            "srgb_chunk": b"sRGB" in chunks, "icc": icc, "cicp_primaries": cicp[0] if cicp else None}


def check_key_render(path: Path) -> None:
    """Sale con un mensaje claro si el render no sirve tal cual para una tecla de Stream Deck."""
    if not path.exists():
        sys.exit(f"Falta el render {path.name}: ejecuta antes el render en el Mac")
    info = png_info(path)
    if info["size"] != (KEY_PX, KEY_PX):
        sys.exit(f"{path.name} mide {info['size']}, se esperaban {KEY_PX}x{KEY_PX}")
    if info["depth"] != 8 or info["color_type"] != 6:
        sys.exit(f"{path.name} es de {info['depth']} bits (tipo {info['color_type']}); "
                 "Stream Deck necesita RGBA de 8 bits: falta la conversión a sRGB del render")
    # Stream Deck no gestiona color: un perfil que no sea sRGB (p. ej. Display P3) se vería mal
    srgb = info["srgb_chunk"] or "srgb" in info["icc"].lower()
    if not srgb or info["cicp_primaries"] not in (None, 1):
        sys.exit(f"{path.name} no está en sRGB (perfil '{info['icc'] or 'ninguno'}'): "
                 "falta la conversión a sRGB del render")


def replace_dir(new: Path, target: Path) -> None:
    """Sustituye target por new; si algo falla, deja target como estaba."""
    old = target.with_name(target.name + ".anterior")
    if old.exists():
        shutil.rmtree(old)
    if target.exists():
        target.rename(old)
    try:
        new.rename(target)
    except OSError:
        if old.exists():
            old.rename(target)
        raise
    if old.exists():
        shutil.rmtree(old)


def main() -> None:
    renders = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "renders"
    catalog = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
    default_variant = catalog["defaultVariant"]
    if not catalog["icons"]:
        sys.exit("catalog.json no tiene iconos")

    # 1) Comprobar todo antes de tocar la biblioteca y el paquete que usa Stream Deck
    for icon in catalog["icons"]:
        if default_variant not in icon["variants"]:
            sys.exit(f"{icon['id']} no tiene la variante por defecto '{default_variant}'")
        for icon_name in icon["variants"].values():
            check_key_render(renders / f"{icon_name}-Default-key.png")

    # 2) Montar la biblioteca y el paquete nuevos aparte
    lib_new = PLUGIN / ".library.nuevo"
    pack_new = PACK.with_name("." + PACK.name + ".nuevo")
    for d in (lib_new, pack_new):
        if d.exists():
            shutil.rmtree(d)
    lib_new.mkdir(parents=True)
    (pack_new / "icons").mkdir(parents=True)

    library, pack_index = [], []
    for icon in catalog["icons"]:
        files = {}
        for variant, icon_name in icon["variants"].items():
            src = renders / f"{icon_name}-Default-key.png"
            file = f"{icon['id']}-{variant}.png"
            shutil.copyfile(src, lib_new / file)
            shutil.copyfile(src, pack_new / "icons" / file)
            files[variant] = file
            pack_index.append({
                "path": file,
                "name": f"{icon['name']} ({variant})",
                "tags": [icon["name"].lower(), variant, "liquid glass"],
            })
        library.append({"id": icon["id"], "name": icon["name"], "match": icon["match"], "variants": files})

    data = {"defaultVariant": default_variant, "icons": library}
    (lib_new / "library.js").write_text(
        "/* Generado por liquid-icons/tools/export_streamdeck.py — no editar a mano. */\n"
        "(function (root, data) {\n"
        "  if (typeof module === 'object' && module.exports) module.exports = data;\n"
        "  else root.LiquidLibrary = data;\n"
        "})(typeof self !== 'undefined' ? self : this, "
        + json.dumps(data, ensure_ascii=False, indent=2)
        + ");\n",
        encoding="utf-8",
    )

    first = catalog["icons"][0]
    shutil.copyfile(lib_new / f"{first['id']}-{default_variant}.png", pack_new / "icon.png")
    (pack_new / "icons.json").write_text(json.dumps(pack_index, ensure_ascii=False, indent=4), encoding="utf-8")
    (pack_new / "manifest.json").write_text(json.dumps({
        "Name": "Liquid Glass",
        "Version": "1.0.0",
        "Description": "Iconos aprobados, renderizados con Icon Composer de Apple (iOS 27).",
        "Author": "ricca",
        "URL": "https://github.com/tekashitm-ops/liquid-icons",
        "Icon": "icon.png",
        "License": "Uso personal",
    }, ensure_ascii=False, indent=4), encoding="utf-8")

    # 3) Sustituir las carpetas en uso (los enlaces de Stream Deck apuntan a estas rutas)
    replace_dir(lib_new, PLUGIN / "library")
    replace_dir(pack_new, PACK)

    print(f"biblioteca del plugin: {len(library)} iconos -> {PLUGIN / 'library'}")
    print(f"paquete de iconos: {len(pack_index)} imágenes -> {PACK}")


if __name__ == "__main__":
    main()
