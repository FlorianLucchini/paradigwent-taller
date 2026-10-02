"""Render the hand-drawn board pieces and card backs to PNG at their native size.

uv run python -m taller.pintar
"""

from PIL import Image

from taller import sprites
from taller.datos import ASSETS, hex_a_rgb, paletas


def pintar(mapa: str, paleta: dict) -> Image.Image:
    filas = sprites.filas(mapa)
    imagen = Image.new("RGBA", (len(filas[0]), len(filas)), (0, 0, 0, 0))
    for y, fila in enumerate(filas):
        for x, letra in enumerate(fila):
            if letra in paleta["colores"]:
                imagen.putpixel((x, y), (*hex_a_rgb(paleta["colores"][letra]), 255))
    return imagen


def oscurecer(color: tuple[int, int, int], factor: float) -> tuple[int, int, int, int]:
    return (*(int(c * factor) for c in color), 255)


def dorso(emblema: str, paleta: dict, ancho: int = 50, alto: int = 70) -> Image.Image:
    """Card back: faction color, a diagonal lattice, a dark border and the emblem at x2."""
    base = hex_a_rgb(paleta["dorso"])
    imagen = Image.new("RGBA", (ancho, alto), (*base, 255))
    for y in range(alto):
        for x in range(ancho):
            if (x + y) % 6 == 0 or (x - y) % 6 == 0:
                imagen.putpixel((x, y), oscurecer(base, 0.82))
            if min(x, y, ancho - 1 - x, alto - 1 - y) < 2:
                imagen.putpixel((x, y), oscurecer(base, 0.55))
    figura = pintar(emblema, paleta)
    figura = figura.resize((figura.width * 2, figura.height * 2), Image.Resampling.NEAREST)
    imagen.alpha_composite(figura, ((ancho - figura.width) // 2, (alto - figura.height) // 2))
    return imagen


def main() -> None:
    pals = paletas()
    destino = ASSETS / "piezas"
    for archivo, (mapa, faccion) in sprites.PIEZAS.items():
        pintar(mapa, pals[faccion]).save(destino / f"{archivo}.png")
    for faccion, emblema in sprites.DORSOS.items():
        dorso(emblema, pals[faccion]).save(ASSETS / "dorsos" / f"dorso-{faccion.lower()}.png")
    print(f"{len(sprites.PIEZAS)} piezas y {len(sprites.DORSOS)} dorsos en {ASSETS}")


if __name__ == "__main__":
    main()
