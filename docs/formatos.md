# Formatos

## cartas.json

Una entrada por carta, 30 por facción. El `id` es el nombre sin tildes en minúscula, y
es también el nombre de su ilustración.

```json
{ "id": "saxardent", "nombre": "Saxardent", "faccion": "DRACONIENS", "tipo": "CRIATURA",
  "linea": "CUERPO_A_CUERPO", "fuerza": 10, "descripcion": "Golem de magma" }
```

| Campo | Valores |
|---|---|
| `faccion` | `DRACONIENS`, `LOTHRIM`, `HOPLITAS` |
| `tipo` | `CRIATURA`, `EFECTO`, `CLIMA` |
| `linea` | `CUERPO_A_CUERPO`, `DISTANCIA`, `ASEDIO` (criaturas) |
| `fuerza` | 1 a 10 (criaturas) |

Algunas cartas suman un campo según su tipo:

| Carta | Campo | Ejemplo |
|---|---|---|
| Criatura con habilidad | `habilidad` | `{ "tipo": "DuplicarLinea", "linea": "ASEDIO" }` |
| Efecto | `efecto` | `{ "tipo": "RobarCartas", "cantidad": 2 }` |
| Clima | `lineaAfectada`, en lugar de `linea` y `fuerza` | `"DISTANCIA"` |

Las habilidades y los efectos posibles son `DuplicarLinea` (con `linea`),
`EliminarCriatura`, `RobarCartas` (con `cantidad`), `ResucitarCarta` y `Sabotear`.

## prompts.json

Los textos en inglés que recibe Stable Diffusion.

| Campo | Qué es |
|---|---|
| `plantillas` | El texto completo: `criatura` para criaturas y climas, `escena` para efectos |
| `negativo` | Lo que no tiene que aparecer en ninguna imagen |
| `facciones` | El estilo de cada facción |
| `escenarios` | El fondo de cada facción |
| `cartas` | Qué se ve en cada carta |

Cada carta es un texto o, si hace falta excluir algo solo en esa carta, un objeto:

```json
"unguis": {
  "texto": "a dragon-headed humanoid warrior with long iron claws on his hands, crouching",
  "evitar": "dragon wings, quadruped dragon, feral dragon, demon"
}
```

## paletas.json

Los colores de cada facción. Las letras de `colores` son las que usan los mapas de
`taller/sprites.py`.

| Campo | Qué es |
|---|---|
| `colores` | Letra → color |
| `cielo`, `suelo` | Tonos oscuros que se suman al pixelar ilustraciones |
| `soloPiezas` | Letras que se usan en las piezas pero no en las ilustraciones |
| `dorso` | Color de fondo del dorso |

## Assets

| Carpeta | Archivo | Tamaño |
|---|---|---|
| `assets/ilustraciones/` | `<id>.png` | 64 × 64 |
| `assets/dorsos/` | `dorso-<faccion>.png` | 50 × 70 |
| `assets/piezas/` | `vida-<faccion>.png`, `linea-<linea>.png` | 12 × 12 |
| `assets/piezas/` | `emblema-<faccion>.png` | 16 × 16 |
| `assets/sonidos/` | `<evento>.wav` (JavaFX no reproduce OGG) | Mono, 22 050 Hz, 16 bits |

Todo se guarda en su tamaño real. El juego lo agranda sin suavizado para que los píxeles
queden nítidos: `imageView.setSmooth(false)` en JavaFX.

El marco de la carta (nombre, fuerza, línea, descripción y color de la facción) no es
una imagen: lo dibuja el juego a partir de `cartas.json`.
