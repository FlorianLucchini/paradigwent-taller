"""Copy the chosen candidate of each card into assets/ilustraciones/.

The choices live in pruebas/<lote>/elegidas.json as {"card_id": option_number}:

    uv run python -m taller.promover mazo-1
"""

import argparse
import json
import shutil

from taller.datos import ASSETS, PRUEBAS


def main() -> None:
    args = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    args.add_argument("lote", help="carpeta dentro de pruebas/")
    args.add_argument("--lado", type=int, default=48)
    a = args.parse_args()

    lote = PRUEBAS / a.lote
    elegidas = json.loads((lote / "elegidas.json").read_text(encoding="utf-8"))
    destino = ASSETS / "ilustraciones"
    for carta_id, opcion in elegidas.items():
        shutil.copyfile(lote / f"pixeladas-{a.lado}" / f"{carta_id}-{opcion}.png", destino / f"{carta_id}.png")
    print(f"{len(elegidas)} ilustraciones copiadas a {destino}")


if __name__ == "__main__":
    main()
