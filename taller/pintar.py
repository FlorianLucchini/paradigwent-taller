"""Render the hand-drawn board pieces to PNG at their native size.

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


def main() -> None:
    pals = paletas()
    destino = ASSETS / "piezas"
    for archivo, (mapa, faccion) in sprites.PIEZAS.items():
        pintar(mapa, pals[faccion]).save(destino / f"{archivo}.png")
    print(f"{len(sprites.PIEZAS)} piezas en {destino}")


if __name__ == "__main__":
    main()
