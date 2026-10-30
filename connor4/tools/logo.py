"""Replace the garbled AI shirt logo on the client's take with the real Pinecrest logo (assets/logo-src.jpg).

Per frame: ECC-track the chest patch against frame 0 (euclidean warp, held through hand occlusions), inpaint the old
print away, then print the real logo through the same warp, shaded by the shirt's local lighting and kept under any
skin (his hand passes in front of it). Writes assets/source_logo.mp4 (video only; timing identical to the source)."""
import os, subprocess
import cv2, numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)

X0, Y0, PW, PH = 330, 900, 130, 120          # reference patch (frame 0) around the chest logo
CX, CY, LH = 394, 959, 88                      # old logo centre and the new logo's height in frame-0 pixels
INK = np.array([228, 230, 232], np.float32)    # off-white print (BGR)

cap = cv2.VideoCapture("assets/source.mp4")
fps = cap.get(cv2.CAP_PROP_FPS); W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
ok, f0 = cap.read(); assert ok
g0 = cv2.GaussianBlur(cv2.cvtColor(f0, cv2.COLOR_BGR2GRAY), (3, 3), 0)
ref = g0[Y0:Y0 + PH, X0:X0 + PW].astype(np.float32)

# old print in reference coords: bright, unsaturated pixels inside the logo footprint
hsv0 = cv2.cvtColor(f0[Y0:Y0 + PH, X0:X0 + PW], cv2.COLOR_BGR2HSV)
old = ((hsv0[..., 2] > 105) & (hsv0[..., 1] < 90)).astype(np.uint8)
foot = np.zeros_like(old); cv2.ellipse(foot, (CX - X0, CY - Y0), (52, 48), 0, 0, 360, 1, -1)
old = cv2.dilate(old * foot, np.ones((5, 5), np.uint8))

# real logo -> alpha in reference coords
lg = cv2.imread("assets/logo-src.jpg", cv2.IMREAD_GRAYSCALE)
ys, xs = np.nonzero(lg > 100); lg = lg[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
s = LH / lg.shape[0]; lg = cv2.resize(lg, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
alpha = np.zeros((PH, PW), np.float32)
ox, oy = CX - X0 - lg.shape[1] // 2, CY - Y0 - lg.shape[0] // 2
alpha[oy:oy + lg.shape[0], ox:ox + lg.shape[1]] = np.clip((lg.astype(np.float32) - 40) / 180, 0, 1)
alpha = cv2.GaussianBlur(alpha, (3, 3), 0.6)

out = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", f"{fps}", "-i", "-",
                        "-c:v", "libx264", "-crf", "15", "-preset", "medium", "-pix_fmt", "yuv420p", "assets/source_logo.mp4"], stdin=subprocess.PIPE)
warp = np.array([[1, 0, X0], [0, 1, Y0]], np.float32)
crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 60, 1e-5)
n, held, scores = 0, 0, []
frame = f0
while True:
    g = cv2.GaussianBlur(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (3, 3), 0).astype(np.float32)
    try:
        cc, w2 = cv2.findTransformECC(ref, g, warp.copy(), cv2.MOTION_EUCLIDEAN, crit, None, 5)
        moved = np.abs(w2[:, 2] - warp[:, 2]).max()
        if cc > 0.55 and moved < 25: warp = w2
        else: held += 1
    except cv2.error:
        cc = 0.0; held += 1
    scores.append(cc)
    # work in a crop around the logo
    bx0, by0 = int(warp[0, 2]) - 20, int(warp[1, 2]) - 20
    bx0, by0 = max(0, bx0), max(0, by0); bx1, by1 = min(W, bx0 + PW + 40), min(H, by0 + PH + 40)
    A = warp.copy(); A[0, 2] -= bx0; A[1, 2] -= by0
    cw, ch = bx1 - bx0, by1 - by0
    crop = frame[by0:by1, bx0:bx1].copy()
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    h = hsv[..., 0]; skin = (((h < 25) | (h > 160)) & (hsv[..., 1] > 40) & (hsv[..., 2] > 60)).astype(np.uint8)
    skin = cv2.dilate(skin, np.ones((3, 3), np.uint8))
    m_old = cv2.warpAffine(old, A, (cw, ch), flags=cv2.INTER_NEAREST)
    m_old = cv2.dilate(m_old, np.ones((3, 3), np.uint8)) & (1 - skin)
    clean = cv2.inpaint(crop, m_old * 255, 5, cv2.INPAINT_TELEA)
    # lighting of the shirt under the print, relative to the shirt's typical value
    lum = cv2.GaussianBlur(cv2.cvtColor(clean, cv2.COLOR_BGR2GRAY).astype(np.float32), (0, 0), 6)
    shade = np.clip(lum / 42.0, 0.72, 1.25)[..., None]
    a = cv2.warpAffine(alpha, A, (cw, ch), flags=cv2.INTER_LINEAR) * (1 - skin) * 0.94
    ink = np.clip(INK * (0.82 + 0.18 * shade), 0, 255)
    comp = clean.astype(np.float32) * (1 - a[..., None]) + ink * a[..., None]
    comp += np.random.default_rng(n).normal(0, 2.0, comp.shape).astype(np.float32) * a[..., None]   # match the footage grain
    frame = frame.copy(); frame[by0:by1, bx0:bx1] = np.clip(comp, 0, 255).astype(np.uint8)
    out.stdin.write(frame.tobytes()); n += 1
    ok, frame = cap.read()
    if not ok: break
out.stdin.close(); out.wait()
sc = np.array(scores)
print(f"{n} frames · ECC median {np.median(sc):.3f} · min {sc.min():.3f} · held {held}")
