"""Cut the presenter take: drop the "roofing for over ... years" flub, cap every pause at ~0.2 s,
clean the voice to -14 LUFS. Writes assets/aroll.mp4 (1080x1920, 30 fps) and assets/segments.json."""
import json, re, subprocess
SRC, KEEP = "assets/source.mp4", 0.08
w = json.load(open("transcript.json")); w = w if isinstance(w, list) else w["words"]
txt = [re.sub(r"[.,?!]+$", "", x["text"]).lower() for x in w]
i_g = txt.index("grapefruit"); i_ive = txt.index("i've")
FLUB = (w[i_g]["end"] + 0.10, w[i_ive]["start"] - 0.04)        # "As someone who's been roofing for over years,"
total = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", SRC],
                             capture_output=True, text=True).stdout)
log = subprocess.run(["ffmpeg", "-i", SRC, "-af", "silencedetect=noise=-35dB:d=0.22", "-f", "null", "-"], capture_output=True, text=True).stderr
sil = list(zip(map(float, re.findall(r"silence_start: ([\d.]+)", log)), map(float, re.findall(r"silence_end: ([\d.]+)", log))))
cuts = [(s + KEEP, e - KEEP) for s, e in sil if e - s > 0.22 and s > 0.05] + [FLUB]
cuts = sorted(c for c in cuts if c[1] > c[0])
segs, cur = [], 0.0
for a, b in cuts:
    if a > cur: segs.append((cur, a))
    cur = max(cur, b)
segs.append((cur, total - 0.05))
json.dump(segs, open("assets/segments.json", "w"))
fc = []
for k, (a, b) in enumerate(segs):
    fc.append(f"[0:v]trim={a:.3f}:{b:.3f},setpts=PTS-STARTPTS,fps=30[v{k}]")
    fc.append(f"[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.008,afade=t=out:st={b - a - 0.008:.3f}:d=0.008[a{k}]")
fc.append("".join(f"[v{k}][a{k}]" for k in range(len(segs))) + f"concat=n={len(segs)}:v=1:a=1[vc][ac]")
fc.append("[ac]highpass=f=85,afftdn=nr=10:nf=-40,equalizer=f=250:t=q:w=1:g=-2,equalizer=f=3500:t=q:w=1.2:g=2.5,"
          "acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=3,loudnorm=I=-14:TP=-1.5:LRA=7,aresample=48000[ao]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-filter_complex", ";".join(fc), "-map", "[vc]", "-map", "[ao]",
                "-c:v", "libx264", "-crf", "15", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                "assets/aroll_raw.mp4"], check=True)
print(len(segs), "segments ->", round(sum(b - a for a, b in segs), 2), "s; flub cut", [round(x, 2) for x in FLUB])
