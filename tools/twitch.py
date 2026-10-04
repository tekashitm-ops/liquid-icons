"""Twitch: logo oficial (el «glitch») ajustado al icono de iOS y montaje de los .icon.

Trazado: brands/twitch.svg (recursos de marca, brand.twitch.tv vía simple-icons), sin
deformar: solo escala uniforme y posición. Ajustado contra el icono de la App Store
(«Twitch: Live Streaming», id 460177396, 1024 px) con IoU 0.992 en la silueta del bocadillo
y 0.978 en la cara blanca. Ese icono dibuja los ojos 13 px más abajo (y el izquierdo 13 px
más a la derecha) que el logo de marca, por eso los ojos solo coinciden con IoU 0.67: se
conserva el dibujo de marca.
Piezas: la silueta, el marco (silueta menos cara), la cara blanca, los ojos y el glitch
monocromo oficial (marco + ojos). Cada concepto las apila en grupos de cristal distintos
para que la pieza de delante refracte el borde de la de detrás donde se pisan:
c1 fiel al icono de iOS, c2 la cara como ventana de cristal claro (lente de Vista Previa),
c3 el glitch de cristal morado sobre la cara blanca (cristal de color de Fotos).

Cambios en c1/c1c tras el panel (eligió c1) y el escéptico (render de CI anterior):
- Costuras: c1c tenía dos líneas rectas de 1 px en el halo de la sombra, a ~9 px de la silueta
  (x=196, y 338-794 y x=827, y 214-572, +5 R / +9 G), y una más débil a 8 px de la cara
  (x=350); en c1, x=192 y x=831 a +1-3 niveles. Son el borde de la caja a la que ictool recorta
  la sombra de cada capa. Ahora todas las capas van a lienzo completo (write_icon con
  full_bounds=True: cuatro puntos casi transparentes en las esquinas) y, por si la costura
  tiene otra causa, la silueta de c1c pasa de sombra de color de capa (0.5) a neutra (0.35).
- Punta de la cola: el bisel concentraba el brillo en un destello de 1 px justo bajo la punta
  de 45° (359,898). Se redondea solo esa punta con radio TIP_R = 3 px (recorta 4.8 px de la
  punta; IoU con el trazado de marca 0.99997). La muesca de la cara no se toca.
- Más cristal en c1: el bocadillo negro baja de alfa 1.0 a 0.9 y su translucidez de 0.25 a
  0.35, así se ve algo del morado a través del marco (negro ahumado: estimado 4.2:1 contra el
  fondo arriba y 3.8:1 en la cola, antes 4.3:1). La cara sigue a alfa 1.0 y refracción
  0.3/0.1 (~19:1 contra el marco; más profunda, su borde superior traería el morado de fuera:
  encima solo hay 51 px de marco). En c1c el morado se queda a alfa 0.95 / translucidez 0.3:
  más transparente bajaría de ~3.5:1 abajo, donde el cristal se aclara.
- c4/c4c (alternativa para comparar): igual que c1/c1c salvo UN parámetro, la refracción
  del bocadillo, de 0.3/0.1 a 0.4/0.15 (el máximo de la regla del proyecto): bisel más ancho y
  brillante. El bocadillo no tiene trazos finos (lo más estrecho es la cola, 128 px, y su
  punta ya va redondeada) y detrás solo hay el fondo liso. Si sale limpio, sustituye a c1.
"""
import re

from shapely.geometry import Point

from brand import place, subpath_shapes
from liquid import ROOT, auto_gradient, clean, color, glass, write_icon

D = re.search(r' d="([^"]+)"', (ROOT / "brands" / "twitch.svg").read_text(encoding="utf-8")).group(1)
FIT = (29.899, 29.899, 153.177, 181.0)  # escala x, escala y, desplazamiento x, y (lienzo de 1024)

TWITCH_PURPLE = "#9146FF"   # color de marca
TWITCH_BG = "#9246FF"       # fondo del icono oficial de iOS (medido, plano)
TWITCH_BLACK = "#000000"    # marco y ojos del icono oficial
TWITCH_DARK = "#0E0E10"     # fondo del tema oscuro de Twitch

