#!/usr/bin/env python3
"""The orchestral score for 'Press play.', written as MIDI from the film's own pattern and rendered free.

  .venv/bin/python templates/sequencer/orchestra.py [--out templates/sequencer/score/orchestra.wav]

Needs fluidsynth and a General MIDI soundfont (Debian/Ubuntu: apt install fluidsynth fluid-soundfont-gm;
or set SF2=/path/to/soundfont.sf2). Every signal row of film.json is a section of the orchestra and
plays only on the steps the grid lights:

  Pricing page viewed 3x  -> timpani and pizzicato basses on the quarters
  New CFO hired           -> a staccato string stab (and brass after the drop) on 2 and 4
  Return visit            -> a pizzicato ostinato on the off-beats
  2 blog views            -> a scattered harp, cut dead on the mute
  Buying committee        -> 3 horn notes, 1 per chip

Around them: a held violin harmonic under "Listen.", a tremolo swell and harp glissandi for 700+, a
timpani roll and tremolo crescendo into the press, 1 beat of silence, the full orchestra on the drop
in E minor, a run on the send, E major (a Picardy lift) for "Meeting booked." and a celesta music box
under the lockup that stops with the playhead.
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
ap.add_argument("--out", default=os.path.join(HERE, "score", "orchestra.wav"))
args = ap.parse_args()
F = json.load(open(os.path.join(HERE, "film.json")))
TR = F["transport"]
SF2 = os.environ.get("SF2", "/usr/share/sounds/sf2/FluidR3_GM.sf2")
SR = 48000
TPB = 480                  # ticks per beat
STEP = TPB // 4            # 1 sixteenth

# channel: (General MIDI program, volume)
CH = {"timp": (0, 47, 112), "bass": (1, 45, 104), "str": (2, 48, 92), "pizz": (3, 45, 100), "harp": (4, 46, 92),
      "horn": (5, 60, 100), "brass": (6, 61, 96), "vln": (7, 48, 100), "cel": (8, 8, 96), "trem": (10, 44, 92),
      "choir": (11, 52, 80), "bone": (12, 57, 90), "glock": (13, 9, 70)}
DRUM = 9                   # orchestra kit
BD, SN, CRASH, CRASH2 = 36, 38, 49, 57

ev = []                    # (tick, order, message)


def tk(bar):
    return int(round(bar * 4 * TPB))


def note(ch, pitch, at, dur, vel):
    c = CH[ch][0] if isinstance(ch, str) else ch
    s, e = tk(at), tk(at + dur)
    ev.append((s, 1, mido.Message("note_on", channel=c, note=int(pitch), velocity=int(max(1, min(127, vel))))))
    ev.append((max(s + 1, e), 0, mido.Message("note_off", channel=c, note=int(pitch), velocity=0)))


def cc(ch, num, val, at):
    ev.append((tk(at), 0, mido.Message("control_change", channel=CH[ch][0], control=num, value=int(max(0, min(127, val))))))


def ramp(ch, a, b, v0, v1, n=24, num=11):
    for i in range(n + 1):
        cc(ch, num, v0 + (v1 - v0) * i / n, a + (b - a) * i / n)


def hits(steps, a, b, mute=None):
    out = []
    for bar in range(int(a), int(b) + 2):
        for k in steps:
            t = bar + k / 16
            if a - 1e-9 <= t < b - 1e-9 and (mute is None or t < mute - 1e-9):
                out.append(t)
    return out


# chords per bar, as MIDI note numbers of root (octave 2), third, fifth
CHORD = {0: (40, 43, 47), 1: (40, 43, 47), 2: (40, 43, 47), 3: (40, 43, 47), 4: (36, 40, 43), 5: (38, 42, 45),
         6: (45, 48, 52), 7: (47, 51, 54), 8: (40, 43, 47), 9: (36, 40, 43), 10: (40, 43, 47), 11: (40, 44, 47)}


def chord(bar):
    return CHORD.get(int(bar), CHORD[11])


for name, (c, prog, vol) in CH.items():
    ev.append((0, 0, mido.Message("program_change", channel=c, program=prog)))
    cc(name, 7, vol, 0)
    cc(name, 11, 127, 0)
ev.append((0, 0, mido.Message("program_change", channel=DRUM, program=48)))

rows = F["rows"]
kick, clap, hat, ghost = rows[0], rows[1], rows[2], rows[3]
drop, send, stop = TR["drop"], TR["send"], TR["stop"]

# ---- intro: a held harmonic, and the clock as a quiet celesta on the beats
cc("vln", 11, 40, 0)
note("vln", 88, 0, 2, 50)                                          # E6, very quiet
note("str", 52, 1, 1, 46)                                          # E3 under "Listen."
note("timp", 40, 1, 0.5, 70)
for t in hits([0, 4, 8, 12], 0, 2):
    note("cel", 88 if (t * 16) % 16 == 0 else 83, t, 0.1, 34)
cc("vln", 11, 127, 2)

# ---- the rows, exactly as the grid lights them
def rows_play(a, b, big):
    for t in hits(kick["steps"], max(a, kick["start"]), b):
        r = chord(t)[0]
        note("timp", r, t, 0.2, 104 if big else 62)
        note("bass", r - 12 if r - 12 >= 28 else r, t, 0.15, 100 if big else 66)
        if big:
            note(DRUM, BD, t, 0.1, 60)
    for t in hits(clap["steps"], max(a, clap["start"]), b):
        r, th, fi = chord(t)
        for p in (r + 12, th + 12, fi + 12, r + 24):
            note("str", p, t, 0.09, 108 if big else 68)
        note(DRUM, SN, t, 0.1, 60 if big else 30)
        if big:
            for p in (th + 12, fi + 12, r + 24):
                note("brass", p, t, 0.08, 92)
    for t in hits(hat["steps"], max(a, hat["start"]), b):
        r, th, fi = chord(t)
        k = int(round((t % 1) * 16)) // 4
        note("pizz", [r + 24, th + 24, fi + 24, th + 24][k], t, 0.08, 96 if big else 64)


rows_play(0, stop, False)
for t in hits(ghost["steps"], ghost["start"], stop, ghost["mute_at"]):
    r, th, fi = chord(t)
    note("harp", [r, th, fi][int(t * 16) % 3] + 36, t, 0.12, 52)
note("str", 40 + 24, 2, 2, 52)                                     # a soft pad under the first notes
note("str", 47 + 12, 2, 2, 48)
note("str", 36 + 24, 4, 1, 52)
note("str", 43 + 12, 4, 1, 48)

# ---- 700+: a tremolo swell and harp glissandi across the pull-back
z = TR["zoom"]
for p in (50, 57, 62, 66, 69):                                     # D major, spread
    note("trem", p, z, 0.95, 90)
ramp("trem", z, z + 0.6, 30, 120)
for i in range(24):
    r, th, fi = chord(z)
    note("harp", [r, th, fi][i % 3] + 24 + 12 * (i // 3 % 3), z + 0.05 + i / 48, 0.2, 70)
rng = np.random.default_rng(700)
for i in range(18):
    note("cel", int(rng.choice([74, 78, 81, 86, 90, 93])), z + 0.1 + rng.uniform(0, 0.8), 0.1, int(rng.integers(30, 60)))

# ---- the build into the press: tremolo crescendo, a timpani roll, horns swell, cut dead before the drop
cut = TR["press"] + 0.75
for p in (57, 60, 64, 69):                                         # A minor
    note("trem", p, stop, 1.0, 96)
for p in (59, 63, 66, 71, 75):                                     # B major
    note("trem", p, stop + 1, cut - stop - 1, 100)
ramp("trem", stop, cut, 34, 127, 48)
for p in (59, 63, 66):
    note("horn", p, TR["press"], cut - TR["press"], 96)
ramp("horn", TR["press"], cut, 40, 127)
roll = TR["press"]
i = 0
while roll + i / 32 < cut:
    note("timp", 47, roll + i / 32, 1 / 32, 50 + 70 * i / ((cut - roll) * 32))
    i += 1
note(DRUM, CRASH2, TR["press"], 0.5, 50)
for name in ("trem", "horn"):
    cc(name, 11, 0, cut)
    cc(name, 11, 127, drop)

# ---- the drop: the whole orchestra in E minor, the rows playing on, a violin line over them
note(DRUM, CRASH, drop, 1, 110)
note(DRUM, BD, drop, 0.2, 120)
for b in (drop, drop + 1):
    r, th, fi = chord(b)
    for p in (r, r + 12, th + 12, fi + 12):
        note("brass", p, b, 0.98, 100 if b == drop else 84)
    note("bone", r, b, 0.98, 90)
    for p in (r + 12, fi + 12, r + 24, th + 24, fi + 24):
        note("str", p, b, 0.99, 92)
for p in (40, 47, 52, 55, 59):
    note("str", p, drop + 2, send - drop - 2, 90)
rows_play(drop, send, True)
MEL = [(76, 0, 0.375), (74, 0.375, 0.125), (71, 0.5, 0.5), (72, 1, 0.375), (74, 1.375, 0.125), (76, 1.5, 0.5),
       (79, 2, 0.375), (78, 2.375, 0.125), (76, 2.5, 0.25)]
for p, at, d in MEL:
    note("vln", p, drop + at, d * 0.98, 104)
    note("vln", p + 12, drop + at, d * 0.98, 78)
cm = F["committee"]
for t, p in zip(hits(cm["steps"], cm["start"], send), (64, 67, 71)):
    note("horn", p, t, send - t, 108)
    note("horn", p - 12, t, send - t, 80)

# ---- the send: a run up, then the meeting in E major
run = [76, 78, 79, 81, 83, 84, 86, 88]
for i, p in enumerate(run):
    note("vln", p, send + i / 32, 1 / 32, 90 + i * 3)
    note("str", p - 12, send + i / 32, 1 / 32, 80)
bk = TR["booked"]
note(DRUM, CRASH, bk, 1.5, 118)
note(DRUM, CRASH2, bk, 1.5, 90)
for k in (0, 4, 8):
    note("timp", 40, bk + k / 16, 0.25, 118 - k * 3)
    note(DRUM, BD, bk + k / 16, 0.2, 110 - k * 4)
for p in (40, 52, 56, 59, 64):
    note("brass", p, bk, 1.0, 110)
note("bone", 28, bk, 1.2, 100)
note("bone", 40, bk, 1.2, 96)
for p in (64, 68, 71, 76):
    note("choir", p, bk, 1.6, 96)
for p in (40, 52, 59, 64, 68, 71, 76, 80):
    note("str", p, bk, 1.6, 100)
note("vln", 88, bk, 1.0, 100)
for i, p in enumerate((76, 80, 83, 88, 92, 95)):
    note("glock", p, bk + 0.25 + i / 16, 0.2, 80)
ramp("str", bk + 0.5, bk + 1.6, 127, 60)

# ---- the lockup: a celesta music box under the ticking strip, stopping with the playhead
lk, end = TR["lockup"], TR["end"]
for p in (52, 59, 64, 68, 71):
    note("str", p, lk, end - lk + 0.4, 70)
ramp("str", lk, end + 0.4, 70, 20)
box = [76, 80, 83, 88, 83, 80, 76, 71]
t = lk + 0.5
i = 0
while t < end - 1e-9:
    note("cel", box[i % len(box)], t, 0.12, 64 - 14 * (t - lk) / (end - lk))
    t += 1 / 8
    i += 1
note("cel", 88, end, 0.5, 52)
note("harp", 76, end, 0.5, 60)

# ---- write the MIDI, render it with the soundfont, add the hall
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
os.makedirs(os.path.dirname(args.out), exist_ok=True)
midi_path = os.path.splitext(args.out)[0] + ".mid"
dry = os.path.splitext(args.out)[0] + "-dry.wav"
mid.save(midi_path)
subprocess.run(["fluidsynth", "-ni", "-q", "-g", "0.6", "-r", str(SR), "-R", "0", "-C", "0", "-F", dry, SF2, midi_path], check=True)
x, sr = sf.read(dry, dtype="float32")
os.remove(dry)
N = int((F["bars"] * 240 / F["bpm"] + 1.5) * SR)
x = np.pad(x, ((0, max(0, N - len(x))), (0, 0)))[:N]
x = Pedalboard([HighpassFilter(30), Reverb(room_size=0.78, damping=0.45, wet_level=0.2, dry_level=0.85, width=1.0),
                Compressor(threshold_db=-16, ratio=2.5, attack_ms=12, release_ms=160)])(x.T, SR)
# the beat of silence before the drop: cut the hall dead too
BARS = 240 / F["bpm"]
g = np.ones(x.shape[1])
a, b = int((cut * BARS + 0.01) * SR), int(drop * BARS * SR)
g[a:b] = 10 ** (-38 / 20)
g[a - 240:a] = np.linspace(1, g[a], 240)
x *= g
x *= 10 ** (-1 / 20) / max(1e-9, float(np.max(np.abs(x))))
sf.write(args.out, x.T, SR, subtype="PCM_24")
print(f"wrote {args.out} and {midi_path}: {N / SR:.2f} s at {F['bpm']} BPM, soundfont {os.path.basename(SF2)}")
