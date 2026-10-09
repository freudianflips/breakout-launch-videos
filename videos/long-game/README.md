# Cartoon

A short story with simple, colourful cartoon characters drawn in code: a buyer, a rep and Breakout's agent as a friendly violet character, moving through a real story with small captions.

![Cartoon](poster.jpg)

| | |
|---|---|
| Use it for | Explaining the full product as a story: a person to root for, something at stake, a payoff. 45 to 60 s. |
| Verdict | Round 16, awaiting a verdict. Asked for by the owner: "simple cartoony entertaining animated colourful animated style to represent characters". |
| New video | `python3 scripts/new-video.py cartoon <name>`, then edit the copy in `videos/<name>/` |

## The example film

**"The Long Game"**: Maya clicks an ad and lands on the site as a faceless visitor. Breakout sees her, answers her question, and brings Sam the SDR into the chat. She leaves. Breakout keeps going: it researches the account and maps the committee, then follows up by email and LinkedIn. Over weeks it reaches out again on each new signal and flags when Northwind comes back, until Maya books. 56 s at 120 BPM, orchestral, small captions from the use-case pages. Story in [`STORYBOARD.md`](STORYBOARD.md).

## Make your own

| What | Where |
|---|---|
| Words: captions, chat lines, alerts, email, signals, slots | `film.json` |
| Beat times (bars at 120 BPM) | `film.json` `at` |
| The cast: skin, hair, top, hairstyle, glasses | `build.py` `C`, drawn by `person()`; the agent by `agent()` |
| Scenes, staging and motion | `template.html`: one `scene` block and one section of `render()` per beat |
| Music and sound | `score.py`, `audio.py` (both follow `at`) |

Characters are SVG with hinged arms (`.armL`, `.armR`), blinking eyes, and a mouth with five shapes (`smile`, `talk`, `flat`, `wow`, `grin`). The `live()` function in `template.html` animates them.
