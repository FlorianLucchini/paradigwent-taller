# Herramientas

Todo es gratuito y corre en una computadora común.

| Herramienta | Para qué |
|---|---|
| [uv](https://docs.astral.sh/uv/) | Instala Python y las dependencias del proyecto |
| [Pillow](https://python-pillow.org/) | Dibuja y procesa las imágenes |
| [Ruff](https://docs.astral.sh/ruff/) | Formatea y revisa el código: `uv run ruff format` y `uv run ruff check` |
| Stable Diffusion 1.5 | Genera imágenes a partir de un texto |
| ComfyUI | El programa que ejecuta Stable Diffusion |
| LoRA Pixel Art Redmond | Le enseña a Stable Diffusion el estilo pixel art |

## Cómo se hace cada imagen

**Piezas del tablero, por código.** Cada pieza es un mapa de letras en `taller/sprites.py`,
donde cada letra es un color de la paleta. `taller.pintar` las convierte en PNG.

**Ilustraciones de las cartas, con Stable Diffusion.** `taller.ilustrar` toma la
descripción en inglés de cada carta (`datos/prompts.json`) y:

1. Le pide a Stable Diffusion varias opciones de 512 × 512, ya en estilo pixel art y con
   el escenario de su facción.
2. Las achica a 48 × 48 (otros tamaños con `--lados 48 64`) y fuerza cada píxel a la
   paleta de la facción, que es lo que hace que todas parezcan del mismo juego. Los colores
   de `soloPiezas` (como el rosa de la flor Lothrim) quedan afuera.
3. Arma `pruebas/<lote>/index.html` para comparar y elegir.

Si se corta, al volver a correrlo sigue desde donde quedó. Las elegidas se anotan en
`pruebas/<lote>/elegidas.json` (`{"saxardent": 3, ...}`) y `taller.promover` las copia a
`assets/ilustraciones/`.

## Stable Diffusion, ComfyUI y LoRA

- **Stable Diffusion** es un modelo abierto que genera imágenes a partir de un texto.
  Corre en la placa de video propia: no hace falta cuenta ni pago. Usamos la versión 1.5
  porque entra en una placa de 4 GB.
- **ComfyUI** es la aplicación que lo ejecuta. Tiene una interfaz web para probar a mano
  y una API, que es la que usa `taller.ilustrar`.
- **Un LoRA** es un archivo chico que se suma al modelo para darle un estilo. El de pixel
  art se activa con la palabra `PixArFK` en el texto.

### Instalación

```bash
git clone https://github.com/comfyanonymous/ComfyUI ~/tools/ComfyUI
cd ~/tools/ComfyUI
uv venv && source .venv/bin/activate
uv pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128
uv pip install -r requirements.txt
```

Después se bajan dos archivos de Hugging Face:

| Archivo | Va en | Origen |
|---|---|---|
| `v1-5-pruned-emaonly-fp16.safetensors` (2 GB) | `models/checkpoints/` | [Comfy-Org/stable-diffusion-v1-5-archive](https://huggingface.co/Comfy-Org/stable-diffusion-v1-5-archive) |
| `PixelArtRedmond15V.safetensors` | `models/loras/` | [artificialguybr/pixelartredmond-1-5v](https://huggingface.co/artificialguybr/pixelartredmond-1-5v-pixel-art-loras-for-sd-1-5) |

### Uso

```bash
cd ~/tools/ComfyUI && source .venv/bin/activate && python main.py   # queda en http://127.0.0.1:8188
```

En otra terminal, desde este repo:

```bash
uv run python -m taller.ilustrar saxardent thoron sideron --lote comparacion
```

## Licencias

- Stable Diffusion 1.5 (CreativeML OpenRAIL-M) permite usar las imágenes generadas.
- El LoRA Pixel Art Redmond permite trabajos derivados y no pide crédito.
- El enunciado del TP permite contenido generado con IA. Las ilustraciones de Stable
  Diffusion se acreditan como tales en el README del juego.

## Sonidos

Todavía no están. La idea es sintetizar los efectos por código (estilo 8 bits, como el
pixel art) y guardarlos en WAV, porque JavaFX no reproduce OGG.
