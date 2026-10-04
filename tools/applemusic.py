"""Apple Music: la nota oficial ajustada al icono de iOS y montaje de los .icon.

Trazado: brands/applemusic.svg (simple-icons 16.34.0, tomado de las pautas de identidad de
Apple Music: el cuadrado redondeado con la nota calada). Solo se usa la nota (su segundo
subtrazado), sin deformar: escala uniforme contra el icono de la App Store (Apple Music,
id 1108187390, "musicCalistoga", 1024 px) con IoU 0.993.

Ronda g (la anterior, c1-c4, era el logo casi opaco y plano: rechazada). Todo es cristal de
color translúcido que deja ver lo de detrás, y cada pieza de cristal pisa algo que doblar:
  - g1 "núcleo": la barra y las cabezas son fundas de cristal rojo translúcido; dentro brilla
    un núcleo rosa (la misma nota encogida 28 px) unido por las plicas, que quedan al aire.
    El bisel de cada funda dobla y agranda el borde del núcleo. Fondo vino casi negro.
  - g2 "ondas" (Buscar): la nota en cristal rosado casi transparente, como el engranaje de
    Discord, sobre tres ondas de sonido concéntricas de cristal rosa-rojo que se apagan hacia
    fuera; la nota tuerce las ondas en su bisel. Fondo oscuro de Apple.
  - g3 "capas" (Cartera): tres copias de la nota apiladas en vertical (36 px), de cristal
    blanco rosado sobre el degradado oficial; cada copia de delante dobla los bordes de la de
    detrás.
Parejas claras (gNc): la misma idea sobre fondo claro, con el cristal en rojos de marca.
Las piezas son siempre trazados de la nota oficial (partidos, encogidos, copiados o
desplazados) y anillos lisos; el color, el cristal, la luz y la sombra los pone Icon Composer.
Ronda 1 (render): g1 era "lentes" (cabezas de cristal sobre el armazón rojo y un disco de luz):
la refracción honda de las cabezas borraba la plica en vez de doblarla, el borde del disco dejaba
un agujero oscuro en la cabeza izquierda y un triángulo suelto en la esquina de la barra, y el
pico de las cabezas (el trozo de plica sobre el chaflán) se veía como una gota. Se cambió por
"núcleo". g2: la nota blanca al 0.34 se veía gris humo; ahora rosada al 0.4. g3: cristal más
claro y más hondo y 36 px entre copias (antes 30), porque la refracción apenas se veía.
"""
import re

from shapely import affinity
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union

from brand import place, subpath_shapes
from liquid import ROOT, WHITE, clean, color, glass, write_icon

D = re.search(r' d="([^"]+)"', (ROOT / "brands" / "applemusic.svg").read_text(encoding="utf-8")).group(1)
FIT = (42.5938, 42.5938, 11.4375, -2.3205)  # escala x, escala y, desplazamiento x, y (lienzo de 1024)

# Medidas de la nota ya ajustada (vértices del trazado oficial en el lienzo de 1024)
STEM_L = (373.4, 412.7)        # plica izquierda: borde exterior e interior (39 px)
STEM_R = (720.4, 759.9)        # plica derecha: borde interior y exterior
SLOPE = -0.2016                # inclinación de la barra; los bordes de arriba de las cabezas son paralelos
BEAM_BOTTOM = (431.4, 377.7)   # punto del borde inferior de la barra
HEAD_CUT = (373.4, 648.0)      # donde empieza el chaflán de cada cabeza (x 373 y 648; x 720 y 578):
                               # una sola recta paralela a la barra corta las dos sin dejar pico
CORNER = 14                    # px: redondeo de las esquinas que deja cada corte
CENTER = (486.8, 501.7)        # centro de la caja de la nota (213.6-759.9, 154.1-849.3)

# g1: grosor de la funda de cristal alrededor del núcleo (4 px en la tecla de 144 px)
INSET = 28
# g2: ondas (radio exterior, grosor); periodo de 120 px, más que los ~50-100 px que toma el bisel
WAVES = [(165, 48), (285, 48), (405, 48)]
# g3: desplazamiento vertical de cada copia (delante, en medio, detrás): la pila sube hacia atrás
STACK = (36, 0, -36)

# Colores
MUSIC_BG_TOP = (1.0, 0.2439, 0.3882)       # degradado del icono oficial, medido arriba y abajo
MUSIC_BG_BOTTOM = (1.0, -0.1118, 0.1647)   # rojo P3, fuera de sRGB (verde negativo en sRGB extendido)
MUSIC_RED = "#FA243C"   # color de marca (pautas de Apple Music)
MUSIC_PINK = "#FF3E62"  # el extremo claro del degradado oficial
MUSIC_DEEP = "#AF192A"  # el rojo de marca oscurecido: cristal de delante sobre fondo claro
ROSE = "#FF8FA6"        # rosa claro
GLOW = "#FFA3B6"        # rosa encendido del núcleo de g1
BLUSH = "#FFD6DF"       # rosa blanquecino: el cristal casi transparente de g2 y la pila de g3
WINE_TOP, WINE_BOTTOM = "#3E0816", "#120207"    # fondo de g1: vino casi negro
BLUSH_TOP, BLUSH_BOTTOM = "#FFF6F8", "#FFE2E9"  # fondo claro rosado de g1c y g3c


