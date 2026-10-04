"""Imágenes por defecto de las acciones de Liquid Deck: teclas vacías (transparentes).

Las teclas solo muestran iconos aprobados de la biblioteca; sin icono, la tecla queda
negra (con el título, si el usuario le pone uno).
"""
import struct
import zlib
from pathlib import Path

KEYS = Path(__file__).resolve().parent.parent.parent / "com.ricca.liquiddeck.sdPlugin" / "imgs" / "keys"


def transparent_png(size: int) -> bytes:
    raw = b"".join(b"\x00" + b"\x00\x00\x00\x00" * size for _ in range(size))

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)  # RGBA de 8 bits
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")


def main() -> None:
    KEYS.mkdir(parents=True, exist_ok=True)
    for name in ("open", "media", "multi"):
        (KEYS / f"{name}.png").write_bytes(transparent_png(72))
        (KEYS / f"{name}@2x.png").write_bytes(transparent_png(144))
    print("teclas por defecto vacías:", sorted(p.name for p in KEYS.iterdir()))


if __name__ == "__main__":
    main()
