"""Assemble work/speaker_cut.mp4 from the cut list: the clean picture area of the source only (y 211-1139, i.e. no
old captions or header bars), frame-exact, 1080x928 @ 30 fps."""
import json, os, subprocess
tl = json.load(open("work/timeline.json")); FPS = tl["fps"]
os.makedirs("work/pieces", exist_ok=True)
lst = []
for k, s in enumerate(tl["segs"]):
    n = round((s["vout"] - s["vin"]) * FPS)
    f0 = round(s["src_v0"] * FPS)
    out = f"work/pieces/v{k:02d}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "/home/user/DEMO/ad_1_for_feed.mp4", "-vf",
                    f"select='between(n\\,{f0}\\,{f0 + n - 1})',setpts=N/{FPS}/TB,crop=1080:928:0:211", "-an", "-frames:v", str(n),
                    "-r", str(FPS), "-c:v", "libx264", "-crf", "12", "-preset", "fast", "-pix_fmt", "yuv420p", out], check=True)
    got = int(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v", "-show_entries", "stream=nb_read_frames",
                              "-of", "csv=p=0", out], capture_output=True, text=True).stdout)
    assert got == n, (k, got, n)
    lst.append(f"file 'pieces/v{k:02d}.mp4'")
open("work/pieces.txt", "w").write("\n".join(lst) + "\n")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", "work/pieces.txt", "-c", "copy", "work/speaker_cut.mp4"], check=True)
n = int(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v", "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0",
                        "work/speaker_cut.mp4"], capture_output=True, text=True).stdout)
print("speaker_cut frames", n, "expected", round(tl["dur"] * FPS))
