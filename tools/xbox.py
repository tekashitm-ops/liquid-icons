"""Xbox: logo oficial (la esfera con la X tallada) ajustado al icono de iOS y montaje de los .icon.

Trazado: brands/xbox.svg (recursos de marca, simple-icons 16.34.0): cuatro piezas (la de abajo,
derecha, izquierda y el arco de arriba). Ajustado contra el icono de la App Store (id 736179781,
versión 2609.3.1, 1024 px). Con escala uniforme y posición: IoU 0.965. El icono de iOS dibuja la
X algo más estrecha: el arco y las dos piezas laterales son 7-10 px más gruesos en los bordes que
miran hacia abajo y hacia dentro. Se modela con un barrido por pieza (suma de Minkowski con un
vector corto, ajustado por máximo IoU) recortado al círculo de la esfera, y las puntas
redondeadas 4 px como en el icono oficial: IoU 0.994. Fondo oficial #1A1B1E; verde #107C10;
brillo lima #9BF00B / #D2EC14.

Conceptos g (Liquid Glass al máximo: todo el logo es cristal de color que deja ver lo de detrás,
y siempre hay algo detrás que el bisel dobla):
- g1 canica: una esfera de cristal transparente (tinte lima levísimo) del tamaño de la esfera,
  delante de todo; su borde grueso dobla las piezas y la X junto al borde. Dentro, las piezas de
  cristal verde esmerilado encendidas por la luz lima de detrás (más fuerte abajo) sobre un
  corazón de cristal verde hondo: la canica entera se lee como una bola de cristal verde.
- g2 doble cristal: las piezas de cristal verde transparente delante de una copia de cristal lima
  esmerilado 18 px más abajo; la lima se ve a través del verde, asoma como canto de luz al pie
  de cada pieza (también en las puntas) y el bisel de delante dobla su borde.
- g3 X de cristal: una X gruesa de cristal transparente (tinte lima levísimo) delante de las
  piezas de cristal verde esmerilado encendidas y de una esfera de cristal verde hondo; la X pisa
  26 px de cada pieza y su bisel dobla esos bordes.
Las parejas claras (sufijo c) son la misma idea sobre fondo claro: verdes más hondos detrás del
cristal en vez de luz lima (sobre blanco la lima no se ve), y en g3 una esfera menta claro.
- g4 canica con luz de abajo: g1 con los arreglos del juez. Logo a 0.85 dentro de la misma
  canica (anillo de cristal de 25 px), canica más visible (lima α0.12, brillo por dentro) y de
  borde estrecho y fuerte (0.5, 0.07); piezas de cristal verde transparente (α0.38, sin
  esmerilar) delante de su copia lima de cristal esmerilado bajada y recortada a cada pieza, en
  vez de la placa de luz plana; corazón de cristal verde hondo (α0.65).
- g5 canica con X de luz: g4 con el hueco de la X de cristal esmerilado blanco lima, que brilla
  (la bola de Xbox 360), en el mismo grupo que el corazón (4 grupos).
Lo aprendido en g4/g5 (sobre los píxeles de ictool):
- La refracción es una cúpula: el bisel amplía el interior de la pieza hasta su borde, y su
  alcance crece con la pieza. Una luz de detrás con el borde paralelo al de la pieza y más cerca
  de ~0.3 radios inscritos desaparece (la franja de 20 px de la copia de g2 se borraba en la pieza
  de abajo). El borde de la luz solo se ve doblado donde cruza el de la pieza en ángulo.
- La canica entera amplía: con (0.55, 0.25) o (0.38, 0.13) llenaba el anillo con logo estirado,
  hinchaba el arco en un tulipán y rizaba los pies; depth 0.07 deja el efecto en el borde.
- Una lente sobre el cruce de la X amplía el hueco oscuro: disco oscuro con cuatro motas (cara).
- Un corazón con canto oscuro también abajo dibuja en la pieza de abajo una U oscura (sonrisa).
"""
import re

