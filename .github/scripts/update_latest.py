#!/usr/bin/env python3
"""Keep the home page's "Tonight's newest episode" block pointing at the newest public long episode.

Source: the public RSS feed of the Full Episodes playlist (long episodes only, curated newest first; the feed
lists PUBLIC videos only, so private/scheduled uploads never appear). Entry 1 = newest episode.
Safety checks before anything changes: oEmbed must answer 200 (public + embeddable) and must not be portrait
(a Short). Duration words are stripped from the shown title. Any failure -> exit 0 with no change, so the
static block already in index.html (the last good episode) stays live.
Rewrites only the text between <!--LATEST:START--> and <!--LATEST:END--> in index.html, writes latest.json,
and saves the thumbnail as img/yt/<ID>.webp (960x540) if missing. Prints CHANGED/UNCHANGED.
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
    if m.group(0) == new:
        print(f"UNCHANGED {vid}"); return
    try:
        thumb(vid)
    except Exception as ex:
        print(f"UNCHANGED (thumbnail failed: {ex})"); return
    open(INDEX, "w", encoding="utf-8").write(s[:m.start()] + new + s[m.end():])
    json.dump({"id": vid, "title": title, "url": f"https://www.youtube.com/watch?v={vid}&list={PLAYLIST}"},
              open(LATEST_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"CHANGED {vid} {title}")

if __name__ == "__main__":
    main()
