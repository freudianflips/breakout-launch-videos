#!/usr/bin/env bash
# Build, render and mix: ./render.sh  ->  ./renders/<folder name>.mp4
set -euo pipefail
cd "$(dirname "$0")"
HERE_REL="$(basename "$(dirname "$PWD")")/$(basename "$PWD")"   # templates/<name> or videos/<name>
NAME="$(basename "$PWD")"
PY="${PYTHON:-../../.venv/bin/python}"; [ -x "$PY" ] || PY=python3
mkdir -p renders
"$PY" build.py
npx -y hyperframes@0.8.77 render -c index.html --quality looks --output renders/picture.mp4 > renders/render.log 2>&1
"$PY" audio.py
echo "kinetic ok: $HERE_REL/renders/$NAME.mp4 ($(ffprobe -v error -show_entries format=duration -of csv=p=0 "renders/$NAME.mp4") s)"