import numpy as np
from shapely import affinity
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union

from brand import place, subpath_shapes
from liquid import ROOT, WHITE, clean, color, write_icon

D = re.search(r' d="([^"]+)"', (ROOT / "brands" / "xbox.svg").read_text(encoding="utf-8")).group(1)
FIT = (31.968, 31.968, 128.25, 128.5)  # escala x, escala y, desplazamiento x, y (lienzo de 1024)
NAMES = ("abajo", "derecha", "izquierda", "arco")  # orden de los subtrazados del SVG
SWEEP = {"derecha": (-5.25, 5.0), "izquierda": (5.25, 5.0), "arco": (0.0, 10.5)}  # px, simétrico
TIP_ROUND = 4.0   # px: puntas romas, como en el icono oficial
CENTER = (12 * FIT[0] + FIT[2], 12 * FIT[1] + FIT[3])  # centro de la esfera (511.9, 512.1)
RADIUS = 12 * FIT[0]                                   # radio de la esfera (383.6)
RES = 256

XBOX_BG = "#1A1B1E"      # fondo del icono oficial de iOS (medido)
XBOX_GREEN = "#107C10"   # verde de marca de Xbox
XBOX_LIME = "#9BF00B"    # lima del brillo del icono de iOS
XBOX_GLOW = "#D2EC14"    # lima amarillo del pie de la pieza de abajo del icono de iOS

# g1: la canica. El logo algo más pequeño: la esfera de cristal refracta hondo y su bisel
# tiene que quedar dentro del lienzo con margen.
MARBLE_SCALE = 0.9   # esfera de 345 px de radio
MARBLE_RIM = 6       # px que la canica sobresale de la esfera: la canica ES la esfera
# luz de dentro de la canica: un círculo bajo (el icono de iOS brilla sobre todo abajo) recortado
# a las piezas; el cristal esmerilado de las piezas suaviza su borde
GLOW_CENTER = (0.0, 0.5)  # desplazamiento del centro, en radios de la esfera
GLOW_RADIUS = 0.85        # en radios de la esfera
# g2: la copia lima de detrás, desplazada hacia abajo (la luz de iOS viene de arriba)
BACK_SHIFT = (0.0, 18.0)
# g3: la X gruesa: el hueco entre las piezas engordado; pisa cada pieza X_GROW px
X_GROW = 26
X_FILLET = 16      # px: redondea las esquinas cóncavas (si no, la refracción se arruga)
X_END_ROUND = 30   # px: extremos redondos
X_INSET = 70       # px: los brazos de abajo acaban dentro de la esfera, donde aún son anchos. Si
                   # llegan al borde (o a 40 px), su bisel recoge el fondo gris de fuera: cuñas grises
X_CROSS = (CENTER[0], 345.0)  # cruce de la X (entre la V del arco, las piezas laterales y la de abajo)
X_TOP_REACH = 185  # px desde el cruce: los brazos de arriba acaban de frente al brazo y a 46 px
                   # del borde de la esfera. Con el corte circular de abajo, el corte cruzaba en
                   # diagonal el borde de la pieza lateral y el bisel traía un triángulo suelto de
                   # ese borde dentro de la X junto a cada extremo
# g4/g5: la canica de g1 con los arreglos del juez. Logo más pequeño dentro de la misma canica
# (r 351): queda un anillo de cristal de 37 px. Con 25 px el bisel de la canica reflejaba las
# puntas de las laterales (motas en el anillo) y dejaba un canto punteado dentro de su borde
G4_SCALE = 0.82        # esfera del logo de 315 px de radio
G4_TIP = {"abajo": 30, "izquierda": 16, "derecha": 16}  # px (el arco 8): puntas romas. En la punta
                       # de abajo el bisel dejaba una gota lima y luego dos orejas (cara de gato)
