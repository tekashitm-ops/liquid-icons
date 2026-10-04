"""Steam: reconstrucción vectorial del logo del icono oficial de iOS y montaje de los .icon.

Geometría ajustada contra el icono de la App Store (1024 px) con IoU 0.989.
Piezas del logo (de atrás a delante): manivela, biela, eje. Cada pieza va en su propio
grupo de Liquid Glass, como los pétalos de Fotos en iOS 27: cristal tintado translúcido
que se solapa, refracta lo que tiene detrás y proyecta sombra cromática.
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

# Colores de marca de Steam
STEAM_BG_TOP, STEAM_BG_BOTTOM = "#158ABD", "#091B3F"   # degradado del icono oficial de iOS
STEAM_CYAN, STEAM_BLUE = "#06BFFF", "#2D73FF"          # degradado de los botones de Steam
STEAM_LIGHT = "#66C0F4"                                # azul claro clásico de Steam


def circle(c, r):
    return Point(c).buffer(r, quad_segs=RES)


def svg(geom) -> str:
    d = []
    for poly in getattr(geom, "geoms", [geom]):
        for ring in [poly.exterior, *poly.interiors]:
            d.append("M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in ring.coords) + "Z")
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024">'
        f'<path fill="#FFFFFF" fill-rule="evenodd" d="{"".join(d)}"/></svg>\n'
    )


def pieces():
    arm = unary_union([circle(C1, HULL_R1), circle(C2, HULL_R2)]).convex_hull
    manivela = unary_union([circle(C1, R1), circle(C2, R2), arm])
    manivela = manivela.difference(circle(C1, R1_OUT)).difference(circle(C2, R2_OUT))
    far = (C2[0] - math.cos(ROD_ANGLE) * 900, C2[1] - math.sin(ROD_ANGLE) * 900)
    biela = LineString([far, C2]).buffer(R2_IN, quad_segs=RES).intersection(CANVAS)
    eje = circle(C1, R1_IN)
    return {"manivela": manivela, "biela": biela, "eje": eje}


def color(hexcolor: str, alpha: float = 1.0) -> str:
    r, g, b = (int(hexcolor[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return f"extended-srgb:{r:.5f},{g:.5f},{b:.5f},{alpha:.5f}"


def group(name, fill, translucency, refraction=None, shadow="layer-color", specular="automatic",
          alpha=1.0, blur=0.5, shadow_opacity=0.5):
    g = {
        "name": name,
        "lighting": "individual",
        "specular": True,
        "specular-highlight-placement": specular,
        "blur-material": blur,
        "shadow": {"kind": shadow, "opacity": shadow_opacity},
        "translucency": {"enabled": translucency > 0, "value": translucency},
        "layers": [{"name": name, "image-name": f"{name}.svg", "glass": True, "fill": {"solid": color(fill, alpha)}}],
    }
    if refraction:
        g["refractivity"] = {"enabled": True, "strength": refraction[0], "depth": refraction[1]}
    return g


# Cada concepto: fondo + grupos de delante hacia atrás (así los ordena Icon Composer)
CONCEPTS = {
    # Como Fotos: fondo System Light de Apple y tres piezas de cristal tintado en los
    # azules de Steam que se mezclan donde se solapan.
    "steam-fotos": {
        "fill": "system-light",
        "groups": [
            group("eje", STEAM_CYAN, 0.35, refraction=(0.6, 0.6)),
            group("biela", STEAM_CYAN, 0.45, refraction=(0.6, 0.6)),
            group("manivela", STEAM_BLUE, 0.35),
        ],
    },
    # Fiel al Steam de siempre: su degradado azul y el logo en cristal claro; la biela,
    # tintada del azul clásico, refracta la manivela que pasa por debajo.
    "steam-cristal": {
        "fill": {"linear-gradient": [color(STEAM_BG_TOP), color(STEAM_BG_BOTTOM)]},
        "groups": [
            group("eje", "#FFFFFF", 0.0, shadow="neutral", specular="inside"),
            group("biela", STEAM_LIGHT, 0.45, refraction=(0.6, 0.6)),
            group("manivela", "#FFFFFF", 0.4, shadow="neutral"),
        ],
    },
    # Como la lente de Vista Previa: la biela es cristal transparente y grueso que dobla
    # el borde de la manivela al pasar por encima; manivela y eje casi opacos y nítidos.
    "steam-lente": {
        "fill": {"linear-gradient": [color(STEAM_BG_TOP), color(STEAM_BG_BOTTOM)]},
        "groups": [
            group("eje", "#FFFFFF", 0.0, shadow="neutral", specular="inside"),
            group("biela", "#FFFFFF", 0.8, refraction=(0.9, 0.8), shadow="neutral",
                  alpha=0.25, blur=0.15, shadow_opacity=0.35),
            group("manivela", "#FFFFFF", 0.2, shadow="neutral"),
        ],
    },
}


def main():
    geo = pieces()
    for name, spec in CONCEPTS.items():
        icon = ROOT / "icons" / f"{name}.icon"
        (icon / "Assets").mkdir(parents=True, exist_ok=True)
        for piece, g in geo.items():
            (icon / "Assets" / f"{piece}.svg").write_text(svg(g), encoding="utf-8")
        doc = {
            "features": ["refractivity", "specular-location"],
            "fill": spec["fill"],
            "groups": spec["groups"],
            "supported-platforms": {"squares": "shared"},
        }
        (icon / "icon.json").write_text(json.dumps(doc, indent=2), encoding="utf-8")
        print("ok", icon.relative_to(ROOT))


if __name__ == "__main__":
    main()
