#!/usr/bin/env python3
"""Breakout's ads engine: campaign idea -> tagged creatives -> LinkedIn -> scores -> learnings -> the next round.

  python3 ads/engine/ads.py new <campaign> --code P2P --idea "..."   scaffold ads/campaigns/<campaign>/
  python3 ads/engine/ads.py lint <campaign>                          brand, claims, LinkedIn limits, tags, diversity
  python3 ads/engine/ads.py render <campaign> [--ids P2P-001 ...]    creatives + a feed preview contact sheet
  python3 ads/engine/ads.py sheet <campaign>                         out/sheet.png: every creative on one page, by round
  python3 ads/engine/ads.py export <campaign> [--all]                launch/ads.csv and launch/plan.json (approved ads)
  python3 ads/engine/ads.py kit <campaign> [--all]                   launch/kit.html: build the round in Campaign Manager by hand
  python3 ads/engine/ads.py launch <campaign> [--live]               create DRAFT campaigns and PAUSED ads on LinkedIn (needs the API)
  python3 ads/engine/ads.py verify <campaign> [--round N]           read Campaign Manager (API) and check it against the kit
  python3 ads/engine/ads.py sync <campaign> --round N [--live]       add a round's approved ads to the live campaigns, PAUSED
  python3 ads/engine/ads.py status <campaign> <ids> --pause|--activate|--archive [--live]   change ads' status (activate only on the owner's yes)
  python3 ads/engine/ads.py audience resolve <facet> <query> [--live]   look up targeting URNs (titles, industries, skills)
  python3 ads/engine/ads.py ingest linkedin <export.csv>             Campaign Manager ad performance export
  python3 ads/engine/ads.py ingest crm <export.csv>                  server-side outcomes by utm_content (meetings, SQLs, pipeline)
  python3 ads/engine/ads.py ingest api --since YYYY-MM-DD [--live]   daily creative metrics from the API
  python3 ads/engine/ads.py score                                    the Banger Score leaderboard -> ads/LEADERBOARD.md
  python3 ads/engine/ads.py learn [--note "..."]                     what wins by tag -> ads/LEARNINGS.md
  python3 ads/engine/ads.py iterate <campaign> <ad_id> [--n 10]      new execution stubs around a winner
  python3 ads/engine/ads.py budget <campaign> --daily 300            test versus scale split, as a recommendation

Standard library only (the renderer needs node and puppeteer: `npm install`). Nothing here spends money or
publishes anything: launch is a dry run unless --live, and live creates everything paused.
"""
import argparse
import csv
import datetime as dt
import difflib
import json
import re
import subprocess
import sys
import urllib.parse
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ADS = HERE.parent
ROOT = ADS.parent
sys.path.insert(0, str(HERE))
import linkedin  # noqa: E402

CAMPAIGNS = ADS / "campaigns"
DATA = ADS / "data"
PERF = DATA / "performance.csv"
CRM = DATA / "crm.csv"
ID_RE = re.compile(r"\b([A-Z][A-Z0-9]{1,7}-\d{3})\b")
PERF_COLS = ["ad_id", "date", "impressions", "clicks", "spend", "video_views", "video_starts", "video_q25",
             "video_q50", "video_completions", "platform_conversions", "leads"]
CRM_COLS = ["ad_id", "date", "meetings", "trials", "sqls", "pipeline"]
LIMITS = {"intro_fold": 150, "intro_soft": 600, "intro_max": 3000, "headline_soft": 70, "headline_max": 200,
          "description_soft": 100, "description_max": 300}


def jload(p):
    return json.loads(Path(p).read_text())


def jsave(p, obj):
    Path(p).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


TAX = jload(ADS / "taxonomy.json")
SCORING = jload(ADS / "scoring.json")
AUD = jload(ADS / "audiences.json")
BRAND = jload(ROOT / "brand" / "brand.json")


def campaign_dir(slug):
    d = CAMPAIGNS / slug
    if not (d / "campaign.json").exists():
        sys.exit(f"no campaign {slug!r} (ads/campaigns/{slug}/campaign.json)")
    return d


def load(slug):
    return jload(campaign_dir(slug) / "campaign.json")


def save(slug, camp):
    jsave(CAMPAIGNS / slug / "campaign.json", camp)


def all_ads():
    """Every ad in every campaign, keyed by id, with its campaign slug."""
    out = {}
    for p in sorted(CAMPAIGNS.glob("*/campaign.json")):
        camp = jload(p)
        for ad in camp.get("ads", []):
            out[ad["id"]] = {**ad, "campaign": p.parent.name, "code": camp["code"]}
    return out


def in_round(ad, rnd):
    """--round N keeps the ads planned for round N plus those marked "always" (an offer that runs every round); no --round keeps them all."""
    return rnd is None or ad.get("round") in (rnd, "always")


def ad_name(ad):
    """The name LinkedIn shows: the id first (the join key), then every tag."""
    return f"{ad['id']} | {ad['concept']} {ad['angle']} | {ad['persona']} | {ad['awareness']} | {ad['format']} | {ad['hook']}"


def landing_url(camp, ad):
    base = ad.get("url") or camp["landing_url"]
    utm = {"utm_source": "linkedin", "utm_medium": "paid_social", "utm_campaign": camp["code"].lower(),
           "utm_content": ad["id"], "utm_term": ad["persona"]}
    sep = "&" if urllib.parse.urlsplit(base).query else "?"
    return base + sep + urllib.parse.urlencode(utm)


def fmt(ad):
    return TAX["formats"].get(ad.get("format"), {})


def creative_file(slug, ad):
    kind = fmt(ad).get("kind")
    ext = {"image": "png", "document": "pdf"}.get(kind)
    if ad.get("asset"):
        return ROOT / ad["asset"]
    return CAMPAIGNS / slug / "out" / f"{ad['id']}.{ext}" if ext else None


# ------------------------------------------------------------------ new

def cmd_new(a):
    d = CAMPAIGNS / a.campaign
    if d.exists():
        sys.exit(f"ads/campaigns/{a.campaign} already exists")
    if not re.fullmatch(r"[A-Z][A-Z0-9]{1,7}", a.code):
        sys.exit("--code is 2 to 8 capitals or digits, starting with a letter, e.g. P2P")
    used = {jload(p)["code"] for p in CAMPAIGNS.glob("*/campaign.json")}
    if a.code in used:
        sys.exit(f"code {a.code} is taken; codes are never reused")
    d.mkdir(parents=True)
    camp = {
        "campaign": a.campaign, "code": a.code, "status": "draft", "platform": "linkedin",
        "idea": a.idea or "", "objective": "WEBSITE_VISIT", "landing_url": BRAND["url"], "cta": "REQUEST_DEMO",
        "abm": False,
        "budget": {"daily_usd": None, "test_share": SCORING["budget"]["test_share"]},
        "personas": [], "concepts": [], "ads": [],
    }
    save(a.campaign, camp)
    (d / "BRIEF.md").write_text(BRIEF_TEMPLATE.format(name=a.campaign, code=a.code, idea=a.idea or "<the campaign idea in one sentence>"))
    print(f"ads/campaigns/{a.campaign}/: campaign.json and BRIEF.md. Write the brief and the concept matrix with the owner first (skills/ads-engine/SKILL.md).")


BRIEF_TEMPLATE = """# {name} ({code})

## Idea
{idea}

## Who buys
Which personas (ads/taxonomy.json), and can one person buy alone? If yes, write for that one person, not a committee.

## The one thing they should feel
One sentence.

## Concepts (genuinely different ideas, 3 to 6)
| Code | Concept | Why it might win | Source line in brand.json copy |
|---|---|---|---|

## What we already know
Rules from ads/LEARNINGS.md that apply here.

## Offer and landing page
CTA, URL, what happens after the click. Unknown facts stay unknown: ask.

## Budget
Daily total, test share (15 to 25%), how long the test runs.

## Approval
- [ ] Brief and concept matrix approved by the owner
- [ ] Feed preview (out/feed.png) approved; approved ads set to "status": "approved"
- [ ] Spend approved
"""


# ------------------------------------------------------------------ lint

def approved_text():
    """Every string the brand has said publicly, plus approved claims: the sources a number may come from."""
    texts = []

    def walk(x):
        if isinstance(x, str):
            texts.append(x)
        elif isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(BRAND.get("copy", {}))
    claims = ADS / "claims.json"
    if claims.exists():
        walk([c["text"] for c in jload(claims).get("claims", [])])
    return texts


def ad_texts(ad):
    """(where, text) for every word a viewer sees."""
    out = []
    for k, v in (ad.get("copy") or {}).items():
        if isinstance(v, str) and k != "cta":
            out.append((f"copy.{k}", v))

    def walk(prefix, x):
        if isinstance(x, str):
            if not prefix.endswith((".template", ".image", ".theme", ".index", ".logo")) and ".crop" not in prefix:
                out.append((prefix, x))
        elif isinstance(x, dict):
            for k, v in x.items():
                walk(f"{prefix}.{k}", v)
        elif isinstance(x, list):
            for i, v in enumerate(x):
                walk(f"{prefix}[{i}]", v)
    walk("design", ad.get("design") or {})
    for k, v in (ad.get("script") or {}).items():   # only what a viewer sees or hears, not production notes
        if k.startswith(("hook", "hold", "product", "cta", "body", "beats", "on_screen", "line")):
            walk(f"script.{k}", v)
    return out


