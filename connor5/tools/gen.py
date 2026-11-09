"""Connor ad in the client's reference style (ref1/STYLE.md): the take untouched in time, framing cuts between a
full shot and closer shots at the reference's beats, a two-box hook header, Bebas captions with the spoken word in
yellow, big build-up lines with the spoken word in green, one photo card, and a dark-bottom CTA. Voice only.

  gen.py      -> index.html (1080x1920)
"""
import html, json, os, re, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
W, H = 1080, 1920
probe = lambda f: float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f], capture_output=True, text=True).stdout)
DUR = round(probe("assets/look.mp4") - 0.04, 3)
words = json.load(open("transcript.json"))
def clean(t): return re.sub(r"[.,?!]+$", "", t).lower()
def find(p, after=0):
    toks = p.lower().split()
    for i in range(after, len(words)):
        if [clean(w["text"]) for w in words[i:i + len(toks)]] == toks: return list(range(i, i + len(toks)))
    sys.exit(f"phrase not found: {p}")
def at(p, after=0): return words[find(p, after)[0]]["start"]
el, js = [], []

# ---------------- framing cuts (same beats as the reference) ----------------
FR = {"W": 1.0, "M": 1.25, "C": 1.45}
CUTS = [(0.0, "W"), (at("you need") - 0.04, "C"), (at("insurance carriers") - 0.04, "W"), (at("doesn't cut") - 0.04, "M"),
        (at("we at") - 0.04, "W"), (at("the documentation") - 0.04, "C"), (at("and with that") - 0.04, "W"),
        (at("with no hidden") - 0.04, "C"), (at("so book") - 0.04, "W")]
for t, k in CUTS: js.append(f'tl.set("#cam", {{scale: {FR[k]}}}, {t:.3f});')
FIRST_CUT = CUTS[1][0]

# ---------------- hook header (until the first cut) ----------------
el.append(f'<div class="clip hdr" id="hdr" data-start="0" data-duration="{FIRST_CUT:.3f}" data-track-index="20">'
          '<div class="hb hb1">TEXAS HOMEOWNERS,</div><div class="hb hb2">read your mail!</div></div>')

# ---------------- photo card: in on "non-renewal", out with a blur-drop into the first cut ----------------
K0 = at("non-renewal")
el.append(f'<div class="clip" id="g-card" data-start="{K0:.3f}" data-duration="{FIRST_CUT - K0:.3f}" data-track-index="21">'
          '<div class="card" id="card"><img src="assets/card-insurance.jpg" alt="" /></div></div>')
js.append(f'tl.fromTo("#card", {{opacity: 0, scale: 0.86, y: 30}}, {{opacity: 1, scale: 1, y: 0, duration: 0.18, ease: "back.out(1.8)"}}, {K0:.3f});')
js.append(f'tl.to("#card", {{opacity: 0, y: 140, filter: "blur(14px)", duration: 0.2, ease: "power2.in"}}, {FIRST_CUT - 0.2:.3f});')

# ---------------- big build-up lines ("you need an expert / to help you navigate it") ----------------
BIG = [["you need", "an expert"], ["to help you", "navigate it"]]
big_idx, k = set(), 0
for bi, lines in enumerate(BIG):
    ids = [find(" ".join(lines))[0] + j for j in range(len(" ".join(lines).split()))]
    big_idx.update(ids)
    b0 = words[ids[0]]["start"] - 0.04
    b1 = words[find(" ".join(BIG[bi + 1]))[0]]["start"] - 0.04 if bi + 1 < len(BIG) else at("insurance carriers") - 0.04
    rows, n = [], 0
    for ln in lines:
        toks = ln.split(); rows.append('<div class="bl">' + " ".join(f'<span class="bw" id="bw{ids[n + j]}">{html.escape(t.upper())}</span>' for j, t in enumerate(toks)) + "</div>"); n += len(toks)
    el.append(f'<div class="clip big" id="g-big{bi}" data-start="{b0:.3f}" data-duration="{b1 - b0:.3f}" data-track-index="22">{"".join(rows)}</div>')
    for j, i in enumerate(ids):
        t = words[i]["start"]
        js.append(f'tl.set("#bw{i}", {{opacity: 1, color: "#22c55e"}}, {t:.3f});')
        if j + 1 < len(ids): js.append(f'tl.set("#bw{i}", {{color: "#ffffff"}}, {words[ids[j + 1]]["start"]:.3f});')

