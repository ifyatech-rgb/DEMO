"""Build the Pinecrest Roofing 9:16 ad around the tightened voiceover.

Shot list -> prep jobs (tools/prep.py) -> index.html. Every shot names a media slot (MEDIA) so a
better clip can be swapped in without touching timing. Times come from transcript.json.
"""
import html, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
words = json.load(open("transcript.json"))
words = words if isinstance(words, list) else words["words"]
probe = lambda f: float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                                       capture_output=True, text=True).stdout)
VO_DUR = round(probe("assets/vo_tight.wav"), 2)
DUR = round(VO_DUR + 1.6, 2)          # end card holds after the last word

def clean(t): return re.sub(r"[.,?!]+$", "", t).lower()
def find(p, after=0):
    toks = p.lower().split()
    for i in range(after, len(words)):
        if [clean(w["text"]) for w in words[i:i + len(toks)]] == toks: return list(range(i, i + len(toks)))
    sys.exit(f"phrase not found: {p}")
def at(p, after=0): return round(words[find(p, after)[0]]["start"], 3)
def end(p, after=0): return round(words[find(p, after)[-1]]["end"], 3)

B, P = "broll/", "broll/photos/"
def ex(*paths):
    for p in paths:
        if p and os.path.exists(p): return p
    sys.exit(f"no media among {paths}")
# Media slots: first existing file wins (Commons finds are listed ahead of fallbacks).
MEDIA = {
    "house-wide":   dict(src=ex(P + "tx-house-1.jpg", P + "fema-c004.jpg"), x=0.3),
    "house-close":  dict(src=ex(P + "tx-house-2.jpg", P + "fema-c014.jpg"), x=0.62),
    "roof-street":  dict(src=ex(P + "tx-house-3.jpg", P + "house-ranch-tract.jpg"), x=0.3),
    "roof-detail":  dict(src=ex(P + "shingles.jpg", P + "cedar-damaged-1.jpg"), x=0.85),
    "look-up":      dict(src=ex(P + "cedar-damaged-2.jpg", P + "fema-c063.jpg"), x=0.62),
    "look-up-2":    dict(src=ex(P + "fema-c065.jpg"), x=0.75),
    "roof-level":   dict(src=ex(P + "housing-shingles-1.jpg", P + "fema-c005.jpg"), x=0.55),
    "roof-level-2": dict(src=ex(P + "fema-c005.jpg"), x=0.45),
    "hail-marks":   dict(src=ex(P + "hail-hole.jpg"), x=0.7),
    "cracked":      dict(src=ex(P + "cedar-damaged-1.jpg", P + "fema-c077.jpg"), x=0.42),
    "wood":         dict(src=ex(P + "rotten-wood-2.jpg", P + "fema-c049.jpg"), x=0.5),
    "attic-stain":  dict(src=ex(P + "ceiling-damage.jpg", B + "water-off-roof--mixkit-2716-1080p.mp4"), x=0.5, ss=1),
    "roof-bright":  dict(src=ex(P + "housing-shingles-2.jpg"), x=0.35),
    "roof-bright-2": dict(src=ex(P + "fema-c004.jpg"), x=0.75),
    "storm":        dict(src=B + "storm-powerlines--mixkit-16199-720p.mp4", x=0.5, ss=2),
    "hail":         dict(src=ex(P + "hailstones-field.jpg"), x=0.5),
    "storm-dark":   dict(src=B + "storm-lightning--mixkit-48918-720p.mp4", x=0.5, ss=1),
    "truck-arrive": dict(src=P + "fema-c014.jpg", x=0.3, vf="crop=iw*0.62:ih*0.5:0:ih*0.5"),
    "door":         dict(src=B + "handoff-door--mixkit-31137-2160p.mp4", x=0.35, ss=1),
    "signing":      dict(src=B + "signing-blue-ink--mixkit-38492-720p.mp4", x=0.55, ss=1),
    "truck-gone":   dict(src=P + "fema-c014.jpg", x=0.5, vf="crop=iw*0.75:ih*0.55:iw*0.25:ih*0.45"),
    "leak":         dict(src=ex(P + "ceiling-leak.jpg", P + "ceiling-damage.jpg"), x=0.3, vf="crop=iw:ih*0.6:0:0"),
    "pinecrest":    dict(src="assets/truck.mov", x=0.5, ss=24.2, hero=True),
    "ladder":       dict(src=ex(P + "ladder.jpg", P + "fema-c063.jpg"), x=0.5),
    "inspect":      dict(src=ex(P + "hail-doc-2.jpg"), x=0.4),
    "pictures":     dict(src=ex(P + "hail-doc-1.jpg"), x=0.72),
    "show":         dict(src=B + "showing-laptop--mixkit-4904-1080p.mp4", x=0.55, ss=2),
    "handshake":    dict(src=B + "handshake-office--mixkit-30005-2160p.mp4", x=0.55, ss=1),
    "finished":     dict(src=ex(P + "tx-house-4.jpg", P + "house-brick-2.jpg"), x=0.58),
}
for m in MEDIA.values(): m["kind"] = "video" if m["src"].endswith((".mp4", ".mov")) else "photo"

