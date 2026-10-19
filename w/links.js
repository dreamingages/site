// Dreaming Ages short links: https://dreamingages.com/w/<slug>
// ONE line per episode:  "slug": ["YouTube video ID", "go-live time in UTC" or null if not set yet],
// Before go-live (or if null) the link opens the channel homepage; from go-live it opens the video.
// After adding a line, run /workspace/dreaming-ages/tools/shortlinks.py (creates the /w/<slug>/ page), commit, push.
var DA_LINKS = {
  "byzantium":    ["GAf-Lmkk8K0", "2026-10-19T21:00:00Z"],
  "allhallows":   ["Xu7BU5ZFYcI", null],
  "mesopotamia":  ["dQ1JFN4K7kk", "2026-10-21T21:00:00Z"],
  "dayofthedead": ["l17l1gyguGM", "2026-10-22T21:00:00Z"]
};
var DA_CHANNEL = "https://www.youtube.com/@DreamingAgesHistory";
var DA_LIST = "PLOHsZ3iVZVdw";