def norm(t):
    t = t.replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"').replace("*", "")
    return re.sub(r"\s+", " ", t).strip().rstrip(".").lower()


def verbatim(line):
    """A line naming a competitor must sit word for word inside a competitive claim (ads/claims.json)."""
    claims = ADS / "claims.json"
    if not claims.exists():
        return False
    texts = [norm(c["text"]) for c in jload(claims).get("claims", []) if c.get("competitive")]
    return any(norm(line) in t for t in texts)


def lint_campaign(slug, camp, quiet=False):
    errs, warns = [], []
    concepts = {c["code"]: c for c in camp.get("concepts", [])}
    sources = {n.rstrip(".,") for t in approved_text() for n in re.findall(r"\d[\d,.]*\+?%?(?:[xX]\b)?", t)}
    comp = [c for c in TAX["competitors"]]
    ids = set()
    if camp.get("cta") not in linkedin.CTAS:
        errs.append(f"campaign cta {camp.get('cta')!r} is not a LinkedIn CTA ({', '.join(sorted(linkedin.CTAS))})")
    if camp.get("objective") not in linkedin.OBJECTIVES:
        errs.append(f"campaign objective {camp.get('objective')!r} is not one of {sorted(linkedin.OBJECTIVES)}")
    for ad in camp.get("ads", []):
        i = ad.get("id", "?")
        E = lambda m: errs.append(f"{i}: {m}")  # noqa: E731
        Wn = lambda m: warns.append(f"{i}: {m}")  # noqa: E731
        if not re.fullmatch(rf"{camp['code']}-\d{{3}}", i):
            E(f"id must be {camp['code']}-NNN")
        if i in ids:
            E("duplicate id")
        ids.add(i)
        if ad.get("status") == "retired":
            continue
        # tags: all 5 dimensions plus hook, from the taxonomy
        if ad.get("concept") not in concepts:
            E(f"concept {ad.get('concept')!r} is not in this campaign's concepts")
        for dim, vocab in (("angle", "angles"), ("persona", "personas"), ("awareness", "awareness"), ("format", "formats"), ("hook", "hooks")):
            if ad.get(dim) not in TAX[vocab]:
                E(f"{dim} {ad.get(dim)!r} is not in ads/taxonomy.json {vocab}")
        if camp.get("personas") and ad.get("persona") not in camp["personas"]:
            E(f"persona {ad.get('persona')!r} is not one of the campaign's personas")
        c = ad.get("copy") or {}
        kind = fmt(ad).get("kind")
        # LinkedIn limits
        intro, head, desc = c.get("intro", ""), c.get("headline", ""), c.get("description", "")
        if kind in ("image", "document", "video") and not intro:
            E("copy.intro is empty")
        if kind in ("image", "document", "video") and not head:
            E("copy.headline is empty")
        if len(intro) > LIMITS["intro_max"]:
            E(f"intro is {len(intro)} chars; LinkedIn's max is 3000")
        elif len(intro) > LIMITS["intro_soft"]:
            Wn(f"intro is {len(intro)} chars; keep it under 600")
        first = intro.split("\n")[0]
        if len(first) > LIMITS["intro_fold"]:
            Wn(f"the first line is {len(first)} chars; only about 150 show before '...see more'. Land the hook first")
        if len(head) > LIMITS["headline_max"]:
            E(f"headline is {len(head)} chars (max 200)")
        elif len(head) > LIMITS["headline_soft"]:
            Wn(f"headline is {len(head)} chars; it truncates after about 70")
        if len(desc) > LIMITS["description_max"]:
            E(f"description is {len(desc)} chars (max 300)")
        elif len(desc) > LIMITS["description_soft"]:
            Wn(f"description is {len(desc)} chars; keep it under 100")
        cta = c.get("cta") or camp.get("cta")
        if cta not in linkedin.CTAS:
            E(f"cta {cta!r} is not a LinkedIn CTA")
        # words: brand, competitors, claims
        for where, text in ad_texts(ad):
            if "TODO" in text:
                E(f"{where} still says TODO")
            if "\u2014" in text:
                E(f"{where} has an em dash; the brand uses commas, colons and full stops")
            for name in comp:
                if re.search(rf"(?<![\w-]){re.escape(name)}(?![\w-])", text):
                    if camp.get("abm") and name == "Qualified":
                        bad = [ln for ln in text.split("\n") if "Qualified" in ln and not verbatim(ln)]
                        if bad:
                            E(f"{where} names Qualified outside a verbatim line from the compare page (ads/claims.json): {bad[0]!r}")
                    else:
                        E(f"{where} names a competitor ({name}); never in a Breakout ad")
            for word in TAX["fluff"]:
                if re.search(rf"\b{re.escape(word)}\b", text, re.I):
                    Wn(f"{where}: {word!r} is fluff; say the concrete thing")
            for num in re.findall(r"\d[\d,.]*\+?%?(?:[xX]\b)?", text):
                core = num.rstrip(".,")
                if core not in sources and core.rstrip("+%") not in {x.rstrip("+%") for x in sources}:
                    E(f"{where}: the number {core!r} has no source (brand.json copy or ads/claims.json). Never invent a number")
        # design
        des = ad.get("design") or {}
        if kind == "image" and not des.get("template") and not ad.get("asset"):
            E("an image ad needs design.template or an asset")
        if kind == "document" and not (des.get("pages") or ad.get("asset")):
            E("a document ad needs design.pages (3 to 6) or an asset")
        if kind == "document" and des.get("pages") and not 2 <= len(des["pages"]) <= 10:
            Wn(f"{len(des['pages'])} pages; 3 to 6 swipe best")
        if kind in ("video", "post") and not (ad.get("asset") or ad.get("script")):
            E("a video or thought-leader ad needs a script (the engine writes it) or an asset")
        if des.get("template") == "chat" and not (des.get("fields") or {}).get("label"):
            Wn("a chat ad shows a sample conversation; add label: \"Illustrative example\"")
        for p in [des] + list(des.get("pages") or []):
            img = (p.get("fields") or {}).get("image")
            if img and not (ROOT / img).exists():
                E(f"image {img} does not exist")
            if img and not img.startswith("assets/screens/"):
                Wn(f"image {img} is not in assets/screens/; product screens must be real, with customer data blurred")
            words = len(re.sub(r"[*\n]", " ", (p.get("fields") or {}).get("headline", "")).split())
            if words > 12:
                Wn(f"the on-image headline is {words} words; little text, held long enough to read")
        if ad.get("ends") and ad["ends"] < dt.date.today().isoformat() and ad.get("status") not in ("retired", "paused"):
            Wn(f"its offer ended on {ad['ends']}: pause it in Campaign Manager and set \"status\": \"retired\"")
        if ad.get("asset") and not (ROOT / ad["asset"]).exists():
            E(f"asset {ad['asset']} does not exist")
        if ad.get("parent") and ad["parent"] not in ids and ad["parent"] not in all_ads():
            Wn(f"parent {ad['parent']} not found")
    # diversity: different concepts, not colour swaps of one ad
    live = [a for a in camp.get("ads", []) if a.get("status") != "retired"]
    used = {a.get("concept") for a in live}
    if live and len(used) < min(3, len(concepts)):
        warns.append(f"only {len(used)} concept(s) in play; test genuinely different concepts (3 or more)")
    groups = defaultdict(list)
    for a in live:
        groups[(a.get("concept"), a.get("angle"), a.get("persona"), a.get("format"), a.get("hook"))].append(a)
    for key, group in groups.items():
        for x in range(len(group)):
            for y in range(x + 1, len(group)):
                ta = (group[x].get("copy") or {}).get("headline", "") + json.dumps((group[x].get("design") or {}).get("fields", {}))
                tb = (group[y].get("copy") or {}).get("headline", "") + json.dumps((group[y].get("design") or {}).get("fields", {}))
                if difflib.SequenceMatcher(None, ta, tb).ratio() > 0.8:
                    warns.append(f"{group[x]['id']} and {group[y]['id']} are near copies with the same tags; a tiny variation teaches nothing")
    if not quiet:
        for e in errs:
            print(f"error  {e}")
        for w in warns:
            print(f"warn   {w}")
        n = len(camp.get("ads", []))
        print(f"{slug}: {n} ads, {len(errs)} errors, {len(warns)} warnings" + ("" if BRAND.get("reviewed") else " (brand.json is not reviewed: every ad is a draft)"))
    return errs, warns


def cmd_lint(a):
    errs, _ = lint_campaign(a.campaign, load(a.campaign))
    sys.exit(1 if errs else 0)


