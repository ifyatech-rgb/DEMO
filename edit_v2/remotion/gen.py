"""High Roof Partners ad 1 v2: NO cut, NO crop. The source's speaker pane (work/pane_look.mp4, 1080x928, graded,
background softened) sits unscaled on a navy canvas; everything else is built on top:
header zone (wordmark + rotating claim chips), animated b-roll scenes (type A: fills the pane + speaker bubble,
type B: rounded card beside/below his face), motion graphics, word-by-word captions, end card.

  gen.py 45   -> remotion/f45/index.html   (1080x1350)
  gen.py 916  -> remotion/f916/index.html  (1080x1920; text only between y 269 and 1536)
Also writes work/sfx.json (cue list for mix.py) and work/plan.json (b-roll / graphics windows for QA)."""
import html, json, os, re, shutil, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
FMT = sys.argv[1] if len(sys.argv) > 1 else "45"
L = json.load(open("logs/layout.json")); DUR = 39.3; W = 1080
if FMT == "45":
    H, PY = 1350, L["speaker_pane"]["y"]                      # pane back at its source position
    Z = dict(wm=22, chips=96, cap=PY + 928 + 105, end=(300, 1290))
else:
    H, PY = 1920, 396
    Z = dict(wm=276, chips=330, cap=PY + 928 + 106, end=(420, 1500))
PH = 928
NAVY, ORANGE, YELLOW = "#0F1B2D", "#FF7A1A", "#FFD400"
words = json.load(open("work/transcript.json"))
def clean(t): return re.sub(r"[^a-z0-9'$-]", "", t.lower()).strip("-")
def at(p, after=0.0):
    toks = [clean(x) for x in p.split()]
    for i in range(len(words)):
        if words[i]["start"] >= after - 1e-6 and [clean(w["text"]) for w in words[i:i + len(toks)]] == toks: return words[i]["start"]
    raise SystemExit(f"not found: {p}")

el, js, sfx = [], [], []
def fx(name, t, vol): sfx.append((name, round(max(0.0, t), 3), vol))
def clip(gid, t0, t1, inner, track, cls="", style=""):
    el.append(f'<div class="clip {cls}" id="{gid}" data-start="{t0:.3f}" data-duration="{t1 - t0:.3f}" data-track-index="{track}" style="{style}">{inner}</div>')

# ======================= b-roll scenes (SVG, 1080x928 viewBox, cover-fit) =======================
def svg(sid, body, bg=("#16243A", NAVY)):
    return (f'<svg class="scn" viewBox="0 0 1080 928" preserveAspectRatio="xMidYMid slice"><defs><linearGradient id="{sid}g" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{bg[0]}"/><stop offset="1" stop-color="{bg[1]}"/></linearGradient></defs>'
            f'<rect width="1080" height="928" fill="url(#{sid}g)"/>{body}</svg>')
def particles(sid, n=14):
    import random; r = random.Random(hash(sid) & 0xffff); out = []
    for k in range(n):
        x, y, s = r.uniform(40, 1040), r.uniform(60, 880), r.uniform(8, 18)
        out.append(f'<rect class="pt" id="{sid}p{k}" x="{x:.0f}" y="{y:.0f}" width="{s:.0f}" height="{s * 0.55:.0f}" rx="2" fill="{ORANGE if k % 3 else YELLOW}" opacity="0.22" transform="rotate({r.uniform(-30, 30):.0f} {x:.0f} {y:.0f})"/>')
    return "".join(out)
def anim_particles(sid, a, b, n=14):
    for k in range(n): js.append(f'tl.fromTo("#{sid}p{k}", {{y: 0}}, {{y: {-40 - 10 * (k % 5)}, x: {(-1) ** k * 12}, duration: {b - a:.3f}, ease: "none"}}, {a:.3f});')

SC = {}
# S1 trash: shared lead cards tip into a trash can
cards = "".join(f'<g id="s1c{k}"><rect x="-90" y="-58" width="180" height="116" rx="14" fill="#fff"/><rect x="-66" y="-34" width="90" height="14" rx="7" fill="#C9D1DD"/>'
                f'<rect x="-66" y="-6" width="132" height="10" rx="5" fill="#E3E8EF"/><rect x="-66" y="14" width="110" height="10" rx="5" fill="#E3E8EF"/>'
                f'<rect x="14" y="-44" width="62" height="26" rx="6" fill="none" stroke="#E5484D" stroke-width="4"/><text x="45" y="-25" text-anchor="middle" class="t18" fill="#E5484D">SHARED</text></g>' for k in range(4))
SC["trash"] = lambda sid: svg(sid, particles(sid) +
    '<ellipse cx="540" cy="800" rx="260" ry="34" fill="#000" opacity="0.35"/>'
    '<path d="M380 430 L415 790 Q418 808 436 808 H644 Q662 808 665 790 L700 430 Z" fill="#8C97AB"/>'
    '<path d="M450 470 L462 760 M540 470 V760 M630 470 L618 760" stroke="#6B7689" stroke-width="16" stroke-linecap="round"/>'
    f'<g id="{sid}lid"><rect x="350" y="380" width="380" height="50" rx="16" fill="#AEB8C9"/><rect x="490" y="350" width="100" height="36" rx="12" fill="#AEB8C9"/></g>'
    + cards.replace('id="s1c', f'id="{sid}c'))
def an_trash(sid, a, b):
    js.append(f'tl.fromTo("#{sid}lid", {{rotation: 0, svgOrigin: "350 430"}}, {{rotation: -34, svgOrigin: "350 430", duration: 0.25, ease: "back.out(2)"}}, {a + 0.08:.3f});')
    for k in range(4):
        t = a + 0.22 + k * 0.2
        js.append(f'tl.fromTo("#{sid}c{k}", {{x: {300 + (k - 1.5) * 150}, y: -120, rotation: {(k - 1.5) * 25}, opacity: 1}}, {{x: 540, y: 560, rotation: {(1.5 - k) * 40}, duration: 0.42, ease: "power2.in"}}, {t:.3f});')
        js.append(f'tl.to("#{sid}c{k}", {{opacity: 0, duration: 0.04}}, {t + 0.42:.3f});')
    js.append(f'tl.to("#{sid}lid", {{rotation: 0, svgOrigin: "350 430", duration: 0.16, ease: "power2.in"}}, {a + 1.12:.3f});'); fx("thud", a + 1.27, 0.10)

