"""Connor selfie ad (9:16): make a frozen-background avatar clip feel like a real phone video.

Picture: #hand (handheld drift / bob / micro-shake on everything) > #look (tiny exposure flickers) >
  #facewrap (110-125 % punch levels, origin below the face so it never drops into the captions) > face video,
  plus b-roll cutaways (the client's own truck + roof/crew footage) every 3-5 s with light push / pan.
Graphics sit outside #hand: top-area pop-ups, the Pinecrest sweep on the truck, captions under the chin,
and the pulsing BOOK YOUR FREE INSPECTION button held to the last frame.
"""
import html, json, math, os, random, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
W, H = 1080, 1920
probe = lambda f: float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f], capture_output=True, text=True).stdout)
DUR = round(probe("assets/prep/face.mp4") - 0.05, 3)
words = json.load(open("transcript.json")); words = words if isinstance(words, list) else words["words"]
def clean(t): return re.sub(r"[.,?!]+$", "", t).lower()
def find(p, after=0):
    toks = p.lower().split()
    for i in range(after, len(words)):
        if [clean(w["text"]) for w in words[i:i + len(toks)]] == toks: return list(range(i, i + len(toks)))
    sys.exit(f"phrase not found: {p}")
def at(p, after=0): return words[find(p, after)[0]]["start"]
def end(p, after=0): return words[find(p, after)[-1]]["end"]

el, js, sfx = [], [], []
def fx(name, t, vol): sfx.append((name, round(max(0.0, t), 3), vol))
E = lambda e: f'<span class="emo">{e}</span>'
def POP(sel, t, d=0.22): js.append(f'tl.fromTo("{sel}", {{opacity: 0, scale: 0.6}}, {{opacity: 1, scale: 1, duration: {d}, ease: "back.out(2.2)"}}, {t:.3f});')
def OUT(sel, t): js.append(f'tl.to("{sel}", {{opacity: 0, scale: 0.92, duration: 0.12, ease: "power2.in"}}, {t - 0.12:.3f});')

# ---------------- handheld phone movement (deterministic) ----------------
rnd = random.Random(7)
ph = [rnd.uniform(0, 6.28) for _ in range(9)]
def hand(t):
    x = 11 * math.sin(2 * math.pi * 0.23 * t + ph[0]) + 6 * math.sin(2 * math.pi * 0.61 * t + ph[1]) + 2.2 * math.sin(2 * math.pi * 1.9 * t + ph[2])
    y = 9 * math.sin(2 * math.pi * 0.19 * t + ph[3]) + 3.5 * math.sin(2 * math.pi * 1.15 * t + ph[4]) + 1.8 * math.sin(2 * math.pi * 2.3 * t + ph[5])
    r = 0.45 * math.sin(2 * math.pi * 0.17 * t + ph[6]) + 0.22 * math.sin(2 * math.pi * 0.53 * t + ph[7]) + 0.06 * math.sin(2 * math.pi * 2.1 * t + ph[8])
    return x, y, r
STEP = 0.2
x0, y0, r0 = hand(0)
js.append(f'tl.set("#hand", {{x: {x0:.1f}, y: {y0:.1f}, rotation: {r0:.3f}}}, 0);')
t = 0.0
while t < DUR:
    x, y, r = hand(t + STEP)
    js.append(f'tl.to("#hand", {{x: {x:.1f}, y: {y:.1f}, rotation: {r:.3f}, duration: {STEP}, ease: "none"}}, {t:.2f});')
    t += STEP
# tiny exposure flickers (phone adjusting to sunlight)
t, k = 0.8, 0
js.append('tl.set("#look", {filter: "brightness(1)"}, 0);')
while t < DUR - 1:
    b = rnd.uniform(0.965, 1.035)
    js.append(f'tl.to("#look", {{filter: "brightness({b:.3f})", duration: 0.5, ease: "sine.inOut"}}, {t:.2f});')
    t += rnd.uniform(1.2, 2.6)

