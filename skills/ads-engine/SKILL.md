---
name: ads-engine
description: Run Breakout's paid social ads engine (LinkedIn first). Turns a campaign idea into a brief, a matrix of genuinely different concepts, audiences per persona, and tagged ad variants (copy plus on-brand static designs, document ads, creator and Thought Leader scripts), lints them against the brand and LinkedIn's limits, renders a feed preview, exports or launches them paused, ingests LinkedIn and CRM results, scores every ad with the Banger Score, writes the learnings and spins 10 new executions around each winner. Use for "ads", "ad creative", "LinkedIn ads", "campaign", "ad variants", "test concepts", "ad copy", "creative testing", "leaderboard", "what's winning", "scale the winners", "ad budget".
---

# Ads engine

The engine lives in [`ads/`](../../ads/README.md); read its README first, then [`ads/LEARNINGS.md`](../../ads/LEARNINGS.md). You do the creative work (concepts, words, design choices); `ads/engine/ads.py` does the structure (ids, tags, linting, rendering, export, launch, scoring, learning). Every command runs from the repo root as `python3 ads/engine/ads.py ...`.

The repo's rules hold here as they do for videos (`CLAUDE.md`): words from Breakout's own copy, no invented numbers, customers or claims, no competitors, real UI only, fictional examples labelled, nothing spent without a stated cost and a yes.

## 1. Idea to brief

The owner gives the idea. Run `new <campaign> --code ABC --idea "..."` (the code is the ad id prefix, 2 to 8 capitals, never reused). Fill `BRIEF.md` with them:

- **Who buys, and can one person buy alone?** For Breakout, yes on the trial door (Signals, a 30-day free trial with no card) and no on the demo door (Growth). Trial ads talk to that one person, like consumer marketing; set `copy.cta` and `url` from `campaign.json` `funnels`.
- **The one feeling** in a sentence.
- **3 to 6 concepts that are genuinely different ideas**, not phrasings of one idea. The test: would each still make sense with the others' headlines removed? Each concept cites the line of `brand/brand.json` `copy` it comes from.
- What `ads/LEARNINGS.md` already says that applies. Start from the winners there before inventing.
- Offer, landing page, the outcome that counts in the CRM, the budget. Unknown facts stay unknown.

Stop and get the brief and the concept matrix approved before writing ads.

## 2. Audiences

Personas are keys in `ads/taxonomy.json`; their LinkedIn targeting is `ads/audiences.json`. Each persona becomes 1 test campaign (LinkedIn targets per campaign). While `audiences.json` says draft, say so. Resolve titles, industries and skills to URNs with `audience resolve titles "Head of Demand Generation" --live` before a live launch; aim for 50,000+ members per audience. A new persona goes into `taxonomy.json` and `audiences.json` first.

## 3. Write the ads

Add ads to `campaign.json` `ads`. Each one:

```json
{"id": "P2P-013", "status": "draft", "concept": "ask-me", "angle": "buyer-experience", "persona": "demand-gen",
 "awareness": "solution", "format": "img-1x1", "hook": "proof",
 "copy": {"intro": "Hook line under 150 characters.\nOne more line.", "headline": "Under 70 characters.", "description": "", "cta": "REQUEST_DEMO"},
 "design": {"template": "chat", "fields": {"headline": "Go ahead. *Ask me stuff.*", "turns": [...], "label": "Illustrative example"}}}
```

- **Spread across concepts first.** A first round is 1 or 2 ads per concept per persona, each a different format or hook. 10 near-identical headlines teach the platform nothing.
- **Intro text**: the hook lands before the "see more" fold (about 150 characters). Short sentences, one idea per line, lead with a verdict. Use brand lines verbatim where they exist.
- **Consumer, not committee**: lead with what the persona already cares about (`unaware`, `humour`, `joke`, `pov`), then the product. A joke must be about their world, never about a real person or another brand.
- **Design**: pick from `ads/designs/README.md`. Little text on the image (12 words at most, 2 to 4 a side on a split). Product screens come only from `assets/screens/`, cropped to the part that matters.
- **Formats people make** (`video-creator`, `thought-leader`, `video-motion`) get a `script` instead of a design: `hook_0_3s`, `hold_3_10s`, `product_...`, `cta`, plus who presents and the length. Creator talent is a real person with a signed release. A Thought Leader post for Sachin is written with the `sachin-linkedin-posts` skill if it is available and goes to him to approve; hooks can be sharpened with `linkedin-hooks`. A motion ad starts from a video template and follows the video workflow in `CLAUDE.md`.
- A number needs a source: brand.json copy or an entry in `ads/claims.json` that the owner gave you.