NUCLEO4_R = 351        # el fondo y el líquido llenan la canica hasta su borde: el bisel de los pies
                       # ve verde y no el fondo oscuro de fuera (manchas oscuras en los pies). Con 345
                       # el canto del líquido dejaba otra raya concéntrica junto al de la canica
# La luz de dentro es un líquido lima que llena la canica hasta LEVEL_Y, recortado a las piezas (el
# hueco de la X sigue hondo). Es una forma propia: su borde recto cruza en ángulo las laterales y
# los flancos de la de abajo, y el bisel de cada pieza lo dobla. La copia de cada pieza recortada a
# sí misma (rondas 1-6) no cruzaba ningún canto: se leía como pieza pintada en dos tonos.
LEVEL_Y = 520
LEVEL_FILLET = 10      # px: esquinas apenas redondas donde el nivel corta el canto (sin puntas
                       # sueltas). Con 24 el nivel se curvaba paralelo al canto antes de llegar:
                       # ya no se veía cruzar
# El arco queda por encima del líquido: le sube un haz de luz desde el centro de la esfera (una cuña
# radial), cuyos bordes cortan el arco casi de frente. Un corte horizontal iría paralelo a sus
# cantos y el bisel lo borraría
BEAM_ANGLE = 22        # grados: media apertura de la cuña
X_GLASS_GROW = 4       # g4/g5: la X de cristal pisa 4 px las piezas


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


def x_thick(logo):
    """La X gruesa: el hueco entre las piezas, engordado X_GROW px y con las esquinas redondeadas.

    Brazos de abajo: cortados a X_INSET px del borde de la esfera; de arriba: a X_TOP_REACH px
    del cruce (corte de frente al brazo).
    """
    gap = largest(disk(RADIUS).difference(logo).buffer(-1.5).buffer(1.5))
    x = gap.buffer(X_GROW, quad_segs=64)
    x = x.buffer(X_FILLET, quad_segs=32).buffer(-X_FILLET, quad_segs=32)
    top = disk(X_TOP_REACH, X_CROSS).intersection(box(0, 0, 1024, X_CROSS[1]))
    bottom = disk(RADIUS - X_INSET).intersection(box(0, X_CROSS[1], 1024, 1024))
    x = x.intersection(unary_union([top, bottom]))
    return x.buffer(-X_END_ROUND, quad_segs=32).buffer(X_END_ROUND, quad_segs=32)


def glow(logo, r):
    """La luz lima: un círculo bajo recortado a las piezas (r: radio de su esfera)."""
    c = (CENTER[0] + GLOW_CENTER[0] * r, CENTER[1] + GLOW_CENTER[1] * r)
    return logo.intersection(disk(GLOW_RADIUS * r, c))


def tidy(geom, r=8, min_area=4000):
    """Abre r px (sin astillas ni colas finas) y quita las islas pequeñas (motas en la tecla)."""
    g = geom.buffer(-r, quad_segs=32).buffer(r, quad_segs=32)
    return unary_union([q for q in getattr(g, "geoms", [g]) if q.area > min_area])


def liquid(parts, clip=False, level=LEVEL_Y):
    """g4: el líquido lima bajo LEVEL_Y y el haz de luz del arco.

    Sin recortar (clip=False) llena la canica entera bajo el nivel: se ve a través de las piezas,
    de la X de cristal y del anillo de la canica. clip=True: solo detrás de las piezas.
    """
    logo = unary_union(list(parts.values()))
    region = logo if clip else disk(NUCLEO4_R)
    f = LEVEL_FILLET
    low = region.intersection(box(0, level, 1024, 1024))
    # redondear solo junto al nivel: abrirlo todo cortaba los pies finos de las laterales
    low = unary_union([low.buffer(-f, quad_segs=32).buffer(f, quad_segs=32),
                       region.intersection(box(0, level + 3 * f, 1024, 1024))])
    t = np.tan(np.radians(BEAM_ANGLE))
    cx, cy = CENTER
    wedge = Polygon([(cx, cy), (cx - t * cy, 0), (cx + t * cy, 0)])
    arc = parts["arco"].intersection(wedge).buffer(-12, quad_segs=32).buffer(12, quad_segs=32)
    return tidy(unary_union([low, arc]), r=2)


