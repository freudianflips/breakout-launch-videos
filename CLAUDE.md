# Working in Breakout Launch Videos

Read README.md, then `skills/launch-film/SKILL.md`. This repo makes Breakout's product launch films: a hook (the story before the cut) on a shared body (the logo, hero words, the product at close range, the lockup).

- The canonical skills are in `skills/`. `.agents/skills` and `.claude/skills` point to that folder. Update `skills/catalog.json` when a skill's name or description changes.
- Start every film from `brand/brand.json`. While it says `"reviewed": false`, any film is a draft: show `brand/preview.png` and say so. The logo comes from the team Drive (`brand/source/`), not from the extractor. Re-running `tools/brand-from-url.mjs` into `brand/` deletes the logo and fonts, so extract into a scratch folder and copy over only what you need.
- The film's words come from Breakout's own copy (`brand.json` `copy`, the Brand Guide for Writers). Voice: challenger brand, direct, confident, short sentences, one idea per line. Keep lines verbatim where they exist, and never invent a number, customer or claim. Unknown facts stay unknown: ask.
- Never show a competitor's name or logo in a film.
- Order of work: the owner says what the launch is; write `film/BRIEF.md` and `film/STORYBOARD.md` (skill `launch-story`) and clarify them with the owner; only after the owner approves the storyboard, make frames or video. Do not generate style frames or renders before that.
- Show frames before building. A contact sheet or snapshots of every new beat come before a full render, and a free render (scratch voice, scratch bed, synthesised sound) comes before any paid generation.
- Paid generation (Higgsfield or any other provider) runs only on the team's own account, and only after you state the cost of the job and the reader says yes. Never write an API key into the repo.
- Scratch voices are for timing only and are never published (`docs/rights.md`). Generated people are fictional; no famous people, lookalikes, real films or third-party brands.
- Product screens in `film/assets/screens/` must be real Breakout UI with customer data blurred or replaced. Never commit an unblurred screen.
- Edit `film/film.json`, `film/hooks/*/hook.json` and `film/templates/body.html`; never a generated file in `film/compositions/`. Every beat stays a pure function of time.
- Record every look verdict (approved or rejected, in the reader's words) in `docs/breakout-style.md`.
- Before committing, run `python3 scripts/check-template.py`. Check a changed helper with a real build (`python3 film/build.py attention`).
