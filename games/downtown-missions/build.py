#!/usr/bin/env python3
"""Build the game: game.src.html + the brand's logo and mark -> index.html (a full page to open locally)
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
page = src.replace("__LOGO__", logo).replace("__MARKSVG__", mark_svg.replace("<svg ", '<svg aria-hidden="true" ', 1)).replace("__MARK64__", mark64)
full = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n' + page + '\n</html>\n')
open(os.path.join(HERE, "index.html"), "w").write(full)
if "--artifact" in sys.argv:
    open(sys.argv[sys.argv.index("--artifact") + 1], "w").write(page)
print("built index.html")
