"""Search Wikimedia Commons for CC0 / public-domain images and videos.

Usage: commons_search.py OUT.json "QUERY" ["QUERY" ...]
Keeps only files whose license is CC0 or public domain (incl. US-government works),
and at least 1600px wide (images) or 1280px (videos).
"""
import json, re, subprocess, sys, time, urllib.parse

UA = "VSL-broll-research/1.0 (pkdigitalldreamers@gmail.com)"
API = "https://commons.wikimedia.org/w/api.php"

def api(params):
    url = API + "?" + urllib.parse.urlencode({**params, "format": "json"})
    for k in range(6):  # Commons rate-limits shared IPs hard (HTTP 429): back off generously
        r = subprocess.run(["curl", "-sS", "-m", "60", "-A", UA, url], capture_output=True, text=True)
        try: return json.loads(r.stdout)
        except ValueError: time.sleep(45 * (k + 1))
    return {}

def free(meta):
    lic = (meta.get("LicenseShortName", {}).get("value", "") + " " + meta.get("License", {}).get("value", "")).lower()
    return "cc0" in lic or "public domain" in lic or lic.strip().startswith("pd")

out, queries = sys.argv[1], sys.argv[2:]
found = {}
for q in queries:
    d = api({"action": "query", "generator": "search", "gsrsearch": q, "gsrnamespace": 6, "gsrlimit": 30,
             "prop": "imageinfo", "iiprop": "url|size|extmetadata|mime", "iiurlwidth": 480})
    n = 0
    for p in d.get("query", {}).get("pages", {}).values():
        ii = (p.get("imageinfo") or [{}])[0]
        meta = ii.get("extmetadata", {})
        video = ii.get("mime", "").startswith("video")
        if not free(meta) or ii.get("width", 0) < (1280 if video else 1600): continue
        desc = re.sub("<[^>]+>", "", meta.get("ImageDescription", {}).get("value", ""))[:160]
        found.setdefault(p["title"], {"title": p["title"], "url": ii.get("url"), "page": ii.get("descriptionurl"),
                                      "thumb": ii.get("thumburl"), "w": ii.get("width"), "h": ii.get("height"),
                                      "mime": ii.get("mime"), "license": meta.get("LicenseShortName", {}).get("value", ""),
                                      "artist": re.sub("<[^>]+>", "", meta.get("Artist", {}).get("value", ""))[:80],
                                      "desc": desc, "queries": []})["queries"].append(q)
        n += 1
    print(f"{q}: {n}", file=sys.stderr, flush=True)
    json.dump(list(found.values()), open(out, "w"), indent=1)  # keep partial results
    time.sleep(12)
json.dump(list(found.values()), open(out, "w"), indent=1)
print(f"{len(found)} free files")
