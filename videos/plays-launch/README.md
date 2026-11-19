# Plays launch: "Signal in. Pipeline out."

The Plays launch film, made from the [`swiss-grid`](../../templates/swiss-grid/README.md) template (its example, approved: "This is great."), iterated on 2026-11-19.

![Plays launch](poster.jpg)

**Before sharing:** the soundtrack is a commercial track the owner supplied (Sébastien Léger, "After That (Original Mix)"). Internal review only until it is licensed for this use ([`docs/rights.md`](../../docs/rights.md)). The mp3 lives in `music/`, which git ignores; put it back there to rebuild.

## Changes from the template's example

Owner: "1\ Remove the Breakout plays small text entirely 2\ Reword to "Signal in. Pipeline out." 3\ Zoom in, slow a little on the changes we detect (New CFO hired, Pricing page viewed etc) 4\ Add this song to the soundtrack instead. Keep the sfx"

| | |
|---|---|
| Small text | The "Breakout · Plays" tag (top right) and the small "Plays" index at the end are gone |
| Lockup | "Signal in. *Pipeline out.*" |
| The detected changes | Bars 3 to 4 (the account card's rows: 2 blog views / No action, New CFO hired / Act, Pricing page viewed 3× / Act) play at half speed (`warp` in `film.json`) under a closer camera (1.68x to 1.74x); one extra bar, so later cuts stay on the song's downbeats |
| Music | The owner's track at its own 126 BPM (the film moved from 128 to 126), from 3:29.8 so its drop (3:33.6) lands on bar 2, where the play starts; faded out under the lockup. Every cut lands within 60 ms of its beat |
| Sound effects | Kept, retimed through the slowed bar |

26.7 s. `./render.sh` -> `renders/signal.mp4`.
