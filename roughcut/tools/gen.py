"""Dress the client's finished rough cut (assets/source.mp4) with everything on top, never re-timing it.

  gen.py 916   -> roughcut/index.html       (1080x1920, Reels/Stories)
  gen.py 45    -> roughcut-4x5/index.html   (1080x1350, feed; picture cover-cropped to the middle)

Layers: the source picture (muted) sits inside three untimed wrappers: #push (slow 100->108 % per scene, reset on
each of the client's cuts), #punch (4-frame punch-ins + per-word snap zooms) and #whip (the one whip transition).
On top: grade, white flash, top pop-ups, damage list, brand reveal, end CTA, word-by-word captions.
Audio: cleaned VO (assets/vo.wav), ducked music bed (assets/music_bed.wav), Mixkit SFX (assets/sfx/*.wav).
"""
import html, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
FMT = sys.argv[1] if len(sys.argv) > 1 else "916"
W, H = 1080, (1920 if FMT == "916" else 1350)
OUT = "." if FMT == "916" else "../roughcut-4x5"
probe = lambda f: float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                                       capture_output=True, text=True).stdout)
DUR = round(probe("assets/source.mp4") - 0.02, 3)
words = json.load(open("transcript.json"))

def clean(t): return re.sub(r"[.,?!]+$", "", t).lower()
def find(p, after=0):
    toks = p.lower().split()
    for i in range(after, len(words)):
        if [clean(w["text"]) for w in words[i:i + len(toks)]] == toks: return list(range(i, i + len(toks)))
    sys.exit(f"phrase not found: {p}")
def at(p, after=0): return words[find(p, after)[0]]["start"]
def end(p, after=0): return words[find(p, after)[-1]]["end"]

# ---------------- layout per format (Meta safe zones) ----------------
if FMT == "916":   # Reels: keep clear of the top 14 % and bottom 35 %; 60 px sides
    L = dict(pop_top=300, pop_h=210, list_top=300, cap_top=1030, cap_h=200, cta_top=640, brand_top=290, disc_gap=14)
else:              # 4:5 feed: 60 px margins all round
    L = dict(pop_top=70, pop_h=200, list_top=70, cap_top=1000, cap_h=190, cta_top=430, brand_top=60, disc_gap=10)
VID_Y = (H - 1920) // 2          # cover crop: 1080x1920 picture centred in the frame

# ---------------- the client's cuts (frame-diff spikes in source.mp4; 14.80 = middle of their dissolve) ----------------
CUTS = [0.0, 3.167, 5.633, 6.700, 11.767, 14.800, 17.567, 18.167, 19.250, 20.300, 20.833, 23.467, 26.000, 26.733,
        28.533, 31.933, 34.367, 36.700, 37.900, 40.233, 43.800, 45.433, 46.500, 49.500]
WHIP = 14.80                                  # "But from up here": whip + blur + 2-frame flash over their dissolve
FLASHES = [5.633, WHIP, 28.533, 40.233]       # 2-frame white flashes only where a hard change needs a hit
PUNCHES = [at("north texas"), at("thirty thousand"), at("thousands of dollars"), at("different story"), at("covered by your"),
           at("taken advantage"), at("pinecrest roofing"), at("nothing there"), at("free inspection")]
SNAPS = [at("hail hits"), at("cracked shingles"), at("soft wood"), at("leaks")]
GRADE = [(0.0, "base"), (23.467, "bright"), (28.533, "dark"), (40.233, "base")]   # changes land on the client's cuts
FILTERS = {"base": "contrast(1.08) saturate(1.06) sepia(0.08) brightness(1.02)",
           "bright": "contrast(1.06) saturate(1.1) sepia(0.06) brightness(1.1)",
           "dark": "contrast(1.12) saturate(0.72) sepia(0.04) brightness(0.88)"}

el, js, sfx = [], [], []
def fx(name, t, vol, dur=None): sfx.append((name, round(max(0.0, t), 3), vol, dur))

