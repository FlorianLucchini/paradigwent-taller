"""Draw the board background (a field split by a river, one lane per attack line).

uv run python -m taller.tablero

Saved at its native 320 x 200; the game scales it x4 to 1280 x 800 without smoothing.
"""

import numpy as np
from PIL import Image

from taller.datos import ASSETS, hex_a_rgb

W, H = 320, 200
LEFT, RIGHT, MID = 52, 284, 100  # left column | center | right column; rival above MID
PLAQUE_W, SCORE_W = 16, 18
# Rows of the grid (name, y0, y1): rival on top, mirrored below the river
ROWS = [
    ("mano-rival", 0, 28), ("asedio", 28, 47), ("distancia", 47, 66), ("cuerpo-a-cuerpo", 66, 85),
    ("info-rival", 85, 96), ("rio", 96, 104), ("info", 104, 115),
    ("cuerpo-a-cuerpo", 115, 134), ("distancia", 134, 153), ("asedio", 153, 172), ("mano", 172, 200),
]  # fmt: skip
GRASS = ["#2b3320", "#334026", "#3c4a2b", "#4a4630"]
GROUND = {
    "cuerpo-a-cuerpo": ["#33281e", "#3b2f24", "#44362a"],  # trodden dirt
    "distancia": ["#3a4a2a", "#435531", "#4c5f37"],  # tall grass
    "asedio": ["#37362f", "#403e37", "#4a473f"],  # gravel
}

rng = np.random.default_rng(5)


def rgb(color: str) -> np.ndarray:
    return np.array(hex_a_rgb(color), dtype=float)


def noise(w: int, h: int, cell: int, seed: int) -> np.ndarray:
    """Value noise: a random grid, bilinear upsampled."""
    g = np.random.default_rng(seed).random((h // cell + 2, w // cell + 2))
    ys, xs = np.mgrid[0:h, 0:w] / cell
    y0, x0 = ys.astype(int), xs.astype(int)
    fy, fx = ys - y0, xs - x0
    a, b = g[y0, x0], g[y0, x0 + 1]
    c, d = g[y0 + 1, x0], g[y0 + 1, x0 + 1]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def quantize(v: np.ndarray, colors: list[str]) -> np.ndarray:
    """Map a 0..1 field to a few palette steps."""
    idx = np.clip((v * len(colors)).astype(int), 0, len(colors) - 1)
    return np.array([rgb(c) for c in colors])[idx]


def campo() -> Image.Image:
    img = quantize(np.clip(noise(W, H, 6, 6) * 0.7 + noise(W, H, 2, 7) * 0.3, 0, 0.999), GRASS)
    x0, x1 = LEFT + 3, RIGHT - 3
    for k, (name, y0, y1) in enumerate(ROWS):
        if name not in GROUND:
            continue
        tex = np.clip(noise(x1 - x0, y1 - y0, 2, 20 + k) * 0.8 + 0.1, 0, 0.999)
        img[y0 + 1 : y1 - 1, x0:x1] = quantize(tex[1:-1], GROUND[name])
        img[y0 + 1, x0:x1] = rgb("#1a1e12")  # curb: dark top, light bottom
        img[y1 - 2, x0:x1] = rgb("#5b5a44")
        img[y0 + 1 : y1 - 1, x0] = img[y0 + 1 : y1 - 1, x1 - 1] = rgb("#1a1e12")
        for px0, px1 in [(x0 + 1, x0 + 1 + PLAQUE_W), (x1 - 1 - SCORE_W, x1 - 1)]:  # icon and strength plaques
            img[y0 + 2 : y1 - 2, px0:px1] = rgb("#4b4a44")
            img[y0 + 2, px0:px1] = rgb("#6a685f")
            img[y1 - 3, px0:px1] = rgb("#2c2b27")

    wave = np.round(np.sin(np.arange(W) / 14)).astype(int)
    for x in range(W):
        c = MID + wave[x]
        img[c - 4 : c + 4, x] = rgb("#5c5236")
        img[c - 3 : c + 3, x] = rgb("#22384a")
        img[c - 1 : c + 1, x] = rgb("#2a4659")
        if x % 7 == int(rng.integers(0, 7)):
            img[c - 1, x] = rgb("#6f8fa0")

    lanes = [(a, b) for n, a, b in ROWS if n in GROUND]
    for _ in range(60):  # tufts and pebbles outside the lanes
        x, y = int(rng.integers(0, W)), int(rng.integers(0, H))
        in_lane = LEFT <= x < RIGHT and any(a <= y < b for a, b in lanes)
        if abs(y - MID) > 6 and not in_lane:
            img[y, x] = rgb("#58613a") if rng.random() < 0.7 else rgb("#6b6658")

    img[:, :LEFT] *= 0.6
    img[:, RIGHT:] *= 0.6
    img[:, LEFT - 1 : LEFT + 1] = img[:, RIGHT - 1 : RIGHT + 1] = rgb("#151a10")

    imagen = Image.fromarray(img.clip(0, 255).astype(np.uint8))
    for name, y0, y1 in ROWS:
        if name in GROUND:
            icono = Image.open(ASSETS / "piezas" / f"linea-{name}.png")
            imagen.paste(icono, (LEFT + 4 + (PLAQUE_W - 12) // 2, y0 + (y1 - y0 - 12) // 2), icono)
    return imagen


def main() -> None:
    destino = ASSETS / "tablero" / "campo.png"
    campo().save(destino)
    print(f"{destino.relative_to(ASSETS.parent)}  {W} x {H}")


if __name__ == "__main__":
    main()
