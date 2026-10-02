"""Render the hand-drawn pixel maps to PNG at their native size.

uv run python -m taller.pintar
"""

from PIL import Image

from taller import sprites
from taller.datos import ASSETS, cartas, hex_a_rgb, paletas


def pintar(mapa: str, paleta: dict, con_fondo: bool = False) -> Image.Image:
    filas = sprites.filas(mapa)
    ancho, alto = len(filas[0]), len(filas)
    imagen = Image.new("RGBA", (ancho, alto), (0, 0, 0, 0))

    if con_fondo:
        cielo = paleta["cielo"]
        banda = -(-(alto - 3) // len(cielo))  # ceil
        for i, color in enumerate(cielo):
            imagen.paste((*hex_a_rgb(color), 255), (0, i * banda, ancho, min(alto, (i + 1) * banda)))
        imagen.paste((*hex_a_rgb(paleta["suelo"]), 255), (0, alto - 3, ancho, alto))

    for y, fila in enumerate(filas):
        for x, letra in enumerate(fila):
            if letra in paleta["colores"]:
                imagen.putpixel((x, y), (*hex_a_rgb(paleta["colores"][letra]), 255))
    return imagen


def main() -> None:
    pals = paletas()
    todas = cartas()

    destino = ASSETS / "piezas"
    for archivo, (mapa, faccion) in sprites.PIEZAS.items():
        pintar(mapa, pals[faccion]).save(destino / f"{archivo}.png")

    destino = ASSETS / "ilustraciones"
    for carta_id, mapa in sprites.ILUSTRACIONES.items():
        faccion = todas[carta_id]["faccion"]
        pintar(mapa, pals[faccion], con_fondo=True).save(destino / f"{carta_id}.png")

    print(f"{len(sprites.PIEZAS)} piezas y {len(sprites.ILUSTRACIONES)} ilustraciones en {ASSETS}")


if __name__ == "__main__":
    main()
