"""Composite a rendered UI video into a green-screen device clip (laptop / phone).

Usage: screen_comp.py GREEN.mp4 UI.mp4 OUT.mp4 [--start S] [--dur D] [--flip]

Per frame: key the green screen (HSV), fit its 4 corners (largest contour -> polygon), smooth the
corners over time, perspective-warp the UI frame onto them, and composite through a feathered key
mask so fingers, bezels and reflections over the screen stay real. Green spill is neutralised.
"""
import argparse, subprocess
import cv2, numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("green"); ap.add_argument("ui"); ap.add_argument("out")
ap.add_argument("--start", type=float, default=0); ap.add_argument("--dur", type=float, default=None)
ap.add_argument("--flip", action="store_true", help="mirror the footage horizontally first")
a = ap.parse_args()

def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height,r_frame_rate",
                          "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip().split(",")
    n, d = out[2].split("/")
    return int(out[0]), int(out[1]), float(n) / float(d)

W, H, FPS = probe(a.green)
uw, uh, _ = probe(a.ui)
dur = a.dur or 1e9
src = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(a.start), "-i", a.green, "-t", str(dur), "-f", "rawvideo",
                        "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
# UI plays at the footage frame rate from its own start.
ui = subprocess.Popen(["ffmpeg", "-v", "error", "-i", a.ui, "-vf", f"fps={FPS}", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                      stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS),
                        "-i", "-", "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-pix_fmt", "yuv420p", a.out],
                       stdin=subprocess.PIPE)

def order(pts):
    pts = pts.reshape(4, 2).astype(np.float32)
    s, d = pts.sum(1), np.diff(pts, axis=1).ravel()
    return np.array([pts[np.argmin(s)], pts[np.argmin(d)], pts[np.argmax(s)], pts[np.argmax(d)]], np.float32)  # tl tr br bl

def corners(mask):
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts: return None
    c = max(cnts, key=cv2.contourArea)
    if cv2.contourArea(c) < 0.01 * W * H: return None
    hull = cv2.convexHull(c)
    for eps in (0.01, 0.02, 0.03, 0.05, 0.08):
        poly = cv2.approxPolyDP(hull, eps * cv2.arcLength(hull, True), True)
        if len(poly) == 4: return order(poly)
    return order(cv2.boxPoints(cv2.minAreaRect(hull)))

prev, last_ui, n = None, None, 0
uisrc = np.float32([[0, 0], [uw, 0], [uw, uh], [0, uh]])
while True:
    buf = src.stdout.read(W * H * 3)
    if len(buf) < W * H * 3: break
    frame = np.frombuffer(buf, np.uint8).reshape(H, W, 3).copy()
    if a.flip: frame = frame[:, ::-1].copy()
    ub = ui.stdout.read(uw * uh * 3)
    if len(ub) == uw * uh * 3: last_ui = np.frombuffer(ub, np.uint8).reshape(uh, uw, 3)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    key = cv2.inRange(hsv, (35, 50, 45), (95, 255, 255))
    key = cv2.morphologyEx(key, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    q = corners(key)
    if q is not None:
        prev = q if prev is None else 0.55 * prev + 0.45 * q   # temporal smoothing against jitter
    if prev is not None and last_ui is not None:
        # Grow the quad a few px so the UI tucks under the bezel edge.
        cx = prev.mean(0); quad = cx + (prev - cx) * 1.012
        M = cv2.getPerspectiveTransform(uisrc, quad.astype(np.float32))
        warped = cv2.warpPerspective(last_ui, M, (W, H), flags=cv2.INTER_LANCZOS4)
        inside = np.zeros((H, W), np.uint8); cv2.fillConvexPoly(inside, quad.astype(np.int32), 255)
        m = cv2.GaussianBlur(cv2.dilate(key, np.ones((3, 3), np.uint8)), (5, 5), 0)
        m = (m.astype(np.float32) / 255) * (inside.astype(np.float32) / 255)
        # Despill: pull green down to the max of red/blue near the key.
        f = frame.astype(np.float32)
        spill = cv2.dilate(key, np.ones((9, 9), np.uint8)) > 0
        f[..., 1] = np.where(spill, np.minimum(f[..., 1], np.maximum(f[..., 0], f[..., 2]) * 1.05), f[..., 1])
        frame = (f * (1 - m[..., None]) + warped.astype(np.float32) * m[..., None]).clip(0, 255).astype(np.uint8)
    enc.stdin.write(frame.tobytes()); n += 1
enc.stdin.close(); enc.wait()
print(f"{n} frames -> {a.out}")
