"""Calm, premium Connor commercial over the client's take (picture and voice timing untouched).
Picture: #hand (barely-there handheld drift) > #cam (110 % framing + 3 slow push-ins: hook, turn/company, offer) > graded take.
B-roll: the client's own clips over the take, one slow move each, 6-frame dissolves. Graphics: 6 cards, one at a time,
lower third / top tag only, never over his face. Captions: fixed lower third, phrase-level, hidden while a card is up."""
import html, json, math, os, re, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
W, H = 1080, 1920
probe = lambda f: float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f], capture_output=True, text=True).stdout)
DUR = round(probe("assets/look.mp4"), 3)
words = json.load(open("transcript.json"))
norm = lambda s: re.sub(r"[^a-z0-9$%-]", "", s.lower())
def find(phrase, after=0):
    p = phrase.lower().split()
    for i in range(after, len(words) - len(p) + 1):
        if all(norm(words[i + k]["text"]) == norm(p[k]) for k in range(len(p))): return list(range(i, i + len(p)))
    raise SystemExit(f"phrase not found: {phrase}")
at = lambda p, after=0: words[find(p, after)[0]]["start"]
end = lambda p, after=0: words[find(p, after)[-1]]["end"]
js, el, sfx = [], [], []
fx = lambda k, t, v: sfx.append((k, t, v))

# ---------------- camera: subtle drift + 110 % framing + 3 slow push-ins ----------------
def hand(t):
    x = 4.0 * math.sin(2 * math.pi * 0.11 * t + 0.7) + 1.6 * math.sin(2 * math.pi * 0.37 * t + 2.1)
    y = 3.0 * math.sin(2 * math.pi * 0.09 * t + 1.9) + 1.2 * math.sin(2 * math.pi * 0.29 * t + 0.4)
    r = 0.12 * math.sin(2 * math.pi * 0.07 * t + 1.1)
    return x, y, r
t = 0.0
js.append('tl.set("#hand", {x: %.2f, y: %.2f, rotation: %.3f}, 0);' % hand(0))
while t < DUR:
    js.append('tl.to("#hand", {x: %.2f, y: %.2f, rotation: %.3f, duration: 0.5, ease: "none"}, %.2f);' % (*hand(t + 0.5), t)); t += 0.5
BR = json.load(open("tools/broll.json"))
def next_broll(t): return min(b["t0"] for b in BR if b["t0"] > t)
PUSH = [(0.3, 3.4, 1.14), (at("is exactly") + 0.05, 3.2, 1.15), (at("also offering") + 0.3, 2.6, 1.14)]
js.append('tl.set("#cam", {scale: 1.10}, 0);')
for t0, d, s in PUSH:
    js.append(f'tl.to("#cam", {{scale: {s}, duration: {d}, ease: "sine.inOut"}}, {t0:.3f});')
    js.append(f'tl.set("#cam", {{scale: 1.10}}, {next_broll(t0) + 0.2:.3f});')   # reset hidden under the next b-roll, never a visible zoom-out

# ---------------- b-roll: one slow move each, soft 6-frame dissolves ----------------
XF = 0.12
for n, b in enumerate(BR):
    t0, t1 = b["t0"], b["t1"]
    s0, s1 = t0 - XF, t1 + XF
    el.append(f'<div class="kb" id="kb{n}"><video id="bv{n}" class="clip" src="assets/br/{b["file"]}" muted playsinline data-start="{s0:.3f}" data-duration="{s1 - s0:.3f}" data-track-index="{2 + n % 2}"></video></div>')
    js.append(f'tl.fromTo("#kb{n}", {{opacity: 0}}, {{opacity: 1, duration: {2 * XF}, ease: "none"}}, {s0:.3f});')
    if not (n + 1 < len(BR) and abs(BR[n + 1]["t0"] - t1) < 0.01):
        js.append(f'tl.to("#kb{n}", {{opacity: 0, duration: {2 * XF}, ease: "none"}}, {t1 - XF:.3f});')
    else: js.append(f'tl.set("#kb{n}", {{opacity: 0}}, {s1:.3f});')
    if b["move"] == "push": js.append(f'tl.fromTo("#bv{n}", {{scale: 1.0, xPercent: 0}}, {{scale: 1.06, xPercent: 0, duration: {s1 - s0:.3f}, ease: "none"}}, {s0:.3f});')
    else:
        d = 1 if n % 2 else -1
        js.append(f'tl.fromTo("#bv{n}", {{scale: 1.07, xPercent: {2.0 * d}}}, {{scale: 1.07, xPercent: {-2.0 * d}, duration: {s1 - s0:.3f}, ease: "none"}}, {s0:.3f});')

