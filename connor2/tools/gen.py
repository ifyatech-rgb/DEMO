"""Connor full-length avatar ad (9:16) with the client's own b-roll cut in. The cut, b-roll placement and voice
are kept exactly; everything else is layered on top.

Picture: #hand (handheld drift / bob / micro-shake, avatar shots only) > #cam (110-125 % punch levels on the avatar,
push / pan on b-roll) > #whip (quick whip in/out of each b-roll) > #shake > video (+ the turn's freeze frame).
Zones (his face sits at y ~510-860): TOP y 280-455 above his head (pills, big numbers), BODY y 890-1115 across
his torso (cards, stamps, offer), CAPTIONS y 1125-1245, FULL screen only over b-roll.
"""
import html, json, math, os, random, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
W, H = 1080, 1920
probe = lambda f: float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f], capture_output=True, text=True).stdout)
DUR = round(probe("assets/source.mp4") - 0.04, 3)
words = json.load(open("transcript.json")); words = words if isinstance(words, list) else words["words"]
def clean(t): return re.sub(r"[.,?!]+$", "", t).lower()
def find(p, after=0):
    toks = p.lower().split()
    for i in range(after, len(words)):
        if [clean(w["text"]) for w in words[i:i + len(toks)]] == toks: return list(range(i, i + len(toks)))
    sys.exit(f"phrase not found: {p}")
def at(p, after=0): return words[find(p, after)[0]]["start"]
def end(p, after=0): return words[find(p, after)[-1]]["end"]

# the client's cuts (frame-diff spikes at 30 fps)
CUTS = [f / 30 for f in (45, 374, 497, 797, 902, 978, 1057, 1244, 1354)]
SEG = list(zip([0.0] + CUTS, CUTS + [DUR]))
KIND = ["broll", "avatar", "broll", "avatar", "broll", "broll", "broll", "avatar", "broll", "avatar"]
BR = [s for s, k in zip(SEG, KIND) if k == "broll"]
def is_broll(t): return any(a <= t < b for a, b in BR)

el, js, sfx = [], [], []
def fx(name, t, vol): sfx.append((name, round(max(0.0, t), 3), vol))
def add(inner, cls, gid, t0, t1, track=20):
    el.append(f'<div class="clip {cls}" id="{gid}" data-start="{t0:.3f}" data-duration="{t1 - t0:.3f}" data-track-index="{track}">{inner}</div>')
def POP(sel, t, d=0.22): js.append(f'tl.fromTo("{sel}", {{opacity: 0, scale: 0.6}}, {{opacity: 1, scale: 1, duration: {d}, ease: "back.out(2.2)"}}, {t:.3f});')
def OUT(sel, t): js.append(f'tl.to("{sel}", {{opacity: 0, scale: 0.92, duration: 0.12, ease: "power2.in"}}, {t - 0.12:.3f});')
def SLAM(sel, t, frm=2.6): js.append(f'tl.fromTo("{sel}", {{opacity: 0, scale: {frm}}}, {{opacity: 1, scale: 1, duration: 0.15, ease: "power4.in"}}, {t - 0.1:.3f});')
def WH(t, v=0.16): fx("wA" if len(sfx) % 2 else "wB", t - 0.08, v)
E = lambda e: f'<span class="emo">{e}</span>'
def flash(t): js.append(f'tl.set("#flash", {{opacity: 1}}, {t:.3f});'); js.append(f'tl.set("#flash", {{opacity: 0}}, {t + 0.067:.3f});')
def shake(t, amp=12, n=6):
    for k in range(n):
        s = amp * (1 - k / n) * (1 if k % 2 == 0 else -1)
        js.append(f'tl.to("#shake", {{x: {s:.1f}, y: {-s * 0.6:.1f}, duration: 0.033, ease: "none"}}, {t + k * 0.033:.3f});')
    js.append(f'tl.to("#shake", {{x: 0, y: 0, duration: 0.05}}, {t + n * 0.033:.3f});')
def pill(gid, txt, t0, t1, kind="pill", zone="top", sound="pop"):
    add(f'<div class="{kind}" id="{gid}i">{txt}</div>', zone, gid, t0, t1)
    POP(f"#{gid}i", t0); OUT(f"#{gid}i", t1)
    if sound: fx(sound, t0, 0.2)

