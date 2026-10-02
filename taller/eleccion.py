"""Build a self-contained page to pick one candidate per card.

    uv run python -m taller.eleccion mazo-1

Writes pruebas/<lote>/eleccion.html with every image embedded. Published as a
Claude artifact, the page stores the choices in its shared database; opened as a
plain file, it shows them as JSON to paste into pruebas/<lote>/elegidas.json.
"""

import argparse
import base64
import io
import json
from pathlib import Path

from PIL import Image

from taller.datos import PRUEBAS, cargar

PLANTILLA = Path(__file__).with_name("eleccion.html")


def uri(imagen: Image.Image, formato: str = "PNG", **opciones) -> str:
    buffer = io.BytesIO()
    imagen.save(buffer, formato, **opciones)
    return f"data:image/{formato.lower()};base64," + base64.b64encode(buffer.getvalue()).decode()


def main() -> None:
    args = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    args.add_argument("lote", help="carpeta dentro de pruebas/")
    args.add_argument("--opciones", type=int, default=4)
    args.add_argument("--lado", type=int, default=48)
    a = args.parse_args()

    lote = PRUEBAS / a.lote
    datos = []
    for c in cargar("cartas.json")["cartas"]:
        rango = range(1, a.opciones + 1)
        datos.append(
            {
                "id": c["id"],
                "nombre": c["nombre"],
                "desc": c["descripcion"],
                "faccion": c["faccion"],
                "tipo": c["tipo"],
                "linea": c.get("linea") or c.get("lineaAfectada"),
                "fuerza": c.get("fuerza"),
                "px": [uri(Image.open(lote / f"pixeladas-{a.lado}" / f"{c['id']}-{n}.png")) for n in rango],
                "raw": [
                    uri(
                        Image.open(lote / "crudas" / f"{c['id']}-{n}.png").convert("RGB").resize((160, 160)),
                        "JPEG",
                        quality=72,
                    )
                    for n in rango
                ],
            }
        )

    html = PLANTILLA.read_text(encoding="utf-8").replace("__CARTAS__", json.dumps(datos)).replace("__LOTE__", a.lote)
    salida = lote / "eleccion.html"
    salida.write_text(html, encoding="utf-8")
    print(f"{len(datos)} cartas en {salida} ({len(html) // 1024} KB)")


if __name__ == "__main__":
    main()
