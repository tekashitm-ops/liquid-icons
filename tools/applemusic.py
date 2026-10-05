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

Ronda h (el juez eligió g2 y pidió más; g1-g3 se quedan tal cual para comparar):
  - g4 "ondas 2": g2 con todos los arreglos del juez. Fondo vino (lo que se ve a través de la
    nota ya no es gris); la nota en dos cristales: barra fucsia delante, que tuerce en remolinos
    la onda del medio, y corcheas de cristal rosa casi transparente detrás; ondas de cristal claro
    encendido con brillo de su color; disco de luz esmerilado en su centro, cuyo borde dobla la
    plica izquierda; refracción de las corcheas (0.35, 0.09) contra el pliegue de las plicas.
  - g5 "vitral 2": g1 con sus defectos arreglados y el aro del icono de iTunes 12 alrededor del
    orbe: corcheas transparentes de verdad, plicas que suben solo 30 px bajo la barra (ni mancha
    en la esquina ni gotas) y, en claro, orbe nacarado y aro para que haya algo que doblar.
  En tintado la nota se perdía: barra y corcheas llevan ahí un relleno blanco casi opaco, y el
  orbe uno tenue (fill-specializations, appearance "tinted").
  h1: con 70 px de plica bajo la barra la punta se veía como una gota dentro de ella; las ondas
  de g2 (radios 117, 165, 237) corrían a 3-4 px de las plicas y del borde de la barra (astillas y
  rayas). h2: la punta redonda de 30 px brillaba como un punto en la esquina de la barra sobre las
  ondas (sobre el orbe liso de g5 no se ve): g4 lleva plicas de punta plana de 10 px. h3: ondas
  claras más limpias (sin esmerilar) en g4c; el orbe de g5 en tintado tapaba la nota. h4: la
  esquina de la barra encerraba el vino de fuera de las ondas en un óvalo oscuro (un punto en la
  tecla): ondas recolocadas (ver RING_C4); notas de las parejas claras algo más rojas.
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
# g4: ondas (radio exterior, grosor) y disco de luz, con su centro a la derecha y por debajo del de
# g2 (que es el de la caja de la nota), puestos para que:
#  - ningún borde de círculo vaya casi paralelo a un borde de la nota más de ~37 px a menos de 6 px
#    (h1: los radios 117, 165 y 237 de g2 corrían a 3-4 px de las plicas y del borde de abajo de la
#    barra: astillas y rayas);
#  - ninguno cruce una plica a menos de 18 px del borde de la barra (h2: una gota bajo la barra);
#  - la esquina de arriba a la derecha de la barra (a 456 px del centro) quede solo 28 px fuera de
#    la última onda: con 60-70 px fuera, el bisel de la esquina encerraba el vino en un óvalo oscuro
#    (un punto en la tecla); con poco fuera, la esquina enseña la onda doblada, como en g2;
#  - la barra pise la primera y la segunda onda (remolinos) y el disco pase bajo la plica izquierda.
# h5: con el centro en (495, 525) el borde de fuera de la primera onda (245) se ponía vertical en
# x=740, dentro de la plica derecha (39 px): 3-4 rayas oscuras como gotas a lo largo de ella. Con el
# centro cerca de la nota no hay radios limpios: todo borde de radio 87-151 o 196-260 (desde x=512)
# baja vertical por dentro de una plica, y los de 150-300 rozan el borde de abajo de la barra o
# cruzan una plica justo bajo ella. Ahora las ondas salen de las cabezas, como ondas en el agua:
# centro (512, 780), abajo y en el eje del icono; ahí las ondas cruzan las plicas casi de lado (se
# doblan, no hacen rayas) y cada borde se ha medido con un barrido (a menos de 14 px y 22° de un
# borde de la nota: tramos de 30 px como mucho; ninguno vertical dentro de una plica; ninguno cruza
# una plica a menos de 22 px bajo la barra; ninguno paralelo a la barra a menos de 45 px de su
# borde de abajo, donde el bisel hace una cáustica de puntos: el de dentro de la tercera onda
# corre paralelo a 58 px y el de fuera a 22 px del borde de arriba). La barra pisa la tercera
# onda y la esquina de arriba a la derecha cae dentro de la cuarta; el disco de luz queda entre
# las cabezas y su borde las cruza; el borde de dentro de la primera onda queda 44 px por encima
# del borde de abajo del icono (no hay rendija contra él). Las ondas de fuera se salen del lienzo,
# recortadas a él (como la biela de Steam).
RING_C4 = (512.0, 780.0)
WAVES4 = [(272, 72), (384, 68), (548, 80), (700, 68)]   # huecos de 40, 44, 84 y 84 px
DISC_R = 176   # h6: con 160 el hueco de vino de 40 px hasta la primera onda se veía en las cabezas
               # como grandes remolinos malva oscuro; con 24 px son líneas finas
