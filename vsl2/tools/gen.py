"""Website VSL (1920x1080): designed motion graphics, kinetic type, captions, camera moves and sound on top of the
client's talking-head take (assets/base.mp4, natural pace; only one >1 s pause shortened).

Three layouts only (see LAYOUT): talk (shot full frame, sharp), split (shot in a rounded frame left, graphic right)
and full (shot hidden, graphic full screen). The face is never blurred or darkened behind a graphic.
Picture stack: #slide (layout) > #cam (slow push / pull / drift) > #punch (115 % punch-ins) > #shake > #grade > video.
Graphics: .stage (full layout) or .panel (right side in split layout). Captions stay at the bottom in every layout.
One font (Montserrat 900/800), one palette (yellow #ffd60a, red #e3121e, white, green #16a34a), one pop-in.
"""
import html, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
W, H = 1920, 1080
probe = lambda f: float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                                       capture_output=True, text=True).stdout)
DUR = round(probe("assets/base.mp4") - 0.04, 3)
words = json.load(open("transcript.json"))

def clean(t): return re.sub(r"[.,?!]+$", "", t).lower()
def find(p, after=0):
    toks = p.lower().split()
    for i in range(after, len(words)):
        if [clean(w["text"]) for w in words[i:i + len(toks)]] == toks: return list(range(i, i + len(toks)))
    sys.exit(f"phrase not found: {p}")
def at(p, after=0): return words[find(p, after)[0]]["start"]
def end(p, after=0): return words[find(p, after)[-1]]["end"]
def after(p, q): return words[find(q, find(p)[-1])[0]]["start"]   # first q after phrase p

el, js, sfx = [], [], []
def fx(name, t, vol, dur=None): sfx.append((name, round(max(0.0, t), 3), vol, dur))
def add(inner, cls, gid, t0, t1, track=20):
    el.append(f'<div class="clip {cls}" id="{gid}" data-start="{t0:.3f}" data-duration="{t1 - t0:.3f}" data-track-index="{track}">{inner}</div>')
def POP(sel, t, d=0.22): js.append(f'tl.fromTo("{sel}", {{opacity: 0, scale: 0.6}}, {{opacity: 1, scale: 1, duration: {d}, ease: "back.out(2.2)"}}, {t:.3f});')
def OUT(sel, t): js.append(f'tl.to("{sel}", {{opacity: 0, scale: 0.94, duration: 0.14, ease: "power2.in"}}, {t - 0.14:.3f});')
def SNAP(sel, t, frm="scale: 1.7"): js.append(f'tl.fromTo("{sel}", {{opacity: 0, {frm}}}, {{opacity: 1, scale: 1, x: 0, y: 0, duration: 0.14, ease: "power4.out"}}, {t:.3f});')
def WH(t, v=0.16): fx("wA" if len(sfx) % 2 else "wB", t - 0.08, v)
E = lambda e: f'<span class="emo">{e}</span>'
def flash(t): js.append(f'tl.set("#flash", {{opacity: 1}}, {t:.3f});'); js.append(f'tl.set("#flash", {{opacity: 0}}, {t + 0.08:.3f});')
def shake(t, amp=12, n=6):
    for k in range(n):
        s = amp * (1 - k / n) * (1 if k % 2 == 0 else -1)
        js.append(f'tl.to("#shake", {{x: {s:.1f}, y: {-s * 0.6:.1f}, duration: 0.04, ease: "none"}}, {t + k * 0.04:.3f});')
    js.append(f'tl.to("#shake", {{x: 0, y: 0, duration: 0.05}}, {t + n * 0.04:.3f});')

DIM, SLIDE = [], []          # (t0, t1) windows

# ======================= 1. OPENING =======================
add(f'<div class="hook" id="hk"><i class="haz"></i><div class="hk1">ROOFERS, STOP. {E("🚨")}</div><i class="haz"></i></div>', "stage", "g-hook", 0.0, at("tired of") - 0.02)
js.append('tl.set("#hk", {opacity: 1, scale: 1}, 0);')
js.append('tl.fromTo("#hk .emo", {rotation: -14}, {rotation: 14, duration: 0.12, yoyo: true, repeat: 7, ease: "sine.inOut"}, 0.0);')
js.append('tl.fromTo("#hk", {scale: 1}, {scale: 1.05, duration: 0.12, yoyo: true, repeat: 1}, 0.55);')
OUT("#hk", at("tired of") - 0.02); fx("boom", 0.0, 0.5); shake(0.0, 10, 5)
DIM.append((0.0, at("tired of")))
TI = [("CHASING DEAD-END LEADS", at("tired of chasing"), end("dead-end leads")),
      ("PRICE SHOPPERS WHO GHOST YOU", at("tired of price"), end("who ghost you")),
      ("RELYING ON REFERRALS & LUCK", at("tired of relying"), end("and luck"))]
rows = "".join(f'<div class="li" id="li{j}"><span class="lx">{E("😩")}</span><b>{html.escape(t)}</b><i class="strike" id="sk{j}"></i></div>' for j, (t, _, _) in enumerate(TI))
L0, L1 = TI[0][1], at("stop what")
add(f'<div class="ptitle" id="lt">TIRED OF…</div>{rows}', "panel", "g-list", L0, L1)
SLIDE.append((L0, L1)); POP("#lt", L0); WH(L0)
for j, (_, ta, tb) in enumerate(TI):
    js.append(f'tl.fromTo("#li{j}", {{opacity: 0, x: 120}}, {{opacity: 1, x: 0, duration: 0.22, ease: "back.out(2)"}}, {ta:.3f});')
    js.append(f'tl.fromTo("#sk{j}", {{scaleX: 0}}, {{scaleX: 1, duration: 0.22, ease: "power3.out"}}, {tb - 0.05:.3f});')
    js.append(f'tl.to("#li{j} b", {{color: "rgba(255,255,255,0.45)", duration: 0.15}}, {tb:.3f});')
    fx("blow", tb, 0.32); WH(ta, 0.14)
