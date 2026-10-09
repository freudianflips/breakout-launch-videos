#!/usr/bin/env python3
"""Sound for 'Signal in. Meeting out.': the cue sheet from film.json (sound-forge palette), the scratch
track, the -14 LUFS master and the mux onto renders/signal-picture.mp4.

  .venv/bin/python templates/swiss-grid/audio.py
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
END = F["bars"] * BAR

os.makedirs("sfx", exist_ok=True)
cues = [{"t": round(c["at"] * BAR, 4), "sound": c["sound"], "gain_db": c.get("gain_db", -10), "args": c.get("args", {}), "pan": c.get("pan", 0)} for c in F["sfx"]]
json.dump({"duration": round(END + 1, 3), "key": "E", "cues": cues}, open("sfx/cues.json", "w"), indent=1)
subprocess.run([PY, os.path.join(REPO, "skills/launch-sound/scripts/sfx_forge.py"), "render", "sfx/cues.json", "sfx/sfx.wav"], check=True)
bed = F["music"]["file"]
if not os.path.exists(bed):
    subprocess.run([PY, "bed.py", "--out", bed], check=True)
os.makedirs("mix", exist_ok=True)
video = "renders/signal-picture.mp4"
cfg = {"duration": round(END, 3), "out": os.path.abspath("mix/master.wav"),
       "music": {"file": os.path.abspath(bed), "gain_db": F["music"].get("gain_db", -2), "start": 0.0, "offset": 0.0, "fade_out": F["music"].get("fade_out", 2.0)},
       "sfx": {"file": os.path.abspath("sfx/sfx.wav"), "gain_db": -1}, "target_lufs": -14.0, "ceiling_dbtp": -2.6}
if os.path.exists(video):
    cfg.update({"video": os.path.abspath(video), "video_out": os.path.abspath("renders/signal-full.mp4")})
json.dump(cfg, open("mix/mix.json", "w"), indent=1)
subprocess.run([PY, os.path.join(REPO, "skills/launch-mix/scripts/mixdown.py"), "mix/mix.json"], check=True)
if os.path.exists(video):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "renders/signal-full.mp4", "-c:v", "libx264", "-preset", "slow", "-crf", "20",
                    "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", "renders/signal.mp4"], check=True)
    os.remove("renders/signal-full.mp4")
    print("master: " + os.path.join(os.path.basename(os.path.dirname(HERE)), os.path.basename(HERE), "renders/signal.mp4"))
