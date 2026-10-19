"""Build index.html for roofing ad #2 from transcript.json of assets/cut.mp4.

Layout (1080x1920): native 1080x1024 picture in the middle (y 448-1472), section headlines in
the top bar, captions + CTA in the bottom bar, motion-graphic b-roll over the picture box.
"""
import json, re, subprocess, html
raw = json.load(open("transcript.json"))
raw = raw if isinstance(raw, list) else raw["words"]
probe = lambda f: float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                                       capture_output=True, text=True).stdout)
DUR = round(probe("assets/cut.mp4") - 0.04, 2)

# Display tokens: normalise spellings and merge spoken money amounts into one caption token.
NORM = {"angie": "ANGI", "three": "3", "six": "6", "seven": "7"}
MERGE = {("seventy", "thousand", "dollars"): "$70K", ("4", "million", "dollars"): "$4 MILLION"}
def clean(t): return re.sub(r"[.,?!]+$", "", t).lower()
words, i = [], 0
while i < len(raw):
    for seq, txt in MERGE.items():
        if tuple(clean(w["text"]) for w in raw[i:i + len(seq)]) == seq:
            words.append({"text": txt, "start": raw[i]["start"], "end": raw[i + len(seq) - 1]["end"]}); i += len(seq); break
    else:
        t = clean(raw[i]["text"]); words.append({"text": NORM.get(t, t.upper()), "start": raw[i]["start"], "end": raw[i]["end"]}); i += 1
for w in words: w["text"] = w["text"].upper()

def find(phrase, after=0):
    target = " ".join(NORM.get(p, p).upper() for p in phrase.lower().split())
    for i in range(after, len(words)):
        txt = ""
        for j in range(i, min(i + 8, len(words))):
            txt = (txt + " " + words[j]["text"]).strip()
            if txt == target: return list(range(i, j + 1))
            if not target.startswith(txt): break
    raise SystemExit(f"phrase not found: {phrase}")
def at(p, after=0): return words[find(p, after)[0]]["start"]
def end(p, after=0): return words[find(p, after)[-1]]["end"]

# Sentence/clause ends (this transcript came back without punctuation).
ENDS = set()
for p in ["roofing companies", "knocking is dead", "angi is dead", "every single day", "handle everything", "the marketing",
          "the ads", "lead qualification", "appointment setting", "and follow-up", "up and closes", "ready to buy",
          "cheapest price", "first 7 days", "14 months", "qualified appointments", "still available"]:
    ENDS.add(find(p)[-1])

# ---------- captions: 2-3 words, yellow keyword phrases kept together ----------
YELLOW = ["door knocking is dead", "angi is dead", "three to six", "every single day", "we handle everything",
          "shows up and closes", "ready to buy", "$70k", "7 days", "$4 million", "14 months", "booked solid", "learn more"]
hl, phrase_of, phrases = set(), {}, []
for p in YELLOW:
    ix = find(p); phrases.append(ix); hl.update(ix)
    for i in ix: phrase_of[i] = len(phrases) - 1

units, i = [], 0
while i < len(words):
    ph = phrase_of.get(i)
    if ph is not None and phrases[ph][0] == i:
        ix = phrases[ph]
        parts = [ix] if len(ix) <= 3 else ([ix[:2], ix[2:]] if len(ix) == 4 else [ix[:2], ix[2:]])
        for k, part in enumerate(parts): units.append((part, True))
        i = ix[-1] + 1
    else:
        units.append(([i], False)); i += 1
groups, cur, cur_locked = [], [], False
for unit, atomic in units:
    if cur:
        brk = (len(cur) + len(unit) > 3 or cur[-1] in ENDS or words[unit[0]]["start"] - words[cur[-1]]["end"] > 0.25
               or cur_locked or (atomic and len(unit) == 3))
        if brk: groups.append(cur); cur = []
    cur = cur + unit; cur_locked = atomic and len(unit) >= 2
groups.append(cur)
merged = []
for g in groups:
    if merged and len(g) == 1 and len(merged[-1]) < 3 and merged[-1][-1] not in ENDS and g[0] not in hl:
        merged[-1] = merged[-1] + g
    else: merged.append(g)
groups = merged
G = []
for gi, g in enumerate(groups):
    s = words[g[0]]["start"]
    nxt = words[groups[gi + 1][0]]["start"] if gi + 1 < len(groups) else DUR
    e = nxt if nxt - words[g[-1]]["end"] < 0.6 else words[g[-1]]["end"] + 0.35
    G.append((g, round(s, 3), round(min(e, DUR), 3)))

