# Paradigwent · Taller

![Dorsos y piezas del tablero](docs/img/muestra.png)

Arte y datos de **Paradigwent**, el juego de cartas del TP1 de Paradigmas de la
Programación (FIUBA): un Gwent simplificado en Java y JavaFX con tres facciones,
**Draconiens**, **Lothrim** y **Hoplitas**.

Este repo no tiene lógica del juego. Tiene lo que el juego carga: las 90 cartas en JSON,
las ilustraciones en pixel art, los dorsos, las piezas del tablero y (más adelante) los
sonidos, junto con los scripts que los generan.

## Qué hay

| Carpeta | Contenido |
|---|---|
| `datos/` | Las cartas, las paletas de cada facción y los textos para generar ilustraciones |
| `assets/` | Lo que usa el juego: ilustraciones, dorsos, piezas del tablero y sonidos |
| `taller/` | Los scripts en Python que generan los assets |
| `scripts/` | Instalación y arranque de ComfyUI |
| `pruebas/` | Ilustraciones candidatas, para elegir antes de pasarlas a `assets/` |
| `docs/` | Documentación |

## Empezar

Hace falta [uv](https://docs.astral.sh/uv/), que instala Python y las dependencias.

```bash
git clone https://github.com/FlorianLucchini/paradigwent-taller
cd paradigwent-taller
uv sync
uv run python -m taller.pintar   # dibuja los dorsos y las piezas en assets/
```

Generar ilustraciones necesita además una placa de video NVIDIA (con 4 GB alcanza) y
ComfyUI, que se instala con `scripts/comfyui.sh instalar`. El paso a paso está en
[docs/uso.md](docs/uso.md).

## Documentación

- [Uso](docs/uso.md): cómo generar cada cosa y cómo agregar o cambiar una carta.
- [Herramientas](docs/herramientas.md): qué se instala, para qué sirve y qué licencias tiene.
- [Formatos](docs/formatos.md): los archivos de `datos/` y cómo están guardados los assets.

## Estado

| Parte | Estado |
|---|---|
| Datos de las 90 cartas | Listos |
| Dorsos, fichas de vida, íconos de línea, emblemas | Listos |
| Ilustraciones | Generadas, en elección (`pruebas/mazo-1/`) |
| Tablero | Pendiente |
| Sonidos | Pendientes |

## Autores y licencia

Florian Lucchini y Matías Portela.

El código está bajo [licencia MIT](LICENSE). Las imágenes, los datos y los sonidos están
bajo [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.es): se pueden usar
citando a los autores. Las ilustraciones de las cartas están generadas con IA (Stable
Diffusion).