# ======================= handheld (avatar only) =======================
rnd = random.Random(11)
ph = [rnd.uniform(0, 6.28) for _ in range(9)]
def hand(t):
    x = 10 * math.sin(2 * math.pi * 0.23 * t + ph[0]) + 5 * math.sin(2 * math.pi * 0.61 * t + ph[1]) + 2 * math.sin(2 * math.pi * 1.9 * t + ph[2])
    y = 8 * math.sin(2 * math.pi * 0.19 * t + ph[3]) + 3.2 * math.sin(2 * math.pi * 1.15 * t + ph[4]) + 1.6 * math.sin(2 * math.pi * 2.3 * t + ph[5])
    r = 0.42 * math.sin(2 * math.pi * 0.17 * t + ph[6]) + 0.2 * math.sin(2 * math.pi * 0.53 * t + ph[7]) + 0.05 * math.sin(2 * math.pi * 2.1 * t + ph[8])
    k = 0.15 if is_broll(t) else 1.0
    return x * k, y * k, r * k
STEP, t = 0.2, 0.0
x0, y0, r0 = hand(0); js.append(f'tl.set("#hand", {{x: {x0:.1f}, y: {y0:.1f}, rotation: {r0:.3f}}}, 0);')
while t < DUR:
    x, y, r = hand(t + STEP)
    js.append(f'tl.to("#hand", {{x: {x:.1f}, y: {y:.1f}, rotation: {r:.3f}, duration: {STEP}, ease: "none"}}, {t:.2f});'); t += STEP

# ======================= camera per segment =======================
EMPH = [at("thirty thousand"), at("denied"), at("risk window"), at("tightening"), at("exactly where"), at("north and east"), at("nine full"), at("free no-obligation"), at("learn more")]
PUNCH_T = []
for k, ((a, b), kind) in enumerate(zip(SEG, KIND)):
    if kind == "avatar":
        js.append(f'tl.set("#cam", {{scale: 1.12, xPercent: 0, yPercent: 0}}, {a:.3f});')
        lvl, t = 1.12, a
        for e in [e for e in EMPH if a < e < b]:
            js.append(f'tl.to("#cam", {{scale: 1.25, duration: 0.3, ease: "power2.out"}}, {e - 0.05:.3f});')
            js.append(f'tl.to("#cam", {{scale: 1.14, duration: 0.45, ease: "power2.inOut"}}, {min(e + 1.5, b - 0.5):.3f});')
            PUNCH_T.append(e)
    else:
        mv = ["push", "pan", "push", "panR", "push", "pan"][len([1 for s in SEG[:k] if s in BR]) % 6]
        a0, b0 = {"push": ("scale: 1.0, xPercent: 0", "scale: 1.1, xPercent: 0"), "pan": ("scale: 1.1, xPercent: 2.5", "scale: 1.1, xPercent: -2.5"),
                  "panR": ("scale: 1.1, xPercent: -2.5", "scale: 1.1, xPercent: 2.5")}[mv]
        js.append(f'tl.fromTo("#cam", {{{a0}, yPercent: 0}}, {{{b0}, duration: {b - a:.3f}, ease: "none", immediateRender: {"true" if a == 0 else "false"}}}, {a:.3f});')
    if a > 0:   # whip into every segment change + a whoosh
        js.append(f'tl.fromTo("#whip", {{yPercent: {7 if kind == "broll" else -7}}}, {{yPercent: 0, duration: 0.2, ease: "power3.out", immediateRender: false}}, {a:.3f});')
        fx("wB" if kind == "broll" else "wA", a - 0.1, 0.16)

# ======================= 1. hook + money =======================
add(f'<div class="hook" id="hk"><i class="haz"></i><div class="hk1">{E("📍")} TEXAS</div><div class="hk2">HOMEOWNERS {E("🚨")}</div><i class="haz"></i></div>', "full", "g-hook", 0.0, CUTS[0])
js.append('tl.set("#hk", {opacity: 1, scale: 1}, 0);')
js.append('tl.fromTo("#hk .emo", {rotation: -12}, {rotation: 12, duration: 0.12, yoyo: true, repeat: 5, ease: "sine.inOut"}, 0.0);')
fx("boom", 0.0, 0.5); shake(0.0, 10, 5); OUT("#hk", CUTS[0])
pill("g-tx", f'{E("📍")} TEXAS HOMEOWNERS', CUTS[0], at("before you") - 0.05, sound=None)
add('<div class="kin"><span id="kb0">BEFORE</span> <span id="kb1">YOU</span> <span id="kb2">SPEND…</span></div>', "top", "g-before", at("before you"), at("thirty thousand") - 0.1)
for j, t in enumerate((at("before you"), at("you spend"), at("spend"))):
    js.append(f'tl.fromTo("#kb{j}", {{opacity: 0, scale: 1.8, y: 30}}, {{opacity: 1, scale: 1, y: 0, duration: 0.14, ease: "power4.out"}}, {t:.3f});'); fx("pop", t, 0.12)