# g5: px que cada plica sube por debajo de la barra (punta redonda); con 70 la punta se veía dentro
# de la barra como una gota. Con 30 no se ve sobre el orbe liso de g5, pero sobre las ondas de g4
# la punta izquierda brillaba como un punto: g4 lleva plicas de punta plana que suben solo STUB px,
# paralelas al borde de la barra, y la barra redondea sus esquinas de abajo con 8 px y no 20
RISE2 = 30.0
STUB, BAR_R = 10.0, 8
# g5: aro de cristal alrededor del orbe (como el icono de iTunes 12). h5: con 318-385 el borde de
# dentro corría 110 px pegado al borde de abajo de la cabeza derecha (media luna gris): 352-400,
# radios sin tramos paralelos a la nota; el orbe crece a 376 para que su borde siga en el centro
# del aro (con 345 quedaba una raya de vino entre los dos)
HALO = (400, 48)
ORB5_R = 376
# g5: núcleo de luz blanca dentro del orbe, para que la barra tenga algo que doblar por dentro.
# h6: centrado en el orbe (512, 500) y de 190, su borde corría paralelo a la barra a 54 px de su
# borde de abajo y el bisel lo apretaba en una lente con forma de pez. Ahora sube y va un poco a
# la izquierda, hacia la luz (de arriba a la izquierda): su borde pasa a 84 px, por el medio de la
# barra, y el de la derecha a 22 px de la plica derecha (sin media luna), sin tramos paralelos a
# la nota de más de 13 px
NUCLEO_C, NUCLEO_R = (500, 480), 198

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
PEARL = "#FFC9D5"       # g5c: abajo del orbe; uno blanco liso no se veía sobre el fondo rosado
ORB_LOW = "#FF6F8A"     # g5 (h7): abajo del orbe, entre ROSE y MUSIC_PINK: la plica derecha baja de claro a rosa


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
    # g4: ondas más abajo y disco de luz en su centro; g5: aro del orbe; g4 y g5: corcheas que suben menos
    canvas = box(0, 0, 1024, 1024)
    for i, (r, w) in enumerate(WAVES4, 1):
        geo[f"aro{i}"] = Point(RING_C4).buffer(r, quad_segs=256).difference(
            Point(RING_C4).buffer(r - w, quad_segs=256)).intersection(canvas)
    geo["disco"] = Point(RING_C4).buffer(DISC_R, quad_segs=128)
    geo["halo"] = ring(*HALO, ORB[0])
    geo["orbe2"] = Point(ORB[0]).buffer(ORB5_R, quad_segs=128)
    geo["nucleo"] = Point(NUCLEO_C).buffer(NUCLEO_R, quad_segs=128)
    tips = unary_union([rod(st, y_beam(sum(st) / 2) - RISE2) for st in (STEM_L, STEM_R)])
    geo["corcheas2"] = solid(nota.difference(beam).union(nota.intersection(tips)))
    cols = unary_union([box(st[0] - 1, -300, st[1] + 1, 1324) for st in (STEM_L, STEM_R)])
    stubs = nota.intersection(below((BEAM_BOTTOM[0], BEAM_BOTTOM[1] - STUB))).intersection(cols)
    geo["corcheas3"] = solid(nota.difference(beam).union(soften(stubs, r=4)))
    geo["barra2"] = soften(beam, r=BAR_R)
    return geo


def grad_fill(top, bottom, alpha):
    return {"linear-gradient": [color(top, alpha), color(bottom, alpha)]}


def grad_dir(start, stop, a, b):
    """Degradado de (color, alfa) a en start a b en stop (puntos 0-1 del lienzo, como Icon Composer)."""
    return {"linear-gradient": [color(*a), color(*b)],
            "orientation": {"start": {"x": start[0], "y": start[1]}, "stop": {"x": stop[0], "y": stop[1]}}}


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
TINT_BACK = {"solid": color(WHITE, 0.3)}   # y lo de detrás, tenue: el orbe de g5 tapaba la nota


