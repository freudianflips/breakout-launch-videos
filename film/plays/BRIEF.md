---
workflow: product-launch-video
message: "Plug in any signal. Breakout researches the account, finds the whole buying committee, writes the email and books the meeting."
destination: TBD (LinkedIn and X assumed; see open questions)
aspect: 1920x1080 (a 1080x1350 cut for LinkedIn feed to confirm)
language: en
length: 45s
angle: Watch it run, framed by a concept hook
status: draft for the owner's review, not approved
---

## Intent

Breakout launches **Plays**. A play starts from any signal (a website visit, for example). From there Breakout:

1. personalizes the email using browsing history, firmographics, AI enrichment and 700+ signals;
2. uncovers the full buying committee;
3. sends through the team's downstream sequencer;
4. books the meeting.

You build a play from a template or by describing it in chat.

**Audience:** demand gen, marketing and RevOps leaders at B2B SaaS companies (the ICP in the Brand Guide for Writers and the partner guide).

**Tone, in the owner's words:** conceptual, analog and vintage. A meta concept frames the film: a nuanced, uncommon, nerdy fact about how the world is changing. Then it jumps into Breakout. The product visuals are real, but the text and motion graphics feel like an indie music video, "like a Tame Impala music video". Background music and sound effects carry it; no narration.

## Assets

The real Plays UI, saved in `film/assets/screens/`, with no customer data:

| File | Shows |
|---|---|
| `plays-new.png` | Create New Play: 4 templates ("Reach out to High-Intent Page Visitors", "Multiple Visitors, One Account", "Convert anonymous traffic to audience", "Convert website visitors to hand-raisers") and "or describe your own" |
| `plays-audience.png` | Multi-Visitor Account Outreach, Audience step: Website Visitors, Account Reveal, Identified going forward, Contacts per Company 3, plus the chat that builds the play from a prompt |
| `plays-filters.png` | Filters step: Visitor Count, Greater than or equal, 3 |
| `plays-personalization.png` | Personalization step: tokens `value_angle` and `team_research_line`, and the Email 1 canvas ("{company_name} a few folks have been looking") |
| `plays-destination.png` | Destination step: Outbound Sequencer, Sequence, Token Mapping, and Test |

Also on hand: the website agent screens (`agent-*.png`), the two-tone wordmark, and the site's fonts, mesh and palette (`brand/brand.json`).

## Words we can use (verbatim sources)

- **Homepage, Outbound Agent:** "Watch signals, not lists", "first-party signals (pricing visits, return visits) plus 700+ third-party ones (hiring, funding, tech-stack changes, champion job moves)", "Research every account first", "Write like your best rep", "Send at moment of intent", "Handle the reply".
- **Homepage:** "every site visitor is identified, enriched, and researched before first outreach", "You guide it. AI does the work.", "Pageview to pipeline."
- **The Plays UI itself:** "Multiple Visitors, One Account", "Catch accounts where three or more people visited this month", "Start from a template, or describe what you want below".
- **The owner's brief:** "plug in any signal", "uncovers full buying committee", "books the meeting".

## Notes

- **Claims:** only "700+ signals" (homepage) and what the UI shows. No customer names, no results, no numbers beyond those.
- **The concept fact (recommended):** honeybee swarms choose a new home by committee, and commit when about 15 scouts gather at one site (Thomas Seeley's research). It maps onto the "3 or more people from one account" play. Sources are in `film/plays/STORYBOARD.md`.
- **Third-party names:** the destination screen names the team's sequencer, as the product shows it. Keep it legible only if the owner wants the integration named; otherwise frame past it. No competitor appears anywhere.
- **Not shown yet:** a booked meeting. We have no screen of it; see open questions.
