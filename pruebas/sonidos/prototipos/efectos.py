"""Proposals: card played (per line), effects (per type) and weather (per card)."""

import sys
from pathlib import Path

import numpy as np
from taller.sonar import SR, add, drum, env, guardar, hz, lowpass, noise_hit, osc, rng, tone


def sweep(kind, f0, f1, dur, curve=1.0):
    n = int(dur * SR)
    x = np.linspace(0, 1, n) ** curve
    f = f0 * (f1 / f0) ** x
    ph = 2 * np.pi * np.cumsum(f) / SR
    if kind == "square":
        return np.sign(np.sin(ph)) * 0.5
    if kind == "pulse25":
        return np.where((ph / (2 * np.pi)) % 1 < 0.25, 1.0, -1.0) * 0.5
    return 2 / np.pi * np.arcsin(np.sin(ph))


def lowpass_var(x, cutoffs):
    y = np.empty_like(x)
    acc = 0.0
    a = np.exp(-2 * np.pi * cutoffs / SR)
    for i, v in enumerate(x):
        acc = (1 - a[i]) * v + a[i] * acc
        y[i] = acc
    return y


def highpass(x, cutoff):
    return x - lowpass(x, cutoff)


def buf(seconds):
    return np.zeros(int(seconds * SR))


def decay(n, k):
    return np.exp(-np.linspace(0, k, n))


# --- card played, one per line ----------------------------------------------------------


def carta_cuerpo():
    out = buf(0.3)
    add(out, 0.5 * drum(0.25, 75), 0)
    s = sweep("square", 220, 110, 0.08)
    add(out, 0.25 * s * env(len(s), 0.002, 0.03), 0)
    add(out, 0.2 * noise_hit(0.05, 2500, 10), 0)
    return out


def carta_distancia():
    out = buf(0.3)
    s = sweep("pulse25", 1600, 500, 0.14, 0.6)
    add(out, 0.25 * s * env(len(s), 0.002, 0.05), 0)
    n = noise_hit(0.16, 6000, 6)
    add(out, 0.12 * highpass(n, 2000), 0.02)
    add(out, 0.2 * drum(0.12, 150), 0.14)
    return out


def carta_asedio():
    out = buf(0.6)
    add(out, 0.55 * drum(0.5, 50), 0)
    add(out, 0.3 * noise_hit(0.5, 700, 6), 0)
    s = sweep("square", 110, 55, 0.2)
    add(out, 0.2 * s * env(len(s), 0.002, 0.08), 0)
    return out


# --- effects, one per type --------------------------------------------------------------


def robar():
    out = buf(0.45)
    for k, (a, b) in enumerate([(72, 79), (74, 81)]):
        t = k * 0.16
        add(out, 0.15 * highpass(noise_hit(0.05, 8000, 10), 3000), t)
        s = sweep("pulse25", hz(a), hz(b), 0.09)
        add(out, 0.22 * s * env(len(s), 0.002, 0.03), t + 0.02)
    return out


def eliminar():
    out = buf(0.7)
    s = sweep("square", 900, 70, 0.5, 0.7)
    add(out, 0.25 * s * env(len(s), 0.002, 0.15), 0)
    add(out, 0.35 * noise_hit(0.45, 3000, 5), 0.05)
    add(out, 0.4 * drum(0.3, 60), 0.4)
    return out


def resucitar():
    out = buf(1.0)
    for k, m in enumerate([64, 68, 71, 76, 80, 83, 88]):
        tone(out, "pulse25", m, k * 0.06, 0.25, 0.18, vib=0.15, gap=1.0, r=0.15)
    for k in range(10):
        tone(out, "tri", 88 + int(rng.integers(0, 12)), 0.3 + k * 0.05, 0.05, 0.08, gap=1.0)
    tone(out, "square", 52, 0, 0.8, 0.08, gap=1.0, a=0.2, r=0.4)
    return out


def duplicar():
    out = buf(0.75)
    tone(out, "pulse25", 67, 0, 0.18, 0.22, gap=1.0, r=0.05)
    for k, v in enumerate([0.22, 0.12, 0.06]):
        t = 0.18 + k * 0.12
        tone(out, "pulse25", 79, t, 0.12, v, gap=0.9)
        tone(out, "square", 67, t, 0.12, v * 0.5, gap=0.9)
    return out


def sabotear():
    out = buf(0.8)
    for det in (1.0, 1.03):
        s = sweep("square", 330 * det, 120 * det, 0.6)
        wob = 1 + 0.4 * np.sin(2 * np.pi * 14 * np.arange(len(s)) / SR)
        add(out, 0.13 * s * wob * env(len(s), 0.002, 0.2), 0)
    for t in (0.05, 0.22, 0.4):
        add(out, 0.25 * noise_hit(0.07, 4000, 8), t)
        tone(out, "square", 40 + int(rng.integers(0, 4)), t, 0.06, 0.15, gap=1.0)
    return out


# --- weather, one per card --------------------------------------------------------------


def swell(n, attack=0.3):
    e = np.ones(n)
    na = int(n * attack)
    e[:na] = np.linspace(0, 1, na)
    e[na:] = np.linspace(1, 0, n - na) ** 1.5
    return e


