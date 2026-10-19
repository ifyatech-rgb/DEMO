"""Build index.html for the letterboxed roofing ad from transcript.json of assets/cut.mp4.

Layout (1080x1920): native 1072x928 picture in the middle (y 496-1424), headline hooks in the
top bar, captions + CTA in the bottom bar, motion-graphic b-roll cutaways over the picture box.
"""
import json, re, subprocess, html
words = json.load(open("transcript.json"))
words = words if isinstance(words, list) else words["words"]
DUR = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                            "assets/cut.mp4"], capture_output=True, text=True).stdout)
DUR = round(DUR - 0.04, 2)
norm = {"five": "5"}
def disp(t):
    t = re.sub(r"[.,?!]+$", "", t)
    return norm.get(t.lower(), t).upper()

def find(phrase, after=0):
    toks = [norm.get(p, p) for p in phrase.lower().split()]
    for i in range(after, len(words)):
        seg = [disp(w["text"]).lower() for w in words[i:i + len(toks)]]
        if seg == toks: return list(range(i, i + len(toks)))
    raise SystemExit(f"phrase not found: {phrase}")
def at(phrase, after=0): return words[find(phrase, after)[0]]["start"]
def end(phrase, after=0): return words[find(phrase, after)[-1]]["end"]

# ---------- captions (unchanged behaviour: 2-3 words, yellow keyword phrases kept together) ----------
YELLOW = ["5 to 10 roofs", "garbage", "don't pay me", "afford a roof", "no monthly retainers",
          "pay per estimate", "exclusive", "your calendar", "one roofing contractor per area"]
hl, phrase_of, phrases = set(), {}, []
for p in YELLOW:
    ix = find(p); phrases.append(ix); hl.update(ix)
    for i in ix: phrase_of[i] = len(phrases) - 1
for i, w in enumerate(words):
    if disp(w["text"]) == "FACE-TO-FACE":
        hl.add(i); phrases.append([i]); phrase_of[i] = len(phrases) - 1

units, i = [], 0
while i < len(words):
    ph = phrase_of.get(i)
    if ph is not None and phrases[ph][0] == i:
        ix = phrases[ph]
        parts = [ix] if len(ix) <= 3 else ([ix[:3], ix[3:]] if len(ix) == 4 else [ix[:2], ix[2:]])
        for k, part in enumerate(parts): units.append((part, len(parts) == 1 or k == 0))
        i = ix[-1] + 1
    else:
        units.append(([i], False)); i += 1
groups, cur, cur_locked = [], [], False
for unit, atomic in units:
    if cur:
        prev = words[cur[-1]]
        brk = (len(cur) + len(unit) > 3 or re.search(r"[.,?!]$", prev["text"])
               or words[unit[0]]["start"] - prev["end"] > 0.25 or cur_locked or (atomic and len(unit) == 3))
        if brk: groups.append(cur); cur = []
    cur = cur + unit; cur_locked = atomic and len(unit) >= 2
groups.append(cur)
merged = []
for g in groups:
    if merged and len(g) == 1 and len(merged[-1]) < 3 and not re.search(r"[.,?!]$", words[merged[-1][-1]]["text"]):
        merged[-1] = merged[-1] + g
    else: merged.append(g)
groups = merged
G = []
for gi, g in enumerate(groups):
    s = words[g[0]]["start"]
    nxt = words[groups[gi + 1][0]]["start"] if gi + 1 < len(groups) else DUR
    e = nxt if nxt - words[g[-1]]["end"] < 0.6 else words[g[-1]]["end"] + 0.35
    G.append((g, round(s, 3), round(min(e, DUR), 3)))

