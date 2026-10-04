"""Xbox: logo oficial (la esfera con la X tallada) ajustado al icono de iOS y montaje de los .icon.

Trazado: brands/xbox.svg (recursos de marca, simple-icons 16.34.0): cuatro piezas (cúpula,
derecha, izquierda y arco). Ajustado contra el icono de la App Store (id 736179781, versión
2609.3.1, 1024 px). Con escala uniforme y posición: IoU 0.965. El icono de iOS dibuja la X algo
más estrecha: el arco y las dos piezas laterales son 7-10 px más gruesos en los bordes que miran
hacia abajo y hacia dentro (la cúpula y el contorno coinciden). Se modela con un barrido por
pieza (suma de Minkowski con un vector corto, ajustado por máximo IoU) recortado al círculo de
la esfera, y las puntas redondeadas 4 px como en el icono oficial: IoU 0.994.
Ese icono oficial ya es de Liquid Glass: cuatro piezas de cristal verde con bordes lima sobre
#1A1B1E (medido en las esquinas). Cuerpo verde hondo (~#447901, 3.2:1 sobre el fondo) que se
aclara hacia el borde de la esfera y sobre todo hacia abajo (#D2EC14 al pie de la pieza de
abajo), con bordes lima brillantes. Conceptos:
- c1 (fiel): las cuatro piezas de cristal verde sobre el fondo oficial, con una luz lima detrás.
- c2 (la esfera como lente): una lente de cristal transparente, del tamaño de la esfera, delante
  de las piezas; su bisel curva el contorno y los extremos de la X, como una canica.
- c3 (la X de cristal): el corazón de la X es una pieza de cristal tintado delante de las piezas
  blancas, sobre el verde de Xbox. Sus bordes curvan los de las piezas; fuera de ella los brazos
  siguen tallados, sin deformar (lo deformado junto a lo no deformado: la señal de lente).
- c4: c1 sin la luz lima detrás (lo único que cambia). Compara si la luz refractada aporta.

Cambios en c1/c1c tras la revisión del render (el jurado eligió c1; el escéptico lo rechazó):
1. Costuras rectas de 1 px en la sombra (oscuro: y=907, x=116 y x=907; claro: y=903, x=120 y
   x=903): ictool recortaba la sombra de la capa a una caja ~8-12 px alrededor de la esfera.
   Ahora las capas van a lienzo completo (write_icon con full_bounds) y la sombra es neutra y
   más suave en vez de cromática: no hay brillo verde que cortar (el icono oficial tampoco lo
   tiene) y, si el recorte siguiera, el escalón de una sombra oscura sobre #1A1B1E no se ve.
2. Cristal plano (alpha 0.95 sobre fondo liso: nada que refractar, cuerpo #60A70C uniforme):
   - relleno en degradado de verde hondo arriba a lima abajo (#58A300 → #8CD10A), como el cuerpo
     del oficial; más translucidez (alpha 0.85, translucidez 0.4). El escéptico pedía
     #3E7A00 con alpha 0.75: la cúpula quedaba a ~2.2:1 sobre #1A1B1E en la tecla de 144 px;
     así queda a ~3.6:1 sin luz (el oficial está a 3.2:1).
   - la refracción con función: detrás del cristal, la luz lima de Xbox (las piezas 6 px hacia
     dentro, sin cristal, de tenue arriba a plena abajo). Sobre un fondo liso el bisel no tiene
     nada que doblar; con la luz detrás sí. Medido en el render de c2 (lente 0.5/0.28): el
     bisel mueve el contenido 6-17 px, hacia dentro en los bordes de arriba y de los lados (se
     ve lo de fuera) y hacia fuera en el de abajo. Así la luz llega al borde de abajo de cada
     pieza (borde lima, como el pie brillante del oficial) y arriba y a los lados deja una línea
     oscura fina antes del cuerpo (el oficial la tiene a ~9 px del borde). La luz nunca asoma
     por los huecos (la tapa el cristal) y no llega a las puntas finas (< 28 px de ancho).
     Con 12 px de margen, en la vista plana se leía como un marco oscuro alrededor de la luz.
   - refracción (0.4, 0.15), el máximo de lo aprendido; no (0.5, 0.3) como pedía el escéptico:
     tan honda arrastra contenido lejano a las puntas finas de las piezas. Blur 0.25: suaviza
     el borde de la luz vista a través del cristal.
   - el contorno negro fino de 2-3 px por fuera de las piezas sale en todos los cristales de
     ictool (también en Twitch c3 y Xbox c3); con la capa a lienzo completo puede que la
     refracción del borde deje de leer transparente fuera de la caja de la pieza. A comprobar.
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

# c1/c4: cristal en degradado (arriba → abajo; con la capa a lienzo completo el degradado va de
# y=0 a y=1024, así que las piezas, de y=129 a 896, ven del 13 % al 87 % de él)
GLASS_DEEP = "#58A300"   # verde hondo arriba: la cúpula, sin luz detrás, a ~3.6:1 sobre #1A1B1E
GLASS_LIME = "#8CD10A"   # lima abajo, como el brillo del pie de la pieza de abajo del oficial
GLASS_DEEP_LIGHT = "#0B5E0B"  # en claro: verde más hondo arriba y el de marca abajo (>= 3.5:1
                              # sobre el fondo claro; un verde más vivo abajo bajaba a ~3.1:1)
# c1: la luz lima detrás del cristal (la refracta su bisel)
XBOX_LIME = "#D2EC14"    # lima del brillo del icono oficial (medido al pie de la pieza de abajo)
LIGHT_INSET = 6          # px hacia dentro de cada pieza: el cristal la tapa entera y el bisel
                         # (que mueve 6-17 px) la lleva al borde de abajo
LIGHT_ROUND = 8          # px: redondea sus puntas (abertura morfológica)
LIGHT_MIN_AREA = 400     # px²: sin islas sueltas donde la pieza se estrecha
LIGHT_ALPHA = (0.2, 1.0) # tenue arriba (la cúpula sigue honda), plena abajo: el oficial brilla
                         # sobre todo al pie de la esfera


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


def light_core(logo):
    """La luz lima: cada pieza LIGHT_INSET px hacia dentro, con las puntas redondeadas y sin islas."""
    core = logo.buffer(-(LIGHT_INSET + LIGHT_ROUND), quad_segs=32).buffer(LIGHT_ROUND, quad_segs=32)
    return unary_union([p for p in getattr(core, "geoms", [core]) if p.area >= LIGHT_MIN_AREA])


def pieces():
    logo = unary_union(list(logo_pieces().values()))
    return {
        # c1, c3 y c4: el logo oficial (las cuatro piezas en una capa)
        "logo": logo,
        # c1: la luz lima detrás del cristal
        "luz": light_core(logo),
        # c2: el logo reducido y, delante, la lente redonda apenas mayor que la esfera
        "logo-lente": affinity.scale(logo, LENS_SCALE, LENS_SCALE, origin=CENTER),
        "lente": disk(RADIUS * LENS_SCALE + LENS_RIM),
        # c3: la X de cristal delante del logo
        "x": x_glass(logo),
    }


BG = {"solid": color(XBOX_BG)}  # el fondo del icono oficial
GREEN_BG = auto_gradient(XBOX_GREEN)


def logo_crystal(light=False):
    """c1/c4: las piezas de cristal verde, en degradado de verde hondo a lima y más translúcidas.

    Sombra neutra y suave (no cromática): sin brillo verde que ictool pueda recortar en recto.
    Refracción (0.4, 0.15): el bisel dobla la luz lima de detrás (c1) hasta el borde de abajo.
    En claro, más opaco (alpha 0.92, translucidez 0.35): la translucidez mezcla el fondo blanco
    y aclara el verde; así el pie de la pieza de abajo sigue a >= 3.5:1.
    """
    if light:
        alpha, top, bottom = 0.92, GLASS_DEEP_LIGHT, XBOX_GREEN
        g = glass("logo", alpha=alpha, translucency=0.35, blur=0.25, refraction=(0.4, 0.15),
                  shadow="neutral", shadow_opacity=0.3)
    else:
        alpha, top, bottom = 0.85, GLASS_DEEP, GLASS_LIME
        g = glass("logo", alpha=alpha, translucency=0.4, blur=0.25, refraction=(0.4, 0.15),
                  shadow="neutral", shadow_opacity=0.35)
    g["layers"][0]["fill"] = {"linear-gradient": [color(top, alpha), color(bottom, alpha)]}
    return g


def lime_light():
    """c1: la luz lima detrás del cristal: contenido plano (sin cristal, sin sombra ni brillo)
    para que el cristal de delante tenga algo que refractar. Tenue arriba, plena abajo."""
    return {
        "name": "luz",
        "lighting": "individual",
        "specular": False,
        "blur-material": 0.0,
        "shadow": {"kind": "none", "opacity": 0.0},
        "translucency": {"enabled": False, "value": 0.0},
        "layers": [{"name": "luz", "image-name": "luz.svg", "glass": False,
                    "fill": {"linear-gradient": [color(XBOX_LIME, LIGHT_ALPHA[0]),
                                                 color(XBOX_LIME, LIGHT_ALPHA[1])]}}],
    }


def logo_glass(image="logo", light=False):
    """c2/c3: las piezas de cristal verde, como el icono oficial; sombra cromática (brillo verde)."""
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
    # c1 (fiel): como el icono oficial, piezas de cristal verde sobre #1A1B1E, con la luz lima
    # detrás que el cristal deja ver y su bisel refracta hasta el borde
    "xbox-c1": {"fill": BG, "groups": [logo_crystal(), lime_light()]},
    "xbox-c1c": {"fill": "system-light", "groups": [logo_crystal(light=True), lime_light()]},
    # c4: c1 sin la luz lima (solo el cristal en degradado): para comparar en el render
    "xbox-c4": {"fill": BG, "groups": [logo_crystal()]},
    "xbox-c4c": {"fill": "system-light", "groups": [logo_crystal(light=True)]},
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
        # full_bounds: capas a lienzo completo, para que ictool no recorte la sombra en recto
        write_icon(name, spec["fill"], spec["groups"], geo, full_bounds=True)


if __name__ == "__main__":
    import sys
    main(sys.argv[1:] or None)