M0 = at("thirty thousand")
add('<div class="m30" id="m30">$30,000</div>', "top", "g-m30", M0, at("forty-seven") - 0.05)
SLAM("#m30", M0, 3.0); shake(M0 + 0.05, 18, 7); fx("kaching", M0, 0.42); fx("boom", M0, 0.25); OUT("#m30", at("forty-seven") - 0.05)
add('<div class="oop" id="oop">OUT OF YOUR POCKET?</div>', "body", "g-oop", at("on a new"), at("forty-seven") - 0.05)
POP("#oop", at("on a new")); fx("coindrop", at("on a new"), 0.4); OUT("#oop", at("forty-seven") - 0.05)

# ======================= 2. denied claims =======================
F0, F1 = at("forty-seven"), CUTS[1] - 0.02
pill("g-47", f'{E("📊")} <span class="r">47%</span> OF TEXAS ROOF CLAIMS…', F0, at("were denied") - 0.05)
pill("g-den", f'{E("❌")} DENIED. NOT PAID OUT.', at("were denied"), F1, "pill red", sound=None)
form = ('<div class="form" id="form"><div class="fh">INSURANCE CLAIM <span>Roof · Storm</span></div>'
        '<div class="frow"><span>Status</span><b id="fst">Under review…</b></div><div class="frow"><span>Payout</span><b>$ ———</b></div>'
        '<div class="stamp s1" id="st1" data-layout-allow-overlap>DENIED</div><div class="stamp s2" id="st2" data-layout-allow-overlap>NOT PAID</div></div>')
add(form, "body", "g-form", F0 + 0.3, F1)
js.append(f'tl.fromTo("#form", {{opacity: 0, y: 120}}, {{opacity: 1, y: 0, duration: 0.25, ease: "power3.out"}}, {F0 + 0.3:.3f});'); WH(F0 + 0.3)
SLAM("#st2", at("not paid"), 2.4); fx("stamp", at("not paid") + 0.02, 0.4)
js.append(f'tl.fromTo("#st1", {{opacity: 0, scale: 3}}, {{opacity: 1, scale: 1, duration: 0.11, ease: "power4.in"}}, {at("were denied") - 0.08:.3f});')
fx("stamp_heavy", at("were denied") + 0.02, 0.42); fx("buzzer", at("were denied") + 0.1, 0.3); shake(at("were denied") + 0.03, 14, 6)
OUT("#form", F1)

# ======================= 3. qualify (over the aerial b-roll) =======================
Q0, Q1 = BR[1]
CK = [("ROOF 10–15 YEARS OLD", at("10 to 15"), end("years old")), ("RECENT STORM", at("recently hit"), at("a storm"))]
rows = "".join(f'<div class="ck" id="ck{j}"><span class="box" id="bx{j}"><b id="tk{j}">✓</b></span>{html.escape(t)}</div>' for j, (t, _, _) in enumerate(CK))
add(f'<div class="check"><div class="ckh" id="ckh">DOES THIS SOUND LIKE YOU?</div>{rows}</div>', "full", "g-check", Q0, Q1)
POP("#ckh", Q0 + 0.05); WH(Q0 + 0.05)
for j, (_, ta, tb) in enumerate(CK):
    js.append(f'tl.fromTo("#ck{j}", {{opacity: 0, x: -80}}, {{opacity: 1, x: 0, duration: 0.2, ease: "back.out(2)"}}, {ta:.3f});'); fx("pop", ta, 0.16)
    tb = min(tb, Q1 - 0.4)
    js.append(f'tl.fromTo("#tk{j}", {{opacity: 0, scale: 2.4}}, {{opacity: 1, scale: 1, duration: 0.16, ease: "back.out(3)"}}, {tb:.3f});')
    js.append(f'tl.to("#bx{j}", {{backgroundColor: "#16a34a", borderColor: "#16a34a", duration: 0.1}}, {tb:.3f});'); fx("tick", tb, 0.38)
