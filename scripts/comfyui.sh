#!/usr/bin/env bash
# Install or start ComfyUI with the model and LoRA this project uses.
#
#   scripts/comfyui.sh instalar   # clone ComfyUI, install PyTorch and download the models
#   scripts/comfyui.sh levantar   # start the server on http://127.0.0.1:8188
#
# ComfyUI lives outside this repo, in $COMFYUI_DIR (default: ~/tools/ComfyUI).
set -euo pipefail

DIR="${COMFYUI_DIR:-$HOME/tools/ComfyUI}"
HF="https://huggingface.co"
MODELO="$HF/Comfy-Org/stable-diffusion-v1-5-archive/resolve/main/v1-5-pruned-emaonly-fp16.safetensors"
LORA="$HF/artificialguybr/pixelartredmond-1-5v-pixel-art-loras-for-sd-1-5/resolve/main/PixelArtRedmond15V-PixelArt-PIXARFK.safetensors"

instalar() {
  command -v uv >/dev/null || { echo "Falta uv: https://docs.astral.sh/uv/" >&2; exit 1; }
  [ -d "$DIR" ] || git clone --depth 1 https://github.com/comfyanonymous/ComfyUI "$DIR"
  cd "$DIR"
  [ -d .venv ] || uv venv --python 3.12 .venv
  export UV_HTTP_TIMEOUT=600
  uv pip install --python .venv/bin/python torch torchvision --index-url https://download.pytorch.org/whl/cu128
  uv pip install --python .venv/bin/python -r requirements.txt
  bajar "$MODELO" models/checkpoints/v1-5-pruned-emaonly-fp16.safetensors
  bajar "$LORA" models/loras/PixelArtRedmond15V.safetensors
  echo "ComfyUI listo en $DIR"
}

bajar() {
  [ -s "$2" ] && { echo "Ya está: $2"; return; }
  curl -L --retry 3 -o "$2" "$1"
}

levantar() {
  cd "$DIR"
  exec .venv/bin/python main.py --listen 127.0.0.1 --port 8188 --disable-auto-launch
}

case "${1:-}" in
  instalar) instalar ;;
  levantar) levantar ;;
  *) echo "Uso: $0 instalar | levantar" >&2; exit 1 ;;
esac
