# Paradigwent · Taller

Assets de **Paradigwent**, el TP1 de Paradigmas de la Programación (FIUBA): un Gwent
simplificado en Java y JavaFX, con tres facciones (Draconiens, Lothrim y Hoplitas).

Acá vive todo lo que **no es lógica del juego**: los datos de las 90 cartas, el pixel art,
las piezas del tablero y los sonidos. El juego toma de este repo lo que necesita.

## Qué hay

| Carpeta | Contenido |
|---|---|
| `datos/` | Las cartas, las paletas de cada facción y los textos para generar ilustraciones |
| `assets/` | Los archivos que usa el juego: ilustraciones, piezas del tablero, dorsos, sonidos |
| `taller/` | Los scripts que generan esos archivos |
| `pruebas/` | Lotes de ilustraciones generadas, para revisar antes de pasarlas a `assets/` |

## Uso

Requiere [uv](https://docs.astral.sh/uv/).

```bash
uv sync                                   # instala las dependencias
uv run python -m taller.pintar            # dibuja el pixel art hecho por código en assets/
uv run python -m taller.ilustrar sideron --lote prueba   # genera ilustraciones (necesita ComfyUI)
```

## Documentación

- [Estructura](docs/estructura.md): qué va en cada carpeta y el formato de las cartas.
- [Herramientas](docs/herramientas.md): con qué se genera cada cosa y cuánto cuesta.

## Autores

Florian Lucchini y Matías Portela.
