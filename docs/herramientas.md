# Herramientas

Todo es gratuito y corre en la computadora propia.

| Herramienta | Para qué | ¿Hace falta? |
|---|---|---|
| [uv](https://docs.astral.sh/uv/) | Instala Python (3.12 o más nuevo) y las dependencias del repo | Siempre |
| [Pillow](https://python-pillow.org/) | Dibuja y procesa las imágenes | Siempre (la instala `uv sync`) |
| [Ruff](https://docs.astral.sh/ruff/) | Formatea y revisa el código Python | Solo para tocar el código |
| [ComfyUI](https://github.com/comfyanonymous/ComfyUI) | Ejecuta Stable Diffusion | Solo para generar ilustraciones |

## Stable Diffusion

Es un modelo abierto que genera imágenes a partir de un texto. Corre en la placa de
video propia, sin cuenta ni pago.

- **Modelo:** Stable Diffusion 1.5, en su versión fp16 (2 GB). Es la versión que entra
  en una placa de 4 GB.
- **LoRA:** Pixel Art Redmond. Un LoRA es un archivo chico que se suma al modelo para
  darle un estilo; este lo lleva al pixel art y se activa con la palabra `PixArFK`.
- **ComfyUI** carga los dos y ofrece una API local, que es la que usa `taller.ilustrar`.

Necesita una placa NVIDIA con al menos 4 GB de memoria. Con una RTX 3050 Ti de
notebook tarda unos 5 segundos por imagen.

### Instalación

```bash
scripts/comfyui.sh instalar
```

Clona ComfyUI en `~/tools/ComfyUI` (otra ruta con la variable `COMFYUI_DIR`), instala
PyTorch con soporte CUDA y descarga el modelo y el LoRA de Hugging Face. Ocupa unos 11 GB.

## Por qué las ilustraciones se pixelan después

Stable Diffusion genera a 512 × 512 en estilo pixel art, pero sus "píxeles" no son
parejos ni respetan una paleta. `taller.pixelar` reduce la imagen a 64 × 64 y fuerza
cada píxel al color más cercano de la paleta de la facción. Eso es lo que hace que las
90 cartas parezcan del mismo juego.

## Licencias

| Recurso | Licencia |
|---|---|
| Stable Diffusion 1.5 | CreativeML OpenRAIL-M: permite usar las imágenes generadas |
| LoRA Pixel Art Redmond | Permite trabajos derivados, sin crédito obligatorio |
| ComfyUI | GPL-3.0 (se usa como programa externo, no se distribuye acá) |

El enunciado del TP permite contenido generado con IA, siempre que se acredite.