OUT("#g-list .ptitle, #g-list .li", L1)
# stop + pay attention: freeze, flash, big card
PA = at("pay attention")
FREEZE = [(at("so we built"), "assets/freeze-turn.jpg")]   # the turn lands in split screen, so the frozen frame shows sharp in the left frame
flash(PA); fx("boom", PA, 0.45); shake(PA + 0.02, 14, 6)
add(f'<div class="big y" id="pa">PAY ATTENTION {E("👇")}</div>', "stage", "g-pay", PA, at("what i'm") + 0.9)
POP("#pa", PA + 0.03, 0.26); OUT("#pa", at("what i'm") + 0.9)
DIM.append((PA, at("what i'm") + 0.9))
# ======================= 2. THE PROBLEM =======================
def phone(pid, screen):
    return f'<div class="phone" id="{pid}"><div class="pscr">{screen}</div><i class="notch"></i></div>'
# lead inbox flooding
IB0, IB1 = at("you've probably"), at("you call")
NOTES = [("Marketplace", "Roof quote – wants 3 bids", "$87"), ("Directory", "Leak repair – price check", "$64"), ("Home app", "New roof – just curious", "$92"),
         ("Social ads", "Inspection – no timeline", "$41"), ("Marketplace", "Re-roof – comparing bids", "$78"), ("Directory", "Shingles – cheapest option", "$55"),
         ("Home app", "Storm damage – already hired?", "$83"), ("Marketplace", "Roof quote – wrong number", "$71")]
NT = [at("angie"), at("homeadvisor"), at("thumbtack"), at("or hired"), at("facebook ads"), at("and what did"), at("recycled"), at("low-intent")]
notes = "".join(f'<div class="note" id="nt{j}"><span class="ni">{E("🔔")}</span><div><b>New lead · {s}</b><i>{html.escape(d)}</i></div><em>{p}</em></div>'
                for j, (s, d, p) in enumerate(NOTES))
add(f'<div class="ptitle" id="ibt">THE LEAD INBOX</div>' + phone("ph1", f'<div class="sbar">Leads <span id="ibn" class="badge">0</span></div><div class="notes">{notes}</div>'),
    "panel", "g-inbox", IB0, IB1 - 0.05)
SLIDE.append((IB0, IB1)); POP("#ibt", IB0); js.append(f'tl.fromTo("#ph1", {{opacity: 0, y: 300}}, {{opacity: 1, y: 0, duration: 0.3, ease: "power3.out"}}, {IB0:.3f});'); WH(IB0)
for j, t in enumerate(NT):
    js.append(f'tl.fromTo("#nt{j}", {{opacity: 0, y: -60}}, {{opacity: 1, y: 0, duration: 0.18, ease: "back.out(2)"}}, {t:.3f});')
    for k in range(j):
        js.append(f'tl.to("#nt{k}", {{y: {(j - k) * 108}, duration: 0.18, ease: "power2.out"}}, {t:.3f});')
    js.append(f'tl.set("#ibn", {{textContent: "{j + 1}"}}, {t:.3f});')
    fx("notify", t, 0.22 if j < 3 else 0.16)
js.append(f'tl.fromTo("#g-inbox .note", {{borderColor: "rgba(255,255,255,0)"}}, {{borderColor: "#e3121e", duration: 0.2, immediateRender: false}}, {at("low-intent"):.3f});')
OUT("#g-inbox .ptitle, #ph1", IB1 - 0.05)
# call failed -> seen 3 days ago
CF0, CF1 = at("you call"), at("the ones who")
scr = ('<div class="call" id="callv"><div class="cav">👤</div><div class="cnm">Mike R. · new lead</div><div class="cst" id="cst">Calling…</div>'
       '<div class="cfail" id="cfail">Call failed ✕</div></div>'
       '<div class="chat" id="chatv"><div class="cnm2">Mike R.</div><div class="bub">Hi Mike, just following up on your roof quote. Still interested?</div>'
       '<div class="seen" id="seen">Seen 3 days ago</div></div>')
add(f'<div class="ptitle" id="cft">YOU FOLLOW UP…</div>' + phone("ph2", scr), "panel", "g-call", CF0, CF1 - 0.05)
SLIDE.append((CF0, CF1)); POP("#cft", CF0); js.append(f'tl.fromTo("#ph2", {{opacity: 0, y: 300}}, {{opacity: 1, y: 0, duration: 0.3, ease: "power3.out"}}, {CF0:.3f});'); WH(CF0)
fx("ring", CF0 + 0.1, 0.2)
js.append(f'tl.fromTo("#cfail", {{opacity: 0, scale: 1.6}}, {{opacity: 1, scale: 1, duration: 0.15, ease: "back.out(3)"}}, {at("don\'t answer"):.3f});')
js.append(f'tl.set("#cst", {{opacity: 0}}, {at("don\'t answer"):.3f});'); fx("buzzer2", at("don't answer"), 0.26)
js.append(f'tl.set("#callv", {{opacity: 0}}, {at("you follow"):.3f});'); js.append(f'tl.fromTo("#chatv", {{opacity: 0}}, {{opacity: 1, duration: 0.15}}, {at("you follow"):.3f});')
fx("pop", at("you follow"), 0.25)
js.append(f'tl.fromTo("#seen", {{opacity: 0, y: 14}}, {{opacity: 1, y: 0, duration: 0.15}}, {at("ghost you", find("follow up")[0]):.3f});')
fx("buzzer", at("ghost you", find("follow up")[0]), 0.24)
OUT("#g-call .ptitle, #ph2", CF1 - 0.05)
# 1 homeowner -> 5 roofers, price drop, race to the bottom
RB0, RB1 = CF1, at("here's what nobody")
lines = "".join(f'<line id="ln{k}" x1="380" y1="230" x2="{80 + k * 150}" y2="92" stroke="#ffd60a" stroke-width="5" stroke-linecap="round" stroke-dasharray="300" stroke-dashoffset="300"/>' for k in range(5))
roofers = "".join(f'<div class="rf" id="rf{k}" style="left:{80 + k * 150 - 45}px">{E("👷")}</div>' for k in range(5))
add(f'<div class="race2"><svg viewBox="0 0 760 300" width="760" height="300">{lines}</svg>{roofers}<div class="ho" id="ho">{E("🏠")}<b>1 HOMEOWNER</b></div>'
    f'<div class="price" id="price"><span id="pv">$18,000</span></div><div class="rtb" id="rtb">RACE TO THE BOTTOM</div></div>', "panel", "g-race", RB0, RB1 - 0.05)
