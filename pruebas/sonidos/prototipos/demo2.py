"""Brighter chiptune variants: other modes, tempos and meters."""

import sys
from pathlib import Path

import numpy as np
from demo import SR, add, drum, env, hz, lowpass, noise_hit, osc, pluck, reverb, save  # noqa: F401

import demo


def seq(tune, unit):
    t = 0.0
    for m, b in tune:
        yield t, m, b * unit
        t += b * unit


def length(tune, unit):
    return sum(b for _, b in tune) * unit


def third_below(m, scale):
    """Diatonic third below within a scale given as pitch classes."""
    pcs = sorted(scale)
    i = pcs.index(m % 12)
    target = pcs[(i - 2) % len(pcs)]
    d = (m % 12 - target) % 12
    return m - d


def lead(out, tune, unit, kind="pulse25", vol=0.26, gap=0.9, vib=0.12):
    for t, m, d in seq(tune, unit):
        n = int(d * gap * SR)
        add(out, vol * osc(kind, hz(m), d * gap, vib=vib) * env(n, 0.004, 0.03), t)


def echo(x, delay, fb=0.35, taps=3):
    y = x.copy()
    k = int(delay * SR)
    for i in range(1, taps + 1):
        y[k * i :] += x[: len(x) - k * i] * fb**i
    return y


def chip_arp(out, root, quality, start, dur, step=1 / 24, vol=0.1):
    """Fast broken chord, the classic chiptune substitute for a chord."""
    ivs = [0, 4, 7, 12] if quality == "M" else [0, 3, 7, 12]
    t = 0.0
    i = 0
    while t < dur - 1e-6:
        d = min(step, dur - t)
        add(out, vol * osc("pulse25", hz(root + ivs[i % 4]), d) * env(int(d * SR), 0.002, 0.005), start + t)
        t += step
        i += 1


# --- 4. Festiva: G mixolydian jig, 6/8 -------------------------------------------------
JIG = [
    (79, 2), (74, 1), (71, 2), (74, 1),
    (77, 2), (74, 1), (72, 2), (74, 1),
    (79, 1), (81, 1), (79, 1), (77, 1), (76, 1), (74, 1),
    (72, 3), (74, 3),
    (79, 2), (74, 1), (71, 2), (74, 1),
    (77, 2), (76, 1), (74, 2), (72, 1),
    (71, 1), (72, 1), (74, 1), (72, 1), (71, 1), (69, 1),
    (67, 6),
]
JIG = JIG * 2
JIG_ROOTS = [43, 41, 43, 36, 43, 41, 38, 43] * 2
JIG_Q = ["M", "M", "M", "M", "M", "M", "M", "M"]
EIGHTH = 0.19
MIXO = [7, 9, 11, 0, 2, 4, 5]


def festiva():
    out = np.zeros(int(length(JIG, EIGHTH) * SR) + 3 * SR)
    lead(out, JIG, EIGHTH, "pulse25", 0.26)
    lead(out, [(third_below(m, MIXO), b) for m, b in JIG], EIGHTH, "square", 0.09, vib=0)
    for bar, r in enumerate(JIG_ROOTS):
        t0 = bar * 6 * EIGHTH
        for k, iv in enumerate([0, 7]):
            d = 3 * EIGHTH * 0.85
            add(out, 0.32 * osc("tri", hz(r + iv), d) * env(int(d * SR), 0.003, 0.04), t0 + k * 3 * EIGHTH)
            add(out, 0.3 * noise_hit(0.1, 1200, 12), t0 + k * 3 * EIGHTH)
        for e in range(6):
            if e % 3:
                add(out, 0.08 * noise_hit(0.04, 7000, 12), t0 + e * EIGHTH)
    return out


# --- 5. Fanfarria: C major march, 4/4 --------------------------------------------------
MARCH = [
    (67, 1), (72, 1), (72, 0.5), (74, 0.5), (76, 1),
    (74, 1), (72, 1), (71, 1), (67, 1),
    (69, 1), (71, 0.5), (72, 0.5), (74, 1), (76, 1),
    (74, 3), (67, 1),
    (67, 1), (72, 1), (72, 0.5), (74, 0.5), (76, 1),
    (79, 1), (77, 1), (76, 1), (74, 1),
    (77, 1), (76, 1), (74, 1), (71, 1),
    (72, 4),
]
MARCH_ROOTS = [48, 43, 41, 43, 48, 45, 43, 48]
MARCH_Q = ["M", "M", "M", "M", "M", "m", "M", "M"]
QUARTER = 0.46
MAJOR = [0, 2, 4, 5, 7, 9, 11]


