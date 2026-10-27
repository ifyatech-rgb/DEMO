"""Cut the VSL take: keep the natural pace, only shorten dead air over 1 s (one spot, ~105 s) to 0.35 s.
Writes assets/base.mp4 (1920x1080, picture untouched apart from the cut), assets/vo.wav (voice, -14 LUFS:
80 Hz high-pass + one linear gain, no denoise/compression) and transcript.json (word times on the cut timeline)."""
import json, subprocess
SRC = "assets/source.mp4"
CUTS = [(105.45, 106.15)]                 # dead air 105.27-106.32 (1.05 s) -> 0.35 s
total = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", SRC], capture_output=True, text=True).stdout)
segs, cur = [], 0.0
for a, b in CUTS: segs.append((cur, a)); cur = b
segs.append((cur, total))
fc = []
for k, (a, b) in enumerate(segs):
    fc.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{k}]")
    fc.append(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st={b - a - 0.01:.3f}:d=0.01[a{k}]")
fc.append("".join(f"[v{k}][a{k}]" for k in range(len(segs))) + f"concat=n={len(segs)}:v=1:a=1[v][a]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "15",
                "-preset", "medium", "-pix_fmt", "yuv420p", "-r", "25", "-c:a", "pcm_s16le", "assets/base_raw.mkv"], check=True)
log = subprocess.run(["ffmpeg", "-i", "assets/base_raw.mkv", "-af", "highpass=f=80,loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
m = json.loads(log[log.rfind("{"):log.rfind("}") + 1])
ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
      f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "assets/base_raw.mkv", "-vn", "-af", f"highpass=f=80,{ln},aresample=48000", "-ac", "2", "assets/vo.wav"], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "assets/base_raw.mkv", "-an", "-c:v", "copy", "assets/base.mp4"], check=True)
w = json.load(open("assets/source-transcript.json")); w = w if isinstance(w, list) else w["words"]
out, shift = [], 0.0
for x in w:
    s, e = x["start"], x["end"]
    for a, b in CUTS:
        if s >= b: s -= b - a; e -= b - a
    out.append({**x, "start": round(s, 3), "end": round(e, 3)})
json.dump(out, open("transcript.json", "w"), indent=1)
print(segs, "->", round(sum(b - a for a, b in segs), 2), "s")