DIM.append((RB0, RB1)); POP("#ho", RB0); WH(RB0)
FIVE = at("five other")
for k in range(5):
    js.append(f'tl.to("#ln{k}", {{strokeDashoffset: 0, duration: 0.25, ease: "power2.out"}}, {FIVE + k * 0.09:.3f});')
    js.append(f'tl.fromTo("#rf{k}", {{opacity: 0, scale: 0.4}}, {{opacity: 1, scale: 1, duration: 0.18, ease: "back.out(3)"}}, {FIVE + 0.1 + k * 0.09:.3f});')
    fx("tick", FIVE + 0.1 + k * 0.09, 0.2)
PR = [("$18,000", end("other roofers") - 0.1), ("$14,500", at("lowest bid")), ("$11,900", at("bid wins"))]
POP("#price", PR[0][1])
for j, (v, t) in enumerate(PR):
    js.append(f'tl.set("#pv", {{textContent: "{v}"}}, {t:.3f});')
    js.append(f'tl.fromTo("#price", {{y: {-20 if j else 0}}}, {{y: 0, duration: 0.15, ease: "power3.out"}}, {t:.3f});')
    if j: js.append(f'tl.to("#price", {{backgroundColor: "{["#ffffff", "#ffd60a", "#e3121e"][j]}", color: "{["#111", "#111", "#fff"][j]}", duration: 0.12}}, {t:.3f});')
    fx("blow", t, 0.28)
js.append(f'tl.fromTo("#rtb", {{opacity: 0, scale: 2.6, rotation: -6}}, {{opacity: 1, scale: 1, rotation: -3, duration: 0.14, ease: "power4.in"}}, {at("race to the bottom") - 0.08:.3f});')
fx("stamp_heavy", at("race to the bottom") + 0.02, 0.32); shake(at("race to the bottom") + 0.04, 10, 5)
OUT("#g-race .race2", RB1 - 0.05)
# nobody wants to admit / don't care / get paid either way
DC0 = at("most lead")
add('<div class="card2"><div class="c2a" id="dc1">MOST LEAD COMPANIES &amp; AGENCIES</div><div class="c2b r" id="dc2">DON\'T CARE ABOUT YOUR RESULTS</div></div>', "panel", "g-care", DC0, at("they get paid") - 0.05)
POP("#dc1", DC0); WH(DC0); js.append(f'tl.fromTo("#dc2", {{opacity: 0, scale: 2.2}}, {{opacity: 1, scale: 1, duration: 0.14, ease: "power4.in"}}, {at("don\'t care") - 0.06:.3f});')
fx("stamp", at("don't care") + 0.02, 0.36); OUT("#g-care .card2", at("they get paid") - 0.05); DIM.append((DC0, at("they get paid")))
GP0 = at("they get paid")
add(f'<div class="card2"><div class="c2a" id="gp1">{E("💸")} THEY GET PAID WHEN LEADS LAND</div><div class="c2b y" id="gp2">CLOSE OR NOT.</div></div>', "panel", "g-paid", GP0, at("the same lead") - 0.05)
POP("#gp1", GP0); WH(GP0); SNAP("#gp2", at("whether you")); fx("pop", at("whether you"), 0.3); OUT("#g-paid .card2", at("the same lead") - 0.05)
DIM.append((GP0, at("the same lead")))
# sold 5x
SL0, SL1 = at("the same lead"), at("you're not broken")
card = lambda k: (f'<div class="lead" id="ld{k}"><div class="lh">🔔 NEW LEAD</div><b>Roof replacement</b><i>Homeowner · Your area</i></div>')
add('<div class="leads">' + "".join(card(k) for k in range(5)) + '<div class="sold" id="sold" data-layout-allow-overlap>SOLD 5X</div><div class="youpay" id="ypay">…AND YOU PAY FOR IT</div></div>',
    "panel", "g-sold", SL0, SL1 - 0.05)
DIM.append((SL0, SL1)); js.append(f'tl.fromTo("#ld0", {{opacity: 0, scale: 0.6}}, {{opacity: 1, scale: 1, x: 0, duration: 0.22, ease: "back.out(2.2)"}}, {SL0:.3f});'); WH(SL0)
SO = at("sold to five")
for k in range(1, 5):
    js.append(f'tl.fromTo("#ld{k}", {{opacity: 0, x: 0, y: 0, rotation: 0}}, {{opacity: 1, x: {(k - 2) * 95}, y: {(k - 2) * 34}, rotation: {(k - 2) * 5}, duration: 0.2, ease: "power3.out"}}, {SO + k * 0.12:.3f});')
    fx("pop", SO + k * 0.12, 0.2)
js.append(f'tl.to("#ld0", {{x: -190, y: -68, rotation: -10, duration: 0.2, ease: "power3.out"}}, {SO:.3f});')
js.append(f'tl.fromTo("#sold", {{opacity: 0, scale: 2.8, rotation: -12}}, {{opacity: 1, scale: 1, rotation: -8, duration: 0.13, ease: "power4.in"}}, {at("competitors") - 0.08:.3f});')
fx("stamp_heavy", at("competitors") + 0.02, 0.4); shake(at("competitors") + 0.03, 8, 4)
POP("#ypay", at("you're the one")); fx("blow", at("you're the one"), 0.25)
OUT("#g-sold .leads", SL1 - 0.05)
# you're not broken. the system is.
NB = at("you're not broken"); SY = at("the system is")
add('<div class="kin xl"><div id="nb1">YOU\'RE NOT BROKEN.</div><div id="nb2" class="y">THE SYSTEM IS.</div></div>', "stage", "g-broken", NB, at("so we built") - 0.02)
SNAP("#nb1", NB, "y: 80"); SNAP("#nb2", SY, "scale: 2.2"); fx("boom", SY, 0.14); shake(SY + 0.02, 8, 4)
DIM.append((NB, at("so we built")))

