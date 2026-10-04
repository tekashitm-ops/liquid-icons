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
DEEPER = "#5C16C5"
DEEPEST = "#451093"

MITRE = 1.5        # las esquinas rectas se quedan vivas; la punta de 45° de la cola se chaflana
TIP_R = 3          # px: radio con el que se redondea solo la punta de 45° de la cola
TIP_ZONE = 30      # px alrededor de la punta en los que se aplica (el resto queda intacto)
FILLET = 12        # px: redondea las esquinas cóncavas (la refracción no se pliega en ellas)
GLITCH = 16        # px: cada copia de g1 se desplaza 16 px en diagonal (32 px entre las dos)
BACK_FILLET = 12   # px: rincones cóncavos de la copia de detrás de g1
PANE = 8           # px que la ventana de cada ojo de g2 pisa la losa alrededor del hueco
CUT_TOP = 552      # g3: cortes de la franja central, por debajo de los ojos (acaban en 476: el
CUT_BOTTOM = 650   #     bisel de la franja no los alcanza) y por la muesca de la cara
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
    return {
        # g1: el glitch delante, arriba a la derecha; el bocadillo detrás, abajo a la izquierda.
        # Desplazado a lo largo de las diagonales del logo: las dos diagonales de la copia de
        # detrás caen sobre las de delante y ningún borde suyo cruza la cola (bisel estrecho)
        "glitch-delante": shift(mark, GLITCH, -GLITCH),
        "glitch-detras": shift(slab, -GLITCH, GLITCH),
        # g2: losa con los ojos huecos, cara con los ojos huecos detrás y una ventana por ojo
        "losa": fillet_concave(round_tip(outer).difference(eyes)),
        "cara": fillet_concave(inner.difference(eyes), 8),
        "ventanas": soften(grow(eyes, PANE), 4),
        # g3: el logo cortado en tres franjas; la del medio, delante y corrida a la derecha
        **slices(mark, fillet_concave(inner.difference(eyes), 8)),
    }


def slices(mark, face):
    """Franja central (marco + cara) corrida SLICE_SHIFT px, y el resto (arriba y abajo).
    La franja pisa OVERLAP px de cada vecina: ahí su bisel dobla el borde de la de detrás."""
    mid = box(0, CUT_TOP - OVERLAP / 2, 1024, CUT_BOTTOM + OVERLAP / 2)
    rest = box(0, 0, 1024, CUT_TOP + OVERLAP / 2).union(box(0, CUT_BOTTOM - OVERLAP / 2, 1024, 1024))
    return {
        "franja-marco": shift(mark.intersection(mid), SLICE_SHIFT, 0),
        "franja-cara": shift(face.intersection(mid), SLICE_SHIFT, 0),
        "resto-marco": mark.intersection(rest),
        "resto-cara": face.intersection(rest),
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

def slab_group(name, frame, face, alpha, translucency, blur, refraction, shadow, shadow_opacity,
               blend=None):
    """Un cuerpo de cristal con dos tintes (marco y cara): lighting combined, así el borde
    entre marco y cara no lleva bisel; solo lo lleva el contorno de la franja."""
    g = vidrio(name, frame, alpha, translucency, blur, refraction, shadow=shadow,
               shadow_opacity=shadow_opacity, blend=blend)
    g["lighting"] = "combined"
    g["layers"] = [
        {"name": f"{name}-marco", "image-name": f"{name}-marco.svg", "glass": True,
         "fill": {"solid": color(frame, alpha)}},
        {"name": f"{name}-cara", "image-name": f"{name}-cara.svg", "glass": True,
         "fill": {"solid": color(face, alpha)}},
    ]
    return g


def g3(light=False, blend=True):
    """La franja del medio, delante y corrida, se suma como luz a lo que pisa (en claro se
    multiplica); sin sombra, para no ensuciar lo de detrás."""
    if light:
        frame, face, mix = TWITCH_PURPLE, "#FFFFFF", "multiply"
        alpha, rest_glow = 0.78, 0.4
    else:
        frame, face, mix = VIOLET, "#EADCFF", "plus-lighter"
        alpha, rest_glow = 0.72, 0.65
    front = slab_group("franja", frame, face, alpha, 0.55, 0.0, (0.3, 0.1), "none", 0.0,
                       blend=mix if blend else None)
    rest = slab_group("resto", frame, face, alpha, 0.5, 0.1, (0.25, 0.08), "layer-color", rest_glow)
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
    # Pruebas de la ronda 3 (se borran solas al escribir sin ellas)
    "twitch-v1": {"fill": BG_DARK, "groups": g3(blend=False)},
    "twitch-v2": {"fill": BG_DARK, "groups": g2(refraction=(0.22, 0.06))},
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
