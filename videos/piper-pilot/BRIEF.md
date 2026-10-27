---
workflow: product-video
message: "Breakout goes live in under 3 hours. Qualified takes 8-12 weeks."
destination: LinkedIn, paid social (16:9 master, 4:5 and 9:16 cuts later)
aspect: 1920x1080
language: en
length: 30s
angle: Two-hander comedy (the genre of the classic two-person computer ads), 1 idea per spot
status: draft, awaiting the owner's approval
---

## Intent

A pilot for a series of short comedy spots: two people on a white backdrop, Breakout and Piper (Qualified's AI SDR) played as characters. They stand side by side and talk. Breakout is relaxed and already working; Piper is pleasant, earnest and still being set up. The joke is always a real, sourced difference, played straight.

The owner chose 1 pilot of 30 s for LinkedIn and paid ads (2026-10-27), with realistic generated actors and voices, so the format and the actors are proved before more spots are written. Naming Qualified and Piper was approved on 2026-10-26 (`CLAUDE.md`).

While `brand/brand.json` says `"reviewed": false`, this film is a draft.

## The idea of this spot

**Go-live.** Breakout went live this morning. Piper is in week 1 of implementation. A visitor walks past: Breakout knows who she is; Piper knows her company. The buyout offer closes it.

## Claims (sources saved 2026-10-27)

From getbreakout.ai/compare/qualified-alternative, verbatim:

| Beat | Breakout | Qualified |
|---|---|---|
| Go-live | "<3 hours, self-serve" | "8-12 weeks, enterprise sales only" |
| Buying | (no demo needed for the paid pilot: "Yes · fixed scope, live in 3 hours") | "Qualified requires a demo, a quote, and an annual contract before you see a number." |
| Who | Person-level de-anonymization: "Yes, waterfall through multiple data providers" | "No &mdash; account-level only" |
| Offer | "Switch to Breakout by November 30, 2026 and we'll cover what's left on your Qualified contract." · "Up to $30,000 covered" | |

About Piper (qualified.com, the 2024 launch release and the AI FAQ): Piper is Qualified's AI SDR agent, which works on the company's website. The claims above are about Qualified, the platform Piper runs on; the Piper character speaks for it.

## Rules for this film

- **Qualified and Piper:** named, never with Qualified's logo, colours, fonts, UI, or Piper's own avatar or likeness. The Piper actor is a fictional person who looks nothing like Qualified's marketing character or staff.
- **Every line is true.** Each joke stages a row above. Exaggeration is in the acting (Piper's patience, the length of the checklist), never in a number.
- **The genre, not the ads.** A white seamless and two people talking is a genre. No lines, music, wardrobe, casting or framing copied from Apple's campaign; no "Hi, I'm a ..." opener.
- **People:** 3 generated, fictional adults (Breakout, Piper, the passing visitor). Check every face for a likeness to anyone famous; regenerate rather than fix.
- **Visitor:** "Maya R., VP Marketing, Northwind" is fictional and labelled "Illustrative example" on screen.
- **Dated offer:** the buyout ends 30 November 2026. This spot must be published before then, or the end card changes.
- **On-screen text** is added in HyperFrames, never generated inside the footage (generated text garbles).

## Assets

- Generated: the 3 actors (character stills first, then video), both voices.
- Brand: `logo.svg`, New Kansas / Fraunces, Manrope, violet `#4c00ff` for Breakout's single accent (a violet sweater), grey `#17161b` only for Piper's side.
- Source captions: small Fragment Mono line, "Source: getbreakout.ai/compare/qualified-alternative", while a claim is up.

## Production (after the storyboard is approved)

Nothing below runs before approval. Quotes are live Higgsfield prices from 2026-10-27; the account holds 40 credits on the free plan.

| Step | Model | Credits |
|---|---|---|
| Character stills, 3 actors × 4 options | Soul 2 or GPT Image | about 2 to 4 |
| Voice audition, both roles, 1 line × about 20 voices × 3 engines | `text2speech_v2` (VibeVoice, CosyVoice, ElevenLabs) and Eleven v4 dialogue | about 6 to 10 |
| Free animatic: stills + chosen voices + captions + logo, timed | HyperFrames, local | 0 |
| Model shoot-off: shot 2 only, 8-10 s | Seedance 2.5 480p, Veo 3.1, Kling 4.0 | about 130 |
| Pilot draft, 30 s | winner at 480p (Seedance: 90) | about 90 |
| Pilot master, 30 s | winner at 1080p (Seedance: 480) | about 200 to 480 |

The stills, voices and animatic fit in the current 40 credits. The shoot-off and the video need a top-up (and a Plus plan for full-quality Seedance), each stated and approved before it runs.