# ------------------------------------------------------------------ render

def cmd_render(a):
    camp = load(a.campaign)
    d = CAMPAIGNS / a.campaign
    errs, _ = lint_campaign(a.campaign, camp, quiet=True)
    blocking = [e for e in errs if "TODO" not in e]
    if blocking and not a.force:
        print("\n".join(f"error  {e}" for e in blocking))
        sys.exit("fix the lint errors first (or --force to preview anyway)")
    jobs = []
    for ad in camp["ads"]:
        if (a.ids and ad["id"] not in a.ids) or not in_round(ad, a.round):
            continue
        if ad.get("status") == "retired" or ad.get("asset"):
            continue
        f = fmt(ad)
        des = ad.get("design") or {}
        if f.get("kind") == "image" and des.get("template"):
            jobs.append({"out": str(d / "out" / f"{ad['id']}.png"), "template": des["template"], "size": f["size"], "fields": des.get("fields", {})})
        elif f.get("kind") == "document" and des.get("pages"):
            jobs.append({"out": str(d / "out" / f"{ad['id']}.pdf"), "size": f["size"], "pages": des["pages"]})
    (d / "out").mkdir(exist_ok=True)
    jobs_file = d / "out" / "jobs.json"
    jsave(jobs_file, jobs)
    r = subprocess.run(["node", str(HERE / "render.mjs"), str(jobs_file)], cwd=ROOT)
    feed = write_feed(a.campaign, camp, a.round)
    jsave(jobs_file, [{"out": str(d / "out" / "feed.png"), "url": feed.as_uri(), "size": [1500, 1000], "full_page": True}])
    subprocess.run(["node", str(HERE / "render.mjs"), str(jobs_file)], cwd=ROOT)
    jobs_file.unlink()
    print(f"feed preview: ads/campaigns/{a.campaign}/out/feed.png")
    sys.exit(r.returncode)


def esc(s):
    return (str(s or "")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def write_feed(slug, camp, rnd=None):
    """A contact sheet: every ad as it reads in a feed, with its tags, for the owner to approve."""
    d = CAMPAIGNS / slug / "out"
    cards = []
    for ad in camp["ads"]:
        if ad.get("status") == "retired" or not in_round(ad, rnd):
            continue
        c = ad.get("copy") or {}
        intro = c.get("intro", "")
        shown = esc(intro if len(intro) <= LIMITS["intro_fold"] else intro[:LIMITS["intro_fold"]].rsplit(" ", 1)[0] + "…")
        more = '<span class="more">...see more</span>' if len(intro) > LIMITS["intro_fold"] else ""
        kind = fmt(ad).get("kind")
        png = d / f"{ad['id']}.png"
        page1 = d / f"{ad['id']}-p1.png"
        if kind == "image" and png.exists():
            media = f'<img src="{png.name}">'
        elif kind == "document" and page1.exists():
            n = len((ad.get("design") or {}).get("pages", []))
            media = f'<div class="doc"><img src="{page1.name}"><span>1 / {n}</span></div>'
        else:
            s = ad.get("script") or {}
            media = '<div class="script"><b>' + esc(fmt(ad).get("note", kind)) + "</b><br><br>" + "<br>".join(
                f"<i>{esc(k)}</i> {esc(v if isinstance(v, str) else json.dumps(v))}" for k, v in s.items()) + "</div>"
        tags = " ".join(f"<span>{esc(ad.get(k))}</span>" for k in ("concept", "angle", "persona", "awareness", "format", "hook"))
        status = esc(ad.get("status", "draft"))
        cards.append(f"""<div class="card"><div class="id">{esc(ad['id'])} <em class="st {status}">{status}</em>{' from ' + esc(ad['parent']) if ad.get('parent') else ''}</div>
<div class="post"><div class="who"><img src="../../../../brand/mark.svg"><div><b>Breakout</b><br><small>Promoted</small></div></div>
<p class="intro">{shown.replace(chr(10), '<br>')} {more}</p>{media}
<div class="bar"><div><b>{esc(c.get('headline'))}</b><br><small>{esc(c.get('description') or BRAND['domain'])}</small></div><span class="cta">{esc((c.get('cta') or camp['cta']).replace('_', ' ').title())}</span></div></div>
<div class="tags">{tags}</div></div>""")
    html = f"""<!doctype html><meta charset="utf-8"><title>{esc(slug)} feed preview</title>
<style>
@font-face {{ font-family: Manrope; src: url("../../../../brand/fonts/manrope-200-800.woff2"); font-weight: 200 800; }}
body {{ margin: 0; padding: 32px; background: #ebe9f2; font: 14px/1.4 Manrope, sans-serif; color: #111; }}
h1 {{ font-size: 22px; margin: 0 0 4px; }} .lede {{ color: #5c5850; margin: 0 0 24px; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, 440px); gap: 24px; }}
.card {{ width: 440px; }} .id {{ font: 12px monospace; margin-bottom: 6px; }}
.st {{ font-style: normal; padding: 1px 6px; border-radius: 4px; background: #ddd; }} .st.approved {{ background: #c9f0d9; }} .st.stub {{ background: #ffe1a8; }}
.post {{ background: #fff; border-radius: 10px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,.12); }}
.who {{ display: flex; gap: 8px; align-items: center; padding: 12px; }} .who img {{ width: 40px; height: 40px; }} small {{ color: #666; }}
.intro {{ margin: 0; padding: 0 12px 10px; }} .more {{ color: #666; }}
.post > img, .doc img {{ width: 100%; display: block; }} .doc {{ position: relative; }} .doc span {{ position: absolute; right: 8px; top: 8px; background: rgba(0,0,0,.6); color: #fff; padding: 2px 8px; border-radius: 10px; font-size: 12px; }}
.script {{ background: #f6f1ff; padding: 16px; min-height: 200px; font-size: 13px; }}
.bar {{ display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 10px 12px; background: #f3f2ef; }}
.cta {{ border: 1px solid #0a66c2; color: #0a66c2; border-radius: 16px; padding: 4px 14px; font-weight: 700; white-space: nowrap; }}
.tags span {{ display: inline-block; font: 11px monospace; background: #fff; border-radius: 4px; padding: 1px 5px; margin: 6px 4px 0 0; }}
</style>
<h1>{esc(slug)} ({esc(camp['code'])}): feed preview</h1><p class="lede">{esc(camp.get('idea'))}{'' if BRAND.get('reviewed') else ' Draft: brand.json is not reviewed yet.'} A neutral mock of a feed, not LinkedIn's UI.</p>
<div class="grid">{''.join(cards)}</div>"""
    out = d / "feed.html"
    out.write_text(html)
    return out


def cmd_sheet(a):
    """A compact contact sheet of every rendered creative, grouped by round, for reviewing a big set at once."""
    camp = load(a.campaign)
    d = CAMPAIGNS / a.campaign / "out"
    groups = defaultdict(list)
    for ad in camp["ads"]:
        if ad.get("status") == "retired":
            continue
        groups[str(ad.get("round", "-"))].append(ad)
    order = sorted(groups, key=lambda r: (r != "always", r))
    html = [f"""<!doctype html><meta charset="utf-8"><style>
@font-face {{ font-family: Manrope; src: url("../../../../brand/fonts/manrope-200-800.woff2"); font-weight: 200 800; }}
body {{ margin: 0; padding: 28px; background: #ebe9f2; font: 13px/1.35 Manrope, sans-serif; color: #111; }}
h1 {{ font-size: 22px; margin: 0 0 4px; }} h2 {{ font-size: 15px; margin: 22px 0 10px; }} p {{ margin: 0; color: #5c5850; }}
.g {{ display: grid; grid-template-columns: repeat(6, 1fr); gap: 14px; }}
.c img {{ width: 100%; display: block; border-radius: 6px; background: #fff; }}
.c .t {{ font: 11px ui-monospace, monospace; margin-top: 5px; }} .c .t b {{ font-family: Manrope; }}
.ph {{ aspect-ratio: 1; background: #f6f1ff; border-radius: 6px; display: grid; place-items: center; color: #5c5850; padding: 10px; text-align: center; }}
</style><h1>{esc(a.campaign)} ({esc(camp['code'])}): every creative</h1><p>{esc(camp.get('idea'))}</p>"""]
    for r in order:
        title = "Every round (the offer)" if r == "always" else f"Round {r}"
        html.append(f"<h2>{title}</h2><div class='g'>")
        for ad in sorted(groups[r], key=lambda x: (x["persona"], x["id"])):
            img = d / f"{ad['id']}.png"
            p1 = d / f"{ad['id']}-p1.png"
            src = img if img.exists() else p1 if p1.exists() else None
            media = f"<img src='{src.name}'>" if src else f"<div class='ph'>{esc(fmt(ad).get('note', ad['format']))}</div>"
            html.append(f"<div class='c'>{media}<div class='t'><b>{esc(ad['id'])}</b> {esc(ad['concept'])} · {esc(ad['persona'])} · {esc(ad['awareness'])}{' · ends ' + esc(ad['ends']) if ad.get('ends') else ''}</div></div>")
        html.append("</div>")
    page = d / "sheet.html"
    page.write_text("".join(html))
    jobs = d / "jobs.json"
    jsave(jobs, [{"out": str(d / "sheet.png"), "url": page.as_uri(), "size": [1800, 1000], "full_page": True}])
    subprocess.run(["node", str(HERE / "render.mjs"), str(jobs)], cwd=ROOT)
    jobs.unlink()
    print(f"ads/campaigns/{a.campaign}/out/sheet.png")


# ------------------------------------------------------------------ export and launch

def plan(slug, camp, include_all=False, rnd=None):
    """Campaign Manager structure: a test group with 1 campaign per persona and ad format (LinkedIn sets the
    format on the campaign), and a scale group for winners later."""
    ads = [a for a in camp["ads"] if in_round(a, rnd) and (a.get("status") == "approved" or (include_all and a.get("status") != "retired"))]
    if not ads:
        sys.exit("no approved ads: set \"status\": \"approved\" on the ads the owner approved (or --all to preview)")
    budget = camp.get("budget") or {}
    daily = budget.get("daily_usd")
    share = budget.get("test_share", SCORING["budget"]["test_share"])
    fixed = budget.get("campaigns") or {}          # {"demand-gen": 50, ...}: the owner's split for this round
    minimum = SCORING["budget"]["linkedin_min_daily_per_campaign"]
    keys = sorted({(a["persona"], fmt(a).get("kind")) for a in ads}, key=lambda k: (k[0], ["image", "document", "video", "post"].index(k[1])))
    personas = sorted({p for p, _ in keys})
    campaigns = []
    for p, kind in keys:
        mine = [a for a in ads if a["persona"] == p and fmt(a).get("kind") == kind]
        kinds_here = sum(1 for q, _ in keys if q == p)
        if p in fixed:
            usd = fixed[p] / kinds_here
        elif daily:
            usd = daily * share / len(personas) / kinds_here
        else:
            usd = None
        campaigns.append({
            "name": f"{camp['code']} | test | {p} | {kind}", "group": "test", "persona": p, "kind": kind,
            "daily_usd": round(max(usd, minimum), 2) if usd else None,
            "targeting": linkedin.targeting({**AUD["shared"], "company_size": [] if "company_size" in (camp.get("audience") or {}).get("replaces", []) else AUD["shared"].get("company_size")}, AUD["personas"][p]),
            "targeting_labels": {k: v for k, v in AUD["personas"][p].items() if k.endswith("_label")},
            "ads": [a["id"] for a in mine],
        })
        if len(mine) > SCORING["budget"]["max_active_ads_per_campaign"]:
            print(f"warn   {p} {kind}: {len(mine)} ads in one campaign; LinkedIn favours 1 or 2 early, so launch at most "
                  f"{SCORING['budget']['max_active_ads_per_campaign']} at a time (1 per concept) and rotate the rest in")
    creatives = []
    for a in ads:
        c = a.get("copy") or {}
        f = creative_file(slug, a)
        creatives.append({"ad_id": a["id"], "name": ad_name(a), "kind": fmt(a).get("kind"), "format": a["format"],
                          "intro": c.get("intro", ""), "headline": c.get("headline", ""), "description": c.get("description", ""),
                          "cta": c.get("cta") or camp["cta"], "url": landing_url(camp, a),
                          "file": str(f.relative_to(ROOT)) if f else None, "script": a.get("script"), "ends": a.get("ends")})
    return {"campaign": slug, "code": camp["code"], "objective": camp["objective"], "daily_usd": daily,
            "groups": [f"{camp['code']} | test", f"{camp['code']} | scale"], "campaigns": campaigns, "creatives": creatives}


def cmd_export(a):
    camp = load(a.campaign)
    errs, _ = lint_campaign(a.campaign, camp, quiet=True)
    if errs:
        print("\n".join(f"error  {e}" for e in errs))
        sys.exit("lint errors: nothing exported")
    p = plan(a.campaign, camp, a.all, a.round)
    d = CAMPAIGNS / a.campaign / "launch"
    d.mkdir(exist_ok=True)
    jsave(d / "plan.json", p)
    tags = {x["id"]: x for x in camp["ads"]}
    with open(d / "ads.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["ad_id", "linkedin_campaign", "ad_name", "format", "intro_text", "headline", "description", "cta",
                    "destination_url", "creative_file", "concept", "angle", "persona", "awareness", "hook"])
        for c in p["creatives"]:
            t = tags[c["ad_id"]]
            lc = next(x["name"] for x in p["campaigns"] if c["ad_id"] in x["ads"])
            w.writerow([c["ad_id"], lc, c["name"], t["format"], c["intro"], c["headline"], c["description"], c["cta"],
                        c["url"], c["file"] or "", t["concept"], t["angle"], t["persona"], t["awareness"], t["hook"]])
    missing = [c["ad_id"] for c in p["creatives"] if c["file"] and not (ROOT / c["file"]).exists()]
    print(f"ads/campaigns/{a.campaign}/launch/ads.csv and plan.json: {len(p['campaigns'])} campaigns, {len(p['creatives'])} ads")
    if missing:
        print(f"warn   not rendered yet: {', '.join(missing)} (run render)")


