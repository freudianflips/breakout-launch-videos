# Kinetic

A minimal, colourful, fast film: one idea per beat, a new colour field flooding in from the last beat's focal point, a small tag, one headline and a code-drawn product moment per beat.

![Kinetic](poster.jpg)

| | |
|---|---|
| Use it for | Overviews of many features or use cases in one film, product tours, social cuts. About 2.3 s per beat. |
| Verdict | Round 15, awaiting a verdict. This video: `videos/use-cases/`. |
| New video | `python3 scripts/new-video.py kinetic <name>`, then edit the copy in `videos/<name>/` |

## The example film

**"Pageview to *pipeline.*"**: the 12 Breakout use cases as one buyer's journey, from a paid click to ABM at scale, then "Meeting *booked.*", the 4 teams it serves and the lockup. 41.3 s at 128 BPM, no narrator. Every line is the headline of its page on getbreakout.ai/use-cases; the visitor and company are fictional. Story in [`STORYBOARD.md`](STORYBOARD.md).

## Make your own

Edit `film.json`:

| Field | What it does |
|---|---|
| `intro.word` | The first word, alone on deep indigo, clicked to start the film |
| `beats[]` | One per idea: `label` (the small tag), `line` (the headline), `visual`, `ground` and `ink` colours |
| `beat_bars` | Length of each beat in bars (1.25 bars = 2.3 s at 128 BPM) |
| `booked`, `personas`, `lockup` | The success state, the chips, the closing line and url |

Visuals available: `paid`, `deanon`, `agent`, `pounce`, `personal`, `routing`, `research`, `committee`, `alerts`, `outbound`, `nurture`, `abm`. A new one is a markup entry in `build.py` (`V`) and a motion function in `template.html` (`VIS`), as a function of `u` from 0 to 1 across the beat.

| File | What it does |
|---|---|
| `build.py` | film.json + brand -> `index.html`, `compositions/kinetic.html`, `timing.json` |
| `template.html` | The look and the motion; every frame is a pure function of time |
| `score.py` | The orchestral score, fitted to the beats (fluidsynth and FluidR3) |
| `audio.py`, `render.sh` | Sound cues from the timeline, the -14 LUFS mix; build, render and mix in one go |