# S2/S9 handshake: roofer (hard hat) and homeowner meet, hands shake
def person(px, hat, shirt, flip):
    s = -1 if flip else 1
    hat_svg = (f'<path d="M{px - 70} 300 Q{px} 210 {px + 70} 300 Z" fill="{YELLOW}"/><rect x="{px - 86}" y="292" width="172" height="20" rx="10" fill="{ORANGE}"/>' if hat
               else f'<path d="M{px - 64} 318 Q{px - 60} 240 {px} 238 Q{px + 64} 240 {px + 66} 320 Q{px} 290 {px - 64} 318 Z" fill="#3A2A22"/>')
    return (f'<rect x="{px - 120}" y="470" width="240" height="330" rx="60" fill="{shirt}"/><circle cx="{px}" cy="360" r="78" fill="#C98E6B"/>{hat_svg}')
SC["handshake"] = lambda sid: svg(sid, particles(sid) +
    '<path d="M180 560 L540 330 L900 560" fill="none" stroke="#2A3B57" stroke-width="18" stroke-linejoin="round"/><rect x="250" y="560" width="580" height="260" fill="#1C2C45"/>'
    + person(300, True, "#25406B", False) + person(780, False, "#3E4C63", True) +
    f'<g id="{sid}ar1"><path d="M400 560 Q470 600 520 590" stroke="#25406B" stroke-width="56" stroke-linecap="round" fill="none"/></g>'
    f'<g id="{sid}ar2"><path d="M680 560 Q610 600 560 590" stroke="#3E4C63" stroke-width="56" stroke-linecap="round" fill="none"/></g>'
    f'<g id="{sid}hand" opacity="0"><ellipse cx="540" cy="588" rx="58" ry="34" fill="#C98E6B"/></g>'
    + "".join(f'<path id="{sid}sp{k}" d="M540 520 L540 470" stroke="{YELLOW}" stroke-width="10" stroke-linecap="round" transform="rotate({k * 45 - 90} 540 588)" opacity="0"/>' for k in range(5)),
    bg=("#1A2A44", NAVY))
def an_handshake(sid, a, b):
    js.append(f'tl.fromTo("#{sid}ar1", {{x: -90}}, {{x: 0, duration: 0.35, ease: "power3.out"}}, {a + 0.05:.3f});')
    js.append(f'tl.fromTo("#{sid}ar2", {{x: 90}}, {{x: 0, duration: 0.35, ease: "power3.out"}}, {a + 0.05:.3f});')
    js.append(f'tl.to("#{sid}hand", {{opacity: 1, duration: 0.05}}, {a + 0.38:.3f});')
    js.append(f'tl.fromTo("#{sid}hand", {{y: 0}}, {{y: 12, duration: 0.1, yoyo: true, repeat: 3, ease: "sine.inOut", immediateRender: false}}, {a + 0.42:.3f});')
    for k in range(5): js.append(f'tl.fromTo("#{sid}sp{k}", {{opacity: 0, scale: 0.4, svgOrigin: "540 588"}}, {{opacity: 1, scale: 1.2, svgOrigin: "540 588", duration: 0.25, ease: "power2.out"}}, {a + 0.42:.3f});')
    js.append(f'tl.to("#{sid}sp0, #{sid}sp1, #{sid}sp2, #{sid}sp3, #{sid}sp4", {{opacity: 0, duration: 0.2}}, {a + 0.75:.3f});')

# S3 house: line-art suburban house, door opens, homeowner steps out, sun glow, yard sign
SC["house"] = lambda sid: svg(sid, particles(sid) +
    f'<circle id="{sid}sun" cx="860" cy="190" r="70" fill="{YELLOW}" opacity="0.85"/><rect x="0" y="760" width="1080" height="168" fill="#13311F" opacity="0.55"/>'
    '<path d="M250 470 L540 250 L830 470" fill="#24344F" stroke="#fff" stroke-width="10" stroke-linejoin="round"/>'
    + "".join(f'<path d="M{300 + k * 10} {455 - k * 38} L{780 - k * 10} {455 - k * 38}" stroke="{ORANGE}" stroke-width="10" opacity="0.8"/>' for k in range(5)) +
    '<rect x="300" y="470" width="480" height="300" fill="none" stroke="#fff" stroke-width="10"/>'
    '<rect x="350" y="530" width="110" height="90" fill="none" stroke="#fff" stroke-width="8"/><rect x="620" y="530" width="110" height="90" fill="none" stroke="#fff" stroke-width="8"/>'
    f'<rect x="495" y="600" width="90" height="170" fill="#0B1424" stroke="#fff" stroke-width="8"/><g id="{sid}per" opacity="0"><circle cx="540" cy="640" r="22" fill="#C98E6B"/><rect x="514" y="664" width="52" height="96" rx="20" fill="{ORANGE}"/></g>'
    f'<rect id="{sid}door" x="499" y="604" width="82" height="162" fill="#3A4A66"/>'
    f'<g id="{sid}sign"><rect x="860" y="600" width="12" height="170" fill="#fff"/><rect x="800" y="590" width="132" height="86" rx="8" fill="#fff"/><path d="M836 650 L866 620 L896 650 V666 H836 Z" fill="{ORANGE}"/></g>',
    bg=("#20375E", "#13213A"))
def an_house(sid, a, b):
    js.append(f'tl.fromTo("#{sid}door", {{scaleX: 1, transformOrigin: "0% 50%"}}, {{scaleX: 0.15, duration: 0.35, ease: "power2.inOut"}}, {a + 0.35:.3f});')
    js.append(f'tl.fromTo("#{sid}per", {{opacity: 0, y: 20}}, {{opacity: 1, y: 0, duration: 0.3, ease: "power2.out"}}, {a + 0.6:.3f});')
    js.append(f'tl.fromTo("#{sid}sign", {{rotation: -12, svgOrigin: "866 770"}}, {{rotation: 0, svgOrigin: "866 770", duration: 0.5, ease: "elastic.out(1, 0.5)"}}, {a + 0.2:.3f});')
    js.append(f'tl.fromTo("#{sid}sun", {{scale: 0.8, svgOrigin: "860 190"}}, {{scale: 1.15, svgOrigin: "860 190", duration: {b - a:.3f}, ease: "sine.inOut"}}, {a:.3f});')

