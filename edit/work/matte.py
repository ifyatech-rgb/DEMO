"""Speaker matte with mediapipe's selfie multiclass segmenter (person = 1 - background confidence), upscaled,
edge-refined against the picture (guided-filter style), feathered 2 px and smoothed over time so the edge does not
flicker. Writes work/matte.mp4 (8-bit gray, 1080x928) and work/matte_stats.json."""
import json, subprocess
import cv2, mediapipe as mp, numpy as np
from mediapipe.tasks import python as mpt
from mediapipe.tasks.python import vision

seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=mpt.BaseOptions(model_asset_path="work/selfie_multiclass.tflite", delegate=mpt.BaseOptions.Delegate.CPU),
    output_confidence_masks=True, running_mode=vision.RunningMode.IMAGE))

def guided(I, p, r=8, eps=1e-3):
    """Grey guided filter: snaps the soft mask edge to the image edges (hair, shoulders)."""
    mean = lambda x: cv2.boxFilter(x, -1, (r, r))
    mI, mp_, mIp, mII = mean(I), mean(p), mean(I * p), mean(I * I)
    a = (mIp - mI * mp_) / (mII - mI * mI + eps); b = mp_ - a * mI
    return mean(a) * I + mean(b)

cap = cv2.VideoCapture("work/speaker_cut.mp4")
W, H = int(cap.get(3)), int(cap.get(4))
out = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "gray", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
                        "-c:v", "libx264", "-crf", "10", "-preset", "fast", "-pix_fmt", "yuv420p", "work/matte.mp4"], stdin=subprocess.PIPE)
prev, flick = None, []
while True:
    ok, f = cap.read()
    if not ok: break
    r = seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(f, cv2.COLOR_BGR2RGB)))
    a = 1.0 - r.confidence_masks[0].numpy_view().astype(np.float32)
    a = cv2.resize(a, (W, H), interpolation=cv2.INTER_LINEAR)
    g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
    a = np.clip(guided(g, a), 0, 1)
    a = cv2.GaussianBlur(a, (0, 0), 1.0)                       # ~2 px feather
    if prev is not None:
        flick.append(float(np.abs(a - prev).mean()))
        a = 0.6 * a + 0.4 * prev                                # temporal smoothing
    prev = a
    out.stdin.write((a * 255).astype(np.uint8).tobytes())
out.stdin.close(); out.wait()
json.dump({"frames": len(flick) + 1, "mean_frame_change": float(np.mean(flick)), "p99_frame_change": float(np.percentile(flick, 99))},
          open("work/matte_stats.json", "w"))
print(open("work/matte_stats.json").read())
