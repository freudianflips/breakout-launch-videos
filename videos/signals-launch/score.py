#!/usr/bin/env python3
"""The score for the Signals launch: punchy, emotional UK house in the Fred again.. vein, synthesised here, free.

  .venv/bin/python score.py [--out score/score.wav]   (from this folder)

No samples and no vocals: a four-on-the-floor kick that every other part ducks under (the pump), off-beat hats,
claps on 2 and 4, a sub on the roots, wide detuned chords (F minor: Fm, Db, Ab, Eb), and a formant "vocal chop"
synth that stutters a short motif. The picture's events are its cues, from film.json "at":

  visit      filtered chords alone, the filter opening
  land       the drop: the kick, the sub and the pump come in as the camera lands on her
  signals    a bright chop per signal as it lands, rising
  agent      a riser and a clap fill, then the full groove while the agent types
  email      a hard cut: one bar with no kick (chords and chops only), the kick back as the body types; a hit on Sent
  close      the last chord rings out under the logo, then silence
"""
import argparse
import json
import os

import numpy as np
import soundfile as sf
from pedalboard import Compressor, HighpassFilter, Limiter, LowpassFilter, Pedalboard, Reverb

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("--out", default=os.path.join(HERE, "score", "score.wav"))
args = ap.parse_args()
F = json.load(open(os.path.join(HERE, "film.json")))
A = F["at"]
SR = 48000
BAR = 240 / F["bpm"]
BEAT = BAR / 4
END = A["end"] * BAR
N = int((END + 2.0) * SR)
rng = np.random.default_rng(7)
L, R = np.zeros(N), np.zeros(N)
KB = np.zeros(N)                                                   # the kick bus: never ducked


def s(bar):
    return bar * BAR


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def kput(x, t):
    i = int(t * SR)
    if i < N:
        x = x[: N - i]
        KB[i:i + len(x)] += x


def put(x, t, gl=1.0, gr=None):
    i = int(t * SR)
    if i >= N or i + len(x) <= 0:
        return
    x = x[: N - i]
    L[i:i + len(x)] += x * gl
    R[i:i + len(x)] += x * (gl if gr is None else gr)


def env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)


def kick(d=0.42):
    n = int(d * SR); t = np.arange(n) / SR
    f = 46 + 120 * np.exp(-t / 0.035)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.16)
    x += 0.35 * np.sin(2 * np.pi * np.cumsum(f * 2) / SR) * np.exp(-t / 0.02)
    return np.tanh(2.2 * x) * 0.9


def clap():
    n = int(0.3 * SR); t = np.arange(n) / SR
    nz = rng.standard_normal(n)
    e = sum(np.exp(-np.maximum(t - o, 0) / 0.012) * (t >= o) for o in (0, 0.01, 0.021)) + 0.6 * np.exp(-t / 0.09)
    return np.convolve(nz * e, np.ones(6) / 6, "same") * 0.35


def hat(open_=False):
    n = int((0.22 if open_ else 0.05) * SR)
    x = rng.standard_normal(n)
    x = np.diff(np.concatenate([[0], x]))
    return x * env(n, 0.0005, 0.06 if open_ else 0.012) * 0.045


def saw(f, n, det=(0, 7, -7, 12, -12)):
    t = np.arange(n) / SR
    out = np.zeros(n)
    for c in det:
        ff = f * 2 ** (c / 1200)
        out += 2 * ((t * ff + rng.random()) % 1) - 1
    return out / len(det)


def chord(notes, dur, bright=1.0):
    n = int(dur * SR)
    x = sum(saw(hz(m), n) for m in notes) / len(notes)
    t = np.arange(n) / SR
    x *= np.minimum(1, t / 0.02) * np.minimum(1, (dur - t) / 0.05).clip(0, 1)
    cut = 900 + 4200 * bright
    return Pedalboard([LowpassFilter(cut)])(x.astype(np.float32)[None, :], SR)[0] * 0.3


def chop(m, dur=0.16, vowel=0):
    """A formant 'vocal chop': a buzzy saw through two vowel-shaped band-passes, short and gated."""
    n = int(dur * SR); t = np.arange(n) / SR
    f0 = hz(m)
    x = saw(f0, n, (0, 4, -4))
    f1, f2 = [(730, 1090), (530, 1840), (300, 2290), (570, 840)][vowel % 4]
    X = np.fft.rfft(x); fr = np.fft.rfftfreq(n, 1 / SR)
    g = np.exp(-((fr - f1) / 120) ** 2) + 0.7 * np.exp(-((fr - f2) / 180) ** 2)
    y = np.fft.irfft(X * g, n)
    y *= np.minimum(1, t / 0.006) * np.exp(-t / (dur * 0.7))
    return y / (np.max(np.abs(y)) + 1e-9) * 0.5


