"""Fetch URLs one at a time with backoff (Wikimedia rate-limits this sandbox's shared IP).

Usage: fetch_slow.py CANDIDATES.json OUTDIR FIELD [DELAY_S]
Saves each candidate's FIELD url to OUTDIR/<id>.<ext>; skips files already fetched.
"""
import json, os, subprocess, sys, time
UA = "VSL-broll-research/1.0 (pkdigitalldreamers@gmail.com)"
cands, out, field = json.load(open(sys.argv[1])), sys.argv[2], sys.argv[3]
delay = float(sys.argv[4]) if len(sys.argv) > 4 else 4
os.makedirs(out, exist_ok=True)
for c in cands:
    url = c[field].split("?")[0]
    p = os.path.join(out, f'{c["id"]}{os.path.splitext(url)[1].lower() or ".bin"}')
    if os.path.exists(p) and os.path.getsize(p) > 5000: continue
    for k in range(6):
        r = subprocess.run(["curl", "-sS", "-m", "300", "-A", UA, "-o", p, "-w", "%{http_code}", url], capture_output=True, text=True)
        if r.stdout == "200": break
        time.sleep(30 * (k + 1))
    print(c["id"], r.stdout, flush=True)
    time.sleep(delay)