def x_glass(logo, r):
    """g4/g5: la X de cristal, el hueco entre las piezas dentro de su esfera (r), que pisa
    X_GLASS_GROW px las piezas (sin raya de líquido entre las dos) y con los extremos romos."""
    gap = largest(disk(r).difference(logo).buffer(-1.5).buffer(1.5))
    x = gap.buffer(X_GLASS_GROW, quad_segs=32).intersection(disk(r))
    return x.buffer(-8, quad_segs=32).buffer(8, quad_segs=32)


def pieces():
    logo = unary_union(list(logo_pieces().values()))
    small = affinity.scale(logo, MARBLE_SCALE, MARBLE_SCALE, origin=CENTER)
    parts4 = {n: affinity.scale(p, G4_SCALE, G4_SCALE, origin=CENTER)
              .buffer(-G4_TIP.get(n, 8), quad_segs=32).buffer(G4_TIP.get(n, 8), quad_segs=32)
              for n, p in logo_pieces().items()}
    logo4 = unary_union(list(parts4.values()))
    return {
        "logo-g4": logo4,                                        # g4, g5: las piezas
        "nucleo-g4": disk(NUCLEO4_R),                            # g4, g5: el corazón hondo
        "liquido-g4": liquid(parts4),                            # g4, g5: el líquido y el haz
        "liquido-e9": liquid(parts4, level=545),                 # exploración: nivel más bajo
        "xvidrio-g4": x_glass(logo4, RADIUS * G4_SCALE),         # g4, g5: la X de cristal
        "luz-canica": glow(small, RADIUS * MARBLE_SCALE),         # g1: la luz de dentro
        "nucleo": disk(RADIUS * MARBLE_SCALE),                   # g1: el corazón verde hondo
        "logo": logo,                                            # g2, g3
        "logo-canica": small,                                    # g1: piezas y su luz
        "canica": disk(RADIUS * MARBLE_SCALE + MARBLE_RIM),      # g1: la esfera de cristal
        "logo-detras": affinity.translate(logo, *BACK_SHIFT),    # g2: la copia lima
        "x": x_thick(logo),                                      # g3: la X de cristal
        "luz": glow(logo, RADIUS),                               # g3: la luz de las piezas
        "esfera": disk(RADIUS),                                  # g3: la esfera de detrás
    }


def fill(c, alpha=1.0, bottom=None):
    """Relleno liso o en degradado vertical (arriba → abajo) con el mismo alpha."""
    if bottom:
        return {"linear-gradient": [color(c, alpha), color(bottom, alpha)]}
    return {"solid": color(c, alpha)}


def group(name, image, paint, *, glass=True, translucency=0.5, blur=0.0, refraction=None,
          shadow="neutral", shadow_opacity=0.5, specular="automatic"):
    """Un grupo de Icon Composer con una capa (como liquid.glass, pero con relleno libre).

    glass=False: la capa es luz plana (sin cristal, sin brillo ni sombra) para que el cristal de
    delante tenga algo que refractar.
    """
    layer = {"name": name, "image-name": f"{image}.svg", "glass": glass, "fill": paint}
    g = {
        "name": name,
        "lighting": "individual",
        "specular": glass,
        "specular-highlight-placement": specular,
        "blur-material": blur,
        "shadow": {"kind": shadow if glass else "none", "opacity": shadow_opacity if glass else 0.0},
        "translucency": {"enabled": translucency > 0, "value": translucency},
        "layers": [layer],
    }
    if refraction:
        g["refractivity"] = {"enabled": True, "strength": refraction[0], "depth": refraction[1]}
    return g