WINDOW_OVER = 6    # px que la ventana de cristal pisa el marco (sin rendija entre piezas)
FACE_UNDER = 10    # px que la cara blanca se mete bajo el marco de cristal
FILLET = 12        # px: redondea las esquinas cóncavas de la ventana (la refracción no se pliega)
MITRE = 1.5        # las esquinas rectas se quedan vivas; la punta de 45° de la cola se chaflana
TIP_R = 3          # px: radio con el que se redondea solo la punta de 45° de la cola (c1)
TIP_ZONE = 30      # px alrededor de la punta en los que se aplica (el resto queda intacto)

BEVEL = (0.3, 0.1)        # refracción del bocadillo en c1/c1c (bisel que mira ~50 px)
BEVEL_DEEP = (0.4, 0.15)  # c4/c4c: bisel más ancho, tope de la regla (mira ~100 px)


def grow(geom, px):
    """Agranda una pieza sin redondear sus esquinas rectas."""
    return geom.buffer(px, join_style="mitre", mitre_limit=MITRE)


def fillet_concave(geom, r):
    """Cierre morfológico: rellena con un radio r solo las esquinas cóncavas."""
    return geom.buffer(r, quad_segs=32).buffer(-r, quad_segs=32)


def round_tip(geom, r=TIP_R, zone=TIP_ZONE):
    """Redondea con radio r solo la punta más baja (la de 45° de la cola): apertura
    morfológica dentro de un círculo alrededor de la punta. Sin ella el bisel junta su brillo
    en un destello de 1 px en el vértice; las demás esquinas siguen vivas."""
    tip = max(geom.exterior.coords, key=lambda p: p[1])
    area = Point(tip).buffer(zone, quad_segs=32)
    opened = geom.buffer(-r, quad_segs=16).buffer(r, quad_segs=16)
    return geom.difference(area).union(opened.intersection(area))


def pieces():
    eye_l, eye_r, outer, inner = (place(s, *FIT) for s in subpath_shapes(D))
    eyes = eye_l.union(eye_r)
    frame = outer.difference(inner)
    return {
        "glitch": round_tip(outer),            # silueta completa del bocadillo (punta redondeada)
        "cara": inner.difference(eyes),        # cara blanca con los ojos huecos
        "marco": frame,
        "ojos": eyes,
        "marca": frame.union(eyes),            # el glitch monocromo oficial
        # Ventana de cristal en el sitio de la cara, 6 px sobre el marco: su bisel dobla el
        # borde negro del marco. Queda a 45 px del borde exterior del marco (la refracción
        # 0.3/0.08 mira unos 40 px), así no trae trozos de morado de fuera.
        "ventana": fillet_concave(grow(inner, WINDOW_OVER), FILLET),
        # Cara blanca que sigue 10 px bajo el marco de cristal: el marco deja verla y la dobla.
        # Queda a 40 px del borde exterior del marco (la refracción 0.3/0.07 mira unos 35 px)
        "cara-fondo": grow(inner, FACE_UNDER),
    }


# --- Concepto 1 (fiel): cara blanca de cristal sobre el bocadillo negro, como el oficial ---

def face_white():
    """La cara blanca, delante; por sus ojos huecos se ve el negro de detrás."""
    return glass("cara", alpha=1.0, translucency=0.2, blur=0.25, refraction=(0.3, 0.1))


def silhouette(fill=TWITCH_BLACK, light=False, refraction=BEVEL):
    """El bocadillo entero detrás de la cara (sin rendijas entre negro y blanco).
    Sombra neutra en los dos: la de color de capa dejaba costuras rectas en el halo de c1c.
    En oscuro, cristal negro ahumado (alfa 0.9): deja ver un poco del morado de detrás."""
    if light:
        return glass("glitch", fill=fill, alpha=0.95, translucency=0.3, blur=0.3,
                     refraction=refraction, shadow_opacity=0.35)
    return glass("glitch", fill=fill, alpha=0.9, translucency=0.35, blur=0.3,
                 refraction=refraction, shadow_opacity=0.45)


# --- Concepto 2 (ventana, como la lente de Vista Previa): la cara es un cristal transparente ---

def eyes_front(fill=TWITCH_BLACK, light=False):
    """Ojos delante de la ventana, nítidos (nada que doblar detrás: la ventana es lisa)."""
    if light:
        return glass("ojos", fill=fill, alpha=0.95, translucency=0.3, blur=0.2,
                     refraction=(0.2, 0.06), shadow="layer-color")
    return glass("ojos", fill=fill, alpha=1.0, translucency=0.2, blur=0.2, refraction=(0.2, 0.06))


