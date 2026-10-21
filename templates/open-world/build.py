#!/usr/bin/env python3
"""Build an open-world film: film.json + brand.json -> index.html and compositions/world.html.

  python3 build.py

The world is drawn by three.js inside template.html (a low-poly city, the cast, the cameras), the HUD in HTML over it.
The words come from film.json and are written into the markup here; the radar's badge is the brand's b-disc mark.
"""
import base64
import html
import json
import os
import re
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
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
for role in ("body", "display"):
    f = BRAND["fonts"][role]
    for face in f.get("faces", []):
        shutil.copy(os.path.join(BRAND_DIR, face["file"]), os.path.join(A, face["file"]))
        src, family = f'url("{A}/{face["file"]}") format("woff2")', f["family"]
        if role == "display":
            family = "NK"
            src = ", ".join(f'local("{n}")' for n in f.get("local", [])) + ", " + src
        fontfaces.append(f'@font-face {{ font-family: "{family}"; src: {src}; font-weight: {face["weight"]}; font-style: {face.get("style", "normal")}; }}')
# the genre's display faces, both SIL Open Font License (fonts/*/OFL.txt)
for family, path in (("Bowlby", "fonts/bowlby-one/BowlbyOne-Regular.ttf"), ("Pirata", "fonts/pirata-one/PirataOne-Regular.ttf")):
    shutil.copy(path, f"{A}/fonts/{os.path.basename(path)}")
    fontfaces.append(f'@font-face {{ font-family: "{family}"; src: url("{A}/fonts/{os.path.basename(path)}") format("truetype"); }}')

libs = {}
for name, local, cdn in (("gsap", "gsap/dist/gsap.min.js", "https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"),
                         ("three", "three/build/three.min.js", "https://cdn.jsdelivr.net/npm/three@0.158.0/build/three.min.js")):
    p = os.path.join(ROOT, "node_modules", local)
    if os.path.exists(p):
        shutil.copy(p, f"{A}/{os.path.basename(p)}")
        libs[name] = f"{A}/{os.path.basename(p)}"
    else:
        libs[name] = cdn

logo = open(os.path.join(BRAND_DIR, BRAND["logo"]["on_dark"])).read()
logo = re.sub(r"<\?xml.*?\?>", "", logo).strip()
mark = base64.b64encode(open(os.path.join(BRAND_DIR, BRAND["logo"]["mark_on_dark"]), "rb").read()).decode()


def kw(text):
    return re.sub(r"\*(.+?)\*", r"<em>\1</em>", E(text))


def hi(parts):
    """[plain, highlighted, plain]: the middle part is the mission's key word, in lilac."""
    return "".join(f'<span class="hi">{E(p)}</span>' if i % 2 else E(p) for i, p in enumerate(parts))


text = []
for m in F["missions"]:
    tag, rest = m["help"][0].split(":", 1)
    text.append(f'<div class="help"><span class="tag">{E(tag)}:</span>{E(rest)}<br>{E(m["help"][1])}</div>')
    text.append(f'<div class="title">{E(m["title"])}</div>')
    text.append(f'<div class="obj ol">{hi(m["objective"])}</div>')
    text.append(f'<div class="pass"><b>{E(m["passed"])}</b><span class="ol">{E(m["result"])}</span></div>')
labels = "".join(f'<div class="label"><i></i>{E(F["labels"][k])}</div>' for k in ("committee", "champion", "new_account"))

cfg = {"bpm": F["bpm"], "bars": F["bars"], "at": F["at"], "missions": F["missions"], "days": F["days"], "signs": F["signs"], "mark": mark}
rep = {
    "__FONTFACES__": "\n        ".join(fontfaces),
    "__TEXT__": "\n        ".join(text),
    "__LABELS__": labels,
    "__TOO_CLOSE__": E(F["missions"][1]["too_close"]),
    "__LOGO__": logo,
    "__LOCK__": kw(F["lockup"]["line"]),
    "__T__": json.dumps(cfg),
}
tpl = open("template.html").read()
for k, v in rep.items():
    tpl = tpl.replace(k, v)
os.makedirs("compositions", exist_ok=True)
open("compositions/world.html", "w").write(tpl)
open("index.html", "w").write(f'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <title>Breakout: open world</title>
    <script src="{libs["gsap"]}"></script>
    <script src="{libs["three"]}"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1920px; height: 1080px; overflow: hidden; background: #000; }}
      #main {{ position: relative; width: 1920px; height: 1080px; overflow: hidden; }}
      [data-composition-id="main"] > div[data-composition-src] {{ position: absolute; inset: 0; }}
    </style>
  </head>
  <body>
    <div id="main" data-composition-id="main" data-start="0" data-duration="{END:.3f}" data-width="1920" data-height="1080">
      <div id="el-w" data-composition-id="world" data-composition-src="compositions/world.html" data-start="0" data-duration="{END:.3f}" data-track-index="1"></div>
    </div>
    <script>
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
''')
print(f"open-world: {END:.2f} s, {F['bars']} bars at {F['bpm']} BPM")
