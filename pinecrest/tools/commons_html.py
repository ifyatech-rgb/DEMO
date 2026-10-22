"""Wikimedia Commons search via the ordinary HTML pages (the API is rate-limited for this sandbox).

Usage: commons_html.py OUT.json "QUERY" ["QUERY" ...]
For each query: Special:Search (files only) -> each File: page -> keep CC0 / public-domain files at
least 1500px wide (or videos) -> record license, author, size and a thumb.php thumbnail URL.
"""
import html, json, re, subprocess, sys, time, urllib.parse

UA = "Mozilla/5.0 (X11; Linux x86_64) VSL-broll-research pkdigitalldreamers@gmail.com"
BASE = "https://commons.wikimedia.org"

def get(url):
    for k in range(4):
        r = subprocess.run(["curl", "-sSL", "-m", "60", "-A", UA, "-w", "\n%{http_code}", url], capture_output=True, text=True)
        body, _, code = r.stdout.rpartition("\n")
        if code == "200": return body
        time.sleep(20 * (k + 1))
    return ""

def thumb(name, w): return f"{BASE}/w/thumb.php?" + urllib.parse.urlencode({"f": name, "w": w})

out, queries = sys.argv[1], sys.argv[2:]
found, seen = {}, set()
try: found = {r["title"]: r for r in json.load(open(out))}; seen = set(found)
except (OSError, ValueError): pass
for q in queries:
    page = get(f"{BASE}/w/index.php?" + urllib.parse.urlencode({"search": q, "title": "Special:Search", "profile": "advanced",
                                                                  "fulltext": 1, "ns6": 1, "limit": 30}))
    titles = []
    for t in re.findall(r'title="(File:[^"]+\.(?:jpe?g|png|webm|ogv))"', page, re.I):
        t = html.unescape(t)
        if t not in titles: titles.append(t)
    kept = 0
    for t in titles[:12]:
        if t in seen: found[t]["queries"].append(q) if t in found else None; continue
        seen.add(t)
        fp = html.unescape(get(f"{BASE}/wiki/" + urllib.parse.quote(t.replace(" ", "_"))))
        lic = " ".join(re.findall(r'class="licensetpl_short[^"]*"[^>]*>([^<]+)<', fp))
        if not re.search(r"public domain|cc0|pd-", lic + " " + " ".join(re.findall(r'title="Category:([^"]+)"', fp)), re.I): continue
        sizes = [(int(a.replace(",", "")), int(b.replace(",", ""))) for a, b in re.findall(r"([\d,]+) × ([\d,]+) pixels", fp)]
        w, h = max(sizes) if sizes else (0, 0)   # largest listed size is the original
        video = t.lower().endswith((".webm", ".ogv"))
        if not video and w < 1500: continue
        art = re.search(r'id="fileinfotpl_aut"[^>]*>.*?</td>\s*<td[^>]*>(.*?)</td>', fp, re.S)
        desc = re.search(r'class="description[^"]*"[^>]*>(.*?)</div>', fp, re.S)
        name = t[5:]
        found[t] = {"title": t, "page": f"{BASE}/wiki/" + urllib.parse.quote(t.replace(" ", "_")), "w": w, "h": h, "video": video,
                    "license": (lic or "Public domain").strip(), "artist": re.sub("<[^>]+>|\\s+", " ", art.group(1)).strip()[:80] if art else "",
                    "desc": re.sub("<[^>]+>|\\s+", " ", desc.group(1)).strip()[:160] if desc else "",
                    "thumb": thumb(name, 480), "queries": [q]}
        kept += 1
        time.sleep(1.5)
    print(f"{q}: {len(titles)} files, {kept} free", file=sys.stderr, flush=True)
    json.dump(list(found.values()), open(out, "w"), indent=1)
    time.sleep(2)
print(f"{len(found)} free files")
