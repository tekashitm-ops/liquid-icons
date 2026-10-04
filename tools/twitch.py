"""Twitch: logo oficial (el «glitch») ajustado al icono de iOS y montaje de los .icon.

Trazado: brands/twitch.svg (recursos de marca, brand.twitch.tv vía simple-icons), sin
deformar: solo escala uniforme y posición. Ajustado contra el icono de la App Store
(«Twitch: Live Streaming», id 460177396, 1024 px) con IoU 0.992 en la silueta del bocadillo
y 0.978 en la cara blanca (los ojos se dejan como en el logo de marca).

Conceptos g (Liquid Glass al máximo: todas las piezas son cristal de color translúcido y cada
cristal tiene algo detrás que refractar). gN = oscuro (negro de Twitch, para la tecla);
gNc = su pareja clara (cristal morado sobre blanco, para un futuro modo día/noche).
- g1 «glitch doble»: dos copias del logo desplazadas como un glitch. Delante, el glitch
  (marco + ojos) de cristal lila transparente; detrás, el bocadillo entero de cristal morado
  profundo, 36 px abajo a la derecha. Por la cara hueca se ve la copia de detrás, y el bisel
  del marco de delante dobla los bordes de la de detrás donde los pisa.
- g2 «cara de luz»: el bocadillo es una losa de cristal violeta con los ojos huecos; detrás,
  la cara de cristal blanco esmerilado brilla a través del violeta. Los ojos son ventanas de
  cristal claro al fondo, y su bisel dobla el borde de la cara. En claro, la cara de detrás
  es morado profundo (blanco sobre blanco no se vería).
- g3 «bloque de cristal»: el glitch de cristal morado encendido dentro de un bloque de cristal
  transparente con la forma del bocadillo (Vista Previa / engranaje de Discord): el bisel del
  bloque aumenta y dobla el marco morado que tiene debajo.
Los conceptos c (logo casi opaco, rechazados: «no tiene Liquid Glass») siguen en el historial.
"""
import re

from shapely import affinity
from shapely.geometry import Point

from brand import place, subpath_shapes
from liquid import ROOT, clean, color, glass, write_icon

D = re.search(r' d="([^"]+)"', (ROOT / "brands" / "twitch.svg").read_text(encoding="utf-8")).group(1)
FIT = (29.899, 29.899, 153.177, 181.0)  # escala x, escala y, desplazamiento x, y (lienzo de 1024)

TWITCH_PURPLE = "#9146FF"   # color de marca
TWITCH_DARK = "#0E0E10"     # fondo del tema oscuro de Twitch
# Escala de morados de Twitch (Core UI): claros para el cristal sobre negro, profundos para
# el de detrás
LAVENDER = "#BF94FF"
LILAC = "#D1B3FF"
VIOLET = "#A970FF"
DEEP = "#772CE8"
DEEPER = "#5C16C5"
DEEPEST = "#451093"

MITRE = 1.5        # las esquinas rectas se quedan vivas; la punta de 45° de la cola se chaflana
TIP_R = 3          # px: radio con el que se redondea solo la punta de 45° de la cola
TIP_ZONE = 30      # px alrededor de la punta en los que se aplica (el resto queda intacto)
FILLET = 12        # px: redondea las esquinas cóncavas (la refracción no se pliega en ellas)
GLITCH = 18        # px: cada copia de g1 se desplaza 18 px en diagonal (36 px entre las dos)
BLOCK = 26         # px que el bloque de cristal de g3 sobresale del glitch
PANE = 8           # px que la ventana de cada ojo de g2 pisa la losa alrededor del hueco


def grow(geom, px):
    """Agranda una pieza sin redondear sus esquinas rectas."""
    return geom.buffer(px, join_style="mitre", mitre_limit=MITRE)


def fillet_concave(geom, r=FILLET):
    """Cierre morfológico: rellena con un radio r solo las esquinas cóncavas."""
    return geom.buffer(r, quad_segs=32).buffer(-r, quad_segs=32)


def soften(geom, r):
    """Apertura morfológica: redondea con un radio r solo las esquinas convexas."""
    return geom.buffer(-r, quad_segs=16).buffer(r, quad_segs=16)


def round_tip(geom, r=TIP_R, zone=TIP_ZONE):
    """Redondea con radio r solo la punta más baja (la de 45° de la cola): sin ella el bisel
    junta su brillo en un destello de 1 px en el vértice; las demás esquinas siguen vivas."""
    tip = max(geom.exterior.coords, key=lambda p: p[1])
    area = Point(tip).buffer(zone, quad_segs=32)
    return geom.difference(area).union(soften(geom, r).intersection(area))


def shift(geom, d):
    return affinity.translate(geom, d, d)


def pieces():
    eye_l, eye_r, outer, inner = (place(s, *FIT) for s in subpath_shapes(D))
    eyes = eye_l.union(eye_r)
    slab = fillet_concave(round_tip(outer))            # bocadillo entero, sin rincones vivos
    mark = fillet_concave(round_tip(outer).difference(inner).union(eyes))  # glitch (marco + ojos)
    return {
        # g1: el glitch delante, arriba a la izquierda; el bocadillo detrás, abajo a la derecha
        "glitch-delante": shift(mark, -GLITCH),
        "glitch-detras": shift(slab, GLITCH),
        # g2: losa con los ojos huecos, cara con los ojos huecos detrás y una ventana por ojo
        "losa": fillet_concave(round_tip(outer).difference(eyes)),
        "cara": fillet_concave(inner.difference(eyes), 8),
        "ventanas": soften(grow(eyes, PANE), 4),
        # g3: el glitch dentro del bloque de cristal (el bocadillo agrandado BLOCK px)
        "glitch": mark,
        "bloque": fillet_concave(grow(round_tip(outer), BLOCK), 20),
    }