def cmd_kit(a):
    import os
    import kit
    camp = load(a.campaign)
    errs, _ = lint_campaign(a.campaign, camp, quiet=True)
    if errs:
        print("\n".join(f"error  {e}" for e in errs))
        sys.exit("lint errors: no kit")
    p = plan(a.campaign, camp, a.all, a.round)
    d = CAMPAIGNS / a.campaign / "launch"
    d.mkdir(exist_ok=True)
    name = f"kit-round{a.round}.html" if a.round else "kit.html"
    page = kit.build(a.campaign, camp, p, AUD, BRAND.get("reviewed"), lambda f: os.path.relpath(ROOT / f, d))
    (d / name).write_text(page)
    # The same sheet as a publishable page (images under img/, files named rather than linked) and a zip of the files.
    import zipfile
    pub = d / name.replace(".html", "-page.html")
    pub.write_text(kit.build(a.campaign, camp, p, AUD, BRAND.get("reviewed"), lambda f: "img/" + Path(f).name, artifact=True))
    with zipfile.ZipFile(d / name.replace(".html", ".zip"), "w", zipfile.ZIP_DEFLATED) as z:
        for c in p["creatives"]:
            if c["file"] and (ROOT / c["file"]).exists():
                z.write(ROOT / c["file"], f"creatives/{Path(c['file']).name}")
        for f in sorted(DATA.glob(f"{camp['code'].lower()}-linkedin-*.csv")):
            z.write(f, f"audiences/{f.name}")
    missing = [c["ad_id"] for c in p["creatives"] if c["file"] and not (ROOT / c["file"]).exists()]
    print(f"ads/campaigns/{a.campaign}/launch/{name}: {len(p['campaigns'])} campaigns, {len(p['creatives'])} ads"
          + (f"; not rendered yet: {', '.join(missing)}" if missing else ""))


def cmd_launch(a):
    import os
    camp = load(a.campaign)
    d = CAMPAIGNS / a.campaign / "launch"
    if not (d / "plan.json").exists():
        sys.exit("run export first")
    p = jload(d / "plan.json")
    account = os.environ.get("LINKEDIN_AD_ACCOUNT") or a.account
    org = os.environ.get("LINKEDIN_ORG") or a.org
    if not account or not org:
        sys.exit("set LINKEDIN_AD_ACCOUNT and LINKEDIN_ORG (the numeric ad account and company page ids)")
    if a.live and not BRAND.get("reviewed"):
        sys.exit("brand/brand.json says reviewed: false; every ad is a draft. Review the brand kit before a live launch")
    if a.live and any(c["daily_usd"] is None for c in p["campaigns"]):
        sys.exit("set budget.daily_usd in campaign.json and re-export before a live launch")
    log = []
    cl = linkedin.Client(live=a.live, log=log)
    print(("LIVE" if a.live else "DRY RUN") + f": {len(p['campaigns'])} campaigns (DRAFT), {len(p['creatives'])} ads (PAUSED)")
    launched = {"when": dt.datetime.now().isoformat(timespec="seconds"), "live": a.live, "account": account, "ads": {}}
    gid = cl.campaign_group(account, p["groups"][0])
    by_id = {c["ad_id"]: c for c in p["creatives"]}
    for c in p["campaigns"]:
        cid = cl.campaign(account, gid, c["name"], c["targeting"], c["daily_usd"] or SCORING["budget"]["linkedin_min_daily_per_campaign"], p["objective"])
        for ad_id in c["ads"]:
            cr = by_id[ad_id]
            if cr["kind"] not in ("image", "document") or not cr["file"]:
                print(f"  skip {ad_id}: {cr['kind']} ads are set up by hand (video upload, Thought Leader Ads need the member's approval)")
                continue
            asset = cl.upload(org, ROOT / cr["file"], "image" if cr["kind"] == "image" else "document")
            post = cl.dark_post(org, account, cr["intro"], cr["headline"], asset, cr["url"], cr["cta"], cr["name"])
            creative = cl.creative(account, cid, post, cr["name"])
            launched["ads"][ad_id] = {"campaign": cid, "post": post, "creative": creative}
    if a.live:
        jsave(d / "launched.json", launched)
        for ad in camp["ads"]:
            if ad["id"] in launched["ads"]:
                ad["status"] = "launched"
        save(a.campaign, camp)
    jsave(d / ("requests.json" if a.live else "requests-dryrun.json"), log)
    print(f"{len(log)} requests logged to ads/campaigns/{a.campaign}/launch/. Everything is paused: activate in Campaign Manager.")


