"""Music bed: Mixkit track 112 (bright, driving, ~123 BPM). Held back (slightly darker and quieter) through the opening
and the claims/adjuster part, opens up at "that is exactly where we come in", then builds to the end. Ducked under the voice."""
import json, os, re, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
run = lambda *a: subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)
DUR = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "assets/source.mp4"], capture_output=True, text=True).stdout)
lufs = lambda f: float(re.findall(r"I:\s+(-?[\d.]+) LUFS", subprocess.run(["ffmpeg", "-i", f, "-af", "ebur128=framelog=quiet", "-f", "null", "-"], capture_output=True, text=True).stderr)[-1])
words = json.load(open("transcript.json"))
TU = [w["start"] for i, w in enumerate(words) if w["text"].lower() == "that" and words[i + 1]["text"].lower() == "is"][0]
SRC = "assets/dl/mk112.mp3"
g = -14 - lufs(SRC)
auto = (f"lowpass=f=3200:enable='lt(t,{TU})',"
        f"volume='if(lt(t,{TU}),0.8,1+0.3*min(1,max(0,(t-{TU + 18})/14)))':eval=frame")
run("-t", f"{DUR}", "-i", SRC, "-i", "assets/vo.wav", "-filter_complex",
    f"[0:a]aresample=48000,aformat=channel_layouts=stereo,volume={g:.2f}dB,{auto},afade=t=in:d=0.3,afade=t=out:st={DUR - 0.8:.2f}:d=0.8,volume=0.17[m];"
    "[1:a]aformat=channel_layouts=stereo[sc];[m][sc]sidechaincompress=threshold=0.07:ratio=2.5:attack=15:release=250:makeup=1[bed]", "-map", "[bed]", "assets/music_bed.wav")
print("music_bed", lufs("assets/music_bed.wav"), "LUFS")
