"""v2 audio: processed voice + background music + fuller SFX.
Music: Mixkit track #112 (Mixkit Stock Music Free License, assets/music.mp3), lowpass 5 kHz, ducked under the voice
by sidechain, fade in 0.5 s / out 1 s, ~-32 LUFS bed. SFX: the graphic cues (work/sfx_45.json) a little louder, plus a
soft swish on every jump cut / punch-in, a riser into the NO ESTIMATE = NO PAY slam and an impact on it.
Master: two-pass loudnorm to -14 LUFS, true peak -1.5 dBTP. Writes work/final_mix.wav."""
import json, re, subprocess
import numpy as np, soundfile as sf
run = lambda *a: subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)
lufs = lambda f: float(re.findall(r"I:\s+(-?[\d.]+) LUFS", subprocess.run(["ffmpeg", "-i", f, "-af", "ebur128=framelog=quiet", "-f", "null", "-"], capture_output=True, text=True).stderr)[-1])
tl = json.load(open("work/timeline.json")); plan = json.load(open("work/plan.json")); DUR = tl["dur"]
cues = [tuple(c) for c in json.load(open("work/sfx_45.json"))]
SFX_GAIN = 1.4
# a soft swish on every cut / punch that has no other cue within 0.25 s
moves = sorted({round(s["vin"], 3) for s in tl["segs"][1:]} | {round(k[0], 3) for k in plan["cam"] if k[0] > 0.1})
for t in moves:
    if not any(abs(t - c[1]) < 0.25 for c in cues): cues.append(("swish", round(t - 0.05, 3), 0.12))
NE = next(c[1] for c in plan["cards"] if c[0] == "noest")
cues += [("riser", round(NE - 0.9, 3), 0.10), ("impact", round(NE + 0.05, 3), 0.16)]
ins, fc = [], []
for k, (name, t, vol) in enumerate(cues):
    ins += ["-i", f"assets/sfx/{name}.wav"]; ms = int(max(0, t) * 1000)
    fc.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo,volume={vol * SFX_GAIN:.4f},adelay={ms}|{ms}[s{k}]")
fc.append("".join(f"[s{k}]" for k in range(len(cues))) + f"amix=inputs={len(cues)}:normalize=0,apad=whole_dur={DUR},atrim=0:{DUR}[o]")
run(*ins, "-filter_complex", ";".join(fc), "-map", "[o]", "work/sfx_stem.wav")

# music bed: lowpassed, set to -24 LUFS, ducked by the voice, then trimmed into a ~-32 LUFS bed
g = -24 - lufs("assets/music.mp3")
run("-t", f"{DUR}", "-i", "assets/music.mp3", "-i", "work/voice_cut.wav", "-filter_complex",
    f"[0:a]aresample=48000,aformat=channel_layouts=stereo,lowpass=f=5000,volume={g:.2f}dB,"
    f"afade=t=in:d=0.5,afade=t=out:st={DUR - 1.0:.2f}:d=1.0[m];"
    "[1:a]aformat=channel_layouts=stereo[sc];[m][sc]sidechaincompress=threshold=0.05:ratio=4:attack=15:release=300:makeup=1[bed]",
    "-map", "[bed]", "work/music_bed_raw.wav")
run("-i", "work/music_bed_raw.wav", "-af", f"volume={-32 - lufs('work/music_bed_raw.wav'):.2f}dB", "work/music_bed.wav")

run("-i", "work/voice_cut.wav", "-i", "work/music_bed.wav", "-i", "work/sfx_stem.wav", "-filter_complex",
    "[0:a][1:a][2:a]amix=inputs=3:normalize=0[m]", "-map", "[m]", "work/mix_raw.wav")
log = subprocess.run(["ffmpeg", "-i", "work/mix_raw.wav", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
m = json.loads(log[log.rfind("{"):log.rfind("}") + 1])
run("-i", "work/mix_raw.wav", "-af", f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
    f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,aresample=48000", "-c:a", "pcm_s16le", "work/final_mix.wav")

v, sr = sf.read("work/voice_cut.wav", always_2d=True); s, _ = sf.read("work/sfx_stem.wav", always_2d=True)
db = lambda x: 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12); W = int(sr * 0.4)
sp = np.median([db(v[i:i + W]) for i in range(0, len(v) - W, W // 2) if db(v[i:i + W]) > -40])
mx = max(db(s[i:i + W]) for i in range(0, len(s) - W, W // 2))
print(f"{len(cues)} sfx cues | loudest SFX {sp - mx:.1f} dB under the voice | voice {lufs('work/voice_cut.wav'):.1f} LUFS, music bed {lufs('work/music_bed.wav'):.1f} LUFS (pre-master)")
r = subprocess.run(["ffmpeg", "-i", "work/final_mix.wav", "-af", "ebur128=peak=true:framelog=quiet", "-f", "null", "-"], capture_output=True, text=True).stderr
print("final mix:", re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1], "LUFS, true peak", re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r)[-1], "dBTP")