# ---------------- graphics: 6 moments, one at a time ----------------
CARDS = []
def card(cid, cls, inner, a, b, sound=True, tag=False):
    CARDS.append((a, b))
    el.append(f'<div class="clip g {cls}" id="{cid}" data-start="{a:.3f}" data-duration="{b - a:.3f}" data-track-index="20">{inner}</div>')
    sel = f"#{cid} .card"
    if a <= 0.01: js.append(f'tl.fromTo("{sel}", {{opacity: 0, y: -10}}, {{opacity: 1, y: 0, duration: 0.5, ease: "power2.out"}}, 0.05);')
    else: js.append(f'tl.fromTo("{sel}", {{opacity: 0, y: 24}}, {{opacity: 1, y: 0, duration: 0.45, ease: "power3.out"}}, {a:.3f});')
    if b < DUR - 0.05: js.append(f'tl.to("{sel}", {{opacity: 0, y: {-8 if tag else 10}, duration: 0.3, ease: "power2.in"}}, {b - 0.3:.3f});')
    if sound: fx("whoosh", max(0, a - 0.05), 0.16)
PIN = '<svg viewBox="0 0 24 24"><path d="M12 2a7 7 0 0 0-7 7c0 5.2 7 13 7 13s7-7.8 7-13a7 7 0 0 0-7-7zm0 9.6a2.6 2.6 0 1 1 0-5.2 2.6 2.6 0 0 1 0 5.2z" fill="#2f7a53"/></svg>'
card("g-tag", "tag", f'<div class="card">{PIN}Texas Homeowners</div>', 0.0, 3.0, tag=True)
P0 = at("were denied") - 0.05
card("g-prob", "prob", '<div class="card"><span>Texas roof insurance</span>Claims often get underpaid<br>or denied</div>', P0, P0 + 2.5)
N0 = at("at pinecrest") + 0.05
card("g-name", "name", '<div class="card"><i class="bar"></i><div><b>Connor</b><i>Pinecrest Roofing &amp; Construction</i></div></div>', N0, N0 + 2.5)
S = [("Inspection", at("fully approved") - 0.2), ("Claim", at("fully approved") + 0.4), ("Approval", at("by their insurance") + 0.35)]
R0 = S[0][1] - 0.45; R1 = R0 + 2.85
steps = "".join(f'<div class="st"><div class="dot" id="dt{j}">{j + 1}</div><b id="sl{j}">{n}</b></div>' for j, (n, _) in enumerate(S))
card("g-proc", "proc", f'<div class="card"><div class="ttl">How we help</div><div class="steps"><div class="track"><div class="fill" id="fill"></div></div>{steps}</div></div>', R0, R1)
for j, (_, ts) in enumerate(S):
    js.append(f'tl.fromTo("#dt{j}", {{backgroundColor: "#ffffff", borderColor: "#dfe5e1", color: "#5d6b63"}}, {{backgroundColor: "#2f7a53", borderColor: "#2f7a53", color: "#ffffff", duration: 0.25, ease: "power1.out", immediateRender: false}}, {ts:.3f});')
    js.append(f'tl.fromTo("#sl{j}", {{color: "#5d6b63"}}, {{color: "#14231b", duration: 0.25, immediateRender: false}}, {ts:.3f});')
    if j: js.append(f'tl.fromTo("#fill", {{scaleX: {(j - 1) / 2}}}, {{scaleX: {j / 2}, duration: 0.35, ease: "power2.out", immediateRender: false}}, {ts - 0.3:.3f});')
    fx("click", ts, 0.22)
O0 = at("free no-obligation") - 0.05
card("g-offer", "offer", '<div class="card"><b>Free Roof Inspection</b><i>No Obligation</i></div>', O0, O0 + 2.7)
E0 = at("just click") + 0.05
ARROW = '<svg viewBox="0 0 24 24" id="arw"><path d="M12 4v15m0 0l-6-6m6 6l6-6" stroke="#2f7a53" stroke-width="2.4" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>'
card("g-end", "end", f'<div class="card"><div class="co">PINECREST ROOFING &amp; CONSTRUCTION</div><b>Book Your Free Inspection</b>{ARROW}</div>', E0, DUR, sound=False)
fx("chime", E0 + 0.1, 0.2)
js.append(f'tl.fromTo("#arw", {{y: -4}}, {{y: 4, duration: 0.7, ease: "sine.inOut", yoyo: true, repeat: 3, immediateRender: false}}, {E0 + 0.6:.3f});')

