"""Overlay composition (HyperFrames: HTML + GSAP, rendered frame-exact) for the High Roof Partners ad.
The plate from work/look.py sits underneath; everything here is graphics, captions and the end card.

  gen.py 45   -> remotion/f45/index.html   (1080x1350 feed)
  gen.py 916  -> remotion/f916/index.html  (1080x1920 Reels: no text in the top 14 % / bottom 20 %, captions above y 1500)
Also writes work/sfx_<fmt>.json (cue list for mix.py)."""
import html, json, os, re, shutil, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
FMT = sys.argv[1] if len(sys.argv) > 1 else "45"
plan = json.load(open("work/plan.json")); DUR = plan["dur"]; G = plan["gfx"]; CARDS = {c[0]: (c[1], c[2]) for c in plan["cards"]}
W = 1080
if FMT == "45":
    H = 1350
    Z = dict(top=26, cap=891, hook=975, name=1238, low=1050, strip0=1100, strip1=1350, safe0=0, safe1=1350, card_mid=675)
else:
    H = 1920
    Z = dict(top=290, cap=1195, hook=1240, name=1412, low=1335, strip0=1280, strip1=1660, safe0=280, safe1=1500, card_mid=890)
NAVY, ORANGE, YELLOW = "#0F1B2D", "#FF7A1A", "#FFD400"
el, js, sfx = [], [], []
def fx(name, t, vol): sfx.append((name, round(max(0.0, t), 3), vol))
def clip(gid, t0, t1, inner, track, style=""):
    el.append(f'<div class="clip g" id="{gid}" data-start="{t0:.3f}" data-duration="{t1 - t0:.3f}" data-track-index="{track}" style="{style}">{inner}</div>')
def spring_in(sel, t, frm="y: 40", d=0.27):   # ~8 frames, ease-out spring
    js.append(f'tl.fromTo("{sel}", {{opacity: 0, {frm}}}, {{opacity: 1, {re.sub(r"-?[0-9.]+", "0", frm) if "scale" not in frm else "scale: 1"}, duration: {d}, ease: "back.out(1.7)"}}, {t:.3f});')
def fade_out(sel, t, d=0.2): js.append(f'tl.to("{sel}", {{opacity: 0, duration: {d}, ease: "power2.in"}}, {t - d:.3f});')

# ---------------- 1. top banner: ATTENTION NC ROOFERS ----------------
a, b = G["banner"]
clip("g-banner", a, b, '<div class="banner" id="banner"><span class="siren" id="siren">🚨</span>ATTENTION NC ROOFERS<span class="siren s2">🚨</span></div>', 20,
     f"top:{Z['top']}px")
js.append(f'tl.fromTo("#banner", {{y: -160}}, {{y: 0, duration: 0.3, ease: "back.out(1.6)", immediateRender: true}}, 0);')
js.append('tl.fromTo("#g-banner .siren", {scale: 1}, {scale: 1.25, duration: 0.18, yoyo: true, repeat: 11, ease: "sine.inOut", immediateRender: false}, 0.1);')
fade_out("#banner", b); fx("whoosh", 0.0, 0.10)

# ---------------- 2/3. hook text + name tag ----------------
a, b = G["hook5to10"]
clip("g-hook", a, b, '<div class="hook" id="hook">5 TO 10 ROOFS<br><span class="y">A MONTH?</span></div>', 21, f"top:{Z['hook']}px")
js.append(f'tl.fromTo("#hook", {{opacity: 0, scale: 2.2}}, {{opacity: 1, scale: 1, duration: 0.22, ease: "back.out(2.4)"}}, {a:.3f});')
js.append(f'tl.to("#hook", {{scale: 0.62, y: 60, duration: 0.25, ease: "power2.inOut"}}, {a + 1.15:.3f});')
fade_out("#hook", b, 0.12); fx("pop", a, 0.22)
a, b = G["nametag"]
clip("g-name", a, b, '<div class="name" id="name"><b>PARTH</b><i>|</i><span>HIGH ROOF PARTNERS</span><u id="nameline"></u></div>', 22, f"top:{Z['name']}px")
js.append(f'tl.fromTo("#name", {{opacity: 0, x: -420}}, {{opacity: 1, x: 0, duration: 0.3, ease: "back.out(1.4)"}}, {a:.3f});')
js.append(f'tl.fromTo("#nameline", {{scaleX: 0}}, {{scaleX: 1, duration: 0.35, ease: "power3.out"}}, {a + 0.25:.3f});')
fade_out("#name", b, 0.12); fx("whoosh", a - 0.05, 0.08)

