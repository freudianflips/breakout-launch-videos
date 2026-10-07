#!/usr/bin/env python3
"""Build 1 split-screen ABM film: split.json + ../abm/accounts/<slug>/account.json + brand.json -> out/<slug>/.

  python3 film/abm-split/build.py korn-ferry

Left pane: the account's site and chat exactly as captured (account.json "tree": each step's capture, its buttons
and which one the visitor clicks). Right pane: the same site with Breakout's widget over theirs (illustrative).
All text is markup; headlines use New Kansas when installed, else the brand's Fraunces stand-in.
"""
import html
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SLUG = sys.argv[1] if len(sys.argv) > 1 else "korn-ferry"
SER = json.load(open(os.path.join(HERE, "split.json")))
ACC_DIR = os.path.normpath(os.path.join(HERE, SER["accounts"], SLUG))
ACC = json.load(open(os.path.join(ACC_DIR, "account.json")))
BRAND_DIR = os.path.normpath(os.path.join(HERE, SER["brand"]))
BRAND = json.load(open(os.path.join(BRAND_DIR, "brand.json")))
OUT = os.path.join(HERE, "out", SLUG)
BAR = 240 / SER["bpm"]
END = SER["bars"] * BAR
E = html.escape
co = ACC["company"]

# ------------------------------------------------------------------ assets
A = "assets"
os.makedirs(OUT, exist_ok=True)
if os.path.exists(os.path.join(OUT, A)):
    shutil.rmtree(os.path.join(OUT, A))
os.makedirs(os.path.join(OUT, A, "fonts"))
fontfaces = []
for role in ("body", "mono", "display"):
    f = BRAND["fonts"][role]
    for face in f.get("faces", []):
        shutil.copy(os.path.join(BRAND_DIR, face["file"]), os.path.join(OUT, A, face["file"]))
        src, family = f'url("{A}/{face["file"]}") format("woff2")', f["family"]
        if role == "display":     # New Kansas first, wherever it is installed
            family = "NK"
            src = ", ".join(f'local("{n}")' for n in f.get("local", [])) + ", " + src
        fontfaces.append(f'@font-face {{ font-family: "{family}"; src: {src}; font-weight: {face["weight"]}; font-style: {face.get("style", "normal")}; }}')
for k in ("file", "mark_on_dark"):
    shutil.copy(os.path.join(BRAND_DIR, BRAND["logo"][k]), os.path.join(OUT, A, os.path.basename(BRAND["logo"][k])))
steps = ACC["tree"]["steps"]
for i, s in enumerate(steps):
    shutil.copy(os.path.join(ACC_DIR, s["file"]), os.path.join(OUT, A, f"step{i}{os.path.splitext(s['file'])[1]}"))
shutil.copy(os.path.join(HERE, "..", "assets", "screens", "agent-avatar.png"), os.path.join(OUT, A, "agent-avatar.png"))
gsap = os.path.join(HERE, "..", "..", "node_modules", "gsap", "dist", "gsap.min.js")
GSAP = "https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"
if os.path.exists(gsap):
    shutil.copy(gsap, os.path.join(OUT, A, "gsap.min.js"))
    GSAP = f"{A}/gsap.min.js"


def kw(text):
    return re.sub(r"\*(.+?)\*", r"<em>\1</em>", E(text))


def chars(text, cls):
    return "".join(f'<span class="{cls}">{E(c)}</span>' for c in text)


def words(text):
    out, pos = [], 0

    def plain(s):
        return " ".join(f'<span class="w">{E(x)}</span>' for x in s.split())

    for m in re.finditer(r"\[(\w+)\](.*?)\[/\1\]", text):
        out.append(plain(text[pos:m.start()]))
        out.append(f'<span class="ph" data-ph="{m.group(1)}">{plain(m.group(2))}</span>')
        pos = m.end()
    out.append(plain(text[pos:]))
    return " ".join(x for x in out if x)


CUR = '<svg class="cur" viewBox="0 0 24 24"><path d="M4 2.5v17.2l4.6-4.4 3.1 6.9 3-1.3-3.1-6.8h6.4z" fill="#040405" stroke="#fff" stroke-width="1.4" stroke-linejoin="round"/></svg>'
MARK = f'<span class="av"><img src="{A}/{os.path.basename(BRAND["logo"]["mark_on_dark"])}" alt=""></span>'
ask, bk, gl, bo, cl = (SER[k] for k in ("ask", "booked", "golive", "buyout", "close"))
vis, em = ACC["visitor"], ACC["email"]

imgs = "".join(f'<img class="step" src="{A}/step{i}{os.path.splitext(s["file"])[1]}" alt="">' for i, s in enumerate(steps))
bw = (f'<div id="bw"><div class="bwh"><img class="bav" src="{A}/agent-avatar.png" alt=""><b>Breakout</b></div>'
      f'<div class="bgreet">{E(ask["greeting"])}</div><div class="bbook">{E(ask["book"])}</div>'
      f'<div class="bpanel"><div class="ub">{E(ACC["question"])}</div>'
      f'<div class="ar"><img class="bav s" src="{A}/agent-avatar.png" alt=""><span class="dots"><i></i><i></i><i></i></span>'
      f'<div class="ans">{words(ACC["answer"])}</div></div>'
      f'<div class="mod"><div><b>{E(ACC["module"]["title"])}</b><span>{E(ACC["module"]["sub"])}</span></div><em>{E(ACC["module"]["cta"])}</em></div>'
      f'<div class="bin"><span class="ph0">{E(ask["placeholder"])}</span><span class="typed">{chars(ACC["question"], "ic")}</span><span class="bcaret"></span>'
      f'<span class="bsend"><svg viewBox="0 0 24 24"><path d="M4 12 20 4l-4 16-4-7z"/></svg></span></div></div>'
      f'<div class="bpow">{E(ask["powered"])} <b>breakout</b></div></div>')
