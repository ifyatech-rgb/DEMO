<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1600, height=1000" />
    <title>Lead Inbox Screen</title>
{{HEAD}}
    <style>
      #root { background: #f5f6f8; color: #111827; }
      /* Rendered small inside a laptop shot: lay out at 1103x690 and zoom 1.45x so text stays legible. */
      #ui { position: relative; width: 1103px; height: 690px; zoom: 1.45; }
      .top { position: absolute; left: 0; right: 0; top: 0; height: 64px; background: #fff; border-bottom: 1px solid #e5e7eb; display: flex; align-items: center; padding: 0 28px; gap: 18px; }
      .brand { font-weight: 800; font-size: 22px; color: #0f172a; letter-spacing: -0.3px; }
      .brand span { color: #2563eb; }
      .search { margin-left: 40px; width: 520px; height: 38px; border-radius: 10px; background: #f1f5f9; color: #94a3b8; font-size: 16px; line-height: 38px; padding-left: 16px; }
      .bell { margin-left: auto; position: relative; width: 38px; height: 38px; border-radius: 50%; background: #f1f5f9; }
      .badge { position: absolute; right: -6px; top: -6px; min-width: 26px; height: 26px; border-radius: 13px; background: #ef4444; color: #fff; font-size: 14px; font-weight: 700; line-height: 26px; text-align: center; padding: 0 6px; box-sizing: border-box; }
      .side { position: absolute; left: 0; top: 64px; bottom: 0; width: 240px; background: #fff; border-right: 1px solid #e5e7eb; padding: 24px 18px; box-sizing: border-box; }
      .nav { height: 42px; border-radius: 10px; font-size: 17px; font-weight: 500; color: #475569; line-height: 42px; padding-left: 14px; margin-bottom: 6px; }
      .nav.on { background: #eff6ff; color: #1d4ed8; font-weight: 600; }
      .nav b { float: right; margin-right: 12px; font-size: 14px; color: #1d4ed8; }
      .main { position: absolute; left: 270px; right: 30px; top: 94px; bottom: 30px; }
      h1 { margin: 0 0 6px; font-size: 30px; font-weight: 700; letter-spacing: -0.5px; }
      .sub { font-size: 16px; color: #64748b; margin-bottom: 20px; }
      .list { position: relative; background: #fff; border: 1px solid #e5e7eb; border-radius: 14px; overflow: hidden; height: 520px; }
      .row { position: absolute; left: 0; right: 0; height: 74px; border-bottom: 1px solid #f1f5f9; display: flex; align-items: center; padding: 0 22px; gap: 16px; background: #fff; box-sizing: border-box; }
      .dot { width: 10px; height: 10px; border-radius: 50%; background: #2563eb; flex: none; }
      .who { width: 170px; font-size: 17px; font-weight: 600; }
      .what { flex: 1; font-size: 16px; color: #475569; white-space: nowrap; overflow: hidden; }
      .src { font-size: 13px; font-weight: 600; padding: 5px 10px; border-radius: 8px; background: #f1f5f9; color: #475569; }
      .price { width: 80px; text-align: right; font-size: 16px; font-weight: 700; color: #b91c1c; }
      .time { width: 80px; text-align: right; font-size: 14px; color: #94a3b8; }
      .toast { position: absolute; right: 28px; width: 400px; height: 86px; border-radius: 14px; background: #0f172a; color: #fff; box-shadow: 0 18px 40px rgba(15, 23, 42, 0.35); padding: 16px 20px; box-sizing: border-box; opacity: 0; }
      .toast b { display: block; font-size: 17px; margin-bottom: 4px; }
      .toast span { font-size: 15px; color: #cbd5e1; }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="1600" data-height="1000" data-duration="5">
      <div id="ui">
      <div class="top"><div class="brand">Lead<span>Desk</span></div><div class="search">Search leads…</div><div class="bell"><div class="badge" id="badge">3</div></div></div>
      <div class="side">
        <div class="nav on">Inbox <b id="navcount">3</b></div><div class="nav">Purchased</div><div class="nav">Contacted</div><div class="nav">No answer</div><div class="nav">Disputes</div><div class="nav">Billing</div>
      </div>
      <div class="main">
        <h1>New leads</h1>
        <div class="sub">Shared leads · sold to up to 5 contractors</div>
        <div class="list" id="list">{{ROWS}}</div>
      </div>
      {{TOASTS}}
      </div>
    </div>
    <script>
      const ROWS = {{N}};
      const tl = gsap.timeline({ paused: true });
      // New lead rows slide in at the top one after another, pushing older rows down.
      for (let i = 0; i < ROWS; i++) {
        const t = 0.25 + i * 0.42;
        tl.fromTo("#row-" + i, { y: -74, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3, ease: "power3.out" }, t);
        for (let j = 0; j < i; j++) tl.to("#row-" + j, { y: "+=74", duration: 0.3, ease: "power3.out" }, t);
        for (let j = 0; j < 3; j++) tl.to("#old-" + j, { y: "+=74", duration: 0.3, ease: "power3.out" }, t);
        tl.set("#badge", { textContent: 4 + i }, t);
        tl.set("#navcount", { textContent: 4 + i }, t);
      }
      for (let k = 0; k < 3; k++) {
        tl.fromTo("#toast-" + k, { opacity: 0, x: 60 }, { opacity: 1, x: 0, duration: 0.3, ease: "power3.out" }, 0.6 + k * 1.3);
        tl.to("#toast-" + k, { opacity: 0, duration: 0.25 }, 1.8 + k * 1.3);
      }
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
