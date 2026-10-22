"""Build the website VSL (1920x1080) from the cut talking head, graded b-roll and transcript.json.

Steps: resolve the shot list against word timings -> write prep jobs and conform media
(tools/prep_media.py) -> write index.html. Commons photos are used when present in broll/photos,
otherwise each photo slot falls back to the Mixkit clip named in the shot list.
"""
import html, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
words = json.load(open("transcript.json"))
words = words if isinstance(words, list) else words["words"]
probe = lambda f: float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                                       capture_output=True, text=True).stdout)
A_DUR = round(probe("assets/aroll.mp4") - 0.05, 2)
DUR = round(A_DUR + 2.0, 2)   # 2 s tail: the end card holds after the last word while the music fades
NORM = {"angie": "Angi", "chancey": "Chancy"}

def clean(t): return re.sub(r"[.,?!]+$", "", t).lower()
def find(phrase, after=0):
    toks = phrase.lower().split()
    for i in range(after, len(words)):
        if [clean(w["text"]) for w in words[i:i + len(toks)]] == toks: return list(range(i, i + len(toks)))
    sys.exit(f"phrase not found: {phrase}")
def at(p, after=0): return round(words[find(p, after)[0]]["start"], 3)
def end(p, after=0): return round(words[find(p, after)[-1]]["end"], 3)

PHOTOS = "broll/photos"
def photo(cid):
    for ext in (".jpg", ".jpeg", ".png"):
        p = f"{PHOTOS}/{cid}{ext}"
        if os.path.exists(p) and os.path.getsize(p) > 20000: return p
    return None

# ---------------- shot list ----------------
# kind: v = video b-roll, p = photo (Ken Burns), plus graphic kinds. Times come from the transcript.
B = "broll/"
S = []
def shot(kind, t0, t1, **kw): S.append(dict(kind=kind, t0=round(t0, 3), t1=round(t1, 3), **kw))
def media(cid, fallback, ss=0.0, kb="in"):
    """Commons photo when downloaded, else a Mixkit clip."""
    p = photo(cid) if cid else None
    return dict(kind="p", src=p, kb=kb) if p else dict(kind="v", src=fallback, ss=ss, kb=kb)

t_stop = at("stop what you're doing")
# 1-3: opening montage once the first 5 s of talking head are done.
shot("v", 5.0, 5.8, src=B + "s01-frustrated-phone--mixkit-1442-1080p.mp4", ss=3.0, kb="in")
shot("v", 5.8, 6.6, src=B + "s02-paperwork--mixkit-46811-720p.mp4", ss=1.5, kb="in")
shot("v", 6.6, t_stop - 0.05, src=B + "s03-empty-calendar--mixkit-22752-720p.mp4", ss=6.0, kb="out")
# 4: STOP card.
shot("stop", t_stop - 0.05, at("what i'm about to"))
# 5: laptop inbox.
shot("v", at("you've probably tried"), at("and what did you"), src="assets/comp/s05-laptop-inbox.mp4", ss=0, kb="none")
# 6: call failed.
shot("v", at("you call they"), at("the ones who do"), src="assets/comp/s06-phone-callfailed.mp4", ss=0, kb="none",
     vf="crop=1152:648:768:0")
# 7: lowest bid wins: price dropping over a roof photo.
shot("price", at("and the lowest bid"), at("here's what nobody"), bg=media("c004", B + "s17-construction--mixkit-1459-1080p.mp4", 1))
# 19: contractor in his vehicle, thinking.
shot("v", at("here's what nobody"), at("most lead companies") + 1.6, src=B + "s19-man-in-vehicle--mixkit-41560-1080p.mp4", ss=1.0, kb="in")
shot("v", at("they get paid when"), at("whether you close"), src=B + "s01-phone-table--mixkit-4915-1080p.mp4", ss=2.0, kb="in")
# 8: one house splitting into five competitors' trucks.
shot("split", at("the same lead gets"), at("you're not broken"),
     house=media("c065", B + "s17-construction--mixkit-1436-1080p.mp4", 2),
     cells=[media("c009", B + "s17-construction--mixkit-1436-1080p.mp4", 9), media("c015", B + "s01-frustrated-phone--mixkit-1442-1080p.mp4", 6),
            media("c014", B + "s08-pickup-truck--mixkit-41535-1080p.mp4", 4), media("c049", B + "s17-construction--mixkit-1459-1080p.mp4", 5),
            media("c005", B + "s01-frustrated-phone--mixkit-1443-1080p.mp4", 1)])
