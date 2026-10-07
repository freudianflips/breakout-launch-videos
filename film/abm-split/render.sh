#!/usr/bin/env bash
# Build, render and mix 1 account's split-screen film:  film/abm-split/render.sh korn-ferry  ->  film/abm-split/out/korn-ferry/renders/breakout-for-korn-ferry.mp4
# All accounts:  for a in film/abm/accounts/*/; do film/abm-split/render.sh "$(basename "$a")"; done
set -euo pipefail
cd "$(dirname "$0")"
SLUG="${1:-korn-ferry}"
PY="${PYTHON:-../../.venv/bin/python}"; [ -x "$PY" ] || PY=python3
"$PY" build.py "$SLUG"
mkdir -p "out/$SLUG/renders"
(cd "out/$SLUG" && npx -y hyperframes@0.8.77 render -c index.html --quality looks --output renders/picture.mp4 > renders/render.log 2>&1)
"$PY" audio.py "$SLUG"
echo "abm-split ok: film/abm-split/out/$SLUG/renders/breakout-for-$SLUG.mp4"
