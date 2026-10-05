#!/usr/bin/env python3
"""A free psych-indie scratch bed on the Plays film's bar grid (no account, seeded, always the same).

  .venv/bin/python film/plays/psych_bed.py [film/plays/film.json] [--out film/plays/score/bed.wav]

Phased, detuned pad chords with tape wobble for the hook; the kick, snare, hats and a round bass enter on
the drop bar; an arpeggio rides the burst; drums thin out for the lockup and the pad fades. It exists to
cut against. Replace it with a real take (launch-score) before anyone judges the music.
"""
import argparse
import json
import math
import os

import numpy as np
import soundfile as sf
from pedalboard import Chorus, Compressor, Delay, HighpassFilter, LowpassFilter, Pedalboard, Phaser, Reverb

SR = 48000
ap = argparse.ArgumentParser()
ap.add_argument("film", nargs="?", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "film.json"))
ap.add_argument("--out")
args = ap.parse_args()
FILM = json.load(open(args.film))
BPM, BARS, DROP = FILM["bpm"], FILM["bars"], FILM["drop_bar"]
BAR = 240 / BPM
BEAT = BAR / 4
DUR = BARS * BAR + 2.5
N = int(DUR * SR)
rng = np.random.default_rng(110)
out = args.out or os.path.join(os.path.dirname(os.path.abspath(args.film)), "score", "bed.wav")


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def at(t):
    return int(t * SR)


def env(n, a, d, s=0.0, r=None):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * (s + (1 - s) * np.exp(-t / max(d, 1e-4)))
    if r:
        rl = min(n, int(r * SR))
        e[-rl:] *= np.linspace(1, 0, rl)
    return e


def saw(f, n, phase=0.0):
    t = np.arange(n) / SR
    x = (t * f + phase) % 1.0
    return 2 * x - 1


def add(buf, x, t0):
    s = at(t0)
    e = min(len(buf), s + len(x))
    if e > s:
        buf[s:e] += x[: e - s]


# Em9, Cmaj7, G6, D/F#: 1 chord a bar
CHORDS = [[52, 55, 59, 62, 66], [48, 52, 55, 59, 64], [43, 50, 55, 59, 64], [42, 50, 54, 57, 62]]
ROOTS = [40, 36, 43, 42]

# ------------------------------------------------------------------ the pad: detuned saws, a slow filter opening
pad = np.zeros(N)
for b in range(BARS):
    ch = CHORDS[b % 4]
    n = at(BAR + 0.6)
    voice = np.zeros(n)
    for m in ch:
        for det in (-0.09, 0.0, 0.08):
            voice += saw(hz(m + det), n, rng.random()) * 0.06
    voice *= env(n, 0.35, 9, 0.85, 0.6)
    gain = 0.55 if b < DROP else 0.42 if b < BARS - 2 else 0.5 * (1 - (b - BARS + 2) / 2.2)
    add(pad, voice * gain, b * BAR)
t = np.arange(N) / SR
# the filter opens across the hook: a moving one-pole low-pass, done in blocks
cut = np.where(t < DROP * BAR, 500 + 2400 * (t / (DROP * BAR)) ** 1.6, 3200)
cut = np.where(t > (BARS - 3) * BAR, cut * np.clip(1 - (t - (BARS - 3) * BAR) / (3 * BAR), 0.2, 1), cut)
y = np.zeros(N)
z = 0.0
blk = 256
for i in range(0, N, blk):
    a = 1 - math.exp(-2 * math.pi * cut[i] / SR)
    seg = pad[i:i + blk]
    o = np.empty_like(seg)
    for j, v in enumerate(seg):
        z += a * (v - z)
        o[j] = z
    y[i:i + blk] = o
pad = y
# tape wobble: a slow wow on a variable delay
wow = 0.0022 * np.sin(2 * math.pi * 0.55 * t) + 0.0008 * np.sin(2 * math.pi * 3.1 * t)
idx = np.clip(np.arange(N) - (0.006 + wow) * SR, 0, N - 1)
pad = np.interp(idx, np.arange(N), pad)
pad_st = np.stack([pad, pad])
pad_st = Pedalboard([Phaser(rate_hz=0.18, depth=0.8, centre_frequency_hz=900, feedback=0.45, mix=0.7),
                     Chorus(rate_hz=0.4, depth=0.35, mix=0.5), Reverb(room_size=0.7, wet_level=0.35, dry_level=0.8, width=1.0)])(pad_st.astype(np.float32), SR)

# ------------------------------------------------------------------ drums, from the drop
def kick():
    n = at(0.5)
    tt = np.arange(n) / SR
    f = 46 + 110 * np.exp(-tt / 0.04)
    return np.sin(2 * math.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.2) * 0.95


