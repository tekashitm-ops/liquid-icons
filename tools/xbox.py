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
"""
import re

import numpy as np
from shapely import affinity
from shapely.geometry import Point, box
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
# (r 351): queda un anillo de cristal vacío de 25 px y el bisel de la canica cae sobre todo en él
G4_SCALE = 0.85             # esfera del logo de 326 px de radio
G4_SHIFT = (0.0, 20.0)      # la copia lima de detrás (la luz de iOS viene de arriba)
LENS_R = 165                # g5: lente sobre el cruce de la X; su borde corta las cuatro piezas
LENS_CENTER = (CENTER[0], CENTER[1] + (345.0 - CENTER[1]) * G4_SCALE)  # cruce de la X a 0.85


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


def x_backing(logo, r, grow):
    """La X clara de detrás: el hueco entre las piezas engordado grow px, dentro de su esfera."""
    gap = largest(disk(r).difference(logo).buffer(-1.5).buffer(1.5))
    x = gap.buffer(grow, quad_segs=64).buffer(12, quad_segs=32).buffer(-12, quad_segs=32)
    return x.intersection(disk(r))


def core(logo, inset, shift):
    """El corazón lima de cada pieza: la pieza encogida inset px y bajada shift px."""
    c = logo.buffer(-inset, quad_segs=32).buffer(-8, quad_segs=32).buffer(8, quad_segs=32)
    c = unary_union([g for g in getattr(c, "geoms", [c]) if g.area > 4000])  # sin islas: motas
    return affinity.translate(c, 0, shift)


def pieces():
    logo = unary_union(list(logo_pieces().values()))
    small = affinity.scale(logo, MARBLE_SCALE, MARBLE_SCALE, origin=CENTER)
    small4 = affinity.scale(logo, G4_SCALE, G4_SCALE, origin=CENTER)
    small8 = affinity.scale(logo, 0.8, 0.8, origin=CENTER)
    return {
        "logo-g4": small4,                                       # g4, g5: las piezas
        "logo-g4-detras": affinity.translate(small4, *G4_SHIFT),  # g4, g5: su copia lima
        "nucleo-g4": disk(RADIUS * G4_SCALE),                    # g4, g5: el corazón
        "lente": disk(LENS_R, LENS_CENTER),                      # g5: la lente del cruce
        # exploración (ronda 2)
        "logo-g4-detras24": affinity.translate(small4, 0, 24),
        "core-g4": core(small4, 24, 12),
        "xclara-g4": x_backing(small4, RADIUS * G4_SCALE, 20),
        "logo-80": small8,
        "logo-80-detras": affinity.translate(small8, 0, 22),
        "nucleo-80": disk(RADIUS * 0.8),
        # exploración (ronda 3)
        "core40-g4": core(small4, 40, 16),
        "brasa-g4": small4.intersection(disk(258)),
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


# --- g4: la canica, sin timidez ---
MARBLE4_REFRACTION = (0.38, 0.13)   # con (0.55, 0.25) el borde ampliaba el logo hasta llenar el
                                    # anillo, hinchaba el arco en un tulipán y rizaba los pies


def marble4(tint, alpha, shadow_opacity, lens=False, refraction=MARBLE4_REFRACTION):
    """La canica de g4: cuerpo de cristal visible (alpha doble que g1) y brillo por dentro.

    lens: una segunda capa en el mismo grupo, la lente sobre el cruce de la X (g5); así el icono
    sigue en 4 grupos.
    """
    g = group("canica", "canica", fill(tint, alpha), translucency=0.85, blur=0.0,
              refraction=refraction, shadow="neutral", shadow_opacity=shadow_opacity,
              specular="inside")
    if lens:
        g["layers"].insert(0, {"name": "lente", "image-name": "lente.svg", "glass": True,
                               "fill": fill(WHITE, 0.10)})
    return g


def g4(light_bg=False, lens=False, tag="g4", back="logo-g4-detras", refraction=MARBLE4_REFRACTION,
       piece_refraction=(0.45, 0.16), back_blur=0.6, piece_fill=(XBOX_GREEN, 0.38)):
    """Canica g1 con los arreglos del juez: dentro, cristal verde claro delante de su copia lima.

    Sin la placa de luz plana (por ella las piezas se veían mate): cada pieza de cristal verde
    transparente tiene detrás su copia lima más abajo, así que dentro de cada pieza hay dos
    tintes (sobre lima / sobre el corazón oscuro) y su bisel dobla el canto lima. El logo a 0.85
    deja un anillo de cristal vacío dentro de la canica y encoge los pies.
    """
    logo, nucleo = f"logo-{tag}", f"nucleo-{tag}"
    if light_bg:
        return {"fill": LIGHT_BG, "groups": [
            marble4(XBOX_GREEN, 0.08, 0.35, lens, refraction),
            group("piezas", logo, fill(XBOX_GREEN, 0.45), translucency=0.75, blur=0.0,
                  refraction=(0.45, 0.16), shadow="layer-color", shadow_opacity=0.8),
            group("detras", back, fill("#5DB80A", 0.9), translucency=0.3, blur=0.6,
                  shadow="neutral", shadow_opacity=0.4),
            group("nucleo", nucleo, fill("#0B4D0B", 0.2), translucency=0.6, blur=0.6,
                  shadow="neutral", shadow_opacity=0.3),
        ]}
    return {"fill": DARK_BG, "groups": [
        marble4(XBOX_LIME, 0.12, 0.4, lens, refraction),
        group("piezas", logo, fill(*piece_fill), translucency=0.8, blur=0.0,
              refraction=piece_refraction, shadow="layer-color", shadow_opacity=1.0),
        group("detras", back, fill(XBOX_LIME, 0.85), translucency=0.3, blur=back_blur,
              shadow="neutral", shadow_opacity=0.5),
        group("nucleo", nucleo, fill("#0A420A", 0.65), translucency=0.55, blur=0.6,
              shadow="neutral", shadow_opacity=0.4),
    ]}


def e_xclara(refraction=MARBLE4_REFRACTION, x_fill=("#E9FFD2", 0.5), piece_fill=(XBOX_GREEN, 0.38)):
    """Exploración: X clara esmerilada detrás de las piezas de cristal verde (injerto del juez)."""
    return {"fill": DARK_BG, "groups": [
        marble4(XBOX_LIME, 0.12, 0.4, refraction=refraction),
        group("piezas", "logo-g4", fill(*piece_fill), translucency=0.8, blur=0.0,
              refraction=(0.45, 0.16), shadow="layer-color", shadow_opacity=1.0),
        group("xclara", "xclara-g4", fill(*x_fill), translucency=0.4, blur=0.6,
              shadow="neutral", shadow_opacity=0.4),
        group("nucleo", "nucleo-g4", fill("#0A420A", 0.65), translucency=0.55, blur=0.6,
              shadow="neutral", shadow_opacity=0.4),
    ]}


APPROVED = {}

CONCEPTS = {
    "xbox-g1": g1(), "xbox-g1c": g1(light_bg=True),
    "xbox-g2": g2(), "xbox-g2c": g2(light_bg=True),
    "xbox-g3": g3(), "xbox-g3c": g3(light_bg=True),
    "xbox-g4": g4(), "xbox-g4c": g4(light_bg=True),
    "xbox-g5": g4(lens=True), "xbox-g5c": g4(light_bg=True, lens=True),
    # exploración (ronda 2)
    "xbox-e1": g4(back="core-g4"),
    "xbox-e2": e_xclara(),
    "xbox-e3": g4(tag="80", back="logo-80-detras", refraction=(0.5, 0.2)),
    "xbox-e4": g4(back="logo-g4-detras24"),
    # exploración (ronda 3)
    "xbox-e5": g4(refraction=(0.5, 0.07)),
    "xbox-e6": g4(refraction=(0.5, 0.07), back="core40-g4", piece_refraction=(0.45, 0.08)),
    "xbox-e7": e_xclara(refraction=(0.5, 0.07), x_fill=("#F4FFE6", 0.75), piece_fill=("#1E9A12", 0.5)),
    "xbox-e8": g4(refraction=(0.5, 0.07), back="brasa-g4", back_blur=0.0),
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
