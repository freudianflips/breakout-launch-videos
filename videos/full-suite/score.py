#!/usr/bin/env python3
"""The jazz score for a dot-matrix film: upbeat swing, written as MIDI on the film's bar grid and rendered free.

  .venv/bin/python score.py [--out score/score.wav]   (from this folder)

Needs fluidsynth and a General MIDI soundfont (apt install fluidsynth fluid-soundfont-gm, or SF2=...).
A bright little big band in F major: piano, walking bass, a jazz kit, vibraphone, trumpet, alto sax, trombone
and, for the easter egg, a square-wave lead. The picture's events are its cues:

  dark        a drum pickup and a horn swell, then the band kicks in
  seen        full swing (I-VI-ii-V); a vibraphone glint when the visitor turns pink
  engage      vibraphone for Breakout's ripples, alto sax answering for the visitor
  rep         a trumpet fanfare when the cyan bloom wakes; a horn chord on the triad ripple
  gone        stop-time: two band stabs and a drum fill, never silence
  follow      back in, a vibraphone run per comet
  game        a fast F blues: a vibraphone ping per sonar ping, an 8-bit blip per signal eaten, a horn "bop" per tap
  back        a shout chorus building into
  booked      the hit: crash, the full band on F6/9
  close       B-flat to F, a vibraphone run, a button
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
for i, x in enumerate(range(0, int(A["gone"]))):
    PROG.append((x, TURN[i % 4]))
PROG += [(A["gone"], (F_, SIX)), (A["follow"], (BB, DOM)), (A["follow"] + 1, (C_, DOM9))]
for i in range(int(A["back"] - A["game"])):
    PROG.append((A["game"] + i, BLUES[i % len(BLUES)]))
PROG += [(A["back"], (G_, MIN)), (A["back"] + 0.5, (C_, DOM9)), (A["back"] + 1, (A_, DOM)), (A["booked"], (F_, SIX)),
         (A["close"], (BB, SIX)), (A["close"] + 1, (C_, DOM9)), (A["close"] + 2, (F_, SIX))]
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
# ---- dark: a pickup, a swell, the band kicks in on the first hop
fill(0.25)
for p, ch in ((77, "tpt"), (72, "alto"), (65, "bone")):
    note(ch, p, 0.5, 0.45, 80)
walk(0, A["gone"], 108)
drums(0.5, A["gone"], 78)
comp(0.5, A["gone"], 80)
flip = A["seen"] + 0.06
for i, p in enumerate((84, 88, 91, 96)):
    note("vibes", p, flip + i / 24, 0.3, 96)

# ---- engage: the conversation
for k, b in enumerate((1, 3, 5, 7)):                              # Breakout: vibraphone, rising
    at = A["engage"] + b * BEAT
    r, v = chord(at)
    for i, s in enumerate((v[0], v[1], v[3])):
        note("vibes", r + 36 + s + (12 if k > 1 else 0), at + i / 32, 0.25, 100)
for k, b in enumerate((2, 4, 6, 7.5)):                            # the visitor answers: alto sax
    at = A["engage"] + b * BEAT
    r, v = chord(at)
    note("alto", r + 24 + v[1], at, 0.06, 100)
    note("alto", r + 24 + v[2], at + SW * BEAT, 0.12, 106)

# ---- the rep: a fanfare, then the triad
for i, p in enumerate((72, 77, 81, 84)):
    note("tpt", p, A["rep"] + 0.06 + i / 24, 0.1 if i < 3 else 0.3, 104)
triad = A["rep"] + 3 * BEAT
stab(triad, 104, 0.2)

# ---- gone: stop-time, never silence
stab(A["gone"], 110, 0.12)
stab(off(A["gone"], 3), 104, 0.08)
note(DRUM, CRASH, A["gone"], 0.5, 96)
for e in (4, 5, 6):
    note(DRUM, RIDE, off(A["gone"], e), 0.08, 70)
fill(A["gone"] + 0.75, 100)

# ---- follow: back in, two comets
walk(A["follow"], A["back"], 110)
drums(A["follow"], A["back"], 82)
comp(A["follow"], A["back"], 78)
for k, at in enumerate((A["follow"], A["follow"] + 1.5 * BEAT)):
    for i, p in enumerate((77, 81, 84, 89, 93, 96) if k == 0 else (79, 82, 86, 89, 94, 98)):
        note("vibes", p, at + i / 32, 0.18, 90 + i * 2)

# ---- the long game: pings, blips, bops
BAR = 240 / F["bpm"]
for x in range(int(A["back"] - A["game"])):
    note("vibes", 96, A["game"] + x, 0.4, 74)                    # the sonar ping
    note("vibes", 89, A["game"] + x + 1 / 16, 0.3, 60)
# when the snake eats and taps, in steps: the same route as template.html, on the coarse 2x2 grid
K, STEP = 2, F["game"]["step"]
VC = (F["game"]["visitor"][0] // K, F["game"]["visitor"][1] // K)
head = ((1160 - 12) // 24 // K, (540 - 12) // 24 // K)


def leg(h, s, x_first):
    x, y = h
    out = []
    def wx():
        nonlocal x
        while x != s[0]:
            x += 1 if s[0] > x else -1
            out.append((x, y))
    def wy():
        nonlocal y
        while y != s[1]:
            y += 1 if s[1] > y else -1
            out.append((x, y))
    if x_first:
        wx(); wy()
    else:
        wy(); wx()
    return out


def walk_to(s):
    global head, n
    a, b = leg(head, s, True), leg(head, s, False)
    hits = lambda l: any(abs(c[0] - VC[0]) <= 1 and abs(c[1] - VC[1]) <= 1 for c in l)
    route = b if hits(a) and not hits(b) else a
    n += len(route)
    head = route[-1] if route else head


n = 0
eats, taps = [], []
for sx, sy in F["game"]["signals"]:
    s = (sx // K, sy // K)
    walk_to(s)
    eats.append(n)
    dx, dy = s[0] - VC[0], s[1] - VC[1]
    sg = lambda v: (v > 0) - (v < 0)
    walk_to((VC[0] + 2 * sg(dx), VC[1]) if abs(dx) >= abs(dy) else (VC[0], VC[1] + 2 * sg(dy)))
    taps.append(n)
for i, e in enumerate(eats):
    at = A["game"] + e * STEP
    for j, p in enumerate((72 + i * 2, 79 + i * 2, 84 + i * 2, 91 + i * 2)):
        note("chip", p, at + j / 48, 1 / 48, 104)
for i, e in enumerate(taps):
    at = A["game"] + e * STEP
    stab(at, 98 + i * 4, 0.08)
    note(DRUM, SNARE, at, 0.05, 104)

# ---- back: the shout chorus, building
walk(A["back"], A["booked"], 116)
drums(A["back"], A["booked"], 92)
comp(A["back"], A["booked"], 88)
riff = [(0, 72, 0.12), (1, 74, 0.06), (2, 77, 0.12), (3, 81, 0.06), (4, 84, 0.2), (6, 82, 0.08), (7, 81, 0.12)]
for bar in (0, 1):
    for e, p, d in riff:
        at = off(A["back"] + bar, e)
        if at < A["booked"]:
            note("tpt", p + bar * 2, at, d, 108)
            note("alto", p + bar * 2 - 4, at, d, 100)
            note("bone", p + bar * 2 - 12, at, d, 96)
fill(A["booked"] - 0.25, 110)

# ---- booked: the hit
bk = A["booked"]
note(DRUM, CRASH, bk, 2, 120)
note(DRUM, KICK, bk, 0.2, 120)
note("bass", F_ - 12, bk, 1.2, 124)
for s in (0, 4, 7, 9, 14):
    note("piano", F_ + 12 + s, bk, 1.0, 108)
for p, ch in ((89, "tpt"), (84, "alto"), (77, "bone")):
    note(ch, p, bk, 1.2, 112)
for i, p in enumerate((77, 81, 84, 89, 93, 96)):
    note("vibes", p, bk + 0.5 + i / 16, 0.3, 92)
walk(bk + 0.5, A["close"], 108)
drums(bk + 0.5, A["close"], 82)
comp(bk + 0.5, A["close"], 80)

# ---- close: B-flat, C, F, a vibraphone run, the button
walk(A["close"], A["close"] + 2, 106)
drums(A["close"], A["close"] + 2, 78)
comp(A["close"], A["close"] + 2, 80)
for i, p in enumerate((81, 84, 88, 91, 93, 96, 100, 105)):
    note("vibes", p, A["close"] + 2 + i / 24, 0.6, 92 - i * 3)
for s in (0, 4, 7, 9, 14):
    note("piano", F_ + 12 + s, A["close"] + 2, 0.9, 92)
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
