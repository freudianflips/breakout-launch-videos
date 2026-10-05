# Breakout Launch Videos

**Apple-style launch films for Breakout, made by a coding agent.**

This repo turns Breakout's brand and its own words into 30 to 60 second launch films. Each one has a hook, the Breakout logo on the music's drop, hero words cut on the voice, the product at close range and the logo in near silence. Claude Code (or Codex) writes the story from Breakout's copy, times every cue to the narrator's words, and renders the film locally with HyperFrames.

The first version of every film is free and needs no accounts: a placeholder narrator, a synthesised music bed and a synthesised sound palette. Swap in a real voice, music and footage once the story works.

## What is here

| Included | What it does |
|---|---|
| [Breakout brand kit](brand/README.md) | `brand/brand.json`: the logo from the team Drive, the indigo palette, Inter, and the copy from the Brand Guide for Writers. `brand/preview.png` shows it at a glance |
| [The film template](film/README.md) | 2 hooks on a shared body. The story lives in `film/film.json`, and every picture cue lands on the narrator's words |
| [10 agent skills](skills/README.md) | Story, voice, music, sound, mix, review, motion and 3D. Each is a short manual your agent follows |
| [Style log](docs/breakout-style.md) | The look decisions for Breakout so far, the open questions, and a verdict log for each round |
| A free audio path | Scratch voice, forced alignment, a scratch music bed on the bar grid, a synthesised sound palette and a -14 LUFS master |
| Paid upgrades, on your account | Narrator voices, music, sound kits and generated footage through Higgsfield, with the cost stated before every job ([costs](docs/costs.md)) |
| A review loop | A script that measures a render (cuts, static runs, loudness, beat grid) and writes a filmstrip and contact sheet, plus the eye checklist |

## Start here

1. Install the tools ([setup](docs/setup.md), about 10 minutes on a Mac):

   ```bash
   brew install node ffmpeg uv whisper-cpp
   npm install
   uv venv .venv && uv pip install -r requirements.txt
   ```

2. Real Breakout screens live in `film/assets/screens/`, with customer data blurred. Add more (a live conversation recording would be the strongest shot) and point the `src` paths in `film/film.json` at them.

3. Open the folder in Claude Code and paste:

   ```text
   Read CLAUDE.md and README.md. Make a Breakout launch video.
   Show me brand/preview.png first. Then use launch-film: show me the
   beats and a contact sheet before rendering, and render the free
   version first.
   ```

## Or run it by hand

```bash
.venv/bin/python skills/launch-voice/scripts/scratch_voice.py film/film.json
.venv/bin/python skills/launch-voice/scripts/prep_lines.py film/film.json --align force   # precise word times; uv fetches torch once
.venv/bin/python skills/launch-score/scripts/scratch_bed.py film/score/bed.wav --bpm 120 --intro-bars 3
film/render.sh attention          # or: film/render.sh  (every hook)
```

The film lands in `film/renders/attention.mp4`.

## The current film

| Part | Now |
|---|---|
| Hook `attention` | Dark ground, type only: "Buyers give you their *attention.* / You give them a *form.*" |
| Hook `who-visited` | Light ground, 1 question: "Who visited your site *today?*" |
| Name | The Breakout logo punches in on the drop: "is your *inbound SDR*, powered by AI." |
| Identify | "Every *visitor.*" on deep indigo, then Accounts (relevance, location, source) and the account's Browsing Summary |
| Engage | "In *real time.*" on indigo, then All Chats with a click on Live Chats and "Meeting booked" |
| Convert | Contacts: email and LinkedIn, "Followed up" |
| Blocks | Identify, Engage, Convert close into "One *AI SDR.*" |
| Switch | "Inbound SDR, *always on.*" |
| End | The logo lockup, "Inbound SDR, powered by AI.", getbreakout.ai, then quiet |

Every line comes from the Brand Guide for Writers or the partner enablement guide. Change it in `film/film.json`.

## How a film is built

```text
brand/brand.json ──────────────┐
                               ├──> film/build.py ──> HyperFrames render ──> film/audio.py ──> master.mp4
film/film.json (lines, beats) ─┤        (every cue is a spoken word's time)     (music on the cut, voice,
voice takes ──> word times ────┘                                                 sound, -14 LUFS)
```

The **hook** is anything before the cut: 2 lines of type (free), your own footage, or generated footage. On the music's drop it cuts to the **body**, which is built from 6 beat types:

| Beat | On screen |
|---|---|
| `name` | The logo punches in from 4x on the drop; the tagline writes in word by word |
| `hero` | Full-frame words on a dark, accent or light ground, each snapping in on its spoken word, leaving by a dive, a collapse or a cut |
| `product` | A real screen in a window; the camera pushes into the part the voice names, with an optional cursor click and a chip |
| `blocks` | Features land on their names, then close into 1 |
| `switch` | A card that turns on: "Inbound SDR, always on." |
| `end` | The lockup, then a quiet hold |

Every hook shares the body, so testing 5 hooks means writing 5 small JSON files, and a change to the body reaches every film.

## Rules learned the hard way

- Type that lands 0.1 to 0.3 s after its word reads as off beat. Time it by forced alignment, never by guesswork.
- 1 narrator for the whole film. A second voice for a new line breaks it, even when it is clearer.
- Show frames before building. A full render on the wrong look wastes a day.
- The whole app window at thumbnail size says nothing. Push into the one part the voice names.
- No text card where the animation already says it, and no monotone stretch longer than a few seconds.
- When photoreal people look fake, go stylised instead of cheaper.

More in [lessons](skills/launch-film/references/lessons.md).

## What is in the repo

```text
skills/     10 skills: launch-film (start here), launch-brand, story, voice, score, sound, mix, review, world, motion
tools/      brand-from-url.mjs, the website to brand kit extractor
brand/      the Breakout brand kit (brand/source/ holds the original logo file)
film/       the template: film.json, hooks/, assets/screens/, templates/body.html, build.py, audio.py, render.sh
examples/   a small fictional site (Acme) to test the extractor offline
docs/       setup, costs, rights, the Breakout style log
```

Adapted from the MIT-licensed launch-video-kit ([license](LICENSE), [third-party notices](THIRD_PARTY_NOTICES.md)).
