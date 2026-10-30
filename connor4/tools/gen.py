"""Connor field ad (9:16): the client's take and voice untouched, the client's own b-roll cut in over it, then
graphics, captions, SFX, music and ambience layered on top. Time everything to the transcript.

Picture: #hand (handheld drift / bob / micro-shake, avatar shots only) > #cam (112 % framing, 117/125 % punch-ins on the
avatar, push / pan / punch on b-roll) > #whip (whip into and out of each b-roll) > #shake > #grade > take + b-roll + freeze.
Zones (face y ~510-840, head top ~505): TOP y 262-452 in the sky above his head, BODY y 905-1285 on his shirt,
CAPTIONS y 1330-1450, SIDE x 724-1054 beside him (phone), FULL screen only over b-roll.
"""
import html, json, math, os, random, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
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
def end(p, after=0): return words[find(p, after)[-1]]["end"]

BRJ = json.load(open("tools/broll.json"))
BR = [(b["t0"], b["t1"]) for b in BRJ]
def is_broll(t): return any(a <= t < b for a, b in BR)
SEG, KIND, t = [], [], 0.0
for a, b in BR:
    if a - t > 0.01: SEG.append((t, a)); KIND.append("avatar")
    SEG.append((a, b)); KIND.append("broll"); t = b
if DUR - t > 0.01: SEG.append((t, DUR)); KIND.append("avatar")
CUTS = [a for a, _ in SEG[1:]]

el, js, sfx = [], [], []
def fx(name, t, vol): sfx.append((name, round(max(0.0, t), 3), vol))
def add(inner, cls, gid, t0, t1, track=20):
    el.append(f'<div class="clip {cls}" id="{gid}" data-start="{t0:.3f}" data-duration="{t1 - t0:.3f}" data-track-index="{track}">{inner}</div>')
def POP(sel, t, d=0.22): js.append(f'tl.fromTo("{sel}", {{opacity: 0, scale: 0.6}}, {{opacity: 1, scale: 1, duration: {d}, ease: "back.out(2.2)"}}, {t:.3f});')
def OUT(sel, t): js.append(f'tl.to("{sel}", {{opacity: 0, scale: 0.92, duration: 0.12, ease: "power2.in"}}, {t - 0.12:.3f});')
def SLAM(sel, t, frm=2.6): js.append(f'tl.fromTo("{sel}", {{opacity: 0, scale: {frm}}}, {{opacity: 1, scale: 1, duration: 0.15, ease: "power4.in"}}, {t - 0.1:.3f});')
def WH(t, v=0.16): fx("wA" if len(sfx) % 2 else "wB", t - 0.08, v)
E = lambda e: f'<span class="emo">{e}</span>'
def flash(t): js.append(f'tl.set("#flash", {{opacity: 1}}, {t:.3f});'); js.append(f'tl.to("#flash", {{opacity: 0, duration: 0.18}}, {t + 0.04:.3f});')
def shake(t, amp=12, n=6):
    for k in range(n):
        s = amp * (1 - k / n) * (1 if k % 2 == 0 else -1)
        js.append(f'tl.to("#shake", {{x: {s:.1f}, y: {-s * 0.6:.1f}, duration: 0.033, ease: "none"}}, {t + k * 0.033:.3f});')
    js.append(f'tl.to("#shake", {{x: 0, y: 0, duration: 0.05}}, {t + n * 0.033:.3f});')
def pill(gid, txt, t0, t1, kind="pill", zone="top", sound="pop", vol=0.2):
    add(f'<div class="{kind}" id="{gid}i">{txt}</div>', zone, gid, t0, t1)
    POP(f"#{gid}i", t0); OUT(f"#{gid}i", t1)
    if sound: fx(sound, t0, vol)

# ======================= handheld (avatar only) =======================
rnd = random.Random(7)
ph = [rnd.uniform(0, 6.28) for _ in range(9)]
def hand(t):
    x = 9 * math.sin(2 * math.pi * 0.23 * t + ph[0]) + 4.5 * math.sin(2 * math.pi * 0.61 * t + ph[1]) + 1.8 * math.sin(2 * math.pi * 1.9 * t + ph[2])
    y = 7 * math.sin(2 * math.pi * 0.19 * t + ph[3]) + 3.6 * math.sin(2 * math.pi * 1.6 * t + ph[4]) + 1.4 * math.sin(2 * math.pi * 2.3 * t + ph[5])   # 1.6 Hz = walking-pace bob
    r = 0.38 * math.sin(2 * math.pi * 0.17 * t + ph[6]) + 0.18 * math.sin(2 * math.pi * 0.53 * t + ph[7]) + 0.05 * math.sin(2 * math.pi * 2.1 * t + ph[8])
    k = 0.15 if is_broll(t) else 1.0
    return x * k, y * k, r * k