# ======================= 3. THE TURN =======================
TU = at("so we built")
fx("riser", TU - 1.6, 0.3); flash(TU); fx("drop", TU, 0.3)
add(f'<div class="gotit" id="dsys">{E("✅")} A DIFFERENT SYSTEM</div>', "panel", "g-diff", TU, at("where we only") + 1.0)
POP("#dsys", TU + 0.04, 0.26); OUT("#dsys", at("where we only") + 1.0); DIM.append((TU, at("where we only") + 1.0))
WO0, WO1 = at("where we only") + 1.0, at("you don't pay for")
chips = [("REAL HOMEOWNER", at("real homeowner")), ("REAL BUDGET", at("real budget")), ("READY TO MOVE", at("ready to move"))]
cr = "".join(f'<div class="ck" id="wc{j}"><span class="box" id="wb{j}"><b id="wt{j}">✓</b></span>{t}</div>' for j, (t, _) in enumerate(chips))
add(f'<div class="ptitle" id="wot">WE ONLY GET PAID WHEN…</div>{cr}<div class="ftf" id="ftf">{E("🤝")} FACE TO FACE</div>', "panel", "g-when", WO0, WO1 - 0.05)
SLIDE.append((WO0, WO1)); POP("#wot", WO0); WH(WO0)
for j, (_, t) in enumerate(chips):
    t = max(t, WO0 + 0.15 + j * 0.3)
    js.append(f'tl.fromTo("#wc{j}", {{opacity: 0, x: 100}}, {{opacity: 1, x: 0, duration: 0.2, ease: "back.out(2)"}}, {t:.3f});')
    js.append(f'tl.fromTo("#wt{j}", {{opacity: 0, scale: 2.4}}, {{opacity: 1, scale: 1, duration: 0.16, ease: "back.out(3)"}}, {t + 0.2:.3f});')
    js.append(f'tl.to("#wb{j}", {{backgroundColor: "#16a34a", borderColor: "#16a34a", duration: 0.1}}, {t + 0.2:.3f});')
    fx("tick", t + 0.2, 0.35)
POP("#ftf", at("face to face")); fx("pop", at("face to face"), 0.35); OUT("#g-when .ptitle, #g-when .ck, #ftf", WO1 - 0.05)
NP0, NP1 = WO1, at("here's how it works")
add('<div class="nopay"><div class="np" id="np0"><span class="xx">✕</span>PAY FOR LEADS</div><div class="np" id="np1"><span class="xx">✕</span>MONTHLY RETAINER</div>'
    f'<div class="okc" id="okc">{E("✅")} ONLY PAY WHEN YOU\'RE FACE TO FACE</div></div>', "panel", "g-nopay", NP0, NP1 + 0.6)
DIM.append((NP0, NP1 + 0.6))
for j, t in enumerate((at("pay for leads"), at("monthly retainer"))):
    POP(f"#np{j}", t - 0.1); fx("buzzer2", t + 0.05, 0.22); WH(t - 0.1, 0.12)
js.append(f'tl.fromTo("#okc", {{opacity: 0, scale: 0.5}}, {{opacity: 1, scale: 1, duration: 0.24, ease: "back.out(2.4)"}}, {end("monthly retainer") + 0.05:.3f});')
fx("ding", end("monthly retainer") + 0.05, 0.32); OUT("#g-nopay .nopay", NP1 + 0.6)
add('<div class="kin mid"><div><span id="kh0">HOW IT WORKS:</span></div><div><span id="kh1" class="y">3 STEPS</span></div></div>', "panel", "g-how", NP1 + 0.6, at("step one") - 0.02)
SNAP("#kh0", NP1 + 0.6, "y: 60"); SNAP("#kh1", at("three steps"), "scale: 2.2"); fx("boom", at("three steps"), 0.25)
DIM.append((NP1 + 0.6, at("step one")))

# ======================= 4. THE 3 STEPS =======================
def step_card(n, t, t1):
    add(f'<div class="stepc" id="sc{n}"><span>STEP</span><b>{n}</b></div>', "panel", f"g-step{n}", t, t1, 24)
    js.append(f'tl.fromTo("#sc{n}", {{opacity: 0, scale: 2.4}}, {{opacity: 1, scale: 1, duration: 0.16, ease: "power4.in"}}, {t - 0.06:.3f});')
    fx("boom", t + 0.04, 0.22); flash(t + 0.04); OUT(f"#sc{n}", t1); DIM.append((t, t1))
S1 = at("step one"); step_card(1, S1, at("we run") + 0.45)
AD0, AD1 = at("we run") + 0.45, at("if you run")
ad = ('<div class="feed"><div class="fhd"><span class="fav">👷</span><div><b>Your Roofing Co.</b><i>Sponsored</i></div></div>'
      '<div class="fimg"><span>👷</span><em>Meet the crew behind your roof</em></div><div class="fcta">Book a free inspection</div></div>')
gen = '<div class="genad" id="genad"><b>FREE QUOTE!</b><i>Roofing · Call now</i><span>GENERIC</span></div>'
add(f'<div class="ptitle" id="adt">ADS BUILT AROUND <span class="y">YOU</span></div><div class="adrow">{phone("ph3", ad)}{gen}</div>', "panel", "g-ads", AD0, AD1 - 0.05)
SLIDE.append((AD0, AD1)); POP("#adt", AD0); WH(AD0)
js.append(f'tl.fromTo("#ph3", {{opacity: 0, y: 300}}, {{opacity: 1, y: 0, duration: 0.3, ease: "power3.out"}}, {AD0 + 0.1:.3f});')
js.append(f'tl.fromTo("#genad", {{opacity: 0, x: 80}}, {{opacity: 1, x: 0, duration: 0.22, ease: "power3.out"}}, {at("generic") - 0.1:.3f});')
js.append(f'tl.to("#genad", {{filter: "grayscale(1) brightness(0.55)", duration: 0.3}}, {at("generic") + 0.5:.3f});')
fx("pop", at("generic") - 0.1, 0.25); fx("buzzer2", at("every roofer", find("generic")[0]), 0.16)
OUT("#g-ads .ptitle, #g-ads .adrow", AD1 - 0.05)
NC0 = at("not by")
add('<div class="card2"><div class="c2a" id="nc1"><s>A COMMODITY</s></div><div class="c2b y" id="nc2">THE ONE THING THEY CAN\'T COPY</div></div>', "panel", "g-commodity", NC0, at("step two") - 0.02)
POP("#nc1", at("commodity")); WH(at("commodity")); SNAP("#nc2", at("the one thing"), "scale: 1.8"); fx("ding", at("replicate"), 0.25)
OUT("#g-commodity .card2", at("step two") - 0.02); DIM.append((NC0, at("step two")))
# step 2
S2 = at("step two"); step_card(2, S2, at("we call") + 0.35)
CA0, CA1 = at("we call") + 0.35, at("no more dealing")
cs = ('<div class="call"><div class="cav">👤</div><div class="cnm">New lead · Roof replacement</div><div class="cst">Calling… <span id="tmr">0:00</span></div></div>')
checks = [("OWNS THE HOME", at("motivated buyers")), ("REAL BUDGET", at("financially qualified")), ("READY TO MOVE", at("to get a roof", find("qualified")[0]))]
cr2 = "".join(f'<div class="ck sm" id="q{j}"><span class="box" id="qb{j}"><b id="qt{j}">✓</b></span>{t}</div>' for j, (t, _) in enumerate(checks))
add(f'<div class="ptitle" id="c2t">WE CALL EVERY LEAD</div><div class="adrow">{phone("ph4", cs)}<div class="qcol"><div class="cin" id="cin">⏱ CALLED IN 2 MIN</div>{cr2}</div></div>',
    "panel", "g-call2", CA0, CA1 + 0.1)
