"""Piezas comunes para montar los .icon de Icon Composer 2 (Liquid Glass) de cada app."""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WHITE = "#FFFFFF"


def svg(geom) -> str:
    """Una pieza del logo como SVG de 1024x1024 en blanco (Icon Composer le pone el color)."""
    d = []
    for poly in getattr(geom, "geoms", [geom]):
        for ring in [poly.exterior, *poly.interiors]:
            d.append("M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in ring.coords) + "Z")
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024">'
        f'<path fill="#FFFFFF" fill-rule="evenodd" d="{"".join(d)}"/></svg>\n'
    )


def color(hexcolor: str, alpha: float = 1.0) -> str:
    r, g, b = (int(hexcolor[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return f"extended-srgb:{r:.5f},{g:.5f},{b:.5f},{alpha:.5f}"


def gradient(colors):
    return {"linear-gradient": [color(c) for c in colors]}


def auto_gradient(hexcolor: str):
    """Degradado automático de Icon Composer a partir de un solo color."""
    return {"automatic-gradient": color(hexcolor)}


def glass(name, fill=WHITE, alpha=1.0, translucency=0.2, blur=0.5, refraction=None,
          shadow="neutral", shadow_opacity=0.5, specular="automatic", image=None):
    """Un grupo de Liquid Glass con una sola pieza del logo (image = otra pieza con la misma forma)."""
    g = {
        "name": name,
        "lighting": "individual",
        "specular": True,
        "specular-highlight-placement": specular,
        "blur-material": blur,
        "shadow": {"kind": shadow, "opacity": shadow_opacity},
        "translucency": {"enabled": translucency > 0, "value": translucency},
        "layers": [{"name": name, "image-name": f"{image or name}.svg", "glass": True,
                    "fill": {"solid": color(fill, alpha)}}],
    }
    if refraction:
        g["refractivity"] = {"enabled": True, "strength": refraction[0], "depth": refraction[1]}
    return g


def write_icon(name: str, fill, groups: list, pieces: dict) -> Path:
    """Escribe icons/<name>.icon con icon.json y las piezas que usan sus grupos."""
    icon = ROOT / "icons" / f"{name}.icon"
    if icon.exists():
        shutil.rmtree(icon)
    (icon / "Assets").mkdir(parents=True)
    used = {layer["image-name"][:-4] for g in groups for layer in g["layers"]}
    for piece in sorted(used):
        (icon / "Assets" / f"{piece}.svg").write_text(svg(pieces[piece]), encoding="utf-8")
    doc = {
        "features": ["refractivity", "specular-location"],
        "fill": fill,
        "groups": groups,
        "supported-platforms": {"squares": "shared"},
    }
    (icon / "icon.json").write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print("ok", icon.relative_to(ROOT))
    return icon


def clean(prefix: str) -> None:
    """Borra de icons/ todos los .icon de una app (antes de escribir los de la ronda actual)."""
    for old in (ROOT / "icons").glob(f"{prefix}*.icon"):
        shutil.rmtree(old)
