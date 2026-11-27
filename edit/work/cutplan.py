"""Cut plan for the High Roof Partners ad, from work/transcript.json.

Story (only lines Parth actually says, reordered: scarcity before the CTA):
  hook, problem, offer (pay only when you sit down / no retainers / pay per estimate), how it works
  (exclusive leads, we call them, book into your calendar), scarcity (one roofing contractor per area), CTA.
Cut out: "who can actually afford a roof", "to make sure that they're motivated buyers and financially
qualified to get a roof" (unprovable claims), "directly", the repeated "if you want us to ... face-to-face
with them" passage, and the leading "as" before the scarcity line.

Each kept phrase is split wherever the voice is silent > 0.25 s. Every piece keeps up to 0.1 s (3 frames) of
room tone on each side; neighbouring pieces cross-fade over exactly those pads (up to 6 frames), so fades only
ever touch room tone. Video cuts land in the middle of each cross-fade, on the word boundary.
Writes work/timeline.json and logs/cutlist.txt."""
import json, re
import numpy as np, soundfile as sf

FPS = 30
words = json.load(open("work/transcript.json"))
def clean(t): return re.sub(r"[^a-z0-9'-]", "", t.lower()).strip("-")
toks = [clean(w["text"]) for w in words]
def span(phrase, after=0):
    p = [clean(x) for x in phrase.split()]
    for i in range(after, len(toks) - len(p) + 1):
        if toks[i:i + len(p)] == p: return i, i + len(p) - 1
    raise SystemExit(f"not found: {phrase}")

PHRASES = [  # (label, first words, last words) -- matched in order in the transcript
    ("hook", "roofers getting", "per month"),
    ("problem", "stop buying", "angi leads"),
    ("offer", "don't pay me", "high -intent homeowners"),
    ("offer", "no monthly", "per estimate"),
    ("how", "here's how", "it works"),
    ("how", "my team", "them ourselves"),
    ("how", "and book them", "and book them"),
    ("how", "into your calendar", "through all the dirt"),
    ("scarcity", "we only work", "per area"),
    ("cta", "click the button", "is available"),
]
pieces = []
for label, a, b in PHRASES:
    i0 = span(a)[0]; i1 = span(b, i0)[1]
    pieces.append({"label": label, "w0": i0, "w1": i1})

# voice energy (10 ms) for boundary refinement and pause detection
v, sr = sf.read("/home/user/DEMO/feedfix/voice_kim_dry.wav", always_2d=True); x = v.mean(1)
H = sr // 100; n = len(x) // H
e = 20 * np.log10(np.sqrt((x[:n * H] ** 2).reshape(n, H).mean(1)) + 1e-9)
floor = np.percentile(e, 10); speech = np.percentile(e, 90)
TH = floor + 0.25 * (speech - floor)                          # speech/silence threshold
def is_sp(t): return e[min(n - 1, max(0, int(t * 100)))] > TH
def refine_start(t):                                          # back up to the true onset (max 0.15 s)
    k = int(t * 100)
    for j in range(k, max(0, k - 15), -1):
        if e[j] < TH: return j / 100
    return max(0, k - 15) / 100
def refine_end(t):                                            # run on to the true offset (max 0.2 s)
    k = int(t * 100)
    for j in range(k, min(n, k + 20)):
        if e[j] < TH: return j / 100
    return min(n, k + 20) / 100

# split each phrase at silences > 0.25 s inside it
segs = []
for p in pieces:
    lo = words[p["w0"] - 1]["end"] if p["w0"] > 0 else 0.0                 # never reach into a word that is not kept
    hi = words[p["w1"] + 1]["start"] if p["w1"] + 1 < len(words) else 99.0
    a = max(refine_start(words[p["w0"]]["start"]), lo); b = min(refine_end(words[p["w1"]]["end"]), hi - 0.01)
    cur = a; k = int(a * 100); quiet = None
    for j in range(int(a * 100), int(b * 100)):
        if e[j] < TH:
            quiet = j if quiet is None else quiet
        else:
            if quiet is not None and (j - quiet) / 100 > 0.25:
                segs.append({"label": p["label"], "a": cur, "b": quiet / 100}); cur = j / 100
            quiet = None
    segs.append({"label": p["label"], "a": cur, "b": b})

# room-tone pads: up to 0.1 s, never reaching into a neighbouring source word that is not kept
starts = sorted(w["start"] for w in words); ends = sorted(w["end"] for w in words)
for s in segs:
    prev_end = max([t for t in ends if t <= s["a"] + 1e-3] or [0.0])
    next_start = min([t for t in starts if t >= s["b"] - 1e-3] or [99])
    s["p"] = round(min(s["a"], max(0.034, min(0.1, s["a"] - prev_end - 0.01))), 3)   # at least 1 frame: every joint
    s["q"] = round(max(0.034, min(0.1, next_start - s["b"] - 0.01)), 3)                # gets a >= 2-frame cross-fade
segs[-1]["tail"] = 0.45                                        # breathing room under the end card (silence)

