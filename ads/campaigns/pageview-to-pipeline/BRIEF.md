# pageview-to-pipeline (P2P)

The engine's worked example: a first LinkedIn test written from Breakout's own copy. **Draft**: brand.json is not reviewed, the personas and audiences are not confirmed, and no ad is approved. Nothing has launched.

## Idea
Introduce Breakout to the people who own website conversion, in consumer-style ads that speak to one person, across 5 genuinely different concepts.

## Who buys
5 personas to test (ads/taxonomy.json): demand-gen, marketing-leader, founder, revops, sales-leader. Open question: can one person buy Breakout without a committee (a self-serve plan, a free trial)? If yes, the founder and demand-gen ads should say so and the CTA should change from Request Demo.

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

12 ads: 9 statics and a document ad rendered here, and 3 scripts (a Thought Leader post for Sachin, a creator video, a motion teaser from the particle-swarm template) that people make.

## What we already know
Nothing from Breakout's own data yet; the starting rules in ads/LEARNINGS.md are Wispr's.

## Offer and landing page
Request Demo to https://getbreakout.ai/ with `utm_content=<ad id>`. To confirm: the landing page, whether HubSpot keeps utm_content on the contact and the meeting, and which outcome counts (meeting booked, SQL or pipeline).

## Budget
To confirm: the daily total. With 20% to testing across 5 persona campaigns, each needs at least $10 a day, so a test budget under $50 a day should test fewer personas at once.

## Approval
- [ ] Brief and concept matrix approved by the owner
- [ ] Feed preview (out/feed.png) approved; approved ads set to "status": "approved"
- [ ] Spend approved
