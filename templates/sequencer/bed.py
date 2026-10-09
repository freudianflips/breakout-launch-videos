#!/usr/bin/env python3
"""The free scratch bed for 'Press play.', played from the same pattern as the picture.

  .venv/bin/python templates/sequencer/bed.py [--out templates/sequencer/score/bed.wav]

Every row in film.json is an instrument (kick, clap, hat, ghost shaker) and sounds only on the steps the
grid lights, from the bar its row starts, until the transport stops; the muted row stops on its mute.
On top: the grid's clock, a wash of ticks for the 700+ pull-back, a riser into the press, 1 beat of
silence, the drop with a pad and the committee's 3 notes, a thinner bar for the meeting and a lone clock
under the lockup. Replace it with a real track before anyone judges the music.
"""
import argparse
import json
import math
import os

import numpy as np
import soundfile as sf
from pedalboard import Compressor, HighpassFilter, LowpassFilter, Pedalboard, Reverb

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000
ap = argparse.ArgumentParser()
ap.add_argument("--out", default=os.path.join(HERE, "score", "bed.wav"))
args = ap.parse_args()
F = json.load(open(os.path.join(HERE, "film.json")))
BAR = 240 / F["bpm"]
S16 = BAR / 16
TR = F["transport"]
N = int((F["bars"] * BAR + 1.5) * SR)
rng = np.random.default_rng(128)
mix = np.zeros(N)


def add(x, t):
    s = int(round(t * SR))
    e = min(N, s + len(x))
    if e > s:
        mix[s:e] += x[: e - s]


def ax(d):
    return np.arange(int(d * SR)) / SR


def noise(d):
    return rng.standard_normal(int(d * SR))


def hp(x):
    return np.diff(np.concatenate([[0], x]))


def kick():
    t = ax(0.4)
    return np.sin(2 * math.pi * np.cumsum(46 + 130 * np.exp(-t / 0.028)) / SR) * np.exp(-t / 0.15) * 0.95


def clap():
    t = ax(0.22)
    env = sum(np.exp(-np.maximum(0, t - o) / 0.012) * (t >= o) for o in (0, 0.011, 0.022)) * 0.4 + np.exp(-t / 0.06) * 0.6
    return hp(hp(noise(0.22))) * env * 0.22


def hat():
    t = ax(0.06)
    return hp(hp(noise(0.06))) * np.exp(-t / 0.014) * 0.14


def shaker():
    t = ax(0.09)
    return hp(noise(0.09)) * np.minimum(1, t / 0.02) * np.exp(-t / 0.03) * 0.08


def click(g=0.05):
    t = ax(0.02)
    return hp(noise(0.02)) * np.exp(-t / 0.003) * g


def sub(f, d):
    t = ax(d)
    return np.sin(2 * math.pi * f * t) * np.minimum(1, t / 0.01) * np.exp(-t / (d * 0.7)) * 0.42


def pluck(f, d=0.9):
    t = ax(d)
    x = sum(np.sin(2 * math.pi * f * h * t) / h ** 1.6 for h in (1, 2, 3, 4))
    return x * np.minimum(1, t / 0.004) * np.exp(-t / 0.28) * 0.16


def pad(freqs, d):
    t = ax(d)
    x = sum(np.sin(2 * math.pi * f * t + 0.3 * np.sin(2 * math.pi * 0.4 * t)) for f in freqs) / len(freqs)
    return x * np.minimum(1, t / 0.3) * np.minimum(1, (d - t) / 0.4) * 0.12


SOUND = {"kick": kick, "clap": clap, "hat": hat, "shaker": shaker}


def hits(steps, a, b, mute=None):
    """Times of every lit step from bar a up to bar b (and before the mute)."""
    out = []
    for bar in range(int(a), int(math.ceil(b)) + 1):
        for k in steps:
            t = (bar * 16 + k) * S16
            if a * BAR - 1e-6 <= t < b * BAR - 1e-6 and (mute is None or t < mute * BAR - 1e-6):
                out.append(t)
    return out


# the grid's clock: a soft tick on every step while the transport runs
for a, b, g in ((0, TR["stop"], 0.035), (TR["drop"], TR["send"], 0.03), (TR["lockup"] + 0.55, TR["end"], 0.05)):
    for t in hits(range(16), a, b):
        add(click(g * (1.6 if round(t / S16) % 4 == 0 else 1)), t)

# the rows: the signals, exactly as the grid lights them
for r in F["rows"]:
    for t in hits(r["steps"], r["start"], TR["stop"], r.get("mute_at")):
        add(SOUND[r["sound"]](), t)
    if not r.get("mute_at"):
        for t in hits(r["steps"], TR["drop"], TR["send"]):
            add(SOUND[r["sound"]](), t)

# the committee: 1 note of the chord per chip
cm = F["committee"]
for t, f in zip(hits(cm["steps"], cm["start"], TR["send"]), (329.6, 392.0, 493.9)):
    add(pluck(f), t)
    add(pluck(f / 2) * 0.6, t)

# the bass under the rows and the drop
ROOT = {2: 41.2, 3: 41.2, 4: 49.0, 5: 55.0, 8: 41.2, 9: 49.0, 10: 55.0}
for b, f in ROOT.items():
    add(sub(f, BAR * (0.75 if b == 10 else 0.95)), b * BAR)

# 700+: a filtered wash of tiny ticks while the camera pulls back
z0 = TR["zoom"] * BAR
for _ in range(260):
    t = z0 + rng.uniform(0.05, 0.9) * BAR
    add(click(rng.uniform(0.01, 0.04)), t)

# the riser into the press, cut dead for the beat of silence before the drop
r0, r1 = TR["stop"] * BAR, (TR["press"] + 0.75) * BAR
t = ax(r1 - r0)
u = t / (r1 - r0)
sweep = np.sin(2 * math.pi * np.cumsum(110 + 330 * u ** 2) / SR) * 0.06 * u ** 1.5
wash = np.convolve(noise(r1 - r0), np.ones(6) / 6, mode="same") * 0.05 * u ** 2
add(sweep + wash, r0)
add(pad((82.4, 123.5), r1 - r0) * 0.8, r0)

# the drop: a pad across the email and the committee
add(pad((164.8, 196.0, 246.9, 293.7), (TR["send"] - TR["drop"]) * BAR + 0.3), TR["drop"] * BAR)

# the meeting: a thinner bar, kick on 1 to 3 and the hats, a bloom of the chord
b0 = TR["booked"]
for k in (0, 4, 8):
    add(kick(), (b0 * 16 + k) * S16)
for t in hits([2, 6, 10, 14], b0, b0 + 0.9):
    add(hat(), t)
add(pad((164.8, 246.9, 329.6, 392.0), BAR * 2.4) * 1.2, b0 * BAR)
add(sub(41.2, BAR * 1.5), b0 * BAR)

st = np.stack([mix, mix]).astype(np.float32)
st = Pedalboard([HighpassFilter(28), Compressor(threshold_db=-12, ratio=3, attack_ms=4, release_ms=90),
                 Reverb(room_size=0.2, wet_level=0.08, dry_level=1.0), LowpassFilter(15000)])(st, SR)
st *= 10 ** (-1 / 20) / max(1e-9, np.max(np.abs(st)))
os.makedirs(os.path.dirname(args.out), exist_ok=True)
sf.write(args.out, st.T, SR, subtype="PCM_24")
print(f"wrote {args.out}: {N / SR:.2f} s at {F['bpm']} BPM")
