# Breakout style log

The look of Breakout's launch films, decided one round at a time. Change 1 variable per round, and write each verdict in the owner's words in the table at the bottom.

## Where it stands (round 2)

| Lever | Now | Where it lives |
|---|---|---|
| Grounds | The site's light grey `#f4f4f4` with a soft violet bloom; dark scenes on the homepage hero's violet mesh; electric violet `#4c00ff` for 1 accent card | `brand/brand.json` `colors`, `gradients.dark_mesh` |
| Key words | *Italic* serif, as on the site ("Pageview to *pipeline.*"); lilac `#be79ff` on dark, no highlighter marker | `fonts.display.key_style`, `accent_on_dark` |
| Type | Headlines in New Kansas (Fraunces stand-in, weight 340, soft), sublines and UI chips in Manrope 500 | `fonts.display`, `fonts.body` |
| Logo | The two-tone wordmark exactly as the app shows it, no mark | `film.json` `"lockup": "logo"` |
| Motion | The kit's Apple and Lovable grammar: hard cuts on the voice, dives and collapses, a push into the product, a quiet end | `film/templates/body.html` |
| Voice | Challenger: direct, confident, 1 idea per line | `film/film.json` `lines` |
| Music | The free scratch bed at 120 BPM, drop on the cut | `film/score/` |

## Open questions to settle together

0. **New Kansas.** Render on a machine with New Kansas active in Adobe Fonts for the final cut; Fraunces is close but not the brand face.
1. **Light or dark world.** Light statement scenes with dark punch cards (now), or a fully dark, indigo-glow film that feels more "AI"?
2. **How much indigo.** 1 accent card per film (now), or indigo as the main ground with white type?
3. **Weight.** The site's New Kansas is light; is the film's 340 right on a 1080p screen, or one step heavier for legibility?
4. **Hook direction.** Type-only problem lines (now), a stylised "visitor leaves the site" moment, or a real website recording with the AI SDR opening a conversation?
5. **Product shots.** Accounts, the account Browsing Summary, All Chats and Contacts are in. The website agent (welcome and an asked question) now carries the engage beat. Missing: the agent's answer and a follow-up email. Contacts is mostly blurred; a demo workspace with sample data would read better.
6. **Narrator.** Gender, age, pace. The kit's default is brisk and clear, 2.2 to 2.7 words a second, never performed.
7. **Music.** Clean electronic at about 120 BPM (now), or something warmer?

## Verdicts

| Date | Round | Film | Approved | Rejected |
|---|---|---|---|---|
| 2026-10-05 | 1 | attention | Awaiting the owner's verdict. Changed: logo and colours taken from the app ("break" `#1C1778`, "out" `#4E46DC`); real screens with customer data blurred, replacing round 0's placeholders | |
| 2026-10-05 | 2 | attention | Awaiting the owner's verdict. Changed: the homepage's type system (New Kansas or Fraunces headlines, italic key words, Manrope), the hero's violet mesh on dark scenes, the site's palette, and "Pageview to *pipeline.*" on the end card | |
| 2026-10-05 | 3 | plays (first cut) | | The analog, vintage, psych direction as a whole. Owner: "more modern, more unexpected, more 'cool' and modern and conceptual. Fast cuts, shorter videos, one crisp message." Next: aesthetic options for approval, then a redo |
| 2026-10-05 | 4 | look tests | Look test 03, the Swiss grid ("i like 03. This is good."), with M1 "Signal in. Meeting out." | The honeybee concept ("Forget the honeybee thing. Let's try a more direct one.") |
| 2026-10-05 | 5 | signal (first cut) | "this is great". "Signal in. Meeting out." in the Swiss grid: type slams, the agent cards reading Notion's signals, the email writing itself from 2 signals with lines to each sentence, approve and send, "out." in violet, the lockup | |
| 2026-10-05 | 6 | signal (v2) | Awaiting the owner's verdict. The owner asked to "go slower on the middle part" and "spend some time on each of the cards on the left", with a zoom, motion and very legible text: a slow camera now visits the run card, the account card (rows 1 a beat, the 2 Acts) and the thinking card; 22.5 s | |
| 2026-10-05 | 7 | signal (v3) | "This is great." A big success state for the booked meeting, from the owner's reference: the slot picker (Thursday, Oct 15, 2:00 PM, Book meeting), then violet floods out of the button into "Meeting booked.", a drawn check and the booked card with 3 attendees; 24.4 s | |
| 2026-10-05 | 8 | swarm-test (motion test) | Awaiting the owner's verdict. Moodboard tile 11, the signal swarm, as a 7.5 s motion test: 5,200 particles drift as labelled signals, snap into "Signal" on the beat, burst into "in.", stream into "Meeting", burst pink into "out." and settle into the two-tone wordmark with "Plays" | |
| 2026-10-05 | 9 | press-play (first cut) | "I love this." Concept 1, "Press play." (owner: "Love (1)"), on the Swiss grid: signals as sequencer rows that play what they light, the agent muting 2 blog views, a pull back to 700+, ▶ pressed for the drop, the email writing itself word by word on 16ths with wires from its 2 signals, the committee as 3 notes, violet flooding from ▶ into "Meeting booked." and a ✓, then "Plays ▶"; 28.1 s, scratch bed | The electronic scratch bed ("Use a better sound track that's more orchestra-y") |
| 2026-10-05 | 10 | press-play (orchestral score) | Awaiting the owner's verdict. Same picture, an orchestral score from the same pattern: timpani and pizzicato basses for the pricing page, string stabs for the new CFO, a pizzicato ostinato for return visits, a harp cut dead on the mute, a tremolo swell for 700+, a timpani roll and crescendo into the press, 1 beat of silence, the full orchestra in E minor on the drop with horns for the committee, E major for "Meeting booked.", a celesta music box under the lockup. Free render (FluidR3 soundfont) | |
| 2026-10-06 | 11 | abm: korn-ferry (first cut) |  A new series for accounts on Qualified (owner: "Rest looks good. Go and create it."): their captured site and widget, "4 buttons. No text box. No way to just ask.", the fold into the grid, Breakout's own widget answering an open question, then Who, Why and Act with rows quoted from the compare page, "Meeting booked.", <3 hours vs 8–12 weeks, the buyout and the close; 36.6 s, orchestral score opening as hold music | Too fast. Owner: "this is very fast. slow it down, esp the text-heavy sections that need a pause" |
| 2026-10-06 | 12 | abm: korn-ferry (slower) | Awaiting the owner's verdict. Same tempo and motion, more bars per beat: 57.2 s. Notes 2 beats apart, the answer and the email typed slower, each comparison row shows Breakout then Qualified a beat later, and every text beat holds to read with a slow 1.8 % drift | |
