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
- g4 «glitch en franjas, con luz»: g3 con los arreglos del juez. Fondo en diagonal más rico; el
  logo entero sin cortes, de cristal morado más transparente, con la franja que pisa la barra más
  clara (el hueco del glitch, a la izquierda); detrás, la cara iluminada (blanco esmerilado)
  corrida 24 px abajo a la derecha, que asoma lila por el marco de la derecha; ventanas de cristal
  claro en los ojos. Delante, la barra de cristal lila casi transparente con brillo de su color,
  esquinas redondeadas y punta derecha en vertical; su cara se corre con ella y brilla (la luz de
  detrás se corre también), y por su marco se ve la franja sin correr: doble imagen del borde de
  la cara y de la muesca. En claro, morado que se multiplica sobre una cara morado profundo.
- g5 «fantasma»: g1 de verdad transparente. Detrás, el logo de cristal morado profundo con la cara
  iluminada, arriba a la derecha; delante, un fantasma del logo en cristal violeta casi incoloro
  (plus-lighter, sin refracción), 40 px abajo a la izquierda: deja ver el logo de detrás y, a la
  izquierda y abajo, una franja de fondo. Los ojos del fantasma son ventanas de cristal claro que
  doblan los ojos de detrás. En claro, el fantasma se multiplica.
