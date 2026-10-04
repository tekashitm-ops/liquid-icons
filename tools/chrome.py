"""Google Chrome: logo oficial de 2022 ajustado al icono de iOS, y conceptos de Liquid Glass (g1-g3).

Geometría. El logo de 2022 es geometría pura y simple-icons (brands/googlechrome.svg) solo trae
una silueta monocroma, así que se construye aquí con la definición de Google: un círculo exterior
de radio R, el círculo blanco de radio R/2 y tres fronteras rectas, cada una la mitad de un lado
del triángulo equilátero inscrito en el círculo exterior (son tangentes al círculo blanco). El
círculo azul va centrado. Ajustado por colores contra el icono de la App Store (Google Chrome,
id 535886823, 1024 px): R = 409.25, círculo blanco R/2, azul 166.25, giro 0. IoU por color: rojo
0.991, amarillo 0.983, verde 0.990, azul 0.995, anillo blanco 0.983; silueta completa 0.992.

Para el cristal, los tres colores siguen por debajo del anillo y del azul hasta el centro (el
"remolino"): cada frontera recta se continúa, sin esquina, con un arco que nace tangente en el
círculo blanco y llega al centro, donde las tres se encuentran a 120°. Así el cristal del centro
tiene detrás colores y curvas que su bisel dobla (sobre un color liso la refracción no se ve).

Conceptos (gN oscuro para la tecla, gNc su pareja clara). Todo el logo es cristal de color
translúcido. En oscuro va detrás una luz (un disco blanco plano) para que el cristal brille como
una vidriera; sin ella, el color sobre negro sale oscuro y el amarillo, mostaza. En claro, la luz
es el propio fondo claro. Piezas blancas y planas: el color, el cristal, la luz y las sombras los
pone Icon Composer. Como mucho 4 grupos.
- g1 vitral: los tres colores son vidrios con rendijas de luz que salen del centro; el azul es una
  lente gruesa de cristal azul por la que se ven, doblados, los tres colores y la Y de luz que se
  junta debajo; el anillo es cristal esmerilado.
- g2 lupa: el anillo y el azul son una sola lente gruesa (como la lupa de Vista Previa) sobre el
  remolino: aumenta y dobla los tres colores que se juntan detrás.
- g3 pétalos: como Fotos, el rojo y el verde son pétalos de cristal que se montan sobre el
  amarillo (naranja y lima donde se pisan; el rojo y el verde no se pisan: saldría marrón); el
  centro es un botón de cristal esmerilado.
Lo que enseñaron los renders de CI (rondas 1-4):
- Un grupo delante de otro cristal va sin sombra: la suya oscurecía lo de detrás (el naranja y la
  lima salían rojo oscuro y menta).
- En las esquinas de 60° del borde exterior (donde cada frontera recta llega al círculo), el bisel
  de un borde de cristal toma lo que hay más allá del otro borde: con fondo oscuro, pliegues negros
  ("rizos") a lo largo de la junta (en claro no se ven). Por eso ningún borde de cristal acaba en
  esquina aguda: las rendijas de g1 paran 64 px antes del borde (los vidrios son una pieza,
  lighting combined) y los bordes libres de los pétalos llegan al círculo en ángulo recto.
- El bisel toma lo de ~50 px hacia dentro: una cuña de solape más estrecha sale revuelta (un gancho
  naranja, una gota lima) y en oscuro arrastra la línea oscura que ictool pone junto a cada borde
  (colas negras en el fin de las rendijas). Los pétalos y los vidrios refractan poco y el solape es
  ancho; la refracción profunda queda para las lentes, grandes y redondas.
- Refracción muy profunda (0.85, 0.65) deja bordes con pelusa y colores invertidos en la lente.
- La luz es blanca de arriba abajo: con un degradado a gris el amarillo salía beige.
Los conceptos c1-c5 (logo casi opaco) se rechazaron y quedan en el historial de git.
"""
import math

from shapely.geometry import LineString, Point, Polygon
from shapely.ops import polygonize, unary_union

