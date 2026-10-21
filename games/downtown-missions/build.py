#!/usr/bin/env python3
"""Build the game: game.src.html + the brand's logo and mark + the target accounts' logos (logos/) -> index.html (a full page to open locally)
and, with --artifact <path>, the same page as a body fragment for publishing.

  python3 build.py [--artifact /path/to/page.html]
"""
import base64
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BRAND = os.path.normpath(os.path.join(HERE, "..", "..", "brand"))
B = json.load(open(os.path.join(BRAND, "brand.json")))
src = open(os.path.join(HERE, "game.src.html")).read()
logo = re.sub(r"<\?xml.*?\?>", "", open(os.path.join(BRAND, B["logo"]["on_dark"])).read()).strip()
mark_svg = re.sub(r"<\?xml.*?\?>", "", open(os.path.join(BRAND, B["logo"]["mark_on_dark"])).read()).strip()
mark64 = base64.b64encode(mark_svg.encode()).decode()
def sized(svg):
    """Give an SVG explicit width and height from its viewBox, so it has a natural size when drawn onto a canvas."""
    head = svg.split(">", 1)[0]
    if "width=" not in head:
        vb = re.search(r'viewBox="([^"]+)"', head).group(1).split()
        svg = svg.replace("<svg ", '<svg width="%s" height="%s" ' % (vb[2], vb[3]), 1)
    return svg


logos = {n: sized(open(os.path.join(HERE, "logos", n + ".svg")).read()) for n in ("vanta", "grammarly", "anthropic")}
logos["breakout"] = sized(re.sub(r"<\?xml.*?\?>", "", open(os.path.join(BRAND, B["logo"]["file"])).read()).strip())
logos["mark"] = sized(re.sub(r"<\?xml.*?\?>", "", open(os.path.join(BRAND, B["logo"]["mark"])).read()).strip())
src = src.replace("__LOGOS__", json.dumps(logos))
page = src.replace("__LOGO__", logo).replace("__MARKSVG__", mark_svg.replace("<svg ", '<svg aria-hidden="true" ', 1)).replace("__MARK64__", mark64)
full = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n' + page + '\n</html>\n')
open(os.path.join(HERE, "index.html"), "w").write(full)
if "--artifact" in sys.argv:
    open(sys.argv[sys.argv.index("--artifact") + 1], "w").write(page)
print("built index.html")
