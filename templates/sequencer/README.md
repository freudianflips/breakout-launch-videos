# Sequencer ("Press play.")

A concept film on the Swiss grid where the story is a step sequencer: signals are rows that play what they light, and the music is generated from the same pattern as the picture.

![Sequencer ("Press play.")](poster.jpg)

| | |
|---|---|
| Use it for | A launch with a strong one-word metaphor, where picture and sound should lock 1:1. Under 30 s. |
| Verdict | Approved: "I love this." Orchestral score preferred over the electronic bed ("more orchestra-y"). |
| New video | `python3 scripts/new-video.py sequencer <name>`, then edit the copy in `videos/<name>/` |

## The example film

The Breakout **Plays** launch film from [`STORYBOARD.md`](STORYBOARD.md): 28 s, 15 bars at 128 BPM, on the Swiss grid (look test 03). Signals are rows of a step sequencer, the agent mutes the noise, ▶ is the drop, the email writes itself on the beat and violet floods into "Meeting booked."

| File | What it does |
|---|---|
| `film.json` | The words, the pattern (rows, steps, starts, the mute), the transport (zoom, stop, press, drop, send, booked, lockup) and the sound cues. One pattern drives the picture and the bed. |
| `template.html` | The look and the motion. Every frame is a pure function of time; a hidden `#err` box shows any script error in a snapshot. |
| `build.py` | film.json + brand.json -> `index.html` and `compositions/press.html` |
| `orchestra.py` | The score: an orchestral arrangement written as MIDI from the same pattern (each signal row is a section of the orchestra and plays only what the grid lights), rendered free with fluidsynth and the FluidR3 General MIDI soundfont (`apt install fluidsynth fluid-soundfont-gm`, or `SF2=`), plus a hall. `film.json` `music.make` points here. |
| `bed.py` | The first scratch bed (electronic), kept for comparison. |
| `audio.py` | The SFX cue sheet (sound forge), the mix at -14 LUFS and the mux |
| `render.sh` | Build, render and mix: `renders/press-play.mp4` |
