"""Pinecrest live-action ad re-cut in the style of the supplied reference ad (9:16).

Reference style: presenter on camera for the opening with kinetic stacked condensed words, a pinned
circular offer seal top-left, small sentence-case captions on black tags (no highlights), moody B-roll
cutting every 1-3 s, a bloom + blur settle when cutting back to the presenter, a stack of inspection
report pages built from real damage photos, and a white BOOK NOW pill under the last caption.
Shares media with ../pinecrest-live. Times come from transcript.json of assets/aroll.mp4.
"""
import html, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
words = json.load(open("transcript.json"))
words = words if isinstance(words, list) else words["words"]
probe = lambda f: float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                                       capture_output=True, text=True).stdout)
DUR = round(probe("assets/aroll.mp4") - 0.05, 2)

def clean(t): return re.sub(r"[.,?!]+$", "", t).lower()
def find(p, after=0):
    toks = p.lower().split()
    for i in range(after, len(words)):
        if [clean(w["text"]) for w in words[i:i + len(toks)]] == toks: return list(range(i, i + len(toks)))
    sys.exit(f"phrase not found: {p}")
def at(p, after=0): return round(words[find(p, after)[0]]["start"], 3)
def end(p, after=0): return round(words[find(p, after)[-1]]["end"], 3)

B, P = "broll/", "broll/photos/"
# ---------------- shot list (B-roll over the presenter) ----------------
# (slot source, start, end, move, extra) ; moves: push | pull | tilt-up | still | snap@t
S = []
def shot(src, t0, t1, move="push", x=0.5, ss=0.0, vf="", snaps=(), enter="cut", bright=False):
    S.append(dict(src=src, t0=round(t0, 3), t1=round(t1, 3), move=move, x=x, ss=ss, vf=vf, snaps=list(snaps), enter=enter, bright=bright))

T = {k: at(v) for k, v in dict(texas="texas", most="most homeowners", could="could be costing", thousands="thousands", and_="and i get",
                                down="from down here", but="but from up", up="up here", glaring="glaring", interior="from interior",
                                black="black mold", these="these homeowners", routine="routine roof", damage2="damage that wasn't",
                                visible="visible from", good="but the good", all_="all of it's", covered="covered by", nt2="north texas is",
                                hail_alley="hail alley", hail2="hail up to", grape="grapefruit", ive="i've seen", taken="taken advantage",
                                its="it's far", oos="out-of-state", show="show up right", force="force you into", that_need="that you don't",
                                at_pine="at pine crest", pine="pine crest", we_value="we value", honesty="honesty", we_get="we get on",
                                take="we take photos", photos="photos of", show_you="and we show", exactly="exactly what", if_="if you want",
                                roof_before="roof before it", tap="tap the link", free="free inspection").items()}
T["end_honesty"] = end("honesty")

shot(P + "hail-hole.jpg", T["thousands"], T["and_"], "push", x=0.7, snaps=[(T["thousands"] + 0.02, 1.12)])
shot(P + "house-brick-2.jpg", T["down"], T["but"], "tilt-up", x=0.58)
shot(P + "fema-c005.jpg", T["but"], T["interior"], "push", x=0.45, snaps=[(T["glaring"], 1.12)])
shot(P + "ceiling-damage.jpg", T["interior"] + 0.22, T["black"], "push", x=0.5, vf="crop=iw:ih*0.62:0:0")
shot(P + "ceiling-damage.jpg", T["black"], T["these"], "still", x=0.2, vf="crop=iw*0.55:ih*0.32:iw*0.25:0")
shot(P + "hail-doc-2.jpg", T["routine"], T["damage2"], "push", x=0.42)
shot(P + "house-brick-2.jpg", T["damage2"], T["damage2"] + 0.7, "still", x=0.58)
shot(P + "cedar-damaged-1.jpg", T["damage2"] + 0.7, T["good"], "push", x=0.42, snaps=[(T["visible"], 1.1)])
shot(B + "tablet-photos--mixkit-41204-2160p.mp4", T["all_"], T["nt2"], "push", x=0.5, ss=2, bright=True)
shot(B + "storm-powerlines--mixkit-16199-720p.mp4", T["nt2"], T["hail_alley"], "push", x=0.5, ss=2)
shot(B + "storm-rain-ground--mixkit-21185-720p.mp4", T["hail_alley"], T["hail2"], "push", x=0.5, ss=1)
shot(P + "hailstones-field.jpg", T["hail2"], T["ive"], "push", x=0.5, snaps=[(T["grape"], 1.25)])
shot(B + "handoff-door--mixkit-31137-2160p.mp4", T["taken"], T["its"], "push", x=0.35, ss=1)
shot(P + "fema-c014.jpg", T["oos"], T["show"], "push", x=0.3, vf="crop=iw*0.62:ih*0.5:0:ih*0.5")
shot(P + "fema-c014.jpg", T["show"], T["force"], "push", x=0.55, vf="crop=iw*0.75:ih*0.55:iw*0.25:ih*0.45")
shot(B + "signing-blue-ink--mixkit-38492-720p.mp4", T["force"], T["that_need"], "push", x=0.55, ss=1, snaps=[(T["force"] + 0.02, 1.1)])
shot(P + "fema-c014.jpg", T["that_need"], T["at_pine"], "pull-fast", x=0.6, vf="crop=iw*0.75:ih*0.55:iw*0.25:ih*0.45")
shot("assets/truck.mov", T["pine"], T["we_value"], "push", x=0.5, ss=25.0, snaps=[(T["pine"] + 0.02, 1.12)])
shot("assets/truck.mov", T["we_value"], T["end_honesty"] + 0.3, "push", x=0.5, ss=9.0, snaps=[(T["we_value"] + 0.02, 1.2)])
shot(P + "fema-c063.jpg", T["we_get"], T["take"], "push", x=0.5)
shot(P + "hail-doc-1.jpg", T["take"], T["photos"], "push", x=0.72)
REPORT = (T["photos"], T["exactly"] + 0.38)          # inspection-report page stack plays here
shot(B + "handshake-office--mixkit-30005-2160p.mp4", T["exactly"] + 0.38, T["if_"], "push", x=0.55, ss=1)
shot(P + "fema-c065.jpg", T["roof_before"], T["tap"], "push", x=0.55, bright=True)