# ---------- section headlines (top bar), each a list of lines ----------
E = lambda c: f'<span class="emo">{c}</span>'
t_dead, t_sys, t_all, t_res, t_end = at("door knocking"), at("we have built"), at("and we handle"), at("one of our partners"), at("so if you want")
HEADS = [(0.0, t_dead, ["ATTENTION", "ROOFING", f"COMPANIES {E('🚨')}"], "red", 100),
         (t_dead, t_sys, ["OLD WAYS", f"ARE DEAD {E('❌')}"], "", 118),
         (t_sys, t_all, ["3-6 APPOINTMENTS", f"/ DAY {E('📅')}"], "", 84),
         (t_all, t_res, ["WE DO IT ALL.", '<span class="yel">YOU CLOSE.</span>'], "", 104),
         (t_res, t_end, ["REAL", f"RESULTS {E('💰')}"], "yel", 118),
         (t_end, DUR, ["IS YOUR MARKET", f"AVAILABLE? {E('⚠️')}"], "", 94)]

# ---------- b-roll: (kind, start, end, overlay?) ; overlays sit on a dimmed, punched-in picture ----------
BROLL = [("door", at("door knocking"), at("angi is dead") - 0.02, True),
         ("leadsite", at("angi is dead"), at("we have built") - 0.05, True),
         ("calendar", at("on your sales"), at("every single day") - 0.03, False),
         ("checklist", at("the marketing"), at("your team just") - 0.06, False),
         ("house", at("who is ready") - 0.1, end("ready to buy") + 0.35, False),
         ("count70", at("$70k"), at("another closed") - 0.06, True),
         ("count4m", at("over $4 million"), at("so if you") - 0.06, True),
         ("booked", at("keep your sales"), end("booked solid") + 0.25, False)]
BROLL = [(k, round(s, 3), round(e, 3), o) for k, s, e, o in BROLL]
CHECK_ITEMS = [("MARKETING", at("the marketing", 0) + 0.1), ("ADS", at("the ads")), ("LEAD QUALIFICATION", at("lead qualification")),
               ("APPOINTMENT SETTING", at("appointment setting")), ("FOLLOW-UP", at("follow-up"))]
DEAD_T = [words[find("knocking is dead")[-1]]["start"], words[find("angi is dead")[-1]]["start"]]
COUNT_END = {"count70": end("$70k") + 0.15, "count4m": end("$4 million") + 0.15}

# ---------- punch-in zooms ----------
ZOOMS = [(at("door knocking"), at("we have built") - 0.05, 1.13),
         (at("three to six"), end("roofing appointments"), 1.13),
         (at("every single day"), end("every single day"), 1.06),
         (at("your team just"), end("shows up and closes"), 1.13),
         (at("$70k"), at("another closed") - 0.06, 1.13),
         (at("over $4 million"), at("so if you") - 0.06, 1.13)]
for a, b, _ in ZOOMS:
    for k, s, e, o in BROLL:
        assert o or b <= s + 0.01 or a >= e - 0.01, f"zoom {a}-{b} hidden by cutaway {k}"

# ---------- sound effects ----------
SFX = [("siren", 0.0, 0.09), ("impact", 0.0, 0.12)]
for t in DEAD_T: SFX.append(("buzzer", t, 0.14))
whooshes = sorted({round(max(0, a - 0.12), 2) for a, _, _ in ZOOMS} | {round(max(0, s - 0.12), 2) for _, s, _, _ in BROLL})
for t in whooshes: SFX.append(("whoosh", t, 0.22))
for k, s, e, o in BROLL:
    if not o and e < DUR - 0.2: SFX.append(("whoosh-short", e - 0.1, 0.16))
pop_t = sorted({round(words[p[0]]["start"], 3) for p in phrases} | {round(t, 3) for _, t in CHECK_ITEMS})
busy = DEAD_T + list(COUNT_END.values())
for t in pop_t:
    if all(abs(t - b) > 0.15 for b in busy): SFX.append(("pop", t, 0.28))
for k in COUNT_END: SFX.append(("kaching", COUNT_END[k], 0.35))
SFX += [("notify", at("on your sales") + 0.35, 0.28), ("notify", at("keep your sales") + 0.4, 0.28)]
SFX.sort(key=lambda x: x[1])
SRC = {"siren": "sfx-siren.wav", "impact": "sfx-impact.mp3", "whoosh": "sfx-whoosh.mp3", "whoosh-short": "sfx-whoosh-short.mp3",
       "pop": "sfx-pop.mp3", "kaching": "sfx-kaching.wav", "notify": "sfx-notify.mp3", "buzzer": "sfx-buzzer.wav"}
