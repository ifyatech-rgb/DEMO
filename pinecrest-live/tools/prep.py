"""Conform media for the 9:16 ad: warm grade, vertical framing, 30 fps.

Usage: prep.py JOBS.json
Job: {"src", "out", "kind": "video"|"photo", "ss", "dur", "x": 0..1 horizontal focus, "vf": extra filters}
  video -> 1080x1920 H.264 (fill-cropped around x), silent
  photo -> 1350x2400 JPEG (fill-cropped around x; headroom for Ken Burns / snap zooms)
Outputs are skipped when newer than their source.
"""
import json, os, subprocess, sys

GRADE = ("colorbalance=rs=0.06:gs=0.01:bs=-0.07:rm=0.045:gm=0.005:bm=-0.05:rh=0.03:bh=-0.04,"
         "curves=all='0/0.035 0.5/0.5 1/0.965',eq=contrast=1.07:saturation=1.0")

def crop(w, h, x):
    # scale to cover WxH, then crop W wide around horizontal focus x (0 = left, 1 = right)
    return (f"scale={w}:{h}:force_original_aspect_ratio=increase:flags=lanczos,"
            f"crop={w}:{h}:(iw-{w})*{x}:(ih-{h})/2")

for j in json.load(open(sys.argv[1])):
    src, out = j["src"], j["out"]
    if os.path.exists(out) and os.path.getmtime(out) > os.path.getmtime(src): continue
    os.makedirs(os.path.dirname(out), exist_ok=True)
    extra = (j["vf"] + ",") if j.get("vf") else ""
    x = j.get("x", 0.5)
    if j["kind"] == "photo":
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf", f"{extra}{crop(1350, 2400, x)},{GRADE}", "-q:v", "2", out], check=True)
    else:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(j.get("ss", 0)), "-i", src, "-t", str(j["dur"]), "-an", "-vf",
                        f"{extra}{crop(1080, 1920, x)},fps=30,{GRADE}", "-c:v", "libx264", "-crf", "15", "-preset", "medium",
                        "-pix_fmt", "yuv420p", out], check=True)
    print("ok", out, flush=True)