# ---------------- full-screen cards ----------------
def card(gid, inner, sfx_in=True):
    a, b = CARDS[gid]
    clip(f"c-{gid}", a, b, f'<div class="card" id="cd-{gid}"><div class="cin" style="top:{Z["card_mid"]}px">{inner}</div></div>', 30)
    prev_card = any(abs(cb - a) < 0.02 for g2, ca, cb in plan["cards"] if g2 != gid)
    if prev_card:   # card follows a card: content is there on the first frame (no empty navy frames), just a small settle
        js.append(f'tl.fromTo("#cd-{gid} .cin", {{opacity: 1, scale: 0.94}}, {{opacity: 1, scale: 1, duration: 0.2, ease: "back.out(1.8)"}}, {a:.3f});')
    else:
        js.append(f'tl.fromTo("#cd-{gid} .cin", {{opacity: 0, scale: 0.86}}, {{opacity: 1, scale: 1, duration: 0.22, ease: "back.out(1.8)"}}, {a:.3f});')
    if sfx_in: fx("whoosh", a - 0.06, 0.12)
    return a, b

# 4. trash: lid opens, lead cards fall in
a, b = card("trash", '<svg class="trash" viewBox="0 0 400 420" width="400" height="420">'
            '<g id="lead1"><rect x="150" y="-40" width="100" height="64" rx="10" fill="#fff"/><text x="200" y="0" text-anchor="middle" class="svgt">LEAD</text></g>'
            '<g id="lead2"><rect x="150" y="-40" width="100" height="64" rx="10" fill="#fff"/><text x="200" y="0" text-anchor="middle" class="svgt">LEAD</text></g>'
            '<g id="lead3"><rect x="150" y="-40" width="100" height="64" rx="10" fill="#fff"/><text x="200" y="0" text-anchor="middle" class="svgt">LEAD</text></g>'
            '<path d="M90 150 L120 400 H280 L310 150 Z" fill="#8A94A6"/><path d="M150 190 L160 370 M200 190 V370 M250 190 L240 370" stroke="#5B6474" stroke-width="12" stroke-linecap="round"/>'
            '<g id="lid"><rect x="70" y="112" width="260" height="34" rx="12" fill="#A9B2C3"/><rect x="170" y="92" width="60" height="26" rx="8" fill="#A9B2C3"/></g></svg>'
            '<div class="ct">SHARED LEADS <span class="o">= TRASH</span></div>')
js.append(f'tl.fromTo("#lid", {{rotation: 0, transformOrigin: "70px 146px"}}, {{rotation: -38, duration: 0.25, ease: "back.out(2)"}}, {a + 0.1:.3f});')
for k in range(3):
    t = a + 0.3 + k * 0.18
    js.append(f'tl.fromTo("#lead{k + 1}", {{y: -120, x: {(k - 1) * 60}, rotation: {(k - 1) * 25}, opacity: 0}}, {{y: 250, x: 0, rotation: {(1 - k) * 40}, opacity: 1, duration: 0.32, ease: "power2.in"}}, {t:.3f});')
    js.append(f'tl.to("#lead{k + 1}", {{opacity: 0, duration: 0.05}}, {t + 0.32:.3f});')
js.append(f'tl.to("#lid", {{rotation: 0, duration: 0.18, ease: "power2.in"}}, {a + 0.95:.3f});'); fx("thud", a + 1.0, 0.10)

