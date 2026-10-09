#!/usr/bin/env bash
# Build, render and mix 1 account's split-screen film:  ./render.sh korn-ferry  ->  ./out/korn-ferry/renders/breakout-for-korn-ferry.mp4
# All accounts:  for a in ../../accounts/*/; do ./render.sh "$(basename "$a")"; done
set -euo pipefail
cd "$(dirname "$0")"
HERE_REL="$(basename "$(dirname "$PWD")")/$(basename "$PWD")"   # templates/<name> or videos/<name>
SLUG="${1:-korn-ferry}"
PY="${PYTHON:-../../.venv/bin/python}"; [ -x "$PY" ] || PY=python3
"$PY" build.py "$SLUG"
mkdir -p "out/$SLUG/renders"
(cd "out/$SLUG" && npx -y hyperframes@0.8.77 render -c index.html --quality looks --output renders/picture.mp4 > renders/render.log 2>&1)
"$PY" audio.py "$SLUG"
echo "abm-split ok: $HERE_REL/out/$SLUG/renders/breakout-for-$SLUG.mp4"
