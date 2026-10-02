"""Generate illustration candidates with Stable Diffusion through ComfyUI.

ComfyUI has to be running (see docs/herramientas.md). Example:

    uv run python -m taller.ilustrar saxardent thoron sideron --lote comparacion

For each card it saves N raw candidates and their pixelated version under
pruebas/<lote>/, then writes the review sheet. Cards that already have their
candidates are skipped, so an interrupted run can be resumed.
"""

import argparse
import io
import json
import time
import urllib.parse
import urllib.request
import uuid
import zlib

from PIL import Image

from taller import hoja
from taller.datos import PRUEBAS, cargar, cartas, paletas
from taller.pixelar import pixelar

CHECKPOINT = "v1-5-pruned-emaonly-fp16.safetensors"
LORA = "PixelArtRedmond15V.safetensors"


def flujo(positivo: str, negativo: str, semilla: int) -> dict:
    """ComfyUI workflow in API format: checkpoint + LoRA -> sampler -> image."""
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CHECKPOINT}},
        "2": {
            "class_type": "LoraLoader",
            "inputs": {
                "model": ["1", 0],
                "clip": ["1", 1],
                "lora_name": LORA,
                "strength_model": 0.9,
                "strength_clip": 0.9,
            },
        },
        "3": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 1], "text": positivo}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 1], "text": negativo}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"width": 512, "height": 512, "batch_size": 1}},
        "6": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["2", 0],
                "positive": ["3", 0],
                "negative": ["4", 0],
                "latent_image": ["5", 0],
                "seed": semilla,
                "steps": 25,
                "cfg": 7.0,
                "sampler_name": "dpmpp_2m",
                "scheduler": "karras",
                "denoise": 1.0,
            },
        },
        "7": {"class_type": "VAEDecode", "inputs": {"samples": ["6", 0], "vae": ["1", 2]}},
        "8": {"class_type": "SaveImage", "inputs": {"images": ["7", 0], "filename_prefix": "paradigwent"}},
    }


def pedir(servidor: str, ruta: str, cuerpo: dict | None = None) -> bytes:
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    req = urllib.request.Request(f"{servidor}{ruta}", data=datos, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return resp.read()


def generar(servidor: str, positivo: str, negativo: str, semilla: int) -> Image.Image:
    cola = json.loads(
        pedir(servidor, "/prompt", {"prompt": flujo(positivo, negativo, semilla), "client_id": str(uuid.uuid4())})
    )
    pid = cola["prompt_id"]
    while True:
        historial = json.loads(pedir(servidor, f"/history/{pid}"))
        if pid in historial:
            break
        time.sleep(1)
    salida = historial[pid]["outputs"]["8"]["images"][0]
    consulta = urllib.parse.urlencode(
        {"filename": salida["filename"], "subfolder": salida["subfolder"], "type": salida["type"]}
    )
    return Image.open(io.BytesIO(pedir(servidor, f"/view?{consulta}")))


def main() -> None:
    args = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    args.add_argument("cartas", nargs="+", help="ids de cartas (ver datos/cartas.json)")
    args.add_argument("--lote", default="lote", help="carpeta dentro de pruebas/")
    args.add_argument("--opciones", type=int, default=4)
    args.add_argument("--lado", type=int, default=64, help="tamaño final en píxeles")
    args.add_argument("--servidor", default="http://127.0.0.1:8188")
    a = args.parse_args()

    todas, pals, prompts = cartas(), paletas(), cargar("prompts.json")
    crudas = PRUEBAS / a.lote / "crudas"
    pixeladas = PRUEBAS / a.lote / "pixeladas"
    crudas.mkdir(parents=True, exist_ok=True)
    pixeladas.mkdir(parents=True, exist_ok=True)

    for carta_id in a.cartas:
        carta = todas[carta_id]
        positivo = prompts["plantilla"].format(
            sujeto=prompts["cartas"][carta_id],
            faccion=prompts["facciones"][carta["faccion"]],
            escenario=prompts["escenarios"][carta["faccion"]],
        )
        for n in range(1, a.opciones + 1):
            nombre = f"{carta_id}-{n}.png"
            if (pixeladas / nombre).exists():
                continue
            inicio = time.time()
            imagen = generar(a.servidor, positivo, prompts["negativo"], semilla=zlib.crc32(nombre.encode()))
            imagen.save(crudas / nombre)
            pixelar(imagen, pals[carta["faccion"]], a.lado).save(pixeladas / nombre)
            print(f"{nombre} en {time.time() - inicio:.0f} s")

    hoja.escribir(a.lote, a.cartas, a.opciones)


if __name__ == "__main__":
    main()
