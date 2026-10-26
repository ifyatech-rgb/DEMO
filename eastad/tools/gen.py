"""Pinecrest East Texas ad: motion graphics, callouts, kinetic type, captions, camera and sound layered on the client's
finished edit (assets/source.mp4). Nothing in the edit is re-timed; the client's VO + music track plays as-is.

  gen.py 916 -> eastad/index.html       (1080x1920)
  gen.py 45  -> eastad-4x5/index.html   (1080x1350, picture cover-cropped to the middle)

Picture stack (all untimed wrappers around one muted <video>):
  #cam (per-scene push / pull / rotate / pan) > #punch (115 % punch-ins) > #shake >
    #soft (dims + blurs the footage while a big graphic is up) > #grade (colour) > video + freeze frames
    #callouts (inspector circles / arrows / labels, in footage coordinates so they ride the camera move)
Graphics sit in a fixed "stage" box above the captions; one font (Montserrat 900/800), one palette
(yellow #ffd60a, red #e3121e, white, green #16a34a), one pop-in (scale 0.6 -> 1, back.out).
"""
import html, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
FMT = sys.argv[1] if len(sys.argv) > 1 else "916"
W, H = 1080, (1920 if FMT == "916" else 1350)
OUT = "." if FMT == "916" else "../eastad-4x5"
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
def nth(p, n):   # start of the n-th occurrence (0-based)
    st = 0
    for _ in range(n): st = find(p, st)[-1] + 1
    return words[find(p, st)[0]]["start"]

# ---------------- layout (Meta safe zones) ----------------
if FMT == "916":   # Reels: clear of top 14 % / bottom 35 %, 60 px sides
    L = dict(stage=560, chip=1180)        # graphics centred on the frame (centre y 860)
else:              # 4:5 feed
    L = dict(stage=375, chip=1200)        # centre y 675
STAGE_H = 600
SHOW_CAPTIONS = False                     # client: no subtitles, the designed text carries the words
VID_Y = (H - 1920) // 2

# ---------------- key times ----------------
T = dict(north=at("east texas"), watch=at("watch this"), before=at("before you"), you1=at("you spend"), spend=at("spend"),
         k30=at("$30,000"), own=at("of your own"), money=at("money"), if_=at("if your roof"), five=at("5 to"), old=at("old"),
         recently=at("recently"), storm=at("storm"), insurance=at("insurance company"), owes=at("owes"), proper=at("proper"),
         replacement=at("replacement"), but=at("but most"), underpay=at("underpay"), deny=at("deny"), that=at("that is exactly"),
         pine=at("pine crest"), weve=at("we've helped"), dozens=at("dozens"), fully=at("fully approved"), ins2=nth("insurance", 1),
         guide=at("we guide"), entire=at("entire"), ins3=nth("insurance", 2), process=at("process"), make=at("make sure"),
         get=at("get what"), entitled=at("entitled"), limited=at("for a limited"), offering=at("offering"), free=at("free no-obligation"),
         inspection1=at("inspection to"), check=at("check for"), storm2=nth("storm", 1), just=at("just click"), learn=at("learn more"),
         below=at("below"), book=at("book your"), free2=nth("free", 1))
T["end_completely"] = end("completely"); T["end_damage"] = end("storm damage")

# The client's cuts (frame-diff spikes); camera move changes on each.
CUTS = [0.0, 1.933, 3.533, 6.233, 8.05, 8.95, 9.567, 11.6, 12.2, 12.567, 13.2, 16.2, 21.1, 23.667, 26.2, 28.833]
MOVES = ["push", "pull", "rot", "pan", "push", "rotr", "pull", "pan", "push", "rot", "pull", "pan", "push", "rotr", "pull", "push"]

el, js, sfx, call = [], [], [], []
def fx(name, t, vol, dur=None): sfx.append((name, round(max(0.0, t), 3), vol, dur))
def add(html_, cls_id, t0, t1, track):
    el.append(f'<div class="clip {cls_id[0]}" id="{cls_id[1]}" data-start="{t0:.3f}" data-duration="{t1 - t0:.3f}" data-track-index="{track}">{html_}</div>')
POP = lambda sel, t, d=0.22: js.append(f'tl.fromTo("{sel}", {{opacity: 0, scale: 0.6}}, {{opacity: 1, scale: 1, duration: {d}, ease: "back.out(2.2)"}}, {t:.3f});')
OUTF = lambda sel, t: js.append(f'tl.to("{sel}", {{opacity: 0, scale: 0.92, duration: 0.12, ease: "power2.in"}}, {t - 0.12:.3f});')
E = lambda e: f'<span class="emo">{e}</span>'

# ---------------- camera ----------------
for k, c0 in enumerate(CUTS):
    c1 = CUTS[k + 1] if k + 1 < len(CUTS) else DUR
    d, mv, ir = c1 - c0, MOVES[k], "true" if k == 0 else "false"
    a, b = {"push": ("scale: 1, rotation: 0, xPercent: 0", "scale: 1.08, rotation: 0, xPercent: 0"),
            "pull": ("scale: 1.1, rotation: 0, xPercent: 0", "scale: 1.0, rotation: 0, xPercent: 0"),
            "rot": ("scale: 1.07, rotation: -1.6, xPercent: 0", "scale: 1.1, rotation: 1.2, xPercent: 0"),
            "rotr": ("scale: 1.07, rotation: 1.6, xPercent: 0", "scale: 1.1, rotation: -1.2, xPercent: 0"),
            "pan": ("scale: 1.09, rotation: 0, xPercent: -2.2", "scale: 1.09, rotation: 0, xPercent: 2.2")}[mv]
    js.append(f'tl.fromTo("#cam", {{{a}}}, {{{b}, duration: {d:.3f}, ease: "sine.inOut", immediateRender: {ir}}}, {c0:.3f});')

# ---------------- punch-ins on every highlighted keyword ----------------
PUNCH = [T["north"], T["k30"], T["own"], T["five"], T["storm"], T["insurance"], T["underpay"], T["deny"], T["pine"], T["dozens"],
         T["fully"], T["ins2"], T["ins3"], T["free"], T["storm2"], T["learn"], T["free2"]]
for n, t in enumerate(PUNCH):
    js.append(f'tl.fromTo("#punch", {{scale: 1}}, {{scale: 1.15, duration: 0.133, ease: "power2.out", immediateRender: false}}, {t:.3f});')
    js.append(f'tl.to("#punch", {{scale: 1, duration: 0.45, ease: "power2.inOut"}}, {t + 0.133:.3f});')
    fx("wA" if n % 2 else "wB", t - 0.07, 0.16)
