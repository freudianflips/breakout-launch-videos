#!/usr/bin/env bash
# Build, render and mix the swarm motion test: ./render.sh  ->  renders/swarm.mp4
set -euo pipefail
cd "$(dirname "$0")"
HERE_REL="$(basename "$(dirname "$PWD")")/$(basename "$PWD")"   # templates/<name> or videos/<name>
PY="${PYTHON:-../../.venv/bin/python}"; [ -x "$PY" ] || PY=python3
mkdir -p renders
"$PY" build.py
npx -y hyperframes@0.8.77 render -c index.html --quality looks --output renders/swarm-picture.mp4 > renders/render.log 2>&1
"$PY" audio.py
echo "swarm ok: $HERE_REL/renders/swarm.mp4 ($(ffprobe -v error -show_entries format=duration -of csv=p=0 renders/swarm.mp4) s)"
