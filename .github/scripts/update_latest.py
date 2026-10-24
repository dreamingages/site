#!/usr/bin/env python3
"""Keep the home page's "Tonight's newest episode" block pointing at the newest public long episode.

Source: the public RSS feed of the Full Episodes playlist (long episodes only, curated newest first; the feed
lists PUBLIC videos only, so private/scheduled uploads never appear). Entry 1 = newest episode.
Safety checks before anything changes: oEmbed must answer 200 (public + embeddable) and must not be portrait
(a Short). Duration words are stripped from the shown title. Any failure -> exit 0 with no change, so the
static block already in index.html (the last good episode) stays live.
Rewrites only the text between <!--LATEST:START--> and <!--LATEST:END--> in index.html, writes latest.json,
and saves the thumbnail as img/yt/<ID>.webp (960x540) if missing. Prints CHANGED/UNCHANGED.
Also owns the "Latest episodes" list (<ul class="eps"> in section h-latest): EVERY public long episode in the same
feed, newest first by its YouTube publish date (not playlist order), linked to its /episodes/<slug>/ page (slug found
by the video ID embedded in each episode page), with a rounded duration from that page's PT..H..M..S. Private or
scheduled videos (e.g. a premiere before launch) are never in the feed, so they never appear. Thumbnails
img/yt/<ID>-320.webp are made if missing. 24 Oct 2026: replaces the hand-kept CANDIDATES list in build_staging2.py.
Standard library + Pillow only."""
import html, io, json, os, re, sys, urllib.request
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLAYLIST = "PLOHsZ3iVZVdw"  # Full Episodes
FEED = f"https://www.youtube.com/feeds/videos.xml?playlist_id={PLAYLIST}"
INDEX = os.path.join(ROOT, "index.html")
LATEST_JSON = os.path.join(ROOT, "latest.json")
NS = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015"}
UA = {"User-Agent": "Mozilla/5.0 (dreamingages.com latest-episode updater)"}
DUR = re.compile(r"\s*[\(\[|·\-–—,:]*\s*\b\d+(?:\.\d+)?\s*(?:\+\s*)?[-\s]?(?:hours?|hrs?|minutes?|mins?)\b(?:\s*long)?\s*[\)\]]?", re.I)

def get(url, timeout=20):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()

def clean_title(t):
    t = DUR.sub(" ", t)
    t = re.sub(r"\s{2,}", " ", t).strip(" -–—|·:,")
    return t.strip()