def light(name, layers):
    """Luz plana detrás del cristal: varias capas sin cristal (delante → detrás), (pieza, relleno)."""
    g = group(name, layers[0][0], layers[0][1], glass=False, translucency=0)
    g["layers"] = [{"name": f"{name}-{i}", "image-name": f"{img}.svg", "glass": False, "fill": paint}
                   for i, (img, paint) in enumerate(layers)]
    return g


DARK_BG = {"linear-gradient": [color("#26282C"), color("#111214")]}   # XBOX_BG con algo de relieve
LIGHT_BG = {"linear-gradient": [color("#FFFFFF"), color("#E4E9E1")]}


# --- g1: la canica ---
def marble(tint, alpha):
    """La esfera de cristal transparente delante de todo: sin esmerilar, su borde dobla las piezas.

    Refracción (0.5, 0.2): la canica es ancha (690 px). Con (0.6, 0.35) el borde arrastraba tanto
    que el arco de arriba quedaba en una isla y la X parecía un muñeco.
    """
    return group("canica", "canica", fill(tint, alpha), translucency=0.9, blur=0.0,
                 refraction=(0.5, 0.2), shadow="neutral", shadow_opacity=0.4)


def g1(light_bg=False):
    """Canica: esfera de cristal transparente / piezas de cristal verde esmerilado / luz / corazón.

    La luz llega a todas las piezas (tenue arriba) y tiene un círculo más fuerte abajo; el cristal
    esmerilado de las piezas suaviza su borde y se ve a través de ellas. Canica con tinte lima: con
    blanco, el verde hondo de dentro se agrisaba.
    """
    if light_bg:
        return {"fill": LIGHT_BG, "groups": [
            marble(XBOX_GREEN, 0.05),
            group("piezas", "logo-canica", fill("#1E9A12", 0.6), translucency=0.6, blur=0.35,
                  refraction=(0.3, 0.1), shadow="layer-color", shadow_opacity=0.5),
            light("luz", [("luz-canica", fill("#0B5E0B", 0.55)),
                          ("logo-canica", fill(XBOX_GREEN, 0.25, "#0B5E0B"))]),
            group("nucleo", "nucleo", fill("#0B4D0B", 0.2), translucency=0.5, blur=0.6,
                  shadow="neutral", shadow_opacity=0.3),
        ]}
    return {"fill": DARK_BG, "groups": [
        marble(XBOX_LIME, 0.06),
        group("piezas", "logo-canica", fill("#2FA012", 0.55), translucency=0.65, blur=0.35,
              refraction=(0.3, 0.1), shadow="layer-color", shadow_opacity=0.8),
        light("luz", [("luz-canica", fill(XBOX_GLOW, 0.55)),
                      ("logo-canica", fill(XBOX_LIME, 0.3))]),
        group("nucleo", "nucleo", fill("#0A420A", 0.85), translucency=0.4, blur=0.6,
              shadow="neutral", shadow_opacity=0.4),
    ]}


# --- g2: doble cristal ---
def g2(light_bg=False):
    """Piezas de cristal verde transparente delante de su copia de cristal lima, más abajo.

    La copia en lima puro: con el #D2EC14 abajo, el pie de la pieza de abajo tiraba a oliva.
    """
    if light_bg:
        return {"fill": LIGHT_BG, "groups": [
            group("piezas", "logo", fill(XBOX_GREEN, 0.55), translucency=0.7, blur=0.0,
                  refraction=(0.45, 0.16), shadow="layer-color", shadow_opacity=0.6),
            group("detras", "logo-detras", fill("#5DB80A", 0.9), translucency=0.3, blur=0.6,
                  shadow="neutral", shadow_opacity=0.4),
        ]}
    return {"fill": DARK_BG, "groups": [
        group("piezas", "logo", fill(XBOX_GREEN, 0.4), translucency=0.75, blur=0.0,
              refraction=(0.45, 0.16), shadow="layer-color", shadow_opacity=1.0),
        group("detras", "logo-detras", fill(XBOX_LIME, 0.85), translucency=0.3, blur=0.6,
              shadow="neutral", shadow_opacity=0.5),
    ]}


