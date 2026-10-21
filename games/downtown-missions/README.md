# Downtown Missions

A playable browser game in the San Andreas style, starring CJ as an SDR: ride and walk a low-poly downtown San Francisco and run two missions, each teaching one buying signal and the move that wins it.

| Mission | The move | Signal | Win | Lose |
|---|---|---|---|---|
| Pizza for the Buying Committee | Speed: act before the signal cools | 3 visitors from 1 office | Reach the target's door before the SIGNAL meter runs out (about 60 s) | The meter empties: "The signal went cold." |
| Tail the Champion | Patience: follow her from her old office to her new one | Your champion just changed jobs | Follow her cab from her old company to Anthropic, staying between 9 m and 80 m | Too close for 3 s: "She spotted you." More than 80 m for 4 s: "You lost her." |

Pick a mission (or free roam) from the menu at the start. After a mission, the city lights violet and the Breakout wordmark comes up, with "Play again" or "Keep driving".

## Target accounts

Every run mixes up the accounts: mission 1 sends the pizzas to one of the Financial District accounts at random, and in mission 2 the champion leaves one of the others for Anthropic. Each is a real company at its real San Francisco HQ, with its own logo on the tower and over the door (`logos/`, sources in [`logos/SOURCES.md`](logos/SOURCES.md)):

| Account | HQ in the game | Where it sits on the map | Role |
|---|---|---|---|
| Vanta | 655 Montgomery St | Across the street from the Transamerica Pyramid | Mission 1 target, or the champion's old company |
| Rippling | 430 California St | On California Street, a block north of Market | Mission 1 target, or the champion's old company |
| Figma | 760 Market St | On Market Street near Union Square | Mission 1 target, or the champion's old company |
| Anthropic | 500 Howard St | South of Market, next to Salesforce Tower | The champion's new company |

The visits, the people (the committee, Sarah F.), Sarah's move and the meetings are fictional, and the game says so on screen. Naming a real company as the champion's old employer can read as saying it was a Breakout customer; it is labelled as fiction, but check before anything public.

Traffic includes Waymos (their sensor dome spins), Muni buses, taxis, SFPD cars, SUVs and pickups.

## The story, with the SDR cutscenes

1. **Pizza for the Buying Committee:** three people from the account are looking at pricing, so CJ takes them pizza before they lose interest. "Uh, we didn't order pizza." "I know. I'm CJ, from Breakout. You were just on our site." Upstairs he books the meeting live on Breakout's booking screen.
2. **The alert:** at CJ's desk, Breakout flags that Sarah F. just left her company.
3. **Tail the Champion:** CJ follows her cab to Anthropic, and they talk it out, voiced, for about 35 seconds: "CJ? I've worked here for four hours." "Did you... follow my taxi?" "We call that account-based marketing." "That is not what that means." ... "How did you even know I left?" "Breakout told me. It keeps an eye on my favorite people." ... "So. Thursday at two?" "...Thursday, 2 PM. And bring pizza." "I always bring pizza."

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
- `build.py` inlines the brand's logo and mark from [`brand/`](../../brand/), the logos in `logos/` and the voice takes in `vo/`, and writes `index.html`; `--artifact <path>` also writes the body-only page used for publishing.
- **Voices:** every CJ and Sarah line in Tail the Champion is spoken (CJ: Kokoro `am_fenrir`, Sarah: `af_heart`). `voice.py` reads the lines from `game.src.html`, speaks the new or changed ones with [Kokoro-82M](https://github.com/thewh1teagle/kokoro-onnx) (Apache 2.0, free, runs locally), levels them and writes `vo/`. The scenes time themselves to the takes, so change a line, run `voice.py`, then `build.py`. Lines from Breakout and the buying committee stay text.
- **The look (owner's decision, 2026-10-21):** "Forget the rights, use the San Andreas look exactly. Use CJ as well." The game uses the San Andreas HUD layout and colours, the PS2 trails and colour filter, and CJ as the hero. This overrides the rights rule in [`CLAUDE.md`](../../CLAUDE.md) for this game only. It does not use the game's name or logo, any of its files, or its music. The real Pricedown font needs a paid web licence, so Bowlby One (SIL OFL) stands in.
- **Real target accounts (owner's requests, 2026-10-21):** "add the logos of actual target companies ... and their actual hqs", then "Remove Northwind altogether, only use real company names". This overrides, for this game only, the rules that a real company appears in plain type and never with its logo, and that no customer is invented. Each is labelled "Illustrative example".
- **CJ** has the face from the reference render the owner supplied (`cj.jpg`) and the outfit from the San Andreas screenshot the owner sent: white tee, baggy woodland camo, black cap, black sneakers.
- **Fonts:** Bowlby One for the Pricedown-style text (the gold lowercase mission title, MISSION PASSED, the clock and money), Nunito Black for the subtitles and objectives (keywords in gold or blue), Pirata One for the area names. All are SIL OFL, loaded from Google Fonts.
- Still in force: every other person and company is fictional and labelled "Illustrative example". `brand/brand.json` is not yet reviewed, and the two signals are not yet confirmed as product claims, so the game is a draft. Using CJ and the game's trade dress carries legal risk for anything public; check with a lawyer before release.