STEP, t = 0.2, 0.0
x0, y0, r0 = hand(0); js.append(f'tl.set("#hand", {{x: {x0:.1f}, y: {y0:.1f}, rotation: {r0:.3f}}}, 0);')
while t < DUR:
    x, y, r = hand(t + STEP)
    js.append(f'tl.to("#hand", {{x: {x:.1f}, y: {y:.1f}, rotation: {r:.3f}, duration: {STEP}, ease: "none"}}, {t:.2f});'); t += STEP

# ======================= camera per segment =======================
TU = at("that is exactly")
KEY = [at("$30,000"), at("denied"), at("risk window"), at("approved"), at("9"), at("free no-obligation"), at("book your")]   # 125 %
MID = [at("tightening"), at("worry now"), TU + 0.6, at("this program"), at("aging roofs", find("this program")[0]), at("we limit"), at("for a limited")]   # 117 %
PUNCH_T = []
for k, ((a, b), kind) in enumerate(zip(SEG, KIND)):
    if kind == "avatar":
        js.append(f'tl.set("#cam", {{scale: 1.12, xPercent: 0, yPercent: 0}}, {a:.3f});')
        hits = sorted([(e, 1.25) for e in KEY if a < e < b] + [(e, 1.17) for e in MID if a < e < b])
        for j, (e, s) in enumerate(hits):
            js.append(f'tl.to("#cam", {{scale: {s}, duration: 0.18, ease: "power3.out"}}, {e - 0.04:.3f});')
            nxt = hits[j + 1][0] if j + 1 < len(hits) else b
            back = min(e + 1.6, nxt - 0.3, b - 0.25)
            if back > e + 0.4: js.append(f'tl.to("#cam", {{scale: 1.12, duration: 0.3, ease: "power2.inOut"}}, {back:.3f});')
            PUNCH_T.append(e)
    else:
        mv = BRJ[[x for x, _ in BR].index(a)]["move"]
        if mv == "push": js.append(f'tl.fromTo("#cam", {{scale: 1.0}}, {{scale: 1.1, duration: {b - a:.3f}, ease: "none", immediateRender: {"true" if a == 0 else "false"}}}, {a:.3f});')
        elif mv == "pan":
            d = 1 if k % 2 else -1
            js.append(f'tl.fromTo("#cam", {{scale: 1.1, xPercent: {2.5 * d}}}, {{scale: 1.1, xPercent: {-2.5 * d}, duration: {b - a:.3f}, ease: "none", immediateRender: false}}, {a:.3f});')
        else:   # quick punch
            js.append(f'tl.fromTo("#cam", {{scale: 1.18}}, {{scale: 1.04, duration: 0.35, ease: "power3.out", immediateRender: false}}, {a:.3f});')
            js.append(f'tl.to("#cam", {{scale: 1.09, duration: {b - a - 0.35:.3f}, ease: "none"}}, {a + 0.35:.3f});')
        js.append(f'tl.set("#cam", {{xPercent: 0}}, {b:.3f});')
    if a > 0:   # whip + whoosh into every b-roll and back out to the avatar
        js.append(f'tl.fromTo("#whip", {{yPercent: {7 if kind == "broll" else -7}}}, {{yPercent: 0, duration: 0.2, ease: "power3.out", immediateRender: false}}, {a:.3f});')
        fx("whip" if kind == "broll" else "wA", a - 0.1, 0.16)