def fanfarria():
    out = np.zeros(int(length(MARCH, QUARTER) * SR) + 3 * SR)
    lead(out, MARCH, QUARTER, "square", 0.22, gap=0.8, vib=0.08)
    lead(out, [(third_below(m, MAJOR), b) for m, b in MARCH], QUARTER, "pulse25", 0.12, gap=0.8, vib=0)
    for bar, r in enumerate(MARCH_ROOTS):
        t0 = bar * 4 * QUARTER
        for k in range(4):
            d = QUARTER * 0.6
            add(out, 0.3 * osc("tri", hz(r - 12 + (0 if k % 2 == 0 else 7)), d) * env(int(d * SR), 0.003, 0.03), t0 + k * QUARTER)
            if k % 2:
                add(out, 0.25 * noise_hit(0.14, 5000, 9), t0 + k * QUARTER)
            else:
                add(out, 0.3 * noise_hit(0.1, 900, 12), t0 + k * QUARTER)
        if bar in (3, 7):
            for s in range(4):
                add(out, 0.12 * noise_hit(0.05, 5000, 14), t0 + 3 * QUARTER + s * QUARTER / 4)
    return out


# --- 6. Bosque: F lydian waltz with arpeggios and echo, 3/4 ----------------------------
LYD = [
    (65, 1), (69, 1), (72, 1),
    (71, 2), (69, 1),
    (67, 1), (69, 1), (71, 1),
    (72, 3),
    (76, 1), (74, 1), (72, 1),
    (71, 1.5), (72, 0.5), (74, 1),
    (72, 1), (71, 1), (67, 1),
    (65, 3),
]
LYD_ROOTS = [53, 55, 55, 53, 48, 55, 55, 53]
LYD_Q = ["M"] * 8
BEAT3 = 0.6


def bosque():
    out = np.zeros(int(length(LYD, BEAT3) * SR) + 3 * SR)
    mel = np.zeros_like(out)
    lead(mel, LYD, BEAT3, "pulse25", 0.24, gap=0.85, vib=0.2)
    out += echo(mel, BEAT3 / 2, 0.4)
    for bar, r in enumerate(LYD_ROOTS):
        t0 = bar * 3 * BEAT3
        chip_arp(out, r, LYD_Q[bar], t0, 3 * BEAT3, step=BEAT3 / 6, vol=0.045)
        d = 3 * BEAT3 * 0.9
        add(out, 0.28 * osc("tri", hz(r - 12), d) * env(int(d * SR), 0.01, 0.3), t0)
    return out


# --- 7. Juglar: the jig with a chip lead over lute and frame drum ----------------------
def juglar():
    out = np.zeros(int(length(JIG, EIGHTH) * SR) + 3 * SR)
    lead(out, JIG, EIGHTH, "pulse25", 0.2)
    for bar, r in enumerate(JIG_ROOTS):
        t0 = bar * 6 * EIGHTH
        for e, iv in enumerate([0, 7, 12, 4, 7, 12]):
            add(out, 0.3 * pluck(hz(r + 12 + iv), EIGHTH * 2.5, bright=0.5), t0 + e * EIGHTH)
        add(out, 0.4 * drum(0.5, 95), t0)
        add(out, 0.25 * drum(0.4, 120), t0 + 3 * EIGHTH)
        add(out, 0.1 * drum(0.2, 170), t0 + 5 * EIGHTH)
    return reverb(out, 1.0, 0.15)


def save_len(path, x, seconds):
    demo.TOTAL = seconds
    save(path, x)


if __name__ == "__main__":
    out = Path(sys.argv[1])
    for name, fn, tune, unit in [
        ("festiva", festiva, JIG, EIGHTH),
        ("fanfarria", fanfarria, MARCH, QUARTER),
        ("bosque", bosque, LYD, BEAT3),
        ("juglar", juglar, JIG, EIGHTH),
    ]:
        save_len(out / f"{name}.wav", fn(), length(tune, unit))
        print(name, round(length(tune, unit), 1), "s")
