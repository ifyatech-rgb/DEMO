"""Rebuild the presenter's voice from the source take with the same cuts as assets/aroll.mp4, but with
stronger, tracked noise reduction and a soft expander so the room hiss between phrases drops away.
Writes assets/voice_v2.wav and assets/aroll_v2.mp4 (graded picture from aroll.mp4 + new voice)."""
import json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
CHAIN = sys.argv[1] if len(sys.argv) > 1 else (
    "highpass=f=90,afftdn=nr=22:nf=-34:tn=1,"
    "agate=threshold=0.018:ratio=2.5:range=0.25:attack=4:release=180:knee=4,"
    "equalizer=f=250:t=q:w=1:g=-2.5,equalizer=f=3200:t=q:w=1.2:g=2,equalizer=f=7500:t=q:w=1.5:g=-2,"
    "acompressor=threshold=-21dB:ratio=2.5:attack=8:release=120:makeup=2,loudnorm=I=-14:TP=-1.5:LRA=7,aresample=48000")
segs = json.load(open("assets/segments.json"))
fc = [f"[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.008,afade=t=out:st={b - a - 0.008:.3f}:d=0.008[a{k}]"
      for k, (a, b) in enumerate(segs)]
fc.append("".join(f"[a{k}]" for k in range(len(segs))) + f"concat=n={len(segs)}:v=0:a=1[ac]")
fc.append(f"[ac]{CHAIN}[ao]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "assets/source.mp4", "-filter_complex", ";".join(fc), "-map", "[ao]",
                "assets/voice_v2.wav"], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "assets/aroll.mp4", "-i", "assets/voice_v2.wav", "-map", "0:v", "-map", "1:a",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "assets/aroll_v2.mp4"], check=True)
print("voice_v2.wav + aroll_v2.mp4 written")
