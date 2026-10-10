"""Riffs transcribed from LaCuerda tabs, rendered as chiptune: literal and hidden versions."""

import re
import sys
from pathlib import Path

import numpy as np
from demo import SR, add, drum, env, hz, noise_hit, osc, reverb

import demo

OPEN = {"e": 64, "B": 59, "G": 55, "D": 50, "A": 45, "E": 40}


def parse(tab, cols_per_unit=2):
    """Tab (high e first) -> list of (onset_units, [midi...]). Column spacing gives rhythm."""
    rows = []
    for line in tab.strip("\n").splitlines():
        line = line.strip()
        name, body = line[0], line[line.index("|") + 1 :] if "|" in line[:3] else line[1:]
        rows.append((OPEN[name], body))
    events = {}
    for base, body in rows:
        for m in re.finditer(r"\d+", body):
            events.setdefault(m.start(), []).append(base + int(m.group()))
    cols = sorted(events)
    c0 = cols[0]
    return [((c - c0) / cols_per_unit, sorted(events[c])) for c in cols]


def to_notes(events, last=2.0):
    """Onsets -> (start, dur, pitches); duration runs to the next onset."""
    out = []
    for i, (t, ps) in enumerate(events):
        nxt = events[i + 1][0] if i + 1 < len(events) else t + last
        out.append((t, nxt - t, ps))
    return out


def swing(notes, ratio=2 / 3):
    """Straight eighths -> 6/8 lilt: first of each pair longer."""
    def warp(t):
        beat, frac = divmod(t, 2)
        return beat * 2 + (frac * 2 * ratio if frac <= 1 else 2 * ratio + (frac - 1) * 2 * (1 - ratio))
    return [(warp(t), warp(t + d) - warp(t), ps) for t, d, ps in notes]


def render(notes, unit, lead="pulse25", fifths=False, transpose=0, drums=None, bass=None, tail=1.0):
    end = max(t + d for t, d, _ in notes) * unit + tail
    out = np.zeros(int((end + 2) * SR))
    for t, d, ps in notes:
        dur = max(0.04, d * unit * 0.88)
        n = int(dur * SR)
        top = ps[-1] + transpose
        voices = [p + transpose for p in ps] if len(ps) > 1 else [top]
        for k, p in enumerate(voices):
            kind = lead if p == top else "square"
            vol = 0.24 if p == top else 0.08
            add(out, vol * osc(kind, hz(p), dur, vib=0.1) * env(n, 0.004, 0.03), t * unit)
        if fifths and len(ps) == 1:
            add(out, 0.1 * osc("square", hz(top - 5), dur) * env(n, 0.004, 0.03), t * unit)
    if bass:
        for t, p, d in bass:
            n = int(d * unit * 0.85 * SR)
            add(out, 0.3 * osc("tri", hz(p + transpose), d * unit * 0.85) * env(n, 0.003, 0.04), t * unit)
    if drums:
        for t, kind in drums:
            if kind == "k":
                add(out, 0.35 * drum(0.35, 90), t * unit)
            elif kind == "s":
                add(out, 0.22 * noise_hit(0.12, 5000, 10), t * unit)
            else:
                add(out, 0.07 * noise_hit(0.04, 7000, 12), t * unit)
    demo.TOTAL = end
    return out


def beats(n_units, pattern, step=1):
    """Repeat a drum pattern string ('k', 's', 'h', '.') every `step` units."""
    return [(i * step, c) for i, c in enumerate((pattern * 64)[: int(n_units / step)]) if c != "."]


# --- tabs (verbatim from LaCuerda, trimmed to the riff) ---------------------------------

PIBE = """
e|---------------|-------------------|---------------|-------------|
B|---------------|-------------------|---------------|-------------|
G|-9-9-7-9-7-----|-------------------|-9-9-7-9-7-----|-------------|
D|-----------9-9-|-5-7-7-5---5-------|-----------9-9-|-5-7-7-5-----|
A|---------------|---------7---7-5---|---------------|---------7-7-|
E|---------------|-----------------7-|---------------|-------------|
"""

AMOR = """
e|-8-8-5------------|-8-8-5------------|-5-5-----5-5--------5---5--7-7-|
B|-------8--5-6-5-6-|-------8--5-6-5-6-|-----5-------5-8--8---8--------|
G|------------------|------------------|-------5-----------------------|
D|------------------|------------------|-------------------------------|
A|------------------|------------------|-------------------------------|
E|------------------|------------------|-------------------------------|
"""

