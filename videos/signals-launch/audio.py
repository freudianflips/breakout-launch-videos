#!/usr/bin/env python3
"""Sound for the Signals launch: cues generated from film.json "at" (sound-forge palette), the upbeat score, the -14 LUFS master and the mux onto renders/picture.mp4.

  .venv/bin/python audio.py   (from this folder)
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

AT = F["at"]


def cue(bar, sound, gain, pan=0, **args):
    return {"t": round(bar * BAR, 4), "sound": sound, "gain_db": gain, "args": args, "pan": pan}


cues = [cue(0.12, "air", -18, 0.6, dur=0.4), cue(AT["land"], "felt_thump", -11), cue(AT["land"], "press", -14), cue(AT["listen"], "arrive", -15, degree=2)]
for k, c in enumerate(AT["signals"]):
    cues += [cue(c, "key_tap", -20, 0.2), cue(c + AT["load"], "glass_tick", -15, 0.2, degree=k + 2)]
cues += [cue(AT["act"], "felt_thump", -10), cue(AT["act"], "press", -14)]
cues += [cue(AT["agent"], "felt_thump", -12), cue(AT["agent"], "arrive", -16, 0.3, degree=4), cue(AT["type"][0], "typing", -22, -0.1, dur=round((AT["type"][1] - AT["type"][0]) * BAR, 2)), cue(AT["reply"], "press", -15)]
cues += [cue(AT["email"], "felt_thump", -12), cue(AT["email"], "air", -15, -0.6, dur=0.3), cue(AT["body"][0], "typing", -22, -0.2, dur=round((AT["body"][1] - AT["body"][0]) * BAR, 2)), cue(AT["sent"], "logo_sting", -14)]
cues += [cue(AT["close"], "sub_drop", -10), cue(AT["close"], "arrive", -16, degree=0)]
os.makedirs("sfx", exist_ok=True)
json.dump({"duration": round(END + 1, 3), "key": "F", "cues": cues}, open("sfx/cues.json", "w"), indent=1)
subprocess.run([PY, os.path.join(REPO, "skills/launch-sound/scripts/sfx_forge.py"), "render", "sfx/cues.json", "sfx/sfx.wav"], check=True)
bed = F["music"]["file"]
if not os.path.exists(bed):
    subprocess.run([PY, "score.py", "--out", bed], check=True)
os.makedirs("mix", exist_ok=True)
video = "renders/picture.mp4"
cfg = {"duration": round(END, 3), "out": os.path.abspath("mix/master.wav"),
       "music": {"file": os.path.abspath(bed), "gain_db": F["music"].get("gain_db", -2), "start": 0.0, "offset": 0.0, "fade_out": F["music"].get("fade_out", 2.0)},
       "sfx": {"file": os.path.abspath("sfx/sfx.wav"), "gain_db": -1}, "target_lufs": -14.0, "ceiling_dbtp": -2.6}
if os.path.exists(video):
    cfg.update({"video": os.path.abspath(video), "video_out": os.path.abspath("renders/full.mp4")})
json.dump(cfg, open("mix/mix.json", "w"), indent=1)
subprocess.run([PY, os.path.join(REPO, "skills/launch-mix/scripts/mixdown.py"), "mix/mix.json"], check=True)
if os.path.exists(video):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "renders/full.mp4", "-c:v", "libx264", "-preset", "slow", "-crf", "20",
                    "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", "renders/signals-launch.mp4"], check=True)
    os.remove("renders/full.mp4")
    print("master: " + os.path.join(os.path.basename(os.path.dirname(HERE)), os.path.basename(HERE), "renders/signals-launch.mp4"))