# S4 roof cross-section: deck, underlayment, shingle courses laying in bottom-up
SC["roof"] = lambda sid: svg(sid, particles(sid) +
    '<g transform="rotate(-14 540 520)"><rect x="40" y="560" width="1000" height="44" fill="#7A5A3A"/><rect x="40" y="540" width="1000" height="22" fill="#9AA6B8"/>'
    + "".join(f'<g id="{sid}r{k}">' + "".join(f'<rect x="{40 + j * 125 + (k % 2) * 62}" y="{500 - k * 46}" width="120" height="58" rx="5" fill="{["#2B3A55", "#33445F", "#3B4D6A"][(j + k) % 3]}" stroke="{NAVY}" stroke-width="4"/>' for j in range(8)) + "</g>" for k in range(5))
    + f'</g><g id="{sid}nail" opacity="0"><circle cx="760" cy="330" r="10" fill="{YELLOW}"/></g>',
    bg=("#1A2B46", NAVY))
def an_roof(sid, a, b):
    for k in range(5):
        js.append(f'tl.fromTo("#{sid}r{k}", {{opacity: 0, y: -60}}, {{opacity: 1, y: 0, duration: 0.2, ease: "back.out(1.6)"}}, {a + 0.1 + k * 0.2:.3f});')
    js.append(f'tl.fromTo("#{sid}nail", {{opacity: 0, scale: 2.5, svgOrigin: "760 330"}}, {{opacity: 1, scale: 1, svgOrigin: "760 330", duration: 0.15}}, {a + 1.15:.3f});')

# S5 aerial neighbourhood: top-down houses, roofs flip to new orange roofs
def roofs(sid):
    out = []
    for r_ in range(3):
        for c in range(4):
            x, y = 90 + c * 240, 110 + r_ * 270
            out.append(f'<rect x="{x}" y="{y}" width="180" height="140" rx="10" fill="#2C3C56"/>'
                       f'<g id="{sid}h{r_ * 4 + c}" opacity="0"><rect x="{x}" y="{y}" width="180" height="140" rx="10" fill="{ORANGE}"/><path d="M{x + 10} {y + 70} H{x + 170}" stroke="#C75C10" stroke-width="10"/></g>'
                       f'<rect x="{x + 30}" y="{y + 150}" width="120" height="40" rx="6" fill="#1D3B2A"/>')
    return "".join(out)
SC["aerial"] = lambda sid: svg(sid, '<rect x="0" y="230" width="1080" height="40" fill="#0A1322"/><rect x="0" y="500" width="1080" height="40" fill="#0A1322"/>' + roofs(sid),
    bg=("#1E3A2B", "#14261C"))
def an_aerial(sid, a, b):
    order = [5, 2, 9, 0, 7, 10, 3, 6, 11, 1, 8, 4]
    for n, k in enumerate(order): js.append(f'tl.fromTo("#{sid}h{k}", {{opacity: 0, scale: 0.7, transformOrigin: "50% 50%"}}, {{opacity: 1, scale: 1, duration: 0.14, ease: "back.out(2)"}}, {a + 0.1 + n * 0.1:.3f});')

# S6 phone: incoming call, rings, then call connected notification
SC["phone"] = lambda sid: svg(sid, particles(sid) +
    "".join(f'<circle id="{sid}ring{k}" cx="540" cy="460" r="150" fill="none" stroke="{ORANGE}" stroke-width="10" opacity="0"/>' for k in range(3)) +
    f'<g id="{sid}ph"><rect x="390" y="130" width="300" height="620" rx="48" fill="#0B1424" stroke="#fff" stroke-width="10"/>'
    '<circle cx="540" cy="330" r="62" fill="#2C3C56"/><circle cx="540" cy="310" r="24" fill="#C9D1DD"/><path d="M500 372 Q540 330 580 372" fill="#C9D1DD"/>'
    '<text x="540" y="440" text-anchor="middle" class="t34" fill="#fff">HOMEOWNER</text><text x="540" y="482" text-anchor="middle" class="t26" fill="#9AA6B8">incoming call</text>'
    f'<circle id="{sid}btn" cx="540" cy="640" r="48" fill="#22C55E"/><path d="M518 628 q8 22 34 34 l10 -10 q4 -3 8 -1 l14 6 q4 2 3 7 l-4 12 q-2 4 -7 4 q-58 -4 -80 -60 q0 -5 4 -7 l12 -4 q5 -1 7 3 l6 14 q2 4 -1 8 z" fill="#fff"/></g>'
    f'<g id="{sid}note" opacity="0"><rect x="240" y="40" width="600" height="110" rx="26" fill="#fff"/><circle cx="300" cy="95" r="30" fill="#22C55E"/>'
    f'<text x="350" y="88" class="t30" fill="{NAVY}">Call connected</text><text x="350" y="124" class="t24" fill="#5D6B80">Lead qualified &amp; booked</text></g>',
    bg=("#1A2A44", NAVY))
def an_phone(sid, a, b):
    for k in range(3): js.append(f'tl.fromTo("#{sid}ring{k}", {{attr: {{r: 150}}, opacity: 0.8}}, {{attr: {{r: 330}}, opacity: 0, duration: 0.7, ease: "power1.out"}}, {a + 0.05 + k * 0.22:.3f});')
    js.append(f'tl.fromTo("#{sid}ph", {{rotation: -3, svgOrigin: "540 440"}}, {{rotation: 3, svgOrigin: "540 440", duration: 0.05, yoyo: true, repeat: 9, ease: "none", immediateRender: false}}, {a + 0.05:.3f});')
    js.append(f'tl.fromTo("#{sid}note", {{opacity: 0, y: -60}}, {{opacity: 1, y: 0, duration: 0.3, ease: "back.out(1.7)"}}, {a + 0.75:.3f});'); fx("pop", a + 0.75, 0.16)

