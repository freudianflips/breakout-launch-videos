#!/usr/bin/env python3
"""Build the Signals launch film: film.json + brand.json -> index.html and compositions/signals.html.

  python3 build.py

All text is written as markup here (typed text as 1 span per character), so nothing falls back to a
system font at render time. Times live in film.json "at", in bars on the 128 BPM grid.
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

# ------------------------------------------------------------------ assets
A = "assets"
if os.path.exists(A):
    shutil.rmtree(A)
os.makedirs(f"{A}/fonts")
faces = []
for role in ("display", "body", "mono"):
    f = BRAND["fonts"][role]
    for face in f.get("faces", []):
        shutil.copy(os.path.join(BRAND_DIR, face["file"]), os.path.join(A, face["file"]))
        faces.append(f'@font-face {{ font-family: "{f["family"]}"; src: url("{A}/{face["file"]}") format("woff2"); '
                     f'font-weight: {face["weight"]}; font-style: {face.get("style", "normal")}; }}')
for k in ("file", "mark_on_dark"):
    shutil.copy(os.path.join(BRAND_DIR, BRAND["logo"][k]), f"{A}/{os.path.basename(BRAND['logo'][k])}")
VLOGO = f"{A}/{os.path.basename(F['visitor']['logo'])}"
shutil.copy(F["visitor"]["logo"], VLOGO)
gsap = os.path.join(HERE, "..", "..", "node_modules", "gsap", "dist", "gsap.min.js")
GSAP = "https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"
if os.path.exists(gsap):
    shutil.copy(gsap, f"{A}/gsap.min.js")
    GSAP = f"{A}/gsap.min.js"
MARK = f'<span class="av"><img src="{A}/{os.path.basename(BRAND["logo"]["mark_on_dark"])}" alt=""></span>'


# ------------------------------------------------------------------ text helpers
def chars(text):
    """1 span per character; spaces kept as spaces so lines wrap naturally."""
    return "".join(f'<span class="ch">{E(c)}</span>' if c != " " else '<span class="ch sp"> </span>' for c in text)


def typed(text):
    """'[key]phrase[/key]' marks become the personalization tokens the camera zooms onto."""
    out, pos = [], 0
    for m in re.finditer(r"\[(\w+)\](.*?)\[/\1\]", text):
        out.append(chars(text[pos:m.start()]))
        out.append(f'<span class="ph" data-ph="{m.group(1)}">{chars(m.group(2))}</span>')
        pos = m.end()
    out.append(chars(text[pos:]))
    return "".join(out)


def kw(text):
    return re.sub(r"\*(.+?)\*", r'<em class="v">\1</em>', E(text))


SPIN = '<svg class="spin" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 3a9 9 0 0 1 9 9"/></svg>'
CHECK = '<svg class="ok" viewBox="0 0 24 24"><path d="m5 12 4.5 4.5L19 7"/></svg>'
ARROW = ('<svg id="arrow" viewBox="0 0 32 32"><path d="M5 3 L5 25 L11 19.5 L15.5 29 L19.5 27.2 L15 18 L23 18 Z" '
         'fill="var(--cur)" stroke="#fff" stroke-width="2" stroke-linejoin="round"/></svg>')

# ------------------------------------------------------------------ markup
AGENT = ('<span class="wav"><svg viewBox="0 0 40 40"><circle cx="20" cy="20" r="20" fill="#16151f"/>'
         '<rect x="13" y="13" width="5" height="14" rx="2.5" fill="#8b7cf6"/><rect x="22" y="13" width="5" height="14" rx="2.5" fill="#8b7cf6"/></svg></span>')
ICONS = ('<span class="wic"><svg viewBox="0 0 24 24"><path d="M14 4h6v6M20 4l-7 7M10 20H4v-6M4 20l7-7"/></svg>'
         '<svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6 6 18"/></svg></span>')
v, site, wg = F["visitor"], F["site"], F["widget"]
plans = "".join(f'<div class="plan{" hot" if i == site["hover"] else ""}"><i class="bar name"></i><i class="bar w60"></i><i class="bar w40 tall"></i>'
                f'<i class="ln"></i><i class="ln"></i><i class="ln s"></i><i class="ln"></i><span class="btn"></span></div>' for i, _ in enumerate(site["plans"]))
widget = (f'<div id="widget"><div class="wh">{AGENT}<b>{E(wg["name"])}</b>{ICONS}</div><div class="wbook">{E(wg["book"])}</div>'
          f'<div class="wmsg">{typed(F["agent"]["text"])}</div><div class="wme">{E(F["agent"]["reply"])}</div>'
          f'<div class="win"><span>{E(wg["placeholder"])}</span><i class="wsend"><svg viewBox="0 0 24 24"><path d="M12 19V5M6 11l6-6 6 6"/></svg></i></div></div>'
          f'<div id="launcher"><svg viewBox="0 0 40 40"><rect x="13" y="12" width="5" height="16" rx="2.5" fill="#8b7cf6"/><rect x="22" y="12" width="5" height="16" rx="2.5" fill="#8b7cf6"/></svg></div>')
browser = (f'<div id="browser"><div class="chrome"><i></i><i></i><i></i><span class="url"><i></i></span></div>'
           f'<div class="page"><i class="ptitle"></i><i class="psub"></i><div class="plans">{plans}</div></div>{widget}</div>')
ICO = {"funding": '<path d="M4 17l5-5 4 4 7-8M15 8h5v5"/>', "people": '<circle cx="12" cy="8" r="3.5"/><path d="M5 20c1.2-3.6 3.8-5.4 7-5.4s5.8 1.8 7 5.4"/>',
       "hiring": '<path d="M8 7V5h8v2M4 7h16v12H4zM4 12h16"/>', "intent": '<path d="M4 18V9M10 18V5M16 18v-7M21 18H3"/>',
       "committee": '<circle cx="8" cy="9" r="3"/><circle cx="16" cy="9" r="3"/><path d="M2.5 19c.9-2.8 3-4.2 5.5-4.2s4.6 1.4 5.5 4.2M12.5 15.2c1-.3 2.2-.4 3.5-.4 2.5 0 4.6 1.4 5.5 4.2"/>'}
COL = F["colors"]
sigs = "".join(f'<div class="sg"><span class="sgi" style="--c:{COL["icons"][i % len(COL["icons"])]}">{SPIN}<svg class="ico" viewBox="0 0 24 24">{ICO.get(x["key"], "")}</svg></span>'
               f'<div class="sgt"><b>{E(x["title"])}</b><span>{E(x["finding"])}</span></div><svg class="ok" viewBox="0 0 24 24"><path d="m5 12 4.5 4.5L19 7"/></svg></div>' for i, x in enumerate(F["signals"]))
cursor = (f'<div id="cursor" style="--cur:{COL["cursor"]}">{ARROW}<div id="tag"><img src="{VLOGO}" alt=""><b>{E(v["name"])}</b><span>{E(v["role"])}, {E(v["company"])}</span></div>'
          f'<div id="card"><div id="listen">{SPIN}<span>{E(F["listening"])}</span></div><div id="sigs">{sigs}</div></div></div>')
em = F["email"]
email = (f'<div id="email"><div class="eh">{MARK}<span>{E(em["head"])}</span><span class="pill sent" id="sent">{CHECK}{E(em["sent"])}</span></div>'
         f'<div class="eto">To&nbsp;&nbsp;{E(em["to"])}</div>'
         f'<div class="esub"><span class="lab">Subject</span><span class="stx">{chars(em["subject"])}</span></div>'
         f'<div class="ebody">{typed(em["body"])}</div></div>')
heads = "".join(f'<div class="hl">{kw(h["text"])}</div>' for h in F["headlines"])
lk = F["lockup"]

T = {"bpm": F["bpm"], "bars": F["bars"], "at": F["at"], "heads": [[h["at"], h["until"]] for h in F["headlines"]]}
tpl = open("template.html").read()
rep = {
    "__FONTFACES__": "\n        ".join(faces), "__HEADS__": heads, "__BROWSER__": browser, "__CURSOR__": cursor,
    "__EMAIL__": email, "__DISCLAIMER__": E(F["disclaimer"]), "__BRANDTAG__": E(F["brandtag"]),
    "__LOGO__": f'{A}/{os.path.basename(BRAND["logo"]["file"])}', "__LINE__": kw(lk["line"]), "__URL__": E(lk["url"]), "__T__": json.dumps(T),
}
for k, val in rep.items():
    tpl = tpl.replace(k, val)
os.makedirs("compositions", exist_ok=True)
open("compositions/signals.html", "w").write(tpl)
open("index.html", "w").write(f'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <title>Breakout: Signals</title>
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
      <div id="el-signals" data-composition-id="signals" data-composition-src="compositions/signals.html" data-start="0" data-duration="{END:.3f}" data-track-index="1"></div>
    </div>
    <script>
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
''')
print(f"signals-launch: {END:.2f} s, {F['bars']} bars at {F['bpm']} BPM")
