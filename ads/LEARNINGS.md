# Ads learnings

The one place every ad experiment's result lives, so each round starts from what the last one taught. Read it before writing a campaign brief; the agent reads it too (`skills/ads-engine/SKILL.md`).

Three parts: **Rules** are what we believe now, in plain words, each with the evidence behind it; the **Log** is dated notes in the order they happened (`python3 ads/engine/ads.py learn --note "..."`); **By tag** is regenerated from the data by `python3 ads/engine/ads.py learn` and never edited by hand. The ranked list of every ad is [`LEADERBOARD.md`](LEADERBOARD.md) once performance data exists.

## Rules

Starting beliefs, borrowed from Wispr Flow's playbook and not yet tested on Breakout's own LinkedIn data. Replace each with Breakout evidence as it comes in, or strike it.

1. Write for the one person who can say yes, not a buying committee. For Breakout that person exists: anyone can start the Signals trial alone (2026-10-14).
2. Consumer-style creative beats B2B-style creative: people, jokes and things the persona already cares about, then the product.
3. Concepts teach, variations don't. Test genuinely different ideas; a colour swap gives the platform no new signal.
4. A winning concept + angle + persona earns 10 new executions before anything new starts from zero.
5. Hook rate alone lies: an ad that stops the scroll and loses everyone by 25% still burns money.
6. Trust the CRM over the platform: meetings and pipeline by `utm_content`, not LinkedIn's conversion count.

## Log

