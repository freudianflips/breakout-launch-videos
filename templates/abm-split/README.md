# ABM, split screen

A per-account ABM film as one split screen in sync: the same visitor on the account's site today (their real chat, as captured) and with Breakout, low on text.

![ABM, split screen](poster.jpg)

| | |
|---|---|
| Use it for | 1:1 ABM sends where showing the user experience beats telling. Needs captures of each step of the account's chat. |
| Verdict | Round 14, awaiting a verdict. |
| New video | `python3 scripts/new-video.py abm-split <name>`, then edit the copy in `videos/<name>/` |

## The example film

A split-screen version of the ABM series. One visitor does the same thing on both sides, in sync. **Left:** the account's site and chat exactly as captured, clicking through their real decision tree. **Right:** the same site with Breakout's widget (illustrative), answering the open question, then finding the person, writing and sending the email, and booking the meeting. It's low on text: two pane labels, the visitor's question, two quoted fragments, the buyout and the close. 35.6 s, 16:9. Storyline in [`STORYBOARD.md`](STORYBOARD.md).

It uses the same accounts as the first ABM template (`accounts/<slug>/`) and needs their `tree` block. That block lists each capture of the chat, its buttons as `[x, y, height]` in capture pixels, which button the visitor clicks, and an empty spot below the last step's buttons (`nobox`).

`templates/abm-split/render.sh <slug>` -> `templates/abm-split/out/<slug>/renders/breakout-for-<slug>.mp4`

| File | What it does |
|---|---|
| `split.json` | The beats (bar times), the few words, the quoted fragments and the sound cues |
| `template.html` | The two panes and their cameras, the left visitor's path through the tree, the right pane's story; every frame is a pure function of time |
| `build.py` | split.json + account + brand -> `out/<slug>/` |
| `score.py` | The orchestral score (MIDI on the grid, rendered free with fluidsynth and FluidR3) |
| `audio.py`, `render.sh` | The SFX, the mix at -14 LUFS, the mux; build, render and mix 1 account |
