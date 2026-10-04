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
- c1 fiel al oficial: segmentos de cristal de color en un grupo y el azul delante; debajo de cada
  cristal, su copia plana (ver ronda 2).
- c2 Fotos: el amarillo es un pétalo de cristal transparente delante; el rojo y el verde se meten
  9° debajo de él, así que a través del pétalo se ven sus cuñas (naranja y lima) y su borde las
  dobla, como los pétalos de Fotos.
- c3 lente: el azul es una lente transparente de refracción profunda sobre su azul plano; su
  borde muestra, doblados, el anillo blanco y el remolino de colores que la rodean (Vista Previa).
- c4 (prueba de c1): c1 con un solo cambio, los segmentos con iluminación "combined" (ver abajo).

Ronda 2 de c1/c1c (el panel eligió c1; un escéptico midió el render de CI y lo rechazó):
- Marcas rectas de 1 px fuera del logo (las "L" en x=145/878 con y=295, y la raya de y=933): ictool
  recorta la sombra de cada capa a la caja de su contenido más unos 12 px (son las cajas del rojo y
  del verde/amarillo). Ahora todas las capas ocupan el lienzo entero (write_icon(full_bounds=True):
  cuatro puntos casi transparentes en las esquinas, fuera de la máscara del icono).
- Pliegues oscuros a lo largo de verde/rojo y verde/amarillo (con una muesca en la punta de abajo),
  contornos grises de 4 px a los dos lados del anillo blanco y un contorno negro de 3-4 px
  alrededor del logo. Todo esto solo sale en el render oscuro. Medido, es siempre la misma banda de
  ~4 px que ictool dibuja con fondo oscuro justo FUERA de cada capa de cristal (con fondo claro va
  dentro de la pieza y se lee como su borde). Va teñida del color de la capa y es algo más fuerte
  con más opacidad de sombra (lente de c3 a 0.6 frente al azul de c1 a 0.5). El fondo plano de la
  lente de c3, que no tiene sombra, no le suma nada. Todo apunta a que es el núcleo de la sombra del
  grupo; sin ictool no se puede comprobar, y por eso está c4. Cae sobre lo que haya detrás: el verde
  (pliegue), el anillo blanco (contorno gris) o el fondo (contorno negro; xbox-c1 y youtube-oscuro
  también lo tienen). Por eso en c1 el azul y los segmentos van sin sombra. La única sombra (neutra, 0.35) la proyecta un disco oculto ("sombra", R-8) detrás de la
  base opaca, que tapa su banda; no la proyecta la base, porque llega casi al borde y su banda
  saldría fuera. c1c (fondo claro) mantiene las sombras de color: allí no hay banda y el icono
  oficial tiene ese halo verde, amarillo y azul.
- Debajo de cada cristal de color va su copia plana y opaca (fondo-rojo, -amarillo, -verde y
  -azul, sin sombra ni brillo). El cristal conserva el color de Chrome (el verde salía desvaído,
  35,175,93 frente a 0,158,64, por el blanco de debajo) y lo que se ve por las juntas es color, no
  blanco ni oscuro. El fondo verde se mete 3 px debajo del rojo y del amarillo, así no queda una
  rendija de antialias. El verde de cristal no se mete: con translucidez 0.5 se vería a través del
  rojo.
- La base blanca de c1 llega a R-1.5 (antes R-8). El borde del cristal queda sobre blanco o color
  en vez de sobre el fondo oscuro, y la ventana de abajo funciona hasta el borde. Sigue acabando
  dentro del borde del cristal, así que no deja halo blanco.
- Cristal más rico, como el material del icono oficial. Medido, el oficial tiene el cuerpo, una
  banda que se aclara hacia el borde (~12 px) y un labio de ~6 px de color en el mismo borde. Aquí
  los fondos planos acaban 14 px antes del borde exterior (y el del azul, 14 px antes del suyo). En
  esa ventana el cristal, más translúcido (0.5; alfa 0.92 los segmentos y 0.9 el azul), deja ver el
  blanco de debajo esmerilado (blur 0.3), y el bisel, que toma el contenido de ~50-100 px hacia
  dentro, pinta el labio del color de la pieza y dobla el borde de la ventana. El azul refracta
  (0.4, 0.15): pieza grande, redonda y lejos del borde del lienzo, y su bisel toma su propio fondo.
  Los segmentos se quedan en (0.3, 0.1), lo mínimo: tienen puntas muy finas donde tocan el anillo.
  Junto al anillo no se deja ventana, porque esas puntas quedarían blancas.
