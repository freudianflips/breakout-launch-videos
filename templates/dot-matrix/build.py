#!/usr/bin/env python3
"""Build a dot-matrix film: film.json + brand.json -> index.html and compositions/dots.html.

  python3 build.py

Everything on screen is one grid of dots drawn on a canvas by template.html; the logo is drawn from the
brand SVG's paths (embedded here) and the words from the brand fonts, then sampled onto the grid.
"""
import html
import json
import os
import re
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
F = json.load(open("film.json"))
BRAND_DIR = os.path.normpath(os.path.join(HERE, F.get("brand", "../../brand")))
BRAND = json.load(open(os.path.join(BRAND_DIR, "brand.json")))
BAR = 240 / F["bpm"]
END = F["bars"] * BAR
E = html.escape

A = "assets"
if os.path.exists(A):
    shutil.rmtree(A)
os.makedirs(f"{A}/fonts")
fontfaces = []
for role in ("body", "mono", "display"):
    f = BRAND["fonts"][role]
    for face in f.get("faces", []):
        shutil.copy(os.path.join(BRAND_DIR, face["file"]), os.path.join(A, face["file"]))
        src, family = f'url("{A}/{face["file"]}") format("woff2")', f["family"]
        if role == "display":
            family = "NK"
            src = ", ".join(f'local("{n}")' for n in f.get("local", [])) + ", " + src
        fontfaces.append(f'@font-face {{ font-family: "{family}"; src: {src}; font-weight: {face["weight"]}; font-style: {face.get("style", "normal")}; }}')
gsap = os.path.join(HERE, "..", "..", "node_modules", "gsap", "dist", "gsap.min.js")
GSAP = "https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"
if os.path.exists(gsap):
    shutil.copy(gsap, f"{A}/gsap.min.js")
    GSAP = f"{A}/gsap.min.js"

svg = open(os.path.join(BRAND_DIR, BRAND["logo"]["on_dark"])).read()
vb = [float(x) for x in re.search(r'viewBox="([^"]+)"', svg).group(1).split()]
paths = [[re.search(r'fill="([^"]+)"', m.group(0)).group(1), re.sub(r"\s+", " ", re.search(r'd="([^"]+)"', m.group(0)).group(1))]
         for m in re.finditer(r"<path[^>]*>", svg)]


def kw(text):
    return re.sub(r"\*(.+?)\*", r"<em>\1</em>", E(text))


cfg = {"bpm": F["bpm"], "bars": F["bars"], "at": F["at"], "colors": F["colors"], "game": F["game"],
       "caps": [[c["at"], c["until"]] for c in F["captions"]],
       "booked": [[re.sub(r"\*", "", l), l.startswith("*")] for l in F["booked"]["lines"]],
       "logo": {"vb": vb, "paths": paths}}
rep = {
    "__FONTFACES__": "\n        ".join(fontfaces),
    "__CAPTIONS__": "".join(f'<div class="cap"><i></i>{E(c["text"])}</div>' for c in F["captions"]),
    "__LOCK__": kw(F["lockup"]["line"]),
    "__T__": json.dumps(cfg),
}
tpl = open("template.html").read()
for k, v in rep.items():
    tpl = tpl.replace(k, v)
os.makedirs("compositions", exist_ok=True)
open("compositions/dots.html", "w").write(tpl)
open("index.html", "w").write(f'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <title>Breakout: dot matrix</title>
    <script src="{GSAP}"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1920px; height: 1080px; overflow: hidden; background: #000; }}
      #main {{ position: relative; width: 1920px; height: 1080px; overflow: hidden; }}
      [data-composition-id="main"] > div[data-composition-src] {{ position: absolute; inset: 0; }}
    </style>
  </head>
  <body>
    <div id="main" data-composition-id="main" data-start="0" data-duration="{END:.3f}" data-width="1920" data-height="1080">
      <div id="el-d" data-composition-id="dotfilm" data-composition-src="compositions/dots.html" data-start="0" data-duration="{END:.3f}" data-track-index="1"></div>
    </div>
    <script>
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
''')
print(f"dot-matrix: {END:.2f} s, {F['bars']} bars at {F['bpm']} BPM")