# Slow push-in on every scene.
for k, c0 in enumerate(CUTS):
    c1 = CUTS[k + 1] if k + 1 < len(CUTS) else DUR
    js.append(f'tl.fromTo("#push", {{scale: 1}}, {{scale: 1.08, duration: {c1 - c0:.3f}, ease: "none", immediateRender: {"true" if k == 0 else "false"}}}, {c0:.3f});')
# Punch-ins: up to 115 % in 4 frames, ease back.
for t in PUNCHES:
    js.append(f'tl.fromTo("#punch", {{scale: 1}}, {{scale: 1.15, duration: 0.133, ease: "power2.out", immediateRender: false}}, {t:.3f});')
    js.append(f'tl.to("#punch", {{scale: 1, duration: 0.5, ease: "power2.inOut"}}, {t + 0.133:.3f});')
    fx("wA" if PUNCHES.index(t) % 2 == 0 else "wB", t - 0.08, 0.22)
# Snap zoom on each damage word.
for t in SNAPS:
    js.append(f'tl.fromTo("#punch", {{scale: 1}}, {{scale: 1.12, duration: 0.1, ease: "power4.out", immediateRender: false}}, {t:.3f});')
    js.append(f'tl.to("#punch", {{scale: 1.0, duration: 0.3, ease: "power2.out"}}, {t + 0.18:.3f});')
# Whip into "from up here": out-blur up, white flash, in-blur from below.
js.append(f'tl.fromTo("#whip", {{yPercent: 0, filter: "blur(0px)"}}, {{yPercent: -9, filter: "blur(22px)", duration: 0.2, ease: "power3.in", immediateRender: false}}, {WHIP - 0.2:.3f});')
js.append(f'tl.fromTo("#whip", {{yPercent: 9, filter: "blur(22px)"}}, {{yPercent: 0, filter: "blur(0px)", duration: 0.22, ease: "power3.out", immediateRender: false}}, {WHIP + 0.067:.3f});')
for t in FLASHES:
    js.append(f'tl.set("#flash", {{opacity: 1}}, {t - 0.033:.3f});')
    js.append(f'tl.set("#flash", {{opacity: 0}}, {t + 0.034:.3f});')
    if t != WHIP: fx("wB", t - 0.1, 0.24)
# Grade.
js.append(f'tl.set("#grade", {{filter: "{FILTERS["base"]}"}}, 0);')
for t, g in GRADE[1:]: js.append(f'tl.set("#grade", {{filter: "{FILTERS[g]}"}}, {t:.3f});')

# ---------------- top pop-ups ----------------
E = lambda e: f'<span class="emo">{e}</span>'
POPS = [  # (html, start, end, style)
    (f'{E("📍")} NORTH TEXAS', 0.0, 1.75, "pill"),
    (f'BEFORE YOU SPEND <span class="yel">$30,000</span> {E("💸")}', at("before you spend"), end("new roof") + 0.25, "pill dark"),
    (f'{E("⚠️")} HIDDEN ROOF DAMAGE', at("costing them"), end("damage") + 0.2, "pill red"),
    (f'{E("👀")} LOOKS FINE...', at("everything looks") - 0.15, WHIP - 0.2, "pill"),
    (f'{E("🔍")} THE REAL STORY', WHIP + 0.05, end("different story"), "pill dark"),
    (f'{E("✅")} OFTEN COVERED BY INSURANCE', at("often covered"), CUTS[14] - 0.05, "pill green"),
    (f'{E("🌩️")} HAIL EVERY SPRING', at("hail pretty much"), end("every spring") + 0.35, "pill dark"),
    (f'{E("🚩")} STORM CHASERS', at("out of town guys"), end("signing") + 0.1, "pill red"),
    (f'{E("📸")} FULL PHOTO REPORT', at("take pictures"), end("what we found"), "pill"),
    (f'{E("🤝")} NO DAMAGE? WE\'LL TELL YOU.', at("if there's nothing"), end("that too") + 0.3, "pill green"),
]
for k, (txt, a, b, kind) in enumerate(POPS):
    sub = '<div class="disc">Coverage depends on your policy</div>' if "INSURANCE" in txt else ""
    el.append(f'<div class="clip pop" id="pop{k}" data-start="{a:.3f}" data-duration="{b - a:.3f}" data-track-index="20">'
              f'<div class="popin" id="pl{k}"><div class="{kind}">{txt}</div>{sub}</div></div>')
    js.append(f'tl.fromTo("#pl{k}", {{opacity: 0, scale: 0.6}}, {{opacity: 1, scale: 1, duration: 0.18, ease: "back.out(2.4)"}}, {a:.3f});')
    js.append(f'tl.to("#pl{k}", {{opacity: 0, scale: 0.9, duration: 0.1, ease: "power2.in"}}, {b - 0.1:.3f});')