from liquid import WHITE, clean, color, write_icon

# Medidas en el lienzo de 1024 (ajustadas por colores contra el icono oficial de iOS)
CENTER = (512.0, 512.0)
R = 409.25            # círculo exterior
R_RING = R / 2        # círculo blanco: la mitad exacta, como en el logo oficial
R_BLUE = 166.25       # círculo azul (en iOS algo mayor que el 9.5/24 del SVG de 2022)
ROTATION = 0.0        # grados; el ajuste da -0.2, se deja recto como el oficial
TANGENTS = (270.0, 30.0, 150.0)  # dónde tocan las fronteras el círculo blanco (grados, y hacia abajo)
RES = 256             # segmentos por cuarto de círculo: curvas suaves a cualquier tamaño

# Cristal
GAP = 18              # px de rendija de luz entre los vidrios de g1 (2.5 px en la tecla)
SLIT_END = 64         # px antes del borde exterior donde acaban las rendijas (fin redondo)
LIGHT_INSET = 1.5     # px: la luz llega casi al borde (dentro del cristal: sin halo)
# Grados de anillo que ocupa la base del solape de cada pétalo. Las fronteras giran todas hacia el
# mismo lado, así que el mismo giro da solapes distintos: rojo 22° (79 px en el anillo, 16° en el
# borde exterior), verde 16° (57 px en el anillo, 21° en el borde)
PETAL_RED, PETAL_GREEN = 22.0, 16.0
FILLET = 16           # px de redondeo de las esquinas libres de los pétalos
# g4/g5: vitral abierto
GAP4 = 20.0           # px de rendija abierta, del centro hasta pasado el borde exterior
FILLET4 = 20.0        # px de redondeo de las esquinas de los vidrios (en el borde y en el centro)
LIGHT_R4 = 0.62 * R   # radio de la luz de detrás (oscuro) y de la placa esmerilada (claro)
SPOKE4 = 56.0         # px de ancho de los rayos de luz bajo cada frontera
SPOKE_END4 = 20.0     # px antes del borde exterior donde acaba cada rayo
OVER5 = 32.0          # px de ancho de los solapes de g5 (rojo sobre amarillo, amarillo sobre verde)
HUB4 = R_BLUE + 15    # dentro de este radio (bajo la lente y el anillo) las rendijas son finas y centradas
SLIT4 = 16.0          # px de las rendijas finas de debajo de la lente (una Y de luz, sin cubo en el centro)
JOINT4 = 80.0         # px de redondeo de las juntas entrantes de la luz (disco y rayos)
CORE_INSET4 = 8.0     # px que el fondo de color queda dentro del borde de cada vidrio (no asoma)
# De cada frontera (por su punto de tangencia): el color del casquete, más allá de la recta, y el
# de la esquina, del lado del centro
CAP_OF = {270.0: "rojo", 30.0: "amarillo", 150.0: "verde"}
CORNER_OF = {270.0: "amarillo", 30.0: "verde", 150.0: "rojo"}

# Colores del icono oficial de iOS (mediana del interior de cada pieza): tintes del cristal
RED, YELLOW, GREEN, BLUE = "#F71C1C", "#FFC100", "#00A141", "#0078F3"
# g4/g5: amarillo más limpio (sobre lo oscuro, ámbar y no mostaza) y azul más claro (los lóbulos
# de debajo de la lente se ven más claros: el amarillo bajo el azul salía gris verdoso)
YELLOW4, BLUE4 = "#FFD23F", "#1A7FFF"
# Fondo de color bajo la parte de fuera de cada vidrio (claro), y el ámbar bajo el amarillo (oscuro:
# el cristal amarillo sobre negro sale oliva, ronda g4-1: 148,123,44)
CORE_RED, CORE_AMBER, CORE_GREEN, CORE_AMBER_DARK = "#C8102E", "#F59E00", "#00873C", "#C77800"


def circle(c, r):
    return Point(c).buffer(r, quad_segs=RES)


