# Breakout style log

The look of Breakout's launch films, decided one round at a time. Change 1 variable per round, and write each verdict in the owner's words in the table at the bottom.

## Where it stands (round 1)

| Lever | Now | Where it lives |
|---|---|---|
| Grounds | The app's white `#fdfdfd` for statement scenes, deep indigo `#1c1778` for dark cards, indigo `#4e46dc` for 1 accent card | `brand/brand.json` `colors` |
| Key words | A soft indigo marker on light grounds, lilac `#9a95ff` on dark | `highlight`, `accent_on_dark` |
| Type | Inter 700, tracking -0.045em, hero words at 110 to 150 px | `fonts.display` |
| Logo | The two-tone wordmark exactly as the app shows it, no mark | `film.json` `"lockup": "logo"` |
| Motion | The kit's Apple and Lovable grammar: hard cuts on the voice, dives and collapses, a push into the product, a quiet end | `film/templates/body.html` |
| Voice | Challenger: direct, confident, 1 idea per line | `film/film.json` `lines` |
| Music | The free scratch bed at 120 BPM, drop on the cut | `film/score/` |

## Open questions to settle together

0. **The homepage.** Its styles could not be read from the build container (network policy). Check them against `brand/preview.png`, or allow getbreakout.ai and re-extract.
1. **Light or dark world.** Light statement scenes with dark punch cards (now), or a fully dark, indigo-glow film that feels more "AI"?
2. **How much indigo.** 1 accent card per film (now), or indigo as the main ground with white type?
3. **Type.** Inter as a stand-in, or the site's own face (needs its files and a video licence)?
4. **Hook direction.** Type-only problem lines (now), a stylised "visitor leaves the site" moment, or a real website recording with the AI SDR opening a conversation?
5. **Product shots.** Accounts, the account Browsing Summary, All Chats and Contacts are in. Missing: a live AI SDR conversation (the engage beat shows a list, not a chat) and a follow-up email. Contacts is mostly blurred; a demo workspace with sample data would read better.
6. **Narrator.** Gender, age, pace. The kit's default is brisk and clear, 2.2 to 2.7 words a second, never performed.
7. **Music.** Clean electronic at about 120 BPM (now), or something warmer?

## Verdicts

| Date | Round | Film | Approved | Rejected |
|---|---|---|---|---|
| 2026-10-05 | 1 | attention | Awaiting the owner's verdict. Changed: logo and colours taken from the app ("break" `#1C1778`, "out" `#4E46DC`); real screens with customer data blurred, replacing round 0's placeholders | |