def cendre():
    # ash: muffled wind and a slow falling note
    out = buf(1.3)
    n = int(1.2 * SR)
    w = lowpass_var(rng.standard_normal(n), 400 + 500 * np.sin(np.linspace(0, np.pi, n)))
    add(out, 0.5 * w * swell(n), 0)
    s = sweep("tri", hz(52), hz(45), 1.1)
    add(out, 0.25 * s * swell(len(s), 0.1), 0)
    return out


def ignisium():
    # rain of fire: falling fireballs and crackle
    out = buf(1.2)
    for k, t in enumerate([0, 0.25, 0.45]):
        s = sweep("square", 1200 - 200 * k, 150, 0.35)
        add(out, 0.15 * s * env(len(s), 0.002, 0.1), t)
        add(out, 0.25 * noise_hit(0.2, 2500, 6), t + 0.3)
    for _ in range(25):
        add(out, 0.15 * highpass(noise_hit(0.015, 9000, 4), 3000), float(rng.uniform(0.1, 1.0)))
    return out


def tremor():
    # earthquake: low rumble with tremolo
    out = buf(1.3)
    n = int(1.2 * SR)
    r = lowpass(rng.standard_normal(n), 150) * 3
    trem = 0.6 + 0.4 * np.sin(2 * np.pi * 11 * np.arange(n) / SR)
    add(out, 0.6 * r * trem * swell(n, 0.15), 0)
    add(out, 0.3 * osc("tri", hz(28), 1.2) * swell(n, 0.15), 0)
    add(out, 0.4 * drum(0.5, 45), 0)
    return out


def meril():
    # thorns: scratchy ticks and a clashing minor second
    out = buf(1.0)
    for k in range(8):
        add(out, 0.2 * highpass(noise_hit(0.03, 9000, 6), 4000), k * 0.09)
    for k, m in enumerate([71, 72, 71, 72]):
        tone(out, "pulse25", m, 0.1 + k * 0.14, 0.12, 0.13, gap=0.8)
    tone(out, "square", 59, 0.1, 0.7, 0.07, gap=1.0, r=0.3)
    return out


def lasgwae():
    # whirl of leaves: wind going round and fluttering ticks
    out = buf(1.3)
    n = int(1.2 * SR)
    cut = 1500 + 1300 * np.sin(np.linspace(0, 4 * np.pi, n))
    add(out, 0.35 * highpass(lowpass_var(rng.standard_normal(n), cut), 300) * swell(n), 0)
    for _ in range(14):
        tone(out, "tri", 84 + int(rng.integers(0, 10)), float(rng.uniform(0.1, 1.0)), 0.03, 0.08, gap=1.0)
    return out


def thond():
    # roots: creaking low wobble growing up from the ground
    out = buf(1.2)
    n = int(1.1 * SR)
    t = np.arange(n) / SR
    f = 55 + 12 * np.sin(2 * np.pi * 2.5 * t) + 40 * t
    ph = 2 * np.pi * np.cumsum(f) / SR
    creak = np.where((ph / (2 * np.pi)) % 1 < 0.15, 1.0, -1.0) * 0.5
    add(out, 0.25 * creak * swell(n, 0.2), 0)
    for k in range(4):
        add(out, 0.25 * drum(0.2, 70 + 15 * k), 0.15 + k * 0.2)
    return out


def tribolos():
    # iron caltrops: metallic clinks scattered on the ground
    out = buf(1.0)
    for k, t in enumerate([0, 0.11, 0.19, 0.33, 0.42, 0.6]):
        f = float(rng.uniform(1800, 3200))
        p = osc("square", f, 0.12) + 0.5 * osc("square", f * 1.41, 0.12)
        add(out, 0.12 * p * decay(len(p), 12), t)
    add(out, 0.2 * noise_hit(0.08, 6000, 8), 0)
    return out


def kapnos():
    # smoke screen: a hiss that swells and hangs
    out = buf(1.4)
    n = int(1.3 * SR)
    h = highpass(lowpass(rng.standard_normal(n), 5000), 1500)
    add(out, 0.35 * h * swell(n, 0.4), 0)
    add(out, 0.2 * osc("tri", hz(43), 1.3) * swell(n, 0.4), 0)
    return out


def hydor():
    # flood: a splash and rising bubbles
    out = buf(1.2)
    add(out, 0.4 * noise_hit(0.3, 2500, 5), 0)
    add(out, 0.3 * drum(0.3, 80), 0)
    for _ in range(12):
        f0 = float(rng.uniform(300, 700))
        s = sweep("tri", f0, f0 * 2.2, 0.06)
        add(out, 0.15 * s * env(len(s), 0.002, 0.02), float(rng.uniform(0.2, 1.0)))
    return out


SONIDOS = {
    "carta-cuerpo": carta_cuerpo, "carta-distancia": carta_distancia, "carta-asedio": carta_asedio,
    "robar": robar, "eliminar": eliminar, "resucitar": resucitar, "duplicar": duplicar, "sabotear": sabotear,
    "cendre": cendre, "ignisium": ignisium, "tremor": tremor,
    "meril": meril, "lasgwae": lasgwae, "thond": thond,
    "tribolos": tribolos, "kapnos": kapnos, "hydor": hydor,
}  # fmt: skip

if __name__ == "__main__":
    out = Path(sys.argv[1])
    for name, fn in SONIDOS.items():
        x = fn()
        guardar(out / f"e-{name}.wav", x, 0.75)
        print(name, round(len(x) / SR, 2))
