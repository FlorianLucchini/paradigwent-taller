"""Board background proposals: 320x200 pixel art scaled x4 to 1280x800 (layout of the view plan)."""

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

W, H = 320, 200
LEFT, RIGHT, MID = 52, 284, 100  # left column | center | right column; rival above MID
rng = np.random.default_rng(5)


def rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i : i + 2], 16) for i in (0, 2, 4)], dtype=float)


def noise(w, h, cell, seed):
    """Value noise: random grid, bilinear upsampled."""
    g = np.random.default_rng(seed).random((h // cell + 2, w // cell + 2))
    ys, xs = np.mgrid[0:h, 0:w] / cell
    y0, x0 = ys.astype(int), xs.astype(int)
    fy, fx = ys - y0, xs - x0
    a, b = g[y0, x0], g[y0, x0 + 1]
    c, d = g[y0 + 1, x0], g[y0 + 1, x0 + 1]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def quantize(v, colors):
    """Map a 0..1 field to a few palette steps (keeps the pixel-art look)."""
    idx = np.clip((v * len(colors)).astype(int), 0, len(colors) - 1)
    return np.array([rgb(c) for c in colors])[idx]


def shade(img, mask, k):
    img[mask] *= k


def frame_columns(img, dark):
    d = rgb(dark)
    img[:, LEFT - 1 : LEFT + 1] = d
    img[:, RIGHT - 1 : RIGHT + 1] = d


def wood():
    planks = ["#3b2416", "#4a2e1b", "#563621", "#62402a"]
    img = np.zeros((H, W, 3))
    grain = noise(W, H, 3, 1) * 0.5 + noise(W * 6, H, 6, 2)[:, ::6] * 0.5
    for i, y in enumerate(range(0, H, 10)):
        base = rng.integers(0, 2)
        v = np.clip(grain[y : y + 10] * 0.7 + base * 0.25, 0, 0.999)
        img[y : y + 10] = quantize(v, planks)
        img[y] = rgb("#24150c")  # seam
        off = int(rng.integers(0, 80))
        for x in range(off, W, 80):  # plank ends with nails
            img[y : y + 10, x] = rgb("#24150c")
            img[y + 3, min(W - 1, x + 2)] = rgb("#8a7b6a")
            img[y + 7, min(W - 1, x + 2)] = rgb("#8a7b6a")
    for _ in range(14):  # knots
        x, y = int(rng.integers(2, W - 4)), int(rng.integers(2, H - 3))
        img[y : y + 2, x : x + 3] = rgb("#2c1a10")
    side = np.zeros((H, W), bool)
    side[:, :LEFT] = side[:, RIGHT:] = True
    shade(img, side, 0.72)
    img[MID - 2 : MID + 2] = rgb("#1c100a")  # beam between halves
    for x in range(LEFT + 6, RIGHT, 16):
        img[MID - 1 : MID + 1, x : x + 2] = rgb("#9a8a74")
    frame_columns(img, "#1c100a")
    return img * 0.72  # darker, so brown cards stand out


def stone():
    greys = ["#3a3633", "#45403b", "#4f4943", "#5a534b"]
    img = np.zeros((H, W, 3))
    speck = noise(W, H, 2, 3)
    for r, y in enumerate(range(0, H, 14)):
        off = 0 if r % 2 == 0 else 11
        for x in range(-off, W, 22):
            v = np.clip(speck[y : y + 14, max(0, x) : x + 22] * 0.5 + rng.random() * 0.5, 0, 0.999)
            img[y : y + 14, max(0, x) : x + 22] = quantize(v, greys)
            img[y : y + 14, max(0, x)] = rgb("#26221f")
        img[y] = rgb("#26221f")
    for _ in range(10):  # cracks
        x, y = int(rng.integers(0, W)), int(rng.integers(0, H))
        for _k in range(6):
            if 0 <= x < W and 0 <= y < H:
                img[y, x] = rgb("#26221f")
            x += int(rng.integers(-1, 2))
            y += 1
    side = np.zeros((H, W), bool)
    side[:, :LEFT] = side[:, RIGHT:] = True
    shade(img, side, 0.75)
    img[MID - 4 : MID + 4, LEFT:RIGHT] = rgb("#4a1c1a")  # faded runner
    img[MID - 4 : MID + 4, LEFT:RIGHT] *= (0.85 + 0.15 * noise(RIGHT - LEFT, 8, 2, 9))[..., None]
    img[MID - 4, LEFT:RIGHT] = img[MID + 3, LEFT:RIGHT] = rgb("#8c6d3a")
    frame_columns(img, "#1f1b18")
    return img * 0.85


def felt():
    img = quantize(np.clip(noise(W, H, 2, 4) * 0.6 + 0.2, 0, 0.999), ["#1b2430", "#1f2a37", "#232f3d"])
    side = np.zeros((H, W), bool)
    side[:, :LEFT] = side[:, RIGHT:] = True
    shade(img, side, 0.8)
    gold = rgb("#a8873e")

    def stitch(x0, y0, x1, y1):
        for x in range(x0, x1 + 1):
            if x % 3 != 2:
                img[y0, x] = img[y1, x] = gold
        for y in range(y0, y1 + 1):
            if y % 3 != 2:
                img[y, x0] = img[y, x1] = gold

    stitch(3, 3, LEFT - 4, H - 4)
    stitch(LEFT + 3, 3, RIGHT - 4, MID - 4)
    stitch(LEFT + 3, MID + 3, RIGHT - 4, H - 4)
    stitch(RIGHT + 3, 3, W - 4, MID - 4)
    stitch(RIGHT + 3, MID + 3, W - 4, H - 4)
    img[MID, LEFT:RIGHT] = gold * 0.8
    cx = (LEFT + RIGHT) // 2
    for d in range(4):  # small diamond on the divider
        img[MID - d, cx - 3 + d : cx + 4 - d] = gold
        img[MID + d, cx - 3 + d : cx + 4 - d] = gold
    frame_columns(img, "#11161e")
    return img


def field():
    img = quantize(np.clip(noise(W, H, 6, 6) * 0.7 + noise(W, H, 2, 7) * 0.3, 0, 0.999),
                   ["#2b3320", "#334026", "#3c4a2b", "#4a4630"])  # fmt: skip
    yy = np.arange(W)
    wave = (np.sin(yy / 14) * 2 + np.sin(yy / 5) * 0.7).astype(int)
    for x in range(W):
        c = MID + wave[x]
        img[c - 7 : c + 7, x] = rgb("#5c5236")  # bank
        img[c - 5 : c + 5, x] = rgb("#22384a")
        img[c - 3 : c + 3, x] = rgb("#2a4659")
        if x % 9 == int(rng.integers(0, 9)):
            img[c - 1, x] = rgb("#6f8fa0")
    for _ in range(60):  # tufts and pebbles
        x, y = int(rng.integers(0, W)), int(rng.integers(0, H))
        if abs(y - MID) > 9:
            img[y, x] = rgb("#58613a") if rng.random() < 0.7 else rgb("#6b6658")
    side = np.zeros((H, W), bool)
    side[:, :LEFT] = side[:, RIGHT:] = True
    shade(img, side, 0.6)
    frame_columns(img, "#151a10")
    return img


def with_cards(img):
    """Example cards over the board, to judge legibility."""
    im = Image.fromarray(img.clip(0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    cols = {"D": (171, 25, 24), "L": (45, 87, 44), "H": (98, 74, 46)}
    rows_rival = [12, 36, 60, 84]  # hand, siege, ranged, melee (rival above)
    rows_me = [104, 128, 152, 176]
    for i, y in enumerate(rows_rival):
        n = 7 if i == 0 else [2, 1, 3][i - 1]
        for k in range(n):
            x = LEFT + 70 + k * 16
            d.rectangle([x, y, x + 13, y + 18], fill=(70, 70, 70) if i == 0 else cols["H"], outline=(0, 0, 0))
    for i, y in enumerate(rows_me):
        n = 5 if i == 3 else [2, 0, 1][i]
        for k in range(n):
            x = LEFT + 70 + k * 16
            d.rectangle([x, y, x + 13, y + 18], fill=cols["D"], outline=(0, 0, 0))
    d.rectangle([10, 30, 42, 74], fill=cols["L"], outline=(0, 0, 0))  # weather card
    for y in (16, 116):
        d.rectangle([RIGHT + 10, y, RIGHT + 26, y + 22], fill=(60, 60, 60), outline=(0, 0, 0))
    return im


if __name__ == "__main__":
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    for name, fn in [("madera", wood), ("piedra", stone), ("tapete", felt), ("campo", field)]:
        img = fn()
        base = Image.fromarray(img.clip(0, 255).astype(np.uint8))
        base.save(out / f"{name}-320.png")
        base.resize((W * 4, H * 4), Image.NEAREST).save(out / f"{name}.png")
        with_cards(img).resize((W * 4, H * 4), Image.NEAREST).save(out / f"{name}-cartas.png")
        print(name, (out / f"{name}.png").stat().st_size // 1024, "KB")


# --- field v2: lanes for the attack lines -----------------------------------------------

PIEZAS = Path.home() / "Documents/projects/paradigwent-taller/assets/piezas"
# rows in the 320x200 grid: (name, y0, y1); rival on top, mirrored below the river
ROWS = [
    ("mano-rival", 0, 28), ("asedio", 28, 47), ("distancia", 47, 66), ("cuerpo-a-cuerpo", 66, 85), ("info-rival", 85, 96),
    ("rio", 96, 104),
    ("info", 104, 115), ("cuerpo-a-cuerpo", 115, 134), ("distancia", 134, 153), ("asedio", 153, 172), ("mano", 172, 200),
]  # fmt: skip
GROUND = {
    "cuerpo-a-cuerpo": ["#33281e", "#3b2f24", "#44362a"],  # trodden dirt
    "distancia": ["#3a4a2a", "#435531", "#4c5f37"],  # tall grass
    "asedio": ["#37362f", "#403e37", "#4a473f"],  # gravel
}
PLAQUE_W, SCORE_W = 16, 18


def field2():
    img = quantize(np.clip(noise(W, H, 6, 6) * 0.7 + noise(W, H, 2, 7) * 0.3, 0, 0.999),
                   ["#2b3320", "#334026", "#3c4a2b", "#4a4630"])  # fmt: skip
    for k, (name, y0, y1) in enumerate(ROWS):
        if name in GROUND:
            x0, x1 = LEFT + 3, RIGHT - 3
            tex = np.clip(noise(x1 - x0, y1 - y0, 2, 20 + k) * 0.8 + 0.1, 0, 0.999)
            img[y0 + 1 : y1 - 1, x0:x1] = quantize(tex[1:-1], GROUND[name])
            img[y0 + 1, x0:x1] = rgb("#1a1e12")  # curb: dark top, light bottom
            img[y1 - 2, x0:x1] = rgb("#5b5a44")
            img[y0 + 1 : y1 - 1, x0] = img[y0 + 1 : y1 - 1, x1 - 1] = rgb("#1a1e12")
            for px0, px1 in [(x0 + 1, x0 + 1 + PLAQUE_W), (x1 - 1 - SCORE_W, x1 - 1)]:  # stone plaques
                img[y0 + 2 : y1 - 2, px0:px1] = rgb("#4b4a44")
                img[y0 + 2, px0:px1] = rgb("#6a685f")
                img[y1 - 3, px0:px1] = rgb("#2c2b27")
    # river, narrow, between the two info rows
    xs = np.arange(W)
    wave = np.round(np.sin(xs / 14) * 1.0).astype(int)
    for x in range(W):
        c = MID + wave[x]
        img[c - 4 : c + 4, x] = rgb("#5c5236")
        img[c - 3 : c + 3, x] = rgb("#22384a")
        img[c - 1 : c + 1, x] = rgb("#2a4659")
        if x % 7 == int(rng.integers(0, 7)):
            img[c - 1, x] = rgb("#6f8fa0")
    for _ in range(60):
        x, y = int(rng.integers(0, W)), int(rng.integers(0, H))
        if abs(y - MID) > 6 and not any(n in GROUND and a <= y < b and LEFT <= x < RIGHT for n, a, b in ROWS):
            img[y, x] = rgb("#58613a") if rng.random() < 0.7 else rgb("#6b6658")
    side = np.zeros((H, W), bool)
    side[:, :LEFT] = side[:, RIGHT:] = True
    shade(img, side, 0.6)
    frame_columns(img, "#151a10")
    im = Image.fromarray(img.clip(0, 255).astype(np.uint8))
    for name, y0, y1 in ROWS:  # line icons on the left plaques
        if name in GROUND:
            icon = Image.open(PIEZAS / f"linea-{name}.png")
            im.paste(icon, (LEFT + 4 + (PLAQUE_W - 12) // 2, y0 + (y1 - y0 - 12) // 2), icon)
    return np.asarray(im).astype(float)


def with_cards2(img):
    im = Image.fromarray(img.clip(0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    cols = {"D": (171, 25, 24), "L": (45, 87, 44), "H": (98, 74, 46)}
    counts = {("asedio", 0): 2, ("distancia", 0): 1, ("cuerpo-a-cuerpo", 0): 3,
              ("cuerpo-a-cuerpo", 1): 2, ("distancia", 1): 0, ("asedio", 1): 1}  # fmt: skip
    for name, y0, y1 in ROWS:
        half = 0 if y0 < MID else 1
        if name in GROUND:
            for k in range(counts[(name, half)]):
                x = LEFT + 4 + PLAQUE_W + 4 + k * 14
                d.rectangle([x, y0 + 3, x + 11, y1 - 4], fill=cols["H" if half == 0 else "D"], outline=(0, 0, 0))
        elif name.startswith("mano"):
            n = 7 if half == 0 else 5
            for k in range(n):
                x = LEFT + 40 + k * 20
                d.rectangle([x, y0 + 2, x + 17, y1 - 3], fill=(70, 70, 70) if half == 0 else cols["D"], outline=(0, 0, 0))
    d.rectangle([10, 30, 42, 74], fill=cols["L"], outline=(0, 0, 0))
    for y in (16, 116):
        d.rectangle([RIGHT + 10, y, RIGHT + 26, y + 22], fill=(60, 60, 60), outline=(0, 0, 0))
    return im


def render_v2(out):
    img = field2()
    base = Image.fromarray(img.clip(0, 255).astype(np.uint8))
    base.save(out / "campo2-320.png")
    base.resize((W * 4, H * 4), Image.NEAREST).save(out / "campo2.png")
    with_cards2(img).resize((W * 4, H * 4), Image.NEAREST).save(out / "campo2-cartas.png")
