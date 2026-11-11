# Signals launch

A 29.5 s launch film for Signals, made from the [`swiss-grid`](../../templates/swiss-grid/README.md) template: the camera snaps onto a visitor's cursor on a pricing page and Breakout lists what just changed at her company under her name; then Breakout's website agent and the AI SDR email use it, each personalization token flashing as it lands.

![Signals launch](poster.jpg)

**Before sharing:** the visitor is Anthropic, by the owner's choice, with illustrative findings; see [`BRIEF.md`](BRIEF.md). Not for public posting as is.

| | |
|---|---|
| Story | [`BRIEF.md`](BRIEF.md), [`STORYBOARD.md`](STORYBOARD.md) |
| Data | `film.json`: every word and every time (`at`, in bars): headlines, the visitor (`visitor.logo` in `media/`), the pricing page, the five signals, the agent's widget and message and the email (`[key]phrase[/key]` marks a personalization token), the close |
| Look | `template.html`: the page, the cursor and its tag with the signals, the widget, the email and the camera (`shots()`); `draw(t)` sets every frame |
| Sound | `score.py` (upbeat swing), `audio.py` (cues from `at`, the mix, the mux) |
| Render | `./render.sh` -> `renders/signals-launch.mp4` |
