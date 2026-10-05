#!/usr/bin/env python3
"""A free, seeded scratch track for 'Signal in. Meeting out.': minimal and dry, on the film's bar grid.

  .venv/bin/python film/signal/bed.py [--out film/signal/score/bed.wav]

Kick on the beat, a rim on 2 and 4, quiet 16th clicks and a sub on each bar's root; the email bars
(6 and 7) double the clicks; the lockup drops to a held sub and a single soft chord. Replace it
with a real track before anyone judges the music.
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
BEAT = BAR / 4
BARS = F["bars"]
N = int((BARS * BAR + 1.5) * SR)
rng = np.random.default_rng(128)
mix = np.zeros(N)


def add(x, t):
    s = int(t * SR)
    e = min(N, s + len(x))
    if e > s:
        mix[s:e] += x[: e - s]


def ax(d):
    return np.arange(int(d * SR)) / SR


def kick():
    t = ax(0.35)
    return np.sin(2 * math.pi * np.cumsum(48 + 120 * np.exp(-t / 0.03)) / SR) * np.exp(-t / 0.13) * 0.9


def rim():
    t = ax(0.12)
    return (np.sin(2 * math.pi * 1700 * t) * 0.5 + np.diff(np.concatenate([[0], rng.standard_normal(len(t))])) * 0.5) * np.exp(-t / 0.018) * 0.35


def click():
    t = ax(0.03)
    return np.diff(np.concatenate([[0], rng.standard_normal(len(t))])) * np.exp(-t / 0.004) * 0.12


def sub(f, d):
    t = ax(d)
    return np.sin(2 * math.pi * f * t) * np.minimum(1, t / 0.01) * np.exp(-t / (d * 0.8)) * 0.5


ROOTS = [41.2, 41.2, 49.0, 49.0, 55.0, 55.0, 41.2, 49.0, 55.0, 61.7, 41.2, 41.2]   # E1, G1, A1, B1
for b in range(BARS):
    t0 = b * BAR
    lock = b >= 10
    if not lock:
        for k in range(4):
            if b == 0 and k > 0:
                continue
            add(kick(), t0 + k * BEAT)
        if b >= 1:
            for k in (1, 3):
                add(rim(), t0 + k * BEAT)
        n = 32 if b in (6, 7) else 16
        for k in range(n):
            add(click() * (1.0 if k % 4 == 2 else 0.6), t0 + k * BAR / n)
        add(sub(ROOTS[b], BAR * 0.95), t0)
    elif b == 10:
        add(kick(), t0)
        add(sub(ROOTS[0], BAR * 2), t0)
        t = ax(BAR * 2)
        chord = sum(np.sin(2 * math.pi * 82.4 * r * t) for r in (2, 2.5198, 2.9966, 3.7754)) / 4
        add(chord * np.minimum(1, t / 0.02) * np.exp(-t / 1.2) * 0.25, t0)
st = np.stack([mix, mix]).astype(np.float32)
st = Pedalboard([HighpassFilter(28), Compressor(threshold_db=-12, ratio=3, attack_ms=4, release_ms=90),
                 Reverb(room_size=0.18, wet_level=0.08, dry_level=1.0), LowpassFilter(14000)])(st, SR)
st *= 10 ** (-1 / 20) / max(1e-9, np.max(np.abs(st)))
os.makedirs(os.path.dirname(args.out), exist_ok=True)
sf.write(args.out, st.T, SR, subtype="PCM_24")
print(f"wrote {args.out}: {N / SR:.2f} s at {F['bpm']} BPM")
