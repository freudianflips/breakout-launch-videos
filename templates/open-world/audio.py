#!/usr/bin/env python3
"""Sound for an open-world film: the game's own effects (a moped engine that follows the ride, a cable car bell,
radar pings, a pager, a tyre squeal, a city bed), synthesised here or by the shared forge, then the G-funk score,
the -14 LUFS master and the mux onto renders/picture.mp4.

  .venv/bin/python audio.py        (from this folder, after build.py and the picture render)

Every time comes from film.json "at" and the same constants template.html uses, so picture and sound stay locked.
"""
import json
import os
import subprocess
import sys

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
PY = sys.executable
F = json.load(open("film.json"))
BAR = 240 / F["bpm"]
BEAT = BAR / 4
A = {k: v * BAR for k, v in F["at"].items()}
END = A["end"]
SR = 48000
rng = np.random.default_rng(11)
# the ride, as template.html times it
T_MOUNT = A["m1_start"] + 2 * BEAT
T_GO = T_MOUNT + 0.37
T_TOP = T_GO + 2
T_EDGE = T_TOP + 12 / 24
T_LAND = T_EDGE + (2.5 + 14 / 42 * 24) / 8
D_START = A["ride"] + 8 * BEAT
T_BRAKE = D_START + 0.45
T_CROSS = A["ride"] + 5 * BEAT + 1.6


def lp(x, f):
    return sosfilt(butter(2, f, "low", fs=SR, output="sos"), x)


def bp(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], "band", fs=SR, output="sos"), x)


def write(name, x):
    os.makedirs("sfx", exist_ok=True)
    sf.write(f"sfx/{name}.wav", (x / (np.abs(x).max() + 1e-9) * 0.9).astype(np.float32), SR)
    return f"{name}.wav"


def speed(t):
    """the moped's speed (m/s) and how loud its engine is at time t."""
    if T_MOUNT <= t < A["m1_pass"]:
        if t < T_GO:
            return 0.0, 0.6
        if t < T_TOP:
            return 12 * (t - T_GO), 1.0
        if T_EDGE <= t < T_LAND:
            return 30.0, 1.1                                       # airborne: the engine screams free
        if t >= T_BRAKE:
            return max(0.0, 24 - 40 * (t - T_BRAKE)), 0.9
        return 24.0, 1.0
    if A["night"] <= t < A["morning"]:
        return 9.0, 0.45
    return 0.0, 0.0


# the engine: a buzzing two-stroke whose pitch follows the speed
n = int((END + 1) * SR)
tt = np.arange(n) / SR
sp = np.array([speed(t) for t in tt[::480]])
spd = np.interp(tt, tt[::480], sp[:, 0]); amp = np.interp(tt, tt[::480], sp[:, 1])
f0 = 38 + spd * 5.2
ph = 2 * np.pi * np.cumsum(f0) / SR
eng = (np.sign(np.sin(ph)) * 0.5 + np.sin(2 * ph) * 0.4 + 0.25 * np.sin(3.01 * ph)) * (0.65 + 0.35 * np.sin(ph * 0.5) ** 2)
eng = lp(eng, 1800) + 0.08 * bp(rng.standard_normal(n), 2000, 5000) * (spd / 24)
engine = write("engine", eng * lp(amp, 20))
# the city: traffic hum, a far horn, wind
city = lp(rng.standard_normal(n), 350) * 0.6 + bp(rng.standard_normal(n), 600, 2400) * 0.08
city *= np.clip(1 - (tt - (A["close"] + BEAT)) / 1.2, 0, 1)
ambience = write("city", city)
# one-shots
def tone(f, d, decay, partials=((1, 1),)):
    t = np.arange(int(d * SR)) / SR
    return sum(a * np.sin(2 * np.pi * f * m * t) for m, a in partials) * np.exp(-t / decay) * np.minimum(1, t / 0.002)


bell = write("bell", tone(1310, 1.4, 0.45, ((1, 1), (2.76, 0.45), (5.4, 0.2))) + tone(880, 1.4, 0.6, ((1, 0.5),)))
ping = write("ping", tone(1568, 0.9, 0.22, ((1, 1), (2, 0.2))) + np.concatenate([np.zeros(int(0.11 * SR)), tone(1568, 0.79, 0.14) * 0.35]))
t3 = np.arange(int(0.7 * SR)) / SR
pager = write("pager", np.sign(np.sin(2 * np.pi * 165 * t3)) * (np.sin(2 * np.pi * 9 * t3) > 0) * np.minimum(1, (0.7 - t3) / 0.05))
t4 = np.arange(int(0.65 * SR)) / SR
squeal = write("squeal", bp(rng.standard_normal(len(t4)), 1800, 3400) * (0.6 + 0.4 * np.sin(2 * np.pi * 31 * t4)) * np.minimum(1, t4 / 0.03) * np.minimum(1, (0.65 - t4) / 0.2))
t5 = np.arange(int(0.5 * SR)) / SR
alarm = write("alarm", np.concatenate([np.sign(np.sin(2 * np.pi * 880 * t5[:int(0.12 * SR)])), np.zeros(int(0.08 * SR)), np.sign(np.sin(2 * np.pi * 880 * t5[:int(0.12 * SR)]))]) * 0.6)


