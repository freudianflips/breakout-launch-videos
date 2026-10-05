# Press play.

The Breakout **Plays** launch film from [`../STORYBOARD.md`](../STORYBOARD.md): 28 s, 15 bars at 128 BPM, on the Swiss grid (look test 03). Signals are rows of a step sequencer, the agent mutes the noise, ▶ is the drop, the email writes itself on the beat and violet floods into "Meeting booked."

| File | What it does |
|---|---|
| `film.json` | The words, the pattern (rows, steps, starts, the mute), the transport (zoom, stop, press, drop, send, booked, lockup) and the sound cues. One pattern drives the picture and the bed. |
| `template.html` | The look and the motion. Every frame is a pure function of time; a hidden `#err` box shows any script error in a snapshot. |
| `build.py` | film.json + brand.json -> `index.html` and `compositions/press.html` |
| `bed.py` | The free scratch bed, played from the same pattern: every lit step is a hit. |
| `audio.py` | The SFX cue sheet (sound forge), the mix at -14 LUFS and the mux |
| `render.sh` | Build, render and mix: `renders/press-play.mp4` |
