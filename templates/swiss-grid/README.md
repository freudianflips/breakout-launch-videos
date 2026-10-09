# Swiss grid

Minimal Swiss-grid motion graphics: off-white ground, hairline grid, mono indexes, huge Manrope type slams, the agent's cards and the email writing itself, violet for the one thing that matters.

![Swiss grid](poster.jpg)

| | |
|---|---|
| Use it for | A crisp product story in under 30 s with no narrator: one message, real UI recreated as cards, a big success state. |
| Verdict | Approved: look test 03 ("i like 03. This is good."); the film "This is great." |
| New video | `python3 scripts/new-video.py swiss-grid <name>`, then edit the copy in `videos/<name>/` |

## The example film

**"Signal in. Meeting out."**: the Breakout Plays film in the Swiss-grid look (look test 03), from [`STORYBOARD.md`](STORYBOARD.md). 24.4 s, 13 bars at 128 BPM, no narrator.

| File | What it is |
|---|---|
| `film.json` | Every word (signal labels, the agent cards, the email with its `[cfo]`/`[pricing]` phrases, the lockup) and every sound cue, on the bar grid |
| `template.html` | The grid, the type slams, the agent cards (from the owner's references), the typed email and the lines from each signal to the sentence it shaped. Every frame is a pure function of time; a hidden `#err` box shows any script error in a snapshot. |
| `build.py` | Writes `compositions/signal.html` and `index.html`; typed text becomes 1 span per character |
| `bed.py` | A free, seeded, minimal 128 BPM scratch track |
| `audio.py` | The sound-forge cue sheet, the -14 LUFS master and the mux |
| `render.sh` | All of it, to `renders/signal.mp4` |

Notion is the owner's chosen example account, shown in plain type (never its logo) with an "Illustrative example" label, because the signals, the contact and the email are invented.