# --- g3: la X de cristal ---
def g3(light_bg=False):
    """X gruesa de cristal transparente / piezas de cristal verde / su luz / esfera de cristal.

    La X lleva un tinte lima muy leve: con blanco, el verde hondo de detrás se veía gris humo.
    En claro, la esfera de detrás es menta claro: la X se lee clara, como el logo sobre blanco.
    """
    if light_bg:
        return {"fill": LIGHT_BG, "groups": [
            group("x", "x", fill(WHITE, 0.1), translucency=0.9, blur=0.0, refraction=(0.45, 0.16),
                  shadow="neutral", shadow_opacity=0.35),
            group("piezas", "logo", fill(XBOX_GREEN, 0.75), translucency=0.5, blur=0.4,
                  refraction=(0.3, 0.1), shadow="layer-color", shadow_opacity=0.5),
            light("luz", [("luz", fill("#0B5E0B", 0.5)), ("logo", fill("#0B5E0B", 0.3))]),
            group("esfera", "esfera", fill("#CFEFC4", 0.7, "#A9DD98"), translucency=0.4, blur=0.6,
                  shadow="neutral", shadow_opacity=0.35),
        ]}
    return {"fill": DARK_BG, "groups": [
        group("x", "x", fill(XBOX_LIME, 0.14), translucency=0.9, blur=0.0, refraction=(0.45, 0.16),
              shadow="neutral", shadow_opacity=0.45),
        group("piezas", "logo", fill("#2FA012", 0.55), translucency=0.65, blur=0.4,
              refraction=(0.3, 0.1), shadow="layer-color", shadow_opacity=0.8),
        light("luz", [("luz", fill(XBOX_GLOW, 0.5)), ("logo", fill(XBOX_LIME, 0.3))]),
        group("esfera", "esfera", fill("#072A07", 0.85, "#125412"), translucency=0.35, blur=0.6,
              shadow="neutral", shadow_opacity=0.5),
    ]}


# --- g4 / g5: la canica, sin timidez ---
MARBLE4_REFRACTION = (0.5, 0.07)   # borde estrecho y fuerte. Con (0.55, 0.25) o (0.38, 0.13) la
                                   # canica ampliaba el logo hasta llenar el anillo, hinchaba el
                                   # arco en un tulipán y rizaba los brazos en pies
PIECE4_REFRACTION = (0.3, 0.07)    # el bisel amplía el interior de la pieza y oscurece su canto:
                                   # con (0.5, 0.14) el nivel se hundía junto a los cantos de las
                                   # laterales (copas con pie) y la punta oscura de la de abajo
                                   # quedaba en una gota; con (0.35, 0.10), en un ojo con borde lima
X4_REFRACTION = (0.35, 0.12)       # la X de cristal, poco esmerilada, dobla el nivel en sus brazos


def marble4(tint, alpha, shadow_opacity):
    """La canica de g4/g5: cuerpo de cristal visible (alpha doble que g1) y brillo por dentro.

    Sin lente sobre el cruce: ampliaba el hueco oscuro de la X y dejaba un disco oscuro con
    cuatro motas (una cara).
    """
    return group("canica", "canica", fill(tint, alpha), translucency=0.85, blur=0.0,
                 refraction=MARBLE4_REFRACTION, shadow="neutral", shadow_opacity=shadow_opacity,
                 specular="inside")