def annulus(r0, r1):
    return circle(CENTER, r1).difference(circle(CENTER, r0))


def _u(angle):
    return math.cos(math.radians(angle)), math.sin(math.radians(angle))


def _at(r, angle):
    return CENTER[0] + r * _u(angle)[0], CENTER[1] + r * _u(angle)[1]


def _beyond(angle, dist, size=3000):
    """Semiplano más allá de la recta tangente al círculo de radio dist en ese ángulo."""
    ux, uy = _u(angle)
    px, py = -uy, ux
    ox, oy = CENTER[0] + ux * dist, CENTER[1] + uy * dist
    return Polygon([(ox + px * size, oy + py * size), (ox + px * size + ux * size, oy + py * size + uy * size),
                    (ox - px * size + ux * size, oy - py * size + uy * size), (ox - px * size, oy - py * size)])


def _sector(a0, a1, r=2000):
    n = max(8, int(abs(a1 - a0)))
    return Polygon([CENTER] + [_at(r, a0 + (a1 - a0) * i / n) for i in range(n + 1)])


def _arc(r, a0, a1, n=96):
    return [_at(r, a0 + (a1 - a0) * i / n) for i in range(n + 1)]


def _polygons(g):
    """Solo las partes con área (las intersecciones dejan a veces líneas sueltas), soldadas en una."""
    parts = [p for p in getattr(g, "geoms", [g]) if p.geom_type in ("Polygon", "MultiPolygon")]
    g = unary_union([q for p in parts for q in getattr(p, "geoms", [p])])
    return g.buffer(0.05, join_style="mitre").buffer(-0.05, join_style="mitre")


def fillet(g, r=FILLET):
    """Redondea las esquinas, vivas y entrantes: el bisel de cristal no trae esquirlas."""
    return g.buffer(-r, quad_segs=64).buffer(2 * r, quad_segs=64).buffer(-r, quad_segs=64)


def segments():
    """Rojo, amarillo y verde oficiales: el casquete más allá de un lado del triángulo inscrito
    más la esquina del triángulo que queda fuera del círculo blanco."""
    t1, t2, t3 = (a + ROTATION for a in TANGENTS)
    disk, ring = circle(CENTER, R), circle(CENTER, R_RING)
    caps = [disk.intersection(_beyond(a, R_RING)) for a in (t1, t2, t3)]
    corners = disk.difference(unary_union(caps)).difference(ring)
    red = unary_union([caps[0], corners.intersection(_sector(t3, t1))])
    yellow = unary_union([caps[1], corners.intersection(_sector(t1, t2 + 360))])
    green = unary_union([caps[2], corners.intersection(_sector(t2, t3))])
    return {"rojo": _polygons(red), "amarillo": _polygons(yellow), "verde": _polygons(green)}


def boundary(t, reach=900.0, n=720):
    """Frontera entre dos colores, del centro hacia fuera: el arco de radio R_RING/2 que sale del
    centro y llega tangente al círculo blanco en el punto de tangencia, y luego la recta oficial
    (reach px). Sin esquina en el punto de tangencia."""
    rho = R_RING / 2
    cx, cy = CENTER[0] + rho * _u(t)[0], CENTER[1] + rho * _u(t)[1]
    arc = [(cx + rho * _u(t - 180 + 180 * i / n)[0], cy + rho * _u(t - 180 + 180 * i / n)[1]) for i in range(n + 1)]
    dx, dy = _u(t + 90)
    return arc + [(arc[-1][0] + dx * reach, arc[-1][1] + dy * reach)]


def swirl():
    """Los tres colores hasta el centro: el disco exterior cortado por las tres fronteras.
    Fuera del círculo blanco coinciden con los segmentos oficiales."""
    official = segments()
    lines = unary_union([LineString(boundary(t + ROTATION)) for t in TANGENTS] + [circle(CENTER, R).exterior])
    faces = [f for f in polygonize(lines) if f.area > 1000]
    return {name: _polygons(max(faces, key=lambda f: f.intersection(seg).area)) for name, seg in official.items()}


