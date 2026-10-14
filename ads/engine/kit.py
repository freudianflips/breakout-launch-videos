"""The browser launch kit: one page that walks a person through building a round in Campaign Manager by hand,
with every field to paste, every file to upload and a checkbox per step. Used until the Advertising API is approved.

  python3 ads/engine/ads.py kit <campaign> [--all]   ->  ads/campaigns/<campaign>/launch/kit.html
"""
import html
import json

CTA_LABEL = {"REQUEST_DEMO": "Request demo", "SIGN_UP": "Sign up", "LEARN_MORE": "Learn more", "DOWNLOAD": "Download",
             "REGISTER": "Register", "SUBSCRIBE": "Subscribe", "JOIN": "Join", "ATTEND": "Attend", "APPLY": "Apply",
             "VIEW_QUOTE": "View quote", "SEE_MORE": "See more", "BUY_NOW": "Buy now", "SHOP_NOW": "Shop now"}
OBJECTIVE_LABEL = {"WEBSITE_VISIT": "Website visits", "WEBSITE_CONVERSION": "Website conversions", "LEAD_GENERATION": "Lead generation",
                   "ENGAGEMENT": "Engagement", "VIDEO_VIEW": "Video views", "BRAND_AWARENESS": "Brand awareness"}
FORMAT_LABEL = {"image": "Single image ad", "document": "Document ad", "video": "Video ad", "post": "Thought leader ad"}
SIZE_LABEL = {"SIZE_1": "1", "SIZE_2_TO_10": "2-10", "SIZE_11_TO_50": "11-50", "SIZE_51_TO_200": "51-200", "SIZE_201_TO_500": "201-500",
              "SIZE_501_TO_1000": "501-1,000", "SIZE_1001_TO_5000": "1,001-5,000", "SIZE_5001_TO_10000": "5,001-10,000", "SIZE_10001_OR_MORE": "10,001+"}


def e(x):
    return html.escape(str(x or ""))


def field(label, value, key, mono=False):
    """A labelled value with a copy button."""
    v = e(value)
    return (f'<div class="f"><div class="fl">{e(label)}</div><div class="fv{" mono" if mono else ""}" id="{key}">{v.replace(chr(10), "<br>")}</div>'
            f'<button class="copy" data-copy="{key}" data-text="{v}">Copy</button></div>')


def step(key, title, body):
    return f'<details class="step" open><summary><label><input type="checkbox" data-k="{key}"> {title}</label></summary><div class="sb">{body}</div></details>'


