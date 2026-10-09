#!/usr/bin/env python3
"""Build a kinetic film: film.json + brand.json -> index.html and compositions/kinetic.html.

  python3 build.py

Each beat in film.json names a code-drawn visual ("paid", "deanon", "agent", ...); its markup is below, its
motion in template.html. All text is markup; headlines use New Kansas when installed, else Fraunces.
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
E = html.escape

# ------------------------------------------------------------------ timeline (bars)
t = F["intro"]["bars"]
starts = []
for _ in F["beats"]:
    starts.append(t)
    t += F["beat_bars"]
AT = {"beats": starts, "booked": t, "personas": t + F["booked"]["bars"]}
AT["lockup"] = AT["personas"] + F["personas"]["bars"]
AT["end"] = AT["lockup"] + F["lockup"]["bars"]
END = AT["end"] * BAR

# ------------------------------------------------------------------ assets
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
shutil.copy(os.path.join(BRAND_DIR, BRAND["logo"]["file"]), f"{A}/logo.svg")
gsap = os.path.join(HERE, "..", "..", "node_modules", "gsap", "dist", "gsap.min.js")
GSAP = "https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"
if os.path.exists(gsap):
    shutil.copy(gsap, f"{A}/gsap.min.js")
    GSAP = f"{A}/gsap.min.js"


def kw(text):
    return re.sub(r"\*(.+?)\*", r"<em>\1</em>", E(text))


def words(text):
    return " ".join(f'<span class="w">{E(x)}</span>' for x in text.split())


SK = '<i class="sk" style="width:{}%"></i>'
CUR = '<svg class="cur" viewBox="0 0 24 24"><path d="M4 2.5v17.2l4.6-4.4 3.1 6.9 3-1.3-3.1-6.8h6.4z" fill="#040405" stroke="#fff" stroke-width="1.4" stroke-linejoin="round"/></svg>'
ENV = '<svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2.5"/><path d="m3.5 7 8.5 6 8.5-6"/></svg>'
BELL = '<svg viewBox="0 0 24 24"><path d="M6 16V11a6 6 0 0 1 12 0v5l1.5 2h-15z"/><path d="M10 20a2 2 0 0 0 4 0"/></svg>'
CHECK = '<svg class="ck" viewBox="0 0 24 24"><path d="m5 12 4.5 4.5L19 7"/></svg>'
vis = F["visitor"]


def page(extra=""):
    return (f'<div class="card page"><div class="pbar"><i></i><i></i><i></i></div><div class="hero"><i class="sk" style="width:60%"></i>'
            f'<i class="sk" style="width:40%"></i></div><div class="prow">{SK.format(90)}{SK.format(70)}{SK.format(80)}</div>{extra}</div>')


V = {
    "paid": (f'<div class="card ad"><span class="tag">Ad</span><div class="adhero"></div>{SK.format(80)}{SK.format(55)}<b class="cta"></b></div>'
             f'{page()}{CUR}'),
    "deanon": (f'<div class="ring"></div><div class="who"><span class="q">?</span><span class="ini">{E(vis["initials"])}</span></div>'
               f'<div class="card idcard"><b>{E(vis["name"])}</b><span>{E(vis["role"])}</span></div>'),
    "agent": (f'<div class="card chat"><div class="chd"><span class="dotav"></span>{SK.format(30)}</div>'
              f'<div class="ub">{SK.format(90)}{SK.format(60)}</div><div class="typing"><i></i><i></i><i></i></div>'
              f'<div class="ab">{SK.format(95)}{SK.format(85)}{SK.format(70)}</div><b class="pill">Book a meeting</b></div>'),
    "pounce": f'{page()}<div class="pulse"></div><div class="card bubble"><span class="dotav rep"></span><div>{SK.format(90)}{SK.format(60)}</div><span class="live"></span></div>',
    "personal": (f'<div class="card page"><div class="pbar"><i></i><i></i><i></i></div><div class="flip"><div class="hero a"><i class="sk" style="width:60%"></i><i class="sk" style="width:40%"></i></div>'
                 f'<div class="hero b"><span class="co">{E(vis["role"].split("·")[-1].strip())}</span><i class="sk" style="width:70%"></i></div></div>'
                 f'<div class="prow">{SK.format(90)}{SK.format(70)}{SK.format(80)}</div></div>'),
    "routing": ('<svg class="wires" viewBox="0 0 740 680"><path d="M150 340 C 350 340 380 140 570 140"/><path d="M150 340 L 570 340"/><path d="M150 340 C 350 340 380 540 570 540"/></svg>'
                '<div class="node lead"></div><div class="node rep r0"></div><div class="node rep r1"></div><div class="node rep r2"></div><div class="traveller"></div>' + CHECK),
    "research": (f'<div class="card acct"><div class="ahd"><span class="logo"></span>{SK.format(40)}</div>'
                 + "".join(f'<div class="arow"><i class="k"></i><i class="v"></i></div>' for _ in range(4)) + '</div><div class="lens"></div>'),
    "committee": ('<svg class="wires" viewBox="0 0 740 680"><path d="M370 190 L 150 420"/><path d="M370 190 L 370 420"/><path d="M370 190 L 590 420"/></svg>'
                  + "".join(f'<div class="person p{i}"><span class="dotav"></span><b>{E(r)}</b></div>' for i, r in enumerate(F["committee"]))),
    "alerts": (f'<div class="bell">{BELL}</div>'
               + "".join(f'<div class="card note n{i}"><span class="sq"></span><div>{SK.format(80)}{SK.format(50)}</div><span class="vdot"></span></div>' for i in range(2))),
    "outbound": (f'<div class="sig"><i></i><i></i><i></i><span></span></div><div class="env">{ENV}</div><div class="inbox"></div>' + CHECK),
    "nurture": ('<div class="tline"><i class="fill"></i></div>' + "".join(f'<div class="nn n{i}">{ENV}</div>' for i in range(3))),
    "abm": "".join(f'<div class="card mini m{i}"><span class="logo"></span>{SK.format(70)}{SK.format(45)}</div>' for i in range(12)),
}

beats = "".join(
    f'<div class="beat" data-i="{i}" data-v="{b["visual"]}" style="--ink:{b["ink"]}"><div class="label">{E(b["label"])}</div>'
    f'<div class="line">{words(b["line"])}</div><div class="vis v-{b["visual"]}">{V[b["visual"]]}</div></div>'
    for i, b in enumerate(F["beats"]))
pr = F["personas"]
chips = "".join(f'<span class="chip" style="background:{c};color:{k}">{E(w)}</span>' for w, c, k in zip(pr["words"], pr["colors"], pr["inks"]))
dots = "".join('<i></i>' for _ in F["beats"])

T = {"bpm": F["bpm"], "at": AT, "intro": F["intro"]["bars"], "beat": F["beat_bars"],
     "grounds": [b["ground"] for b in F["beats"]], "inks": [b["ink"] for b in F["beats"]], "visuals": [b["visual"] for b in F["beats"]]}
tpl = open("template.html").read()
rep = {"__FONTFACES__": "\n        ".join(fontfaces), "__INTRO__": E(F["intro"]["word"]), "__BEATS__": beats, "__DOTS__": dots,
       "__BOOKED__": kw(F["booked"]["big"]), "__CHIPS__": chips, "__LOCK__": kw(F["lockup"]["line"]), "__URL__": E(F["lockup"]["url"]),
       "__DISC__": E(F["disclaimer"]), "__SOURCE__": E(F.get("source", "")), "__T__": json.dumps(T)}
for k, v in rep.items():
    tpl = tpl.replace(k, v)
os.makedirs("compositions", exist_ok=True)
open("compositions/kinetic.html", "w").write(tpl)
open("index.html", "w").write(f'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <title>Breakout: {E(F["lockup"]["line"].replace("*", ""))}</title>
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
      <div id="el-k" data-composition-id="kinetic" data-composition-src="compositions/kinetic.html" data-start="0" data-duration="{END:.3f}" data-track-index="1"></div>
    </div>
    <script>
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
''')
json.dump(AT, open("timing.json", "w"), indent=1)
print(f"kinetic: {END:.2f} s, {AT['end']} bars at {F['bpm']} BPM, {len(F['beats'])} beats")
