"""Reference-style "sketch reveal" on the first frames: Connor appears as a white line drawing over the empty field,
fills into a glowing white ghost, then resolves into the real picture (~0.28 s). Everything after is untouched.

In:  assets/source_logo.mp4 (take with the real shirt logo), assets/intro_matte.webm (his cut-out, first 0.8 s)
Out: assets/source_final.mp4 (video only, same timing)"""
import os, subprocess
import cv2, numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)

# frame k -> (line opacity, ghost amount, colour amount)
STAGES = [(0.35, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.8, 0.6, 0.0), (0.5, 1.0, 0.0), (0.3, 0.7, 0.45), (0.1, 0.3, 0.85)]

def alpha_frames(path, n):
    r = subprocess.run(["ffmpeg", "-v", "error", "-c:v", "libvpx-vp9", "-i", path, "-frames:v", str(n), "-vf", "alphaextract,format=gray",
                        "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(r, np.uint8).reshape(n, 1920, 1080).astype(np.float32) / 255

def clean_plate(img, mask):
    """Fill his silhouette with scenery sampled from the same row on either side (sky, trees, fence and grass run in
    horizontal bands), so the field reads as continuous texture rather than a smear."""
    rng = np.random.default_rng(3)
    out = img.copy(); m = cv2.dilate(mask, np.ones((31, 31), np.uint8)) > 0
    for y in range(img.shape[0]):
        xs = np.nonzero(m[y])[0]
        if not len(xs): continue
        free = np.nonzero(~m[y])[0]
        if not len(free): continue
        for x in xs:   # nearest free pixels within ~250 px, picked at random
            near = free[np.abs(free - x) < 250]
            if not len(near): near = free
            out[y, x] = img[y, rng.choice(near)]
    out = cv2.medianBlur(out, 3)
    soft = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 6)[..., None]
    return (img * (1 - soft) + out * soft).astype(np.uint8)

cap = cv2.VideoCapture("assets/source_logo.mp4")
fps = cap.get(cv2.CAP_PROP_FPS); W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
A = alpha_frames("assets/intro_matte.webm", len(STAGES))
out = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", f"{fps}", "-i", "-",
                        "-c:v", "libx264", "-crf", "15", "-preset", "medium", "-pix_fmt", "yuv420p", "assets/source_final.mp4"], stdin=subprocess.PIPE)
ok, f0 = cap.read()
plate = clean_plate(f0, (A[0] > 0.3).astype(np.uint8)).astype(np.float32)
n, frame = 0, f0
while ok:
    if n < len(STAGES):
        lo, gh, co = STAGES[n]
        a = A[n][..., None]
        g = cv2.GaussianBlur(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (0, 0), 1.2)
        edges = cv2.Canny(g, 30, 80).astype(np.float32) / 255
        sil = cv2.Canny((A[n] * 255).astype(np.uint8), 60, 160).astype(np.float32) / 255     # strong outer contour
        lines = np.clip(cv2.dilate(np.maximum(edges * (A[n] > 0.5), sil), np.ones((2, 2), np.uint8)), 0, 1)
        glow = cv2.GaussianBlur(lines, (0, 0), 3) * 0.6
        ghost = (255 * 0.5 + cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(np.float32)[..., None] * 0.5)
        aura = cv2.GaussianBlur(A[n], (0, 0), 14)[..., None] * 0.18 * gh                         # soft white glow around the ghost
        img = plate.copy()
        img = img * (1 - a * gh * 0.85) + ghost * a * gh * 0.85
        img = img + 255 * aura
        img = img * (1 - a * co) + frame.astype(np.float32) * a * co
        img = img * (1 - co * (1 - a)) + frame.astype(np.float32) * co * (1 - a)                # background settles back to the live frame
        L = np.clip(lines + glow, 0, 1)[..., None] * lo
        img = img * (1 - L) + 245 * L
        frame = np.clip(img, 0, 255).astype(np.uint8)
    out.stdin.write(frame.tobytes()); n += 1
    ok, frame = cap.read()
out.stdin.close(); out.wait()
print(n, "frames written; sketch reveal on frames 0-%d" % (len(STAGES) - 1))