def g4(light=False):
    """Ondas, segunda versión: la nota en dos cristales sobre ondas de cristal encendidas.

    Delante, la barra de cristal fucsia, pieza ancha (165 px) con refracción (0.4, 0.12), sobre la
    tercera y la cuarta onda: las tuerce en remolinos. Detrás, las corcheas de cristal nácar casi
    transparente, con 10 px de plica bajo la barra; su refracción (0.35, 0.09) quita el pliegue del
    centro de las plicas (39 px). Las ondas, de cristal claro encendido (rosa arriba, rojo abajo,
    apenas esmerilado) y con brillo de su color, salen de las cabezas como ondas en el agua (ver
    RING_C4). En su centro, entre las cabezas, un disco de luz: su borde cruza las dos cabezas, que
    lo doblan. Fondo vino de g1: lo que se ve a través de la nota ya no es gris.
    """
    # h5: el disco esmerilado al 0.85 dejaba pasar el vino y se veía gris malva (#cbb3b9): ahora luz
    # casi opaca (translucidez 0.15, esmerilado 0.25), blanca arriba y rosa blanquecino abajo (h6: con
    # nácar #FFC9D5 abajo se quedaba en L 224). Las corcheas
    # rosas tenían el mismo tono y brillo que las ondas y se perdían en la tecla: corcheas nácar y
    # ondas algo más apagadas. En claro, las ondas al 0.42-0.85 dejaban bordes grises y la de fuera
    # casi no se veía: más color (0.64-1.0), brillo de su color y sombra del disco de su color.
    # h7: con (0.35, 0.09) las plicas (39 px) estiraban cada onda que cruzan en vetas oscuras largas,
    # como gotas: (0.28, 0.07) y una pizca de esmerilado (0.04); las cabezas siguen doblando el disco.
    # En claro, el fondo pasa a system-light: sobre un degradado propio ictool deja fuera de cada
    # borde una línea gris malva de 4 px (también en g1c y g3c); sobre system-light, como en g2c y
    # discord-claro, es de 1-2 px y de su color. El disco, nácar abajo para no perderse en él.
    disc_span = ((0.5, 0.6), (0.5, 0.92))   # el degradado del disco ocupa el disco, no el lienzo
    if light:
        bar, note = (HOT_PINK, 0.6), (MUSIC_RED, 0.58)
        # h6: con translucidez 0.4, apenas esmerilado y sin refracción, cada onda dejaba fuera de su
        # borde una línea gris malva de 3-4 px (#c4929b): ahora el cristal de Clyde en discord-claro
        # (aprobado, borde de su color): translucidez 0.35, esmerilado 0.2, refracción (0.35, 0.3)
        wave, alphas, wave_glass = (ROSE, MUSIC_RED), (1.0, 0.88, 0.76, 0.64), (0.35, 0.2, 0.5)
        disc = group("disco", [("disco", grad_dir(*disc_span, (WHITE, 0.95), (PEARL, 0.95)))],
                     translucency=0.3, blur=0.5, shadow="layer-color", shadow_opacity=0.3)
        shadow = 0.4
    else:
        bar, note = (HOT_PINK, 0.5), (PEARL, 0.42)
        wave, alphas, wave_glass = (ROSE, MUSIC_RED), (0.9, 0.76, 0.62, 0.5), (0.45, 0.1, 0.6)
        disc = group("disco", [("disco", grad_dir(*disc_span, (WHITE, 1.0), (BLUSH, 1.0)))],
                     translucency=0.15, blur=0.25, shadow="layer-color", shadow_opacity=0.5)
        shadow = 0.5
    waves = [(f"aro{i}", grad_fill(*wave, a)) for i, a in enumerate(alphas, 1)]
    return [
        solo("barra2", *bar, tinted=TINT_NOTE, translucency=0.6, blur=0.0, refraction=(0.4, 0.12),
             shadow="layer-color", shadow_opacity=0.8),
        solo("corcheas3", *note, tinted=TINT_NOTE, translucency=0.75, blur=0.04, refraction=(0.28, 0.07),
             shadow="layer-color", shadow_opacity=shadow),
        group("aros", waves, translucency=wave_glass[0], blur=wave_glass[1], shadow="layer-color",
              shadow_opacity=wave_glass[2], refraction=(0.35, 0.3) if light else None),
        disc,
    ]


