"""Search Mixkit stock videos politely (sequential, throttled; Mixkit rate-limits bursts).

  mixkit_search.py list OUT.json TERM [TERM ...]   # listing pages -> {id, title, terms, thumb}
  mixkit_search.py license ID [ID ...]             # detail page -> Free/Restricted + HD sizes

Only clips under the Mixkit *Free* license (https://mixkit.co/license/#videoFree) may be used.
"""
import json, re, subprocess, sys, time

def get(url, tries=4):
    for k in range(tries):
        r = subprocess.run(["curl", "-sSL", "-m", "40", "-A", "Mozilla/5.0", "-w", "\n%{http_code}", url],
                           capture_output=True, text=True)
        body, _, code = r.stdout.rpartition("\n")
        if code == "200" and "cf_chl" not in body[:5000]: return body
        time.sleep(20 * (k + 1))
    return ""

def head_ok(url):
    r = subprocess.run(["curl", "-sSI", "-m", "20", "-o", "/dev/null", "-w", "%{http_code}", url], capture_output=True, text=True)
    return r.stdout.strip() == "200"

def listing(out, terms):
    found = {}
    for term in terms:
        slug = term.strip().lower().replace(" ", "-")
        html = get(f"https://mixkit.co/free-stock-video/discover/{slug}/")
        for vid, title in re.findall(r'item-id-value="(\d+)".*?overlay-video-title">\s*([^<]+?)\s*</span>', html, re.S):
            found.setdefault(vid, {"id": vid, "title": title, "terms": [],
                                   "thumb": f"https://assets.mixkit.co/videos/{vid}/{vid}-thumb-360-0.jpg"})["terms"].append(term)
        print(f"{term}: {len(html) and html.count('item-id-value')} items", file=sys.stderr)
        time.sleep(3)
    json.dump(list(found.values()), open(out, "w"), indent=1)
    print(f"{len(found)} unique clips")

def license(ids):
    for vid in ids:
        html = get(f"https://mixkit.co/free-stock-video/x-{vid}/")
        m = re.search(r'"license":"([^"]+)"', html)
        canon = re.search(r'<link rel="canonical" href="([^"]+)"', html)
        sizes = [s for s in ("2160", "1080", "720") if head_ok(f"https://assets.mixkit.co/videos/{vid}/{vid}-{s}.mp4")]
        print(json.dumps({"id": vid, "license": m.group(1) if m else "?", "url": canon.group(1) if canon else "", "sizes": sizes}))
        time.sleep(3)

if __name__ == "__main__":
    if sys.argv[1] == "list": listing(sys.argv[2], sys.argv[3:])
    else: license(sys.argv[2:])
