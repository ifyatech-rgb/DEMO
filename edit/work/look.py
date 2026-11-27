"""Picture pass: fake-relight the speaker and frame him for both formats.

Look (on the 1080x928 cut, with the mediapipe matte):
  background: blur ~25 px, -35 % brightness, -25 % saturation, navy #0F1B2D overlay at 25 %  (posters unreadable)
  speaker:    +0.08 stop exposure, lifted shadows, slightly warmer skin, soft key light from camera-left
  overall:    contrast +10 %, saturation +8 %, gentle S-curve, unsharp 5x5 0.6, 20 % vignette (per output)
Framing: base scale 1.56 x the cut (fills 4:5), punch-ins / pushes / shake from work/plan.json, face followed
horizontally (smoothed within each shot), eyes held at y 450 (4:5) / 720 (9:16). 9:16 fills the top with a deep
blur of the same frame and fades the bottom into navy. Frames under old graphics that no card covers are held
on the nearest clean frame.
Writes work/plate_45.mp4 (1080x1350) and work/plate_916.mp4 (1080x1920)."""
import json, math, subprocess
import cv2, numpy as np

FPS = 30
plan = json.load(open("work/plan.json")); tl = json.load(open("work/timeline.json"))
cut = cv2.VideoCapture("work/speaker_cut.mp4"); mat = cv2.VideoCapture("work/matte.mp4")
N = int(cut.get(cv2.CAP_PROP_FRAME_COUNT)); CW, CH = int(cut.get(3)), int(cut.get(4))
NAVY = np.array([0x2D, 0x1B, 0x0F], np.float32) / 255           # BGR
S0 = 1.56

