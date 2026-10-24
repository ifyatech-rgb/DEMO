"""Voice cleanup + music bed for the rough-cut ad. Never re-times anything: the VO keeps every sample position.

  assets/vo.wav         VO from the rough cut: highpass, light denoise, gentle compression, loudnorm -14 LUFS (2-pass)
  assets/music_bed.wav  mood-mapped bed from Mixkit tracks, cut on beats, ducked under the VO (sidechain)
Mood map (ad time -> source):
  0.00-14.20  tense hook       Epical Drums 01 (676)
  14.20-14.80 one-beat dropout (silence) before "But from up here"
  14.80-23.25 slams back in    Driving Ambition (32) from its downbeat at 37.84 s, on the whip's white flash
  23.25-27.53 lift             Driving Ambition from its fuller section (61.99 s)
  27.53-40.30 dark + tense     Epical Drums 06 (686), low-passed, a touch quieter
  40.30-end   warm, building   Driving Ambition, aligned so its last build beat (86.13 s) lands on "free" (54.93 s)
"""
import json, os, re, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
DUR = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "assets/source.mp4"],
                           capture_output=True, text=True).stdout)
run = lambda *a: subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)

# ---- VO ----
pre = "highpass=f=80,afftdn=nr=6:nf=-50,equalizer=f=250:t=q:w=1:g=-1.5,equalizer=f=3500:t=q:w=1.2:g=1.5,acompressor=threshold=-18dB:ratio=2.5:attack=6:release=90:makeup=1.5"
log = subprocess.run(["ffmpeg", "-i", "assets/source.mp4", "-af", f"{pre},loudnorm=I=-14:TP=-1.5:LRA=7:print_format=json", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
m = json.loads(log[log.rfind("{"):log.rfind("}") + 1])
ln = (f"loudnorm=I=-14:TP=-1.5:LRA=7:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
      f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
run("-i", "assets/source.mp4", "-vn", "-af", f"{pre},{ln},aresample=48000", "-ac", "2", "assets/vo.wav")

# ---- music sections: (src, src_start, ad_start, ad_end, extra filter, gain dB) ----
D = "assets/dl/"
SECS = [(D + "m676.mp3", 10.0, 0.0, 14.20, "", 0),
        (D + "m32.mp3", 37.84, 14.80, 23.25, "", 0),
        (D + "m32.mp3", 61.99, 23.25, 27.53, "", 1.0),
        (D + "m686.mp3", 20.0, 27.53, 40.30, "lowpass=f=1400,", -1.5),
        (D + "m32.mp3", 86.13 - (54.93 - 40.30), 40.30, DUR, "", 0.5)]
def lufs(src, s0, d, extra):
    o = subprocess.run(["ffmpeg", "-ss", f"{s0}", "-t", f"{d}", "-i", src, "-af", f"{extra}ebur128=framelog=quiet", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", o)[-1])
ins, fc = [], []
for k, (src, s0, a0, a1, extra, g) in enumerate(SECS):
    d = a1 - a0
    g += -14 - lufs(src, s0, d, extra)          # static gain to -14 LUFS per section (no pumping)
    ins += ["-i", src]
    fade_out = f"afade=t=out:st={d - 0.03:.3f}:d=0.03" if k < len(SECS) - 1 else f"afade=t=out:st={54.93 - a0 + 0.6:.3f}:d={DUR - 54.93 - 0.6:.3f}"
    fc.append(f"[{k}:a]atrim={s0:.3f}:{s0 + d:.3f},asetpts=PTS-STARTPTS,{extra}volume={g:.2f}dB,aresample=48000,"
              f"aformat=channel_layouts=stereo,afade=t=in:d=0.02,{fade_out},adelay={int(a0 * 1000)}|{int(a0 * 1000)},apad=whole_dur={DUR:.3f}[m{k}]")
fc.append("".join(f"[m{k}]" for k in range(len(SECS))) + f"amix=inputs={len(SECS)}:normalize=0,atrim=0:{DUR:.3f}[mus]")
# Duck under the voice: base bed at ~24 % (about 15 % once ducked), sidechain pulls it ~4 dB further down while he talks.
fc.append(f"[{len(SECS)}:a]aformat=channel_layouts=stereo[sc]")
fc.append("[mus]volume=0.24[m15];[m15][sc]sidechaincompress=threshold=0.08:ratio=2.5:attack=15:release=250:makeup=1[bed]")
run(*ins, "-i", "assets/vo.wav", "-filter_complex", ";".join(fc), "-map", "[bed]", "-ar", "48000", "assets/music_bed.wav")
for f in ("assets/vo.wav", "assets/music_bed.wav"):
    o = subprocess.run(["ffmpeg", "-i", f, "-af", "ebur128=framelog=quiet", "-f", "null", "-"], capture_output=True, text=True).stderr
    print(f, re.findall(r"I:\s+(-?[\d.]+) LUFS", o)[-1], "LUFS")
