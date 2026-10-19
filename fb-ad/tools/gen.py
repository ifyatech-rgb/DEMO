"""Build index.html (captions, punch-ins, pop-ups, CTA) from transcript.json of assets/cut.mp4."""
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

YELLOW = ["5 to 10 roofs", "garbage", "don't pay me", "afford a roof", "no monthly retainers",
          "pay per estimate", "exclusive", "your calendar", "one roofing contractor per area"]
hl, phrase_of, phrases = set(), {}, []
for p in YELLOW:
    ix = find(p); phrases.append(ix); hl.update(ix)
    for i in ix: phrase_of[i] = len(phrases) - 1
for i, w in enumerate(words):
    if disp(w["text"]) == "FACE-TO-FACE": hl.add(i)

# 2-3 word groups. Yellow phrases are packed as atomic units (4 words -> 3+1, 5 -> 2+3) so they read together.
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

def span(ix):
    return words[ix[0]]["start"], words[ix[-1]]["end"]
ZOOMS = [span(find("stop buying garbage angie leads")), span(find("don't pay me anything")),
         span(find("only pay per estimate")), span(find("one roofing contractor per area"))]
nr = find("no monthly retainers"); ppe = find("only pay per estimate"); one = find("one roofing contractor per area")
POPS = [("NO RETAINERS", words[nr[0]]["start"], words[ppe[0]]["start"] - 0.05),
        ("PAY PER ESTIMATE", words[ppe[0]]["start"], words[ppe[-1]]["end"] + 0.6),
        ("1 ROOFER PER AREA", words[one[0]]["start"], DUR)]
CTA_START = words[find("as we only work")[0]]["start"]

cap_html = []
for gi, (g, s, e) in enumerate(G):
    ws = "".join(f'<span class="w{" hl" if i in hl else ""}" id="w{i}">{html.escape(disp(words[i]["text"]))}</span>' for i in g)
    cap_html.append(f'      <div class="cg" id="cg-{gi}">{ws}</div>')
pop_html = [f'    <div class="clip pop" id="pop-{k}" data-start="{s:.3f}" data-duration="{e - s:.3f}" data-track-index="{4 + k % 2}">'
            f'<span class="pill" id="pill-{k}">{t}</span></div>' for k, (t, s, e) in enumerate(POPS)]
data = {"groups": [{"words": g, "start": s, "end": e} for g, s, e in G],
        "words": [{"start": round(w["start"], 3), "end": round(w["end"], 3)} for w in words],
        "zooms": [[round(a, 3), round(b, 3)] for a, b in ZOOMS], "pops": len(POPS)}

tpl = open("tools/index.template.html").read()
out = (tpl.replace("{{DUR}}", f"{DUR}").replace("{{CAPTIONS}}", "\n".join(cap_html))
          .replace("{{POPS}}", "\n".join(pop_html)).replace("{{DATA}}", json.dumps(data))
          .replace("{{CTA_START}}", f"{CTA_START:.3f}").replace("{{CTA_DUR}}", f"{DUR - CTA_START:.3f}"))
open("index.html", "w").write(out)
print(f"duration {DUR}s, {len(G)} caption groups, zooms {data['zooms']}, pops {[(t, round(s,2), round(e,2)) for t,s,e in POPS]}, cta {CTA_START:.2f}")
for g, s, e in G: print(f"  {s:6.2f}-{e:6.2f} " + " ".join(("*" if i in hl else "") + disp(words[i]["text"]) for i in g))
