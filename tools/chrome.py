"""Google Chrome: logo oficial de 2022 reconstruido y ajustado al icono de iOS, y montaje de los .icon.

El logo de 2022 es geometría pura y simple-icons (brands/googlechrome.svg) solo trae una silueta
monocroma, así que se construye aquí con la definición de Google: un círculo exterior de radio R,
el círculo blanco de radio R/2 y tres fronteras rectas, cada una la mitad de un lado del triángulo
equilátero inscrito en el círculo exterior (son tangentes al círculo blanco). El círculo azul va
centrado. Ajustado por colores contra el icono de la App Store (Google Chrome, id 535886823,
1024 px): R = 409.25, círculo blanco R/2 (la proporción oficial, sin tocar), azul 166.25, giro 0.
IoU por color: rojo 0.991, amarillo 0.983 (el brillo especular de su borde interior no pasa el
umbral de color), verde 0.990, azul 0.995, anillo blanco 0.983; silueta completa 0.992.

Piezas: los tres segmentos, el azul y una base blanca debajo de todo (el fondo blanco del icono
oficial recortado al logo: es el anillo blanco y hace que el cristal de color se vea como en el
oficial también sobre el fondo oscuro). Ninguna lleva sombras, degradados ni brillos: los pone
Icon Composer.
Conceptos (cN oscuro para la tecla, cNc su pareja clara):
- c1 fiel al oficial: segmentos de cristal de color en un grupo y el azul delante, cuyo borde
  recoge el blanco del anillo.
- c2 Fotos: el amarillo es un pétalo de cristal transparente delante; el rojo y el verde se meten
  9° debajo de él, así que a través del pétalo se ven sus cuñas (naranja y lima) y su borde las
  dobla, como los pétalos de Fotos.
- c3 lente: el azul es una lente transparente de refracción profunda sobre su azul plano; su
  borde muestra, doblados, el anillo blanco y el remolino de colores que la rodean (Vista Previa).
"""
import math

from shapely import affinity
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

from liquid import WHITE, clean, color, glass, write_icon

# Medidas en el lienzo de 1024 (ajustadas por colores contra el icono oficial de iOS)
CENTER = (512.0, 512.0)
R = 409.25            # círculo exterior
R_RING = R / 2        # círculo blanco: la mitad exacta, como en el logo oficial
R_BLUE = 166.25       # círculo azul (en iOS algo mayor que el 9.5/24 del SVG de 2022)
ROTATION = 0.0        # grados; el ajuste da -0.2, se deja recto como el oficial
TANGENTS = (270.0, 30.0, 150.0)  # dónde tocan las fronteras el círculo blanco (grados, y hacia abajo)

RES = 256             # segmentos por cuarto de círculo: curvas suaves a cualquier tamaño
BASE_INSET = 8        # px: la base blanca acaba un poco antes del borde para no dejar halo blanco
OVERLAP = 9.0         # grados que el rojo y el verde se meten debajo del pétalo amarillo (~58 px)

# Colores del icono oficial de iOS (mediana del interior de cada pieza)
RED, YELLOW, GREEN, BLUE = "#F71C1C", "#FFC100", "#00A141", "#0078F3"


def circle(c, r):
    return Point(c).buffer(r, quad_segs=RES)


def _beyond(angle, dist, size=3000):
    """Semiplano más allá de la recta tangente al círculo de radio dist en ese ángulo."""
    ux, uy = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    px, py = -uy, ux
    ox, oy = CENTER[0] + ux * dist, CENTER[1] + uy * dist
    return Polygon([(ox + px * size, oy + py * size), (ox + px * size + ux * size, oy + py * size + uy * size),
                    (ox - px * size + ux * size, oy - py * size + uy * size), (ox - px * size, oy - py * size)])


