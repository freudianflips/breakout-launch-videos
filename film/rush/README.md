# film/rush/

**Rush**: a fast-cut, high-contrast social film for the LinkedIn feed (1080x1350), separate from the brand-look films. 17.1 s, 40 beats at 140 BPM, 27 shots, no narrator. Its own palette (black, white, acid yellow, hot pink, electric blue), Anton slams, the white Breakout logo throughout, and real product screens from `film/assets/screens/` (customer data blurred).

| File | What it is |
|---|---|
| `film.json` | Every shot on the beat grid: ground, words, screen crops, chips, the logo hits and flicks |
| `template.html` | The look and the motion. Every frame is a pure function of t |
| `build.py` | Writes `index.html` and copies fonts, logos, screens and GSAP into `assets/` |
| `sound.py` | A free, seeded 140 BPM track and a snappy SFX stem from the shots, then the -14 LUFS master and the mux |
| `render.sh` | All of it, to `renders/rush.mp4` |

Words are Breakout's own lines ("Who visited your site today?", "Inbound SDR, powered by AI.", "Every visitor.", "700+ signals", "In real time.", "Signal in. Meeting out.", "Pageview to pipeline."). Ground flips stay at or under 1 per beat (2.3 a second), under the 3-flash limit.
