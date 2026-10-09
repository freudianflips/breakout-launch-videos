#!/usr/bin/env python3
"""Sound for 1 ABM film: the cue sheet from series.json (sound-forge palette), the series score, the -14 LUFS
master and the mux onto out/<slug>/renders/picture.mp4.

  .venv/bin/python templates/abm-cinematic/audio.py korn-ferry
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
SLUG = sys.argv[1] if len(sys.argv) > 1 else "korn-ferry"
PY = sys.executable
F = json.load(open(os.path.join(HERE, "series.json")))
BAR = 240 / F["bpm"]
END = F["bars"] * BAR
OUT = os.path.join(HERE, "out", SLUG)

# the score and the sound effects are the same for every account: make them once
score = os.path.join(HERE, "out", F["music"]["file"])
if not os.path.exists(score):
    subprocess.run([PY, os.path.join(HERE, F["music"]["make"]), "--out", score], check=True)
sfx_dir = os.path.join(HERE, "out", "sfx")
os.makedirs(sfx_dir, exist_ok=True)


def at(x):
    """A cue time in bars: a number, or 'section+bars' (e.g. 'ask+0.5') so cues follow series.json "at"."""
    if isinstance(x, str):
        name, _, off = x.partition("+")
        return F["at"][name.strip()] + float(off or 0)
    return x


cues = [{"t": round(at(c["at"]) * BAR, 4), "sound": c["sound"], "gain_db": c.get("gain_db", -10), "args": c.get("args", {}), "pan": c.get("pan", 0)} for c in F["sfx"]]
json.dump({"duration": round(END + 1, 3), "key": "E", "cues": cues}, open(os.path.join(sfx_dir, "cues.json"), "w"), indent=1)
subprocess.run([PY, os.path.join(REPO, "skills/launch-sound/scripts/sfx_forge.py"), "render", os.path.join(sfx_dir, "cues.json"), os.path.join(sfx_dir, "sfx.wav")], check=True)

mix = os.path.join(OUT, "mix")
os.makedirs(mix, exist_ok=True)
video = os.path.join(OUT, "renders", "picture.mp4")
full = os.path.join(OUT, "renders", "full.mp4")
cfg = {"duration": round(END, 3), "out": os.path.join(mix, "master.wav"),
       "music": {"file": score, "gain_db": F["music"].get("gain_db", -1), "start": 0.0, "offset": 0.0, "fade_out": F["music"].get("fade_out", 1.0)},
       "sfx": {"file": os.path.join(sfx_dir, "sfx.wav"), "gain_db": -1}, "target_lufs": -14.0, "ceiling_dbtp": -3.2}
if os.path.exists(video):
    cfg.update({"video": video, "video_out": full})
json.dump(cfg, open(os.path.join(mix, "mix.json"), "w"), indent=1)
subprocess.run([PY, os.path.join(REPO, "skills/launch-mix/scripts/mixdown.py"), os.path.join(mix, "mix.json")], check=True)
if os.path.exists(video):
    final = os.path.join(OUT, "renders", f"breakout-for-{SLUG}.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", full, "-c:v", "libx264", "-preset", "slow", "-crf", "20",
                    "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", final], check=True)
    os.remove(full)
    print(f"master: {os.path.relpath(final, REPO)}")
