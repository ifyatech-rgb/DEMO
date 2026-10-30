"""Prep for the Connor field ad: light phone look on the client's take (timing untouched), the client's own b-roll clips
graded to match, voice at -14 LUFS with a slight outdoor feel, job-site ambience under the avatar shots (~-28 LUFS, dipped
under the b-roll), an upbeat music bed (tools/music.py) and the turn's freeze frame."""
import json, os, re, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
run = lambda *a: subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)
DUR = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "assets/source.mp4"], capture_output=True, text=True).stdout)
lufs = lambda f: float(re.findall(r"I:\s+(-?[\d.]+) LUFS", subprocess.run(["ffmpeg", "-i", f, "-af", "ebur128=framelog=quiet", "-f", "null", "-"], capture_output=True, text=True).stderr)[-1])
words = json.load(open("transcript.json"))
TU = [w["start"] for i, w in enumerate(words) if w["text"].lower() == "that" and words[i + 1]["text"].lower() == "is"][0]
BR = json.load(open("tools/broll.json"))

LOOK = "eq=contrast=1.04:saturation=1.05,colorbalance=rs=0.015:bs=-0.015"
run("-i", "assets/source.mp4", "-an", "-vf", f"{LOOK},noise=alls=4:allf=t", "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-g", "25", "-pix_fmt", "yuv420p", "assets/look.mp4")
run("-ss", f"{TU}", "-i", "assets/look.mp4", "-frames:v", "1", "-q:v", "2", "assets/freeze-turn.jpg")
os.makedirs("assets/br", exist_ok=True)
for b, ss in {(b["file"], b.get("ss", 0)) for b in BR}:   # ss trims a clip's fade-from-black head
    run("-ss", f"{ss}", "-i", f"../connor/assets/prep/{b}", "-an", "-vf", LOOK, "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-g", "15", "-pix_fmt", "yuv420p", f"assets/br/{b}")

# voice: gentle cleanup + a touch of open-air early reflection, then two-pass linear loudnorm to -14
pre = "highpass=f=80,acompressor=threshold=-20dB:ratio=2:attack=10:release=150:makeup=1,aecho=0.9:0.25:35:0.07"
log = subprocess.run(["ffmpeg", "-i", "assets/source.mp4", "-af", f"{pre},loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
m = json.loads(log[log.rfind("{"):log.rfind("}") + 1])
run("-i", "assets/source.mp4", "-vn", "-af", f"{pre},loudnorm=I=-14:TP=-1.5:LRA=9:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
    f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,aresample=48000", "-ac", "2", "assets/vo.wav")

# job-site ambience: wind, birds, distant construction bed, hammering, nail-gun bursts, ladder clanks
D = "assets/dl/"
layers = [(D + "s2658.mp3", 0.0, 0.0, DUR, "", -6), (D + "s2464.mp3", 48.0, 0.0, DUR, "highpass=f=600,", -10), (D + "s797.mp3", 20.0, 0.0, DUR, "lowpass=f=2200,", -14)]
for t in [3.4, 3.75, 9.9, 10.25, 17.6, 17.95, 21.0, 21.35, 38.0, 38.34, 45.0, 45.35, 50.0, 57.0, 57.35]: layers.append((D + "s830.mp3", 0.0, t, 0.8, "lowpass=f=3000,aecho=0.8:0.5:60:0.3,", -15))
for t in [7.6, 7.86, 19.0, 19.26, 19.52, 29.9, 30.16, 47.4, 47.66]: layers.append((D + "s817.mp3", 0.0, t, 0.6, "lowpass=f=3500,aecho=0.8:0.4:50:0.25,", -18))
for t, f in [(10.4, "s835"), (16.6, "s833"), (39.4, "s835"), (48.6, "s833"), (58.2, "s835")]: layers.append((D + f + ".mp3", 0.0, t, 1.0, "lowpass=f=3500,aecho=0.8:0.4:70:0.3,", -16))
ins, fc = [], []
for k, (f, ss, t, d, flt, g) in enumerate(layers):
    ins += ["-ss", f"{ss}", "-t", f"{d}", "-i", f]; ms = int(t * 1000)
    fc.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo,{flt}volume={g}dB,adelay={ms}|{ms}[l{k}]")
dip = "+".join(f"between(t,{b['t0']:.3f},{b['t1']:.3f})" for b in BR)
fc.append("".join(f"[l{k}]" for k in range(len(layers))) + f"amix=inputs={len(layers)}:normalize=0,apad=whole_dur={DUR},atrim=0:{DUR},volume='if({dip},0.4,1)':eval=frame[o]")
run(*ins, "-filter_complex", ";".join(fc), "-map", "[o]", "assets/amb_raw.wav")
run("-i", "assets/amb_raw.wav", "-af", f"volume={-28 - lufs('assets/amb_raw.wav'):.2f}dB", "assets/ambience.wav")
subprocess.run(["python3", "tools/music.py"], check=True)
for f in ("assets/vo.wav", "assets/ambience.wav", "assets/music_bed.wav"): print(f, lufs(f), "LUFS")