SLIDE.append((CA0, CA1 + 0.1)); POP("#c2t", CA0); WH(CA0)
js.append(f'tl.fromTo("#ph4", {{opacity: 0, y: 300}}, {{opacity: 1, y: 0, duration: 0.3, ease: "power3.out"}}, {CA0:.3f});')
js.append(f'tl.fromTo("#ph4", {{rotation: -2}}, {{rotation: 2, duration: 0.06, yoyo: true, repeat: 9, immediateRender: false}}, {CA0 + 0.35:.3f});')
fx("ring", CA0 + 0.35, 0.3); fx("ring", CA0 + 1.4, 0.24)
tsec = [f"0:{s:02d}" for s in range(0, 60, 7)] + ["1:05", "1:24", "1:39", "1:52"]
T0, T1 = CA0 + 0.3, at("first five") + 0.2
for k, v in enumerate(tsec): js.append(f'tl.set("#tmr", {{textContent: "{v}"}}, {T0 + (T1 - T0) * k / len(tsec):.3f});')
js.append(f'tl.fromTo("#cin", {{opacity: 0, scale: 2}}, {{opacity: 1, scale: 1, duration: 0.15, ease: "power4.in"}}, {T1:.3f});'); fx("ding", T1 + 0.05, 0.3)
for j, (_, t) in enumerate(checks):
    js.append(f'tl.fromTo("#q{j}", {{opacity: 0, x: 100}}, {{opacity: 1, x: 0, duration: 0.2, ease: "back.out(2)"}}, {t:.3f});')
    js.append(f'tl.fromTo("#qt{j}", {{opacity: 0, scale: 2.4}}, {{opacity: 1, scale: 1, duration: 0.16, ease: "back.out(3)"}}, {t + 0.18:.3f});')
    js.append(f'tl.to("#qb{j}", {{backgroundColor: "#16a34a", borderColor: "#16a34a", duration: 0.1}}, {t + 0.18:.3f});')
    fx("tick", t + 0.18, 0.35)
OUT("#g-call2 .ptitle, #g-call2 .adrow", CA1 + 0.1)
FO0, FO1 = CA1 + 0.1, at("lastly")
add('<div class="fwrap"><div class="lead big" id="fl"><div class="lh">🔔 NEW LEAD</div><b>“Just looking for a price”</b><i>Not ready to buy</i></div><div class="fout" id="fout" data-layout-allow-overlap>FILTERED OUT</div></div>',
    "panel", "g-filter", FO0, FO1 - 0.02)
DIM.append((FO0, FO1)); POP("#fl", FO0); WH(FO0)
js.append(f'tl.fromTo("#fout", {{opacity: 0, scale: 2.6, rotation: -10}}, {{opacity: 1, scale: 1, rotation: -6, duration: 0.13, ease: "power4.in"}}, {at("tire kickers") - 0.06:.3f});')
fx("stamp", at("tire kickers") + 0.02, 0.4)
js.append(f'tl.to("#fl, #fout", {{x: 1500, rotation: 8, duration: 0.45, ease: "power3.in"}}, {at("ready to buy") - 0.2:.3f});'); fx("whip", at("ready to buy") - 1.0, 0.26)
# step 3
S3 = at("lastly"); step_card(3, S3, at("we book") - 0.3)
CL0, CL1 = at("we book") - 0.3, at("show up") - 0.05   # hold the calendar until the full-screen beat
days = ["MON", "TUE", "WED", "THU", "FRI"]
BK = [(0, 1, "Roof estimate · 9:00"), (2, 0, "Roof estimate · 8:30"), (1, 2, "Roof estimate · 1:00"), (3, 1, "Roof estimate · 10:30"), (4, 0, "Roof estimate · 9:30"), (2, 2, "Roof estimate · 3:00")]
grid = "".join(f'<div class="cd"><b>{d}</b>' + "".join(f'<div class="slot"></div>' for _ in range(3)) + '</div>' for d in days)
appts = "".join(f'<div class="appt" id="ap{k}" style="left:{30 + d * 156}px; top:{96 + s * 104}px">{html.escape(txt)}</div>' for k, (d, s, txt) in enumerate(BK))
add(f'<div class="ptitle" id="clt">STRAIGHT INTO <span class="y">YOUR CALENDAR</span></div><div class="cal"><div class="cgrid">{grid}</div>{appts}</div>'
    f'<div class="crm" id="crm">SYNCED TO CRM {E("✅")}</div>', "panel", "g-cal", CL0, CL1 - 0.05)
SLIDE.append((CL0, CL1)); POP("#clt", CL0); WH(CL0); POP("#g-cal .cal", CL0 + 0.1)
for k in range(len(BK)):
    t = CL0 + 0.45 + k * 0.42
    js.append(f'tl.fromTo("#ap{k}", {{opacity: 0, scale: 0.5}}, {{opacity: 1, scale: 1, duration: 0.16, ease: "back.out(3)"}}, {t:.3f});'); fx("ding", t, 0.2)
js.append(f'tl.fromTo("#crm", {{opacity: 0, scale: 2}}, {{opacity: 1, scale: 1, duration: 0.15, ease: "power4.in"}}, {at("crm") - 0.05:.3f});'); fx("pop", at("crm"), 0.35)
OUT("#g-cal .ptitle, #g-cal .cal, #crm", CL1 - 0.05)
SH0 = at("so all you")
add('<div class="kin xl"><span id="sh0">SHOW UP.</span> <span id="sh1">INSPECT.</span> <span id="sh2" class="y">CLOSE.</span></div>', "stage", "g-show", at("show up") - 0.05, at("one of our") - 0.05)
for j, t in enumerate((at("show up"), at("estimate"), at("close the sale"))): SNAP(f"#sh{j}", t, "scale: 2"); fx("blow", t, 0.26)
OUT("#g-show .kin", at("one of our") - 0.05); DIM.append((at("show up") - 0.05, at("one of our")))

