#!/usr/bin/env python3
"""Sound for a cartoon story: sound cues placed on the story's moments (film.json "at"), the score, the -14 LUFS
master and the mux onto renders/picture.mp4.

  .venv/bin/python audio.py        (from this folder)
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
AT = F["at"]
BAR = 240 / F["bpm"]
END = F["bars"] * BAR


def cue(at, sound, gain, **args):
    return {"t": round(at * BAR, 4), "sound": sound, "gain_db": gain, "args": args, "pan": 0}


seg = (AT["back"] - AT["lapse"]) / 3
cues = [cue(0.15, "arrive", -15, degree=0), cue(1.0, "press", -9), cue(1.15, "air", -14, dur=0.4),
        cue(AT["seen"], "air", -12, dur=0.6), cue(AT["seen"] + 0.4, "grow", -14, dur=1.0), cue(AT["seen"] + 0.95, "glass_tick", -10, degree=4),
        cue(AT["chat"], "arrive", -13, degree=2), cue(AT["chat"] + 0.2, "typing", -17, chars=24, cps=20), cue(AT["chat"] + 0.95, "glass_tick", -12, degree=2),
        cue(AT["rep"], "wood_knock", -8, degree=0), cue(AT["rep"] + 0.1, "wood_knock", -10, degree=0), cue(AT["rep"] + 0.25, "lock", -10),
        cue(AT["repjoin"] + 0.05, "glass_tick", -12, degree=0), cue(AT["repjoin"] + 0.25, "arrive", -15, degree=4),
        cue(AT["leave"] + 0.3, "air", -10, dur=0.5), cue(AT["leave"] + 0.35, "felt_thump", -10),
        cue(AT["research"], "arrive", -14, degree=0), cue(AT["research"] + 1.0, "glass_tick", -12, degree=0), cue(AT["research"] + 1.25, "glass_tick", -12, degree=2),
        cue(AT["research"] + 1.5, "glass_tick", -12, degree=4),
        cue(AT["follow"] + 0.2, "air", -13, dur=0.5), cue(AT["follow"] + 0.55, "lock", -11), cue(AT["follow"] + 1.1, "air", -13, dur=0.5), cue(AT["follow"] + 1.45, "lock", -11)]
for k in range(3):
    a = AT["lapse"] + k * seg
    cues += [cue(a, "felt_thump", -9), cue(a + 0.3, "glass_tick", -10, degree=[0, 2, 4][k]), cue(a + 0.7, "air", -13, dur=0.5), cue(a + 1.1, "lock", -12)]
cues += [cue(AT["back"], "felt_thump", -7), cue(AT["back"] + 0.6, "wood_knock", -9, degree=0), cue(AT["back"] + 0.7, "wood_knock", -10, degree=0),
         cue(AT["yes"], "arrive", -13, degree=2), cue(AT["yes"] + 1.0, "press", -8),
         cue(AT["booked"], "sub_drop", -6), cue(AT["booked"], "logo_sting", -8), cue(AT["booked"] + 0.4, "lock", -11),
         cue(AT["close"] + 1.0, "arrive", -13, degree=0)]
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