SEMEN = """
e|----------------------------4-4----4-4----4-4-|
B|-3-4-3-4------3-4-----------4-4----4-4----4-4-|
G|------------------3-4-------4-4----4-4----4-4-|
D|----------------------5-6---------------------|
A|----------------------------------------------|
E|----------------------------4------4------4---|
"""

REMERA = """
e|----------------------------------------10----|
B|----------------10----------------10-12-------|
G|--11-9---11--11----12-11--9----12-------------|
D|-------12-------------------12----------------|
A|----------------------------------------------|
E|----------------------------------------------|
"""

DIENTES = """
e|10-10-7-7-----------------------------------|
B|---------10-10-7-7--------------------------|
G|------------------9-9-7-7-------------------|
D|-------------------------9-9-7-9------------|
A|--------------------------------------------|
E|--------------------------------------------|
"""

HEROE = """
e|--------------------------------|------------3-3-2------------------|
B|--------------------------5--5--|------------3-3-2----------5--5----|
G|-----------2--2-2---------4--4--|---------------------------4--4----|
D|-----------2--2-2---------------|-----------------------------------|
A|------2-4---------4-2-4---------|-------2-4----------4-2-4----------|
E|--2-4---------------------------|--2-4------------------------------|
"""

PALO = """
e|------------------------------5--5-5--5-6-6-6-5-|
B|---------------3--------------5--5-6--6-6-6-6-5-|
G|------2-2------3--3-3-2-------5--5-5--5-5-5-5-5-|
D|--0-0-----3-0-----------3-----------------------|
A|------------------------------------------------|
E|------------------------------------------------|
"""

BANDAS = """
e|------------------|----6-6--------------------|
B|------------------|----6-6-----------3--3-(3)-|
G|------------------|---------------5--3--3-(3)-|
D|-7-7-7-7--7-7-7-7-|--5------------5-----------|
A|-5-5-5-5--5-5-5-5-|--5------------3-----------|
E|------------------|--3------------------------|
"""

PERRO = """
e|-------------|-------------|-------------|-------------|
B|-------------|-------------|-------------|-------------|
G|-------------|-------------|-------------|-------------|
D|-------------|-------------|-10-10-12-10-|-10-10-12-10-|
A|-10-10-12-10-|-10-10-12-10-|-8--8--8--8--|-8--8--8--8--|
E|-8--8--8--8--|-8--8--8--8--|-------------|-------------|
"""

# name, tab, cols per eighth, literal tempo (s per eighth), hidden: (transpose, unit, swing, fifths, drums)
RIFFS = [
    ("pibe", PIBE, 2, 0.15, (-2, 0.16, True, True, "k..s..")),
    ("amor", AMOR, 2, 0.14, (-3, 0.17, True, False, "k..s..")),
    ("semen", SEMEN, 2, 0.11, (-6, 0.15, False, True, "k.h.s.h.")),
    ("remera", REMERA, 2, 0.12, (-7, 0.15, True, False, "k..s..")),
    ("dientes", DIENTES, 2, 0.1, (-9, 0.13, True, True, "k..s..")),
    ("heroe", HEROE, 2, 0.12, (11, 0.14, True, False, "k..s..")),
    ("palo", PALO, 2, 0.12, (2, 0.15, True, False, "k..s..")),
    ("bandas", BANDAS, 2, 0.11, (0, 0.14, False, False, "k.h.s.h.")),
    ("perro", PERRO, 3, 0.16, (14, 0.19, True, False, "k..s..")),
]


def literal(tab, cpu, unit):
    notes = to_notes(parse(tab, cpu))
    end = max(t + d for t, d, _ in notes)
    lift = 12 if np.mean([p for _, _, ps in notes for p in ps]) < 55 else 0
    return render(notes, unit, transpose=lift, drums=beats(end, "k.h.s.h."), tail=0.6)


def hidden(tab, cpu, cfg):
    transpose, unit, sw, fifths, pat = cfg
    notes = to_notes(parse(tab, cpu))
    if sw:
        notes = swing(notes)
    notes = notes + [(t + max(a + b for a, b, _ in notes), d, p) for t, d, p in notes]  # play it twice
    end = max(t + d for t, d, _ in notes)
    return reverb(render(notes, unit, fifths=fifths, transpose=transpose, drums=beats(end, pat)), 0.8, 0.12)


if __name__ == "__main__":
    out = Path(sys.argv[1])
    for name, tab, cpu, unit, cfg in RIFFS:
        demo.save(out / f"r-{name}-literal.wav", literal(tab, cpu, unit))
        demo.save(out / f"r-{name}-oculto.wav", hidden(tab, cpu, cfg))
        print(name, [p for _, p in parse(tab, cpu)][:16])
