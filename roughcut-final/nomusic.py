"""v4: the v3 re-edit with the background music removed. VO and SFX stems, their balance and the picture are
unchanged; the VO+SFX mix is levelled to -14 LUFS. Run after rebuild.py (uses its stems)."""
import re, subprocess
run = lambda *a: subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)
mix = "[0:a][1:a]amix=inputs=2:normalize=0"
log = subprocess.run(["ffmpeg", "-i", "assets/vo_edit.wav", "-i", "assets/sfx_edit.wav", "-filter_complex", f"{mix},ebur128=framelog=quiet",
                      "-f", "null", "-"], capture_output=True, text=True).stderr
gain = -14 - float(re.findall(r"I:\s+(-?[\d.]+) LUFS", log)[-1])
run("-i", "assets/vo_edit.wav", "-i", "assets/sfx_edit.wav", "-filter_complex",
    f"{mix},volume={gain:.2f}dB,alimiter=limit=0.84:level=false[a]", "-map", "[a]", "assets/mix_nomusic.wav")
for src, out, vf in (("assets/edit.mp4", "../pinecrest-roughcut-9x16-v4-nomusic.mp4", None),
                     ("../pinecrest-roughcut-4x5-v3.mp4", "../pinecrest-roughcut-4x5-v4-nomusic.mp4", None)):
    run("-i", src, "-i", "assets/mix_nomusic.wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart", "-shortest", out)
print("gain", round(gain, 2), "dB")
