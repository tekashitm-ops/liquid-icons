"""Twitch: logo oficial (el «glitch») ajustado al icono de iOS y montaje de los .icon.

Trazado: brands/twitch.svg (recursos de marca, brand.twitch.tv vía simple-icons), sin
deformar: solo escala uniforme y posición. Ajustado contra el icono de la App Store
(«Twitch: Live Streaming», id 460177396, 1024 px) con IoU 0.992 en la silueta del bocadillo
y 0.978 en la cara blanca (los ojos se dejan como en el logo de marca).

Conceptos g (Liquid Glass al máximo: todas las piezas son cristal de color translúcido y cada
cristal tiene algo detrás que refractar). gN = oscuro (negro de Twitch, para la tecla);
gNc = su pareja clara (cristal morado sobre blanco, para un futuro modo día/noche).
- g1 «glitch doble»: dos copias del logo desplazadas 40 px en diagonal, como un glitch.
  Delante, el glitch (marco + ojos) de cristal lila transparente que se suma como luz
  (plus-lighter); detrás, el bocadillo entero de cristal morado profundo, que asoma arriba a la
  derecha y es lo que se ve por la cara hueca. En claro: cristal morado que se multiplica sobre
  una copia violeta.
- g2 «cara de luz»: el bocadillo es una losa de cristal violeta con los ojos huecos; detrás,
  la cara de cristal blanco esmerilado brilla a través del violeta y el bisel de la losa la
  dobla hacia su borde (línea lila arriba, a la derecha y en la diagonal). Los ojos son
  ventanas de cristal claro al fondo, y su bisel dobla el borde de la cara. En claro, la cara
  de detrás es morado profundo (blanco sobre blanco no se vería).
- g3 «glitch en franjas»: el glitch morado sobre cristal casi transparente (como el logo en
  tema oscuro, la cara deja ver el fondo), cortado en tres franjas: la del medio, delante y
  corrida 36 px a la derecha, es una barra de cristal que dobla con su bisel los bordes de las
  franjas que pisa y deja a la izquierda el hueco del glitch.
Los conceptos c (logo casi opaco, rechazados: «no tiene Liquid Glass») siguen en el historial.
"""
import re

from shapely import affinity
from shapely.geometry import Point, box

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
DEEPEST = "#451093"

MITRE = 1.5        # las esquinas rectas se quedan vivas; la punta de 45° de la cola se chaflana
TIP_R = 3          # px: radio con el que se redondea solo la punta de 45° de la cola
TIP_ZONE = 30      # px alrededor de la punta en los que se aplica (el resto queda intacto)
FILLET = 12        # px: redondea las esquinas cóncavas (la refracción no se pliega en ellas)
GLITCH = 20        # px: cada copia de g1 se desplaza 20 px en diagonal (40 px entre las dos)
BACK_FILLET = 12   # px: rincones cóncavos de la copia de detrás de g1
PANE = 8           # px que la ventana de cada ojo de g2 pisa la losa alrededor del hueco
CUT_TOP = 560      # g3: cortes de la franja central, por debajo de los ojos (acaban en 476: el
CUT_BOTTOM = 660   #     bisel de la franja no los alcanza) y por la muesca de la cara
OVERLAP = 24       # px que la franja pisa a cada vecina
SLICE_SHIFT = 36   # px que se corre la franja (el glitch)


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


def shift(geom, dx, dy):
    return affinity.translate(geom, dx, dy)


def pieces():
    eye_l, eye_r, outer, inner = (place(s, *FIT) for s in subpath_shapes(D))
    eyes = eye_l.union(eye_r)
    slab = fillet_concave(round_tip(outer), BACK_FILLET)  # bocadillo entero, sin rincones vivos
    mark = fillet_concave(round_tip(outer).difference(inner).union(eyes))  # glitch (marco + ojos)
    face = fillet_concave(inner.difference(eyes), 8)  # cara con los ojos huecos
    return {
        **glitch_pair(mark, slab),
        # g2: losa con los ojos huecos, cara con los ojos huecos detrás y una ventana por ojo
        "losa": fillet_concave(round_tip(outer).difference(eyes)),
        "cara": face,
        "ventanas": soften(grow(eyes, PANE), 4),
        # g3: el logo cortado en tres franjas; la del medio, delante y corrida a la derecha
        **slices(mark, face),
    }


