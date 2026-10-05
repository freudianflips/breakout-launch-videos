#!/usr/bin/env bash
# Build, render and mix: film/press-play/render.sh  ->  film/press-play/renders/press-play.mp4
set -euo pipefail
cd "$(dirname "$0")"
PY="${PYTHON:-../../.venv/bin/python}"; [ -x "$PY" ] || PY=python3
mkdir -p renders
"$PY" build.py
npx -y hyperframes@0.8.77 render -c index.html --quality looks --output renders/press-picture.mp4 > renders/render.log 2>&1
"$PY" audio.py
echo "press-play ok: film/press-play/renders/press-play.mp4 ($(ffprobe -v error -show_entries format=duration -of csv=p=0 renders/press-play.mp4) s)"
