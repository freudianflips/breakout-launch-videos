"""LinkedIn Marketing API client for the ads engine. Standard library only.

Everything is a dry run unless live=True: the requests are printed and logged, nothing is sent.
Live runs read the token from the environment (LINKEDIN_ACCESS_TOKEN) and never write it anywhere.
Every campaign group and campaign is created as DRAFT and every creative as PAUSED, so nothing
spends until a person activates it in Campaign Manager.

The token needs the r_ads, rw_ads and r_ads_reporting scopes (Advertising API) and, to create
the sponsored posts, w_organization_social on the company page. Payload shapes follow the
versioned REST API (https://learn.microsoft.com/linkedin/marketing/); check them against the
current version before the first live run, and set LINKEDIN_VERSION (YYYYMM) to a live version.
"""
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.linkedin.com/rest"
VERSION = os.environ.get("LINKEDIN_VERSION", "202609")
STAFF = {"SIZE_1": "(1,1)", "SIZE_2_TO_10": "(2,10)", "SIZE_11_TO_50": "(11,50)", "SIZE_51_TO_200": "(51,200)",
         "SIZE_201_TO_500": "(201,500)", "SIZE_501_TO_1000": "(501,1000)", "SIZE_1001_TO_5000": "(1001,5000)",
         "SIZE_5001_TO_10000": "(5001,10000)", "SIZE_10001_OR_MORE": "(10001,2147483647)"}
OBJECTIVES = {"WEBSITE_VISIT", "WEBSITE_CONVERSION", "LEAD_GENERATION", "ENGAGEMENT", "VIDEO_VIEW", "BRAND_AWARENESS"}
CTAS = {"APPLY", "DOWNLOAD", "VIEW_QUOTE", "LEARN_MORE", "SIGN_UP", "SUBSCRIBE", "REGISTER", "JOIN", "ATTEND",
        "REQUEST_DEMO", "SEE_MORE", "BUY_NOW", "SHOP_NOW"}
METRICS = ["impressions", "clicks", "landingPageClicks", "costInUsd", "videoViews", "videoStarts",
           "videoFirstQuartileCompletions", "videoMidpointCompletions", "videoCompletions",
           "externalWebsiteConversions", "oneClickLeads", "dateRange", "pivotValues"]