# 9: slow push-in on the talking head + music drop (handled in score and #cam).
T_BROKEN, T_BUILT = at("you're not broken"), at("so we built")
# 10: aerial over a suburb.
shot("v" if not photo("c093") else "p", T_BUILT, at("a real homeowner"),
     **(dict(src=photo("c093"), kb="drone") if photo("c093") else dict(src=B + "s10-aerial-suburb--mixkit-48394-720p.mp4", ss=3, kb="in")))
# 11: handshake.
shot("v", at("a real homeowner"), at("you don't pay for"), src=B + "s11-handshake--mixkit-30005-1080p.mp4", ss=1.0, kb="in")
# 20: NO APPOINTMENTS = NO PAY.
shot("nopay", at("you don't pay for"), at("here's how it works"))
# 12: STEP 1: crew, then the social ad on a phone.
T_S1, T_GEN = at("step one"), at("not the same generic")
shot("p" if photo("c014") else "v", T_S1, T_GEN, title=("STEP 1", "Ads built around your crew"),
     **(dict(src=photo("c014"), kb="in") if photo("c014") else dict(src=B + "s17-construction--mixkit-1459-1080p.mp4", ss=0.5, kb="in")))
shot("v", T_GEN, at("if you run the same"), src="assets/comp/s12-phone-socialad.mp4", ss=0, kb="none", vf="crop=1152:648:0:0")
# 17: montage (new roofs, crews, trucks, shingle close-ups).
m0, m1 = at("you'll be attracting"), at("that's why we've")
mont = [media("c077", B + "s17-hammering-nails--mixkit-44864-720p.mp4", 1), media("c063", B + "s17-construction--mixkit-1436-1080p.mp4", 6),
        dict(kind="v", src=B + "s17-hammering-nails--mixkit-44864-720p.mp4", ss=2), media("c004", B + "s08-pickup-truck--mixkit-41535-1080p.mp4", 10)]
step = (m1 - m0) / len(mont)
for k, m in enumerate(mont): shot(m["kind"], m0 + k * step, m0 + (k + 1) * step, src=m["src"], ss=m.get("ss", 0), kb="in" if k % 2 else "out")
cr = dict(kind="v", src=B + "s17-construction--mixkit-1459-1080p.mp4", ss=0.5)
shot(cr["kind"], at("not by positioning"), at("one thing your competition") - 0.3, src=cr["src"], ss=cr.get("ss", 0), kb="in")
# 13: STEP 2: call center + timer.
T_S2, T_SURE = at("step two"), at("to make sure that")
shot("v", T_S2, T_SURE, src=B + "s13-call-center--mixkit-22987-720p.mp4", ss=2, kb="in", title=("STEP 2", "We call every lead in minutes"), timer=True)
# 14: three checkmarks over a house exterior.
shot("checks", T_SURE, at("no more dealing") + 0.6, bg=media("c065", B + "s11-handshake--mixkit-30005-1080p.mp4", 5),
     items=["Motivated buyer", "Financially qualified", "Ready for a new roof"],
     times=[at("motivated buyers"), at("financially qualified"), at("financially qualified") + 0.6])
# 15: STEP 3: iPhone calendar, then roofer up on the roof for the inspection.
T_S3, T_CRM = at("lastly"), at("and integrate with")
shot("v", T_S3, T_CRM, src="assets/comp/s15-phone-calendar.mp4", ss=0, kb="none", vf="crop=1152:648:768:0", title=("STEP 3", "Booked straight onto your calendar"),
     title_right=True)
insp = media("c051", B + "s01-frustrated-phone--mixkit-1443-1080p.mp4", 2)
shot(insp["kind"], T_CRM, at("so all you have"), src=insp["src"], ss=insp.get("ss", 0), kb="in")
# 18: counters over finished roofs.
T_RES, T_500 = at("one of our roofing"), at("and just hit")
shot("counter", T_RES, T_500, bg=media("c014", B + "s17-construction--mixkit-1459-1080p.mp4", 3), value=4000000,
     label="in sales", done=end("in sales") + 0.1, who="CHANCY · ROOFING CLIENT")
shot("counter", T_500, at("that's what happens"), bg=media("c092", B + "s17-construction--mixkit-1436-1080p.mp4", 8), value=500000,
     label="booked in one month", done=words[find("in booked revenue")[0]]["start"] + 0.2, who="ONE SINGLE MONTH")