# output timeline, frame-quantised
def fr(t): return round(t * FPS) / FPS
T = 0.0
for k, s in enumerate(segs):
    s["T"] = fr(T)                                            # output time where this piece's audio starts
    s["len"] = fr(s["b"] + s["q"]) - fr(s["a"] - s["p"])
    if k + 1 < len(segs):
        ov = fr(s["q"] + segs[k + 1]["p"]); s["xf"] = ov
        T = s["T"] + s["len"] - ov
    else:
        s["xf"] = 0.0
DUR = fr(segs[-1]["T"] + segs[-1]["len"] + segs[-1]["tail"])
# video: cut in the middle of each cross-fade
for k, s in enumerate(segs):
    s["vin"] = 0.0 if k == 0 else fr(s["T"] + s["xf_prev"] / 2) if "xf_prev" in s else 0.0
    if k + 1 < len(segs): segs[k + 1]["xf_prev"] = s["xf"]
for k, s in enumerate(segs):
    s["vin"] = 0.0 if k == 0 else fr(s["T"] + segs[k - 1]["xf"] / 2)
    s["vout"] = DUR if k == len(segs) - 1 else fr(segs[k + 1]["T"] + s["xf"] / 2)
    s["src_v0"] = round(s["a"] - s["p"] + (s["vin"] - s["T"]), 4)   # source time shown at vin
def out_time(t_src):
    for s in segs:
        if s["a"] - s["p"] - 1e-3 <= t_src <= s["b"] + s["q"] + 1e-3: return s["T"] + (t_src - (s["a"] - s["p"]))
    return None

# words on the output timeline
W = []
for s in segs:
    for i, w in enumerate(words):
        if w["start"] >= s["a"] - 0.05 and w["end"] <= s["b"] + 0.08:
            o = out_time(w["start"]); oe = out_time(min(w["end"], s["b"] + s["q"]))
            if o is not None: W.append({"i": i, "text": w["text"], "t": round(o, 3), "te": round(oe, 3), "label": s["label"]})
W = sorted({w["i"]: w for w in W}.values(), key=lambda w: w["t"])

# source spans covered by old burned-in graphics -> output intervals that must be covered by full-screen cards
ov = json.load(open("work/source_overlays.json"))
BAD = [(3.25, 4.85), (6.35, 7.65), (8.5, 10.65), (11.85, 13.25), (17.82, 19.4), (23.05, 25.08), (32.2, 33.5)]   # takeovers + money emojis, with margin
RED = [tuple(r) for r in ov["red"] if r[1] - r[0] > 1]
cover = []
for a, b in BAD:
    for s in segs:
        lo, hi = max(a, s["src_v0"]), min(b, s["src_v0"] + (s["vout"] - s["vin"]))
        if hi > lo: cover.append((round(s["vin"] + lo - s["src_v0"], 3), round(s["vin"] + hi - s["src_v0"], 3)))
redout = []
for a, b in RED:
    for s in segs:
        lo, hi = max(a, s["src_v0"]), min(b, s["src_v0"] + (s["vout"] - s["vin"]))
        if hi > lo: redout.append((round(s["vin"] + lo - s["src_v0"], 3), round(s["vin"] + hi - s["src_v0"], 3)))

json.dump({"fps": FPS, "dur": DUR, "segs": segs, "words": W, "cover": cover, "red": redout}, open("work/timeline.json", "w"), indent=1)
with open("logs/cutlist.txt", "w") as f:
    f.write(f"High Roof Partners ad 1 - cut list (output {DUR:.2f} s @ {FPS} fps)\n")
    f.write("audio piece = source [a-p, b+q]; video shows source from src_v0 over output [vin, vout); cross-fade over the pads\n\n")
    f.write(f"{'#':>2} {'part':9} {'src audio':>17} {'out audio':>17} {'out video':>17}  {'xfade':>5}  text\n")
    for k, s in enumerate(segs):
        txt = " ".join(w["text"] for w in W if s["T"] - 0.01 <= w["t"] <= s["T"] + s["len"] and abs(out_time(words[w["i"]]["start"]) - w["t"]) < 0.01 and s["a"] - 0.05 <= words[w["i"]]["start"] <= s["b"])
        f.write(f"{k:2d} {s['label']:9} {s['a'] - s['p']:7.3f}-{s['b'] + s['q']:7.3f}  {s['T']:7.3f}-{s['T'] + s['len']:7.3f}  {s['vin']:7.3f}-{s['vout']:7.3f}  {s['xf']:5.3f}  {txt}\n")
    f.write(f"\nfinal tail: {segs[-1]['tail']} s of silence under the end card\n")
    f.write(f"output intervals that must be covered by new full-screen cards (old burned-in graphics): {cover}\n")
    f.write(f"output intervals with the old red CTA banner in frame (covered by the lower strip): {redout}\n")
print(f"{DUR:.2f}s, {len(segs)} pieces, first word at {W[0]['t']:.3f}s")
print(open("logs/cutlist.txt").read())