class Client:
    def __init__(self, live=False, log=None):
        self.live = live
        self.log = log            # a list that collects every request, for the launch record
        self.token = os.environ.get("LINKEDIN_ACCESS_TOKEN")
        if live and not self.token and os.environ.get("LINKEDIN_REFRESH_TOKEN"):
            self.token = refresh_access_token()
        if live and not self.token:
            raise SystemExit("set LINKEDIN_ACCESS_TOKEN, or LINKEDIN_REFRESH_TOKEN with LINKEDIN_CLIENT_ID and "
                             "LINKEDIN_CLIENT_SECRET, in the environment's settings (never in the repo or the chat)")
        self._fake = 0

    def call(self, method, path, body=None, query=None, raw=None, url=None, headers=None, soft=False):
        url = url or API + path + (("?" + query) if query else "")
        entry = {"method": method, "url": url, "body": body if raw is None else f"<{len(raw)} bytes>"}
        if self.log is not None:
            self.log.append(entry)
        if not self.live:
            print(f"  dry run  {method} {url}")
            self._fake += 1
            return {"id": f"DRYRUN-{self._fake}", "value": {"uploadUrl": "https://example.invalid/upload", "image": f"urn:li:image:DRYRUN-{self._fake}", "document": f"urn:li:document:DRYRUN-{self._fake}"}}
        data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
        req = urllib.request.Request(url, data=data, method=method)
        if raw is None:
            req.add_header("Authorization", f"Bearer {self.token}")
            req.add_header("LinkedIn-Version", VERSION)
            req.add_header("X-Restli-Protocol-Version", "2.0.0")
            req.add_header("Content-Type", "application/json")
            for k, v in (headers or {}).items():
                req.add_header(k, v)
        else:
            req.add_header("Authorization", f"Bearer {self.token}")
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    text = r.read().decode() or "{}"
                    out = json.loads(text) if text.strip().startswith(("{", "[")) else {}
                    out.setdefault("id", r.headers.get("x-restli-id") or r.headers.get("x-linkedin-id"))
                    return out
            except urllib.error.HTTPError as e:
                if e.code in (429, 500, 502, 503) and attempt < 3:
                    time.sleep(2 ** (attempt + 1))
                    continue
                if soft and e.code in (401, 403, 404):   # the caller carries on without this one
                    return {"_error": e.code, "_detail": e.read().decode()[:300]}
                raise SystemExit(f"LinkedIn {e.code} on {method} {url}: {e.read().decode()[:800]}")

    # ---------------------------------------------------------------- build

    def campaign_group(self, account, name):
        body = {"account": f"urn:li:sponsoredAccount:{account}", "name": name, "status": "DRAFT",
                "runSchedule": {"start": int(time.time() * 1000)}}
        return self.call("POST", f"/adAccounts/{account}/adCampaignGroups", body)["id"]

    def campaign(self, account, group_id, name, targeting, daily_budget, objective="WEBSITE_VISIT", currency="USD"):
        body = {
            "account": f"urn:li:sponsoredAccount:{account}",
            "campaignGroup": f"urn:li:sponsoredCampaignGroup:{group_id}",
            "name": name, "type": "SPONSORED_UPDATES", "objectiveType": objective, "costType": "CPM",
            "dailyBudget": {"amount": f"{daily_budget:.2f}", "currencyCode": currency},
            "locale": {"country": "US", "language": "en"},
            "offsiteDeliveryEnabled": False, "audienceExpansionEnabled": False,
            "targetingCriteria": targeting, "status": "DRAFT",
        }
        return self.call("POST", f"/adAccounts/{account}/adCampaigns", body)["id"]

    def upload(self, org, path, kind="image"):
        """kind: image or document. Returns the asset URN."""
        init = self.call("POST", f"/{kind}s", {"initializeUploadRequest": {"owner": f"urn:li:organization:{org}"}},
                         query="action=initializeUpload")["value"]
        raw = open(path, "rb").read() if self.live else b"x" * os.path.getsize(path)
        self.call("PUT", "", raw=raw, url=init["uploadUrl"])
        return init[kind]

    def dark_post(self, org, account, intro, headline, asset_urn, url, cta, name):
        body = {
            "author": f"urn:li:organization:{org}", "commentary": intro, "visibility": "PUBLIC",
            "distribution": {"feedDistribution": "NONE", "targetEntities": [], "thirdPartyDistributionChannels": []},
            "content": {"media": {"title": headline, "id": asset_urn}},
            "contentLandingPage": url, "contentCallToActionLabel": cta,
            "lifecycleState": "PUBLISHED", "isReshareDisabledByAuthor": False,
            "adContext": {"dscAdAccount": f"urn:li:sponsoredAccount:{account}", "dscStatus": "ACTIVE", "dscName": name},
        }
        return self.call("POST", "/posts", body)["id"]

    def creative(self, account, campaign_id, post_urn, name):
        body = {"campaign": f"urn:li:sponsoredCampaign:{campaign_id}", "content": {"reference": post_urn},
                "intendedStatus": "PAUSED", "name": name}
        return self.call("POST", f"/adAccounts/{account}/creatives", body)["id"]

    def set_creative_status(self, account, creative_id, status):
        """status: ACTIVE, PAUSED or ARCHIVED. ACTIVE spends money: only on the owner's yes."""
        urn = urllib.parse.quote(f"urn:li:sponsoredCreative:{creative_id}", safe="")
        return self.call("POST", f"/adAccounts/{account}/creatives/{urn}", {"patch": {"$set": {"intendedStatus": status}}},
                         headers={"X-RestLi-Method": "PARTIAL_UPDATE"})

    # ---------------------------------------------------------------- read

    def _pages(self, path, query):
        """Every element of a paged search."""
        out, token = [], None
        while True:
            q = query + "&pageSize=100" + (f"&pageToken={urllib.parse.quote(token)}" if token else "")
            res = self.call("GET", path, query=q)
            out += res.get("elements", [])
            token = (res.get("metadata") or {}).get("nextPageToken")
            if not token or not self.live:
                return out

    def ad_accounts(self):
        return self._pages("/adAccounts", "q=search")

    def campaigns(self, account):
        return self._pages(f"/adAccounts/{account}/adCampaigns", "q=search")

    def creatives(self, account, campaign_ids):
        ids = ",".join(urllib.parse.quote(f"urn:li:sponsoredCampaign:{c}", safe="") for c in campaign_ids)
        return self._pages(f"/adAccounts/{account}/creatives", f"q=criteria&campaigns=List({ids})")

    def post(self, urn):
        return self.call("GET", "/posts/" + urllib.parse.quote(urn, safe=""), soft=True)

    def typeahead(self, facet, query):
        q = urllib.parse.urlencode({"q": "typeahead", "facet": f"urn:li:adTargetingFacet:{facet}", "query": query, "locale": "(language:en,country:US)"}, safe="():,")
        return self.call("GET", "/adTargetingEntities", query=q)

    def analytics(self, account, start, end):
        """Daily metrics per creative between two dates (YYYY-MM-DD)."""
        y1, m1, d1 = (int(x) for x in start.split("-"))
        y2, m2, d2 = (int(x) for x in end.split("-"))
        acct = urllib.parse.quote(f"urn:li:sponsoredAccount:{account}", safe="")
        q = (f"q=analytics&pivot=CREATIVE&timeGranularity=DAILY"
             f"&dateRange=(start:(year:{y1},month:{m1},day:{d1}),end:(year:{y2},month:{m2},day:{d2}))"
             f"&accounts=List({acct})&fields={','.join(METRICS)}")
        return self.call("GET", "/adAnalytics", query=q).get("elements", [])