# 21: signing at the table.
shot("v", at("this only works"), at("and your real bottleneck"), src=B + "s21-signing--mixkit-241-1080p.mp4", ss=3, kb="in")
# 16: one roofer per service area: map.
shot("map", at("we only work with"), at("so if you're serious"), bg=media("c093", B + "s16-map-tablet--mixkit-39787-1080p.mp4", 2))
# 22: end card.
T_APPLY = at("scroll down and")
shot("endcard", T_APPLY, DUR)

# ---------------- media prep ----------------
jobs, used = [], []
def prep(m, t0, t1, tag, vf=""):
    """Register a conform job; returns the prepared file path (named by slot + source so a re-pointed slot re-preps)."""
    tag = f"{tag}--{os.path.splitext(os.path.basename(m['src']))[0][-28:]}"
    if m["kind"] == "p":
        out = f"assets/prep/{tag}.jpg"
        jobs.append(dict(src=m["src"], out=out, kind="photo"))
    else:
        out = f"assets/prep/{tag}.mp4"
        jobs.append(dict(src=m["src"], out=out, kind="video", ss=m.get("ss", 0), dur=round(t1 - t0 + 0.3, 2), vf=vf))
    used.append(m["src"])
    return out
for n, s in enumerate(S):
    if s["kind"] in ("v", "p"): s["file"] = prep(s, s["t0"], s["t1"], f"shot{n:02d}", s.get("vf", ""))
    for key in ("bg", "house"):
        if key in s: s[key]["file"] = prep(s[key], s["t0"], s["t1"], f"shot{n:02d}-{key}")
    for c, m in enumerate(s.get("cells", [])):
        if m.get("src"): m["file"] = prep(m, s["t0"], s["t1"], f"shot{n:02d}-cell{c}")
json.dump(jobs, open("assets/prep-jobs.json", "w"), indent=1)
subprocess.run([sys.executable, "tools/prep_media.py", "assets/prep-jobs.json"], check=True, stdout=subprocess.DEVNULL)
json.dump(sorted(set(used)), open("assets/used-media.json", "w"), indent=1)

# ---------------- captions ----------------
YELLOW = ["pay attention", "race to the bottom", "the system is", "you don't pay", "within the first five minutes",
          "one roofer per service area", "$4 million", "$500,000", "apply"]
hl, ph_of, phrases = set(), {}, []
for p in YELLOW:
    start = 0
    while True:
        try: ix = find(p, start)
        except SystemExit: break
        phrases.append(ix); hl.update(ix)
        for i in ix: ph_of[i] = len(phrases) - 1
        start = ix[-1] + 1
# Split at clause punctuation / pauses, balance long clauses into 3-5 word chunks, merge stragglers
# within the sentence, and never break inside a yellow phrase.
import math
clauses, cur = [], []
for i, w in enumerate(words):
    if cur and (re.search(r"[.,?!]$", words[cur[-1]]["text"]) or w["start"] - words[cur[-1]]["end"] > 0.35) and ph_of.get(i) is None:
        clauses.append(cur); cur = []
    cur.append(i)
clauses.append(cur)
def legal(i): return i == 0 or ph_of.get(i) is None or ph_of.get(i) != ph_of.get(i - 1)
groups = []
for c in clauses:
    k = 1 if len(c) <= 6 else math.ceil(len(c) / 5); size = len(c) / k; cuts = []
    for j in range(1, k):
        x = round(j * size)
        for d in (0, 1, -1, 2, -2):
            if 0 < x + d < len(c) and legal(c[x + d]): x += d; break
        cuts.append(x)
    edges = [0] + cuts + [len(c)]
    groups += [c[edges[j]:edges[j + 1]] for j in range(len(edges) - 1) if edges[j] < edges[j + 1]]
ends_sentence = lambda g: re.search(r"[.?!]$", words[g[-1]]["text"])
merged = []
for g in groups:
    cap = 6 if merged and any(i in hl for i in merged[-1] + g) else 5   # one extra word keeps a yellow phrase whole
    if merged and (len(g) <= 2 or len(merged[-1]) <= 2) and len(merged[-1]) + len(g) <= cap and not ends_sentence(merged[-1]):
        merged[-1] = merged[-1] + g
    else: merged.append(g)
