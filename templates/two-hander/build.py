#!/usr/bin/env python3
"""Build the two-hander animatic or film: film.json + the cast stills + the voice lines + brand.json -> a HyperFrames project.

  python3 build.py            # -> index.html, compositions/two.html, assets/, timing.json

Timing comes from the voice lines: each line starts after the one before it plus its gap (film "gap" by default),
and each beat adds its own gap first. A line's "frame" cuts the picture when the line starts: "two" (the 2-shot),
"breakout" or "piper" (their single). A beat can carry a claim card (verbatim, with the source line), the name tags,
or Sarah crossing behind them. Everything on screen is markup over the stills; every frame is a pure function of t.
Missing cast stills are fetched again from cast/jobs.json. "cutouts" are mattes made here from stills on white
(free, deterministic): Sarah, and the pair cut out of the 2-shot so she can cross behind them.
"""
import html
import json
import os
import re
import shutil
import subprocess
import urllib.request

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as nd

HERE = os.path.dirname(os.path.abspath(__file__))
F = json.load(open(os.path.join(HERE, "film.json")))
BRAND_DIR = os.path.normpath(os.path.join(HERE, F["brand"]))
BRAND = json.load(open(os.path.join(BRAND_DIR, "brand.json")))
E = html.escape
A = "assets"


def kw(text):
    return re.sub(r"\*(.+?)\*", r"<em>\1</em>", E(text))


def dur(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path], capture_output=True, text=True).stdout
    return float(out) if out.strip() else None


# ------------------------------------------------------------------ assets
if os.path.exists(os.path.join(HERE, A)):
    shutil.rmtree(os.path.join(HERE, A))
os.makedirs(os.path.join(HERE, A, "fonts"))
jobs_path = os.path.join(HERE, "cast", "jobs.json")
jobs = json.load(open(jobs_path)) if os.path.exists(jobs_path) else {}
for key, rel in F["cast"].items():
    src = os.path.join(HERE, rel)
    if not os.path.exists(src):
        name = os.path.splitext(os.path.basename(rel))[0]
        if name not in jobs:
            raise SystemExit(f"missing {rel} and no job for {name!r} in cast/jobs.json")
        urllib.request.urlretrieve(jobs[name]["url"], src)
    shutil.copy(src, os.path.join(HERE, A, f"{key}.png"))


def cutout(src, dst):
    """Matte a person off a near-white seamless: unsaturated pixels near the border colour that touch the edge are backdrop."""
    im = Image.open(src).convert("RGB")
    a = np.asarray(im).astype(np.int16)
    bg = np.median(np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]]), axis=0)
    near = (np.abs(a - bg).max(axis=2) < 55) & (a.max(axis=2) - a.min(axis=2) < 14)
    lab, _ = nd.label(near)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    fg = nd.binary_fill_holes(nd.binary_opening(~np.isin(lab, list(edge)), iterations=2))
    keep, k = nd.label(fg)
    sizes = nd.sum(fg, keep, range(1, k + 1))
    fg = np.isin(keep, [i + 1 for i, n in enumerate(sizes) if n > 0.01 * fg.size])
    im.putalpha(Image.fromarray((fg * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5)))
    im.save(dst)


for key, rel in F.get("cutouts", {}).items():
    cutout(os.path.join(HERE, rel), os.path.join(HERE, A, f"{key}.png"))
fontfaces = []
for role in ("body", "mono", "display"):
    f = BRAND["fonts"][role]
    for face in f.get("faces", []):
        shutil.copy(os.path.join(BRAND_DIR, face["file"]), os.path.join(HERE, A, face["file"]))
        src, family = f'url("{A}/{face["file"]}") format("woff2")', f["family"]
        if role == "display":     # New Kansas first, wherever it is installed
            family = "NK"
            src = ", ".join(f'local("{n}")' for n in f.get("local", [])) + ", " + src
        fontfaces.append(f'@font-face {{ font-family: "{family}"; src: {src}; font-weight: {face["weight"]}; font-style: {face.get("style", "normal")}; }}')
shutil.copy(os.path.join(BRAND_DIR, BRAND["logo"]["file"]), os.path.join(HERE, A, "logo.svg"))
gsap = os.path.join(HERE, "..", "..", "node_modules", "gsap", "dist", "gsap.min.js")
GSAP = "https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"
if os.path.exists(gsap):
    shutil.copy(gsap, os.path.join(HERE, A, "gsap.min.js"))
    GSAP = f"{A}/gsap.min.js"

