"""Exports + step 9 QA. Writes out/*.mp4, logs/contact_45_*.png, logs/contact_916_*.png, logs/qa.json."""
import json, re, subprocess, difflib
import numpy as np
run = lambda *a: subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)
SRC_DUR = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "../ad_1_for_feed.mp4"], capture_output=True, text=True).stdout)
EXP = {"ad1_feed_4x5_1080x1350.mp4": "work/overlay_45.mp4", "ad1_reels_9x16_1080x1920.mp4": "work/overlay_916.mp4"}
for out, src in EXP.items():
    run("-i", src, "-i", "work/final_mix.wav", "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-profile:v", "high", "-crf", "17", "-preset", "slow", "-r", "30",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", "-shortest", f"out/{out}")
qa = {"source_duration": SRC_DUR}
for out in EXP:
    p = f"out/{out}"
    pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,codec_name,profile,width,height,r_frame_rate,pix_fmt:format=duration", "-of", "json", p],
                                   capture_output=True, text=True).stdout)
    r = subprocess.run(["ffmpeg", "-i", p, "-af", "ebur128=peak=true:framelog=quiet", "-f", "null", "-"], capture_output=True, text=True).stderr
    I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1]); TP = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r)[-1])
    vs = [s for s in pr["streams"] if s["codec_type"] == "video"][0]; d = float(pr["format"]["duration"])
    qa[out] = {"duration": d, "dur_ok": abs(d - SRC_DUR) <= 0.1, "size": [vs["width"], vs["height"]], "fps": vs["r_frame_rate"], "profile": vs["profile"],
               "lufs": I, "true_peak": TP, "loud_ok": abs(I + 14) <= 0.5 and TP < -1.0}
    tag = "45" if "4x5" in out else "916"
    for half, (a, b) in enumerate(((0, 20), (20, 39.3))):
        w = 216 if tag == "45" else 180
        run("-ss", str(a), "-t", str(b - a), "-i", p, "-vf", f"fps=2,scale={w}:-1,drawtext=text='%{{pts\\:hms}}':x=4:y=4:fontsize=16:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=10x4",
            "-frames:v", "1", f"logs/contact_{tag}_{half + 1}.png")
json.dump(qa, open("logs/qa.json", "w"), indent=1)
print(json.dumps({k: v for k, v in qa.items()}, indent=1))