def window(light=False):
    """Ventana de cristal claro, sin esmerilar: deja ver el fondo y su borde dobla el marco.
    En oscuro, un velo blanco sobre el morado (lila); en claro, un velo morado sobre el blanco."""
    if light:
        return glass("ventana", fill=TWITCH_PURPLE, alpha=0.15, translucency=0.85, blur=0.0,
                     refraction=(0.3, 0.08), shadow_opacity=0.3, specular="inside")
    return glass("ventana", alpha=0.4, translucency=0.8, blur=0.0,
                 refraction=(0.3, 0.08), shadow_opacity=0.3, specular="inside")


def frame_back(fill=TWITCH_BLACK, light=False):
    if light:
        return glass("marco", fill=fill, alpha=0.95, translucency=0.3, blur=0.3,
                     refraction=(0.3, 0.1), shadow="layer-color")
    return glass("marco", fill=fill, alpha=1.0, translucency=0.25, blur=0.3,
                 refraction=(0.3, 0.1), shadow_opacity=0.45)


# --- Concepto 3 (cristal de color, como los pétalos de Fotos): el glitch es cristal morado ---

def mark_purple(light=False):
    """Glitch oficial de cristal morado delante de la cara blanca: donde la pisa (el borde
    interior del marco y los ojos) se ve más claro, y su bisel interior dobla ese borde.
    Sombra cromática: en el fondo oscuro deja un halo morado."""
    return glass("marca", fill=TWITCH_PURPLE, alpha=0.92 if light else 1.0, translucency=0.35,
                 blur=0.0, refraction=(0.3, 0.07), shadow="layer-color",
                 shadow_opacity=0.5 if light else 0.6)


def face_under():
    return glass("cara-fondo", alpha=1.0, translucency=0.15, blur=0.3, refraction=(0.2, 0.08),
                 shadow_opacity=0.4)


BG = {"solid": color(TWITCH_BG)}          # el morado plano del icono oficial
BG_AUTO = auto_gradient(TWITCH_PURPLE)    # el mismo morado con el degradado automático de Apple
BG_DARK = {"solid": color(TWITCH_DARK)}   # negro de Twitch (system-dark es más claro arriba: < 3:1)

APPROVED = {}

CONCEPTS = {
    # c1 (fiel al icono de iOS): fondo morado, bocadillo negro y cara blanca de cristal
    "twitch-c1": {"fill": BG, "groups": [face_white(), silhouette()]},
    # su pareja clara: fondo claro de Apple y bocadillo de cristal morado
    "twitch-c1c": {"fill": "system-light", "groups": [face_white(), silhouette(TWITCH_PURPLE, light=True)]},
    # c4 (alternativa de c1): solo cambia la refracción del bocadillo, 0.3/0.1 -> 0.4/0.15
    "twitch-c4": {"fill": BG, "groups": [face_white(), silhouette(refraction=BEVEL_DEEP)]},
    "twitch-c4c": {"fill": "system-light", "groups": [
        face_white(), silhouette(TWITCH_PURPLE, light=True, refraction=BEVEL_DEEP),
    ]},
    # c2 (ventana): la cara es cristal transparente; se ve el morado detrás y su borde
    # dobla el del marco negro; los ojos flotan delante
    "twitch-c2": {"fill": BG_AUTO, "groups": [eyes_front(), window(), frame_back()]},
    "twitch-c2c": {"fill": "system-light", "groups": [
        eyes_front(TWITCH_PURPLE, light=True), window(light=True), frame_back(TWITCH_PURPLE, light=True),
    ]},
    # c3 (cristal morado): el glitch de cristal morado sobre el negro de Twitch, delante de
    # la cara blanca, que sigue bajo el marco; el cristal cambia de tono según lo que pisa
    # (descartado el cristal ahumado sobre morado: en plano se veía apagado)
    "twitch-c3": {"fill": BG_DARK, "groups": [mark_purple(), face_under()]},
    "twitch-c3c": {"fill": "system-light", "groups": [mark_purple(light=True), face_under()]},
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