# Shot list: (slot, t0, t1, move) ; move = in | out | pan | push | still, plus optional snaps [(t, scale)] and enter.
S = []
def shot(slot, t0, t1, move="in", snaps=(), enter="cut", **kw): S.append(dict(slot=slot, t0=round(t0, 3), t1=round(t1, 3), move=move, snaps=list(snaps), enter=enter, **kw))

t_tx, t_30k = at("north texas"), at("$30,000")
t_most, t_th, t_dmg = at("most homeowners"), at("thousands of dollars"), at("damage")
t_and, t_from, t_but = at("and i get"), at("from down here"), at("but from up")
t_story, t_hail = at("it's a different"), at("hail hits")
t_crack, t_wood, t_leak = at("cracked shingles"), at("soft wood"), at("sometimes leaks") + 0.25
t_good, t_cov = at("the good news"), at("covered by your")
t_out, t_hail2, t_seen = at("but out here"), at("hail pretty much"), at("and we've seen")
t_taken, t_town, t_push, t_sign = at("taken advantage of"), at("out of town"), at("push you into"), at("signing")
t_gone, t_wrong, t_pine = at("gone before"), at("anything goes wrong"), at("at pine crest")
t_pine_w, t_we, t_pics, t_show = at("pine crest"), at("we get up on"), at("pictures of everything"), at("and show you")
t_if, t_nothing, t_want, t_tap, t_free = at("if there's nothing"), at("nothing there"), at("if you want to"), at("tap the link"), at("free inspection")

# 1
shot("house-wide", 0.0, t_30k - 0.35, "push", snaps=[(t_tx, 1.12)])
shot("house-close", t_30k - 0.35, t_most, "in", snaps=[(t_30k, 1.18)])
# 2
shot("roof-street", t_most, at("could already"), "push")
shot("roof-detail", at("could already"), t_th, "push")
shot("roof-street", t_th, t_and, "in", snaps=[(t_th + 0.05, 1.22)], tag="b")
# 3
shot("look-up", t_and, t_from + 0.6, "pan")
shot("look-up-2", t_from + 0.6, t_but, "pan", pan_dir=-1)
# 4: whip up to roof level
shot("roof-level", t_but, t_story, "in", enter="whip-up", snaps=[(t_but + 0.02, 1.15)])
shot("roof-level-2", t_story, t_hail, "in", snaps=[(t_story + 0.3, 1.12)])
# 5: four close-ups
shot("hail-marks", t_hail, t_crack, "still", snaps=[(t_hail + 0.02, 1.25)])
shot("cracked", t_crack, t_wood, "still", snaps=[(t_crack + 0.02, 1.25)])
shot("wood", t_wood, t_leak, "still", snaps=[(t_wood + 0.02, 1.25)])
shot("attic-stain", t_leak, t_good, "in", snaps=[(t_leak + 0.02, 1.2)])
# 6: wider, brighter
shot("roof-bright", t_good, t_cov - 0.3, "out", bright=True)
shot("roof-bright-2", t_cov - 0.3, t_out, "out", bright=True)
# 7
shot("storm", t_out, t_hail2, "push")
shot("hail", t_hail2, t_seen, "push")
# 8
shot("storm-dark", t_seen, t_town, "push")
shot("truck-arrive", t_town, at("right after a") , "in")
shot("door", at("right after a"), t_sign - 0.05, "in")
shot("signing", t_sign - 0.05, t_gone, "in", snaps=[(t_sign, 1.1)])
shot("truck-gone", t_gone, t_wrong, "out-fast")
shot("leak", t_wrong, t_pine, "in", snaps=[(t_wrong + 0.1, 1.12)])
# 9: hero truck
shot("pinecrest", t_pine, t_we, "push", snaps=[(t_pine_w, 1.14)], enter="flash")
# 10
shot("ladder", t_we, at("roof take"), "in", snaps=[(t_we + 0.05, 1.1)])
shot("inspect", at("roof take"), t_pics, "in")
shot("pictures", t_pics, t_show, "in", snaps=[(t_pics + 0.05, 1.12), (at("everything") + 0.05, 1.22)])
shot("show", t_show, t_if, "in", snaps=[(t_show + 0.05, 1.1)])
# 11
shot("handshake", t_if, t_want, "push")
# 12
shot("finished", t_want, DUR, "push", snaps=[(t_want + 0.05, 1.06)])
T_END = t_tap

