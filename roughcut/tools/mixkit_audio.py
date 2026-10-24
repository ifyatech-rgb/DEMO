"""List Mixkit sound effects or music tracks by tag (sequential + throttled; Mixkit rate-limits bursts).

  mixkit_audio.py sfx OUT.json TAG [TAG ...]     # https://mixkit.co/free-sound-effects/TAG/
  mixkit_audio.py music OUT.json TAG [TAG ...]   # https://mixkit.co/free-stock-music/tag/TAG/

All Mixkit SFX and music are under the Mixkit free licenses (#sfxFree, #musicFree).
"""
import json, re, subprocess, sys, time

def get(url, tries=3):
    for k in range(tries):
        r = subprocess.run(["curl", "-sSL", "-m", "40", "-A", "Mozilla/5.0", "-w", "\n%{http_code}", url], capture_output=True, text=True)
        body, _, code = r.stdout.rpartition("\n")
        if code == "200" and "cf_chl" not in body[:5000]: return body
        if code == "404": return ""
        time.sleep(15 * (k + 1))
    return ""

kind, out, tags = sys.argv[1], sys.argv[2], sys.argv[3:]
found = {}
for tag in tags:
    url = f"https://mixkit.co/free-sound-effects/{tag}/" if kind == "sfx" else f"https://mixkit.co/free-stock-music/tag/{tag}/"
    html = get(url)
    cards = html.split('data-controller="audio-player"')[1:]
    for c in cards:
        m = re.search(r'preview-url-value="([^"]+)"', c); t = re.search(r'item-grid-card__title">\s*([^<]+?)\s*<', c)
        d = re.search(r'data-test-id="duration">\s*([\d:]+)', c)
        if not m: continue
        iid = re.search(r'/(\d+)/[^/]*$', m.group(1)).group(1)
        found.setdefault(iid, dict(id=iid, title=t.group(1) if t else "?", dur=d.group(1) if d else "?", url=m.group(1), tags=[]))["tags"].append(tag)
    print(f"{tag}: {len(cards)} items", file=sys.stderr)
    time.sleep(3)
json.dump(list(found.values()), open(out, "w"), indent=1)
for v in found.values(): print(v["id"], v["dur"], v["title"], v["tags"])
