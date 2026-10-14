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

- 2026-10-14: Owner on the first Qualified ads: "mostly straightforward"; wants more awareness and left-of-field concepts. Round 1 for qualified-switch is now 6 awareness ads in everyday-object formats plus 1 offer ad per campaign. Watch whether the objects (resume, quiz, poster, letter, receipt) beat the straight comparisons on hold and CTR, not only on hook.

- 2026-10-14: Second campaign: qualified-switch, the owner's "Qualified alternative" idea. Product-aware buyers held back by switching cost, so the buyout offer (ends 30 November 2026) leads; Qualified named only in compare-page lines, word for word. Pattern breaks added to round 1 at the owner's ask, one per campaign beside a standard version of the same concept, to measure the break itself.

- 2026-10-14: Round 1 set (owner): personas demand-gen, markops and cmo at about $33/day each. Identify is a 30-day free trial, not a free tier. A trial signup counts 0.24 of a booked meeting (ACV $6,000 vs $25,000). The LinkedIn Insight Tag is installed.

- 2026-10-14: Facts from the owner. A free trial exists: Signals (identify visitors) is self-serve, $500/mo after a 30-day trial with no credit card, so one person can buy it; Growth (the AI SDR) goes through a demo. Meeting booked is the outcome that counts. HubSpot keeps utm_content on conversion. Budget starts at $100/day. Launch by hand in Campaign Manager until the Advertising API is approved.

## By tag

<!-- auto:start -->
No ad has enough data yet.
<!-- auto:end -->
