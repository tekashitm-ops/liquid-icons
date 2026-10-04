"""Logos oficiales: lee el trazado SVG de la marca, lo ajusta al icono de la App Store y lo exporta.

El trazado sale de los recursos de marca (simple-icons recoge los SVG oficiales). Se escala
y coloca para que coincida con el logo del icono de iOS publicado en la App Store, y la
coincidencia se mide con IoU (intersección / unión de las dos máscaras).
"""
import math
import re

import numpy as np
from PIL import Image, ImageDraw
from shapely import affinity
from shapely.geometry import Polygon
from shapely.ops import unary_union

_CMD = re.compile(r"\s*([MmLlHhVvCcSsQqTtAaZz])")
_NUM = re.compile(r"[\s,]*([-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?)")
_FLAG = re.compile(r"[\s,]*([01])")


def parse_path(d: str, steps: int = 64) -> list[list[tuple[float, float]]]:
    """Subtrazados de un atributo `d` de SVG como listas de puntos (curvas y arcos aplanados)."""
    pos = 0

    def num() -> float:
        nonlocal pos
        m = _NUM.match(d, pos)
        if not m:
            raise ValueError(f"se esperaba un número en la posición {pos}: {d[pos:pos + 20]!r}")
        pos = m.end()
        return float(m.group(1))

    def flag() -> bool:
        nonlocal pos
        m = _FLAG.match(d, pos)
        if not m:
            raise ValueError(f"se esperaba una bandera 0/1 en la posición {pos}")
        pos = m.end()
        return m.group(1) == "1"

    subpaths, cur = [], []
    x = y = sx = sy = 0.0
    cmd, prev_ctrl, prev_cmd = None, None, None
    while True:
        m = _CMD.match(d, pos)
        if m:
            cmd, pos = m.group(1), m.end()
        elif not _NUM.match(d, pos):
            break
        rel = cmd.islower()
        c = cmd.upper()
        ox, oy = (x, y) if rel else (0.0, 0.0)
        ctrl = None
        if c == "M":
            if cur:
                subpaths.append(cur)
            x, y = ox + num(), oy + num()
            sx, sy, cur = x, y, [(x, y)]
            cmd = "l" if rel else "L"  # pares siguientes = líneas
        elif c == "L":
            x, y = ox + num(), oy + num()
            cur.append((x, y))
        elif c == "H":
            x = ox + num()
            cur.append((x, y))
        elif c == "V":
            y = (y if rel else 0.0) + num()
            cur.append((x, y))
        elif c in "CS":
            if c == "C":
                x1, y1 = ox + num(), oy + num()
            else:  # reflejo del control anterior
                x1, y1 = (2 * x - prev_ctrl[0], 2 * y - prev_ctrl[1]) if prev_cmd in "CS" else (x, y)
            x2, y2 = ox + num(), oy + num()
            ex, ey = ox + num(), oy + num()
            for i in range(1, steps + 1):
                t = i / steps
                a, b, cc, dd = (1 - t) ** 3, 3 * t * (1 - t) ** 2, 3 * t * t * (1 - t), t ** 3
                cur.append((a * x + b * x1 + cc * x2 + dd * ex, a * y + b * y1 + cc * y2 + dd * ey))
            ctrl, (x, y) = (x2, y2), (ex, ey)
        elif c in "QT":
            if c == "Q":
                x1, y1 = ox + num(), oy + num()
            else:
                x1, y1 = (2 * x - prev_ctrl[0], 2 * y - prev_ctrl[1]) if prev_cmd in "QT" else (x, y)
            ex, ey = ox + num(), oy + num()
            for i in range(1, steps + 1):
                t = i / steps
                a, b, cc = (1 - t) ** 2, 2 * t * (1 - t), t * t
                cur.append((a * x + b * x1 + cc * ex, a * y + b * y1 + cc * ey))
            ctrl, (x, y) = (x1, y1), (ex, ey)
        elif c == "A":
            rx, ry, phi = num(), num(), math.radians(num())
            large, sweep = flag(), flag()
            ex, ey = ox + num(), oy + num()
            cur.extend(_arc(x, y, rx, ry, phi, large, sweep, ex, ey, steps))
            x, y = ex, ey
        elif c == "Z":
            x, y = sx, sy
            if cur:
                subpaths.append(cur)
            cur = []
        prev_ctrl, prev_cmd = ctrl, c
    if cur:
        subpaths.append(cur)
    return [p for p in subpaths if len(p) >= 3]