fx("thunder", at("recently hit"), 0.32); OUT("#g-check .check", Q1)
pill("g-foryou", f'THIS IS FOR YOU {E("👇")}', Q1, at("risk window") - 0.05, "pill yel")
pill("g-risk", f'{E("⚠️")} YOU\'RE IN THE RISK WINDOW', at("risk window"), at("insurance companies") - 0.05, "pill red")
pill("g-tight", 'INSURERS ARE <span class="y">TIGHTENING</span> GUIDELINES', at("insurance companies"), at("but you don't") - 0.05, "pill dark")
add('<div class="kin"><span id="kw0">DON\'T</span> <span id="kw1" class="y">WORRY.</span></div>', "top", "g-worry", at("but you don't"), at("that is exactly") - 0.05)
for j, t in enumerate((at("don't need"), at("worry now"))):
    js.append(f'tl.fromTo("#kw{j}", {{opacity: 0, scale: 1.8}}, {{opacity: 1, scale: 1, duration: 0.14, ease: "power4.out"}}, {t:.3f});'); fx("pop", t, 0.14)
OUT("#g-worry .kin", at("that is exactly") - 0.05)

# ======================= 4. the turn + company =======================
TU = at("that is exactly")
fx("riser", TU - 1.6, 0.32); flash(TU); fx("drop", TU, 0.4)
FREEZE = (TU, "assets/freeze-turn.jpg")
pill("g-got", f'{E("✅")} WE\'VE GOT YOU', TU + 0.03, CUTS[3] - 0.05, "pill green", sound=None)
T0, T1 = BR[2]
add('<div class="brandin" id="brandin"><div class="b1">PINECREST</div><div class="b2">ROOFING &amp; CONSTRUCTION</div><i id="sweep" data-layout-allow-overflow></i></div>', "full", "g-brand", T0, T1)
js.append(f'tl.fromTo("#brandin", {{opacity: 0, scale: 1.3}}, {{opacity: 1, scale: 1, duration: 0.22, ease: "back.out(2)"}}, {at("pinecrest"):.3f});')
js.append(f'tl.fromTo("#sweep", {{xPercent: -150}}, {{xPercent: 440, duration: 0.9, ease: "power2.inOut"}}, {at("pinecrest") + 0.3:.3f});')
fx("swoosh", at("pinecrest") - 0.12, 0.38); fx("pop", at("pinecrest") + 0.06, 0.34); OUT("#brandin", T1)

# ======================= 5. proof + program (over b-roll) =======================
P0, P1 = BR[3][0], BR[4][0] + 0.9
houses = "".join(f'<span class="hs" id="hs{j}">🏠</span>' for j in range(12))
add(f'<div class="proof"><div class="houses">{houses}</div><div class="dz"><span class="dz1">DOZENS OF LOCAL</span><span class="dz2">HOMEOWNERS</span></div>'
    f'<div class="approved" id="appr">FULLY APPROVED {E("✅")}</div></div>', "full", "g-proof", P0, P1)
POP("#g-proof .houses", P0); POP("#g-proof .dz", P0 + 0.15)
for j in range(12):
    t = P0 + 0.2 + (at("fully approved") - 0.2 - P0 - 0.2) * (j + 1) / 12
    js.append(f'tl.to("#hs{j}", {{opacity: 1, filter: "grayscale(0)", scale: 1.25, duration: 0.06}}, {t:.3f});')
    js.append(f'tl.to("#hs{j}", {{scale: 1, duration: 0.1}}, {t + 0.06:.3f});')
    if j % 2 == 0: fx("count", t, 0.22)
