"""Synthesize the game sounds (8-bit style) to WAV in assets/sonidos/.

uv run python -m taller.sonar

The background loop and the victory/defeat/end-of-round jingles quote riffs by
Patricio Rey y sus Redonditos de Ricota (see README).
"""

import wave
from pathlib import Path

import numpy as np

from taller.datos import ASSETS

SR = 22050
BAR = 1.08  # one 6/8 bar, in seconds
E8 = BAR / 6  # eighth note
EM = [4, 6, 7, 9, 11, 0, 2]  # E aeolian pitch classes
D_MAJOR = [2, 4, 6, 7, 9, 11, 1]

rng = np.random.default_rng(7)

# --- synthesis --------------------------------------------------------------------------


def hz(midi: float) -> float:
    return 440 * 2 ** ((midi - 69) / 12)


def osc(kind: str, f: float, dur: float, vib: float = 0.0) -> np.ndarray:
    t = np.arange(int(dur * SR)) / SR
    ph = 2 * np.pi * f * t + (vib * np.sin(2 * np.pi * 5.2 * t) if vib else 0)
    if kind == "square":
        return np.sign(np.sin(ph)) * 0.5
    if kind == "pulse25":
        return np.where((ph / (2 * np.pi)) % 1 < 0.25, 1.0, -1.0) * 0.5
    if kind == "tri":
        return 2 / np.pi * np.arcsin(np.sin(ph))
    raise ValueError(kind)


