#!/usr/bin/env python3
"""Get a LinkedIn API token on your own computer, without LinkedIn's token generator page.

  python3 ads/engine/oauth.py

Run it on the computer where you are signed in to LinkedIn (not in a cloud session). Before the first run,
add this redirect URL to your app (developer portal, your app, Auth tab, Authorized redirect URLs):

  http://localhost:8765/callback

It asks for the app's Client ID and Client Secret (Auth tab; the secret is typed hidden), opens LinkedIn's
approval page in your browser, catches LinkedIn's answer on localhost, checks it, trades it for a token and
prints the token here. Nothing is written to disk or sent anywhere but LinkedIn. Put the token in the
environment's settings as LINKEDIN_ACCESS_TOKEN (and the refresh token, if LinkedIn gives one, as
LINKEDIN_REFRESH_TOKEN with LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET). Never paste them into a chat.

Standard library only.
"""
import getpass
import http.server
import json
import os
import secrets
import sys
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

PORT = int(os.environ.get("LINKEDIN_OAUTH_PORT", "8765"))
REDIRECT = f"http://localhost:{PORT}/callback"
SCOPES = os.environ.get("LINKEDIN_SCOPES", "r_ads rw_ads r_ads_reporting w_organization_social")


def auth_url(client_id, state, scopes=SCOPES):
    return "https://www.linkedin.com/oauth/v2/authorization?" + urllib.parse.urlencode(
        {"response_type": "code", "client_id": client_id, "redirect_uri": REDIRECT, "state": state, "scope": scopes})


def exchange(code, client_id, client_secret):
    data = urllib.parse.urlencode({"grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECT,
                                   "client_id": client_id, "client_secret": client_secret}).encode()
    req = urllib.request.Request("https://www.linkedin.com/oauth/v2/accessToken", data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        sys.exit(f"LinkedIn refused the exchange ({e.code}): {e.read().decode()[:400]}")


def wait_for_code(state):
    """Serve one request on localhost and return the code LinkedIn sends back."""
    got = {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlsplit(self.path).query)
            if not self.path.startswith("/callback"):
                self.send_response(404)
                self.end_headers()
                return
            got.update({k: v[0] for k, v in q.items()})
            ok = "code" in got and got.get("state") == state
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            msg = "Done. Go back to the terminal." if ok else "Something went wrong. Go back to the terminal."
            self.wfile.write(f"<p style='font:16px sans-serif;margin:40px'>{msg}</p>".encode())

        def log_message(self, *args):
            pass

    with http.server.HTTPServer(("127.0.0.1", PORT), Handler) as srv:
        while "code" not in got and "error" not in got:
            srv.handle_request()
    if "error" in got:
        sys.exit(f"LinkedIn said: {got.get('error')}: {got.get('error_description', '')}")
    if got.get("state") != state:
        sys.exit("The answer's state did not match this run. Start again.")
    return got["code"]


def main():
    client_id = os.environ.get("LINKEDIN_CLIENT_ID") or input("Client ID: ").strip()
    client_secret = os.environ.get("LINKEDIN_CLIENT_SECRET") or getpass.getpass("Client Secret (hidden): ").strip()
    state = secrets.token_urlsafe(24)
    url = auth_url(client_id, state)
    print(f"\nOpening LinkedIn. If no browser opens, paste this into the browser where you're signed in:\n\n{url}\n")
    print(f"Make sure {REDIRECT} is in the app's Authorized redirect URLs, or LinkedIn will refuse.\n")
    webbrowser.open(url)
    code = wait_for_code(state)
    tok = exchange(code, client_id, client_secret)
    days = int(tok.get("expires_in", 0)) // 86400
    print("\nLINKEDIN_ACCESS_TOKEN (valid about", days, "days):\n")
    print(tok["access_token"])
    if tok.get("refresh_token"):
        rdays = int(tok.get("refresh_token_expires_in", 0)) // 86400
        print(f"\nLINKEDIN_REFRESH_TOKEN (valid about {rdays} days; store it with LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET):\n")
        print(tok["refresh_token"])
    print("\nScopes granted:", tok.get("scope", "(not listed)"))
    print("\nPut these in the environment's settings (cloud environment menu, Edit, environment variables). Not in a chat.")


if __name__ == "__main__":
    main()
