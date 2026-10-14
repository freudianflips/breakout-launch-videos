# pageview-to-pipeline (P2P)

The first LinkedIn test, written from Breakout's own copy. **Draft**: brand.json is not reviewed, the audiences are not confirmed, no ad is approved and the round 1 plan below awaits a yes. Nothing has launched.

## Idea
Introduce Breakout to the people who own website conversion, in consumer-style ads that speak to one person, across 5 genuinely different concepts.

## Who buys
Two doors (owner, 2026-10-14; getbreakout.ai/pricing and /product/identify):
- **Trial**: Signals (identify visitors) starts at $500/mo with a 30-day free trial, no credit card, live in 5 minutes. One person can start it alone, so these ads are written for one person, consumer-style. CTA Sign up, to /product/identify.
- **Demo**: Growth (the AI SDR) starts at $2k/mo, via a demo. CTA Request demo, to the homepage.

5 personas in the taxonomy; round 1 tests 2 (below).

## The one thing they should feel
"My website could be booking meetings right now, and it isn't."

## Concepts
| Code | Concept | Why it might win | Source line in brand.json copy |
|---|---|---|---|
| always-on | Your best SDR, always on | Names a gap every marketer feels: nights, weekends, lunch | one_liners[2] |
| ask-me | Go ahead. Ask me stuff. | Shows the buyer's side, which few B2B ads do; the product is the proof | the agent's welcome line; features[1] |
| earned | Attention is earned | A challenger verdict marketers will argue with | h2[0..2] |
| pretty-good | "Pretty good, actually" | Self-deprecating humour reads as consumer, not B2B | site_h2[1] |
| touch-grass | You touch grass | A joke for RevOps about the stack they live in | site_h2[3] |
| know-who (proposed) | Know every buyer on your site | The self-serve door: start free today, see who is on your site | claims.json (the Identify page) |

12 ads: 9 statics and a document ad rendered here, and 3 scripts (a Thought Leader post for Sachin, a creator video, a motion teaser from the particle-swarm template) that people make.

## What we already know
Nothing from Breakout's own data yet; the starting rules in ads/LEARNINGS.md are Wispr's.

## Offer, tracking and what counts
Every URL carries `utm_content=<ad id>`; HubSpot keeps it on conversion (confirmed). **Meeting booked** is the outcome that counts. Trial signups are tracked and weigh 0 until the owner sets their worth (scoring.json `outcomes`). The site loads Google Tag Manager; whether the LinkedIn Insight Tag fires through it is unchecked.

## Launch
By hand in Campaign Manager with `ads.py kit` (launch/kit.html) until the Advertising API is approved (applied for, 2026-10-14).

## Budget and round 1 (proposed, awaiting approval)
$100/day (owner). No winner exists yet, so all of it tests; the 15 to 25% test share starts once winners do.

| Campaign | $/day | Ads (1 per concept) |
|---|---|---|
| P2P \| test \| demand-gen \| image | 50 | P2P-001 always-on, P2P-003 ask-me, P2P-007 pretty-good, + 1 know-who (trial) |
| P2P \| test \| founder \| image | 50 | P2P-002 always-on, + 1 know-who (trial), + 1 pretty-good for founders |

At an assumed $45 CPM, $50 a day is about 1,100 impressions, so 3 to 4 ads reach 3,000 each in about 2 weeks. Statics only: LinkedIn sets the format per campaign, and a document or video campaign would split $100 too thin. Round 2 adds the document ad, the creator video and Sachin's Thought Leader post, and the personas round 1 did not test.

## Approval
- [ ] Brief and concept matrix approved by the owner
- [ ] Feed preview (out/feed.png) approved; approved ads set to "status": "approved"
- [ ] Spend approved