def shake(t, amp=14, n=6):
    for k in range(n):
        s = amp * (1 - k / n) * (1 if k % 2 == 0 else -1)
        js.append(f'tl.to("#shake", {{x: {s:.1f}, y: {-s * 0.6:.1f}, duration: 0.033, ease: "none"}}, {t + k * 0.033:.3f});')
    js.append(f'tl.to("#shake", {{x: 0, y: 0, duration: 0.05}}, {t + n * 0.033:.3f});')

# ---------------- grade + dim/blur while big graphics are up ----------------
G = {"base": "contrast(1.08) saturate(1.08) sepia(0.06) brightness(1.02)",
     "dark": "contrast(1.14) saturate(0.55) brightness(0.8)",
     "warm": "contrast(1.08) saturate(1.18) sepia(0.14) brightness(1.1)"}
js.append(f'tl.set("#grade", {{filter: "{G["base"]}"}}, 0);')
js.append(f'tl.set("#grade", {{filter: "{G["dark"]}"}}, {T["but"]:.3f});')
js.append(f'tl.set("#grade", {{filter: "{G["warm"]}"}}, {T["that"]:.3f});')
DIM = [(0.0, 1.933), (T["k30"] - 0.05, 6.2), (T["if_"], 12.1), (12.1, T["but"]), (T["but"], T["that"]), (T["that"], 22.62),
       (T["dozens"] - 0.1, T["guide"] - 0.05), (T["guide"], T["get"] - 0.1), (T["limited"], T["free"]), (T["free"], T["check"]), (T["just"], DUR)]
ON, OFF = "blur(6px) brightness(0.68)", "blur(0px) brightness(1)"
js.append(f'tl.set("#soft", {{filter: "{ON}"}}, 0);')
merged = []
for a, b in DIM:
    if merged and a - merged[-1][1] < 0.15: merged[-1] = (merged[-1][0], b)
    else: merged.append((a, b))
for k, (a, b) in enumerate(merged):
    if k: js.append(f'tl.to("#soft", {{filter: "{ON}", duration: 0.18}}, {a:.3f});')
    if b < DUR - 0.05: js.append(f'tl.to("#soft", {{filter: "{OFF}", duration: 0.18}}, {b:.3f});')

# ---------------- freeze frames (0.5 s holds, the edit underneath keeps its timing) ----------------
for k, (t, img) in enumerate(((T["that"], "assets/freeze-that.jpg"), (21.12, "assets/freeze-21.12.jpg"))):
    el.append(f'<img class="clip freeze" id="fz{k}" src="{img}" alt="" data-start="{t:.3f}" data-duration="0.5" data-track-index="{4 + k}" />')
    # (placed inside #grade below by the template string)
FREEZE = el[-2:]; del el[-2:]
def flash(t):
    js.append(f'tl.set("#flash", {{opacity: 1}}, {t:.3f});'); js.append(f'tl.set("#flash", {{opacity: 0}}, {t + 0.067:.3f});')

# ---------------- inspector callouts (footage coordinates, 1080x1920) ----------------
def callout(cid, t0, t1, spots):
    """spots: (kind, x, y, label, label_side) ; kind circle|arrow"""
    svg, labels = [], []
    for j, (kind, x, y, lab, side) in enumerate(spots):
        if kind == "circle":
            svg.append(f'<circle id="{cid}c{j}" cx="{x}" cy="{y}" r="92" fill="none" stroke="#e3121e" stroke-width="10" stroke-linecap="round" '
                       f'stroke-dasharray="580" stroke-dashoffset="580" transform="rotate(-80 {x} {y})"/>')
            js.append(f'tl.to("#{cid}c{j}", {{strokeDashoffset: 0, duration: 0.35, ease: "power2.out"}}, {t0 + j * 0.45:.3f});')
            ly = y - 170
        else:   # arrow pointing down-left at (x, y)
            svg.append(f'<g id="{cid}a{j}" opacity="0"><line x1="{x + 150}" y1="{y - 150}" x2="{x + 22}" y2="{y - 22}" stroke="#ffd60a" stroke-width="12" stroke-linecap="round"/>'
                       f'<polygon points="{x},{y} {x + 52},{y - 12} {x + 12},{y - 52}" fill="#ffd60a"/></g>')
            js.append(f'tl.fromTo("#{cid}a{j}", {{opacity: 0, x: 40, y: -40}}, {{opacity: 1, x: 0, y: 0, duration: 0.2, ease: "power3.out"}}, {t0 + j * 0.45:.3f});')
            ly = y - 230
        lx = x - 40 if side == "l" else x + 40
        anchor = "right" if side == "l" else "left"
        labels.append(f'<div class="clabel" id="{cid}l{j}" style="top:{ly}px; {anchor}:{1080 - lx if side == "l" else lx}px">{html.escape(lab)}</div>')
        POP(f"#{cid}l{j}", t0 + j * 0.45 + 0.15, 0.2)
        fx("pop", t0 + j * 0.45 + 0.15, 0.22)
    call.append(f'<div class="clip callout" id="{cid}" data-start="{t0:.3f}" data-duration="{t1 - t0:.3f}" data-track-index="{6 + len(call)}">'
                f'<svg viewBox="0 0 1080 1920" width="1080" height="1920">{"".join(svg)}</svg>{"".join(labels)}</div>')
callout("cc", T["get"] - 0.05, T["limited"] - 0.05, [("circle", 760, 1260, "HAIL DAMAGE?", "l"), ("arrow", 260, 1500, "WORN SHINGLES?", "r")])
callout("cd", T["check"] + 0.05, T["just"] - 0.05, [("circle", 840, 900, "STORM DAMAGE?", "l"), ("arrow", 200, 1150, "WORN SHINGLES?", "r")])

# ---------------- 1. hook (frame 1) ----------------
add('<div class="hook" id="hk"><i class="haz"></i><div class="hk1">EAST TEXAS</div><div class="hk2">HOMEOWNERS ' + E("🚨") + '</div><i class="uline" id="hkline"></i><i class="haz"></i></div>',
    ("stage", "s-hook"), 0.0, 1.95, 20)
