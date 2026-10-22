<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=600, height=1300" />
    <title>Social Ad Screen</title>
{{HEAD}}
    <style>
      #root { background: #f0f2f5; color: #050505; }
      .status { position: absolute; left: 0; right: 0; top: 18px; display: flex; justify-content: space-between; padding: 0 44px; font-size: 22px; font-weight: 600; }
      .bar { position: absolute; left: 0; right: 0; top: 60px; height: 70px; background: #fff; border-bottom: 1px solid #dddfe2; display: flex; align-items: center; padding: 0 24px; font-size: 30px; font-weight: 800; color: #1c1e21; }
      .post { position: absolute; left: 0; right: 0; top: 150px; background: #fff; }
      .ph { display: flex; align-items: center; gap: 14px; padding: 18px 22px; }
      .av { width: 60px; height: 60px; border-radius: 50%; background: linear-gradient(135deg, #b45309, #78350f); color: #fff; font-size: 26px; font-weight: 800; line-height: 60px; text-align: center; }
      .pn { font-size: 22px; font-weight: 700; }
      .pn span { display: block; font-size: 17px; font-weight: 500; color: #65676b; }
      .txt { padding: 0 22px 16px; font-size: 21px; line-height: 1.35; }
      .media { position: relative; width: 600px; height: 600px; overflow: hidden; background: #000; }
      .media img { position: absolute; left: 0; top: 0; width: 600px; height: 600px; }
      .prog { position: absolute; left: 0; bottom: 0; height: 6px; width: 600px; background: rgba(255,255,255,0.3); }
      .prog i { display: block; height: 6px; width: 600px; background: #fff; transform-origin: 0 50%; }
      .cap { position: absolute; left: 22px; right: 22px; bottom: 30px; font-size: 30px; font-weight: 800; color: #fff; text-shadow: 0 2px 12px rgba(0,0,0,0.7); }
      .cta { display: flex; align-items: center; justify-content: space-between; padding: 16px 22px; background: #f0f2f5; }
      .cta div { font-size: 19px; color: #65676b; }
      .cta div b { display: block; font-size: 22px; color: #050505; }
      .cta span { padding: 12px 20px; border-radius: 10px; background: #e4e6eb; font-size: 20px; font-weight: 700; }
      .react { display: flex; justify-content: space-around; padding: 14px 0; font-size: 20px; font-weight: 600; color: #65676b; border-top: 1px solid #e4e6eb; }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="600" data-height="1300" data-duration="4">
      <div class="status"><span>9:41</span><span>5G ▮▮▮</span></div>
      <div class="bar">Feed</div>
      <div class="post" id="post">
        <div class="ph"><div class="av">YR</div><div class="pn">Your Roofing Co.<span>Sponsored · Your city</span></div></div>
        <div class="txt">Meet Mike and the crew who've replaced 2,400 roofs across Dallas. Same faces, start to finish.</div>
        <div class="media"><img id="img" src="ad.jpg" alt="" /><div class="cap" id="cap">Your roof. Our crew. Done right.</div><div class="prog"><i id="prog"></i></div></div>
        <div class="cta"><div>Local, family-owned crew<b>Book a roof inspection</b></div><span>Book now</span></div>
        <div class="react"><span>Like</span><span>Comment</span><span>Share</span></div>
      </div>
    </div>
    <script>
      const tl = gsap.timeline({ paused: true });
      tl.fromTo("#post", { y: 140 }, { y: 0, duration: 0.6, ease: "power3.out" }, 0);
      tl.fromTo("#img", { scale: 1.0 }, { scale: 1.12, duration: 4, ease: "none" }, 0);
      tl.fromTo("#prog", { scaleX: 0 }, { scaleX: 0.45, duration: 4, ease: "none" }, 0);
      tl.fromTo("#cap", { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }, 0.8);
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
