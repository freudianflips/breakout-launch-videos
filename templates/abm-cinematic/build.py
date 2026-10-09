#!/usr/bin/env python3
"""Build 1 ABM film: series.json + accounts/<slug>/account.json + brand.json -> out/<slug>/ (a HyperFrames project).

  python3 templates/abm-cinematic/build.py korn-ferry

All text is written as markup here (typed text as 1 span per character, the answer and the email as 1 span
per word), so nothing falls back to a system font at render time. '*word*' becomes an italic key word.
Headlines use New Kansas when it is installed, else the brand's Fraunces stand-in.
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
ACC_DIR = os.path.join(HERE, "..", "..", "accounts", SLUG)
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
        src = f'url("{A}/{face["file"]}") format("woff2")'
        family = f["family"]
        if role == "display":     # New Kansas first, wherever it is installed
            family = "NK"
            src = ", ".join(f'local("{n}")' for n in f.get("local", [])) + ", " + src
        fontfaces.append(f'@font-face {{ font-family: "{family}"; src: {src}; font-weight: {face["weight"]}; font-style: {face.get("style", "normal")}; }}')
for k in ("file", "mark_on_dark", "on_dark"):
    shutil.copy(os.path.join(BRAND_DIR, BRAND["logo"][k]), os.path.join(OUT, A, os.path.basename(BRAND["logo"][k])))
cap = ACC["capture"]
shutil.copy(os.path.join(ACC_DIR, cap["file"]), os.path.join(OUT, A, "site" + os.path.splitext(cap["file"])[1]))
shutil.copy(os.path.join(HERE, "..", "..", "assets", "screens", "agent-avatar.png"), os.path.join(OUT, A, "agent-avatar.png"))
gsap = os.path.join(HERE, "..", "..", "node_modules", "gsap", "dist", "gsap.min.js")
GSAP = "https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"
if os.path.exists(gsap):
    shutil.copy(gsap, os.path.join(OUT, A, "gsap.min.js"))
    GSAP = f"{A}/gsap.min.js"


# ------------------------------------------------------------------ markup helpers
def kw(text):
    """'*word*' -> an italic key word, the site's headline style."""
    return re.sub(r"\*(.+?)\*", r"<em>\1</em>", E(text))


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


def versus(key, b_big, q_big):
    v = SER[key]
    return (f'<div class="vs" id="{key}"><div class="half hb"><span class="who">Breakout</span><div class="vb nk">{kw(b_big)}</div></div>'
            f'<div class="half hq"><span class="who">Qualified</span><div class="vq nk">{kw(q_big)}</div></div>'
            f'<div class="vlabel mono">{E(v["label"])}</div></div>')


MARK = f'<span class="av"><img src="{A}/{os.path.basename(BRAND["logo"]["mark_on_dark"])}" alt=""></span>'
ask, who, why, act, bo, cl, bk = (SER[k] for k in ("ask", "who", "why", "act", "buyout", "close", "booked"))
vis, em = ACC["visitor"], ACC["email"]

notes = "".join(f'<div class="note nk">{kw(x)}</div>' for x in ACC["widget_notes"])
hook = "".join(f'<div class="x nk hookl">{kw(x)}</div>' for x in SER["hook"])
bw = (f'<div id="bw"><div class="bwh"><img class="bav" src="{A}/agent-avatar.png" alt=""><b>Breakout</b></div>'
      f'<div class="bgreet">{E(ask["greeting"])}</div><div class="bbook">{E(ask["book"])}</div>'
      f'<div class="bpanel"><div class="ub">{E(ACC["question"])}</div>'
      f'<div class="ar"><img class="bav s" src="{A}/agent-avatar.png" alt=""><span class="dots"><i></i><i></i><i></i></span>'
      f'<div class="ans">{words(ACC["answer"])}</div></div>'
      f'<div class="mod"><div><b>{E(ACC["module"]["title"])}</b><span>{E(ACC["module"]["sub"])}</span></div><em>{E(ACC["module"]["cta"])}</em></div>'
      f'<div class="bin"><span class="ph0">{E(ask["placeholder"])}</span><span class="typed">{chars(ACC["question"], "ic")}</span><span class="bcaret"></span>'
      f'<span class="bsend"><svg viewBox="0 0 24 24"><path d="M4 12 20 4l-4 16-4-7z"/></svg></span></div></div>'
      f'<div class="bpow">{E(ask["powered"])} <b>breakout</b></div></div>')