js.append('tl.set("#hk", {opacity: 1, scale: 1}, 0);')                       # already on screen at frame 1
js.append('tl.fromTo("#hk .emo", {rotation: -14}, {rotation: 14, duration: 0.12, yoyo: true, repeat: 7, ease: "sine.inOut"}, 0.0);')
js.append(f'tl.fromTo("#hkline", {{scaleX: 0}}, {{scaleX: 1, duration: 0.25, ease: "power3.out"}}, {T["watch"] - 0.75:.3f});')
js.append(f'tl.fromTo("#hk", {{scale: 1}}, {{scale: 1.06, duration: 0.12, yoyo: true, repeat: 1}}, {T["watch"]:.3f});')
OUTF("#hk", 1.95)
fx("boom", 0.0, 0.5); shake(0.0, 10, 5)
fx("wB", 1.93 - 0.08, 0.2)
# kinetic: BEFORE YOU SPEND
add('<div class="kin"><span id="kb0">BEFORE</span> <span id="kb1">YOU</span> <span id="kb2">SPEND</span></div>', ("stage", "s-before"), T["before"], T["k30"], 20)
for j, t in enumerate((T["before"], T["you1"], T["spend"])):
    js.append(f'tl.fromTo("#kb{j}", {{opacity: 0, scale: 1.8, y: 40}}, {{opacity: 1, scale: 1, y: 0, duration: 0.14, ease: "power4.out"}}, {t:.3f});')
    fx("wA", t - 0.05, 0.14)
# $30,000 slam + OUT OF YOUR POCKET?
add('<div class="money"><div class="m30" id="m30">$30,000</div><div class="oop" id="oop">OUT OF YOUR POCKET?</div></div>', ("stage", "s-money"), T["k30"], 6.2, 21)
js.append(f'tl.fromTo("#m30", {{opacity: 0, scale: 3.2}}, {{opacity: 1, scale: 1, duration: 0.16, ease: "power4.in"}}, {T["k30"] - 0.12:.3f});')
shake(T["k30"] + 0.04, 22, 8); fx("kaching", T["k30"], 0.45); fx("boom", T["k30"] + 0.02, 0.3)
POP("#oop", T["own"]); fx("coindrop", T["own"], 0.45)
OUTF("#s-money .money", 6.2)

# ---------------- 2. qualify ----------------
CK = [("ROOF 5-10 YEARS OLD", T["five"], T["old"]), ("RECENT STORM", T["recently"], T["storm"])]
rows = "".join(f'<div class="ck" id="ck{j}"><span class="box" id="bx{j}"><b id="tk{j}">✓</b></span>{html.escape(t)}</div>' for j, (t, _, _) in enumerate(CK))
add(f'<div class="check"><div class="ckh" id="ckh">DOES THIS SOUND LIKE YOU?</div>{rows}<div class="foryou" id="foryou">THIS IS FOR YOU {E("👇")}</div></div>',
    ("stage", "s-check"), T["if_"], 12.1, 22)
POP("#ckh", T["if_"]); fx("wB", T["if_"] - 0.06, 0.18)
for j, (_, ta, tb) in enumerate(CK):
    js.append(f'tl.fromTo("#ck{j}", {{opacity: 0, x: -80}}, {{opacity: 1, x: 0, duration: 0.2, ease: "back.out(2)"}}, {ta:.3f});')
    fx("wA", ta - 0.05, 0.16)
    js.append(f'tl.fromTo("#tk{j}", {{opacity: 0, scale: 2.4}}, {{opacity: 1, scale: 1, duration: 0.16, ease: "back.out(3)"}}, {tb:.3f});')
    js.append(f'tl.to("#bx{j}", {{backgroundColor: "#16a34a", borderColor: "#16a34a", duration: 0.1}}, {tb:.3f});')
    fx("tick", tb, 0.4)
fx("thunder", T["recently"], 0.3)
POP("#foryou", T["insurance"] - 0.12); fx("pop", T["insurance"] - 0.12, 0.3)
OUTF("#s-check .check", 12.1)
# kinetic: OWES YOU A PROPER REPLACEMENT
add('<div class="kin big2"><div><span id="ko0">OWES</span> <span id="ko1">YOU</span> <span id="ko2">A</span></div>'
    '<div><span id="ko3" class="y">PROPER</span></div><div><span id="ko4" class="y">REPLACEMENT</span></div></div>', ("stage", "s-owes"), 12.1, T["but"], 20)
for j, t in enumerate((T["owes"], at("you a"), at("a proper"), T["proper"], T["replacement"])):
    js.append(f'tl.fromTo("#ko{j}", {{opacity: 0, x: {-120 if j % 2 else 120}, scale: 1.3}}, {{opacity: 1, x: 0, scale: 1, duration: 0.14, ease: "power4.out"}}, {max(12.1, t):.3f});')
fx("wB", 12.1 - 0.05, 0.16); fx("pop", T["replacement"], 0.25)

# ---------------- 3. problem: split screen + stamps ----------------
form = ('<div class="form" id="form"><div class="fh">INSURANCE CLAIM</div><div class="fsub">Claim #TX-0000 · Roof / Storm</div>'
        '<div class="fr"><span>Damage</span><b>Hail &amp; wind</b></div><div class="fr"><span>Roof age</span><b>5-10 yrs</b></div>'
        '<div class="fr"><span>Adjuster</span><b>Pending</b></div><div class="fr"><span>Payout</span><b>???</b></div>'
        '<div class="stamp s1" id="st1" data-layout-allow-overlap data-layout-allow-overflow>UNDERPAID</div><div class="stamp s2" id="st2" data-layout-allow-overlap>DENIED</div></div>')
add(f'<div class="split"><div class="sl" id="sl"><span>YOUR ROOF</span></div>{form}<div class="adj" id="adj">MOST ADJUSTERS…</div></div>',
    ("full", "s-split"), T["but"], T["that"], 22)
js.append(f'tl.fromTo("#form", {{xPercent: 110}}, {{xPercent: 0, duration: 0.25, ease: "power3.out"}}, {T["but"]:.3f});')
POP("#sl span", T["but"] + 0.15); POP("#adj", at("most adjusters")); fx("whip", T["but"] - 0.6, 0.3)
for sel, t, heavy in (("#st1", T["underpay"], False), ("#st2", T["deny"], True)):
    js.append(f'tl.fromTo("{sel}", {{opacity: 0, scale: {3.0 if heavy else 2.4}}}, {{opacity: 1, scale: 1, duration: {0.11 if heavy else 0.13}, ease: "power4.in"}}, {t - 0.08:.3f});')
    fx("stamp_heavy" if heavy else "stamp", t + 0.02, 0.42 if heavy else 0.42)
fx("buzzer", T["deny"] + 0.08, 0.32); shake(T["deny"] + 0.03, 16, 7)

