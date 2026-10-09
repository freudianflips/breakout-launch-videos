# Dot matrix

A wordless story told by one grid of dots: the visitor, Breakout and the rep are blooms of dots that snap on the beat, trade ripples and merge; the words at the end are dots too.

![Dot matrix](poster.jpg)

| | |
|---|---|
| Use it for | Brand films and product stories told abstractly, with no UI or people on screen; social cuts. Small captions only. |
| Verdict | Round 19 (v2), awaiting a verdict. Round 18: "This storyline doesn't show how Breakout chases a buyer even during the slow period" and "this jazz track is too downbeat". The look was chosen from the abstract reel (owner: "Use the dot matrix style"); the notes for this film: "Use very cool snappy motion. A jazzy atmospheric soundtrack. Add an Easter egg joke. Keep the captions small and precise". |
| New video | `python3 scripts/new-video.py dot-matrix <name>`, then edit the copy in `videos/<name>/` |

## The example film

**"Full suite, in dots"**: an anonymous visitor (grey) is seen (pink), gets a first conversation with Breakout (violet), the rep (cyan) is called in; the visitor leaves but stays on screen, small and dim; Breakout follows up, then plays the long game as Snake (the easter egg): it pings as it listens, eats each signal near her account (a score in the corner) and slithers over to tap her, and she warms up each time; the visitor comes back, they merge, "Meeting *booked.*", the wordmark and "Pageview to *pipeline.*". 40.3 s at 128 BPM, with a free, upbeat swing score. Captions are the use-case page headlines, verbatim. Story in [`STORYBOARD.md`](STORYBOARD.md).

## Make your own

Edit `film.json`:

| Field | What it does |
|---|---|
| `at` | When each beat starts, in bars (dark, seen, engage, rep, gone, follow, game, back, booked, close, end) |
| `captions[]` | Small captions: `text`, `at` and `until` in bars; they cut in and out on those bars |
| `colors` | Ground, idle dot, visitor, anonymous visitor, Breakout, rep, signal and snake colours |
| `game` | The long game: the corner label, where she waits and the signal cells (on the 80 x 45 dot grid), the snake's step in bars and how far the grid dims |
| `booked.lines`, `lockup.line` | The words spelled in dots (`*key*` lines in the visitor colour) and the closing line |

The motion lives in `template.html` (`frame(t)` redraws the grid from nothing, so every frame is a pure function of time). The score is `score.py` (an upbeat General MIDI swing band, cued from `at` and the snake's route); the sound cues are in `audio.py`.

| File | What it does |
|---|---|
| `build.py` | `film.json` + `brand.json` -> `index.html`, `compositions/dots.html` (the logo's paths are embedded and sampled onto the grid) |
| `score.py` | The jazz score -> `score/score.wav` |
| `audio.py` | Sound cues, the mix at -14 LUFS and the mux |
| `render.sh` | All of it -> `renders/<folder>.mp4` |