# ======================= 1. hook + money =======================
B1 = BR[0][1]
add(f'<div class="hook" id="hk"><i class="haz"></i><div class="hk1">{E("📍")} TEXAS</div><div class="hk2">HOMEOWNERS {E("🚨")}</div><i class="haz"></i></div>', "full", "g-hook", 0.0, B1)
js.append('tl.set("#hk", {opacity: 1, scale: 1}, 0);')
js.append('tl.fromTo("#hk .emo", {rotation: -12}, {rotation: 12, duration: 0.12, yoyo: true, repeat: 5, ease: "sine.inOut"}, 0.0);')
fx("boom", 0.0, 0.36); shake(0.0, 10, 5); OUT("#hk", B1)
pill("g-watch", f'{E("⚠️")} WATCH THIS FIRST', B1 + 0.02, at("$30,000") - 0.08, "pill yel", sound="blow", vol=0.24)
js.append(f'tl.fromTo("#g-watchi", {{scale: 1}}, {{scale: 1.12, duration: 0.1, yoyo: true, repeat: 3, immediateRender: false}}, {at("watch this"):.3f});')
M0 = at("$30,000")
add('<div class="m30" id="m30">$30,000</div>', "top", "g-m30", M0, BR[1][0])
SLAM("#m30", M0, 3.0); shake(M0 + 0.05, 18, 7); fx("kaching", M0, 0.42); fx("boom", M0, 0.22); OUT("#m30", BR[1][0])
W0 = at("on a new")
coins = "".join(f'<i class="coin" id="cn{j}" style="left:{40 + j * 50}px">$</i>' for j in range(3))
add(f'<div class="wal"><div class="wallet" id="wlt"><i class="wbody"></i><i class="wflap"></i>{coins}</div><div class="oop" id="oop">OUT OF YOUR POCKET?</div></div>', "body", "g-wal", W0, BR[1][0])
POP("#wlt", W0, 0.2); POP("#oop", W0 + 0.15); fx("coindrop", W0 + 0.1, 0.4)
for j in range(3):
    js.append(f'tl.fromTo("#cn{j}", {{opacity: 1, y: 0}}, {{opacity: 0, y: 230, rotation: {(j - 1) * 40}, duration: 0.5, ease: "power2.in", immediateRender: false}}, {W0 + 0.2 + j * 0.12:.3f});')
js.append(f'tl.to("#wlt", {{rotation: -8, duration: 0.1, yoyo: true, repeat: 3}}, {W0 + 0.2:.3f});')
OUT("#g-wal .wal", BR[1][0])

# ======================= 2. denied claims =======================
F0, F1 = BR[1]
pill("g-47", f'{E("📊")} <span class="r">47%</span> OF TEXAS ROOF CLAIMS…', at("47%"), F1 - 0.05, "pill", "full")
D0, D1 = F1, at("and if your")
pill("g-den", f'{E("❌")} DENIED. NOT PAID OUT.', at("denied"), D1, "pill red", sound=None)
form = ('<div class="form" id="form" data-layout-allow-occlusion><div class="fh">INSURANCE CLAIM <span>Roof · Storm</span></div>'
        '<div class="frow"><span>Status</span><b id="fst">Under review…</b></div><div class="frow"><span>Payout</span><b>$ ———</b></div>'
        f'<div class="mag" id="mag">🔍</div>'
        '<div class="stamp s1" id="st1" data-layout-allow-overlap data-layout-allow-occlusion>DENIED</div><div class="stamp s2" id="st2" data-layout-allow-overlap data-layout-allow-occlusion>NOT PAID OUT</div></div>')
add(form, "body", "g-form", D0, D1)
js.append(f'tl.fromTo("#form", {{opacity: 0, y: 120}}, {{opacity: 1, y: 0, duration: 0.25, ease: "power3.out"}}, {D0:.3f});'); WH(D0 + 0.05)
js.append(f'tl.fromTo("#mag", {{opacity: 1, x: 0, y: 0}}, {{x: 640, y: 40, duration: 1.2, ease: "sine.inOut", immediateRender: false}}, {D0 + 0.3:.3f});')
js.append(f'tl.to("#mag", {{opacity: 0, duration: 0.1}}, {at("denied") - 0.15:.3f});')
js.append(f'tl.fromTo("#st1", {{opacity: 0, scale: 3}}, {{opacity: 1, scale: 1, duration: 0.11, ease: "power4.in"}}, {at("denied") - 0.08:.3f});')
fx("stamp_heavy", at("denied") + 0.02, 0.3); fx("buzzer", at("denied") + 0.1, 0.2); shake(at("denied") + 0.03, 14, 6)
SLAM("#st2", at("not paid"), 2.4); fx("stamp", at("not paid") + 0.02, 0.36)
OUT("#form", D1)

