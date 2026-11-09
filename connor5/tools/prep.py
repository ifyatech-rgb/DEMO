"""Prep for the reference-style Connor ad: the take with the real shirt logo (tools/logo.py) and the sketch-reveal
opening (tools/intro.py), a light natural look, and the voice cleaned to -14 LUFS. Voice only: no music, no ambience."""
import json, os, re, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
run = lambda *a: subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)
lufs = lambda f: float(re.findall(r"I:\s+(-?[\d.]+) LUFS", subprocess.run(["ffmpeg", "-i", f, "-af", "ebur128=framelog=quiet", "-f", "null", "-"], capture_output=True, text=True).stderr)[-1])

if not os.path.exists("assets/source_logo.mp4"): subprocess.run(["python3", "tools/logo.py"], check=True)
if not os.path.exists("assets/source_final.mp4"): subprocess.run(["python3", "tools/intro.py"], check=True)
run("-i", "assets/source_final.mp4", "-an", "-vf", "eq=contrast=1.03:saturation=1.04", "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-g", "25",
    "-pix_fmt", "yuv420p", "assets/look.mp4")

pre = "highpass=f=80,acompressor=threshold=-20dB:ratio=1.8:attack=12:release=180:makeup=1"
log = subprocess.run(["ffmpeg", "-i", "assets/source.mp4", "-af", f"{pre},loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
m = json.loads(log[log.rfind("{"):log.rfind("}") + 1])
run("-i", "assets/source.mp4", "-vn", "-af", f"{pre},loudnorm=I=-14:TP=-1.5:LRA=9:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
    f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,aresample=48000", "-ac", "2", "assets/vo.wav")
print("assets/vo.wav", lufs("assets/vo.wav"), "LUFS")