# S7 calendar: estimate slots fill one by one, counter to 9, EXAMPLE label
def cal(sid):
    out = ['<rect x="110" y="120" width="860" height="660" rx="30" fill="#fff"/><rect x="110" y="120" width="860" height="90" rx="30" fill="#E8EDF4"/>']
    for d, day in enumerate(["MON", "TUE", "WED", "THU", "FRI"]):
        out.append(f'<text x="{196 + d * 172}" y="180" text-anchor="middle" class="t28" fill="{NAVY}">{day}</text>')
        for r_ in range(3):
            x, y = 130 + d * 172, 240 + r_ * 170
            out.append(f'<rect x="{x}" y="{y}" width="150" height="150" rx="14" fill="#F2F5F9"/>')
    k = 0
    for d, r_ in [(0, 0), (2, 1), (4, 0), (1, 2), (3, 1), (0, 2), (2, 0), (4, 2), (1, 0)]:
        x, y = 130 + d * 172, 240 + r_ * 170
        out.append(f'<g id="{sid}s{k}" opacity="0"><rect x="{x}" y="{y}" width="150" height="150" rx="14" fill="{ORANGE}"/>'
                   f'<text x="{x + 75}" y="{y + 66}" text-anchor="middle" class="t28" fill="#fff">{["9 AM", "1 PM", "11 AM", "3 PM", "10 AM", "4 PM", "2 PM", "5 PM", "12 PM"][k]}</text>'
                   f'<text x="{x + 75}" y="{y + 104}" text-anchor="middle" class="t20" fill="#fff">Free estimate</text></g>'); k += 1
    out.append(f'<rect x="760" y="806" width="210" height="80" rx="18" fill="{NAVY}" stroke="{YELLOW}" stroke-width="4"/><text id="{sid}cnt" x="865" y="862" text-anchor="middle" class="t44" fill="{YELLOW}">0</text>'
               f'<text x="740" y="860" text-anchor="end" class="t28" fill="#fff">ESTIMATES BOOKED</text>'
               f'<rect x="110" y="806" width="170" height="56" rx="10" fill="none" stroke="#fff" stroke-width="3"/><text x="195" y="844" text-anchor="middle" class="t26" fill="#fff">EXAMPLE</text>')
    return "".join(out)
SC["calendar"] = lambda sid: svg(sid, f'<g transform="translate(300 30) scale(0.72)">{cal(sid)}</g>', bg=("#1A2A44", NAVY))   # kept clear of the speaker bubble (bottom-left)
def an_calendar(sid, a, b):
    for k in range(9):
        t = a + 0.15 + k * 0.15
        js.append(f'tl.fromTo("#{sid}s{k}", {{opacity: 0, scale: 0.6, transformOrigin: "50% 50%"}}, {{opacity: 1, scale: 1, duration: 0.12, ease: "back.out(2.2)"}}, {t:.3f});')
        js.append(f'tl.set("#{sid}cnt", {{textContent: "{k + 1}"}}, {t:.3f});')
    fx("ding", a + 0.15 + 8 * 0.15 + 0.05, 0.12)

# S8 clipboard estimate on a roof
SC["clipboard"] = lambda sid: svg(sid, particles(sid) +
    '<path d="M0 700 L540 520 L1080 700 V928 H0 Z" fill="#2B3A55"/>'
    '<rect x="330" y="110" width="420" height="600" rx="30" fill="#7A5A3A"/><rect x="360" y="160" width="360" height="530" rx="12" fill="#fff"/><rect x="470" y="90" width="140" height="60" rx="16" fill="#9AA6B8"/>'
    f'<text x="540" y="230" text-anchor="middle" class="t40" fill="{NAVY}">ESTIMATE</text>'
    + "".join(f'<rect x="400" y="{290 + k * 90}" width="44" height="44" rx="8" fill="none" stroke="{NAVY}" stroke-width="5"/><rect x="465" y="{300 + k * 90}" width="{210 - k * 20}" height="20" rx="10" fill="#D5DCE6"/>'
              f'<path id="{sid}k{k}" d="M408 {312 + k * 90} l12 12 l22 -26" stroke="{ORANGE}" stroke-width="9" fill="none" stroke-linecap="round" opacity="0"/>' for k in range(4)) +
    f'<g id="{sid}pen"><rect x="700" y="420" width="22" height="200" rx="8" fill="{YELLOW}" transform="rotate(30 711 520)"/></g>',
    bg=("#1A2A44", NAVY))
def an_clipboard(sid, a, b):
    for k in range(4): js.append(f'tl.fromTo("#{sid}k{k}", {{opacity: 0, scale: 0.4, transformOrigin: "50% 50%"}}, {{opacity: 1, scale: 1, duration: 0.14, ease: "back.out(2.5)"}}, {a + 0.25 + k * 0.32:.3f});')
    js.append(f'tl.fromTo("#{sid}pen", {{x: 0, y: 0}}, {{x: -260, y: 300, duration: {b - a - 0.3:.3f}, ease: "none"}}, {a + 0.15:.3f});')

AN = {"trash": an_trash, "handshake": an_handshake, "house": an_house, "roof": an_roof, "aerial": an_aerial, "phone": an_phone,
      "calendar": an_calendar, "clipboard": an_clipboard}
BROLL = [  # (scene, type, start, end)  -- snapped to the words; type A also hides the old baked graphic windows
    ("trash", "A", 3.30, 4.80),           # "stop buying garbage, Angi leads"
    ("handshake", "A", 6.37, 7.63),       # "face-to-face meetings"
    ("house", "A", 8.53, 10.63),          # "homeowners who can actually afford a roof"
    ("roof", "A", 11.92, 13.53),          # "only pay per estimate" (covers the old money emojis)
    ("aerial", "B", 15.35, 16.95),        # "exclusive homeowner leads"
    ("phone", "A", 17.87, 19.37),         # "call them ourselves"
    ("calendar", "A", 23.10, 25.03),      # "book them directly into your calendar"
    ("clipboard", "B", 28.40, 30.90),     # "high-intent homeowner estimates"
    ("handshake", "A", 32.20, 33.50),     # "when you're face to face with them"
]
LEAK = f"radial-gradient(ellipse at 0% 50%, rgba(255,122,26,0.75) 0%, rgba(255,212,0,0.35) 30%, rgba(255,122,26,0) 65%)"
for n, (scene, typ, a, b) in enumerate(BROLL):
    sid = f"s{n}"; inner = SC[scene](sid)
    whip = n % 2 == 1
    box = ('class="ba"' if typ == "A" else 'class="bb"')
    clip(f"br{n}", a, b, f'<div {box} id="{sid}box"><div class="push" id="{sid}push">{inner}</div><div class="tint"></div><div class="grain" id="{sid}gr"></div>'
                         f'<div class="leak" id="{sid}leak" style="background:{LEAK}"></div></div>', 10 + n, "pane-abs")
    js.append(f'tl.fromTo("#{sid}push", {{scale: 1.0}}, {{scale: 1.08, duration: {b - a:.3f}, ease: "none"}}, {a:.3f});')
    if typ == "A":
        if whip: js.append(f'tl.fromTo("#{sid}box", {{opacity: 0, xPercent: 18, filter: "blur(18px)"}}, {{opacity: 1, xPercent: 0, filter: "blur(0px)", duration: 0.2, ease: "power3.out"}}, {a:.3f});')
        else: js.append(f'tl.fromTo("#{sid}box", {{opacity: 0}}, {{opacity: 1, duration: 0.2, ease: "none"}}, {a:.3f});')
        js.append(f'tl.to("#{sid}box", {{opacity: 0, {"xPercent: -18, filter: \"blur(18px)\", " if whip else ""}duration: 0.2, ease: "power2.in"}}, {b - 0.2:.3f});')
    else:
        js.append(f'tl.fromTo("#{sid}box", {{opacity: 0, x: 420}}, {{opacity: 1, x: 0, duration: 0.3, ease: "back.out(1.4)"}}, {a:.3f});')
        js.append(f'tl.to("#{sid}box", {{opacity: 0, x: 420, duration: 0.2, ease: "power2.in"}}, {b - 0.2:.3f});')
    js.append(f'tl.fromTo("#{sid}leak", {{opacity: 0.9, xPercent: -60}}, {{opacity: 0, xPercent: 60, duration: 0.45, ease: "power1.out"}}, {a:.3f});')
    for k in range(int((b - a) * 15)): js.append(f'tl.set("#{sid}gr", {{backgroundPosition: "{(k * 73) % 256}px {(k * 151) % 256}px"}}, {a + k / 15:.3f});')
    AN[scene](sid, a, b)
    if scene not in ("aerial", "calendar"): anim_particles(sid, a, b)
    fx("whoosh", a - 0.05, 0.12); fx("whoosh", b - 0.2, 0.07)

