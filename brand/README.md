# brand/

The Breakout brand kit. `brand.json` is the only file the film reads.

| File | What | Source |
|---|---|---|
| `logo.svg` | Mark and wordmark in `#232323`, for light grounds | `source/breakout-logo-white.svg` (team Drive, `Breakout_logo 8.svg`), recoloured |
| `logo-on-dark.svg` | The same in white | as shipped in Drive |
| `mark.svg`, `mark-on-dark.svg` | The circle-b mark alone | the mark group of the same file |
| `fonts/inter-100-900.woff2` | Inter, variable weight, Latin | [Inter](https://github.com/rsms/inter), SIL Open Font License (`fonts/OFL.txt`) |
| `preview.png` | The kit on one sheet | `node tools/brand-from-url.mjs --preview --out brand` |

## Still to confirm (`"reviewed": false` until then)

- **Colours.** `accent` `#4e46dc` and the deep indigo behind `dark` come from the colour classes in the Drive logo files (`#4E46DC`, `#1C1778`). `ground` is a cool off-white picked to sit with the indigo. Check them against the live site or a brand guide.
- **Font.** Inter is a stand-in. If the site uses a different face, put its files in `fonts/` and update `fonts` in `brand.json`. Check the licence covers video.
- **Copy.** It comes from the Brand Guide for Writers and the partner enablement guide. To pull the live site's headline and features, extract into a scratch folder so the logo here is not overwritten:

  ```bash
  node tools/brand-from-url.mjs https://getbreakout.ai --out /tmp/breakout-site
  ```

  Then copy only the values you want (`copy`, `screens/`, `images/`) into this folder.