# ---------------- media prep ----------------
jobs = []
for n, s in enumerate(S):
    m = MEDIA[s["slot"]]
    base = os.path.splitext(os.path.basename(m["src"]))[0][-24:]
    if m["kind"] == "photo":
        s["file"] = f"assets/prep/{s['slot']}--{base}--{m['x']}.jpg"
        jobs.append(dict(src=m["src"], out=s["file"], kind="photo", x=m["x"], vf=m.get("vf", "")))
    else:
        ss = m.get("ss", 0) + (0 if s.get("tag") != "b" else 0)
        s["file"] = f"assets/prep/{s['slot']}{s.get('tag', '')}--{base}--{ss}.mp4"
        jobs.append(dict(src=m["src"], out=s["file"], kind="video", ss=ss, dur=round(s["t1"] - s["t0"] + 0.4, 2), x=m["x"]))
json.dump(jobs, open("assets/prep-jobs.json", "w"), indent=1)
subprocess.run([sys.executable, "tools/prep.py", "assets/prep-jobs.json"], check=True, stdout=subprocess.DEVNULL)

# ---------------- captions (2-3 words, word-by-word highlight) ----------------
NORM = {"$30,000": "$30,000"}
YELLOW = ["north texas", "$30,000", "thousands of dollars", "hail", "cracked shingles", "leaks", "insurance", "taken advantage of",
          "pine crest", "nothing there", "free inspection"]
hl, ph_of, phrases = set(), {}, []
for p in YELLOW:
    st = 0
    while True:
        try: ix = find(p, st)
        except SystemExit: break
        phrases.append(ix); hl.update(ix)
        for i in ix: ph_of[i] = len(phrases) - 1
        st = ix[-1] + 1
groups, cur = [], []
for i, w in enumerate(words):
    if cur:
        prev = words[cur[-1]]
        inside = ph_of.get(i) is not None and ph_of.get(i) == ph_of.get(cur[-1])
        brk = (len(cur) >= 3 or re.search(r"[.,?!]$", prev["text"]) or w["start"] - prev["end"] > 0.25) and not inside
        ph = ph_of.get(i)
        if ph is not None and not inside and len(cur) + len(phrases[ph]) > 3: brk = True
        if brk: groups.append(cur); cur = []
    cur.append(i)
groups.append(cur)
merged = []
for g in groups:   # fold 1-word stragglers into the previous group when it stays <= 3 words
    if merged and len(g) == 1 and len(merged[-1]) < 3 and not re.search(r"[.?!]$", words[merged[-1][-1]]["text"]) and g[0] not in hl:
        merged[-1] = merged[-1] + g
    else: merged.append(g)
groups = merged
def disp(i):
    t = re.sub(r"[.,?!]+$", "", words[i]["text"]).upper()
    if clean(words[i]["text"]) == "pine" and i + 1 < len(words) and clean(words[i + 1]["text"]) == "crest": return "PINECREST"
    if clean(words[i]["text"]) == "crest" and i > 0 and clean(words[i - 1]["text"]) == "pine": return None
    return t

# ---------------- HTML + timeline ----------------
el, js, sfx = [], [], []
def fx(name, t, vol, ms=0.0): sfx.append((name, round(max(0, t), 3), vol, ms))

