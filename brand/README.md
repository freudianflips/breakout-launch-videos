# brand/

The Breakout brand kit. `brand.json` is the only file the film reads.

| File | What | Source |
|---|---|---|
| `logo.svg` | The wordmark as the app shows it: "break" in deep indigo `#1C1778`, "out" in indigo `#4E46DC` | geometry from `source/breakout-logo-white.svg` (team Drive, `Breakout_logo 8.svg`), colours from the product screenshots |
| `logo-on-dark.svg` | "break" in white, "out" in lilac `#9A95FF` | the same |
| `mark.svg`, `mark-on-dark.svg` | The b-disc, indigo (the app's favicon) and white | the mark group of the same file |
| `fonts/fraunces-100-900*.woff2` | Fraunces, upright and italic, all axes: the open stand-in for the site's headline face, New Kansas | [Fraunces](https://github.com/undercasetype/Fraunces), SIL Open Font License (`fonts/OFL.txt`) |
| `fonts/manrope-200-800.woff2` | Manrope, the site's body face | [Manrope](https://github.com/sharanda/manrope), SIL Open Font License (`fonts/OFL.txt`) |
| `preview.png` | The kit on one sheet | `node tools/brand-from-url.mjs --preview --out brand` |

## What the homepage uses (from the saved getbreakout.ai HTML, 2026-10-05)

| Element | Site | In the film |
|---|---|---|
| Every headline (H1, H2s, agent card titles) | New Kansas (Adobe Fonts kit `jzj8tvx`), weight 400; emphasised words in *italic*. H1 "Pageview to *pipeline.*" 90px, tracking -0.05em, line height 0.95, near-white on the dark hero | `fonts.display`: New Kansas when installed, else Fraunces at 340 with `SOFT` 100; `key_style: italic` replaces the highlighter marker |
| Body, nav, buttons | Manrope 500, tracking -0.3px; Funnel Sans in the CMS sections | `fonts.body`: Manrope (taglines, chips, block labels) |
| Hero | Violet radial mesh, blurred: `#4c00ff` core, `#261678` and `#280961` lobes, on near-black, fading to white | `gradients.dark_mesh` on the hook and every dark card |
| Light sections | `#ffffff` and `#f4f4f4`, headings `#040405`, body `#5c5850` | `ground`, `ink`, `ink_secondary` |
| Accents | Violet pill `#421cff` → `#8a1dff` → `#be79ff`; demo chip `#613cf1` → `#68e6ff`; pastel agent cards (lavender, mint, sky) | `accent` `#4c00ff`, `accent_on_dark` `#be79ff`, all kept in `gradients` |

**New Kansas is a commercial Adobe Fonts face.** Adobe's licence covers video for subscribers, but the files cannot be bundled here. To render with it, activate New Kansas in Adobe Creative Cloud on the machine that renders; the film picks it up by name (`fonts.display.local`).

## Still to confirm (`"reviewed": false` until then)

- **Colours.** `accent` `#4e46dc` and `dark` `#1c1778` are the 2 wordmark colours, confirmed in the product screenshots. `ground` `#fdfdfd` is the app's background. Still to check against the homepage (blocked from the build container): its section colours, any gradient, and whether hero type is ink or deep indigo.
- **Font.** Confirm the headline face renders as New Kansas on the rendering machine (Fraunces otherwise), and which New Kansas weight the brand wants: the site forces 400 on the family it calls `new-kansas-thin`.
- **Copy.** It comes from the Brand Guide for Writers and the partner enablement guide. To pull the live site's headline and features, extract into a scratch folder so the logo here is not overwritten:

  ```bash
  node tools/brand-from-url.mjs https://getbreakout.ai --out /tmp/breakout-site
  ```

  Then copy only the values you want (`copy`, `screens/`, `images/`) into this folder.