SLAM("#appr", at("fully approved"), 2.2); fx("ding", at("fully approved"), 0.36); OUT("#g-proof .proof", P1)
add(f'<div class="prog" id="prog"><span class="pl">NOW LAUNCHING</span><b>{E("🛡️")} ROOF PROTECTION PROGRAM</b></div>', "full", "g-prog", P1, BR[4][1])
POP("#prog", P1, 0.26); WH(P1); fx("pop", at("protection program"), 0.25)
js.append(f'tl.fromTo("#prog b", {{scale: 1}}, {{scale: 1.06, duration: 0.15, yoyo: true, repeat: 1}}, {at("protection program"):.3f});')
OUT("#prog", BR[4][1])
pill("g-ne", f'{E("📍")} NORTH &amp; EAST TEXAS ONLY', at("exclusively"), at("this program") - 0.05)
pill("g-age", 'BUILT FOR <span class="y">AGING ROOFS</span>', at("this program"), CUTS[7] - 0.05, "pill dark")

# ======================= 6. roof callouts =======================
R0, R1 = BR[5]
def callout(spots, t0, t1):
    svg, labs = [], []
    for j, (kind, x, y, lab, side, tt) in enumerate(spots):
        if kind == "circle":
            svg.append(f'<circle id="cc{j}" cx="{x}" cy="{y}" r="95" fill="none" stroke="#e3121e" stroke-width="10" stroke-linecap="round" stroke-dasharray="600" stroke-dashoffset="600" transform="rotate(-80 {x} {y})"/>')
            js.append(f'tl.to("#cc{j}", {{strokeDashoffset: 0, duration: 0.35, ease: "power2.out"}}, {tt:.3f});'); ly = y - 175
        else:
            svg.append(f'<g id="ca{j}" opacity="0"><line x1="{x + 150}" y1="{y - 150}" x2="{x + 22}" y2="{y - 22}" stroke="#ffd60a" stroke-width="12" stroke-linecap="round"/>'
                       f'<polygon points="{x},{y} {x + 52},{y - 12} {x + 12},{y - 52}" fill="#ffd60a"/></g>')
            js.append(f'tl.fromTo("#ca{j}", {{opacity: 0, x: 40, y: -40}}, {{opacity: 1, x: 0, y: 0, duration: 0.2, ease: "power3.out"}}, {tt:.3f});'); ly = y - 230
        style = f"right:{1080 - (x - 40)}px" if side == "l" else f"left:{x + 40}px"
        labs.append(f'<div class="clabel" id="cl{j}" style="top:{ly}px; {style}">{lab}</div>')
        POP(f"#cl{j}", tt + 0.15, 0.2); fx("blow", tt + 0.15, 0.28)
        if j < len(spots) - 1:   # one callout per beat: clear it as the next one lands
            js.append(f'tl.to("#cl{j}, #{"cc" if kind == "circle" else "ca"}{j}", {{opacity: 0, duration: 0.12}}, {spots[j + 1][5] - 0.08:.3f});')
    add(f'<svg viewBox="0 0 1080 1920" width="1080" height="1920">{"".join(svg)}</svg>{"".join(labs)}', "callout", "g-call", t0, t1, 19)
callout([("circle", 760, 980, "CRACKED SHINGLES?", "l", R0 + 0.15), ("circle", 320, 990, "HAIL DAMAGE?", "r", R0 + 1.1), ("arrow", 560, 1060, "LEAKS?", "r", R0 + 2.05)], R0, R1)
pill("g-qp", 'QUALITY + PRECISION', at("quality and"), R1 - 0.05, "pill dark")

# ======================= 7. offer =======================
add('<div class="nine" id="nine"><span class="n9">9</span><div><b>ROOF PROJECTS</b><i>PER MONTH · THAT\'S IT</i></div></div>', "body", "g-nine", at("we limit"), at("for a limited") - 0.05)
SLAM("#nine", at("nine full"), 2.2); fx("stamp", at("nine full"), 0.32); OUT("#nine", at("for a limited") - 0.05)
pill("g-lim0", f'{E("🔒")} LIMITED SPOTS', at("we limit"), at("nine full") - 0.05, "pill red", sound="pop")
pill("g-lim", f'{E("⏳")} LIMITED TIME', at("for a limited"), at("free no-obligation") - 0.05, "pill yel", sound="clock")
add('<div class="offer" id="offer"><b>FREE ROOF INSPECTION</b><i>$0 • NO OBLIGATION</i></div>', "body", "g-offer", at("free no-obligation"), at("complete with") - 0.05)
SLAM("#offer", at("free no-obligation"), 2.2); fx("pop", at("free no-obligation"), 0.4); fx("ding", at("no-obligation") + 0.3, 0.25); OUT("#offer", at("complete with") - 0.05)
pill("g-photo", f'{E("📸")} PHOTO + VIDEO REPORT', at("complete with"), at("check for") - 0.05, "pill dark")
pill("g-storm", f'{E("🔍")} STORM DAMAGE CHECK', at("check for"), at("just click") - 0.05, "pill red")

