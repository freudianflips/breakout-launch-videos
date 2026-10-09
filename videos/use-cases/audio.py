#!/usr/bin/env python3
"""Sound for a kinetic film: sound cues generated from the timeline in timing.json (a swish on every colour
flood, a tick on every product moment, hits for the meeting and the chips), the score, the -14 LUFS master
and the mux onto renders/picture.mp4.

  .venv/bin/python audio.py        (from this folder; build.py writes timing.json first)
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
AT = json.load(open("timing.json"))
BAR = 240 / F["bpm"]
END = AT["end"] * BAR
L = F["beat_bars"]


def cue(at, sound, gain, **args):
    return {"t": round(at * BAR, 4), "sound": sound, "gain_db": gain, "args": args, "pan": 0}


cues = [cue(0.25, "arrive", -15, degree=0), cue(1.03, "press", -9)]
for i, s in enumerate(AT["beats"]):
    cues += [cue(s, "air", -14, dur=0.35), cue(s, "felt_thump", -10), cue(s + 0.55 * L, "glass_tick", -13, degree=[0, 2, 4, 5][i % 4])]
cues += [cue(AT["booked"], "sub_drop", -6), cue(AT["booked"], "logo_sting", -8), cue(AT["booked"] + 0.25, "lock", -11)]
cues += [cue(AT["personas"] + 0.05 + j * 0.25, "felt_thump", -7) for j in range(len(F["personas"]["words"]))]
cues += [cue(AT["lockup"], "arrive", -13, degree=0)]
os.makedirs("sfx", exist_ok=True)
json.dump({"duration": round(END + 1, 3), "key": "E", "cues": cues}, open("sfx/cues.json", "w"), indent=1)
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