- 2026-10-28: 2026-10-28 correction: the owner meant pause only the other practitioner ads. CMO campaign and its 4 ads back on at $25/day, extended to 30 November; practitioners run QSW-060 alone at $75/day.
- 2026-10-28: 2026-10-28, week 1 of stage 1 ($663, 1,630 impressions, 629 people, 8 clicks): the practitioner dictionary ad QSW-060 (qualified = limited, 'Or break out.') won with 5 of 8 clicks, 1.62% CTR, $28 per click; the same ad got 0 clicks from CMOs, and CMOs clicked once in 692 impressions (QSW-063). Owner: scale only the dictionary ad, pause the rest. QSW-060 runs alone in S1 practitioner at $75/day to 30 November; the other 7 ads paused and the CMO campaign paused. Watch frequency: one ad on about 1,000 people.
- 2026-10-21: 2026-10-21: stage 1 loaded over the API and the 8 ads set ACTIVE at the owner's word (QSW-010, 060, 061, 062 in S1 practitioner; QSW-009, 063, 064, 065 in S1 CMO); QSW-011 and QSW-013 deleted. Campaigns still DRAFT until launched in Campaign Manager.
- 2026-10-21: Owner (2026-10-21): 'buttons instead of answers is not a differentiator' (QSW-011, QSW-013 retired; still to delete on LinkedIn). Stage 1 is pure brand plays, wordplay on Breakout and qualified (QSW-060 to 065, plus 009 Overqualified and 010 qualified/booked). Stage 2 practitioners: the 4 real tactical gaps, each a compare-page row: person-level vs account-level only, LinkedIn follow-ups, 700+ signals vs one, self-serve vs enterprise sales only (QSW-066 to 069). Stage 3 approved as is ('Stage3s look good').
- 2026-10-21: Owner reset the qualified-switch order (2026-10-21): stage 1 pure awareness on Qualified's weak spots (practitioners tactical: hand-raise, manual assignment, feedback sessions, CSM churn; CMOs ROI and the SDRs still manning the tool), stage 2 side by side on dimensions per persona, stage 3 easy to switch (practitioners: the work; CMOs: the contract and cost). 16 new drafts QSW-044 to 059, all lines from the compare page; existing ads mapped into the stages (sequence block in campaign.json). Awaiting the owner's look at the stage sheet.
- 2026-10-19: Strategy reset for qualified-switch: a displacement sequence (Four Forces: push + pull > anxiety + habit; why change vs why stay; don't attack a tool the buyer chose; one campaign per stage, retarget forward). Week 1 loaded as 3 stage campaigns: practitioners S1 (QSW-011, $50), CMOs S1 (QSW-013, $25), CMOs S3 buyout (QSW-005, $25). LinkedIn: an unreviewed ad cannot be paused or moved to draft, so a stage change means a new campaign, not pausing ads; attaching conversions needs rw_conversions (done by hand in Campaign Manager); the matched lists show 1,000 and 2,100 members but 0 active, which holds delivery until LinkedIn refreshes them.

- 2026-10-19: A compare-page line can be true on the page and still wrong as an ad: the email rows (Qualified hands off to a sequencer, Breakout sends) are not a real difference ("Breakout also hands off to sequencer"). Before building a product contrast, confirm with the owner that the gap is real; claims.json now has a do_not_use list. The real email gaps (owner): personalization from each visitor's signals, and emailing visitors who never raised a hand (QSW-043).

- 2026-10-19: For a product callout, the owner wants it plain: "clearly and simply call out" the weakness, no metaphor (the ration book was rejected). Objects and wordplay suit awareness ads; a capability gap gets a clear, named, sourced split (QSW-042). LinkedIn: a draft ad cannot be archived before review, only deleted (`status --delete`).

- 2026-10-19: Owner rejected 6 question-led pain-point ads ("These are terrible. Remove these."): a question as the headline with a quoted answer reads as straight B2B. Kept only email volume, redone as an object (a ration book, QSW-041). The owner's taste so far: everyday objects and wordplay, yes; questions, comparisons and feature lists, no.

- 2026-10-14: First ads loaded over the API (QSW-033, QSW-034, the demo gift, clicks to the home page). What LinkedIn's API actually does on Breakout's account: the Advertising API token alone uploads images and creates ads in one call (createInline), so the Community Management app is not needed; a new ad cannot start PAUSED before its review (DRAFT works); Campaign Manager stores single-image ads as an "article" (title, description, thumbnail, source); uploads need `Content-Type: application/octet-stream`.

- 2026-10-14: qualified-switch round 1 loaded into Campaign Manager by the owner (in their own Claude window). The 382 companies in the audience export are verified Qualified users (owner checked them). Advertising API access granted; `ads.py verify` checks the live setup against the kit once a read-only token is in the environment.

- 2026-10-14: Owner liked the conceptual, everyday-object direction for the Qualified audience ("I like these ideas") over the straight comparisons ("mostly straightforward"). Full set built: 32 ads, 20 concepts, 3 rounds. First test of the hypothesis: object formats beat comparisons on hold and CTR with a product-aware audience.

- 2026-10-14: Owner on the first Qualified ads: "mostly straightforward"; wants more awareness and left-of-field concepts. Round 1 for qualified-switch is now 6 awareness ads in everyday-object formats plus 1 offer ad per campaign. Watch whether the objects (resume, quiz, poster, letter, receipt) beat the straight comparisons on hold and CTR, not only on hook.

- 2026-10-14: Second campaign: qualified-switch, the owner's "Qualified alternative" idea. Product-aware buyers held back by switching cost, so the buyout offer (ends 30 November 2026) leads; Qualified named only in compare-page lines, word for word. Pattern breaks added to round 1 at the owner's ask, one per campaign beside a standard version of the same concept, to measure the break itself.

- 2026-10-14: Round 1 set (owner): personas demand-gen, markops and cmo at about $33/day each. Identify is a 30-day free trial, not a free tier. A trial signup counts 0.24 of a booked meeting (ACV $6,000 vs $25,000). The LinkedIn Insight Tag is installed.

- 2026-10-14: Facts from the owner. A free trial exists: Signals (identify visitors) is self-serve, $500/mo after a 30-day trial with no credit card, so one person can buy it; Growth (the AI SDR) goes through a demo. Meeting booked is the outcome that counts. HubSpot keeps utm_content on conversion. Budget starts at $100/day. Launch by hand in Campaign Manager until the Advertising API is approved.

## By tag

<!-- auto:start -->
No ad has enough data yet.
<!-- auto:end -->
