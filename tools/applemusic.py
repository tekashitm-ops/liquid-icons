"""Apple Music: la nota oficial ajustada al icono de iOS y montaje de los .icon.

Trazado: brands/applemusic.svg (simple-icons 16.34.0, tomado de las pautas de identidad de
Apple Music: el cuadrado redondeado con la nota calada). Solo se usa la nota (su segundo
subtrazado), sin deformar: escala uniforme contra el icono de la App Store (Apple Music,
id 1108187390, "musicCalistoga", 1024 px) con IoU 0.993.
Ese icono ya es Liquid Glass hecho por Apple: una sola pieza de cristal blanco esmerilado
sobre el degradado rojo de Apple Music (c1 lo reproduce tal cual).
Piezas:
  - nota: la nota entera (c1).
  - cabezas + armazon (c2, "lentes", como la lupa de Vista Previa): las dos cabezas son
    lentes de cristal claro delante; detrás, la barra y las plicas en rojo, y cada plica
    entra en su cabeza, así que la lente la desvía donde la cruza.
  - barra + corcheas (c3, "vitral", como los pétalos de Fotos): la barra es una lámina de
    cristal de color delante y las dos corcheas (plica y cabeza) suben por debajo de ella;
    donde se pisan se mezclan los colores y el borde inferior de la barra dobla las plicas.
La unión de las piezas de cada concepto es exactamente la nota oficial.
Fondos: c1 usa el degradado oficial; c2 y c3 el fondo oscuro de Apple (como los iconos de
Apple en modo oscuro), porque sobre el rojo de marca solo el blanco casi opaco llega a 3:1
y el cristal claro o de color desaparecería en la tecla. Las parejas claras (cNc) usan el
fondo claro de Apple con cristal rojo de marca.
"""
import re

from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union

from brand import place, subpath_shapes
from liquid import ROOT, WHITE, clean, glass, write_icon

D = re.search(r' d="([^"]+)"', (ROOT / "brands" / "applemusic.svg").read_text(encoding="utf-8")).group(1)
FIT = (42.5938, 42.5938, 11.4375, -2.3205)  # escala x, escala y, desplazamiento x, y (lienzo de 1024)

# Medidas de la nota ya ajustada (vértices del trazado oficial en el lienzo de 1024)
STEM_L = (373.4, 412.7)        # plica izquierda: borde exterior e interior (39 px)
STEM_R = (720.4, 759.9)        # plica derecha: borde interior y exterior
SLOPE = -0.2016                # inclinación de la barra; los bordes de arriba de las cabezas son paralelos
BEAM_BOTTOM = (431.4, 377.7)   # punto del borde inferior de la barra
HEAD_CUT_L = (373.4, 625.0)    # corte de la cabeza izquierda: 19 px por encima del chaflán con la plica
HEAD_CUT_R = (720.4, 555.0)    # corte de la cabeza derecha (18 px por encima de su chaflán)
STUB_END_L, STUB_END_R = 745.0, 680.0  # hasta dónde entra cada plica en su cabeza (≈120 px)
RISE = 95.0                    # px que cada plica sube por debajo de la barra (c3)
CORNER = 14                    # px: redondeo de las esquinas que deja cada corte

# Colores
MUSIC_BG_TOP = (1.0, 0.2439, 0.3882)       # degradado del icono oficial, medido arriba y abajo
MUSIC_BG_BOTTOM = (1.0, -0.1118, 0.1647)   # rojo P3, fuera de sRGB (verde negativo en sRGB extendido)
MUSIC_RED = "#FA243C"   # color de marca (pautas de Apple Music)
MUSIC_PINK = "#FF3E62"  # el extremo claro del degradado oficial
MUSIC_DEEP = "#AF192A"  # el rojo de marca oscurecido: el cristal de delante sobre fondo claro


def xsrgb(rgb, alpha=1.0) -> str:
    """Color en sRGB extendido (admite componentes fuera de 0..1, como el rojo P3 de Apple)."""
    return "extended-srgb:" + ",".join(f"{v:.5f}" for v in (*rgb, alpha))


MUSIC_BG = {"linear-gradient": [xsrgb(MUSIC_BG_TOP), xsrgb(MUSIC_BG_BOTTOM)]}


def below(point, slope=SLOPE):
    """Semiplano por debajo (y mayor) de la recta que pasa por point con esa pendiente."""
    x0, y0 = point
    y = lambda x: y0 + slope * (x - x0)  # noqa: E731
    return Polygon([(-200, y(-200)), (1224, y(1224)), (1224, 1300), (-200, 1300)])


def soften(geom, r=CORNER):
    """Redondea las esquinas convexas que deja un corte (no toca las curvas oficiales)."""
    return geom.buffer(-r, quad_segs=64).buffer(r, quad_segs=64)


def stub(stem, end, top=0.0):
    """Tramo de plica acabado en semicírculo: hacia abajo hasta end o, con top, hacia arriba hasta top."""
    r = (stem[1] - stem[0]) / 2
    cx = (stem[0] + stem[1]) / 2
    if top:
        return unary_union([box(stem[0] - 1, top + r, stem[1] + 1, end), Point(cx, top + r).buffer(r, quad_segs=64)])
    return unary_union([box(stem[0] - 1, 500, stem[1] + 1, end - r), Point(cx, end - r).buffer(r, quad_segs=64)])


def solid(geom, min_area=1.0):
    """Quita las astillas de menos de min_area px² que dejan las restas de shapely."""
    return unary_union([p for p in getattr(geom, "geoms", [geom]) if p.area >= min_area])