def xsrgb(rgb, alpha=1.0) -> str:
    """Color en sRGB extendido (admite componentes fuera de 0..1, como el rojo P3 de Apple)."""
    return "extended-srgb:" + ",".join(f"{v:.5f}" for v in (*rgb, alpha))


MUSIC_BG = {"linear-gradient": [xsrgb(MUSIC_BG_TOP), xsrgb(MUSIC_BG_BOTTOM)]}
WINE_BG = {"linear-gradient": [color(WINE_TOP), color(WINE_BOTTOM)]}
BLUSH_BG = {"linear-gradient": [color(BLUSH_TOP), color(BLUSH_BOTTOM)]}


def below(point, slope=SLOPE):
    """Semiplano por debajo (y mayor) de la recta que pasa por point con esa pendiente."""
    x0, y0 = point
    y = lambda x: y0 + slope * (x - x0)  # noqa: E731
    return Polygon([(-200, y(-200)), (1224, y(1224)), (1224, 1300), (-200, 1300)])


def above(point, slope=SLOPE):
    return box(-200, -300, 1224, 1324).difference(below(point, slope))


def soften(geom, r=CORNER):
    """Redondea las esquinas convexas que deja un corte (no toca las curvas oficiales)."""
    return geom.buffer(-r, quad_segs=64).buffer(r, quad_segs=64)


def solid(geom, min_area=1.0):
    """Quita las astillas de menos de min_area px² que dejan las restas de shapely."""
    return unary_union([p for p in getattr(geom, "geoms", [geom]) if p.area >= min_area])


def ring(r_out, width, c=CENTER):
    return Point(c).buffer(r_out, quad_segs=128).difference(Point(c).buffer(r_out - width, quad_segs=128))


def shift(point, dy):
    return point[0], point[1] + dy


def pieces():
    nota = place(subpath_shapes(D)[1], *FIT)
    # g1: fundas (barra y cabezas) y núcleo (la nota encogida + las plicas que las unen)
    barra_raw = nota.intersection(above(BEAM_BOTTOM))
    cabezas_raw = nota.intersection(below(HEAD_CUT))
    stems = box(STEM_L[0] - 1, 0, STEM_L[1] + 1, 1024).union(box(STEM_R[0] - 1, 0, STEM_R[1] + 1, 1024))
    # las plicas entran en cada funda hasta tocar el núcleo: INSET + 12 px en la barra y INSET + 40
    # en las cabezas (junto a la plica, el núcleo de la cabeza empieza ~46 px por debajo del corte)
    links = stems.intersection(nota).intersection(below(shift(BEAM_BOTTOM, -INSET - 12))).intersection(
        above(shift(HEAD_CUT, INSET + 40)))
    nucleo = soften(solid(unary_union([nota.buffer(-INSET, quad_segs=64), links])), r=8)
    geo = {"nota": nota, "barra": soften(barra_raw, r=20), "cabezas": soften(cabezas_raw), "nucleo": nucleo}
    # g2: ondas concéntricas en el centro de la nota
    for i, (r, w) in enumerate(WAVES, 1):
        geo[f"onda{i}"] = ring(r, w)
    # g3: copias desplazadas en vertical (la de delante abajo, la de detrás arriba)
    for name, dy in zip(("pila1", "pila2", "pila3"), STACK):
        geo[name] = affinity.translate(nota, 0, dy)
    return geo


def grad_fill(top, bottom, alpha):
    return {"linear-gradient": [color(top, alpha), color(bottom, alpha)]}


def group(name, layers, lighting="individual", blend=None, **kw):
    """Grupo de Liquid Glass con varias piezas [(pieza, relleno)], de delante hacia atrás.

    Con las claves de Icon Composer que glass() no pone: lighting y blend-mode del grupo.
    """
    g = glass(name, **kw)
    g["lighting"] = lighting
    g["layers"] = [{"name": n, "image-name": f"{n}.svg", "glass": True, "fill": f} for n, f in layers]
    if blend:
        g["blend-mode"] = blend
    return g