Los conceptos c (logo casi opaco, rechazados: «no tiene Liquid Glass») siguen en el historial.
"""
import re

from shapely import affinity
from shapely.geometry import Point, Polygon, box

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
        **g4_pieces(outer, inner, eyes),
        **g5_pieces(outer, inner, eyes),
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


# --- piezas comunes de g4 y g5 ---

BODY_FILLET = 16   # g4/g5: rincones cóncavos del bocadillo (raíz de la cola) con más radio: la
                   # refracción más fuerte no hace astillas en ellos
NOTCH_R = 6        # radio de la punta de la muesca de la cara (sin él, un destello de 1 px)


def base_shapes(outer, inner):
    """Bocadillo entero y cara (con la zona de los ojos, sin huecos), con la punta de la cola y
    la de la muesca redondeadas."""
    body = fillet_concave(round_tip(outer), BODY_FILLET)
    face = round_tip(inner, NOTCH_R, 24)
    return body, face


def capa(name, fill, alpha, glass_=True):
    return {"name": name, "image-name": f"{name}.svg", "glass": glass_,
            "fill": {"solid": color(fill, alpha)}}


def grupo(name, layers, translucency, blur, refraction=None, shadow="neutral", shadow_opacity=0.5,
          blend=None, lighting="individual", specular="automatic"):
    """Grupo de cristal hecho a mano: varias capas, modo de luz y fusión."""
    g = vidrio(name, "#FFFFFF", 1.0, translucency, blur, refraction, shadow=shadow,
               shadow_opacity=shadow_opacity, specular=specular, blend=blend)
    g["lighting"] = lighting
    g["layers"] = layers
    return g


def diagonal(top, bottom):
    """Degradado de arriba a la izquierda a abajo a la derecha (orientation de Icon Composer)."""
    return {"linear-gradient": [color(top), color(bottom)],
            "orientation": {"start": {"x": 0, "y": 0}, "stop": {"x": 1, "y": 1}}}


# --- g4: glitch en franjas, con todo el cristal (g3 con los arreglos del juez y del escéptico) ---

BAND = (548, 712)   # g4: la franja va de 548 (el bisel no llega a los ojos, que acaban en 476) a
                    # 712 (la muesca entera, que acaba en 706, cae dentro: no asoma su punta)
BAR_SHIFT = 36      # px que se corre la barra a la derecha
BAR_R = 12          # radio de las esquinas de la barra (menos la de arriba a la derecha, viva)
BAR_END = 820       # la barra acaba en vertical en el borde derecho del logo: su punta aguda de
                    # 45° (aun redondeada con 24 px) hacía un rizo especular, como un pliegue
LIT_SHIFT = 24      # px que la cara iluminada de detrás se corre abajo a la derecha
NOTCH_CUT = 680     # la muesca de la luz bajo la barra acaba aquí: en 698 el bisel del logo traía su
                    # punta a su borde de abajo (un punto caliente en 510-545, 765)
LIT_LEFT = 244      # g4: la luz bajo la barra llega hasta aquí por la izquierda (si no, el borde de
                    # abajo de la barra salía blanco solo de 394 a 680, como una raya dibujada)
LIT_LEFT_C = 358    # g4c: hasta el borde de la cara (sin hueco blanco bajo la barra: rayitas blancas)
CHAMFER = 513.5     # x + y del chaflán de arriba a la izquierda del bocadillo
HYPOT = 1256.8      # x + y de la hipotenusa de la cola
STREAK = (34, 133)  # g4: raya de luz bajo el chaflán, de 24 a 94 px dentro de él (en x + y)
SLIVER = (23, 79)   # raya de luz bajo la hipotenusa de la cola, de 16 a 56 px dentro de ella
CORNER = 113        # g4c: esquina blanca de la cara de luz, 80 px desde su esquina (en x + y)
INSET = 14          # px que las rayas de luz quedan dentro del borde de su pieza
TAIL_TOP = 776      # g4: la raya de la cola empieza aquí: más arriba, el bisel del borde de arriba del
                    # marco de abajo (712) doblaba su punta en un garabato


def diag_band(c0, c1):
    """Franja entre las rectas x + y = c0 y x + y = c1 (paralela a las diagonales del logo)."""
    return Polygon([(c0, 0), (c1, 0), (0, c1), (0, c0)])


def streak(region, c0, c1, clip=None):
    """Raya de luz diagonal dentro de una pieza (a INSET px de su borde), con las puntas suaves."""
    s = diag_band(c0, c1).intersection(region.buffer(-INSET, join_style="mitre"))
    return soften(s.intersection(clip) if clip is not None else s, 8)


def g4_pieces(outer, inner, eyes):
    """Barra corrida (marco + cara), el logo entero debajo (la franja que pisa la barra va aparte,
    más clara: el hueco del glitch), ventanas en los ojos y la cara iluminada de detrás, corrida
    LIT_SHIFT px. Bajo la barra la luz se corre con la barra (la cara de la franja, muesca incluida)
    y llega a la izquierda hasta LIT_LEFT: por el marco de la barra se ve la franja del logo sin
    correr (el borde de la cara y la muesca, 36 px a la izquierda: la doble imagen del glitch).
    Rayas de luz bajo el chaflán y bajo la cola: el marco y la cola tienen dos tintes y un borde
    que su bisel dobla.
    Junta de la barra con el marco, a la derecha: el marco baja recto hasta 548 (sin el pico de 8 px
    de la diagonal) y la barra y la franja tienen viva la esquina de arriba a la derecha (con radio,
    la silueta hacía una V y el borde de arriba de la barra un gancho)."""
    body, face = base_shapes(outer, inner)
    frame = body.difference(face)
    band = box(0, BAND[0], 1024, BAND[1])
    xr = body.bounds[2]
    raw = shift(body.intersection(band), BAR_SHIFT, 0).intersection(box(0, 0, BAR_END, 1024))
    bar = soften(raw, BAR_R).union(raw.intersection(box(BAR_END - 30, BAND[0], BAR_END, BAND[0] + 20)))
    # la luz se corre a la derecha y abajo, pero arriba llega al borde de la cara: el hueco en L
    # hacía en las esquinas de la cara, bajo su bisel, dos manchas oscuras; queda el de la izquierda
    lit = shift(face, LIT_SHIFT, LIT_SHIFT).union(shift(face, LIT_SHIFT, 0))
    lit = lit.difference(eyes).intersection(box(0, 0, 1024, BAND[0]))
    corner = lit.intersection(diag_band(0, sum(lit.bounds[:2]) + CORNER))
    # luz bajo la barra: la cara de la franja corrida, con la punta de la muesca cortada y redonda
    under = shift(face.intersection(band), BAR_SHIFT, 0).difference(box(0, NOTCH_CUT, 1024, 1024))
    tip = box(0, NOTCH_CUT - 30, 1024, 1024)
    under = under.difference(tip).union(soften(under, 6).intersection(tip))
    fb = face.intersection(box(0, 0, 400, 1024)).bounds[3]  # borde de abajo de la cara (616.7)
    x0 = under.bounds[0] + 1
    return {
        "g4-barra-marco": shift(frame.intersection(band), BAR_SHIFT, 0).intersection(bar),
        "g4-barra-cara": shift(face.intersection(band), BAR_SHIFT, 0).intersection(bar),
        "g4-marco": frame.difference(band).union(box(xr - 30, BAND[0] - 30, xr, BAND[0])),
        # la franja sin correr sigue bajo la punta de la barra que sobresale del logo (2 px dentro
        # de su borde): ahí no queda otro borde paralelo bajo el bisel de la barra (salía una astilla
        # a lo largo de la diagonal y un rizo oscuro arriba a la derecha)
        "g4-marco-franja": frame.intersection(band)
        .union(bar.buffer(-2, join_style="mitre").difference(body))
        .union(box(xr - 30, BAND[0], xr - 2, BAND[0] + 20)),
        "g4-cara": face,
        "g4-ventanas": soften(grow(eyes, PANE), 4),
        "g4-luz": lit,
        "g4-luz-barra": under.union(box(LIT_LEFT, BAND[0], x0, fb)),
        "g4c-luz-barra": under.union(box(LIT_LEFT_C, BAND[0], x0, fb)),
        "g4-luz-chaflan": streak(frame, CHAMFER + STREAK[0], CHAMFER + STREAK[1]),
        "g4-luz-cola": streak(body, HYPOT - SLIVER[1], HYPOT - SLIVER[0], box(0, TAIL_TOP, 1024, 1024)),
        "g4c-luz": lit.difference(corner),
        "g4c-luz-esquina": corner,
    }


def g4(light=False):
    """Delante la barra de cristal violeta casi transparente (en claro, morado que se multiplica),
    con brillo del color de la capa; luego las ventanas de los ojos, de cristal morado; luego el logo
    entero de cristal morado transparente (cara casi incolora) con luz individual, así la cara tiene
    su propio bisel contra el marco y dobla el borde de la luz de detrás; detrás, las luces.
    Con la cara en el grupo de las ventanas (y luz combinada en el logo), su bisel traía el hueco
    de la luz a su borde de arriba en rayitas.
    Refracción del logo 0.26/0.08: a 0.35/0.15 su borde de arriba traía la cara iluminada (a 75 px)
    y los huecos de los ojos (a 141 px) en rayitas. Barra a 0.3/0.04: a 0.4/0.1 y 0.35/0.08 su
    punta derecha se doblaba en una mancha oscura y un rizo, y a 0.3/0.06 aún hacía un gancho."""
    if light:
        bar_c, bar_a, bar_mix, bar_glow = TWITCH_PURPLE, 0.5, "multiply", 0.45
        frame_c, frame_a, band_a, glow = TWITCH_PURPLE, 0.7, 0.42, 0.4
        bar_face, bar_face_a, win_c, win_a = LAVENDER, 0.12, "#FFFFFF", 0.14
        # cara de luz morado profundo (blanco sobre blanco no se vería) con la esquina blanca: la cara
        # tiene dos tintes; rayas de morado profundo bajo el chaflán y la cola
        lights = [capa("g4c-luz-esquina", "#FFFFFF", 0.8), capa("g4c-luz", DEEP, 0.6),
                  capa("g4c-luz-barra", DEEP, 0.6), capa("g4-luz-chaflan", DEEP, 0.6),
                  capa("g4-luz-cola", DEEP, 0.6)]
    else:
        bar_c, bar_a, bar_mix, bar_glow = VIOLET, 0.5, "plus-lighter", 0.5
        frame_c, frame_a, band_a, glow = TWITCH_PURPLE, 0.38, 0.3, 0.65
        bar_face, bar_face_a, win_c, win_a = LAVENDER, 0.18, TWITCH_PURPLE, 0.22
        # la luz bajo la barra a 0.8: a 0.55 la cara de la barra salía gris (172,165,186)
        lights = [capa("g4-luz", "#FFFFFF", 0.9), capa("g4-luz-barra", "#FFFFFF", 0.8),
                  capa("g4-luz-chaflan", "#FFFFFF", 0.7), capa("g4-luz-cola", "#FFFFFF", 0.6)]
    bar = grupo("barra", [capa("g4-barra-marco", bar_c, bar_a), capa("g4-barra-cara", bar_face, bar_face_a)],
                0.8, 0.0, (0.3, 0.04), "layer-color", bar_glow, blend=bar_mix, lighting="combined")
    face = capa("g4-cara", LAVENDER, 0.1)
    # sin sombra en las ventanas: hacía un bisel gris alrededor de los ojos
    windows = grupo("ventanas", [capa("g4-ventanas", win_c, win_a)],
                    0.9, 0.0, (0.25, 0.08), "neutral", 0.0)
    logo = grupo("logo", [capa("g4-marco", frame_c, frame_a), capa("g4-marco-franja", frame_c, band_a),
                          face], 0.7, 0.05, (0.26, 0.08), "layer-color", glow)
    backing = grupo("luz", lights, 0.3, 0.5, None, "neutral", 0.3)
    return [bar, windows, logo, backing]


# --- g5: glitch doble de verdad transparente (g1 con los arreglos del juez y del escéptico) ---

GHOST = 32       # px: cada copia se corre 32 px en diagonal (64 px entre las dos): la franja de fondo
                 # que deja ver el fantasma es más ancha que lo que alcanza su bisel (a 40 px la
                 # plegaba en una varilla oscura)


def g5_pieces(outer, inner, eyes, g=GHOST):
    """Delante, un fantasma de cristal del logo (cuerpo entero: marco y cara a la vez, sin hueco,
    así no hay halo alrededor de la cara), abajo a la izquierda; ventanas en sus ojos. Detrás, el
    logo «de verdad», arriba a la derecha: un bocadillo morado profundo con la cara hueca solo donde
    cae bajo la cara del fantasma (fuera, la franja de luz de arriba y la de la derecha hacían cuatro
    marcos anidados) y los ojos justo bajo las ventanas (un solo par de ojos, que las ventanas
    agrandan). La cara del fantasma entera es la luz: por ella se ve la cara de detrás, blanca, y el
    marco de detrás, morado encendido. Bajo la banda de abajo y la cola del fantasma, la copia de
    detrás llega a sus bordes: la cola se ve morada en la tecla.
    Las diagonales del logo caen sobre sí mismas al correrlo en diagonal; el borde izquierdo de
    detrás cruza el chaflán del fantasma y su borde de abajo: ahí su bisel lo dobla."""
    body, face = base_shapes(outer, inner)
    front, front_face = shift(body, -g, g), shift(face, -g, g)
    back, back_face = shift(body, g, -g), shift(face, g, -g)
    eyes_f = shift(eyes, -g, g)
    # bajo la banda de abajo y la cola del fantasma, la copia de detrás se rellena hasta sus bordes
    # (como en g1): con su propia cola recortada 16 px dentro, el bisel estrecho de la cola la
    # doblaba en una gota, y una raya de luz debajo salía como una mancha blanca
    back = back.union(front.intersection(box(back.bounds[0], 700, 1024, 1024)))
    hole = back_face.intersection(front_face)
    return {
        "g5-fantasma-marco": front.difference(front_face),
        "g5-fantasma-cara": front_face,
        "g5-ventanas": shift(soften(grow(eyes, PANE), 4), -g, g),
        "g5-detras-marco": back.difference(hole.difference(eyes_f)),
        "g5-detras-cara": hole.difference(eyes_f),
        "g5-luz": front_face.difference(eyes_f),
    }


def g5(light=False):
    """Fantasma de cristal violeta casi incoloro que se suma como luz (plus-lighter; en claro,
    morado que se multiplica): deja ver la copia de detrás y el fondo en dos tintes. Detrás, el
    logo de cristal morado profundo con brillo de su color, y la luz debajo.
    Refracción del fantasma 0.2/0.04: con 40 px entre las copias, a 0.3/0.1, 0.2/0.06 y 0.12/0.04
    plegaba la franja de fondo en una varilla oscura; con 64 px la franja es más ancha que su bisel.
    Ventanas a 0.3/0.06: a 0.3/0.1 sus esquinas traían motas moradas de los ojos de detrás."""
    if light:
        ghost_c, ghost_a, mix, ghost_glow = TWITCH_PURPLE, 0.75, "multiply", 0.2
        back_c, back_a, face_a, glow = DEEP, 0.85, 0.12, 0.45
    else:
        # violeta (no lila): sobre el negro el lila salía gris (la cola, 29,23,41)
        ghost_c, ghost_a, mix, ghost_glow = VIOLET, 0.5, "plus-lighter", 0.5
        back_c, back_a, face_a, glow = DEEP, 0.8, 0.15, 0.75
    ghost = grupo("fantasma", [capa("g5-fantasma-marco", ghost_c, ghost_a),
                               capa("g5-fantasma-cara", ghost_c, 0.06)],
                  0.8, 0.0, (0.2, 0.04), "layer-color", ghost_glow, blend=mix, lighting="combined")
    windows = grupo("ventanas", [capa("g5-ventanas", "#FFFFFF", 0.14)], 0.9, 0.0, (0.3, 0.06),
                    "neutral", 0.0)
    back = grupo("detras", [capa("g5-detras-marco", back_c, back_a),
                            capa("g5-detras-cara", LAVENDER, face_a)],
                 0.45, 0.2, None, "layer-color", glow, lighting="combined")
    backing = grupo("luz", [capa("g5-luz", "#FFFFFF", 0.9)], 0.3, 0.5, None, "neutral", 0.3)
    return [ghost, windows, back, backing]


# Negro de Twitch con un poco de morado arriba: el cristal tiene un degradado que doblar
BG_DARK = {"linear-gradient": [color("#1A1426"), color(TWITCH_DARK)]}
BG_LIGHT = {"linear-gradient": [color("#FFFFFF"), color("#F1EAFF")]}
# g4/g5: degradado en diagonal más rico (morado arriba a la izquierda), para que el cristal
# tenga algo que teñir y doblar
BG4_DARK = diagonal("#2E1858", "#100A1C")  # abajo, negro con algo de morado: sobre #0B0A10 el
                                           # cristal de abajo salía apagado (66,42,105)
BG4_LIGHT = diagonal("#F3EDFF", "#E4D6FF")  # arriba lila muy claro: en blanco puro la parte de
                                            # arriba del icono se veía lavada

APPROVED = {}

CONCEPTS = {
    "twitch-g1": {"fill": BG_DARK, "groups": g1()},
    "twitch-g1c": {"fill": BG_LIGHT, "groups": g1(light=True)},
    "twitch-g2": {"fill": BG_DARK, "groups": g2()},
    "twitch-g2c": {"fill": BG_LIGHT, "groups": g2(light=True)},
    "twitch-g3": {"fill": BG_DARK, "groups": g3()},
    "twitch-g3c": {"fill": BG_LIGHT, "groups": g3(light=True)},
    "twitch-g4": {"fill": BG4_DARK, "groups": g4()},
    "twitch-g4c": {"fill": BG4_LIGHT, "groups": g4(light=True)},
    "twitch-g5": {"fill": BG4_DARK, "groups": g5()},
    "twitch-g5c": {"fill": BG4_LIGHT, "groups": g5(light=True)},
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