def refresh_access_token():
    """Trade a refresh token (valid about a year) for a fresh access token (valid 60 days). Nothing is written to disk."""
    data = urllib.parse.urlencode({"grant_type": "refresh_token", "refresh_token": os.environ["LINKEDIN_REFRESH_TOKEN"],
                                   "client_id": os.environ.get("LINKEDIN_CLIENT_ID", ""),
                                   "client_secret": os.environ.get("LINKEDIN_CLIENT_SECRET", "")}).encode()
    req = urllib.request.Request("https://www.linkedin.com/oauth/v2/accessToken", data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())["access_token"]
    except urllib.error.HTTPError as e:
        raise SystemExit(f"LinkedIn refused the refresh token ({e.code}): {e.read().decode()[:300]}")


def targeting(shared, persona):
    """audiences.json persona -> targetingCriteria. Facets with URNs only; labels are for people."""
    ands = [{"or": {"urn:li:adTargetingFacet:locations": shared["locations"]}}]
    sizes = persona.get("company_size_override") or shared.get("company_size") or []
    if sizes:
        ands.append({"or": {"urn:li:adTargetingFacet:staffCountRanges": [f"urn:li:staffCountRange:{STAFF[s]}" for s in sizes]}})
    for key, facet in (("functions", "jobFunctions"), ("seniorities", "seniorities"), ("titles", "titles"),
                       ("industries", "industries"), ("skills", "skills")):
        if persona.get(key):
            ands.append({"or": {f"urn:li:adTargetingFacet:{facet}": persona[key]}})
    crit = {"include": {"and": ands}}
    excl = shared.get("exclude", {}).get("matched_audiences") or []
    if excl:
        crit["exclude"] = {"or": {"urn:li:adTargetingFacet:audienceMatchingSegments": excl}}
    return crit