# --- g1: núcleo ---------------------------------------------------------------------------
def g1(light=False):
    """Fundas de cristal rojo sin esmerilar (barra y cabezas) sobre un núcleo rosa encendido.

    Fundas: piezas anchas (barra 160 px, cabezas 200 px) sin partes finas, así que aguantan una
    refracción honda (0.5, 0.2): el bisel toma lo que hay a ~70 px hacia dentro, el núcleo, y lo
    agranda hasta el borde. Las plicas (39 px) son del núcleo, que no refracta: sin astillas.
    Núcleo: cristal esmerilado con sombra de su color (el resplandor); es el respaldo iluminado
    que doblan las fundas, y en las plicas se ve tal cual.
    """
    if light:
        case, core = (MUSIC_DEEP, 0.45), (MUSIC_RED, 0.9)
    else:
        case, core = (MUSIC_RED, 0.5), (GLOW, 0.92)
    return [
        group("fundas", [("barra", {"solid": color(*case)}), ("cabezas", {"solid": color(*case)})],
              translucency=0.7, blur=0.0, refraction=(0.5, 0.2), shadow="layer-color", shadow_opacity=0.5,
              specular="inside"),
        glass("nucleo", fill=core[0], alpha=core[1], translucency=0.35, blur=0.5,
              shadow="layer-color", shadow_opacity=0.9),
    ]


# --- g2: ondas ----------------------------------------------------------------------------
def g2(light=False):
    """Nota de cristal casi transparente (como el engranaje de Discord) sobre ondas de cristal rosa.

    Las ondas, de dentro afuera cada vez más tenues, en un solo grupo esmerilado y con sombra de
    su color; la nota delante, sin esmerilar, las tuerce en el bisel. Refracción (0.35, 0.12): la
    nota tiene plicas de 39 px; las ondas tienen periodo de 120 px, así que el bisel siempre
    encuentra un borde que doblar.
    """
    alphas = (0.75, 0.5, 0.32)
    waves = [(f"onda{i}", grad_fill(MUSIC_PINK, MUSIC_RED, a)) for i, a in enumerate(alphas, 1)]
    note = (MUSIC_DEEP, 0.45) if light else (BLUSH, 0.4)
    return [
        glass("nota", fill=note[0], alpha=note[1], translucency=0.85, blur=0.0,
              refraction=(0.35, 0.12), shadow="neutral", shadow_opacity=0.3),
        group("ondas", waves, translucency=0.45, blur=0.35, shadow="layer-color", shadow_opacity=0.6),
    ]


# --- g3: capas ----------------------------------------------------------------------------
def g3(light=False):
    """Tres notas de cristal apiladas (36 px entre una y otra): la de delante, la más clara.

    Cada copia dobla en su bisel los bordes de la de detrás (a 36 px, dentro de lo que toma el
    bisel con (0.5, 0.18)). La de delante sin esmerilar; las de detrás cada vez más esmeriladas.
    """
    if light:
        tints = ((MUSIC_RED, 0.45), (MUSIC_PINK, 0.45), (ROSE, 0.45))
    else:
        tints = ((WHITE, 0.35), (BLUSH, 0.45), (ROSE, 0.45))
    shadow = "layer-color" if light else "neutral"
    return [
        glass("pila1", fill=tints[0][0], alpha=tints[0][1], translucency=0.8, blur=0.0,
              refraction=(0.5, 0.18), shadow=shadow, shadow_opacity=0.35),
        glass("pila2", fill=tints[1][0], alpha=tints[1][1], translucency=0.65, blur=0.15,
              refraction=(0.4, 0.12), shadow=shadow, shadow_opacity=0.35),
        glass("pila3", fill=tints[2][0], alpha=tints[2][1], translucency=0.6, blur=0.4,
              shadow=shadow, shadow_opacity=0.4),
    ]


APPROVED = {}

CONCEPTS = {
    # g1 (núcleo): fundas de cristal rojo que agrandan un núcleo rosa encendido
    "applemusic-g1": {"fill": WINE_BG, "groups": g1()},
    "applemusic-g1c": {"fill": BLUSH_BG, "groups": g1(light=True)},
    # g2 (ondas, Buscar): nota de cristal casi transparente sobre ondas de sonido de cristal rosa
    "applemusic-g2": {"fill": "system-dark", "groups": g2()},
    "applemusic-g2c": {"fill": "system-light", "groups": g2(light=True)},
    # g3 (capas, Cartera): tres notas de cristal apiladas
    "applemusic-g3": {"fill": MUSIC_BG, "groups": g3()},
    "applemusic-g3c": {"fill": BLUSH_BG, "groups": g3(light=True)},
}


def main(names=None):
    """Escribe los aprobados; con nombres de concepto, escribe esos para renderizarlos.

    Capas a lienzo completo (full_bounds): ictool recorta la sombra de cada capa a la caja de
    su contenido y deja costuras rectas de 1 px.
    """
    geo = pieces()
    clean("applemusic")
    targets = {n: n for n in names} if names else APPROVED
    for name, concept in targets.items():
        spec = CONCEPTS[concept]
        write_icon(name, spec["fill"], spec["groups"], geo, full_bounds=True)


if __name__ == "__main__":
    import sys
    main(sys.argv[1:] or None)