bar = f'<div class="pbar"><i></i><i></i><i></i><span>{E(ACC["domain"])}</span></div>'
left = (f'<div class="pane" id="pL">{bar}<div class="pv"><div class="pc" id="cL">{imgs}<div class="hl"></div>{CUR}</div>'
        f'<div class="gone nk">{kw(SER["left_gone"])}</div>'
        f'<div class="acl"><div class="acn nk">{E(vis["company"])}</div><div class="acw">Qualified</div><div class="acq nk">{E(SER["account_level"])}</div></div>'
        f'<div class="glv"><div class="glw">{E(gl["left_who"])} · {E(gl["label"])}</div><div class="gln nk">{kw(gl["left"])}</div></div></div></div>')
chips = "".join(f'<span class="schip">{E(a)}</span>' for a, b in ACC["signals"])
person = (f'<div id="person"><div class="pav">{E(vis["initials"])}</div><div class="pname nk">{E(vis["person"])}</div>'
          f'<div class="prole">{E(vis["role"])}</div><div class="pco">{E(vis["company"])} · {E(vis["company_sub"])}</div><div class="chips">{chips}</div></div>')
body = "".join(f'<p>{words(p)}</p>' for p in em["body"])
email = (f'<div id="email"><div class="eh">{E(em["head"])} · From {E(em["from"])}</div>'
         f'<div class="eto"><span class="lab">To</span>{E(em["to"])}</div>'
         f'<div class="esub"><span class="lab">Subject</span><span class="stx">{E(em["subject"])}</span></div>'
         f'<div class="ebody">{body}</div><div class="esend" id="esend">{E(em["send"])}<svg viewBox="0 0 24 24"><path d="M4 12 20 4l-4 16-4-7z"/></svg></div></div>')
CAL = '<svg viewBox="0 0 24 24"><rect x="3.5" y="5" width="17" height="15" rx="2.5"/><path d="M3.5 10h17M8 3v4M16 3v4"/></svg>'
people = "".join(f'<span class="face f{i}">{E(x)}</span>' for i, x in enumerate(ACC["booked"]["people"]))
booked = (f'<div id="flood"></div><div id="bk"><svg id="tick" viewBox="0 0 200 200"><circle cx="100" cy="100" r="86"/><path d="M58 104l28 28 58-62"/></svg>'
          f'<div id="bigok" class="nk">{kw(bk["big"])}</div>'
          f'<div class="card" id="c-bd"><div class="hd">{MARK}<b>{E(bk["title"])}</b><span class="tm">{E(bk["time"])}</span></div>'
          f'<div class="rw">{CAL}<div><div class="tx">{E(bk["row"])}</div><div class="sub">{E(ACC["booked"]["when"])}</div></div>'
          f'<span class="faces">{people}</span></div></div></div>')
right = (f'<div class="pane" id="pR">{bar}<div class="pv"><div class="pc" id="cR"><img class="step on" src="{A}/step0{os.path.splitext(steps[0]["file"])[1]}" alt="">'
         f'<div id="bwrap">{bw}</div>{CUR}</div><div id="dim"></div>{person}{email}{booked}'
         f'<div class="glv"><div class="glw">{E(gl["right_who"])} · {E(gl["label"])}</div><div class="gln nk">{kw(gl["right"])}</div></div></div></div>')

T = {"bpm": SER["bpm"], "bars": SER["bars"], "at": SER["at"], "steps": steps, "size": ACC["capture"]["size"]}
tpl = open(os.path.join(HERE, "template.html")).read()
rep = {
    "__FONTFACES__": "\n        ".join(fontfaces), "__LOGO__": f'{A}/{os.path.basename(BRAND["logo"]["file"])}',
    "__LEFT__": left, "__RIGHT__": right, "__TAGL__": kw(SER["labels"]["left"]), "__TAGR__": kw(SER["labels"]["right"]),
    "__QUESTION__": E(ACC["question"]), "__DOMAIN__": E(ACC["domain"]),
    "__BO1__": kw(bo["line1"]), "__BO2__": kw(bo["line2"]), "__BON__": E(bo["note"]),
    "__CTA__": E(cl["cta"]), "__URL__": E(cl["url"]), "__MADE__": kw(cl["made_for"].replace("{company}", co)), "__T__": json.dumps(T),
}
for k, v in rep.items():
    tpl = tpl.replace(k, v)
os.makedirs(os.path.join(OUT, "compositions"), exist_ok=True)
open(os.path.join(OUT, "compositions", "split.html"), "w").write(tpl)
open(os.path.join(OUT, "index.html"), "w").write(f'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <title>Breakout for {E(co)}: same visitor, two sites</title>
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
      <div id="el-split" data-composition-id="split" data-composition-src="compositions/split.html" data-start="0" data-duration="{END:.3f}" data-track-index="1"></div>
    </div>
    <script>
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
''')
print(f"Split ABM film for {co}: {END:.2f} s, {SER['bars']} bars at {SER['bpm']} BPM -> film/abm-split/out/{SLUG}/")
