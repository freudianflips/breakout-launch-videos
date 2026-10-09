#!/usr/bin/env python3
"""The orchestral score for a kinetic film, written as MIDI on the film's bar grid and rendered free.

  .venv/bin/python score.py [--out score/score.wav]   (from this folder)

Needs fluidsynth and a General MIDI soundfont (apt install fluidsynth fluid-soundfont-gm, or SF2=...).
Same for every account: the beats are fixed in series.json "at".

  the intro          a held string chord and a soft timpani roll under "Pageview", cut dead before the first flood
  the beats          a bright pizzicato and glockenspiel drive; a hit on every colour change; the harmony walks per beat
  meeting booked     E major: brass, choir, cymbals, glockenspiel
  the personas       4 staccato stabs, one per chip
  the lockup         a pad and a celesta, then silence
Times follow the beats in film.json, so a longer or shorter list of beats still fits.
"""
import argparse
import json
import os
import subprocess

import mido
import numpy as np
import soundfile as sf
from pedalboard import Compressor, HighpassFilter, Pedalboard, Reverb

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("--out", default=os.path.join(HERE, "score", "score.wav"))
args = ap.parse_args()
F = json.load(open(os.path.join(HERE, "film.json")))
SF2 = os.environ.get("SF2", "/usr/share/sounds/sf2/FluidR3_GM.sf2")
SR, TPB = 48000, 480
CH = {"timp": (0, 47, 112), "bass": (1, 45, 104), "str": (2, 48, 92), "pizz": (3, 45, 100), "harp": (4, 46, 90),
      "horn": (5, 60, 100), "brass": (6, 61, 96), "vln": (7, 48, 100), "cel": (8, 8, 100), "trem": (10, 44, 92),
      "choir": (11, 52, 80), "bone": (12, 57, 90), "glock": (13, 9, 72)}
DRUM, BD, SN, CRASH, CRASH2 = 9, 36, 38, 49, 57
ev = []


def tk(bar):
    return int(round(bar * 4 * TPB))


def note(ch, pitch, at, dur, vel):
    c = CH[ch][0] if isinstance(ch, str) else ch
    ev.append((tk(at), 1, mido.Message("note_on", channel=c, note=int(pitch), velocity=int(max(1, min(127, vel))))))
    ev.append((max(tk(at) + 1, tk(at + dur)), 0, mido.Message("note_off", channel=c, note=int(pitch), velocity=0)))


def cc(ch, num, val, at):
    ev.append((tk(at), 0, mido.Message("control_change", channel=CH[ch][0], control=num, value=int(max(0, min(127, val))))))


def ramp(ch, a, b, v0, v1, n=24):
    for i in range(n + 1):
        cc(ch, 11, v0 + (v1 - v0) * i / n, a + (b - a) * i / n)


def steps(a, b, every):
    out, x = [], a
    while x < b - 1e-9:
        out.append(x)
        x += every
    return out


# chords: (from bar, root in octave 2, third, fifth)
EM, C, G, D, AM, B, E, A = (40, 43, 47), (36, 40, 43), (43, 47, 50), (38, 42, 45), (45, 48, 52), (47, 51, 54), (40, 44, 47), (45, 49, 52)
# the timeline in bars, as build.py computes it
_t = F["intro"]["bars"]
STARTS = []
for _ in F["beats"]:
    STARTS.append(_t)
    _t += F["beat_bars"]
booked = _t
personas = booked + F["booked"]["bars"]
lockup = personas + F["personas"]["bars"]
end = lockup + F["lockup"]["bars"]
L = F["beat_bars"]
CYCLE = [EM, C, G, D, AM, C, G, B]
PROG = [(0, EM)] + [(s, CYCLE[i % len(CYCLE)]) for i, s in enumerate(STARTS)] + [(booked, E), (personas, A), (personas + 0.75, B), (lockup, E)]


def chord(bar):
    c = PROG[0][1]
    for b, ch in PROG:
        if bar >= b - 1e-9:
            c = ch
    return c


