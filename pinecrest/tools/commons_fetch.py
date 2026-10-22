"""Download Commons files via thumb.php (originals are throttled) and log them in broll/sources.txt.

Usage: commons_fetch.py CANDIDATES.json OUTDIR KEY=TITLE_SUBSTRING [...]
Each KEY becomes OUTDIR/KEY.jpg (max 2560 px wide).
"""
import json, os, subprocess, sys, time, urllib.parse
UA = "Mozilla/5.0 (X11; Linux x86_64) VSL-broll-research pkdigitalldreamers@gmail.com"
cands, outdir = json.load(open(sys.argv[1])), sys.argv[2]
os.makedirs(outdir, exist_ok=True)
log = open("broll/sources.txt", "a")
for spec in sys.argv[3:]:
    key, sub = spec.split("=", 1)
    r = next(c for c in cands if sub in c["title"])
    out = os.path.join(outdir, key + ".jpg")
    url = "https://commons.wikimedia.org/w/thumb.php?" + urllib.parse.urlencode({"f": r["title"][5:], "w": min(2560, r["w"])})
    for k in range(4):
        x = subprocess.run(["curl", "-sSL", "-m", "120", "-A", UA, "-o", out, "-w", "%{http_code}", url], capture_output=True, text=True)
        if x.stdout == "200" and open(out, "rb").read(3) == b"\xff\xd8\xff": break
        time.sleep(20 * (k + 1))
    print(key, x.stdout, os.path.getsize(out), flush=True)
    log.write(f"photos/{key}.jpg\tWikimedia Commons\t{r['page']}\t{r['license']} - author: {r.get('artist') or 'see page'}\n")
    time.sleep(2)