LEN = {k: probe(f"assets/{v}") for k, v in SRC.items()}
CTA_START = at("click learn more")

# ---------- HTML ----------
def fit_size(texts, width=960, gap=54, char=0.74):
    """Largest caption size (96 down to 60) whose greedy wrap stays within two lines."""
    for fs in range(96, 58, -4):
        lines, cur = 1, 0
        for t in texts:
            w = len(t) * char * fs * 1.06  # 1.06: room for the active-word pop
            if cur and cur + gap + w > width: lines, cur = lines + 1, w
            else: cur = cur + (gap if cur else 0) + w
        if lines <= 2 and cur <= width: return fs
    return 60
cap_html = []
for gi, (g, s, e) in enumerate(G):
    ws = "".join(f'<span class="w{" hl" if i in hl else ""}" id="w{i}">{html.escape(words[i]["text"])}</span>' for i in g)
    fs = fit_size([words[i]["text"] for i in g])
    cap_html.append(f'        <div class="cg" id="cg-{gi}" style="font-size:{fs}px">{ws}</div>')
head_html = []
for k, (s, e, lines, cls, size) in enumerate(HEADS):
    ls = "".join(f'<span class="ln">{l}</span>' for l in lines)
    head_html.append(f'      <div class="clip head" id="head-{k}" data-start="{s:.3f}" data-duration="{e - s:.3f}" data-track-index="3">'
                     f'<div class="head-in {cls}" id="headin-{k}" style="font-size:{size}px">{ls}</div></div>')
sfx_html = [f'    <audio id="sfx-{n}" src="assets/{SRC[k]}" data-start="{s:.3f}" data-duration="{min(LEN[k], DUR - s):.3f}" '
            f'data-track-index="{8 + n}" data-volume="{v}"></audio>' for n, (k, s, v) in enumerate(SFX)]

def calendar(pid, booked):
    cells = []
    for i in range(20):
        on = booked or i in (1, 3, 6, 8, 10, 12, 15, 17, 19)
        chip = f'<div class="chip{" full" if booked else ""}" id="{pid}-k{i}">{"BOOKED" if booked else f"APPT {8 + i % 5}AM"}</div>' if on else ""
        cells.append(f'<div class="cell"><b>{i + 1 + (i // 5) * 2}</b>{chip}</div>')
    return (f'<div class="cal" id="{pid}-cal"><div class="calhd">{"FULLY BOOKED" if booked else "SALES REP CALENDAR"}</div>'
            f'<div class="days"><span>MON</span><span>TUE</span><span>WED</span><span>THU</span><span>FRI</span></div>'
            f'<div class="grid">{"".join(cells)}</div></div>')
