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
- g1 canica: las piezas de cristal verde, encendidas por la luz lima de detrás, dentro de una
  esfera de cristal transparente del tamaño de la esfera; su borde grueso dobla las piezas.
- g2 doble cristal: las piezas de cristal verde transparente delante de una copia de cristal lima
  esmerilado algo más abajo; se ve la lima a través del verde y el bisel dobla su borde.
- g3 X de cristal: una X gruesa de cristal transparente delante de las piezas de cristal verde y
  de una esfera de cristal verde hondo; la X dobla los bordes de las piezas.
Las parejas claras (sufijo c) son la misma idea con verdes más hondos sobre fondo claro.
"""
import re

import numpy as np
from shapely import affinity
from shapely.geometry import Point
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
# g2: la copia lima de detrás, desplazada hacia abajo (la luz de iOS viene de arriba)
BACK_SHIFT = (0.0, 14.0)
# g3: la X gruesa: el hueco entre las piezas engordado; pisa cada pieza X_GROW px
X_GROW = 18
X_FILLET = 16      # px: redondea las esquinas cóncavas (si no, la refracción se arruga)
X_END_ROUND = 18   # px: redondea las esquinas de los extremos


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
    """La X gruesa: el hueco entre las piezas, engordado X_GROW px y con las esquinas redondeadas."""
    gap = largest(disk(RADIUS).difference(logo).buffer(-1.5).buffer(1.5))
    x = gap.buffer(X_GROW, quad_segs=64)
    x = x.buffer(X_FILLET, quad_segs=32).buffer(-X_FILLET, quad_segs=32)
    x = x.intersection(disk(RADIUS))
    return x.buffer(-X_END_ROUND, quad_segs=32).buffer(X_END_ROUND, quad_segs=32)


def pieces():
    logo = unary_union(list(logo_pieces().values()))
    small = affinity.scale(logo, MARBLE_SCALE, MARBLE_SCALE, origin=CENTER)
    return {
        "logo": logo,                                            # g2, g3
        "logo-canica": small,                                    # g1: piezas y su luz
        "canica": disk(RADIUS * MARBLE_SCALE + MARBLE_RIM),      # g1: la esfera de cristal
        "logo-detras": affinity.translate(logo, *BACK_SHIFT),    # g2: la copia lima
        "x": x_thick(logo),                                      # g3: la X de cristal
        "esfera": disk(RADIUS),                                  # g3: la esfera de detrás
    }


def fill(c, alpha=1.0, bottom=None):
    """Relleno liso o en degradado vertical (arriba → abajo) con el mismo alpha."""
    if bottom:
        return {"linear-gradient": [color(c, alpha), color(bottom, alpha)]}
    return {"solid": color(c, alpha)}


def group(name, image, paint, *, glass=True, translucency=0.5, blur=0.0, refraction=None,
          shadow="neutral", shadow_opacity=0.5, specular="automatic", lighting="individual",
          blend=None, opacity=None):
    """Un grupo de Icon Composer con una capa, con todas las claves que usa el cristal de Xbox.

    glass=False: la capa es luz plana (sin cristal, sin brillo ni sombra) para que el cristal de
    delante tenga algo que refractar.
    """
    layer = {"name": name, "image-name": f"{image}.svg", "glass": glass, "fill": paint}
    g = {
        "name": name,
        "lighting": lighting,
        "specular": glass,
        "specular-highlight-placement": specular,
        "blur-material": blur,
        "shadow": {"kind": shadow if glass else "none", "opacity": shadow_opacity if glass else 0.0},
        "translucency": {"enabled": translucency > 0, "value": translucency},
        "layers": [layer],
    }
    if refraction:
        g["refractivity"] = {"enabled": True, "strength": refraction[0], "depth": refraction[1]}
    if blend:
        g["blend-mode"] = blend
    if opacity is not None:
        g["opacity"] = opacity
    return g


DARK_BG = {"linear-gradient": [color("#26282C"), color("#111214")]}   # el #1A1B1E con algo de relieve
LIGHT_BG = {"linear-gradient": [color("#FFFFFF"), color("#E4E9E1")]}


# --- g1: la canica ---
def g1(light=False):
    if light:
        return {"fill": LIGHT_BG, "groups": [
            group("canica", "canica", fill(XBOX_GREEN, 0.08), translucency=0.9, blur=0.0,
                  refraction=(0.6, 0.35), shadow="neutral", shadow_opacity=0.35),
            group("piezas", "logo-canica", fill("#1E9A12", 0.75, "#0B5E0B"), translucency=0.5,
                  blur=0.1, refraction=(0.3, 0.1), shadow="layer-color", shadow_opacity=0.6),
            group("luz", "logo-canica", fill("#0B5E0B", 0.9), glass=False, translucency=0),
        ]}
    return {"fill": DARK_BG, "groups": [
        group("canica", "canica", fill(WHITE, 0.08), translucency=0.9, blur=0.0,
              refraction=(0.6, 0.35), shadow="neutral", shadow_opacity=0.4),
        group("piezas", "logo-canica", fill("#2FA012", 0.6, "#5BC20C"), translucency=0.6,
              blur=0.1, refraction=(0.3, 0.1), shadow="layer-color", shadow_opacity=0.7),
        group("luz", "logo-canica", fill(XBOX_LIME, 0.45, XBOX_GLOW), glass=False, translucency=0),
    ]}


# --- g2: doble cristal ---
def g2(light=False):
    if light:
        return {"fill": LIGHT_BG, "groups": [
            group("piezas", "logo", fill(XBOX_GREEN, 0.6), translucency=0.6, blur=0.0,
                  refraction=(0.35, 0.12), shadow="layer-color", shadow_opacity=0.5),
            group("detras", "logo-detras", fill("#5DB80A", 0.9), translucency=0.3, blur=0.6,
                  shadow="layer-color", shadow_opacity=0.5),
        ]}
    return {"fill": DARK_BG, "groups": [
        group("piezas", "logo", fill(XBOX_GREEN, 0.55), translucency=0.65, blur=0.0,
              refraction=(0.35, 0.12), shadow="layer-color", shadow_opacity=0.7),
        group("detras", "logo-detras", fill(XBOX_LIME, 0.85, XBOX_GLOW), translucency=0.3, blur=0.6,
              shadow="layer-color", shadow_opacity=0.7),
    ]}


# --- g3: la X de cristal ---
def g3(light=False):
    if light:
        return {"fill": LIGHT_BG, "groups": [
            group("x", "x", fill(WHITE, 0.2), translucency=0.85, blur=0.0, refraction=(0.4, 0.18),
                  shadow="neutral", shadow_opacity=0.35),
            group("piezas", "logo", fill(XBOX_GREEN, 0.7, "#2E9E12"), translucency=0.5, blur=0.2,
                  refraction=(0.3, 0.1), shadow="layer-color", shadow_opacity=0.5),
            group("esfera", "esfera", fill("#0B4D0B", 0.8), translucency=0.4, blur=0.6,
                  shadow="neutral", shadow_opacity=0.4),
        ]}
    return {"fill": DARK_BG, "groups": [
        group("x", "x", fill(WHITE, 0.15), translucency=0.85, blur=0.0, refraction=(0.4, 0.18),
              shadow="neutral", shadow_opacity=0.4),
        group("piezas", "logo", fill("#3FAE10", 0.65, XBOX_LIME), translucency=0.5, blur=0.2,
              refraction=(0.3, 0.1), shadow="layer-color", shadow_opacity=0.6),
        group("esfera", "esfera", fill("#0E4A0E", 0.75), translucency=0.4, blur=0.6,
              shadow="neutral", shadow_opacity=0.5),
    ]}


# --- variantes de exploración (ronda 1) ---
def e1():
    """g1 con la canica teñida de verde y más honda."""
    c = g1()
    c["groups"][0] = group("canica", "canica", fill(XBOX_LIME, 0.12), translucency=0.85, blur=0.0,
                           refraction=(0.8, 0.5), shadow="layer-color", shadow_opacity=0.5)
    return c


def e2():
    """g2 con la luz lima plana (sin cristal) con la forma exacta de las piezas."""
    return {"fill": DARK_BG, "groups": [
        group("piezas", "logo", fill("#2FA012", 0.55), translucency=0.65, blur=0.0,
              refraction=(0.35, 0.12), shadow="layer-color", shadow_opacity=0.9),
        group("luz", "logo", fill(XBOX_LIME, 0.45, XBOX_GLOW), glass=False, translucency=0),
    ]}


def e3():
    """g3 sin la esfera de detrás: la X deja ver el fondo; las piezas sobre la luz lima."""
    return {"fill": DARK_BG, "groups": [
        group("x", "x", fill(WHITE, 0.2), translucency=0.85, blur=0.0, refraction=(0.45, 0.2),
              shadow="neutral", shadow_opacity=0.4),
        group("piezas", "logo", fill("#2FA012", 0.6, "#5BC20C"), translucency=0.6, blur=0.1,
              refraction=(0.3, 0.1), shadow="layer-color", shadow_opacity=0.7),
        group("luz", "logo", fill(XBOX_LIME, 0.45, XBOX_GLOW), glass=False, translucency=0),
    ]}


APPROVED = {}

CONCEPTS = {
    "xbox-g1": g1(), "xbox-g1c": g1(light=True),
    "xbox-g2": g2(), "xbox-g2c": g2(light=True),
    "xbox-g3": g3(), "xbox-g3c": g3(light=True),
    "xbox-e1": e1(), "xbox-e2": e2(), "xbox-e3": e3(),
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