def _sector(a0, a1, r=2000):
    n = max(8, int(abs(a1 - a0)))
    return Polygon([CENTER] + [(CENTER[0] + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
                                CENTER[1] + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
                               for i in range(n + 1)])


def _polygons(g):
    """Solo las partes con área (las intersecciones dejan a veces líneas sueltas), soldadas en una:
    el casquete y la esquina de un segmento quedan separados por una rendija de redondeo que en el
    render sería una costura (y un bisel de cristal) atravesando el segmento."""
    parts = [p for p in getattr(g, "geoms", [g]) if p.geom_type in ("Polygon", "MultiPolygon")]
    g = unary_union([q for p in parts for q in getattr(p, "geoms", [p])])
    return g.buffer(0.05, join_style="mitre").buffer(-0.05, join_style="mitre")


def segments():
    """Rojo, amarillo y verde: cada uno es el casquete más allá de un lado del triángulo inscrito
    más la esquina del triángulo que queda fuera del círculo blanco."""
    t1, t2, t3 = (a + ROTATION for a in TANGENTS)
    disk, ring = circle(CENTER, R), circle(CENTER, R_RING)
    caps = [disk.intersection(_beyond(a, R_RING)) for a in (t1, t2, t3)]
    corners = disk.difference(unary_union(caps)).difference(ring)
    red = unary_union([caps[0], corners.intersection(_sector(t3, t1))])
    yellow = unary_union([caps[1], corners.intersection(_sector(t1, t2 + 360))])
    green = unary_union([caps[2], corners.intersection(_sector(t2, t3))])
    return {"rojo": _polygons(red), "amarillo": _polygons(yellow), "verde": _polygons(green)}


def tuck(piece, front, degrees):
    """La pieza más una cuña que se mete debajo de la de delante (girándola sobre el centro).

    Girar mantiene la frontera tangente al círculo blanco: la cuña nace en el anillo y se abre
    hasta el borde exterior. Se recorta con la pieza de delante para que nunca asome."""
    wedges = [affinity.rotate(piece, s * degrees, origin=CENTER).intersection(front) for s in (1, -1)]
    return _polygons(unary_union([piece, *wedges]))


def pieces():
    seg = segments()
    return {
        **seg,
        "azul": circle(CENTER, R_BLUE),
        # Base blanca bajo todo el logo: el anillo blanco que se ve y el blanco de detrás del cristal
        "base": circle(CENTER, R - BASE_INSET),
        # Concepto Fotos: rojo y verde con la cuña que se mete debajo del pétalo amarillo
        "rojo-solapa": tuck(seg["rojo"], seg["amarillo"], OVERLAP),
        "verde-solapa": tuck(seg["verde"], seg["amarillo"], OVERLAP),
    }


def group(name, layers, **kw):
    """Un grupo de Liquid Glass con varias piezas, cada una con su color (de delante hacia atrás)."""
    g = glass(name, **kw)
    g["layers"] = [{"name": n, "image-name": f"{image}.svg", "glass": True, "fill": {"solid": color(fill, alpha)}}
                   for n, image, fill, alpha in layers]
    return g


WHITE_BG = {"solid": color(WHITE)}  # el fondo del icono oficial


# --- Concepto 1: fiel al icono oficial de iOS ---------------------------------------------------
def blue_official():
    """Azul de cristal casi opaco; su borde recoge el blanco del anillo (el brillo del oficial)."""
    return glass("azul", fill=BLUE, alpha=0.96, translucency=0.3, blur=0.3, refraction=(0.3, 0.12),
                 shadow="layer-color", shadow_opacity=0.5)


def segments_official():
    """Los tres segmentos en un solo grupo de cristal de color, con sombra del color de cada uno."""
    return group("segmentos", [("rojo", "rojo", RED, 0.97), ("amarillo", "amarillo", YELLOW, 0.97),
                               ("verde", "verde", GREEN, 0.97)],
                 translucency=0.3, blur=0.3, refraction=(0.3, 0.1), shadow="layer-color", shadow_opacity=0.5)


def base(extra=()):
    """Base blanca (el anillo), opaca y sin refracción: el blanco del anillo queda limpio.

    extra: piezas planas que van encima de la base, debajo de un cristal transparente, para que
    ese cristal conserve el color de Chrome y solo cambie lo que dobla su borde."""
    return group("base", [*extra, ("base", "base", WHITE, 1.0)],
                 translucency=0.0, blur=0.5, shadow="neutral", shadow_opacity=0.35)


# --- Concepto 2: Fotos (pétalo amarillo de cristal delante del rojo y del verde) ---------------
def blue_photos():
    return glass("azul", fill=BLUE, alpha=0.95, translucency=0.35, blur=0.2, refraction=(0.35, 0.15),
                 shadow="layer-color", shadow_opacity=0.5)


def yellow_petal():
    """Pétalo amarillo de cristal claro y sin esmerilar: se ven debajo las cuñas del rojo y el verde
    (naranja y lima) y su borde las dobla. Refracción moderada: es grande, pero su borde exterior
    queda a 103 px del borde del lienzo y las fronteras acaban en el borde del logo."""
    return glass("amarillo", fill=YELLOW, alpha=0.85, translucency=0.6, blur=0.0, refraction=(0.35, 0.12),
                 shadow="layer-color", shadow_opacity=0.55)


# Debajo del pétalo transparente, el amarillo plano (en el grupo de la base): el pétalo sigue siendo
# del amarillo de Chrome (sobre la base blanca saldría desvaído) y solo cambia donde están las cuñas.
PETAL_BACKING = ("fondo-amarillo", "amarillo", YELLOW, 1.0)


def red_green_tucked():
    """Rojo y verde con sus cuñas debajo del amarillo; no se pisan entre ellos (rojo sobre verde
    daría marrón), así que comparten grupo."""
    return group("rojo-verde", [("rojo", "rojo-solapa", RED, 0.97), ("verde", "verde-solapa", GREEN, 0.97)],
                 translucency=0.3, blur=0.3, refraction=(0.3, 0.1), shadow="layer-color", shadow_opacity=0.5)


# --- Concepto 3: lente (el azul como una canica de cristal transparente) ------------------------
def blue_lens():
    """Lente azul transparente, sin esmerilar, con refracción profunda (pieza grande, redonda y lisa,
    a 346 px del borde del lienzo): su borde recoge el anillo blanco y el remolino de colores.
    No más profunda: con (0.75, 0.55) el bisel se comería medio azul y lo haría parecer pequeño."""
    return glass("azul", fill=BLUE, alpha=0.75, translucency=0.65, blur=0.0, refraction=(0.6, 0.3),
                 shadow="layer-color", shadow_opacity=0.6, specular="inside")


def lens_backing():
    """El azul plano y opaco debajo de la lente transparente: el centro sigue siendo del azul de
    Chrome y lo que cambia es el borde, que muestra lo que rodea a la lente. Va en su propio grupo,
    delante de los segmentos, para que el bisel interior de los segmentos no traiga trozos de azul."""
    return glass("fondo-lente", fill=BLUE, translucency=0.0, blur=0.5, shadow="none", shadow_opacity=0.0,
                 image="azul")


APPROVED = {}

CONCEPTS = {
    # c1 (fiel al oficial): fondo oscuro de Apple, base blanca, segmentos y azul de cristal
    "chrome-c1": {"fill": "system-dark", "groups": [blue_official(), segments_official(), base()]},
    # c1c: exactamente el icono oficial de iOS (fondo blanco, el anillo es el fondo)
    "chrome-c1c": {"fill": WHITE_BG, "groups": [blue_official(), segments_official()]},
    # c2 (Fotos): pétalo amarillo de cristal claro delante del rojo y el verde, que se meten debajo
    "chrome-c2": {"fill": "system-dark", "groups": [blue_photos(), yellow_petal(), red_green_tucked(),
                                                    base([PETAL_BACKING])]},
    "chrome-c2c": {"fill": "system-light", "groups": [blue_photos(), yellow_petal(), red_green_tucked(),
                                                      base([PETAL_BACKING])]},
    # c3 (lente): el azul como lente transparente sobre su azul plano
    "chrome-c3": {"fill": "system-dark", "groups": [blue_lens(), lens_backing(), segments_official(), base()]},
    "chrome-c3c": {"fill": "system-light", "groups": [blue_lens(), lens_backing(), segments_official(), base()]},
}


def main(names=None):
    """Escribe los aprobados; con nombres de concepto, escribe esos para renderizarlos."""
    geo = pieces()
    clean("chrome")
    targets = {n: n for n in names} if names else APPROVED
    for name, concept in targets.items():
        spec = CONCEPTS[concept]
        write_icon(name, spec["fill"], spec["groups"], geo)


if __name__ == "__main__":
    import sys
    main(sys.argv[1:] or None)