def _flat(t):
    return re.sub(r"\s+", " ", (t or "").replace("\u2019", "'")).strip()


def compare(p, camp, live_campaigns, creatives_by_campaign, posts):
    """What Campaign Manager holds against the plan. Pure: the API reads happen in cmd_verify.

    Returns (rows, mapping): rows are (level, where, message) with level ok, warn or error;
    mapping is {ad_id: {campaign, creative, post}} for ingest.
    """
    rows, mapping = [], {}
    by_name = {c.get("name"): c for c in live_campaigns}
    by_id = {c["ad_id"]: c for c in p["creatives"]}
    audiences = camp.get("audience_by_persona") or {}
    for pc in p["campaigns"]:
        lc = by_name.get(pc["name"])
        if not lc:
            rows.append(("error", pc["name"], "campaign not found (names must match the kit exactly)"))
            continue
        cid = str(lc.get("id"))
        rows.append(("ok", pc["name"], f"found, status {lc.get('status')}"))
        if lc.get("objectiveType") and lc["objectiveType"] != p["objective"]:
            rows.append(("warn", pc["name"], f"objective {lc['objectiveType']}, plan says {p['objective']}"))
        if lc.get("audienceExpansionEnabled"):
            rows.append(("warn", pc["name"], "audience expansion is on; the plan says off"))
        if lc.get("offsiteDeliveryEnabled"):
            rows.append(("warn", pc["name"], "LinkedIn Audience Network is on; the plan says off"))
        budget = (lc.get("dailyBudget") or {}).get("amount")
        if pc.get("daily_usd") and budget and abs(float(budget) - pc["daily_usd"]) > 0.01:
            rows.append(("warn", pc["name"], f"daily budget {budget}, plan says {pc['daily_usd']}"))
        rows.append(("ok" if budget else "warn", pc["name"], f"daily budget {budget or 'not set'}"))
        tgt = json.dumps(lc.get("targetingCriteria") or {})
        want_list = audiences.get(pc["persona"], {})
        if (want_list.get("contact_list") or want_list.get("company_list")) and "audienceMatchingSegments" not in tgt:
            rows.append(("error", pc["name"], "no Matched Audience in the targeting; the plan targets an uploaded list"))
        live = creatives_by_campaign.get(cid, [])
        seen = set()
        for ad_id in pc["ads"]:
            want = by_id[ad_id]
            match = [c for c in live if (c.get("name") or "").startswith(ad_id)]
            if not match:
                rows.append(("error", ad_id, "ad not found in this campaign (its name must start with the ad id)"))
                continue
            cr = match[0]
            seen.add(cr.get("id"))
            ref = (cr.get("content") or {}).get("reference")
            mapping[ad_id] = {"campaign": cid, "creative": cr.get("id"), "post": ref}
            post = posts.get(ref) or {}
            issues = []
            if _flat(post.get("commentary")) != _flat(want["intro"]):
                issues.append("intro text differs")
            if _flat(((post.get("content") or {}).get("media") or {}).get("title")) != _flat(want["headline"]):
                issues.append("headline differs")
            landing = post.get("contentLandingPage") or ""
            if f"utm_content={ad_id}" not in landing:
                issues.append(f"URL lacks utm_content={ad_id} (the scores cannot find its meetings)")
            if post.get("contentCallToActionLabel") and post["contentCallToActionLabel"] != want["cta"]:
                issues.append(f"CTA {post['contentCallToActionLabel']}, plan says {want['cta']}")
            status = cr.get("intendedStatus") or cr.get("status")
            rows.append(("error" if issues else "ok", ad_id, "; ".join(issues) or f"matches the kit, status {status}"))
        for c in live:
            if c.get("id") not in seen:
                rows.append(("warn", pc["name"], f"extra ad not in the plan: {c.get('name')!r}"))
    return rows, mapping


def cmd_verify(a):
    import os
    camp = load(a.campaign)
    p = plan(a.campaign, camp, False, a.round)
    account = os.environ.get("LINKEDIN_AD_ACCOUNT") or a.account
    if not os.environ.get("LINKEDIN_ACCESS_TOKEN"):
        sys.exit("no LINKEDIN_ACCESS_TOKEN in the environment: add a read-only token (r_ads, r_ads_reporting) to the "
                 "environment's settings, never to the repo or the chat")
    cl = linkedin.Client(live=True)
    if not account:
        accts = cl.ad_accounts()
        print("set LINKEDIN_AD_ACCOUNT to one of: " + ", ".join(f"{x.get('id')} ({x.get('name')})" for x in accts))
        sys.exit(1)
    live_campaigns = cl.campaigns(account)
    ids = [str(c["id"]) for c in live_campaigns if c.get("name") in {x["name"] for x in p["campaigns"]}]
    creatives = cl.creatives(account, ids) if ids else []
    by_campaign = defaultdict(list)
    for c in creatives:
        by_campaign[str(c.get("campaign", "")).split(":")[-1]].append(c)
    posts = {}
    for c in creatives:
        ref = (c.get("content") or {}).get("reference")
        if ref and ref.startswith(("urn:li:share", "urn:li:ugcPost")):
            posts[ref] = cl.post(ref)
    rows, mapping = compare(p, camp, live_campaigns, by_campaign, posts)
    for level, where, msg in rows:
        print(f"{level:5}  {where}: {msg}")
    errs = sum(1 for r in rows if r[0] == "error")
    print(f"\n{len(mapping)} of {len(p['creatives'])} ads found, {errs} errors, {sum(1 for r in rows if r[0] == 'warn')} warnings")
    if mapping:
        d = CAMPAIGNS / a.campaign / "launch"
        d.mkdir(exist_ok=True)
        known = jload(d / "launched.json") if (d / "launched.json").exists() else {"ads": {}}
        known.update({"verified": dt.datetime.now().isoformat(timespec="seconds"), "account": account})
        known["ads"].update(mapping)
        jsave(d / "launched.json", known)
        print(f"ads/campaigns/{a.campaign}/launch/launched.json: the ad ids LinkedIn uses, for `ingest api`")
    sys.exit(1 if errs else 0)


def sync_actions(p, live_campaigns, live_creatives):
    """Which planned ads are missing from the campaigns already in Campaign Manager. Pure, for testing."""
    by_name = {c.get("name"): c for c in live_campaigns}
    by_campaign = defaultdict(list)
    for c in live_creatives:
        by_campaign[str(c.get("campaign", "")).split(":")[-1]].append(c.get("name") or "")
    actions = []
    for pc in p["campaigns"]:
        lc = by_name.get(pc["name"])
        if not lc:
            actions.append(("missing-campaign", pc["name"], None))
            continue
        names = by_campaign.get(str(lc["id"]), [])
        for ad_id in pc["ads"]:
            if not any(n.startswith(ad_id) for n in names):
                actions.append(("create", ad_id, str(lc["id"])))
            else:
                actions.append(("exists", ad_id, str(lc["id"])))
    return actions


def _account_and_org(a):
    import os
    account = os.environ.get("LINKEDIN_AD_ACCOUNT") or getattr(a, "account", None)
    org = os.environ.get("LINKEDIN_ORG") or getattr(a, "org", None)
    if not account:
        sys.exit("set LINKEDIN_AD_ACCOUNT (the numeric ad account id) in the environment's settings")
    return account, org