# 5a. pay only when you sit down
card("sitdown", '<div class="ct big">YOU ONLY PAY</div><div class="ct">WHEN YOU SIT DOWN</div><div class="ct y">&amp; GIVE AN ESTIMATE</div>')
# 5b. high-intent homeowners
card("intent", '<div class="ct big">HIGH-INTENT</div><div class="ct big y">HOMEOWNERS</div>')
# 5c. no retainers chip (lower zone)
a, b = G["noret"]
clip("g-noret", a, b, '<div class="chip orange" id="noret">NO MONTHLY RETAINERS ✓</div>', 23, f"top:{Z['low']}px")
spring_in("#noret", a, "scale: 0.6"); fade_out("#noret", b, 0.12); fx("pop", a, 0.20)
# 5d. NO ESTIMATE = NO PAY slam, then pinned top-centre chip + NO RETAINERS sub chip
a, b = card("noest", '<div class="ct huge" id="ne1">NO ESTIMATE</div><div class="ct huge y" id="ne2">= NO PAY</div>', sfx_in=False)
js.append(f'tl.fromTo("#ne1, #ne2", {{scale: 2.4, opacity: 0}}, {{scale: 1, opacity: 1, duration: 0.2, ease: "back.out(2.2)", stagger: 0.12}}, {a:.3f});'); fx("thud", a + 0.12, 0.08); fx("pop", a + 0.25, 0.16)
pa, pb = G["pinned"]
clip("g-pinned", pa, pb, '<div class="pin" id="pin"><div class="pmain">NO ESTIMATE = <span class="y">NO PAY</span></div><div class="psub">NO RETAINERS</div></div>', 24, f"top:{Z['top']}px")
js.append(f'tl.fromTo("#pin", {{opacity: 0, y: -40, scale: 1.3}}, {{opacity: 1, y: 0, scale: 1, duration: 0.3, ease: "back.out(1.6)"}}, {pa:.3f});'); fade_out("#pin", pb, 0.15)
# exclusive chip
a, b = G["exclusive"]
clip("g-excl", a, b, '<div class="chip yellow" id="excl">EXCLUSIVE TO YOU</div>', 23, f"top:{Z['low']}px")
spring_in("#excl", a, "scale: 0.6"); fade_out("#excl", b, 0.12); fx("pop", a, 0.20)
# 8. phone: we call every homeowner
a, b = card("phone", '<svg class="phone" viewBox="0 0 300 420" width="300" height="420" id="phonesvg">'
            '<circle id="ring1" cx="150" cy="190" r="120" fill="none" stroke="#FF7A1A" stroke-width="8" opacity="0"/>'
            '<circle id="ring2" cx="150" cy="190" r="120" fill="none" stroke="#FF7A1A" stroke-width="8" opacity="0"/>'
            '<rect x="85" y="40" width="130" height="300" rx="26" fill="#1E2A3F" stroke="#fff" stroke-width="8"/>'
            '<circle cx="150" cy="250" r="34" fill="#22C55E"/><path d="M133 238c6 14 14 22 28 28l8-8c2-2 5-2 7-1l12 5c3 1 4 4 3 7l-3 10c-1 3-4 5-7 5-34-3-61-30-64-64 0-3 2-6 5-7l10-3c3-1 6 0 7 3l5 12c1 2 1 5-1 7z" fill="#fff" transform="translate(-6 -10) scale(0.6) translate(100 165)"/>'
            '</svg><div class="ct">WE CALL EVERY <span class="y">HOMEOWNER</span></div>')
for k, rid in enumerate(("ring1", "ring2")):
    js.append(f'tl.fromTo("#{rid}", {{attr: {{r: 100}}, opacity: 0.9}}, {{attr: {{r: 200}}, opacity: 0, duration: 0.6, ease: "power1.out", repeat: 1}}, {a + 0.1 + k * 0.3:.3f});')
js.append(f'tl.fromTo("#phonesvg", {{rotation: -4}}, {{rotation: 4, duration: 0.06, yoyo: true, repeat: 9, ease: "none", immediateRender: false}}, {a + 0.1:.3f});')
# 7. calendar: 9 free-estimate slots fill one by one, counter to 9, EXAMPLE label
a, b = CARDS["calendar"]
times = ["9 AM", "1 PM", "4 PM", "10 AM", "2 PM", "5 PM", "11 AM", "3 PM", "6 PM"]
slots = "".join(f'<div class="slot" id="sl{k}"><span>{t}</span></div>' for k, t in enumerate(times))
card("calendar", '<div class="cal"><div class="calh">MON<span>TUE</span>WED</div>'
     f'<div class="grid">{slots}</div></div><div class="ct">FREE ESTIMATES: <span class="y" id="cnt">0</span></div><div class="ex">EXAMPLE</div>')   # illustrative, not a result