# speaker bubble during type A (bottom-left of the pane, never leaves him off screen)
AW = [(a, b) for _, t, a, b in BROLL if t == "A"]
for k, (a, b) in enumerate(AW):
    js.append(f'tl.fromTo("#bubble", {{opacity: 0, scale: 0.7}}, {{opacity: 1, scale: 1, duration: 0.25, ease: "back.out(1.8)", immediateRender: {"true" if k == 0 else "false"}}}, {a + 0.05:.3f});')
    js.append(f'tl.to("#bubble", {{opacity: 0, scale: 0.8, duration: 0.18, ease: "power2.in"}}, {b - 0.18:.3f});')

# ======================= header zone: wordmark + rotating claim chips =======================
hdr = (f'<div class="wm" style="top:{Z["wm"]}px">HIGH ROOF <span class="o">PARTNERS</span></div>'
       f'<div class="chiprow" style="top:{Z["chips"]}px">'
       '<div class="chip red" id="hc0"><span class="siren" id="siren">🚨</span>ATTENTION NC ROOFERS</div>'
       '<div class="chip nav" id="hc1">NO ESTIMATE = <span class="y">NO PAY</span></div>'
       '<div class="chip nav" id="hc2"><span class="lock">🔒</span>1 ROOFER PER AREA</div>'
       '<div class="chip nav" id="hc3">NO ESTIMATE = <span class="y">NO PAY</span><span class="sub">NO RETAINERS</span></div></div>')
el.append(f'<div class="clip hdr" id="hdr" data-start="0" data-duration="{DUR}" data-track-index="30">{hdr}</div>')
OFFER = at("no monthly")
SEQ = [("hc0", 0.0, 2.5), ("hc1", 2.5, 6.3), ("hc2", 6.3, OFFER - 0.05), ("hc3", OFFER, 36.05)]
for k, (cid, a, b) in enumerate(SEQ):
    if a == 0: js.append(f'tl.fromTo("#{cid}", {{opacity: 0, y: -90}}, {{opacity: 1, y: 0, duration: 0.3, ease: "back.out(1.7)", immediateRender: true}}, 0.03);')
    else: js.append(f'tl.fromTo("#{cid}", {{opacity: 0, y: -40}}, {{opacity: 1, y: 0, duration: 0.25, ease: "back.out(1.7)"}}, {a:.3f});'); fx("pop", a, 0.12)
    js.append(f'tl.to("#{cid}", {{opacity: 0, y: 30, duration: 0.18, ease: "power2.in"}}, {b - 0.18:.3f});')
js.append('tl.fromTo("#siren", {scale: 1}, {scale: 1.3, duration: 0.2, yoyo: true, repeat: 11, ease: "sine.inOut", immediateRender: false}, 0.1);')
fx("whoosh", 0.0, 0.10)

# ======================= graphics on the pane (never on the face: face lives in x 380-800, y 60-600 of the pane) =======================
def pane_gfx(gid, t0, t1, inner, track, style):
    clip(gid, t0, t1, inner, track, "pane-abs", style)
# name tag
pane_gfx("g-name", 0.6, 3.3, '<div class="name" id="name"><b>PARTH</b><i>|</i><span>HIGH ROOF PARTNERS</span><u id="nameline"></u></div>', 40, "")
js.append('tl.fromTo("#name", {opacity: 0, x: -460}, {opacity: 1, x: 0, duration: 0.3, ease: "back.out(1.4)"}, 0.6);')
js.append('tl.fromTo("#nameline", {scaleX: 0}, {scaleX: 1, duration: 0.35, ease: "power3.out"}, 0.85);')
js.append('tl.to("#name", {opacity: 0, x: -200, duration: 0.18, ease: "power2.in"}, 3.12);'); fx("whoosh", 0.55, 0.07)
# hook slam, then shrinks into a small tag in the open space left of his head
H0 = at("5")
pane_gfx("g-hook", H0, 3.3, '<div class="hook" id="hook">5 TO 10 ROOFS<br><span class="y">A MONTH?</span></div>', 41, "")
js.append(f'tl.fromTo("#hook", {{opacity: 0, scale: 2.3}}, {{opacity: 1, scale: 1, duration: 0.22, ease: "back.out(2.4)"}}, {H0:.3f});'); fx("whoosh", H0 - 0.06, 0.1); fx("thud", H0 + 0.1, 0.07)
js.append(f'tl.to("#hook", {{scale: 0.5, x: -330, y: -470, duration: 0.3, ease: "power2.inOut"}}, {at("month") + 0.25:.3f});')
js.append('tl.to("#hook", {opacity: 0, duration: 0.15}, 3.12);')
# keyword pops beside his head (left open space)
for gid, word, txt in (("g-kw1", "monthly", "NO<br>RETAINERS"), ("g-kw2", "exclusive", "EXCLUSIVE")):
    t = at(word)
    pane_gfx(gid, t, t + 0.6, f'<div class="kw" id="{gid}i">{txt}</div>', 42, "")
    js.append(f'tl.fromTo("#{gid}i", {{opacity: 0, scale: 1.8}}, {{opacity: 1, scale: 1, duration: 0.16, ease: "back.out(2.2)"}}, {t:.3f});')
    js.append(f'tl.to("#{gid}i", {{opacity: 0, scale: 0.9, duration: 0.12}}, {t + 0.48:.3f});'); fx("pop", t, 0.14)