# ---------- section headlines (top bar) ----------
t_offer, t_how, t_recap, t_end = at("stop buying"), at("here's how"), at("if you want"), at("click the button")
HEADS = [(0.0, t_offer, '<span class="ln red">ATTENTION</span><span class="ln red">ROOFERS <span class="emo">🚨</span></span>', "alarm"),
         (t_offer, t_how, '<span class="ln">NO LEADS =</span><span class="ln yel">NO PAY</span>', ""),
         (t_how, t_recap, '<span class="ln">WE BOOK.</span><span class="ln yel">YOU CLOSE.</span>', ""),
         (t_recap, t_end, '<span class="ln">NO LEADS =</span><span class="ln yel">NO PAY</span>', ""),
         (t_end, DUR, '<span class="ln yel">1 ROOFER</span><span class="ln yel">PER AREA <span class="emo">⚠️</span></span>', "")]
# Small tags under the headline (the earlier pop-ups).
TAGS = [("NO RETAINERS", at("no monthly retainers"), at("only pay per estimate") - 0.05),
        ("PAY PER ESTIMATE", at("only pay per estimate"), at("here's how") - 0.05)]

# ---------- b-roll cutaways over the picture box ----------
ff1 = find("face-to-face")[0]; ff2 = find("face-to-face", ff1 + 1)[0]
BROLL = [("trash", at("garbage"), at("don't pay me")),
         ("hands", words[ff1 - 1]["start"], words[ff1 + 1]["end"]),
         ("house", at("homeowners who can"), end("afford a roof") + 0.05),
         ("phone", at("call them ourselves"), end("call them ourselves") + 0.6),
         ("calendar", at("book them directly"), end("into your calendar") + 0.1),
         ("hands2", words[ff2]["start"] - 0.1, words[ff2 + 2]["end"] + 0.05)]
BROLL = [(k, round(s, 3), round(e, 3)) for k, s, e in BROLL]

# ---------- punch-in zooms on the picture (never during b-roll) ----------
ZOOMS = [(at("stop buying"), at("garbage") - 0.02, 1.12), (at("don't pay me"), end("anything"), 1.12),
         (at("only pay per estimate"), end("only pay per estimate"), 1.12),
         (at("financially qualified"), end("financially qualified"), 1.08),
         (at("all sifting through"), end("all the dirt"), 1.08),
         (at("high intent homeowner"), end("homeowner estimates"), 1.08),
         (at("one roofing contractor"), DUR, 1.12)]
for a, b, _ in ZOOMS:
    for k, s, e in BROLL: assert b <= s + 0.01 or a >= e - 0.01, f"zoom {a}-{b} overlaps b-roll {k}"

# ---------- sound effects ----------
SFX = [("siren", 0.0, 0.09), ("impact", 0.0, 0.12)]
for a, b, _ in ZOOMS: SFX.append(("whoosh", max(0, a - 0.12), 0.22))
for k, s, e in BROLL:
    SFX.append(("whoosh", max(0, s - 0.12), 0.24))
    if e < DUR - 0.2: SFX.append(("whoosh-short", e - 0.1, 0.18))
kaching = at("pay per estimate")
pops = sorted({round(words[p[0]]["start"], 3) for p in phrases})
for t in pops:
    if abs(t - kaching) > 0.15: SFX.append(("pop", t, 0.3))
SFX += [("kaching", kaching, 0.4), ("notify", at("book them directly") + 0.35, 0.3), ("ping", at("your calendar"), 0.3)]
SFX.sort(key=lambda x: x[1])
SRC = {"siren": "sfx-siren.wav", "impact": "sfx-impact.mp3", "whoosh": "sfx-whoosh.mp3",
       "whoosh-short": "sfx-whoosh-short.mp3", "pop": "sfx-pop.mp3", "kaching": "sfx-kaching.wav",
       "notify": "sfx-notify.mp3", "ping": "sfx-ping.mp3"}
LEN = {k: float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                f"assets/{v}"], capture_output=True, text=True).stdout) for k, v in SRC.items()}

CTA_START = at("as we only work")

