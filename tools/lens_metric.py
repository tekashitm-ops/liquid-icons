"""Métrica de la lente de Ajustes de Discord sobre los renders de Icon Composer.

- lejos: píxeles con color de Clyde dentro del engranaje a más de 80 px de Clyde (esquirlas
  que el bisel trae de lejos; el panel de jueces las rechazó).
- deforma: % de píxeles del engranaje cerca del borde de Clyde (a menos de 60 px) cuyo
  blanco/morado no coincide con el Clyde sin deformar (cuánto se ve la deformación).

Uso:  python tools/lens_metric.py v20 v21 ...   (lee renders/discord-ajustes-<v>-Default.png)
"""
import sys

import numpy as np
from PIL import Image

import brand
import discord_ajustes as da
from liquid import ROOT


def measure(variant: str, light: bool = False) -> dict:
    pos, _, *shape = da.LENS_VARIANTS[variant]
    pieces = da.pieces()
    gear = pieces[f"{shape[0] if shape else 'engranaje'}-{pos}"]
    clyde = pieces[f"clyde-{pos}"]
    name = f"discord-ajustes-{variant}{'c' if light else ''}"
    a = np.asarray(Image.open(ROOT / "renders" / f"{name}-Default.png").convert("RGB")).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    # Color de Clyde: blanco en oscuro, morado saturado en claro
    clyde_px = (r > 200) & (g > 200) if not light else (b - r > 60) & (r < 170)
    gm = brand.raster(gear)
    cm = brand.raster(clyde)
    far = gm & ~brand.raster(clyde.buffer(80)) & clyde_px
    near = gm & brand.raster(clyde.buffer(60)) & ~brand.raster(clyde.buffer(-60))
    mismatch = near & (clyde_px != cm)
    return {"lejos": int(far.sum()), "deforma": round(100 * mismatch.sum() / max(1, near.sum()), 1)}


if __name__ == "__main__":
    for v in sys.argv[1:]:
        d, c = measure(v), measure(v, light=True)
        print(f"{v:4s} oscuro: lejos {d['lejos']:5d} px, deforma {d['deforma']:5.1f}%   "
              f"claro: lejos {c['lejos']:5d} px, deforma {c['deforma']:5.1f}%")
