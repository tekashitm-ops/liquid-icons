"""Steam: reconstrucción vectorial del logo del icono oficial de iOS y montaje del .icon.

Geometría ajustada contra el icono de la App Store (1024 px) con IoU 0.989.
Capas (de atrás a delante): manivela, eje, biela — las piezas mecánicas del logo.
"""
import json
import math
from pathlib import Path

from shapely.geometry import LineString, Point, box
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parent.parent

# Medidas en el lienzo de 1024 (ajustadas por mínimos cuadrados contra el original)
C1, R1, R1_IN, R1_OUT = (678.5, 379.5), 193.0, 96.5, 128.5   # círculo grande y su anillo hueco
C2, R2, R2_IN, R2_OUT = (355.5, 702.5), 144.0, 80.0, 109.0   # círculo pequeño y su anillo hueco
HULL_R1, HULL_R2 = 155.5, 77.0                               # brazo: envolvente de dos círculos
ROD_ANGLE = 0.3941                                           # inclinación de la biela (rad)

CANVAS = box(0, 0, 1024, 1024)
RES = 256  # segmentos por cuarto de círculo: curvas suaves a cualquier tamaño


def circle(c, r):
    return Point(c).buffer(r, quad_segs=RES)


def svg_path(geom) -> str:
    polys = getattr(geom, "geoms", [geom])
    d = []
    for poly in polys:
        for ring in [poly.exterior, *poly.interiors]:
            pts = list(ring.coords)
            d.append("M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in pts) + "Z")
    return "".join(d)


def svg(geom) -> str:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024">'
        f'<path fill="#FFFFFF" fill-rule="evenodd" d="{svg_path(geom)}"/></svg>\n'
    )


def build():
    arm = unary_union([circle(C1, HULL_R1), circle(C2, HULL_R2)]).convex_hull
    manivela = unary_union([circle(C1, R1), circle(C2, R2), arm])
    manivela = manivela.difference(circle(C1, R1_OUT)).difference(circle(C2, R2_OUT))
    eje = circle(C1, R1_IN)
    far = (C2[0] - math.cos(ROD_ANGLE) * 900, C2[1] - math.sin(ROD_ANGLE) * 900)
    biela = LineString([far, C2]).buffer(R2_IN, quad_segs=RES).intersection(CANVAS)
    return {"1-manivela.svg": manivela, "2-eje.svg": eje, "3-biela.svg": biela}


def srgb(hexcolor: str) -> str:
    r, g, b = (int(hexcolor[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return f"extended-srgb:{r:.5f},{g:.5f},{b:.5f},1.00000"


def icon_json(translucency: float | None) -> dict:
    group = {
        "name": "logo",
        # Cada pieza recibe su propio canto de cristal (capas de cristal distintas, iOS 27)
        "lighting": "individual",
        "specular": True,
        "shadow": {"kind": "neutral", "opacity": 0.5},
        "translucency": {"enabled": translucency is not None, "value": translucency or 0.0},
        # Icon Composer lista de delante hacia atrás
        "layers": [
            {"name": "3-biela", "image-name": "3-biela.svg", "glass": True},
            {"name": "2-eje", "image-name": "2-eje.svg", "glass": True},
            {"name": "1-manivela", "image-name": "1-manivela.svg", "glass": True},
        ],
    }
    return {
        # Degradado del fondo, muestreado del icono oficial (arriba → abajo)
        "fill": {"linear-gradient": [srgb("#158ABD"), srgb("#091B3F")]},
        "groups": [group],
        "supported-platforms": {"squares": "shared"},
    }


def main():
    layers = build()
    variants = {"steam": 0.5, "steam-solido": None}
    for name, tr in variants.items():
        icon = ROOT / "icons" / f"{name}.icon"
        (icon / "Assets").mkdir(parents=True, exist_ok=True)
        for file, geom in layers.items():
            (icon / "Assets" / file).write_text(svg(geom), encoding="utf-8")
        (icon / "icon.json").write_text(json.dumps(icon_json(tr), indent=2), encoding="utf-8")
        print("ok", icon.relative_to(ROOT))


if __name__ == "__main__":
    main()
