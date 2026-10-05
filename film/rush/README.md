# film/rush/

**Rush**: a fast-cut, high-contrast social film, separate from the brand-look films, in 2 formats from 1 storyline: `wide` (1920x1080) and `feed` (the LinkedIn feed's 1080x1350). 18.9 s, 44 beats at 140 BPM, 30 shots, no narrator.

The hook (0 to 3.4 s): "Someone / is on your / pricing page. / Right now." with a LIVE tag, "Who?" over the real Accounts table, "They won't / fill a form.", then the logo slams in on the drop.

Its own palette (black, white, acid yellow, hot pink, electric blue), Anton slams, the white Breakout logo throughout, and real product screens from `film/assets/screens/` (customer data blurred).

| File | What it is |
|---|---|
| `film.json` | Every shot on the beat grid: ground, words, screen crops, chips, the logo hits and flicks. An item's `wide` or `feed` block overrides its layout in that format; `"hide": true` drops it there |
| `template.html` | The look and the motion. Every frame is a pure function of t |
| `build.py` | `build.py wide` or `build.py feed` writes `index-<format>.html` (and `index.html` for snapshots) and copies fonts, logos, screens and GSAP into `assets/` |
| `sound.py` | `sound.py <format>`: a free, seeded 140 BPM track and a snappy SFX stem from the shots, then the -14 LUFS master and the mux |
| `render.sh` | All of it, to `renders/rush-wide.mp4` and `renders/rush-feed.mp4` (`render.sh wide` for 1) |

Words are Breakout's own lines ("Inbound SDR, powered by AI.", "Every visitor.", "700+ signals", "In real time.", "Signal in. Meeting out.", "Pageview to pipeline."), except the hook's scene-setting lines, which state no number, customer or result. Ground flips stay at or under 1 per beat (2.3 a second), under the 3-flash limit.