- c4/c4c (alternativa con un solo parámetro distinto): lighting "combined" en el grupo de
  segmentos. Los tres se iluminan como una sola pieza de cristal, así que el bisel solo recorre el
  círculo exterior y el anillo, como en el icono oficial, que tiene juntas limpias y la banda
  clara continua a través de ellas. Además, la pieza de cristal ya no tiene puntas finas. Si la
  banda de sombra no fuera la causa de los pliegues, c4 los quita igual; si "combined" hace algo
  raro con los colores por capa, c1 queda como respaldo.
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
BASE_INSET = 8        # px: la base blanca de c2/c3 acaba un poco antes del borde para no dejar halo blanco
OVERLAP = 9.0         # grados que el rojo y el verde se meten debajo del pétalo amarillo (~58 px)

# c1 (ronda 2): copias planas debajo del cristal y ventanas de blanco bajo su borde
BASE_INSET_FIEL = 1.5  # px: base blanca de c1 casi hasta el borde (dentro del borde del cristal: sin halo)
OUTER_WINDOW = 14      # px antes del borde exterior donde acaban los fondos planos: banda clara del bisel
BLUE_WINDOW = 14       # px antes del borde del azul donde acaba su fondo plano
UNDERLAP = 3           # px que el fondo verde se mete debajo del rojo y del amarillo (sin rendijas)
SHADOW_INSET = 8       # px: disco que proyecta la sombra de c1; su banda de ~4 px queda 2.5 px dentro de la base

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
    window = circle(CENTER, R - OUTER_WINDOW)
    # El verde (el de más atrás) con 3 px de más debajo del rojo y del amarillo
    green_under = _polygons(unary_union([
        seg["verde"], seg["verde"].buffer(UNDERLAP).intersection(unary_union([seg["rojo"], seg["amarillo"]]))]))
    return {
        **seg,
        "azul": circle(CENTER, R_BLUE),
        # Base blanca bajo todo el logo: el anillo blanco que se ve y el blanco de detrás del cristal
        "base": circle(CENTER, R - BASE_INSET),
        # Concepto Fotos: rojo y verde con la cuña que se mete debajo del pétalo amarillo
        "rojo-solapa": tuck(seg["rojo"], seg["amarillo"], OVERLAP),
        "verde-solapa": tuck(seg["verde"], seg["amarillo"], OVERLAP),
        # c1 (ronda 2): copias planas de cada pieza, acabadas antes del borde (la ventana de blanco)
        "fondo-rojo": _polygons(seg["rojo"].intersection(window)),
        "fondo-amarillo": _polygons(seg["amarillo"].intersection(window)),
        "fondo-verde": _polygons(green_under.intersection(window)),
        "fondo-azul": circle(CENTER, R_BLUE - BLUE_WINDOW),
        "base-fiel": circle(CENTER, R - BASE_INSET_FIEL),
        "sombra": circle(CENTER, R - SHADOW_INSET),
    }


def group(name, layers, **kw):
    """Un grupo de Liquid Glass con varias piezas, cada una con su color (de delante hacia atrás)."""
    g = glass(name, **kw)
    g["layers"] = [{"name": n, "image-name": f"{image}.svg", "glass": True, "fill": {"solid": color(fill, alpha)}}
                   for n, image, fill, alpha in layers]
    return g


WHITE_BG = {"solid": color(WHITE)}  # el fondo del icono oficial


# --- Concepto 1: fiel al icono oficial de iOS (ronda 2) ------------------------------------------
def blue_fiel(shadow="none", shadow_opacity=0.0):
    """Azul de cristal translúcido sobre su fondo plano (14 px más pequeño). En el centro es el azul
    de Chrome; en el borde deja ver el blanco de debajo (la banda clara del oficial) y el bisel lo
    dobla. Refracción (0.4, 0.15): pieza grande, redonda y a 346 px del borde del lienzo; su bisel
    toma ~50-100 px hacia dentro, dentro de su propio fondo, así que no trae trozos de otro color.
    Sin sombra en oscuro (su banda dibujaba un contorno gris en el anillo); con la de su color en
    claro (el halo azul del anillo del oficial)."""
    return glass("azul", fill=BLUE, alpha=0.9, translucency=0.5, blur=0.3, refraction=(0.4, 0.15),
                 shadow=shadow, shadow_opacity=shadow_opacity)