for n, s in enumerate(S):
    sid, t0, t1 = f"s{n:02d}", s["t0"], s["t1"]
    cls = "shot bright" if s.get("bright") else "shot"
    if s["file"].endswith(".mp4"):
        el.append(f'<div class="kb" id="kb-{sid}"><div class="snap" id="sn-{sid}"><video id="v-{sid}" class="clip media" src="{s["file"]}" muted playsinline '
                  f'data-start="{t0:.3f}" data-duration="{t1 - t0:.3f}" data-track-index="{2 + n % 2}"></video></div></div>')
    else:
        el.append(f'<div class="clip {cls}" id="c-{sid}" data-start="{t0:.3f}" data-duration="{t1 - t0:.3f}" data-track-index="{2 + n % 2}">'
                  f'<div class="kb" id="kb-{sid}"><div class="snap" id="sn-{sid}"><img class="media photo" src="{s["file"]}" alt="" /></div></div></div>')
    sel, d = f"#kb-{sid}", t1 - t0
    mv = s["move"]
    # Base movement (the frame never sits still).
    if mv in ("in", "push"):
        js.append(f'tl.fromTo("{sel}", {{scale: 1.0}}, {{scale: {1.1 if mv == "push" else 1.07}, duration: {d:.3f}, ease: "none"}}, {t0});')
    elif mv == "out":
        js.append(f'tl.fromTo("{sel}", {{scale: 1.16}}, {{scale: 1.0, duration: {d:.3f}, ease: "power2.out"}}, {t0});')
    elif mv == "out-fast":
        js.append(f'tl.fromTo("{sel}", {{scale: 1.35}}, {{scale: 1.0, duration: 0.45, ease: "power3.out"}}, {t0});')
        fx("peel", t0 - 0.05, 0.22)
    elif mv == "pan":
        dx = 6 * s.get("pan_dir", 1)
        js.append(f'tl.fromTo("{sel}", {{scale: 1.08, xPercent: {-dx / 2}}}, {{scale: 1.1, xPercent: {dx / 2}, duration: {d:.3f}, ease: "none"}}, {t0});')
    elif mv == "still":
        js.append(f'tl.fromTo("{sel}", {{scale: 1.0}}, {{scale: 1.04, duration: {d:.3f}, ease: "none"}}, {t0});')
    # Snap zooms layered on an inner wrapper so they compound with the base move.
    if s["snaps"]:
        prev = 1.0
        for k, (ts, sc) in enumerate(s["snaps"]):
            js.append(f'tl.fromTo("#sn-{sid}", {{scale: {prev}}}, {{scale: {sc}, duration: 0.14, ease: "power4.out", immediateRender: {"true" if k == 0 else "false"}}}, {ts:.3f});')
            prev = sc
            fx("whoosh-short", ts - 0.08, 0.16)
    if s["enter"] == "whip-up":
        js.append(f'tl.fromTo("{sel} .media", {{yPercent: 35, filter: "blur(18px)"}}, {{yPercent: 0, filter: "blur(0px)", duration: 0.28, ease: "power3.out"}}, {t0});')
        fx("whoosh", t0 - 0.15, 0.4)
    elif s["enter"] == "flash":
        js.append(f'tl.fromTo("#flash", {{opacity: 0.9}}, {{opacity: 0, duration: 0.35, ease: "power2.out", immediateRender: false}}, {t0});')
    elif n and not s["snaps"]:
        fx("whoosh-short", t0 - 0.08, 0.1)

# Light leaks (real Mixkit overlays) at the scene turns.
LEAKS = [(t_but, 0), (t_good, 1), (t_pine, 0), (t_want, 1)]
for k, (t, src) in enumerate(LEAKS):
    f = f"assets/prep/leak{k}.mp4"
    jobs_leak = [dict(src=B + ("fx-lightleaks--mixkit-48495-720p.mp4" if src == 0 else "fx-lightleaks2--mixkit-48011-720p.mp4"),
                      out=f, kind="video", ss=1 + k, dur=1.6, x=0.5)]
    json.dump(jobs_leak, open("assets/leak-job.json", "w")); subprocess.run([sys.executable, "tools/prep.py", "assets/leak-job.json"], check=True, stdout=subprocess.DEVNULL)
    el.append(f'<div class="leak" id="lk{k}"><video id="lkv{k}" class="clip media" src="{f}" muted playsinline data-start="{t - 0.3:.3f}" data-duration="1.4" data-track-index="{12 + k}"></video></div>')
    js.append(f'tl.fromTo("#lk{k}", {{opacity: 0}}, {{opacity: 0.8, duration: 0.3}}, {t - 0.3:.3f});')
    js.append(f'tl.to("#lk{k}", {{opacity: 0, duration: 0.6}}, {t + 0.5:.3f});')