def snare():
    n = at(0.4)
    tt = np.arange(n) / SR
    body = np.sin(2 * math.pi * 185 * tt) * env(n, 0.001, 0.06) * 0.5
    noise = rng.standard_normal(n) * env(n, 0.001, 0.11) * 0.5
    noise = np.diff(np.concatenate([[0], noise]))
    return body + noise


def hat(openh=False):
    n = at(0.35 if openh else 0.08)
    x = np.diff(np.concatenate([[0], rng.standard_normal(n)]))
    x = np.diff(np.concatenate([[0], x]))
    return x * env(n, 0.0005, 0.12 if openh else 0.018) * 0.12


def tamb():
    n = at(0.12)
    x = np.diff(np.concatenate([[0], rng.standard_normal(n)]))
    return x * env(n, 0.001, 0.04) * 0.07


drums = np.zeros(N)
LAST_DRUM_BAR = BARS - 2
for b in range(DROP, LAST_DRUM_BAR):
    t0 = b * BAR
    for k in (0, 2.5 if b % 2 else 2):
        add(drums, kick(), t0 + k * BEAT)
    for k in (1, 3):
        add(drums, snare(), t0 + k * BEAT)
    for e in range(8):
        add(drums, hat(openh=(e % 4 == 3)), t0 + e * BEAT / 2 + (0.012 if e % 2 else 0))
    if 12 <= b < 16:
        for s16 in range(16):
            add(drums, tamb() * (1.2 if s16 % 4 == 2 else 0.7), t0 + s16 * BEAT / 4)
drums = Pedalboard([Compressor(threshold_db=-14, ratio=3, attack_ms=8, release_ms=120), Reverb(room_size=0.25, wet_level=0.12, dry_level=0.95),
                    LowpassFilter(9000)])(np.stack([drums, drums]).astype(np.float32), SR)

# ------------------------------------------------------------------ bass: round, on the roots, a push on the and of 2
bass = np.zeros(N)
for b in range(DROP, BARS - 1):
    r = ROOTS[b % 4]
    for k, off, ln in ((0, 0, 0.9), (1.5, 0, 0.4), (2, 7, 0.4), (3, 12, 0.35), (3.5, 0, 0.4)):
        n = at(ln * BEAT * 2)
        tt = np.arange(n) / SR
        f = hz(r + off)
        x = np.sin(2 * math.pi * f * tt) * 0.7 + np.tanh(3 * np.sin(2 * math.pi * f * tt)) * 0.2
        add(bass, x * env(n, 0.004, 0.35, 0.6, 0.05) * 0.55, b * BAR + k * BEAT)
bass = Pedalboard([LowpassFilter(1400), Compressor(threshold_db=-16, ratio=4)])(np.stack([bass, bass]).astype(np.float32), SR)

# ------------------------------------------------------------------ the burst arpeggio
arp = np.zeros(N)
for b in range(12, 16):
    ch = CHORDS[b % 4]
    for s16 in range(16):
        m = ch[[1, 2, 3, 4, 3, 2][s16 % 6]] + 12
        n = at(0.16)
        tt = np.arange(n) / SR
        x = np.sign(np.sin(2 * math.pi * hz(m) * tt)) * 0.5 + np.sin(2 * math.pi * hz(m) * tt) * 0.5
        add(arp, x * env(n, 0.002, 0.07) * 0.12, b * BAR + s16 * BEAT / 4)
arp = Pedalboard([LowpassFilter(3800), Delay(delay_seconds=BEAT * 0.75, feedback=0.35, mix=0.35), Phaser(rate_hz=0.6, mix=0.5)])(
    np.stack([arp, arp]).astype(np.float32), SR)

# ------------------------------------------------------------------ the tape master
mix = pad_st * 0.9 + drums * 0.9 + bass * 0.9 + arp
mix = np.tanh(mix * 1.6) / 1.6                       # tape saturation
mix = Pedalboard([HighpassFilter(30), LowpassFilter(11500)])(mix.astype(np.float32), SR)
fade = at(1.5)
mix[:, -fade:] *= np.linspace(1, 0, fade)
mix *= 10 ** (-1 / 20) / max(1e-9, np.max(np.abs(mix)))
os.makedirs(os.path.dirname(out), exist_ok=True)
sf.write(out, mix.T, SR, subtype="PCM_24")
print(f"wrote {out}: {DUR:.2f} s, {BPM} BPM, drop at bar {DROP + 1} ({DROP * BAR:.2f} s)")