# A group spoken in under 0.6 s flashes by: fold it into the next one (up to 7 words).
merged = []
for g in groups:
    if merged and words[merged[-1][-1]]["end"] - words[merged[-1][0]]["start"] < 0.45 and len(merged[-1]) + len(g) <= 7:
        merged[-1] = merged[-1] + g
    else: merged.append(g)
groups = merged
CARD_HIDE = [(s["t0"], s["t1"]) for s in S if s["kind"] in ("stop",)]
G = []
for gi, g in enumerate(groups):
    s0 = words[g[0]]["start"]; nxt = words[groups[gi + 1][0]]["start"] if gi + 1 < len(groups) else DUR
    e = nxt if nxt - words[g[-1]]["end"] < 0.7 else words[g[-1]]["end"] + 0.4
    if gi == len(groups) - 1: e = DUR  # the closing line holds to the end
    if any(a - 0.05 <= s0 < b for a, b in CARD_HIDE): continue
    G.append((g, round(s0, 3), round(min(e, DUR), 3)))
def disp(i):
    t = words[i]["text"]
    return NORM.get(clean(t), t)

# ---------------- HTML ----------------
el, js = [], []
def kb_js(sel, kind, t0, t1):
    d = t1 - t0
    if kind == "in": js.append(f'tl.fromTo("{sel}", {{scale: 1.0}}, {{scale: 1.15, duration: {d:.3f}, ease: "sine.inOut"}}, {t0});')
    elif kind == "out": js.append(f'tl.fromTo("{sel}", {{scale: 1.16}}, {{scale: 1.0, duration: {d:.3f}, ease: "sine.inOut"}}, {t0});')
    elif kind == "drone": js.append(f'tl.fromTo("{sel}", {{scale: 1.05, xPercent: -2, yPercent: 1.5}}, {{scale: 1.18, xPercent: 2, yPercent: -1.5, duration: {d:.3f}, ease: "none"}}, {t0});')
def visual(m, sid, t0, t1, track, cls="full"):
    """A video clip (timed <video> in an untimed Ken Burns wrapper) or a photo inside a timed clip."""
    kbsel = f"#kb-{sid}"
    if m["file"].endswith(".mp4"):
        el.append(f'<div class="kb {cls}" id="kb-{sid}"><video id="v-{sid}" class="clip media" src="{m["file"]}" muted playsinline '
                  f'data-start="{t0:.3f}" data-duration="{t1 - t0:.3f}" data-track-index="{track}"></video></div>')
    else:
        el.append(f'<div class="clip {cls}" id="c-{sid}" data-start="{t0:.3f}" data-duration="{t1 - t0:.3f}" data-track-index="{track}">'
                  f'<div class="kb" id="kb-{sid}"><img class="media" src="{m["file"]}" alt="" /></div></div>')
    kb_js(kbsel, m.get("kb", "in"), t0, t1)
def overlay(sid, t0, t1, inner, track=20, cls="ov"):
    el.append(f'<div class="clip {cls}" id="{sid}" data-start="{t0:.3f}" data-duration="{t1 - t0:.3f}" data-track-index="{track}">{inner}</div>')

