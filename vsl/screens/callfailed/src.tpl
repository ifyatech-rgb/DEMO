<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=600, height=1300" />
    <title>Call Failed Screen</title>
{{HEAD}}
    <style>
      #root { background: linear-gradient(#3b4252, #1f2430); color: #fff; text-align: center; }
      .status { position: absolute; left: 0; right: 0; top: 18px; display: flex; justify-content: space-between; padding: 0 44px; font-size: 22px; font-weight: 600; }
      .name { position: absolute; left: 0; right: 0; top: 200px; font-size: 52px; font-weight: 500; letter-spacing: -0.5px; }
      .num { position: absolute; left: 0; right: 0; top: 272px; font-size: 26px; color: #c7cdd8; }
      .state { position: absolute; left: 0; right: 0; top: 330px; font-size: 30px; color: #c7cdd8; }
      .failed { color: #ff5a5a; font-weight: 600; opacity: 0; }
      .btns { position: absolute; left: 0; right: 0; bottom: 230px; display: flex; justify-content: center; gap: 150px; }
      .b { width: 140px; text-align: center; font-size: 24px; color: #e5e7eb; }
      .b i { display: block; width: 140px; height: 140px; border-radius: 50%; margin-bottom: 18px; }
      .vm { position: absolute; left: 40px; right: 40px; bottom: 90px; height: 92px; border-radius: 22px; background: rgba(255,255,255,0.12); font-size: 24px; line-height: 92px; opacity: 0; }
      .end { position: absolute; left: 50%; margin-left: -70px; bottom: 230px; width: 140px; height: 140px; border-radius: 50%; background: #ff3b30; }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="600" data-height="1300" data-duration="3.2">
      <div class="status"><span>9:41</span><span>5G ▮▮▮</span></div>
      <div class="name">Roof Lead #4821</div>
      <div class="num">(214) 555-0148</div>
      <div class="state"><span id="calling">calling…</span></div>
      <div class="state failed" id="failed">Call Failed</div>
      <div class="end" id="end"></div>
      <div class="btns" id="btns" style="opacity:0"><div class="b"><i style="background:#4b5563"></i>Cancel</div><div class="b"><i style="background:#34c759"></i>Call Again</div></div>
      <div class="vm" id="vm">Voicemail full · 3rd attempt today</div>
    </div>
    <script>
      const tl = gsap.timeline({ paused: true });
      tl.fromTo("#calling", { opacity: 1 }, { opacity: 0.35, duration: 0.35, yoyo: true, repeat: 3, ease: "sine.inOut" }, 0);
      tl.set("#calling", { opacity: 0 }, 1.4);
      tl.fromTo("#failed", { opacity: 0, scale: 0.9 }, { opacity: 1, scale: 1, duration: 0.2, ease: "power2.out" }, 1.4);
      tl.to("#end", { opacity: 0, scale: 0.6, duration: 0.2 }, 1.4);
      tl.fromTo("#btns", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.3, ease: "power3.out" }, 1.55);
      tl.fromTo("#vm", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.3, ease: "power3.out" }, 2.1);
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
