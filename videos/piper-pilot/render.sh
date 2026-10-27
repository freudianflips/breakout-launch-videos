#!/usr/bin/env bash
# Build, render and mix the two-hander:  ./render.sh  ->  ./renders/two-hander.mp4
set -euo pipefail
cd "$(dirname "$0")"
PY="${PYTHON:-../../.venv/bin/python}"; [ -x "$PY" ] || PY=python3
"$PY" build.py
mkdir -p renders
npx -y hyperframes@0.8.77 render -c index.html --quality looks --output renders/picture.mp4 > renders/render.log 2>&1
"$PY" audio.py
echo "two-hander ok: $(basename "$(dirname "$PWD")")/$(basename "$PWD")/renders/two-hander.mp4"