Run `lint <campaign>` until it shows 0 errors, and treat every warning as a question to answer.

## 4. Preview and approval

`render <campaign>` writes each creative to `out/` and `out/feed.png`, every ad as it reads in a feed with its tags. Show the owner `feed.png` (and say it is a draft while brand.json is not reviewed). Record each look verdict in the owner's words in `docs/breakout-style.md`. Ads the owner approves get `"status": "approved"`.

## 5. Launch

State the plan and the spend: personas, ads per campaign, daily budget, test share, and how long until each ad reaches `min_impressions`. Wait for a yes.

- **By hand (now)**: `kit <campaign> [--round N]` writes `launch/kit-roundN.html`, every campaign setting and ad field in build order with Copy buttons and the files to upload. Open it, or publish it as a private page so the owner can keep it next to Campaign Manager. Ad names must start with the ad id.
- **In the owner's browser.** Loading Campaign Manager needs the owner's own logged-in browser, so it runs in a Claude session on their computer (Claude Desktop, or `claude remote-control` in this repo), never in a cloud container and never with their password typed into a chat. That session follows the kit top to bottom: upload the Matched Audience files first (they take up to 48 hours to match), then the campaign group, the campaigns and the ads. It saves campaigns as **drafts**, never clicks Launch or turns an ad on, and leaves the budget at what the kit says (or blank when the kit says "not set"). It stops and asks when a screen differs from the kit, and finishes by listing what it created. The owner activates.
- **Audience files** (contact or company lists) hold personal data: build them in `ads/data/` (not in git) with only the columns LinkedIn matches on (email, name, title, company, country; or company name, website, domain). Drop phone numbers and profile text.
- `export <campaign>` writes `launch/ads.csv` (manual upload: ad name with tags, intro, headline, CTA, URL with `utm_content=<id>`, file) and `launch/plan.json`.
- `launch <campaign>` is a dry run that logs every API request. `launch <campaign> --live` (token in the environment, never in the repo) creates the campaign group and campaigns as DRAFT and the ads as PAUSED. A person activates them in Campaign Manager. Video and Thought Leader ads are set up by hand.
- **After loading**, run `verify <campaign> --round N` (read-only API: `LINKEDIN_ACCESS_TOKEN` with r_ads and r_ads_reporting, `LINKEDIN_AD_ACCOUNT`, both in the environment's settings). It checks every campaign and ad against the kit (names, intro, headline, URL with `utm_content`, CTA, budget, Matched Audience, audience expansion and the Audience Network off) and writes `launch/launched.json`, which `ingest api` needs. Fix every error before activating.
- **The next round, over the API**: once the owner approves a round's ads, `sync <campaign> --round N` (dry run) then `--live` uploads them and creates them PAUSED in the existing campaigns. `status ... --pause --live` stops ads (an offer's end date, a loser); `--activate` spends money and runs only on the owner's explicit yes in this conversation. Pausing a round's outgoing ads and activating the incoming ones is the rotation.
- At most 5 active ads per campaign, 1 per concept; rotate the next set in as ads are judged.

## 6. Results, score, learn

Weekly, or when asked "what's working":

1. `ingest linkedin <Campaign Manager ad export.csv>` (or `ingest api --since YYYY-MM-DD --live`) and `ingest crm <CRM export.csv>` with a `utm_content` column and meetings, SQLs or pipeline. Server-side outcomes are the truth; LinkedIn's own conversion count is not scored.
2. `score` writes `ads/LEADERBOARD.md`. Read it before you report: `learning` means not enough data yet; a `hook trap` stopped the scroll and lost people by 25%.
3. `learn` regenerates the by-tag tables in `LEARNINGS.md`. Then write what you conclude as a dated note (`learn --note "..."`): what won, the evidence, what to do next. Promote a note to a numbered Rule when the owner agrees; strike a rule the data contradicts.

## 7. The next round

- **Winners**: `iterate <campaign> <ad>` adds 10 stubs with the winner's concept, angle and persona, each a different format and hook. Fill every TODO with a new execution of the same idea (new words, new picture, same insight), lint, render, preview.
- **Hook traps**: keep the hook, rewrite what follows it.
- **Losers**: pause; note what you think failed.
- **Budget**: `budget <campaign> --daily N` recommends 15 to 25% for testing and the rest behind winners, weighted by score. Bring it to the owner; change budgets in Campaign Manager only after a yes.
- Keep at least a third of each round for new concepts, so the account keeps finding winners.

## Before committing

`python3 ads/engine/test_ads.py`, `python3 ads/engine/ads.py lint <campaign>` for every changed campaign, and `python3 scripts/check-template.py`. Renders, request logs and raw performance exports stay out of git.
