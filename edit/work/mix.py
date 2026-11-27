"""Final audio: processed voice (work/voice_cut.wav) + synthetic SFX cues (work/sfx_45.json; same timings in both
formats), no music (no ./assets/music.mp3 supplied). Two-pass loudnorm to -14 LUFS, true peak -1.5 dBTP.
Writes work/final_mix.wav and prints the SFX level relative to the voice."""
import json, re, subprocess
import numpy as np, soundfile as sf
run = lambda *a: subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)
tl = json.load(open("work/timeline.json")); DUR = tl["dur"]
cues = json.load(open("work/sfx_45.json"))
SFX_GAIN = 0.8
ins, fc = [], []
for k, (name, t, vol) in enumerate(cues):
    ins += ["-i", f"assets/sfx/{name}.wav"]; ms = int(t * 1000)
    fc.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo,volume={vol * SFX_GAIN:.4f},adelay={ms}|{ms}[s{k}]")
fc.append("".join(f"[s{k}]" for k in range(len(cues))) + f"amix=inputs={len(cues)}:normalize=0,apad=whole_dur={DUR},atrim=0:{DUR}[o]")
run(*ins, "-filter_complex", ";".join(fc), "-map", "[o]", "work/sfx_stem.wav")
run("-i", "work/voice_cut.wav", "-i", "work/sfx_stem.wav", "-filter_complex", "[0:a][1:a]amix=inputs=2:normalize=0[m]", "-map", "[m]", "work/mix_raw.wav")
log = subprocess.run(["ffmpeg", "-i", "work/mix_raw.wav", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
m = json.loads(log[log.rfind("{"):log.rfind("}") + 1])
run("-i", "work/mix_raw.wav", "-af", f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
    f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,aresample=48000", "-c:a", "pcm_s16le", "work/final_mix.wav")
v, sr = sf.read("work/voice_cut.wav", always_2d=True); s, _ = sf.read("work/sfx_stem.wav", always_2d=True)
db = lambda x: 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)
W = sr // 2.5; W = int(W)
sp = [db(v[i:i + W]) for i in range(0, len(v) - W, W // 2) if db(v[i:i + W]) > -40]
sx = [(i / sr, db(s[i:i + W])) for i in range(0, len(s) - W, W // 2)]
print(f"cues {len(cues)} | speech level (median 400 ms) {np.median(sp):.1f} dB | loudest SFX window {max(x for _, x in sx):.1f} dB at {max(sx, key=lambda z: z[1])[0]:.2f}s "
      f"-> {np.median(sp) - max(x for _, x in sx):.1f} dB under the voice")
r = subprocess.run(["ffmpeg", "-i", "work/final_mix.wav", "-af", "ebur128=peak=true:framelog=quiet", "-f", "null", "-"], capture_output=True, text=True).stderr
print("final mix:", re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1], "LUFS, true peak", re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r)[-1], "dBTP")