order = [0, 3, 6, 1, 4, 7, 2, 5, 8]
for n, k in enumerate(order):
    t = a + 0.18 + n * 0.12
    js.append(f'tl.fromTo("#sl{k}", {{backgroundColor: "rgba(255,255,255,0.08)", scale: 0.7}}, {{backgroundColor: "{ORANGE}", scale: 1, duration: 0.12, ease: "back.out(2)", immediateRender: false}}, {t:.3f});')
    js.append(f'tl.set("#cnt", {{textContent: "{n + 1}"}}, {t:.3f});')
    fx("tick", t, 0.10)
fx("ding", a + 0.18 + 8 * 0.12 + 0.05, 0.12)
# 6. WE BOOK. YOU CLOSE.
a, b = G["webook"]
clip("g-webook", a, b, '<div class="webook" id="webook">WE BOOK. <span class="y">YOU CLOSE.</span><u id="wbline"></u></div>', 23, f"top:{Z['low']}px")
spring_in("#webook", a, "scale: 0.7"); js.append(f'tl.fromTo("#wbline", {{scaleX: 0}}, {{scaleX: 1, duration: 0.3, ease: "power3.out"}}, {a + 0.2:.3f});')
fade_out("#webook", b, 0.12); fx("whoosh", a - 0.05, 0.09)
# 9/10. lower navy strip (also hides the old red banner), NC map, ONLY 1 ROOFER PER AREA
a, b = G["strip"]
clip("g-strip", a, b, f'<div class="strip" style="top:{Z["strip0"]}px;height:{Z["strip1"] - Z["strip0"]}px"></div>', 25)
js.append(f'tl.fromTo("#g-strip .strip", {{opacity: 0}}, {{opacity: 1, duration: 0.1}}, {a:.3f});')
a, b = G["ncmap"]
NC = "M8 70 L60 52 L120 50 L180 40 L260 30 L340 22 L420 14 L470 8 L478 30 L462 52 L440 70 L410 96 L370 110 L330 104 L300 122 L250 120 L205 104 L160 104 L120 98 L70 104 L30 112 L12 100 Z"
pins = "".join(f'<g id="pin{k}"><circle cx="{x}" cy="{y}" r="12" fill="{ORANGE}"/><circle class="pulse" cx="{x}" cy="{y}" r="12" fill="none" stroke="{ORANGE}" stroke-width="4"/></g>'
               for k, (x, y) in enumerate(((175, 92), (330, 62), (262, 54))))   # Charlotte, Raleigh, Greensboro (approx.)
clip("g-nc", a, b, f'<div class="nc" id="nc"><svg viewBox="0 0 490 130" width="420" height="111"><path d="{NC}" fill="#1E2A3F" stroke="#fff" stroke-width="5" stroke-linejoin="round"/>{pins}</svg>'
     '<div class="nct">NORTH CAROLINA<br><span class="y">ONLY</span></div></div>', 26, f"top:{Z['strip0'] + 28}px")
spring_in("#nc", a, "y: 40"); js.append(f'tl.fromTo("#g-nc .pulse", {{attr: {{r: 12}}, opacity: 1}}, {{attr: {{r: 34}}, opacity: 0, duration: 0.5, repeat: 2, stagger: 0.12}}, {a + 0.1:.3f});')
fade_out("#nc", b, 0.1); fx("whoosh", a - 0.05, 0.09)
a, b = G["oneroofer"]
clip("g-one", a, b, '<div class="one" id="one"><svg viewBox="0 0 24 24" width="62" height="62"><path d="M7 10V7a5 5 0 0 1 10 0v3" fill="none" stroke="#0F1B2D" stroke-width="2.6"/><rect x="4.5" y="10" width="15" height="11" rx="2.5" fill="#0F1B2D"/></svg>ONLY 1 ROOFER PER AREA</div>', 26,
     f"top:{Z['strip0'] + 40}px")
js.append(f'tl.fromTo("#one", {{opacity: 0, scale: 2.2}}, {{opacity: 1, scale: 1, duration: 0.2, ease: "power4.in"}}, {a - 0.1:.3f});'); fx("thud", a + 0.08, 0.14)
fade_out("#one", b, 0.1)

