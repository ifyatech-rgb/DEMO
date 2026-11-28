"""Audio, timing untouched (same start, same length as the source).
Voice: the source track has the old edit's music + SFX baked in, so the voice is first separated and de-reverbed
(MelBand-RoFormer vocals + anvuew de-reverb, ../feedfix/voice_kim_dry.wav); DeepFilterNet / arnndn are unavailable
here (models download from GitHub, blocked), so the brief's last fallback afftdn=nr=12:nf=-30 runs next, then:
HP 90 / LP 14k, EQ -3 dB @ 300 Hz, +2.5 dB @ 3.5 kHz, +1.5 dB shelf @ 100 Hz, de-esser, 3:1 @ -20 dB 5/80 ms, limiter,
loudnorm -14 LUFS / -1.5 dBTP.  -> out/voice_only_test.wav
Music: assets/music.mp3 (lowpass 5 kHz, sidechain-ducked, ~-26 dB under the voice, fade in 0.5 s / out 1 s).
SFX: synthetic cues from work/sfx.json, ~-18 dB under the voice.  -> work/final_mix.wav"""
import json, re, subprocess
import numpy as np, soundfile as sf
run = lambda *a: subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)
lufs = lambda f: float(re.findall(r"I:\s+(-?[\d.]+) LUFS", subprocess.run(["ffmpeg", "-i", f, "-af", "ebur128=framelog=quiet", "-f", "null", "-"], capture_output=True, text=True).stderr)[-1])
DUR = 39.3
def loudnorm(src, dst):
    log = subprocess.run(["ffmpeg", "-i", src, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = json.loads(log[log.rfind("{"):log.rfind("}") + 1])
    run("-i", src, "-af", f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
        f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,aresample=48000", "-c:a", "pcm_s16le", dst)
CHAIN = ("aresample=48000,afftdn=nr=12:nf=-30,highpass=f=90,lowpass=f=14000,"
         "equalizer=f=300:t=q:w=1.2:g=-3,equalizer=f=3500:t=q:w=1.0:g=2.5,lowshelf=f=100:g=1.5,deesser=i=0.4:m=0.5:f=0.5,"
         "acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=2,alimiter=limit=0.84:attack=2:release=50:level=false,"
         f"apad=whole_dur={DUR},atrim=0:{DUR}")
run("-i", "../feedfix/voice_kim_dry.wav", "-af", CHAIN, "-ac", "2", "work/voice_proc.wav")
loudnorm("work/voice_proc.wav", "out/voice_only_test.wav")

cues = json.load(open("work/sfx.json")); SFX = "../edit/assets/sfx"
ins, fc = [], []
for k, (name, t, vol) in enumerate(cues):
    ins += ["-i", f"{SFX}/{name}.wav"]; ms = int(t * 1000)
    fc.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo,volume={vol:.4f},adelay={ms}|{ms}[s{k}]")
fc.append("".join(f"[s{k}]" for k in range(len(cues))) + f"amix=inputs={len(cues)}:normalize=0,apad=whole_dur={DUR},atrim=0:{DUR}[o]")
run(*ins, "-filter_complex", ";".join(fc), "-map", "[o]", "work/sfx_raw.wav")
V = lufs("out/voice_only_test.wav")
# SFX: loudest 400 ms window ~18 dB under the median speech level
v, sr = sf.read("out/voice_only_test.wav", always_2d=True); s, _ = sf.read("work/sfx_raw.wav", always_2d=True)
db = lambda x: 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12); W = int(sr * 0.4)
sp = float(np.median([db(v[i:i + W]) for i in range(0, len(v) - W, W // 2) if db(v[i:i + W]) > -40]))
mx = max(db(s[i:i + W]) for i in range(0, len(s) - W, W // 2))
run("-i", "work/sfx_raw.wav", "-af", f"volume={sp - 18 - mx:.2f}dB", "work/sfx_stem.wav")
g = -14 - lufs("assets/music.mp3")
run("-t", f"{DUR}", "-i", "assets/music.mp3", "-i", "out/voice_only_test.wav", "-filter_complex",
    f"[0:a]aresample=48000,aformat=channel_layouts=stereo,lowpass=f=5000,volume={g:.2f}dB,afade=t=in:d=0.5,afade=t=out:st={DUR - 1:.2f}:d=1[m];"
    "[1:a]aformat=channel_layouts=stereo[sc];[m][sc]sidechaincompress=threshold=0.05:ratio=4:attack=15:release=300:makeup=1[bed]", "-map", "[bed]", "work/music_raw.wav")
run("-i", "work/music_raw.wav", "-af", f"volume={V - 26 - lufs('work/music_raw.wav'):.2f}dB", "work/music_bed.wav")
run("-i", "out/voice_only_test.wav", "-i", "work/music_bed.wav", "-i", "work/sfx_stem.wav", "-filter_complex", "[0:a][1:a][2:a]amix=inputs=3:normalize=0[m]",
    "-map", "[m]", "work/mix_raw.wav")
loudnorm("work/mix_raw.wav", "work/final_mix.wav")
print(f"voice {V:.1f} LUFS | music bed {lufs('work/music_bed.wav'):.1f} LUFS ({lufs('work/music_bed.wav') - V:.1f} dB) | loudest SFX {sp - 18:.1f} dB vs speech {sp:.1f} | final {lufs('work/final_mix.wav'):.1f} LUFS")