# ======================= 5. PROOF =======================
P0 = at("one of our")
add(f'<div class="big y" id="rr">REAL RESULTS {E("💰")}</div>', "stage", "g-rr", P0, at("generated") - 0.05)
POP("#rr", P0, 0.26); WH(P0); OUT("#rr", at("generated") - 0.05); DIM.append((P0, at("generated")))
C1a, C1b = at("generated"), end("four million dollars")
C2a, C2b = at("five hundred thousand"), end("single month")
add('<div class="cnt"><div class="cl1" id="cn1">$0</div><div class="cs1" id="cs1">IN SALES</div><div class="cl2" id="cn2">$0</div><div class="cs2" id="cs2">BOOKED IN ONE MONTH</div></div>',
    "stage", "g-cnt", C1a, at("that's what happens") - 0.05)
DIM.append((C1a, at("that's what happens")))
POP("#cn1", C1a); POP("#cs1", C1a + 0.1); WH(C1a)
js.append(f'const c1 = {{v: 0}}; tl.fromTo(c1, {{v: 0}}, {{v: 4000000, duration: {C1b - C1a:.3f}, ease: "power2.out", onUpdate: () => {{ document.getElementById("cn1").textContent = "$" + (Math.round(c1.v / 1000) * 1000).toLocaleString("en-US"); }}}}, {C1a:.3f});')
for k in range(8): fx("count", C1a + (C1b - C1a) * k / 8, 0.2)
fx("kaching", C1b, 0.4); js.append(f'tl.fromTo("#cn1", {{scale: 1}}, {{scale: 1.12, duration: 0.1, yoyo: true, repeat: 1}}, {C1b:.3f});')
js.append(f'tl.to("#cn1, #cs1", {{scale: 0.62, y: -40, duration: 0.25, ease: "power2.inOut"}}, {C2a - 0.3:.3f});')
POP("#cn2", C2a); POP("#cs2", C2a + 0.1); WH(C2a)
js.append(f'const c2 = {{v: 0}}; tl.fromTo(c2, {{v: 0}}, {{v: 500000, duration: {C2b - C2a:.3f}, ease: "power2.out", onUpdate: () => {{ document.getElementById("cn2").textContent = "$" + (Math.round(c2.v / 1000) * 1000).toLocaleString("en-US"); }}}}, {C2a:.3f});')
for k in range(6): fx("count", C2a + (C2b - C2a) * k / 6, 0.2)
fx("kaching", C2b, 0.4); js.append(f'tl.fromTo("#cn2", {{scale: 1}}, {{scale: 1.12, duration: 0.1, yoyo: true, repeat: 1}}, {C2b:.3f});')
OUT("#g-cnt .cnt", at("that's what happens") - 0.05)
BC0 = at("this only works")
add('<div class="ycard" id="ycard">BUILT FOR ROOFERS WHO CAN CLOSE</div>', "panel", "g-close", BC0, at("if you do well") + 1.2)
POP("#ycard", BC0 + 0.05, 0.26); fx("blow", at("can close"), 0.32); OUT("#ycard", at("if you do well") + 1.2); DIM.append((BC0, at("if you do well") + 1.2))
BN0 = at("if you do well") + 1.2
add('<div class="kin mid"><div><span id="bn0">YOUR REAL BOTTLENECK:</span></div><div><span id="bn1" class="y">QUALIFIED APPOINTMENTS</span></div><div><span id="bn2">→ THIS IS BUILT FOR YOU</span></div></div>',
    "panel", "g-bottle", BN0, at("we only work") - 0.05)
SNAP("#bn0", at("bottleneck"), "y: 60"); SNAP("#bn1", at("qualified appointments"), "scale: 1.8"); SNAP("#bn2", at("this is built"), "x: 120")
WH(at("bottleneck")); fx("pop", at("qualified appointments"), 0.25); fx("ding", at("this is built"), 0.25)
OUT("#g-bottle .kin", at("we only work") - 0.05); DIM.append((BN0, at("we only work")))
MP0, MP1 = at("we only work"), at("so if you're")
REG = ["M60,40 L300,20 L340,190 L120,230 Z", "M300,20 L560,50 L540,210 L340,190 Z", "M560,50 L780,30 L800,240 L540,210 Z",
       "M120,230 L340,190 L360,400 L90,420 Z", "M340,190 L540,210 L560,420 L360,400 Z", "M540,210 L800,240 L780,430 L560,420 Z"]
paths = "".join(f'<path id="rg{k}" d="{d}" fill="{"#1f2937" if k != 4 else "#374151"}" stroke="#94a3b8" stroke-width="4"/>' for k, d in enumerate(REG))
add(f'<div class="ptitle" id="mpt"><span class="y">1 ROOFER</span> PER AREA</div><div class="map"><svg viewBox="0 0 860 460" width="760" height="406">{paths}</svg>'
    f'<div class="lock" id="lock">{E("🔒")}</div><div class="taken" id="taken">TAKEN</div></div><div class="gone r" id="gone">ONCE IT\'S TAKEN, IT\'S GONE.</div>', "panel", "g-map", MP0, MP1 - 0.05)
SLIDE.append((MP0, MP1)); POP("#mpt", MP0); WH(MP0); POP("#g-map .map", MP0 + 0.1)
js.append(f'tl.to("#rg4", {{fill: "#ffd60a", duration: 0.25}}, {at("one roofer per"):.3f});'); fx("pop", at("one roofer per"), 0.3)
js.append(f'tl.fromTo("#lock", {{opacity: 0, scale: 2.4, y: -40}}, {{opacity: 1, scale: 1, y: 0, duration: 0.18, ease: "back.out(3)"}}, {at("service area"):.3f});'); fx("gear", at("service area") + 0.05, 0.32)
js.append(f'tl.fromTo("#taken", {{opacity: 0, scale: 2.4, rotation: -14}}, {{opacity: 1, scale: 1, rotation: -10, duration: 0.13, ease: "power4.in"}}, {at("is taken") - 0.05:.3f});'); fx("stamp", at("is taken"), 0.36)
POP("#gone", at("it's gone")); fx("blow", at("it's gone"), 0.3)
OUT("#g-map .ptitle, #g-map .map, #gone", MP1 - 0.05)

