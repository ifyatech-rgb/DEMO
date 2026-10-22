"""Conform footage and stills to the VSL look before compositing.

Usage: prep_media.py JOBS.json
Each job: {"src": path, "out": path, "ss": seconds, "dur": seconds, "kind": "video"|"photo"|"aroll", "vf": "<extra filters>"}
  video -> 1920x1080 25fps H.264, silent, warm grade (fill-cropped to 16:9)
  photo -> 2560px-wide graded JPEG (headroom for Ken Burns moves)
  aroll -> graded talking-head with its cleaned audio kept
Skips outputs that are newer than their source.
"""
import json, os, subprocess, sys

# One warm grade shared by every source so stock clips and the talking head cut together.
GRADE = ("colorbalance=rs=0.06:gs=0.01:bs=-0.07:rm=0.045:gm=0.005:bm=-0.05:rh=0.03:bh=-0.04,"
         "curves=all='0/0.04 0.5/0.5 1/0.96',eq=contrast=1.05:saturation=0.88")

def run(cmd): subprocess.run(cmd, check=True)

for j in json.load(open(sys.argv[1])):
    src, out = j["src"], j["out"]
    if os.path.exists(out) and os.path.getmtime(out) > os.path.getmtime(src): continue
    os.makedirs(os.path.dirname(out), exist_ok=True)
    extra = (j.get("vf") + ",") if j.get("vf") else ""
    if j["kind"] == "photo":
        run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf", f"{extra}scale=2560:-2:flags=lanczos,{GRADE}", "-q:v", "2", out])
    elif j["kind"] == "aroll":
        run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf", f"{extra}{GRADE}", "-c:v", "libx264", "-crf", "14", "-preset", "medium",
             "-pix_fmt", "yuv420p", "-c:a", "copy", out])
    else:
        ss, dur = str(j.get("ss", 0)), str(j["dur"])
        run(["ffmpeg", "-v", "error", "-y", "-ss", ss, "-i", src, "-t", dur, "-an", "-vf",
             f"{extra}scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,crop=1920:1080,fps=25,{GRADE}",
             "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-pix_fmt", "yuv420p", out])
    print("ok", out, flush=True)
