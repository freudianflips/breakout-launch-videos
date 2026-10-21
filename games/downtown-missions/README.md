# Downtown Missions

A playable browser game in the San Andreas style, starring CJ: ride and walk a low-poly downtown San Francisco and run two missions, each teaching one buying signal and the move that wins it.

| Mission | The move | Signal | Win | Lose |
|---|---|---|---|---|
| Pizza for the Buying Committee | Speed: act before the signal cools | 3 visitors from 1 office | Reach Northwind's door before the SIGNAL meter runs out (about 60 s) | The meter empties: "The signal went cold." |
| Tail the Champion | Patience: follow her from her old office to her new one | Your champion just changed jobs | Follow her taxi to Halcyon, staying between 9 m and 80 m | Too close for 3 s: "She spotted you." More than 80 m for 4 s: "You lost her." |

Pick a mission (or free roam) from the menu at the start. After a mission, the city lights violet and the Breakout wordmark comes up, with "Play again" or "Keep driving".

## Play

Open `index.html` in a browser (it loads three.js and the fonts from public CDNs), or play the published version.

| Key | What it does |
|---|---|
| `W` `A` `S` `D` or arrows | Walk (relative to the camera) or ride (throttle, brake and reverse, steer) |
| `E` or `F` | Get on or off the scooter |
| `Esc` | Mission select |
| `Shift` | Run |
| `Space` | Brake |
| Mouse drag | Look around |
| `R` | Radio on or off |

On a phone: the stick steers, the buttons get you on or off and brake.

## How it is made

- `game.src.html` is the whole game: the city, the cast, the physics (terraced hills you can jump off, buildings, traffic and the cable car you bump into), the missions, the HUD, the radar and all the sound (an original G-funk radio loop and the effects, synthesised with Web Audio). The city, the cast and the HUD are the same as the video template [`templates/open-world`](../../templates/open-world/README.md).
- `build.py` inlines the brand's logo and mark from [`brand/`](../../brand/) and writes `index.html`; `--artifact <path>` also writes the body-only page used for publishing.
- **The look (owner's decision, 2026-10-21):** "Forget the rights, use the San Andreas look exactly. Use CJ as well." The game uses the San Andreas HUD layout and colours, the PS2 trails and colour filter, and CJ as the hero. This overrides the rights rule in [`CLAUDE.md`](../../CLAUDE.md) for this game only. It does not use the game's name or logo, any of its files, or its music. The real Pricedown font needs a paid web licence, so Bowlby One (SIL OFL) stands in.
- Still in force: every other person and company is fictional and labelled "Illustrative example". `brand/brand.json` is not yet reviewed, and the two signals are not yet confirmed as product claims, so the game is a draft. Using CJ and the game's trade dress carries legal risk for anything public; check with a lawyer before release.
