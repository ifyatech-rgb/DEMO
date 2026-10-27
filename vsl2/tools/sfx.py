"""Trim + peak-normalise Mixkit SFX (assets/dl/s<ID>.mp3) into assets/sfx/<name>.wav, each starting on its transient.
All Mixkit Sound Effects Free License (https://mixkit.co/license/#sfxFree)."""
import os, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT); os.makedirs("assets/sfx", exist_ok=True)
SFX = {  # name: (mixkit id, start, duration)
    "boom": (2908, 0.03, 3.0), "coins": (1993, 0.02, 1.0), "bell": (931, 0.0, 1.2), "coindrop": (1989, 0.08, 1.0),
    "tick": (1120, 0.08, 0.25), "thunder": (1296, 0.05, 3.5), "stamp": (2182, 0.04, 0.4), "bass": (2299, 0.05, 1.0),
    "buzzer": (954, 0.0, 0.9), "riser": (790, 0.9, 1.7), "swoosh": (1464, 0.0, 0.8), "pop": (3005, 0.0, 0.2),
    "count": (2568, 0.0, 0.2), "ding": (600, 0.0, 1.8), "click": (2585, 0.0, 0.5), "clock": (1063, 0.1, 1.6),
    "notify": (933, 0.06, 2.4), "buzzer2": (954, 0.0, 0.9), "ring": (1350, 0.08, 1.0), "gear": (2858, 0.0, 1.0),
    "blow": (2655, 0.0, 0.8), "tap": (1120, 0.08, 0.25), "wA": (166, 0.05, 0.75), "wB": (3115, 0.04, 0.55), "whip": (1474, 0.30, 2.2),
}
def norm(src, out, ss, d):
    f = min(0.3, d / 3)
    o = subprocess.run(["ffmpeg", "-ss", f"{ss}", "-t", f"{d}", "-i", src, "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True).stderr
    peak = float(o.split("max_volume:")[1].split("dB")[0])
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ss}", "-t", f"{d}", "-i", src, "-af",
                    f"volume={-1 - peak:.2f}dB,afade=t=out:st={d - f:.3f}:d={f:.3f},aresample=48000", "-ac", "2", out], check=True)
for name, (iid, ss, d) in SFX.items(): norm(f"assets/dl/s{iid}.mp3", f"assets/sfx/{name}.wav", ss, d)
mix = lambda ins, fc, out: subprocess.run(["ffmpeg", "-v", "error", "-y", *sum((["-i", i] for i in ins), []), "-filter_complex", fc, out], check=True)
mix(["assets/sfx/coins.wav", "assets/sfx/bell.wav"], "[1]adelay=60|60,volume=0.9[b];[0]volume=0.8[c];[c][b]amix=inputs=2:normalize=0:duration=longest,alimiter=limit=0.89", "assets/sfx/kaching.wav")
mix(["assets/sfx/stamp.wav", "assets/sfx/bass.wav"], "[0][1]amix=inputs=2:normalize=0:duration=longest,alimiter=limit=0.89", "assets/sfx/stamp_heavy.wav")
mix(["assets/sfx/bass.wav", "assets/sfx/boom.wav"], "[1]volume=0.6[b];[0][b]amix=inputs=2:normalize=0:duration=longest,alimiter=limit=0.89", "assets/sfx/drop.wav")
mix(["assets/sfx/gear.wav", "assets/sfx/boom.wav"], "[1]volume=0.55[b];[0][b]amix=inputs=2:normalize=0:duration=longest,alimiter=limit=0.89", "assets/sfx/machine.wav")
print(len(SFX) + 4, "sfx ready")