# ======================= 3. qualify (over the aging-roof + storm b-roll) =======================
Q0, Q1 = BR[2][0], BR[3][1]
CK = [("ROOF 10–15 YEARS OLD", "", at("10 to 15"), end("years old")), ("RECENT STORM", "⛈️", at("recently hit"), at("a storm"))]
rows = "".join(f'<div class="ck" id="ck{j}"><span class="box" id="bx{j}"><b id="tk{j}">✓</b></span>{html.escape(t)}{f"<span class=ckico>{i}</span>" if i else ""}</div>' for j, (t, i, _, _) in enumerate(CK))
add(f'<div class="check"><div class="ckh" id="ckh">DOES THIS SOUND LIKE YOU?</div>{rows}</div>', "full", "g-check", Q0, Q1)
POP("#ckh", Q0 + 0.05); fx("pop", Q0 + 0.1, 0.16)
for j, (_, _, ta, tb) in enumerate(CK):
    ta = max(ta, Q0 + 0.25)
    js.append(f'tl.fromTo("#ck{j}", {{opacity: 0, x: -80}}, {{opacity: 1, x: 0, duration: 0.2, ease: "back.out(2)"}}, {ta:.3f});'); fx("pop", ta, 0.16)
    tb = min(tb, Q1 - 0.4)
    js.append(f'tl.fromTo("#tk{j}", {{opacity: 0, scale: 2.4}}, {{opacity: 1, scale: 1, duration: 0.16, ease: "back.out(3)"}}, {tb:.3f});')
    js.append(f'tl.to("#bx{j}", {{backgroundColor: "#16a34a", borderColor: "#16a34a", duration: 0.1}}, {tb:.3f});'); fx("tick", tb, 0.38)
js.append(f'tl.fromTo("#ck1 .ckico", {{y: 0}}, {{y: -10, duration: 0.15, yoyo: true, repeat: 5, immediateRender: false}}, {at("recently hit") + 0.2:.3f});')
fx("thunder", at("recently hit"), 0.3); OUT("#g-check .check", Q1)
pill("g-risk", f'{E("⚠️")} YOU\'RE IN THE RISK WINDOW', Q1 + 0.05, at("because insurance") - 0.05, "pill red", sound="blow", vol=0.24)
pill("g-tight", 'INSURERS ARE <span class="y">TIGHTENING</span> GUIDELINES', at("because insurance"), at("but you") - 0.05, "pill dark")
add(f'<div class="badge" id="corner"><span class="bk">✓</span>WE\'RE IN YOUR CORNER {E("🤝")}</div>', "top", "g-corner", at("but you"), TU - 0.05)
POP("#corner", at("but you")); fx("ding", at("but you"), 0.2); OUT("#corner", TU - 0.05)

# ======================= 4. the turn + company =======================
fx("riser", TU - 1.6, 0.3); flash(TU); fx("drop", TU, 0.28)
FREEZE = (TU, "assets/freeze-turn.jpg")
pill("g-got", f'{E("✅")} WE\'VE GOT YOU', TU + 0.5, BR[4][0] - 0.05, "pill green", sound="pop", vol=0.3)
T0, T1 = BR[4]
add('<div class="brandin" id="brandin"><div class="b1">PINECREST</div><div class="b2">ROOFING &amp; CONSTRUCTION</div><i id="sweep" data-layout-allow-overflow></i></div>', "full", "g-brand", T0, T1)
js.append(f'tl.fromTo("#brandin", {{opacity: 0, scale: 1.3}}, {{opacity: 1, scale: 1, duration: 0.22, ease: "back.out(2)"}}, {at("pinecrest"):.3f});')
js.append(f'tl.fromTo("#sweep", {{xPercent: -150}}, {{xPercent: 440, duration: 0.9, ease: "power2.inOut"}}, {at("pinecrest") + 0.3:.3f});')
fx("swoosh", at("pinecrest") - 0.12, 0.34); fx("pop", at("pinecrest") + 0.06, 0.3); OUT("#brandin", T1)

# ======================= 5. proof, tracker + approval =======================
P0, P1 = BR[5]
houses = "".join(f'<span class="hs" id="hs{j}">🏠</span>' for j in range(12))
add(f'<div class="proof"><div class="houses">{houses}</div><div class="dz"><span class="dz1">DOZENS OF LOCAL</span><span class="dz2">HOMEOWNERS</span></div></div>', "full", "g-proof", P0, P1)
POP("#g-proof .houses", P0); POP("#g-proof .dz", at("dozens") if at("dozens") > P0 else P0 + 0.15)
for j in range(12):
    t = P0 + 0.15 + (P1 - 0.35 - P0 - 0.15) * (j + 1) / 12
    js.append(f'tl.to("#hs{j}", {{opacity: 1, filter: "grayscale(0)", scale: 1.25, duration: 0.06}}, {t:.3f});')
    js.append(f'tl.to("#hs{j}", {{scale: 1, duration: 0.1}}, {t + 0.06:.3f});')
    if j % 2 == 0: fx("count", t, 0.2)
