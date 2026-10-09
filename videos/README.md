# videos/

Your videos, one folder each. Make one from a template:

```bash
python3 scripts/new-video.py                        # list the templates
python3 scripts/new-video.py swiss-grid q4-launch   # -> videos/q4-launch/
```

The folder is a full copy of the template (its `TEMPLATE` file says which), so its README explains the data file to edit and how to render. Work in this order: `BRIEF.md` and `STORYBOARD.md` approved by the owner, then stills of every beat, then the free render (`./render.sh`), then paid upgrades if any. Renders and other build output stay out of git; share the finished MP4 directly.