sfx = []
def fx(name, t, vol, ms=0.0): sfx.append((name, round(max(0, t), 3), round(min(vol * 2.5, 0.6), 3), ms))  # 2.5x: effects were buried
for n, s in enumerate(S):
    sid, t0, t1, k = f"s{n:02d}", s["t0"], s["t1"], s["kind"]
    if k in ("v", "p"):
        visual(s, sid, t0, t1, 2 + n % 2)
        fx("whoosh-short", t0 - 0.12, 0.10)
    elif k == "stop":
        overlay(sid, t0, t1, '<div class="stop"><div id="stop-a">STOP.</div><div id="stop-b">PAY ATTENTION.</div></div>', cls="card")
        js.append(f'tl.fromTo("#stop-a", {{opacity: 0, scale: 1.25}}, {{opacity: 1, scale: 1, duration: 0.18, ease: "power4.out"}}, {t0 + 0.05});')
        js.append(f'tl.fromTo("#stop-b", {{opacity: 0, y: 30}}, {{opacity: 1, y: 0, duration: 0.3, ease: "power3.out"}}, {at("pay attention"):.3f});')
        fx("impact", t0, 0.32)
    elif k == "nopay":
        overlay(sid, t0, t1, '<div class="nopay"><div class="np1" id="np1">NO APPOINTMENTS</div><div class="np2" id="np2">=</div>'
                             '<div class="np3" id="np3">NO PAY</div></div>', cls="card warm")
        js.append(f'tl.fromTo("#np1", {{opacity: 0, y: 30}}, {{opacity: 1, y: 0, duration: 0.35, ease: "power3.out"}}, {t0 + 0.05});')
        js.append(f'tl.fromTo("#np2", {{opacity: 0}}, {{opacity: 1, duration: 0.3}}, {t0 + 0.35});')
        js.append(f'tl.fromTo("#np3", {{opacity: 0, scale: 1.15}}, {{opacity: 1, scale: 1, duration: 0.35, ease: "power3.out"}}, {t0 + 0.6});')
        fx("impact", t0, 0.18)
    elif k == "price":
        visual(s["bg"], sid, t0, t1, 2)
        overlay(sid + "-px", t0, t1, '<div class="price"><div class="plabel">LOWEST BID WINS</div><div class="pval" id="pval">$18,000</div>'
                                    '<div class="pbar"><i id="pbar"></i></div></div>')
        vals = ["$18,000", "$14,500", "$11,900"]
        for j, v in enumerate(vals):
            tj = t0 + 0.25 + j * (t1 - t0 - 0.6) / 2.5
            js.append(f'tl.set("#pval", {{textContent: "{v}"}}, {tj:.3f});')
            js.append(f'tl.fromTo("#pval", {{y: -26, opacity: 0.3}}, {{y: 0, opacity: 1, duration: 0.25, ease: "power3.out"}}, {tj:.3f});')
            if j: fx("tick", tj, 0.22)
        js.append(f'tl.fromTo("#pbar", {{scaleX: 1}}, {{scaleX: 0.66, duration: {t1 - t0 - 0.5:.3f}, ease: "power2.inOut"}}, {t0 + 0.25});')
        js.append(f'tl.fromTo("#{sid}-px .price", {{opacity: 0, y: 30}}, {{opacity: 1, y: 0, duration: 0.4, ease: "power3.out"}}, {t0 + 0.05});')
    elif k == "split":
        visual(s["house"], sid + "h", t0, t0 + 1.2, 2)
        cells = "".join(f'<div class="cell" id="cell{c}"></div>' for c in range(5))
        overlay(sid + "-grid", t0 + 1.0, t1, f'<div class="grid5" id="grid5">{cells}<div class="g5label" id="g5l">SOLD TO 5 ROOFERS</div></div>', track=4)
        for c, m in enumerate(s["cells"]):
            if not m.get("file"): continue
            if m["file"].endswith(".mp4"):
                el.append(f'<div class="cellmedia" id="cm{c}"><video id="v-{sid}c{c}" class="clip media" src="{m["file"]}" muted playsinline '
                          f'data-start="{t0 + 1.0:.3f}" data-duration="{t1 - t0 - 1.0:.3f}" data-track-index="{5 + c}"></video></div>')
            else:
                overlay(f"cm{c}", t0 + 1.0, t1, f'<img class="media" src="{m["file"]}" alt="" />', track=5 + c, cls="cellmedia")
            js.append(f'tl.fromTo("#cm{c}", {{opacity: 0, scale: 1.15}}, {{opacity: 1, scale: 1, duration: 0.3, ease: "power3.out"}}, {t0 + 1.0 + c * 0.16:.3f});')
            fx("tick", t0 + 1.0 + c * 0.16, 0.16)
        js.append(f'tl.fromTo("#g5l", {{opacity: 0, y: 20}}, {{opacity: 1, y: 0, duration: 0.35, ease: "power3.out"}}, {t0 + 1.9:.3f});')
        fx("whoosh", t0 + 0.85, 0.12)
    elif k == "checks":
        visual(s["bg"], sid, t0, t1, 2)
        items = "".join(f'<div class="chk" id="chk{j}"><span class="tick" id="tk{j}"></span>{html.escape(t)}</div>' for j, t in enumerate(s["items"]))
        overlay(sid + "-ck", t0, t1, f'<div class="checks">{items}</div>')
        for j, tj in enumerate(s["times"]):
            js.append(f'tl.fromTo("#chk{j}", {{opacity: 0, x: -40}}, {{opacity: 1, x: 0, duration: 0.35, ease: "power3.out"}}, {tj:.3f});')
            js.append(f'tl.fromTo("#tk{j}", {{scale: 0}}, {{scale: 1, duration: 0.3, ease: "back.out(2.5)"}}, {tj + 0.08:.3f});')
            fx("tick", tj + 0.08, 0.3)
    elif k == "counter":
        visual(s["bg"], sid, t0, t1, 2)
        overlay(sid + "-ct", t0, t1, f'<div class="counter"><div class="cwho">{s["who"]}</div><div class="cval" id="cv{sid}">$0</div>'
                                    f'<div class="clab">{s["label"]}</div></div>')
        js.append(f'(function(){{ const n = document.getElementById("cv{sid}"); const st = {{v: 0}};'
                  f' tl.fromTo(st, {{v: 0}}, {{v: {s["value"]}, duration: {s["done"] - t0 - 0.3:.3f}, ease: "power2.out",'
                  f' onUpdate: function(){{ n.textContent = "$" + Math.round(st.v).toLocaleString("en-US"); }}}}, {t0 + 0.3:.3f}); }})();')
        js.append(f'tl.fromTo("#{sid}-ct .counter", {{opacity: 0, y: 30}}, {{opacity: 1, y: 0, duration: 0.45, ease: "power3.out"}}, {t0 + 0.05:.3f});')
        js.append(f'tl.fromTo("#cv{sid}", {{scale: 1}}, {{scale: 1.06, duration: 0.15, yoyo: true, repeat: 1, ease: "power2.out"}}, {s["done"]:.3f});')
        fx("kaching", s["done"], 0.12)
    elif k == "map":
        visual(s["bg"], sid, t0, t1, 2)
        js[-1] = f'tl.fromTo("#kb-{sid}", {{scale: 1.0}}, {{scale: 1.7, xPercent: 0, yPercent: 4, duration: {t1 - t0:.3f}, ease: "power2.inOut"}}, {t0});'
        overlay(sid + "-mp", t0, t1, '<div class="mapov"><div class="dim" id="mdim"></div><div class="area" id="marea"><i></i></div>'
                                    '<div class="mlabel" id="mlabel">YOUR SERVICE AREA · 1 ROOFER</div></div>')
        js.append(f'tl.fromTo("#mdim", {{opacity: 0}}, {{opacity: 1, duration: 0.6}}, {t0 + 0.8:.3f});')
        js.append(f'tl.fromTo("#marea", {{opacity: 0, scale: 0.6}}, {{opacity: 1, scale: 1, duration: 0.5, ease: "back.out(1.6)"}}, {t0 + 0.9:.3f});')
        js.append(f'tl.fromTo("#mlabel", {{opacity: 0, y: 20}}, {{opacity: 1, y: 0, duration: 0.4, ease: "power3.out"}}, {t0 + 1.3:.3f});')
        js.append(f'tl.to("#marea i", {{scale: 1.12, opacity: 0.5, duration: 0.6, yoyo: true, repeat: 3, ease: "sine.inOut"}}, {t0 + 1.4:.3f});')
        fx("whoosh", t0 - 0.12, 0.12)
    elif k == "endcard":
        overlay(sid, t0, t1, '<div class="endcard"><div class="eb" id="eb">APPLY BELOW</div><div class="arrow" id="earrow"></div>'
                             '<div class="es" id="es">See if your service area is still open</div></div>', cls="card glass")
        js.append(f'tl.fromTo("#{sid}", {{opacity: 0}}, {{opacity: 1, duration: 0.5, ease: "power2.out"}}, {t0});')
        js.append(f'tl.fromTo("#eb", {{opacity: 0, y: 30}}, {{opacity: 1, y: 0, duration: 0.5, ease: "power3.out"}}, {t0 + 0.2:.3f});')
        js.append(f'tl.fromTo("#es", {{opacity: 0}}, {{opacity: 1, duration: 0.5}}, {t0 + 0.6:.3f});')
        js.append(f'tl.fromTo("#earrow", {{y: 0}}, {{y: 16, duration: 0.6, yoyo: true, repeat: {max(1, int((t1 - t0 - 1) / 0.6))}, ease: "sine.inOut"}}, {t0 + 0.8:.3f});')
        js.append(f'tl.fromTo("#eb", {{scale: 1}}, {{scale: 1.04, duration: 0.9, yoyo: true, repeat: {max(1, int((t1 - t0 - 1) / 0.9))}, ease: "sine.inOut"}}, {t0 + 0.8:.3f});')
    if s.get("title"):
        a, b = s["title"]
        side = " right" if s.get("title_right") else ""
        overlay(sid + "-tt", t0, min(t1, t0 + 3.2), f'<div class="steptitle{side}"><div class="stn">{a}</div><div class="stl">{html.escape(b)}</div></div>', track=21)
        js.append(f'tl.fromTo("#{sid}-tt .stn", {{opacity: 0, x: -30}}, {{opacity: 1, x: 0, duration: 0.45, ease: "power3.out"}}, {t0 + 0.1:.3f});')
        js.append(f'tl.fromTo("#{sid}-tt .stl", {{opacity: 0, x: -30}}, {{opacity: 1, x: 0, duration: 0.45, ease: "power3.out"}}, {t0 + 0.25:.3f});')
        js.append(f'tl.to("#{sid}-tt .steptitle", {{opacity: 0, duration: 0.3}}, {min(t1, t0 + 3.2) - 0.3:.3f});')
    if s.get("timer"):
        tt = at("within the first five")
        overlay(sid + "-tm", tt, t1, '<div class="timer"><span class="dot"></span><span id="tmtext">Calling lead…</span>'
                                    '<b id="tmclock">0:00</b></div>', track=22)
        js.append(f'tl.fromTo("#{sid}-tm .timer", {{opacity: 0, y: -20}}, {{opacity: 1, y: 0, duration: 0.35, ease: "power3.out"}}, {tt:.3f});')
        js.append(f'(function(){{ const c = document.getElementById("tmclock"); const st = {{v: 0}};'
                  f' tl.fromTo(st, {{v: 0}}, {{v: 112, duration: 1.6, ease: "none", onUpdate: function(){{ const s = Math.round(st.v);'
                  f' c.textContent = Math.floor(s / 60) + ":" + String(s % 60).padStart(2, "0"); }}}}, {tt + 0.3:.3f}); }})();')
        js.append(f'tl.set("#tmtext", {{textContent: "Called in 2 min"}}, {tt + 1.95:.3f});')
        js.append(f'tl.fromTo("#{sid}-tm .timer", {{backgroundColor: "rgba(20,20,20,0.72)"}}, {{backgroundColor: "rgba(22,120,60,0.85)", duration: 0.3}}, {tt + 1.95:.3f});')
        fx("tick", tt + 1.95, 0.25)