OUT("#g-proof .proof", P1)
A0, A1 = P1, at("and we're launching")
STEPS = [("INSPECTION", at("get their")), ("CLAIM", at("fully approved")), ("APPROVAL", at("approved"))]
trk = "".join((f'<span class="tarr" id="ta{j}">→</span>' if j else "") + f'<div class="tst"><div class="tdot" id="td{j}">{j + 1}</div><b id="tb{j}">{n}</b></div>' for j, (n, _) in enumerate(STEPS))
add(f'<div class="trk" id="trk"><div class="trh">YOUR INSURANCE CLAIM</div><div class="trs">{trk}</div><div class="gstamp" id="appr" data-layout-allow-overlap>FULLY APPROVED {E("✅")}</div></div>', "body", "g-trk", A0, A1)
js.append(f'tl.fromTo("#trk", {{opacity: 0, y: 120}}, {{opacity: 1, y: 0, duration: 0.25, ease: "power3.out"}}, {A0:.3f});'); WH(A0 + 0.05)
for j, (_, ts) in enumerate(STEPS):
    ts = max(ts, A0 + 0.3 + j * 0.3)
    js.append(f'tl.to("#td{j}", {{backgroundColor: "#16a34a", borderColor: "#16a34a", color: "#ffffff", scale: 1.15, duration: 0.1}}, {ts:.3f});')
    js.append(f'tl.to("#td{j}", {{scale: 1, duration: 0.12}}, {ts + 0.1:.3f});')
    js.append(f'tl.to("#tb{j}", {{color: "#0f2a44", duration: 0.1}}, {ts:.3f});')
    if j: js.append(f'tl.to("#ta{j}", {{color: "#15803d", duration: 0.1}}, {ts - 0.05:.3f});')
    fx("click", ts, 0.3)
AP = at("approved") + 0.12
js.append(f'tl.fromTo("#appr", {{opacity: 0, scale: 2.6, xPercent: -50, yPercent: -50, rotation: -8}}, {{opacity: 1, scale: 1, xPercent: -50, yPercent: -50, rotation: -8, duration: 0.15, ease: "power4.in"}}, {AP:.3f});')
fx("stamp", AP + 0.05, 0.3); fx("ding", AP + 0.1, 0.32)
OUT("#trk", A1)

# ======================= 6. program + area (over b-roll) =======================
G0, G1 = BR[6]
add(f'<div class="prog" id="prog"><span class="pl">NOW LAUNCHING</span><b>{E("🛡️")} ROOF PROTECTION PROGRAM</b></div>', "full", "g-prog", G0, at("exclusively") - 0.05)
POP("#prog", G0 + 0.05, 0.26); fx("pop", G0 + 0.05, 0.24)
js.append(f'tl.fromTo("#prog b", {{scale: 1}}, {{scale: 1.06, duration: 0.15, yoyo: true, repeat: 1}}, {at("protection program"):.3f});')
OUT("#prog", at("exclusively") - 0.05)
pill("g-ne", f'{E("📍")} NORTH &amp; EAST TEXAS ONLY', at("exclusively"), BR[7][1] - 0.05, "pill", "full")
pill("g-age", 'BUILT FOR <span class="y">AGING ROOFS</span>', at("this program"), BR[8][0] - 0.05, "pill dark")
pill("g-qp", f'{E("🔨")} QUALITY + PRECISION', max(at("maintain"), BR[8][0] + 0.1), BR[8][1] - 0.05, "pill", "full")

# ======================= 7. offer =======================
pill("g-lim0", f'{E("🔒")} LIMITED SPOTS', BR[8][1] + 0.05, at("for a limited") - 0.05, "pill red", sound="pop")
add('<div class="nine" id="nine"><span class="n9">9</span><div><b>ROOF PROJECTS</b><i>PER MONTH · THAT\'S IT</i></div></div>', "body", "g-nine", at("9") - 0.1, at("for a limited") - 0.05)
SLAM("#nine", at("9"), 2.2); fx("stamp", at("9"), 0.3); OUT("#nine", at("for a limited") - 0.05)
L0, L1 = at("for a limited"), at("free no-obligation") - 0.05
ring = ('<svg class="ring" viewBox="0 0 150 150"><circle cx="75" cy="75" r="62" fill="rgba(0,0,0,0.55)" stroke="#333" stroke-width="12"/>'
        '<circle id="rg" cx="75" cy="75" r="62" fill="none" stroke="#ffd60a" stroke-width="12" stroke-linecap="round" stroke-dasharray="390" stroke-dashoffset="0" transform="rotate(-90 75 75)"/>'
        '<text x="75" y="92" text-anchor="middle" font-size="52" fill="#fff" font-family="Montserrat" font-weight="900" id="rgt">3</text></svg>')
