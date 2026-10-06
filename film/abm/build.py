#!/usr/bin/env python3
"""Build 1 ABM film: series.json + accounts/<slug>/account.json + brand.json -> out/<slug>/ (a HyperFrames project).

  python3 film/abm/build.py korn-ferry

All text is written as markup here (typed text as 1 span per character, the email as 1 span per word),
so nothing falls back to a system font at render time. The beats' times live in series.json "at".
"""
import html
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SLUG = sys.argv[1] if len(sys.argv) > 1 else "korn-ferry"
SER = json.load(open(os.path.join(HERE, "series.json")))
ACC_DIR = os.path.join(HERE, "accounts", SLUG)
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
for role in ("body", "mono"):
    f = BRAND["fonts"][role]
    for face in f.get("faces", []):
        shutil.copy(os.path.join(BRAND_DIR, face["file"]), os.path.join(OUT, A, face["file"]))
        fontfaces.append(f'@font-face {{ font-family: "{f["family"]}"; src: url("{A}/{face["file"]}") format("woff2"); '
                         f'font-weight: {face["weight"]}; font-style: {face.get("style", "normal")}; }}')
for k in ("file", "mark_on_dark"):
    shutil.copy(os.path.join(BRAND_DIR, BRAND["logo"][k]), os.path.join(OUT, A, os.path.basename(BRAND["logo"][k])))
cap = ACC["capture"]
shutil.copy(os.path.join(ACC_DIR, cap["file"]), os.path.join(OUT, A, "site" + os.path.splitext(cap["file"])[1]))
shutil.copy(os.path.join(HERE, "..", "assets", "screens", "agent-avatar.png"), os.path.join(OUT, A, "agent-avatar.png"))
gsap = os.path.join(HERE, "..", "..", "node_modules", "gsap", "dist", "gsap.min.js")
GSAP = "https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"
if os.path.exists(gsap):
    shutil.copy(gsap, os.path.join(OUT, A, "gsap.min.js"))
    GSAP = f"{A}/gsap.min.js"


# ------------------------------------------------------------------ markup helpers
def chars(text, cls="ch"):
    return "".join(f'<span class="{cls}">{E(c)}</span>' for c in text)


def words(text):
    """1 span per word; '[0]phrase[/0]' marks the phrase drawn from signal 0."""
    out, pos = [], 0

    def plain(s):
        return " ".join(f'<span class="w">{E(x)}</span>' for x in s.split())

    for m in re.finditer(r"\[(\w+)\](.*?)\[/\1\]", text):
        out.append(plain(text[pos:m.start()]))
        out.append(f'<span class="ph" data-ph="{m.group(1)}">{plain(m.group(2))}</span>')
        pos = m.end()
    out.append(plain(text[pos:]))
    return " ".join(x for x in out if x)


def row(feature, b, q):
    return (f'<div class="cmp"><div class="cf mono">{E(feature)}</div>'
            f'<div class="cr b"><span class="who">Breakout</span><span class="txt">{E(b)}</span></div>'
            f'<div class="cr q"><span class="who">Qualified</span><span class="txt">{E(q)}</span></div>'
            f'<div class="csrc mono">Source: {E(SER["source"])}</div></div>')


MARK = f'<span class="av"><img src="{A}/{os.path.basename(BRAND["logo"]["mark_on_dark"])}" alt=""></span>'
CHECK = '<svg class="ck" viewBox="0 0 24 24"><path d="m5 12 4.5 4.5L19 7"/></svg>'
ask, who, why, act, sw, bo, cl, bk = (SER[k] for k in ("ask", "who", "why", "act", "switch", "buyout", "close", "booked"))
vis, em = ACC["visitor"], ACC["email"]

notes = "".join(f'<div class="note">{E(x)}</div>' for x in ACC["widget_notes"])
turn = "".join(f'<div class="slam turn">{E(x)}</div>' for x in SER["turn"])
bw = (f'<div id="bw"><div class="bwh"><img class="bav" src="{A}/agent-avatar.png" alt=""><b>Breakout</b></div>'
      f'<div class="bgreet">{E(ask["greeting"])}</div><div class="bbook">{E(ask["book"])}</div>'
      f'<div class="bpanel"><div class="ub">{chars(ACC["question"], "qc")}</div>'
      f'<div class="ar"><img class="bav s" src="{A}/agent-avatar.png" alt=""><span class="dots"><i></i><i></i><i></i></span>'
      f'<div class="ans">{words(ACC["answer"])}</div></div>'
      f'<div class="mod"><div><b>{E(ACC["module"]["title"])}</b><span>{E(ACC["module"]["sub"])}</span></div><em>{E(ACC["module"]["cta"])}</em></div>'
      f'<div class="bin"><span class="ph0">{E(ask["placeholder"])}</span><span class="typed">{chars(ACC["question"], "ic")}</span><span class="bcaret"></span>'
      f'<span class="bsend"><svg viewBox="0 0 24 24"><path d="M4 12 20 4l-4 16-4-7z"/></svg></span></div></div>'
      f'<div class="bpow">{E(ask["powered"])} <b>breakout</b></div></div>')
