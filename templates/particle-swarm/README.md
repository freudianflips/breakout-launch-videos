# Particle swarm

A music-video motion test: thousands of particles snap into each word on the beat, burst into the next, and settle into the wordmark.

![Particle swarm](poster.jpg)

| | |
|---|---|
| Use it for | Teasers, openers and closers; 6 to 10 s social cuts; a logo reveal. |
| Verdict | "ok this is cool": liked as a style, not yet used in a full film. |
| New video | `python3 scripts/new-video.py particle-swarm <name>`, then edit the copy in `videos/<name>/` |

## The example film

Its example is a 4-bar motion test at 128 BPM: "Signal", "in.", "Meeting", "out." and the wordmark, with "Plays" and the url.

| File | What it does |
|---|---|
| `film.json` | Tempo, bars, the music file and the sound cues |
| `template.html` | The swarm: the words (`STAGES`), particle count, colours and the burst, sampled from real letterforms and the wordmark; every frame is a pure function of time |
| `build.py`, `bed.py`, `audio.py`, `render.sh` | Build, a free scratch bed, the mix, and all three plus the render |