# Damage list: one item per word, stacked.
DL = [("HAIL HITS", SNAPS[0]), ("CRACKED SHINGLES", SNAPS[1]), ("SOFT WOOD", SNAPS[2]), ("LEAKS", SNAPS[3])]
DL_END = end("the attic") + 0.3
items = "".join(f'<div class="dl" id="dl{k}"><span class="x">✕</span>{html.escape(t)}</div>' for k, (t, _) in enumerate(DL))
el.append(f'<div class="clip dlist" id="dlist" data-start="{DL[0][1]:.3f}" data-duration="{DL_END - DL[0][1]:.3f}" data-track-index="21">{items}</div>')
for k, (_, t) in enumerate(DL):
    js.append(f'tl.fromTo("#dl{k}", {{opacity: 0, x: -60, scale: 1.15}}, {{opacity: 1, x: 0, scale: 1, duration: 0.14, ease: "power3.out"}}, {t:.3f});')
js.append(f'tl.to("#dlist", {{opacity: 0, duration: 0.12}}, {DL_END - 0.12:.3f});')
# Brand reveal with a light sweep.
B0, B1 = at("pinecrest roofing"), at("we get up") - 0.1
el.append(f'<div class="clip brand" id="brand" data-start="{B0:.3f}" data-duration="{B1 - B0:.3f}" data-track-index="22">'
          f'<div class="brandin" id="brandin"><div class="b1">PINECREST</div><div class="b2">ROOFING &amp; CONSTRUCTION</div><i id="sweep"></i></div></div>')
js.append(f'tl.fromTo("#brandin", {{opacity: 0, scale: 1.3}}, {{opacity: 1, scale: 1, duration: 0.2, ease: "back.out(2)"}}, {B0:.3f});')
js.append(f'tl.fromTo("#sweep", {{xPercent: -150}}, {{xPercent: 420, duration: 0.9, ease: "power2.inOut"}}, {B0 + 0.3:.3f});')
js.append(f'tl.to("#brandin", {{opacity: 0, duration: 0.12}}, {B1 - 0.12:.3f});')
# End CTA: name above a red pulsing button, held to the last frame.
C0 = at("tap the link")
el.append(f'<div class="clip cta" id="cta" data-start="{C0:.3f}" data-duration="{DUR - C0:.3f}" data-track-index="23">'
          f'<div class="ctaname" id="ctaname">PINECREST ROOFING &amp; CONSTRUCTION</div>'
          f'<div class="ctabtn" id="ctabtn">BOOK YOUR FREE INSPECTION {E("👇")}</div></div>')
