#!/usr/bin/env python3
"""Build the signal-swarm motion test: copies fonts, the wordmark and GSAP, writes index.html.

  python3 templates/particle-swarm/build.py
"""
import json
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
F = json.load(open("film.json"))
BRAND = os.path.normpath(os.path.join(HERE, F["brand"]))
B = json.load(open(os.path.join(BRAND, "brand.json")))
END = F["bars"] * 240 / F["bpm"]
if os.path.exists("assets"):
    shutil.rmtree("assets")
os.makedirs("assets")
shutil.copy(os.path.join(BRAND, "fonts/manrope-200-800.woff2"), "assets/manrope.woff2")
shutil.copy(os.path.join(BRAND, "fonts/fragment-mono-400.woff2"), "assets/fragment-mono.woff2")
shutil.copy(os.path.join(BRAND, B["logo"]["on_dark"]), "assets/logo-on-dark.svg")
shutil.copy(os.path.join(HERE, "..", "..", "node_modules", "gsap", "dist", "gsap.min.js"), "assets/gsap.min.js")
tpl = open("template.html").read().replace("__T__", json.dumps({"bpm": F["bpm"], "bars": F["bars"]}))
os.makedirs("compositions", exist_ok=True)
open("compositions/swarm.html", "w").write(tpl)
open("index.html", "w").write(f'''<!doctype html>
<html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width=1920, height=1080" />
<title>Signal swarm motion test</title><script src="assets/gsap.min.js"></script>
<style>* {{ margin: 0; padding: 0; box-sizing: border-box; }} html, body {{ width: 1920px; height: 1080px; overflow: hidden; background: #000; }}
#main {{ position: relative; width: 1920px; height: 1080px; overflow: hidden; }} [data-composition-id="main"] > div[data-composition-src] {{ position: absolute; inset: 0; }}</style>
</head><body>
<div id="main" data-composition-id="main" data-start="0" data-duration="{END:.3f}" data-width="1920" data-height="1080">
  <div id="el-swarm" data-composition-id="swarm" data-composition-src="compositions/swarm.html" data-start="0" data-duration="{END:.3f}" data-track-index="1"></div>
</div>
<script>window.__timelines["main"] = gsap.timeline({{ paused: true }});</script>
</body></html>
''')
print(f"swarm test: {END:.2f} s")
