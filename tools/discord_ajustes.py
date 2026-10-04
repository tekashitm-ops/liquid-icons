"""Ajustes de Discord: engranaje de Ajustes + Clyde, en el mundo del icono de Discord aprobado.

No existe un icono oficial: es una composición nueva con piezas que sí lo son.
- Clyde: el trazado oficial (brands/discord.svg), igual que en discord.py, solo escalado.
- Engranaje: dibujado aquí (geométrico). No se usa el de SF Symbols porque su licencia
  prohíbe usarlos en iconos de app.
- Fondo y cristal: los del Discord aprobado (opción A), para que las dos teclas casen.
El cristal tiene una función: donde el engranaje pisa a Clyde, lo refracta (como Fotos).
"""
import math

from shapely import affinity
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

import discord
from liquid import clean, glass, gradient, write_icon

RES = 128
GRAY_ON_LIGHT = "#7C7C80"  # gris de Ajustes de Apple, algo más oscuro para llegar a 3:1 sobre fondo claro


def gear(cx, cy, r_tip, r_root, teeth=8, hole=0.0, fillet=10.0, root_frac=0.55, tip_frac=0.38, rotation=0.0):
    """Engranaje redondeado: cuerpo + dientes trapezoidales, esquinas suavizadas y eje hueco."""
    body = Point(cx, cy).buffer(r_root, quad_segs=RES)
    pitch = 2 * math.pi / teeth
    w_root, w_tip = root_frac * pitch * r_root, tip_frac * pitch * r_root  # anchura del diente (px)
    parts = [body]
    for i in range(teeth):
        a = i * pitch - math.pi / 2 + rotation * pitch  # rotation en dientes (0.5 = medio)
        ux, uy = math.cos(a), math.sin(a)          # hacia fuera
        px, py = -uy, ux                            # perpendicular
        base, tip = r_root * 0.9, r_tip
        parts.append(Polygon([
            (cx + ux * base - px * w_root / 2, cy + uy * base - py * w_root / 2),
            (cx + ux * tip - px * w_tip / 2, cy + uy * tip - py * w_tip / 2),
            (cx + ux * tip + px * w_tip / 2, cy + uy * tip + py * w_tip / 2),
            (cx + ux * base + px * w_root / 2, cy + uy * base + py * w_root / 2),
        ]))
    g = unary_union(parts)
    # Redondea esquinas exteriores e interiores (como los engranajes de Apple)
    g = g.buffer(fillet, quad_segs=RES).buffer(-2 * fillet, quad_segs=RES).buffer(fillet, quad_segs=RES)
    if hole:
        g = g.difference(Point(cx, cy).buffer(hole, quad_segs=RES))
    return g


def smooth_gear(cx, cy, r_mid, depth, teeth=8, sharpness=2.5, hole=0.0, steps=2048):
    """Engranaje de perfil continuo: r(θ) = r_mid + depth·tanh(s·cos(nθ))/tanh(s).

    Sin esquinas vivas ni hendiduras: la normal del borde cambia con suavidad, así la refracción
    de Liquid Glass se dobla limpia (los dientes con esquinas traían trozos de Clyde de lejos).
    """
    pts = []
    for i in range(steps):
        t = 2 * math.pi * i / steps
        r = r_mid + depth * math.tanh(sharpness * math.cos(teeth * (t + math.pi / 2))) / math.tanh(sharpness)
        pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
    g = Polygon(pts).buffer(0)
    if hole:
        g = g.difference(Point(cx, cy).buffer(hole, quad_segs=RES))
    return g


def clyde_at(scale, cx, cy):
    """Clyde oficial escalado (sin deformar) con su centro en (cx, cy)."""
    c = discord.pieces()["clyde"]
    x0, y0, x1, y1 = c.bounds
    c = affinity.scale(c, scale, scale, origin=((x0 + x1) / 2, (y0 + y1) / 2))
    x0, y0, x1, y1 = c.bounds
    return affinity.translate(c, cx - (x0 + x1) / 2, cy - (y0 + y1) / 2)


