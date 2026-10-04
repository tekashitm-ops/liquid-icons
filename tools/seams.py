"""Detector de costuras de render: líneas rectas de 1 px que ictool deja al recortar sombras.

Una costura es una fila (o columna) de píxeles más clara u oscura que sus dos vecinas por más
de THRESHOLD niveles, con el mismo signo, a lo largo de más de MIN_RUN píxeles seguidos, en una
zona lisa: a 4 px a cada lado el color es el mismo (si no, es el borde de una pieza y su brillo).
No se mira la franja del borde del icono (su brillo es el de Apple).

Uso:  python tools/seams.py renders/steam-oscuro-Default.png ...   (o sin argumentos: todos los Default)
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
THRESHOLD = 3
MIN_RUN = 40
EDGE = 16  # px del borde del icono que no se miran


def runs(mask_line):
    """(inicio, longitud) de cada tramo seguido de True."""
    out, start = [], None
    for i, v in enumerate(list(mask_line) + [False]):
        if v and start is None:
            start = i
        elif not v and start is not None:
            out.append((start, i - start))
            start = None
    return out


def scan(path: Path):
    im = Image.open(path).convert("RGBA")
    a = np.asarray(im).astype(float)
    lum = a[..., :3].mean(axis=2)
    opaque = a[..., 3] > 250
    # Solo dentro del icono y lejos de su borde (EDGE px), donde está el brillo del propio icono
    inside = opaque.copy()
    for shift in range(1, EDGE + 1):
        inside[shift:] &= opaque[:-shift]
        inside[:-shift] &= opaque[shift:]
        inside[:, shift:] &= opaque[:, :-shift]
        inside[:, :-shift] &= opaque[:, shift:]
    found = []
    for axis in (0, 1):  # 0: filas (líneas horizontales), 1: columnas (verticales)
        L = lum if axis == 0 else lum.T
        ins = inside if axis == 0 else inside.T
        d = np.zeros_like(L)
        d[1:-1] = L[1:-1] - (L[:-2] + L[2:]) / 2
        flat = np.zeros_like(L, dtype=bool)
        flat[4:-4] = np.abs(L[:-8] - L[8:]) < THRESHOLD  # sin salto de color a 4 px a cada lado
        for sign in (1, -1):
            m = (sign * d > THRESHOLD) & ins & flat
            for row in np.nonzero(m.sum(axis=1) >= MIN_RUN)[0]:
                for start, length in runs(m[row]):
                    if length >= MIN_RUN:
                        found.append(("horizontal" if axis == 0 else "vertical", int(row), start, length,
                                      "clara" if sign > 0 else "oscura"))
    return found


def main(paths):
    paths = [Path(p) for p in paths] or sorted((ROOT / "renders").glob("*-Default.png"))
    bad = 0
    for p in paths:
        seams = scan(p)
        if seams:
            bad += 1
            desc = "; ".join(f"{k} {'y' if k == 'horizontal' else 'x'}={pos} desde {s} ({n} px, {c})"
                             for k, pos, s, n, c in seams[:4])
            print(f"COSTURA  {p.name}: {len(seams)} — {desc}")
        else:
            print(f"limpio   {p.name}")
    return bad


if __name__ == "__main__":
    sys.exit(1 if main(sys.argv[1:]) else 0)