# ---------------- 4. the turn ----------------
fx("riser", T["that"] - 1.6, 0.4)
flash(T["that"]); fx("drop", T["that"], 0.5)
add(f'<div class="gotyou" id="gy">{E("✅")} WE\'VE GOT YOU</div>', ("stage", "s-gotyou"), T["that"], T["pine"], 23)
POP("#gy", T["that"] + 0.05, 0.26); OUTF("#gy", T["pine"])
add('<div class="kin small"><span id="kw0">THAT\'S</span> <span id="kw1">WHERE</span> <span id="kw2" class="y">WE COME IN</span></div>', ("stage2", "s-where"),
    at("exactly where"), T["pine"], 24)
for j, t in enumerate((at("exactly where"), at("where we"), at("we come"))):
    js.append(f'tl.fromTo("#kw{j}", {{opacity: 0, y: 50}}, {{opacity: 1, y: 0, duration: 0.14, ease: "power4.out"}}, {t:.3f});')
# brand
B1 = T["weve"] - 0.08
add('<div class="brandin" id="brandin"><div class="b1">PINECREST</div><div class="b2">ROOFING &amp; CONSTRUCTION</div><i id="sweep" data-layout-allow-overflow></i></div>',
    ("stage", "s-brand"), T["pine"], B1, 23)
js.append(f'tl.fromTo("#brandin", {{opacity: 0, scale: 1.35}}, {{opacity: 1, scale: 1, duration: 0.22, ease: "back.out(2)"}}, {T["pine"]:.3f});')
js.append(f'tl.fromTo("#sweep", {{xPercent: -150}}, {{xPercent: 460, duration: 0.9, ease: "power2.inOut"}}, {T["pine"] + 0.3:.3f});')
OUTF("#brandin", B1)
fx("swoosh", T["pine"] - 0.12, 0.4); fx("pop", T["pine"] + 0.06, 0.4); flash(21.12)

# ---------------- 5. proof ----------------
NH = 24   # "dozens" = at least two dozen
houses = "".join(f'<span class="hs" id="hs{j}">🏠</span>' for j in range(12))
add(f'<div class="proof"><div class="cnt"><b id="cnum">0</b><span>+</span></div><div class="cl">LOCAL HOMEOWNERS HELPED</div>'
    f'<div class="houses">{houses}</div><div class="approved" id="appr">FULLY APPROVED {E("✅")}</div></div>', ("stage", "s-proof"), T["dozens"] - 0.1, T["guide"] - 0.08, 22)
POP("#s-proof .cnt", T["dozens"] - 0.1); POP("#s-proof .cl", T["dozens"]); fx("wB", T["dozens"] - 0.15, 0.18)
c0, c1 = T["dozens"], T["fully"] - 0.15
js.append(f'tl.fromTo("#cnum", {{textContent: 0}}, {{textContent: {NH}, duration: {c1 - c0:.3f}, ease: "power1.out", snap: {{textContent: 1}}}}, {c0:.3f});')
for j in range(12):
    t = c0 + (c1 - c0) * (j + 1) / 12
    js.append(f'tl.to("#hs{j}", {{opacity: 1, filter: "grayscale(0)", scale: 1.25, duration: 0.06}}, {t:.3f});')
    js.append(f'tl.to("#hs{j}", {{scale: 1, duration: 0.1}}, {t + 0.06:.3f});')
    if j % 2 == 0: fx("count", t, 0.25)
js.append(f'tl.fromTo("#appr", {{opacity: 0, scale: 2.2}}, {{opacity: 1, scale: 1, duration: 0.16, ease: "power4.in"}}, {T["fully"] - 0.08:.3f});')
fx("ding", T["fully"], 0.4); OUTF("#s-proof .proof", T["guide"] - 0.08)
# 3-step tracker
STEPS = [("INSPECTION", T["guide"]), ("CLAIM", T["entire"]), ("APPROVAL", T["ins3"] + 0.25)]
steps = "".join(f'<div class="stp" id="sp{j}"><span class="dot" id="dt{j}">{j + 1}</span><b>{s}</b></div>' + ('<i class="bar"><i id="br{0}"></i></i>'.format(j) if j < 2 else "")
                for j, (s, _) in enumerate(STEPS))
add(f'<div class="track"><div class="th">WE HANDLE THE CLAIM</div><div class="steps">{steps}</div></div>', ("stage", "s-track"), T["guide"] - 0.05, T["get"] - 0.1, 22)
POP("#s-track .th", T["guide"] - 0.05); fx("wA", T["guide"] - 0.1, 0.18)
for j, (_, t) in enumerate(STEPS):
    js.append(f'tl.fromTo("#sp{j}", {{opacity: 0.25}}, {{opacity: 1, duration: 0.1}}, {t:.3f});')
    js.append(f'tl.fromTo("#dt{j}", {{scale: 0.6}}, {{scale: 1, backgroundColor: "#16a34a", borderColor: "#16a34a", duration: 0.2, ease: "back.out(3)"}}, {t:.3f});')
    if j < 2: js.append(f'tl.fromTo("#br{j}", {{scaleX: 0}}, {{scaleX: 1, duration: {STEPS[j + 1][1] - t:.3f}, ease: "none"}}, {t:.3f});')
    fx("click", t, 0.45)
OUTF("#s-track .track", T["get"] - 0.1)
add('<div class="kin small"><span id="ke0">GET</span> <span id="ke1">WHAT</span> <span id="ke2">YOU\'RE</span> <span id="ke3" class="y">ENTITLED TO</span></div>',
    ("stage", "s-entitled"), T["get"], T["limited"], 20)
for j, t in enumerate((T["get"], at("what you're"), at("you're entitled"), T["entitled"])):
    js.append(f'tl.fromTo("#ke{j}", {{opacity: 0, scale: 1.6}}, {{opacity: 1, scale: 1, duration: 0.13, ease: "power4.out"}}, {t:.3f});')

# ---------------- 6. offer ----------------
add(f'<div class="limited" id="lim">{E("⏳")} LIMITED TIME</div>', ("stage", "s-limited"), T["limited"], T["free"] - 0.05, 23)
POP("#lim", T["limited"]); fx("clock", T["limited"], 0.4); fx("wB", T["limited"] - 0.08, 0.18)
js.append(f'tl.fromTo("#lim", {{scale: 1}}, {{scale: 1.05, duration: 0.25, yoyo: true, repeat: 3, ease: "sine.inOut", immediateRender: false}}, {T["limited"] + 0.4:.3f});')
OUTF("#lim", T["free"] - 0.05)
add('<div class="offer"><div class="o1" id="o1">FREE</div><div class="o2" id="o2">ROOF INSPECTION</div><div class="o3" id="o3">$0 • NO OBLIGATION</div></div>',
    ("stage", "s-offer"), T["free"], T["check"], 23)
