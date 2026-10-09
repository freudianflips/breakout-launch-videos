#!/usr/bin/env python3
"""Build 'Press play.': film.json + brand.json -> index.html and compositions/press.html.

  python3 templates/sequencer/build.py

All text is written as markup here (the email as 1 span per word), so nothing falls back to a system
font at render time. The pattern in film.json drives the picture here and the bed in bed.py.
"""
import html
import json
import os
import re
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
FILM = json.load(open("film.json"))
BRAND_DIR = os.path.normpath(os.path.join(HERE, FILM.get("brand", "../../brand")))
BRAND = json.load(open(os.path.join(BRAND_DIR, "brand.json")))
BAR = 240 / FILM["bpm"]
END = FILM["bars"] * BAR
E = html.escape

# ------------------------------------------------------------------ assets
A = "assets"
if os.path.exists(A):
    shutil.rmtree(A)
os.makedirs(f"{A}/fonts")
fontfaces = []
for role in ("body", "mono"):
    f = BRAND["fonts"][role]
    for face in f.get("faces", []):
        shutil.copy(os.path.join(BRAND_DIR, face["file"]), os.path.join(A, face["file"]))
        fontfaces.append(f'@font-face {{ font-family: "{f["family"]}"; src: url("{A}/{face["file"]}") format("woff2"); '
                         f'font-weight: {face["weight"]}; font-style: {face.get("style", "normal")}; }}')
for k in ("file", "mark_on_dark"):
    shutil.copy(os.path.join(BRAND_DIR, BRAND["logo"][k]), f"{A}/{os.path.basename(BRAND['logo'][k])}")
gsap = os.path.join(HERE, "..", "..", "node_modules", "gsap", "dist", "gsap.min.js")
GSAP = "https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"
if os.path.exists(gsap):
    shutil.copy(gsap, f"{A}/gsap.min.js")
    GSAP = f"{A}/gsap.min.js"


# ------------------------------------------------------------------ markup
def chars(text):
    return "".join(f'<span class="ch">{E(c)}</span>' for c in text)


def words(text):
    """1 span per word; '[cfo]phrase[/cfo]' marks become phrase spans the wires point at."""
    out, pos = [], 0

    def plain(s):
        return " ".join(f'<span class="w">{E(x)}</span>' for x in s.split())

    for m in re.finditer(r"\[(\w+)\](.*?)\[/\1\]", text):
        out.append(plain(text[pos:m.start()]))
        out.append(f'<span class="ph" data-ph="{m.group(1)}">{plain(m.group(2))}</span>')
        pos = m.end()
    out.append(plain(text[pos:]))
    return " ".join(x for x in out if x)


def cells(n=16, cls="c"):
    return "".join(f'<i class="{cls}{" q" if k % 4 == 0 else ""}"></i>' for k in range(n))


rows = "".join(
    f'<div class="row{" ghost" if r.get("mute_at") else ""}" data-r="{i}">'
    f'<span class="mbtn">M</span><span class="rl">{chars(r["label"])}</span>'
    f'<span class="tag{" no" if r.get("mute_at") else ""}">{E(r["tag"])}</span>'
    f'<span class="steps">{cells()}</span></div>' for i, r in enumerate(FILM["rows"]))
stepnums = "".join(f'<b>{k + 1:02d}</b>' for k in range(16))
mini = "".join(
    f'<div class="mrow" data-r="{i}"><span class="ml">{E(r["label"])}</span><span class="ms">{cells(cls="d")}</span></div>'
    for i, r in enumerate(FILM["rows"]) if not r.get("mute_at"))
cm = FILM["committee"]
mini += f'<div class="mrow cm" data-r="cm"><span class="ml">{E(cm["label"])}</span><span class="ms">{cells(cls="d")}</span></div>'

em = FILM["email"]
body = "".join(f'<p>{words(p)}</p>' for p in em["body"])
chips = "".join(f'<span class="chip">{E(x)}</span>' for x in cm["chips"])
email = (f'<div id="email"><div class="eh">{E(em["head"])}</div>'
         f'<div class="eto"><span class="lab">To</span><span id="to1">{E(em["to"])}</span><span id="chips">{chips}</span></div>'
         f'<div class="esub"><span class="lab">Subject</span><span class="stx">{E(em["subject"])}</span></div>'
         f'<div class="ebody">{body}</div></div>')
elabels = "".join(f'<span class="el">{E(x)}</span>' for x in em["labels"])

bd = FILM["booked"]
MARK = f'<span class="av"><img src="{A}/{os.path.basename(BRAND["logo"]["mark_on_dark"])}" alt=""></span>'
CAL = '<svg viewBox="0 0 24 24"><rect x="3.5" y="5" width="17" height="15" rx="2.5"/><path d="M3.5 10h17M8 3v4M16 3v4"/></svg>'
people_html = "".join(f'<span class="face f{i}">{E(x)}</span>' for i, x in enumerate(bd["people"]))
booked = (f'<div id="bigok">{E(bd["big"])}</div>'
          f'<div class="card" id="c-bd"><div class="hd">{MARK}<b>{E(bd["title"])}</b><span class="tm">{E(bd["time"])}</span></div>'
          f'<div class="rw">{CAL}<div><div class="tx">{E(bd["row"])}</div><div class="sub">{E(bd["when"])}</div></div>'
          f'<span class="faces">{people_html}</span></div></div>')

wd = FILM["words"]
lk = FILM["lockup"]
T = {k: FILM[k] for k in ("bpm", "bars", "rows", "committee", "transport", "counter")}
T["links"] = em["links"]
tpl = open("template.html").read()
rep = {
    "__FONTFACES__": "\n        ".join(fontfaces), "__LOGO__": f'{A}/{os.path.basename(BRAND["logo"]["file"])}',
    "__ROWS__": rows, "__STEPNUMS__": stepnums, "__MINI__": mini, "__EMAIL__": email, "__ELABELS__": elabels, "__BOOKED__": booked,
    "__LISTEN__": E(wd["listen"]), "__PRESS__": E(wd["press"]), "__SENT__": E(wd["sent"]), "__PLAYLINE__": chars(wd["play_line"]),
    "__COUNTER_LABEL__": E(FILM["counter"]["label"]), "__DISCLAIMER__": E(FILM["disclaimer"]),
    "__TITLE__": E(lk["title"]), "__URL__": E(lk["url"]), "__LCELLS__": cells(), "__T__": json.dumps(T),
}
for k, v in rep.items():
    tpl = tpl.replace(k, v)
os.makedirs("compositions", exist_ok=True)
open("compositions/press.html", "w").write(tpl)
open("index.html", "w").write(f'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <title>Breakout Plays: Press play.</title>
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
      <div id="el-press" data-composition-id="press" data-composition-src="compositions/press.html" data-start="0" data-duration="{END:.3f}" data-track-index="1"></div>
    </div>
    <script>
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
''')
print(f"Press play.: {END:.2f} s, {FILM['bars']} bars at {FILM['bpm']} BPM")