def g5(light=False):
    """Vitral, segunda versión: la nota de cristal de color ante el orbe con su aro (iTunes 12).

    Las corcheas bajan de 0.75 a 0.45 de color y suben a 0.75 de translucidez, sin esmerilar.
    Las plicas suben solo 30 px bajo la barra: su punta ya no cae en la esquina de arriba a la
    derecha (la mancha) ni se estira por el bisel de los lados (las gotas). Detrás del orbe
    esmerilado, un aro de cristal rojo claro que pisa su borde (como el icono de iTunes 12): la
    esquina de la barra y la cabeza izquierda salen del orbe por encima del aro, así que dentro de
    ellas se ven tres cosas (luz, aro, vino) y el bisel dobla los dos bordes. En claro, el mismo
    orbe blanco y el mismo aro sobre el fondo rosado: el cristal rojo tiene por fin algo que doblar.
    """
    # h5: el orbe blanco esmerilado al 0.85 dejaba pasar el vino y se veía gris malva (#cfb8be), las
    # plicas encima eran de un solo tono y la barra no tenía nada que doblar por dentro. Ahora el
    # orbe es luz casi opaca (translucidez 0.15) en degradado vertical rosa (claro arriba, rosa
    # abajo), con un núcleo blanco delante: la barra pisa el borde del núcleo (blanco abajo, rosa
    # arriba) y lo dobla dentro de su bisel; la plica izquierda pasa del blanco al rosa, y la
    # derecha y las cabezas bajan de claro a rosa. Las piezas de la nota son las de g4 (plicas de
    # punta plana de 10 px, barra con esquinas de 8): el borde del núcleo no puede tocar puntas
    # redondas. Corcheas al 0.52 (con 0.45 el vino de fuera del aro se veía como un agujero en la
    # cabeza izquierda; h6: con 0.6, y la barra al 0.65, el núcleo apenas se veía a través: 6 L).
    # En claro, el aro con el cristal de Clyde y fondo system-light (ver g4c) contra la línea gris de
    # su borde. h7: el orbe baja a ORB_LOW (con ROSE la plica derecha era de un solo tono). En claro, el aro se apaga hacia abajo a la izquierda (sin el aire de señal
    # de prohibido de un aro rojo uniforme con una barra cruzada).
    span = ((0.5, 0.12), (0.5, 0.88))   # el degradado ocupa el orbe, no el lienzo
    if light:
        bar, note, shadow = (HOT_PINK, 0.45), (MUSIC_RED, 0.52), "layer-color"
        orb = grad_dir(*span, (BLUSH, 1.0), (ORB_LOW, 1.0))
        halo = grad_dir((0.85, 0.1), (0.2, 0.9), (MUSIC_RED, 1.0), (ROSE, 0.45))
    else:
        bar, note, shadow = (HOT_PINK, 0.5), (MUSIC_RED, 0.52), "layer-color"
        orb = grad_dir(*span, (BLUSH, 1.0), (ORB_LOW, 1.0))
        halo = grad_fill(ROSE, MUSIC_RED, 0.9)
    return [
        solo("barra2", *bar, tinted=TINT_NOTE, translucency=0.75, blur=0.0, refraction=(0.4, 0.12),
             shadow="layer-color", shadow_opacity=0.6),
        solo("corcheas3", *note, tinted=TINT_NOTE, translucency=0.75, blur=0.0, refraction=(0.3, 0.08),
             shadow="layer-color", shadow_opacity=0.6, specular="inside"),
        group("halo", [("halo", halo)], translucency=0.35 if light else 0.5, blur=0.2 if light else 0.1,
              refraction=(0.35, 0.12), shadow="layer-color", shadow_opacity=0.5 if light else 0.7),
        dict(group("orbe", [], translucency=0.15, blur=0.3, shadow=shadow, shadow_opacity=0.4),
             layers=[layer("nucleo", {"solid": color(WHITE, 1.0)}, TINT_BACK), layer("orbe2", orb, TINT_BACK)]),
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
    "applemusic-g4c": {"fill": "system-light", "groups": g4(light=True)},
    # g5 (vitral 2): la nota de cristal de color, transparente de verdad, ante el orbe de luz
    "applemusic-g5": {"fill": WINE_BG, "groups": g5()},
    "applemusic-g5c": {"fill": "system-light", "groups": g5(light=True)},
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
