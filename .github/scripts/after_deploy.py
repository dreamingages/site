#!/usr/bin/env python3
"""After a site change goes live (Dreaming Ages, Ian approved 22 Oct 2026 5:10 PM ET). Runs only on GitHub Actions.
  1. Wait (up to ~10 min) until GitHub Pages has built the commit we are on (pages/builds/latest), then until the live
     sitemap.xml equals the committed one.
  2. IndexNow: tell Bing, Yandex and the other IndexNow engines which sitemap URLs changed between BEFORE and HEAD
     (key file /cc3be8ab57eb7e3627d8ba5b5b3cbac3.txt in this repo). Cloudflare Crawler Hints cannot do this for us because
     the site is served by GitHub Pages with DNS-only (grey cloud) records, so Cloudflare never sees the pages.
  3. Search Console sitemaps.submit for sc-domain:dreamingages.com with secret GSC_SA_KEY (never printed); read back lastSubmitted.
Exit code: 1 only if the Search Console submit failed (shows red in Actions; the Pages deploy is a separate workflow and
is never affected). IndexNow problems are warnings. Everything is written to the job summary.
Env: BEFORE (sha), GITHUB_TOKEN, GITHUB_REPOSITORY, GSC_SA_KEY (optional), GITHUB_STEP_SUMMARY."""
import json, os, re, subprocess, sys, time, urllib.parse, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_sitemap  # noqa: E402
SITE, HOST = "https://dreamingages.com", "dreamingages.com"
GSC_SITE, FEED = "sc-domain:dreamingages.com", "https://dreamingages.com/sitemap.xml"
INDEXNOW_KEY = "cc3be8ab57eb7e3627d8ba5b5b3cbac3"
summary = []

def log(msg, level=None):
    print(f"::{level}::{msg}" if level else msg); summary.append(("⚠️ " if level else "") + msg)

def git(*a):
    return subprocess.run(["git", "-C", ROOT, *a], capture_output=True, text=True).stdout.strip()

def http(url, data=None, headers=None, method=None, timeout=30):
    r = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    with urllib.request.urlopen(r, timeout=timeout) as resp: return resp.status, resp.read().decode("utf-8", "replace")

def wait_pages(sha):
    tok, repo = os.environ.get("GITHUB_TOKEN"), os.environ.get("GITHUB_REPOSITORY", "dreamingages/site")
    if not tok: log("no GITHUB_TOKEN: skipping the Pages build wait"); return
    for _ in range(40):
        try:
            _, body = http(f"https://api.github.com/repos/{repo}/pages/builds/latest",
                           headers={"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json"})
            b = json.loads(body)
            if b.get("commit") == sha and b.get("status") == "built": log(f"GitHub Pages built {sha[:7]}"); return
            if b.get("commit") == sha and b.get("status") == "errored": log(f"GitHub Pages build errored for {sha[:7]}", "warning"); return
        except Exception as e: print("pages wait:", e.__class__.__name__)
        time.sleep(15)
    log(f"GitHub Pages had not finished building {sha[:7]} after 10 min; continuing", "warning")

def wait_live_sitemap():
    want = open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8").read()
    for _ in range(20):
        try:
            _, live = http(f"{FEED}?nc={time.time():.0f}", headers={"Cache-Control": "no-cache", "User-Agent": "dreamingages-sitemap-bot"})
            if live == want: log("live sitemap.xml matches the commit"); return
        except Exception as e: print("live fetch:", e.__class__.__name__)
        time.sleep(15)
    log("live sitemap.xml still differs from the commit after 5 min; submitting anyway (Google re-fetches later)", "warning")

def changed_urls(before):
    found = build_sitemap.pages()  # url -> repo-relative file
    if not before or set(before) == {"0"}: return []
    files = set(git("diff", "--name-only", before, "HEAD").splitlines())
    if not files and git("cat-file", "-t", before) != "commit": log(f"BEFORE {before[:7]} unknown; IndexNow skipped", "warning"); return []
    urls = sorted(u for u, rel in found.items() if rel in files)
    return urls

def indexnow(urls):
    if not urls: log("IndexNow: no indexable page changed, nothing to send"); return
    body = json.dumps({"host": HOST, "key": INDEXNOW_KEY, "keyLocation": f"{SITE}/{INDEXNOW_KEY}.txt", "urlList": urls[:10000]}).encode()
    try:
        st, txt = http("https://api.indexnow.org/indexnow", data=body, headers={"Content-Type": "application/json; charset=utf-8"}, method="POST")
        log(f"IndexNow: HTTP {st} for {len(urls)} URL(s): " + ", ".join(u.replace(SITE, "") or "/" for u in urls))
    except urllib.error.HTTPError as e:
        log(f"IndexNow: HTTP {e.code} {e.read().decode('utf-8','replace')[:200]}", "warning")
    except Exception as e:
        log(f"IndexNow: {e.__class__.__name__}", "warning")

def gsc_submit():
    key = os.environ.get("GSC_SA_KEY", "").strip()
    if not key: log("Search Console: GSC_SA_KEY secret not set, submit skipped", "warning"); return False
    from google.oauth2 import service_account
    from google.auth.transport.requests import AuthorizedSession
    creds = service_account.Credentials.from_service_account_info(json.loads(key), scopes=["https://www.googleapis.com/auth/webmasters"])
    s = AuthorizedSession(creds)
    base = f"https://www.googleapis.com/webmasters/v3/sites/{urllib.parse.quote(GSC_SITE, safe='')}/sitemaps/{urllib.parse.quote(FEED, safe='')}"
    for attempt in range(3):
        try:
            r = s.put(base, timeout=30)
            if r.status_code in (200, 204):
                g = s.get(base, timeout=30).json()
                log(f"Search Console: submitted (HTTP {r.status_code}); lastSubmitted {g.get('lastSubmitted')}, errors {g.get('errors')}, warnings {g.get('warnings')}")
                return True
            err = f"HTTP {r.status_code} {(r.text or '')[:200]}"
        except Exception as e: err = e.__class__.__name__
        time.sleep(20 * (attempt + 1))
    log(f"Search Console submit FAILED: {err}", "error"); return False

def main():
    sha = git("rev-parse", "HEAD")
    wait_pages(sha); wait_live_sitemap()
    indexnow(changed_urls(os.environ.get("BEFORE", "").strip()))
    ok = gsc_submit()
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write("### After deploy\n" + "\n".join(f"- {x}" for x in summary) + "\n")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