def slits(width, end):
    """g1: las tres fronteras como rendijas de width px, del centro hasta end px antes del borde
    exterior, con el fin redondo (sin esquinas agudas en el borde del cristal)."""
    reach = math.sqrt((R - end) ** 2 - R_RING ** 2)  # la recta es perpendicular al radio en la tangencia
    return unary_union([LineString(boundary(t + ROTATION, reach)).buffer(width / 2, quad_segs=32)
                        for t in TANGENTS])


def free_edge(t, side, base, straight=0.7, n=240):
    """Borde libre de un pétalo que se monta sobre el color vecino de la frontera t (side: +1 o -1,
    hacia el vecino). Sale del círculo blanco base grados más allá del punto de tangencia, paralelo
    a la frontera oficial (girada), sigue recto (straight de su largo) y acaba en un arco de
    círculo ortogonal al círculo exterior: llega al borde en ángulo recto, sin esquina aguda."""
    a = t + side * base
    sx, sy = _at(R_RING, a)
    dx, dy = _u(a + 90)
    length = math.sqrt(R ** 2 - R_RING ** 2)                 # de la tangencia al círculo exterior
    qx, qy = sx + dx * length * straight, sy + dy * length * straight
    ox, oy = qx - CENTER[0], qy - CENTER[1]
    nx, ny = -dy, dx
    if ox * nx + oy * ny < 0:                                # gira hacia fuera
        nx, ny = -nx, -ny
    rho = (R ** 2 - ox * ox - oy * oy) / (2 * (ox * nx + oy * ny))  # ortogonal: |C-O|² = R² + rho²
    cx, cy = qx + rho * nx, qy + rho * ny
    a0 = math.atan2(qy - cy, qx - cx)
    turn = 1 if (math.cos(a0 + 0.01) - math.cos(a0)) * dx + (math.sin(a0 + 0.01) - math.sin(a0)) * dy > 0 else -1
    # punto del arco en el círculo exterior: el ángulo que barre se calcula por bisección
    lo, hi = 0.0, math.pi
    for _ in range(60):
        mid = (lo + hi) / 2
        px, py = cx + rho * math.cos(a0 + turn * mid), cy + rho * math.sin(a0 + turn * mid)
        lo, hi = (mid, hi) if math.hypot(px - CENTER[0], py - CENTER[1]) < R else (lo, mid)
    arc = [(cx + rho * math.cos(a0 + turn * lo * i / n), cy + rho * math.sin(a0 + turn * lo * i / n))
           for i in range(n + 1)]
    return [(sx, sy)] + arc


def overlap(t, side, base, straight=0.7):
    """Zona entre la frontera oficial t y el borde libre del pétalo que la cruza (la cuña que se
    monta sobre el vecino). Toca el círculo blanco por su base y el borde exterior."""
    edge = free_edge(t, side, base, straight)
    ex, ey = edge[-1]
    rim_end = math.degrees(math.atan2(ey - CENTER[1], ex - CENTER[0]))
    v = t + 60
    rim_end += 360 * round((v - rim_end) / 360)               # el mismo giro que el final de la frontera
    pts = [_at(R_RING, t), _at(R, v)] + _arc(R, v, rim_end) + edge[::-1] + _arc(R_RING, t + side * base, t)
    return _polygons(Polygon(pts).buffer(0)).intersection(circle(CENTER, R))


def strip(sw, t, width):
    """Franja de width px a lo largo de toda la frontera t (el arco bajo el anillo y la recta, del
    centro hasta pasado el borde exterior), solo del lado de la esquina. El arco va por dentro del
    círculo blanco (le es tangente por dentro), así que la franja no asoma por fuera del anillo:
    sale de debajo de él en el punto de tangencia."""
    line = LineString(boundary(t + ROTATION, reach=R))
    return _polygons(line.buffer(width, quad_segs=32).intersection(sw[CORNER_OF[t]]))