def cmd_sync(a):
    """Add a round's approved ads to the campaigns already in Campaign Manager, PAUSED. Reads live; writes only with --live."""
    camp = load(a.campaign)
    errs, _ = lint_campaign(a.campaign, camp, quiet=True)
    if errs:
        print("\n".join(f"error  {e}" for e in errs))
        sys.exit("lint errors: nothing synced")
    p = plan(a.campaign, camp, False, a.round)
    account, org = _account_and_org(a)
    reader = linkedin.Client(live=True)
    live_campaigns = reader.campaigns(account)
    ids = [str(c["id"]) for c in live_campaigns if c.get("name") in {x["name"] for x in p["campaigns"]}]
    actions = sync_actions(p, live_campaigns, reader.creatives(account, ids) if ids else [])
    todo = [x for x in actions if x[0] == "create"]
    for kind, what, cid in actions:
        print({"missing-campaign": f"campaign  {what}: not in Campaign Manager; build it from the kit first",
               "create": f"create    {what} in campaign {cid} (PAUSED)", "exists": f"exists    {what}"}[kind])
    if not todo:
        print("nothing to create")
        return
    if not a.live:
        print(f"\ndry run: {len(todo)} ads would be created PAUSED. Add --live to create them.")
        return
    if not org:
        sys.exit("set LINKEDIN_ORG (the company page id) to post the ads as Breakout")
    if not BRAND.get("reviewed"):
        print("note   brand/brand.json says reviewed: false; these ads are drafts in the repo's terms")
    writer = linkedin.Client(live=True)
    by_id = {c["ad_id"]: c for c in p["creatives"]}
    d = CAMPAIGNS / a.campaign / "launch"
    d.mkdir(exist_ok=True)
    known = jload(d / "launched.json") if (d / "launched.json").exists() else {"ads": {}}
    for _, ad_id, cid in todo:
        cr = by_id[ad_id]
        if cr["kind"] not in ("image", "document") or not cr["file"] or not (ROOT / cr["file"]).exists():
            print(f"skip   {ad_id}: {cr['kind']} ads, or ads not rendered yet, are set up by hand")
            continue
        asset = writer.upload(org, ROOT / cr["file"], "image" if cr["kind"] == "image" else "document")
        post = writer.dark_post(org, account, cr["intro"], cr["headline"], asset, cr["url"], cr["cta"], cr["name"])
        creative = writer.creative(account, cid, post, cr["name"])
        known["ads"][ad_id] = {"campaign": cid, "creative": str(creative).split(":")[-1], "post": post}
        jsave(d / "launched.json", known)
        print(f"made   {ad_id}: creative {creative}, PAUSED")
    print("Created paused. Activate in Campaign Manager, or `ads.py status ... --activate --live` after the owner says yes.")


def cmd_status(a):
    """Pause, archive or activate ads by id, using launch/launched.json (written by verify and sync)."""
    account, _ = _account_and_org(a)
    known = jload(CAMPAIGNS / a.campaign / "launch" / "launched.json")
    status = "ACTIVE" if a.activate else "ARCHIVED" if a.archive else "PAUSED"
    cl = linkedin.Client(live=a.live)
    for ad_id in a.ad_ids:
        x = known["ads"].get(ad_id)
        if not x:
            print(f"skip   {ad_id}: not in launched.json (run verify first)")
            continue
        cl.set_creative_status(account, str(x["creative"]).split(":")[-1], status)
        print(f"{'set' if a.live else 'dry run'}  {ad_id} -> {status}")


def cmd_audience(a):
    cl = linkedin.Client(live=a.live)
    res = cl.typeahead(a.facet, a.query)
    for e in res.get("elements", []):
        print(f"{e.get('urn')}  {e.get('name')}")


# ------------------------------------------------------------------ ingest

ALIASES = {
    "ad_name": ["ad name", "creative name", "ad", "creative", "name"],
    "date": ["start date (in utc)", "start date", "date", "day", "meeting date", "activity date", "create date", "close date"],
    "impressions": ["impressions"],
    "clicks": ["clicks to landing page", "landing page clicks", "clicks"],
    "spend": ["total spent", "amount spent", "spend", "cost", "cost in usd"],
    "video_views": ["video views"],
    "video_starts": ["video starts", "video plays"],
    "video_q25": ["video views at 25%", "viewed 25%", "video first quartile completions", "25% video views"],
    "video_q50": ["video views at 50%", "viewed 50%", "video midpoint completions", "50% video views"],
    "video_completions": ["video completions", "video views at 100%", "completions"],
    "platform_conversions": ["conversions", "total conversions", "external website conversions"],
    "leads": ["leads", "lead form completions", "one click leads"],
    "ad_id": ["ad_id", "utm_content", "utm content"],
    "meetings": ["meetings", "meetings booked", "meeting booked"],
    "trials": ["trials", "trial signups", "trial sign-ups", "signups", "sign-ups"],
    "sqls": ["sqls", "sql", "sales qualified leads"],
    "pipeline": ["pipeline", "pipeline usd", "amount", "pipeline amount"],
}


def num(x):
    try:
        return float(str(x).replace(",", "").replace("$", "").replace("%", "").strip() or 0)
    except ValueError:
        return 0.0


def read_export(path):
    """Read a CSV whose header may sit under a few lines of preamble (Campaign Manager adds some)."""
    lines = Path(path).read_text(encoding="utf-8-sig", errors="ignore").splitlines()
    want = {a for al in ALIASES.values() for a in al}
    start = next((i for i, l in enumerate(lines[:20]) if sum(c.strip().lower() in want for c in next(csv.reader([l]))) >= 2), 0)
    rows = list(csv.DictReader(lines[start:]))
    cols = {}
    if rows:
        lower = {k.strip().lower(): k for k in rows[0].keys() if k}
        for field, names in ALIASES.items():
            for n in names:
                if n in lower:
                    cols[field] = lower[n]
                    break
    return rows, cols


def upsert(path, header, new_rows):
    keyed = {}
    if path.exists():
        for r in csv.DictReader(open(path)):
            keyed[(r["ad_id"], r["date"])] = r
    for r in new_rows:
        keyed[(r["ad_id"], r["date"])] = r
    DATA.mkdir(exist_ok=True)
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=header)
        w.writeheader()
        for k in sorted(keyed):
            w.writerow({h: keyed[k].get(h, "") for h in header})
    return len(new_rows)


def cmd_ingest(a):
    if a.source == "api":
        import os
        account = os.environ.get("LINKEDIN_AD_ACCOUNT") or a.account
        if not account:
            sys.exit("set LINKEDIN_AD_ACCOUNT")
        creative_to_ad = {}
        for p in CAMPAIGNS.glob("*/launch/launched.json"):
            for ad_id, x in jload(p)["ads"].items():
                creative_to_ad[str(x["creative"]).split(":")[-1]] = ad_id
        cl = linkedin.Client(live=a.live)
        end = dt.date.today().isoformat()
        rows = []
        for e in cl.analytics(account, a.since, end) if a.live else []:
            cid = str((e.get("pivotValues") or [""])[0]).split(":")[-1]
            if cid not in creative_to_ad:
                continue
            s = e["dateRange"]["start"]
            rows.append({"ad_id": creative_to_ad[cid], "date": f"{s['year']:04d}-{s['month']:02d}-{s['day']:02d}",
                         "impressions": e.get("impressions", 0), "clicks": e.get("landingPageClicks") or e.get("clicks", 0),
                         "spend": e.get("costInUsd", 0), "video_views": e.get("videoViews", 0), "video_starts": e.get("videoStarts", 0),
                         "video_q25": e.get("videoFirstQuartileCompletions", 0), "video_q50": e.get("videoMidpointCompletions", 0),
                         "video_completions": e.get("videoCompletions", 0), "platform_conversions": e.get("externalWebsiteConversions", 0),
                         "leads": e.get("oneClickLeads", 0)})
        print(f"{upsert(PERF, PERF_COLS, rows)} rows into ads/data/performance.csv")
        return
    rows, cols = read_export(a.file)
    out, skipped = [], 0
    for r in rows:
        if a.source == "linkedin":
            m = ID_RE.search(r.get(cols.get("ad_name", ""), "") or "")
            if not m:
                skipped += 1
                continue
            o = {"ad_id": m[1], "date": (r.get(cols.get("date", ""), "") or "total").strip()}
            for f in PERF_COLS[2:]:
                o[f] = num(r.get(cols[f], 0)) if f in cols else 0
        else:
            raw = (r.get(cols.get("ad_id", ""), "") or "")
            m = ID_RE.search(raw.upper())
            if not m:
                skipped += 1
                continue
            o = {"ad_id": m[1], "date": (r.get(cols.get("date", ""), "") or "total").strip()}
            counted = [f for f in CRM_COLS[2:] if f in cols]
            for f in CRM_COLS[2:]:
                o[f] = num(r.get(cols[f], 0)) if f in cols else 0
            if not counted:   # 1 row per meeting (a HubSpot meetings or contacts export): each row is 1 meeting
                o["meetings"] = 1
        out.append(o)
    if a.source == "crm":   # one row per ad and date: sum the deals
        agg = {}
        for o in out:
            k = (o["ad_id"], o["date"])
            agg.setdefault(k, {"ad_id": o["ad_id"], "date": o["date"], **{f: 0 for f in CRM_COLS[2:]}})
            for f in CRM_COLS[2:]:
                agg[k][f] += o[f]
        out = list(agg.values())
    path, header = (PERF, PERF_COLS) if a.source == "linkedin" else (CRM, CRM_COLS)
    print(f"{upsert(path, header, out)} rows into ads/data/{path.name}" + (f"; {skipped} rows had no ad id" if skipped else ""))
    print("mapped columns: " + ", ".join(f"{k} <- {v!r}" for k, v in cols.items()))
    if a.source == "crm" and not any(f in cols for f in CRM_COLS[2:]):
        print("no meetings, trials, SQL or pipeline column: counted each row as 1 meeting booked")