def _arc(x1, y1, rx, ry, phi, large, sweep, x2, y2, steps):
    """Arco elíptico de SVG (forma de extremos) aplanado; ver la especificación SVG, apéndice F.6.5."""
    if rx == 0 or ry == 0:
        return [(x2, y2)]
    rx, ry = abs(rx), abs(ry)
    c, s = math.cos(phi), math.sin(phi)
    dx, dy = (x1 - x2) / 2, (y1 - y2) / 2
    x1p, y1p = c * dx + s * dy, -s * dx + c * dy
    lam = x1p ** 2 / rx ** 2 + y1p ** 2 / ry ** 2
    if lam > 1:
        rx, ry = rx * math.sqrt(lam), ry * math.sqrt(lam)
    num = rx * rx * ry * ry - rx * rx * y1p * y1p - ry * ry * x1p * x1p
    den = rx * rx * y1p * y1p + ry * ry * x1p * x1p
    coef = math.sqrt(max(0.0, num / den)) * (-1 if large == sweep else 1)
    cxp, cyp = coef * rx * y1p / ry, -coef * ry * x1p / rx
    cx, cy = c * cxp - s * cyp + (x1 + x2) / 2, s * cxp + c * cyp + (y1 + y2) / 2

    def angle(ux, uy, vx, vy):
        return math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)

    t1 = angle(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dt = angle((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if not sweep and dt > 0:
        dt -= 2 * math.pi
    elif sweep and dt < 0:
        dt += 2 * math.pi
    n = max(2, int(steps * abs(dt) / (math.pi / 2)))
    pts = []
    for i in range(1, n + 1):
        t = t1 + dt * i / n
        px, py = rx * math.cos(t), ry * math.sin(t)
        pts.append((c * px - s * py + cx, s * px + c * py + cy))
    return pts


def subpath_shapes(d: str) -> list[Polygon]:
    """Cada subtrazado como polígono válido, en el orden del SVG."""
    return [Polygon(p).buffer(0) for p in parse_path(d)]


def evenodd(shapes):
    """Relleno par-impar: los subtrazados interiores se convierten en huecos."""
    out = shapes[0]
    for s in shapes[1:]:
        out = out.symmetric_difference(s)
    return out


def raster(geom, size: int = 1024) -> np.ndarray:
    """Máscara booleana de una geometría de shapely en un lienzo de size x size."""
    im = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(im)
    for poly in getattr(geom, "geoms", [geom]):
        draw.polygon([tuple(p) for p in poly.exterior.coords], fill=255)
        for ring in poly.interiors:
            draw.polygon([tuple(p) for p in ring.coords], fill=0)
    return np.asarray(im) > 127


def iou(a: np.ndarray, b: np.ndarray) -> float:
    return float((a & b).sum() / max(1, (a | b).sum()))


def place(geom, sx, sy, tx, ty):
    return affinity.translate(affinity.scale(geom, sx, sy, origin=(0, 0)), tx, ty)


def fit(geom, mask: np.ndarray, uniform: bool = True):
    """Escala y posición que hacen coincidir geom con la máscara del icono oficial (máximo IoU)."""
    ys, xs = np.nonzero(mask)
    gx0, gy0, gx1, gy1 = geom.bounds
    sx = (xs.max() - xs.min() + 1) / (gx1 - gx0)
    sy = sx if uniform else (ys.max() - ys.min() + 1) / (gy1 - gy0)
    p = [sx, sy, xs.min() - gx0 * sx, ys.min() - gy0 * sy]
    score = iou(raster(place(geom, *p)), mask)
    for step in (8.0, 4.0, 2.0, 1.0, 0.5, 0.25):
        improved = True
        while improved:
            improved = False
            for i in (0, 2, 3) if uniform else (0, 1, 2, 3):
                for sign in (1, -1):
                    q = list(p)
                    q[i] += sign * (step * p[i] / 1000 if i < 2 else step)
                    if uniform and i == 0:
                        q[1] = q[0]
                    s = iou(raster(place(geom, *q)), mask)
                    if s > score:
                        p, score, improved = q, s, True
    return p, score