def glitch_pair(mark, slab, g=GLITCH):
    """g1: el glitch delante, abajo a la izquierda; el bocadillo detrás, arriba a la derecha.
    Desplazados a lo largo de las diagonales del logo (las diagonales de detrás caen sobre las
    de delante). Así el único borde de la copia de detrás que queda bajo el cristal de delante
    es el izquierdo, bajo la banda gruesa del marco (154 px): bajo las finas (51 px, arriba y a
    la derecha) su bisel se veía como una banda gris.
    Bajo la banda de abajo y la cola de delante la copia de detrás se rellena hasta los bordes
    de delante (no se ve desde fuera): con su propia cola, el borde caía dentro del bisel
    estrecho de la cola y salía como una gota; sin cola, la de delante quedaba sobre el negro
    del fondo y se veía gris."""
    base = 19.714 * FIT[1] + FIT[3]  # base de la cola en el lienzo (y = 19.714 en el SVG)
    front = shift(slab, -g, g)
    under = front.intersection(box(slab.bounds[0] + g, base - g, 1024, 1024))
    back = shift(slab.intersection(box(0, 0, 1024, base)), g, -g).union(under)
    return {
        "glitch-delante": shift(mark, -g, g),
        "glitch-detras": fillet_concave(back),
    }


def slices(mark, face):
    """Franja central corrida SLICE_SHIFT px, y el resto (arriba y abajo). Cada franja es
    un cuerpo de cristal entero (la cara también, casi transparente) con el glitch tintado.
    La franja pisa OVERLAP px de cada vecina: ahí su bisel dobla los bordes de la de detrás.
    Lo que pisa se recorta a lo que la franja tapa: a la izquierda (donde la franja se ha
    ido) asomaban dos pestañas; ahí queda el hueco del glitch."""
    top, bottom = CUT_TOP - OVERLAP / 2, CUT_BOTTOM + OVERLAP / 2
    mid = box(0, top, 1024, bottom)
    left = mark.bounds[0] + SLICE_SHIFT  # borde izquierdo de la franja ya corrida
    under = box(left, top, 1024, top + OVERLAP).union(box(left, bottom - OVERLAP, 1024, bottom))
    rest = box(0, 0, 1024, top).union(box(0, bottom, 1024, 1024)).union(under)
    return {
        "franja-marco": shift(mark.intersection(mid), SLICE_SHIFT, 0),
        "franja-cara": shift(face.intersection(mid), SLICE_SHIFT, 0),
        "resto-marco": mark.intersection(rest),
        "resto-cara": face.intersection(rest),
    }


def vidrio(name, fill, alpha, translucency, blur, refraction=None, shadow="neutral",
           shadow_opacity=0.5, specular="automatic", blend=None):
    """glass() con una palanca más: el modo de fusión del grupo (blend-mode)."""
    g = glass(name, fill=fill, alpha=alpha, translucency=translucency, blur=blur,
              refraction=refraction, shadow=shadow, shadow_opacity=shadow_opacity, specular=specular)
    if blend:
        g["blend-mode"] = blend
    return g


# --- g1: glitch doble ---

