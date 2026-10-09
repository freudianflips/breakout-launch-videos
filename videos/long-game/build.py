#!/usr/bin/env python3
"""Build a cartoon story: film.json + brand.json -> index.html and compositions/cartoon.html.

  python3 build.py

The characters are simple SVG people made here by person() (head, hair, eyes, mouth, arms on hinges) and the
agent by agent(); template.html moves them. All text is markup; New Kansas when installed, else Fraunces.
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
for k in ("file", "on_dark"):
    shutil.copy(os.path.join(BRAND_DIR, BRAND["logo"][k]), f"{A}/{os.path.basename(BRAND['logo'][k])}")
gsap = os.path.join(HERE, "..", "..", "node_modules", "gsap", "dist", "gsap.min.js")
GSAP = "https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"
if os.path.exists(gsap):
    shutil.copy(gsap, f"{A}/gsap.min.js")
    GSAP = f"{A}/gsap.min.js"


def kw(text):
    return re.sub(r"\*(.+?)\*", r"<em>\1</em>", E(text))


INK = "#1d1530"
HAIR = {
    "bob": ('<circle cx="100" cy="108" r="70" fill="{h}"/><rect x="30" y="100" width="140" height="70" rx="30" fill="{h}"/>',
            '<path d="M44 104 Q56 44 100 44 Q144 44 156 104 Q132 72 100 76 Q68 72 44 104Z" fill="{h}"/>'),
    "short": ("", '<path d="M46 98 Q52 48 100 46 Q148 48 154 98 Q128 66 100 70 Q72 66 46 98Z" fill="{h}"/>'),
    "bun": ('<circle cx="100" cy="46" r="26" fill="{h}"/>', '<path d="M46 102 Q52 50 100 50 Q148 50 154 102 Q128 70 100 74 Q72 70 46 102Z" fill="{h}"/>'),
}


def person(pid, skin, hair, top, style="bob", glasses=False, grey=False):
    """A cartoon person in a 200x320 box: hinged arms (.armL/.armR), blinking eyes (.eye), a mouth (.mouth)."""
    if grey:
        skin = hair = top = "#b4b1c4"
    back, front = (s.format(h=hair) for s in HAIR[style])
    face = "" if grey else (
        f'<g class="eyes"><ellipse class="eye" cx="82" cy="116" rx="5.5" ry="7.5" fill="{INK}"/><ellipse class="eye" cx="118" cy="116" rx="5.5" ry="7.5" fill="{INK}"/></g>'
        f'<circle cx="68" cy="134" r="9" fill="#ff7aa8" opacity="0.45"/><circle cx="132" cy="134" r="9" fill="#ff7aa8" opacity="0.45"/>'
        f'<path class="mouth" d="M86 138 Q100 152 114 138" stroke="{INK}" stroke-width="4.5" fill="none" stroke-linecap="round"/>'
        + (f'<g fill="none" stroke="{INK}" stroke-width="3"><circle cx="82" cy="116" r="14"/><circle cx="118" cy="116" r="14"/><path d="M96 116h8"/></g>' if glasses else ""))
    arm = lambda cls, x0, x1: (f'<g class="{cls}" style="transform-origin:{x0}px 205px"><path d="M{x0} 205 L{x1} 285" stroke="{top}" stroke-width="28" stroke-linecap="round"/>'
                               f'<circle cx="{x1}" cy="290" r="15" fill="{skin}"/></g>')
    return (f'<svg class="person" id="{pid}" viewBox="0 0 200 320" overflow="visible"><g class="bob">{back}'
            f'{arm("armL", 58, 34)}{arm("armR", 142, 166)}'
            f'<path d="M38 320 Q38 192 100 186 Q162 192 162 320Z" fill="{top}"/><rect x="88" y="158" width="24" height="34" rx="8" fill="{skin}"/>'
            f'<g class="head" style="transform-origin:100px 165px"><circle cx="100" cy="112" r="56" fill="{skin}"/>{front}{face}</g></g></svg>')


def agent(aid):
    """Breakout's agent: a friendly violet character with eyes that look around (.pupil) and a pink antenna."""
    return (f'<svg class="agent" id="{aid}" viewBox="0 0 200 220" overflow="visible"><defs><radialGradient id="ag{aid}" cx="40%" cy="35%" r="70%">'
            f'<stop offset="0" stop-color="#a46bff"/><stop offset="0.6" stop-color="#5a12ff"/><stop offset="1" stop-color="#3a00c4"/></radialGradient></defs>'
            f'<g class="bob"><circle class="glow" cx="100" cy="120" r="96" fill="#4c00ff" opacity="0.18"/>'
            f'<path d="M100 52 L100 30" stroke="#5a12ff" stroke-width="6" stroke-linecap="round"/><circle class="tip" cx="100" cy="24" r="11" fill="#ff5ad1"/>'
            f'<circle cx="100" cy="120" r="70" fill="url(#ag{aid})"/><ellipse cx="74" cy="88" rx="18" ry="10" fill="#fff" opacity="0.25"/>'
            f'<g class="eyes"><ellipse class="eye" cx="78" cy="114" rx="14" ry="18" fill="#fff"/><ellipse class="eye" cx="122" cy="114" rx="14" ry="18" fill="#fff"/>'
            f'<circle class="pupil" cx="80" cy="117" r="7" fill="{INK}"/><circle class="pupil" cx="124" cy="117" r="7" fill="{INK}"/></g>'
            f'<path class="mouth" d="M84 146 Q100 160 116 146" stroke="#fff" stroke-width="5" fill="none" stroke-linecap="round"/></g></svg>')


