#!/usr/bin/env python3
"""The voices: one take per spoken line (people talking to each other, and the radio DJs; never CJ talking to
himself, which stays subtitles), into vo/<key>.mp3 and vo/vo.json, which build.py inlines.

  CHATTERBOX=/path/to/venv/bin/python python3 voice.py [--redo] [--line "some words" ...]

Resemble AI's Chatterbox (MIT) speaks each line in a character's voice, cloned zero-shot from vo/ref/<voice>.wav.
The references are Kokoro-82M preset voices (Apache 2.0), so every voice here is free to publish. The venv needs
chatterbox-tts, "transformers==4.46.3", "torchvision==0.21.0", "setuptools<81", soundfile and faster-whisper.
Each line gets 2 takes; whisper must hear the exact words, and the take nearest a natural pace wins.
The lines are read from game.src.html itself (node runs its script() for every account, plus DJ_LINES), so the
words on screen and the words spoken never drift. Unchanged lines keep their take; --redo re-records all, --line only those.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "vo")
# voice -> (reference, exaggeration, cfg weight): more exaggeration is more expressive, lower cfg is looser pacing
CAST = {"CJ": ("cj", 0.55, 0.4), "Sarah": ("sarah", 0.6, 0.4), "Team": ("team", 0.5, 0.45), "DJ": ("dj", 0.8, 0.3)}
SAY = [(" St.", " Street."), ("2 PM", "two P.M."), ("K-Pipe", "Kay Pipe")]                 # how to say what is written

src = open(os.path.join(HERE, "game.src.html")).read()
js = src[src.index("  var TARGETS = ["):src.index("  var TXT = {")].replace("__VO__", "{}")
probe = js + """
function timed(l) { return l; }
var seen = {}, out = [];
function add(who, line) { who = who === "CJ" || who === "Sarah" ? who : who === "DJ" ? "DJ" : "Team"; if (!seen[who + "|" + line]) { seen[who + "|" + line] = 1; out.push([who, line]); } }
FIDI.forEach(function (a) { FIDI.forEach(function (f) { var w = script(a, f, ANTHROPIC);
  [w.m1.door, w.m1.room, w.m2.room].forEach(function (list) { list.forEach(function (l) { var tm = typeof l[0] === "number", who = tm ? l[2] : l[0], line = tm ? l[3] : l[1];
    if (who !== "BREAKOUT") add(who, line); }); }); }); });
Object.keys(DJ_LINES).forEach(function (k) { DJ_LINES[k].forEach(function (l) { add("DJ", l); }); });
console.log(JSON.stringify(out));"""
lines = json.loads(subprocess.run(["node", "-e", probe], capture_output=True, text=True, check=True).stdout)


def key(who, line):
    return hashlib.sha1((who + "|" + line).encode()).hexdigest()[:10]


def said(line):
    for x, y in SAY:
        line = line.replace(x, y)
    return line


os.makedirs(OUT, exist_ok=True)
FRAGS = [sys.argv[i + 1] for i, x in enumerate(sys.argv) if x == "--line"]       # --line "words" re-records the lines containing them
todo = [(w, l) for w, l in lines if "--redo" in sys.argv or any(f in l for f in FRAGS) or not os.path.exists(os.path.join(OUT, key(w, l) + ".mp3"))]
if todo:
    PY = os.environ.get("CHATTERBOX")
    if not PY:
        sys.exit("set CHATTERBOX to the python of a venv with chatterbox-tts (see the docstring)")
    speak = r"""
import json, re, sys, numpy as np, soundfile as sf, torch
from chatterbox.tts import ChatterboxTTS
from faster_whisper import WhisperModel
m, asr = ChatterboxTTS.from_pretrained(device="cpu"), WhisperModel("base.en", device="cpu", compute_type="int8")
NUM = dict(zip("0 1 2 3 4 5 6 7 8 9 10 92.3".split(), "zero one two three four five six seven eight nine ten ninety-two-point-three".split()))
norm = lambda s: re.sub(r"[^a-z ]", "", " ".join(NUM.get(w, w) for w in re.sub(r"[,.!?;:](\s|$)", " ", s.lower()).replace("p.m", "pm").split()).replace("-", " ")).split()
for text, heard_as, ref, ex, cfg, wav in json.loads(sys.argv[1]):
    best = None
    for seed in (11, 23, 37, 51):
        torch.manual_seed(seed)
        a = m.generate(text, audio_prompt_path=ref, exaggeration=ex, cfg_weight=cfg, temperature=0.75).squeeze(0).numpy()
        x = np.interp(np.arange(0, len(a), m.sr / 16000), np.arange(len(a)), a).astype(np.float32)
        got = " ".join(s.text for s in asr.transcribe(x)[0])
        ok = norm(got) == norm(heard_as)
        pace = len(text.split()) / (len(a) / m.sr)
        score = (0 if ok else 10) + abs(pace - 2.7)
        print(("ok  " if ok else "MISS"), round(pace, 2), "w/s |", text, "|", got.strip(), flush=True)
        if best is None or score < best[0]:
            best = (score, a)
        if seed == 23 and best[0] < 10:                            # 2 takes, unless neither has the exact words
            break
    sf.write(wav, best[1], m.sr)
"""
    job = [[said(l), l, os.path.join(OUT, "ref", CAST[w][0] + ".wav"), CAST[w][1], CAST[w][2], os.path.join(OUT, key(w, l) + ".wav")] for w, l in todo]
    subprocess.run([PY, "-c", speak, json.dumps(job)], check=True)
    for w, l in todo:                                              # trim, level to -16 LUFS, mp3; the DJ through a radio
        base = os.path.join(OUT, key(w, l))
        fx = "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,highpass=f=90,"
        fx += "highpass=f=280,lowpass=f=4200,acompressor=threshold=-20dB:ratio=4,loudnorm=I=-17:TP=-1.5" if w == "DJ" else "loudnorm=I=-16:TP=-1.5:LRA=7"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", base + ".wav", "-af", fx, "-ar", "24000", "-ac", "1", "-c:a", "libmp3lame", "-b:a", "48k", base + ".mp3"], check=True)
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