def spokes(dist):
    """Tres rayos de luz de SPOKE4 px a lo largo de las rectas de las fronteras, con el eje a dist
    px del centro (el de la rendija o el del solape), hasta SPOKE_END4 px antes del borde (fin redondo)."""
    out = []
    for t in TANGENTS:
        (ux, uy), (dx, dy) = _u(t + ROTATION), _u(t + ROTATION + 90)
        ox, oy = CENTER[0] + ux * dist, CENTER[1] + uy * dist
        s = math.sqrt((R - SPOKE_END4) ** 2 - dist ** 2) - SPOKE4 / 2
        out.append(LineString([(ox, oy), (ox + dx * s, oy + dy * s)]).buffer(SPOKE4 / 2, quad_segs=32))
    return unary_union(out)


def light_shape(dist):
    """g4/g5: la luz de detrás, un disco de LIGHT_R4 con los tres rayos. Las juntas entrantes, muy
    redondeadas (JOINT4): con 24 px el bisel de los vidrios las enseñaba como goterones (ronda g4-1)."""
    g = unary_union([circle(CENTER, LIGHT_R4), spokes(dist)])
    return _polygons(g.buffer(JOINT4, quad_segs=64).buffer(-JOINT4, quad_segs=64))


def inner_slits():
    """Bajo la lente (dentro de HUB4): las tres fronteras como rendijas finas centradas (SLIT4), una Y
    de luz. Con la franja de un lado y su cubo, la lente honda los aumentaba en una cara (ronda g4-1)."""
    hub = circle(CENTER, HUB4)
    return unary_union([LineString(boundary(t + ROTATION, reach=R)).buffer(SLIT4 / 2, quad_segs=32)
                        for t in TANGENTS]).intersection(hub)


def gap4(sw, t, width=GAP4):
    """Rendija de la frontera t: de un lado (el de la esquina) fuera de HUB4, fina y centrada dentro."""
    return strip(sw, t, width).difference(circle(CENTER, HUB4))


def panes4(sw):
    """g4: tres vidrios sueltos. Cada frontera es una rendija abierta de GAP4 px hasta pasado el borde
    exterior, que se come el color de la esquina; el del casquete guarda el borde oficial. Bajo la
    lente, las tres rendijas siguen finas: una Y de luz que la lente dobla."""
    gaps = unary_union([gap4(sw, t) for t in TANGENTS] + [inner_slits()])
    return {k: _polygons(fillet(v.difference(gaps), FILLET4)) for k, v in sw.items()}


def panes5(sw):
    """g5: el rojo se monta OVER5 px sobre el amarillo (naranja) y el amarillo sobre el verde (lima),
    en franjas de ancho constante del anillo al borde; la frontera rojo-verde es una rendija abierta
    (el rojo sobre el verde saldría marrón). Bajo la lente, la misma Y de luz que g4."""
    slits = inner_slits()
    band = {t: gap4(sw, t, OVER5) for t in (270.0, 30.0)}
    out = {
        "rojo": unary_union([sw["rojo"].difference(gap4(sw, 150.0)), band[270.0]]),
        "amarillo": unary_union([sw["amarillo"], band[30.0]]),
        "verde": sw["verde"],
    }
    return {k: _polygons(fillet(v.difference(slits), FILLET4)) for k, v in out.items()}


def cores(panes, dist):
    """El fondo de color de fuera de cada vidrio: el vidrio menos la luz (disco y rayos), CORE_INSET4
    px por dentro de su borde para que no asome por las rendijas ni por el borde exterior."""
    lit = light_shape(dist)
    return {k: _polygons(fillet(v.buffer(-CORE_INSET4).difference(lit), FILLET)) for k, v in panes.items()}


