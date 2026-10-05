# brand/

The Breakout brand kit. `brand.json` is the only file the film reads.

| File | What | Source |
|---|---|---|
| `logo.svg` | The wordmark as the app shows it: "break" in deep indigo `#1C1778`, "out" in indigo `#4E46DC` | geometry from `source/breakout-logo-white.svg` (team Drive, `Breakout_logo 8.svg`), colours from the product screenshots |
| `logo-on-dark.svg` | "break" in white, "out" in lilac `#9A95FF` | the same |
| `mark.svg`, `mark-on-dark.svg` | The b-disc, indigo (the app's favicon) and white | the mark group of the same file |
| `fonts/inter-100-900.woff2` | Inter, variable weight, Latin | [Inter](https://github.com/rsms/inter), SIL Open Font License (`fonts/OFL.txt`) |
| `preview.png` | The kit on one sheet | `node tools/brand-from-url.mjs --preview --out brand` |

## Still to confirm (`"reviewed": false` until then)

- **Colours.** `accent` `#4e46dc` and `dark` `#1c1778` are the 2 wordmark colours, confirmed in the product screenshots. `ground` `#fdfdfd` is the app's background. Still to check against the homepage (blocked from the build container): its section colours, any gradient, and whether hero type is ink or deep indigo.
- **Font.** Inter is a stand-in. If the site uses a different face, put its files in `fonts/` and update `fonts` in `brand.json`. Check the licence covers video.
- **Copy.** It comes from the Brand Guide for Writers and the partner enablement guide. To pull the live site's headline and features, extract into a scratch folder so the logo here is not overwritten:

  ```bash
  node tools/brand-from-url.mjs https://getbreakout.ai --out /tmp/breakout-site
  ```

  Then copy only the values you want (`copy`, `screens/`, `images/`) into this folder.