js.append(f'tl.fromTo("#ctaname", {{opacity: 0, y: -20}}, {{opacity: 1, y: 0, duration: 0.2, ease: "power3.out"}}, {C0:.3f});')
js.append(f'tl.fromTo("#ctabtn", {{opacity: 0, scale: 0.5}}, {{opacity: 1, scale: 1, duration: 0.22, ease: "back.out(2.2)"}}, {C0:.3f});')
n_pulse = int((DUR - C0 - 0.3) / 0.5)
js.append(f'tl.fromTo("#ctabtn", {{scale: 1}}, {{scale: 1.07, duration: 0.25, ease: "sine.inOut", yoyo: true, repeat: {n_pulse * 2 - 1}, immediateRender: false}}, {C0 + 0.3:.3f});')

# ---------------- captions: 2-3 words, word-by-word highlight, yellow/red keywords ----------------
YEL = ["north texas", "thirty thousand dollars", "thousands of dollars", "everything looks fine", "different story", "hail",
       "cracked shingles", "soft wood", "leaks", "covered by your insurance", "taken advantage of", "pinecrest", "nothing there",
       "free inspection"]
RED = ["damage", "out of town guys", "gone"]
color = {}
for lst, c in ((YEL, "y"), (RED, "r")):
    for p in lst:
        st = 0
        while True:
            try: ix = find(p, st)
            except SystemExit: break
            for i in ix: color[i] = c
            st = ix[-1] + 1
i30 = find("thirty thousand dollars")[0]
OVERRIDE = {i30: "$30,000", i30 + 1: None, i30 + 2: None}      # spoken "thirty thousand dollars", shown as the number
def disp(i):
    if i in OVERRIDE: return OVERRIDE[i]
    return re.sub(r"[.,?!]+$", "", words[i]["text"]).upper()
KEEP = [find(p) for p in ("north texas", "it's a different story", "cracked shingles", "soft wood", "nothing there", "free inspection",
                          "taken advantage of", "out of town guys", "up here", "the attic", "your insurance", "what we found",
                          "goes wrong", "i get it", "of everything", "really in", "that too", "the good news is", "every spring")]
together = {i: tuple(g) for g in KEEP for i in g}
groups, cur = [], []
for i, w in enumerate(words):
    if cur:
        prev = words[cur[-1]]
        same = together.get(i) is not None and together.get(i) == together.get(cur[-1])
        brk = len([j for j in cur if disp(j)]) >= 3 or re.search(r"[.,?!]$", prev["text"]) or w["start"] - prev["end"] > 0.3
        if same and len(cur) < 4: brk = False
        if together.get(i) and together.get(i)[0] == i and len(cur) + len(together[i]) > 3: brk = True   # keep phrases whole
        if brk: groups.append(cur); cur = []
    cur.append(i)
groups.append(cur)
merged = []   # fold one-word stragglers into the previous card so each stays readable
for g in groups:
    if merged and len([i for i in g if disp(i)]) <= 1 and len([i for i in merged[-1] if disp(i)]) <= 2 \
            and not re.search(r"[.?!]$", words[merged[-1][-1]]["text"]):
        merged[-1] = merged[-1] + g
    else: merged.append(g)
groups, k = [], 0
while k < len(merged):   # a lone word that could not join the card before it joins the next one when that stays short
    g = merged[k]
    if k + 1 < len(merged) and len([i for i in g if disp(i)]) == 1 and len(" ".join(disp(i) for i in g + merged[k + 1] if disp(i))) <= 14:
        groups.append(g + merged[k + 1]); k += 2
    else: groups.append(g); k += 1
GAP_EM = 0.32
def units(t):   # approximate width in em of Montserrat 900 caps
    return sum(0.3 if c == " " else 0.32 if c in ".,'-?!" else 1.0 if c in "MW" else 0.42 if c in "I1" else 0.6 if c in "$" else 0.8 for c in t)
