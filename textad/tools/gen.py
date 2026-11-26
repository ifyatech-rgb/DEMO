"""Text-box ad over the client's roof b-roll: the four white bubble boxes from their reference frame, on screen from
1 s to the last frame. Improvements: staggered pop-in timed for reading, the key words in bold, a soft shadow so
the white boxes lift off bright sky, and a gently pulsing CTA with a bouncing down-arrow. Original sound kept,
with a soft pop on each box."""
import json, os, shutil, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
W, H = 1080, 1920
FMT = sys.argv[1] if len(sys.argv) > 1 else "916"   # "45" writes the 4:5 feed version to ../<project>-4x5
if FMT == "45": H = 1350
# "safe": 9:16 with all text, big, inside the centred 4:5 feed crop (y 285-1635)
DUR = round(float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "assets/source.mp4"],
                                 capture_output=True, text=True).stdout) - 0.03, 3)
BOXES = [  # (id, top px, class, html, in-time)
    ("b1", 250, "tb bold", "Roofing owners: tired<br>of paying for leads<br>that never pick up?", 0.0),
    ("b2", 650, "tb", "Pay only when you<br>sit down with a<br><b>qualified homeowner.</b>", 0.0),
    ("b3", 1000, "tb", "Bad appointment?<br><b>You don’t pay for it.</b>", 0.0),
    ("b4", 1470, "tb bold cta", "Tap below to see if<br>your area is open", 0.0),
]
el, js, aud = [], [], []
FS_N, FS_B = (66, 74)                                  # "safe" font sizes (normal / bold boxes): as big as the widest line allows
if FMT == "45":   # same boxes, re-spaced and a touch smaller to fit 1350 px; the video is centre-cropped
    BOXES = [(b, round(70 + (t - BOXES[0][1]) * 0.74), c, x, tt) for b, t, c, x, tt in BOXES]
if FMT == "safe":   # big text spread evenly over y 330-1570, inside the feed's centre crop (y 285-1635)
    hts = [(x.count("<br>") + 1) * (FS_B if "bold" in c else FS_N) * 1.42 + 14 for _, _, c, x, _ in BOXES]
    gap = (1570 - 330 - sum(hts)) / (len(BOXES) - 1); y, nb = 330.0, []
    for (b, _, c, x, tt), h in zip(BOXES, hts): nb.append((b, round(y), c, x, tt)); y += h + gap
    BOXES = nb
for k, (bid, top, cls, txt, t) in enumerate(BOXES):
    el.append(f'<div class="box" id="{bid}" style="top:{top}px"><div class="{cls}"><span>{txt}</span></div></div>')
    js.append(f'tl.set("#{bid}", {{opacity: 1}}, 0);')
doc = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <title>Roofing Text Ad</title>
    <script src="vendor/gsap.min.js"></script>
    <style>
      @font-face {{ font-family: "Inter"; font-weight: 500; src: url("vendor/inter-latin-500-normal.woff2") format("woff2"); }}
      @font-face {{ font-family: "Inter"; font-weight: 800; src: url("vendor/inter-latin-800-normal.woff2") format("woff2"); }}
      @font-face {{ font-family: "Noto Color Emoji"; src: url("vendor/NotoColorEmoji.ttf") format("truetype"); }}
      body {{ margin: 0; background: #000; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; background: #000; }}
      #src {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; }}
      .box {{ position: absolute; left: 60px; right: 60px; display: flex; justify-content: center; opacity: 1; filter: drop-shadow(0 10px 18px rgba(0,0,0,0.28)); }}
      .tb {{ font-family: "Inter", sans-serif; font-weight: 500; font-size: 64px; line-height: 1.42; color: #111; text-align: center; }}
      .tb span {{ background: #fff; padding: 6px 26px 8px; border-radius: 22px; -webkit-box-decoration-break: clone; box-decoration-break: clone; }}
      .tb b {{ font-weight: 800; }}
      .tb.bold {{ font-weight: 800; font-size: 70px; }}
      .cta {{ transform-origin: 50% 50%; }}
      .arrow {{ position: absolute; left: 0; right: 0; top: 1720px; text-align: center; font-family: "Noto Color Emoji", sans-serif; font-size: 92px; line-height: 1; opacity: 0; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="{W}" data-height="{H}" data-duration="{DUR}">
      <video id="src" class="clip" src="assets/source.mp4" playsinline data-has-audio="true" data-start="0" data-duration="{DUR}" data-track-index="0"></video>
      {chr(10).join("      " + e for e in el).lstrip()}
    </div>
    {chr(10).join("    " + a for a in aud).lstrip()}
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      {chr(10).join("      " + j for j in js).lstrip()}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
if FMT in ("45", "safe"):
    fs = (50, 56) if FMT == "45" else (FS_N, FS_B)
    doc = doc.replace("</style>", f"  .tb {{ font-size: {fs[0]}px; }}\n      .tb.bold {{ font-size: {fs[1]}px; }}\n    </style>", 1)
    OUTD = f"../{os.path.basename(ROOT)}-{'4x5' if FMT == '45' else 'safe'}"; os.makedirs(OUTD, exist_ok=True)
    for x in ("assets", "vendor"):
        if not os.path.lexists(f"{OUTD}/{x}"): shutil.copytree(x, f"{OUTD}/{x}")   # real copies: the renderer does not serve symlinked folders
    for f in ("hyperframes.json", "package.json"): open(f"{OUTD}/{f}", "w").write(open(f).read())
    json.dump({"id": f"{os.path.basename(ROOT)}-{'4x5' if FMT == '45' else 'safe'}"}, open(f"{OUTD}/meta.json", "w"))
    open(f"{OUTD}/index.html", "w").write(doc)
else: open("index.html", "w").write(doc)
print(f"{DUR}s · {len(BOXES)} boxes")
