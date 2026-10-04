"""Discord: logo oficial (Clyde) ajustado al icono de iOS y montaje de los .icon.

Trazado: brands/discord.svg (recursos de marca). Ajustado contra el icono de la App Store
(1024 px) con IoU 0.996. Ese icono oficial ya es de Liquid Glass: Clyde de cristal blanco
sobre el degradado morado de la marca.
Piezas: la cara (con los ojos huecos) y, en algunos conceptos, los ojos como lentes de
cristal delante, que refractan el borde de la cara a su alrededor.
"""
import re

from brand import place, subpath_shapes
from liquid import ROOT, clean, glass, gradient, write_icon

D = re.search(r' d="([^"]+)"', (ROOT / "brands" / "discord.svg").read_text(encoding="utf-8")).group(1)
FIT = (31.443, 31.284, 134.0, 138.375)  # escala x, escala y, desplazamiento x, y (lienzo de 1024)

BLURPLE = "#5865F2"                      # color de marca
DISCORD_BG = ["#747FF7", "#5662F5"]      # degradado del icono oficial de iOS (medido arriba y abajo)
EYE_LENS = 14                            # px que la lente sobresale del hueco del ojo


def pieces():
    face, *eyes = (place(s, *FIT) for s in subpath_shapes(D))
    eye_holes = eyes[0].union(eyes[1])
    return {
        "clyde": face.difference(eye_holes),
        "ojos": eye_holes.buffer(EYE_LENS),
    }


def clyde_white():
    """Como el icono oficial: Clyde de cristal blanco."""
    return glass("clyde", alpha=0.95, translucency=0.3, blur=0.3, refraction=(0.4, 0.35))


def clyde_clear():
    """Clyde de cristal transparente: se ve el degradado de detrás deformado."""
    return glass("clyde", alpha=0.55, translucency=0.75, blur=0.0, refraction=(0.6, 0.5),
                 shadow_opacity=0.35)


def clyde_blurple():
    """Clyde de cristal morado, para fondo claro."""
    return glass("clyde", fill=BLURPLE, alpha=0.92, translucency=0.35, blur=0.2,
                 refraction=(0.35, 0.3), shadow="layer-color")


def eyes(fill=BLURPLE):
    """Ojos como lentes de cristal morado que deforman el borde de la cara."""
    return glass("ojos", fill=fill, alpha=0.8, translucency=0.5, blur=0.0, refraction=(0.6, 0.5),
                 shadow="layer-color", specular="inside")


APPROVED = {}

CONCEPTS = {
    # Oscuro (marca), fiel al icono oficial
    "discord-c1": {"fill": gradient(DISCORD_BG), "groups": [clyde_white()]},
    # Oscuro con los ojos como lentes de cristal
    "discord-c2": {"fill": gradient(DISCORD_BG), "groups": [eyes(), clyde_white()]},
    # Oscuro con Clyde de cristal transparente
    "discord-c3": {"fill": gradient(DISCORD_BG), "groups": [clyde_clear()]},
    # Claro: fondo claro estándar de Apple y Clyde de cristal morado, ojos de lente (pareja de c2)
    "discord-c4": {"fill": "system-light", "groups": [eyes(), clyde_blurple()]},
    # (c3 descartado: en la tecla Clyde transparente se ve lavado)
    # Claro con los ojos huecos, como el oficial (pareja de c1)
    "discord-c5": {"fill": "system-light", "groups": [clyde_blurple()]},
}


def main(names=None):
    """Escribe los aprobados; con nombres de concepto, escribe esos para renderizarlos."""
    geo = pieces()
    clean("discord")
    targets = {n: n for n in names} if names else APPROVED
    for name, concept in targets.items():
        spec = CONCEPTS[concept]
        write_icon(name, spec["fill"], spec["groups"], geo)


if __name__ == "__main__":
    import sys
    main(sys.argv[1:] or None)
