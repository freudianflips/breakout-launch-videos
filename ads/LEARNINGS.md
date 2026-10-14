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

- 2026-10-14: Facts from the owner. A free trial exists: Signals (identify visitors) is self-serve, $500/mo after a 30-day trial with no credit card, so one person can buy it; Growth (the AI SDR) goes through a demo. Meeting booked is the outcome that counts. HubSpot keeps utm_content on conversion. Budget starts at $100/day. Launch by hand in Campaign Manager until the Advertising API is approved.

## By tag

<!-- auto:start -->
No ad has enough data yet.
<!-- auto:end -->