def vidrio(name, fill, alpha, translucency, blur, refraction=None, shadow="neutral",
           shadow_opacity=0.5, specular="automatic", blend=None, fill_to=None):
    """glass() con dos palancas más: modo de fusión del grupo y relleno en degradado (de
    fill arriba a fill_to abajo, con el mismo alfa)."""
    g = glass(name, fill=fill, alpha=alpha, translucency=translucency, blur=blur,
              refraction=refraction, shadow=shadow, shadow_opacity=shadow_opacity, specular=specular)
    if blend:
        g["blend-mode"] = blend
    if fill_to:
        g["layers"][0]["fill"] = {"linear-gradient": [color(fill, alpha), color(fill_to, alpha)]}
    return g


# --- g1: glitch doble ---

def g1(light=False, front_refraction=(0.35, 0.12), blend=None):
    """Delante el glitch de cristal claro sin esmerilar; detrás el bocadillo de cristal de
    color, que es lo que se ve por la cara hueca y lo que el marco de delante dobla."""
    if light:
        front = vidrio("glitch-delante", TWITCH_PURPLE, 0.72, 0.5, 0.0, front_refraction,
                       shadow="layer-color", shadow_opacity=0.45, blend=blend)
        back = vidrio("glitch-detras", LILAC, 0.8, 0.45, 0.2, (0.3, 0.1),
                      shadow="layer-color", shadow_opacity=0.4)
    else:
        front = vidrio("glitch-delante", LILAC, 0.62, 0.55, 0.0, front_refraction,
                       shadow="layer-color", shadow_opacity=0.5, blend=blend)
        back = vidrio("glitch-detras", DEEP, 0.85, 0.4, 0.2, (0.3, 0.1),
                      shadow="layer-color", shadow_opacity=0.75)
    return [front, back]


# --- g2: cara de luz ---

def g2(light=False, panes=True):
    """Losa violeta translúcida delante de la cara esmerilada; ventanas claras en los ojos."""
    windows = vidrio("ventanas", "#FFFFFF", 0.14, 0.9, 0.0, (0.25, 0.08), shadow_opacity=0.3)
    if light:
        slab = vidrio("losa", TWITCH_PURPLE, 0.62, 0.55, 0.0, (0.35, 0.12),
                      shadow="layer-color", shadow_opacity=0.45)
        face = vidrio("cara", DEEPEST, 0.92, 0.3, 0.5, (0.2, 0.06), shadow_opacity=0.25)
    else:
        slab = vidrio("losa", TWITCH_PURPLE, 0.55, 0.6, 0.0, (0.35, 0.12),
                      shadow="layer-color", shadow_opacity=0.65)
        face = vidrio("cara", "#FFFFFF", 0.95, 0.25, 0.5, (0.2, 0.06), shadow_opacity=0.3)
    return ([windows] if panes else []) + [slab, face]


# --- g3: bloque de cristal ---

def g3(light=False, block_refraction=(0.45, 0.2)):
    """Bloque transparente (casi sin color, sin esmerilar) sobre el glitch encendido."""
    if light:
        block = vidrio("bloque", LAVENDER, 0.22, 0.85, 0.0, block_refraction, shadow_opacity=0.4)
        mark = vidrio("glitch", TWITCH_PURPLE, 0.88, 0.4, 0.3, None,
                      shadow="layer-color", shadow_opacity=0.5)
    else:
        block = vidrio("bloque", "#EDE3FF", 0.16, 0.88, 0.0, block_refraction, shadow_opacity=0.35)
        mark = vidrio("glitch", VIOLET, 0.88, 0.45, 0.3, None,
                      shadow="layer-color", shadow_opacity=0.8)
    return [block, mark]


# Negro de Twitch con un poco de morado arriba: el cristal tiene un degradado que doblar
BG_DARK = {"linear-gradient": [color("#1A1426"), color(TWITCH_DARK)]}
BG_LIGHT = {"linear-gradient": [color("#FFFFFF"), color("#F1EAFF")]}

APPROVED = {}

CONCEPTS = {
    "twitch-g1": {"fill": BG_DARK, "groups": g1()},
    "twitch-g1c": {"fill": BG_LIGHT, "groups": g1(light=True)},
    "twitch-g2": {"fill": BG_DARK, "groups": g2()},
    "twitch-g2c": {"fill": BG_LIGHT, "groups": g2(light=True)},
    "twitch-g3": {"fill": BG_DARK, "groups": g3()},
    "twitch-g3c": {"fill": BG_LIGHT, "groups": g3(light=True)},
    # Pruebas de la ronda 1 (se borran solas al escribir sin ellas)
    "twitch-v1": {"fill": BG_DARK, "groups": g1(blend="plus-lighter")},
    "twitch-v2": {"fill": BG_DARK, "groups": g1(front_refraction=(0.45, 0.2))},
    "twitch-v3": {"fill": BG_DARK, "groups": g2(panes=False)},
    "twitch-v4": {"fill": BG_DARK, "groups": g3(block_refraction=(0.6, 0.35))},
}


def main(names=None):
    """Escribe los aprobados; con nombres de concepto, escribe esos para renderizarlos."""
    geo = pieces()
    clean("twitch")
    targets = {n: n for n in names} if names else APPROVED
    for name, concept in targets.items():
        spec = CONCEPTS[concept]
        # Capas a lienzo completo: ictool ya no recorta la sombra a la caja de cada pieza
        write_icon(name, spec["fill"], spec["groups"], geo, full_bounds=True)


if __name__ == "__main__":
    import sys
    main(sys.argv[1:] or None)
