"""Fetch URLs one at a time with backoff (Wikimedia rate-limits this sandbox's shared IP).

Usage: fetch_slow.py CANDIDATES.json OUTDIR FIELD [DELAY_S]
Saves each candidate's FIELD url to OUTDIR/<id>.<ext>; skips files already fetched.
For Commons originals it asks for the cached 3840px / 1920px thumbnail first: originals are
throttled far harder than standard thumbnail sizes.
"""
import json, os, subprocess, sys, time
UA = "Mozilla/5.0 (X11; Linux x86_64) VSL-broll-research pkdigitalldreamers@gmail.com"
cands, out, field = json.load(open(sys.argv[1])), sys.argv[2], sys.argv[3]
delay = float(sys.argv[4]) if len(sys.argv) > 4 else 4
os.makedirs(out, exist_ok=True)
for c in cands:
    url = c[field].split("?")[0]
    p = os.path.join(out, f'{c["id"]}{os.path.splitext(url)[1].lower() or ".bin"}')
    if os.path.exists(p) and os.path.getsize(p) > 5000: continue
    urls = [url]
    if "/wikipedia/commons/" in url and "/thumb/" not in url:
        rel = url.split("/wikipedia/commons/")[1]; name = rel.split("/")[-1]
        urls = [f"https://upload.wikimedia.org/wikipedia/commons/thumb/{rel}/{w}px-{name}"
                for w in (3840, 1920) if w < c.get("w", 99999)] + [url]
    for k in range(6):
        r = subprocess.run(["curl", "-sS", "-m", "300", "-A", UA, "-o", p, "-w", "%{http_code}", urls[min(k, len(urls) - 1)]],
                           capture_output=True, text=True)
        if r.stdout == "200": break
        time.sleep(5 if k < len(urls) - 1 else 30 * (k + 1))
    print(c["id"], r.stdout, flush=True)
    time.sleep(delay)
