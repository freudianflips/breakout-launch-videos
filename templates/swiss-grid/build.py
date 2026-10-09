#!/usr/bin/env python3
"""Build the 'Signal in. Meeting out.' film: film.json + brand.json -> index.html and compositions/signal.html.

  python3 templates/swiss-grid/build.py

All text is written as markup here (typed text as 1 span per character), so nothing falls back to a
system font at render time. Times live in the template, on the 128 BPM bar grid.
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
faces = []
for role in ("display", "body", "mono"):
    f = BRAND["fonts"][role]
    for face in f.get("faces", []):
        shutil.copy(os.path.join(BRAND_DIR, face["file"]), os.path.join(A, face["file"]))
        faces.append(f'@font-face {{ font-family: "{f["family"]}"; src: url("{A}/{face["file"]}") format("woff2"); '
                     f'font-weight: {face["weight"]}; font-style: {face.get("style", "normal")}; }}')
for k in ("file", "mark_on_dark"):
    shutil.copy(os.path.join(BRAND_DIR, BRAND["logo"][k]), f"{A}/{os.path.basename(BRAND['logo'][k])}")
gsap = os.path.join(HERE, "..", "..", "node_modules", "gsap", "dist", "gsap.min.js")
GSAP = "https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"
if os.path.exists(gsap):
    shutil.copy(gsap, f"{A}/gsap.min.js")
    GSAP = f"{A}/gsap.min.js"


# ------------------------------------------------------------------ text helpers
def chars(text, cls="ch"):
    """1 span per character; spaces kept as spaces so lines wrap naturally."""
    return "".join(f'<span class="{cls}">{E(c)}</span>' if c != " " else '<span class="ch sp"> </span>' for c in text)


def typed(text):
    """'[cfo]phrase[/cfo]' marks become phrase spans the connecting lines point at."""
    out, pos = [], 0
    for m in re.finditer(r"\[(\w+)\](.*?)\[/\1\]", text):
        out.append(chars(text[pos:m.start()]))
        out.append(f'<span class="ph" data-ph="{m.group(1)}">{chars(m.group(2))}</span>')
        pos = m.end()
    out.append(chars(text[pos:]))
    return "".join(out)


ICON = {
    "eye": '<svg viewBox="0 0 24 24"><path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/></svg>',
    "person": '<svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6"/></svg>',
    "tag": '<svg viewBox="0 0 24 24"><path d="M3 12V4h8l10 10-8 8z"/><circle cx="7.5" cy="8.5" r="1.5"/></svg>',
    "building": '<svg viewBox="0 0 24 24"><path d="M4 21V4h11v17M15 9h5v12M8 8h3M8 12h3M8 16h3"/></svg>',
    "mail": '<svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>',
    "check": '<svg viewBox="0 0 24 24"><path d="m5 12 4.5 4.5L19 7"/></svg>',
    "you": '<svg viewBox="0 0 24 24"><circle cx="12" cy="9" r="3.6"/><path d="M5.5 19.5c1.3-3 3.7-4.5 6.5-4.5s5.2 1.5 6.5 4.5"/></svg>',
}
MARK = f'<span class="av"><img src="{A}/{os.path.basename(BRAND["logo"]["mark_on_dark"])}" alt=""></span>'
YOU = f'<span class="av you">{ICON["you"]}</span>'


def head(av, title, time, extra=""):
    return f'<div class="hd">{av}<b>{E(title)}</b>{extra}<span class="tm">{E(time)}</span></div>'


ag = FILM["agent"]
run = ag["run"]
card_run = (f'<div class="card" id="c-run">{head(MARK, run["title"], run["time"])}'
            f'<div class="rw"><span class="pill vio">{E(run["chip"])}</span><span class="dim">Source</span><b class="src">{E(run["source"])}</b></div></div>')
acc = ag["account"]
rows = "".join(f'<div class="rw sig" data-act="{1 if tag == "Act" else 0}">{ICON[ic]}<span class="tx">{E(text)}</span>'
               f'<span class="pill {"act" if tag == "Act" else "no"}">{E(tag)}</span></div>' for ic, text, tag in acc["rows"])
card_acc = (f'<div class="card" id="c-acc">{head(MARK, acc["title"], acc["time"])}'
            f'<div class="rw big">{ICON["building"]}<div><div class="tx">{E(acc["line"])}</div><div class="sub">{E(acc["sub"])}</div></div></div>'
            f'<div class="sep"></div>{rows}</div>')
th = ag["think"]
people = "".join(f'<span class="pill no">{E(p)}</span>' for p in th["people"])
card_think = (f'<div class="card" id="c-think">{head(MARK, th["title"], th["time"])}'
              f'<div class="say">{chars(th["text"])}</div><div class="sep"></div>'
              f'<div class="rw small"><span class="dim caps">{E(th["committee"])}</span>{people}</div></div>')
ap = ag["approve"]
ok_tag = '<span class="pill ok">' + E(ap["tag"]) + '</span>'
card_ap = (f'<div class="card" id="c-ap">{head(YOU, ap["title"], ap["time"], ok_tag)}'
           f'<div class="rw"><span class="cb">{ICON["check"]}</span><span class="tx">{E(ap["item"])}</span></div></div>')
dn = ag["done"]
card_dn = (f'<div class="card" id="c-dn">{head(MARK, dn["title"], dn["time"])}'
           f'<div class="rw">{ICON["mail"]}<span class="tx">{E(dn["row"])}</span><span class="tm">{E(dn["time"])}</span></div><div class="sep"></div>'
           f'<div class="rw small"><span class="dim caps">Stage</span><span class="sp1"></span><span class="pill no" id="st-from">{E(dn["from"])}</span>'
           f'<span class="arr">→</span><span class="pill vio" id="st-to">{E(dn["to"])}</span></div></div>')

bk = FILM["booking"]
slots = "".join(f'<span class="slot{" pick" if i == bk["pick"] else ""}">{E(x)}</span>' for i, x in enumerate(bk["slots"]))
card_bk = (f'<div class="card" id="c-bk">{head(MARK, bk["title"], bk["time"])}'
           f'<div class="day"><span class="chev">‹</span><b>{E(bk["day"])}</b><span class="chev">›</span></div>'
           f'<div class="slots">{slots}</div><div class="bkbtn">{E(bk["button"])}<span>→</span></div></div>')
bd = FILM["booked"]
people_html = "".join(f'<span class="face f{i}">{E(x)}</span>' for i, x in enumerate(bd["people"]))
CAL = '<svg viewBox="0 0 24 24"><rect x="3.5" y="5" width="17" height="15" rx="2.5"/><path d="M3.5 10h17M8 3v4M16 3v4"/></svg>'
card_bd = (f'<div class="card" id="c-bd">{head(MARK, bd["title"], bd["time"])}'
           f'<div class="rw big">{CAL}<div><div class="tx">{E(bd["row"])}</div><div class="sub">{E(bd["when"])}</div></div>'
           f'<span class="faces">{people_html}</span></div></div>')
booked = (f'<div id="flood"></div><div id="booked"><svg id="tick" viewBox="0 0 200 200"><circle cx="100" cy="100" r="86"/><path d="M58 104l28 28 58-62"/></svg>'
          f'<div id="bigok">{E(bd["big"])}</div>{card_bd}<div id="bnote" class="mono">{E(bd["note"])}</div></div>')
em = FILM["email"]
body = "".join(f'<p>{typed(p)}</p>' for p in em["body"])
email = (f'<div id="email"><div class="eh">{E(em["head"])}</div><div class="eto">To&nbsp;&nbsp;{E(em["to"])}</div>'
         f'<div class="esub"><span class="lab">Subject</span><span class="stx">{chars(em["subject"])}</span></div>'
         f'<div class="ebody">{body}</div><span id="caret"></span></div>')
elabels = "".join(f'<span class="el">{E(x)}</span>' for x in em["labels"])

labels = "".join(f'<div class="lbl"><i></i>{E(x)}</div>' for x in FILM["signal_labels"])
lk = FILM["lockup"]
line2 = E(lk["line2"]).replace("out.", '<span class="v">out.</span>')

T = {"bpm": FILM["bpm"], "bars": FILM["bars"], "counter": FILM["counter"]}
tpl = open("template.html").read()
rep = {
    "__FONTFACES__": "\n        ".join(faces),
    "__LOGO__": f'{A}/{os.path.basename(BRAND["logo"]["file"])}',
    "__LABELS__": labels, "__CARDS__": card_run + card_acc + card_think + card_ap + card_dn + card_bk, "__BOOKED__": booked, "__BOOKS__": E(FILM["words"]["books"]),
    "__EMAIL__": email, "__ELABELS__": elabels, "__DISCLAIMER__": E(FILM["disclaimer"]),
    "__READS__": E(FILM["words"]["reads"]), "__THINKS__": E(FILM["words"]["thinks"]), "__SENDS__": E(FILM["words"]["sends"]),
    "__L1__": E(lk["line1"]), "__L2__": line2, "__TITLE__": E(lk["title"]), "__URL__": E(lk["url"]),
    "__COUNTER_LABEL__": E(FILM["counter"]["label"]), "__T__": json.dumps(T),
}
for k, v in rep.items():
    tpl = tpl.replace(k, v)
os.makedirs("compositions", exist_ok=True)
open("compositions/signal.html", "w").write(tpl)
open("index.html", "w").write(f'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <title>Breakout Plays: Signal in. Meeting out.</title>
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
      <div id="el-signal" data-composition-id="signal" data-composition-src="compositions/signal.html" data-start="0" data-duration="{END:.3f}" data-track-index="1"></div>
    </div>
    <script>
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
''')
print(f"Signal in. Meeting out.: {END:.2f} s, {FILM['bars']} bars at {FILM['bpm']} BPM")
