"""Xbox: logo oficial (la esfera con la X tallada) ajustado al icono de iOS y montaje de los .icon.

Trazado: brands/xbox.svg (recursos de marca, simple-icons 16.34.0): cuatro piezas (cúpula,
derecha, izquierda y arco). Ajustado contra el icono de la App Store (id 736179781, versión
2609.3.1, 1024 px). Con escala uniforme y posición: IoU 0.965. El icono de iOS dibuja la X algo
más estrecha: el arco y las dos piezas laterales son 7-10 px más gruesos en los bordes que miran
hacia abajo y hacia dentro (la cúpula y el contorno coinciden). Se modela con un barrido por
pieza (suma de Minkowski con un vector corto, ajustado por máximo IoU) recortado al círculo de
la esfera, y las puntas redondeadas 4 px como en el icono oficial: IoU 0.994.
Ese icono oficial ya es de Liquid Glass: cuatro piezas de cristal verde con bordes lima sobre
#1A1B1E (medido en las esquinas). Conceptos:
- c1 (fiel): las cuatro piezas de cristal verde sobre el fondo oficial.
- c2 (la esfera como lente): una lente de cristal transparente, del tamaño de la esfera, delante
  de las piezas; su bisel curva el contorno y los extremos de la X, como una canica.
- c3 (la X de cristal): el corazón de la X es una pieza de cristal tintado delante de las piezas
  blancas, sobre el verde de Xbox. Sus bordes curvan los de las piezas; fuera de ella los brazos
  siguen tallados, sin deformar (lo deformado junto a lo no deformado: la señal de lente).
"""
import re

import numpy as np
from shapely import affinity
from shapely.geometry import Point
from shapely.ops import unary_union

from brand import place, subpath_shapes
from liquid import ROOT, WHITE, auto_gradient, clean, color, glass, write_icon

D = re.search(r' d="([^"]+)"', (ROOT / "brands" / "xbox.svg").read_text(encoding="utf-8")).group(1)
FIT = (31.968, 31.968, 128.25, 128.5)  # escala x, escala y, desplazamiento x, y (lienzo de 1024)
NAMES = ("cupula", "derecha", "izquierda", "arco")  # orden de los subtrazados del SVG
SWEEP = {"derecha": (-5.25, 5.0), "izquierda": (5.25, 5.0), "arco": (0.0, 10.5)}  # px, simétrico
TIP_ROUND = 4.0   # px: puntas romas, como en el icono oficial
CENTER = (12 * FIT[0] + FIT[2], 12 * FIT[1] + FIT[3])  # centro de la esfera (511.9, 512.1)
RADIUS = 12 * FIT[0]                                   # radio de la esfera (383.6)
RES = 256

# c2: el logo algo más pequeño para que la lente (que refracta fuerte) quede lejos del borde
LENS_SCALE = 0.86  # esfera de 330 px de radio: la lente acaba a 174 px del borde del lienzo
LENS_RIM = 8       # px que la lente sobresale de la esfera: la lente ES la esfera (con 22 px se
                   # leía como un anillo añadido alrededor del logo)
# c3: la X de cristal. Los brazos miden 30-45 px junto al borde de la esfera; el bisel recoge
# contenido de ~50 px y los llenaría de blanco, así que el cristal solo cubre la parte ancha:
X_MIN_WIDTH = 72   # px: se queda con la X donde mide al menos esto (abertura morfológica): los
                   # brazos de abajo acaban redondeados a r ~292 del centro de la esfera
X_REACH = 310      # radio máximo: los brazos de arriba (anchos hasta el borde) acaban a 50 px de
                   # las puntas finas del arco. (Un corte circular a r 300 sobre toda la X unía los
                   # dos brazos de arriba en una tapa; uno centrado en el cruce hacía un disco-lupa.)
X_OVERLAP = 12     # px que el cristal pisa las piezas: su borde se ve como una pieza aparte
X_FILLET = 12      # px: redondea las esquinas cóncavas (si no, la refracción se arruga)
X_END_ROUND = 16   # px: redondea las esquinas de los extremos

XBOX_BG = "#1A1B1E"      # fondo del icono oficial de iOS (medido)
XBOX_GREEN = "#107C10"   # verde de marca de Xbox
GLASS_GREEN = "#6AB80A"  # cristal verde para fondo oscuro: con translucidez 0.25 da el #578F03 medido


def disk(r, c=CENTER):
    return Point(c).buffer(r, quad_segs=RES)


def sweep(p, v, n=12):
    """Suma de Minkowski de la pieza con el segmento 0→v (engorda solo los bordes que miran hacia v)."""
    return unary_union([affinity.translate(p, v[0] * t, v[1] * t) for t in np.linspace(0, 1, n)])


def logo_pieces():
    """Las cuatro piezas oficiales colocadas como en el icono de iOS."""
    sphere = disk(RADIUS)
    out = {}
    for name, s in zip(NAMES, subpath_shapes(D)):
        p = place(s, *FIT)
        if name in SWEEP:
            p = sweep(p, SWEEP[name])
        p = p.buffer(-TIP_ROUND, quad_segs=32).buffer(TIP_ROUND, quad_segs=32)
        out[name] = p.intersection(sphere)
    return out