# ======================= 7. ENDING =======================
fx("riser", at("scroll down") - 1.6, 0.34)
SG0 = at("so if you're")
AP = at("scroll down")
add(f'<div class="apply"><div class="apb" id="apb">APPLY BELOW {E("👇")}</div><svg class="arrow" id="arw" viewBox="0 0 120 150" width="110" height="138"><path d="M42 0h36v80h32L60 145 10 80h32z" fill="#ffd60a" stroke="#000" stroke-width="8" stroke-linejoin="round"/></svg>'
    '<div class="apl" id="apl">We\'ll check if your area is open</div></div>', "panel", "g-apply", AP, DUR)
flash(AP); fx("drop", AP, 0.28)
js.append(f'tl.fromTo("#apb", {{opacity: 0, scale: 2.2}}, {{opacity: 1, scale: 1, duration: 0.16, ease: "power4.in"}}, {AP - 0.06:.3f});')
POP("#arw", AP + 0.25); POP("#apl", at("check if your") - 0.4); fx("pop", at("check if your") - 0.4, 0.25)
n_p = int((DUR - AP - 0.5) / 0.5)
js.append(f'tl.fromTo("#apb", {{scale: 1}}, {{scale: 1.05, duration: 0.25, ease: "sine.inOut", yoyo: true, repeat: {n_p * 2 - 1}, immediateRender: false}}, {AP + 0.4:.3f});')
js.append(f'tl.fromTo("#arw", {{y: 0}}, {{y: 34, duration: 0.3, ease: "power2.in", yoyo: true, repeat: {int((DUR - AP - 0.6) / 0.3) - 1}, immediateRender: false}}, {AP + 0.5:.3f});')
DIM.append((AP, DUR))

# ======================= camera, grade, dim, slide =======================
EVT = sorted({0.0, *[w["start"] for i, w in enumerate(words) if i and re.search(r"[.?!]$", words[i - 1]["text"])]})
MV, last = [], -9
for t in EVT:
    if t - last >= 3.2: MV.append(t); last = t
NB_T = at("you're not broken")
MOVES = ["push", "pull", "driftL", "push", "driftR", "pull"]
for k, c0 in enumerate(MV):
    c1 = MV[k + 1] if k + 1 < len(MV) else DUR
    mv = "slowpush" if abs(c0 - NB_T) < 0.6 else MOVES[k % len(MOVES)]
    a, b = {"push": ("scale: 1, xPercent: 0", "scale: 1.07, xPercent: 0"), "pull": ("scale: 1.09, xPercent: 0", "scale: 1.0, xPercent: 0"),
            "driftL": ("scale: 1.06, xPercent: 1.2", "scale: 1.08, xPercent: -1.2"), "driftR": ("scale: 1.06, xPercent: -1.2", "scale: 1.08, xPercent: 1.2"),
            "slowpush": ("scale: 1, xPercent: 0", "scale: 1.16, xPercent: 0")}[mv]
    js.append(f'tl.fromTo("#cam", {{{a}}}, {{{b}, duration: {c1 - c0:.3f}, ease: "sine.inOut", immediateRender: {"true" if k == 0 else "false"}}}, {c0:.3f});')
KEY = ["change how", "new way", "same ads", "same exact", "competing on", "right message", "right homeowner", "right time", "one more thing", "serious about", "dead-end leads", "price shoppers", "ghost you", "pay attention", "low-intent", "race to the bottom", "sold to five", "the system is", "different one",
       "face to face", "within", "your calendar", "four million", "five hundred thousand", "one roofer per service area", "you don't pay", "apply"]
PUNCH = sorted({at(k) for k in KEY})
for t in PUNCH:
    js.append(f'tl.fromTo("#punch", {{scale: 1}}, {{scale: 1.15, duration: 0.16, ease: "power2.out", immediateRender: false}}, {t:.3f});')
    js.append(f'tl.to("#punch", {{scale: 1, duration: 0.45, ease: "power2.inOut"}}, {t + 0.16:.3f});')
    fx("wA", t - 0.07, 0.12)
G = {"base": "contrast(1.06) saturate(1.06) brightness(1.02)", "dark": "contrast(1.1) saturate(0.7) brightness(0.84)",
     "bright": "contrast(1.06) saturate(1.15) sepia(0.08) brightness(1.08)"}
js.append(f'tl.set("#grade", {{filter: "{G["base"]}"}}, 0);')
js.append(f'tl.to("#grade", {{filter: "{G["dark"]}", duration: 0.4}}, {at("you\'ve probably"):.3f});')
js.append(f'tl.set("#grade", {{filter: "{G["bright"]}"}}, {TU:.3f});')
# Three layouts only, never a blurred/darkened face:
#   talk  = my shot full frame, sharp, captions only
#   split = my shot in a rounded frame on the left, graphic on the right (dark background)
#   full  = shot hidden, graphic full screen on the dark background (voice keeps playing)
LAYOUT = [(0.0, "full"), (at("tired of"), "split"), (at("stop what"), "talk"), (PA, "full"), (at("what i'm") + 0.9, "talk"),
          (at("you've probably"), "split"), (at("here's what nobody"), "talk"), (at("most lead"), "split"), (NB, "full"),
          (TU, "split"), (at("if you run"), "talk"), (at("not by"), "split"), (at("show up") - 0.05, "full"),
          (at("that's what happens"), "talk"), (at("this only works"), "split"), (at("so if you're"), "talk"), (AP, "split")]
STATE = {"talk": "x: 0, y: 0, scale: 1, borderRadius: 0, opacity: 1", "split": "x: -440, y: -20, scale: 0.52, borderRadius: 54, opacity: 1",
         "full": "opacity: 0"}
js.append(f'tl.set("#slide", {{{STATE["full"]}}}, 0);')
prev = "full"
for t, mode in LAYOUT[1:]:
    if mode == "full":                                     # quick cut away from the shot
        js.append(f'tl.to("#slide", {{opacity: 0, duration: 0.12, ease: "power1.in"}}, {t - 0.06:.3f});')
    elif prev == "full":                                   # cut back in, already in place
        js.append(f'tl.set("#slide", {{{STATE[mode].replace(", opacity: 1", "")}}}, {t - 0.07:.3f});')
        js.append(f'tl.to("#slide", {{opacity: 1, duration: 0.12, ease: "power1.out"}}, {t - 0.07:.3f});')
    else:                                                  # quick slide between talk and split
        js.append(f'tl.to("#slide", {{{STATE[mode]}, duration: 0.35, ease: "power3.inOut"}}, {t - 0.18:.3f});')
    if mode != "full": fx("wB", t - 0.12, 0.12)
    prev = mode