# Text pops (top third).
POPS = [("$30,000?!", t_30k + 0.1, t_most - 0.1, "big"), ("⚠️ HIDDEN ROOF DAMAGE", t_th, t_and - 0.1, ""),
        ("✅ INSURANCE MAY COVER IT", t_cov, t_out - 0.1, "green"), ("🚩 STORM CHASERS", t_town, t_gone - 0.1, "red"),
        ("📸 FULL PHOTO REPORT", t_pics, t_if - 0.1, ""), ("🤝 HONEST ANSWERS", t_nothing, t_want - 0.1, "")]
for k, (txt, a, b, kind) in enumerate(POPS):
    emo = re.match(r"^(\S+)\s(.*)$", txt) if not txt.startswith("$") else None
    inner = (f'<span class="emo">{emo.group(1)}</span> {html.escape(emo.group(2))}' if emo else html.escape(txt))
    el.append(f'<div class="clip pop" id="pop{k}" data-start="{a:.3f}" data-duration="{b - a:.3f}" data-track-index="20"><div class="pill {kind}" id="pl{k}">{inner}</div></div>')
    js.append(f'tl.fromTo("#pl{k}", {{opacity: 0, scale: 0.4, rotation: -4}}, {{opacity: 1, scale: 1, rotation: 0, duration: 0.3, ease: "back.out(2.6)"}}, {a:.3f});')
    js.append(f'tl.to("#pl{k}", {{opacity: 0, scale: 0.9, duration: 0.15, ease: "power2.in"}}, {b - 0.15:.3f});')
    fx("pop", a, 0.3)
# Pinecrest title with a light sweep.
el.append(f'<div class="clip brand" id="brand" data-start="{t_pine_w:.3f}" data-duration="{t_we - t_pine_w:.3f}" data-track-index="21">'
          f'<div class="brandin" id="brandin"><div class="b1">PINECREST</div><div class="b2">ROOFING &amp; CONSTRUCTION</div><i id="sweep"></i></div></div>')
js.append(f'tl.fromTo("#brandin", {{opacity: 0, y: 40, scale: 0.9}}, {{opacity: 1, y: 0, scale: 1, duration: 0.4, ease: "power3.out"}}, {t_pine_w:.3f});')
js.append(f'tl.fromTo("#sweep", {{xPercent: -120}}, {{xPercent: 260, duration: 0.9, ease: "power2.inOut"}}, {t_pine_w + 0.35:.3f});')
# End card.
el.append(f'<div class="clip endcard" id="endcard" data-start="{T_END:.3f}" data-duration="{DUR - T_END:.3f}" data-track-index="22">'
          f'<div class="ecbg"></div><div class="ecname" id="ecname">PINECREST<span>ROOFING &amp; CONSTRUCTION</span></div>'
          f'<div class="ecbtn" id="ecbtn">BOOK YOUR FREE INSPECTION <span class="emo">👇</span></div><div class="ecsub" id="ecsub">North Texas · Photo report included</div></div>')
js.append(f'tl.fromTo("#endcard", {{opacity: 0}}, {{opacity: 1, duration: 0.35}}, {T_END:.3f});')
js.append(f'tl.fromTo("#ecname", {{opacity: 0, y: -30}}, {{opacity: 1, y: 0, duration: 0.45, ease: "power3.out"}}, {T_END + 0.1:.3f});')
js.append(f'tl.fromTo("#ecbtn", {{opacity: 0, scale: 0.6}}, {{opacity: 1, scale: 1, duration: 0.4, ease: "back.out(2.2)"}}, {T_END + 0.3:.3f});')
js.append(f'tl.to("#ecbtn", {{scale: 1.07, duration: 0.35, yoyo: true, repeat: {int((DUR - T_END - 0.8) / 0.35) | 1}, ease: "sine.inOut"}}, {T_END + 0.75:.3f});')
js.append(f'tl.fromTo("#ecsub", {{opacity: 0}}, {{opacity: 1, duration: 0.4}}, {T_END + 0.6:.3f});')

