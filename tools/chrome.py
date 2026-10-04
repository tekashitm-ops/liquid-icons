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
círculo blanco y llega al centro, donde las tres se encuentran a 120°. Así cada cristal del centro
tiene detrás colores y curvas que su bisel dobla (sobre un color liso la refracción no se ve).

Conceptos (gN oscuro para la tecla, gNc su pareja clara). Todo el logo es cristal de color
translúcido; detrás del cristal de color va una luz (un disco blanco plano) para que brille
como una vidriera sobre el fondo oscuro. Piezas blancas y planas: el color, el cristal, la luz
y las sombras los pone Icon Composer. Como mucho 4 grupos.
- g1 vitral: los tres colores son vidrios separados por rendijas de luz que llegan al centro;
  el azul es una lente gruesa de cristal azul por la que se ven, doblados, los tres colores y
  las rendijas que se juntan debajo; el anillo es cristal esmerilado.
- g2 lupa: el anillo y el centro son una sola lente gruesa de cristal transparente (como la lupa
  de Vista Previa) que aumenta lo que tiene detrás: el disco azul de cristal y los tres colores.
- g3 pétalos: como Fotos, el rojo y el verde son pétalos de cristal que se montan sobre el
  amarillo (naranja y lima donde se pisan; el rojo y el verde no se pisan: saldría marrón) y el
  centro es un botón de cristal (anillo y azul en una pieza) sobre el remolino de colores.
