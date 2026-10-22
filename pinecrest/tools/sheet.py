"""Download candidate thumbnails and tile them into labeled contact sheets.

Usage: sheet.py CANDIDATES.json THUMBDIR OUTPREFIX [PER_SHEET]
Each candidate needs "id" (or "title") and "thumb". Labels show id + short title.
"""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
cands, tdir, prefix = json.load(open(sys.argv[1])), sys.argv[2], sys.argv[3]
per = int(sys.argv[4]) if len(sys.argv) > 4 else 30
os.makedirs(tdir, exist_ok=True)
def key(c): return str(c.get("id") or abs(hash(c["title"])) % 10**6)
def fetch(c):
    p = os.path.join(tdir, key(c) + ".jpg")
    if not os.path.exists(p):
        subprocess.run(["curl", "-sS", "-m", "30", "-A", "VSL-broll-research/1.0", "-o", p, c["thumb"]], capture_output=True)
    return p
with ThreadPoolExecutor(8) as ex: paths = list(ex.map(fetch, cands))
for s in range(0, len(cands), per):
    args = []
    for c, p in zip(cands[s:s + per], paths[s:s + per]):
        if os.path.exists(p) and open(p, "rb").read(3) == b"\xff\xd8\xff":
            args += ["-label", f"{key(c)} {(c.get('title') or '')[:34]}", p]
    out = f"{prefix}-{s // per + 1}.jpg"
    subprocess.run(["montage", *args, "-tile", "6x", "-geometry", "300x169+4+4", "-pointsize", "13", "-background", "#222",
                    "-fill", "white", out], check=True)
    print(out)
