"""Tighten pauses, strip the letterbox bars at native size, clean voice. Writes assets/cut.mp4 and assets/segments.json."""
import json, re, subprocess, sys
SRC = "assets/source.mp4"; PAD = 0.05
log = subprocess.run(["ffmpeg", "-i", "assets/source16k.wav", "-af", "silencedetect=noise=-30dB:d=0.11",
                      "-f", "null", "-"], capture_output=True, text=True).stderr
st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
total = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", SRC],
                           capture_output=True, text=True).stdout)
segs, cur = [], 0.0
for s, e in zip(st, en):
    if s <= 0.01: cur = max(0.0, e - PAD); continue
    if e >= total - 0.05: segs.append((cur, s + 0.12)); cur = None; break
    segs.append((cur, s + PAD)); cur = e - PAD
if cur is not None: segs.append((cur, total))
json.dump(segs, open("assets/segments.json", "w"), indent=1)
print(len(segs), "segments, out duration %.2f" % sum(b - a for a, b in segs))
# Keep only the native 1080x1024 picture area (no scaling); the composition re-adds the black bars.
crop = "crop=1080:1024:0:448,setsar=1"
fc = []
for i, (a, b) in enumerate(segs):
    fc.append(f"[0:v]trim={a:.3f}:{b:.3f},setpts=PTS-STARTPTS[v{i}]")
    fc.append(f"[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.008,"
              f"afade=t=out:st={b - a - 0.008:.3f}:d=0.008[a{i}]")
fc.append("".join(f"[v{i}][a{i}]" for i in range(len(segs))) + f"concat=n={len(segs)}:v=1:a=1[vc][ac]")
fc.append(f"[vc]{crop}[vo]")
# Voice: rumble cut, denoise, de-mud, presence, compression, loudness to -14 LUFS.
fc.append("[ac]highpass=f=85,afftdn=nr=12:nf=-40,equalizer=f=250:t=q:w=1:g=-2,"
          "equalizer=f=3500:t=q:w=1.2:g=3,acompressor=threshold=-20dB:ratio=3.5:attack=5:release=80:makeup=4,"
          "loudnorm=I=-14:TP=-1.5:LRA=7,aresample=48000[ao]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-filter_complex", ";".join(fc), "-map", "[vo]", "-map", "[ao]",
                "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", "25",
                "-c:a", "aac", "-b:a", "192k", "assets/cut.mp4"], check=True)
