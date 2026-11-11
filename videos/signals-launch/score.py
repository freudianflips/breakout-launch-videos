#!/usr/bin/env python3
"""The score for the Signals launch: upbeat swing, written as MIDI on the film's bar grid and rendered free.

  .venv/bin/python score.py [--out score/score.wav]   (from this folder)

Needs fluidsynth and a General MIDI soundfont (apt install fluidsynth fluid-soundfont-gm, or SF2=...).
The dot-matrix band (piano, walking bass, jazz kit, vibraphone, trumpet, alto sax, trombone), cued from film.json "at":

  questions   a drum pickup, then a band stab on each question while the bass and ride keep moving
  turn        the hit, and the full band swings
  two         down to piano, bass and ride ("good...")
  sort        the horns climb back in; a hit when the second visit lights up
  library     a vibraphone note per tile
  hot         a stab per flaring visit
  rep, agent  a trumpet fanfare when the hook lands; vibraphone and alto trade; a run for the comet
  run, same   each stream brings in a part; the hit on "the same account"
  close       the shockwave hit, a vibraphone run under the wordmark, B-flat, C, F and a button
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
PROG = [(x, TURN[i % 4]) for i, x in enumerate(A["q"])]
x, i = A["turn"], 0
while x < A["close"] - 1e-9:
    PROG.append((x, [(F_, SIX), (D_, DOM), (G_, MIN), (C_, DOM9)][i % 4] if not (A["two"] <= x < A["sort"]) else [(BB, SIX), (G_, MIN), (C_, DOM9), (F_, SIX)][i % 4]))
    x += 1
    i += 1
PROG += [(A["same"], (F_, SIX)), (A["close"], (BB, SIX)), (A["close"] + 1, (C_, DOM9)), (A["close"] + 2, (F_, SIX))]
PROG.sort()


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
SEC = 1 / BAR                                                   # one second, in bars
q = A["q"]

# ---- the questions: a pickup, then a stab per question over bass and ride
fill(q[0] - 0.25, 92)
for p, ch in ((77, "tpt"), (72, "alto"), (65, "bone")):
    note(ch, p, 0.05, 0.4, 76)
walk(q[0], A["two"], 104)
drums(q[0], A["turn"], 70, snare=False)
for k, at in enumerate(q):
    stab(at, 100 + 4 * k, 0.1)
    note(DRUM, CRASH if k == 0 else SNARE, at, 0.3, 96)
    r, v = chord(at)
    for i, s_ in enumerate((v[0], v[1], v[3])):
        note("vibes", r + 36 + s_, at + 0.25 + i / 24, 0.2, 90)

# ---- the turn: the hit, full swing
tn = A["turn"] + 0.3 * SEC
fill(A["turn"] - 0.25, 100)
stab(tn, 116, 0.25)
note(DRUM, CRASH, tn, 1, 116)
note(DRUM, KICK, tn, 0.1, 118)
drums(A["turn"], A["two"], 84)
comp(A["turn"], A["two"], 82)

# ---- two visits: down to the trio, then the horns climb back
walk(A["two"], A["close"], 108)
drums(A["two"], A["sort"], 66, snare=False)
comp(A["two"], A["sort"], 72)
for i, p in enumerate((65, 69, 72, 77, 81, 84)):
    note("tpt" if i % 2 else "alto", p, A["sort"] + i / 8, 0.12, 86 + i * 4)
lit = A["sort"] + 2.5 * 0.25
stab(lit, 118, 0.3)
note(DRUM, CRASH, lit, 1, 112)
drums(A["sort"], A["close"], 84)
comp(A["sort"], A["close"], 80)

# ---- the library: a vibraphone note per tile
for i in range(10):
    r, v = chord(A["lib"] + i / 16)
    note("vibes", r + 36 + [0, 4, 7, 9, 12][i % 5] + (12 if i >= 5 else 0), A["lib"] + i / 16, 0.25, 96)

# ---- hot: a stab per flare
for k in range(3):
    stab(A["hot"] + (1 + k) * 0.25, 104 + 4 * k, 0.08)

# ---- the rep and the agent
hook = A["rep"] + 0.25 + 0.4 * SEC
for i, p in enumerate((72, 77, 81, 84)):
    note("tpt", p, hook + i / 24, 0.1 if i < 3 else 0.3, 106)
for b_, ch, ps in ((1, "vibes", (84, 88, 91)), (2, "alto", (76, 79)), (3, "vibes", (86, 89, 93))):
    at = A["agent"] + b_ * 0.25
    for i, p in enumerate(ps):
        note(ch, p, at + i / 24, 0.15, 100)
for i, p in enumerate((96, 93, 89, 86, 84, 81, 77, 81, 84, 89)):
    note("vibes", p, A["agent"] + 4.5 * 0.25 + i / 24, 0.15, 92)

# ---- what you already run: a part per stream, then the hit
for k in range(3):
    at = A["run"] + k * 1.5 * 0.25
    for i, p in enumerate([(65, 69, 72), (72, 77, 81), (77, 81, 84)][k]):
        note(["piano", "alto", "tpt"][k], p, at + i / 16, 0.1, 96 + 4 * k)
stab(A["same"], 118, 0.3)
note(DRUM, CRASH, A["same"], 1, 114)
riff = [(0, 72, 0.12), (1, 74, 0.06), (2, 77, 0.12), (3, 81, 0.06), (4, 84, 0.2), (6, 82, 0.08), (7, 81, 0.12)]
for e, p, d in riff:
    at = off(A["same"] + 0.25, e)
    if at < A["close"] - 0.05:
        note("tpt", p, at, d, 106)
        note("alto", p - 4, at, d, 98)
        note("bone", p - 12, at, d, 94)
fill(A["close"] - 0.25, 108)

# ---- close: the shockwave hit, the wordmark, B-flat, C, F, the button
sh = A["close"] + 0.2 * SEC
stab(sh, 120, 0.4)
note(DRUM, CRASH, sh, 2, 120)
note(DRUM, KICK, sh, 0.2, 120)
note("bass", BB - 12, sh, 0.9, 124)
for i, p in enumerate((77, 81, 84, 89, 93, 96, 101, 105)):
    note("vibes", p, A["close"] + 0.5 + i / 24, 0.4, 94 - i * 3)
walk(A["close"] + 1, A["close"] + 2, 104)
drums(A["close"] + 0.5, A["close"] + 2, 76)
comp(A["close"] + 0.5, A["close"] + 2, 78)
for s_ in (0, 4, 7, 9, 14):
    note("piano", F_ + 12 + s_, A["close"] + 2, 0.9, 92)
note("bass", F_, A["close"] + 2, 0.9, 110)
for p, ch in ((84, "tpt"), (81, "alto"), (72, "bone")):
    note(ch, p, A["close"] + 2, 0.8, 92)
note(DRUM, CRASH, A["close"] + 2, 1.0, 96)
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
