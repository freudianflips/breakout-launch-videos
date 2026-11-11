#!/usr/bin/env python3
"""The score for the Signals launch: upbeat swing on the film's bar grid, rendered free.

  .venv/bin/python score.py [--out score/score.wav]   (from this folder)

Needs fluidsynth and a General MIDI soundfont (apt install fluidsynth fluid-soundfont-gm, or SF2=...).
The dot-matrix band (piano, walking bass, jazz kit, vibraphone, trumpet, alto sax, trombone), cued from film.json "at":
a pickup and a hit as the camera lands on the visitor, the band in when Breakout starts listening, a vibraphone figure
as each signal lands (rising one by one), a hit on "Act today", lighter comping under the typing, a horn line for
"Sent", and the button under the close.
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
A = F["at"]
SF2 = os.environ.get("SF2", "/usr/share/sounds/sf2/FluidR3_GM.sf2")
SR, TPB = 48000, 480
CH = {"piano": (0, 0, 100), "bass": (1, 32, 120), "vibes": (2, 11, 96), "tpt": (3, 56, 92), "alto": (4, 65, 92),
      "bone": (5, 57, 88), "chip": (6, 80, 54)}
DRUM = 9
KICK, SNARE, HAT, RIDE, CRASH, TOM_H, TOM_M, TOM_L = 36, 38, 44, 51, 49, 50, 47, 45
ev = []
BEAT = 0.25
SW = 2 / 3                                    # swing: the off-beat eighth lands two thirds into the beat


def tk(bar):
    return int(round(bar * 4 * TPB))


def note(ch, pitch, at, dur, vel):
    c = CH[ch][0] if isinstance(ch, str) else ch
    ev.append((tk(at), 1, mido.Message("note_on", channel=c, note=int(pitch), velocity=int(max(1, min(127, vel))))))
    ev.append((max(tk(at) + 1, tk(at + dur)), 0, mido.Message("note_off", channel=c, note=int(pitch), velocity=0)))


def cc(ch, num, val, at):
    ev.append((tk(at), 0, mido.Message("control_change", channel=CH[ch][0], control=num, value=int(max(0, min(127, val))))))


def off(x, eighth):
    """The bar position of a swung eighth (0..7) in the bar starting at x."""
    return x + (eighth // 2) * BEAT + (SW * BEAT if eighth % 2 else 0)


# chords: root (octave 2) and a voicing in semitones above it
SIX, DOM, MIN, DOM9 = (4, 7, 9, 14), (4, 10, 14, 21), (3, 7, 10, 14), (4, 10, 14, 19)
F_, D_, G_, C_, BB, A_ = 41, 38, 43, 36, 46, 45
TURN = [(F_, SIX), (D_, DOM), (G_, MIN), (C_, DOM9)]
BLUES = [(F_, DOM), (BB, DOM), (F_, DOM), (C_, DOM9), (BB, DOM), (F_, SIX)]
PROG = []
for i, x in enumerate(range(0, int(A["end"]) + 1)):
    PROG.append((x, TURN[i % 4]))
LK = A["close"]
PROG = [p for p in PROG if p[0] < LK] + [(LK, (BB, SIX)), (LK + 0.75, (C_, DOM9)), (LK + 1.25, (F_, SIX))]


def chord(bar):
    c = PROG[0][1]
    for b, ch in PROG:
        if bar >= b - 1e-9:
            c = ch
    return c


def comp(a, b, vel=82):
    """Piano: the Charleston (1 and the and-of-2), voicings in the middle register."""
    x = a
    while x < b - 1e-9:
        r, v = chord(x)
        for e, d in ((0, 0.08), (3, 0.06)):
            at = off(x, e)
            if at < b:
                for s in v:
                    note("piano", r + 12 + s, at, d, vel - (6 if e else 0))
        x += 0.5 if b - x >= 0.5 and chord(x + 0.5) != chord(x) else 1


def walk(a, b, vel=110):
    x = a
    while x < b - 1e-9:
        r, v = chord(x)
        nr, _ = chord(x + 1)
        line = [r, r + v[0], r + 7, nr + (1 if nr <= r else -1)]
        for i, p in enumerate(line):
            at = x + i * BEAT
            if at < b:
                note("bass", p if p >= 28 else p + 12, at, BEAT * 0.85, vel - (6 if i % 2 else 0))
        x += 1


def drums(a, b, vel=80, snare=True):
    x, k = a, 0
    while x < b - 1e-9:
        for i in range(4):
            at = x + i * BEAT
            if at >= b:
                break
            note(DRUM, RIDE, at, 0.1, vel + (8 if i % 2 else 0))
            if i % 2:
                note(DRUM, RIDE, at + SW * BEAT, 0.08, vel - 6)
                note(DRUM, HAT, at, 0.05, vel)
            note(DRUM, KICK, at, 0.05, vel - 34)
        if snare:                                               # comping on the offbeats, a different pattern each bar
            for e in [(3, 7), (5,), (1, 6), (3, 4, 7)][k % 4]:
                if off(x, e) < b:
                    note(DRUM, SNARE, off(x, e), 0.05, vel - 16)
        x += 1
        k += 1


def fill(at, vel=96):
    for i, p in enumerate((SNARE, SNARE, TOM_H, TOM_M, TOM_L, SNARE)):
        note(DRUM, p, at + i * BEAT / 6, 0.05, vel + i * 4)


def stab(at, vel=104, d=0.1, horns=True):
    r, v = chord(at)
    for s in v:
        note("piano", r + 12 + s, at, d, vel)
    if horns:
        note("tpt", r + 24 + v[3], at, d, vel)
        note("alto", r + 24 + v[1], at, d, vel - 6)
        note("bone", r + 12 + v[0], at, d, vel - 6)


for name, (c, prog, vol) in CH.items():
    ev.append((0, 0, mido.Message("program_change", channel=c, program=prog)))
    cc(name, 7, vol, 0)
    cc(name, 11, 127, 0)
    cc(name, 91, 50, 0)
ev.append((0, 0, mido.Message("program_change", channel=DRUM, program=32)))      # the jazz kit

end = A["end"]
BAR = 240 / F["bpm"]

# ---- the visit: a pickup, piano and bass; the band comes in when Breakout starts listening
fill(0.0, 84)
walk(0.25, A["close"], 104)
comp(0.25, A["close"], 74)
drums(0.25, A["listen"], 66, snare=False)
stab(A["land"], 104, 0.1, horns=False)
note(DRUM, CRASH, A["land"], 0.6, 96)
for p, ch in ((77, "tpt"), (72, "alto"), (65, "bone")):
    note(ch, p, A["listen"] - 0.25, 0.25, 84)
fill(A["listen"] - 0.25, 96)
stab(A["listen"], 108, 0.15)
note(DRUM, CRASH, A["listen"], 1, 104)
drums(A["listen"], A["agent"], 82)

# ---- the intel: a loading shimmer on the ride, then a vibraphone figure as each signal lands
for k, c in enumerate(A["signals"]):
    land = c + A["load"]
    r, v = chord(land)
    for i, s_ in enumerate((v[0], v[1], v[3])):
        note("vibes", r + 36 + s_ + (12 if k >= 3 else 0), land + i / 32, 0.25, 96 + 2 * k)
    note(DRUM, SNARE, land, 0.05, 96)
stab(A["act"], 118, 0.25)
note(DRUM, CRASH, A["act"], 1, 116)
note(DRUM, KICK, A["act"], 0.1, 118)

# ---- the agent and the email: lighter under the typing, horns for the reply and for Sent
drums(A["agent"], A["sent"], 70, snare=False)
for i, p in enumerate((84, 88, 91)):
    note("vibes", p, A["agent"] + i / 24, 0.3, 92)
for i, p in enumerate((76, 79, 84)):
    note("alto", p, A["reply"] + i / 16, 0.1, 96)
stab(A["email"], 104, 0.1)
for i, p in enumerate((72, 77, 81, 84, 89)):
    note("tpt", p, A["sent"] + i / 24, 0.1 if i < 4 else 0.4, 108)
note(DRUM, CRASH, A["sent"], 1, 112)
drums(A["sent"], A["close"], 84)
riff = [(0, 72, 0.12), (1, 74, 0.06), (2, 77, 0.12), (3, 81, 0.06), (4, 84, 0.2), (6, 82, 0.08), (7, 81, 0.12)]
for e, p, d in riff[:4]:
    at = off(A["sent"] + 0.25, e)
    note("tpt", p, at, d, 104)
    note("alto", p - 4, at, d, 96)
    note("bone", p - 12, at, d, 92)
fill(A["close"] - 0.25, 106)

# ---- the lockup: B-flat, C, F, a vibraphone run, the button
lk = A["close"]
stab(lk, 116, 0.3)
note(DRUM, CRASH, lk, 1.5, 116)
walk(lk, lk + 1.25, 104)
drums(lk, lk + 1.25, 76)
comp(lk, lk + 1.25, 78)
for i, p in enumerate((81, 84, 88, 91, 93, 96, 100, 105)):
    note("vibes", p, lk + 1.25 + i / 24, 0.6, 92 - i * 3)
for s_ in (0, 4, 7, 9, 14):
    note("piano", F_ + 12 + s_, lk + 1.25, 0.7, 92)
note("bass", F_, lk + 1.25, 0.7, 110)
button = end - 0.375
stab(button, 116, 0.1)
note("bass", F_ - 12, button, 0.1, 124)
note(DRUM, KICK, button, 0.1, 120)
note(DRUM, CRASH, button, 0.6, 110)

# ---- write, render, room, the cut
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
x = Pedalboard([HighpassFilter(35), Reverb(room_size=0.45, damping=0.5, wet_level=0.14, dry_level=0.9, width=1.0),
                Compressor(threshold_db=-18, ratio=2.2, attack_ms=15, release_ms=180)])(x.T, SR)
x *= 10 ** (-1 / 20) / max(1e-9, float(np.max(np.abs(x))))
sf.write(args.out, x.T, SR, subtype="PCM_24")
print(f"wrote {args.out} and {midi_path}: {N / SR:.2f} s at {F['bpm']} BPM")