# Sound design (all under the voice; levels set in the mix check).
fx("impact", t_tx - 0.02, 0.45); fx("kaching", t_30k + 0.15, 0.3)
fx("riser", t_most, 0.18, ms=4.5); fx("beep", t_dmg, 0.22)
fx("whoosh", t_but - 0.15, 0.45)
fx("ice", t_hail, 0.35); fx("crack", t_crack + 0.05, 0.4); fx("creak", t_wood, 0.3); fx("drip", t_leak, 0.4)
fx("chime", t_cov + 0.2, 0.3)
fx("thunder", t_out, 0.35); fx("hail", t_hail2 - 0.3, 0.22)
fx("scribble", t_sign, 0.35)
fx("whoosh", t_pine - 0.12, 0.35); fx("pop", t_pine_w + 0.05, 0.35)
fx("ladder", t_we, 0.3); fx("shutter", t_pics + 0.05, 0.4); fx("shutter", at("everything") + 0.05, 0.35)
fx("warm", t_if, 0.4)
fx("notify", t_free, 0.3)

cap = []
for gi, g in enumerate(groups):
    vis = [i for i in g if disp(i)]
    s0 = words[g[0]]["start"]; nxt = words[groups[gi + 1][0]]["start"] if gi + 1 < len(groups) else VO_DUR + 0.3
    e0 = min(nxt, words[g[-1]]["end"] + 0.5)
    ws = "".join(f'<span class="w{" hl" if i in hl else ""}" id="w{i}">{html.escape(disp(i))}</span>' for i in vis)
    cap.append(f'<div class="cg" id="cg{gi}"><div class="line">{ws}</div></div>')
    js.append(f'tl.fromTo("#cg{gi}", {{opacity: 0, scale: 0.85}}, {{opacity: 1, scale: 1, duration: 0.1, ease: "back.out(2)"}}, {s0:.3f});')
    for i in vis:
        w = words[i]; lit = '{opacity: 1, scale: 1.08, duration: 0.07, ease: "power2.out"' + (', color: "#ffd60a"' if i in hl else "") + "}"
        js.append(f'tl.fromTo("#w{i}", {{opacity: 0.6, scale: 1, color: "#ffffff"}}, {lit}, {w["start"]:.3f});')
        js.append(f'tl.to("#w{i}", {{scale: 1, duration: 0.1}}, {max(w["start"] + 0.07, w["end"]):.3f});')
    js.append(f'tl.to("#cg{gi}", {{opacity: 0, duration: 0.05}}, {e0 - 0.05:.3f});')
    js.append(f'tl.set("#cg{gi}", {{opacity: 0, visibility: "hidden"}}, {e0:.3f});')
# Grain
frames = int(DUR * 30)
js.append(f'tl.fromTo("#grain", {{backgroundPosition: "0px 0px"}}, {{backgroundPosition: "{frames * 337 % 1024}px {frames * 211 % 1024}px", duration: {DUR}, ease: "steps({frames})"}}, 0);')

SRC = {k: f"sfx-{k}.{'mp3' if k in ('impact', 'whoosh', 'whoosh-short', 'pop', 'chime', 'notify', 'riser') else 'wav'}"
       for k in {s[0] for s in sfx}}
aud = []
for n, (k, t, v, ms) in enumerate(sorted(sfx, key=lambda x: x[1])):
    ln = probe("assets/" + SRC[k]) - ms
    aud.append(f'<audio id="fx{n}" src="assets/{SRC[k]}" data-start="{t:.3f}" data-duration="{min(ln, DUR - t):.3f}"'
               + (f' data-media-start="{ms}"' if ms else "") + f' data-track-index="{40 + n}" data-volume="{v}"></audio>')

tpl = open("tools/ad.template.html").read()
for k, v in {"{{DUR}}": f"{DUR}", "{{VO_DUR}}": f"{VO_DUR}", "{{ELEMENTS}}": "\n      ".join(el), "{{CAPTIONS}}": "\n        ".join(cap),
             "{{AUDIO}}": "\n    ".join(aud), "{{JS}}": "\n      ".join(js)}.items():
    tpl = tpl.replace(k, v)
open("index.html", "w").write(tpl)
lens = [s["t1"] - s["t0"] for s in S]
print(f"duration {DUR}s · {len(S)} shots (longest {max(lens):.2f}s) · {len(groups)} caption groups · {len(sfx)} sfx")
print("media:", {k: os.path.basename(v["src"]) for k, v in MEDIA.items()})
