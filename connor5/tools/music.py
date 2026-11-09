"""Music bed: Mixkit track 112 (bright, light, ~123 BPM) at ~10 % under the voice, ducked while he speaks, with a small
lift into the "book your 30-minute inspection" ending."""
import json, os, re, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
run = lambda *a: subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)
DUR = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "assets/look.mp4"], capture_output=True, text=True).stdout)
lufs = lambda f: float(re.findall(r"I:\s+(-?[\d.]+) LUFS", subprocess.run(["ffmpeg", "-i", f, "-af", "ebur128=framelog=quiet", "-f", "null", "-"], capture_output=True, text=True).stderr)[-1])
words = json.load(open("transcript.json"))
END = [w["start"] for i, w in enumerate(words) if w["text"].lower() == "so" and words[i + 1]["text"].lower() == "book"][0]
SRC = "assets/mk112.mp3"
g = -14 - lufs(SRC)
run("-t", f"{DUR}", "-i", SRC, "-i", "assets/vo.wav", "-filter_complex",
    f"[0:a]aresample=48000,aformat=channel_layouts=stereo,volume={g:.2f}dB,volume='1+0.25*min(1,max(0,(t-{END:.2f})/1.5))':eval=frame,"
    f"afade=t=in:d=0.5,afade=t=out:st={DUR - 1.0:.2f}:d=1.0,volume=0.16[m];"
    "[1:a]aformat=channel_layouts=stereo[sc];[m][sc]sidechaincompress=threshold=0.06:ratio=3:attack=15:release=250:makeup=1[bed]", "-map", "[bed]", "assets/music_bed.wav")
print("music_bed", lufs("assets/music_bed.wav"), "LUFS")