# PRE-QUALIFIED pop on "financially qualified"
Q0 = at("financially")
pane_gfx("g-qual", Q0, Q0 + 1.6, '<div class="bar" id="qual">✓ PRE-QUALIFIED <span class="y">HOMEOWNERS</span></div>', 43, "")
js.append(f'tl.fromTo("#qual", {{opacity: 0, scale: 0.6}}, {{opacity: 1, scale: 1, duration: 0.22, ease: "back.out(2)"}}, {Q0:.3f});')
js.append(f'tl.to("#qual", {{opacity: 0, duration: 0.15}}, {Q0 + 1.45:.3f});'); fx("pop", Q0, 0.14)
# WE BOOK. YOU CLOSE.
B0 = 25.15
pane_gfx("g-book", B0, B0 + 1.7, '<div class="punch" id="book">WE BOOK. <span class="y">YOU CLOSE.</span><u id="bookline"></u></div>', 44, "")
js.append(f'tl.fromTo("#book", {{opacity: 0, scale: 1.9}}, {{opacity: 1, scale: 1, duration: 0.2, ease: "back.out(2)"}}, {B0:.3f});')
js.append(f'tl.fromTo("#bookline", {{scaleX: 0}}, {{scaleX: 1, duration: 0.3, ease: "power3.out"}}, {B0 + 0.2:.3f});')
js.append(f'tl.to("#book", {{opacity: 0, duration: 0.15}}, {B0 + 1.55:.3f});'); fx("whoosh", B0 - 0.05, 0.1)

# ======================= end card (36.05 -> end: the old red CTA pill starts at 36.2, this covers it) =======================
E0 = 36.05; ONE = at("one")
e0, e1 = Z["end"]
NC = "M18 158 L130 118 L265 112 L400 90 L575 66 L755 48 L930 30 L1040 18 L1058 66 L1022 116 L972 156 L906 214 L818 244 L730 230 L664 270 L553 266 L453 230 L353 230 L265 216 L155 230 L66 248 L26 222 Z"
pins = [(386, 205, "CHARLOTTE"), (735, 140, "RALEIGH"), (580, 122, "GREENSBORO")]
pin_svg = "".join(f'<g id="pin{k}"><circle cx="{x}" cy="{y}" r="16" fill="{ORANGE}"/><circle class="pulse" cx="{x}" cy="{y}" r="16" fill="none" stroke="{ORANGE}" stroke-width="6"/></g>' for k, (x, y, _) in enumerate(pins))
lock = (f'<g id="lockg" opacity="0"><rect x="707" y="88" width="56" height="44" rx="8" fill="{YELLOW}"/><path d="M718 90 v-12 a17 17 0 0 1 34 0 v12" fill="none" stroke="{YELLOW}" stroke-width="8"/></g>')
el.append(f'<div class="clip" id="endc" data-start="{E0:.3f}" data-duration="{DUR - E0:.3f}" data-track-index="60"><div class="dim" id="dim"></div>'
          f'<div class="ecard" id="ecard" style="top:{e0}px;height:{e1 - e0}px"><div class="ewm">HIGH ROOF <span class="o">PARTNERS</span></div>'
          f'<svg class="ncmap" viewBox="0 0 1080 300" id="ncmap"><path d="{NC}" fill="#1E2E4A" stroke="#fff" stroke-width="6" stroke-linejoin="round"/>{pin_svg}{lock}</svg>'
          f'<div class="ebadge" id="ebadge">🔒 1 ROOFER PER AREA · <span class="y">NC ONLY</span></div>'
          '<div class="etap">TAP SEND<br>MESSAGE</div><div class="esub">Only 1 roofer per area.<br>Check if yours is open.</div>'
          f'<svg class="earrow" id="earrow" viewBox="0 0 120 150"><path d="M42 0h36v80h32L60 145 10 80h32z" fill="{ORANGE}"/></svg></div></div>')
js.append(f'tl.fromTo("#dim", {{opacity: 0}}, {{opacity: 1, duration: 0.25}}, {E0:.3f});')
js.append(f'tl.fromTo("#ecard", {{opacity: 0, y: 60}}, {{opacity: 1, y: 0, duration: 0.3, ease: "back.out(1.4)"}}, {E0:.3f});'); fx("whoosh", E0 - 0.05, 0.12)
js.append(f'tl.fromTo("#ncmap .pulse", {{attr: {{r: 16}}, opacity: 1}}, {{attr: {{r: 46}}, opacity: 0, duration: 0.6, repeat: 3, stagger: 0.15, immediateRender: false}}, {E0 + 0.3:.3f});')
js.append(f'tl.fromTo("#lockg", {{opacity: 0, y: -60}}, {{opacity: 1, y: 0, duration: 0.14, ease: "power4.in"}}, {ONE - 0.1:.3f});')
js.append(f'tl.fromTo("#ebadge", {{opacity: 0, scale: 1.8}}, {{opacity: 1, scale: 1, duration: 0.16, ease: "back.out(2)"}}, {ONE:.3f});'); fx("thud", ONE + 0.04, 0.14)
for k, (dx, dy) in enumerate(((6, -3), (-6, 3))): js.append(f'tl.set("#stage", {{x: {dx}, y: {dy}}}, {ONE + 0.04 + k / 30:.3f});')
js.append(f'tl.set("#stage", {{x: 0, y: 0}}, {ONE + 0.04 + 2 / 30:.3f});')
js.append(f'tl.fromTo("#earrow", {{y: 0}}, {{y: 26, duration: 0.32, ease: "power2.in", yoyo: true, repeat: {int((DUR - E0 - 0.5) / 0.32)}, immediateRender: false}}, {E0 + 0.4:.3f});')

# ======================= captions (word by word; hidden under the end card) =======================
KEY = {"ESTIMATE", "ESTIMATES", "PAY", "EXCLUSIVE", "RETAINERS", "ONE", "CALENDAR"}
ws = []
for w in words:
    d = re.sub(r"^-", "", w["text"]).upper().strip(",.?!")
    if w["text"].startswith("-") and ws: ws[-1]["d"] += "-" + d; ws[-1]["end"] = w["end"]
    else: ws.append(dict(w, d=d))
