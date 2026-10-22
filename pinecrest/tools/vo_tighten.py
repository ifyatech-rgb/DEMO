"""Tighten the voiceover: every pause over 0.15 s becomes 0.12 s; normalise to -14 LUFS.
Writes assets/vo_tight.wav and assets/vo_segments.json."""
import json, re, subprocess
SRC, KEEP = "assets/vo.mp3", 0.06   # 0.06 s of air kept on each side of a cut
log = subprocess.run(["ffmpeg", "-i", SRC, "-af", "silencedetect=noise=-38dB:d=0.15", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
total = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", SRC],
                             capture_output=True, text=True).stdout)
segs, cur = [], 0.0
for s, e in zip(st, en):
    if s <= 0.02: cur = max(0, e - KEEP); continue
    segs.append((cur, s + KEEP)); cur = e - KEEP
if cur < total - 0.05: segs.append((cur, total))
json.dump(segs, open("assets/vo_segments.json", "w"))
fc = [f"[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.006,afade=t=out:st={b - a - 0.006:.3f}:d=0.006[a{i}]"
      for i, (a, b) in enumerate(segs)]
fc.append("".join(f"[a{i}]" for i in range(len(segs))) + f"concat=n={len(segs)}:v=0:a=1,highpass=f=70,"
          "acompressor=threshold=-18dB:ratio=2.5:attack=8:release=90:makeup=2,loudnorm=I=-14:TP=-1.5:LRA=7,aresample=48000[o]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-filter_complex", ";".join(fc), "-map", "[o]", "assets/vo_tight.wav"], check=True)
print(len(segs), "segments ->", round(sum(b - a for a, b in segs), 2), "s")