add(f'<div class="lim" id="lim">{ring}<div class="pill yel">{E("⏳")} LIMITED TIME</div></div>', "top", "g-lim", L0, L1)
POP("#lim", L0); fx("clock", L0, 0.3)
js.append(f'tl.fromTo("#rg", {{strokeDashoffset: 0}}, {{strokeDashoffset: 390, duration: {L1 - L0 - 0.15:.3f}, ease: "none", immediateRender: false}}, {L0 + 0.1:.3f});')
for j, n in enumerate(("2", "1")): js.append(f'tl.set("#rgt", {{textContent: "{n}"}}, {L0 + (L1 - L0) * (j + 1) / 3:.3f});')
OUT("#lim", L1)
O0 = at("free no-obligation")
add('<div class="offer" id="offer"><b>FREE ROOF INSPECTION</b><i>$0 • NO OBLIGATION</i></div>', "body", "g-offer", O0, BR[9][0])
SLAM("#offer", O0, 2.2); fx("pop", O0, 0.38); fx("ding", at("no-obligation") + 0.3, 0.24); OUT("#offer", BR[9][0])
pill("g-photo", f'{E("📸")} PHOTO + VIDEO REPORT', BR[9][0] + 0.1, BR[9][1] - 0.05, "pill dark", "full")

# ======================= 8. damage callouts on the roof b-roll =======================
R0, R1 = BR[10]
def callout(spots, t0, t1):
    svg, labs = [], []
    for j, (x, y, lab, side, tt) in enumerate(spots):
        svg.append(f'<circle id="cc{j}" cx="{x}" cy="{y}" r="105" fill="none" stroke="#e3121e" stroke-width="11" stroke-linecap="round" stroke-dasharray="680" stroke-dashoffset="680" transform="rotate(-80 {x} {y})"/>')
        js.append(f'tl.to("#cc{j}", {{strokeDashoffset: 0, duration: 0.35, ease: "power2.out"}}, {tt:.3f});')
        style = f"right:{1080 - (x + 60)}px" if side == "l" else f"left:{x - 60}px"
        labs.append(f'<div class="clabel" id="cl{j}" style="top:{y - 200}px; {style}">{lab}</div>')
        POP(f"#cl{j}", tt + 0.15, 0.2); fx("blow", tt + 0.15, 0.28)
        if j < len(spots) - 1: js.append(f'tl.to("#cl{j}, #cc{j}", {{opacity: 0, duration: 0.12}}, {spots[j + 1][4] - 0.08:.3f});')
    add(f'<svg viewBox="0 0 1080 1920" width="1080" height="1920">{"".join(svg)}</svg>{"".join(labs)}', "callout", "g-call", t0, t1, 19)
callout([(700, 660, "HAIL DAMAGE?", "l", max(at("check for"), R0 + 0.15)), (360, 470, "CRACKED SHINGLES?", "r", at("storm damage") + 0.1)], R0, R1)

# ======================= 9. CTA =======================
PH0, C0 = at("just click"), at("button below")
add('<div class="phone" id="phone"><div class="pscr"><div class="ptop">Pinecrest Roofing</div><div class="ptitle">Free Roof Inspection</div>'
    '<div class="pf"><label>Name</label><div class="pin"><span id="ty0"></span></div></div><div class="pf"><label>Address</label><div class="pin"><span id="ty1"></span></div></div>'
    '<div class="psub" id="psub">SUBMIT</div><div class="pok" id="pok">✓ Request sent</div></div><i class="finger" id="fing"></i></div>', "side", "g-phone", PH0, C0 + 0.1)