# Presenter punch levels (jump cuts on the same take): (time, scale). 1.0 chest-up, 1.18 shoulders, 1.35 face.
PUNCH = [(0.0, 1.35), (T["most"], 1.0), (T["could"], 1.18), (T["and_"], 1.18), (T["these"], 1.35), (T["good"], 1.0),
         (T["ive"], 1.35), (T["its"], 1.18), (T["end_honesty"] + 0.3, 1.0), (T["if_"], 1.18), (T["tap"], 1.0)]

# ---------------- prep (grade + 9:16 conform) ----------------
jobs = []
for n, s in enumerate(S):
    base = os.path.splitext(os.path.basename(s["src"]))[0][-22:]
    if s["src"].endswith((".jpg", ".png")):
        s["file"] = f"assets/prep/p{n:02d}-{base}.jpg"
        jobs.append(dict(src=s["src"], out=s["file"], kind="photo", x=s["x"], vf=s["vf"]))
    else:
        s["file"] = f"assets/prep/v{n:02d}-{base}-{s['ss']}.mp4"
        jobs.append(dict(src=s["src"], out=s["file"], kind="video", ss=s["ss"], dur=round(s["t1"] - s["t0"] + 0.4, 2), x=s["x"], vf=s["vf"]))
json.dump(jobs, open("assets/prep-jobs.json", "w"), indent=1)
subprocess.run([sys.executable, "tools/prep.py", "assets/prep-jobs.json"], check=True, stdout=subprocess.DEVNULL)

el, js, sfx = [], [], []
def fx(name, t, vol, ms=0.0): sfx.append((name, round(max(0, t), 3), vol, ms))

# Presenter base layer.
js.append('tl.set("#cam", {scale: 1.35}, 0);')
for t, sc in PUNCH[1:]: js.append(f'tl.set("#cam", {{scale: {sc}}}, {t:.3f});')