js.append(f'tl.fromTo("#o1", {{opacity: 0, scale: 2.6}}, {{opacity: 1, scale: 1, duration: 0.15, ease: "power4.in"}}, {T["free"] - 0.08:.3f});')
POP("#o2", T["free"] + 0.18); POP("#o3", at("no-obligation") + 0.1)
fx("pop", T["free"], 0.45); fx("pop", at("no-obligation") + 0.1, 0.35); OUTF("#s-offer .offer", T["check"])
add(f'<div class="chip" id="chip">{E("👇")} TAP LEARN MORE</div>', ("chipz", "s-chip"), at("we're also"), T["just"], 26)
POP("#chip", at("we're also")); fx("tap", at("we're also"), 0.3)

# ---------------- 7. call to action ----------------
fx("riser", T["just"] - 1.6, 0.38)
PH0, PH1 = T["just"], T["book"] - 0.05
add('<div class="phone" id="phone"><div class="pscr"><div class="ptop">Pinecrest Roofing</div><div class="ptitle">Free Roof Inspection</div>'
    '<div class="pf"><label>Name</label><div class="pin"><span id="ty0"></span></div></div>'
    '<div class="pf"><label>Address</label><div class="pin"><span id="ty1"></span></div></div>'
    '<div class="pf"><label>Phone</label><div class="pin"><span id="ty2"></span></div></div>'
    '<div class="psub" id="psub">SUBMIT</div><div class="pok" id="pok">✓ Request sent</div></div><i class="finger" id="fing"></i></div>',
    ("stage", "s-phone"), PH0, PH1, 23)
js.append(f'tl.fromTo("#phone", {{opacity: 0, y: 260, rotation: 6}}, {{opacity: 1, y: 0, rotation: 0, duration: 0.3, ease: "power3.out"}}, {PH0:.3f});')
fx("whip", PH0 - 0.8, 0.28)
TY = [("Your name", PH0 + 0.35), ("Your address", PH0 + 0.7), ("(555) 000-0000", PH0 + 1.05)]
for j, (txt, t) in enumerate(TY):
    js.append(f'tl.fromTo("#fing", {{opacity: 1, y: {j * 92 - 20}, scale: 1.2}}, {{y: {j * 92}, scale: 0.9, duration: 0.08}}, {t - 0.05:.3f});')
    js.append(f'tl.to("#fing", {{scale: 1.1, duration: 0.08}}, {t + 0.04:.3f});')
    fx("tap", t, 0.35)
    for c in range(1, len(txt) + 1):
        js.append(f'tl.set("#ty{j}", {{textContent: {json.dumps(txt[:c])}}}, {t + c * 0.022:.3f});')
TS = PH0 + 1.42
js.append(f'tl.to("#fing", {{y: 300, scale: 0.9, duration: 0.1}}, {TS - 0.12:.3f});')
js.append(f'tl.fromTo("#psub", {{scale: 1}}, {{scale: 0.92, duration: 0.06, yoyo: true, repeat: 1}}, {TS:.3f});')
fx("click", TS, 0.45)
POP("#pok", TS + 0.15); fx("notify", TS + 0.15, 0.38)
OUTF("#phone", PH1)
C0 = T["book"] - 0.05
add(f'<div class="cta"><div class="ctaname" id="ctn">PINECREST ROOFING &amp; CONSTRUCTION</div>'
    f'<div class="ctabtn" id="ctb">BOOK YOUR FREE INSPECTION {E("👇")}</div><svg class="arrow" id="arw" viewBox="0 0 120 150" width="120" height="150"><path d="M42 0h36v80h32L60 145 10 80h32z" fill="#ffd60a" stroke="#000" stroke-width="8" stroke-linejoin="round"/></svg></div>', ("stage", "s-cta"), C0, DUR, 25)
js.append(f'tl.fromTo("#ctn", {{opacity: 0, y: -24}}, {{opacity: 1, y: 0, duration: 0.2, ease: "power3.out"}}, {C0:.3f});')
POP("#ctb", C0 + 0.05, 0.24); fx("pop", C0 + 0.05, 0.4); fx("tap", T["free2"], 0.35); fx("notify", T["free2"] + 0.1, 0.3)
np_ = int((DUR - C0 - 0.35) / 0.44)
js.append(f'tl.fromTo("#ctb", {{scale: 1}}, {{scale: 1.07, duration: 0.22, ease: "sine.inOut", yoyo: true, repeat: {max(1, np_ * 2 - 1)}, immediateRender: false}}, {C0 + 0.35:.3f});')
POP("#arw", C0 + 0.2, 0.2)
js.append(f'tl.fromTo("#arw", {{y: 0}}, {{y: 36, duration: 0.3, ease: "power2.in", yoyo: true, repeat: {max(1, int((DUR - C0 - 0.45) / 0.3) - 1)}, immediateRender: false}}, {C0 + 0.42:.3f});')

# ---------------- captions ----------------
YEL = ["east texas homeowners", "$30,000", "5 to 10 years old", "storm", "insurance", "pine crest", "dozens of local homeowners",
       "fully approved", "free", "learn more"]
RED = ["your own money", "underpay", "deny"]
color = {}
for lst, c in ((YEL, "y"), (RED, "r")):
    for p in lst:
        st = 0
        while True:
            try: ix = find(p, st)
            except SystemExit: break
            for i in ix: color[i] = c
            st = ix[-1] + 1
ip = find("pine crest")[0]
OVERRIDE = {ip: "PINECREST", ip + 1: None}
def disp(i):
    if i in OVERRIDE: return OVERRIDE[i]
    return re.sub(r"[.,?!]+$", "", words[i]["text"]).upper()
KEEP = [find(p) for p in ("east texas", "your own money", "5 to 10", "years old", "a storm", "your insurance", "proper replacement",
                          "most adjusters", "to underpay", "deny you", "come in", "pine crest roofing", "dozens of", "local homeowners",
                          "fully approved", "their insurance", "insurance process", "entitled to", "limited time", "no-obligation roof",
                          "storm damage", "learn more", "free inspection")]
together = {i: tuple(g) for g in KEEP for i in g}
groups, cur = [], []
for i, w in enumerate(words):
    if cur:
        prev = words[cur[-1]]
        same = together.get(i) is not None and together.get(i) == together.get(cur[-1])
        brk = len([j for j in cur if disp(j)]) >= 3 or re.search(r"[.,?!]$", prev["text"]) or w["start"] - prev["end"] > 0.3
        if same and len(cur) < 4: brk = False
        if together.get(i) and together.get(i)[0] == i and len(cur) + len(together[i]) > 3: brk = True
        if brk: groups.append(cur); cur = []
    cur.append(i)
