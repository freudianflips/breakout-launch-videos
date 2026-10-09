#!/usr/bin/env python3
"""Sound for a dot-matrix film: small synthesised cues on the picture's events (a tick per hop, a pop per bloom,
a soft tap per snake step, the shockwave), the jazz score, the -14 LUFS master and the mux onto renders/picture.mp4.

  .venv/bin/python audio.py        (from this folder, after build.py and the picture render)
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
PY = sys.executable
F = json.load(open("film.json"))
BAR = 240 / F["bpm"]
BEAT = BAR / 4
A = {k: v * BAR for k, v in F["at"].items()}
END = A["end"]


def cue(t, sound, gain, pan=0, **args):
    return {"t": round(t, 4), "sound": sound, "gain_db": gain, "args": args, "pan": pan}


cues = [cue(0.05, "air", -22, dur=0.8)]
cues += [cue(k * BEAT, "glass_tick", -20, -0.5 + k * 0.1, degree=k) for k in (1, 2, 3)]                   # the grey bloom hops in
cues += [cue(A["seen"], "air", -18, dur=0.45), cue(A["seen"] + 0.2, "arrive", -16, -0.2, degree=4)]       # the scan, the flip
cues += [cue(A["engage"], "felt_thump", -12, 0.2), cue(A["engage"], "press", -16, 0.2)]                    # Breakout pops in
cues += [cue(A["engage"] + b * BEAT, "orbit_tick", -22, 0.25 if b % 2 else -0.25) for b in (1, 2, 3, 4, 5, 6, 7, 7.5)]
cues += [cue(A["rep"], "grow", -18, 0.6, dur=0.3), cue(A["rep"] + 0.25, "press", -16, 0.7)]
cues += [cue(A["rep"] + k * BEAT, "glass_tick", -20, 0.4, degree=5 + k) for k in (1, 2)]
cues += [cue(A["gone"], "glass_tick", -20, -0.4, degree=2), cue(A["gone"] + BEAT, "air", -18, -0.8, dur=0.5)]
cues += [cue(t, "air", -16, -0.6, dur=0.5) for t in (A["follow"], A["follow"] + 1.5 * BEAT)]
step = F["game"]["step"] * BAR
n = 0
while A["game"] + n * step < A["back"]:                                                                  # the snake's steps
    cues.append(cue(A["game"] + n * step, "key_tap", -27, 0.15))
    n += 1
cues += [cue(A["back"] + k * BEAT, "glass_tick", -18, -0.5 + 0.2 * k, degree=k + 3) for k in (0, 1, 2)]
cues += [cue(A["back"] + BEAT, "felt_thump", -12)]
cues += [cue(A["booked"] + 0.18, "sub_drop", -8), cue(A["booked"] + 0.18, "logo_sting", -12), cue(A["booked"] + 0.5 * BAR, "typing", -20, dur=0.25)]
cues += [cue(A["close"] + BEAT, "lock", -14), cue(A["close"] + 3 * BEAT, "arrive", -18, degree=0)]
os.makedirs("sfx", exist_ok=True)
json.dump({"duration": round(END + 1, 3), "key": "D", "cues": cues}, open("sfx/cues.json", "w"), indent=1)
subprocess.run([PY, os.path.join(REPO, "skills/launch-sound/scripts/sfx_forge.py"), "render", "sfx/cues.json", "sfx/sfx.wav"], check=True)
music = F["music"]["file"]
if not os.path.exists(music):
    os.makedirs(os.path.dirname(music), exist_ok=True)
    subprocess.run([PY, F["music"]["make"], "--out", music], check=True)
os.makedirs("mix", exist_ok=True)
video = "renders/picture.mp4"
cfg = {"duration": round(END, 3), "out": os.path.abspath("mix/master.wav"),
       "music": {"file": os.path.abspath(music), "gain_db": F["music"].get("gain_db", -1), "start": 0.0, "offset": 0.0, "fade_out": F["music"].get("fade_out", 1.0)},
       "sfx": {"file": os.path.abspath("sfx/sfx.wav"), "gain_db": -1}, "target_lufs": -14.0, "ceiling_dbtp": -3.2}
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
