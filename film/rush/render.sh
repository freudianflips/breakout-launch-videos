#!/usr/bin/env bash
# Build, render and mix: film/rush/render.sh [wide|feed ...]  ->  film/rush/renders/rush-<format>.mp4 (default: both)
set -euo pipefail
cd "$(dirname "$0")"
PY="${PYTHON:-../../.venv/bin/python}"; [ -x "$PY" ] || PY=python3
mkdir -p renders
for FMT in "${@:-wide feed}"; do for F in $FMT; do
  "$PY" build.py "$F"
  npx -y hyperframes@0.8.77 render -c "index-$F.html" --quality looks --output "renders/rush-$F-picture.mp4" > "renders/render-$F.log" 2>&1
  "$PY" sound.py "$F"
  echo "rush ok: film/rush/renders/rush-$F.mp4 ($(ffprobe -v error -show_entries format=duration -of csv=p=0 "renders/rush-$F.mp4") s)"
done; done
