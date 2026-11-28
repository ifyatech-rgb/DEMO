"""Light-touch edit of ad_1_for_feed.mp4: full 39.3 s, no cut, no crop, no zoom, speaker untouched.
Only: black over the old header line (with NO ESTIMATE = NO PAY where NO LEADS = NO PAY used to be), new captions
in the bottom bar (replacing the old ones), 4 simple 1.5 s cutaways over the top 1139 px, a 2 s navy end card.
At most one added element at a time; no chips, tags, badges, particles, glows, pops, music or SFX."""
import html, json, os, re, shutil
ROOT = os.path.dirname(os.path.abspath(__file__)); os.chdir(ROOT)
W, H, DUR, PY1 = 1080, 1350, 39.3, 1139
NAVY, ORANGE, YELLOW = "#0F1B2D", "#FF7A1A", "#FFD400"
words = json.load(open("../edit_v2/work/transcript.json"))
NOLEADS = json.load(open("work/noleads.json"))["no_leads_header"]
CUTS = [("trash", 3.30), ("phone", 17.87), ("calendar", 23.10), ("area", 35.80)]   # 1.5 s each
END0 = DUR - 2.0
el, js = [], []
def fade(sel, a, b, d=0.13):
    js.append(f'tl.fromTo("{sel}", {{opacity: 0}}, {{opacity: 1, duration: {d}, ease: "none"}}, {a:.3f});')
    if b < DUR - 0.01: js.append(f'tl.to("{sel}", {{opacity: 0, duration: {d}, ease: "none"}}, {b - d:.3f});')

# header: old text hidden; NO ESTIMATE = NO PAY in the old line's slots (hidden under cutaways automatically: they sit above)
for k, (a, b) in enumerate(NOLEADS):
    el.append(f'<div class="clip hl" id="hl{k}" data-start="{a:.3f}" data-duration="{b - a:.3f}" data-track-index="{10 + k}">NO ESTIMATE = <span class="y">NO PAY</span></div>')
    fade(f"#hl{k}", a, b)

# cutaways: simple, calm animations (no stock footage available)
def scene(kind):
    if kind == "trash":
        cards = "".join(f'<g id="tc{k}"><rect x="-90" y="-56" width="180" height="112" rx="14" fill="#fff"/><rect x="-64" y="-30" width="96" height="14" rx="7" fill="#C9D1DD"/>'
                        f'<rect x="-64" y="0" width="128" height="10" rx="5" fill="#E3E8EF"/><rect x="-64" y="20" width="100" height="10" rx="5" fill="#E3E8EF"/></g>' for k in range(3))
        return ('<path d="M380 520 L415 900 Q418 918 436 918 H644 Q662 918 665 900 L700 520 Z" fill="#8C97AB"/>'
                '<path d="M455 560 L466 870 M540 560 V870 M625 560 L614 870" stroke="#6B7689" stroke-width="16" stroke-linecap="round"/>'
                '<g id="tlid"><rect x="350" y="470" width="380" height="50" rx="16" fill="#AEB8C9"/><rect x="490" y="440" width="100" height="36" rx="12" fill="#AEB8C9"/></g>'
                + cards + '<text x="540" y="1040" text-anchor="middle" class="st">SHARED LEADS</text>')
    if kind == "phone":
        return ("".join(f'<circle id="pr{k}" cx="540" cy="540" r="170" fill="none" stroke="{ORANGE}" stroke-width="10" opacity="0"/>' for k in range(2)) +
                '<g id="ph"><rect x="380" y="200" width="320" height="660" rx="50" fill="#0B1424" stroke="#fff" stroke-width="10"/>'
                '<circle cx="540" cy="410" r="66" fill="#2C3C56"/><circle cx="540" cy="390" r="26" fill="#C9D1DD"/><path d="M498 456 Q540 410 582 456" fill="#C9D1DD"/>'
                '<text x="540" y="530" text-anchor="middle" class="sm">HOMEOWNER</text>'
                f'<circle id="pbtn" cx="540" cy="740" r="52" fill="#22C55E"/></g>'
                '<g id="pn" opacity="0"><rect x="250" y="70" width="580" height="100" rx="26" fill="#fff"/><circle cx="310" cy="120" r="28" fill="#22C55E"/>'
                f'<text x="360" y="133" class="nt">Call connected</text></g>')
    if kind == "calendar":
        out = ['<rect x="110" y="190" width="860" height="700" rx="30" fill="#fff"/><rect x="110" y="190" width="860" height="96" rx="30" fill="#E8EDF4"/>']
        for d, day in enumerate(["MON", "TUE", "WED", "THU", "FRI"]):
            out.append(f'<text x="{196 + d * 172}" y="252" text-anchor="middle" class="dy">{day}</text>')
            for r in range(3): out.append(f'<rect x="{130 + d * 172}" y="{310 + r * 186}" width="150" height="166" rx="14" fill="#F2F5F9"/>')
        for k, (d, r) in enumerate([(0, 0), (2, 1), (4, 0), (1, 2), (3, 1), (2, 0)]):
            out.append(f'<g id="cs{k}" opacity="0"><rect x="{130 + d * 172}" y="{310 + r * 186}" width="150" height="166" rx="14" fill="{ORANGE}"/>'
                       f'<text x="{205 + d * 172}" y="{400 + r * 186}" text-anchor="middle" class="sl">ESTIMATE</text></g>')
        return "".join(out)
    if kind == "area":
        NC = "M18 158 L130 118 L265 112 L400 90 L575 66 L755 48 L930 30 L1040 18 L1058 66 L1022 116 L972 156 L906 214 L818 244 L730 230 L664 270 L553 266 L453 230 L353 230 L265 216 L155 230 L66 248 L26 222 Z"
        return (f'<g transform="translate(40 330) scale(0.926)"><path d="{NC}" fill="#1E2E4A" stroke="#fff" stroke-width="7" stroke-linejoin="round"/>'
                + "".join(f'<circle cx="{x}" cy="{y}" r="18" fill="{ORANGE}"/>' for x, y in ((386, 205), (580, 122), (735, 140)))
                + f'<g id="lk" opacity="0"><rect x="700" y="66" width="70" height="56" rx="10" fill="{YELLOW}"/><path d="M714 68 v-16 a21 21 0 0 1 42 0 v16" fill="none" stroke="{YELLOW}" stroke-width="10"/></g></g>'
                '<text x="540" y="760" text-anchor="middle" class="st">ONE ROOFER PER AREA</text>')
