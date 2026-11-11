# Signals launch

A 40 s launch film for Signals, made from the [`dot-matrix`](../../templates/dot-matrix/README.md) template: why one pricing-page visit matters more than another, with the signals library's own art as the signals.

![Signals launch](poster.jpg)

| | |
|---|---|
| Story | [`BRIEF.md`](BRIEF.md), [`STORYBOARD.md`](STORYBOARD.md); words verbatim from the Signals launch email and getbreakout.ai/signals |
| Data | `film.json`: beats in bars (`at`), the questions and their motifs, captions, the library tiles (`library`, from `assets/refs/signals/`), the stream labels, the lockup |
| Look | `template.html`: the dot grid plus live particle motifs (`motif()`: funding, people, hiring, intent) |
| Sound | `score.py` (upbeat swing, cued from `at`), `audio.py` (cues, mix, mux) |
| Render | `./render.sh` -> `renders/signals-launch.mp4` |