js.append(f'tl.fromTo("#phone", {{opacity: 0, x: 260, rotation: 8}}, {{opacity: 1, x: 0, rotation: 0, duration: 0.28, ease: "power3.out"}}, {PH0:.3f});'); WH(PH0)
for j, (txt, t) in enumerate((("Your name", PH0 + 0.25), ("Your address", PH0 + 0.55))):
    js.append(f'tl.fromTo("#fing", {{opacity: 1, y: {j * 96 - 20}, scale: 1.2}}, {{y: {j * 96}, scale: 0.9, duration: 0.08}}, {t - 0.05:.3f});'); fx("tap", t, 0.32)
    for c in range(1, len(txt) + 1): js.append(f'tl.set("#ty{j}", {{textContent: {json.dumps(txt[:c])}}}, {t + c * 0.02:.3f});')
TS = PH0 + 0.9
js.append(f'tl.to("#fing", {{y: 205, scale: 0.9, duration: 0.1}}, {TS - 0.12:.3f});'); fx("click", TS, 0.4)
POP("#pok", TS + 0.12); fx("notify", TS + 0.12, 0.28); OUT("#phone", C0 + 0.1)
add('<div class="pill dark" id="g-namei">PINECREST ROOFING &amp; CONSTRUCTION</div>', "top", "g-name", C0, DUR); POP("#g-namei", C0)
add(f'<div class="cta"><div class="ctabtn" id="ctb">BOOK YOUR FREE INSPECTION {E("👇")}</div><svg class="arrow" id="arw" viewBox="0 0 120 150" width="84" height="104">'
    '<path d="M42 0h36v80h32L60 145 10 80h32z" fill="#ffd60a" stroke="#000" stroke-width="8" stroke-linejoin="round"/></svg></div>', "body", "g-cta", C0, DUR)
POP("#ctb", C0 + 0.05, 0.24); fx("pop", C0 + 0.05, 0.32); fx("notify", at("free inspection"), 0.26); POP("#arw", C0 + 0.25)
n_p = int((DUR - C0 - 0.35) / 0.44)
js.append(f'tl.fromTo("#ctb", {{scale: 1}}, {{scale: 1.06, duration: 0.22, ease: "sine.inOut", yoyo: true, repeat: {max(1, n_p * 2 - 1)}, immediateRender: false}}, {C0 + 0.35:.3f});')
js.append(f'tl.fromTo("#arw", {{y: 0}}, {{y: 26, duration: 0.3, ease: "power2.in", yoyo: true, repeat: {max(1, int((DUR - C0 - 0.5) / 0.3) - 1)}, immediateRender: false}}, {C0 + 0.45:.3f});')

# ======================= grade =======================
js.append('tl.set("#grade", {filter: "contrast(1.04) saturate(1.04)"}, 0);')
js.append(f'tl.to("#grade", {{filter: "contrast(1.1) saturate(0.78) brightness(0.88)", duration: 0.25}}, {at("denied"):.3f});')
js.append(f'tl.to("#grade", {{filter: "contrast(1.06) saturate(0.9) brightness(0.95)", duration: 0.4}}, {D1:.3f});')
js.append(f'tl.set("#grade", {{filter: "contrast(1.07) saturate(1.14) sepia(0.05) brightness(1.06)"}}, {TU:.3f});')

# ======================= captions =======================
YEL = ["texas homeowners", "$30,000", "10 to 15 years old", "storm", "insurance", "pinecrest", "dozens of local homeowners", "fully approved", "free", "learn more"]
RED = ["denied", "not paid out at all"]
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
    if merged and len(g) == 1 and len(merged[-1]) <= 2 and not re.search(r"[.?!]$", words[merged[-1][-1]]["text"]): merged[-1] += g
    else: merged.append(g)
groups = merged
merged = []
for g in groups:   # a lone word flashing by (< 0.4 s) joins the phrase before it
    if merged and len(g) == 1 and words[g[0]]["end"] - words[g[0]]["start"] < 0.4 and len(merged[-1]) <= 3: merged[-1] += g
    else: merged.append(g)