def animate(kind, a):
    if kind == "trash":
        js.append(f'tl.fromTo("#tlid", {{rotation: 0, svgOrigin: "350 520"}}, {{rotation: -30, svgOrigin: "350 520", duration: 0.25, ease: "power2.out"}}, {a + 0.1:.3f});')
        for k in range(3):
            t = a + 0.3 + k * 0.22
            js.append(f'tl.fromTo("#tc{k}", {{x: {360 + k * 180}, y: 120, rotation: {(k - 1) * 20}, opacity: 1}}, {{x: 540, y: 640, rotation: {(1 - k) * 30}, duration: 0.4, ease: "power2.in"}}, {t:.3f});')
            js.append(f'tl.to("#tc{k}", {{opacity: 0, duration: 0.04}}, {t + 0.4:.3f});')
        js.append(f'tl.to("#tlid", {{rotation: 0, svgOrigin: "350 520", duration: 0.15}}, {a + 1.15:.3f});')
    if kind == "phone":
        for k in range(2): js.append(f'tl.fromTo("#pr{k}", {{attr: {{r: 170}}, opacity: 0.7}}, {{attr: {{r: 340}}, opacity: 0, duration: 0.7}}, {a + 0.05 + k * 0.3:.3f});')
        js.append(f'tl.fromTo("#pn", {{opacity: 0, y: -40}}, {{opacity: 1, y: 0, duration: 0.3, ease: "power2.out"}}, {a + 0.75:.3f});')
    if kind == "calendar":
        for k in range(6): js.append(f'tl.fromTo("#cs{k}", {{opacity: 0, scale: 0.8, transformOrigin: "50% 50%"}}, {{opacity: 1, scale: 1, duration: 0.15, ease: "power2.out"}}, {a + 0.2 + k * 0.17:.3f});')
    if kind == "area":
        js.append(f'tl.fromTo("#lk", {{opacity: 0, y: -30}}, {{opacity: 1, y: 0, duration: 0.2, ease: "power2.out"}}, {a + 0.5:.3f});')
for n, (kind, a) in enumerate(CUTS):
    b = a + 1.5
    el.append(f'<div class="clip cut" id="cut{n}" data-start="{a:.3f}" data-duration="{1.5 if b < END0 - 0.01 else 2.0:.1f}" data-track-index="{20 + n}">'
              f'<svg viewBox="0 0 1080 1139" width="1080" height="1139">{scene(kind)}</svg></div>')
    fade(f"#cut{n}", a, b if b < END0 - 0.01 else DUR, 0.13)   # the last cutaway stays solid under the end card (old red pill never shows)
    animate(kind, a)

# end card (last 2 s)
el.append(f'<div class="clip endc" id="endc" data-start="{END0:.3f}" data-duration="2.0" data-track-index="40"><div class="tap">TAP SEND<br>MESSAGE</div></div>')
js.append(f'tl.fromTo("#endc", {{opacity: 0}}, {{opacity: 1, duration: 0.2, ease: "none"}}, {END0:.3f});')

# captions: one style, <= 3 words, bottom bar only, active word yellow
ws = []
for w in words:
    d = re.sub(r"^-", "", w["text"]).upper().strip(",.?!")
    if w["text"].startswith("-") and ws: ws[-1]["d"] += "-" + d; ws[-1]["end"] = w["end"]
    else: ws.append(dict(w, d=d))
groups, cur = [], []
for k, w in enumerate(ws):
    if cur and (len(cur) >= 3 or re.search(r"[.,?!]$", ws[cur[-1]]["text"]) or w["start"] - ws[cur[-1]]["end"] > 0.3): groups.append(cur); cur = []
    cur.append(k)