# ---------- pass 1: face track (Haar on a half-size frame) ----------
casc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
fx, fy, fw = np.full(N, np.nan), np.full(N, np.nan), np.full(N, np.nan)
for i in range(N):
    ok, f = cut.read()
    g = cv2.cvtColor(cv2.resize(f, (CW // 2, CH // 2)), cv2.COLOR_BGR2GRAY)
    d = casc.detectMultiScale(g, 1.1, 6, minSize=(90, 90))
    if len(d):
        x, y, w, h = max(d, key=lambda r: r[2] * r[3])
        fx[i], fy[i], fw[i] = (x + w / 2) * 2, (y + 0.42 * h) * 2, w * 2      # face centre x, eye line y
shot_starts = sorted({round(s["vin"] * FPS) for s in tl["segs"]})
def smooth_track(v):
    out = v.copy()
    bounds = shot_starts + [N]
    for a, b in zip(bounds, bounds[1:]):
        seg = v[a:b]; ok = ~np.isnan(seg)
        fill = np.nanmedian(v) if not ok.any() else np.nanmedian(seg[ok])
        seg = np.where(ok, seg, fill)
        k = min(len(seg), 21) | 1
        pad = np.pad(seg, (k // 2, k // 2), mode="edge")
        sm = np.convolve(pad, np.ones(k) / k, mode="valid")
        out[a:b] = np.clip(sm, np.median(sm) - 60, np.median(sm) + 60)   # a stable, slow follow
    return out
FX, FY, FW = smooth_track(fx), smooth_track(fy), smooth_track(fw)
FY = np.full(N, float(np.nanmedian(fy)))                            # vertical framing fixed (no bobbing)
print(f"face found in {np.mean(~np.isnan(fx)) * 100:.0f}% of frames; median face x {np.nanmedian(fx):.0f}, eye y {np.nanmedian(fy):.0f}")

# ---------- camera curve ----------
def rel_at(t):
    v = 1.0; cur_t = 0.0; start_v = 1.0; mode = "set"; dur = 0.0; target = 1.0
    for kt, kv, km in plan["cam"]:
        if kt > t + 1e-9: break
        # value at kt from the previous segment
        if mode != "set" and dur > 0:
            u = min(1.0, (kt - cur_t) / dur); start_v = start_v + (target - start_v) * curve(mode, u)
        else:
            start_v = target
        cur_t, target = kt, kv
        if km == "set": mode, dur, start_v = "set", 0.0, kv
        else: mode, dur = km
    if mode == "set" or dur <= 0: return target
    return start_v + (target - start_v) * curve(mode, min(1.0, (t - cur_t) / dur))
def curve(mode, u):
    return {"push": u, "punch": 1 - (1 - u) ** 3, "ease": 0.5 - 0.5 * math.cos(math.pi * u)}[mode]
shake = {}
for t, nfr, px in plan["shake"]:
    for k in range(nfr): shake[round(t * FPS) + k] = (px if k % 2 == 0 else -px, -px // 2 if k % 2 == 0 else px // 2)

# hold-frames for the few frames of old graphics that no card covers
hold = {}
for a, b in plan["hold"]:
    for i in range(math.floor(a * FPS), math.ceil(b * FPS) + 1): hold[i] = math.ceil(b * FPS) + 1
need = sorted(set(hold.values()))

# ---------- look ----------
def to_f(x): return x.astype(np.float32) / 255
GRADE_LUT = np.clip(np.linspace(0, 1, 256) + 0.035 * np.sin(np.linspace(0, 2 * np.pi, 256)) * -1, 0, 1)   # gentle S
GRADE_LUT = ((GRADE_LUT - 0.5) * 1.10 + 0.5).clip(0, 1)                                             # contrast +10 %
def sat(img, k):
    g = img.mean(2, keepdims=True); return np.clip(g + (img - g) * k, 0, 1)
def look(f, a, fxi, fyi, fwi):
    img = to_f(f)
    bg = cv2.GaussianBlur(img, (0, 0), 12.5)
    bg = sat(bg * 0.65, 0.75); bg = bg * 0.75 + NAVY * 0.25
    fg = np.clip(img * 2 ** 0.08, 0, 1)
    fg = fg + 0.06 * (1 - fg) * (1 - fg) * fg * 4                     # lift shadows / low mids
    fg = fg * np.array([0.975, 1.0, 1.03], np.float32)                 # slightly warmer (B down, R up)
    yy, xx = np.mgrid[0:CH, 0:CW].astype(np.float32)
    kx, ky, r = fxi - 0.35 * fwi, fyi, 1.1 * fwi
    key = np.exp(-(((xx - kx) ** 2 + (yy - ky) ** 2) / (2 * r * r)))[..., None]
    soft = np.where(fg < 0.5, 2 * fg * (fg + 0.5 * (1 - fg)) , fg + (1 - fg) * 0.35 * fg)     # soft-light lift
    fg = fg * (1 - 0.18 * key) + np.clip(soft, 0, 1) * 0.18 * key
    A = a[..., None]
    out = np.clip(fg * A + bg * (1 - A), 0, 1)
    out = GRADE_LUT[(out * 255).astype(np.uint8)].astype(np.float32)
    out = sat(out, 1.08)
    bl = cv2.blur(out, (5, 5)); out = np.clip(out + 0.6 * (out - bl), 0, 1)
    return out

def vignette(h, w, amt=0.2):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2) / math.sqrt(2)
    return (1 - amt * np.clip(d, 0, 1) ** 2)[..., None]
V45, V916 = vignette(1350, 1080), vignette(1920, 1080)

def frame_45(img, i, t):
    rel = rel_at(t); S = S0 * rel
    ox, oy = 540 - FX[i] * S, 450 - FY[i] * S
    ox = min(0, max(1080 - CW * S, ox)); oy = min(0, max(1350 - CH * S, oy))
    sx, sy = shake.get(i, (0, 0))
    M = np.float32([[S, 0, ox + sx], [0, S, oy + sy]])
    return cv2.warpAffine(img, M, (1080, 1350), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT) * V45

YY916 = np.mgrid[0:1920, 0:1080][0].astype(np.float32)
def frame_916(img, i, t):
    rel = rel_at(t); S = S0 * rel
    ox, oy = 540 - FX[i] * S, 720 - FY[i] * S
    ox = min(0, max(1080 - CW * S, ox))
    sx, sy = shake.get(i, (0, 0))
    plate = cv2.warpAffine(img, np.float32([[S, 0, ox + sx], [0, S, oy + sy]]), (1080, 1920), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT)
    top, bot = oy + sy, oy + sy + CH * S
    small = cv2.resize(img, (CW // 4, CH // 4))
    Sb = 1920 / (CH // 4) * 1.15
    back = cv2.warpAffine(small, np.float32([[Sb, 0, 540 - CW // 8 * Sb], [0, Sb, 960 - CH // 8 * Sb]]), (1080, 1920), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    back = cv2.GaussianBlur(back, (0, 0), 25) * 0.55
    a_top = np.clip((YY916 - top) / 140, 0, 1)                          # feather the top edge into the blur fill
    a_bot = np.clip((bot - 10 - YY916) / 60, 0, 1)
    A = (a_top * a_bot)[..., None]
    out = plate * A + back * (1 - A)
    navy = np.clip((YY916 - 1420) / 220, 0, 1)[..., None]                # bottom fades into navy (no text below 1536)
    out = out * (1 - navy) + NAVY * navy
    return out * V916

def writer(path, w, h):
    return subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{w}x{h}", "-r", str(FPS), "-i", "-",
                             "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
o45, o916 = writer("work/plate_45.mp4", 1080, 1350), writer("work/plate_916.mp4", 1080, 1920)
cut.set(cv2.CAP_PROP_POS_FRAMES, 0)
held = {}
for j in need:   # grab the clean frames used for holds
    cut.set(cv2.CAP_PROP_POS_FRAMES, j); mat.set(cv2.CAP_PROP_POS_FRAMES, j)
    held[j] = (cut.read()[1], mat.read()[1])
cut.set(cv2.CAP_PROP_POS_FRAMES, 0); mat.set(cv2.CAP_PROP_POS_FRAMES, 0)
for i in range(N):
    f = cut.read()[1]; m = mat.read()[1]
    if i in hold: f, m = held[hold[i]]
    a = m[..., 0].astype(np.float32) / 255
    img = look(f, a, FX[i], FY[i], FW[i])
    t = i / FPS
    o45.stdin.write((np.clip(frame_45(img, i, t), 0, 1) * 255).astype(np.uint8).tobytes())
    o916.stdin.write((np.clip(frame_916(img, i, t), 0, 1) * 255).astype(np.uint8).tobytes())
for o in (o45, o916): o.stdin.close(); o.wait()
print("plates written:", N, "frames; held frames:", sorted(hold))
