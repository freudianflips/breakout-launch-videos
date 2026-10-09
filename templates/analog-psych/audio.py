#!/usr/bin/env python3
"""Sound for the Plays film: an analog SFX palette, the cue sheet from film.json, the mix and the mux.

  .venv/bin/python templates/analog-psych/audio.py            (after build.py and the render; psych_bed.py makes the music)

The analog sounds (needle, crackle, swarm hum, tally counter, typewriter, stamp, desk bell, film burn, tape)
are synthesised and seeded here, written to sfx/kit/, and placed with the sound forge's renderer so they
share one plate. Forge sounds (glass_tick, key_tap, ...) can sit in the same cue list. Then mixdown.py
masters to -14 LUFS and -1 dBTP and lays the sound onto renders/plays-picture.mp4.
"""
import json
import math
import os
import subprocess
import sys

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
PY = sys.executable
FILM = json.load(open("film.json"))
BAR = 240 / FILM["bpm"]
END = FILM["bars"] * BAR
SR = 48000
rng = np.random.default_rng(2026)
FORGE = {"glass_tick", "felt_thump", "wood_knock", "key_tap", "typing", "press", "arrive", "grow", "orbit_tick", "logo_sting", "air", "sub_drop", "lock"}


def tax(d):
    return np.arange(int(d * SR)) / SR


def env(d, a, tau):
    t = tax(d)
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / tau)


def hp(x):
    return np.diff(np.concatenate([[0], x]))


def lp(x, fc):
    from scipy.signal import butter, lfilter
    b, a = butter(2, fc / (SR / 2))
    return lfilter(b, a, x)


def bp(x, lo, hi):
    from scipy.signal import butter, lfilter
    b, a = butter(2, [lo / (SR / 2), hi / (SR / 2)], btype="band")
    return lfilter(b, a, x)


def crackle(d, density=14, hiss=0.02):
    n = int(d * SR)
    x = rng.standard_normal(n) * hiss
    x = lp(x, 6000)
    for _ in range(int(d * density)):
        i = rng.integers(0, n - 200)
        k = rng.integers(20, 120)
        x[i:i + k] += hp(rng.standard_normal(k)) * rng.uniform(0.2, 0.9) * np.exp(-np.arange(k) / (k / 4))
    return x


def needle():
    thump = np.sin(2 * math.pi * 60 * tax(0.25)) * env(0.25, 0.002, 0.05)
    x = np.concatenate([thump, np.zeros(int(0.9 * SR))])
    c = crackle(1.2, density=60, hiss=0.05)[: len(x)]
    x[: len(c)] += c * np.linspace(1, 0.25, len(c))
    return x


def swarm_hum(d=6.4):
    t = tax(d)
    x = np.zeros_like(t)
    for i in range(14):
        f = rng.uniform(205, 250)
        fm = 1 + 0.012 * np.sin(2 * math.pi * rng.uniform(4, 9) * t + rng.random() * 6)
        ph = np.cumsum(f * fm) / SR
        x += ((ph % 1) * 2 - 1) * (0.6 + 0.4 * np.sin(2 * math.pi * rng.uniform(0.2, 0.8) * t + rng.random() * 6))
    x = bp(x, 180, 1600) / 14
    fade = np.minimum(1, t / 1.5) * np.minimum(1, (d - t) / 1.2)
    return x * fade


def flutter():
    d = 0.42
    t = tax(d)
    x = bp(rng.standard_normal(len(t)), 300, 2400) * (0.5 + 0.5 * np.sin(2 * math.pi * 38 * t))
    return x * np.sin(np.pi * t / d) ** 2


def counter_click(seed=0):
    d = 0.09
    t = tax(d)
    r = np.random.default_rng(seed)
    x = sum(np.sin(2 * math.pi * f * t) * np.exp(-t / 0.012) for f in (2300 * r.uniform(0.97, 1.03), 4100, 6300))
    x += hp(r.standard_normal(len(t))) * np.exp(-t / 0.004) * 0.6
    return x


