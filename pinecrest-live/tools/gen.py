"""Build the Pinecrest live-action ad (9:16) from the cut presenter take, the truck video and stock stand-ins.

Follows the line-by-line blueprint: the presenter take is the base layer (jump-cut punch levels),
B-roll cuts land on the stressed word of each line, mute-first text sits inside the Meta safe zone
(y 300-1220), and every SFX is anchored to a word. Times come from transcript.json of assets/aroll.mp4.
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

shot(P + "c093-aerial.jpg", 0.0, T["texas"], "push-fast", x=0.5)                                      # drone-style open
shot(P + "hail-hole.jpg", T["thousands"], T["and_"], "push", x=0.7, snaps=[(T["thousands"] + 0.02, 1.12)])
shot(P + "house-brick-2.jpg", T["down"], T["but"], "tilt-up", x=0.58)
shot(P + "fema-c005.jpg", T["but"], T["interior"], "push", x=0.45, enter="whip-up", snaps=[(T["glaring"], 1.12)])
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
shot("assets/truck.mov", T["pine"], T["we_value"], "push", x=0.5, ss=25.0, snaps=[(T["pine"] + 0.02, 1.12)], enter="flash")
shot("assets/truck.mov", T["we_value"], T["end_honesty"] + 0.3, "push", x=0.5, ss=9.0, snaps=[(T["we_value"] + 0.02, 1.2)])
shot(P + "fema-c063.jpg", T["we_get"], T["take"], "push", x=0.5)
shot(P + "hail-doc-1.jpg", T["take"], T["show_you"], "push", x=0.72, snaps=[(T["photos"] + 0.02, 1.1)])
shot(B + "showing-laptop--mixkit-4904-1080p.mp4", T["show_you"], T["exactly"] + 0.38, "push", x=0.55, ss=2)
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

# ---------------- mute-first text (safe zone y 300-1220) ----------------
POPS = [  # (html, start, end, style)
    ('NORTH TEXAS <span class="emo">👇</span>', 0.0, T["most"] - 0.25, "hook"),
    ('BEFORE YOU SPEND <span class="red">$30,000</span>', T["most"] - 0.25, T["could"] - 0.4, "hook2"),
    ('<span class="emo">🚩</span> STORM CHASERS', T["oos"], T["that_need"] + 0.85, "pill red"),
    ('<span class="emo">📸</span> FULL PHOTO REPORT', T["take"], T["exactly"] + 0.38, "pill"),
    ('<span class="emo">🤝</span> NO DAMAGE? WE\'LL TELL YOU.', T["exactly"] + 0.38, T["exactly"] + 0.38 + 2.3, "pill green"),
]
for k, (txt, a, b, kind) in enumerate(POPS):
    el.append(f'<div class="clip pop" id="pop{k}" data-start="{a:.3f}" data-duration="{b - a:.3f}" data-track-index="20"><div class="{kind}" id="pl{k}">{txt}</div></div>')
    js.append(f'tl.fromTo("#pl{k}", {{opacity: 0, scale: 1.2}}, {{opacity: 1, scale: 1, duration: 0.13, ease: "power3.out"}}, {a:.3f});')
# Damage list builds one item per cut (lines 11-19 s).
DLIST = [("LEAKS", T["interior"] + 0.22), ("MOLD", T["black"]), ("HAIL HITS", T["routine"]), ("CRACKED SHINGLES", T["damage2"] + 0.7)]
items = "".join(f'<div class="dl" id="dl{k}">{html.escape(t)}</div>' for k, (t, _) in enumerate(DLIST))
el.append(f'<div class="clip dlist" id="dlist" data-start="{DLIST[0][1]:.3f}" data-duration="{T["good"] - DLIST[0][1]:.3f}" data-track-index="21">{items}</div>')
for k, (_, t) in enumerate(DLIST):
    js.append(f'tl.fromTo("#dl{k}", {{opacity: 0, x: -40}}, {{opacity: 1, x: 0, duration: 0.15, ease: "power3.out"}}, {t:.3f});')
# Insurance disclaimer.
el.append(f'<div class="clip disc" id="disc" data-start="{T["all_"]:.3f}" data-duration="{T["nt2"] - T["all_"]:.3f}" data-track-index="22">Coverage depends on your policy.</div>')
# Pinecrest brand reveal over the truck.
el.append(f'<div class="clip brand" id="brand" data-start="{T["pine"]:.3f}" data-duration="{T["we_value"] - T["pine"]:.3f}" data-track-index="23">'
          f'<div class="brandin" id="brandin"><div class="b1">PINECREST</div><div class="b2">ROOFING &amp; CONSTRUCTION</div><i id="sweep"></i></div></div>')
js.append(f'tl.fromTo("#brandin", {{opacity: 0, scale: 1.15}}, {{opacity: 1, scale: 1, duration: 0.16, ease: "power3.out"}}, {T["pine"]:.3f});')
js.append(f'tl.fromTo("#sweep", {{xPercent: -120}}, {{xPercent: 260, duration: 0.8, ease: "power2.inOut"}}, {T["pine"] + 0.3:.3f});')
# CTA block above the Meta button.
el.append(f'<div class="clip cta" id="cta" data-start="{T["tap"]:.3f}" data-duration="{DUR - T["tap"]:.3f}" data-track-index="24">'
          f'<div class="ctaname">PINECREST ROOFING &amp; CONSTRUCTION</div><div class="ctabtn" id="ctabtn">BOOK YOUR FREE INSPECTION <span class="emo">👇</span></div></div>')
js.append(f'tl.fromTo("#ctabtn", {{scale: 1.2, opacity: 0}}, {{scale: 1, opacity: 1, duration: 0.12, ease: "power3.out"}}, {T["tap"]:.3f});')

# Light leak at the two mood turns.
LEAKS = [(T["good"], B + "fx-lightleaks--mixkit-48495-720p.mp4"), (T["pine"], B + "fx-lightleaks2--mixkit-48011-720p.mp4")]
for k, (t, src) in enumerate(LEAKS):
    f = f"assets/prep/leak{k}.mp4"
    json.dump([dict(src=src, out=f, kind="video", ss=1 + k, dur=1.6, x=0.5)], open("assets/leak-job.json", "w"))
    subprocess.run([sys.executable, "tools/prep.py", "assets/leak-job.json"], check=True, stdout=subprocess.DEVNULL)
    el.append(f'<div class="leak" id="lk{k}"><video id="lkv{k}" class="clip media" src="{f}" muted playsinline data-start="{t - 0.3:.3f}" data-duration="1.4" data-track-index="{12 + k}"></video></div>')
    js.append(f'tl.fromTo("#lk{k}", {{opacity: 0}}, {{opacity: 0.75, duration: 0.3}}, {t - 0.3:.3f});')
    js.append(f'tl.to("#lk{k}", {{opacity: 0, duration: 0.6}}, {t + 0.5:.3f});')
# "Good news" grade lift.
js.append(f'tl.fromTo("#lift", {{opacity: 0}}, {{opacity: 1, duration: 0.2}}, {T["good"]:.3f});')
js.append(f'tl.to("#lift", {{opacity: 0, duration: 0.3}}, {T["nt2"] - 0.3:.3f});')
# Grain.
frames = int(DUR * 30)
js.append(f'tl.fromTo("#grain", {{backgroundPosition: "0px 0px"}}, {{backgroundPosition: "{frames * 337 % 1024}px {frames * 211 % 1024}px", duration: {DUR}, ease: "steps({frames})"}}, 0);')

# ---------------- captions: 2-3 words, yellow/red keywords, insurance line corrected on screen ----------------
YEL = ["north texas", "no idea", "thousands", "down here", "fine", "up here", "interior leaks", "roof inspection", "visible",
       "good news", "covered", "insurance", "hail alley", "too many", "out-of-state", "storm", "pine crest", "honesty", "your roof",
       "photos", "exactly", "real condition", "below", "free inspection"]
RED = ["damages", "glaring", "black mold", "grapefruit", "taken advantage of", "force you", "don't need"]
color = {}
for lst, c in ((YEL, "y"), (RED, "r")):
    for p in lst:
        st = 0
        while True:
            try: ix = find(p, st)
            except SystemExit: break
            for i in ix: color[i] = c
            st = ix[-1] + 1
ia = find("all of it's")[0]
OVERRIDE = {ia: "OFTEN", ia + 1: None, ia + 2: None}          # "All of it's covered" -> "OFTEN COVERED" on screen
color[ia] = "y"
def disp(i):
    if i in OVERRIDE: return OVERRIDE[i]
    t = clean(words[i]["text"]).upper()
    if t == "PINE" and clean(words[i + 1]["text"]) == "crest": return "PINECREST"
    if t == "CREST" and clean(words[i - 1]["text"]) == "pine": return None
    return re.sub(r"[.,?!]+$", "", words[i]["text"]).upper()
groups, cur = [], []
for i, w in enumerate(words):
    if cur:
        prev = words[cur[-1]]
        inside = color.get(i) and color.get(cur[-1]) and w["start"] - prev["end"] < 0.12 and len(cur) < 3
        brk = len(cur) >= 3 or re.search(r"[.,?!]$", prev["text"]) or w["start"] - prev["end"] > 0.25
        if brk and not (inside and not re.search(r"[.,?!]$", prev["text"])): groups.append(cur); cur = []
    cur.append(i)
groups.append(cur)
merged = []   # fold single-word stragglers into the previous caption (fast talker: keeps each card on screen long enough to read)
for g in groups:
    if merged and len([i for i in g if disp(i)]) <= 1 and len(merged[-1]) <= 3: merged[-1] = merged[-1] + g
    else: merged.append(g)
groups = merged
GAP_EM = 0.6
def text_units(t):
    """Approximate width in em of Montserrat 900 caps."""
    return sum(0.3 if c == " " else 0.32 if c in ".,'-?!" else 1.0 if c in "MW" else 0.42 if c in "I1" else 0.8 for c in t)
cap = []
for gi, g in enumerate(groups):
    vis = [i for i in g if disp(i)]
    s0 = words[g[0]]["start"]; nxt = words[groups[gi + 1][0]]["start"] if gi + 1 < len(groups) else DUR
    e0 = DUR if gi == len(groups) - 1 else min(nxt, words[g[-1]]["end"] + 0.45, DUR)
    ws = "".join(f'<span class="w{" " + color[i] if i in color else ""}" id="w{i}">{html.escape(disp(i))}</span>' for i in vis)
    em = sum(text_units(disp(i)) for i in vis) + GAP_EM * (len(vis) - 1)
    fs = int(min(84, 940 / 1.12 / em))                       # 1.12: the active-word pop
    wrap = ""
    if fs < 60 and len(vis) > 2:                              # too long for one readable line: two lines instead
        fs, wrap = int(min(70, 940 / 1.12 / (em / 2 + GAP_EM))), "; flex-wrap: wrap; line-height: 1.02"
    cap.append(f'<div class="cg" id="cg{gi}"><div class="line" style="font-size:{fs}px{wrap}">{ws}</div></div>')
    js.append(f'tl.fromTo("#cg{gi}", {{opacity: 0, scale: 0.88}}, {{opacity: 1, scale: 1, duration: 0.08, ease: "power2.out"}}, {s0:.3f});')
    for i in vis:
        c = {"y": ', color: "#ffd60a"', "r": ', color: "#ff3b30"'}.get(color.get(i), "")
        js.append(f'tl.fromTo("#w{i}", {{opacity: 0.6, scale: 1, color: "#ffffff"}}, {{opacity: 1, scale: {1.12 if i in color else 1.05}, duration: 0.07{c}}}, {words[i]["start"]:.3f});')
        js.append(f'tl.to("#w{i}", {{scale: 1, duration: 0.1}}, {max(words[i]["start"] + 0.07, words[i]["end"]):.3f});')
    js.append(f'tl.to("#cg{gi}", {{opacity: 0, duration: 0.05}}, {e0 - 0.05:.3f});')
    js.append(f'tl.set("#cg{gi}", {{opacity: 0, visibility: "hidden"}}, {e0:.3f});')

# ---------------- sound design (all under the voice) ----------------
fx("whoosh", 0.0, 0.18); fx("impact", T["texas"], 0.22); fx("kaching", T["most"] - 0.2, 0.2)
fx("crack", T["thousands"], 0.16); fx("beep", T["thousands"] + 1.2, 0.12)
fx("whoosh", T["but"] - 0.12, 0.32); fx("ladder", T["up"], 0.18)
fx("drip", T["interior"] + 0.22, 0.3); fx("creak", T["black"], 0.22); fx("scribble", T["routine"], 0.16); fx("crack", T["damage2"] + 0.7, 0.24)
fx("chime", T["covered"], 0.2)
fx("thunder", T["nt2"], 0.3); fx("hail", T["hail_alley"], 0.2); fx("ice", T["grape"], 0.3)
fx("warm", T["taken"], 0.25)
fx("peel", T["show"], 0.14); fx("scribble", T["force"], 0.28); fx("peel", T["that_need"], 0.24)
fx("whoosh", T["pine"] - 0.1, 0.3); fx("impact", T["we_value"], 0.16)
fx("ladder", T["we_get"], 0.24); fx("shutter", T["photos"], 0.35); fx("shutter", T["photos"] + 0.4, 0.3); fx("shutter", T["photos"] + 0.75, 0.3)
fx("warm", T["exactly"] + 0.38, 0.3)
fx("pop", T["tap"], 0.25); fx("notify", T["free"], 0.25)
for s in S:
    if s["enter"] == "cut" and s["t0"] > 0.1: fx("whoosh-short", s["t0"] - 0.06, 0.06)
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
