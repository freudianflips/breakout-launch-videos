#!/usr/bin/env python3
"""The voices: one take per CJ and Sarah line in Tail the Champion, spoken by Kokoro-82M (Apache 2.0: open weights and
voices, fine to publish), into vo/<key>.mp3 and vo/vo.json, which build.py inlines.

  KOKORO=/path/to/kokoro ESPEAK_DATA_PATH=/short/path/espeak-ng-data python3 voice.py

KOKORO holds kokoro-v1.0.onnx, voices-v1.0.bin (github.com/thewh1teagle/kokoro-onnx, release model-files-v1.0) and a
venv with kokoro-onnx and soundfile. ESPEAK_DATA_PATH points at the venv's espeakng_loader/espeak-ng-data through a
short path (a symlink): espeak-ng ignores long ones. The lines are read from game.src.html itself (node runs its
script() for every account), so the words on screen and the words spoken never drift. Unchanged lines keep their take.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "vo")
CAST = {"CJ": ("am_fenrir", 1.0), "Sarah": ("af_heart", 1.0)}      # Kokoro voice and speed per character
SAY = [(" St.", " Street.")]                                       # how to say what is written

src = open(os.path.join(HERE, "game.src.html")).read()
js = src[src.index("  var TARGETS = ["):src.index("  var TXT = {")].replace("__VO__", "{}")
probe = js + """
function timed(l) { return l; }
var seen = {}, out = [];
FIDI.forEach(function (a) { FIDI.forEach(function (f) { var w = script(a, f, ANTHROPIC);
  ["alert", "intro", "door", "room"].forEach(function (k) { w.m2[k].forEach(function (l) { var tm = typeof l[0] === "number", who = tm ? l[2] : l[0], line = tm ? l[3] : l[1];
    if ((who === "CJ" || who === "Sarah") && !seen[who + "|" + line]) { seen[who + "|" + line] = 1; out.push([who, line]); } }); }); }); });
console.log(JSON.stringify(out));"""
lines = json.loads(subprocess.run(["node", "-e", probe], capture_output=True, text=True, check=True).stdout)


def key(who, line):
    return hashlib.sha1((who + "|" + line).encode()).hexdigest()[:10]


os.makedirs(OUT, exist_ok=True)
todo = [(w, l) for w, l in lines if not os.path.exists(os.path.join(OUT, key(w, l) + ".mp3"))]
if todo:
    K = os.environ.get("KOKORO")
    if not K:
        sys.exit("set KOKORO and ESPEAK_DATA_PATH (see the docstring)")
    speak = """
import json, sys, soundfile as sf
from kokoro_onnx import Kokoro
k = Kokoro(sys.argv[1] + '/kokoro-v1.0.onnx', sys.argv[1] + '/voices-v1.0.bin')
for line, voice, speed, wav in json.loads(sys.argv[2]):
    a, sr = k.create(line, voice=voice, speed=speed, lang='en-us'); sf.write(wav, a, sr)
"""
    def said(l):
        for x, y in SAY:
            l = l.replace(x, y)
        return l
    job = [[said(l), CAST[w][0], CAST[w][1], os.path.join(OUT, key(w, l) + ".wav")] for w, l in todo]
    subprocess.run([os.path.join(K, "venv", "bin", "python"), "-c", speak, K, json.dumps(job)], check=True)
    for w, l in todo:                                              # trim, level to -16 LUFS, a little room, mp3
        base = os.path.join(OUT, key(w, l))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", base + ".wav", "-af",
                        "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
                        "highpass=f=90,loudnorm=I=-16:TP=-1.5:LRA=7,aecho=0.8:0.5:28:0.12",
                        "-ar", "24000", "-ac", "1", "-c:a", "libmp3lame", "-b:a", "48k", base + ".mp3"], check=True)
        os.remove(base + ".wav")
manifest = {}
for w, l in lines:
    f = os.path.join(OUT, key(w, l) + ".mp3")
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f], capture_output=True, text=True, check=True).stdout)
    manifest[w + "|" + l] = {"file": os.path.basename(f), "d": round(d, 3), "voice": CAST[w][0]}
keep = {m["file"] for m in manifest.values()}
for f in os.listdir(OUT):
    if f.endswith(".mp3") and f not in keep:
        os.remove(os.path.join(OUT, f))
json.dump(manifest, open(os.path.join(OUT, "vo.json"), "w"), indent=1, ensure_ascii=False)
print(f"voice: {len(manifest)} lines ({len(todo)} new) in vo/")
