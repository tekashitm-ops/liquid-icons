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
GLITCH = 16        # px: cada copia de g1 se desplaza 16 px en diagonal (32 px entre las dos)
BACK_FILLET = 12   # px: rincones cóncavos de la copia de detrás de g1
PANE = 8           # px que la ventana de cada ojo de g2 pisa la losa alrededor del hueco
LENS_OVER = 20     # px que la lente de g3 pisa el marco (su bisel dobla el borde del marco)
FACE_UNDER = 16    # px que la cara blanca de g3 sigue bajo el marco de cristal


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
        # g3: lente sobre la cara (pisa el marco), el glitch y la cara blanca que sigue bajo él
        "glitch": mark,
        "lente": fillet_concave(grow(inner, LENS_OVER), 16),
        "cara-fondo": grow(inner, FACE_UNDER),
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

def g1(light=False, blend=None, alpha=None):
    """Delante el glitch de cristal claro sin esmerilar, que se suma como luz a lo de detrás
    (plus-lighter; en claro, multiply: se mezcla como dos cristales tintados); detrás el
    bocadillo de cristal de color, que es lo que se ve por la cara hueca y lo que el marco de
    delante dobla. Sin sombra delante: oscurecía la copia de detrás (gris sucio)."""
    if light:
        front = vidrio("glitch-delante", TWITCH_PURPLE, alpha or 0.62, 0.6, 0.0, (0.3, 0.1),
                       shadow="none", shadow_opacity=0.0, blend=blend or "multiply")
        back = vidrio("glitch-detras", LAVENDER, 0.75, 0.45, 0.15, (0.3, 0.1),
                      shadow="layer-color", shadow_opacity=0.45)
    else:
        front = vidrio("glitch-delante", LILAC, alpha or 0.5, 0.65, 0.0, (0.3, 0.1),
                       shadow="none", shadow_opacity=0.0, blend=blend or "plus-lighter")
        back = vidrio("glitch-detras", DEEP, 0.85, 0.4, 0.15, (0.3, 0.1),
                      shadow="layer-color", shadow_opacity=0.75)
    return [front, back]


# --- g2: cara de luz ---

def g2(light=False, refraction=(0.3, 0.1)):
    """Losa violeta translúcida delante de la cara esmerilada; ventanas claras en los ojos.
    Refracción de la losa 0.3/0.1: a 0.35/0.12 su borde exterior traía los ojos (a 141 px)."""
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


# --- g3: lente ---

def g3(light=False, refraction=(0.3, 0.1)):
    """Lente de cristal transparente sobre la cara: su bisel dobla el borde interior del marco
    morado. El marco es cristal de color: por dentro deja ver la cara blanca que sigue debajo
    (morado claro) y por fuera el fondo (morado oscuro)."""
    if light:
        lens = vidrio("lente", LAVENDER, 0.2, 0.85, 0.0, refraction, shadow_opacity=0.3)
        mark = vidrio("glitch", TWITCH_PURPLE, 0.75, 0.5, 0.05, (0.25, 0.06),
                      shadow="layer-color", shadow_opacity=0.45)
    else:
        lens = vidrio("lente", "#FFFFFF", 0.14, 0.88, 0.0, refraction, shadow_opacity=0.3)
        mark = vidrio("glitch", VIOLET, 0.72, 0.55, 0.05, (0.25, 0.06),
                      shadow="layer-color", shadow_opacity=0.7)
    face = vidrio("cara-fondo", "#FFFFFF", 0.95, 0.3, 0.5, None, shadow_opacity=0.3)
    return [lens, mark, face]


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
    # Pruebas de la ronda 2 (se borran solas al escribir sin ellas)
    "twitch-v1": {"fill": BG_DARK, "groups": g1(blend="normal", alpha=0.42)},
    "twitch-v2": {"fill": BG_DARK, "groups": g3(refraction=(0.4, 0.15))},
    "twitch-v3": {"fill": BG_LIGHT, "groups": g1(light=True, blend="normal")},
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