for name, (c, prog, vol) in CH.items():
    ev.append((0, 0, mido.Message("program_change", channel=c, program=prog)))
    cc(name, 7, vol, 0)
    cc(name, 11, 127, 0)
ev.append((0, 0, mido.Message("program_change", channel=DRUM, program=48)))

for name, (c, prog, vol) in CH.items():
    ev.append((0, 0, mido.Message("program_change", channel=c, program=prog)))
    cc(name, 7, vol, 0)
    cc(name, 11, 127, 0)
ev.append((0, 0, mido.Message("program_change", channel=DRUM, program=48)))
def hit(at, chord_notes, big=True):
    """A trailer hit on a hard cut: cymbal, bass drum, timpani, low brass and the strings."""
    r = chord_notes[0]
    note(DRUM, CRASH, at, 1, 112 if big else 90)
    note(DRUM, BD, at, 0.2, 120 if big else 100)
    note("timp", r if r >= 40 else r + 12, at, 0.5, 124 if big else 104)
    for p in (r - 12 if r - 12 >= 28 else r, r):
        note("bone", p, at, 0.45, 104 if big else 88)
    for p in (r, r + 7, r + 12, r + 16 if chord_notes[1] - r == 4 else r + 15):
        note("brass", p, at, 0.45, 104 if big else 88)


