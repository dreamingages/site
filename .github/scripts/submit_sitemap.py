#!/usr/bin/env python3
"""Submit https://dreamingages.com/sitemap.xml to Search Console (sc-domain:dreamingages.com) with the service
account JSON in env GSC_SA_KEY (GitHub Actions secret; never printed). Missing secret -> skip, exit 0.
First waits (up to ~6 min) until the live sitemap equals the committed one, so Google fetches the new version."""
import json, os, sys, time, urllib.parse, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = "sc-domain:dreamingages.com"; FEED = "https://dreamingages.com/sitemap.xml"
key = os.environ.get("GSC_SA_KEY", "").strip()
if not key:
    print("SKIP: GSC_SA_KEY secret not set (add it in repo Settings > Secrets and variables > Actions)"); sys.exit(0)
want = open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8").read()
for i in range(24):
    try:
        live = urllib.request.urlopen(urllib.request.Request(f"{FEED}?nc={time.time():.0f}", headers={"Cache-Control": "no-cache"}), timeout=20).read().decode()
        if live == want: print("live sitemap matches the commit"); break
    except Exception as e: print(f"live fetch: {e}")
    time.sleep(15)
else:
    print("note: live sitemap not updated yet after 6 min; submitting anyway (Google re-fetches later)")
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession
creds = service_account.Credentials.from_service_account_info(json.loads(key), scopes=["https://www.googleapis.com/auth/webmasters"])
s = AuthorizedSession(creds)
base = f"https://www.googleapis.com/webmasters/v3/sites/{urllib.parse.quote(SITE, safe='')}/sitemaps/{urllib.parse.quote(FEED, safe='')}"
r = s.put(base)
print(f"submit: HTTP {r.status_code}")
if r.status_code not in (200, 204):
    print((r.text or "")[:300]); sys.exit(1)
g = s.get(base).json()
print("lastSubmitted:", g.get("lastSubmitted"), "| errors:", g.get("errors"), "| warnings:", g.get("warnings"))
