<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=600, height=1300" />
    <title>Calendar Screen</title>
{{HEAD}}
    <style>
      #root { background: #fff; color: #111; }
      .status { position: absolute; left: 0; right: 0; top: 18px; display: flex; justify-content: space-between; padding: 0 44px; font-size: 22px; font-weight: 600; }
      .hd { position: absolute; left: 36px; top: 80px; font-size: 46px; font-weight: 700; letter-spacing: -0.6px; }
      .hd span { color: #ff3b30; }
      .week { position: absolute; left: 24px; right: 24px; top: 160px; display: flex; justify-content: space-between; }
      .d { width: 70px; text-align: center; font-size: 18px; color: #8e8e93; font-weight: 600; }
      .d b { display: block; margin: 8px auto 0; width: 56px; height: 56px; border-radius: 50%; font-size: 26px; line-height: 56px; color: #111; }
      .d.on b { background: #ff3b30; color: #fff; }
      .grid { position: absolute; left: 0; right: 0; top: 270px; bottom: 0; }
      .hr { position: absolute; left: 0; right: 0; height: 1px; background: #e5e5ea; }
      .hr span { position: absolute; left: 18px; top: -12px; font-size: 18px; color: #8e8e93; background: #fff; padding-right: 8px; }
      .ev { position: absolute; left: 96px; right: 22px; border-radius: 12px; background: #e8f7ee; border-left: 7px solid #34c759; padding: 10px 16px; box-sizing: border-box; opacity: 0; }
      .ev b { display: block; font-size: 23px; font-weight: 700; color: #14532d; }
      .ev span { font-size: 18px; color: #166534; }
      .toast { position: absolute; left: 20px; right: 20px; top: 70px; height: 110px; border-radius: 26px; background: rgba(242,242,247,0.97); box-shadow: 0 12px 30px rgba(0,0,0,0.18); padding: 18px 22px; box-sizing: border-box; opacity: 0; }
      .toast b { display: block; font-size: 22px; margin-bottom: 4px; }
      .toast span { font-size: 20px; color: #3a3a3c; }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="600" data-height="1300" data-duration="4.5">
      <div class="status"><span>9:41</span><span>5G ▮▮▮</span></div>
      <div class="hd">Tuesday <span>Estimates</span></div>
      <div class="week"><div class="d">MON<b>13</b></div><div class="d on">TUE<b>14</b></div><div class="d">WED<b>15</b></div><div class="d">THU<b>16</b></div><div class="d">FRI<b>17</b></div><div class="d">SAT<b>18</b></div></div>
      <div class="grid">
        <div class="hr" style="top:20px"><span>8 AM</span></div><div class="hr" style="top:160px"><span>10 AM</span></div>
        <div class="hr" style="top:300px"><span>12 PM</span></div><div class="hr" style="top:440px"><span>2 PM</span></div>
        <div class="hr" style="top:580px"><span>4 PM</span></div><div class="hr" style="top:720px"><span>6 PM</span></div>
        <div class="ev" id="ev-0" style="top:28px;height:120px"><b>Roof estimate · J. Miller</b><span>Full replacement · budget confirmed</span></div>
        <div class="ev" id="ev-1" style="top:168px;height:120px"><b>Roof estimate · R. Alvarez</b><span>Hail damage · insurance approved</span></div>
        <div class="ev" id="ev-2" style="top:308px;height:120px"><b>Roof estimate · K. Thompson</b><span>Owns home · ready this month</span></div>
        <div class="ev" id="ev-3" style="top:448px;height:120px"><b>Roof estimate · D. Nguyen</b><span>Re-roof · financing pre-qualified</span></div>
        <div class="ev" id="ev-4" style="top:588px;height:120px"><b>Roof estimate · S. Patel</b><span>Leak + replacement · wants to start</span></div>
      </div>
      <div class="toast" id="toast"><b>New appointment booked</b><span>Roof estimate · Tue 4:00 PM</span></div>
    </div>
    <script>
      const tl = gsap.timeline({ paused: true });
      for (let i = 0; i < 5; i++) {
        tl.fromTo("#ev-" + i, { opacity: 0, scale: 0.92, x: 30 }, { opacity: 1, scale: 1, x: 0, duration: 0.3, ease: "back.out(1.6)" }, 0.3 + i * 0.6);
      }
      tl.fromTo("#toast", { opacity: 0, y: -60 }, { opacity: 1, y: 0, duration: 0.35, ease: "power3.out" }, 2.75);
      tl.to("#toast", { opacity: 0, y: -40, duration: 0.3, ease: "power2.in" }, 4.0);
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