def pieces():
    return {
        # Concepto "eje": engranaje grande centrado con Clyde dentro del hueco del eje
        # (margen de la rejilla de Apple: los dientes acaban a 102 px del borde)
        "engranaje-anillo": gear(512, 512, 410, 346, teeth=8, hole=266, fillet=16),
        "clyde-eje": clyde_at(0.50, 512, 506),
        # Concepto "insignia": Clyde arriba a la izquierda y el engranaje delante, pisando solo
        # su esquina; el conjunto queda centrado en el lienzo
        "clyde-insignia": clyde_at(0.80, 414, 390),
        "engranaje-insignia": gear(697, 675, 215, 174, teeth=8, hole=66, fillet=10),
        # Lente de cristal transparente (ronda 2): el engranaje pisa más a Clyde para deformarlo.
        # p2: pisa el 24 % y el hueco del eje cae sobre su borde; p3: pisa el 32 % y llega al
        # ojo derecho. Cada pareja se desplaza para que el conjunto siga centrado.
        "clyde-p2": clyde_at(0.80, 432, 394),
        "engranaje-p2": gear(678, 644, 215, 174, teeth=8, hole=66, fillet=10),
        "clyde-p3": clyde_at(0.80, 448, 434),
        "engranaje-p3": gear(664, 604, 215, 174, teeth=8, hole=66, fillet=10),
        # Ronda 3: engranaje "lente" de dientes cortos y anchos, con más cuerpo macizo donde
        # la refracción deforma a Clyde con suavidad (los dientes finos lo rompían en trozos)
        "lente-p2": gear(678, 644, 215, 184, teeth=10, hole=70, fillet=12, root_frac=0.6, tip_frac=0.46),
        "lente-p3": gear(664, 604, 215, 184, teeth=10, hole=70, fillet=12, root_frac=0.6, tip_frac=0.46),
        # Ronda 4: perfil continuo (sin esquinas) y el trapecio de siempre con esquinas muy suaves
        "suave-p2": smooth_gear(678, 644, 194, 22, teeth=8, sharpness=2.5, hole=66),
        "redondo-p2": gear(678, 644, 215, 174, teeth=8, hole=66, fillet=20),
        # Ronda 6: el mismo, girado medio diente (cambia qué dientes quedan cerca del borde de Clyde)
        "girado-p2": gear(678, 644, 215, 174, teeth=8, hole=66, fillet=20, rotation=0.5),
    }


def clyde_glass(image, light=False):
    """El Clyde del Discord aprobado, con el mismo cristal (blanco u, en claro, morado)."""
    g = discord.clyde_blurple() if light else discord.clyde_white()
    g["layers"][0]["image-name"] = f"{image}.svg"
    return g


def gear_glass(image, fill, alpha=0.92, translucency=0.35, refraction=(0.55, 0.45)):
    """Engranaje de cristal sin esmerilar: refracta el borde de Clyde donde lo pisa."""
    return glass("engranaje", fill=fill, alpha=alpha, translucency=translucency, blur=0.05,
                 refraction=refraction, shadow="neutral", shadow_opacity=0.55, image=image)


def lens(image, fill="#FFFFFF", alpha=0.22, translucency=0.85, refraction=(0.75, 0.65), shadow_opacity=0.35,
         blur=0.0):
    """Engranaje de cristal transparente: casi sin color, sin esmerilar, refracta a Clyde debajo."""
    return glass("engranaje", fill=fill, alpha=alpha, translucency=translucency, blur=blur,
                 refraction=refraction, shadow="neutral", shadow_opacity=shadow_opacity, image=image)


# Grados de cristal para la lente
CLARO = {"alpha": 0.22, "translucency": 0.85, "refraction": (0.75, 0.65), "shadow_opacity": 0.35}
INVISIBLE = {"alpha": 0.10, "translucency": 0.92, "refraction": (0.95, 0.85), "shadow_opacity": 0.3}
CON_CUERPO = {"alpha": 0.38, "translucency": 0.75, "refraction": (0.6, 0.5), "shadow_opacity": 0.45}

BG = gradient(discord.DISCORD_BG)

APPROVED = {
    # v24 (aprobada): engranaje de cristal transparente girado medio diente, refracción 0.3/0.1
    "discord-ajustes-oscuro": "discord-ajustes-v24",
    # su pareja clara (guardada para el modo claro): cristal gris sobre fondo claro
    "discord-ajustes-claro": "discord-ajustes-v24c",
}

CONCEPTS = {
    # Eje: el engranaje de Ajustes en blanco y Clyde como su eje
    "discord-ajustes-c1": {"fill": BG, "groups": [
        clyde_glass("clyde-eje"),
        gear_glass("engranaje-anillo", "#FFFFFF", alpha=0.9, translucency=0.3, refraction=(0.4, 0.35)),
    ]},
    # Insignia: Clyde y, delante, un engranaje blanco que pisa su esquina y la refracta.
    # (El gris de Ajustes y el morado quedaban por debajo de 3:1 sobre el fondo morado.)
    "discord-ajustes-c2": {"fill": BG, "groups": [
        gear_glass("engranaje-insignia", "#FFFFFF"),
        clyde_glass("clyde-insignia"),
    ]},
    # Parejas claras (fondo claro de Apple, Clyde morado como en discord-claro)
    "discord-ajustes-c4": {"fill": "system-light", "groups": [
        clyde_glass("clyde-eje", light=True),
        gear_glass("engranaje-anillo", discord.BLURPLE, alpha=0.9, translucency=0.3, refraction=(0.4, 0.35)),
    ]},
    # Engranaje gris de Ajustes: sobre fondo claro llega a 3.7:1
    "discord-ajustes-c5": {"fill": "system-light", "groups": [
        gear_glass("engranaje-insignia", GRAY_ON_LIGHT),
        clyde_glass("clyde-insignia", light=True),
    ]},
}