groups, cur = [], []
for k, w in enumerate(ws):
    if cur:
        prev = ws[cur[-1]]
        if len(cur) >= 3 or re.search(r"[.,?!]$", prev["text"]) or w["start"] - prev["end"] > 0.3: groups.append(cur); cur = []
    cur.append(k)
groups.append(cur)
cap = []
def em(s): return sum(0.40 if c == " " else 0.36 if c in ",.'-?!" else 0.95 if c in "MW" else 0.36 if c in "I1" else 0.74 for c in s)
for gi, g in enumerate(groups):
    t0 = ws[g[0]]["start"] - 2 / 30
    if t0 >= E0: continue
    t1 = ws[groups[gi + 1][0]]["start"] - 2 / 30 if gi + 1 < len(groups) else E0
    t1 = min(t1, ws[g[-1]]["end"] + 0.5, E0)
    fs = min(66, int(900 / em(" ".join(ws[k]["d"] for k in g))))
    body = " ".join(f'<span class="w{" key" if ws[k]["d"] in KEY else ""}" id="w{k}">{html.escape(ws[k]["d"])}</span>' for k in g)
    cap.append(f'<div class="cg" id="cg{gi}" style="font-size:{fs}px"><div>{body}</div></div>')
    js.append(f'tl.set("#cg{gi}", {{opacity: 1}}, {max(0, t0):.3f}); tl.set("#cg{gi}", {{opacity: 0}}, {t1:.3f});')
    for k in g:
        a = max(0, ws[k]["start"] - 2 / 30); b = max(a + 0.08, min(ws[k]["end"], t1))
        js.append(f'tl.fromTo("#w{k}", {{color: "#ffffff", scale: 1}}, {{color: "{YELLOW}", scale: 1.1, duration: 0.05, immediateRender: false}}, {a:.3f});')
        js.append(f'tl.to("#w{k}", {{color: "#ffffff", scale: 1, duration: 0.05}}, {b:.3f});')

CSS = f"""
      @font-face {{ font-family: "Montserrat"; font-weight: 800; src: url("vendor/montserrat-latin-800-normal.woff2") format("woff2"); }}
      @font-face {{ font-family: "Montserrat"; font-weight: 900; src: url("vendor/montserrat-latin-900-normal.woff2") format("woff2"); }}
      @font-face {{ font-family: "Noto Color Emoji"; src: url("vendor/NotoColorEmoji.ttf") format("truetype"); }}
      body {{ margin: 0; background: {NAVY}; }}
      #root {{ position: relative; width: {W}px; height: {H}px; overflow: hidden; background: {NAVY}; font-family: "Montserrat", "Noto Color Emoji", sans-serif; font-weight: 900; color: #fff; }}
      #stage {{ position: absolute; inset: 0; }}
      .bgc {{ position: absolute; inset: 0; background: linear-gradient(180deg, #13223A 0%, {NAVY} 45%, #0A1322 100%); }}
      .shingle {{ position: absolute; inset: -400px; opacity: 0.06; transform: rotate(-24deg);
                  background-image: linear-gradient(90deg, rgba(255,255,255,0.9) 0 3px, transparent 3px 100%), linear-gradient(0deg, rgba(255,255,255,0.9) 0 3px, transparent 3px 100%);
                  background-size: 90px 46px, 90px 46px; background-position: 0 0, 45px 23px; }}
      #pane {{ position: absolute; left: 0; top: {PY}px; width: {W}px; height: {PH}px; overflow: hidden; }}
      #pv {{ position: absolute; inset: 0; width: {W}px; height: {PH}px; }}
      .pane-abs {{ position: absolute; left: 0; top: 0; width: {W}px; height: {PH}px; }}
      .ba {{ position: absolute; inset: 0; overflow: hidden; opacity: 0; }}
      .bb {{ position: absolute; left: 600px; top: 600px; width: 450px; height: 300px; border-radius: 26px; overflow: hidden; border: 5px solid #fff; box-shadow: 0 16px 40px rgba(0,0,0,0.55); opacity: 0; }}
      .push {{ position: absolute; inset: 0; }}
      .scn {{ width: 100%; height: 100%; display: block; }}
      .tint {{ position: absolute; inset: 0; background: rgba(15,27,45,0.2); }}
      .grain {{ position: absolute; inset: 0; background-image: url("assets/grain.png"); background-size: 256px 256px; opacity: 0.07; mix-blend-mode: overlay; }}
      .leak {{ position: absolute; inset: 0; mix-blend-mode: screen; opacity: 0; }}
      .t18 {{ font: 900 18px Montserrat; }} .t20 {{ font: 800 20px Montserrat; }} .t24 {{ font: 800 24px Montserrat; }} .t26 {{ font: 800 26px Montserrat; }}
      .t28 {{ font: 900 28px Montserrat; }} .t30 {{ font: 900 30px Montserrat; }} .t34 {{ font: 900 34px Montserrat; }} .t40 {{ font: 900 40px Montserrat; }} .t44 {{ font: 900 44px Montserrat; }}
      #bubble {{ position: absolute; left: 40px; top: {PH - 40 - 240}px; width: 240px; height: 240px; border-radius: 50%; overflow: hidden; border: 6px solid #fff; box-sizing: border-box;
                 box-shadow: 0 0 0 4px rgba(255,122,26,0.55), 0 0 46px 14px rgba(255,122,26,0.55); opacity: 0; }}
      #bv {{ position: absolute; left: -210px; top: -95px; width: 594px; height: 510px; }}
      .y {{ color: {YELLOW}; }} .o {{ color: {ORANGE}; }}
      .hdr {{ position: absolute; left: 0; top: 0; width: {W}px; height: {PY}px; }}
      .wm {{ position: absolute; left: 0; right: 0; text-align: center; font-size: 44px; letter-spacing: 3px; }}
      .chiprow {{ position: absolute; left: 0; right: 0; height: 100px; }}
      .chip {{ position: absolute; left: 50%; top: 0; transform: translateX(-50%); display: flex; align-items: center; gap: 14px; white-space: nowrap; padding: 12px 30px 10px; border-radius: 16px; font-size: 50px; opacity: 0; }}
      .chip.red {{ background: #E01E26; }} .chip.nav {{ background: #16253D; border: 4px solid {ORANGE}; }}
      .chip .sub {{ margin-left: 10px; padding: 4px 16px 2px; border-radius: 999px; background: {ORANGE}; color: {NAVY}; font-size: 34px; }}
      .siren, .lock {{ font-family: "Noto Color Emoji", sans-serif; display: inline-block; font-size: 44px; }}
      .name {{ position: absolute; left: 40px; top: 790px; display: flex; align-items: baseline; gap: 14px; padding: 16px 28px 22px; border-radius: 14px; background: rgba(15,27,45,0.94); font-size: 54px; white-space: nowrap; opacity: 0; }}
      .name i {{ font-style: normal; color: {ORANGE}; }} .name span {{ font-weight: 800; }}
      .name u {{ position: absolute; left: 28px; right: 28px; bottom: 9px; height: 7px; border-radius: 4px; background: {ORANGE}; transform-origin: 0 50%; }}
      .hook {{ position: absolute; left: 0; right: 0; top: 590px; text-align: center; font-size: 96px; line-height: 1.02; -webkit-text-stroke: 10px #000; paint-order: stroke fill; text-shadow: 0 8px 20px rgba(0,0,0,0.6); opacity: 0; transform-origin: 50% 50%; }}
      .kw {{ position: absolute; left: 30px; top: 150px; width: 340px; text-align: center; font-size: 66px; line-height: 1.0; color: #fff; -webkit-text-stroke: 8px #000; paint-order: stroke fill;
             text-shadow: 0 0 26px rgba(255,212,0,0.95), 0 0 6px rgba(255,212,0,0.9); opacity: 0; }}
      .bar {{ position: absolute; left: 50%; top: 700px; transform: translateX(-50%); white-space: nowrap; padding: 16px 30px 12px; border-radius: 16px; background: rgba(15,27,45,0.92); border: 4px solid {YELLOW}; font-size: 52px; opacity: 0; }}
      .punch {{ position: absolute; left: 0; right: 0; top: 670px; text-align: center; font-size: 78px; white-space: nowrap; -webkit-text-stroke: 10px #000; paint-order: stroke fill; text-shadow: 0 8px 20px rgba(0,0,0,0.6); opacity: 0; }}
      .punch u {{ position: absolute; left: 190px; right: 190px; bottom: -14px; height: 12px; border-radius: 6px; background: {YELLOW}; transform-origin: 0 50%; }}
      #captions {{ position: absolute; left: 90px; right: 90px; top: {Z['cap'] - 80}px; height: 160px; }}
      .cg {{ position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; opacity: 0; }}
      .cg div {{ white-space: nowrap; line-height: 1.1; }}
      .w {{ display: inline-block; color: #fff; -webkit-text-stroke: 6px #000; paint-order: stroke fill; text-shadow: 0 6px 14px rgba(0,0,0,0.6); margin: 0 0.12em; }}
      .w.key {{ background: linear-gradient(transparent 12%, {ORANGE} 12%, {ORANGE} 92%, transparent 92%); border-radius: 8px; padding: 0 0.12em; }}
      .dim {{ position: absolute; inset: 0; background: rgba(0,0,0,0.7); opacity: 0; }}
      .ecard {{ position: absolute; left: 40px; right: 40px; border-radius: 34px; background: linear-gradient(180deg, #16253D 0%, {NAVY} 100%); border: 4px solid rgba(255,122,26,0.7);
                display: flex; flex-direction: column; align-items: center; justify-content: space-evenly; text-align: center; opacity: 0; }}
      .ewm {{ font-size: 50px; letter-spacing: 3px; padding-bottom: 10px; border-bottom: 7px solid {ORANGE}; }}
      .ncmap {{ width: 860px; height: 240px; }}
      .ebadge {{ padding: 12px 28px 10px; border-radius: 16px; background: {ORANGE}; color: {NAVY}; font-size: 46px; white-space: nowrap; opacity: 0; }}
      .ebadge .y {{ color: #fff; }}
      .etap {{ font-size: 110px; line-height: 1.0; color: {YELLOW}; }}
      .esub {{ font-size: 46px; font-weight: 800; line-height: 1.2; }}
      .earrow {{ width: 96px; height: 120px; }}"""
