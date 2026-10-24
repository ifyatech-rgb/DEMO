"""Voice levelling + music bed for the rough-cut ad. Never re-times anything: the VO keeps every sample position.

  assets/vo.wav         the client's VO, untouched apart from one linear gain to -14 LUFS (no denoise, EQ or compression)
  assets/music_bed.wav  ONE continuous track, Mixkit "Running Out of Time" (77), ad t -> track t + 20.5 s, ducked under the VO.
Mood map is done on that single track (no stitching between songs):
  0.00-14.20  tense hook       muffled (low-pass), slightly lower
  14.20-14.80 one-beat dropout (silence) before "But from up here"
  14.80       slams back in    full band, on the whip's white flash (track 35.3 s, on the beat)
  23.25-27.53 lift             +1.5 dB on "The good news is"
  27.53-40.25 dark + tense     the track's own breakdown (47.4-60.75 s) plus a low-pass
  40.25-end   warm, building   the full section returns on "Pinecrest Roofing" (track 60.75 s)
  54.93       last hit         music rings out over "free inspection" and fades
"""
import json, os, re, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
DUR = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "assets/source.mp4"],
                           capture_output=True, text=True).stdout)
run = lambda *a: subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)

# ---- VO ----
pre = "anull"
log = subprocess.run(["ffmpeg", "-i", "assets/source.mp4", "-af", f"{pre},loudnorm=I=-14:TP=-1.5:LRA=7:print_format=json", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
m = json.loads(log[log.rfind("{"):log.rfind("}") + 1])
ln = (f"loudnorm=I=-14:TP=-1.5:LRA=7:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
      f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
run("-i", "assets/source.mp4", "-vn", "-af", f"{pre},{ln},aresample=48000", "-ac", "2", "assets/vo.wav")

# ---- music: one track, automated ----
OFF, END_HIT = 20.5, 54.93
lp_vol = (f"lowpass=f=700:enable='lt(t,14.2)',lowpass=f=1600:enable='between(t,27.53,40.25)',"
          f"volume='if(lt(t,14.2),0.8,if(lt(t,14.8),0,if(between(t,23.25,27.53),1.19,1)))':eval=frame")
g = -14 - float(re.findall(r"I:\s+(-?[\d.]+) LUFS", subprocess.run(["ffmpeg", "-ss", f"{OFF + 15}", "-t", "20", "-i", "assets/dl/m77.mp3",
    "-af", "ebur128=framelog=quiet", "-f", "null", "-"], capture_output=True, text=True).stderr)[-1])
ins = ["-ss", f"{OFF}", "-t", f"{DUR}", "-i", "assets/dl/m77.mp3"]
fc = [f"[0:a]asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,volume={g:.2f}dB,{lp_vol},"
      f"afade=t=out:st={END_HIT + 0.15:.3f}:d={DUR - END_HIT - 0.15:.3f},apad=whole_dur={DUR:.3f},atrim=0:{DUR:.3f}[mus]"]
fc.append("[1:a]aformat=channel_layouts=stereo[sc]")
fc.append("[mus]volume=0.24[m15];[m15][sc]sidechaincompress=threshold=0.08:ratio=2.5:attack=15:release=250:makeup=1[bed]")
run(*ins, "-i", "assets/vo.wav", "-filter_complex", ";".join(fc), "-map", "[bed]", "-ar", "48000", "assets/music_bed.wav")
for f in ("assets/vo.wav", "assets/music_bed.wav"):
    o = subprocess.run(["ffmpeg", "-i", f, "-af", "ebur128=framelog=quiet", "-f", "null", "-"], capture_output=True, text=True).stderr
    print(f, re.findall(r"I:\s+(-?[\d.]+) LUFS", o)[-1], "LUFS")
