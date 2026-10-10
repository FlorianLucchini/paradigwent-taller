"""Third round: short, sharp sounds. Water drop, sword clash, delicate bell."""

import sys
from pathlib import Path

import numpy as np
from taller.sonar import SR, add, guardar, hz, lowpass

rng = np.random.default_rng(11)


def buf(s):
    return np.zeros(int(s * SR))


def partial(f, dur, decay, phase=0.0, detune=0.0):
    t = np.arange(int(dur * SR)) / SR
    return np.sin(2 * np.pi * f * (1 + detune) * t + phase) * np.exp(-t * decay)


def gota():
    """Water drop: a sine whose pitch jumps up fast, then a fainter second drop."""
    out = buf(0.45)
    for t0, f0, f1, v in [(0, 700, 1900, 0.5), (0.16, 900, 2300, 0.18)]:
        n = int(0.09 * SR)
        x = np.linspace(0, 1, n)
        f = f0 * (f1 / f0) ** (x**0.5)
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 6) * np.minimum(1, x * 40)
        add(out, v * s, t0)
    return out


def espadas_a():
    """Sword clash: inharmonic metal partials with a tiny bright transient."""
    out = buf(0.6)
    base = 1250
    for ratio, v, dec in [(1.0, 0.35, 9), (2.76, 0.22, 12), (5.4, 0.12, 16), (8.93, 0.06, 22)]:
        add(out, v * partial(base * ratio, 0.6, dec, detune=0.0), 0)
        add(out, v * 0.6 * partial(base * ratio, 0.6, dec, detune=0.006), 0)  # second blade, beating
    click = rng.standard_normal(int(0.012 * SR))
    click -= lowpass(click, 3000)
    add(out, 0.25 * click * np.linspace(1, 0, len(click)), 0)
    return out


def espadas_b():
    """Clash plus a short scrape of one blade along the other."""
    out = espadas_a()
    out = np.concatenate([out, np.zeros(int(0.15 * SR))])
    n = int(0.18 * SR)
    sc = rng.standard_normal(n)
    sc -= lowpass(sc, 4000)
    sc = lowpass(sc, 9000)
    shape = np.sin(np.linspace(0, np.pi, n)) ** 2
    add(out, 0.12 * sc * shape, 0.07)
    add(out, 0.08 * partial(3450, 0.25, 14), 0.07)
    return out


def campana():
    """Delicate bell: two high sines, soft attack, slow decay."""
    out = buf(1.0)
    for m, v, dec in [(88, 0.22, 5), (95, 0.08, 7), (100, 0.03, 9)]:
        s = partial(hz(m), 0.95, dec)
        att = int(0.004 * SR)
        s[:att] *= np.linspace(0, 1, att)
        add(out, v * s, 0)
    return out


SONIDOS = {"gota": gota, "espadas-a": espadas_a, "espadas-b": espadas_b, "campana": campana}

if __name__ == "__main__":
    out = Path(sys.argv[1])
    for name, fn in SONIDOS.items():
        x = fn()
        guardar(out / f"t-{name}.wav", x, 0.55)
        print(name, round(len(x) / SR, 2), end="  ")
