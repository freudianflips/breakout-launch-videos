# Plays launch: "Signal in. Pipeline out."

The Plays launch film, made from the [`swiss-grid`](../../templates/swiss-grid/README.md) template (its example, approved: "This is great."), iterated on 2026-11-19.

![Plays launch](poster.jpg)

**Before sharing:** the soundtrack is a commercial track the owner supplied (Sébastien Léger, "After That (Original Mix)"). Internal review only until it is licensed for this use ([`docs/rights.md`](../../docs/rights.md)). The mp3 lives in `music/`, which git ignores; put it back there to rebuild.

## Changes from the template's example

Owners notes, round 1: "1\ Remove the Breakout plays small text entirely 2\ Reword to "Signal in. Pipeline out." 3\ Zoom in, slow a little on the changes we detect (New CFO hired, Pricing page viewed etc) 4\ Add this song to the soundtrack instead. Keep the sfx"

| | |
|---|---|
| Small text | Gone: the "Breakout · Plays" tag, the index breadcrumbs ("01 / Signal"...), the timecode, "Illustrative example" and the labels under the email |
| Just the cards | The words beside the cards ("Reads.", "Thinks.", "Sends.", "Books.") are gone; the cards sit centred (the camera frames them at the centre; during the email, cards and email are centred as a pair) |
| Lockup | "Signal in. *Pipeline out.*" |
| The detected changes | Bars 3 to 4 (the account card's rows: 2 blog views / No action, New CFO hired / Act, Pricing page viewed 3× / Act) play at half speed (`warp` in `film.json`) under a closer camera (1.68x to 1.74x); one extra bar, so later cuts stay on the song's downbeats |
| Music | The owner's track at its own 126 BPM (the film moved from 128 to 126), from its very first beat (0.249 s) on bar 0; faded out under the lockup. Cuts land on its beats |
| Sound effects | Kept, retimed through the slowed bar |

26.7 s. `./render.sh` -> `renders/signal.mp4`.

Round 2 (owner): "remove the "reads", "thinks" etc text from the right and center align the cards so its just the cards with no text. Remove stuff like illustrative example, breadcrumbs. Start the soundtarck fromt he beginnng of the soundtrack"