# ---------------- face punch levels (110 % base, 125 % on emphasis) ----------------
ZOOM = [(0.0, 1.24), (at("watch this"), 1.12), (at("47%"), 1.25), (at("in the state"), 1.12), (at("not paid"), 1.25), (at("and if your"), 1.12),
        (at("risk window"), 1.25), (at("but you don't"), 1.12), (at("exactly where"), 1.25), (at("we're launching") - 0.1, 1.13), (at("roof protection"), 1.22),
        (at("designed specifically"), 1.12), (at("aging roofs", find("designed specifically")[0]), 1.24), (at("we limit"), 1.12), (at("nine full"), 1.25),
        (at("free no-obligation") - 0.05, 1.25), (at("just click"), 1.12), (at("free inspection"), 1.22)]
js.append(f'tl.set("#facewrap", {{scale: {ZOOM[0][1]}}}, 0);')
for t, s in ZOOM[1:]: js.append(f'tl.to("#facewrap", {{scale: {s}, duration: 0.4, ease: "power2.inOut"}}, {t - 0.1:.3f});')

# ---------------- b-roll cutaways ----------------
BR = json.load(open("tools/broll.json"))
for n, b in enumerate(BR):
    t0, t1 = b["t0"], b["t1"]
    el.append(f'<div class="kb" id="kb{n}"><video id="bv{n}" class="clip media" src="{b["file"]}" muted playsinline data-start="{t0:.3f}" data-duration="{t1 - t0:.3f}" data-track-index="{2 + n % 2}"></video></div>')
    if b["move"] == "push": js.append(f'tl.fromTo("#kb{n}", {{scale: 1.04, xPercent: 0}}, {{scale: 1.12, xPercent: 0, duration: {t1 - t0:.3f}, ease: "none"}}, {t0:.3f});')
    else:
        d = 1 if n % 2 else -1
        js.append(f'tl.fromTo("#kb{n}", {{scale: 1.1, xPercent: {2.4 * d}}}, {{scale: 1.1, xPercent: {-2.4 * d}, duration: {t1 - t0:.3f}, ease: "none"}}, {t0:.3f});')
    if n == 0 or abs(BR[n - 1]["t1"] - t0) > 0.05: fx("wA" if n % 2 else "wB", t0 - 0.08, 0.09)

# ---------------- top pop-ups (one at a time, 1.5-3 s) ----------------
POPS = [(f'{E("📍")} TEXAS HOMEOWNERS', 0.0, at("before you") - 0.1, "pill"),
        (f'BEFORE YOU SPEND <span class="y">$30,000</span> {E("💸")}', at("before you"), end("new roof") + 0.3, "pill dark"),
        (f'{E("📊")} <span class="r">47%</span> OF ROOF CLAIMS…', at("47%"), at("were denied") - 0.05, "pill"),
        (f'{E("❌")} DENIED. NOT PAID OUT.', at("were denied"), end("at all") + 0.1, "pill red"),
        (f'{E("🏠")} 10–15 YEAR OLD ROOF?', at("10 to 15") - 0.2, at("recently hit") - 0.05, "pill dark"),
        (f'{E("🌩️")} RECENT STORM?', at("recently hit"), at("risk window") - 0.05, "pill dark"),
        (f'{E("⚠️")} THE RISK WINDOW', at("risk window"), end("aging roofs") + 0.2, "pill red"),
        (f'{E("✅")} THAT\'S WHERE WE COME IN', at("that is exactly"), at("at pinecrest") - 0.05, "pill green"),
        (f'{E("🏡")} DOZENS OF LOCAL HOMEOWNERS', at("dozens of"), at("fully approved") - 0.05, "pill"),
        (f'{E("✅")} FULLY APPROVED', at("fully approved"), end("by their insurance") + 0.3, "pill green"),
        (f'{E("🛡️")} NEW ROOF PROTECTION PROGRAM', at("the new roof"), at("exclusively") - 0.05, "pill dark"),
        (f'{E("📍")} NORTH &amp; EAST TEXAS ONLY', at("exclusively"), end("east texas") + 0.3, "pill"),
        ('BUILT FOR <span class="y">AGING ROOFS</span>', at("designed specifically"), end("aging roofs", find("designed specifically")[0]) + 0.3, "pill dark"),
        (f'ONLY <span class="y">9 ROOF PROJECTS</span> / MONTH', at("we limit"), end("per month") + 0.2, "pill red"),
        (f'{E("⏳")} LIMITED TIME', at("for a limited"), at("free no-obligation") - 0.05, "pill"),
        ('FREE ROOF INSPECTION<small>$0 • NO OBLIGATION</small>', at("free no-obligation"), at("complete with") - 0.05, "pill green"),
        (f'{E("📸")} PHOTO + VIDEO REPORT', at("photo and video"), at("just click") - 0.1, "pill dark")]
