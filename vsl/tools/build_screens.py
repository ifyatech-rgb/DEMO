"""Assemble the device-screen UI compositions (screens/<name>/src.tpl -> index.html) and copy vendor files.

Each screen is rendered on its own (npx hyperframes render screens/<name>) and then warped into the
green-screen laptop/phone footage by tools/screen_comp.py.
"""
import os, shutil
HERE = os.path.join(os.path.dirname(__file__), "..", "screens")
head = open(os.path.join(HERE, "head.html")).read()

LEADS = [("Mike R.", "Roof replacement – wants 3 quotes", "Marketplace", "$87", "now"),
         ("Dana P.", "Leak repair – just looking for prices", "Directory", "$64", "1m"),
         ("Steve K.", "Roof inspection – price check only", "Social ads", "$41", "2m"),
         ("Tara L.", "Full re-roof – comparing bids", "Marketplace", "$92", "3m"),
         ("Josh M.", "Storm damage – already hired someone?", "Home app", "$78", "4m"),
         ("Linda W.", "Gutter + roof quote – no timeline", "Directory", "$55", "6m"),
         ("Carlos G.", "Shingle repair – cheapest option", "Marketplace", "$71", "8m"),
         ("Amy H.", "New roof – ‘just curious’", "Social ads", "$38", "9m"),
         ("Ben T.", "Roof replacement – wrong number?", "Home app", "$83", "11m"),
         ("Rita S.", "Leak – renting, landlord decides", "Directory", "$49", "12m")]
OLD = [("Greg F.", "No answer – 4 attempts", "Marketplace", "$85", "1h"),
       ("Kim D.", "Went with lowest bid", "Directory", "$66", "2h"),
       ("Paul N.", "Disconnected number", "Social ads", "$44", "3h")]

def row(rid, l, top, cls=""):
    who, what, src, price, t = l
    dot = ' style="background:#cbd5e1"' if cls else ""
    return (f'<div class="row {cls}" id="{rid}" style="top:{top}px"><div class="dot"{dot}></div>'
            f'<div class="who">{who}</div><div class="what">{what}</div><div class="src">{src}</div>'
            f'<div class="price">{price}</div><div class="time">{t}</div></div>')

def build(name, rep):
    d = os.path.join(HERE, name)
    s = open(os.path.join(d, "src.tpl")).read().replace("{{HEAD}}", head)
    for k, v in rep.items(): s = s.replace(k, v)
    open(os.path.join(d, "index.html"), "w").write(s)
    os.makedirs(os.path.join(d, "vendor"), exist_ok=True)
    for f in os.listdir(os.path.join(HERE, "..", "vendor")):
        if f.endswith((".woff2", ".js")): shutil.copy(os.path.join(HERE, "..", "vendor", f), os.path.join(d, "vendor", f))
    shutil.copy(os.path.join(HERE, "..", "hyperframes.json"), os.path.join(d, "hyperframes.json"))

rows = "".join(row(f"row-{i}", l, 0) for i, l in enumerate(reversed(LEADS)))
rows += "".join(row(f"old-{i}", l, i * 74, "old") for i, l in enumerate(OLD))
toasts = "".join(f'<div class="toast" id="toast-{k}" style="top:{84 + k * 0}px"><b>{t}</b><span>{s}</span></div>'
                 for k, (t, s) in enumerate([("New lead purchased · $87", "Also sent to 4 other roofers"),
                                             ("New lead purchased · $64", "Also sent to 5 other roofers"),
                                             ("New lead purchased · $92", "Also sent to 3 other roofers")]))
build("inbox", {"{{ROWS}}": rows, "{{TOASTS}}": toasts, "{{N}}": str(len(LEADS))})
for name in ("callfailed", "socialad", "calendar"):
    if os.path.exists(os.path.join(HERE, name, "src.tpl")): build(name, {})
print("built")