cap = []
for gi, g in enumerate(groups):
    vis = [i for i in g if disp(i)]
    s0 = words[g[0]]["start"]; nxt = words[groups[gi + 1][0]]["start"] if gi + 1 < len(groups) else DUR
    e0 = DUR if gi == len(groups) - 1 else min(nxt, words[g[-1]]["end"] + 0.4, DUR)
    ws = "".join(f'<span class="w" id="w{i}">{html.escape(disp(i))}</span>' for i in vis)
    em = sum(units(disp(i)) for i in vis) + GAP_EM * (len(vis) - 1)
    fs = int(min(92, (W - 140) / 1.14 / em))
    wrap = ""
    if fs < 64 and len(vis) > 1:
        fs, wrap = int(min(80, (W - 140) / 1.14 / max(em / 2 + GAP_EM, max(units(disp(i)) for i in vis)))), "; flex-wrap: wrap"
    cap.append(f'<div class="cg" id="cg{gi}"><div class="line" style="font-size:{fs}px{wrap}">{ws}</div></div>')
    js.append(f'tl.fromTo("#cg{gi}", {{opacity: 0, scale: 0.85}}, {{opacity: 1, scale: 1, duration: 0.08, ease: "power2.out"}}, {s0:.3f});')
    for i in vis:
        col = {"y": "#ffd60a", "r": "#ff3b30"}.get(color.get(i), "#ffffff")
        js.append(f'tl.fromTo("#w{i}", {{opacity: 0.55, scale: 1, color: "#ffffff"}}, {{opacity: 1, scale: 1.12, color: "{col}", duration: 0.07}}, {words[i]["start"]:.3f});')
        js.append(f'tl.to("#w{i}", {{scale: 1, duration: 0.1}}, {max(words[i]["start"] + 0.07, words[i]["end"]):.3f});')
    js.append(f'tl.set("#cg{gi}", {{opacity: 0, visibility: "hidden"}}, {e0:.3f});')

# ---------------- sound design (Mixkit SFX, always under the voice) ----------------
fx("boom", at("north texas"), 0.42)
fx("kaching", at("thirty thousand"), 0.38)
fx("beep", at("damage"), 0.28)
fx("birds", CUTS[4], 0.32, end("fine") - CUTS[4])                       # suburban birds, hard cut on "fine"
fx("whip", WHIP - 0.86, 0.42)                                          # big whoosh peaks on the flash
fx("ice", SNAPS[0], 0.42); fx("crack", SNAPS[1], 0.45); fx("creak", SNAPS[2], 0.45); fx("drip", SNAPS[3], 0.5)
fx("ding", at("covered by your"), 0.34)
fx("thunder", at("hail pretty much") - 0.1, 0.42)
fx("scribble", at("push you into"), 0.4)
fx("peel", at("gone") - 0.27, 0.42)
fx("swoosh", at("pinecrest roofing") - 0.12, 0.42); fx("pop", at("pinecrest roofing") + 0.05, 0.4)
for k, t in enumerate((at("pictures of"), at("pictures of") + 0.42, at("everything", find("pictures of")[0]))):
    fx("shutter" if k % 2 == 0 else "shutter2", t, 0.45)
fx("warm", at("we'll tell you"), 0.42)
fx("tap", at("tap the link"), 0.45)
fx("notify", at("free inspection"), 0.4); fx("boom", at("free inspection"), 0.26)   # last hit with the music

aud = []
for n, (k, t, v, d) in enumerate(sorted(sfx, key=lambda x: x[1])):
    f = f"assets/sfx/{k}.wav"
    aud.append(f'<audio id="fx{n}" src="{f}" data-start="{t:.3f}" data-duration="{min(d or probe(f), DUR - t):.3f}" data-track-index="{40 + n}" data-volume="{v}"></audio>')

