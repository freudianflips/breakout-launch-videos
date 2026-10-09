#!/usr/bin/env python3
"""The jazz score for a dot-matrix film, written as swung MIDI on the film's bar grid and rendered free.

  .venv/bin/python score.py [--out score/score.wav]   (from this folder)

Needs fluidsynth and a General MIDI soundfont (apt install fluidsynth fluid-soundfont-gm, or SF2=...).
A small late-night band: Rhodes, warm pad, upright bass, brushes, vibraphone, muted trumpet, a celesta and,
for the easter egg, a square-wave lead. The picture's events are its cues:

  dark        a Rhodes Dm9 under a pad, nothing else
  seen        the ride comes in; a vibraphone glint when the visitor turns pink
  engage      walking bass and brushes; vibraphone for Breakout's ripples, muted trumpet for the visitor's
  rep         a celesta ping when the line hits the corner; a 3-note chord on the triad ripple
  gone        the band cuts dead (the hall too)
  follow      the bass alone comes back; a vibraphone run per comet
  game        bass and brushes keep the long game; an 8-bit blip per signal eaten, rising
  back        the band returns and builds; the trumpet leads
  booked      the hit: crash, low F, the full chord
  close       B-flat to F, Rhodes and vibraphone, ringing out
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
CH = {"rhodes": (0, 4, 96), "bass": (1, 32, 118), "vibes": (2, 11, 92), "tpt": (3, 59, 84), "pad": (4, 89, 62),
      "cel": (5, 8, 86), "chip": (6, 80, 56)}
DRUM = 9
KICK, TAP, SWIRL, HAT, RIDE, BELL, CRASH = 36, 38, 40, 44, 51, 53, 49
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


def ramp(ch, a, b, v0, v1, n=24):
    for i in range(n + 1):
        cc(ch, 11, v0 + (v1 - v0) * i / n, a + (b - a) * i / n)


# chords as (root in octave 2, voicing above it in semitones): minor 9, dominant 13, major 9
M9, D13, MA9 = (3, 7, 10, 14), (4, 10, 14, 21), (4, 7, 11, 14)
D, G, C, FF, BB, EB = 38, 43, 36, 41, 46, 39
PROG = [(0, (D, M9)), (A["engage"], (G, M9)), (A["engage"] + 1, (C, D13)), (A["rep"], (FF, MA9)),
        (A["follow"], (D, M9)), (A["game"] + 2, (G, M9)), (A["game"] + 3, (EB, MA9)),
        (A["back"], (G, M9)), (A["back"] + 0.5, (C, D13)), (A["booked"], (FF, MA9)), (A["close"], (BB, MA9)), (A["close"] + 1, (FF, MA9))]


def chord(bar):
    c = PROG[0][1]
    for b, ch in PROG:
        if bar >= b - 1e-9:
            c = ch
    return c


def comp(a, b, vel=70):
    """Rhodes comping: a voicing on the 'and' of 2 and the 4, swung, short."""
    x = a
    while x < b - 1e-9:
        r, v = chord(x)
        for off, d in ((1 + SW, 0.18), (3, 0.12)):
            at = x + off * BEAT
            if at < b:
                for s in v:
                    note("rhodes", r + 12 + s, at, d, vel)
        x += 1


def walk(a, b, vel=96):
    """A walking bass in quarter notes: root, a chord tone, a passing tone, an approach to the next root."""
    x = a
    while x < b - 1e-9:
        r, v = chord(x)
        nr, _ = chord(x + 1)
        line = [r, r + v[1] if v[1] < 12 else r + 7, r + (v[0] if v[0] < 5 else 3) + 7, nr + (1 if nr < r + 6 else -1)]
        for i, p in enumerate(line):
            at = x + i * BEAT
            if at < b:
                note("bass", p if p >= 28 else p + 12, at, BEAT * 0.9, vel - (8 if i % 2 else 0))
        x += 1


def brushes(a, b, vel=60, ride=True):
    x = a
    while x < b - 1e-9:
        for i in range(4):
            at = x + i * BEAT
            if at >= b:
                break
            if ride:
                note(DRUM, RIDE, at, 0.1, vel + (6 if i % 2 else 0))
                if i % 2:
                    note(DRUM, RIDE, at + SW * BEAT, 0.08, vel - 14)
            note(DRUM, SWIRL, at, BEAT, vel - 22)
            if i % 2:
                note(DRUM, HAT, at, 0.05, vel - 10)
                note(DRUM, TAP, at, 0.05, vel - 16)
        x += 1


def hold(a, b, vel=56, ch="rhodes", octave=12):
    x = a
    while x < b - 1e-9:
        r, v = chord(x)
        nxt = min([p for p, _ in PROG if p > x + 1e-9] + [b])
        for s in (0,) + v:
            note(ch, r + octave + s, x, nxt - x, vel)
        x = nxt


for name, (c, prog, vol) in CH.items():
    ev.append((0, 0, mido.Message("program_change", channel=c, program=prog)))
    cc(name, 7, vol, 0)
    cc(name, 11, 127, 0)
    cc(name, 91, 70, 0)
ev.append((0, 0, mido.Message("program_change", channel=DRUM, program=40)))      # the brush kit

# ---- dark and seen
hold(0, A["gone"], 50, "pad", 12)
hold(0, A["engage"], 58, "rhodes", 12)
brushes(A["seen"], A["engage"], 50)
comp(A["seen"], A["engage"], 54)
flip = A["seen"] + 0.08
for i, p in enumerate((86, 89, 93)):
    note("vibes", p, flip + i / 24, 0.4, 84)

# ---- engage: the conversation
walk(A["engage"], A["gone"], 98)
brushes(A["engage"], A["gone"], 62)
comp(A["engage"], A["gone"], 66)
for k, b in enumerate((1, 3, 5, 7)):                              # Breakout: vibraphone, rising
    at = A["engage"] + b * BEAT
    r, v = chord(at)
    for i, s in enumerate((v[1], v[2], v[3])):
        note("vibes", r + 36 + s + (12 if k > 1 else 0), at + i / 32, 0.3, 90)
for k, b in enumerate((2, 4, 6, 7.5)):                            # the visitor answers: muted trumpet
    at = A["engage"] + b * BEAT
    r, v = chord(at)
    note("tpt", r + 24 + v[1], at, 0.08, 92)
    note("tpt", r + 24 + v[2], at + SW * BEAT, 0.14, 98)

# ---- the rep
note("cel", 89, A["rep"] + 0.1, 0.4, 96)
note("cel", 96, A["rep"] + 0.15, 0.4, 84)
triad = A["rep"] + 3 * BEAT
for p, ch in ((77, "vibes"), (81, "cel"), (84, "tpt")):
    note(ch, p, triad, 0.3, 92)

# ---- follow: the bass alone, two vibraphone runs
walk(A["follow"], A["back"], 84)
for k, at in enumerate((A["follow"], A["follow"] + 1.5 * BEAT)):
    for i, p in enumerate((93, 89, 86, 84, 81, 77) if k == 0 else (86, 89, 84, 86, 81, 84)):
        note("vibes", p, at + i / 24, 0.2, 86 - i * 4)

# ---- the long game: brushes, the bass, and the easter egg's blips
brushes(A["game"], A["back"], 50, ride=False)
for x in (A["game"], A["game"] + 2):
    r, v = chord(x)
    for s in v:
        note("rhodes", r + 12 + s, x, 0.6, 44)
STEP = F["game"]["step"]
# when the snake eats, in steps: the same walk as template.html, on the coarse 2x2 grid
K = 2
x, y = (1160 - 12) // 24 // K, round((540 - 12) / 24) // K
n = 0
eats = []
for sx, sy in F["game"]["signals"]:
    sx, sy = sx // K, sy // K
    n += abs(sx - x) + abs(sy - y)
    x, y = sx, sy
    eats.append(n)
for i, e in enumerate(eats):
    at = A["game"] + e * STEP
    for j, p in enumerate((72 + i * 2, 79 + i * 2, 84 + i * 2)):
        note("chip", p, at + j / 32, 1 / 40, 100)

# ---- back: the band returns and builds
walk(A["back"], A["booked"], 104)
brushes(A["back"], A["booked"], 70)
comp(A["back"], A["booked"], 74)
for p, at, d in ((74, 0, 0.12), (77, 0.25, 0.12), (81, 0.5 - (1 - SW) * BEAT, 0.08), (84, 0.5, 0.2), (82, 0.75, 0.24)):
    note("tpt", p, A["back"] + at, d, 104)
ramp("pad", A["back"], A["booked"], 60, 127)
hold(A["back"], A["booked"], 58, "pad", 12)

# ---- booked: the hit
bk = A["booked"]
note(DRUM, CRASH, bk, 2, 112)
note(DRUM, KICK, bk, 0.2, 110)
note("bass", 29, bk, 1.5, 120)
for s in (0, 4, 7, 11, 14, 19):
    note("rhodes", 53 + s, bk, 1.4, 92)
    note("pad", 53 + s, bk, A["close"] - bk, 70)
note("tpt", 84, bk, 0.9, 108)
for i, p in enumerate((77, 81, 84, 88, 91, 96)):
    note("vibes", p, bk + 0.5 + i / 16, 0.3, 84)
brushes(bk + 0.5, A["close"], 54)

# ---- close: B-flat to F, ringing out
end = A["end"]
hold(A["close"], end - 0.2, 64, "rhodes", 12)
hold(A["close"], end - 0.2, 56, "pad", 24)
note("bass", BB - 12 + 12, A["close"], 1, 96)
note("bass", FF - 12 + 12, A["close"] + 1, 1.3, 96)
for i, p in enumerate((81, 84, 88, 91, 93, 96, 100)):
    note("vibes", p, A["close"] + 1 + i / 12, 0.5, 80 - i * 4)
note("cel", 101, A["close"] + 1.75, 0.6, 70)
ramp("rhodes", A["close"] + 1, end - 0.2, 127, 60)

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
x = Pedalboard([HighpassFilter(35), Reverb(room_size=0.6, damping=0.6, wet_level=0.18, dry_level=0.9, width=1.0),
                Compressor(threshold_db=-18, ratio=2.2, attack_ms=15, release_ms=180)])(x.T, SR)
g = np.ones(x.shape[1])
i0, i1 = int((A["gone"] * BAR + 0.01) * SR), int(A["follow"] * BAR * SR)       # the band cuts dead when she leaves
g[i0:i1] = 10 ** (-40 / 20)
g[i0 - 240:i0] = np.linspace(1, g[i0], 240)
g[i1:i1 + 480] = np.linspace(g[i0], 1, 480)
x *= g
x *= 10 ** (-1 / 20) / max(1e-9, float(np.max(np.abs(x))))
sf.write(args.out, x.T, SR, subtype="PCM_24")
print(f"wrote {args.out} and {midi_path}: {N / SR:.2f} s at {F['bpm']} BPM")
