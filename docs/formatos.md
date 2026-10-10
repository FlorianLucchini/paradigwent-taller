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
| `assets/tablero/` | `campo.png` | 320 × 200 |
| `assets/sonidos/` | `<evento>.wav` (JavaFX no reproduce OGG) | Mono, 22 050 Hz, 16 bits |

Todo se guarda en su tamaño real. El juego lo agranda sin suavizado para que los píxeles
queden nítidos: `imageView.setSmooth(false)` en JavaFX.

El marco de la carta (nombre, fuerza, línea, descripción y color de la facción) no es
una imagen: lo dibuja el juego a partir de `cartas.json`.

## Tablero

`campo.png` se muestra agrandado ×4, a 1280 × 800. Las coordenadas de esta sección
están en píxeles de esa pantalla.

| Columna | Desde x | Hasta x | Para qué |
|---|---|---|---|
| Izquierda | 0 | 208 | Clima y botones |
| Centro | 208 | 1136 | Manos y líneas de los dos jugadores |
| Derecha | 1136 | 1280 | Mazo y descarte |

En el centro, las franjas de las líneas van de x = 220 a x = 1124. Cada una tiene a la
izquierda una placa con el ícono de la línea (x de 224 a 288) y a la derecha una placa
vacía para el número de fuerza (x de 1052 a 1124). Las cartas entran entre las dos, de
x = 288 a x = 1052.

| Fila | Desde y | Hasta y | Alto |
|---|---|---|---|
| Mano del rival | 0 | 112 | 112 |
| Asedio del rival | 112 | 188 | 76 |
| Distancia del rival | 188 | 264 | 76 |
| Cuerpo a cuerpo del rival | 264 | 340 | 76 |
| Vidas y puntaje del rival | 340 | 384 | 44 |
| Río | 384 | 416 | 32 |
| Tus vidas y puntaje | 416 | 460 | 44 |
| Tu cuerpo a cuerpo | 460 | 536 | 76 |
| Tu distancia | 536 | 612 | 76 |
| Tu asedio | 612 | 688 | 76 |
| Tu mano | 688 | 800 | 112 |
