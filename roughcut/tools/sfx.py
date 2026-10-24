"""Trim + peak-normalise the Mixkit sound effects (assets/dl/s<ID>.mp3) into assets/sfx/<name>.wav.
Each file starts at its transient so a cue's time is its hit time. All are Mixkit Sound Effects Free License."""
import os, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT); os.makedirs("assets/sfx", exist_ok=True)
SFX = {  # name: (mixkit id, start, duration)
    "boom": (2908, 0.03, 3.2), "coins": (1993, 0.02, 1.0), "bell": (931, 0.0, 1.2), "beep": (2964, 0.0, 0.6),
    "birds": (2464, 48.0, 3.0), "whip": (1474, 0.30, 2.2), "ice": (2834, 0.0, 1.2), "crack": (2943, 0.0, 0.8),
    "creak": (337, 0.06, 0.9), "drip": (3179, 0.02, 1.2), "ding": (951, 0.03, 1.6), "thunder": (1296, 0.05, 4.5),
    "scribble": (2370, 0.0, 1.6), "peel": (1538, 0.45, 2.4), "swoosh": (1464, 0.0, 0.8), "pop": (3005, 0.0, 0.2),
    "shutter": (1430, 0.09, 0.5), "shutter2": (1133, 0.12, 0.3), "warm": (3109, 0.02, 1.7), "tap": (1120, 0.08, 0.25),
    "notify": (933, 0.06, 2.6), "wA": (166, 0.05, 0.75), "wB": (3115, 0.04, 0.55),
}
def norm(src, out, ss, d, pre=""):
    fade = f"afade=t=out:st={max(0.0, d - min(0.4, d / 3)):.3f}:d={min(0.4, d / 3):.3f}"
    o = subprocess.run(["ffmpeg", "-ss", f"{ss}", "-t", f"{d}", "-i", src, "-af", f"{pre}volumedetect", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    peak = float(o.split("max_volume:")[1].split("dB")[0])
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ss}", "-t", f"{d}", "-i", src, "-af",
                    f"{pre}volume={-1 - peak:.2f}dB,{fade},aresample=48000", "-ac", "2", out], check=True)
for name, (iid, ss, d) in SFX.items():
    norm(f"assets/dl/s{iid}.mp3", f"assets/sfx/{name}.wav", ss, d)
# Ka-ching: coin rattle with the register bell landing 60 ms later.
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "assets/sfx/coins.wav", "-i", "assets/sfx/bell.wav", "-filter_complex",
                "[1]adelay=60|60,volume=0.9[b];[0]volume=0.8[c];[c][b]amix=inputs=2:normalize=0:duration=longest,alimiter=limit=0.89", "assets/sfx/kaching.wav"], check=True)
print(len(SFX) + 1, "sfx ready")
