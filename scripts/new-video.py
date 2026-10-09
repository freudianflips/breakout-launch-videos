#!/usr/bin/env python3
"""Start a new video from a template: copy templates/<template>/ to videos/<name>/, without anything a build makes.

  python3 scripts/new-video.py                      # list the templates
  python3 scripts/new-video.py swiss-grid q4-launch # -> videos/q4-launch/

The copy is yours to change (words, beats, timing, look); the template stays as it is, so the next video
starts clean. Videos sit at the same depth as templates, so every relative path (../../brand, ../../assets,
../../accounts, ../../skills) keeps working.
"""
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES = os.path.join(ROOT, "templates")
GENERATED = {"assets", "compositions", "renders", "snapshots", "review", "mix", "sfx", "score", "vo", "out", "__pycache__"}


def summary(name):
    """The first sentence under a template README's title."""
    try:
        text = open(os.path.join(TEMPLATES, name, "README.md")).read()
    except OSError:
        return ""
    for line in text.splitlines()[1:]:
        line = line.strip()
        if line and not line.startswith(("#", "|", "!", "<")):
            return re.sub(r"[*`]", "", line).split(". ")[0].rstrip(".") + "."
    return ""


names = sorted(d for d in os.listdir(TEMPLATES) if os.path.isdir(os.path.join(TEMPLATES, d)))
if len(sys.argv) < 3:
    print("usage: python3 scripts/new-video.py <template> <video-name>\n\ntemplates:")
    for n in names:
        print(f"  {n:16} {summary(n)}")
    sys.exit(0 if len(sys.argv) == 1 else 1)

template, video = sys.argv[1], sys.argv[2]
if template not in names:
    sys.exit(f"no template {template!r}; pick one of: {', '.join(names)}")
if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", video):
    sys.exit("name the video in lowercase with dashes, e.g. q4-launch")
dst = os.path.join(ROOT, "videos", video)
if os.path.exists(dst):
    sys.exit(f"videos/{video} already exists")


def ignore(folder, entries):
    out = set()
    for e in entries:
        if e in GENERATED or e.endswith(".log"):
            out.add(e)
        elif re.fullmatch(r"index(-.*)?\.html|timing.*\.json", e):
            out.add(e)
    return out


shutil.copytree(os.path.join(TEMPLATES, template), dst, ignore=ignore)
with open(os.path.join(dst, "TEMPLATE"), "w") as f:
    f.write(f"{template}\n")
print(f"videos/{video}/ from templates/{template}/\n")
print("Next, in this order (CLAUDE.md):")
print(f"  1. Write videos/{video}/BRIEF.md and STORYBOARD.md with the owner (skill launch-story); get the storyboard approved.")
print(f"  2. Change the words and beats in the data file (see videos/{video}/README.md), build, and show stills of every beat.")
print(f"  3. Render the free version: videos/{video}/render.sh")
