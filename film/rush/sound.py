#!/usr/bin/env python3
"""Free sound for 'Rush': a synthesised 140 BPM track and a snappy SFX stem, both on the shot grid
in film.json, then the -14 LUFS master and the mux onto renders/rush-<format>-picture.mp4.

  .venv/bin/python film/rush/sound.py [wide|feed]

Everything is seeded, so the same film.json always gives the same audio. Scratch only: swap in a
real track before anyone judges the music.
"""
import json
import os
import subprocess
import sys

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
F = json.load(open("film.json"))
SR = 48000
BEAT = 60 / F["bpm"]
END = F["beats"] * BEAT
N = int((END + 1.5) * SR)
FMT = sys.argv[1] if len(sys.argv) > 1 else "wide"
# the markers the music follows, read from the shots
first = lambda ty: next(s["at"] for s in F["shots"] if any(i["type"] == ty for i in s["items"]))
DROP, BOOKED, LOCK = first("logo"), first("booked"), first("lockup")
COUNT = first("counter")
rng = np.random.default_rng(140)


def t_ax(d):
    return np.arange(int(d * SR)) / SR


def env(d, tau, att=0.001):
    t = t_ax(d)
    return np.minimum(t / att, 1) * np.exp(-t / tau)


def lp(x, cut):
    a = np.exp(-2 * np.pi * cut / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def noise(d):
    return rng.standard_normal(int(d * SR))


def kick(d=0.35):
    t = t_ax(d)
    f = 45 + 130 * np.exp(-t / 0.035)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(d, 0.12) + 0.3 * noise(d) * env(d, 0.004)


def clap(d=0.25):
    x = np.zeros(int(d * SR))
    for o in (0, 0.011, 0.022):
        e = np.zeros(int(d * SR))
        k = int(o * SR)
        e[k:] = env(d - o, 0.03 if o < 0.02 else 0.09)[: len(e) - k]
        x += e
    n = noise(d)
    return (n - lp(n, 900)) * x * 0.6


def hat(d=0.06, open_=False):
    n = noise(d if not open_ else 0.22)
    n = n - lp(n, 6000)
    return n * env(len(n) / SR, 0.015 if not open_ else 0.08) * 0.35


def bass(note, d):
    t = t_ax(d)
    f = 55 * 2 ** (note / 12)
    x = np.tanh(2.2 * (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t)))
    return x * np.minimum(t / 0.004, 1) * np.exp(-t / (d * 0.9))


def impact(d=1.2):
    t = t_ax(d)
    f = 30 + 90 * np.exp(-t / 0.06)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(d, 0.35)
    n = noise(d)
    return 0.9 * body + 0.5 * lp(n, 2500) * env(d, 0.08) + 0.25 * n * env(d, 0.01)


def whoosh(d=0.32, up=True):
    n = noise(d)
    t = t_ax(d)
    cut = 400 + 7000 * ((t / d) if up else (1 - t / d))
    hi = n - lp(n, 300)
    out = np.empty_like(hi)
    acc = 0.0
    for i, v in enumerate(hi):
        a = np.exp(-2 * np.pi * cut[i] / SR)
        acc = (1 - a) * v + a * acc
        out[i] = acc
    shape = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 1.5
    return out * shape * 1.6


def tick(f=2600, d=0.05):
    t = t_ax(d)
    return np.sin(2 * np.pi * f * t) * env(d, 0.008) + 0.4 * noise(d) * env(d, 0.002)


def glitch(d=0.14):
    x = np.zeros(int(d * SR))
    seg = int(0.012 * SR)
    src = noise(0.012) * 0.6 + np.sign(np.sin(2 * np.pi * 180 * t_ax(0.012))) * 0.5
    for k in range(0, len(x) - seg, seg * 2):
        x[k:k + seg] = src * (1 - k / len(x))
    return x


def riser(d):
    t = t_ax(d)
    f = 200 * 2 ** (3 * t / d)
    tone = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.25
    n = noise(d)
    return (tone + 0.5 * (n - lp(n, 1500))) * (t / d) ** 2


def chime(f=1318.5, d=1.6):
    t = t_ax(d)
    return sum(a * np.sin(2 * np.pi * f * m * t) * np.exp(-t / (d * 0.3 / m)) for m, a in ((1, 1), (2.01, 0.4), (3.02, 0.2)))


def put(buf, x, at, gain_db, pan=0.0):
    k = int(at * SR)
    if k >= len(buf):
        return
    x = x[: len(buf) - k] * 10 ** (gain_db / 20)
    buf[k:k + len(x), 0] += x * np.sqrt(0.5 * (1 - pan))
    buf[k:k + len(x), 1] += x * np.sqrt(0.5 * (1 + pan))


