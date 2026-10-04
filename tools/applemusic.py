"""Apple Music: la nota oficial ajustada al icono de iOS y montaje de los .icon.

Trazado: brands/applemusic.svg (simple-icons 16.34.0, tomado de las pautas de identidad de
Apple Music: el cuadrado redondeado con la nota calada). Solo se usa la nota (su segundo
subtrazado), sin deformar: escala uniforme contra el icono de la App Store (Apple Music,
id 1108187390, "musicCalistoga", 1024 px) con IoU 0.993.

Ronda g (la anterior, c1-c4, era el logo casi opaco y plano: rechazada). Todo es cristal de
color translúcido que deja ver lo de detrás, y cada pieza de cristal pisa algo que doblar:
  - g1 "vitral" (Fotos, vidriera ante la luz): la barra es una lámina de cristal fucsia sin
    esmerilar delante; las dos corcheas (cabeza y plica) son de cristal rojo y sus plicas suben
    125 px por debajo de la barra, que las mezcla y las dobla en su bisel. Detrás, un orbe de
    cristal rosa blanquecino esmerilado (la luz, como el orbe de iTunes) del que asoman la
    esquina de la barra y la cabeza izquierda. Fondo vino casi negro.
  - g2 "ondas" (Buscar): la nota en cristal rosado casi transparente, como el engranaje de
    Discord, sobre tres ondas de sonido concéntricas de cristal rosa-rojo que se apagan hacia
    fuera; la nota tuerce las ondas en su bisel. Fondo oscuro de Apple.
  - g3 "capas" (Cartera): tres copias de la nota apiladas en vertical (36 px), de cristal
    blanco rosado sobre el degradado oficial; cada copia de delante dobla los bordes de la de
    detrás.
Parejas claras (gNc): la misma idea sobre fondo claro, con el cristal en rojos de marca.
Las piezas son siempre trazados de la nota oficial (partidos, copiados o desplazados) y anillos
lisos; el color, el cristal, la luz y la sombra los pone Icon Composer.
Ronda 1 (render): g1 era "lentes" (cabezas de cristal sobre el armazón rojo y un disco de luz):
la refracción honda de las cabezas borraba la plica en vez de doblarla, el borde del disco dejaba
un agujero oscuro en la cabeza izquierda y un triángulo suelto en la esquina de la barra, y el
pico de las cabezas se veía como una gota. g2: la nota blanca al 0.34 se veía gris humo. g3: la
refracción apenas se veía (cristal más claro y más hondo y 36 px entre copias, antes 30).
Ronda 2: g1 fue "núcleo" (fundas de cristal rojo sobre la nota encogida 28 px y encendida): la
refracción honda agrandaba el núcleo hasta el borde y las fundas se veían macizas, como un
caramelo, con picos oscuros en las esquinas. Se cambió por "vitral". g2: la nota pasa a rosa.
Ronda 3: el vitral oscuro (barra fucsia "plus-lighter" sobre corcheas rojas) se veía plano: cristal
de color sobre fondo oscuro liso no enseña nada y la suma de la barra apenas se notaba sobre las
plicas. Ahora las corcheas son el respaldo claro (como la pieza blanca de Steam) y la barra se
mezcla normal. g2: la nota rosa se confundía con las ondas en la tecla; vuelve a rosa blanquecino.
Ronda 4: el vitral con corcheas claras (rosa blanquecino al 0.78 sobre el vino) se veía malva gris,
como plástico. Lo que sí se ve como cristal es el vitral claro (g1c): cristal de color con luz
detrás. En oscuro esa luz la pone ahora el orbe, y las corcheas vuelven a rojo.
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
CORNER = 14                    # px: redondeo de las esquinas que deja cada corte
CENTER = (486.8, 501.7)        # centro de la caja de la nota (213.6-759.9, 154.1-849.3)

# g1: px que cada plica sube por debajo de la barra (la barra mide ~165 px junto a las plicas)
RISE = 125.0
# g1: el orbe de luz; su borde cruza solo piezas anchas: la esquina de arriba a la derecha de la
# barra (asoma 133 x 106 px; cruza su borde de arriba en x 625 y el de la derecha en y 260) y la
# cabeza izquierda (asoma por abajo a la izquierda); las plicas quedan dentro
ORB = ((512, 500), 345)
# g2: ondas (radio exterior, grosor); periodo de 120 px, más que los ~50-100 px que toma el bisel
WAVES = [(165, 48), (285, 48), (405, 48)]
# g3: desplazamiento vertical de cada copia (delante, en medio, detrás): la pila sube hacia atrás
STACK = (36, 0, -36)
# g4: centro de las ondas y del disco de luz; 30 px por debajo del de g2, para que la barra
# doble una banda de onda y no el hueco oscuro que había justo bajo su borde de arriba
RING_C4 = (CENTER[0], CENTER[1] + 30)
DISC_R = 105                   # disco de luz: dentro del hueco de la primera onda (radio 117)
RISE4 = 70.0                   # g4: las plicas acaban hacia la mitad de la barra (165 px)
RISE5 = 30.0                   # g5: un trozo corto, lejos de la esquina de arriba de la barra

# Colores
MUSIC_BG_TOP = (1.0, 0.2439, 0.3882)       # degradado del icono oficial, medido arriba y abajo
MUSIC_BG_BOTTOM = (1.0, -0.1118, 0.1647)   # rojo P3, fuera de sRGB (verde negativo en sRGB extendido)
MUSIC_RED = "#FA243C"   # color de marca (pautas de Apple Music)
MUSIC_PINK = "#FF3E62"  # el extremo claro del degradado oficial
MUSIC_DEEP = "#AF192A"  # el rojo de marca oscurecido: cristal de delante sobre fondo claro
ROSE = "#FF8FA6"        # rosa claro
HOT_PINK = "#FF3D8B"    # rosa fucsia de la barra de g1 (el rosa del icono de Apple Music de 2015)
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


def rod(stem, top):
    """Plica desde top hacia abajo, con la punta de arriba en semicírculo."""
    r = (stem[1] - stem[0]) / 2
    cx = (stem[0] + stem[1]) / 2
    return unary_union([box(stem[0] - 1, top + r, stem[1] + 1, 1024), Point(cx, top + r).buffer(r, quad_segs=64)])


def pieces():
    nota = place(subpath_shapes(D)[1], *FIT)
    # g1: la barra delante; las corcheas (plica y cabeza) suben por debajo hasta RISE px dentro de ella
    beam = nota.intersection(above(BEAM_BOTTOM))
    y_beam = lambda x: BEAM_BOTTOM[1] + SLOPE * (x - BEAM_BOTTOM[0])  # noqa: E731
    rods = unary_union([rod(st, y_beam(sum(st) / 2) - RISE) for st in (STEM_L, STEM_R)])
    geo = {"nota": nota, "barra": soften(beam, r=20),
           "corcheas": solid(nota.difference(beam).union(nota.intersection(rods))),
           "orbe": Point(ORB[0]).buffer(ORB[1], quad_segs=128)}
    # g2: ondas concéntricas en el centro de la nota
    for i, (r, w) in enumerate(WAVES, 1):
        geo[f"onda{i}"] = ring(r, w)
    # g3: copias desplazadas en vertical (la de delante abajo, la de detrás arriba)
    for name, dy in zip(("pila1", "pila2", "pila3"), STACK):
        geo[name] = affinity.translate(nota, 0, dy)
    # g4: ondas más abajo y disco de luz en su centro; g4 y g5: corcheas que suben menos
    for i, (r, w) in enumerate(WAVES, 1):
        geo[f"aro{i}"] = ring(r, w, RING_C4)
    geo["disco"] = Point(RING_C4).buffer(DISC_R, quad_segs=128)
    for key, rise in (("corcheas4", RISE4), ("corcheas5", RISE5)):
        tips = unary_union([rod(st, y_beam(sum(st) / 2) - rise) for st in (STEM_L, STEM_R)])
        geo[key] = solid(nota.difference(beam).union(nota.intersection(tips)))
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


# --- g1: vitral ---------------------------------------------------------------------------
def g1(light=False):
    """Vidriera ante la luz: barra de cristal fucsia sobre las corcheas de cristal rojo.

    Barra: lámina ancha (165 px) sin esmerilar con refracción (0.4, 0.12), sobre los 125 px de
    plica que suben por debajo: donde las pisa, los dos colores se mezclan y el bisel las dobla.
    Corcheas: refracción baja (0.3, 0.08) porque las plicas miden 39 px.
    En oscuro, detrás, el orbe: un disco de cristal rosa blanquecino esmerilado (la luz, como el
    orbe de iTunes) del que asoman la esquina de la barra y la cabeza izquierda: dentro del orbe
    el cristal de color brilla con la luz que lo atraviesa, fuera se ve el vino a través, y el
    bisel dobla el borde del orbe donde lo cruza. En claro la luz es el propio fondo: sin orbe.
    """
    if light:
        return [
            glass("barra", fill=MUSIC_PINK, alpha=0.55, translucency=0.7, blur=0.0,
                  refraction=(0.4, 0.12), shadow="layer-color", shadow_opacity=0.6),
            glass("corcheas", fill=MUSIC_DEEP, alpha=0.7, translucency=0.5, blur=0.1,
                  refraction=(0.3, 0.08), shadow="layer-color", shadow_opacity=0.8, specular="inside"),
        ]
    return [
        glass("barra", fill=HOT_PINK, alpha=0.65, translucency=0.65, blur=0.0,
              refraction=(0.4, 0.12), shadow="layer-color", shadow_opacity=0.6),
        glass("corcheas", fill=MUSIC_RED, alpha=0.75, translucency=0.5, blur=0.05,
              refraction=(0.3, 0.08), shadow="layer-color", shadow_opacity=0.7, specular="inside"),
        group("orbe", [("orbe", grad_fill(WHITE, BLUSH, 0.85))], translucency=0.4, blur=0.6,
              shadow="layer-color", shadow_opacity=0.5),
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
    note = (MUSIC_DEEP, 0.45) if light else (BLUSH, 0.45)
    return [
        glass("nota", fill=note[0], alpha=note[1], translucency=0.85, blur=0.0,
              refraction=(0.35, 0.12), shadow="neutral", shadow_opacity=0.3),
        group("ondas", waves, translucency=0.45, blur=0.35, shadow="layer-color", shadow_opacity=0.6),
    ]


# --- g3: capas ----------------------------------------------------------------------------
def g3(light=False):
    """Tres notas de cristal apiladas (36 px entre una y otra): la de delante, la más clara.

    Cada copia dobla en su bisel los bordes de la de detrás (a 36 px, dentro de lo que toma el
    bisel con (0.4, 0.15)). La de delante sin esmerilar; las de detrás cada vez más esmeriladas.
    Ronda 3: con fuerza 0.5 las plicas de la copia de delante (39 px) tenían un pliegue recto de
    2 px en el centro, donde se juntan los dos biseles; con 0.4 desaparece en oscuro. En claro
    (cristal rojo sobre rosa) seguía marcado con 0.4: ahí (0.3, 0.1).
    """
    if light:
        tints = ((MUSIC_RED, 0.45), (MUSIC_PINK, 0.45), (ROSE, 0.45))
    else:
        tints = ((WHITE, 0.35), (BLUSH, 0.45), (ROSE, 0.45))
    shadow = "layer-color" if light else "neutral"
    return [
        glass("pila1", fill=tints[0][0], alpha=tints[0][1], translucency=0.8, blur=0.0,
              refraction=(0.3, 0.1) if light else (0.4, 0.15), shadow=shadow, shadow_opacity=0.35),
        glass("pila2", fill=tints[1][0], alpha=tints[1][1], translucency=0.65, blur=0.15,
              refraction=(0.4, 0.12), shadow=shadow, shadow_opacity=0.35),
        glass("pila3", fill=tints[2][0], alpha=tints[2][1], translucency=0.6, blur=0.4,
              shadow=shadow, shadow_opacity=0.4),
    ]


# --- ronda h: g4 (ondas, con los arreglos del juez) y g5 (vitral, con sus defectos arreglados) ---
def layer(name, fill, tinted=None):
    """Capa de cristal; tinted: otro relleno solo en el modo tintado (fill-specializations)."""
    lay = {"name": name, "image-name": f"{name}.svg", "glass": True}
    if tinted:
        lay["fill-specializations"] = [{"value": fill}, {"appearance": "tinted", "value": tinted}]
    else:
        lay["fill"] = fill
    return lay


def solo(name, fill, alpha, tinted=None, **kw):
    """glass() de una pieza, con relleno propio en el modo tintado."""
    g = glass(name, fill=fill, alpha=alpha, **kw)
    g["layers"] = [layer(name, {"solid": color(fill, alpha)}, tinted)]
    return g


TINT_NOTE = {"solid": color(WHITE, 0.85)}  # en tintado la nota se perdía: ahí, blanca casi opaca


def g4(light=False):
    """Ondas, segunda versión: la nota en dos cristales sobre ondas de cristal encendidas.

    Delante, la barra de cristal fucsia (0.4, 0.12) sobre los 70 px de plica que suben por debajo
    y sobre la banda de la onda del medio (las ondas bajan 30 px): dentro de la barra se ven dos
    cristales y la onda torcida. Detrás, las corcheas de cristal rosa casi transparente; su
    refracción baja a (0.35, 0.09) para quitar el pliegue del centro de las plicas (39 px). Las
    ondas pasan a cristal claro y encendido (rosa arriba, rojo abajo, apenas esmerilado). Al fondo,
    un disco de luz esmerilado en el centro de las ondas (como el orbe de g1): la plica izquierda
    pasa por encima y dobla su borde. Fondo vino de g1: lo que se ve a través ya no es gris.
    """
    if light:
        bar, note, wave, disc = (HOT_PINK, 0.45), (MUSIC_RED, 0.40), (MUSIC_PINK, MUSIC_RED), (ROSE, MUSIC_PINK)
        alphas, wave_glass, shadow = (0.75, 0.5, 0.32), (0.45, 0.3, 0.45), 0.4
    else:
        bar, note, wave, disc = (HOT_PINK, 0.5), (ROSE, 0.42), (ROSE, MUSIC_RED), (WHITE, BLUSH)
        alphas, wave_glass, shadow = (0.9, 0.7, 0.5), (0.55, 0.1, 0.8), 0.5
    waves = [(f"aro{i}", grad_fill(*wave, a)) for i, a in enumerate(alphas, 1)]
    return [
        solo("barra", *bar, tinted=TINT_NOTE, translucency=0.6, blur=0.0, refraction=(0.4, 0.12),
             shadow="layer-color", shadow_opacity=0.6),
        solo("corcheas4", *note, tinted=TINT_NOTE, translucency=0.75, blur=0.0, refraction=(0.35, 0.09),
             shadow="layer-color", shadow_opacity=shadow),
        group("aros", waves, translucency=wave_glass[0], blur=wave_glass[1], shadow="layer-color",
              shadow_opacity=wave_glass[2]),
        group("disco", [("disco", grad_fill(*disc, 0.75 if light else 0.8))], translucency=0.4,
              blur=0.5 if light else 0.6, shadow="layer-color", shadow_opacity=0.4 if light else 0.5),
    ]


def g5(light=False):
    """Vitral, segunda versión: barra fucsia y corcheas de cristal rojo de verdad transparente.

    Las corcheas bajan de 0.75 a 0.5 de color y suben a 0.7 de translucidez, sin esmerilar: a
    través de ellas se ve el orbe (y el vino donde la cabeza izquierda sale de él). Las plicas
    suben solo 30 px bajo la barra: su punta ya no cae en la esquina de arriba a la derecha (la
    mancha) ni se estira por el bisel de los lados (las gotas). En claro, el orbe es de cristal
    rosa esmerilado sobre el fondo rosado: el cristal rojo tiene por fin algo que doblar.
    """
    if light:
        bar, note, orb = (HOT_PINK, 0.55), (MUSIC_DEEP, 0.5), grad_fill(ROSE, MUSIC_PINK, 0.7)
    else:
        bar, note, orb = (HOT_PINK, 0.65), (MUSIC_RED, 0.5), grad_fill(WHITE, BLUSH, 0.85)
    return [
        solo("barra", *bar, tinted=TINT_NOTE, translucency=0.65, blur=0.0, refraction=(0.4, 0.12),
             shadow="layer-color", shadow_opacity=0.6),
        solo("corcheas5", *note, tinted=TINT_NOTE, translucency=0.7, blur=0.0, refraction=(0.3, 0.08),
             shadow="layer-color", shadow_opacity=0.6, specular="inside"),
        group("orbe", [("orbe", orb)], translucency=0.4, blur=0.6, shadow="layer-color", shadow_opacity=0.5),
    ]


APPROVED = {}

CONCEPTS = {
    # g1 (vitral, Fotos): barra de cristal rosa sobre las corcheas de cristal rojo
    "applemusic-g1": {"fill": WINE_BG, "groups": g1()},
    "applemusic-g1c": {"fill": BLUSH_BG, "groups": g1(light=True)},
    # g2 (ondas, Buscar): nota de cristal casi transparente sobre ondas de sonido de cristal rosa
    "applemusic-g2": {"fill": "system-dark", "groups": g2()},
    "applemusic-g2c": {"fill": "system-light", "groups": g2(light=True)},
    # g3 (capas, Cartera): tres notas de cristal apiladas
    "applemusic-g3": {"fill": MUSIC_BG, "groups": g3()},
    "applemusic-g3c": {"fill": BLUSH_BG, "groups": g3(light=True)},
    # g4 (ondas 2): barra fucsia y corcheas rosas de cristal sobre ondas encendidas y un disco de luz
    "applemusic-g4": {"fill": WINE_BG, "groups": g4()},
    "applemusic-g4c": {"fill": BLUSH_BG, "groups": g4(light=True)},
    # g5 (vitral 2): la nota de cristal de color, transparente de verdad, ante el orbe de luz
    "applemusic-g5": {"fill": WINE_BG, "groups": g5()},
    "applemusic-g5c": {"fill": BLUSH_BG, "groups": g5(light=True)},
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
