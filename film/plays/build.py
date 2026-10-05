#!/usr/bin/env python3
"""Build the Plays launch film: film.json + brand.json -> index.html and compositions/plays.html (HyperFrames).

  python3 film/plays/build.py

Every cue sits on the bar grid (no narration). Words are written as markup here so they never fall back
to a serif; their landing times are written beside them. Writes timing.json for audio.py.
"""
import html
import json
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
FILM = json.load(open("film.json"))
BRAND_DIR = os.path.normpath(os.path.join(HERE, FILM.get("brand", "../../brand")))
BRAND = json.load(open(os.path.join(BRAND_DIR, "brand.json")))
BAR = 240 / FILM["bpm"]
BEAT = BAR / 4
END = FILM["bars"] * BAR
EIGHTH = BEAT / 2

# ------------------------------------------------------------------ assets the renderer can serve
ASSET = "assets"
if os.path.exists(ASSET):
    shutil.rmtree(ASSET)
os.makedirs(f"{ASSET}/fonts")
os.makedirs(f"{ASSET}/screens")
for role in ("display", "body"):
    for face in BRAND["fonts"][role].get("faces", []):
        shutil.copy(os.path.join(BRAND_DIR, face["file"]), os.path.join(ASSET, face["file"]))
shutil.copy(os.path.join(BRAND_DIR, BRAND["logo"]["on_dark"]), f"{ASSET}/logo-on-dark.svg")
SCREENS = {"new": "plays-new.png", "aud1": "plays-audience.png", "filt": "plays-filters.png", "aud2": "plays-audience.png",
           "pers": "plays-personalization.png", "dest": "plays-destination.png"}
for f in set(SCREENS.values()):
    shutil.copy(os.path.join(HERE, "..", "assets", "screens", f), f"{ASSET}/screens/{f}")
gsap = os.path.join(HERE, "..", "..", "node_modules", "gsap", "dist", "gsap.min.js")
GSAP_SRC = "https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"
if os.path.exists(gsap):
    shutil.copy(gsap, f"{ASSET}/gsap.min.js")
    GSAP_SRC = f"{ASSET}/gsap.min.js"

FONTFACES = []
for role in ("display", "body"):
    f = BRAND["fonts"][role]
    for face in f.get("faces", []):
        FONTFACES.append(f'@font-face {{ font-family: "{f["family"]}"; src: url("{ASSET}/{face["file"]}") format("woff2"); '
                         f'font-weight: {face["weight"]}; font-style: {face.get("style", "normal")}; }}')
disp = BRAND["fonts"]["display"]
SERIF = ", ".join(f'"{x}"' for x in disp.get("local", []) + [disp["family"]]) + ", Georgia, serif"
SANS = f'"{BRAND["fonts"]["body"]["family"]}", system-ui, sans-serif'


# ------------------------------------------------------------------ words
def words(text):
    """'Then they *dance for it.' -> [('Then', False), ..., ('dance', True), ...]"""
    return [(w.lstrip("*"), w.startswith("*")) for w in text.split()]


def spans(text, t0, step=EIGHTH):
    out = []
    for i, (w, k) in enumerate(words(text)):
        out.append(f'<span class="w{" k" if k else ""}" data-at="{t0 + i * step:.3f}">{html.escape(w)}</span>')
    return "".join(out)


EVENTS = []
paper_html = []
for p in FILM["paper"]:
    a, b = p["from"] * BAR, p["to"] * BAR
    for j, (text, at) in enumerate(p["rows"]):
        top = p["top"] + j * p["size"] * 1.12
        paper_html.append(f'<div class="prow serif" data-from="{a:.3f}" data-to="{b:.3f}" style="top:{top:.0f}px;font-size:{p["size"]}px">'
                          f'{spans(text, at * BAR)}</div>')

cap_html = []
for c in FILM["captions"]:
    t0 = c["from"] * BAR + 0.06
    rows = "".join(f'<div class="row serif {cls}">{spans(c["text"], t0)}</div>' for cls in ("e2", "e1", "main"))
    cap_html.append(f'<div class="cap" data-from="{c["from"]}" data-to="{c["to"]}">{rows}</div>')

tick_html = []
for k in FILM["tickers"]:
    items = "".join(f"<span>{html.escape(x)}</span>" for x in k["items"])
    tick_html.append(f'<div class="tick sans" data-from="{k["from"]}" data-to="{k["to"]}">{items}</div>')

m = FILM["meeting"]
meeting_html = "".join(f'<div class="big serif {cls}" style="top:430px;font-size:170px">{spans(m["text"], m["from"] * BAR + 0.05, BEAT)}</div>'
                       for cls in ("e2", "e1", "main"))
lk = FILM["lockup"]
line_html = spans(lk["line"], 0)

# ------------------------------------------------------------------ the product shots
COVERS = {"aud1": '<div class="cover cov1"></div><div class="cover cov2"></div>'}
GLOWS = {"filt": '<div class="glow g1"></div>', "pers": '<div class="glow"></div>' * 4, "dest": '<div class="glow g1"></div>'}
shots_html = []
for name, f in SCREENS.items():
    src = f"{ASSET}/screens/{f}"
    shots_html.append(f'<div class="shot" data-shot="{name}"><div class="echo b"><img src="{src}" alt=""></div><div class="echo a"><img src="{src}" alt=""></div>'
                      f'<div class="win"><div class="cam"><img src="{src}" alt="">{COVERS.get(name, "")}{GLOWS.get(name, "")}</div></div></div>')

T = {"bpm": FILM["bpm"], "bars": FILM["bars"]}
tpl = open("template.html").read()
comp = (tpl.replace("__FONTFACES__", "\n        ".join(FONTFACES)).replace("__SERIF__", SERIF).replace("__SANS__", SANS)
        .replace("__SHOTS__", "\n            ".join(shots_html)).replace("__CAPTIONS__", "\n            ".join(cap_html))
        .replace("__TICKERS__", "\n            ".join(tick_html)).replace("__MEETING__", meeting_html)
        .replace("__PAPER__", "\n            ".join(paper_html)).replace("__LOGO__", f"{ASSET}/logo-on-dark.svg")
        .replace("__TITLE__", html.escape(lk["title"])).replace("__LINE__", line_html).replace("__URL__", html.escape(lk["url"]))
        .replace("__T__", json.dumps(T)))
os.makedirs("compositions", exist_ok=True)
open("compositions/plays.html", "w").write(comp)
open("index.html", "w").write(f'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <title>Breakout Plays launch film</title>
    <script src="{GSAP_SRC}"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1920px; height: 1080px; overflow: hidden; background: #000; }}
      #main {{ position: relative; width: 1920px; height: 1080px; overflow: hidden; }}
      [data-composition-id="main"] > div[data-composition-src] {{ position: absolute; inset: 0; }}
    </style>
  </head>
  <body>
    <div id="main" data-composition-id="main" data-start="0" data-duration="{END:.3f}" data-width="1920" data-height="1080">
      <div id="el-plays" data-composition-id="plays" data-composition-src="compositions/plays.html" data-start="0" data-duration="{END:.3f}" data-track-index="1"></div>
    </div>
    <script>
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
''')
json.dump({"bpm": FILM["bpm"], "bar": BAR, "end": END, "drop": FILM["drop_bar"] * BAR}, open("timing.json", "w"), indent=1)
print(f"Breakout Plays: {END:.2f} s, {FILM['bars']} bars at {FILM['bpm']} BPM, drop at {FILM['drop_bar'] * BAR:.2f} s")
print("render: cd film/plays && npx -y hyperframes@0.8.77 render -c index.html --quality looks --output renders/plays-picture.mp4")