cut = booked - 0.25
def ostinato(a, b, vel=86, stabs=False, brass=False):
    for t in steps(a, b, 1 / 8):
        r, th, fi = chord(t)
        k = int(round((t % 1) * 8))
        note("pizz", [r + 24, fi + 24, r + 36, fi + 24][(k // 2) % 4] if k % 2 else r + 12, t, 0.08, vel if k % 2 else vel - 10)
    for t in steps(a, b, 1 / 4):
        r, th, fi = chord(t)
        q = int(round((t % 1) * 4))
        note("timp", r if r >= 40 else r + 12, t, 0.15, vel + 8 if q == 0 else vel - 6)
        note("bass", r - 12 if r - 12 >= 28 else r, t, 0.12, vel + 6)
        if stabs and q in (1, 3):
            for p in (r + 12, th + 12, fi + 12, r + 24):
                note("str", p, t, 0.08, vel + 14)
            note(DRUM, SN, t, 0.08, 50)
            if brass:
                for p in (th + 12, fi + 12, r + 24):
                    note("brass", p, t, 0.07, vel)
    for t in steps(a, b, 0.5):
        r, th, fi = chord(t)
        for p in (r + 24, fi + 24, th + 36):
            note("str", p, t, min(0.49, b - t - 0.01), 58)



# ---- intro: a held chord, a rising timpani roll, cut dead a beat before the first flood
first = STARTS[0]
for p in (40, 47, 52, 55, 59):
    note("trem", p, 0, first - 0.25, 80)
ramp("trem", 0, first - 0.25, 40, 120)
for i, t in enumerate(steps(first - 0.75, first - 0.25, 1 / 32)):
    note("timp", 47, t, 1 / 32, 60 + 60 * i / 16)
for i, p in enumerate((76, 79, 83, 88)):
    note("cel", p, 0.25 + i * 0.125, 0.12, 70)

# ---- the beats: a hit on every colour change, a glockenspiel figure, the drive underneath
for i, s in enumerate(STARTS):
    hit(s, chord(s), i % 4 == 0)
    r, th, fi = chord(s)
    for j, p in enumerate((r + 36, fi + 36, th + 48, r + 48)):
        note("glock", p, s + 0.4 + j / 16, 0.15, 74)
ostinato(first, cut, 92, stabs=True)
for p, at, d in [(71, 0, 0.375), (72, 0.375, 0.125), (74, 0.5, 0.5), (76, 1.0, 0.375), (74, 1.375, 0.125), (79, 1.5, 0.5), (78, 2.0, 0.5)]:
    for rep in range(0, int((cut - first) // 2.5)):
        a = first + rep * 2.5 + 2.5 + at
        if a + d < cut:
            note("vln", p, a, d * 0.98, 96)
for i, t in enumerate(steps(cut - 0.5, cut, 1 / 32)):
    note("timp", 47, t, 1 / 32, 70 + 50 * i / 16)

# ---- meeting booked: E major
note(DRUM, CRASH, booked, 1.5, 120)
note(DRUM, CRASH2, booked, 1.5, 92)
for k in (0, 0.25, 0.5):
    note("timp", 40, booked + k, 0.25, 118)
    note(DRUM, BD, booked + k, 0.2, 110)
for p in (40, 52, 56, 59, 64):
    note("brass", p, booked, 1.4, 112)
for p in (28, 40):
    note("bone", p, booked, 1.4, 100)
for p in (64, 68, 71, 76):
    note("choir", p, booked, 1.45, 98)
for p in (40, 52, 59, 64, 68, 71, 76, 80):
    note("str", p, booked, 1.45, 102)
for i, p in enumerate((76, 80, 83, 88, 92, 95)):
    note("glock", p, booked + 0.25 + i / 16, 0.2, 86)

# ---- the personas: a staccato stab per chip
for j in range(len(F["personas"]["words"])):
    at = personas + 0.05 + j * 0.25
    r, th, fi = chord(at)
    for p in (r + 12, th + 12, fi + 12, r + 24):
        note("str", p, at, 0.1, 108)
        note("brass", p, at, 0.08, 92)
    note("timp", r if r >= 40 else r + 12, at, 0.15, 104)

# ---- lockup: a pad, a celesta, silence
for p in (40, 52, 59, 64, 68, 71):
    note("str", p, lockup, end - lockup - 0.4, 74)
ramp("str", lockup, end - 0.4, 92, 20)
for i, p in enumerate((76, 80, 83, 88, 83, 80, 76, 88)):
    note("cel", p, lockup + 0.25 + i / 8, 0.12, 72 - i * 3)
note("harp", 64, lockup, 1.0, 70)

# ---- write, render, hall, the beat of silence
ev.sort(key=lambda e: (e[0], e[1]))
mid = mido.MidiFile(ticks_per_beat=TPB)
tr = mido.MidiTrack()
mid.tracks.append(tr)
tr.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(F["bpm"]), time=0))
last = 0
for t, _, m in ev:
    tr.append(m.copy(time=t - last))
    last = t
tr.append(mido.MetaMessage("end_of_track", time=tk(1.0)))
midi_path = os.path.splitext(args.out)[0] + ".mid"
dry = os.path.splitext(args.out)[0] + "-dry.wav"
os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
mid.save(midi_path)
subprocess.run(["fluidsynth", "-ni", "-q", "-g", "0.6", "-r", str(SR), "-R", "0", "-C", "0", "-F", dry, SF2, midi_path], check=True)
x, _ = sf.read(dry, dtype="float32")
os.remove(dry)
BAR = 240 / F["bpm"]
N = int((end * BAR + 1.5) * SR)
x = np.pad(x, ((0, max(0, N - len(x))), (0, 0)))[:N]
x = Pedalboard([HighpassFilter(30), Reverb(room_size=0.78, damping=0.45, wet_level=0.2, dry_level=0.85, width=1.0),
                Compressor(threshold_db=-16, ratio=2.5, attack_ms=12, release_ms=160)])(x.T, SR)
g = np.ones(x.shape[1])
for a, b in ((first - 0.25, first), (cut, booked)):          # cut the hall dead too
    i0, i1 = int((a * BAR + 0.01) * SR), int(b * BAR * SR)
    g[i0:i1] = 10 ** (-38 / 20)
    g[i0 - 240:i0] = np.linspace(1, g[i0], 240)
x *= g
x *= 10 ** (-1 / 20) / max(1e-9, float(np.max(np.abs(x))))
sf.write(args.out, x.T, SR, subtype="PCM_24")
print(f"wrote {args.out} and {midi_path}: {N / SR:.2f} s at {F['bpm']} BPM")