def cue(t, sound, gain, pan=0, **args):
    return {"t": round(t, 4), "sound": sound, "gain_db": gain, "args": args, "pan": pan}


def fcue(t, f, gain, pan=0, dur=None, verb=-14):
    c = {"t": round(t, 4), "file": f, "gain_db": gain, "pan": pan, "verb_db": verb}
    if dur:
        c["dur"] = dur
    return c


cues = [fcue(0, ambience, -30, verb=-40), fcue(0, engine, -17, verb=-24), cue(0.05, "air", -18, dur=1.6)]
cues += [cue(1.0 + k * 0.12, "key_tap", -24, 0.5) for k in range(3)]                                   # the HUD clicks on
cues += [fcue(1.25 * BAR + k * BEAT / 2, ping, -20, -0.6) for k in range(3)]                            # 3 blips on the radar
cues += [cue(1.25 * BAR + BEAT / 2, "press", -18, -0.5)]
cues += [cue(A["m1_title"] + (k + 0.5) * BEAT, "glass_tick", -18, 0, degree=k + 2) for k in range(3)]    # 3 windows light
cues += [cue(A["m1_title"] + 1.5 * BEAT, "air", -16, dur=0.6), cue(A["m1_title"] + 1.5 * BEAT, "felt_thump", -12)]
cues += [cue(T_MOUNT, "felt_thump", -14), cue(A["m1_start"] + BEAT, "press", -20)]
cues += [cue(T_EDGE, "air", -14, dur=1.1), cue(T_LAND, "sub_drop", -10), cue(T_LAND, "felt_thump", -8), fcue(T_LAND + 0.05, squeal, -24, 0.2)]
cues += [fcue(T_CROSS - 1.3, bell, -16, 0.3), fcue(T_CROSS - 1.0, bell, -17, 0.3), cue(T_CROSS - 0.15, "air", -12, 0.5, dur=0.5)]
cues += [fcue(T_BRAKE, squeal, -15, 0.2)]
cues += [cue(A["m1_pass"] + 2 * BEAT, "sub_drop", -10), cue(A["m1_pass"] + 2.6 * BEAT, "press", -20)]
cues += [cue(A["m2_title"], "typing", -22, chars=60, cps=16), cue(A["m2_title"], "air", -18, dur=2.5)]   # the clock spins
cues += [fcue(A["m2_title"] + BEAT, pager, -16, -0.5), cue(A["m2_title"] + 2 * BEAT, "air", -16, dur=0.6)]
cues += [fcue(A["tail"] + 1.62, alarm, -20, 0.5)]
cues += [cue(A["night"], "air", -16, dur=0.5), fcue(A["night"] + 0.4, bell, -20, 0), fcue(A["night"] + 0.7, bell, -21, 0)]
cues += [cue(A["morning"], "air", -16, dur=0.5)]
cues += [cue(A["m2_pass"] + 0.6, "wood_knock", -16), cue(A["m2_pass"] + BEAT, "glass_tick", -16, degree=4), cue(A["m2_pass"] + 2 * BEAT, "sub_drop", -10)]
cues += [cue(A["close"] + i * BEAT / 2, "glass_tick", -22, -0.6 + 0.1 * i, degree=i % 7) for i in range(12)]   # the city lights violet
cues += [cue(A["close"] + 3 * BEAT, "lock", -14), cue(A["close"] + 4 * BEAT, "arrive", -18, degree=0)]
json.dump({"duration": round(END + 1, 3), "key": "C", "cues": cues}, open("sfx/cues.json", "w"), indent=1)
subprocess.run([PY, os.path.join(REPO, "skills/launch-sound/scripts/sfx_forge.py"), "render", "sfx/cues.json", "sfx/sfx.wav"], check=True)
music = F["music"]["file"]
if not os.path.exists(music):
    subprocess.run([PY, F["music"]["make"], "--out", music], check=True)
os.makedirs("mix", exist_ok=True)
video = "renders/picture.mp4"
cfg = {"duration": round(END, 3), "out": os.path.abspath("mix/master.wav"),
       "music": {"file": os.path.abspath(music), "gain_db": F["music"].get("gain_db", -1), "start": 0.0, "offset": 0.0, "fade_out": F["music"].get("fade_out", 1.0)},
       "sfx": {"file": os.path.abspath("sfx/sfx.wav"), "gain_db": 0}, "target_lufs": -14.0, "ceiling_dbtp": -3.2}
if os.path.exists(video):
    cfg.update({"video": os.path.abspath(video), "video_out": os.path.abspath("renders/full.mp4")})
json.dump(cfg, open("mix/mix.json", "w"), indent=1)
subprocess.run([PY, os.path.join(REPO, "skills/launch-mix/scripts/mixdown.py"), "mix/mix.json"], check=True)
if os.path.exists(video):
    name = os.path.basename(HERE)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "renders/full.mp4", "-c:v", "libx264", "-preset", "slow", "-crf", "20",
                    "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", f"renders/{name}.mp4"], check=True)
    os.remove("renders/full.mp4")
    print(f"master: {os.path.basename(os.path.dirname(HERE))}/{name}/renders/{name}.mp4")
