"""Voice: start from the AI-separated, de-reverbed voice of the source (MelBand-RoFormer vocals + anvuew de-reverb;
the source track has music and SFX baked in), then the brief's chain:
  light FFT denoise (DeepFilterNet / arnndn unavailable: their models download from GitHub, blocked here)
  highpass 90 Hz, lowpass 14 kHz; EQ -3 dB @ 300 Hz, +2.5 dB @ 3.5 kHz, +1.5 dB low shelf @ 100 Hz; de-esser;
  compressor 3:1 @ -20 dB, 5 ms / 80 ms; limiter. No reverb.
Cut with the cut list (room-tone pads + cross-fades over the pads), then:
  work/voice_cut.wav (processed voice on the output timeline, before final loudness)
  out/voice_only_test.wav (voice only, -14 LUFS / -1.5 dBTP)
SFX (synthetic) + final mix are built by mix.py."""
import json, re, subprocess
run = lambda *a: subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)
tl = json.load(open("work/timeline.json"))
CHAIN = ("aresample=48000,afftdn=nr=6:nf=-40:tn=1,highpass=f=90,lowpass=f=14000,"
         "equalizer=f=300:t=q:w=1.2:g=-3,equalizer=f=3500:t=q:w=1.0:g=2.5,lowshelf=f=100:g=1.5,"
         "deesser=i=0.4:m=0.5:f=0.5,"
         "acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=2,"
         "alimiter=limit=0.84:attack=2:release=50:level=false")
run("-i", "/home/user/DEMO/feedfix/voice_kim_dry.wav", "-af", CHAIN, "-ac", "2", "work/voice_proc.wav")

# cut: each piece = source [a-p, b+q]; consecutive pieces cross-fade over their pads (triangular, 6 frames max)
segs = tl["segs"]; ins, fc = [], []
for k, s in enumerate(segs):
    a0, a1 = s["a"] - s["p"], s["b"] + s["q"]
    fc.append(f"[0:a]atrim={a0:.4f}:{a1:.4f},asetpts=PTS-STARTPTS[p{k}]")
cur = "p0"
for k in range(1, len(segs)):
    xf = segs[k - 1]["xf"]
    if xf >= 0.03:
        fc.append(f"[{cur}][p{k}]acrossfade=d={xf:.4f}:c1=tri:c2=tri[x{k}]")
    else:   # no pad available: tiny 5 ms fades, butt-joined
        fc.append(f"[{cur}]afade=t=out:st=0:d=0.005:curve=tri,areverse,afade=t=in:d=0.005,areverse[o{k}];"
                  f"[p{k}]afade=t=in:d=0.005[i{k}];[o{k}][i{k}]concat=n=2:v=0:a=1[x{k}]")
    cur = f"x{k}"
fc.append(f"[{cur}]afade=t=out:st={tl['dur'] - 0.6:.3f}:d=0.15,apad=whole_dur={tl['dur']:.3f},atrim=0:{tl['dur']:.3f}[v]")
run("-i", "work/voice_proc.wav", "-filter_complex", ";".join(fc), "-map", "[v]", "work/voice_cut.wav")

def loudnorm(src, dst):
    log = subprocess.run(["ffmpeg", "-i", src, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = json.loads(log[log.rfind("{"):log.rfind("}") + 1])
    run("-i", src, "-af", f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
        f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,aresample=48000", "-c:a", "pcm_s16le", dst)
loudnorm("work/voice_cut.wav", "out/voice_only_test.wav")
r = subprocess.run(["ffmpeg", "-i", "out/voice_only_test.wav", "-af", "ebur128=peak=true:framelog=quiet", "-f", "null", "-"], capture_output=True, text=True).stderr
print("voice_only_test:", re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1], "LUFS, true peak", re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r)[-1], "dBTP")
print("duration", subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "work/voice_cut.wav"], capture_output=True, text=True).stdout.strip())