for n, s in enumerate(S):
    sid, t0, t1 = f"s{n:02d}", s["t0"], s["t1"]
    cls = "shot bright" if s["bright"] else "shot"
    if s["file"].endswith(".mp4"):
        el.append(f'<div class="kb" id="kb-{sid}"><div class="snap" id="sn-{sid}"><video id="v-{sid}" class="clip media" src="{s["file"]}" muted playsinline '
                  f'data-start="{t0:.3f}" data-duration="{t1 - t0:.3f}" data-track-index="{2 + n % 2}"></video></div></div>')
    else:
        el.append(f'<div class="clip {cls}" id="c-{sid}" data-start="{t0:.3f}" data-duration="{t1 - t0:.3f}" data-track-index="{2 + n % 2}">'
                  f'<div class="kb" id="kb-{sid}"><div class="snap" id="sn-{sid}"><img class="media photo" src="{s["file"]}" alt="" /></div></div></div>')
    sel, d, mv = f"#kb-{sid}", t1 - t0, s["move"]
    if mv == "push": js.append(f'tl.fromTo("{sel}", {{scale: 1.0}}, {{scale: 1.08, duration: {d:.3f}, ease: "none"}}, {t0});')
    elif mv == "push-fast": js.append(f'tl.fromTo("{sel}", {{scale: 1.0, yPercent: 0}}, {{scale: 1.18, yPercent: -3, duration: {d:.3f}, ease: "none"}}, {t0});')
    elif mv == "pull-fast": js.append(f'tl.fromTo("{sel}", {{scale: 1.3}}, {{scale: 1.0, duration: 0.45, ease: "power3.out"}}, {t0});')
    elif mv == "tilt-up": js.append(f'tl.fromTo("{sel}", {{scale: 1.15, yPercent: 6}}, {{scale: 1.15, yPercent: -6, duration: {d:.3f}, ease: "sine.inOut"}}, {t0});')
    elif mv == "still": js.append(f'tl.fromTo("{sel}", {{scale: 1.0}}, {{scale: 1.03, duration: {d:.3f}, ease: "none"}}, {t0});')
    prev = 1.0
    for k, (ts, sc) in enumerate(s["snaps"]):
        js.append(f'tl.fromTo("#sn-{sid}", {{scale: {prev}}}, {{scale: {sc}, duration: 0.13, ease: "power4.out", immediateRender: {"true" if k == 0 else "false"}}}, {ts:.3f});')
        prev = sc
    if s["enter"] == "whip-up":
        js.append(f'tl.fromTo("{sel} .media", {{yPercent: 30, filter: "blur(16px)"}}, {{yPercent: 0, filter: "blur(0px)", duration: 0.22, ease: "power3.out"}}, {t0});')
    elif s["enter"] == "flash":
        js.append(f'tl.fromTo("#flash", {{opacity: 0.9}}, {{opacity: 0, duration: 0.3, ease: "power2.out", immediateRender: false}}, {t0});')

# ---------------- reference-style graphics ----------------
# Pinned circular offer seal (top-left, whole ad).
el.append(f'<div class="clip seal" id="seal" data-layout-ignore data-start="0" data-duration="{DUR}" data-track-index="25">'
          '<svg viewBox="0 0 240 240" width="232" height="232"><defs>'
          '<path id="arcT" d="M 32 120 A 88 88 0 0 1 208 120"/><path id="arcB" d="M 30 120 A 90 90 0 0 0 210 120"/></defs>'
          '<circle cx="120" cy="120" r="116" fill="#0f2a44"/><circle cx="120" cy="120" r="108" fill="#fff"/>'
          '<circle cx="120" cy="120" r="72" fill="#fff" stroke="#0f2a44" stroke-width="3"/>'
          '<text class="arc"><textPath href="#arcT" startOffset="50%" text-anchor="middle">PINECREST ROOFING</textPath></text>'
          '<text class="arc"><textPath href="#arcB" startOffset="50%" text-anchor="middle" dominant-baseline="hanging">NORTH TEXAS</textPath></text>'
          '<text x="120" y="122" class="sbig" text-anchor="middle">FREE</text>'
          '<text x="120" y="152" class="ssmall" text-anchor="middle">INSPECTION</text></svg></div>')

# Kinetic opener: stacked condensed words appear as they are spoken (no captions underneath).
def wt(p, k=0): return words[find(p)[k]]["start"]
KIN = [  # stack, lines of (word, size px, colour, time)
    [[("NORTH", 150, "b", wt("north texas")), ("TEXAS", 150, "b", wt("north texas", 1))],
     [("MOST", 64, "w", wt("most homeowners")), ("HOMEOWNERS", 112, "w", wt("most homeowners", 1))],
     [("HAVE NO", 64, "w", wt("have no idea")), ("IDEA", 150, "b", wt("have no idea", 2))]],
    [[("THEIR", 64, "w", wt("their roofing")), ("ROOF", 150, "w", wt("their roofing", 1))],
     [("COULD BE", 64, "w", wt("could be costing")), ("COSTING", 120, "b", wt("could be costing", 2))],
     [("THEM", 70, "w", wt("them thousands"))]]]
