# film/signal/

**"Signal in. Meeting out."**: the Breakout Plays film in the Swiss-grid look (look test 03), from [`../STORYLINE-signal.md`](../STORYLINE-signal.md). 22.5 s, 12 bars at 128 BPM, no narrator.

| File | What it is |
|---|---|
| `film.json` | Every word (signal labels, the agent cards, the email with its `[cfo]`/`[pricing]` phrases, the lockup) and every sound cue, on the bar grid |
| `template.html` | The grid, the type slams, the agent cards (from the owner's references), the typed email and the lines from each signal to the sentence it shaped. Every frame is a pure function of time; a hidden `#err` box shows any script error in a snapshot. |
| `build.py` | Writes `compositions/signal.html` and `index.html`; typed text becomes 1 span per character |
| `bed.py` | A free, seeded, minimal 128 BPM scratch track |
| `audio.py` | The sound-forge cue sheet, the -14 LUFS master and the mux |
| `render.sh` | All of it, to `renders/signal.mp4` |

Notion is the owner's chosen example account, shown in plain type (never its logo) with an "Illustrative example" label, because the signals, the contact and the email are invented.
