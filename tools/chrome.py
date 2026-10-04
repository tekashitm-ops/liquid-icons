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

# Colores del icono oficial de iOS (mediana del interior de cada pieza): tintes del cristal
RED, YELLOW, GREEN, BLUE = "#F71C1C", "#FFC100", "#00A141", "#0078F3"


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


APPROVED = {}

CONCEPTS = {
    "chrome-g1": vitral(dark=True),
    "chrome-g1c": vitral(dark=False),
    "chrome-g2": lupa(dark=True),
    "chrome-g2c": lupa(dark=False),
    "chrome-g3": petalos(dark=True),
    "chrome-g3c": petalos(dark=False),
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
