# qualified-switch (QSW)

Companies running Qualified's website widget. Campaign idea from the owner (2026-10-14): "Qualified alternative / Qualified killer". "Qualified killer" is the internal name only; no ad says it. **Draft**: 8 ads written, awaiting the owner's look at the feed preview; budget and the domain list not set.

## Who they are
They already bought the category: an AI or chat widget on their site, an annual contract, an admin, a Salesforce-first setup. So skip education; they are **product-aware**. What stops them is not desire, it is switching cost: the contract, the implementation, the risk. The best creative names what they live with, then removes the reason not to move.

| Persona | What they live with (compare page, verbatim where quoted) | Lead concept |
|---|---|---|
| markops | "needs a CRM, an admin, and a hand-raise event"; the 8-12 week implementation | hours |
| demand-gen | buttons instead of answers; "a widget that waits"; account-level identification | just-ask, signals |
| cmo | the contract and the renewal: "Teams are paying top-of-market rates and getting a fraction of it back." | buyout |

## The one thing they should feel
"Switching is easier than staying, and the contract isn't a reason anymore."

## Concepts
| Code | Concept | Awareness | Design | Lines (claims.json, verbatim) |
|---|---|---|---|---|
| buyout | We'll buy out the rest of it | most-aware | dark verdict; a 3-page document ad (send the contract, we credit it, go live) | "Still under contract? We'll buy out the rest of it." · "Up to $30,000 covered" · "LIMITED OFFER · ENDS 30 NOVEMBER 2026" · "Stop paying for Qualified the day you switch" |
| hours | Hours, not weeks | product | split, 2 to 4 words a side | Go-live: "<3 hours, self-serve" vs "8-12 weeks, enterprise sales only" · "No implementation project. No admin ticket or technical handoff." |
| just-ask | Ask, don't click | solution | pattern break: a generic button-tree widget where every button misses, beside "Go ahead. Ask me stuff." (not Qualified's UI; never their logo) | "Modern demand gen teams need agents that act, not a widget that waits." |
| signals | 700+ versus one | solution | Swiss slam: "700+" against "1" | "Breakout tracks 700+ buying signals. Qualified tracks one." |
| tried-others | "Pretty good, actually" | product | verdict | "Meet the AI SDR considered \"pretty good, actually\" by people who've tried others" (brand copy) |
| your-widget | Your widget, today (tier 1) | product | their own capture next to Breakout; stills or a cut-down of the abm-split film | the account's widget_notes, as captured |

**Naming.** Recommended: name Qualified only where the line is the compare page's own (the buyout, the go-live split, the signals line), and leave the rest unnamed. The audience is already qualified by the targeting, so the unnamed ads lose nothing and read confident rather than petty; and it doubles as a test of named versus unnamed. Never Qualified's logo. The linter enforces the verbatim rule (`abm: true`).

**Urgency.** The buyout ends 30 November 2026, about 6 weeks from now: launch this campaign first and fast, and stop the buyout ads on 30 November.

## Audience
LinkedIn cannot target "uses Qualified". Build it:

1. **The company list.** Run `python3 ads/engine/stack.py qualified <domains.csv> --browser` on a list of ICP domains (a HubSpot, Clay or Breakout export). It checks each homepage for Qualified's widget (`js.qualified.com`, `QualifiedObject`; verified on kornferry.com) and writes LinkedIn's company list format. Better still if Breakout's own tech-stack signals already list them. Upload in Campaign Manager: Plan, Audiences, Create audience, Upload a list. LinkedIn needs 300+ matched members to serve, and not every company on the list will match: check the match count after upload.
2. **Layer the people** on the list: 2 campaigns, not 3, because the audience is small: *practitioners* (demand-gen and markops titles, Manager to VP) and *leaders* (Marketing, VP and CXO).
3. **Retarget** visitors of the compare page (the Insight Tag is in) with the buyout ads.
4. **Tier 1, 1:1**: the 10 to 20 biggest accounts on the list, each its own campaign with their own captured widget (`accounts/<slug>/`, the abm templates). Only where the company has 300+ members on LinkedIn.

## Offer, landing page and what counts
CTA Request demo, to getbreakout.ai/compare/qualified-alternative (the buyout is on it). A meeting booked counts 1, as everywhere. To ask: can HubSpot see a buyout submission (the contract upload) as its own event? It is the strongest intent signal this campaign makes.

## Budget
To ask: on top of round 1's $100/day, or out of it. Suggested: $50/day, $25 per campaign, for 2 weeks, then everything behind the winners until 30 November. A small audience means higher CPMs than round 1's assumed $45 and fast frequency: judge at 2,000 impressions an ad here, not 3,000, and watch frequency weekly.

## Round 1 (8 ads, statics)
| Campaign | Ads |
|---|---|
| QSW \| test \| practitioner \| image (demand gen + marketing ops titles, on the company list) | QSW-001 hours (split, 8-12 weeks vs <3 hours), QSW-002 just-ask (pattern break: buttons vs a question), QSW-003 signals (700+ or one), QSW-004 buyout (dark verdict) |
| QSW \| test \| cmo \| image (on the company list) | QSW-005 buyout (pattern break: one quiet line), QSW-006 hours (no implementation project), QSW-007 tried-others ("Pretty good, actually"), QSW-008 pricing (quote-based vs from $2,000/month) |

Every line naming Qualified is word for word from the compare page (the linter checks it), and the splits show the page as their source. Stop QSW-004 and QSW-005 on 30 November 2026.

## Approval
- [x] Concepts and naming Qualified in ads (verbatim from the compare page, no logo) taken as approved with the campaign idea (2026-10-14)
- [ ] Domain list source agreed; company list built and uploaded
- [ ] Feed preview approved
- [ ] Budget approved