# ------------------------------------------------------------------ score

def totals():
    t = defaultdict(lambda: defaultdict(float))
    for path in (PERF, CRM):
        if path.exists():
            for r in csv.DictReader(open(path)):
                for k, v in r.items():
                    if k not in ("ad_id", "date"):
                        t[r["ad_id"]][k] += num(v)
    return t


def pct(values, x):
    """Percentile of x within values, 0 to 100, ties counted half."""
    if not values:
        return 50.0
    lo = sum(v < x for v in values)
    eq = sum(v == x for v in values)
    return 100.0 * (lo + 0.5 * eq) / len(values)


def score(tot=None, ads=None, cfg=SCORING):
    """Banger Score per ad. Returns a list of dicts, best first."""
    tot = tot if tot is not None else totals()
    ads = ads if ads is not None else all_ads()
    k = cfg["prior_strength"]
    rows = []
    for ad_id, m in tot.items():
        ad = ads.get(ad_id, {})
        kind = TAX["formats"].get(ad.get("format"), {}).get("kind", "unknown")
        rows.append({"ad_id": ad_id, "kind": kind, "ad": ad, **{x: m.get(x, 0.0) for x in PERF_COLS[2:] + CRM_COLS[2:]}})
    weights = cfg.get("outcomes", {"meetings": 1.0})
    for r in rows:   # server-side outcomes, weighted (scoring.json "outcomes"); meetings booked count most
        r["outcome"] = sum(r.get(o, 0) * w for o, w in weights.items())
    any_crm = any(r["outcome"] for r in rows)
    conv_key = "outcome"
    total_spend = sum(r["spend"] for r in rows) or 1
    conv_rate = sum(r[conv_key] for r in rows) / total_spend
    by_kind = defaultdict(list)
    for r in rows:
        by_kind[r["kind"]].append(r)
    for kind, group in by_kind.items():
        imp = sum(r["impressions"] for r in group) or 1
        vv = sum(r["video_views"] for r in group)
        mean_ctr = sum(r["clicks"] for r in group) / imp
        mean_hook = vv / imp
        mean_hold = sum(r["video_q25"] for r in group) / vv if vv else 0
        for r in group:
            r["ctr"] = (r["clicks"] + k["ctr"] * mean_ctr) / (r["impressions"] + k["ctr"])
            r["cpm"] = r["spend"] / r["impressions"] * 1000 if r["impressions"] else None
            r["raw_ctr"] = r["clicks"] / r["impressions"] if r["impressions"] else 0
            if kind == "video" and vv:
                r["hook"] = (r["video_views"] + k["hook"] * mean_hook) / (r["impressions"] + k["hook"])
                r["hold"] = (r["video_q25"] + k["hold"] * mean_hold) / (r["video_views"] + k["hold"])
                r["raw_hook"] = r["video_views"] / r["impressions"] if r["impressions"] else 0
                r["raw_hold"] = r["video_q25"] / r["video_views"] if r["video_views"] else 0
            if any_crm:
                r["conversion"] = (r[conv_key] + conv_rate * k["conversion_spend"]) / (r["spend"] + k["conversion_spend"]) * 1000
        for metric in ("ctr", "hook", "hold"):
            vals = [r[metric] for r in group if r.get(metric) is not None]
            for r in group:
                if r.get(metric) is not None:
                    r[f"{metric}_pct"] = pct(vals, r[metric])
        cpms = [r["cpm"] for r in group if r["cpm"] is not None]
        for r in group:
            if r["cpm"] is not None:
                r["cpm_pct"] = 100 - pct(cpms, r["cpm"])
    if any_crm:
        convs = [r["conversion"] for r in rows]
        for r in rows:
            r["conversion_pct"] = pct(convs, r["conversion"])
    w = cfg["weights"]
    th = cfg["thresholds"]
    trap = cfg["hook_trap"]
    for r in rows:
        parts = {m: r[f"{m}_pct"] for m in w if r.get(f"{m}_pct") is not None}
        wsum = sum(w[m] for m in parts)
        r["banger"] = round(sum(w[m] * parts[m] for m in parts) / wsum, 1) if wsum else None
        r["hook_trap"] = r.get("hook_pct") is not None and r["hook_pct"] >= trap["hook_pct_at_least"] and r["hold_pct"] <= trap["hold_pct_at_most"]
        enough = r["impressions"] >= cfg["min_impressions"] and r["spend"] >= cfg["min_spend"]
        if not enough:
            r["verdict"] = "learning"
        elif r["banger"] >= th["winner"] and not r["hook_trap"]:
            r["verdict"] = "winner"
        elif r["banger"] <= th["loser"] or r["hook_trap"]:
            r["verdict"] = "pause"
        else:
            r["verdict"] = "keep testing"
        r["conv_metric"] = "meetings" if any_crm else None
    rows.sort(key=lambda r: (r["verdict"] == "learning", -(r["banger"] or 0)))
    return rows


def money(x):
    return f"${x:,.0f}"