def pieces():
    sw = swirl()
    disk = circle(CENTER, R)
    # g3: el rojo se monta sobre el amarillo en la frontera de 270° (hacia más grados) y el verde
    # en la de 30° (hacia menos). El amarillo, debajo, también llega en ángulo recto al borde en su
    # esquina de 60° (la de abajo, bajo el pétalo verde): pierde la cuña que hay hasta ese arco.
    red_over = overlap(270 + ROTATION, +1, PETAL_RED)
    green_over = overlap(30 + ROTATION, -1, PETAL_GREEN)
    yellow_cut = overlap(30 + ROTATION, -1, 0.0)
    red, green = unary_union([sw["rojo"], red_over]), unary_union([sw["verde"], green_over])
    p4, p5 = panes4(sw), panes5(sw)
    return {
        # g2: los tres colores hasta el centro
        **{f"{k}-centro": v for k, v in sw.items()},
        # g1: vidrios con rendijas de luz (acaban antes del borde: los vidrios van en una pieza)
        **{f"vidrio-{k}": _polygons(v.difference(slits(GAP, SLIT_END))) for k, v in sw.items()},
        # g3: pétalos; la junta del rojo y el verde no se redondea (van en una pieza, combined)
        "petalo-rojo": _polygons(unary_union([fillet(red), red.intersection(green.buffer(3 * FILLET))])
                                 .intersection(disk)),
        "petalo-verde": _polygons(unary_union([fillet(green), green.intersection(red.buffer(3 * FILLET))])
                                  .intersection(disk)),
        "petalo-amarillo": _polygons(fillet(sw["amarillo"].difference(yellow_cut)).intersection(disk)),
        "azul": circle(CENTER, R_BLUE),
        "aro": annulus(R_BLUE, R_RING),              # el anillo blanco solo
        "luz": circle(CENTER, R - LIGHT_INSET),      # la luz de detrás del cristal de color
        # g4: vidrios sueltos con rendijas abiertas; g5: dos solapes y una rendija
        **{f"panel-{k}": v for k, v in p4.items()},
        **{f"panel5-{k}": v for k, v in p5.items()},
        "luz4": light_shape(R_RING - GAP4 / 2),      # rayos en el eje de las rendijas
        "luz5": light_shape(R_RING - OVER5 / 2),     # rayos en el eje de los solapes
        # el fondo de color de la parte de fuera de cada vidrio
        **{f"fondo-{k}": v for k, v in cores(p4, R_RING - GAP4 / 2).items()},
        **{f"fondo5-{k}": v for k, v in cores(p5, R_RING - OVER5 / 2).items()},
    }


# --- Grupos y capas con las claves de Icon Composer ----------------------------------------------
def layer(name, image, fill, alpha=1.0, glass=True):
    return {"name": name, "image-name": f"{image}.svg", "glass": glass,
            "fill": {"solid": color(fill, alpha)} if isinstance(fill, str) else fill}


def group(name, layers, translucency, blur, refraction=None, shadow=("none", 0.0), specular=True,
          placement="automatic", lighting="individual"):
    """Un grupo de Liquid Glass (de delante hacia atrás) con todas sus claves a mano."""
    g = {
        "name": name,
        "lighting": lighting,
        "specular": specular,
        "specular-highlight-placement": placement,
        "blur-material": blur,
        "shadow": {"kind": shadow[0], "opacity": shadow[1]},
        "translucency": {"enabled": translucency > 0, "value": translucency},
        "layers": layers,
    }
    if refraction:
        g["refractivity"] = {"enabled": True, "strength": refraction[0], "depth": refraction[1]}
    return g


def light():
    """La luz de detrás (solo en oscuro): disco blanco plano, opaco, sin brillo ni refracción;
    proyecta la sombra del logo sobre el fondo. Blanca de arriba abajo: con un degradado a gris
    (ronda 4) el amarillo de abajo salía beige y el verde, salvia."""
    return group("luz", [layer("luz", "luz", WHITE)], translucency=0.0, blur=0.5, shadow=("neutral", 0.4),
                 specular=False)


def tint(dark):
    """Alfa del color de los tres segmentos. ictool deja ver más lo de detrás abajo que arriba (el
    22% arriba y el 55% abajo con alfa 0.8, medido en la ronda 1): sobre la luz blanca el verde de
    abajo sale menta; en oscuro, algo más de color."""
    return 0.78 if dark else 0.75