def segments_fiel(shadow="none", shadow_opacity=0.0, lighting="individual"):
    """Los tres segmentos en un grupo de cristal de color, translúcido sobre sus fondos planos.
    Refracción mínima (0.3, 0.1): cada segmento acaba en una punta muy fina junto al anillo.
    lighting="combined" (c4) los ilumina como una sola pieza: sin bisel en las juntas."""
    g = group("segmentos", [("rojo", "rojo", RED, 0.92), ("amarillo", "amarillo", YELLOW, 0.92),
                            ("verde", "verde", GREEN, 0.92)],
              translucency=0.5, blur=0.3, refraction=(0.3, 0.1), shadow=shadow, shadow_opacity=shadow_opacity)
    g["lighting"] = lighting
    return g


def flat(name, layers):
    """Grupo plano: opaco, sin sombra (sin la banda de ~4 px), sin brillo y sin refracción."""
    g = group(name, layers, translucency=0.0, blur=0.5, shadow="none", shadow_opacity=0.0)
    g["specular"] = False
    return g


# Copias planas de los segmentos bajo el cristal (el verde, detrás, con 3 px bajo los otros dos)
FONDOS = [("fondo-rojo", "fondo-rojo", RED, 1.0), ("fondo-amarillo", "fondo-amarillo", YELLOW, 1.0),
          ("fondo-verde", "fondo-verde", GREEN, 1.0)]


def blue_backing():
    """El azul plano bajo el cristal azul, en su grupo delante de los segmentos (como en c3)."""
    return flat("fondo-azul", [("fondo-azul", "fondo-azul", BLUE, 1.0)])


def base_fiel():
    """Base de c1: los fondos planos delante y el blanco (el anillo y las ventanas) detrás, hasta R-1.5."""
    return flat("base", [*FONDOS, ("base", "base-fiel", WHITE, 1.0)])


def shadow_caster():
    """Disco oculto detrás de la base opaca: la única sombra de c1 (neutra, suave). La base tapa
    su banda de ~4 px, que con la sombra en la base saldría como contorno negro fuera del logo."""
    g = glass("sombra", fill=WHITE, translucency=0.0, blur=0.5, shadow="neutral", shadow_opacity=0.35)
    g["specular"] = False
    return g


def fiel(dark, lighting="individual"):
    """c1 (oscuro) o c1c (claro, el fondo blanco es el anillo); lighting distinto para c4/c4c."""
    if dark:
        return {"fill": "system-dark",
                "groups": [blue_fiel(), blue_backing(), segments_fiel(lighting=lighting), base_fiel(),
                           shadow_caster()]}
    return {"fill": WHITE_BG,
            "groups": [blue_fiel("layer-color", 0.5), blue_backing(),
                       segments_fiel("layer-color", 0.5, lighting), flat("fondos", FONDOS)]}


# --- Base y segmentos de c2/c3 (sin cambios) -----------------------------------------------------
def segments_official():
    """Los tres segmentos en un solo grupo de cristal de color, con sombra del color de cada uno (c3)."""
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
    # c1 (fiel al oficial): fondo oscuro de Apple, base blanca con los fondos planos, segmentos y
    # azul de cristal sin sombra, y la sombra de un disco oculto
    "chrome-c1": fiel(dark=True),
    # c1c: el icono oficial de iOS (fondo blanco, el anillo es el fondo), con sombras de color
    "chrome-c1c": fiel(dark=False),
    # c4/c4c: c1/c1c con un solo cambio, los segmentos iluminados como una sola pieza ("combined")
    "chrome-c4": fiel(dark=True, lighting="combined"),
    "chrome-c4c": fiel(dark=False, lighting="combined"),
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
        # Capas a lienzo completo: ictool ya no recorta la sombra a la caja de cada pieza
        write_icon(name, spec["fill"], spec["groups"], geo, full_bounds=True)


if __name__ == "__main__":
    import sys
    main(sys.argv[1:] or None)
