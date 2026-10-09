# Treatment: the analog film

A conceptual, analog, vintage launch film. A true, uncommon fact about how buying changed frames it. Then it cuts into Breakout, and the type and motion play like an indie psych music video: liquid colour, echoed type, film grain, a little wobble. There is no narrator. A music track carries it, with sound effects on every cut and click.

Style frames: [contact.jpg](style-frames/contact.jpg) (frames 1 to 8 in `style-frames/`, source `frames.html`, re-shoot with `node docs/style-frames/shoot.mjs`).

## The concept (pick 1)

| | Concept | The fact | The turn into Breakout |
|---|---|---|---|
| **A (recommended)** | **The clerk** | Until 1916, a grocery clerk took your order, knew your name and fetched the goods. On September 6, 1916, a store in Memphis opened with open shelves and baskets: the first self-service grocery. | A century later, the web is the biggest self-service store ever built. Nobody greets you; you fill in a form. Breakout brings the clerk back: it "greets every visitor like it already knows them". |
| B | **The operator** | Kansas City, 1889. The story goes that a switchboard operator, married to a rival undertaker, routed Almon Strowger's calls to her husband. So he invented the automatic exchange (US patent 447,918, 1891). The story itself is disputed, so the film says "the story goes". | Your inbound still runs through an operator: a form, a queue, a round-robin. Breakout routes every visitor to the right rep, live. |
| C | **Hits** | In the early web, a "hit" was every file a server sent: 1 page with 9 images counted as 10 hits. Analysts joked that HITS stood for "How Idiots Track Success". | We counted files, then pageviews, never people. Breakout "turns every pageview into a person". |

A is the strongest story of how the world changed: personal, then anonymous, then personal again at scale. It is fully verifiable, and it hands the film its best line from Breakout's own copy. Sources are at the bottom; no brand is named on screen.

## Beat sheet for A (about 40 s at 108 BPM, 1 bar = 2.22 s)

| Bars | Time | Picture | Words on screen | Sound |
|---|---|---|---|---|
| 1-2 | 0-4.4 | 1916 paper: cream, halftone, sepia; a slow push | "Until 1916, a clerk fetched *everything.*" | Needle drop, crackle, a soft tape-hiss bed |
| 3-4 | 4.4-8.9 | The same paper; the italic wobbles on | "Then a store in Memphis said *help yourself.*" | A shop bell, a cash register drawer |
| 5-6 | 8.9-13.3 | A paper web form fades up: Name, Work email, Company size | "A century later, the web is the biggest *self-service store* ever built." / "Nobody greets you. You fill in a *form.*" | Typewriter keys on each field, a flat submit thunk |
| drop, 7-8 | 13.3-17.8 | Film burn: the paper melts into the violet liquid | "The clerk *is back.*" plus the wordmark | The track's kick and bass enter on the cut |
| 9-10 | 17.8-22.2 | The website agent's welcome, echoed in 3 hues, then the asked question | "Greets every visitor *like it already knows them.*" | A tape swell, a soft chime as the question lands |
| 11-12 | 22.2-26.7 | Accounts and the Browsing Summary through a mirror pass; the cursor clicks Book a Meeting | The site's Inbound Agent lines, one per beat: "Know who's on your site." "Answer real product questions." "Book before the tab closes." | A click and a ring on Book a Meeting, glass ticks on each line |
| 13-14 | 26.7-31.1 | Echo type, hue cycling on the liquid | "Pageview to *pipeline.*" | A filter sweep, the track at its fullest |
| 15-16 | 31.1-40 | The lockup on the liquid; grain and gate stay | The wordmark and getbreakout.ai | Tape stop into silence, then crackle |

Every line on screen is the brand's own copy or the verified fact. The Inbound Agent lines and "Pageview to pipeline." are from the homepage; "Greets every visitor like it already knows them" is from the website graphics spec.

## Style rules

- **Two worlds.** The hook is analog paper: cream `#f1e6cf`, ink `#2a1d14`, halftone, sepia, a warm light leak. Breakout is a liquid psychedelic ground: the homepage's violet mesh pushed toward magenta `#ff4fd8` and amber `#ff9a3c` (the pinks and blues of the agent widget's header), slowly warping.
- **Type.** New Kansas (Fraunces stand-in, with its "wonky" italic on) for every line. Key words go italic. On the liquid, type gets 2 echo copies offset in time and hue (amber, magenta), a slight red and cyan split, and a soft halo. Small labels are in letter-spaced Manrope caps.
- **The analog layer, always on.** Grain, a vignette, a rounded film gate, gate weave (a few pixels of drift), occasional light leaks and a slow breathing exposure, all as pure functions of time.
- **Motion.** Slow and hypnotic between hits, hard on the bar. Liquid warps and hue cycles, type that wobbles on (a displacement filter easing out), echo trails, mirror and kaleidoscope passes on product screens, a film burn for the cut. No bounce, no stock transitions.
- **Product.** The real screens, untouched inside their frames. The effects live around them (echo copies, colour and light) so the UI stays legible.
- **Sound.** 1 track and 1 palette of analog sounds (needle, crackle, tape, typewriter, shop bell, register, chime). No narrator.

## What changes in the kit

1. **No narration.** A new `"timing": "bars"` mode in `film.json`: every cue sits on the music's bar and beat grid instead of on spoken words, and `audio.py` skips the voice bus.
2. **The analog layer and the liquid ground** go into `templates/body.html` as brand-driven options (`look: "analog"`), so the current clean film still builds.
3. **New beat types:** `paper` (the hook pages), `echo` (hero words with trails), `burn` (the film-burn cut) and `lines` (a run of short captions on the grid).
4. **Sound:** a free psych scratch bed (phased chords, tape wobble, a dry kick) for timing, plus an analog palette in the sound forge.

## Music

| Route | Cost | Notes |
|---|---|---|
| Free scratch bed | free | For timing and review only; it sounds like a sketch |
| Higgsfield Sonilo, 2 or 3 takes of 40 s, prompted "warm psychedelic indie, phased synths, round bass, dry drums, 108 BPM, tape saturation" | about 2 to 3 credits a take, roughly $0.10 to $0.15 each (2026-09 prices, `docs/costs.md`) | Runs only on your account, after you say yes |
| A licensed track you choose | the licence | The film fits itself to its bar grid and drop |

## Sources

- The first self-service grocery, Memphis, September 6, 1916: [Clarence Saunders](https://en.wikipedia.org/wiki/Clarence_Saunders), [Tennessee history](https://www.tnhistoryforkids.org/?p=629), [Salem Press, Great Events from History](https://online.salempress.com/10.3331/GE20a_2611005322).
- Strowger, US patent 447,918 (1891), and the disputed operator story: [99% Invisible](https://99percentinvisible.org/episode/strowger-switch-purple-reign-redux/transcript/), [Telecommunications History Group](https://www.telcomhistory.org/newsletters/winter2019.pdf).
- Hits, and "How Idiots Track Success" (Katie Delahaye Paine): [ClickZ](https://www.clickz.com/clickz/column/2104348/idiots-track-success), [Google Analytics blog](https://analytics.googleblog.com/2010/04/back-to-hits.html).
