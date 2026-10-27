"""Final audio for the VSL: voice (-14 LUFS, untouched otherwise) + ducked music bed + SFX cues from index.html,
mastered to -14 LUFS and muxed onto the rendered picture: mix.py RENDER.mp4 OUT.mp4"""
import re, subprocess, sys
run = lambda *a: subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)
DUR = float(re.search(r'data-duration="([\d.]+)"', open("index.html").read()).group(1))
cues = re.findall(r'<audio id="fx\d+" src="([^"]+)" data-start="([\d.]+)" data-duration="([\d.]+)" data-track-index="\d+" data-volume="([\d.]+)"', open("index.html").read())
ins, fc = [], []
for k, (src, st, du, vol) in enumerate(cues):
    ins += ["-i", src]; ms = int(float(st) * 1000)
    fc.append(f"[{k}:a]atrim=0:{du},aformat=sample_rates=48000:channel_layouts=stereo,volume={vol},adelay={ms}|{ms}[s{k}]")
fc.append("".join(f"[s{k}]" for k in range(len(cues))) + f"amix=inputs={len(cues)}:normalize=0,apad=whole_dur={DUR},atrim=0:{DUR}[o]")
run(*ins, "-filter_complex", ";".join(fc), "-map", "[o]", "assets/sfx_stem.wav")
SFX_GAIN = -3.0
mix = f"[2:a]volume={SFX_GAIN}dB[s];[0:a][1:a][s]amix=inputs=3:normalize=0"
meas = lambda f: float(re.findall(r"I:\s+(-?[\d.]+) LUFS", subprocess.run(["ffmpeg", "-i", f, "-af", "ebur128=framelog=quiet", "-f", "null", "-"],
                                                                         capture_output=True, text=True).stderr)[-1])
gain = 0.0
for _ in range(4):
    run("-i", "assets/vo.wav", "-i", "assets/music_bed.wav", "-i", "assets/sfx_stem.wav", "-filter_complex",
        f"{mix},volume={gain:.2f}dB,alimiter=limit=0.87:level=false[a]", "-map", "[a]", "assets/final_mix.wav")
    i = meas("assets/final_mix.wav")
    if abs(i + 14) < 0.06: break
    gain += -14 - i
if len(sys.argv) > 2:
    run("-i", sys.argv[1], "-i", "assets/final_mix.wav", "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "18", "-preset", "medium",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", sys.argv[2])
print(len(cues), "cues; master gain", round(gain, 2), "; mix", round(i, 2), "LUFS")