def pieces():
    nota = place(subpath_shapes(D)[1], *FIT)
    # c2: las cabezas como lentes; el armazón (barra y plicas) detrás, con las plicas dentro
    raw_heads = (nota.intersection(below(HEAD_CUT_L)).intersection(box(0, 0, 470, 1024))
                 .union(nota.intersection(below(HEAD_CUT_R)).intersection(box(470, 0, 1024, 1024))))
    cabezas = soften(raw_heads)  # solo cambia las esquinas del corte, que tapan las plicas de detrás
    stubs = nota.intersection(stub(STEM_L, STUB_END_L).union(stub(STEM_R, STUB_END_R)))
    armazon = solid(nota.difference(raw_heads).union(stubs))
    # c3: la barra de cristal delante; las corcheas suben por debajo y acaban redondas dentro de ella
    above_beam = box(0, 0, 1024, 1024).difference(below(BEAM_BOTTOM))
    barra = soften(nota.intersection(above_beam), r=20)
    y_beam = lambda x: BEAM_BOTTOM[1] + SLOPE * (x - BEAM_BOTTOM[0])  # noqa: E731
    rods = [stub(st, 1024, top=y_beam(sum(st) / 2) - RISE) for st in (STEM_L, STEM_R)]
    corcheas = solid(nota.difference(above_beam).union(nota.intersection(unary_union(rods))))
    return {"nota": nota, "cabezas": cabezas, "armazon": armazon, "barra": barra, "corcheas": corcheas}


# --- c1: el icono de Apple tal cual -------------------------------------------------------
def nota_blanca():
    """Como el icono oficial: nota de cristal blanco esmerilado (el rojo se trasluce un poco).

    Translucidez baja para llegar a 3:1 contra la parte alta del degradado, que es clara.
    """
    return glass("nota", alpha=1.0, translucency=0.25, blur=0.5, refraction=(0.35, 0.3))


def nota_roja():
    """Pareja clara: la nota en cristal rojo de marca con sombra de color."""
    return glass("nota", fill=MUSIC_RED, alpha=1.0, translucency=0.25, blur=0.3,
                 refraction=(0.35, 0.3), shadow="layer-color")


# --- c2: lentes ---------------------------------------------------------------------------
def lentes(fill=WHITE, alpha=0.8, translucency=0.5, shadow="neutral"):
    """Cabezas de cristal sin esmerilar: lentes que desvían la plica roja que entra en ellas.

    Sobre fondo oscuro son de cristal blanco claro; sobre fondo claro, de rojo oscuro de marca
    (un cristal claro sobre fondo claro no llega a 3:1).

    Refracción moderada: la cabeza derecha está a 150 px de la plica izquierda y no debe
    traer trozos suyos a su borde.
    """
    return glass("cabezas", fill=fill, alpha=alpha, translucency=translucency, blur=0.0,
                 refraction=(0.4, 0.2), shadow=shadow, shadow_opacity=0.45, specular="inside")


def armazon(fill=MUSIC_RED):
    """Barra y plicas en cristal rojo de marca, casi opaco (detrás solo dobla el fondo liso)."""
    return glass("armazon", fill=fill, alpha=1.0, translucency=0.25, blur=0.3,
                 refraction=(0.3, 0.2), shadow="layer-color")


# --- c3: vitral ---------------------------------------------------------------------------
def barra(fill=MUSIC_PINK, alpha=0.95, translucency=0.35):
    """Barra como lámina de cristal de color sin esmerilar, con sombra de su color."""
    return glass("barra", fill=fill, alpha=alpha, translucency=translucency, blur=0.0,
                 refraction=(0.4, 0.25), shadow="layer-color", shadow_opacity=0.6)


def corcheas(fill=WHITE):
    """Las dos corcheas en el cristal blanco de la nota oficial (rojo en la pareja clara)."""
    if fill == WHITE:
        return glass("corcheas", alpha=0.95, translucency=0.3, blur=0.4, refraction=(0.3, 0.2))
    return glass("corcheas", fill=fill, alpha=1.0, translucency=0.25, blur=0.3,
                 refraction=(0.3, 0.2), shadow="layer-color")


APPROVED = {}

CONCEPTS = {
    # c1 (fiel): el icono de iOS de Apple, nota de cristal blanco sobre su degradado rojo
    "applemusic-c1": {"fill": MUSIC_BG, "groups": [nota_blanca()]},
    "applemusic-c1c": {"fill": "system-light", "groups": [nota_roja()]},
    # c2 (lentes, Vista Previa): cabezas de cristal claro sobre el armazón rojo, fondo oscuro de Apple
    "applemusic-c2": {"fill": "system-dark", "groups": [lentes(), armazon()]},
    "applemusic-c2c": {"fill": "system-light", "groups": [
        lentes(fill=MUSIC_DEEP, alpha=1.0, translucency=0.35, shadow="layer-color"), armazon()]},
    # c3 (vitral, Fotos): barra de cristal rosa sobre las corcheas blancas, fondo oscuro de Apple
    "applemusic-c3": {"fill": "system-dark", "groups": [barra(), corcheas()]},
    "applemusic-c3c": {"fill": "system-light", "groups": [
        barra(fill=MUSIC_DEEP, alpha=1.0, translucency=0.3), corcheas(MUSIC_RED)]},
}


def main(names=None):
    """Escribe los aprobados; con nombres de concepto, escribe esos para renderizarlos."""
    geo = pieces()
    clean("applemusic")
    targets = {n: n for n in names} if names else APPROVED
    for name, concept in targets.items():
        spec = CONCEPTS[concept]
        write_icon(name, spec["fill"], spec["groups"], geo)


if __name__ == "__main__":
    import sys
    main(sys.argv[1:] or None)
