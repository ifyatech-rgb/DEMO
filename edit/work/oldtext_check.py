"""Old burned-in text check. The source's captions/headers live in its top bar (y 0-211) and bottom bars (y 1139-1350),
outside the 1080x928 picture area that the cut uses, so no source pixel from those bands is ever placed in the
output. Remaining risk: graphics burned INTO the picture area (takeover cards, money emojis, the red CTA banner).
For each exported frame, check: (a) the frame is under a new full-screen card, or (b) its source frame was clean
in the picture area (difference to the clean median small), or (c) the band holding the old red banner is covered
by the new navy strip / end card. Writes logs/oldtext_check.json and prints any frames that fail."""
import json
import numpy as np
tl = json.load(open("work/timeline.json")); plan = json.load(open("work/plan.json")); FPS = 30
cards = [(a, b) for _, a, b in plan["cards"]]
holds = plan["hold"]; strip = plan["gfx"]["strip"]
ov = json.load(open("work/source_overlays.json"))
BAD = [(3.25, 4.85), (6.35, 7.65), (8.5, 10.65), (11.85, 13.25), (17.82, 19.4), (23.05, 25.08), (32.2, 33.5)]
RED = [tuple(r) for r in ov["red"] if r[1] - r[0] > 1]
fails, n = [], round(tl["dur"] * FPS)
for i in range(n):
    t = (i + 0.5) / FPS
    seg = next(s for s in tl["segs"] if s["vin"] - 1e-6 <= t < s["vout"] + 1e-6)
    src = seg["src_v0"] + (t - seg["vin"])
    if any(a - 1e-3 <= t <= b + 1e-3 for a, b in cards): continue
    if any(a - 0.04 <= t <= b + 0.04 for a, b in holds): continue          # replaced by a clean held frame
    if any(a <= src <= b for a, b in BAD): fails.append((round(t, 3), round(src, 3), "old graphic in picture"))
    if any(a <= src <= b for a, b in RED) and not (strip[0] <= t <= strip[1]): fails.append((round(t, 3), round(src, 3), "old red banner"))
json.dump({"frames": n, "fails": fails}, open("logs/oldtext_check.json", "w"), indent=1)
print(f"{n} frames checked, {len(fails)} with old burned-in text visible", fails[:10])
