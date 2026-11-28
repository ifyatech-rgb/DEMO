"""Speaker pane (no crop, no scale, no retime): source y 211-1139 -> 1080x928, 1179 frames.
1. pane_clean: frames inside the old baked-graphic windows (layout.json) are replaced with a ping-pong of the clean
   frames just before the window. These only ever show inside the small speaker bubble (the window itself is covered
   by a new full-pane scene), so the bubble never shows old graphics.
2. matte (mediapipe selfie multiclass, guided-filter edge, ~2 px feather, temporal smoothing).
3. look: contrast +8 %, saturation +6 %, gentle S-curve; background only: light blur + 20 % navy tint; subtle vignette.
Writes work/pane_look.mp4 and logs/matte_edge.json."""
import json, subprocess
import cv2, mediapipe as mp, numpy as np
from mediapipe.tasks import python as mpt
from mediapipe.tasks.python import vision

L = json.load(open("logs/layout.json")); P = L["speaker_pane"]; Y0, H = P["y"], P["h"]; W = 1080
BAD = [(a - 2 / 30, b + 2 / 30) for a, b in L["fullscreen_graphics"] + L["money_emoji_overlay"]]
cap = cv2.VideoCapture("../ad_1_for_feed.mp4"); N = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
frames = []
while True:
    ok, f = cap.read()
    if not ok: break
    frames.append(f[Y0:Y0 + H].copy())
N = len(frames)
bad = np.zeros(N, bool)
for a, b in BAD: bad[max(0, int(a * 30)):min(N, int(np.ceil(b * 30)) + 1)] = True
src = list(range(N)); i = 0
while i < N:
    if not bad[i]: i += 1; continue
    j = i
    while j < N and bad[j]: j += 1
    k = i - 1; pool = []
    while k >= 0 and not bad[k] and len(pool) < 45: pool.insert(0, k); k -= 1
    pp = pool + pool[-2:0:-1] if len(pool) > 2 else pool
    for n, t in enumerate(range(i, j)): src[t] = pp[n % len(pp)]
    i = j
filled = int(bad.sum())

seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=mpt.BaseOptions(model_asset_path="../edit/work/selfie_multiclass.tflite", delegate=mpt.BaseOptions.Delegate.CPU),
    output_confidence_masks=True, running_mode=vision.RunningMode.IMAGE))
def guided(I, p, r=8, eps=1e-3):
    m = lambda x: cv2.boxFilter(x, -1, (r, r))
    mI, mp_, mIp, mII = m(I), m(p), m(I * p), m(I * I)
    a = (mIp - mI * mp_) / (mII - mI * mI + eps); b = mp_ - a * mI
    return m(a) * I + m(b)
NAVY = np.array([0x2D, 0x1B, 0x0F], np.float32) / 255
x = np.linspace(0, 1, 256); LUT = np.clip(x + 0.03 * np.sin(2 * np.pi * x) * -1, 0, 1); LUT = ((LUT - 0.5) * 1.08 + 0.5).clip(0, 1)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = (1 - 0.14 * np.clip(np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / 1.414, 0, 1) ** 2)[..., None]
out = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
                        "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-g", "30", "-pix_fmt", "yuv420p", "work/pane_look.mp4"], stdin=subprocess.PIPE)
prev, edge = None, []
cuts = {t for t in range(1, N) if src[t] != src[t - 1] + 1}
for t in range(N):
    f = frames[src[t]]
    r = seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(f, cv2.COLOR_BGR2RGB)))
    a = 1 - cv2.resize(r.confidence_masks[0].numpy_view().astype(np.float32), (W, H))
    a = np.clip(guided(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255, a), 0, 1)
    a = cv2.GaussianBlur(a, (0, 0), 1.0)
    if prev is not None and t not in cuts:
        band = (a > 0.1) & (a < 0.9)
        if band.any() and not bad[t]: edge.append(float(np.abs(a - prev)[band].mean()))
        a = 0.6 * a + 0.4 * prev
    prev = a
    img = f.astype(np.float32) / 255
    bg = cv2.GaussianBlur(img, (0, 0), 5) * 0.8 + NAVY * 0.2
    A = a[..., None]
    o = img * A + bg * (1 - A)
    o = LUT[(o * 255).astype(np.uint8)].astype(np.float32)
    g = o.mean(2, keepdims=True); o = np.clip(g + (o - g) * 1.06, 0, 1) * VIG
    out.stdin.write((o * 255).astype(np.uint8).tobytes())
out.stdin.close(); out.wait()
e = np.array(edge)
json.dump({"frames": N, "filled_frames": filled, "edge_median": float(np.median(e)), "edge_p95": float(np.percentile(e, 95))}, open("logs/matte_edge.json", "w"))
print(open("logs/matte_edge.json").read())