CSS = f"""
      @font-face {{ font-family: "Montserrat"; font-weight: 900; src: url("vendor/montserrat-latin-900-normal.woff2") format("woff2"); }}
      @font-face {{ font-family: "Inter"; font-weight: 600; src: url("vendor/inter-latin-600-normal.woff2") format("woff2"); }}
      @font-face {{ font-family: "Inter"; font-weight: 800; src: url("vendor/inter-latin-800-normal.woff2") format("woff2"); }}
      @font-face {{ font-family: "Noto Color Emoji"; src: url("vendor/NotoColorEmoji.ttf") format("truetype"); }}
      body {{ margin: 0; background: #000; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; background: #000; color: #fff;
              font-family: "Montserrat", "Noto Color Emoji", sans-serif; font-weight: 900; }}
      .emo {{ font-family: "Noto Color Emoji", sans-serif; }}
      .yel {{ color: #ffd60a; }}

      /* Picture: whip > punch > push wrappers (untimed), graded */
      #whip, #punch, #push {{ position: absolute; inset: 0; transform-origin: 50% 50%; }}
      #grade {{ position: absolute; left: 0; top: {VID_Y}px; width: 1080px; height: 1920px; }}
      #src {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; }}
      #warmth {{ position: absolute; inset: 0; pointer-events: none; background: rgba(255, 170, 90, 0.06); mix-blend-mode: soft-light; }}
      #vignette {{ position: absolute; inset: 0; pointer-events: none; background: radial-gradient(ellipse 85% 70% at 50% 48%, rgba(0,0,0,0) 60%, rgba(0,0,0,0.32) 100%); }}
      #flash {{ position: absolute; inset: 0; background: #fff; opacity: 0; pointer-events: none; }}

      /* Top pop-ups */
      .pop {{ position: absolute; left: 60px; right: 60px; top: {L["pop_top"]}px; height: {L["pop_h"]}px; display: flex; align-items: center; justify-content: center; }}
      .popin {{ display: flex; flex-direction: column; align-items: center; }}
      .pill {{ display: block; padding: 20px 34px 16px; border-radius: 20px; background: #fff; color: #111; font-size: 54px; white-space: nowrap;
              box-shadow: 0 12px 34px rgba(0, 0, 0, 0.45); }}
      .pill.dark {{ background: rgba(12, 12, 12, 0.86); color: #fff; }}
      .pill.red {{ background: #dc2626; color: #fff; }}
      .pill.green {{ background: #16a34a; color: #fff; font-size: 48px; }}
      .disc {{ margin-top: {L["disc_gap"]}px; padding: 6px 16px; border-radius: 10px; background: rgba(0, 0, 0, 0.6); font-family: "Inter", sans-serif;
              font-weight: 600; font-size: 28px; color: rgba(255, 255, 255, 0.92); }}
      .dlist {{ position: absolute; left: 60px; top: {L["list_top"]}px; width: 800px; }}
      .dl {{ display: flex; align-items: center; width: fit-content; margin-bottom: 14px; padding: 12px 26px 10px 18px; border-radius: 14px;
            background: rgba(0, 0, 0, 0.78); border-left: 10px solid #ffd60a; font-size: 56px; color: #ffd60a; opacity: 0; transform-origin: 0 50%; }}
      .dl .x {{ margin-right: 16px; font-size: 44px; color: #ff3b30; }}
      .brand {{ position: absolute; left: 60px; right: 60px; top: {L["brand_top"]}px; height: 260px; display: flex; align-items: center; justify-content: center; }}
      .brandin {{ position: relative; overflow: hidden; padding: 22px 36px 26px; border-radius: 22px; background: rgba(10, 10, 10, 0.62);
                 border: 3px solid rgba(232, 199, 122, 0.9); text-align: center; }}
      .b1 {{ font-size: 132px; letter-spacing: 6px; color: #fff; line-height: 1; }}
      .b2 {{ margin-top: 10px; font-size: 44px; letter-spacing: 3px; color: #e8c77a; }}
      #sweep {{ position: absolute; top: -30%; bottom: -30%; left: 0; width: 28%; transform: skewX(-18deg);
               background: linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,250,230,0.8) 50%, rgba(255,255,255,0) 100%); }}
      .cta {{ position: absolute; left: 60px; right: 60px; top: {L["cta_top"]}px; height: 300px; display: flex; flex-direction: column; align-items: center; justify-content: center; }}
      .ctaname {{ margin-bottom: 20px; font-size: 44px; letter-spacing: 1px; color: #fff; -webkit-text-stroke: 9px #000; paint-order: stroke fill; white-space: nowrap; }}
      .ctabtn {{ width: 100%; padding: 32px 20px 28px; border-radius: 30px; background: #e3121e; text-align: center; font-size: 48px; line-height: 1.1;
                box-shadow: 0 12px 0 #7a0000, 0 18px 44px rgba(227, 18, 30, 0.5); box-sizing: border-box; white-space: nowrap; }}

      /* Captions: lower-middle, bold white, thick outline, word-by-word */
      #captions {{ position: absolute; left: 0; right: 0; top: {L["cap_top"]}px; height: {L["cap_h"]}px; }}
      .cg {{ position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; opacity: 0; }}
      .cg .line {{ display: flex; flex-wrap: nowrap; justify-content: center; align-items: center; gap: 0 0.32em; max-width: {W - 120}px; line-height: 1.08; }}
      .w {{ display: inline-block; color: #fff; -webkit-text-stroke: 0.17em #000; paint-order: stroke fill; text-shadow: 0 0.08em 0 #000, 0 0.1em 0.25em rgba(0,0,0,0.5);
           opacity: 0.55; white-space: nowrap; }}
"""
doc = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <title>Pinecrest Rough Cut {"9x16" if FMT == "916" else "4x5"}</title>
    <script src="vendor/gsap.min.js"></script>
    <style>{CSS}    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="{W}" data-height="{H}" data-duration="{DUR}">
      <div id="whip"><div id="punch"><div id="push"><div id="grade">
        <video id="src" class="clip" src="assets/source.mp4" muted playsinline data-start="0" data-duration="{DUR}" data-track-index="0"></video>
      </div></div></div></div>
      <div id="warmth"></div>
      <div id="vignette"></div>
      {chr(10).join("      " + e for e in el).lstrip()}
      <div id="captions" class="clip" data-start="0" data-duration="{DUR}" data-track-index="30">
        {chr(10).join("        " + c for c in cap).lstrip()}
      </div>
      <div id="flash"></div>
    </div>
    <audio id="vo" src="assets/vo.wav" data-start="0" data-duration="{DUR}" data-track-index="1" data-volume="1"></audio>
    <audio id="music" src="assets/music_bed.wav" data-start="0" data-duration="{DUR}" data-track-index="2" data-volume="1"></audio>
    {chr(10).join("    " + a for a in aud).lstrip()}
    <script>
      const tl = gsap.timeline({{ paused: true }});
      {chr(10).join("      " + j for j in js).lstrip()}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
if OUT != ".":
    os.makedirs(OUT, exist_ok=True)
    for d in ("assets", "vendor"):
        if not os.path.lexists(f"{OUT}/{d}"): os.symlink(f"../roughcut/{d}", f"{OUT}/{d}")
    for f in ("hyperframes.json", "package.json"):
        open(f"{OUT}/{f}", "w").write(open(f).read())
    json.dump({"id": "roughcut-ad-4x5", "name": "roughcut-ad-4x5"}, open(f"{OUT}/meta.json", "w"), indent=2)
    if not os.path.lexists(f"{OUT}/transcript.json"): os.symlink("../roughcut/transcript.json", f"{OUT}/transcript.json")
open(f"{OUT}/index.html", "w").write(doc)
print(f"{FMT}: {W}x{H} · {DUR}s · {len(CUTS)} scenes · {len(PUNCHES)} punches · {len(POPS)} pop-ups · {len(groups)} captions · {len(sfx)} sfx")
for g in groups: print(" ", round(words[g[0]]["start"], 2), " ".join(disp(i) for i in g if disp(i)))
