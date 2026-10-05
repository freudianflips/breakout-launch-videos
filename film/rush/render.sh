#!/usr/bin/env bash
# Build, render and mix: film/rush/render.sh  ->  film/rush/renders/rush.mp4
set -euo pipefail
cd "$(dirname "$0")"
PY="${PYTHON:-../../.venv/bin/python}"; [ -x "$PY" ] || PY=python3
mkdir -p renders
"$PY" build.py
npx -y hyperframes@0.8.77 render -c index.html --quality looks --output renders/rush-picture.mp4 > renders/render.log 2>&1
"$PY" sound.py
echo "rush ok: film/rush/renders/rush.mp4 ($(ffprobe -v error -show_entries format=duration -of csv=p=0 renders/rush.mp4) s)"