# ======================= 8. CTA =======================
PH0, C0 = at("just click"), at("and book")
add('<div class="phone" id="phone"><div class="pscr"><div class="ptop">Pinecrest Roofing</div><div class="ptitle">Free Roof Inspection</div>'
    '<div class="pf"><label>Name</label><div class="pin"><span id="ty0"></span></div></div><div class="pf"><label>Address</label><div class="pin"><span id="ty1"></span></div></div>'
    '<div class="psub" id="psub">SUBMIT</div><div class="pok" id="pok">✓ Request sent</div></div><i class="finger" id="fing"></i></div>', "side", "g-phone", PH0, C0 + 0.1)
js.append(f'tl.fromTo("#phone", {{opacity: 0, x: 260, rotation: 8}}, {{opacity: 1, x: 0, rotation: 0, duration: 0.28, ease: "power3.out"}}, {PH0:.3f});'); WH(PH0)
for j, (txt, t) in enumerate((("Your name", PH0 + 0.35), ("Your address", PH0 + 0.75))):
    js.append(f'tl.fromTo("#fing", {{opacity: 1, y: {j * 96 - 20}, scale: 1.2}}, {{y: {j * 96}, scale: 0.9, duration: 0.08}}, {t - 0.05:.3f});'); fx("tap", t, 0.32)
    for c in range(1, len(txt) + 1): js.append(f'tl.set("#ty{j}", {{textContent: {json.dumps(txt[:c])}}}, {t + c * 0.025:.3f});')
TS = PH0 + 1.2
js.append(f'tl.to("#fing", {{y: 205, scale: 0.9, duration: 0.1}}, {TS - 0.12:.3f});'); fx("click", TS, 0.4)
POP("#pok", TS + 0.12); fx("notify", TS + 0.12, 0.3); OUT("#phone", C0 + 0.1)
pill("g-name", 'PINECREST ROOFING &amp; CONSTRUCTION', C0, DUR + 0.2, "pill dark", sound=None)
add(f'<div class="cta"><div class="ctabtn" id="ctb">BOOK YOUR FREE INSPECTION {E("👇")}</div><svg class="arrow" id="arw" viewBox="0 0 120 150" width="84" height="104">'
    '<path d="M42 0h36v80h32L60 145 10 80h32z" fill="#ffd60a" stroke="#000" stroke-width="8" stroke-linejoin="round"/></svg></div>', "body", "g-cta", C0, DUR)
POP("#ctb", C0 + 0.05, 0.24); fx("pop", C0 + 0.05, 0.35); fx("notify", at("free inspection"), 0.28); POP("#arw", C0 + 0.25)
n_p = int((DUR - C0 - 0.35) / 0.44)
js.append(f'tl.fromTo("#ctb", {{scale: 1}}, {{scale: 1.06, duration: 0.22, ease: "sine.inOut", yoyo: true, repeat: {max(1, n_p * 2 - 1)}, immediateRender: false}}, {C0 + 0.35:.3f});')
js.append(f'tl.fromTo("#arw", {{y: 0}}, {{y: 26, duration: 0.3, ease: "power2.in", yoyo: true, repeat: {max(1, int((DUR - C0 - 0.5) / 0.3) - 1)}, immediateRender: false}}, {C0 + 0.45:.3f});')

# ======================= grade =======================
js.append('tl.set("#grade", {filter: "contrast(1.04) saturate(1.04)"}, 0);')
js.append(f'tl.to("#grade", {{filter: "contrast(1.08) saturate(0.8) brightness(0.92)", duration: 0.3}}, {F0:.3f});')
js.append(f'tl.to("#grade", {{filter: "contrast(1.04) saturate(1.04) brightness(1)", duration: 0.3}}, {CUTS[1]:.3f});')
js.append(f'tl.set("#grade", {{filter: "contrast(1.06) saturate(1.12) sepia(0.06) brightness(1.06)"}}, {TU:.3f});')