for k, (txt, a, b, kind) in enumerate(POPS):
    el.append(f'<div class="clip pop" id="pop{k}" data-start="{a:.3f}" data-duration="{b - a:.3f}" data-track-index="20"><div class="{kind}" id="pl{k}">{txt}</div></div>')
    if k == 0: js.append('tl.set("#pl0", {opacity: 1, scale: 1}, 0);')
    else: POP(f"#pl{k}", a); fx("pop", a, 0.11)
    OUT(f"#pl{k}", b)
# Pinecrest sweep on the truck
B0, B1 = at("pinecrest"), at("we've helped") - 0.05
el.append(f'<div class="clip brand" id="brand" data-start="{B0:.3f}" data-duration="{B1 - B0:.3f}" data-track-index="21">'
          '<div class="brandin" id="brandin"><div class="b1">PINECREST</div><div class="b2">ROOFING &amp; CONSTRUCTION</div><i id="sweep" data-layout-allow-overflow></i></div></div>')
js.append(f'tl.fromTo("#brandin", {{opacity: 0, scale: 1.25}}, {{opacity: 1, scale: 1, duration: 0.2, ease: "back.out(2)"}}, {B0:.3f});')
js.append(f'tl.fromTo("#sweep", {{xPercent: -150}}, {{xPercent: 440, duration: 0.9, ease: "power2.inOut"}}, {B0 + 0.3:.3f});')
OUT("#brandin", B1); fx("swoosh", B0 - 0.1, 0.18); fx("pop", B0 + 0.05, 0.16)
# end CTA, held to the last frame
C0 = at("just click")
el.append(f'<div class="clip cta" id="cta" data-start="{C0:.3f}" data-duration="{DUR - C0:.3f}" data-track-index="22">'
          f'<div class="ctaname" id="ctn">PINECREST ROOFING &amp; CONSTRUCTION</div><div class="ctabtn" id="ctb">BOOK YOUR FREE INSPECTION {E("👇")}</div></div>')
js.append(f'tl.fromTo("#ctn", {{opacity: 0, y: -20}}, {{opacity: 1, y: 0, duration: 0.2, ease: "power3.out"}}, {C0:.3f});')
POP("#ctb", C0 + 0.05, 0.24); fx("pop", C0 + 0.05, 0.14); fx("notify", at("free inspection"), 0.22)
n_p = int((DUR - C0 - 0.35) / 0.44)
js.append(f'tl.fromTo("#ctb", {{scale: 1}}, {{scale: 1.06, duration: 0.22, ease: "sine.inOut", yoyo: true, repeat: {max(1, n_p * 2 - 1)}, immediateRender: false}}, {C0 + 0.35:.3f});')

# ---------------- captions ----------------
YEL = ["texas homeowners", "$30,000", "insurance", "pinecrest", "roof protection program", "north and east texas", "dozens of local homeowners",
       "fully approved", "free", "free inspection", "learn more", "nine full roof projects"]
RED = ["47%", "denied", "not paid out at all", "risk window", "tightening guidelines", "aging roofs", "storm damage"]
color = {}
for lst, c in ((YEL, "y"), (RED, "r")):
    for p in lst:
        st = 0
        while True:
            try: ix = find(p, st)
            except SystemExit: break
            for i in ix: color[i] = c
            st = ix[-1] + 1
def disp(i): return re.sub(r"[.,?!]+$", "", words[i]["text"]).upper()
groups, cur = [], []
for i, w in enumerate(words):
    if cur:
        prev = words[cur[-1]]
        if len(cur) >= 3 or re.search(r"[.,?!]$", prev["text"]) or w["start"] - prev["end"] > 0.3: groups.append(cur); cur = []
    cur.append(i)
