"""Exporta los iconos aprobados (catalog.json + renders de Icon Composer) a Stream Deck.

Escribe:
  - la biblioteca del plugin Liquid Deck: library/<id>-<variante>.png + library/library.js
  - el paquete de iconos "Liquid Glass" para la biblioteca de iconos de Stream Deck

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


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as f:
        head = f.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path.name} no es un PNG")
    return struct.unpack(">II", head[16:24])


def main() -> None:
    renders = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "renders"
    catalog = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
    default_variant = catalog["defaultVariant"]

    lib_dir = PLUGIN / "library"
    if lib_dir.exists():
        shutil.rmtree(lib_dir)
    lib_dir.mkdir(parents=True)

    pack_icons = PACK / "icons"
    if PACK.exists():
        shutil.rmtree(PACK)
    pack_icons.mkdir(parents=True)

    library, pack_index = [], []
    for icon in catalog["icons"]:
        files = {}
        for variant, icon_name in icon["variants"].items():
            src = renders / f"{icon_name}-Default-key.png"
            if not src.exists():
                sys.exit(f"Falta el render {src.name}: ejecuta antes el render en el Mac")
            if png_size(src) != (KEY_PX, KEY_PX):
                sys.exit(f"{src.name} mide {png_size(src)}, se esperaban {KEY_PX}x{KEY_PX}")
            file = f"{icon['id']}-{variant}.png"
            shutil.copyfile(src, lib_dir / file)
            shutil.copyfile(src, pack_icons / file)
            files[variant] = file
            pack_index.append({
                "path": file,
                "name": f"{icon['name']} ({variant})",
                "tags": [icon["name"].lower(), variant, "liquid glass"],
            })
        if default_variant not in files:
            sys.exit(f"{icon['id']} no tiene la variante por defecto '{default_variant}'")
        library.append({"id": icon["id"], "name": icon["name"], "match": icon["match"], "variants": files})

    data = {"defaultVariant": default_variant, "icons": library}
    (lib_dir / "library.js").write_text(
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
    shutil.copyfile(lib_dir / f"{first['id']}-{default_variant}.png", PACK / "icon.png")
    (PACK / "icons.json").write_text(json.dumps(pack_index, ensure_ascii=False, indent=4), encoding="utf-8")
    (PACK / "manifest.json").write_text(json.dumps({
        "Name": "Liquid Glass",
        "Version": "1.0.0",
        "Description": "Iconos aprobados, renderizados con Icon Composer de Apple (iOS 27).",
        "Author": "ricca",
        "URL": "https://github.com/tekashitm-ops/liquid-icons",
        "Icon": "icon.png",
        "License": "Uso personal",
    }, ensure_ascii=False, indent=4), encoding="utf-8")

    print(f"biblioteca del plugin: {len(library)} iconos -> {lib_dir}")
    print(f"paquete de iconos: {len(pack_index)} imágenes -> {PACK}")


if __name__ == "__main__":
    main()