# ------------------------------------------------------------------ timing
# Two ways in: 1 file per line (placed with gaps), or 1 dialogue track generated as a conversation (film "dialogue"),
# where each line carries "at": [start, end] in the track (from word timings) and the track plays from lead_in.
DLG = F.get("dialogue")
t = F["lead_in"]
lines, beats, cuts = [], [], []
for b in F["beats"]:
    if lines and not DLG:
        t += b.get("gap", F["gap"])
    b0 = None
    for i, ln in enumerate(b["lines"]):
        if DLG:
            s0, s1 = F["lead_in"] + ln["at"][0], F["lead_in"] + ln["at"][1]
            rec = {**ln, "beat": b["beat"], "start": round(s0, 3), "end": round(s1, 3)}
            t = s1
        else:
            if i:
                t += ln.get("gap", F["gap"])
            elif "gap" in ln:
                t += ln["gap"]
            wav = os.path.join(HERE, F["voices"][ln["who"]]["dir"], f"line-{ln['line']}.wav")
            d = (dur(wav) if os.path.exists(wav) else None) or ln["dur"]
            rec = {**ln, "beat": b["beat"], "start": round(t, 3), "end": round(t + d, 3), "wav": os.path.relpath(wav, HERE)}
            t += d
        lines.append(rec)
        b0 = rec["start"] if b0 is None else b0
        cut = max(rec["start"] - 0.12, 0) if cuts else 0
        if not cuts or cuts[-1]["frame"] != ln["frame"]:
            cuts.append({"frame": ln["frame"], "start": round(cut, 3)})
    beats.append({**{k: v for k, v in b.items() if k != "lines"}, "start": round(b0, 3), "end": round(t, 3)})
END0 = round(t + F["tail"], 3)
TOTAL = round(END0 + F["end"]["hold"], 3)
for i, c in enumerate(cuts):
    c["end"] = cuts[i + 1]["start"] if i + 1 < len(cuts) else END0
T = {"lines": lines, "beats": beats, "cuts": cuts, "end": END0, "total": TOTAL}
if DLG:
    T["dialogue"] = {"file": DLG["file"], "at": F["lead_in"]}
json.dump(T, open(os.path.join(HERE, "timing.json"), "w"), indent=1)

# ------------------------------------------------------------------ markup
claims = ""
for b in beats:
    c = b.get("claim")
    if not c:
        continue
    note = f'<div class="cnote">{E(c["note"])}</div>' if c.get("note") else ""
    claims += (f'<div class="claim" id="claim{b["beat"]}"><div class="clab mono">{E(c["label"])}</div>'
               f'<div class="crow b"><span>Breakout</span><b>{E(c["breakout"])}</b></div>'
               f'<div class="crow q"><span>Qualified</span><b>{E(c["piper"])}</b></div>{note}</div>')
lowers = "".join(f'<div class="lower{"" if b["lower"].get("text") else " note"}" id="lower{b["beat"]}">'
                 + (f'<b>{E(b["lower"]["text"])}</b>' if b["lower"].get("text") else "")
                 + (f'<span class="mono">{E(b["lower"]["note"])}</span>' if b["lower"].get("note") else "") + '</div>'
                 for b in beats if b.get("lower"))
subs = "".join(f'<div class="sub" id="sub{i}"><span>{E(ln["text"])}</span></div>' for i, ln in enumerate(lines)) if F.get("subtitles") else ""
tags = (f'<div class="tag" id="tagB">{E(F["names"]["breakout"])}</div><div class="tag" id="tagP">{E(F["names"]["piper"])}</div>')
tpl = open(os.path.join(HERE, "template.html")).read()
rep = {"__FONTFACES__": "\n        ".join(fontfaces), "__CLAIMS__": claims, "__SUBS__": subs, "__TAGS__": tags + lowers,
       "__SOURCE__": E(F.get("source", "")), "__ENDLINE__": kw(F["end"]["line"]), "__T__": json.dumps(T)}
for k, v in rep.items():
    tpl = tpl.replace(k, v)
os.makedirs(os.path.join(HERE, "compositions"), exist_ok=True)
open(os.path.join(HERE, "compositions", "two.html"), "w").write(tpl)
open(os.path.join(HERE, "index.html"), "w").write(f'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <title>{E(F["title"])}</title>
    <script src="{GSAP}"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1920px; height: 1080px; overflow: hidden; background: #fff; }}
      #main {{ position: relative; width: 1920px; height: 1080px; overflow: hidden; }}
      [data-composition-id="main"] > div[data-composition-src] {{ position: absolute; inset: 0; }}
    </style>
  </head>
  <body>
    <div id="main" data-composition-id="main" data-start="0" data-duration="{TOTAL:.3f}" data-width="1920" data-height="1080">
      <div id="el-two" data-composition-id="two" data-composition-src="compositions/two.html" data-start="0" data-duration="{TOTAL:.3f}" data-track-index="1"></div>
    </div>
    <script>
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
''')
print(f"{F['title']}: {len(lines)} lines, {len(cuts)} shots, {TOTAL:.2f} s")
