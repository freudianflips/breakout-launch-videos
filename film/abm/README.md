# ABM series: "Do more than chat"

One film per account that runs Qualified on its site: their homepage and chat widget as captured, then where Breakout outperforms Qualified (quoted from getbreakout.ai/compare/qualified-alternative), then the contract buyout. 57.2 s, 16:9, Swiss grid, orchestral score. Story in [`STORYBOARD.md`](STORYBOARD.md), claims and rules in [`BRIEF.md`](BRIEF.md).

## Add an account

1. `mkdir film/abm/accounts/<slug>` and save a homepage capture, about 2000 px wide, with the chat widget open, as `site.webp` (or .png/.jpg).
2. Copy `accounts/korn-ferry/account.json` and change it:
   - `capture`: the widget box, each button `[x, y, height]` and an empty spot below the buttons (`nobox`), in capture pixels.
   - `widget_notes` and `today_line`: what the capture shows. Check them against the capture; they are claims.
   - `question` and `answer`: the answer in the account's own words (from their site).
   - `visitor`, `signals`, `email` and `booked`: fictional and illustrative. Never use a real person.
3. `film/abm/render.sh <slug>` -> `film/abm/out/<slug>/renders/breakout-for-<slug>.mp4`

| File | What it does |
|---|---|
| `series.json` | The fixed beats (bar times), words, the quoted comparison rows, the buyout and the sound cues |
| `accounts/<slug>/` | The account: `account.json` and the capture |
| `template.html` | The look and the motion; every frame is a pure function of time |
| `build.py` | series + account + brand -> `out/<slug>/` (a HyperFrames project) |
| `score.py` | The orchestral score, written as MIDI on the grid and rendered free with fluidsynth and the FluidR3 GM soundfont (`apt install fluidsynth fluid-soundfont-gm`) |
| `audio.py` | The SFX, the score, the -14 LUFS mix and the mux |
| `render.sh` | Build, render and mix 1 account |