# ======================= captions =======================
YEL = ["texas homeowners", "thirty thousand dollars", "texas", "10 to 15 years old", "storm", "insurance", "pinecrest", "roof protection program",
       "north and east texas", "dozens of local homeowners", "fully approved", "free", "free inspection", "learn more"]
RED = ["forty-seven percent", "denied", "not paid out at all", "risk window", "tightening guidelines", "storm damage"]
color = {}
for lst, c in ((YEL, "y"), (RED, "r")):
    for p in lst:
        st = 0
        while True:
            try: ix = find(p, st)
            except SystemExit: break
            for i in ix: color[i] = c
            st = ix[-1] + 1
i30 = find("thirty thousand dollars")[0]; i47 = find("forty-seven percent")[0]
OVR = {i30: "$30,000", i30 + 1: None, i30 + 2: None, i47: "47%", i47 + 1: None}
def disp(i): return OVR.get(i, re.sub(r"[.,?!]+$", "", words[i]["text"]).upper()) if i in OVR else re.sub(r"[.,?!]+$", "", words[i]["text"]).upper()
groups, cur = [], []
for i, w in enumerate(words):
    if cur:
        prev = words[cur[-1]]
        if len([j for j in cur if disp(j)]) >= 3 or re.search(r"[.,?!]$", prev["text"]) or w["start"] - prev["end"] > 0.3: groups.append(cur); cur = []
    cur.append(i)
groups.append(cur)
merged = []
for g in groups:
    if merged and len([i for i in g if disp(i)]) == 1 and len([i for i in merged[-1] if disp(i)]) <= 2 and not re.search(r"[.?!]$", words[merged[-1][-1]]["text"]): merged[-1] += g
    else: merged.append(g)
groups = merged
def units(t): return sum(0.3 if c == " " else 0.32 if c in ".,'-?!" else 1.0 if c in "MW%" else 0.42 if c in "I1" else 0.62 if c in "$0123456789" else 0.8 for c in t)
cap = []
for gi, g in enumerate(groups):
    vis = [i for i in g if disp(i)]
    s0 = words[g[0]]["start"]; nxt = words[groups[gi + 1][0]]["start"] if gi + 1 < len(groups) else DUR
    e0 = DUR if gi == len(groups) - 1 else min(nxt, words[g[-1]]["end"] + 0.4, DUR)
    ws = "".join(f'<span class="w" id="w{i}">{html.escape(disp(i))}</span>' for i in vis)
    em = sum(units(disp(i)) for i in vis) + 0.3 * (len(vis) - 1)
    fs = int(min(76, 940 / 1.12 / em))
    cap.append(f'<div class="cg" id="cg{gi}"><div class="line" style="font-size:{fs}px">{ws}</div></div>')
    js.append(f'tl.fromTo("#cg{gi}", {{opacity: 0, scale: 0.88}}, {{opacity: 1, scale: 1, duration: 0.08, ease: "power2.out"}}, {s0:.3f});')
    for i in vis:
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
    <title>Connor Avatar Ad</title>
    <script src="vendor/gsap.min.js"></script>
    <style>
{CSS}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="{W}" data-height="{H}" data-duration="{DUR}">
      <div id="hand"><div id="cam"><div id="whip"><div id="shake"><div id="grade">
        <video id="src" class="clip" src="assets/look.mp4" muted playsinline data-start="0" data-duration="{DUR}" data-track-index="0"></video>
        <img class="clip freeze" id="fz" src="{FREEZE[1]}" alt="" data-start="{FREEZE[0]:.3f}" data-duration="0.5" data-track-index="3" />
      </div></div></div></div></div>
      {nl.join(el)}
      <div id="captions" class="clip" data-start="0" data-duration="{DUR}" data-track-index="30">
        {nl.join(cap)}
      </div>
      <div id="flash"></div>
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
ev = sorted({0.0, *CUTS, *PUNCH_T, *[float(re.search(r'data-start="([\d.]+)"', e).group(1)) for e in el], *[t for _, t, _ in sfx]})
gaps = [(round(a, 2), round(b - a, 2)) for a, b in zip(ev, ev[1:] + [DUR]) if b - a > 3.0]
print(f"{DUR}s · {len(el)} graphics · {len(PUNCH_T)} punches · {len(groups)} captions · {len(sfx)} sfx · gaps>3s: {gaps or 'none'}")