groups = merged
def units(t): return sum(0.3 if c == " " else 0.32 if c in ".,'-?!" else 1.0 if c in "MW%" else 0.42 if c in "I1" else 0.62 if c in "$0123456789" else 0.8 for c in t)
cap = []
for gi, g in enumerate(groups):
    s0 = words[g[0]]["start"]; nxt = words[groups[gi + 1][0]]["start"] if gi + 1 < len(groups) else DUR
    e0 = DUR if gi == len(groups) - 1 else min(nxt - 0.05, words[g[-1]]["end"] + 0.4, DUR)
    ws = "".join(f'<span class="w" id="w{i}">{html.escape(disp(i))}</span>' for i in g)
    em = sum(units(disp(i)) * 1.06 for i in g) + 0.42 * (len(g) - 1)
    fs = int(min(78, 940 / 1.14 / em))
    cap.append(f'<div class="cg" id="cg{gi}"><div class="line" style="font-size:{fs}px">{ws}</div></div>')
    js.append(f'tl.fromTo("#cg{gi}", {{opacity: 0, scale: 0.9}}, {{opacity: 1, scale: 1, duration: 0.12, ease: "back.out(2)"}}, {s0 - 0.04:.3f});')
    for i in g:
        col = {"y": "#ffd60a", "r": "#ff3b30"}.get(color.get(i), "#5cf27a")
        js.append(f'tl.fromTo("#w{i}", {{scale: 1, color: "#ffffff"}}, {{scale: 1.08, color: "{col}", duration: 0.08, ease: "power2.out"}}, {words[i]["start"]:.3f});')
        js.append(f'tl.to("#w{i}", {{scale: 1, duration: 0.12, ease: "power2.inOut"{', color: "#ffffff"' if i not in color else ''}}}, {max(words[i]["start"] + 0.07, words[i]["end"]):.3f});')
    js.append(f'tl.set("#cg{gi}", {{opacity: 0, visibility: "hidden"}}, {e0:.3f});')

aud = []
for n, (k, t, v) in enumerate(sorted(sfx, key=lambda x: x[1])):
    f = f"assets/sfx/{k}.wav"
    aud.append(f'<audio id="fx{n}" src="{f}" data-start="{t:.3f}" data-duration="{min(probe(f), DUR - t):.3f}" data-track-index="{40 + n}" data-volume="{v}"></audio>')
brv = [f'<video class="clip brv" id="bv{n}" src="assets/br/{b["file"]}" muted playsinline data-start="{b["t0"]:.3f}" data-duration="{b["t1"] - b["t0"]:.3f}" data-track-index="{2 + n % 2}"></video>' for n, b in enumerate(BRJ)]
CSS = open("tools/style.css").read()
nl = "\n      "
doc = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <title>Connor Field Ad</title>
    <script src="vendor/gsap.min.js"></script>
    <style>
{CSS}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="{W}" data-height="{H}" data-duration="{DUR}">
      <div id="hand"><div id="cam"><div id="whip"><div id="shake"><div id="grade">
        <video id="src" class="clip" src="assets/look.mp4" muted playsinline data-start="0" data-duration="{DUR}" data-track-index="0"></video>
        {(nl + "  ").join(brv)}
        <img class="clip freeze" id="fz" src="{FREEZE[1]}" alt="" data-start="{FREEZE[0]:.3f}" data-duration="0.5" data-track-index="4" />
      </div></div></div></div></div>
      {nl.join(el)}
      <div id="captions" class="clip" data-start="0" data-duration="{DUR}" data-track-index="30">
        {nl.join(cap)}
      </div>
      <div id="flash"></div>
    </div>
    <audio id="vo" src="assets/vo.wav" data-start="0" data-duration="{DUR}" data-track-index="1" data-volume="1"></audio>
    <audio id="amb" src="assets/ambience.wav" data-start="0" data-duration="{DUR}" data-track-index="5" data-volume="1"></audio>
    <audio id="music" src="assets/music_bed.wav" data-start="0" data-duration="{DUR}" data-track-index="6" data-volume="1"></audio>
    {chr(10).join("    " + a for a in aud).lstrip()}
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
ev = sorted({0.0, *CUTS, *PUNCH_T, *[float(re.search(r'data-start="([\d.]+)"', e).group(1)) for e in el], *[t for _, t, _ in sfx]})
gaps = [(round(a, 2), round(b - a, 2)) for a, b in zip(ev, ev[1:] + [DUR]) if b - a > 3.0]
wide = []   # avatar stretches held at 112 % for more than 3 s with no punch, graphic or cut
for (a, b), kind in zip(SEG, KIND):
    if kind != "avatar": continue
    pts = sorted({a, b, *[p for p in PUNCH_T if a < p < b], *[float(re.search(r'data-start="([\d.]+)"', e).group(1)) for e in el if a < float(re.search(r'data-start="([\d.]+)"', e).group(1)) < b]})
    wide += [(round(x, 2), round(y - x, 2)) for x, y in zip(pts, pts[1:]) if y - x > 3.0]
print(f"{DUR}s · {len(el)} graphics · {len(PUNCH_T)} punches · {len(groups)} captions · {len(sfx)} sfx · gaps>3s: {gaps or 'none'} · wide>3s: {wide or 'none'}")
