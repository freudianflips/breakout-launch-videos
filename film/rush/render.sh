#!/usr/bin/env bash
# Build, render and mix: [STORY=headcount] film/rush/render.sh [wide|feed ...]
#   ->  film/rush/renders/rush-[<story>-]<format>.mp4 (default: both formats of film.json)
set -euo pipefail
cd "$(dirname "$0")"
PY="${PYTHON:-../../.venv/bin/python}"; [ -x "$PY" ] || PY=python3
STORY="${STORY:-}"; TAG="${STORY:+$STORY-}"
mkdir -p renders
for F in ${@:-wide feed}; do
  "$PY" build.py "$F" $STORY
  npx -y hyperframes@0.8.77 render -c "index-$TAG$F.html" --quality looks --output "renders/rush-$TAG$F-picture.mp4" > "renders/render-$TAG$F.log" 2>&1
  "$PY" sound.py "$F" $STORY
  echo "rush ok: film/rush/renders/rush-$TAG$F.mp4 ($(ffprobe -v error -show_entries format=duration -of csv=p=0 "renders/rush-$TAG$F.mp4") s)"
done