# ---------------- 8. end card ----------------
a, b = CARDS["end"]
clip("c-end", a, b, f'<div class="card end" id="cd-end"><div class="cin" style="top:{Z["card_mid"] - 40}px">'
     '<div class="wm">HIGH ROOF <span class="o">PARTNERS</span></div><div class="tap" id="tap">TAP SEND<br>MESSAGE</div>'
     '<div class="sub">Only 1 roofer per area.<br>Check if yours is open.</div></div>'
     f'<svg class="arrow" id="arw" viewBox="0 0 120 150" width="110" height="138" style="top:{(1180 if FMT == "45" else 1380)}px"><path d="M42 0h36v80h32L60 145 10 80h32z" fill="{ORANGE}"/></svg></div>', 31)
js.append(f'tl.fromTo("#cd-end", {{opacity: 0}}, {{opacity: 1, duration: 0.2}}, {a:.3f});')
js.append(f'tl.fromTo("#cd-end .cin", {{scale: 0.9}}, {{scale: 1, duration: 0.3, ease: "back.out(1.6)"}}, {a:.3f});')
js.append(f'tl.fromTo("#arw", {{y: 0}}, {{y: 30, duration: 0.32, ease: "power2.in", yoyo: true, repeat: {int((b - a - 0.4) / 0.32)}, immediateRender: false}}, {a + 0.3:.3f});')
fx("whoosh", a - 0.06, 0.12); fx("ding", a + 0.3, 0.08)

# ---------------- captions (word-by-word) ----------------
HIDE = [(ca, cb) for _, ca, cb in plan["cards"]] + [(G["hook5to10"][0], G["hook5to10"][0] + 1.2)]
CUTS_T = [sg["T"] + 0.02 for sg in json.load(open("work/timeline.json"))["segs"][1:]]
KEY = {"ESTIMATE", "ESTIMATES", "PAY", "EXCLUSIVE", "FREE", "ONE", "ROOFING"}
FIX = {"angi": "ANGI", "roofers": "ROOFERS"}
ws = []
for w in plan["words"]:
    t = re.sub(r"^-", "", w["text"]).strip()
    ws.append(dict(w, d=t.upper().strip(",.?!")))
words = []   # join whisper's split hyphen words ("high", "-intent")
for w in ws:
    if w["text"].startswith("-") and words: words[-1]["d"] += "-" + w["d"]; words[-1]["te"] = w["te"]
    else: words.append(dict(w))
def em(s): return sum(0.40 if c == " " else 0.36 if c in ",.'-?!" else 0.95 if c in "MW" else 0.36 if c in "I1" else 0.74 for c in s)
groups, cur = [], []
for k, w in enumerate(words):
    if cur:
        prev = words[cur[-1]]
        if len(cur) >= 3 or re.search(r"[.,?!]$", prev["text"]) or w["t"] - prev["te"] > 0.25 or any(prev["t"] < ca <= w["t"] + 0.05 for ca, _ in HIDE) \
                or any(prev["t"] < c - 0.01 <= w["t"] for c in CUTS_T):   # never span a jump cut
            groups.append(cur); cur = []
    cur.append(k)
