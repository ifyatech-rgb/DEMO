"""Phone-camera look + b-roll cutaways + audio beds for the Connor selfie ad.

Video: every clip gets the same light phone look (slight softness, light film-free sensor grain, compression
softness from a modest CRF, neutral daylight colour). B-roll comes only from the client's own footage:
the Pinecrest truck video and the roof/crew clips from their earlier edits (the edits' audio is never used).
Audio: voice (-14 LUFS, light clean, no studio polish), job-site ambience bed (~-29 LUFS), music bed (~-34 LUFS,
ducked under the voice). All Mixkit sounds under the Mixkit free licences."""
import json, os, re, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT); os.makedirs("assets/prep", exist_ok=True)
run = lambda *a: subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)
probe = lambda f: float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f], capture_output=True, text=True).stdout)
LOOK = "gblur=sigma=0.55,noise=alls=7:allf=t,eq=saturation=1.02:contrast=1.02"
RC, TRUCK = "../roughcut/assets/source.mp4", "../pinecrest-live/assets/truck.mov"
DUR = probe("assets/source.mp4")

# ---- video ----
run("-i", "assets/source.mp4", "-an", "-vf", f"fps=30,{LOOK}", "-c:v", "libx264", "-crf", "23", "-preset", "medium", "-pix_fmt", "yuv420p", "assets/prep/face.mp4")
BROLL = json.load(open("tools/broll.json"))
for b in BROLL:
    src = TRUCK if b["src"] == "truck" else RC
    d = b["t1"] - b["t0"] + 0.4
    vf = f"scale=1080:1920:flags=lanczos,fps=30,{LOOK}" if b["src"] == "truck" else f"fps=30,{LOOK}"
    if b.get("speed"): vf = f"setpts={1 / b['speed']:.4f}*PTS," + vf
    run("-ss", f"{b['ss']}", "-t", f"{d * (b.get('speed') or 1):.3f}", "-i", src, "-an", "-vf", vf, "-c:v", "libx264", "-crf", "23", "-preset", "medium",
        "-pix_fmt", "yuv420p", "-t", f"{d:.3f}", b["file"])

# ---- voice: high-pass, gentle compression, loudnorm -14 (2-pass, linear) ----
pre = "highpass=f=80,acompressor=threshold=-20dB:ratio=2:attack=10:release=150:makeup=1"
log = subprocess.run(["ffmpeg", "-i", "assets/source.mp4", "-af", f"{pre},loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
m = json.loads(log[log.rfind("{"):log.rfind("}") + 1])
ln = (f"loudnorm=I=-14:TP=-1.5:LRA=9:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
      f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
run("-i", "assets/source.mp4", "-vn", "-af", f"{pre},{ln},aresample=48000", "-ac", "2", "assets/vo.wav")

# ---- job-site ambience bed ----
D = "assets/dl/"
layers = [  # (file, ss, at, dur, filter, gain dB)
    (D + "s2658.mp3", 0.0, 0.0, DUR, "", -6),                                   # wind
    (D + "s2464.mp3", 48.0, 0.0, DUR, "highpass=f=600,", -10),                  # birds
    (D + "s797.mp3", 20.0, 0.0, DUR, "lowpass=f=2200,", -14),                   # distant crew working
    (D + "s802.mp3", 8.0, 21.0, 12.0, "lowpass=f=1200,afade=t=in:d=3,afade=t=out:st=9:d=3,", -16),   # distant truck passing
]
HAMMER = [3.1, 3.42, 3.75, 11.5, 11.85, 19.0, 19.36, 27.4, 34.2, 34.52, 34.86, 44.0, 44.33, 52.0, 52.34, 59.2]
NAIL = [7.2, 7.46, 23.1, 23.36, 23.62, 40.8, 41.06, 55.0, 55.26]
CLANK = [(15.0, "s835"), (31.0, "s833"), (47.3, "s835")]
for t in HAMMER: layers.append((D + "s830.mp3", 0.0, t, 0.8, "lowpass=f=3000,aecho=0.8:0.5:60:0.3,", -15))
for t in NAIL: layers.append((D + "s817.mp3", 0.0, t, 0.6, "lowpass=f=3500,aecho=0.8:0.4:50:0.25,", -18))
for t, f in CLANK: layers.append((D + f + ".mp3", 0.0, t, 1.0, "lowpass=f=3500,aecho=0.8:0.4:70:0.3,", -16))
ins, fc = [], []
for k, (f, ss, t, d, flt, g) in enumerate(layers):
    ins += ["-ss", f"{ss}", "-t", f"{d}", "-i", f]
    ms = int(t * 1000)
    fc.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo,{flt}volume={g}dB,adelay={ms}|{ms}[l{k}]")
fc.append("".join(f"[l{k}]" for k in range(len(layers))) + f"amix=inputs={len(layers)}:normalize=0,apad=whole_dur={DUR},atrim=0:{DUR},afade=t=in:d=0.3[o]")
run(*ins, "-filter_complex", ";".join(fc), "-map", "[o]", "assets/amb_raw.wav")
lufs = lambda f: float(re.findall(r"I:\s+(-?[\d.]+) LUFS", subprocess.run(["ffmpeg", "-i", f, "-af", "ebur128=framelog=quiet", "-f", "null", "-"], capture_output=True, text=True).stderr)[-1])
run("-i", "assets/amb_raw.wav", "-af", f"volume={-29 - lufs('assets/amb_raw.wav'):.2f}dB", "assets/ambience.wav")

# ---- music bed: light, ~9 % under the voice, ducked ----
g = -14 - lufs(D + "m1167.mp3")
run("-i", D + "m1167.mp3", "-i", "assets/vo.wav", "-filter_complex",
    f"[0:a]atrim=0:{DUR},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,volume={g:.2f}dB,afade=t=in:d=1,afade=t=out:st={DUR - 2.5:.2f}:d=2.5,volume=0.15[m];"
    "[1:a]aformat=channel_layouts=stereo[sc];[m][sc]sidechaincompress=threshold=0.08:ratio=2:attack=20:release=300:makeup=1[bed]",
    "-map", "[bed]", "assets/music_bed.wav")
for f in ("assets/vo.wav", "assets/ambience.wav", "assets/music_bed.wav"): print(f, lufs(f), "LUFS")