def env(n: int, a: float = 0.01, r: float = 0.1) -> np.ndarray:
    e = np.ones(n)
    na, nr = min(int(a * SR), n // 2), min(int(r * SR), n // 2)
    e[:na] = np.linspace(0, 1, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def lowpass(x: np.ndarray, cutoff: float) -> np.ndarray:
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def noise_hit(dur: float, cutoff: float, decay: float) -> np.ndarray:
    n = int(dur * SR)
    return lowpass(rng.standard_normal(n), cutoff) * np.exp(-np.linspace(0, decay, n))


def drum(dur: float, f0: float) -> np.ndarray:
    """Frame drum: falling sine plus a little skin noise."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f0 * (1 + 0.6 * np.exp(-t * 30))
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
    return body + 0.15 * noise_hit(dur, 3000, 25)


def reverb(x: np.ndarray, seconds: float, wet: float) -> np.ndarray:
    n = int(seconds * SR)
    ir = rng.standard_normal(n) * np.exp(-np.linspace(0, 7, n))
    ir[0] = 0
    size = 1 << int(np.ceil(np.log2(len(x) + n)))
    y = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)[: len(x)]
    y /= np.max(np.abs(y)) + 1e-9
    return x * (1 - wet) + y * wet * np.max(np.abs(x))


def add(out: np.ndarray, sig: np.ndarray, t: float) -> None:
    i = int(t * SR)
    n = min(len(sig), len(out) - i)
    out[i : i + n] += sig[:n]


def tone(out, kind, m, t, d, vol, vib=0.0, gap=0.9, a=0.004, r=0.03):
    dur = max(0.03, d * gap)
    add(out, vol * osc(kind, hz(m), dur, vib=vib) * env(int(dur * SR), a, r), t)


def line(out, t0, notes, kind="pulse25", vol=0.22, shift=0, vib=0.12, gap=0.9, unit=E8):
    """Play (midi or None, length in units) notes from t0; return the end time."""
    t = t0
    for m, b in notes:
        if m is not None:
            tone(out, kind, m + shift, t, b * unit, vol, vib, gap)
        t += b * unit
    return t


def diatonic(m: int, steps: int, scale=EM) -> int:
    """Move a note `steps` scale degrees within `scale`."""
    pcs = sorted(scale)
    octv, pc = divmod(m, 12)
    j = pcs.index(pc) + steps
    return (octv + j // len(pcs)) * 12 + pcs[j % len(pcs)]


# --- material ---------------------------------------------------------------------------

# Skay's riff from "El pibe de los astilleros", recast in 6/8 (8 bars)
PIBE = [
    (64, 1), (64, 1), (62, 1), (64, 1), (62, 2),
    (59, 1), (59, 2), (55, 1), (57, 1), (57, 1),
    (55, 1), (52, 1), (55, 1), (52, 1), (50, 1), (47, 1),
    (47, 3), (None, 3),
    (64, 1), (64, 1), (62, 1), (64, 1), (62, 2),
    (59, 1), (59, 2), (55, 1), (57, 1), (57, 1),
    (55, 2), (52, 1), (52, 3),
    (None, 6),
]  # fmt: skip
PIBE_ROOTS = [40, 43, 40, 40, 40, 43, 36, 38]

# Original tune over the song's verse chords (Em G C D)
TONADA = [
    (71, 2), (67, 1), (64, 2), (67, 1),
    (74, 2), (71, 1), (67, 3),
    (72, 2), (71, 1), (69, 2), (67, 1),
    (69, 3), (66, 3),
    (71, 1), (72, 1), (71, 1), (69, 1), (67, 1), (66, 1),
    (67, 2), (71, 1), (74, 3),
    (76, 2), (74, 1), (72, 2), (71, 1),
    (69, 6),
]  # fmt: skip
TONADA_ROOTS = [40, 43, 36, 38, 40, 43, 36, 38]


def chord_ivs(root: int) -> list[int]:
    return [0, 3, 7] if root % 12 in (4, 9) else [0, 4, 7]


def bass(out, t0, roots, style="jig", vol=0.3):
    for i, r in enumerate(roots):
        t = t0 + i * BAR
        if style == "jig":
            tone(out, "tri", r, t, 3 * E8, vol, gap=0.8)
            tone(out, "tri", r + 7, t + 3 * E8, 3 * E8, vol, gap=0.8)
        elif style == "drone":
            tone(out, "tri", r, t, BAR, vol * 0.9, gap=1.0, a=0.05, r=0.1)
        elif style == "walk":
            for k, iv in enumerate([0, 7, 12, 7, 0, 7]):
                tone(out, "tri", r + iv, t + k * E8, E8, vol * 0.8, gap=0.7)


def arps(out, t0, roots, vol=0.06, octave=24, per_eighth=2):
    step = E8 / per_eighth
    for i, r in enumerate(roots):
        ivs = chord_ivs(r) + [12]
        for k in range(6 * per_eighth):
            tone(out, "pulse25", r + octave + ivs[k % 4], t0 + i * BAR + k * step, step, vol, gap=0.8, r=0.005)


def drums(out, t0, bars, pattern):
    """Pattern over 6 eighths: k frame drum, s snare, h hat, j tambourine, . rest."""
    for b in range(bars):
        for k, c in enumerate(pattern):
            t = t0 + b * BAR + k * E8
            if c == "k":
                add(out, 0.35 * drum(0.35, 90), t)
            elif c == "s":
                add(out, 0.2 * noise_hit(0.12, 5000, 10), t)
            elif c == "h":
                add(out, 0.06 * noise_hit(0.04, 7000, 12), t)
            elif c == "j":
                add(out, 0.12 * drum(0.2, 170), t)
                add(out, 0.06 * noise_hit(0.15, 8000, 8), t)


def fill(out, t0):
    for k in range(6):
        add(out, (0.08 + 0.03 * k) * noise_hit(0.06, 5000, 12), t0 + k * E8)


# --- sounds -----------------------------------------------------------------------------


def musica() -> np.ndarray:
    """Seamless ~47 s loop: intro, riff, tune, riff up, breakdown, tune."""
    length = 44 * BAR
    out = np.zeros(int((length + 4) * SR))
    t = 0.0
    bass(out, t, [40] * 4, "drone", 0.25)
    arps(out, t + 2 * BAR, [40, 40], vol=0.04)
    drums(out, t, 4, "j..j..")
    fill(out, t + 3 * BAR)
    t += 4 * BAR

    line(out, t, PIBE, "pulse25", 0.22)
    line(out, t, [(None if m is None else diatonic(m, 4), b) for m, b in PIBE], "square", 0.08, vib=0)
    bass(out, t, PIBE_ROOTS, "jig")
    drums(out, t, 8, "k.hsh.")
    fill(out, t + 7 * BAR)
    t += 8 * BAR

    line(out, t, TONADA, "pulse25", 0.2, vib=0.18)
    bass(out, t, TONADA_ROOTS, "jig", 0.26)
    arps(out, t, TONADA_ROOTS, vol=0.035, octave=12, per_eighth=1)
    drums(out, t, 8, "j.hj.h")
    t += 8 * BAR

    line(out, t, PIBE, "pulse25", 0.2, shift=12)
    line(out, t, [(None if m is None else diatonic(m, -2) + 12, b) for m, b in PIBE], "square", 0.07, vib=0)
    bass(out, t, PIBE_ROOTS, "walk")
    drums(out, t, 8, "k.hsjh")
    fill(out, t + 7 * BAR)
    t += 8 * BAR

    slow = [(m, b * 2) for m, b in PIBE[:12]]
    calm = [40, 40, 36, 36, 43, 43, 38, 38]
    line(out, t, slow, "tri", 0.26, shift=12, vib=0.2, gap=0.95)
    bass(out, t, calm, "drone", 0.22)
    arps(out, t, calm, vol=0.05)
    drums(out, t + 4 * BAR, 4, "j.....")
    fill(out, t + 7 * BAR)
    t += 8 * BAR

    line(out, t, TONADA, "pulse25", 0.21)
    line(out, t, [(None if m is None else diatonic(m, -3), b) for m, b in TONADA], "square", 0.07, vib=0)
    bass(out, t, TONADA_ROOTS, "jig")
    drums(out, t, 8, "k.hsh.")

    wet = reverb(out, 0.9, 0.12)
    n = int(length * SR)
    loop = wet[:n].copy()
    tail = wet[n:]
    loop[: len(tail)] += tail[:n]  # wrap the reverb tail onto the start
    return loop


def jingle(build, seconds: float) -> np.ndarray:
    out = np.zeros(int((seconds + 1) * SR))
    build(out)
    return out[: int(seconds * SR)]


def victoria() -> np.ndarray:
    """Sax line of "Ya nadie va a escuchar tu remera", fast, ending on D major."""
    u = 0.085
    notes = [
        (66, 2), (64, 1), (62, 2), (66, 1), (66, 2), (69, 1), (67, 1),
        (66, 1), (64, 1), (62, 2), (67, 1), (69, 1), (71, 1),
    ]  # fmt: skip

    def b(out):
        t = line(out, 0, notes, "pulse25", 0.24, shift=12, unit=u, gap=0.85)
        thirds = [(diatonic(m, -2, D_MAJOR), d) for m, d in notes]
        line(out, 0, thirds, "square", 0.08, shift=12, unit=u, vib=0)
        for m, v in [(86, 0.24), (81, 0.1), (78, 0.1), (74, 0.1)]:
            tone(out, "pulse25" if v > 0.2 else "square", m, t, 1.2, v, vib=0.2, gap=1.0, r=0.5)
        tone(out, "tri", 50, t, 1.2, 0.3, gap=1.0, r=0.5)
        for k in range(4):
            add(out, 0.12 * noise_hit(0.05, 5000, 12), t - 0.34 + k * 0.085)
        add(out, 0.3 * noise_hit(0.5, 4000, 5), t)

    return jingle(b, 2.6)


def derrota() -> np.ndarray:
    """Chromatic pairs of "Semen-up" falling into its intro's descending chords."""
    pairs = [(62, 1), (63, 1), (62, 1), (63, 2), (58, 1), (59, 1), (55, 1), (56, 2)]

    def b(out):
        t = line(out, 0, pairs, "pulse25", 0.22, unit=0.12)
        for i, root in enumerate([56, 55, 54, 53]):
            last = i == 3
            d = 1.1 if last else 0.3
            for iv, v in [(0, 0.1), (3, 0.08), (7, 0.08)]:
                tone(out, "square", root + iv, t, d, v, gap=1.0 if last else 0.9, r=0.6 if last else 0.05)
            tone(out, "tri", root - 12, t, d, 0.3, gap=1.0 if last else 0.9, r=0.6 if last else 0.05)
            t += d

    return jingle(b, 2.7)


def fin_ronda() -> np.ndarray:
    """Four falling notes (a nod to the "Rock para los dientes" lead) and a chord."""

    def b(out):
        t = line(out, 0, [(74, 1), (71, 1), (69, 1), (66, 1)], "pulse25", 0.2, unit=0.07, gap=0.85)
        for m, v in [(71, 0.18), (66, 0.08), (62, 0.08)]:
            tone(out, "pulse25" if v > 0.1 else "square", m, t, 0.45, v, gap=1.0, r=0.3)
        tone(out, "tri", 47, t, 0.45, 0.28, gap=1.0, r=0.3)

    return jingle(b, 0.85)


def pase() -> np.ndarray:
    def b(out):
        tone(out, "pulse25", 72, 0, 0.08, 0.2, gap=1.0)
        tone(out, "pulse25", 67, 0.09, 0.16, 0.2, gap=1.0, r=0.08)

    return jingle(b, 0.35)


# Short sounds (card, weather, effect) draw from their own stream, in SONIDOS order
rng_sfx = np.random.default_rng(21)


def bandpass(x: np.ndarray, lo: float, hi: float) -> np.ndarray:
    return lowpass(x, hi) - lowpass(x, lo)


def clima() -> np.ndarray:
    """A big, round water drop with a tiny splash tick."""
    out = np.zeros(int(0.35 * SR))
    dur = 0.3
    n = int(dur * SR)
    x = np.linspace(0, 1, n)
    f = 500 * (1250 / 500) ** np.minimum(1, x * dur / 0.03) ** 0.4  # pitch rises in the first 30 ms
    drop = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * dur * 28) * np.minimum(1, x * n / (0.002 * SR))
    add(out, 0.6 * drop, 0)
    tick = bandpass(rng_sfx.standard_normal(int(0.006 * SR)), 2000, 7000)
    add(out, 0.15 * tick * np.linspace(1, 0, len(tick)), 0)
    return out


def jugar_carta() -> np.ndarray:
    """Sword clash: dense inharmonic partials, an impact burst and a little grit."""
    length, modes = 0.5, 24
    n = int(length * SR)
    t = np.arange(n) / SR
    clang = np.zeros(n)
    for f in np.exp(rng_sfx.uniform(np.log(1800), np.log(8500), modes)):
        dec = rng_sfx.uniform(6, 30) * (f / 3000) ** 0.5
        amp = rng_sfx.uniform(0.3, 1.0)
        clang += amp * np.sin(2 * np.pi * f * t + rng_sfx.uniform(0, 6.28)) * np.exp(-t * dec)
    clang /= modes**0.5
    clang += np.sin(2 * np.pi * 640 * t) * np.exp(-t * 25) * 0.5  # lower ring of the blade
    nb = int(0.03 * SR)
    clang[:nb] += 1.5 * bandpass(rng_sfx.standard_normal(nb), 1500, 9000) * np.exp(-np.linspace(0, 6, nb))
    out = np.zeros(int(0.55 * SR))
    add(out, 0.5 * np.tanh(clang * 1.6), 0)
    return out


def efecto() -> np.ndarray:
    """Singing bowl: one low triangle note beating slowly against a detuned copy."""

    def voice(m, decay, detune=0.0):
        s = osc("tri", hz(m) * (1 + detune), 1.05)
        s *= np.exp(-np.linspace(0, decay, len(s)))
        a = int(0.03 * SR)
        s[:a] *= np.linspace(0, 1, a)
        return s

    out = np.zeros(int(1.1 * SR))
    add(out, 0.15 * voice(64, 4), 0)
    add(out, 0.12 * voice(64, 4, detune=0.006), 0)
    add(out, 0.04 * voice(76, 6), 0)
    return lowpass(out, 2500)


def guardar(path: Path, x: np.ndarray, pico: float = 0.85) -> None:
    x = x / (np.max(np.abs(x)) + 1e-9) * pico
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())


SONIDOS = {
    "musica": (musica, 0.85),
    "victoria": (victoria, 0.85),
    "derrota": (derrota, 0.85),
    "fin-ronda": (fin_ronda, 0.7),
    "pase": (pase, 0.7),
    "clima": (clima, 0.55),
    "jugar-carta": (jugar_carta, 0.55),
    "efecto": (efecto, 0.55),
}


def main() -> None:
    destino = ASSETS / "sonidos"
    destino.mkdir(parents=True, exist_ok=True)
    for nombre, (generar, pico) in SONIDOS.items():
        x = generar()
        guardar(destino / f"{nombre}.wav", x, pico)
        print(f"{nombre}.wav  {len(x) / SR:.2f} s")


if __name__ == "__main__":
    main()