Los conceptos c1-c5 (logo casi opaco) se rechazaron y quedan en el historial de git.
"""
import math

from shapely import affinity
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
FILLET = 24           # px de redondeo de las esquinas: las de 60° del borde exterior traían pliegues
LIGHT_INSET = 1.5     # px: la luz llega casi al borde (dentro del cristal: sin halo). Si acaba antes,
                      # el bisel de las esquinas de 60° toma el fondo oscuro y salen pliegues negros
PETAL = 16.0          # grados que el rojo y el verde se montan sobre el amarillo en g3 (~114 px fuera)
LENS_OVER = 30        # px que la lupa de g2 sobresale del anillo blanco (su borde dobla los colores)

# Colores del icono oficial de iOS (mediana del interior de cada pieza) y tintes del cristal
RED, YELLOW, GREEN, BLUE = "#F71C1C", "#FFC100", "#00A141", "#0078F3"


def circle(c, r):
    return Point(c).buffer(r, quad_segs=RES)


def annulus(r0, r1):
    return circle(CENTER, r1).difference(circle(CENTER, r0))


def _u(angle):
    return math.cos(math.radians(angle)), math.sin(math.radians(angle))


def _beyond(angle, dist, size=3000):
    """Semiplano más allá de la recta tangente al círculo de radio dist en ese ángulo."""
    ux, uy = _u(angle)
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


def boundary(t, n=720):
    """Frontera entre dos colores, del centro hacia fuera: el arco de radio R_RING/2 que sale del
    centro y llega tangente al círculo blanco en el punto de tangencia, y luego la recta oficial
    hasta más allá del círculo exterior. Sin esquina en el punto de tangencia."""
    rho = R_RING / 2
    cx, cy = CENTER[0] + rho * _u(t)[0], CENTER[1] + rho * _u(t)[1]
    arc = [(cx + rho * _u(t - 180 + 180 * i / n)[0], cy + rho * _u(t - 180 + 180 * i / n)[1]) for i in range(n + 1)]
    dx, dy = _u(t + 90)
    return arc + [(arc[-1][0] + dx * 900, arc[-1][1] + dy * 900)]


def swirl():
    """Los tres colores hasta el centro: el disco exterior cortado por las tres fronteras.
    Fuera del círculo blanco coinciden con los segmentos oficiales."""
    official = segments()
    lines = unary_union([LineString(boundary(t + ROTATION)) for t in TANGENTS] + [circle(CENTER, R).exterior])
    faces = [f for f in polygonize(lines) if f.area > 1000]
    out = {}
    for name, seg in official.items():
        out[name] = _polygons(max(faces, key=lambda f: f.intersection(seg).area))
    return out


def gaps(width):
    """Las tres fronteras como rendijas de width px, de la punta del centro al borde."""
    return unary_union([LineString(boundary(t + ROTATION)).buffer(width / 2, cap_style="flat", quad_segs=32)
                        for t in TANGENTS])


def overlap_wedge(piece, into, degrees, r_min):
    """Cuña de piece que se monta sobre into: piece girada sobre el centro, recortada con into.
    Girar mantiene la frontera tangente al círculo blanco; la cuña nace bajo el anillo (r_min)."""
    wedges = [affinity.rotate(piece, s * degrees, origin=CENTER).intersection(into) for s in (1, -1)]
    return max(wedges, key=lambda w: w.area).intersection(annulus(r_min, R))


def petal_fillets(petals):
    """Esquinas redondeadas en los pétalos, menos en la junta del rojo y el verde: van en una sola
    pieza de cristal (combined), sin bisel ahí; redondearla abriría una muesca en el borde."""
    red, green = petals["rojo"], petals["verde"]
    return {
        "rojo": unary_union([fillet(red), red.intersection(green.buffer(3 * FILLET))]),
        "verde": unary_union([fillet(green), green.intersection(red.buffer(3 * FILLET))]),
        "amarillo": fillet(petals["amarillo"]),
    }


def pieces():
    sw = swirl()
    disk = circle(CENTER, R)
    vidrio = {k: _polygons(fillet(v.difference(gaps(GAP)).intersection(disk))) for k, v in sw.items()}
    petals = {
        "rojo": unary_union([sw["rojo"], overlap_wedge(sw["rojo"], sw["amarillo"], PETAL, R_RING - 16)]),
        "verde": unary_union([sw["verde"], overlap_wedge(sw["verde"], sw["amarillo"], PETAL, R_RING - 16)]),
        "amarillo": sw["amarillo"],
    }
    return {
        # Los tres colores hasta el centro (g2)
        **{f"{k}-centro": v for k, v in sw.items()},
        # g1: vidrios con rendijas de luz entre ellos
        **{f"vidrio-{k}": v for k, v in vidrio.items()},
        # g3: el rojo y el verde con la cuña que se monta sobre el amarillo
        **{f"petalo-{k}": _polygons(v.intersection(disk)) for k, v in petal_fillets(petals).items()},
        "azul": circle(CENTER, R_BLUE),
        "aro": annulus(R_BLUE, R_RING),              # el anillo blanco solo
        "lupa": circle(CENTER, R_RING + LENS_OVER),  # g2: la lente, algo mayor que el anillo
        "luz": circle(CENTER, R - LIGHT_INSET),      # la luz de detrás del cristal de color
    }


# --- Grupos y capas con las claves de Icon Composer ----------------------------------------------
def layer(name, image, fill, alpha=1.0, glass=True, blend=None, opacity=None):
    out = {"name": name, "image-name": f"{image}.svg", "glass": glass,
           "fill": {"solid": color(fill, alpha)} if isinstance(fill, str) else fill}
    if blend:
        out["blend-mode"] = blend
    if opacity is not None:
        out["opacity"] = opacity
    return out


def group(name, layers, translucency, blur, refraction=None, shadow=("none", 0.0), specular=True,
          placement="automatic", lighting="individual", blend=None, opacity=None):
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
    if blend:
        g["blend-mode"] = blend
    if opacity is not None:
        g["opacity"] = opacity
    return g


def light(shadow=("neutral", 0.35)):
    """La luz de detrás: disco blanco plano, opaco, sin brillo ni refracción; da la sombra del logo."""
    return group("luz", [layer("luz", "luz", WHITE)], translucency=0.0, blur=0.5, shadow=shadow,
                 specular=False)


def tri(images, tints, alpha):
    return [layer(k, f"{k}-centro" if images == "centro" else f"{images}-{k}", c, alpha)
            for k, c in zip(("rojo", "amarillo", "verde"), tints)]


def spec(dark, groups):
    """Oscuro: la luz detrás de todo (sin ella el cristal de color sobre negro sale oscuro y el
    amarillo, mostaza). Claro: el fondo claro ya es la luz; lo de atrás proyecta su sombra de
    color sobre él."""
    if dark:
        return {"fill": "system-dark", "groups": [*groups, light()]}
    return {"fill": "system-light", "groups": groups}


# Sombras: un grupo delante de otro cristal va sin sombra (la suya oscurecía lo de detrás: el
# naranja y la lima de los pétalos salían rojo oscuro y menta); solo lo de atrás la proyecta.
NONE = ("none", 0.0)


# --- g1 vitral ----------------------------------------------------------------------------------
def vitral(dark, placement="automatic", pane_refraction=(0.4, 0.18)):
    """Lente azul (refracción profunda: pieza grande y redonda), anillo esmerilado, vidrios con
    rendijas y la luz detrás. La lente ve debajo los tres colores y las rendijas juntándose."""
    lens = group("lente", [layer("azul", "azul", BLUE, 0.74)], translucency=0.55, blur=0.0,
                 refraction=(0.7, 0.5), shadow=("layer-color", 0.3), placement="inside")
    ring = group("anillo", [layer("aro", "aro", WHITE, 0.72)], translucency=0.55, blur=0.35,
                 refraction=(0.3, 0.1), shadow=NONE)
    panes = group("vidrios", tri("vidrio", (RED, YELLOW, GREEN), 0.78 if dark else 0.82), translucency=0.55,
                  blur=0.0, refraction=pane_refraction, shadow=NONE if dark else ("layer-color", 0.45),
                  placement=placement)
    return spec(dark, [lens, ring, panes])


# --- g2 lupa ------------------------------------------------------------------------------------
def lupa(dark):
    """Vista Previa: una lupa de cristal transparente, algo mayor que el anillo, sobre el anillo y
    el azul (cristal esmerilado) y los colores (una sola pieza de cristal: lighting combined, sin
    biseles en las juntas). Refracción muy profunda: su borde aumenta y dobla lo de debajo."""
    lens = group("lupa", [layer("lupa", "lupa", WHITE, 0.1)], translucency=0.85, blur=0.0,
                 refraction=(0.85, 0.65), shadow=("neutral", 0.25))
    core = group("centro", [layer("azul", "azul", BLUE, 0.8), layer("aro", "aro", WHITE, 0.8)],
                 translucency=0.5, blur=0.3, refraction=(0.35, 0.15), shadow=NONE)
    segs = group("colores", tri("centro", (RED, YELLOW, GREEN), 0.78 if dark else 0.82), translucency=0.55,
                 blur=0.0, refraction=(0.45, 0.2), shadow=NONE if dark else ("layer-color", 0.45),
                 lighting="combined")
    return spec(dark, [lens, core, segs])


def lupa_tintada(dark):
    """Prueba para g2: la lente es el anillo blanco y el azul juntos (combined), sin disco azul
    detrás; por ella se ven los colores juntándose en el centro."""
    lens = group("lupa", [layer("azul", "azul", BLUE, 0.62), layer("aro", "aro", WHITE, 0.6)],
                 translucency=0.6, blur=0.0, refraction=(0.85, 0.65), shadow=("layer-color", 0.3),
                 lighting="combined")
    segs = group("colores", tri("centro", (RED, YELLOW, GREEN), 0.78 if dark else 0.82), translucency=0.55,
                 blur=0.0, refraction=(0.45, 0.2), shadow=NONE if dark else ("layer-color", 0.45),
                 lighting="combined")
    return spec(dark, [lens, segs])


# --- g3 pétalos ---------------------------------------------------------------------------------
def petalos(dark):
    """Fotos: rojo y verde delante (una pieza: combined, sin bisel en su junta), montados sobre el
    amarillo; el centro, un botón de cristal (anillo y azul en una pieza) sobre el remolino."""
    center = group("centro", [layer("azul", "azul", BLUE, 0.74), layer("aro", "aro", WHITE, 0.7)],
                   translucency=0.55, blur=0.05, refraction=(0.55, 0.35), shadow=("neutral", 0.2),
                   lighting="combined")
    front = group("rojo-verde", [layer("rojo", "petalo-rojo", RED, 0.72), layer("verde", "petalo-verde", GREEN, 0.72)],
                  translucency=0.6, blur=0.0, refraction=(0.45, 0.22), shadow=NONE, lighting="combined")
    back = group("amarillo", [layer("amarillo", "petalo-amarillo", YELLOW, 0.8)], translucency=0.55, blur=0.0,
                 refraction=(0.4, 0.18), shadow=NONE if dark else ("layer-color", 0.45))
    return spec(dark, [center, front, back])


APPROVED = {}

CONCEPTS = {
    "chrome-g1": vitral(dark=True),
    "chrome-g1c": vitral(dark=False),
    "chrome-g2": lupa(dark=True),
    "chrome-g2c": lupa(dark=False),
    "chrome-g3": petalos(dark=True),
    "chrome-g3c": petalos(dark=False),
    # Pruebas de la ronda 2 (se borran después)
    "chrome-gx1": lupa_tintada(dark=True),
    "chrome-gx2": vitral(dark=True, placement="outside", pane_refraction=(0.6, 0.4)),
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
