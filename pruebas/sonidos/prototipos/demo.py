"""Three style samples of the same modal tune, to choose a sound direction."""

import sys
import wave
from pathlib import Path

import numpy as np

SR = 22050
BPM = 96
BEAT = 60 / BPM
rng = np.random.default_rng(7)

# D dorian tune in 3/4: (midi, beats)
TUNE = [
    (62, 1), (65, 1), (69, 1),
    (67, 1.5), (65, 0.5), (64, 1),
    (62, 1), (64, 1), (65, 1),
    (64, 2), (57, 1),
    (62, 1), (65, 1), (69, 1),
    (72, 1.5), (71, 0.5), (69, 1),
    (67, 1), (65, 1), (64, 1),
    (62, 3),
]
# drone root per bar (8 bars)
ROOTS = [38, 38, 38, 45, 38, 36, 36, 38]
TOTAL = sum(b for _, b in TUNE) * BEAT


def hz(m):
    return 440 * 2 ** ((m - 69) / 12)


def buf(seconds):
    return np.zeros(int(seconds * SR) + SR * 2)


def add(out, sig, t):
    i = int(t * SR)
    n = min(len(sig), len(out) - i)
    out[i : i + n] += sig[:n]


def env(n, a=0.01, r=0.1):
    e = np.ones(n)
    na, nr = min(int(a * SR), n // 2), min(int(r * SR), n // 2)
    e[:na] = np.linspace(0, 1, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def osc(kind, f, dur, vib=0.0):
    t = np.arange(int(dur * SR)) / SR
    ph = 2 * np.pi * f * t + (vib * np.sin(2 * np.pi * 5.2 * t) if vib else 0)
    if kind == "sine":
        return np.sin(ph)
    if kind == "square":
        return np.sign(np.sin(ph)) * 0.5 + np.sign(np.sin(ph * 2 + 1)) * 0.0
    if kind == "pulse25":
        return np.where((ph / (2 * np.pi)) % 1 < 0.25, 1.0, -1.0) * 0.5
    if kind == "tri":
        return 2 / np.pi * np.arcsin(np.sin(ph))
    if kind == "saw":
        return 2 * ((ph / (2 * np.pi)) % 1) - 1
    raise ValueError(kind)


def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def pluck(f, dur, bright=0.5, decay=0.996):
    """Karplus-Strong plucked string (lute / harp)."""
    n = int(dur * SR)
    p = max(2, int(SR / f))
    ring = rng.uniform(-1, 1, p)
    ring = lowpass(ring, 2000 + bright * 6000)
    out = np.empty(n)
    for i in range(n):
        j = i % p
        out[i] = ring[j]
        ring[j] = decay * 0.5 * (ring[j] + ring[(j + 1) % p])
    return out


def reverb(x, seconds=1.6, wet=0.25):
    n = int(seconds * SR)
    ir = rng.standard_normal(n) * np.exp(-np.linspace(0, 7, n))
    ir[0] = 0
    size = 1 << int(np.ceil(np.log2(len(x) + n)))
    y = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)[: len(x)]
    y /= np.max(np.abs(y)) + 1e-9
    return x * (1 - wet) + y * wet * np.max(np.abs(x))


def noise_hit(dur, cutoff, decay):
    n = int(dur * SR)
    s = lowpass(rng.standard_normal(n), cutoff)
    return s * np.exp(-np.linspace(0, decay, n))


def drum(dur, f0=110):
    """Frame drum: falling sine plus a little skin noise."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f0 * (1 + 0.6 * np.exp(-t * 30))
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
    return body + 0.15 * noise_hit(dur, 3000, 25)


def notes():
    t = 0.0
    for m, b in TUNE:
        yield t, m, b * BEAT
        t += b * BEAT


def chiptune():
    out = buf(TOTAL)
    for t, m, d in notes():
        add(out, 0.28 * osc("pulse25", hz(m), d * 0.92, vib=0.15) * env(int(d * 0.92 * SR), 0.005, 0.03), t)
    for bar, r in enumerate(ROOTS):
        for k in range(3):
            tb = (bar * 3 + k) * BEAT
            arp = [r + 12, r + 19, r + 24][k]
            add(out, 0.3 * osc("tri", hz(r if k == 0 else arp), BEAT * 0.9) * env(int(BEAT * 0.9 * SR), 0.003, 0.05), tb)
            hit = noise_hit(0.12 if k == 0 else 0.05, 6000 if k else 1500, 10)
            add(out, (0.35 if k == 0 else 0.12) * hit, tb)
    return out


def taberna():
    out = buf(TOTAL)
    # recorder melody: sine + 2nd harmonic, breath noise, vibrato
    for t, m, d in notes():
        n = int(d * SR)
        f = hz(m)
        s = osc("sine", f, d, vib=0.25) + 0.25 * osc("sine", 2 * f, d) + 0.08 * osc("sine", 3 * f, d)
        s += 0.06 * lowpass(rng.standard_normal(n), 2500)
        add(out, 0.2 * s * env(n, 0.04, 0.08), t)
    # lute: plucked chord tones on each beat
    for bar, r in enumerate(ROOTS):
        for k, iv in enumerate([0, 7, 12]):
            tb = (bar * 3 + k) * BEAT
            add(out, 0.35 * pluck(hz(r + 12 + iv), BEAT * 1.6, bright=0.4), tb)
            if k == 0:
                add(out, 0.35 * drum(BEAT, 95), tb)
            else:
                add(out, 0.12 * drum(BEAT * 0.5, 160), tb)
    # hurdy-gurdy drone: filtered saw on D2 + A2
    dr = lowpass(osc("saw", hz(38), TOTAL + 1) + 0.7 * osc("saw", hz(45), TOTAL + 1), 700)
    add(out, 0.08 * dr * env(len(dr), 0.6, 1.0), 0)
    return reverb(out, 1.2, 0.2)


def mazmorra():
    out = buf(TOTAL)
    slow = 1.0
    for t, m, d in notes():
        n = int(d * SR * 1.4)
        s = lowpass(osc("saw", hz(m - 12), d * 1.4, vib=0.1) + osc("saw", hz(m - 12) * 1.004, d * 1.4), 1400)
        add(out, 0.12 * s * env(len(s), 0.15, 0.6), t * slow)
    for bar, r in enumerate(ROOTS):
        d = 3 * BEAT + 0.6
        pad = sum(osc("saw", hz(r + 12 + iv) * det, d) for iv in (0, 3, 7) for det in (1, 1.006))
        add(out, 0.05 * lowpass(pad, 600) * env(int(d * SR), 0.8, 0.8), bar * 3 * BEAT)
        add(out, 0.4 * drum(1.2, 55), bar * 3 * BEAT)
    return reverb(out, 3.0, 0.45)


def save(path, x):
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.85
    fade = int(0.5 * SR)
    end = int((TOTAL + 1.2) * SR)
    x = x[:end]
    x[-fade:] *= np.linspace(1, 0, fade)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())


if __name__ == "__main__":
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    for name, fn in [("chiptune", chiptune), ("taberna", taberna), ("mazmorra", mazmorra)]:
        save(out / f"{name}.wav", fn())
        print(name, "ok")