# Talking-head push-ins: slow push on "You're not broken. The system is." plus gentle reframes on long A-roll runs.
js.append(f'tl.fromTo("#cam", {{scale: 1.0}}, {{scale: 1.14, duration: {T_BUILT - T_BROKEN:.3f}, ease: "power1.inOut", immediateRender: false}}, {T_BROKEN:.3f});')
js.append(f'tl.set("#cam", {{scale: 1.0}}, {T_BUILT:.3f});')
broll_windows = sorted((s["t0"], s["t1"]) for s in S)
aroll_runs, last = [], 0.0
for a, b in broll_windows:
    if a - last > 1.2: aroll_runs.append((last, a))
    last = max(last, b)
# Every return to camera alternates wide / tight (jump-cut punch), drifts slowly, and longer runs snap in mid-way.
for k, (a, b) in enumerate(aroll_runs):
    if a <= T_BROKEN < b: continue
    base = 1.0 if k % 2 == 0 else 1.17
    js.append(f'tl.set("#cam", {{scale: {base}}}, {a:.3f});')
    if a > 0.5: fx("whoosh-short", a - 0.1, 0.08)
    if b - a > 2.8:
        mid = round(a + (b - a) * 0.5, 3)
        js.append(f'tl.fromTo("#cam", {{scale: {base}}}, {{scale: {base + 0.03}, duration: {mid - a:.3f}, ease: "none", immediateRender: false}}, {a:.3f});')
        js.append(f'tl.fromTo("#cam", {{scale: {base + 0.03}}}, {{scale: {base + 0.14}, duration: 0.22, ease: "power3.out", immediateRender: false}}, {mid:.3f});')
        js.append(f'tl.fromTo("#cam", {{scale: {base + 0.14}}}, {{scale: {base + 0.16}, duration: {b - mid - 0.22:.3f}, ease: "none", immediateRender: false}}, {mid + 0.22:.3f});')
        fx("whoosh", mid - 0.12, 0.09)
    else:
        js.append(f'tl.fromTo("#cam", {{scale: {base}}}, {{scale: {base + 0.04}, duration: {b - a:.3f}, ease: "none", immediateRender: false}}, {a:.3f});')