def g1(light=False):
    """Delante el glitch de cristal claro sin esmerilar, que se suma como luz a lo de detrás
    (plus-lighter; en claro, multiply: se mezcla como dos cristales tintados); detrás el
    bocadillo de cristal de color, que es lo que se ve por la cara hueca y lo que el marco de
    delante dobla. Sin sombra delante: oscurecía la copia de detrás (gris sucio). Detrás sin
    refracción: su bisel traía el negro del fondo y, visto a través del de delante, era una
    banda gris."""
    if light:
        front = vidrio("glitch-delante", TWITCH_PURPLE, 0.62, 0.6, 0.0, (0.3, 0.1),
                       shadow="none", shadow_opacity=0.0, blend="multiply")
        back = vidrio("glitch-detras", VIOLET, 0.7, 0.45, 0.25, None,
                      shadow="layer-color", shadow_opacity=0.45)
    else:
        front = vidrio("glitch-delante", LILAC, 0.5, 0.65, 0.0, (0.3, 0.1),
                       shadow="none", shadow_opacity=0.0, blend="plus-lighter")
        back = vidrio("glitch-detras", DEEP, 0.9, 0.4, 0.25, None,
                      shadow="layer-color", shadow_opacity=0.75)
    return [front, back]


# --- g2: cara de luz ---

def g2(light=False, refraction=(0.26, 0.08)):
    """Losa violeta translúcida delante de la cara esmerilada; ventanas claras en los ojos.
    Refracción de la losa 0.26/0.08: a 0.35/0.12 su borde exterior traía los ojos (a 141 px)
    y a 0.3/0.1 aún traía la cara en tramos sueltos."""
    windows = vidrio("ventanas", "#FFFFFF", 0.14, 0.9, 0.0, (0.25, 0.08), shadow_opacity=0.3)
    if light:
        slab = vidrio("losa", TWITCH_PURPLE, 0.62, 0.55, 0.0, refraction,
                      shadow="layer-color", shadow_opacity=0.45)
        face = vidrio("cara", DEEPEST, 0.92, 0.3, 0.5, (0.2, 0.06), shadow_opacity=0.25)
    else:
        slab = vidrio("losa", TWITCH_PURPLE, 0.55, 0.6, 0.0, refraction,
                      shadow="layer-color", shadow_opacity=0.65)
        face = vidrio("cara", "#FFFFFF", 0.95, 0.25, 0.5, (0.2, 0.06), shadow_opacity=0.3)
    return [windows, slab, face]


# --- g3: glitch en franjas ---

def slab_group(name, frame, alpha, face, face_alpha, translucency, blur, refraction, shadow,
               shadow_opacity, blend=None):
    """Un cuerpo de cristal con dos tintes (el glitch y la cara): lighting combined, así el
    borde entre marco y cara no lleva bisel; solo lo lleva el contorno de la franja."""
    g = vidrio(name, frame, alpha, translucency, blur, refraction, shadow=shadow,
               shadow_opacity=shadow_opacity, blend=blend)
    g["lighting"] = "combined"
    g["layers"] = [
        {"name": f"{name}-marco", "image-name": f"{name}-marco.svg", "glass": True,
         "fill": {"solid": color(frame, alpha)}},
        {"name": f"{name}-cara", "image-name": f"{name}-cara.svg", "glass": True,
         "fill": {"solid": color(face, face_alpha)}},
    ]
    return g


def g3(light=False, refraction=(0.4, 0.15)):
    """El glitch morado sobre cristal transparente (el logo de Twitch en tema oscuro: la cara
    deja ver el fondo), cortado en tres franjas. La del medio, delante y corrida, se suma como
    luz a lo que pisa (en claro se multiplica); sin sombra, para no ensuciar lo de detrás.
    Cara de cristal casi transparente, con un tinte lila mínimo: con lila al 0.72 se veía gris
    sobre el negro y con blanco al 0.12, la franja era una mancha gris. Refracción de la franja
    0.4/0.15 (bisel ancho): dobla el borde de la cara de detrás, 36 px a la izquierda."""
    if light:
        frame, alpha, mix, glow = TWITCH_PURPLE, 0.8, "multiply", 0.4
    else:
        frame, alpha, mix, glow = VIOLET, 0.75, "plus-lighter", 0.65
    front = slab_group("franja", frame, alpha, LAVENDER, 0.16, 0.6, 0.0, refraction, "none", 0.0,
                       blend=mix)
    rest = slab_group("resto", frame, alpha, LAVENDER, 0.1, 0.55, 0.05, (0.25, 0.08),
                      "layer-color", glow)
    return [front, rest]


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