def spec(dark, groups):
    if dark:
        return {"fill": "system-dark", "groups": [*groups, light()]}
    return {"fill": "system-light", "groups": groups}


def colors(images, alpha):
    return [layer(k, images.format(k), c, alpha) for k, c in zip(("rojo", "amarillo", "verde"), (RED, YELLOW, GREEN))]


NONE = ("none", 0.0)
BACK_SHADOW = ("layer-color", 0.5)  # en claro, lo de atrás proyecta luz de su color sobre el fondo


# --- g1 vitral ----------------------------------------------------------------------------------
def vitral(dark):
    """Lente azul (refracción profunda: pieza grande y redonda) sobre la Y de luz y los tres colores;
    anillo esmerilado; vidrios en una pieza (combined: el bisel recorre las rendijas y el borde)."""
    lens = group("lente", [layer("azul", "azul", BLUE, 0.75)], translucency=0.55, blur=0.0,
                 refraction=(0.7, 0.5), shadow=("layer-color", 0.3), placement="inside")
    ring = group("anillo", [layer("aro", "aro", WHITE, 0.7)], translucency=0.55, blur=0.35,
                 refraction=(0.3, 0.1), shadow=NONE)
    panes = group("vidrios", colors("vidrio-{}", tint(dark)), translucency=0.6, blur=0.0, refraction=(0.2, 0.06),
                  shadow=NONE if dark else BACK_SHADOW, lighting="combined")
    return spec(dark, [lens, ring, panes])


# --- g2 lupa ------------------------------------------------------------------------------------
def lupa(dark):
    """Una sola lente gruesa: el anillo blanco y el azul juntos (combined), sin esmerilar, sobre el
    remolino; su bisel aumenta y dobla los colores que se juntan detrás. Refracción profunda, pero
    no tanto como (0.85, 0.65), que dejaba pelusa. Los colores, una pieza de cristal (combined)."""
    lens = group("lupa", [layer("azul", "azul", BLUE, 0.72), layer("aro", "aro", WHITE, 0.62)],
                 translucency=0.6, blur=0.0, refraction=(0.6, 0.4), shadow=("neutral", 0.3),
                 lighting="combined")
    segs = group("colores", colors("{}-centro", tint(dark)), translucency=0.6, blur=0.0, refraction=(0.45, 0.2),
                 shadow=NONE if dark else BACK_SHADOW, lighting="combined")
    return spec(dark, [lens, segs])


# --- g3 pétalos ---------------------------------------------------------------------------------
def petalos(dark):
    """Fotos: rojo y verde delante (una pieza: combined, sin bisel en su junta) montados sobre el
    amarillo; refracción suave para que el naranja y la lima se vean en su sitio y solo se doblen
    junto al borde del pétalo. El centro, un botón de cristal esmerilado."""
    center = group("centro", [layer("azul", "azul", BLUE, 0.78), layer("aro", "aro", WHITE, 0.72)],
                   translucency=0.55, blur=0.2, refraction=(0.45, 0.25), shadow=("neutral", 0.25),
                   lighting="combined")
    front = group("rojo-verde", [layer("rojo", "petalo-rojo", RED, tint(dark) - 0.05),
                                 layer("verde", "petalo-verde", GREEN, tint(dark) - 0.05)],
                  translucency=0.6, blur=0.0, refraction=(0.15, 0.05), shadow=NONE, lighting="combined")
    back = group("amarillo", [layer("amarillo", "petalo-amarillo", YELLOW, tint(dark))], translucency=0.6, blur=0.0,
                 refraction=(0.4, 0.15), shadow=NONE if dark else BACK_SHADOW)
    return spec(dark, [center, front, back])


