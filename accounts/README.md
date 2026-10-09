# accounts/

Target accounts for the ABM templates ([`abm-cinematic`](../templates/abm-cinematic/README.md), [`abm-split`](../templates/abm-split/README.md)), one folder per account: `account.json` and the captures of their site and chat. `korn-ferry/` is the worked example.

| In `account.json` | What it is |
|---|---|
| `company`, `domain` | The account |
| `capture` | The homepage capture with the chat open: size, the widget box, each button as `[x, y, height]` in capture pixels |
| `tree` | For `abm-split`: each step of their chat as captured, its buttons, and which one the visitor clicks |
| `widget_notes` | What the capture shows ("4 buttons.", "No text box."). These are claims: check them against the capture |
| `question`, `answer`, `module` | The visitor's open question and Breakout's answer, in the account's own words from their site |
| `visitor`, `signals`, `email`, `booked` | The illustrative visitor story. Fictional people and companies only |

Captures are the account's public website, taken by the team. Then: `templates/abm-split/render.sh <slug>` (or a copy in `videos/`).