fz = [f'<img class="clip freeze" id="fz{k}" src="{img}" alt="" data-start="{t:.3f}" data-duration="0.5" data-track-index="{4 + k}" />' for k, (t, img) in enumerate(FREEZE)]

# ======================= captions =======================
YEL = ["dead-end leads", "price shoppers", "pay attention", "race to the bottom", "the system is", "different one", "face to face", "within", "your calendar",
       "one roofer per service area", "a machine", "four million dollars", "five hundred thousand dollars", "you don't pay", "apply"]
RED = ["ghost you", "low-intent", "sold to five", "overpromise"]
color = {}
for lst, c in ((YEL, "y"), (RED, "r")):
    for p in lst:
        st = 0
        while True:
            try: ix = find(p, st)
            except SystemExit: break
            for i in ix: color[i] = c
            st = ix[-1] + 1
def disp(i): return re.sub(r"[.,?!]+$", "", words[i]["text"]).upper().replace("ANGIE", "ANGI")
groups, cur = [], []
for i, w in enumerate(words):
    if cur:
        prev = words[cur[-1]]
        if len(cur) >= 4 or (len(cur) >= 2 and re.search(r"[.,?!]$", prev["text"])) or re.search(r"[.?!]$", prev["text"]) or w["start"] - prev["end"] > 0.35:
            groups.append(cur); cur = []
    cur.append(i)
groups.append(cur)
def units(t): return sum(0.3 if c == " " else 0.32 if c in ".,'-?!" else 1.0 if c in "MW" else 0.42 if c in "I1" else 0.8 for c in t)
cap = []
for gi, g in enumerate(groups):
    s0 = words[g[0]]["start"]; nxt = words[groups[gi + 1][0]]["start"] if gi + 1 < len(groups) else DUR
    e0 = DUR if gi == len(groups) - 1 else min(nxt, words[g[-1]]["end"] + 0.4, DUR)
    ws = "".join(f'<span class="w" id="w{i}">{html.escape(disp(i))}</span>' for i in g)
    em = sum(units(disp(i)) for i in g) + 0.3 * (len(g) - 1)
    fs = int(min(66, 1500 / 1.12 / em))
    cap.append(f'<div class="cg" id="cg{gi}"><div class="line" style="font-size:{fs}px">{ws}</div></div>')
    js.append(f'tl.fromTo("#cg{gi}", {{opacity: 0, scale: 0.88}}, {{opacity: 1, scale: 1, duration: 0.08, ease: "power2.out"}}, {s0:.3f});')
    for i in g:
        col = {"y": "#ffd60a", "r": "#ff3b30"}.get(color.get(i), "#ffffff")
        js.append(f'tl.fromTo("#w{i}", {{opacity: 0.55, scale: 1, color: "#ffffff"}}, {{opacity: 1, scale: 1.1, color: "{col}", duration: 0.07}}, {words[i]["start"]:.3f});')
        js.append(f'tl.to("#w{i}", {{scale: 1, duration: 0.1}}, {max(words[i]["start"] + 0.07, words[i]["end"]):.3f});')
    js.append(f'tl.set("#cg{gi}", {{opacity: 0, visibility: "hidden"}}, {e0:.3f});')

aud = []
for n, (k, t, v, d) in enumerate(sorted(sfx, key=lambda x: x[1])):
    f = f"assets/sfx/{k}.wav"
    aud.append(f'<audio id="fx{n}" src="{f}" data-start="{t:.3f}" data-duration="{min(d or probe(f), DUR - t):.3f}" data-track-index="{40 + n}" data-volume="{v}"></audio>')

CSS = open("tools/style.css").read()
nl = "\n      "
doc = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <title>Roofer VSL</title>
    <script src="vendor/gsap.min.js"></script>
    <style>
{CSS}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="{W}" data-height="{H}" data-duration="{DUR}">
      <div id="bgpanel"></div>
      <div id="slide"><div id="cam"><div id="punch"><div id="shake"><div id="soft"><div id="grade">
        <video id="src" class="clip" src="assets/base.mp4" muted playsinline data-start="0" data-duration="{DUR}" data-track-index="0"></video>
        {nl.join(fz)}
      </div></div></div></div></div></div>
      <div id="vignette"></div>
      {nl.join(el)}
      <div id="captions" class="clip" data-start="0" data-duration="{DUR}" data-track-index="30">
        {nl.join(cap)}
      </div>
      <div id="flash"></div>
    </div>
    <audio id="vo" src="assets/vo.wav" data-start="0" data-duration="{DUR}" data-track-index="1" data-volume="1"></audio>
    <audio id="music" src="assets/music_bed.wav" data-start="0" data-duration="{DUR}" data-track-index="2" data-volume="1"></audio>
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
gr = sorted([float(re.search(r'data-start="([\d.]+)"', e).group(1)) for e in el] + PUNCH + [t for _, t, _, _ in sfx])
gaps = [(round(a, 2), round(b - a, 2)) for a, b in zip([0.0] + gr, gr + [DUR]) if b - a > 3.5]
print(f"{DUR}s · {len(el)} graphics · {len(PUNCH)} punches · {len(groups)} captions · {len(sfx)} sfx · layout switches {len(LAYOUT) - 1} · gaps>3.5s: {gaps or 'none'}")
# layout check: a split screen must never show an empty right panel
pan = sorted((float(a), float(a) + float(b)) for a, b in re.findall(r'class="clip panel" id="[^"]+" data-start="([\d.]+)" data-duration="([\d.]+)"', "".join(el)))
empty = []
for k, (t, mode) in enumerate(LAYOUT):
    if mode != "split": continue
    t1 = LAYOUT[k + 1][0] if k + 1 < len(LAYOUT) else DUR
    cur = t
    for a, b in pan:
        if b <= cur or a >= t1: continue
        if a - cur > 0.3: empty.append((round(cur, 2), round(a - cur, 2)))
        cur = max(cur, b)
    if t1 - cur > 0.3: empty.append((round(cur, 2), round(t1 - cur, 2)))
print("empty split panels:", empty or "none")