def cmd_score(a):
    rows = score()
    if not rows:
        sys.exit("no performance data yet: ingest a LinkedIn export (ads/data/performance.csv)")
    conv = rows[0]["conv_metric"]
    lines = ["# Creative leaderboard", "",
             f"Generated {dt.date.today().isoformat()} by `python3 ads/engine/ads.py score`. The Banger Score (0 to 100) ranks each ad against ads of the same kind on "
             + ", ".join(f"{m} {int(v * 100)}%" for m, v in SCORING["weights"].items())
             + f". Conversions are server-side meetings booked from HubSpot (trial signups weighted per scoring.json `outcomes`){'' if conv else ', none ingested yet, so the score runs without them'}, never the platform's own count. "
             f"An ad needs {SCORING['min_impressions']:,} impressions and {money(SCORING['min_spend'])} before it is judged. Do not edit by hand.", "",
             "| # | Ad | Banger | Verdict | Concept / angle / persona | Format | Impr. | Spend | CTR | CPM | Hook | Hold | Meetings | Trials | Pipeline |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(rows, 1):
        ad = r["ad"]
        flag = " (hook trap)" if r["hook_trap"] else ""
        hook = f"{r['raw_hook'] * 100:.1f}%" if r.get("raw_hook") is not None else ""
        hold = f"{r['raw_hold'] * 100:.1f}%" if r.get("raw_hold") is not None else ""
        lines.append(f"| {i} | {r['ad_id']} | {r['banger'] if r['banger'] is not None else ''} | {r['verdict']}{flag} | "
                     f"{ad.get('concept', '?')} / {ad.get('angle', '?')} / {ad.get('persona', '?')} | {ad.get('format', '?')} | {r['impressions']:,.0f} | {money(r['spend'])} | "
                     f"{r['raw_ctr'] * 100:.2f}% | {money(r['cpm']) if r['cpm'] is not None else ''} | {hook} | {hold} | {r['meetings']:.0f} | {r['trials']:.0f} | {money(r['pipeline'])} |")
    (ADS / "LEADERBOARD.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[6:]))
    print("\nads/LEADERBOARD.md written")


# ------------------------------------------------------------------ learn

AUTO_START, AUTO_END = "<!-- auto:start -->", "<!-- auto:end -->"


def cmd_learn(a):
    path = ADS / "LEARNINGS.md"
    text = path.read_text()
    if a.note:
        stamp = dt.date.today().isoformat()
        text = text.replace("## Log\n", f"## Log\n\n- {stamp}: {a.note}", 1)
        path.write_text(text)
        print("note added to ads/LEARNINGS.md")
        return
    rows = [r for r in score() if r["verdict"] != "learning" and r["ad"]]
    out = [AUTO_START, "", f"_Generated {dt.date.today().isoformat()} from {len(rows)} judged ads. Spend-weighted mean Banger Score; n is the number of ads._", ""]
    if not rows:
        out += ["No ad has enough data yet.", ""]
    for dim in ("concept", "angle", "persona", "awareness", "format", "hook"):
        g = defaultdict(list)
        for r in rows:
            g[r["ad"].get(dim)].append(r)
        if not g:
            continue
        out += [f"**By {dim}**", "", "| Value | Banger | n | Spend | Meetings |", "|---|---|---|---|---|"]
        for v, rs in sorted(g.items(), key=lambda kv: -wmean(kv[1])):
            out.append(f"| {v} | {wmean(rs):.0f} | {len(rs)} | {money(sum(r['spend'] for r in rs))} | {sum(r['meetings'] for r in rs):.0f} |")
        out.append("")
    combos = defaultdict(list)
    for r in rows:
        combos[(r["ad"].get("concept"), r["ad"].get("angle"), r["ad"].get("persona"))].append(r)
    if combos:
        out += ["**Combinations (concept + angle + persona), best first**", "", "| Combination | Banger | n | Next |", "|---|---|---|---|"]
        for (c, an, p), rs in sorted(combos.items(), key=lambda kv: -wmean(kv[1]))[:10]:
            best = max(rs, key=lambda r: r["banger"] or 0)
            nxt = f"`ads.py iterate {best['ad']['campaign']} {best['ad_id']}`" if best["verdict"] == "winner" else ""
            out.append(f"| {c} + {an} + {p} | {wmean(rs):.0f} | {len(rs)} | {nxt} |")
        out.append("")
    traps = [r["ad_id"] for r in rows if r["hook_trap"]]
    if traps:
        out += [f"**Hook traps** (they stop the scroll, then lose people): {', '.join(traps)}. Keep the hook, fix what follows it.", ""]
    out.append(AUTO_END)
    block = "\n".join(out)
    text = re.sub(re.escape(AUTO_START) + r".*?" + re.escape(AUTO_END), lambda _: block, text, flags=re.S)
    path.write_text(text)
    print(block)


def wmean(rs):
    s = sum(r["spend"] for r in rs)
    return sum((r["banger"] or 0) * r["spend"] for r in rs) / s if s else sum(r["banger"] or 0 for r in rs) / len(rs)


# ------------------------------------------------------------------ iterate

def cmd_iterate(a):
    camp = load(a.campaign)
    parent = next((x for x in camp["ads"] if x["id"] == a.ad_id), None)
    if not parent:
        sys.exit(f"no ad {a.ad_id} in {a.campaign}")
    n = a.n or SCORING["iterate"]["executions_per_winner"]
    formats = [f for f in TAX["formats"] if f != "video-motion"] + ["video-motion"]
    hooks = list(TAX["hooks"])
    pairs = [(f, h) for h in hooks for f in formats if (f, h) != (parent["format"], parent["hook"])]
    # spread across formats first, then hooks, so 10 stubs are 10 different executions
    pairs.sort(key=lambda fh: (formats.index(fh[0]) + hooks.index(fh[1])) % len(formats))
    seen, chosen = set(), []
    for f, h in pairs:
        if (f, h) in seen:
            continue
        seen.add((f, h))
        chosen.append((f, h))
        if len(chosen) == n:
            break
    nums = [int(x["id"].split("-")[1]) for x in camp["ads"]]
    nxt = max(nums, default=0) + 1
    for f, h in chosen:
        kind = TAX["formats"][f]["kind"]
        stub = {"id": f"{camp['code']}-{nxt:03d}", "status": "stub", "parent": parent["id"],
                "concept": parent["concept"], "angle": parent["angle"], "persona": parent["persona"], "awareness": parent["awareness"],
                "format": f, "hook": h,
                "copy": {"intro": f"TODO: a new {h} execution of {parent['concept']} for {parent['persona']}", "headline": "TODO", "description": ""}}
        if kind == "image":
            stub["design"] = {"template": "TODO: verdict, slam, chat, split or screen", "fields": {"headline": "TODO"}}
        elif kind == "document":
            stub["design"] = {"pages": [{"template": "verdict", "fields": {"headline": "TODO"}} for _ in range(4)]}
        else:
            stub["script"] = {"hook_0_3s": "TODO", "hold_3_10s": "TODO", "product": "TODO", "cta": "TODO"}
        camp["ads"].append(stub)
        nxt += 1
    save(a.campaign, camp)
    print(f"{len(chosen)} stubs around {parent['id']} ({parent['concept']} + {parent['angle']} + {parent['persona']}): "
          + ", ".join(f"{f}/{h}" for f, h in chosen))
    print("Fill every TODO (skills/ads-engine/SKILL.md, step 'iterate'), then lint and render.")


# ------------------------------------------------------------------ budget

def cmd_budget(a):
    camp = load(a.campaign)
    b = SCORING["budget"]
    share = min(max(a.test_share or camp.get("budget", {}).get("test_share") or b["test_share"], b["test_share_min"]), b["test_share_max"])
    rows = [r for r in score() if r["ad"].get("campaign") == a.campaign]
    winners = [r for r in rows if r["verdict"] == "winner"]
    testing = [r for r in rows if r["verdict"] in ("learning", "keep testing")]
    pause = [r for r in rows if r["verdict"] == "pause"]
    daily = a.daily
    if not winners:
        print(f"No proven winner yet: all {money(daily)}/day goes to testing until one appears.")
        share = 1.0
    test_budget, scale_budget = daily * share, daily * (1 - share)
    personas = sorted({x["persona"] for x in camp["ads"] if x.get("status") in ("approved", "launched")}) or sorted(camp.get("personas", []))
    per = test_budget / max(len(personas), 1)
    print(f"Test {money(test_budget)}/day ({share:.0%}) across {len(personas)} persona campaigns, {money(per)} each"
          + (f"  (under LinkedIn's {money(b['linkedin_min_daily_per_campaign'])} minimum: test fewer personas at once)" if per < b["linkedin_min_daily_per_campaign"] else ""))
    if winners:
        tot = sum(r["banger"] for r in winners)
        print(f"Scale {money(scale_budget)}/day ({1 - share:.0%}) behind {len(winners)} winners in the '{camp['code']} | scale' group:")
        for r in winners:
            print(f"  {r['ad_id']}  banger {r['banger']}  {money(scale_budget * r['banger'] / tot)}/day")
    if pause:
        print("Pause: " + ", ".join(f"{r['ad_id']}{' (hook trap)' if r['hook_trap'] else ''}" for r in pause))
    if testing:
        print(f"Still testing: {', '.join(r['ad_id'] for r in testing)}")
    print("A recommendation only: change budgets in Campaign Manager after the owner says yes.")


# ------------------------------------------------------------------ main

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("new"); s.add_argument("campaign"); s.add_argument("--code", required=True); s.add_argument("--idea"); s.set_defaults(fn=cmd_new)
    s = sub.add_parser("lint"); s.add_argument("campaign"); s.set_defaults(fn=cmd_lint)
    s = sub.add_parser("render"); s.add_argument("campaign"); s.add_argument("--round", type=int); s.add_argument("--ids", nargs="*"); s.add_argument("--force", action="store_true"); s.set_defaults(fn=cmd_render)
    s = sub.add_parser("sheet"); s.add_argument("campaign"); s.set_defaults(fn=cmd_sheet)
    s = sub.add_parser("export"); s.add_argument("campaign"); s.add_argument("--round", type=int); s.add_argument("--all", action="store_true"); s.set_defaults(fn=cmd_export)
    s = sub.add_parser("kit"); s.add_argument("campaign"); s.add_argument("--round", type=int); s.add_argument("--all", action="store_true"); s.set_defaults(fn=cmd_kit)
    s = sub.add_parser("launch"); s.add_argument("campaign"); s.add_argument("--live", action="store_true"); s.add_argument("--account"); s.add_argument("--org"); s.set_defaults(fn=cmd_launch)
    s = sub.add_parser("verify"); s.add_argument("campaign"); s.add_argument("--round", type=int); s.add_argument("--account"); s.set_defaults(fn=cmd_verify)
    s = sub.add_parser("sync"); s.add_argument("campaign"); s.add_argument("--round", type=int, required=True); s.add_argument("--live", action="store_true"); s.add_argument("--account"); s.add_argument("--org"); s.set_defaults(fn=cmd_sync)
    s = sub.add_parser("status"); s.add_argument("campaign"); s.add_argument("ad_ids", nargs="+"); g = s.add_mutually_exclusive_group(required=True)
    g.add_argument("--pause", action="store_true"); g.add_argument("--activate", action="store_true"); g.add_argument("--archive", action="store_true")
    s.add_argument("--live", action="store_true"); s.add_argument("--account"); s.set_defaults(fn=cmd_status)
    s = sub.add_parser("audience"); s.add_argument("action", choices=["resolve"]); s.add_argument("facet"); s.add_argument("query"); s.add_argument("--live", action="store_true"); s.set_defaults(fn=cmd_audience)
    s = sub.add_parser("ingest"); s.add_argument("source", choices=["linkedin", "crm", "api"]); s.add_argument("file", nargs="?")
    s.add_argument("--since"); s.add_argument("--account"); s.add_argument("--live", action="store_true"); s.set_defaults(fn=cmd_ingest)
    s = sub.add_parser("score"); s.set_defaults(fn=cmd_score)
    s = sub.add_parser("learn"); s.add_argument("--note"); s.set_defaults(fn=cmd_learn)
    s = sub.add_parser("iterate"); s.add_argument("campaign"); s.add_argument("ad_id"); s.add_argument("--n", type=int); s.set_defaults(fn=cmd_iterate)
    s = sub.add_parser("budget"); s.add_argument("campaign"); s.add_argument("--daily", type=float, required=True); s.add_argument("--test-share", type=float); s.set_defaults(fn=cmd_budget)
    a = p.parse_args(argv)
    if a.cmd == "ingest" and a.source != "api" and not a.file:
        sys.exit("give the export file")
    if a.cmd == "ingest" and a.source == "api" and not a.since:
        sys.exit("--since YYYY-MM-DD")
    a.fn(a)


if __name__ == "__main__":
    main()