groups.append(cur)
merged = []
for g in groups:
    if merged and len([i for i in g if disp(i)]) <= 1 and len([i for i in merged[-1] if disp(i)]) <= 2 \
            and not re.search(r"[.?!]$", words[merged[-1][-1]]["text"]):
        merged[-1] = merged[-1] + g
    else: merged.append(g)
groups, k = [], 0
while k < len(merged):
    g = merged[k]
    if k + 1 < len(merged) and len([i for i in g if disp(i)]) == 1 and len(" ".join(disp(i) for i in g + merged[k + 1] if disp(i))) <= 14:
        groups.append(g + merged[k + 1]); k += 2
    else: groups.append(g); k += 1
GAP_EM = 0.3
def units(t):
    return sum(0.3 if c == " " else 0.32 if c in ".,'-?!" else 1.0 if c in "MW" else 0.42 if c in "I1" else 0.62 if c in "$0123456789" else 0.8 for c in t)
cap = []
for gi, g in enumerate(groups if SHOW_CAPTIONS else []):
    vis = [i for i in g if disp(i)]
    s0 = words[g[0]]["start"]; nxt = words[groups[gi + 1][0]]["start"] if gi + 1 < len(groups) else DUR
    e0 = DUR if gi == len(groups) - 1 else min(nxt, words[g[-1]]["end"] + 0.4, DUR)
    ws = "".join(f'<span class="w" id="w{i}">{html.escape(disp(i))}</span>' for i in vis)
    em = sum(units(disp(i)) for i in vis) + GAP_EM * (len(vis) - 1)
    fs = int(min(80, (W - 140) / 1.14 / em)); wrap = ""
    if fs < 58 and len(vis) > 1:
        fs, wrap = int(min(70, (W - 140) / 1.14 / max(em / 2 + GAP_EM, max(units(disp(i)) for i in vis)))), "; flex-wrap: wrap"
    cap.append(f'<div class="cg" id="cg{gi}"><div class="line" style="font-size:{fs}px{wrap}">{ws}</div></div>')
    js.append(f'tl.fromTo("#cg{gi}", {{opacity: 0, scale: 0.85}}, {{opacity: 1, scale: 1, duration: 0.08, ease: "power2.out"}}, {s0:.3f});')
    for i in vis:
        col = {"y": "#ffd60a", "r": "#ff3b30"}.get(color.get(i), "#ffffff")
        js.append(f'tl.fromTo("#w{i}", {{opacity: 0.55, scale: 1, color: "#ffffff"}}, {{opacity: 1, scale: 1.12, color: "{col}", duration: 0.07}}, {words[i]["start"]:.3f});')
        js.append(f'tl.to("#w{i}", {{scale: 1, duration: 0.1}}, {max(words[i]["start"] + 0.07, words[i]["end"]):.3f});')
    js.append(f'tl.set("#cg{gi}", {{opacity: 0, visibility: "hidden"}}, {e0:.3f});')

# ---------------- audio ----------------
aud = []
for n, (k, t, v, d) in enumerate(sorted(sfx, key=lambda x: x[1])):
    f = f"assets/sfx/{k}.wav"
    aud.append(f'<audio id="fx{n}" src="{f}" data-start="{t:.3f}" data-duration="{min(d or probe(f), DUR - t):.3f}" data-track-index="{40 + n}" data-volume="{v}"></audio>')

