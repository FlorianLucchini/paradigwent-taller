"""Second round for card / effect / weather: musical, soft, in E minor like the loop. No noise."""

import sys
from pathlib import Path

import numpy as np
from taller.sonar import SR, add, env, guardar, hz, lowpass, osc, tone

rng = np.random.default_rng(3)


def buf(s):
    return np.zeros(int(s * SR))


def pluck(f, dur, bright=0.4, decay=0.996):
    """Karplus-Strong plucked string."""
    n = int(dur * SR)
    p = max(2, int(SR / f))
    ring = lowpass(rng.uniform(-1, 1, p), 2000 + bright * 6000)
    out = np.empty(n)
    for i in range(n):
        j = i % p
        out[i] = ring[j]
        ring[j] = decay * 0.5 * (ring[j] + ring[(j + 1) % p])
    return out


def echo(x, delay, fb=0.35, taps=3):
    y = x.copy()
    k = int(delay * SR)
    for i in range(1, taps + 1):
        if k * i < len(x):
            y[k * i :] += x[: len(x) - k * i] * fb**i
    return y


def soft(out, kind, m, t, d, vol, a=0.01, r=0.08, vib=0.0):
    tone(out, kind, m, t, d, vol, vib=vib, gap=1.0, a=a, r=r)


# --- jugar carta ------------------------------------------------------------------------


def carta_a():
    """One short note with a triangle under it."""
    out = buf(0.2)
    soft(out, "pulse25", 76, 0, 0.12, 0.16, a=0.003, r=0.08)
    soft(out, "tri", 64, 0, 0.12, 0.2, a=0.003, r=0.08)
    return out


def carta_b():
    """Two-note pickup, low to high."""
    out = buf(0.25)
    soft(out, "pulse25", 71, 0, 0.07, 0.14, a=0.003, r=0.03)
    soft(out, "pulse25", 76, 0.07, 0.13, 0.16, a=0.003, r=0.1)
    return out


def carta_c():
    """A single lute pluck."""
    out = buf(0.4)
    add(out, 0.5 * pluck(hz(64), 0.4), 0)
    return out


# --- efecto -----------------------------------------------------------------------------


def efecto_a():
    """E minor arpeggio up to the octave, with echo."""
    out = buf(0.9)
    for k, m in enumerate([64, 67, 71, 76]):
        soft(out, "pulse25", m, k * 0.08, 0.12, 0.14, a=0.003, r=0.06)
    return echo(out, 0.12, 0.35)


def efecto_b():
    """Dorian colour: B D F# A on triangle, slower, ringing."""
    out = buf(1.0)
    for k, m in enumerate([71, 74, 78, 81]):
        soft(out, "tri", m, k * 0.11, 0.5, 0.18, a=0.005, r=0.35)
    return out


def efecto_c():
    """Bell: a fifth struck together, long decay."""
    out = buf(1.0)
    for m, v in [(76, 0.16), (83, 0.1), (88, 0.05)]:
        s = osc("tri", hz(m), 0.9)
        add(out, v * s * np.exp(-np.linspace(0, 5, len(s))), 0)
    return out


# --- clima ------------------------------------------------------------------------------


def clima_a():
    """A slow falling line on triangle with tremolo: the sky turns."""
    out = buf(1.1)
    for k, m in enumerate([76, 74, 71, 67]):
        soft(out, "tri", m, k * 0.2, 0.35, 0.18, a=0.03, r=0.2, vib=0.3)
    t = np.arange(len(out)) / SR
    return out * (0.75 + 0.25 * np.sin(2 * np.pi * 6 * t))


def clima_b():
    """Low drone swell with a soft Em9 above."""
    out = buf(1.3)
    soft(out, "tri", 40, 0, 1.2, 0.3, a=0.4, r=0.6)
    soft(out, "tri", 47, 0, 1.2, 0.2, a=0.4, r=0.6)
    for k, m in enumerate([64, 67, 71, 74, 78]):
        soft(out, "pulse25", m, 0.2 + k * 0.12, 0.5, 0.05, a=0.05, r=0.3)
    return out


def clima_c():
    """Two chords, E minor to C: the mood shifts."""
    out = buf(1.2)
    for t, chord in [(0, [64, 67, 71]), (0.5, [64, 67, 72])]:
        for m in chord:
            soft(out, "square", m, t, 0.55, 0.05, a=0.04, r=0.25)
        soft(out, "tri", chord[0] - 24 if t == 0 else 36, t, 0.55, 0.2, a=0.04, r=0.25)
    return out


SONIDOS = {
    "carta-a": carta_a, "carta-b": carta_b, "carta-c": carta_c,
    "efecto-a": efecto_a, "efecto-b": efecto_b, "efecto-c": efecto_c,
    "clima-a": clima_a, "clima-b": clima_b, "clima-c": clima_c,
}  # fmt: skip

if __name__ == "__main__":
    out = Path(sys.argv[1])
    for name, fn in SONIDOS.items():
        x = fn()
        # quieter than the jingles: these sound over the music
        guardar(out / f"n-{name}.wav", x, 0.55)
        print(name, round(len(x) / SR, 2), end="  ")
