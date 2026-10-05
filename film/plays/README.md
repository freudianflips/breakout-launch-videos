# film/plays/

The Breakout **Plays** launch film, built from [`../STORYBOARD.md`](../STORYBOARD.md) and [`../BRIEF.md`](../BRIEF.md). It is its own HyperFrames project because it runs on the music's bar grid with no narrator, unlike the voice-led template in `film/`.

| File | What it is |
|---|---|
| `film.json` | The timeline in bars (110 BPM, 20 bars): the hook's lines, the captions, the tickers, the lockup and every sound cue. Change words and timing here. |
| `template.html` | The look and motion: the paper world, the film burn, the liquid world, the product shots with their camera moves, the analog layer. Every frame is a pure function of time. |
| `build.py` | Writes `compositions/plays.html` and `index.html` from the template, `film.json` and `brand/brand.json`; copies the fonts, logo and screens into `assets/`. |
| `psych_bed.py` | A free, seeded psych-indie scratch bed on the grid; the drop lands on bar 8. Replace it with a real take before judging the music. |
| `audio.py` | The analog sound palette (needle, crackle, swarm hum, tally counter, typewriter, stamp, desk bell, film burn, tape), the cue sheet, and the -14 LUFS master laid onto the picture. |
| `render.sh` | All of it: `film/plays/render.sh` writes `renders/plays.mp4`. |

Snapshot any second while you work: `cd film/plays && python3 build.py && npx -y hyperframes@0.8.77 snapshot --at 15.5,24,30`.

The product screens are in `film/assets/screens/plays-*.png` (real UI, no customer data). The Destination shot is framed tightly on the workflow step and the Test button, so the sequencer's name never reads. Headlines use New Kansas when it is installed (Adobe Fonts), Fraunces otherwise.
