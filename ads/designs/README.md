# Ad designs

The static ad designs, in the brand, for every LinkedIn size. The last three are pattern breaks (hook `pattern-break`): they should look like nothing else in the feed. One runtime (`ad.html`, `ad.css`, `designs.js`) draws any design at any size from a few fields; `ads/engine/render.mjs` sets the size and the fields and takes the picture. Colours come from `brand/brand.json`, fonts from `brand/fonts/`, product UI from `assets/screens/`.

![The designs in the example campaign's feed preview](../campaigns/pageview-to-pipeline/feed.jpg)

| Design | Looks like | Fields |
|---|---|---|
| `verdict` | A short claim in the display face, key words in italic violet; light ground with a soft bloom, or `"theme": "dark"` on the homepage mesh | `headline`, `kicker`, `sub`, `cta`, `theme`, `label`, `logo` |
| `slam` | The approved Swiss grid: hairlines, a mono index, lines in Manrope 800 that fill the width, one in violet | `lines` (wrap a line in `*` for violet), `index`, `kicker`, `sub` |
| `chat` | Breakout's website agent rebuilt from the real widget, answering a visitor | `headline`, `turns` (`{"who": "me" or "agent", "text"}`), `label` ("Illustrative example") |
| `split` | Today versus with Breakout: grey and violet panes, 2 to 4 words a side | `left`, `right`, `left_label`, `right_label`, `source` (shown while a quote is up) |
| `screen` | A real product screen, pushed in on the part that matters | `headline`, `image` (`assets/screens/...`), `crop` (`[x, y, w, h]` in image pixels) |
| `buttons` | A generic button-only chat widget (never a real vendor's UI or logo) beside Breakout's open question | `headline`, `buttons`, `greeting`, `miss`, `question`, `answer`, `label` |
| `form` | Pattern break: a lead form with every field struck through in violet | `headline`, `kicker`, `fields`, `submit`, `cta` |
| `notice` | Pattern break: one small Breakout notification in a lot of dark, empty space | `message`, `when`, `app`, `caption`, `label` ("Illustrative example") |
| `quiet` | Pattern break: a near-empty violet field and one small line | `line` |

Text fields take the brand's markup: `*pipeline.*` (or a lone `*` to the end of the line) sets italic violet, `\n` breaks a line. Each design reflows for square (1200x1200), wide (1200x627) and tall (1080x1350); type shrinks to fit. A document ad is a list of `pages`, each one of these designs, rendered to a PDF.

To add a design, add a function to `T` in `designs.js` and its styles to `ad.css`, render it at all 3 sizes, and log the look's verdict in [`docs/breakout-style.md`](../../docs/breakout-style.md).
