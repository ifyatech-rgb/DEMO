"""Prep for the Connor avatar ad: phone look on the client's cut (picture timing untouched), voice at -14 LUFS with a
light outdoor feel, job-site ambience under the avatar shots (dipped under the b-roll), and an upbeat music bed
(tools/music.py)."""
import json, os, re, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
run = lambda *a: subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)
DUR = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "assets/source.mp4"], capture_output=True, text=True).stdout)
lufs = lambda f: float(re.findall(r"I:\s+(-?[\d.]+) LUFS", subprocess.run(["ffmpeg", "-i", f, "-af", "ebur128=framelog=quiet", "-f", "null", "-"], capture_output=True, text=True).stderr)[-1])
words = json.load(open("transcript.json"))
TU = [w["start"] for i, w in enumerate(words) if w["text"].lower() == "that" and words[i + 1]["text"].lower() == "is"][0]
BR = [(0, 1.5), (374 / 30, 497 / 30), (797 / 30, 902 / 30), (902 / 30, 978 / 30), (978 / 30, 1057 / 30), (1244 / 30, 1354 / 30)]
run("-i", "assets/source.mp4", "-an", "-vf", "gblur=sigma=0.45,noise=alls=6:allf=t,eq=saturation=1.02:contrast=1.02", "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-pix_fmt", "yuv420p", "assets/look.mp4")
run("-ss", f"{TU}", "-i", "assets/look.mp4", "-frames:v", "1", "-q:v", "2", "assets/freeze-turn.jpg")
pre = "highpass=f=80,acompressor=threshold=-20dB:ratio=2:attack=10:release=150:makeup=1"
log = subprocess.run(["ffmpeg", "-i", "assets/source.mp4", "-af", f"{pre},loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
m = json.loads(log[log.rfind("{"):log.rfind("}") + 1])
run("-i", "assets/source.mp4", "-vn", "-af", f"{pre},loudnorm=I=-14:TP=-1.5:LRA=9:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
    f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,aresample=48000", "-ac", "2", "assets/vo.wav")
D = "assets/dl/"
layers = [(D + "s2658.mp3", 0.0, 0.0, DUR, "", -6), (D + "s2464.mp3", 48.0, 0.0, DUR, "highpass=f=600,", -10), (D + "s797.mp3", 20.0, 0.0, DUR, "lowpass=f=2200,", -14)]
for t in [5.4, 5.75, 6.1, 17.2, 17.55, 21.0, 21.35, 37.0, 37.34, 39.1, 47.8, 48.15, 55.2, 55.55]: layers.append((D + "s830.mp3", 0.0, t, 0.8, "lowpass=f=3000,aecho=0.8:0.5:60:0.3,", -15))
for t in [8.4, 8.66, 19.6, 19.86, 20.12, 38.0, 38.26, 52.6, 52.86]: layers.append((D + "s817.mp3", 0.0, t, 0.6, "lowpass=f=3500,aecho=0.8:0.4:50:0.25,", -18))
for t, f in [(11.0, "s835"), (23.4, "s833"), (46.3, "s835"), (59.6, "s833")]: layers.append((D + f + ".mp3", 0.0, t, 1.0, "lowpass=f=3500,aecho=0.8:0.4:70:0.3,", -16))
ins, fc = [], []
for k, (f, ss, t, d, flt, g) in enumerate(layers):
    ins += ["-ss", f"{ss}", "-t", f"{d}", "-i", f]; ms = int(t * 1000)
    fc.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo,{flt}volume={g}dB,adelay={ms}|{ms}[l{k}]")
dip = "+".join(f"between(t,{a:.3f},{b:.3f})" for a, b in BR)
fc.append("".join(f"[l{k}]" for k in range(len(layers))) + f"amix=inputs={len(layers)}:normalize=0,apad=whole_dur={DUR},atrim=0:{DUR},volume='if({dip},0.4,1)':eval=frame[o]")
run(*ins, "-filter_complex", ";".join(fc), "-map", "[o]", "assets/amb_raw.wav")
run("-i", "assets/amb_raw.wav", "-af", f"volume={-28.5 - lufs('assets/amb_raw.wav'):.2f}dB", "assets/ambience.wav")
subprocess.run(["python3", "tools/music.py"], check=True)
for f in ("assets/vo.wav", "assets/ambience.wav", "assets/music_bed.wav"): print(f, lufs(f), "LUFS")