nl = "\n      "
doc = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <title>High Roof Partners Ad 1 v2 {FMT}</title>
    <script src="vendor/gsap.min.js"></script>
    <style>{CSS}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="{W}" data-height="{H}" data-duration="{DUR}">
      <div id="stage"><div class="bgc"></div><div class="shingle"></div>
      <div id="pane">
        <video id="pv" class="clip" src="assets/pane_look.mp4" muted playsinline data-start="0" data-duration="{DUR}" data-track-index="0"></video>
        {(nl + "  ").join(el_ for el_ in el if 'pane-abs' in el_)}
        <div id="bubble"><video id="bv" class="clip" src="assets/pane_look.mp4" muted playsinline data-start="0" data-duration="{DUR}" data-track-index="1"></video></div>
      </div>
      {nl.join(el_ for el_ in el if 'pane-abs' not in el_)}
      <div id="captions" class="clip" data-start="0" data-duration="{DUR}" data-track-index="50">
        {(nl + "  ").join(cap)}
      </div>
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
if not os.path.exists(f"{OUT}/vendor"): shutil.copytree("../edit/remotion/vendor", f"{OUT}/vendor")
for a in ("pane_look.mp4",): shutil.copy(f"work/{a}", f"{OUT}/assets/{a}")
shutil.copy("assets/grain.png", f"{OUT}/assets/grain.png")
for f in ("package.json", "hyperframes.json"): shutil.copy(f"../edit/remotion/{f}", f"{OUT}/{f}")
json.dump({"id": f"hrp-ad1v2-{FMT}"}, open(f"{OUT}/meta.json", "w"))
open(f"{OUT}/index.html", "w").write(doc)
json.dump(sfx, open("work/sfx.json", "w"))
json.dump({"broll": BROLL, "endcard": [E0, DUR], "graphics": {"name": [0.6, 3.3], "hook": [H0, 3.3], "kw_retainers": [at("monthly"), at("monthly") + 0.6],
           "kw_exclusive": [at("exclusive"), at("exclusive") + 0.6], "prequal": [Q0, Q0 + 1.6], "webook": [B0, B0 + 1.7]}}, open("work/plan.json", "w"), indent=1)
print(f"{FMT}: {W}x{H}, {len(BROLL)} b-roll ({sum(1 for b in BROLL if b[1] == 'A')} A / {sum(1 for b in BROLL if b[1] == 'B')} B), {len(cap)} caption groups, {len(sfx)} sfx")