KIN_END = [wt("their roofing"), T["thousands"]]
for k, stack in enumerate(KIN):
    t0 = 0.0 if k == 0 else KIN_END[0]
    rows = "".join('<div class="krow">' + "".join(f'<span class="kw {c}" id="kw{k}-{r}-{j}" style="font-size:{sz}px">{html.escape(w)}</span>'
                                                  for j, (w, sz, c, _) in enumerate(line)) + "</div>" for r, line in enumerate(stack))
    el.append(f'<div class="clip kin" id="kin{k}" data-start="{t0:.3f}" data-duration="{KIN_END[k] - t0:.3f}" data-track-index="26">{rows}</div>')
    for r, line in enumerate(stack):
        for j, (_, _, _, tw) in enumerate(line):
            js.append(f'tl.fromTo("#kw{k}-{r}-{j}", {{opacity: 0, scale: 1.25}}, {{opacity: 1, scale: 1, duration: 0.09, ease: "power3.out"}}, {max(t0, tw - 0.03):.3f});')
CAP_START = T["thousands"]

# Inspection report: tilted white pages of real damage photos stacking up.
REP_PHOTOS = [("hail-hole.jpg", "Hail impact through skylight"), ("hail-doc-2.jpg", "Inspector documenting roof"),
              ("cedar-damaged-1.jpg", "Cracked & lifted shingles"), ("ceiling-damage.jpg", "Interior water damage"),
              ("hail-inspect-1.jpg", "Roof surface walkthrough"), ("hail-partners.jpg", "Rooftop unit check"),
              ("fema-c005.jpg", "Underlayment exposed"), ("fema-c077.jpg", "Shingle fastening check")]
for f, _ in REP_PHOTOS:
    out = f"assets/prep/rep-{f}"
    if not os.path.exists(out):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", P + f, "-vf", "scale=640:480:force_original_aspect_ratio=increase,crop=640:480", "-q:v", "3", out], check=True)
pages, rots = [], [-5, 4, -2, 6]
for pg in range(4):
    cells = "".join(f'<div class="rcell"><img src="assets/prep/rep-{f}" alt="" /><span>{html.escape(lbl)}</span></div>'
                    for f, lbl in REP_PHOTOS[pg * 2: pg * 2 + 2] + REP_PHOTOS[(pg * 2 + 3) % 8: (pg * 2 + 3) % 8 + 2])
    head = '<div class="rhead">ROOF INSPECTION REPORT<b>Photo documentation · Page ' + str(pg + 1) + ' of 20</b></div>'
    pages.append(f'<div class="rpage" id="rp{pg}" style="transform: rotate({rots[pg]}deg)">{head}<div class="rgrid">{cells}</div></div>')
el.append(f'<div class="clip report" id="report" data-start="{REPORT[0]:.3f}" data-duration="{REPORT[1] - REPORT[0]:.3f}" data-track-index="24">'
          f'<div class="rbg"></div>{"".join(pages)}</div>')
step = (REPORT[1] - REPORT[0] - 0.3) / 4
for pg in range(4):
    tp = REPORT[0] + pg * step
    js.append(f'tl.fromTo("#rp{pg}", {{opacity: 0, y: 260, scale: 1.08}}, {{opacity: 1, y: 0, scale: 1, duration: 0.22, ease: "power3.out"}}, {tp:.3f});')
    fx("shutter", tp + 0.05, 0.3)
    if pg:   # the page underneath keeps only its edge visible once covered
        js.append(f'tl.set("#rp{pg - 1} .rhead, #rp{pg - 1} .rgrid", {{visibility: "hidden"}}, {tp + 0.22:.3f});')
js.append(f'tl.fromTo("#report .rbg", {{scale: 1}}, {{scale: 1.05, duration: {REPORT[1] - REPORT[0]:.3f}, ease: "none"}}, {REPORT[0]:.3f});')

# BOOK NOW pill under the closing caption.
el.append(f'<div class="clip booknow" id="booknow" data-start="{T["tap"]:.3f}" data-duration="{DUR - T["tap"]:.3f}" data-track-index="27"><span id="bn">BOOK NOW</span></div>')
js.append(f'tl.fromTo("#bn", {{opacity: 0, scale: 0.6}}, {{opacity: 1, scale: 1, duration: 0.18, ease: "back.out(2.5)"}}, {T["tap"]:.3f});')

# Back to the presenter: quick bloom-dissolve into a zoomed, blurred frame that settles sharp.
cover = sorted((s["t0"], s["t1"]) for s in S) + [REPORT]
cover.sort()
returns = []
for k, (a0, a1) in enumerate(cover):
    nxt = cover[k + 1][0] if k + 1 < len(cover) else DUR
    if nxt - a1 > 0.25: returns.append(a1)
for t in returns:
    js.append(f'tl.fromTo("#bloom", {{opacity: 0.75}}, {{opacity: 0, duration: 0.28, ease: "power2.out", immediateRender: false}}, {t:.3f});')
    js.append(f'tl.fromTo("#settle", {{scale: 1.1, filter: "blur(10px)"}}, {{scale: 1, filter: "blur(0px)", duration: 0.3, ease: "power2.out", immediateRender: false}}, {t:.3f});')