groups.append(cur)
merged = []
for g in groups:
    if merged and len(g) == 1 and len(merged[-1]) <= 2 and not re.search(r"[.?!]$", words[merged[-1][-1]]["text"]): merged[-1] = merged[-1] + g
    else: merged.append(g)
groups = merged
def units(t): return sum(0.3 if c == " " else 0.32 if c in ".,'-?!" else 1.0 if c in "MW%" else 0.42 if c in "I1" else 0.62 if c in "$0123456789" else 0.8 for c in t)
cap = []
for gi, g in enumerate(groups):
    s0 = words[g[0]]["start"]; nxt = words[groups[gi + 1][0]]["start"] if gi + 1 < len(groups) else DUR
    e0 = DUR if gi == len(groups) - 1 else min(nxt, words[g[-1]]["end"] + 0.4, DUR)
    ws = "".join(f'<span class="w" id="w{i}">{html.escape(disp(i))}</span>' for i in g)
    em = sum(units(disp(i)) for i in g) + 0.3 * (len(g) - 1)
    fs = int(min(78, 940 / 1.12 / em))
    cap.append(f'<div class="cg" id="cg{gi}"><div class="line" style="font-size:{fs}px">{ws}</div></div>')
    js.append(f'tl.fromTo("#cg{gi}", {{opacity: 0, scale: 0.88}}, {{opacity: 1, scale: 1, duration: 0.08, ease: "power2.out"}}, {s0:.3f});')
    for i in g:
        col = {"y": "#ffd60a", "r": "#ff3b30"}.get(color.get(i), "#ffffff")
        js.append(f'tl.fromTo("#w{i}", {{opacity: 0.6, scale: 1, color: "#ffffff"}}, {{opacity: 1, scale: 1.1, color: "{col}", duration: 0.07}}, {words[i]["start"]:.3f});')
        js.append(f'tl.to("#w{i}", {{scale: 1, duration: 0.1}}, {max(words[i]["start"] + 0.07, words[i]["end"]):.3f});')
    js.append(f'tl.set("#cg{gi}", {{opacity: 0, visibility: "hidden"}}, {e0:.3f});')

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
    <title>Connor Selfie Ad</title>
    <script src="vendor/gsap.min.js"></script>
    <style>
{CSS}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="{W}" data-height="{H}" data-duration="{DUR}">
      <div id="hand"><div id="look">
        <div id="facewrap"><video id="face" class="clip" src="assets/prep/face.mp4" muted playsinline data-start="0" data-duration="{DUR}" data-track-index="0"></video></div>
        {nl.join(el[:len(BR)])}
      </div></div>
      {nl.join(el[len(BR):])}
      <div id="captions" class="clip" data-start="0" data-duration="{DUR}" data-track-index="30">
        {nl.join(cap)}
      </div>
    </div>
    <audio id="vo" src="assets/vo.wav" data-start="0" data-duration="{DUR}" data-track-index="1" data-volume="1"></audio>
    <audio id="amb" src="assets/ambience.wav" data-start="0" data-duration="{DUR}" data-track-index="4" data-volume="1"></audio>
    <audio id="music" src="assets/music_bed.wav" data-start="0" data-duration="{DUR}" data-track-index="5" data-volume="1"></audio>
    {chr(10).join("    " + a for a in aud).lstrip()}
    <script>
      const tl = gsap.timeline({{ paused: true }});
      {nl.join(js)}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
open("index.html", "w").write(doc)
# checks: the wide face shot is never held more than 3 s without a cutaway or a punch change
ev = sorted({0.0, *[b["t0"] for b in BR], *[b["t1"] for b in BR], *[t for t, _ in ZOOM]})
long = [(round(a, 2), round(b - a, 2)) for a, b in zip(ev, ev[1:] + [DUR]) if b - a > 3.0 and not any(x["t0"] <= a < x["t1"] for x in BR)]
print(f"{DUR}s · {len(BR)} cutaways · {len(POPS)} pop-ups · {len(groups)} captions · {len(sfx)} sfx · face holds >3s: {long or 'none'}")
