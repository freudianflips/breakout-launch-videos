#!/usr/bin/env python3
"""Find which companies run a vendor's website widget, for a LinkedIn company-list audience.

  python3 ads/engine/stack.py qualified domains.csv [--browser] [--out ads/data/qualified-companies.csv]

domains.csv: a column named domain, website or company website (company name optional), e.g. an export of
your ICP accounts from HubSpot, Clay or Breakout. Each homepage is fetched once, politely (1 at a time,
a pause between sites), and searched for the vendor's markers (ads/stack.json). --browser also loads
the pages that show no marker in headless Chrome, to catch widgets a tag manager injects.

Writes LinkedIn's company list format (companyname, companywebsite, companyemaildomain) for
Campaign Manager, Plan, Audiences, Create audience, Upload a list, plus the evidence for each match.
The list holds companies, not people; it stays out of git (ads/data/).
"""
import argparse
import csv
import json
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"


def clean(d):
    d = re.sub(r"^https?://", "", (d or "").strip().lower()).split("/")[0]
    return d[4:] if d.startswith("www.") else d


def fetch(domain):
    for url in (f"https://{domain}/", f"https://www.{domain}/"):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.read(3_000_000).decode("utf-8", "ignore")
        except Exception:
            continue
    return None


def browser(domain):
    r = subprocess.run(["node", str(HERE / "requests.mjs"), f"https://{domain}/"], capture_output=True, text=True, timeout=60)
    return r.stdout


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("vendor")
    p.add_argument("domains")
    p.add_argument("--browser", action="store_true")
    p.add_argument("--pause", type=float, default=1.0)
    p.add_argument("--out")
    a = p.parse_args()
    markers = json.loads((ROOT / "ads" / "stack.json").read_text())["vendors"].get(a.vendor)
    if not markers:
        sys.exit(f"no markers for {a.vendor!r} in ads/stack.json")
    rows = list(csv.DictReader(open(a.domains, encoding="utf-8-sig")))
    if not rows:
        sys.exit("no rows")
    lower = {k.strip().lower(): k for k in rows[0]}
    dcol = next((lower[k] for k in ("domain", "website", "company website", "company domain name", "companywebsite") if k in lower), None)
    ncol = next((lower[k] for k in ("company", "company name", "name", "companyname") if k in lower), None)
    if not dcol:
        sys.exit(f"no domain column among {list(rows[0])}")
    out = Path(a.out or ROOT / "ads" / "data" / f"{a.vendor}-companies.csv")
    out.parent.mkdir(exist_ok=True)
    found, checked, failed = [], 0, 0
    seen = set()
    for r in rows:
        d = clean(r.get(dcol))
        if not d or d in seen:
            continue
        seen.add(d)
        checked += 1
        page = fetch(d)
        if page is None:
            failed += 1
        hits = [m for m in markers if page and m.lower() in page.lower()]
        how = "page source"
        if not hits and a.browser:
            reqs = browser(d)
            hits = [m for m in markers if m.lower() in reqs.lower()]
            how = "browser requests"
        if hits:
            found.append({"companyname": (r.get(ncol) or "").strip() if ncol else "", "companywebsite": f"https://{d}",
                          "companyemaildomain": d, "evidence": f"{how}: {', '.join(hits)}", "checked": time.strftime("%Y-%m-%d")})
        print(f"{'YES' if hits else 'no ':3} {d}" + (f"  ({how}: {', '.join(hits)})" if hits else "  (unreachable)" if page is None and not a.browser else ""))
        time.sleep(a.pause)
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["companyname", "companywebsite", "companyemaildomain", "evidence", "checked"])
        w.writeheader()
        w.writerows(found)
    print(f"\n{len(found)} of {checked} run {a.vendor} ({failed} unreachable) -> {out.relative_to(ROOT) if out.is_relative_to(ROOT) else out}")
    print("Upload companyname, companywebsite and companyemaildomain to Campaign Manager (drop the evidence columns). LinkedIn needs 300+ matched members to serve.")


if __name__ == "__main__":
    main()