provs = "".join(f'<span class="prov">{E(p)}</span>' for p in who["providers"])
card_who = (f'<div class="card" id="c-who"><div class="hd">{MARK}<b>Breakout · Visitor identified</b><span class="tm">9:14 AM</span></div>'
            f'<div class="rw" id="w-co"><span class="k mono">Company</span><div><div class="tx">{E(vis["company"])}</div><div class="sub">{E(vis["company_sub"])}</div></div>{CHECK}</div>'
            f'<div class="rw" id="w-wf"><span class="k mono">Waterfall</span><div class="provs">{provs}</div></div>'
            f'<div class="rw" id="w-pe"><span class="k mono">Person</span><span class="pav">{E(vis["initials"])}</span><div><div class="tx">{E(vis["person"])}</div><div class="sub">{E(vis["role"])}</div></div>{CHECK}</div></div>')
sigs = "".join(f'<div class="sig"><span class="sl mono">{E(a)}</span><span class="cat mono">{E(b)}</span><span class="tag">Act</span></div>' for a, b in ACC["signals"])
body = "".join(f'<p>{words(p)}</p>' for p in em["body"])
email = (f'<div id="email"><div class="eh">{E(em["head"])} · From {E(em["from"])}</div>'
         f'<div class="eto"><span class="lab">To</span>{E(em["to"])}</div>'
         f'<div class="esub"><span class="lab">Subject</span><span class="stx">{E(em["subject"])}</span></div>'
         f'<div class="ebody">{body}</div><div class="esend" id="esend">{E(em["send"])}<svg viewBox="0 0 24 24"><path d="M4 12 20 4l-4 16-4-7z"/></svg></div></div>')
CAL = '<svg viewBox="0 0 24 24"><rect x="3.5" y="5" width="17" height="15" rx="2.5"/><path d="M3.5 10h17M8 3v4M16 3v4"/></svg>'
people = "".join(f'<span class="face f{i}">{E(x)}</span>' for i, x in enumerate(ACC["booked"]["people"]))
booked = (f'<div id="bigok">{E(bk["big"])}</div><svg id="tick" viewBox="0 0 200 200"><circle cx="100" cy="100" r="86"/><path d="M58 104l28 28 58-62"/></svg>'
          f'<div class="card" id="c-bd"><div class="hd">{MARK}<b>{E(bk["title"])}</b><span class="tm">{E(bk["time"])}</span></div>'
          f'<div class="rw">{CAL}<div><div class="tx">{E(bk["row"])}</div><div class="sub">{E(ACC["booked"]["when"])} · {E(vis["person"])} and {E(co)}</div></div>'
          f'<span class="faces">{people}</span></div></div>')

T = {"bpm": SER["bpm"], "bars": SER["bars"], "at": SER["at"], "cap": cap, "nsig": len(ACC["signals"])}
tpl = open(os.path.join(HERE, "template.html")).read()
rep = {
    "__FONTFACES__": "\n        ".join(fontfaces), "__LOGO__": f'{A}/{os.path.basename(BRAND["logo"]["file"])}',
    "__SITE__": f'{A}/site{os.path.splitext(cap["file"])[1]}', "__DOMAIN__": E(ACC["domain"]), "__COMPANY__": E(co),
    "__NOTES__": notes, "__TURN__": turn, "__ASKTITLE__": E(ask["title"]), "__TODAY__": E(ACC["today_line"]), "__BLINE__": E(ask["breakout_line"]),
    "__BW__": bw, "__CARDWHO__": card_who, "__ROWWHO__": row(who["feature"], who["breakout"], who["qualified"]),
    "__WHY1__": E(why["line1"]), "__WHY2__": E(why["line2"]), "__SIGS__": sigs, "__SIGHEAD__": E(f'{vis["company"]} · {vis["person"]}, {vis["role"]}'),
    "__ROWACT__": row(act["feature"], act["breakout"], act["qualified"]), "__EMAIL__": email, "__BOOKED__": booked,
    "__SWB__": E(sw["breakout_big"]), "__SWBN__": E(sw["breakout_note"]), "__SWQ__": E(sw["qualified_big"]), "__SWQN__": E(sw["qualified_note"]), "__SWF__": E(sw["feature"]),
    "__BO1__": E(bo["line1"]), "__BO2__": E(bo["line2"]), "__BON__": E(bo["note"]),
    "__CTA__": E(cl["cta"]), "__URL__": E(cl["url"]), "__MADE__": E(cl["made_for"].replace("{company}", co)), "__T__": json.dumps(T),
}
for k, v in rep.items():
    tpl = tpl.replace(k, v)
os.makedirs(os.path.join(OUT, "compositions"), exist_ok=True)
open(os.path.join(OUT, "compositions", "abm.html"), "w").write(tpl)
open(os.path.join(OUT, "index.html"), "w").write(f'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <title>Breakout for {E(co)}</title>
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
      <div id="el-abm" data-composition-id="abm" data-composition-src="compositions/abm.html" data-start="0" data-duration="{END:.3f}" data-track-index="1"></div>
    </div>
    <script>
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
''')
print(f"ABM film for {co}: {END:.2f} s, {SER['bars']} bars at {SER['bpm']} BPM -> film/abm/out/{SLUG}/")