# ---------- HTML ----------
cap_html = []
for gi, (g, s, e) in enumerate(G):
    ws = "".join(f'<span class="w{" hl" if i in hl else ""}" id="w{i}">{html.escape(disp(words[i]["text"]))}</span>' for i in g)
    cap_html.append(f'        <div class="cg" id="cg-{gi}">{ws}</div>')
head_html = [f'      <div class="clip head" id="head-{k}" data-start="{s:.3f}" data-duration="{e - s:.3f}" data-track-index="3">'
             f'<div class="head-in{" " + c if c else ""}" id="headin-{k}">{h}</div></div>' for k, (s, e, h, c) in enumerate(HEADS)]
tag_html = [f'      <div class="clip tag" id="tag-{k}" data-start="{s:.3f}" data-duration="{e - s:.3f}" data-track-index="4">'
            f'<span class="pill" id="pill-{k}">{t}</span></div>' for k, (t, s, e) in enumerate(TAGS)]
sfx_html = []
for n, (k, s, v) in enumerate(SFX):
    d = min(LEN[k], DUR - s)
    sfx_html.append(f'    <audio id="sfx-{n}" src="assets/{SRC[k]}" data-start="{s:.3f}" data-duration="{d:.3f}" '
                    f'data-track-index="{8 + n}" data-volume="{v}"></audio>')

def scene(kind, pid):
    if kind == "trash":
        cards = "".join(f'<div class="lead" id="{pid}-c{i}">LEAD</div>' for i in range(5))
        return (f'<div class="bg" style="background:radial-gradient(circle at 50% 40%,#5a1010,#1a0505)"></div>'
                f'<div class="label" id="{pid}-lb">SHARED LEADS = <span class="yel">TRASH</span></div>{cards}'
                f'<div class="bin" id="{pid}-bin"><div class="lid" id="{pid}-lid"></div><div class="can">'
                f'<i></i><i></i><i></i></div></div><div class="stamp" id="{pid}-x">✕</div>')
    if kind == "house":
        return (f'<div class="bg" style="background:linear-gradient(#5ab8ff,#bfe6ff 70%)"></div>'
                f'<div class="sun" id="{pid}-sun"></div><div class="lawn"></div>'
                f'<div class="tree" style="left:150px"></div><div class="tree" style="left:820px"></div>'
                f'<div class="house" id="{pid}-h"><div class="roof" id="{pid}-roof"></div><div class="walls">'
                f'<div class="win" style="left:70px"></div><div class="win" style="right:70px"></div>'
                f'<div class="door"></div></div></div>'
                f'<div class="check" id="{pid}-ok">✓</div>'
                f'<div class="label dark" id="{pid}-lb">HOMEOWNERS WHO CAN <span class="grn">AFFORD IT</span></div>')
    if kind == "phone":
        rings = "".join(f'<div class="ring" id="{pid}-r{i}"></div>' for i in range(3))
        return (f'<div class="bg" style="background:radial-gradient(circle at 50% 45%,#2b3fb8,#0b1240)"></div>{rings}'
                f'<div class="phone" id="{pid}-ph"><div class="scr"><div class="ava">🏠</div>'
                f'<div class="who">HOMEOWNER</div><div class="calling" id="{pid}-st">calling…</div>'
                f'<div class="btns"><span class="b red"></span><span class="b green" id="{pid}-ans"></span></div></div></div>'
                f'<div class="label" id="{pid}-lb">WE CALL <span class="yel">EVERY LEAD</span></div>')
    if kind == "calendar":
        cells = []
        for i in range(20):
            chip = (f'<div class="chip" id="{pid}-k{i}">EST {8 + i % 5}AM</div>' if i in (1, 3, 6, 8, 10, 12, 15, 17, 19) else "")
            cells.append(f'<div class="cell"><b>{i + 1 + (i // 5) * 2}</b>{chip}</div>')
        return (f'<div class="bg" style="background:linear-gradient(135deg,#0f3d2e,#062018)"></div>'
                f'<div class="cal" id="{pid}-cal"><div class="calhd">YOUR CALENDAR</div>'
                f'<div class="days"><span>MON</span><span>TUE</span><span>WED</span><span>THU</span><span>FRI</span></div>'
                f'<div class="grid">{"".join(cells)}</div></div>'
                f'<div class="label" id="{pid}-lb"><span class="grn">9 ESTIMATES</span> BOOKED</div>')
    if kind.startswith("hands"):
        return (f'<div class="bg" style="background:radial-gradient(circle at 50% 50%,#ff9b2f,#b54a00)"></div>'
                f'<div class="burst" id="{pid}-bu"></div>'
                f'<div class="person" id="{pid}-p1"><div class="hat"></div><div class="hd"></div><div class="bd" style="background:#1d4ed8"></div><div class="nm">ROOFER</div></div>'
                f'<div class="person" id="{pid}-p2"><div class="hd"></div><div class="bd" style="background:#15803d"></div><div class="nm">HOMEOWNER</div></div>'
                f'<div class="shake" id="{pid}-hs">🤝</div>'
                f'<div class="label" id="{pid}-lb"><span class="yel">FACE-TO-FACE</span> MEETINGS</div>')
