#!/usr/bin/env python3
"""The score for the Signals launch: punchy deep house, synthesised here, free.

  .venv/bin/python score.py [--out score/score.wav]   (from this folder)

No samples, no vocals, nothing bright: a round, heavy four-on-the-floor kick that everything else ducks under,
a rolling syncopated sub bassline, warm dark electric-piano chord stabs (F minor 9ths), a low pad, soft dark
off-beat hats and a shaker, a clap on 2 and 4. The picture's events are its cues, from film.json "at":

  visit      the pad and a filtered stab alone, opening up
  land       the drop: kick, bass and the pump as the camera lands on her
  signals    a low thump and a chord stab as each signal lands
  agent      a filtered noise sweep and a clap roll, then the full groove
  email      a breakdown bar on the cut (no kick, no bass), the groove back as the body types; a hit on Sent
  close      the last chord rings out under the logo
"""
import argparse
import json
import os

import numpy as np
import soundfile as sf
from pedalboard import Compressor, HighpassFilter, HighShelfFilter, Limiter, LowpassFilter, Pedalboard, Reverb

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("--out", default=os.path.join(HERE, "score", "score.wav"))
args = ap.parse_args()
F = json.load(open(os.path.join(HERE, "film.json")))
A = F["at"]
SR = 48000
BAR = 240 / F["bpm"]
END = A["end"] * BAR
N = int((END + 2.0) * SR)
rng = np.random.default_rng(11)
BED = np.zeros((2, N))                                              # everything that ducks under the kick
KB = np.zeros(N)                                                    # the kick and the bass's attack: never ducked


def s(bar):
    return bar * BAR


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def put(x, t, gl=1.0, gr=None, bus=None):
    i = int(t * SR)
    if i >= N or i < 0:
        return
    x = x[: N - i]
    if bus is KB:
        KB[i:i + len(x)] += x
        return
    BED[0, i:i + len(x)] += x * gl
    BED[1, i:i + len(x)] += x * (gl if gr is None else gr)


def lp(x, f):
    return Pedalboard([LowpassFilter(f)])(x.astype(np.float32)[None, :], SR)[0]


def bp(x, lo, hi):
    return Pedalboard([HighpassFilter(lo), LowpassFilter(hi)])(x.astype(np.float32)[None, :], SR)[0]


def kick(d=0.5):
    n = int(d * SR); t = np.arange(n) / SR
    f = 48 + 110 * np.exp(-t / 0.045)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.22)
    click = lp(rng.standard_normal(n) * np.exp(-t / 0.004), 2500) * 0.25
    return np.tanh(2.6 * (body + click)) * 0.95


def clap():
    n = int(0.25 * SR); t = np.arange(n) / SR
    e = sum(np.exp(-np.maximum(t - o, 0) / 0.01) * (t >= o) for o in (0, 0.012, 0.024)) + 0.5 * np.exp(-t / 0.07)
    return bp(rng.standard_normal(n) * e, 700, 3200) * 0.6


def hat(open_=False):
    n = int((0.16 if open_ else 0.04) * SR); t = np.arange(n) / SR
    return bp(rng.standard_normal(n), 5000, 9000) * np.exp(-t / (0.05 if open_ else 0.012)) * 0.11


def shaker():
    n = int(0.06 * SR); t = np.arange(n) / SR
    return bp(rng.standard_normal(n), 3000, 7000) * np.minimum(1, t / 0.01) * np.exp(-t / 0.02) * 0.05


def keys(notes, dur, cut=1600):
    """A warm electric-piano stab: sines with a soft second harmonic, a quick decay, low-passed."""
    n = int(dur * SR); t = np.arange(n) / SR
    x = np.zeros(n)
    for m in notes:
        f = hz(m)
        x += np.sin(2 * np.pi * f * t + 0.6 * np.sin(2 * np.pi * f * t) * np.exp(-t / 0.05)) + 0.25 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.08)
    x *= np.minimum(1, t / 0.004) * np.exp(-t / 0.22)
    return lp(x / len(notes), cut) * 1.3


