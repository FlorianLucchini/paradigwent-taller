import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DATOS = RAIZ / "datos"
ASSETS = RAIZ / "assets"
PRUEBAS = RAIZ / "pruebas"


def cargar(nombre: str) -> dict:
    return json.loads((DATOS / nombre).read_text(encoding="utf-8"))


def cartas() -> dict[str, dict]:
    return {c["id"]: c for c in cargar("cartas.json")["cartas"]}


def paletas() -> dict[str, dict]:
    return cargar("paletas.json")


def hex_a_rgb(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))