def counter_run(n=15, dur=1.85):
    out = np.zeros(int((dur + 0.3) * SR))
    for i in range(n):
        at = (i / n) ** 0.75 * dur
        c = counter_click(i) * (0.6 + 0.4 * i / n)
        s = int(at * SR)
        out[s:s + len(c)] += c
    return out


def tape(d, f0, f1, noise=0.25):
    t = tax(d)
    f = f0 * (f1 / f0) ** (t / d)
    ph = np.cumsum(f) / SR
    x = np.sin(2 * math.pi * ph) * 0.5 + bp(rng.standard_normal(len(t)), 200, 3000) * noise
    return x * np.sin(np.pi * t / d) ** 1.5


def burn():
    d = 1.6
    x = crackle(d, density=220, hiss=0.12)
    x += lp(rng.standard_normal(int(d * SR)), 220) * 0.6
    t = tax(d)
    return x * np.minimum(1, t / 0.25) * np.exp(-np.maximum(0, t - 0.6) / 0.5)


def click():
    t = tax(0.06)
    return hp(rng.standard_normal(len(t))) * np.exp(-t / 0.003) + np.sin(2 * math.pi * 1800 * t) * np.exp(-t / 0.008) * 0.5


def typewriter(chars=24, dur=1.2):
    out = np.zeros(int((dur + 0.3) * SR))
    for i in range(chars):
        at = i * dur / chars + rng.uniform(-0.012, 0.012)
        t = tax(0.07)
        k = hp(rng.standard_normal(len(t))) * np.exp(-t / 0.006) * 0.8 + np.sin(2 * math.pi * rng.uniform(140, 190) * t) * np.exp(-t / 0.02) * 0.7
        s = max(0, int(at * SR))
        out[s:s + len(k)] += k * rng.uniform(0.6, 1.0)
    return out


def stamp():
    t = tax(0.4)
    thud = np.sin(2 * math.pi * (70 + 60 * np.exp(-t / 0.03)) * t) * np.exp(-t / 0.08)
    slap = bp(rng.standard_normal(len(t)), 600, 5000) * np.exp(-t / 0.02) * 0.8
    return thud + slap


def tape_swell():
    d = 1.4
    t = tax(d)
    x = bp(rng.standard_normal(len(t)), 400, 4000) * 0.4 + np.sin(2 * math.pi * 330 * t * (1 + 0.004 * np.sin(2 * math.pi * 5 * t))) * 0.3
    return x * (t / d) ** 2 * np.exp(-np.maximum(0, t - d * 0.85) / 0.08)


def paper_send():
    d = 0.45
    t = tax(d)
    return bp(rng.standard_normal(len(t)), 900, 6500) * np.sin(np.pi * t / d) ** 3 * 0.6


def desk_bell():
    d = 3.2
    t = tax(d)
    f0 = 1960
    x = sum(a * np.sin(2 * math.pi * f0 * r * t + p) * np.exp(-t / tau) for r, a, tau, p in
            ((1.0, 1.0, 1.4, 0), (2.32, 0.5, 0.8, 1), (4.25, 0.3, 0.4, 2), (6.63, 0.15, 0.25, 3), (0.5, 0.15, 1.8, 0.5)))
    strike = hp(rng.standard_normal(len(t))) * np.exp(-t / 0.002) * 0.6
    return (x + strike) * (1 + 0.04 * np.sin(2 * math.pi * 5.5 * t))


def needle_lift():
    t = tax(0.6)
    x = np.sin(2 * math.pi * 55 * t) * np.exp(-t / 0.04) * 0.6 + crackle(0.6, density=40, hiss=0.03) * np.linspace(1, 0, len(t))
    return x