# Ronda 2 (elegida la idea 2): el engranaje como lente de cristal transparente encima de Clyde.
# vN = oscuro (fondo de Discord); vNc = su pareja clara (fondo claro, Clyde morado, lente gris).
LENS_VARIANTS = {
    "v1": ("p2", CLARO),
    "v2": ("p2", INVISIBLE),
    "v3": ("p3", CLARO),
    "v4": ("p3", INVISIBLE),
    "v5": ("p2", CON_CUERPO),
    "v6": ("insignia", CLARO),  # posición original
}
# (Ronda 2 descartada: los dientes finos con refracción profunda rompían a Clyde en trozos,
# como cristal roto.)
# Ronda 3: refracción poco profunda (se curva en un borde limpio) y engranaje con más cuerpo.
FINO = {"alpha": 0.18, "translucency": 0.85, "shadow_opacity": 0.35}
LENS_VARIANTS.update({
    "v7": ("p2", {**FINO, "refraction": (0.6, 0.25)}, "engranaje"),
    "v8": ("p2", {**FINO, "refraction": (0.85, 0.25)}, "engranaje"),
    "v9": ("p2", {**FINO, "refraction": (0.6, 0.3)}, "lente"),
    "v10": ("p2", {**FINO, "refraction": (0.85, 0.3)}, "lente"),
    "v11": ("p2", {**FINO, "refraction": (0.75, 0.5)}, "lente"),
    "v12": ("p3", {**FINO, "refraction": (0.75, 0.3)}, "lente"),
})
# (Ronda 3 descartada por el panel de jueces: esquirlas en las esquinas hendidas entre dientes,
# costuras en la base de los dientes y una pareja clara casi invisible, 1.07:1.)
# Ronda 4: perfil sin esquinas, refracción algo menor, borde y sombra más marcados, y en claro
# un cristal gris con más cuerpo para que el engranaje se lea sobre el fondo claro.
SUAVE = {"alpha": 0.22, "translucency": 0.85, "shadow_opacity": 0.45}
LIGHT_BODY = {"alpha": 0.34, "shadow_opacity": 0.55}
LENS_VARIANTS.update({
    "v13": ("p2", {**SUAVE, "refraction": (0.55, 0.25)}, "suave"),
    "v14": ("p2", {**SUAVE, "refraction": (0.7, 0.3)}, "suave"),
    "v15": ("p2", {**SUAVE, "refraction": (0.55, 0.4)}, "suave"),
    "v16": ("p2", {**SUAVE, "refraction": (0.6, 0.25)}, "redondo"),
})
# Ronda 5: el bisel aún recogía trozos de Clyde de alrededor (un Clyde en miniatura en un
# diente). Menos fuerza y profundidad para que solo recoja lo cercano; en dos, un esmerilado
# mínimo que suaviza los destellos sin quitar transparencia.
LENS_VARIANTS.update({
    "v17": ("p2", {**SUAVE, "refraction": (0.45, 0.2)}, "suave"),
    "v18": ("p2", {**SUAVE, "refraction": (0.45, 0.2), "blur": 0.1}, "suave"),
    "v19": ("p2", {**SUAVE, "refraction": (0.5, 0.2), "blur": 0.06}, "redondo"),
    "v20": ("p2", {**SUAVE, "refraction": (0.4, 0.15)}, "redondo"),
})
# Ronda 6: el panel aún encontró en v20 dos destellos traídos de ~100 px (el bisel "mira" a esa
# distancia). Menos refracción para que mire más cerca, y el engranaje girado medio diente.
LENS_VARIANTS.update({
    "v21": ("p2", {**SUAVE, "refraction": (0.3, 0.1)}, "redondo"),
    "v22": ("p2", {**SUAVE, "refraction": (0.25, 0.08)}, "redondo"),
    "v23": ("p2", {**SUAVE, "refraction": (0.4, 0.15)}, "girado"),
    "v24": ("p2", {**SUAVE, "refraction": (0.3, 0.1)}, "girado"),
})
ROUND4 = {"v13", "v14", "v15", "v16", "v17", "v18", "v19", "v20", "v21", "v22", "v23", "v24"}
for v, (pos, grade, *shape) in LENS_VARIANTS.items():
    gear_piece = f"{shape[0] if shape else 'engranaje'}-{pos}"
    CONCEPTS[f"discord-ajustes-{v}"] = {"fill": BG, "groups": [
        lens(gear_piece, **grade),
        clyde_glass(f"clyde-{pos}"),
    ]}
    light_grade = {**grade, **LIGHT_BODY} if v in ROUND4 else grade
    CONCEPTS[f"discord-ajustes-{v}c"] = {"fill": "system-light", "groups": [
        lens(gear_piece, fill=GRAY_ON_LIGHT, **light_grade),
        clyde_glass(f"clyde-{pos}", light=True),
    ]}


def main(names=None):
    """Escribe los aprobados; con nombres de concepto, escribe esos para renderizarlos."""
    geo = pieces()
    clean("discord-ajustes")
    targets = {n: n for n in names} if names else APPROVED
    for name, concept in targets.items():
        spec = CONCEPTS[concept]
        write_icon(name, spec["fill"], spec["groups"], geo)


if __name__ == "__main__":
    import sys
    main(sys.argv[1:] or None)