broll_html = [f'      <div class="clip broll" id="br-{k}" data-start="{s:.3f}" data-duration="{e - s:.3f}" data-track-index="2">'
              f'<div class="br-in" id="brin-{k}">{scene(k, "br-" + k)}</div></div>' for k, s, e in BROLL]
money_t = kaching
money = "".join(f'<div class="cash" id="cash-{i}" style="left:{x}px">💵</div>' for i, x in enumerate([20, 175, 330, 475, 620, 775, 930]))
money_html = f'      <div class="clip money" id="money" data-start="{money_t:.3f}" data-duration="1.400" data-track-index="5">{money}</div>'

data = {"groups": [{"words": g, "start": s, "end": e} for g, s, e in G],
        "words": [{"start": round(w["start"], 3), "end": round(w["end"], 3)} for w in words],
        "zooms": [[round(a, 3), round(b, 3), z] for a, b, z in ZOOMS],
        "heads": [[round(s, 3), round(e, 3)] for s, e, _, _ in HEADS],
        "tags": [[round(s, 3), round(e, 3)] for _, s, e in TAGS],
        "broll": [[k, s, e] for k, s, e in BROLL], "money": round(money_t, 3), "cta": round(CTA_START, 3), "dur": DUR}

tpl = open("tools/index.template.html").read()
rep = {"{{DUR}}": f"{DUR}", "{{CAPTIONS}}": "\n".join(cap_html), "{{HEADS}}": "\n".join(head_html),
       "{{TAGS}}": "\n".join(tag_html), "{{BROLL}}": "\n".join(broll_html), "{{MONEY}}": money_html,
       "{{SFX}}": "\n".join(sfx_html), "{{DATA}}": json.dumps(data),
       "{{CTA_START}}": f"{CTA_START:.3f}", "{{CTA_DUR}}": f"{DUR - CTA_START:.3f}"}
for k, v in rep.items(): tpl = tpl.replace(k, v)
open("index.html", "w").write(tpl)

# Pacing report: every on-screen/sound change, flagging gaps over 3s.
ev = sorted({0.0, *[s for s, *_ in HEADS], *[s for _, s, _ in TAGS], *[s for _, s, _ in BROLL],
             *[e for _, _, e in BROLL], *[a for a, _, _ in ZOOMS], *[b for _, b, _ in ZOOMS], *pops, CTA_START, kaching})
gaps = [(round(a, 2), round(b - a, 2)) for a, b in zip(ev, ev[1:] + [DUR]) if b - a > 3]
print(f"duration {DUR}s | {len(G)} caption groups | {len(SFX)} sfx | b-roll {BROLL}")
print("headlines", [(round(s, 2), re.sub('<[^>]+>', '', h)) for s, _, h, _ in HEADS])
print("gaps > 3s:", gaps or "none")
