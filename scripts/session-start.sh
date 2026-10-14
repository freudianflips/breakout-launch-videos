#!/usr/bin/env bash
# Install what the ads engine and the renderers need, once per fresh checkout (cloud sessions start clean).
# Quiet and never blocking: a failure here only means `npm install` has to be run by hand.
cd "$(dirname "$0")/.." || exit 0
if [ ! -d node_modules/puppeteer ]; then
  # Cloud containers ship Chromium in /opt/pw-browsers, so skip puppeteer's own download there.
  [ -d /opt/pw-browsers ] && export PUPPETEER_SKIP_DOWNLOAD=1
  npm ci --no-audit --no-fund >/dev/null 2>&1 || npm install --no-audit --no-fund >/dev/null 2>&1 || true
fi
exit 0
