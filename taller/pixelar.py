"""Turn a large generated image into faction pixel art.

The image is shrunk by averaging blocks and every pixel is forced onto the
faction palette, which is what keeps all illustrations consistent.
"""

from PIL import Image

from taller.datos import hex_a_rgb


def colores_de(paleta: dict) -> list[tuple[int, int, int]]:
    excluidos = set(paleta.get("soloPiezas", []))
    hexas = [h for letra, h in paleta["colores"].items() if letra not in excluidos]
    hexas += paleta["cielo"]
    if paleta["suelo"]:
        hexas.append(paleta["suelo"])
    return [hex_a_rgb(h) for h in hexas]


def pixelar(imagen: Image.Image, paleta: dict, lado: int = 64) -> Image.Image:
    chica = imagen.convert("RGB").resize((lado, lado), Image.Resampling.BOX)

    colores = colores_de(paleta)
    plana = [canal for color in colores for canal in color]
    plana += plana[:3] * (256 - len(colores))  # PIL needs a full 256-color palette

    molde = Image.new("P", (1, 1))
    molde.putpalette(plana)
    return chica.quantize(palette=molde, dither=Image.Dither.NONE).convert("RGB")
