# Uso

Todos los comandos se corren desde la raíz del repo, después de `uv sync`.

## Dorsos y piezas del tablero

```bash
uv run python -m taller.pintar
```

Dibuja los 3 dorsos en `assets/dorsos/` y las fichas de vida, los íconos de línea y los
emblemas en `assets/piezas/`. Salen de mapas de píxeles escritos a mano en
`taller/sprites.py`, así que siempre dan el mismo resultado.

## Ilustraciones de las cartas

Se hacen en cuatro pasos: generar candidatas, elegir, revisar y pasar a `assets/`.

**1. Levantar ComfyUI** (la primera vez, `scripts/comfyui.sh instalar`):

```bash
scripts/comfyui.sh levantar      # queda escuchando en http://127.0.0.1:8188
```

**2. Generar candidatas**, en otra terminal:

```bash
uv run python -m taller.ilustrar saxardent thoron sideron --lote mi-lote
```

Por cada carta genera 8 opciones (`--opciones` para cambiarlo), cada una en dos
versiones: la original de 512 × 512 en `pruebas/mi-lote/crudas/` y la pixelada de
64 × 64 en `pruebas/mi-lote/pixeladas-64/`. Tarda unos 5 segundos por imagen. Si se
corta, al volver a correrlo sigue desde donde quedó.

**3. Elegir**:

```bash
uv run python -m taller.eleccion mi-lote
```

Arma `pruebas/mi-lote/eleccion.html`, una página con todas las opciones de cada carta.
Se abre en el navegador, se toca la mejor de cada una y abajo aparece el resultado en
JSON. Ese texto se guarda como `pruebas/mi-lote/elegidas.json`:

```json
{ "saxardent": 3, "thoron": 1, "sideron": 6 }
```

**4. Pasar a `assets/`**:

```bash
uv run python -m taller.promover mi-lote
```

Copia cada opción elegida a `assets/ilustraciones/<id>.png`.

## Agregar o cambiar una carta

1. Editar la carta en `datos/cartas.json`.
2. Escribir o ajustar su descripción en inglés en `datos/prompts.json`.
3. Generar solo esa carta: `uv run python -m taller.ilustrar <id> --lote <lote>`.

Si una carta sale mal en todas las opciones, conviene describirla más literal y con un
solo elemento quieto ("una torre rota caída de costado" funciona mejor que "una torre
que cae en una grieta"). Lo que no tiene que aparecer va en el campo `evitar` de esa
carta (ver [formatos](formatos.md#promptsjson)).

## Código

```bash
uv run ruff format   # formatea
uv run ruff check    # revisa errores comunes
```