groups.append(cur)
def em(s): return sum(0.40 if c == " " else 0.36 if c in ",.'-?!" else 0.95 if c in "MW" else 0.36 if c in "I1" else 0.74 for c in s)
cap = []
for gi, g in enumerate(groups):
    t0 = max(0.0, ws[g[0]]["start"] - 2 / 30)
    if t0 >= END0: continue
    t1 = ws[groups[gi + 1][0]]["start"] - 2 / 30 if gi + 1 < len(groups) else END0
    t1 = min(t1, ws[g[-1]]["end"] + 0.5, END0)
    fs = min(68, int(920 / em(" ".join(ws[k]["d"] for k in g))))
    cap.append(f'<div class="cg" id="cg{gi}" style="font-size:{fs}px">' + " ".join(f'<span class="w" id="w{k}">{html.escape(ws[k]["d"])}</span>' for k in g) + "</div>")
    js.append(f'tl.set("#cg{gi}", {{opacity: 1}}, {t0:.3f}); tl.set("#cg{gi}", {{opacity: 0}}, {t1:.3f});')
    for k in g:
        a = max(t0, ws[k]["start"] - 2 / 30); b = max(a + 0.08, min(ws[k]["end"], t1))
        js.append(f'tl.set("#w{k}", {{color: "{YELLOW}"}}, {a:.3f}); tl.set("#w{k}", {{color: "#ffffff"}}, {b:.3f});')

doc = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <title>HRP Ad 1 Light</title>
    <script src="vendor/gsap.min.js"></script>
    <style>
      @font-face {{ font-family: "Montserrat"; font-weight: 800; src: url("vendor/montserrat-latin-800-normal.woff2") format("woff2"); }}
      @font-face {{ font-family: "Montserrat"; font-weight: 900; src: url("vendor/montserrat-latin-900-normal.woff2") format("woff2"); }}
      body {{ margin: 0; background: #000; }}
      #root {{ position: relative; width: {W}px; height: {H}px; overflow: hidden; background: #000; font-family: "Montserrat", sans-serif; font-weight: 900; color: #fff; }}
      #base {{ position: absolute; inset: 0; width: {W}px; height: {H}px; }}
      .bar {{ position: absolute; left: 0; right: 0; background: #000; }}
      .y {{ color: {YELLOW}; }}
      .hl {{ position: absolute; left: 0; right: 0; top: 60px; text-align: center; font-size: 52px; opacity: 0; }}
      .cut {{ position: absolute; left: 0; top: 0; width: {W}px; height: {PY1}px; background: linear-gradient(180deg, #16243A 0%, {NAVY} 100%); opacity: 0; }}
      .cut svg {{ display: block; }}
      .st {{ font: 900 62px Montserrat; fill: #fff; letter-spacing: 1px; }}
      .sm {{ font: 900 34px Montserrat; fill: #fff; }}
      .nt {{ font: 800 38px Montserrat; fill: {NAVY}; }}
      .dy {{ font: 900 30px Montserrat; fill: {NAVY}; }}
      .sl {{ font: 900 22px Montserrat; fill: #fff; }}
      .endc {{ position: absolute; inset: 0; background: {NAVY}; display: flex; align-items: center; justify-content: center; opacity: 0; }}
      .tap {{ font-size: 130px; line-height: 1.0; text-align: center; color: #fff; }}
      #captions {{ position: absolute; left: 60px; right: 60px; top: {PY1}px; height: {H - PY1}px; }}
      .cg {{ position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; gap: 0 0.28em; white-space: nowrap; opacity: 0; }}
      .w {{ color: #fff; -webkit-text-stroke: 6px #000; paint-order: stroke fill; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="{W}" data-height="{H}" data-duration="{DUR}">
      <video id="base" class="clip" src="assets/base.mp4" muted playsinline data-start="0" data-duration="{DUR}" data-track-index="0"></video>
      <div class="bar" style="top:0;height:211px"></div>
      <div class="bar" style="top:{PY1}px;height:{H - PY1}px"></div>
      {chr(10).join("      " + e for e in el).lstrip()}
      <div id="captions" class="clip" data-start="0" data-duration="{DUR}" data-track-index="50">
        {chr(10).join("        " + c for c in cap).lstrip()}
      </div>
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      {chr(10).join("      " + j for j in js).lstrip()}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
os.makedirs("remotion/assets", exist_ok=True)
if not os.path.exists("remotion/vendor"): shutil.copytree("../edit_v2/remotion/f45/vendor", "remotion/vendor")
for f in ("package.json", "hyperframes.json"): shutil.copy(f"../edit_v2/remotion/f45/{f}", f"remotion/{f}")
json.dump({"id": "hrp-ad1-light"}, open("remotion/meta.json", "w"))
shutil.copy("work/base.mp4", "remotion/assets/base.mp4")
open("remotion/index.html", "w").write(doc)
print(f"{len(CUTS)} cutaways, end card {END0:.1f}-{DUR}, {len(cap)} captions, NO ESTIMATE slots {NOLEADS}")
