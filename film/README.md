# film/

The launch film template: a **hook** (the story before the cut) on a shared **body** (the Breakout logo on the music's drop, hero words cut on the voice, the product at close range, the logo lockup). Everything is drawn from `../brand/brand.json`.

| File | What it is |
|---|---|
| `film.json` | The body: the narrator's lines and the beats they play under. Full reference: [body.md](../skills/launch-film/references/body.md). |
| `hooks/<name>/hook.json` | One hook each. `attention` (dark, 2 lines) and `who-visited` (light, 1 question) are free, type-only hooks. Reference: [hooks.md](../skills/launch-film/references/hooks.md). |
| `assets/screens/` | Breakout product screenshots or screen recordings (png, jpg, mp4, webm). `accounts.png`, `account.png`, `chats.png` and `contacts.png` are real app screens with visitor names, emails, LinkedIn handles and visitor companies blurred. Never commit an unblurred screen. After swapping a screen, adjust its beat's `focus` rect. |
| `templates/body.html` | The look and motion. One HyperFrames composition; every beat is a pure function of time. |
| `build.py`, `audio.py`, `render.sh` | Timing from the aligned voice, the sound and mix, and both plus the render per hook. |

## Run it

From the repo root, with the venv from `requirements.txt`:

```bash
.venv/bin/python skills/launch-voice/scripts/scratch_voice.py film/film.json      # free placeholder narrator
.venv/bin/python skills/launch-voice/scripts/prep_lines.py film/film.json         # word times
.venv/bin/python skills/launch-score/scripts/scratch_bed.py film/score/bed.wav --bpm 120 --intro-bars 3
film/render.sh attention                                                           # -> film/renders/attention.mp4
```

No voice yet? `python3 film/build.py attention` still builds a silent animatic from the text, and `npx -y hyperframes@0.8.77 snapshot --at 5.5,8,12` (run inside `film/`) shows any second as a still.

GSAP is loaded from `node_modules` when `npm install` has run, so renders work offline; otherwise it falls back to the CDN.

Generated files (`compositions/`, `index-*.html`, `timing-*.json`, `renders/`, `mix/`, takes) are ignored by git and rebuilt on every run.
