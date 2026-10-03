# Estructura

```
paradigwent-taller/
├── datos/
│   ├── cartas.json       las 90 cartas: fuente de verdad
│   ├── paletas.json      colores del pixel art de cada facción
│   └── prompts.json      descripción en inglés de cada carta para Stable Diffusion
├── assets/
│   ├── ilustraciones/    una imagen por carta: <id>.png
│   ├── piezas/           fichas de vida, íconos de línea, emblemas
│   ├── dorsos/           la parte de atrás de las cartas
│   ├── tablero/          la mesa y sus zonas
│   └── sonidos/          música y efectos (WAV)
├── taller/               scripts en Python
└── pruebas/<lote>/       candidatas generadas, index.html para revisarlas y elegidas.json
```

## Las cartas

`datos/cartas.json` tiene una entrada por carta. El `id` es el nombre sin tildes, y es
también el nombre de su ilustración (`assets/ilustraciones/saxardent.png`).

```json
{ "id": "saxardent", "nombre": "Saxardent", "faccion": "DRACONIENS", "tipo": "criatura",
  "linea": "CUERPO_A_CUERPO", "fuerza": 10, "descripcion": "Golem de magma" }
```

Según el `tipo`, la carta suma un campo:

| Tipo | Campo extra | Ejemplo |
|---|---|---|
| `criatura` con habilidad | `habilidad` | `{ "tipo": "DuplicarLinea", "linea": "ASEDIO" }` |
| `efecto` | `efecto` | `{ "tipo": "RobarCartas", "cantidad": 2 }` |
| `clima` | `lineaAfectada` (en vez de `linea` y `fuerza`) | `"DISTANCIA"` |

Los efectos posibles son `DuplicarLinea`, `EliminarCriatura`, `RobarCartas`,
`ResucitarCarta` y `Sabotear`.

## El pixel art

- Se guarda en su **tamaño real**: ilustraciones de 64 × 64, piezas de 12 × 12 y
  emblemas de 16 × 16.
- El juego lo agranda **sin suavizado**, así los píxeles quedan nítidos:
  `imageView.setSmooth(false)` en JavaFX.
- Cada facción usa solo los colores de su paleta en `datos/paletas.json`.

## Marco, dorsos y tablero

El marco de la carta (nombre, fuerza, línea, descripción, color de la facción) lo dibuja
el juego con JavaFX a partir de `cartas.json`, así que no hay una imagen por carta
completa. En `assets/` quedan solo las partes gráficas: la ilustración, los íconos y los
fondos.