def pad(notes, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    x = sum(np.sin(2 * np.pi * hz(m) * (1 + d) * t) for m in notes for d in (-0.002, 0.002)) / (2 * len(notes))
    return lp(x * np.minimum(1, t / 0.3) * np.minimum(1, (dur - t) / 0.3).clip(0, 1), 900) * 0.5


def bass(m, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    f = hz(m)
    x = np.sin(2 * np.pi * f * t) + 0.3 * np.tanh(3 * np.sin(2 * np.pi * f * t))
    return lp(x * np.minimum(1, t / 0.004) * np.exp(-t / 0.18), 380) * 0.55


def thump():
    n = int(0.35 * SR); t = np.arange(n) / SR
    f = 70 + 60 * np.exp(-t / 0.03)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.12) * 0.6


def sweep(dur):
    n = int(dur * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n) * (t / dur) ** 2
    out = np.zeros(n); step = int(0.05 * SR)
    for i in range(0, n, step):                                     # a low-pass that opens as it rises, kept dark
        out[i:i + step] = lp(x[i:i + step], 400 + 3600 * (i / n))
    return out * 0.2


# F minor deep house: Fm9, Dbmaj9, Bbm9, C7sus4, one per bar
PROG = [(41, [56, 60, 63, 67]), (37, [53, 56, 60, 63]), (46, [56, 61, 65, 68]), (36, [55, 58, 60, 65])]
STABS = [0.5 / 4, 1.5 / 4 + 0.0625, 2.5 / 4, 3.5 / 4 - 0.0625]     # syncopated, in bars
BASSLINE = [(0, 0, 0.18), (3, 12, 0.08), (6, 0, 0.12), (8, 7, 0.1), (10, 0, 0.14), (14, 12, 0.08)]   # (16th, interval, dur)

end_music = A["close"] + 1.75
pump = np.ones(N)


def kick_at(b):
    return (A["land"] <= b < A["email"]) or (A["email"] + 1 <= b < A["close"] + 0.01)


b = 0.0
while b < end_music:
    root, notes = PROG[int(b) % 4]
    dur = s(min(1, end_music - b))
    brk = A["email"] <= b < A["email"] + 1
    put(pad([n - 12 for n in notes[:3]], dur), s(b), 0.9, 1.0)
    cut = 500 + 1100 * min(1, b / max(A["land"], 0.01)) if b < A["land"] else (900 if brk else 1600)
    for k, st in enumerate(STABS):
        if b + st < end_music:
            put(keys(notes, 0.4, cut), s(b + st), 0.85 if k % 2 else 1.0, 1.0 if k % 2 else 0.85)
    if b >= A["land"] and not brk:
        for q, iv, d in BASSLINE:
            put(bass(root - 12 + iv, d * BAR), s(b + q / 16))
    for k in range(4):
        bb = b + k / 4
        if bb >= end_music:
            break
        if kick_at(bb):
            put(kick(), s(bb), bus=KB)
            i = int(s(bb) * SR); n = int(0.3 * SR)
            if i < N:
                seg = 1 - 0.92 * np.exp(-np.arange(min(n, N - i)) / SR / 0.12)
                pump[i:i + len(seg)] = np.minimum(pump[i:i + len(seg)], seg)
            if k in (1, 3):
                put(clap(), s(bb), 0.95, 1.0)
        if bb >= A["land"] and not brk:
            put(hat(open_=True), s(bb + 1 / 8), 0.75, 0.95)
            for q in (1 / 16, 3 / 16):
                put(shaker(), s(bb + q), 0.6, 0.9)
    b += 1

# the cues
for i, at in enumerate(A["signals"]):
    land = at + A["load"]
    root, notes = PROG[int(land) % 4]
    put(thump(), s(land), bus=KB)
    put(keys([n + 12 for n in notes], 0.35, 1900) * 0.8, s(land), 0.9, 1.0)
put(sweep(s(A["agent"]) - s(A["agent"] - 0.75)), s(A["agent"] - 0.75), 0.9, 1.0)
for k in range(4):
    put(clap() * (0.4 + 0.15 * k), s(A["agent"] - 0.25 + k / 16), 1.0)
put(sweep(s(A["email"]) - s(A["email"] - 0.5)), s(A["email"] - 0.5), 1.0, 0.9)
put(thump(), s(A["sent"]), bus=KB)
put(keys(PROG[int(A["sent"]) % 4][1], 0.5, 1900), s(A["sent"]))
put(kick() * 1.05, s(A["close"]), bus=KB)
put(pad(PROG[0][1], 3.5) * 1.2, s(A["close"]), 1.0)

duck = 0.1 + 0.9 * pump
mix = np.stack([BED[0] * duck + KB, BED[1] * duck + KB]).astype(np.float32)
fx = Pedalboard([HighpassFilter(30), HighShelfFilter(cutoff_frequency_hz=5000, gain_db=-5),
                 Reverb(room_size=0.3, damping=0.7, wet_level=0.06, dry_level=1.0, width=1.0),
                 Compressor(threshold_db=-16, ratio=2.5, attack_ms=12, release_ms=140), Limiter(threshold_db=-1.0)])
y = fx(mix, SR)
tail = int((END + 0.6) * SR)
fade = np.ones(y.shape[1]); fade[tail:] = 0
f0 = int(END * SR) - int(1.2 * SR)
fade[f0:tail] = np.linspace(1, 0, tail - f0)
y *= fade[None, :]
y *= 10 ** (-1 / 20) / max(1e-9, float(np.max(np.abs(y))))
os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
sf.write(args.out, y.T, SR, subtype="PCM_24")
print(f"wrote {args.out}: {y.shape[1] / SR:.2f} s at {F['bpm']} BPM")
