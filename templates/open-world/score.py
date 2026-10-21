#!/usr/bin/env python3
"""The free score for an open-world film: an original West Coast G-funk bed, synthesised here from nothing
(no samples, no soundfont), on the film's bar grid.

  .venv/bin/python score.py --out score/score.wav

C minor at the film's BPM: an FM electric piano on Cm9 and Fm9, a gliding sub bass, a kick, a clap-snare and swung
16th hats, a high portamento sine lead (the genre's whine) for the ride, our own mission-passed sting, half-time drums
for the tail, and the bed dropping out for the logo. Sections come from film.json "at" (in bars).
"""
import argparse
import json
import os

import numpy as np
import soundfile as sf
from scipy.signal import butter, fftconvolve, sosfilt

HERE = os.path.dirname(os.path.abspath(__file__))
F = json.load(open(os.path.join(HERE, "film.json")))
SR = 48000
BAR = 240 / F["bpm"]
BEAT = BAR / 4
AT = F["at"]
END = F["bars"] * BAR + 1.5
N = int(END * SR)
rng = np.random.default_rng(7)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def lp(x, f, order=2):
    return sosfilt(butter(order, f, "low", fs=SR, output="sos"), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, "high", fs=SR, output="sos"), x)


def bp(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], "band", fs=SR, output="sos"), x)


def place(buf, x, t, gain=1.0):
    i = int(t * SR)
    if i >= len(buf) or i + len(x) <= 0:
        return
    j = min(len(buf), i + len(x))
    buf[max(i, 0):j] += gain * x[max(0, -i):j - i]


def env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)


def b(bars):                       # bars -> seconds
    return bars * BAR


# ---- instruments
def kick():
    n = int(0.5 * SR); t = np.arange(n) / SR
    f = 46 + 90 * np.exp(-t / 0.035)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.28)
    x[:200] += np.linspace(0.6, 0, 200) * rng.standard_normal(200)
    return x


def clap():
    n = int(0.35 * SR); t = np.arange(n) / SR
    noise = bp(rng.standard_normal(n), 900, 5200)
    e = np.zeros(n)
    for k, off in enumerate((0, 0.009, 0.018)):
        i = int(off * SR); e[i:] += np.exp(-(t[:n - i]) / (0.012 if k < 2 else 0.16))
    tone = np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.05) * 0.4
    return 0.7 * noise * e + tone


def hat(open_=False):
    n = int((0.25 if open_ else 0.06) * SR)
    return hp(rng.standard_normal(n), 7000) * env(n, 0.0005, 0.08 if open_ else 0.018)


def rhodes(notes, dur, vel=1.0):
    n = int(dur * SR); t = np.arange(n) / SR; x = np.zeros(n)
    for m in notes:
        f = midi(m); idx = 2.2 * np.exp(-t / 0.35) + 0.3
        x += np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * t)) * np.exp(-t / 1.6)
    trem = 1 + 0.18 * np.sin(2 * np.pi * 4.6 * t)
    return vel * x * trem * np.minimum(1, t / 0.004) * np.minimum(1, (dur - t) / 0.08).clip(0) / len(notes)


def glide_line(events, total, wave="bass"):
    """events: (t, midi, dur, glide): one monophonic line with portamento."""
    f = np.zeros(total); a = np.zeros(total)
    for k, (t0, m, d, g) in enumerate(events):
        i0, i1 = int(t0 * SR), min(total, int((t0 + d) * SR))
        if i0 >= total:
            continue
        prev = midi(events[k - 1][1]) if k and g else midi(m)
        tt = np.arange(i1 - i0) / SR
        f[i0:i1] = midi(m) + (prev - midi(m)) * np.exp(-tt / max(g, 1e-3)) if g else midi(m)
        rel = np.minimum(1, (d - tt) / 0.03).clip(0)
        a[i0:i1] = np.minimum(1, tt / 0.006) * rel
    ph = 2 * np.pi * np.cumsum(f) / SR
    if wave == "bass":
        x = np.sin(ph) + 0.25 * np.sin(2 * ph) + 0.12 * np.sign(np.sin(ph)) * 0.3
        return lp(x * a, 900)
    tt = np.arange(total) / SR                                     # the whine: vibrato that grows into each note
    vib = 1 + 0.012 * np.sin(2 * np.pi * 5.6 * tt)
    ph = 2 * np.pi * np.cumsum(f * vib) / SR
    return (np.sin(ph) + 0.18 * np.sin(2 * ph) + 0.06 * np.sin(3 * ph)) * a