groups.append(cur)
cap, CAPW = [], 900
for gi, g in enumerate(groups):
    t0 = words[g[0]]["t"] - 2 / 30
    t1 = words[groups[gi + 1][0]]["t"] - 2 / 30 if gi + 1 < len(groups) else plan["end0"]
    t1 = min(t1, words[g[-1]]["te"] + 0.5)
    # hide under cards
    for ca, cb in HIDE:
        if ca <= t0 < cb: t0 = cb
        if t0 < ca < t1: t1 = ca
    if t1 - t0 < 0.1: continue
    txt = [words[k]["d"] for k in g]
    lines = [g] if em(" ".join(txt)) * 68 <= CAPW else [g[:max(1, len(g) // 2 + len(g) % 2)], g[max(1, len(g) // 2 + len(g) % 2):]]
    fs = min(68, int(CAPW / max(em(" ".join(words[k]["d"] for k in ln)) for ln in lines)))
    body = "".join("<div>" + " ".join(f'<span class="w{" key" if words[k]["d"] in KEY else ""}" id="w{k}">{html.escape(words[k]["d"])}</span>' for k in ln) + "</div>" for ln in lines)
    cap.append(f'<div class="cg" id="cg{gi}" style="font-size:{fs}px">{body}</div>')
    js.append(f'tl.set("#cg{gi}", {{opacity: 1}}, {t0:.3f}); tl.set("#cg{gi}", {{opacity: 0}}, {t1:.3f});')
    for k in g:
        a = max(t0, words[k]["t"] - 2 / 30); bb = max(a + 0.08, min(words[k]["te"], t1))
        base = YELLOW if words[k]["d"] in KEY else "#ffffff"
        js.append(f'tl.fromTo("#w{k}", {{color: "{base}", scale: 1}}, {{color: "{YELLOW}", scale: 1.1, duration: 0.05, immediateRender: false}}, {a:.3f});')
        js.append(f'tl.to("#w{k}", {{color: "{base}", scale: 1, duration: 0.05}}, {bb:.3f});')

CSS = f"""
      @font-face {{ font-family: "Montserrat"; font-weight: 800; src: url("vendor/montserrat-latin-800-normal.woff2") format("woff2"); }}
      @font-face {{ font-family: "Montserrat"; font-weight: 900; src: url("vendor/montserrat-latin-900-normal.woff2") format("woff2"); }}
      @font-face {{ font-family: "Noto Color Emoji"; src: url("vendor/NotoColorEmoji.ttf") format("truetype"); }}
      body {{ margin: 0; background: #000; }}
      #root {{ position: relative; width: {W}px; height: {H}px; overflow: hidden; background: {NAVY}; font-family: "Montserrat", "Noto Color Emoji", sans-serif; font-weight: 900; color: #fff; }}
      #plate {{ position: absolute; inset: 0; width: {W}px; height: {H}px; }}
      .g {{ position: absolute; left: 0; right: 0; display: flex; justify-content: center; }}
      .y {{ color: {YELLOW}; }} .o {{ color: {ORANGE}; }}
      .banner {{ display: flex; align-items: center; gap: 18px; padding: 14px 34px 12px; border-radius: 16px; background: #E01E26; font-size: 62px; letter-spacing: 1px; box-shadow: 0 10px 28px rgba(0,0,0,0.45); white-space: nowrap; }}
      .siren {{ font-family: "Noto Color Emoji", sans-serif; display: inline-block; font-size: 58px; }}
      .hook {{ font-size: 96px; line-height: 1.02; text-align: center; white-space: nowrap; -webkit-text-stroke: 10px #000; paint-order: stroke fill; text-shadow: 0 8px 18px rgba(0,0,0,0.5); opacity: 0; }}
      .name {{ position: absolute; left: 60px; display: flex; align-items: baseline; gap: 14px; padding: 16px 28px 20px; border-radius: 14px; background: rgba(15,27,45,0.94); font-size: 56px; white-space: nowrap; opacity: 0; }}
      .name i {{ font-style: normal; color: {ORANGE}; }} .name span {{ font-weight: 800; }}
      .name u {{ position: absolute; left: 28px; right: 28px; bottom: 8px; height: 7px; border-radius: 4px; background: {ORANGE}; transform-origin: 0 50%; }}
      .chip {{ padding: 16px 34px 14px; border-radius: 999px; font-size: 60px; white-space: nowrap; box-shadow: 0 10px 26px rgba(0,0,0,0.45); opacity: 0; }}
      .chip.orange {{ background: {ORANGE}; color: {NAVY}; }} .chip.yellow {{ background: {YELLOW}; color: {NAVY}; }}
      .pin {{ display: flex; flex-direction: column; align-items: center; gap: 8px; opacity: 0; }}
      .pmain {{ padding: 12px 30px 10px; border-radius: 14px; background: {NAVY}; border: 4px solid {YELLOW}; font-size: 58px; white-space: nowrap; }}
      .psub {{ padding: 6px 22px 4px; border-radius: 999px; background: {ORANGE}; color: {NAVY}; font-size: 56px; white-space: nowrap; }}
      .card {{ position: absolute; inset: 0; background: radial-gradient(ellipse at 50% 40%, #1B2C47 0%, {NAVY} 70%); }}
      .cin {{ position: absolute; left: 50px; right: 50px; transform: translateY(-50%); display: flex; flex-direction: column; align-items: center; gap: 18px; text-align: center; }}
      .ct {{ font-size: 76px; line-height: 1.05; }} .ct.big {{ font-size: 100px; }} .ct.huge {{ font-size: 128px; line-height: 1.0; }}
      .svgt {{ font-family: "Montserrat"; font-weight: 900; font-size: 30px; fill: {NAVY}; }}
      .cal {{ width: 960px; padding: 22px; border-radius: 26px; background: rgba(255,255,255,0.07); border: 4px solid rgba(255,255,255,0.25); }}
      .calh {{ display: flex; justify-content: space-around; font-size: 56px; color: {ORANGE}; margin-bottom: 14px; }}
      .grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }}
      .slot {{ height: 104px; border-radius: 16px; background: rgba(255,255,255,0.08); display: flex; align-items: center; justify-content: center; font-size: 56px; }}
      .ex {{ padding: 6px 18px 4px; border-radius: 10px; border: 3px solid #fff; font-size: 56px; }}
      .webook {{ position: relative; font-size: 84px; white-space: nowrap; -webkit-text-stroke: 9px #000; paint-order: stroke fill; text-shadow: 0 8px 18px rgba(0,0,0,0.5); opacity: 0; }}
      .webook u {{ position: absolute; left: 0; right: 0; bottom: -12px; height: 10px; border-radius: 5px; background: {YELLOW}; transform-origin: 0 50%; }}
      .strip {{ position: absolute; left: 0; right: 0; background: {NAVY}; box-shadow: 0 -60px 50px -10px rgba(15,27,45,0.85); opacity: 0; }}
      .nc {{ display: flex; align-items: center; gap: 30px; opacity: 0; }}
      .nct {{ font-size: 60px; line-height: 1.05; }}
      .one {{ display: flex; align-items: center; gap: 18px; padding: 22px 40px 20px; border-radius: 22px; background: {ORANGE}; color: {NAVY}; font-size: 66px; white-space: nowrap; box-shadow: 0 12px 30px rgba(0,0,0,0.5); opacity: 0; }}
      .end {{ background: {NAVY}; opacity: 0; }}
      .wm {{ font-size: 64px; letter-spacing: 2px; padding-bottom: 12px; border-bottom: 8px solid {ORANGE}; }}
      .tap {{ font-size: 124px; line-height: 1.0; color: {YELLOW}; margin-top: 30px; }}
      .sub {{ font-size: 56px; line-height: 1.2; font-weight: 800; margin-top: 10px; }}
      .arrow {{ position: absolute; left: 485px; }}
      #captions {{ position: absolute; left: 90px; right: 90px; top: {Z['cap'] - 110}px; height: 220px; }}
      .cg {{ position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; opacity: 0; line-height: 1.12; }}
      .cg div {{ display: flex; gap: 0 0.58em; white-space: nowrap; }}
      .w {{ display: inline-block; color: #fff; -webkit-text-stroke: 6px #000; paint-order: stroke fill; text-shadow: 0 6px 14px rgba(0,0,0,0.6); }}
      .w.key {{ color: {YELLOW}; }}"""
nl = "\n      "
doc = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <title>High Roof Partners Ad {FMT}</title>
    <script src="vendor/gsap.min.js"></script>
    <style>{CSS}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="{W}" data-height="{H}" data-duration="{DUR:.3f}">
      <video id="plate" class="clip" src="assets/plate.mp4" muted playsinline data-start="0" data-duration="{DUR:.3f}" data-track-index="0"></video>
      {nl.join(el)}
      <div id="captions" class="clip" data-start="0" data-duration="{DUR:.3f}" data-track-index="40">
        {(nl + "  ").join(cap)}
      </div>
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      {nl.join(js)}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
OUT = f"remotion/f{FMT}"
os.makedirs(f"{OUT}/assets", exist_ok=True)
if not os.path.exists(f"{OUT}/vendor"): shutil.copytree("remotion/vendor", f"{OUT}/vendor")
shutil.copy(f"work/plate_{FMT}.mp4", f"{OUT}/assets/plate.mp4")
for f in ("package.json", "hyperframes.json"): shutil.copy(f"remotion/{f}", f"{OUT}/{f}")
json.dump({"id": f"hrp-ad1-{FMT}"}, open(f"{OUT}/meta.json", "w"))
if FMT == "916": doc = doc.replace("</style>", "  .hook { font-size: 80px; }\n    </style>", 1)   # Reels: shorter lower zone
open(f"{OUT}/index.html", "w").write(doc)
json.dump(sfx, open(f"work/sfx_{FMT}.json", "w"))
print(f"{FMT}: {W}x{H}, {DUR:.2f}s, {len(el)} graphics, {len(cap)} caption groups, {len(sfx)} sfx")