KIT = {
    "needle": lambda a: needle(), "crackle_bed": lambda a: crackle(a.get("dur", END + 2), density=9, hiss=0.015),
    "swarm_hum": lambda a: swarm_hum(a.get("dur", 6.4)), "flutter": lambda a: flutter(), "counter_click": lambda a: counter_click(),
    "counter_run": lambda a: counter_run(a.get("n", 15), a.get("dur", 1.85)), "tape_slow": lambda a: tape(1.4, 420, 60),
    "tape_start": lambda a: tape(0.5, 80, 520, 0.15), "burn": lambda a: burn(), "click": lambda a: click(),
    "typewriter": lambda a: typewriter(a.get("chars", 24), a.get("dur", 1.2)), "stamp": lambda a: stamp(),
    "tape_swell": lambda a: tape_swell(), "paper_send": lambda a: paper_send(), "desk_bell": lambda a: desk_bell(),
    "needle_lift": lambda a: needle_lift(),
}

# ------------------------------------------------------------------ the cue sheet
os.makedirs("sfx/kit", exist_ok=True)
cues = []
for i, c in enumerate(FILM["sfx"]):
    t = c["at"] * BAR
    args = dict(c.get("args", {}))
    if c["sound"] in FORGE:
        cues.append({"t": round(t, 4), "sound": c["sound"], "gain_db": c.get("gain_db", -10), "args": args, "pan": c.get("pan", 0)})
        continue
    if c.get("dur") == "film":
        args["dur"] = END - t + 2
    elif c.get("dur"):
        args["dur"] = c["dur"]
    x = KIT[c["sound"]](args)
    x = x / max(1e-9, np.max(np.abs(x))) * 0.9
    f = f"sfx/kit/{i:02d}-{c['sound']}.wav"
    sf.write(f, x, SR, subtype="PCM_24")
    cues.append({"t": round(t, 4), "file": os.path.relpath(f, "sfx"), "gain_db": c.get("gain_db", -10), "pan": c.get("pan", 0), "verb_db": c.get("verb_db", -14)})
json.dump({"duration": round(END + 1.0, 3), "key": FILM.get("key", "E"), "cues": cues}, open("sfx/cues.json", "w"), indent=1)
subprocess.run([PY, os.path.join(REPO, "skills/launch-sound/scripts/sfx_forge.py"), "render", "sfx/cues.json", "sfx/sfx.wav"], check=True)

# ------------------------------------------------------------------ the music
bed = FILM["music"]["file"]
if not os.path.exists(bed):
    subprocess.run([PY, "psych_bed.py", "film.json", "--out", bed], check=True)

# ------------------------------------------------------------------ mix and mux
os.makedirs("mix", exist_ok=True)
video = "renders/plays-picture.mp4"
mixcfg = {
    "duration": round(END, 3), "out": os.path.abspath("mix/master.wav"),
    "music": {"file": os.path.abspath(bed), "gain_db": FILM["music"].get("gain_db", -2), "start": 0.0, "offset": 0.0, "fade_out": FILM["music"].get("fade_out", 3.0)},
    "sfx": {"file": os.path.abspath("sfx/sfx.wav"), "gain_db": -1},
    "target_lufs": -14.0, "ceiling_dbtp": -2.6,
}
if os.path.exists(video):
    mixcfg.update({"video": os.path.abspath(video), "video_out": os.path.abspath("renders/plays-full.mp4")})
json.dump(mixcfg, open("mix/mix.json", "w"), indent=1)
subprocess.run([PY, os.path.join(REPO, "skills/launch-mix/scripts/mixdown.py"), "mix/mix.json"], check=True)
if os.path.exists(video):
    # the grain makes the raw render huge; encode a copy to share (the picture-only render is kept)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "renders/plays-full.mp4", "-c:v", "libx264", "-preset", "slow", "-crf", "23",
                    "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", "renders/plays.mp4"], check=True)
    os.remove("renders/plays-full.mp4")
    print("master: " + os.path.join(os.path.basename(os.path.dirname(HERE)), os.path.basename(HERE), "renders/plays.mp4"))
else:
    print("master: " + os.path.join(os.path.basename(os.path.dirname(HERE)), os.path.basename(HERE), "mix/master.wav (no picture yet)"))