C = {  # the cast
    "maya": dict(skin="#e8b08a", hair="#3a1f5c", top="#ff5ad1", style="bob"),
    "sam": dict(skin="#b97c55", hair="#1d1530", top="#9cf5c0", style="short", glasses=True),
    "cmo": dict(skin="#8d5a3b", hair="#1d1530", top="#be79ff", style="bun"),
    "cfo": dict(skin="#f2cfb3", hair="#9a96a8", top="#140b3c", style="short"),
    "revops": dict(skin="#e3a985", hair="#7a3b1f", top="#68e6ff", style="bob"),
}
mm, rp, ch, al, em, lp, bk = (F[k] for k in ("maya", "rep", "chat", "alert", "email", "lapse", "back"))
ENV = '<svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2.5"/><path d="m3.5 7 8.5 6 8.5-6"/></svg>'

rep = {
    "__FONTFACES__": "\n        ".join(fontfaces),
    "__MAYA__": person("maya", **C["maya"]), "__MAYA_GREY__": person("mayaGrey", **C["maya"], grey=True),
    "__MAYA2__": person("maya2", **C["maya"]), "__MAYA3__": person("maya3", **C["maya"]), "__MAYA4__": person("maya4", **C["maya"]),
    "__SAM__": person("sam", **C["sam"]), "__SAM2__": person("sam2", **C["sam"]), "__SAM3__": person("sam3", **C["sam"]),
    "__CMO__": person("cmo", **C["cmo"]), "__CFO__": person("cfo", **C["cfo"]), "__REVOPS__": person("revops", **C["revops"]),
    "__CFO2__": person("cfo2", **C["cfo"]), "__MAYAHEAD__": person("mayaHead", **C["maya"]),
    "__AGENT1__": agent("ag1"), "__AGENT2__": agent("ag2"), "__AGENT3__": agent("ag3"), "__AGENT4__": agent("ag4"), "__AGENT5__": agent("ag5"),
    "__AGENTNAME__": E(F["agent"]), "__MNAME__": E(mm["name"]), "__MROLE__": E(mm["role"]), "__COMPANY__": E(mm["company"]),
    "__RNAME__": E(rp["name"]), "__Q__": "".join(f'<span class="qc">{E(c)}</span>' for c in ch["question"]),
    "__A__": " ".join(f'<span class="w">{E(x)}</span>' for x in ch["answer"].split()), "__HELLO__": E(ch["rep_hello"]), "__LEAVE__": E(ch["leave"]),
    "__ALERT__": E(al["title"]), "__ACHIPS__": "".join(f"<span>{E(x)}</span>" for x in al["chips"]),
    "__COMMITTEE__": "".join(f'<b class="role r{i}">{E(x)}</b>' for i, x in enumerate(F["committee"])),
    "__ESUBJ__": E(em["subject"]), "__EFROM__": E(em["from"]), "__LINKEDIN__": E(F["linkedin"]), "__ENV__": ENV,
    "__DAYS__": "".join(f'<b class="day">{E(x)}</b>' for x in lp["days"]), "__SIGNALS__": "".join(f'<span class="signal">{E(x)}</span>' for x in lp["signals"]),
    "__BTITLE__": E(bk["title"]), "__BSUB__": E(bk["sub"]), "__SLOTS__": "".join(f'<span class="slot">{E(x)}</span>' for x in F["slots"]),
    "__BOOKED__": kw(F["booked"]), "__LOCK__": kw(F["lockup"]["line"]), "__URL__": E(F["lockup"]["url"]), "__DISC__": E(F["disclaimer"]),
    "__CAPTIONS__": "".join(f'<div class="cap">{E(c["text"])}</div>' for c in F["captions"]),
    "__T__": json.dumps({"bpm": F["bpm"], "bars": F["bars"], "at": F["at"], "caps": [[c["at"], c["until"]] for c in F["captions"]]}),
}
tpl = open("template.html").read()
for k, v in rep.items():
    tpl = tpl.replace(k, v)
os.makedirs("compositions", exist_ok=True)
open("compositions/cartoon.html", "w").write(tpl)
open("index.html", "w").write(f'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <title>Breakout: the long game</title>
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
      <div id="el-c" data-composition-id="cartoon" data-composition-src="compositions/cartoon.html" data-start="0" data-duration="{END:.3f}" data-track-index="1"></div>
    </div>
    <script>
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
''')
print(f"cartoon: {END:.2f} s, {F['bars']} bars at {F['bpm']} BPM")
