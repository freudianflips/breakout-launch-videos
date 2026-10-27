#!/usr/bin/env python3
"""Lay the voice lines at their times (timing.json), master to -14 LUFS and -1 dBTP, and mux onto the picture.

  python3 audio.py      # renders/picture.mp4 + the lines -> renders/two-hander.mp4

Dialogue only: dry voices on a quiet room tone, no music under the words (the storyboard's choice).
"""
import json
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
T = json.load(open(os.path.join(HERE, "timing.json")))
R = os.path.join(HERE, "renders")
os.makedirs(R, exist_ok=True)

ins, chain = [], []
for i, l in enumerate(T["lines"]):
    ins += ["-i", os.path.join(HERE, l["wav"])]
    ms = int(round(l["start"] * 1000))
    chain.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=mono,adelay={ms}[v{i}]")
n = len(T["lines"])
ins += ["-f", "lavfi", "-t", f"{T['total']:.3f}", "-i", "anoisesrc=color=brown:amplitude=0.0025:sample_rate=48000"]
chain.append(f"[{n}:a]lowpass=f=900,aformat=channel_layouts=mono[room]")
mix = "".join(f"[v{i}]" for i in range(n)) + "[room]"
chain.append(f"{mix}amix=inputs={n + 1}:normalize=0,apad,atrim=0:{T['total']:.3f},pan=stereo|c0=c0|c1=c0[out]")
raw = os.path.join(R, "mix-raw.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(chain), "-map", "[out]", "-ar", "48000", raw], check=True)


def lufs(path):
    log = subprocess.run(["ffmpeg", "-nostats", "-i", path, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", log)[-1])


# a static gain to -14 LUFS, then a -3.2 dB brickwall so the AAC encode stays under -1 dBTP
gain = -14.0 - lufs(raw)
wav = os.path.join(R, "mix.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", f"volume={gain:.2f}dB,alimiter=limit=0.69:level=disabled", wav], check=True)
pic = os.path.join(R, "picture.mp4")
out = os.path.join(R, "two-hander.mp4")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", pic, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)
print(f"mixed: {os.path.relpath(out, HERE)}")