provs = "".join(f'<span class="prov">{E(p)}</span>' for p in who["providers"])
person = (f'<div id="person"><div class="pav">{E(vis["initials"])}</div><div class="pname nk">{E(vis["person"])}</div>'
          f'<div class="prole">{E(vis["role"])}</div><div class="pco">{E(vis["company"])} · {E(vis["company_sub"])}</div>'
          f'<div class="provs">{provs}<span class="match">✓ {E(who["matched"])}</span></div></div>')
chips = "".join(f'<span class="schip">{E(a)}</span>' for a, b in ACC["signals"])
body = "".join(f'<p>{words(p)}</p>' for p in em["body"])
email = (f'<div id="email"><div class="eh">{E(em["head"])} · From {E(em["from"])}</div>'
         f'<div class="eto"><span class="lab">To</span>{E(em["to"])}</div>'
         f'<div class="esub"><span class="lab">Subject</span><span class="stx">{E(em["subject"])}</span></div>'
         f'<div class="ebody">{body}</div><div class="esend" id="esend">{E(em["send"])}<svg viewBox="0 0 24 24"><path d="M4 12 20 4l-4 16-4-7z"/></svg></div></div>')
CAL = '<svg viewBox="0 0 24 24"><rect x="3.5" y="5" width="17" height="15" rx="2.5"/><path d="M3.5 10h17M8 3v4M16 3v4"/></svg>'
people = "".join(f'<span class="face f{i}">{E(x)}</span>' for i, x in enumerate(ACC["booked"]["people"]))
booked = (f'<div id="bigok" class="nk">{kw(bk["big"])}</div><svg id="tick" viewBox="0 0 200 200"><circle cx="100" cy="100" r="86"/><path d="M58 104l28 28 58-62"/></svg>'
          f'<div class="card" id="c-bd"><div class="hd">{MARK}<b>{E(bk["title"])}</b><span class="tm">{E(bk["time"])}</span></div>'
          f'<div class="rw">{CAL}<div><div class="tx">{E(bk["row"])}</div><div class="sub">{E(ACC["booked"]["when"])} · {E(vis["person"])} and {E(co)}</div></div>'
          f'<span class="faces">{people}</span></div></div>')
vs1, vs2, vs3 = SER["vs1"], SER["vs2"], SER["vs3"]

T = {"bpm": SER["bpm"], "bars": SER["bars"], "at": SER["at"], "cap": cap, "count": why["count"], "suffix": why["suffix"]}
tpl = open(os.path.join(HERE, "template.html")).read()
rep = {
    "__FONTFACES__": "\n        ".join(fontfaces), "__LOGO__": f'{A}/{os.path.basename(BRAND["logo"]["file"])}',
    "__SITE__": f'{A}/site{os.path.splitext(cap["file"])[1]}', "__DOMAIN__": E(ACC["domain"]), "__COMPANY__": E(co),
    "__NOTES__": notes, "__HOOK__": hook, "__YEAR__": kw(SER["year"]), "__AGENT__": kw(SER["agent"]),
    "__ASKTITLE__": kw(ask["title"]), "__ASKSUB__": E(ask["sub"]), "__BW__": bw,
    "__WHOLINE__": kw(who["line"]), "__PERSON__": person, "__VS1__": versus("vs1", vs1["breakout"], vs1["qualified"]),
    "__COUNTLABEL__": kw(why["label"]), "__CHIPS__": chips, "__VS2Q__": kw(vs2["qualified"]), "__VS2L__": E(vs2["label"]),
    "__ACT1__": kw(act["line1"]), "__ACT2__": kw(act["line2"]), "__EMAIL__": email, "__BOOKED__": booked,
    "__VS3__": versus("vs3", vs3["breakout"], vs3["qualified"]),
    "__BO1__": kw(bo["line1"]), "__BO2__": kw(bo["line2"]), "__BON__": E(bo["note"]),
    "__CTA__": E(cl["cta"]), "__URL__": E(cl["url"]), "__MADE__": kw(cl["made_for"].replace("{company}", co)), "__T__": json.dumps(T),
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
print(f"ABM film for {co}: {END:.2f} s, {SER['bars']} bars at {SER['bpm']} BPM -> {os.path.relpath(OUT, os.path.join(HERE, '..', '..'))}/")
