"""Map every frame of the client's re-edit (assets/edit.mp4) back to the v2 render timeline -> kept segments."""
import json, subprocess, numpy as np
def frames(f):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-vf", "scale=36:64,format=gray", "-r", "30", "-f", "rawvideo", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, 64 * 36).astype(np.float32)
A = frames("assets/edit.mp4"); B = frames("../roughcut/renders/916-v2.mp4")
print(len(A), len(B))
best = []
for i, a in enumerate(A):
    lo = i; hi = min(len(B), i + 400)
    d = np.abs(B[lo:hi] - a).mean(1)
    j = int(np.argmin(d)); best.append((lo + j, float(d[j])))
off = [b - i for i, (b, _) in enumerate(best)]
# segments of constant offset
segs, s0 = [], 0
for i in range(1, len(off) + 1):
    if i == len(off) or abs(off[i] - off[s0]) > 1:
        segs.append(dict(edit_start=s0 / 30, edit_end=i / 30, v2_start=(s0 + off[s0]) / 30, n=i - s0,
                         err=round(float(np.mean([best[k][1] for k in range(s0, i)])), 2)))
        s0 = i
for s in segs: print({k: round(v, 3) if isinstance(v, float) else v for k, v in s.items()})
json.dump(segs, open("segments_raw.json", "w"), indent=1)
