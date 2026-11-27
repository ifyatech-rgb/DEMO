"""Graphics + camera plan on the output timeline (from work/timeline.json word times). Shared by the picture pass
(look.py: punch-ins, shake, hold-frames) and the overlay pass (remotion/gen.py: graphics, captions, end card).
Writes work/plan.json."""
import json
tl = json.load(open("work/timeline.json")); W = tl["words"]; DUR = tl["dur"]
def at(text, after=0.0):
    for w in W:
        if w["t"] >= after - 1e-6 and w["text"].lower().strip(",.?!").replace("-", "") == text.lower().replace("-", ""): return w["t"]
    raise SystemExit(f"word not found: {text}")
END0 = round(DUR - 2.5, 3)

# full-screen cards (cover every old burned-in graphic; each <= 1.6 s)
CARDS = [
    ("trash", 2.88, 4.26),
    ("sitdown", 5.70, 7.06),
    ("intent", 7.50, 8.42),
    ("noest", 9.55, 10.92),
    ("phone", 15.34, 16.38),
    ("calendar", 16.38, 17.95),
    ("end", END0, DUR),
]
def covered(a, b):   # is [a, b] inside the union of the cards?
    t = a
    while t < b - 1e-3:
        nxt = [cb for _, ca, cb in CARDS if ca - 1e-3 <= t < cb]
        if not nxt: return False
        t = max(nxt)
    return True
HOLD = []
for a, b in tl["cover"]:   # every old-graphic interval is under a card, or (<= 3 frames) fixed with a hold-frame
    if covered(a, b): continue
    if b - a > 0.1: raise SystemExit(f"old graphic at {a}-{b} not covered")
    HOLD.append((a, b))

# lower-zone / top-zone graphics (never over the face)
GFX = {
    "banner": (0.0, 2.5),
    "hook5to10": (at("5"), 2.88),
    "nametag": (0.5, 2.88),
    "noret": (at("no"), 9.55),
    "pinned": (10.92, at("we", 20.0)),
    "exclusive": (at("exclusive"), at("exclusive") + 1.6),
    "webook": (at("sifting") - 0.35, at("dirt") + 0.3),
    "ncmap": (at("we", 20.0), at("one")),
    "oneroofer": (at("one"), END0),
    "strip": (tl["red"][0][0] - 0.05, END0),   # navy lower strip that also hides the old red banner
}
# camera: relative scale keys (t, rel, ease) on top of the base framing; shots alternate 100/112/100/118
CAM = [
    (0.00, 1.00, "set"), (0.00, 1.06, ("push", 2.33)),
    (2.333, 1.12, "set"),
    (4.10, 1.00, "set"), (4.10, 1.07, ("push", 1.6)),
    (7.06, 1.18, "set"),
    (8.30, 1.00, "set"), (8.30, 1.06, ("push", 1.25)),
    (10.90, 1.12, "set"),
    (11.833, 1.00, "set"), (11.833, 1.05, ("push", 1.15)), (at("exclusive"), 1.20, ("punch", 0.2)),
    (14.50, 1.06, ("ease", 0.4)),
    (17.95, 1.12, "set"), (17.95, 1.18, ("push", 2.9)),
    (20.90, 1.12, "set"), (at("one"), 1.20, ("punch", 0.2)),
    (23.833, 1.00, "set"),
]
SHAKE = [(at("one") + 0.1, 2, 6)]   # (t, frames, px)
json.dump({"dur": DUR, "end0": END0, "cards": CARDS, "hold": HOLD, "gfx": GFX, "cam": CAM, "shake": SHAKE, "words": W},
          open("work/plan.json", "w"), indent=1)
print("cards", CARDS); print("hold", HOLD); print("gfx", GFX)
