#!/usr/bin/env bash
# Build, render and mix the Plays film: ./render.sh   ->  film/plays/renders/plays.mp4
set -euo pipefail
cd "$(dirname "$0")"
PY="${PYTHON:-../../.venv/bin/python}"; [ -x "$PY" ] || PY=python3
mkdir -p renders
"$PY" build.py
npx -y hyperframes@0.8.77 render -c index.html --quality looks --output renders/plays-picture.mp4 > renders/render.log 2>&1
[ -f score/bed.wav ] || "$PY" psych_bed.py film.json --out score/bed.wav
"$PY" audio.py
echo "plays ok: film/plays/renders/plays.mp4 ($(ffprobe -v error -show_entries format=duration -of csv=p=0 renders/plays.mp4) s)"