def build(slug, camp, p, aud, reviewed, file_url):
    """file_url(path) -> the href the page uses for a creative file."""
    shared = aud["shared"]
    blocks = []
    setup = (
        "<p>Once per ad account, before the first round.</p><ol>"
        "<li><b>Insight Tag.</b> Campaign Manager, Analyze, Insight Tag. If it is not firing on getbreakout.ai, add it through Google Tag Manager "
        "(the site already loads GTM). It also builds the website retargeting audience for later rounds.</li>"
        "<li><b>Conversions.</b> Analyze, Conversion tracking: <i>Meeting booked</i> (the meeting confirmation page or event) and <i>Trial signup</i> "
        "(dashboard.getbreakout.ai/signup). The scores never use LinkedIn's count, but its optimisation does.</li>"
        "<li><b>Exclusions.</b> Plan, Audiences: upload current customers and Breakout employees as a company list; exclude it in every campaign.</li>"
        "<li><b>HubSpot.</b> Keep <code>utm_content</code> on the contact and the meeting (confirmed): it carries each ad's id.</li></ol>")
    blocks.append(step("setup", "0. One-time setup", setup))
    blocks.append(step("group", f"1. Campaign group: {e(p['groups'][0])}", field("Name", p["groups"][0], "g0")
                       + '<p class="note">Status active, no group budget (budgets live on the campaigns), start today.</p>'))
    by_id = {c["ad_id"]: c for c in p["creatives"]}
    n = 2
    for ci, c in enumerate(p["campaigns"]):
        labels = c["targeting_labels"]
        persona = aud["personas"][c["persona"]]
        sizes = persona.get("company_size_override") or shared.get("company_size") or []
        aud_rows = [("Locations", shared.get("locations_label", ""))]
        if sizes:
            aud_rows.append(("Company size", ", ".join(SIZE_LABEL[x] for x in sizes)))
        for k, lab in (("functions_label", "Job functions"), ("seniorities_label", "Job seniorities")):
            if labels.get(k):
                aud_rows.append((lab, ", ".join(labels[k])))
        if not labels.get("functions_label") and labels.get("titles_label"):
            aud_rows.append(("Job titles", ", ".join(labels["titles_label"])))
        aud_html = "".join(f"<tr><th>{e(a)}</th><td>{e(b)}</td></tr>" for a, b in aud_rows)
        alt = (f'<p class="note">If the audience is under 50,000, add these titles as an alternative (OR) instead: {e(", ".join(labels.get("titles_label", [])))}.</p>'
               if labels.get("functions_label") and labels.get("titles_label") else "")
        settings = (field("Campaign name", c["name"], f"c{ci}")
                    + f'<table class="kv"><tr><th>Group</th><td>{e(p["groups"][0])}</td></tr>'
                    f'<tr><th>Objective</th><td>{e(OBJECTIVE_LABEL.get(p["objective"], p["objective"]))}</td></tr>{aud_html}'
                    f'<tr><th>Audience expansion</th><td>Off</td></tr><tr><th>LinkedIn Audience Network</th><td>Off</td></tr>'
                    f'<tr><th>Ad format</th><td>{e(FORMAT_LABEL.get(c["kind"], c["kind"]))}</td></tr>'
                    f'<tr><th>Daily budget</th><td>{"$" + format(c["daily_usd"], ",.2f") if c["daily_usd"] else "<b>not set</b>"}</td></tr>'
                    f'<tr><th>Bidding</th><td>Maximum delivery (automated)</td></tr><tr><th>Schedule</th><td>Start today, no end date</td></tr>'
                    f'<tr><th>Conversions</th><td>Meeting booked, Trial signup</td></tr></table>{alt}')
        ads_html = []
        for ai, ad_id in enumerate(c["ads"]):
            cr = by_id[ad_id]
            k = f"c{ci}a{ai}"
            if cr["kind"] in ("image", "document") and cr["file"]:
                href = file_url(cr["file"])
                thumb = (f'<a href="{e(href)}" download><img src="{e(href)}" alt="{e(ad_id)} creative"></a>' if cr["kind"] == "image"
                         else f'<a class="dl" href="{e(href)}" download>Download {e(ad_id)}.pdf</a>')
                body = (f'<div class="ad"><div class="thumb">{thumb}<a class="dl" href="{e(href)}" download>Download file</a></div><div class="fields">'
                        + field("Ad name", cr["name"], k + "n", True)
                        + field("Introductory text", cr["intro"], k + "i")
                        + (field("Document title" if cr["kind"] == "document" else "Headline", cr["headline"], k + "h"))
                        + (field("Description", cr["description"], k + "d") if cr["description"] else "")
                        + field("Destination URL", cr["url"], k + "u", True)
                        + f'<div class="f"><div class="fl">Call to action</div><div class="fv">{e(CTA_LABEL.get(cr["cta"], cr["cta"]))} (pick from the list)</div></div>'
                        + "</div></div>")
            else:
                body = (f'<p class="note">Made by a person, not rendered here. Set it up when the asset exists; name the ad exactly as below so the scores can find it.</p>'
                        + field("Ad name", cr["name"], k + "n", True)
                        + f'<pre class="script">{e(json.dumps(cr.get("script") or {}, indent=2, ensure_ascii=False))}</pre>')
            ads_html.append(step(f"{k}", f"Ad {e(ad_id)}", body))
        blocks.append(step(f"c{ci}", f"{n}. Campaign: {e(c['name'])}", settings + "".join(ads_html)))
        n += 1
    after = ("<ol><li>Check every ad name starts with its id (P2P-001 ...): the scores join on it.</li>"
             "<li>Wait for LinkedIn's review (usually within a day), then let it run. Judge nothing before about 3,000 impressions an ad.</li>"
             "<li>Weekly: Campaign Manager, Analyze, Export, <i>Ad performance</i>, daily breakdown. Then "
             "<code>python3 ads/engine/ads.py ingest linkedin &lt;file&gt;</code>.</li>"
             "<li>Weekly: export HubSpot meetings (or contacts with a meeting) with <code>utm_content</code>. Then "
             "<code>python3 ads/engine/ads.py ingest crm &lt;file&gt;</code>, <code>score</code> and <code>learn</code>.</li></ol>")
    blocks.append(step("after", f"{n}. After launch", after))
    total = sum(c["daily_usd"] or 0 for c in p["campaigns"])
    warn = "" if reviewed else '<p class="draft">Draft: brand/brand.json is not reviewed yet.</p>'
    unapproved = [c["ad_id"] for c in p["creatives"] if not any(a["id"] == c["ad_id"] and a.get("status") == "approved" for a in camp["ads"])]
    if unapproved:
        warn += f'<p class="draft">Preview only: {len(unapproved)} ads are not approved ({e(", ".join(unapproved))}). Do not build them.</p>'
    return PAGE.format(title=e(f"{camp['code']} launch kit"), code=e(camp["code"]), slug=e(slug), idea=e(camp.get("idea")),
                       n_c=len(p["campaigns"]), n_a=len(p["creatives"]), total=f"${total:,.0f}", warn=warn, body="".join(blocks))


PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
:root {{ --bg: #f4f4f4; --card: #fff; --ink: #040405; --ink2: #5c5850; --line: #e3e1ea; --accent: #4c00ff; --soft: #f6f1ff; --warn: #fff1d6; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg: #140b3c; --card: #1d1450; --ink: #fafafa; --ink2: #c9c3e6; --line: #33296e; --accent: #be79ff; --soft: #2a1f66; --warn: #4a3a10; }} }}
:root[data-theme="dark"] {{ --bg: #140b3c; --card: #1d1450; --ink: #fafafa; --ink2: #c9c3e6; --line: #33296e; --accent: #be79ff; --soft: #2a1f66; --warn: #4a3a10; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--bg); color: var(--ink); font: 15px/1.5 Manrope, system-ui, -apple-system, sans-serif; }}
main {{ max-width: 1040px; margin: 0 auto; padding: 32px 16px 80px; }}
h1 {{ font: 400 34px/1.1 Fraunces, Georgia, serif; letter-spacing: -0.02em; margin: 0 0 6px; }}
.lede {{ color: var(--ink2); margin: 0 0 8px; }}
.meta {{ font: 13px ui-monospace, monospace; color: var(--ink2); margin-bottom: 20px; }}
.draft {{ background: var(--warn); padding: 8px 12px; border-radius: 8px; margin: 8px 0; }}
.step {{ background: var(--card); border: 1px solid var(--line); border-radius: 12px; margin: 12px 0; }}
.step .step {{ margin: 10px 0 0; background: var(--soft); }}
summary {{ cursor: pointer; padding: 12px 16px; font-weight: 700; list-style: none; }}
summary::-webkit-details-marker {{ display: none; }}
summary input {{ width: 18px; height: 18px; vertical-align: -3px; margin-right: 6px; accent-color: var(--accent); }}
.sb {{ padding: 0 16px 16px; }}
.f {{ display: grid; grid-template-columns: 150px 1fr auto; gap: 10px; align-items: start; padding: 8px 0; border-top: 1px solid var(--line); }}
.fl {{ color: var(--ink2); font-size: 13px; padding-top: 2px; }}
.fv {{ white-space: normal; overflow-wrap: anywhere; }}
.mono {{ font: 13px ui-monospace, monospace; }}
button.copy {{ font: 600 12px Manrope, system-ui, sans-serif; border: 1px solid var(--accent); color: var(--accent); background: transparent; border-radius: 999px; padding: 4px 12px; cursor: pointer; }}
button.copy.done {{ background: var(--accent); color: #fff; }}
table.kv {{ border-collapse: collapse; margin: 8px 0; width: 100%; }}
table.kv th {{ text-align: left; font-weight: 500; color: var(--ink2); width: 190px; padding: 5px 8px 5px 0; vertical-align: top; }}
table.kv td {{ padding: 5px 0; }}
.note {{ color: var(--ink2); font-size: 13px; }}
.ad {{ display: grid; grid-template-columns: 220px 1fr; gap: 16px; }}
.thumb img {{ width: 100%; border-radius: 8px; border: 1px solid var(--line); display: block; }}
a.dl {{ display: inline-block; margin-top: 6px; color: var(--accent); font-size: 13px; }}
pre.script {{ white-space: pre-wrap; font-size: 12px; background: var(--card); padding: 10px; border-radius: 8px; }}
code {{ font-size: 13px; }}
@media (max-width: 640px) {{ .ad {{ grid-template-columns: 1fr; }} .f {{ grid-template-columns: 1fr auto; }} .fl {{ grid-column: 1 / -1; }} }}
</style></head>
<body><main>
<h1>{code} launch kit</h1>
<p class="lede">{idea}</p>
<div class="meta">{slug} · {n_c} campaigns · {n_a} ads · {total}/day</div>
{warn}
<p class="note">Build it in Campaign Manager, top to bottom. Every value has a Copy button; ticks are remembered in this browser.</p>
{body}
</main>
<script>
document.querySelectorAll('button.copy').forEach((b) => b.addEventListener('click', async () => {{
  const t = b.dataset.text;
  try {{ await navigator.clipboard.writeText(t); }} catch (err) {{
    const ta = document.createElement('textarea'); ta.value = t; document.body.appendChild(ta); ta.select();
    try {{ document.execCommand('copy'); }} catch (e2) {{}} ta.remove();
  }}
  b.textContent = 'Copied'; b.classList.add('done');
  setTimeout(() => {{ b.textContent = 'Copy'; b.classList.remove('done'); }}, 1400);
}}));
const KEY = 'kit:' + document.title;
let saved = {{}};
try {{ saved = JSON.parse(localStorage.getItem(KEY) || '{{}}'); }} catch (err) {{ saved = {{}}; }}
document.querySelectorAll('input[data-k]').forEach((c) => {{
  c.checked = !!saved[c.dataset.k];
  c.addEventListener('click', (ev) => ev.stopPropagation());
  c.addEventListener('change', () => {{
    saved[c.dataset.k] = c.checked;
    try {{ localStorage.setItem(KEY, JSON.stringify(saved)); }} catch (err) {{}}
  }});
}});
</script>
</body></html>
"""