def sub(m, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * hz(m) * t) * np.minimum(1, t / 0.01) * np.minimum(1, (dur - t) / 0.03).clip(0, 1) * 0.5


def riser(dur):
    n = int(dur * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n) * (t / dur) ** 2
    x = Pedalboard([HighpassFilter(1200)])(x.astype(np.float32)[None, :], SR)[0]
    return x * 0.18


# F minor: Fm, Db, Ab, Eb, one per bar, voiced wide
PROG = [(53, [65, 68, 72, 77]), (49, [65, 68, 73, 77]), (56, [63, 68, 72, 75]), (51, [63, 67, 70, 75])]
MOTIF = [(0, 77, 0), (0.75, 75, 1), (1.5, 72, 2), (2.5, 75, 1), (3, 72, 3)]       # (beat, note, vowel)

end_music = A["close"] + 1.75
kick_on = lambda b: (A["land"] <= b < A["email"]) or (A["email"] + 1 <= b < A["close"])
pump = np.ones(N)

b = 0.0
while b < end_music:
    root, notes = PROG[int(b) % 4]
    bright = 0.15 + 0.85 * min(1, b / max(A["land"], 0.01)) if b < A["land"] else 1.0
    dur = s(min(1, end_music - b))
    brk = A["email"] <= b < A["email"] + 1                        # the breakdown bar on the cut to the email
    put(chord(notes, dur, 0.35 if brk else bright) * (0.55 if brk else 1.0), s(b), 0.9, 1.0)
    if b >= A["land"] and not brk:
        put(sub(root - 12, dur), s(b), 1.0)
    for k in range(4):
        bb = b + k / 4
        if bb >= end_music:
            break
        if kick_on(bb):
            kput(kick(), s(bb))
            i = int(s(bb) * SR); n = int(0.28 * SR)
            if i < N:
                seg = 1 - 0.9 * np.exp(-np.arange(min(n, N - i)) / SR / 0.11)
                pump[i:i + len(seg)] = np.minimum(pump[i:i + len(seg)], seg)
            if k in (1, 3):
                put(clap(), s(bb), 0.9, 1.0)
        if bb >= A["land"] and not brk:
            put(hat(open_=True), s(bb + 1 / 8), 0.7, 0.9)
            for q in (1 / 16, 3 / 16):
                put(hat(), s(bb + q), 0.5 + 0.3 * (q > 0.1), 0.8)
    if b >= A["agent"]:                                           # the chop motif on the groove
        for beat, m, vw in MOTIF:
            if b + beat / 4 < end_music:
                put(chop(m, 0.14, vw), s(b + beat / 4), 0.8, 1.0)
    b += 1

# the cues
for i, at in enumerate(A["signals"]):
    land = at + A["load"]
    for j, m in enumerate((72 + [0, 3, 5, 7, 10][i], 84 + [0, 3, 5, 7, 10][i])):
        put(chop(m, 0.12, i), s(land) + j * BEAT / 4, 0.9 if j else 1.0, 1.0 if j else 0.9)
put(riser(s(A["agent"]) - s(A["agent"] - 0.75)), s(A["agent"] - 0.75), 0.9, 1.0)
for k in range(4):
    put(clap() * (0.5 + 0.15 * k), s(A["agent"] - 0.25 + k / 16), 1.0)
put(riser(s(A["email"]) - s(A["email"] - 0.5)), s(A["email"] - 0.5), 1.0, 0.9)
for j, m in enumerate((77, 80, 84)):
    put(chop(m, 0.18, j), s(A["sent"]) + j * BEAT / 4, 1.0)
kput(kick() * 1.1, s(A["close"]))
put(chop(77, 0.5, 0) * 0.8, s(A["close"]), 1.0)

duck = 0.12 + 0.88 * pump                                            # the pump: everything but the kick ducks under it
mix = np.stack([L * duck + KB, R * duck + KB]).astype(np.float32)
fx = Pedalboard([HighpassFilter(28), Reverb(room_size=0.35, damping=0.5, wet_level=0.08, dry_level=1.0, width=1.0),
                 Compressor(threshold_db=-14, ratio=3, attack_ms=8, release_ms=120), Limiter(threshold_db=-1.5)])
y = fx(mix, SR)
tail = int((END + 0.6) * SR)
fade = np.ones(y.shape[1]); fade[tail:] = 0
fade[int(END * SR) - int(1.2 * SR):tail] = np.linspace(1, 0, tail - (int(END * SR) - int(1.2 * SR)))
y *= fade[None, :]
y *= 10 ** (-1 / 20) / max(1e-9, float(np.max(np.abs(y))))
os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
sf.write(args.out, y.T, SR, subtype="PCM_24")
print(f"wrote {args.out}: {y.shape[1] / SR:.2f} s at {F['bpm']} BPM")
