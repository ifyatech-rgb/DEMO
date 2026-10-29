"""Prep for the calm Connor commercial: warm daylight grade on the client's take (timing untouched) and on the b-roll so they
read as one shoot, voice at -14 LUFS (light cleanup only), quiet wind + birds under the avatar shots (~-30 LUFS, dipped under
b-roll), a calm music bed (Mixkit track 143) at ~8-10 % with a gentle lift into the offer and ending, and softened SFX."""
import json, os, re, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
run = lambda *a: subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)
DUR = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "assets/source.mp4"], capture_output=True, text=True).stdout)
lufs = lambda f: float(re.findall(r"I:\s+(-?[\d.]+) LUFS", subprocess.run(["ffmpeg", "-i", f, "-af", "ebur128=framelog=quiet", "-f", "null", "-"], capture_output=True, text=True).stderr)[-1])
BR = json.load(open("tools/broll.json"))
OFFER = [w["start"] for w in json.load(open("transcript.json")) if w["text"].lower().startswith("no-obligation")][0] - 0.6

# one warm, natural daylight grade for everything
GRADE = "eq=contrast=1.05:saturation=1.04:gamma=0.99,colorbalance=rs=0.025:gs=0.008:bs=-0.03:rh=0.015:bh=-0.02"
run("-i", "assets/source.mp4", "-an", "-vf", GRADE, "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-g", "25", "-pix_fmt", "yuv420p", "assets/look.mp4")
for b in {b["file"] for b in BR}:
    run("-i", f"../connor/assets/prep/{b}", "-an", "-vf", f"{GRADE},eq=saturation=0.96", "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-g", "15", "-pix_fmt", "yuv420p", f"assets/br/{b}")

# voice: gentle cleanup, two-pass linear loudnorm to -14
pre = "highpass=f=80,acompressor=threshold=-20dB:ratio=1.8:attack=12:release=180:makeup=1"
log = subprocess.run(["ffmpeg", "-i", "assets/source.mp4", "-af", f"{pre},loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
m = json.loads(log[log.rfind("{"):log.rfind("}") + 1])
run("-i", "assets/source.mp4", "-af", f"{pre},loudnorm=I=-14:TP=-1.5:LRA=9:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
    f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,aresample=48000", "-ac", "2", "assets/vo.wav")

# ambience: light wind + birds, dipped to 40 % under the b-roll
dip = "+".join(f"between(t,{b['t0']:.2f},{b['t1']:.2f})" for b in BR)
run("-stream_loop", "-1", "-i", "assets/dl/s2658.mp3", "-stream_loop", "-1", "-ss", "48", "-i", "assets/dl/s2464.mp3", "-filter_complex",
    f"[0:a]atrim=0:{DUR},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,lowpass=f=5000,volume=-4dB[a];"
    f"[1:a]atrim=0:{DUR},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,highpass=f=600,volume=-8dB[b];"
    f"[a][b]amix=inputs=2:normalize=0,afade=t=in:d=0.5,afade=t=out:st={DUR - 0.8:.2f}:d=0.8,volume='if({dip},0.4,1)':eval=frame[o]", "-map", "[o]", "assets/amb_raw.wav")
run("-i", "assets/amb_raw.wav", "-af", f"volume={-30 - lufs('assets/amb_raw.wav'):.2f}dB", "assets/ambience.wav")

# music: calm bed, gentle lift into the offer and the ending, ducked under the voice
SRC = "assets/dl/mk143.mp3"
g = -14 - lufs(SRC)
auto = f"volume='0.85+0.2*min(1,max(0,(t-{OFFER:.2f})/3))':eval=frame"
run("-t", f"{DUR}", "-i", SRC, "-i", "assets/vo.wav", "-filter_complex",
    f"[0:a]aresample=48000,aformat=channel_layouts=stereo,volume={g:.2f}dB,{auto},afade=t=in:d=1.0,afade=t=out:st={DUR - 1.2:.2f}:d=1.2,volume=0.17[m];"
    "[1:a]aformat=channel_layouts=stereo[sc];[m][sc]sidechaincompress=threshold=0.06:ratio=2.5:attack=20:release=300:makeup=1[bed]", "-map", "[bed]", "assets/music_bed.wav")

# soft SFX: whoosh for card entrances, click for the steps, chime for the end card
for name, src, af in [("whoosh", "swoosh", "lowpass=f=4500,afade=t=in:d=0.04"), ("click", "tap", "lowpass=f=6000"), ("chime", "ding", "lowpass=f=7000,afade=t=out:st=1.0:d=0.8")]:
    run("-i", f"../connor2/assets/sfx/{src}.wav", "-af", af, "-ar", "48000", "-ac", "2", f"assets/sfx/{name}.wav")
for f in ("assets/vo.wav", "assets/ambience.wav", "assets/music_bed.wav"): print(f, lufs(f), "LUFS")