# --- g4 vitral abierto (g5: con solapes) ----------------------------------------------------------
def abierto(dark, overlap=False):
    """g1 con todo el cristal: vidrios sueltos (individual: bisel y brillo propios en cada uno) con
    rendijas abiertas hasta el borde, sobre una luz más pequeña (disco de 0.62 R y tres rayos bajo
    las fronteras): cada vidrio se ve claro sobre la luz y hondo sobre lo oscuro, y su bisel dobla
    el borde de la luz. Lente azul más honda y más clara, que tiñe de azul lo de alrededor.
    En claro, detrás, una placa de cristal esmerilado blanco (su canto y su sombra se ven a través)."""
    five = "5" if overlap else ""
    names = ("rojo", "amarillo", "verde")
    # Lente: (0.85, 0.6) pasa del foco: invertía los lóbulos en tres manchas (una cara) con bordes
    # peinados (ronda g4-1). Azul más lleno: al 0.62 salía celeste pálido (158,201,255)
    lens = group("lente", [layer("azul", "azul", BLUE4, 0.72)], translucency=0.6, blur=0.0,
                 refraction=(0.7, 0.5), shadow=("layer-color", 0.5), placement="inside")
    # Anillo: el injerto de g2, algo de refracción y poco esmerilado (bandas limpias a 2x, ronda g4-1)
    ring = group("anillo", [layer("aro", "aro", WHITE, 0.7)], translucency=0.55, blur=0.15,
                 refraction=(0.45, 0.2), shadow=NONE)
    # Vidrios: en oscuro, su sombra de color tiñe la luz de las rendijas (rosa, ámbar, verde)
    panes = group("vidrios", [layer(k, f"panel{five}-{k}", c, 0.72) for k, c in zip(names, (RED, YELLOW4, GREEN))],
                  translucency=0.6, blur=0.0, refraction=(0.45, 0.2),
                  shadow=("layer-color", 0.4) if dark else BACK_SHADOW)
    if dark:
        # La luz: el disco con rayos, blanco, y el ámbar bajo la parte de fuera del amarillo
        back = group("luz", [layer("ambar", f"fondo{five}-amarillo", CORE_AMBER_DARK, glass=False),
                             layer("luz", f"luz{five or 4}", WHITE, glass=False)],
                     translucency=0.0, blur=0.0, shadow=NONE, specular=False)
        return {"fill": "system-dark", "groups": [lens, ring, panes, back]}
    # Claro: la placa esmerilada blanca (ronda g4-1) no se veía sobre el fondo claro (rojo 249,94,94
    # sobre ella y 250,106,106 fuera). Ahora, bajo la parte de fuera de cada vidrio, su color hondo
    back = group("fondo", [layer(k, f"fondo{five}-{k}", c, glass=False)
                           for k, c in zip(names, (CORE_RED, CORE_AMBER, CORE_GREEN))],
                 translucency=0.0, blur=0.0, shadow=NONE, specular=False)
    return {"fill": "system-light", "groups": [lens, ring, panes, back]}


APPROVED = {}

CONCEPTS = {
    "chrome-g1": vitral(dark=True),
    "chrome-g1c": vitral(dark=False),
    "chrome-g2": lupa(dark=True),
    "chrome-g2c": lupa(dark=False),
    "chrome-g3": petalos(dark=True),
    "chrome-g3c": petalos(dark=False),
    "chrome-g4": abierto(dark=True),
    "chrome-g4c": abierto(dark=False),
    "chrome-g5": abierto(dark=True, overlap=True),
    "chrome-g5c": abierto(dark=False, overlap=True),
}


def main(names=None):
    """Escribe los aprobados; con nombres de concepto, escribe esos para renderizarlos."""
    geo = pieces()
    clean("chrome")
    targets = {n: n for n in names} if names else APPROVED
    for name, concept in targets.items():
        spec = CONCEPTS[concept]
        # Capas a lienzo completo: ictool no recorta la sombra a la caja de cada pieza
        write_icon(name, spec["fill"], spec["groups"], geo, full_bounds=True)


if __name__ == "__main__":
    import sys
    main(sys.argv[1:] or None)
