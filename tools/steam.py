"""Steam: reconstrucción vectorial del logo del icono oficial de iOS y montaje de los .icon.

Geometría ajustada contra el icono de la App Store (1024 px) con IoU 0.989.
Piezas del logo (de atrás a delante): manivela, biela, eje. Cada pieza va en su propio
grupo de Liquid Glass para que el cristal de delante refracte (deforme) lo que tiene
detrás, como los pétalos de Fotos o la lente de Vista Previa en iOS 27.
"""
import math

from shapely.geometry import LineString, Point, box
from shapely.ops import unary_union

from liquid import WHITE, clean, glass, gradient, write_icon

# Medidas en el lienzo de 1024 (ajustadas por mínimos cuadrados contra el original)
C1, R1, R1_IN, R1_OUT = (678.5, 379.5), 193.0, 96.5, 128.5   # círculo grande y su anillo hueco
C2, R2, R2_IN, R2_OUT = (355.5, 702.5), 144.0, 80.0, 109.0   # círculo pequeño y su anillo hueco
HULL_R1, HULL_R2 = 155.5, 77.0                               # brazo: envolvente de dos círculos
ROD_ANGLE = 0.3941                                           # inclinación de la biela (rad)

CANVAS = box(0, 0, 1024, 1024)
RES = 256  # segmentos por cuarto de círculo: curvas suaves a cualquier tamaño

# Colores de marca de Steam
STEAM_BG = ["#158ABD", "#091B3F"]         # degradado del icono oficial de iOS
STEAM_CYAN, STEAM_BLUE = "#06BFFF", "#2D73FF"
STEAM_LIGHT = "#66C0F4"


def circle(c, r):
    return Point(c).buffer(r, quad_segs=RES)


def pieces():
    arm = unary_union([circle(C1, HULL_R1), circle(C2, HULL_R2)]).convex_hull
    manivela = unary_union([circle(C1, R1), circle(C2, R2), arm])
    manivela = manivela.difference(circle(C1, R1_OUT)).difference(circle(C2, R2_OUT))
    far = (C2[0] - math.cos(ROD_ANGLE) * 900, C2[1] - math.sin(ROD_ANGLE) * 900)
    biela = LineString([far, C2]).buffer(R2_IN, quad_segs=RES).intersection(CANVAS)
    eje = circle(C1, R1_IN)
    return {"manivela": manivela, "biela": biela, "eje": eje}


# Fondo + grupos de delante hacia atrás (así los ordena Icon Composer).
# Cristal claro (poco esmerilado) para que la deformación de lo que hay detrás se vea nítida.
def eje_blanco():
    """Eje blanco casi opaco con una lente suave en el borde: el centro del logo sigue siendo blanco."""
    return glass("eje", alpha=0.92, translucency=0.2, blur=0.1, refraction=(0.35, 0.3), specular="inside")


APPROVED = {
    # v10 (aprobada): colores de Steam sobre su fondo; biela y eje en cian de cristal.
    "steam-oscuro": "steam-v10",
    # v11 (guardada para el futuro modo claro): estilo Fotos, fondo System Light.
    "steam-claro": "steam-v11",
}

CONCEPTS = {
    # Biela de cristal azul claro, sin esmerilar: deforma nítidamente el círculo pequeño.
    "steam-v7": {"fill": gradient(STEAM_BG), "groups": [
        eje_blanco(),
        glass("biela", fill=STEAM_LIGHT, alpha=0.7, translucency=0.6, blur=0.0,
              refraction=(0.5, 0.4), shadow="layer-color"),
        glass("manivela", translucency=0.25),
    ]},
    # Igual, con refracción más marcada en la biela.
    "steam-v8": {"fill": gradient(STEAM_BG), "groups": [
        eje_blanco(),
        glass("biela", fill=STEAM_LIGHT, alpha=0.7, translucency=0.6, blur=0.0,
              refraction=(0.75, 0.6), shadow="layer-color"),
        glass("manivela", translucency=0.25),
    ]},
    # Biela de cristal transparente (como la lente de Vista Previa).
    "steam-v9": {"fill": gradient(STEAM_BG), "groups": [
        eje_blanco(),
        glass("biela", alpha=0.45, translucency=0.75, blur=0.0, refraction=(0.6, 0.5),
              shadow_opacity=0.35),
        glass("manivela", translucency=0.25),
    ]},
    # Colores de Steam sobre su fondo: biela y eje en cian de cristal.
    "steam-v10": {"fill": gradient(STEAM_BG), "groups": [
        glass("eje", fill=STEAM_CYAN, alpha=0.9, translucency=0.3, blur=0.1,
              refraction=(0.35, 0.3), shadow="layer-color", specular="inside"),
        glass("biela", fill=STEAM_CYAN, alpha=0.75, translucency=0.55, blur=0.0,
              refraction=(0.55, 0.45), shadow="layer-color"),
        glass("manivela", alpha=0.92, translucency=0.3),
    ]},
    # Como Fotos (fondo System Light), con cristal sin esmerilar.
    "steam-v11": {"fill": "system-light", "groups": [
        glass("eje", fill=STEAM_CYAN, alpha=0.9, translucency=0.3, blur=0.1,
              refraction=(0.35, 0.3), shadow="layer-color", specular="inside"),
        glass("biela", fill=STEAM_CYAN, alpha=0.75, translucency=0.55, blur=0.0,
              refraction=(0.55, 0.45), shadow="layer-color"),
        glass("manivela", fill=STEAM_BLUE, alpha=0.9, translucency=0.35, blur=0.2,
              refraction=(0.3, 0.3), shadow="layer-color"),
    ]},
    # Referencias de la ronda anterior.
    "steam-v5": {"fill": "system-light", "groups": [
        glass("eje", fill=STEAM_CYAN, alpha=0.6, translucency=0.5, blur=0.15,
              refraction=(0.7, 0.6), shadow="layer-color"),
        glass("biela", fill=STEAM_CYAN, alpha=0.75, translucency=0.45, blur=0.15,
              refraction=(0.6, 0.5), shadow="layer-color"),
        glass("manivela", fill=STEAM_BLUE, alpha=0.9, translucency=0.3, blur=0.3,
              refraction=(0.4, 0.4), shadow="layer-color"),
    ]},
    # Como v4 pero con la biela en blanco (más cercano al logo original).
    "steam-v6": {"fill": gradient(STEAM_BG), "groups": [
        glass("eje", alpha=0.35, translucency=0.6, blur=0.15, refraction=(0.7, 0.6)),
        glass("biela", alpha=0.6, translucency=0.5, blur=0.15, refraction=(0.55, 0.45)),
        glass("manivela", alpha=0.9, translucency=0.35, blur=0.3, refraction=(0.4, 0.4)),
    ]},
}


def main():
    """Escribe en icons/ solo los aprobados; el resto de conceptos quedan aquí como historial."""
    geo = pieces()
    clean("steam")
    for name, concept in APPROVED.items():
        spec = CONCEPTS[concept]
        write_icon(name, spec["fill"], spec["groups"], geo)


if __name__ == "__main__":
    main()