def pad(notes, dur):
    n = int(dur * SR); t = np.arange(n) / SR; x = np.zeros(n)
    for m in notes:
        for det in (-0.07, 0.07):
            ph = (midi(m) * (1 + det / 100) * t) % 1
            x += 2 * ph - 1
    e = np.minimum(1, t / 0.5) * np.minimum(1, (dur - t) / 0.6).clip(0)
    return lp(x * e / len(notes), 1400)


def reverb(x, decay=1.6, wet=0.25):
    n = int(decay * SR); t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t / (decay / 5)); ir = lp(ir, 5000); ir /= np.abs(ir).sum() ** 0.5 * 4
    return x + wet * fftconvolve(x, ir)[:len(x)]


# ---- the arrangement
drums = np.zeros(N); bass_ev = []; keys = np.zeros(N); lead_ev = []; pads = np.zeros(N); fx = np.zeros(N)
CHORDS = [[48, 51, 55, 58, 62], [53, 56, 60, 63, 67]]               # Cm9, Fm9 (2-bar loop)
BASS = [[(0, 36, 0.45, 0), (0.75, 36, 0.2, 0), (1.5, 39, 0.4, 0.03), (2.5, 31, 0.4, 0), (3.25, 34, 0.3, 0.05), (3.75, 36, 0.22, 0.04)],
        [(0, 29, 0.45, 0), (0.75, 29, 0.2, 0), (1.5, 32, 0.4, 0.03), (2.5, 36, 0.4, 0), (3.25, 39, 0.3, 0.05), (3.75, 38, 0.22, 0.04)]]
LEAD = [(0, 79, 1.4, 0.09), (1.5, 82, 0.45, 0.05), (2.0, 84, 0.9, 0.06), (3.0, 82, 0.45, 0.05), (3.5, 79, 0.45, 0.05),
        (4.0, 77, 1.4, 0.08), (5.5, 75, 0.45, 0.05), (6.0, 77, 0.9, 0.05), (7.0, 79, 0.9, 0.06)]
drop = [(AT["m1_pass"] + 0.25, AT["m1_pass"] + 0.5), (AT["m2_pass"] + 0.25, AT["m2_pass"] + 0.5)]    # a beat of silence before each sting
end_bed = AT["close"] + 0.75


def silent(bar):
    return any(a <= bar < b2 for a, b2 in drop) or bar >= end_bed