def pick():
    root = ET.fromstring(get(FEED))
    for e in root.findall("a:entry", NS):
        vid = e.findtext("yt:videoId", namespaces=NS)
        title = e.findtext("a:title", namespaces=NS) or ""
        if not vid or not re.fullmatch(r"[A-Za-z0-9_-]{11}", vid):
            continue
        try:
            o = json.loads(get(f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={vid}&format=json"))
        except Exception as ex:
            print(f"skip {vid}: oEmbed failed ({ex})"); continue
        if int(o.get("height") or 0) > int(o.get("width") or 1):
            print(f"skip {vid}: portrait (Short)"); continue
        return vid, clean_title(o.get("title") or title)
    return None, None

EPS_RX = re.compile(r'(<section aria-labelledby="h-latest">\s*<h2 id="h-latest">[^<]*</h2>\s*<ul class="eps">)(.*?)(</ul>)', re.S)

def all_public():
    """Every usable feed entry: [(vid, title, published_iso)], in feed order."""
    root = ET.fromstring(get(FEED))
    out = []
    for e in root.findall("a:entry", NS):
        vid = e.findtext("yt:videoId", namespaces=NS)
        title = e.findtext("a:title", namespaces=NS) or ""
        pub = e.findtext("a:published", namespaces=NS) or ""
        if not vid or not re.fullmatch(r"[A-Za-z0-9_-]{11}", vid) or not pub:
            continue
        try:
            o = json.loads(get(f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={vid}&format=json"))
        except Exception as ex:
            print(f"skip {vid}: oEmbed failed ({ex})"); continue
        if int(o.get("height") or 0) > int(o.get("width") or 1):
            print(f"skip {vid}: portrait (Short)"); continue
        out.append((vid, clean_title(o.get("title") or title), pub))
    return out

def episode_pages():
    """{video id: (slug, seconds or None)} from the episode pages already in the repo."""
    res = {}
    d = os.path.join(ROOT, "episodes")
    for slug in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        f = os.path.join(d, slug, "index.html")
        if not os.path.isfile(f):
            continue
        t = open(f, encoding="utf-8").read()
        m = re.search(r"youtube-nocookie\.com/embed/([A-Za-z0-9_-]{11})", t)
        if not m:
            continue
        sec = None
        dm = re.search(r'"duration":\s*"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?"', t)
        if dm:
            sec = int(dm.group(1) or 0) * 3600 + int(dm.group(2) or 0) * 60 + int(dm.group(3) or 0)
        res[m.group(1)] = (slug, sec)
    return res

def human(sec):
    m = (sec + 30) // 60  # nearest minute, as the list has always shown
    return f"{m // 60} hr {m % 60} min" if m >= 60 else f"{m} min"

def thumb320(vid):
    out = os.path.join(ROOT, "img", "yt", f"{vid}-320.webp")
    if os.path.exists(out):
        return True
    try:
        from PIL import Image
        src = os.path.join(ROOT, "img", "yt", f"{vid}.webp")
        im = Image.open(src).convert("RGB") if os.path.exists(src) else None
        if im is None:
            for name in ("maxresdefault", "sddefault", "hqdefault"):
                try:
                    im = Image.open(io.BytesIO(get(f"https://i.ytimg.com/vi/{vid}/{name}.jpg"))).convert("RGB")
                except Exception:
                    continue
                if im.width >= 400:
                    break
                im = None
        if im is None:
            return False
        w, h = im.size
        th = int(w * 9 / 16)
        im = im.crop((0, (h - th) // 2, w, (h - th) // 2 + th)).resize((320, 180), Image.LANCZOS)
        im.save(out, "WEBP", quality=80, method=6)
        return True
    except Exception as ex:
        print(f"thumb320 {vid} failed: {ex}"); return False

def eps_list(entries):
    pages = episode_pages()
    items = []
    for vid, title, pub in sorted(entries, key=lambda x: x[2], reverse=True):
        if not thumb320(vid):
            print(f"list skip {vid}: no thumbnail"); continue
        slug, sec = pages.get(vid, (None, None))
        href = f"/episodes/{slug}/" if slug else f"https://www.youtube.com/watch?v={vid}&amp;list={PLAYLIST}"
        t = html.escape(title.replace(" | History for Sleep", "").strip(), quote=False)
        small = f"<small>{human(sec)}</small>" if sec else ""
        items.append(f'<li><a href="{href}"><img src="/img/yt/{vid}-320.webp" alt="" loading="lazy" width="96" height="54"><span class="t">{t}{small}</span></a></li>')
    return "".join(items)

def thumb(vid):
    out = os.path.join(ROOT, "img", "yt", f"{vid}.webp")
    if os.path.exists(out):
        return
    from PIL import Image
    for name in ("maxresdefault", "sddefault", "hqdefault"):
        try:
            im = Image.open(io.BytesIO(get(f"https://i.ytimg.com/vi/{vid}/{name}.jpg"))).convert("RGB")
        except Exception:
            continue
        if im.width < 400:
            continue
        w, h = im.size  # crop to 16:9 (sd/hq have letterbox bars), then 960x540
        th = int(w * 9 / 16)
        im = im.crop((0, (h - th) // 2, w, (h - th) // 2 + th)).resize((960, 540), Image.LANCZOS)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        im.save(out, "WEBP", quality=82, method=6)
        return
    raise RuntimeError("no thumbnail")

def block(vid, title):
    t = html.escape(title, quote=True)
    watch = f"https://www.youtube.com/watch?v={vid}&amp;list={PLAYLIST}"
    return (
        '<!--LATEST:START-->\n'
        f'<div class="vid hero-vid"><button type="button" class="yt" aria-label="Play: {t}" onclick="var t=this.nextElementSibling;this.parentNode.replaceChild(t.content.cloneNode(true),this);t.remove()"><img src="/img/yt/{vid}.webp" alt="" width="960" height="540" decoding="async" fetchpriority="high"><span class="yt-play" aria-hidden="true"></span></button><template><iframe src="https://www.youtube-nocookie.com/embed/{vid}?list={PLAYLIST}&amp;rel=0&amp;autoplay=1" title="{t}" allow="autoplay; accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></template></div>\n'
        f'<p class="vid-title"><a href="{watch}">{t}</a></p>\n'
        '<p class="yt-note">Plays from YouTube, which may set cookies. <a href="/privacy/#cookies">Privacy</a></p>\n'
        f'<p class="play"><a class="btn big" href="{watch}"><span class="tri" aria-hidden="true"></span>Watch on YouTube</a></p>\n'
        '<!--LATEST:END-->'
    )

def main():
    try:
        vid, title = pick()
    except Exception as ex:
        print(f"UNCHANGED (feed error: {ex})"); return
    if not vid:
        print("UNCHANGED (no usable entry)"); return
    s = open(INDEX, encoding="utf-8").read()
    m = re.search(r"<!--LATEST:START-->.*?<!--LATEST:END-->", s, re.S)
    if not m:
        print("UNCHANGED (markers missing)"); sys.exit(1)
    new = block(vid, title)
    s2 = s
    if m.group(0) != new:
        try:
            thumb(vid)
        except Exception as ex:
            print(f"UNCHANGED (thumbnail failed: {ex})"); return
        s2 = s[:m.start()] + new + s[m.end():]
    # the "Latest episodes" list: every public long episode, newest first (guarded: needs the section and >= 3 items)
    try:
        lst = eps_list(all_public())
        if lst.count("<li>") >= 3 and len(EPS_RX.findall(s2)) == 1:
            s2 = EPS_RX.sub(lambda mm: mm.group(1) + lst + mm.group(3), s2)
        else:
            print("list not updated (section missing or fewer than 3 episodes)")
    except Exception as ex:
        print(f"list not updated ({ex})")
    if s2 == s:
        print(f"UNCHANGED {vid}"); return
    open(INDEX, "w", encoding="utf-8").write(s2)
    json.dump({"id": vid, "title": title, "url": f"https://www.youtube.com/watch?v={vid}&list={PLAYLIST}"},
              open(LATEST_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"CHANGED {vid} {title}")

if __name__ == "__main__":
    main()