STAGE_CSS = f"top: {L['stage']}px; height: {STAGE_H}px;"
CSS = f"""
      @font-face {{ font-family: "Montserrat"; font-weight: 900; src: url("vendor/montserrat-latin-900-normal.woff2") format("woff2"); }}
      @font-face {{ font-family: "Montserrat"; font-weight: 800; src: url("vendor/montserrat-latin-800-normal.woff2") format("woff2"); }}
      @font-face {{ font-family: "Noto Color Emoji"; src: url("vendor/NotoColorEmoji.ttf") format("truetype"); }}
      body {{ margin: 0; background: #000; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; background: #000; color: #fff;
              font-family: "Montserrat", "Noto Color Emoji", sans-serif; font-weight: 900; }}
      .emo {{ font-family: "Noto Color Emoji", sans-serif; display: inline-block; }}
      .y {{ color: #ffd60a; }}

      #cam, #punch, #shake, #soft {{ position: absolute; inset: 0; transform-origin: 50% 50%; }}
      #grade, #callwrap {{ position: absolute; left: 0; top: {VID_Y}px; width: 1080px; height: 1920px; }}
      #src, .freeze {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; }}
      #vignette {{ position: absolute; inset: 0; pointer-events: none; background: radial-gradient(ellipse 85% 70% at 50% 46%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.38) 100%); }}
      #flash {{ position: absolute; inset: 0; background: #fff; opacity: 0; pointer-events: none; }}

      /* inspector callouts */
      .callout {{ position: absolute; inset: 0; }}
      .callout svg {{ position: absolute; inset: 0; }}
      .clabel {{ position: absolute; padding: 10px 20px 8px; border-radius: 12px; background: #e3121e; font-size: 40px; white-space: nowrap;
                box-shadow: 0 8px 22px rgba(0,0,0,0.5); opacity: 0; }}

      /* stage: every big designed moment lives here (above the captions) */
      .stage {{ position: absolute; left: 60px; right: 60px; {STAGE_CSS} display: flex; align-items: center; justify-content: center; }}
      .stage2 {{ position: absolute; left: 60px; right: 60px; top: {L['stage']}px; height: 200px; display: flex; align-items: center; justify-content: center; }}
      .chipz {{ position: absolute; left: 0; right: 0; top: {L['chip']}px; height: 70px; display: flex; align-items: center; justify-content: center; }}
      .full {{ position: absolute; inset: 0; }}
      .hook {{ position: relative; text-align: center; line-height: 0.95; }}
      .haz {{ display: block; height: 34px; margin: 26px auto; width: 92%; border-radius: 6px; background: repeating-linear-gradient(-45deg, #ffd60a 0 34px, #111 34px 68px); }}
      .hk1 {{ white-space: nowrap; font-size: 132px; color: #ffd60a; -webkit-text-stroke: 14px #000; paint-order: stroke fill; text-shadow: 0 10px 0 #000; }}
      .hk2 {{ white-space: nowrap; font-size: 96px; color: #ffd60a; -webkit-text-stroke: 12px #000; paint-order: stroke fill; text-shadow: 0 9px 0 #000; }}
      .uline {{ display: block; height: 16px; margin: 18px auto 0; width: 80%; background: #e3121e; border-radius: 8px; transform-origin: 0 50%; }}
      .kin {{ text-align: center; font-size: 120px; line-height: 1.02; -webkit-text-stroke: 12px #000; paint-order: stroke fill; text-shadow: 0 9px 0 #000; }}
      .kin span {{ display: inline-block; }}
      .kin.big2 {{ font-size: 112px; }}
      .kin.small {{ font-size: 76px; -webkit-text-stroke: 10px #000; }}
      .money {{ text-align: center; }}
      .m30 {{ font-size: 230px; line-height: 1; color: #ffd60a; -webkit-text-stroke: 16px #000; paint-order: stroke fill; text-shadow: 0 14px 0 #000, 0 0 60px rgba(255,214,10,0.45); }}
      .oop {{ display: inline-block; margin-top: 26px; padding: 18px 34px 14px; border-radius: 18px; background: #e3121e; font-size: 66px; white-space: nowrap;
             box-shadow: 0 12px 30px rgba(0,0,0,0.5); }}
      .check {{ width: 100%; }}
      .ckh {{ text-align: center; font-size: 56px; margin-bottom: 34px; -webkit-text-stroke: 9px #000; paint-order: stroke fill; }}
      .ck {{ display: flex; align-items: center; margin: 0 0 26px; padding: 26px 30px; border-radius: 22px; background: rgba(255,255,255,0.96); color: #111; font-size: 60px;
            box-shadow: 0 12px 30px rgba(0,0,0,0.45); opacity: 0; }}
      .box {{ flex: none; display: inline-flex; align-items: center; justify-content: center; width: 78px; height: 78px; margin-right: 26px; border-radius: 16px;
             border: 6px solid #111; color: #fff; font-size: 60px; }}
      .box b {{ display: inline-block; opacity: 0; }}
      .foryou {{ margin-top: 30px; text-align: center; font-size: 84px; color: #ffd60a; -webkit-text-stroke: 11px #000; paint-order: stroke fill; text-shadow: 0 8px 0 #000; opacity: 0; }}
      .split .sl {{ position: absolute; left: 0; top: 0; bottom: 0; width: 46%; }}
      .split .sl span {{ position: absolute; left: 40px; top: {L['stage'] + 20}px; padding: 10px 18px 8px; border-radius: 10px; background: rgba(0,0,0,0.75); font-size: 36px; opacity: 0; }}
      .form {{ position: absolute; right: 0; top: 0; bottom: 0; width: 54%; background: #f6f5f1; color: #1f2937; box-shadow: -18px 0 40px rgba(0,0,0,0.5);
              padding: {L['stage'] + 30}px 40px 0; box-sizing: border-box; font-weight: 800; }}
      .fh {{ font-size: 54px; font-weight: 900; color: #0f2a44; border-bottom: 6px solid #0f2a44; padding-bottom: 14px; }}
      .fsub {{ margin: 14px 0 24px; font-size: 28px; color: #6b7280; }}
      .fr {{ display: flex; justify-content: space-between; padding: 22px 0; border-bottom: 3px dashed #cbd5e1; font-size: 34px; }}
      .fr span {{ color: #6b7280; }}
      .stamp {{ position: absolute; left: 24px; right: 24px; text-align: center; color: #e3121e; border: 12px solid #e3121e; border-radius: 18px; opacity: 0;
               mix-blend-mode: multiply; }}
      .s1 {{ top: {L['stage'] + 330}px; font-size: 60px; padding: 10px 0 4px; transform: rotate(-10deg); }}
      .s2 {{ top: {L['stage'] + 520}px; font-size: 120px; padding: 10px 0 4px; border-width: 16px; transform: rotate(8deg); }}
      .adj {{ position: absolute; left: 30px; width: 40%; top: {L['stage'] + 520}px; font-size: 64px; line-height: 1.05; -webkit-text-stroke: 9px #000; paint-order: stroke fill; opacity: 0; }}
      .gotyou {{ padding: 30px 46px 24px; border-radius: 28px; background: #16a34a; font-size: 92px; white-space: nowrap; box-shadow: 0 16px 40px rgba(0,0,0,0.5); }}
      .brandin {{ position: relative; overflow: hidden; padding: 30px 44px 34px; border-radius: 26px; background: rgba(10,10,10,0.7); border: 4px solid #ffd60a; text-align: center; }}
      .b1 {{ font-size: 136px; letter-spacing: 4px; line-height: 1; }}
      .b2 {{ margin-top: 14px; font-size: 50px; letter-spacing: 2px; color: #ffd60a; }}
      #sweep {{ position: absolute; top: -30%; bottom: -30%; left: 0; width: 26%; transform: skewX(-18deg);
               background: linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,250,230,0.85) 50%, rgba(255,255,255,0) 100%); }}
      .proof {{ text-align: center; }}
      .cnt {{ font-size: 200px; line-height: 1; color: #ffd60a; -webkit-text-stroke: 14px #000; paint-order: stroke fill; text-shadow: 0 12px 0 #000; }}
      .cl {{ font-size: 56px; margin-top: 6px; -webkit-text-stroke: 9px #000; paint-order: stroke fill; }}
      .houses {{ display: grid; grid-template-columns: repeat(6, 1fr); gap: 6px 10px; width: 760px; margin: 22px auto 0; }}
      .hs {{ display: inline-block; font-size: 72px; line-height: 1; opacity: 0.35; filter: grayscale(1); font-family: "Noto Color Emoji", sans-serif; }}
      .approved {{ display: inline-block; margin-top: 26px; padding: 22px 40px 18px; border-radius: 22px; background: #16a34a; font-size: 82px; white-space: nowrap; opacity: 0;
                  box-shadow: 0 14px 36px rgba(0,0,0,0.5); }}
      .track {{ width: 100%; text-align: center; }}
      .th {{ font-size: 66px; margin-bottom: 50px; -webkit-text-stroke: 10px #000; paint-order: stroke fill; }}
      .steps {{ display: flex; align-items: flex-start; justify-content: center; }}
      .stp {{ display: flex; flex-direction: column; align-items: center; width: 250px; opacity: 0.25; }}
      .stp b {{ margin-top: 18px; font-size: 40px; -webkit-text-stroke: 7px #000; paint-order: stroke fill; }}
      .dot {{ display: flex; align-items: center; justify-content: center; width: 150px; height: 150px; border-radius: 50%; border: 8px solid #fff; background: rgba(0,0,0,0.6); font-size: 80px; }}
      .bar {{ position: relative; display: block; width: 90px; height: 16px; margin-top: 67px; border-radius: 8px; background: rgba(255,255,255,0.3); overflow: hidden; }}
      .bar i {{ position: absolute; inset: 0; background: #16a34a; transform-origin: 0 50%; }}
      .limited {{ padding: 28px 46px 22px; border-radius: 26px; background: #ffd60a; color: #111; font-size: 100px; white-space: nowrap; box-shadow: 0 16px 40px rgba(0,0,0,0.5); }}
      .offer {{ text-align: center; }}
      .o1 {{ font-size: 210px; line-height: 0.95; color: #16a34a; -webkit-text-stroke: 16px #fff; paint-order: stroke fill; text-shadow: 0 14px 0 rgba(0,0,0,0.6); }}
      .o2 {{ font-size: 88px; line-height: 1; -webkit-text-stroke: 12px #000; paint-order: stroke fill; text-shadow: 0 9px 0 #000; }}
      .o3 {{ display: inline-block; margin-top: 30px; padding: 16px 34px 12px; border-radius: 16px; background: #fff; color: #111; font-size: 56px; white-space: nowrap; }}
      .chip {{ padding: 14px 30px 10px; border-radius: 40px; background: #fff; color: #111; font-size: 40px; white-space: nowrap; box-shadow: 0 8px 22px rgba(0,0,0,0.5); }}
      .phone {{ position: relative; width: 380px; height: 680px; border-radius: 56px; background: #111; border: 10px solid #2b2b2b; box-shadow: 0 30px 60px rgba(0,0,0,0.6); }}
      .pscr {{ position: absolute; inset: 14px; border-radius: 42px; background: #fff; color: #111; padding: 40px 26px 0; box-sizing: border-box; font-weight: 800; }}
      .ptop {{ font-size: 28px; color: #6b7280; }}
      .ptitle {{ margin: 6px 0 20px; font-size: 36px; font-weight: 900; color: #0f2a44; }}
      .pf {{ margin-bottom: 18px; }}
      .pf label {{ display: block; font-size: 28px; color: #6b7280; margin-bottom: 6px; }}
      .pin {{ height: 56px; border-radius: 12px; border: 3px solid #cbd5e1; font-size: 28px; line-height: 50px; padding: 0 14px; color: #111; }}
      .psub {{ margin-top: 26px; height: 74px; border-radius: 16px; background: #e3121e; color: #fff; font-size: 32px; font-weight: 900; text-align: center; line-height: 74px; }}
      .pok {{ margin-top: 18px; text-align: center; font-size: 28px; color: #16a34a; opacity: 0; }}
      .finger {{ position: absolute; left: 230px; top: 230px; width: 66px; height: 66px; border-radius: 50%; background: rgba(255,214,10,0.55); border: 5px solid #ffd60a; opacity: 0; }}
      .cta {{ width: 100%; display: flex; flex-direction: column; align-items: center; }}
      .ctaname {{ margin-bottom: 26px; font-size: 46px; white-space: nowrap; -webkit-text-stroke: 9px #000; paint-order: stroke fill; }}
      .ctabtn {{ width: 100%; padding: 36px 20px 30px; border-radius: 32px; background: #e3121e; text-align: center; font-size: 50px; white-space: nowrap;
                box-shadow: 0 14px 0 #7a0000, 0 20px 50px rgba(227,18,30,0.55); box-sizing: border-box; }}
      .arrow {{ display: block; margin-top: 34px; overflow: visible; }}

      /* captions */
      #captions {{ position: absolute; left: 0; right: 0; top: {L.get('cap', 0)}px; height: 180px; }}
      .cg {{ position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; opacity: 0; }}
      .cg .line {{ display: flex; flex-wrap: nowrap; justify-content: center; align-items: center; gap: 0 0.3em; max-width: {W - 120}px; line-height: 1.08; }}
      .w {{ display: inline-block; color: #fff; -webkit-text-stroke: 0.17em #000; paint-order: stroke fill; text-shadow: 0 0.08em 0 #000, 0 0.1em 0.25em rgba(0,0,0,0.5);
           opacity: 0.55; white-space: nowrap; }}
"""
nl = "\n      "
CAPS = (f'<div id="captions" class="clip" data-start="0" data-duration="{DUR}" data-track-index="30">' + nl + "  " + (nl + "  ").join(cap) + nl + '</div>') if SHOW_CAPTIONS else ""
doc = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <title>Pinecrest Final Ad {"9x16" if FMT == "916" else "4x5"}</title>
    <script src="vendor/gsap.min.js"></script>
    <style>{CSS}    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="{W}" data-height="{H}" data-duration="{DUR}">
      <div id="cam"><div id="punch"><div id="shake">
        <div id="soft"><div id="grade">
          <video id="src" class="clip" src="assets/source.mp4" muted playsinline data-start="0" data-duration="{DUR}" data-track-index="0"></video>
          {nl.join(FREEZE)}
        </div></div>
        <div id="callwrap">
          {nl.join(call)}
        </div>
      </div></div></div>
      <div id="vignette"></div>
      {nl.join(el)}
      {CAPS}
      <div id="flash"></div>
    </div>
    <audio id="track" src="assets/track.wav" data-start="0" data-duration="{DUR}" data-track-index="1" data-volume="1"></audio>
    {chr(10).join("    " + a for a in aud).lstrip()}
    <script>
      const tl = gsap.timeline({{ paused: true }});
      {nl.join(js)}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
if OUT != ".":
    os.makedirs(OUT, exist_ok=True)
    for d in ("assets", "vendor"):
        if not os.path.lexists(f"{OUT}/{d}"): os.symlink(f"../eastad/{d}", f"{OUT}/{d}")
    for f in ("hyperframes.json", "package.json"): open(f"{OUT}/{f}", "w").write(open(f).read())
    json.dump({"id": "eastad-4x5", "name": "eastad-4x5"}, open(f"{OUT}/meta.json", "w"), indent=2)
    if not os.path.lexists(f"{OUT}/transcript.json"): os.symlink("../eastad/transcript.json", f"{OUT}/transcript.json")
open(f"{OUT}/index.html", "w").write(doc)
# retention check: something must change at least every 3 s
ev = sorted({*[t for _, t, _, _ in sfx], *CUTS, *PUNCH, *([words[g[0]]["start"] for g in groups] if SHOW_CAPTIONS else [])})
gaps = [(round(a, 2), round(b - a, 2)) for a, b in zip(ev, ev[1:] + [DUR]) if b - a > 3.0]
print(f"{FMT}: {W}x{H} · {DUR}s · {len(PUNCH)} punches · {len(groups)} captions · {len(sfx)} sfx · gaps>3s: {gaps or 'none'}")