for bar in range(int(F["bars"]) + 1):
    ch = bar % 2
    for beat in range(4):
        pos = bar + beat / 4
        if silent(pos):
            continue
        half = AT["tail"] <= pos < AT["m2_pass"]                     # the tail: half-time, sneaky
        lapse = AT["m2_title"] <= pos < AT["tail"]
        if pos >= 1 and lapse and beat == 0:
            place(drums, kick(), b(pos), 0.8)                       # the time-lapse keeps only the downbeat
        if pos >= 1 and not lapse:
            if beat == 0 or (beat == 2 and not half) or (beat == 1 and bar % 2 == 1 and not half):
                place(drums, kick(), b(pos), 1.0)
            if (beat in (1, 3) and not half) or (half and beat == 2):
                place(drums, clap(), b(pos), 0.55)
        if pos >= 0.5:
            for k in range(4):
                t16 = b(pos) + k * BEAT / 4 + (BEAT / 4 * 0.16 if k % 2 else 0)
                if lapse and k % 2:
                    continue
                place(drums, hat(open_=(k == 2 and beat == 3)), t16, 0.16 if k % 2 else 0.24)
    if silent(bar):
        continue
    keys_on = [(0, 1.4), (1.5, 0.45), (2.5, 1.2)]
    for off, d in keys_on:
        if not silent(bar + off / 4):
            place(keys, rhodes(CHORDS[ch], d * BEAT + 0.2), b(bar) + off * BEAT, 0.9)
    if bar >= 1 and not (AT["m2_title"] <= bar < AT["tail"]):
        for (o, m, d, g) in BASS[ch]:
            if not silent(bar + o / 4):
                bass_ev.append((b(bar) + o * BEAT, m, d * BEAT * 1.6, g))
    place(pads, pad([c + 12 for c in CHORDS[ch][:3]], BAR), b(bar), 0.5 if bar >= AT["m1_start"] else 0.25)
# the whine sings over the ride and over the close of the tail
for start in (AT["ride"], AT["ride"] + 2):
    for (o, m, d, g) in LEAD:
        tb = start + o / 4
        if tb < AT["m1_pass"] + 0.25:
            lead_ev.append((b(tb), m, d * BEAT, g))
for (o, m, d, g) in LEAD[:5]:
    lead_ev.append((b(AT["morning"] + o / 4), m - 12, d * BEAT, g))
# our own sting for a mission passed: a rising arpeggio on the whine, a synth-brass stab, a cymbal swell into it
STING = [60, 63, 67, 70, 72, 75, 79]
for sp in (AT["m1_pass"] + 0.5, AT["m2_pass"] + 0.5):
    for k, m in enumerate(STING):
        lead_ev.append((b(sp) + k * 0.075, m + 12, 0.07 if k < len(STING) - 1 else 1.3, 0.02))
    place(pads, pad([60, 63, 67, 70, 74], 1.6) * 2.2, b(sp), 1.0)
    n = int(0.9 * SR); swell = hp(rng.standard_normal(n), 4000) * np.linspace(0, 1, n) ** 2
    place(fx, swell * 0.35, b(sp) - 0.9)
# the time-lapse: a tape-speed swirl of noise; the close: one last held note under the logo
n = int(b(AT["tail"] - AT["m2_title"]) * SR); tt = np.arange(n) / SR
place(fx, bp(rng.standard_normal(n), 300, 3000) * np.sin(np.pi * tt / tt[-1]) * 0.12, b(AT["m2_title"]))
place(keys, rhodes([48, 55, 62, 67], 4.0, 1.2), b(end_bed), 1.0)
# vinyl dust under everything
crackle = np.zeros(N); idx = rng.integers(0, N, int(END * 18)); crackle[idx] = rng.uniform(-1, 1, len(idx))
crackle = hp(crackle, 1500) * 0.5 + hp(rng.standard_normal(N), 6000) * 0.004

bass = glide_line(sorted(bass_ev), N, "bass")
lead = glide_line(sorted(lead_ev), N, "lead")
mixL = 0.9 * drums + 0.75 * bass + reverb(0.55 * keys, 1.4, 0.3) + 0.12 * pads + reverb(0.22 * lead, 1.8, 0.35) + fx + crackle
mixR = 0.9 * drums + 0.75 * bass + reverb(0.55 * np.roll(keys, 240), 1.4, 0.3) + 0.12 * pads + reverb(0.22 * np.roll(lead, 360), 1.8, 0.35) + fx + np.roll(crackle, 5000)
st = np.stack([mixL, mixR], 1)
st /= np.abs(st).max() / 0.7

ap = argparse.ArgumentParser(); ap.add_argument("--out", default="score/score.wav")
out = ap.parse_args().out
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
sf.write(out, st.astype(np.float32), SR)
print(f"score: {out} ({END:.1f} s, {F['bpm']} BPM, C minor)")
