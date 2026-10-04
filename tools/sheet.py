"""Hoja de comparación de conceptos: render grande de Icon Composer y, debajo, a tamaño de tecla.

Uso:  python tools/sheet.py salida.png youtube-c1 youtube-c2 ...  (lee renders/)
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
BIG, KEY, PAD = 300, 144, 28


def font(size):
    for name in ("segoeuisb.ttf", "segoeui.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def main(out: str, names: list[str]) -> None:
    w = PAD + len(names) * (BIG + PAD)
    h = PAD + 34 + BIG + PAD + KEY + 24 + PAD
    sheet = Image.new("RGB", (w, h), (28, 28, 30))
    draw = ImageDraw.Draw(sheet)
    title, small = font(22), font(15)
    for i, name in enumerate(names):
        x = PAD + i * (BIG + PAD)
        draw.text((x, PAD), name, fill=(242, 242, 247), font=title)
        big = Image.open(ROOT / "renders" / f"{name}-Default.png").convert("RGBA").resize((BIG, BIG), Image.LANCZOS)
        sheet.paste(big, (x, PAD + 34), big)
        # Tecla de Stream Deck: LCD negro con el render a tamaño de tecla (144 px)
        ky = PAD + 34 + BIG + PAD
        kx = x + (BIG - KEY) // 2
        draw.rounded_rectangle((kx - 8, ky - 8, kx + KEY + 8, ky + KEY + 8), 18, fill=(0, 0, 0))
        key = Image.open(ROOT / "renders" / f"{name}-Default-key.png").convert("RGBA")
        sheet.paste(key, (kx, ky), key)
        draw.text((x, ky + KEY + 12), "en la tecla", fill=(142, 142, 147), font=small)
    sheet.save(out)
    print("hoja:", out, sheet.size)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
