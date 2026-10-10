"""Fourth round: single water drop, metallic sword clash, softer bell close to option C."""

import sys
from pathlib import Path

import numpy as np
from taller.sonar import SR, add, guardar, hz, lowpass, osc, reverb

rng = np.random.default_rng(21)


def buf(s):
    return np.zeros(int(s * SR))


def bandpass(x, lo, hi):
    return lowpass(x, hi) - lowpass(x, lo)


def lfsr_noise(dur, period_hz, short=True):
    """NES noise channel: 15-bit LFSR; short mode (93-step) sounds metallic."""
    n = int(dur * SR)
    reg = 1
    out = np.empty(n)
    step = SR / period_hz
    acc = 0.0
    val = 1.0
    for i in range(n):
        acc += 1
        while acc >= step:
            acc -= step
            bit = (reg ^ (reg >> (6 if short else 1))) & 1
            reg = (reg >> 1) | (bit << 14)
            val = 1.0 if reg & 1 else -1.0
        out[i] = val
    return out * 0.5


# --- clima: one drop --------------------------------------------------------------------


def drop(f0, f1, dur, rise=0.5):
    n = int(dur * SR)
    x = np.linspace(0, 1, n)
    f = f0 * (f1 / f0) ** np.minimum(1, (x * dur / 0.03)) ** rise  # pitch rises in the first 30 ms
    s = np.sin(2 * np.pi * np.cumsum(f) / SR)
    e = np.exp(-x * dur * 28) * np.minimum(1, x * n / (0.002 * SR))
    return s * e


def gota_a():
    """Small clean drop."""
    out = buf(0.3)
    add(out, 0.6 * drop(900, 2000, 0.25), 0)
    return out


def gota_b():
    """Bigger, rounder drop with a tiny splash tick."""
    out = buf(0.35)
    add(out, 0.6 * drop(500, 1250, 0.3, 0.4), 0)
    tick = bandpass(rng.standard_normal(int(0.006 * SR)), 2000, 7000)
    add(out, 0.15 * tick * np.linspace(1, 0, len(tick)), 0)
    return out


def gota_c():
    """Drop in a cave: the same drop with a long, dark echo."""
    out = buf(1.2)
    add(out, 0.6 * drop(700, 1600, 0.28, 0.45), 0)
    return reverb(out, 1.0, 0.35)


# --- jugar carta: swords ----------------------------------------------------------------


def clang(base_lo=1800, base_hi=8500, modes=24, length=0.5):
    """Dense inharmonic partials, an impact burst and a little grit."""
    n = int(length * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    freqs = np.exp(rng.uniform(np.log(base_lo), np.log(base_hi), modes))
    for f in freqs:
        dec = rng.uniform(6, 30) * (f / 3000) ** 0.5
        out += rng.uniform(0.3, 1.0) * np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28)) * np.exp(-t * dec)
    out /= modes**0.5
    body = np.sin(2 * np.pi * 640 * t) * np.exp(-t * 25) * 0.5  # lower ring of the blade
    burst = bandpass(rng.standard_normal(int(0.03 * SR)), 1500, 9000) * np.exp(-np.linspace(0, 6, int(0.03 * SR)))
    out += body
    out[: len(burst)] += 1.5 * burst
    return np.tanh(out * 1.6)  # grit


def espada_a():
    """One realistic clash."""
    out = buf(0.55)
    add(out, 0.5 * clang(), 0)
    return out


def espada_b():
    """Two blades: a clash and a quicker second contact."""
    out = buf(0.65)
    add(out, 0.5 * clang(), 0)
    add(out, 0.3 * clang(2200, 9000, 18, 0.35), 0.09)
    return out


def espada_c():
    """8-bit sword, NES-style metallic noise channel."""
    out = buf(0.3)
    n1 = lfsr_noise(0.25, 9000, short=True)
    add(out, 0.4 * n1 * np.exp(-np.linspace(0, 9, len(n1))), 0)
    n2 = lfsr_noise(0.03, 20000, short=False)
    add(out, 0.3 * n2 * np.linspace(1, 0, len(n2)), 0)
    return out


# --- efecto: softer option C ------------------------------------------------------------


def soft_tri(m, dur, decay, detune=0.0, attack=0.01):
    s = osc("tri", hz(m) * (1 + detune), dur)
    s *= np.exp(-np.linspace(0, decay, len(s)))
    a = int(attack * SR)
    s[:a] *= np.linspace(0, 1, a)
    return s


def campana_a():
    """Option C an octave lower, with soft attack and a slight chorus."""
    out = buf(0.9)
    for m, v in [(64, 0.16), (71, 0.08)]:
        add(out, v * soft_tri(m, 0.85, 5, attack=0.012), 0)
        add(out, v * 0.6 * soft_tri(m, 0.85, 5, detune=0.004, attack=0.012), 0)
    return lowpass(out, 3500)


def campana_b():
    """Same fifth as C, filtered and with a faint airy tail."""
    out = buf(1.1)
    for m, v in [(76, 0.12), (83, 0.06)]:
        add(out, v * soft_tri(m, 0.7, 6, attack=0.008), 0)
    return reverb(lowpass(out, 3000), 0.9, 0.3)


def campana_c():
    """Singing bowl: one low note with slow beating."""
    out = buf(1.1)
    add(out, 0.15 * soft_tri(64, 1.05, 4, attack=0.03), 0)
    add(out, 0.12 * soft_tri(64, 1.05, 4, detune=0.006, attack=0.03), 0)
    add(out, 0.04 * soft_tri(76, 1.05, 6, attack=0.03), 0)
    return lowpass(out, 2500)


SONIDOS = {
    "gota-a": gota_a, "gota-b": gota_b, "gota-c": gota_c,
    "espada-a": espada_a, "espada-b": espada_b, "espada-c": espada_c,
    "campana-a": campana_a, "campana-b": campana_b, "campana-c": campana_c,
}  # fmt: skip

if __name__ == "__main__":
    out = Path(sys.argv[1])
    for name, fn in SONIDOS.items():
        x = fn()
        guardar(out / f"u-{name}.wav", x, 0.55)
        print(name, round(len(x) / SR, 2), end="  ")
