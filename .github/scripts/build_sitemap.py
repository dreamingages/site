#!/usr/bin/env python3
"""Rebuild sitemap.xml from the HTML pages actually in the repo (Dreaming Ages, 20 Oct 2026, Ian approved).
A page <dir>/index.html is listed as https://dreamingages.com/<dir>/ when ALL hold:
  - no <meta name="robots" ... noindex>   (premiere pages, subscriber library, private pages are noindex)
  - its <link rel="canonical"> points to that same URL
  - not under a robots.txt Disallow path (e.g. /p/), not 404.html, not in EXCLUDE (pages kept out on purpose)
Companion PDFs are listed only if the public /companions/ sample page links them (subscriber PDFs stay out).
lastmod = date of the file's last git commit (needs full history: actions/checkout fetch-depth 0).
Order: URLs already in the sitemap keep their place; new ones are appended in path order.
Video entries (22 Oct 2026): a page whose JSON-LD has a VideoObject also gets a Google video-sitemap block
(thumbnail_loc, title, description, player_loc = embedUrl, duration, publication_date, family_friendly), built from
that JSON-LD only, so nothing new is written. Spec: https://developers.google.com/search/docs/crawling-indexing/sitemaps/video-sitemaps
Prints CHANGED/UNCHANGED and the added/removed URLs. Standard library only."""
import os, re, subprocess, sys, json
from xml.sax.saxutils import escape
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = "https://dreamingages.com"
EXCLUDE = {"/privacy/", "/terms/"}  # never in the sitemap (legal pages, kept out since 16 Oct 2026)
SM = os.path.join(ROOT, "sitemap.xml")

def git_date(rel):
    out = subprocess.run(["git", "-C", ROOT, "log", "-1", "--format=%cs", "--", rel], capture_output=True, text=True).stdout.strip()
    return out or None

def disallowed():
    try: txt = open(os.path.join(ROOT, "robots.txt"), encoding="utf-8").read()
    except FileNotFoundError: return []
    return [d.strip() for d in re.findall(r"(?im)^\s*Disallow:\s*(\S+)", txt)]

def iso_secs(d):
    m = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", d or "")
    return sum(int(x or 0) * k for x, k in zip(m.groups(), (3600, 60, 1))) if m else None

def video_block(rel):
    """<video:video> XML for the page's VideoObject JSON-LD, or '' if it has none / lacks required fields."""
    try: html = open(os.path.join(ROOT, rel), encoding="utf-8", errors="replace").read()
    except OSError: return ""
    for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        try: j = json.loads(raw)
        except ValueError: continue
        items = j if isinstance(j, list) else j.get("@graph", [j])
        for v in items:
            if not isinstance(v, dict) or v.get("@type") != "VideoObject": continue
            th = v.get("thumbnailUrl"); th = th[0] if isinstance(th, list) and th else th
            name, desc, player = v.get("name"), v.get("description"), v.get("embedUrl")
            if not (th and name and desc and player): return ""
            x = ["<video:video>", f"<video:thumbnail_loc>{escape(th)}</video:thumbnail_loc>",
                 f"<video:title>{escape(name)}</video:title>", f"<video:description>{escape(desc[:2048])}</video:description>",
                 f"<video:player_loc>{escape(player)}</video:player_loc>"]
            sec = iso_secs(v.get("duration"))
            if sec and 1 <= sec <= 28800: x.append(f"<video:duration>{sec}</video:duration>")
            if v.get("uploadDate"): x.append(f"<video:publication_date>{escape(v['uploadDate'])}</video:publication_date>")
            if v.get("isFamilyFriendly") is True: x.append("<video:family_friendly>yes</video:family_friendly>")
            x.append("</video:video>")
            return "".join(x)
    return ""

def pages():
    dis = disallowed()
    found = {}
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [d for d in dn if not d.startswith(".")]
        if "index.html" not in fn: continue
        rel = os.path.relpath(os.path.join(dp, "index.html"), ROOT).replace(os.sep, "/")
        url_path = "/" + rel[:-len("index.html")]
        if url_path in EXCLUDE or any(url_path.startswith(d) for d in dis): continue
        head = open(os.path.join(dp, "index.html"), encoding="utf-8", errors="replace").read().split("</head>", 1)[0]
        if re.search(r'<meta\s+name=["\']robots["\'][^>]*noindex', head, re.I): continue
        can = re.search(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)["\']', head, re.I)
        if not can or can.group(1) != SITE + url_path: continue
        found[SITE + url_path] = rel
    comp = os.path.join(ROOT, "companions", "index.html")
    if os.path.exists(comp) and SITE + "/companions/" in found:
        for href in re.findall(r'href="(/companions/[a-z0-9-]+\.pdf)"', open(comp, encoding="utf-8").read()):
            if os.path.exists(os.path.join(ROOT, href.lstrip("/"))): found[SITE + href] = href.lstrip("/")
    return found

def main():
    found = pages()
    old = open(SM, encoding="utf-8").read() if os.path.exists(SM) else ""
    old_urls = re.findall(r"<loc>([^<]+)</loc>", old)
    order = [u for u in old_urls if u in found] + sorted(u for u in found if u not in old_urls)
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">']
    for u in order:
        d = git_date(found[u])
        lines.append(f"  <url><loc>{u}</loc>" + (f"<lastmod>{d}</lastmod>" if d else "") + video_block(found[u]) + "</url>")
    lines.append("</urlset>")
    new = "\n".join(lines) + "\n"
    added = [u for u in order if u not in old_urls]; removed = [u for u in old_urls if u not in found]
    if "--check" in sys.argv:
        print(new, end=""); print(f"# {len(order)} URLs; added {added}; removed {removed}", file=sys.stderr); return
    if new == old: print(f"UNCHANGED ({len(order)} URLs)"); return
    open(SM, "w", encoding="utf-8").write(new)
    print(f"CHANGED ({len(order)} URLs) added={added} removed={removed}")

if __name__ == "__main__":
    main()