# ---------------- captions: phrases at natural pauses, max 2 lines x ~6 words, 1 highlight at most ----------------
PH = ["Texas homeowners,", "watch this video", "before you spend $30,000 / on a new roof.", "47% of roof insurance claims / in the state of Texas",
      "were denied and not paid out at all.", "And if your roof is / 10 to 15 years old", "and was recently / hit by a storm,",
      "you may already be / in the risk window,", "because insurance companies", "are tightening guidelines / on aging roofs.",
      "But you don't need / to worry now,", "because that is exactly / where we come in.", "At Pinecrest Roofing and Construction,",
      "we've helped dozens / of local homeowners", "get their roofs fully approved / by their insurance,", "and we're launching the new / Roof Protection Program,",
      "exclusively for homeowners / in North and East Texas.", "This program is designed / specifically for aging roofs,", "and just to maintain / quality and precision,",
      "we limit it to just nine / full roof projects per month.", "For a limited time, / we're also offering a free,", "no-obligation roof inspection,",
      "complete with photo and / video documentation", "to check for storm damage.", "Just click the Learn More / button below,", "and book your free inspection."]
groups, k = [], 0
for ph in PH:
    ls = [x.split() for x in ph.split(" / ")]
    g = []
    for ln in ls:
        g.append(list(range(k, k + len(ln)))); k += len(ln)
    assert all(norm(words[i]["text"]) == norm(t) for ln, tl_ in zip(g, ls) for i, t in zip(ln, tl_)), ph
    groups.append(g)
assert k == len(words), (k, len(words))
HL = {find("$30,000")[0], find("47%")[0], find("risk")[0], find("nine")[0]}
clean = lambda s: re.sub(r"[.,]+$", "", s)
def visible(a, b):
    segs = [(a, b)]
    for ca, cb in CARDS:
        segs = [s for x, y in segs for s in ((x, min(y, ca)), (max(x, cb), y)) if s[1] - s[0] > 0.6]
    return segs
cap = []
for gi, g in enumerate(groups):
    a = words[g[0][0]]["start"] - 0.05
    b = words[groups[gi + 1][0][0]]["start"] - 0.05 if gi + 1 < len(groups) else DUR
    b = min(b, words[g[-1][-1]]["end"] + 0.7)
    body = "".join("<div>" + " ".join(f'<span class="hl">{html.escape(clean(words[i]["text"]))}</span>' if i in HL else html.escape(clean(words[i]["text"])) for i in ln) + "</div>" for ln in g)
    cap.append(f'<div class="cg" id="cg{gi}">{body}</div>')
    for x, y in visible(a, b):
        js.append(f'tl.fromTo("#cg{gi}", {{opacity: 0}}, {{opacity: 1, duration: 0.15, ease: "none", immediateRender: false}}, {x:.3f});')
        js.append(f'tl.to("#cg{gi}", {{opacity: 0, duration: 0.12, ease: "none"}}, {y - 0.12:.3f});')

aud = []
for n, (k, t, v) in enumerate(sorted(sfx, key=lambda x: x[1])):
    f = f"assets/sfx/{k}.wav"
    aud.append(f'<audio id="fx{n}" src="{f}" data-start="{t:.3f}" data-duration="{min(probe(f), DUR - t):.3f}" data-track-index="{40 + n}" data-volume="{v}"></audio>')
CSS = open("tools/style.css").read()
nl = "\n      "
doc = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <title>Connor Commercial</title>
    <script src="vendor/gsap.min.js"></script>
    <style>
{CSS}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="{W}" data-height="{H}" data-duration="{DUR}">
      <div id="hand"><div id="cam">
        <video id="src" class="clip" src="assets/look.mp4" muted playsinline data-start="0" data-duration="{DUR}" data-track-index="0"></video>
      </div></div>
      {nl.join(el)}
      <div id="captions" class="clip" data-start="0" data-duration="{DUR}" data-track-index="30">
        {(nl + "  ").join(cap)}
      </div>
      {nl.join(aud)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      {nl.join(js)}
      tl.set({{}}, {{}}, {DUR});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
open("index.html", "w").write(doc)
# report: caption groups, cards, and any moment where a card entrance, caption change and push-in start together
starts = [p[0] for p in PUSH]
clash = [round(a, 2) for a, _ in CARDS if any(abs(a - s) < 0.25 for s in starts)]
print(f"{DUR}s · {len(CARDS)} cards · {len(groups)} captions · {len(sfx)} sfx · card/push clashes: {clash or 'none'}")
for gi, g in enumerate(groups):
    a = words[g[0][0]]["start"] - 0.05; b = min(words[groups[gi + 1][0][0]]["start"] - 0.05 if gi + 1 < len(groups) else DUR, words[g[-1][-1]]["end"] + 0.7)
    print(f"  {a:6.2f}  {' / '.join(' '.join(clean(words[i]['text']) for i in ln) for ln in g):58s} shown: {[(round(x, 2), round(y, 2)) for x, y in visible(a, b)]}")
