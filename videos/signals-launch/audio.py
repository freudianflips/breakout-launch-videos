#!/usr/bin/env python3
"""Sound for the Signals launch: small synthesised cues on the picture's events (a sparkle per signal, a tick per
library tile, pops for blooms, a whoosh per stream, the shockwave), the score, the -14 LUFS master and the mux.

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
A = {k: ([x * BAR for x in v] if isinstance(v, list) else v * BAR) for k, v in F["at"].items()}
END = A["end"]


def cue(t, sound, gain, pan=0, **args):
    return {"t": round(t, 4), "sound": sound, "gain_db": gain, "args": args, "pan": pan}


PANS = [-0.5, 0.5, 0.5, -0.5]                                    # the questions' motifs sit in the four corners
cues = [cue(0.05, "air", -22, dur=0.6), cue(0.15, "felt_thump", -14)]
cues += [cue(t, "arrive", -15, PANS[k], degree=k + 2) for k, t in enumerate(A["q"])]
cues += [cue(t + 0.05, "grow", -20, PANS[k], dur=0.25) for k, t in enumerate(A["q"])]
cues += [cue(A["turn"], "orbit_tick", -14), cue(A["turn"] + 0.3, "logo_sting", -14)]
cues += [cue(A["two"], "air", -16, dur=0.45), cue(A["two"] + 0.2, "press", -16, -0.4), cue(A["two"] + 0.2 + BEAT, "press", -16, 0.4)]
cues += [cue(A["sort"] + k * BEAT, "arrive", -15, 0.4, degree=4 + k) for k in (0, 1)]
cues += [cue(A["sort"] + 2.5 * BEAT, "sub_drop", -14, 0.3)]
cues += [cue(A["lib"] + i * BEAT / 4, "glass_tick", -20, -0.6 + 0.13 * i, degree=i % 5) for i in range(10)]
cues += [cue(A["hot"] + 0.1 + 0.03 * i, "key_tap", -26, -0.6 + 0.05 * i) for i in range(22)]
cues += [cue(A["hot"] + (1 + k) * BEAT, "felt_thump", -13, [-0.2, -0.5, 0.2][k]) for k in range(3)]
cues += [cue(A["rep"], "press", -16, 0.5), cue(A["rep"] + BEAT, "grow", -17, 0.3, dur=0.4), cue(A["rep"] + BEAT + 0.4, "lock", -15, 0.5)]
cues += [cue(A["agent"], "felt_thump", -13), cue(A["agent"] + 4.5 * BEAT, "air", -16, 0.6, dur=0.7)]
cues += [cue(A["run"] + k * 1.5 * BEAT, "air", -15, [-0.7, 0.7, 0.7][k], dur=0.6) for k in range(3)]
cues += [cue(A["same"], "sub_drop", -10), cue(A["same"], "lock", -14)]
cues += [cue(A["close"] + 0.2, "sub_drop", -8), cue(A["close"] + 0.2, "logo_sting", -12), cue(A["close"] + 2 * BEAT, "typing", -20, dur=0.4)]
cues += [cue(A["close"] + 4 * BEAT, "arrive", -18, degree=0)]
os.makedirs("sfx", exist_ok=True)
json.dump({"duration": round(END + 1, 3), "key": "F", "cues": cues}, open("sfx/cues.json", "w"), indent=1)
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
