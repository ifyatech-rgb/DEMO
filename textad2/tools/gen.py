"""Text-box ad over the client's roof b-roll: the four white bubble boxes from their reference frame, on screen from
1 s to the last frame. Improvements: staggered pop-in timed for reading, the key words in bold, a soft shadow so
the white boxes lift off bright sky, and a gently pulsing CTA with a bouncing down-arrow. Original sound kept,
with a soft pop on each box."""
import os, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
W, H = 1080, 1920
DUR = round(float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "assets/source.mp4"],
                                 capture_output=True, text=True).stdout) - 0.03, 3)
BOXES = [  # (id, top px, class, html, in-time)
    ("b1", 370, "tb bold", "“I was just curious<br>what a roof costs.”", 1.0),
    ("b2", 690, "tb", "That’s not a lead.<br>That’s a <b>tire kicker</b> you paid for.", 2.4),
    ("b3", 960, "tb", "We put you at the kitchen table<br>with homeowners who are <b>ready</b><br><b>for a new roof.</b>", 3.9),
    ("b4", 1310, "tb", "<b>You pay per sit.</b><br>Not per lead. Not per click.", 5.5),
    ("b5", 1570, "tb bold cta", "Tap below to see if<br>your area is open", 6.9),
]
el, js, aud = [], [], []
for k, (bid, top, cls, txt, t) in enumerate(BOXES):
    el.append(f'<div class="box" id="{bid}" style="top:{top}px"><div class="{cls}"><span>{txt}</span></div></div>')
    js.append(f'tl.fromTo("#{bid}", {{opacity: 0, scale: 0.82, y: 24}}, {{opacity: 1, scale: 1, y: 0, duration: 0.32, ease: "back.out(2)"}}, {t:.2f});')
    aud.append(f'<audio id="p{k}" src="assets/pop.wav" data-start="{t:.2f}" data-duration="0.08" data-track-index="{10 + k}" data-volume="0.25"></audio>')
C0 = BOXES[-1][4]
el.append('<div class="arrow" id="arw">👇</div>')
js.append(f'tl.fromTo("#arw", {{opacity: 0, y: -10}}, {{opacity: 1, y: 0, duration: 0.25}}, {C0 + 0.35:.2f});')
js.append(f'tl.fromTo("#arw", {{y: 0}}, {{y: 18, duration: 0.35, ease: "sine.inOut", yoyo: true, repeat: {int((DUR - C0 - 0.7) / 0.35)}, immediateRender: false}}, {C0 + 0.6:.2f});')
js.append(f'tl.fromTo("#b4 .tb", {{scale: 1}}, {{scale: 1.04, duration: 0.45, ease: "sine.inOut", yoyo: true, repeat: {int((DUR - C0 - 0.6) / 0.45)}, immediateRender: false}}, {C0 + 0.45:.2f});')

doc = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <title>Roofing Text Ad 2</title>
    <script src="vendor/gsap.min.js"></script>
    <style>
      @font-face {{ font-family: "Inter"; font-weight: 500; src: url("vendor/inter-latin-500-normal.woff2") format("woff2"); }}
      @font-face {{ font-family: "Inter"; font-weight: 800; src: url("vendor/inter-latin-800-normal.woff2") format("woff2"); }}
      @font-face {{ font-family: "Noto Color Emoji"; src: url("vendor/NotoColorEmoji.ttf") format("truetype"); }}
      body {{ margin: 0; background: #000; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; background: #000; }}
      #src {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; }}
      .box {{ position: absolute; left: 60px; right: 60px; display: flex; justify-content: center; opacity: 0; filter: drop-shadow(0 10px 18px rgba(0,0,0,0.28)); }}
      .tb {{ font-family: "Inter", sans-serif; font-weight: 500; font-size: 58px; line-height: 1.42; color: #111; text-align: center; }}
      .tb span {{ background: #fff; padding: 6px 26px 8px; border-radius: 22px; -webkit-box-decoration-break: clone; box-decoration-break: clone; }}
      .tb b {{ font-weight: 800; }}
      .tb.bold {{ font-weight: 800; font-size: 70px; }}
      .cta {{ transform-origin: 50% 50%; }}
      .arrow {{ position: absolute; left: 0; right: 0; top: 1790px; text-align: center; font-family: "Noto Color Emoji", sans-serif; font-size: 80px; line-height: 1; opacity: 0; }}
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
open("index.html", "w").write(doc)
print(f"{DUR}s · {len(BOXES)} boxes")