# ---------------- captions: small sentence-case text on black tags, 2-3 words, no highlights ----------------
ia = find("all of it's")[0]
OVERRIDE = {ia: "Often", ia + 1: None, ia + 2: None}          # "All of it's covered" -> "Often covered" on screen
def disp(i):
    if i in OVERRIDE: return OVERRIDE[i]
    t = words[i]["text"]
    if clean(t) == "pine" and clean(words[i + 1]["text"]) == "crest": return "Pinecrest"
    if clean(t) == "crest" and clean(words[i - 1]["text"]) == "pine": return None
    return t
first = next(i for i, w in enumerate(words) if w["start"] >= CAP_START - 0.01)
groups, cur = [], []
for i in range(first, len(words)):
    w = words[i]
    if cur:
        prev = words[cur[-1]]
        if len(cur) >= 3 or re.search(r"[.,?!]$", prev["text"]) or w["start"] - prev["end"] > 0.25: groups.append(cur); cur = []
    cur.append(i)
groups.append(cur)
merged = []
for g in groups:
    if merged and len([i for i in g if disp(i)]) <= 1 and len(merged[-1]) <= 2 and not re.search(r"[.?!]$", words[merged[-1][-1]]["text"]):
        merged[-1] = merged[-1] + g
    else: merged.append(g)
groups = merged
cap = []
for gi, g in enumerate(groups):
    txt = " ".join(disp(i) for i in g if disp(i))
    s0 = words[g[0]]["start"]; nxt = words[groups[gi + 1][0]]["start"] if gi + 1 < len(groups) else DUR
    e0 = DUR if gi == len(groups) - 1 else min(nxt, words[g[-1]]["end"] + 0.45, DUR)
    cap.append(f'<div class="cg" id="cg{gi}"><span class="tag">{html.escape(txt)}</span></div>')
    js.append(f'tl.set("#cg{gi}", {{opacity: 1, visibility: "visible"}}, {s0:.3f});')
    js.append(f'tl.set("#cg{gi}", {{opacity: 0, visibility: "hidden"}}, {e0:.3f});')

# ---------------- sound design: clean, like the reference (whooshes on cuts, a few anchors) ----------------
for k, stack in enumerate(KIN):
    for line in stack: fx("pop", line[-1][3], 0.08)
fx("impact", T["texas"], 0.14)
fx("thunder", T["nt2"], 0.2); fx("hail", T["hail_alley"], 0.12)
fx("whoosh", T["pine"] - 0.1, 0.22)
fx("notify", T["free"], 0.22)
for t in returns: fx("whoosh-short", t - 0.08, 0.07)
for s in S:
    if s["t0"] > 0.1: fx("whoosh-short", s["t0"] - 0.06, 0.06)
EXT = {"impact": "mp3", "whoosh": "mp3", "whoosh-short": "mp3", "pop": "mp3", "chime": "mp3", "notify": "mp3", "riser": "mp3"}
aud = []
for n, (k, t, v, ms) in enumerate(sorted(sfx, key=lambda x: x[1])):
    f = f"assets/sfx-{k}.{EXT.get(k, 'wav')}"
    aud.append(f'<audio id="fx{n}" src="{f}" data-start="{t:.3f}" data-duration="{min(probe(f), DUR - t):.3f}" data-track-index="{40 + n}" data-volume="{v}"></audio>')

tpl = open("tools/ad.template.html").read()
for k, v in {"{{DUR}}": f"{DUR}", "{{ELEMENTS}}": "\n      ".join(el), "{{CAPTIONS}}": "\n        ".join(cap),
             "{{AUDIO}}": "\n    ".join(aud), "{{JS}}": "\n      ".join(js)}.items():
    tpl = tpl.replace(k, v)
open("index.html", "w").write(tpl)
json.dump({k: v for k, v in T.items()}, open("assets/times.json", "w"), indent=1)
spans, last = [], 0.0
ev = sorted({0.0, *[s["t0"] for s in S], *[s["t1"] for s in S], *[t for t, _ in PUNCH], *[t for s in S for t, _ in s["snaps"]]})
gaps = [(round(a, 2), round(b - a, 2)) for a, b in zip(ev, ev[1:] + [DUR]) if b - a > 3.0]
print(f"duration {DUR}s · {len(S)} B-roll shots · {len(groups)} caption groups · {len(sfx)} sfx · gaps>3s: {gaps or 'none'}")