# ---------------- end CTA (dark bottom, holds to the last frame) ----------------
C0 = at("so book")
arrow = '<svg viewBox="0 0 74 92"><path d="M37 4v70M10 50l27 30 27-30" stroke="#22c55e" stroke-width="10" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>'
el.append(f'<div class="clip" id="g-cta" data-start="{C0:.3f}" data-duration="{DUR - C0:.3f}" data-track-index="23"><div class="shade" id="shade"></div>'
          f'<div class="cta" id="cta"><div class="c1">BOOK YOUR</div><div class="c2">30-MINUTE<br>INSPECTION</div><div class="arrows">{arrow * 3}</div></div></div>')
js.append(f'tl.to("#shade", {{opacity: 1, duration: 0.25}}, {C0:.3f});')
js.append(f'tl.fromTo("#cta", {{opacity: 0, y: 40}}, {{opacity: 1, y: 0, duration: 0.25, ease: "power3.out"}}, {C0:.3f});')

# ---------------- captions: 2-4 words, spoken word yellow; the big lines replace them while they are up ----------------
DISP = {"pine": "PINECREST", "crest": None}
def disp(i):
    c = clean(words[i]["text"])
    return DISP[c] if c in DISP else words[i]["text"].upper()   # the reference keeps commas and full stops
# phrases broken the way the reference breaks them (2-4 words, at natural pauses); the big lines are skipped
PH = ["If you've received a", "non-renewal notice", "from your insurance", "or your premiums", "are skyrocketing,",
      "Insurance carriers", "in Texas are", "tightening the screws", "and simply good", "enough just doesn't", "cut it anymore.",
      "We at Pine Crest", "Roofing and Construction", "provide a detailed", "roof analysis to", "provide you with", "the documentation",
      "you need to satisfy", "your insurance.", "And with that, we give", "you a real cost on", "roof replacement", "with no hidden fees.",
      "So book your", "30-minute inspection", "to get your", "roof analyzed", "for insurance", "compliance and", "save your coverage."]
order = [i for i in range(len(words)) if i not in big_idx]
groups, k = [], 0
for ph in PH:
    n = len(ph.split()); g = order[k:k + n]
    assert [clean(words[i]["text"]) for i in g] == [clean(t) for t in ph.split()], (ph, [words[i]["text"] for i in g])
    groups.append(g); k += n
assert k == len(order)
cap = []
for gi, g in enumerate(groups):
    vis = [i for i in g if disp(i)]
    s0 = words[g[0]]["start"] - 0.03
    nxt = words[groups[gi + 1][0]]["start"] - 0.03 if gi + 1 < len(groups) else DUR
    e0 = min(nxt, words[g[-1]]["end"] + 0.35, DUR) if gi + 1 < len(groups) else DUR
    if any(s0 < words[i]["start"] < e0 for i in big_idx): e0 = min(e0, min(words[i]["start"] for i in big_idx if words[i]["start"] > s0) - 0.04)
    cap.append(f'<div class="cg" id="cg{gi}">' + "".join(f'<span class="w" id="w{i}">{html.escape(disp(i))}</span>' for i in vis) + "</div>")
    js.append(f'tl.set("#cg{gi}", {{opacity: 1}}, {s0:.3f});'); js.append(f'tl.set("#cg{gi}", {{opacity: 0}}, {e0:.3f});')
    seq = [i for i in g if words[i]["start"] < e0]
    for j, i in enumerate(seq):
        tgt = i if disp(i) else i - 1          # "Crest" keeps PINECREST lit
        js.append(f'tl.set("#w{tgt}", {{color: "#ffd21f"}}, {words[i]["start"]:.3f});')
        nt = words[seq[j + 1]]["start"] if j + 1 < len(seq) else e0
        if not (j + 1 < len(seq) and not disp(seq[j + 1])): js.append(f'tl.set("#w{tgt}", {{color: "#ffffff"}}, {nt:.3f});')

CSS = open("tools/style.css").read()
nl = "\n      "
doc = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <title>Connor Reference Ad</title>
    <script src="vendor/gsap.min.js"></script>
    <style>
{CSS}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="{W}" data-height="{H}" data-duration="{DUR}">
      <div id="cam">
        <video id="src" class="clip" src="assets/look.mp4" muted playsinline data-start="0" data-duration="{DUR}" data-track-index="0"></video>
      </div>
      {nl.join(el)}
      <div id="captions" class="clip" data-start="0" data-duration="{DUR}" data-track-index="30">
        {(nl + "  ").join(cap)}
      </div>
    </div>
    <audio id="vo" src="assets/vo.wav" data-start="0" data-duration="{DUR}" data-track-index="1" data-volume="1"></audio>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      {nl.join(js)}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
open("index.html", "w").write(doc)
print(f"{DUR}s · {len(CUTS) - 1} framing cuts · {len(groups)} caption groups · big lines {len(BIG)}")
for g in groups: print(f"  {words[g[0]]['start']:6.2f} " + " ".join(d for d in (disp(i) for i in g) if d))
