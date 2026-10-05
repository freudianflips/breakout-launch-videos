#!/usr/bin/env python3
"""Build 'Rush', the fast-cut LinkedIn feed film: film.json -> index.html (1080x1350, HyperFrames).

  python3 film/rush/build.py [wide|feed] [story]   (default wide: 1920x1080; feed: 1080x1350)

A story is film.json, or film-<story>.json beside it ("headcount" reads film-headcount.json).

Every shot sits on the 140 BPM beat grid in film.json. Words are written into the markup here, so
nothing falls back to a system font at render time. The look and the motion live in template.html.
"""
import html
import json
import math
import os
import shutil
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
STORY = sys.argv[2] if len(sys.argv) > 2 else ""
TAG = f"{STORY}-" if STORY else ""
F = json.load(open(f"film-{STORY}.json" if STORY else "film.json"))
BEAT = 60 / F["bpm"]
END = F["beats"] * BEAT
FMT = sys.argv[1] if len(sys.argv) > 1 else "wide"
W, H = F["formats"][FMT]
LOCK = next(s["at"] for s in F["shots"] if any(i["type"] == "lockup" for i in s["items"]))
E = html.escape

# ------------------------------------------------------------------ assets
A = "assets"
if os.path.exists(A):
    shutil.rmtree(A)
os.makedirs(A)
for src in ("docs/look-tests/fonts/anton-400.woff2", "brand/fonts/manrope-200-800.woff2", "brand/fonts/fragment-mono-400.woff2",
            "brand/source/breakout-logo-white.svg", "brand/logo.svg", "brand/mark-on-dark.svg"):
    shutil.copy(os.path.join(REPO, src), A)
shutil.copy(os.path.join(REPO, "node_modules", "gsap", "dist", "gsap.min.js"), A)


def png_size(path):
    with open(path, "rb") as f:
        f.read(16)
        return struct.unpack(">II", f.read(8))


# ------------------------------------------------------------------ shots
P = F["palette"]
col = lambda c: P.get(c, c)
out = []
for i, s in enumerate(F["shots"]):
    attrs = f'data-a="{s["at"]}" data-b="{s["to"]}" data-shake="{s.get("shake", 0)}"'
    inner = []
    if s.get("lines"):
        rays = "".join(
            f'<line x1="{W / 2 + 90 * math.cos(k * 0.2244):.1f}" y1="{H / 2 + 90 * math.sin(k * 0.2244):.1f}" '
            f'x2="{W / 2 + 1400 * math.cos(k * 0.2244):.1f}" y2="{H / 2 + 1400 * math.sin(k * 0.2244):.1f}" '
            f'stroke-width="{3 + (k * 7) % 9}" stroke-dasharray="{60 + (k * 37) % 140} {220 + (k * 53) % 300}"/>'
            for k in range(28))
        inner.append(f'<svg class="lines" viewBox="0 0 {W} {H}" stroke="{col(s["lines"])}">{rays}</svg>')
    for it in s["items"]:
        it = {**it, **it.get(FMT, {})}
        if it.get("hide"):
            continue
        t, at = it["type"], it.get("at", 0)
        common = f'data-at="{at}" data-fx="{it.get("fx", "slam")}"'
        if t == "word":
            inner.append(f'<div class="it word{" rgb" if it.get("rgb") else ""}" {common} data-fit="{it.get("fit", 0.9)}" '
                         f'style="left:{it.get("x", 0.5) * W:.0f}px;top:{it["y"] * H:.0f}px;color:{col(it["color"])}">'
                         f'<span{" style=" + chr(34) + "text-transform:none" + chr(34) if it.get("keep_case") else ""}>{E(it["text"])}</span></div>')
        elif t == "screen":
            sw, sh = png_size(os.path.join(REPO, "film/assets/screens", it["src"]))
            shutil.copy(os.path.join(REPO, "film/assets/screens", it["src"]), A)
            cx, cy, cw, ch = it["crop"]
            bx, by, bw, bh = it["box"]
            k = bw / cw
            img = (f'<img src="{A}/{it["src"]}" style="width:{sw * k:.1f}px;height:{sh * k:.1f}px;'
                   f'left:{-cx * k:.1f}px;top:{-cy * k:.1f}px">')
            filt = (f'filter:grayscale(1) brightness({it["dim"] * 3:.2f});opacity:{it["dim"]};' if it.get("gray") else "")
            inner.append(f'<div class="it screen{" bg" if it.get("dim") else ""}" {common} data-tilt="{it.get("tilt", 0)}" '
                         f'style="left:{bx}px;top:{by}px;width:{bw}px;height:{bh}px;border-radius:{it.get("radius", 22)}px;{filt}">{img}</div>')
        elif t == "logo":
            inner.append(f'<div class="it logo" {common} style="top:{it["y"] * H:.0f}px">'
                         f'<img src="{A}/breakout-logo-white.svg" style="width:{it["w"]}px"></div>')
        elif t == "counter":
            inner.append(f'<div class="it word counter" {common} data-fit="{it["fit"]}" data-to="{it["to"]}" data-suffix="{E(it["suffix"])}" '
                         f'style="left:{it.get("x", 0.5) * W:.0f}px;top:{it["y"] * H:.0f}px;color:{col(it["color"])}"><span>{it["to"]}{E(it["suffix"])}</span></div>')
        elif t == "chip":
            inner.append(f'<div class="it chip" {common} data-rot="{it["rot"]}" style="left:{it["x"] * W:.0f}px;top:{it["y"] * H:.0f}px;'
                         f'background:{col(it["color"])};color:{P["w"] if it["color"] in ("blue", "hot") else P["k"]}">{E(it["text"])}</div>')
        elif t == "ring":
            inner.append(f'<div class="it ring" {common} style="left:{it["x"] * W:.0f}px;top:{it["y"] * H:.0f}px"></div>')
        elif t == "booked":
            inner.append(f'<div class="it booked" {common}><div class="flood" style="background:{col(it["flood"])}"></div>'
                         f'<svg class="tick" viewBox="0 0 200 200" stroke="{col(it["color"])}"><circle cx="100" cy="100" r="86"/><path d="M58 104l28 28 58-62"/></svg>'
                         f'<div class="word bk" data-fit="0.9" style="color:{col(it["color"])}"><span>{E(it["text"])}</span></div></div>')
        elif t == "lockup":
            inner.append(f'<div class="it lockup" {common}><img class="lk-logo" src="{A}/breakout-logo-white.svg">'
                         f'<div class="lk-line">{E(it["line"])}</div><div class="lk-url" style="color:{P["acid"]}">{E(it["url"])}</div></div>')
    out.append(f'<div class="shot" id="s{i}" {attrs} style="background:{col(s["ground"])}">{"".join(inner)}</div>')

flick = (f'<div id="flick"><img src="{A}/breakout-logo-white.svg"></div>')
tpl = open("template.html").read()
for k, v in {"__SHOTS__": "\n      ".join(out), "__FLICK__": flick, "__W__": str(W), "__H__": str(H), "__END__": f"{END:.4f}",
             "__T__": json.dumps({"beat": BEAT, "end": END, "flicks": F["flicks"], "palette": P, "lock": LOCK})}.items():
    tpl = tpl.replace(k, v)
open(f"index-{TAG}{FMT}.html", "w").write(tpl)
open("index.html", "w").write(tpl)  # hyperframes snapshot reads index.html: the last format built
print(f"Rush ({TAG}{FMT}): {END:.2f} s, {F['beats']} beats at {F['bpm']} BPM, {len(F['shots'])} shots, {W}x{H}")
