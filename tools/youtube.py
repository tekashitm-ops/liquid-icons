"""YouTube: logo oficial ajustado al icono de iOS y montaje de los .icon.

Trazado: brands/youtube.svg (recursos de marca). Ajustado contra el icono de la App Store
(logo_youtube_2024_q4, 1024 px) con IoU 0.995.
Piezas: la pastilla roja detrás y el triángulo de reproducción delante. El triángulo es
cristal y refracta lo que tiene debajo, como la lente de Vista Previa en iOS 27.
"""
import re

from brand import place, subpath_shapes
from liquid import ROOT, WHITE, clean, color, glass, write_icon

D = re.search(r' d="([^"]+)"', (ROOT / "brands" / "youtube.svg").read_text(encoding="utf-8")).group(1)
FIT = (32.583, 32.272, 121.0, 124.787)  # escala x, escala y, desplazamiento x, y (lienzo de 1024)

YT_RED = "#FF0033"  # rojo de YouTube desde 2024
LENS_INSET = 18     # px: el hueco de la pastilla es más pequeño que el triángulo de cristal


def pieces():
    pill, play = (place(s, *FIT) for s in subpath_shapes(D))
    return {
        # Como el logo: la pastilla con el hueco exacto del triángulo
        "pastilla": pill.difference(play),
        # Hueco más pequeño: el borde del triángulo de cristal queda sobre el rojo y lo refracta
        "pastilla-lente": pill.difference(play.buffer(-LENS_INSET, join_style="mitre")),
        "play": play,
    }


WHITE_BG = {"solid": color(WHITE)}  # el fondo del icono oficial


def pill(image="pastilla"):
    return glass("pastilla", fill=YT_RED, alpha=0.95, translucency=0.25, blur=0.3,
                 refraction=(0.35, 0.3), shadow="layer-color", image=image)


def play_white():
    """Triángulo blanco de cristal casi opaco."""
    return glass("play", alpha=0.95, translucency=0.2, blur=0.1, refraction=(0.5, 0.4), specular="inside")


def play_prism():
    """Triángulo de cristal más claro y sin esmerilar: deja ver el rojo refractado en sus bordes."""
    return glass("play", alpha=0.82, translucency=0.45, blur=0.0, refraction=(0.65, 0.5), specular="inside")


APPROVED = {
    # c1 (aprobado): fondo oscuro de Apple, pastilla roja y triángulo blanco de cristal
    "youtube-oscuro": "youtube-c1",
    # c5 (guardado para el modo claro): fondo blanco como el oficial
    "youtube-claro": "youtube-c5",
}

CONCEPTS = {
    # Oscuro: fondo oscuro estándar de Apple, triángulo blanco sobre su hueco
    "youtube-c1": {"fill": "system-dark", "groups": [play_white(), pill()]},
    # Oscuro: triángulo como prisma; su borde refracta el rojo de la pastilla
    "youtube-c2": {"fill": "system-dark", "groups": [play_prism(), pill("pastilla-lente")]},
    # Claro: fondo blanco como el icono oficial
    "youtube-c3": {"fill": WHITE_BG, "groups": [play_white(), pill()]},
    # Claro con el triángulo prisma
    "youtube-c4": {"fill": WHITE_BG, "groups": [play_prism(), pill("pastilla-lente")]},
    # (c2 y c4 descartados: la refracción del hueco pequeño dibuja una estrella dentro del triángulo)
    # Claro con el rojo más fiel: la pastilla deja pasar menos el blanco del fondo
    "youtube-c5": {"fill": WHITE_BG, "groups": [
        play_white(),
        glass("pastilla", fill=YT_RED, alpha=1.0, translucency=0.1, blur=0.3,
              refraction=(0.35, 0.3), shadow="layer-color"),
    ]},
}


def main(names=None):
    """Escribe los aprobados; con nombres de concepto, escribe esos para renderizarlos."""
    geo = pieces()
    clean("youtube")
    targets = {n: n for n in names} if names else APPROVED
    for name, concept in targets.items():
        spec = CONCEPTS[concept]
        write_icon(name, spec["fill"], spec["groups"], geo)


if __name__ == "__main__":
    import sys
    main(sys.argv[1:] or None)
