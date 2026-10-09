#!/usr/bin/env python3
"""The orchestral score for a cartoon story, written as MIDI on the film's bar grid and rendered free.

  .venv/bin/python score.py [--out score/score.wav]   (from this folder)

Needs fluidsynth and a General MIDI soundfont (apt install fluidsynth fluid-soundfont-gm, or SF2=...).
Same for every account: the beats are fixed in series.json "at".

  the site          curious pizzicato and celesta; a sparkle and Breakout's 4-note theme when she is seen
  the rep           a hit and string stabs when the alert lands
  she leaves        the music thins and stops for a beat
  homework, follow  a low, patient pulse, then the theme again
  the long horizon  a clock-like ostinato, building; a horn lift on every signal
  they're back      a hit; then a rise into the booking
  meeting booked    E major: brass, choir, cymbals, glockenspiel; then a celebration and a quiet close
Times follow film.json "at".
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
AT = F["at"]
end = F["bars"]
THEME = [76, 79, 83, 88]          # Breakout's theme: E G B E
PROG = [(0, EM), (1, C), (2, G), (AT["seen"], EM), (AT["chat"], C), (AT["chat"] + 1, G), (AT["chat"] + 2, D), (AT["rep"], AM), (AT["repjoin"], C),
        (AT["leave"], AM), (AT["research"], EM), (AT["research"] + 1.25, C), (AT["follow"], G), (AT["follow"] + 1.25, D)]
seg = (AT["back"] - AT["lapse"]) / 3
PROG += [(AT["lapse"] + k * seg, c) for k, c in enumerate((EM, C, D))] + [(AT["back"], AM), (AT["back"] + 1.25, B), (AT["yes"], C), (AT["yes"] + 0.75, D),
         (AT["booked"], E), (AT["close"], A), (AT["close"] + 0.5, B), (AT["close"] + 1, E)]


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





def theme(at, vel=78):
    for i, p in enumerate(THEME):
        note("cel", p, at + i / 8, 0.15, vel)
        note("glock", p + 12, at + i / 8, 0.12, vel - 20)


# ---- the site: curious and light
for t in steps(0, AT["leave"], 1 / 4):
    note("pizz", chord(t)[0] + 12, t, 0.1, 60 if t < AT["chat"] else 70)
for t in steps(0, AT["seen"], 1 / 8):
    if int(round((t % 1) * 8)) % 2 == 1:
        r, th, fi = chord(t)
        note("cel", [r + 36, fi + 36, th + 36, fi + 36][int(round((t % 1) * 8)) // 2], t, 0.1, 58)
theme(AT["seen"] + 0.1, 86)
for i, p in enumerate((83, 88, 91, 95, 100)):
    note("glock", p, AT["seen"] + 0.4 + i / 16, 0.12, 70)
ostinato(AT["chat"], AT["rep"], 78)
hit(AT["rep"], chord(AT["rep"]), False)
ostinato(AT["rep"], AT["leave"], 86, stabs=True)
# she leaves: a falling figure, then nothing
for i, p in enumerate((76, 72, 69, 64)):
    note("pizz", p, AT["leave"] + i / 8, 0.12, 80 - i * 6)

# ---- homework and the follow-up: patient, then the theme
for t in steps(AT["research"], AT["lapse"], 1 / 4):
    r = chord(t)[0]
    note("bass", r, t, 0.12, 70)
    if int(round((t % 1) * 4)) == 0:
        note("timp", r if r >= 40 else r + 12, t, 0.15, 64)
for b in steps(AT["research"], AT["lapse"], 0.5):
    r, th, fi = chord(b)
    for p in (r + 24, fi + 24, th + 36):
        note("str", p, b, 0.49, 52)
theme(AT["follow"] + 0.2, 80)
theme(AT["follow"] + 1.1, 80)

# ---- the long horizon: a clock-like ostinato that builds, a horn lift on every signal
for k in range(3):
    a = AT["lapse"] + k * seg
    ostinato(a, a + seg, 80 + k * 8, stabs=k > 0, brass=k == 2)
    for p, at, d in [(64, 0, 0.25), (67, 0.25, 0.25), (71, 0.5, 0.5)]:
        note("horn", p + 2 * k, a + 0.3 + at, d, 96 + k * 4)
    theme(a + 0.7, 72)
for t in steps(AT["lapse"], AT["back"], 1 / 4):
    note(DRUM, 76 if int(round((t % 1) * 4)) % 2 else 77, t, 0.05, 70)      # woodblocks: the clock

# ---- they're back, then the rise into the booking
hit(AT["back"], chord(AT["back"]))
ostinato(AT["back"], AT["booked"] - 0.25, 96, stabs=True, brass=True)
for i, t in enumerate(steps(AT["booked"] - 0.75, AT["booked"] - 0.25, 1 / 32)):
    note("timp", 47, t, 1 / 32, 70 + 50 * i / 16)
booked = AT["booked"]
note(DRUM, CRASH, booked, 1.5, 120)
note(DRUM, CRASH2, booked, 1.5, 92)
for k in (0, 0.25, 0.5):
    note("timp", 40, booked + k, 0.25, 118)
    note(DRUM, BD, booked + k, 0.2, 110)
for p in (40, 52, 56, 59, 64):
    note("brass", p, booked, 1.2, 112)
for p in (28, 40):
    note("bone", p, booked, 1.2, 100)
for p in (64, 68, 71, 76):
    note("choir", p, booked, 1.2, 98)
for p in (40, 52, 59, 64, 68, 71, 76, 80):
    note("str", p, booked, 1.2, 102)
theme(booked + 0.3, 92)

# ---- the celebration, then quiet
close = AT["close"]
ostinato(close, close + 1, 98, stabs=True, brass=True)
for p, at, d in [(64, 0, 0.25), (68, 0.25, 0.25), (71, 0.5, 0.25), (76, 0.75, 0.5)]:
    note("horn", p, close + at, d, 108)
    note("brass", p, close + at, d, 94)
note(DRUM, CRASH, close + 1, 1, 96)
for p in (40, 52, 59, 64, 68, 71):
    note("str", p, close + 1, end - close - 1.4, 74)
ramp("str", close + 1, end - 0.4, 92, 20)
theme(close + 1.25, 70)
note("harp", 64, close + 1, 1.0, 70)
cut = booked - 0.25

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
for a, b in ((AT["leave"] + 0.5, AT["research"]), (cut, booked)):          # cut the hall dead too
    i0, i1 = int((a * BAR + 0.01) * SR), int(b * BAR * SR)
    g[i0:i1] = 10 ** (-38 / 20)
    g[i0 - 240:i0] = np.linspace(1, g[i0], 240)
x *= g
x *= 10 ** (-1 / 20) / max(1e-9, float(np.max(np.abs(x))))
sf.write(args.out, x.T, SR, subtype="PCM_24")
print(f"wrote {args.out} and {midi_path}: {N / SR:.2f} s at {F['bpm']} BPM")
