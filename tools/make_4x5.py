"""Derive a 4:5 (1080x1350) feed version from a letterboxed 9:16 ad composition.

Usage: make_4x5.py SRC_PROJECT OUT_PROJECT PICTURE_HEIGHT

Everything that is timed (cuts, captions, zooms, b-roll, sound, music) is copied verbatim from
SRC_PROJECT/index.html; only layout changes:
  - the native picture box stays full width in the middle; the top/bottom bars shrink to
    (1350 - PICTURE_HEIGHT) / 2 each,
  - headlines are re-flowed to one or two lines and sized to fit the top bar with margins
    (above the small tag pills, when the ad has them),
  - captions are sized to sit on one line inside the bottom bar with margins,
  - the end CTA moves onto the lower edge of the picture (the bottom bar holds the captions).
Media folders are symlinked, so the 4:5 project renders from the same files.
"""
import os, re, shutil, sys

SRC, OUT, PIC = sys.argv[1], sys.argv[2], int(sys.argv[3])
W, H = 1080, 1350
BAR = (H - PIC) // 2
MARGIN_X, MARGIN_Y = 44, 14          # safe margins inside each bar
TEXT_W = W - 2 * MARGIN_X

os.makedirs(OUT, exist_ok=True)
for d in ("assets", "vendor"):
    link = os.path.join(OUT, d)
    if not os.path.lexists(link): os.symlink(os.path.relpath(os.path.join(SRC, d), OUT), link)
for f in ("hyperframes.json", "package.json", "meta.json"):
    shutil.copy(os.path.join(SRC, f), os.path.join(OUT, f))
doc = open(os.path.join(SRC, "index.html")).read()

def text_units(fragment):
    """Approximate rendered width of a fragment in em (Montserrat 900 caps; emoji ~1.25em)."""
    t = re.sub(r"<[^>]+>", "", fragment)
    em = 0.0
    for ch in t:
        if ch == " ": em += 0.3
        elif ord(ch) > 0x2000: em += 0.62 if ch in "️‍" else 1.25
        elif ch in ".,:;!'": em += 0.32
        elif ch in "MW": em += 1.0
        elif ch in "I1": em += 0.42
        else: em += 0.8
    return em

# ---------- headlines: 1-2 lines, sized to the top bar (leaving a row for tag pills if the ad has them) ----------
HAS_TAGS = 'class="clip tag"' in doc
TAG_H = 62 if HAS_TAGS else 0
HEAD_H = BAR - 2 * MARGIN_Y - (TAG_H + 8 if HAS_TAGS else 0)
def fit(lines):
    return int(min(HEAD_H / (len(lines) * 1.06), TEXT_W / max(text_units(l) for l in lines) / 1.08))   # 1.08: pulse headroom
def reflow(inner):
    parts = inner.split('<span class="ln')[1:]
    lines = []
    for p in parts:
        cls, _, body = p.partition('">')
        body = body[: body.rfind("</span>")] if body.rstrip().endswith("</span>") else body
        cls = cls.strip()
        lines.append(f'<span class="{cls}">{body}</span>' if cls else body)
    while len(lines) > 2:   # merge the adjacent pair that keeps the widest line narrowest
        best = min(range(len(lines) - 1), key=lambda i: text_units(lines[i]) + text_units(lines[i + 1]))
        lines[best:best + 2] = [lines[best] + " " + lines[best + 1]]
    if len(lines) == 2 and fit([lines[0] + " " + lines[1]]) > fit(lines): lines = [lines[0] + " " + lines[1]]   # one line reads bigger
    return "".join(f'<span class="ln">{l}</span>' for l in lines), fit(lines)

def fix_head(m):
    attrs, inner = m.group(1), m.group(2)
    new, size = reflow(inner)
    attrs = re.sub(r'\sstyle="[^"]*"', "", attrs)
    return f'<div class="head-in{attrs} style="font-size:{size}px">{new}</div>'   # attrs already ends with a quote
doc, n_heads = re.subn(r'<div class="head-in([^>]*)>(.*?)</div>(?=</div>)', fix_head, doc)

# ---------- captions: one line inside the bottom bar ----------
CAP_MAX = min(96, int((BAR - 2 * MARGIN_Y) / 1.32))   # 9:16 size, or less if the bar is short (line + outline + shadow)
GAP_EM = 0.6   # word gap scales with the type so a popped word never crowds its neighbour
def fix_cap(m):
    gid, inner = m.group(1), m.group(2)
    words = re.findall(r'<span class="w[^"]*"[^>]*>(.*?)</span>', inner)
    em = sum(text_units(w) for w in words)
    size = int(min(CAP_MAX, TEXT_W / 1.1 / (em + GAP_EM * (len(words) - 1))))   # 1.1: active-word pop
    return f'<div class="cg" id="cg-{gid}" style="font-size:{size}px">{inner}</div>'
doc, n_caps = re.subn(r'<div class="cg" id="cg-(\d+)"(?: style="[^"]*")?>(.*?)</div>', fix_cap, doc)

# ---------- canvas + layout overrides ----------
doc = doc.replace('content="width=1080, height=1920"', f'content="width={W}, height={H}"')
doc = doc.replace('data-height="1920"', f'data-height="{H}"')
css = f"""
      /* ---- 4:5 feed layout (derived by tools/make_4x5.py) ---- */
      #box, .broll, .money {{ top: {BAR}px; }}
      .head {{ left: {MARGIN_X}px; right: {MARGIN_X}px; top: {MARGIN_Y}px; height: {HEAD_H}px; }}
      .head-in {{ line-height: 1.04; }}
      .tag {{ top: {BAR - MARGIN_Y - TAG_H}px; height: {TAG_H}px; }}
      .pill {{ font-size: 36px; padding: 10px 26px 8px; }}
      #captions {{ top: {BAR + PIC}px; height: {BAR}px; }}
      .cg {{ flex-wrap: nowrap; gap: 0 {GAP_EM}em; padding: 0 {MARGIN_X}px; }}
      .w {{ font-size: inherit; -webkit-text-stroke-width: 0.15em; text-shadow: 0 0.07em 0 #000; }}
      #cta {{ top: {BAR + PIC - 186}px; bottom: auto; height: 160px; }}
      #cta-box {{ max-width: 900px; }}
    </style>"""
doc = doc.replace("    </style>", css, 1)
open(os.path.join(OUT, "index.html"), "w").write(doc)
print(f"{OUT}: bars {BAR}px, {n_heads} headlines, {n_caps} caption groups, caption max {CAP_MAX}px")