js.append(f'tl.set("#cam", {{scale: 1.0}}, {DUR - 0.01:.3f});')

# Light leaks at section turns.
js.append('tl.set("#leak", {opacity: 0, xPercent: -20}, 0);')
for t in (T_BUILT, T_S1, T_S2, T_S3, T_RES, T_APPLY):
    js.append(f'tl.fromTo("#leak", {{opacity: 0, xPercent: -20}}, {{opacity: 0.55, xPercent: 0, duration: 0.45, ease: "power2.out"}}, {t - 0.2:.3f});')
    js.append(f'tl.to("#leak", {{opacity: 0, xPercent: 20, duration: 0.9, ease: "power2.in"}}, {t + 0.25:.3f});')
# Grain: stepped texture offsets (one jump per frame, deterministic).
frames = int(DUR * 25)
js.append(f'tl.fromTo("#grain", {{backgroundPosition: "0px 0px"}}, {{backgroundPosition: "{frames * 337 % 1024}px {frames * 211 % 1024}px",'
          f' duration: {DUR}, ease: "steps({frames})"}}, 0);')

# Pops on the yellow keyphrases, risers into the big turns.
for ix in phrases:
    fx("pop", words[ix[0]]["start"], 0.1)
for t in (t_stop, T_BUILT, T_RES):
    fx("riser", t - 2.6, 0.1, ms=7.4)