# ------------------------------------------------------------------ music on the beat grid
music = np.zeros((N, 2))
ROOTS = [0, 0, 3, 3, 5, 5, -2, -2]  # E minor-ish walk, 1 root per bar pair
for b in range(int(LOCK)):
    t = b * BEAT
    bar = (b - DROP) // 4
    if b < DROP:  # the hook: tight hats and a clap on every word, a riser into the drop
        put(music, clap(), t, -8)
        put(music, hat(), t + BEAT / 2, -10, 0.3)
        continue
    if BOOKED <= b < BOOKED + 2:  # the booked moment breathes: kick only
        put(music, kick(), t, -2)
        continue
    put(music, kick(), t, -2)
    if b % 2 == 1:
        put(music, clap(), t, -6)
    put(music, hat(), t + BEAT / 2, -9, 0.25)
    put(music, hat(), t + BEAT / 4, -16, -0.25)
    put(music, hat(), t + 3 * BEAT / 4, -16, -0.25)
    note = ROOTS[bar % len(ROOTS)]
    put(music, bass(note, BEAT * 0.45), t + BEAT / 2, -9)
    put(music, bass(note + 12, BEAT * 0.2), t + 3 * BEAT / 4, -14)
for k in range(16):  # snare roll into OUT. (beats 22 to 25)
    put(music, clap(0.12), (BOOKED - 4) * BEAT + k * BEAT / 4 if k < 8 else (BOOKED - 2) * BEAT + (k - 8) * BEAT / 8, -14 + k * 0.5)
put(music, riser(DROP * BEAT), 0, -16)
put(music, riser(2 * BEAT), (BOOKED - 2) * BEAT, -14)
# the lockup: everything stops, 1 low hit and a long tail
put(music, impact(2.5), LOCK * BEAT, -6)
music[int((LOCK * BEAT + 2.5) * SR):] *= 0

# ------------------------------------------------------------------ SFX from the shots
sfx = np.zeros((N, 2))
for f in F["flicks"]:
    put(sfx, glitch(), f * BEAT, -8)
for s in F["shots"]:
    a = s["at"] * BEAT
    for it in s["items"]:
        t = a + it.get("at", 0) * BEAT
        ty, fx = it["type"], it.get("fx", "slam")
        if ty == "word" or ty == "counter":
            put(sfx, impact(0.5), t, -10 if not it.get("rgb") else -7)
            if it.get("rgb"):
                put(sfx, glitch(0.08), t, -14)
        elif ty == "screen":
            if fx.startswith("whip") or fx == "rise":
                put(sfx, whoosh(0.22), t - 0.16, -6, 0.6 if fx == "whip-r" else -0.6)
            else:
                put(sfx, whoosh(0.18, up=False), t, -10)
                put(sfx, tick(1800), t, -12)
        elif ty == "logo":
            put(sfx, whoosh(0.35), t - 0.33, -6)
            put(sfx, impact(1.4), t, -3)
        elif ty == "chip":
            put(sfx, tick(2200 + 300 * (it.get("at", 0) * 4 % 5)), t, -8, it["x"] * 2 - 0.6)
        elif ty == "ring":
            put(sfx, tick(3200, 0.04), t, -6)
        elif ty == "booked":
            put(sfx, impact(1.6), t, -2)
            put(sfx, chime(1318.5), t + 0.3, -9)
            put(sfx, chime(1975.5), t + 0.42, -12)
        elif ty == "lockup":
            put(sfx, chime(659.3, 2.4), t + 0.3, -14)
    if s.get("ground") and s["at"] > 0:
        put(sfx, tick(5200, 0.02), a, -20)
for k in range(13):  # the 700+ counter rattles
    put(sfx, tick(3000 + 60 * k, 0.03), COUNT * BEAT + k * BEAT * 1.6 / 13, -16)

os.makedirs("mix", exist_ok=True)
# stems leave at -12 dBFS peak so the mixdown always has to raise them, which runs its limiter
pk = max(np.abs(music).max(), np.abs(sfx).max())
sf.write("mix/music.wav", music * 10 ** (-12 / 20) / pk, SR)
sf.write("mix/sfx.wav", sfx * 10 ** (-12 / 20) / pk, SR)
video = f"renders/rush-{FMT}-picture.mp4"
cfg = {"duration": round(END + 0.4, 3), "out": os.path.abspath("mix/master.wav"),
       "music": {"file": os.path.abspath("mix/music.wav"), "gain_db": -1, "start": 0.0, "offset": 0.0, "fade_out": 0.5},
       "sfx": {"file": os.path.abspath("mix/sfx.wav"), "gain_db": -2}, "target_lufs": -14.0, "ceiling_dbtp": -2.8}
if os.path.exists(video):
    cfg.update({"video": os.path.abspath(video), "video_out": os.path.abspath(f"renders/rush-{FMT}-full.mp4")})
json.dump(cfg, open("mix/mix.json", "w"), indent=1)
subprocess.run([sys.executable, os.path.join(REPO, "skills/launch-mix/scripts/mixdown.py"), "mix/mix.json"], check=True)
if os.path.exists(video):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"renders/rush-{FMT}-full.mp4", "-c:v", "libx264", "-preset", "slow", "-crf", "18",
                    "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", f"renders/rush-{FMT}.mp4"], check=True)
    os.remove(f"renders/rush-{FMT}-full.mp4")
    print(f"master: film/rush/renders/rush-{FMT}.mp4")