def largest(geom):
    return max(getattr(geom, "geoms", [geom]), key=lambda g: g.area)


def x_glass(logo):
    """El corazón de la X: el hueco entre las piezas donde es ancho, algo más ancho que el hueco."""
    gap = largest(disk(RADIUS).difference(logo).buffer(-1.5).buffer(1.5))  # sin astillas en el borde
    r = X_MIN_WIDTH / 2
    core = largest(gap.buffer(-r, quad_segs=64).buffer(r, quad_segs=64)).intersection(disk(X_REACH - X_OVERLAP))
    x = core.buffer(X_OVERLAP, quad_segs=64)
    x = x.buffer(X_FILLET, quad_segs=32).buffer(-X_FILLET, quad_segs=32)
    return x.buffer(-X_END_ROUND, quad_segs=32).buffer(X_END_ROUND, quad_segs=32)


def pieces():
    logo = unary_union(list(logo_pieces().values()))
    return {
        # c1 y c3: el logo oficial (las cuatro piezas en una capa)
        "logo": logo,
        # c2: el logo reducido y, delante, la lente redonda apenas mayor que la esfera
        "logo-lente": affinity.scale(logo, LENS_SCALE, LENS_SCALE, origin=CENTER),
        "lente": disk(RADIUS * LENS_SCALE + LENS_RIM),
        # c3: la X de cristal delante del logo
        "x": x_glass(logo),
    }


BG = {"solid": color(XBOX_BG)}  # el fondo del icono oficial
GREEN_BG = auto_gradient(XBOX_GREEN)


def logo_glass(image="logo", light=False):
    """Las piezas de cristal verde, como el icono oficial; sombra cromática (brillo verde)."""
    if light:
        return glass("logo", fill=XBOX_GREEN, alpha=0.95, translucency=0.2, blur=0.3,
                     refraction=(0.35, 0.2), shadow="layer-color", shadow_opacity=0.5, image=image)
    return glass("logo", fill=GLASS_GREEN, alpha=0.95, translucency=0.25, blur=0.3,
                 refraction=(0.35, 0.2), shadow="layer-color", shadow_opacity=0.6, image=image)


def logo_white():
    """Las piezas de cristal blanco sobre el verde de Xbox (el logo clásico de la marca)."""
    return glass("logo", alpha=0.95, translucency=0.2, blur=0.3, refraction=(0.35, 0.2),
                 shadow="neutral", shadow_opacity=0.5)


def lens(light=False):
    """La esfera como lente: cristal transparente sin esmerilar, redondo y liso, refracción fuerte."""
    return glass("lente", fill=XBOX_GREEN if light else WHITE, alpha=0.05 if light else 0.08,
                 translucency=0.85, blur=0.0, refraction=(0.5, 0.28), shadow="neutral", shadow_opacity=0.3)


def x_front(light=False):
    """La X de cristal tintado sin esmerilar. Sobre el hueco no cambia el color (verde sobre verde,
    blanco sobre claro), así la X se sigue leyendo tallada; sobre el borde de las piezas se ve el
    tinte y ahí curva sus bordes. Refracción suave: es una pieza de brazos estrechos.
    En claro, el blanco con alpha 0.35 aclaraba el borde verde que pisa a 2.9:1 contra la X; 0.25 da 3:1."""
    if light:
        return glass("x", fill=WHITE, alpha=0.25, translucency=0.8, blur=0.0, refraction=(0.3, 0.12),
                     shadow="neutral", shadow_opacity=0.25, specular="inside")
    return glass("x", fill=XBOX_GREEN, alpha=0.3, translucency=0.8, blur=0.0, refraction=(0.3, 0.12),
                 shadow="layer-color", shadow_opacity=0.35, specular="inside")


APPROVED = {}

CONCEPTS = {
    # c1 (fiel): como el icono oficial, piezas de cristal verde sobre #1A1B1E
    "xbox-c1": {"fill": BG, "groups": [logo_glass()]},
    "xbox-c1c": {"fill": "system-light", "groups": [logo_glass(light=True)]},
    # c2: la esfera como lente transparente delante de las piezas
    "xbox-c2": {"fill": BG, "groups": [lens(), logo_glass("logo-lente")]},
    "xbox-c2c": {"fill": "system-light", "groups": [lens(light=True), logo_glass("logo-lente", light=True)]},
    # c3: la X de cristal delante de las piezas (blanco sobre el verde de Xbox; en claro, verde)
    "xbox-c3": {"fill": GREEN_BG, "groups": [x_front(), logo_white()]},
    "xbox-c3c": {"fill": "system-light", "groups": [x_front(light=True), logo_glass(light=True)]},
}


def main(names=None):
    """Escribe los aprobados; con nombres de concepto, escribe esos para renderizarlos."""
    geo = pieces()
    clean("xbox")
    targets = {n: n for n in names} if names else APPROVED
    for name, concept in targets.items():
        spec = CONCEPTS[concept]
        write_icon(name, spec["fill"], spec["groups"], geo)


if __name__ == "__main__":
    import sys
    main(sys.argv[1:] or None)