cap = []
for gi, (g, s0, e0) in enumerate(G):
    ws = " ".join(f'<span class="{"y" if i in hl else ""}">{html.escape(disp(i))}</span>' for i in g)
    cap.append(f'<div class="cg" id="cg{gi}"><div class="line">{ws}</div></div>')
    js.append(f'tl.fromTo("#cg{gi}", {{opacity: 0, y: 8}}, {{opacity: 1, y: 0, duration: 0.14, ease: "power2.out"}}, {s0:.3f});')
    js.append(f'tl.to("#cg{gi}", {{opacity: 0, duration: 0.08}}, {e0 - 0.08:.3f});')
    js.append(f'tl.set("#cg{gi}", {{opacity: 0, visibility: "hidden"}}, {e0:.3f});')

SRC = {"whoosh-short": "sfx-whoosh-short.mp3", "whoosh": "sfx-whoosh.mp3", "impact": "sfx-impact.mp3", "tick": "sfx-tick.mp3",
       "kaching": "sfx-kaching.wav", "pop": "sfx-pop.mp3", "riser": "sfx-riser.mp3"}
LEN = {k: probe("assets/" + v) for k, v in SRC.items()}
aud = [f'<audio id="fx{n}" src="assets/{SRC[k]}" data-start="{t:.3f}" data-duration="{min(LEN[k] - ms, DUR - t):.3f}"'
       + (f' data-media-start="{ms}"' if ms else "") + f' data-track-index="{40 + n}" data-volume="{v}"></audio>'
       for n, (k, t, v, ms) in enumerate(sorted(sfx, key=lambda x: x[1]))]

tpl = open("tools/vsl.template.html").read()
for k, v in {"{{A_DUR}}": f"{A_DUR}", "{{DUR}}": f"{DUR}", "{{ELEMENTS}}": "\n      ".join(el), "{{CAPTIONS}}": "\n        ".join(cap),
             "{{AUDIO}}": "\n    ".join(aud), "{{JS}}": "\n      ".join(js)}.items():
    tpl = tpl.replace(k, v)
open("index.html", "w").write(tpl)

cover = sum(min(s["t1"], DUR) - s["t0"] for s in S if s["kind"] not in ("stop", "nopay", "endcard"))
ev = sorted({s["t0"] for s in S} | {s["t1"] for s in S} | {a for a, _ in aroll_runs})
gaps = [(round(a, 1), round(b - a, 1)) for a, b in zip(ev, ev[1:]) if b - a > 4.0]
print(f"duration {DUR}s · {len(S)} shots · b-roll {cover:.1f}s = {100 * cover / DUR:.0f}% · {len(G)} caption groups · {len(sfx)} sfx")
print("photos used:", sorted({m for m in used if m.startswith(PHOTOS)}))
print("gaps > 4s:", gaps or "none")