def scene(kind, pid):
    if kind == "door":
        return (f'<div class="scrim"></div><div class="card" id="{pid}-card" style="background:linear-gradient(#3b2a1d,#1c130c)">'
                f'<div class="door"><div class="knob"></div><div class="panel" style="top:60px"></div><div class="panel" style="top:300px"></div></div>'
                f'<div class="bigx" id="{pid}-x">✕</div><div class="label" id="{pid}-lb">DOOR KNOCKING</div></div>')
    if kind == "leadsite":
        rows = "".join(f'<div class="row"><i></i><span></span><em>★★★☆☆</em></div>' for _ in range(4))
        return (f'<div class="scrim"></div><div class="card" id="{pid}-card" style="background:linear-gradient(#e5e7eb,#9ca3af)">'
                f'<div class="browser"><div class="bar"><i></i><i></i><i></i><span>leads-marketplace.com</span></div>'
                f'<div class="site"><div class="logo">LEADS<b>4</b>SALE</div>{rows}<div class="shared">SOLD TO 5 ROOFERS</div></div></div>'
                f'<div class="bigx" id="{pid}-x">✕</div><div class="label" id="{pid}-lb">SHARED LEAD SITES</div></div>')
    if kind == "calendar":
        return (f'<div class="bg" style="background:linear-gradient(135deg,#0f3d2e,#062018)"></div>{calendar(pid, False)}'
                f'<div class="label" id="{pid}-lb">ON YOUR REPS\' <span class="grn">CALENDARS</span></div>')
    if kind == "booked":
        return (f'<div class="bg" style="background:linear-gradient(135deg,#4c0519,#1a0108)"></div>{calendar(pid, True)}'
                f'<div class="label" id="{pid}-lb"><span class="yel">BOOKED SOLID</span></div>')
    if kind == "checklist":
        items = "".join(f'<div class="item" id="{pid}-i{n}"><span class="box" id="{pid}-b{n}">✓</span>{t}</div>' for n, (t, _) in enumerate(CHECK_ITEMS))
        return (f'<div class="bg" style="background:linear-gradient(160deg,#1e3a8a,#0b1437)"></div>'
                f'<div class="cltitle" id="{pid}-tt">WE HANDLE <span class="yel">EVERYTHING</span></div><div class="list">{items}</div>')
    if kind == "house":
        return (f'<div class="bg" style="background:linear-gradient(#5ab8ff,#bfe6ff 70%)"></div><div class="sun" id="{pid}-sun"></div>'
                f'<div class="lawn"></div><div class="tree" style="left:140px"></div><div class="tree" style="left:810px"></div>'
                f'<div class="house" id="{pid}-h"><div class="roof" id="{pid}-roof"></div><div class="walls">'
                f'<div class="win" style="left:70px"></div><div class="win" style="right:70px"></div><div class="hdoor"></div></div></div>'
                f'<div class="check" id="{pid}-ok">✓</div><div class="label" id="{pid}-lb"><span class="grn">READY TO BUY</span></div>')
    if kind.startswith("count"):
        cap = "IN THE FIRST 7 DAYS" if kind == "count70" else "IN JUST 14 MONTHS"
        return (f'<div class="scrim"></div><div class="card money-card" id="{pid}-card">'
                f'<div class="ctop">PARTNER CLOSED</div><div class="num" id="{pid}-n" style="font-size:{118 if kind == "count4m" else 150}px">$0</div>'
                f'<div class="csub" id="{pid}-sub">{cap}</div></div>')
broll_html = [f'      <div class="clip broll" id="br-{k}" data-start="{s:.3f}" data-duration="{e - s:.3f}" data-track-index="2">'
              f'<div class="br-in" id="brin-{k}">{scene(k, "br-" + k)}</div></div>' for k, s, e, o in BROLL]

data = {"groups": [{"words": g, "start": s, "end": e} for g, s, e in G],
        "words": [{"start": round(w["start"], 3), "end": round(w["end"], 3)} for w in words],
        "zooms": [[round(a, 3), round(b, 3), z] for a, b, z in ZOOMS],
        "heads": [[round(s, 3), round(e, 3)] for s, e, *_ in HEADS],
        "broll": [[k, s, e, o] for k, s, e, o in BROLL],
        "checks": [round(t, 3) for _, t in CHECK_ITEMS], "dead": [round(t, 3) for t in DEAD_T],
        "counts": {"count70": [70000, round(COUNT_END["count70"], 3)], "count4m": [4000000, round(COUNT_END["count4m"], 3)]},
        "cta": round(CTA_START, 3), "dur": DUR}
tpl = open("tools/index.template.html").read()
rep = {"{{DUR}}": f"{DUR}", "{{CAPTIONS}}": "\n".join(cap_html), "{{HEADS}}": "\n".join(head_html),
       "{{BROLL}}": "\n".join(broll_html), "{{SFX}}": "\n".join(sfx_html), "{{DATA}}": json.dumps(data),
       "{{CTA_START}}": f"{CTA_START:.3f}", "{{CTA_DUR}}": f"{DUR - CTA_START:.3f}"}
for k, v in rep.items(): tpl = tpl.replace(k, v)
open("index.html", "w").write(tpl)

ev = sorted({0.0, *[h[0] for h in HEADS], *[s for _, s, _, _ in BROLL], *[e for _, _, e, _ in BROLL], *[a for a, _, _ in ZOOMS],
             *[b for _, b, _ in ZOOMS], *pop_t, CTA_START})
gaps = [(round(a, 2), round(b - a, 2)) for a, b in zip(ev, ev[1:] + [DUR]) if b - a > 3]
print(f"duration {DUR}s | {len(G)} caption groups | {len(SFX)} sfx")
print("b-roll", [(k, s, e) for k, s, e, _ in BROLL])
print("heads", [(round(h[0], 2), re.sub("<[^>]+>", "", " ".join(h[2]))) for h in HEADS])
print("gaps > 3s:", gaps or "none")
for g, s, e in G: print(f"  {s:6.2f}-{e:6.2f} " + " ".join(("*" if i in hl else "") + words[i]["text"] for i in g))
