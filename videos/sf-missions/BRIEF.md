---
workflow: product-story
message: "Every signal is a mission. Breakout tells you which one to run."
destination: to confirm (LinkedIn, getbreakout.ai?)
aspect: 1920x1080
language: en
length: about 45 s (2 missions); or 2 cuts of about 25 s, one per mission (to confirm)
angle: A 2004-era open-world crime game set in downtown San Francisco. Breakout is the radar; each buying signal is a mission marker; the hero runs the right move for it
style: new template (working name `open-world`), to build once this storyboard is approved
status: DRAFT, not yet approved by the owner. brand/brand.json says "reviewed": false, so every frame is a draft
---

## Intent

The owner's ask (2026-10-21): "make a new GTA: San Andreas mission where CJ has to do a series of activities around downtown SF. It has to look and feel like GTA San Andreas."

| Mission | The move | Signal it teaches |
|---|---|---|
| Pizza for the Buying Committee | Speed: act before the signal cools | 3+ visitors from one office |
| Tail the Champion | Patience: follow them from their old office to their new office | To confirm: the champion changes jobs? |

Each mission teaches one signal and the move that wins it. Breakout is what spots the signal and puts the marker on the map.

## The look: the genre, not the game

The rights rules (`docs/rights.md`, `CLAUDE.md`) let us use a game's era and genre, never the game itself, its characters or its brand. So this film looks and feels like a PS2-era open-world game without being that game:

| Use (genre) | Never use (the game itself) |
|---|---|
| Low-poly city, chunky textures, short draw distance with a hazy smog-orange and teal grade, slight PS2 dither and jaggies | CJ, or any character, likeness, outfit or voice from the game |
| A circular radar bottom left with blips; a money counter, clock and health bars top right (our own design) | The game's name, logo, title card, box art or loading screens |
| Mission title in a heavy, black-outlined display face; yellow objective text bottom centre; letterboxed cutscenes | The "Mission passed! Respect +" sting and its sound, the theme, any radio track |
| A big end state across the screen, our own words ("MISSION PASSED" is generic; to confirm) | Grove Street, San Fierro, or any place, gang or brand made for the game |
| A 90s West Coast feel in the music: G-funk synth lead, Rhodes, talkbox-style line, 808, our own composition | Rockstar's or the game's typefaces, if licence-restricted (see Notes) |

**The hero:** a fictional character of our own (not CJ, no lookalike), seen third person from behind like the genre. Name and look to agree with the owner. Working name: "the rep".

**Downtown SF:** real places are fine as generic geography (Market Street, the hills, cable cars, the Financial District skyline), built in low poly. No real company's building signage or logo.

**Breakout in the world:** the radar is Breakout. Signals arrive as blips and turn violet `#4c00ff` (lilac `#be79ff` on dark) when Breakout picks them up. The radar carries the b-disc mark (`brand/mark-on-dark.svg`) in its centre. The close is the real wordmark lockup.

## Words

- Mission titles verbatim from the owner: "Pizza for the Buying Committee", "Tail the Champion".
- Objective lines (yellow, genre style), short, one idea per line. Draft lines below in the storyboard; the owner to approve each.
- Close: a line from `brand.json` copy, proposed "Every visit is a growth opportunity." or "Pageview to *pipeline.*"
- Fictional companies and people only, labelled "Illustrative example" on screen (e.g. "Northwind" for the buying committee's office, a fictional champion "Maya R.").

## Sound

- No narrator. The game's radio feel carries it: an original G-funk bed, free first (MIDI, General MIDI soundfont).
- Genre SFX made by us: radar ping, mission-start whoosh, pager buzz, moped engine, pizza box thump, footsteps, a "mission passed" brass and synth sting of our own.
- -14 LUFS, -1 dBTP.

## Notes, and what to confirm before anything is built

1. **Claims.** Can Breakout today (a) detect 3+ visitors from one office and (b) flag a champion who changed jobs and track them to the new company? The features copy only says "company, person, buying group and intent signals". Nothing goes on screen until confirmed.
2. **Format.** One 45 s film with both missions, or a series (one cut per mission, more missions later)?
3. **The hero.** Name and look for our fictional protagonist.
4. **Font.** The genre's look comes from a heavy outlined display face. Use an open (OFL) face styled to match, unless the owner has cleared a commercial one for video.
5. **Guideline tension.** The style log rejected cartoon characters and literal B2B scenery ("This animation style is bad. The story is also too b2b"). This brief is character-led and literal by the owner's request; offices appear only as buildings on the map, never as desks or screens.
6. **How it is made (free first).** A low-poly city and hero built in code (three.js inside the HyperFrames page, every frame a pure function of time), or Blender (skill `launch-world`). Generated plates on Higgsfield only after a stated cost and a yes.