def lake(liquid_paint, back_paint, image="liquido-g4", blur=0.25, shadow_opacity=0.5):
    """El líquido de cristal lima y, detrás, el fondo plano de la canica (sin bisel propio)."""
    g = group("luz", image, liquid_paint, translucency=0.3, blur=blur, shadow="neutral",
              shadow_opacity=shadow_opacity)
    g["layers"].append({"name": "fondo", "image-name": "nucleo-g4.svg", "glass": False,
                        "fill": back_paint})
    return g


def g4(light_bg=False, x_light=False, piece_refraction=PIECE4_REFRACTION, x_refraction=X4_REFRACTION,
       liquid_image="liquido-g4"):
    """Canica / piezas de cristal verde / X de cristal / líquido lima que llena media canica.

    La canica está medio llena de un líquido lima que brilla (más amarillo abajo). No va recortado
    a nada: se ve a través de las piezas de cristal verde transparente (lima encendido), a través
    de la X de cristal oscuro (apagado) y a través del anillo de la canica (lima limpio), siempre
    con el mismo nivel recto, y cada bisel lo dobla donde lo cruza: el de la canica en la pared,
    los de las piezas y los de la X dentro de la marca. El arco, por encima, recibe un haz de luz
    desde el centro. x_light (g5): la X es cristal esmerilado blanco lima que brilla (la X de luz
    de la bola de Xbox 360); el líquido asoma apenas por sus brazos de abajo.
    """
    if light_bg:
        x = (group("x", "xvidrio-g4", fill(WHITE, 0.92), translucency=0.3, blur=0.35,
                   refraction=x_refraction, shadow="neutral", shadow_opacity=0.3) if x_light else
             group("x", "xvidrio-g4", fill("#BFF0A8", 0.6), translucency=0.6, blur=0.12,
                   refraction=x_refraction, shadow="neutral", shadow_opacity=0.3))
        return {"fill": LIGHT_BG, "groups": [
            marble4(XBOX_LIME, 0.08, 0.35),
            group("piezas", "logo-g4", fill(XBOX_GREEN, 0.6), translucency=0.75, blur=0.0,
                  refraction=piece_refraction, shadow="layer-color", shadow_opacity=0.8),
            x,
            lake(fill("#5DB80A", 0.9, "#86CC0C"), fill("#E2F5DA"), liquid_image, shadow_opacity=0.4),
        ]}
    # X oscura con tinte verde azulado: con #04301A el lima de detrás daba oliva (55,107,21), y
    # esmerilada 0.3 borraba el nivel en sus brazos
    x = (group("x", "xvidrio-g4", fill("#F2FFE0", 0.92), translucency=0.3, blur=0.35,
               refraction=x_refraction, shadow="neutral", shadow_opacity=0.4) if x_light else
         group("x", "xvidrio-g4", fill("#053A28", 0.82), translucency=0.5, blur=0.12,
               refraction=x_refraction, shadow="neutral", shadow_opacity=0.4))
    return {"fill": DARK_BG, "groups": [
        marble4(XBOX_LIME, 0.12, 0.4),
        group("piezas", "logo-g4", fill(XBOX_GREEN, 0.38), translucency=0.8, blur=0.0,
              refraction=piece_refraction, shadow="layer-color", shadow_opacity=1.0),
        x,
        lake(fill(XBOX_LIME, 0.85, XBOX_GLOW), fill("#0B3F0B", 1.0, "#1A6614"), liquid_image),
    ]}


APPROVED = {}

CONCEPTS = {
    "xbox-g1": g1(), "xbox-g1c": g1(light_bg=True),
    "xbox-g2": g2(), "xbox-g2c": g2(light_bg=True),
    "xbox-g3": g3(), "xbox-g3c": g3(light_bg=True),
    "xbox-g4": g4(), "xbox-g4c": g4(light_bg=True),
    "xbox-g5": g4(x_light=True), "xbox-g5c": g4(light_bg=True, x_light=True),
    "xbox-e9": g4(liquid_image="liquido-e9"),
    "xbox-e10": g4(piece_refraction=(0.25, 0.05)),
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
