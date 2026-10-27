---
workflow: product-video
message: "Breakout went live this morning and already booked the meeting. Piper is still at kickoff."
destination: LinkedIn, paid social (16:9 master, 4:5 and 9:16 cuts later)
aspect: 1920x1080
language: en
length: 35s
angle: Two-hander comedy in the tone of the classic two-person computer ads: 1 premise (kickoff), the rival proud and oblivious, Breakout kind
status: cast and look approved 2026-10-27; v4 dialogue awaiting sign-off
---

## Intent

A pilot for a series of short comedy spots: two people on a white backdrop, Breakout and Piper (Qualified's AI SDR) played as characters. They stand side by side and talk. Breakout is young, attractive, quick and already working. Piper is the straight man: deadpan, literal, short answers, never a villain. Every joke is a real, sourced difference, played dry.

The owner chose 1 pilot for LinkedIn and paid ads (2026-10-27), with realistic generated actors and voices, so the format and the actors are proved before more spots are written. Naming Qualified and Piper was approved on 2026-10-26 (`CLAUDE.md`).

v2, from the owner's notes (2026-10-27): "Replace Maya Northwind with Sarah, VP Demand Gen at Vanta. Piper says Vanta. Say 'Piper' don't say 'From Qualified'. Add a few more jokes. Maybe a Pied Piper joke. Breakout needs to look young, attractive. Let Piper play a straight man. Keep the end card with Breakout logo + pageview to pipeline." The run grew from 30 s to 45 s to hold the jokes; a 30 s cut-down drops beats 4 and 6.

v4, after the first animatic ("this is terrible, not sounding natural at all"; "need better jokes here. Make it sound like the pc/mac joke tone"; "breakout comes off as braggy in the opener, skip that. Let's jump directly to 'Big week. Kickoff.'"): 1 premise, about 35 s. Piper is proud and oblivious and gets the jokes; Breakout is kind. The Pied Piper, LinkedIn and signals jokes are saved for later spots. The voices are generated as 1 conversation (Eleven v4 dialogue) instead of line by line.

While `brand/brand.json` says `"reviewed": false`, this film is a draft.

## Claims (sources saved 2026-10-27)

From getbreakout.ai/compare/qualified-alternative, verbatim:

| Joke | Breakout | Qualified |
|---|---|---|
| Kickoff, go-live | "<3 hours, self-serve" | "8-12 weeks, enterprise sales only" |
| Price | "Transparent pricing, published." | "Qualified requires a demo, a quote, and an annual contract before you see a number." |
| Sarah | Person-level de-anonymization: "Yes, waterfall through multiple data providers" | "No &mdash; account-level only" |
| Hand-raise, admin | (`brand.json` copy) "qualifies and books meetings" | "Qualified runs on chat-era architecture that needs a CRM, an admin, and a hand-raise event." |

Saved for later spots: signals ("Breakout tracks 700+ buying signals. Qualified tracks one."), LinkedIn follow-ups (Breakout, `brand.json` copy: "Converts drop-offs with personalized email and LinkedIn follow-ups"; Qualified: "No").

About Piper (qualified.com, the 2024 launch release and the AI FAQ): Piper is Qualified's AI SDR agent. The claims above are about Qualified, the platform Piper runs on; the Piper character speaks for it. Piper is never introduced aloud as "from Qualified"; the on-screen name tag carries it.

## Rules for this film

- **Qualified and Piper:** named, never with Qualified's logo, colours, fonts, UI, or Piper's own avatar or likeness. The Piper actor is a fictional person who looks nothing like Qualified's marketing character or staff.
- **Every line is true.** Each joke stages a row above. Exaggeration is in the acting (Piper's deadpan, the pause), never in a number.
- **The genre, not the ads.** A white seamless and two people talking is a genre. No lines, music, wardrobe, casting or framing copied from Apple's campaign; no "Hi, I'm a ..." opener.
- **People:** 3 generated, fictional adults (Breakout, Piper, Sarah). Check every face for a likeness to anyone famous; regenerate rather than fix.
- **Vanta:** a real company, named in plain type only, never its logo, colours or site, with "Illustrative example" on screen while it is up. Sarah is a fictional person; the film implies nothing about Vanta's vendors or customers.
- **On-screen text** is added in HyperFrames, never generated inside the footage (generated text garbles).

## Assets

- Generated: the 3 actors (character stills first, then video), both voices.
- Brand: `logo.svg`, New Kansas / Fraunces, Manrope, violet `#4c00ff` for Breakout's single accent (a violet sweater), grey `#17161b` only for Piper's side.
- End card: the Breakout logo and "Pageview to *pipeline.*" (`brand.json` `copy.site_h1`).
- Source captions: small Fragment Mono line, "Source: getbreakout.ai/compare/qualified-alternative", while a claim is up.

## Production (after the storyboard is approved)

Nothing below runs before approval. Quotes are live Higgsfield prices from 2026-10-27; the account holds 40 credits on the free plan.

| Step | Model | Credits |
|---|---|---|
| Character stills, 3 actors × 4 options | Soul 2 or GPT Image | about 2 to 4 |
| Voice audition, both roles, 1 line × about 20 voices × 3 engines | `text2speech_v2` (VibeVoice, CosyVoice, ElevenLabs) and Eleven v4 dialogue | about 6 to 10 |
| Free animatic: stills + chosen voices + captions + logo, timed | HyperFrames, local | 0 |
| Model shoot-off: 1 beat, 8-10 s | Seedance 2.5 480p, Veo 3.1, Kling 4.0 | about 130 |
| Pilot draft, 45 s | winner at 480p (Seedance: about 135) | about 135 |
| Pilot master, 45 s | winner at 1080p (Seedance: about 720) | about 300 to 720 |

The stills, voices and animatic fit in the current 40 credits. The shoot-off and the video need a top-up (and a Plus plan for full-quality Seedance), each stated and approved before it runs.
