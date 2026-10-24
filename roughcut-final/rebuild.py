"""Re-score the client's re-edit (assets/edit.mp4) with a fresh, continuous music bed.

The re-edit is the v2 render with one section removed (v2 27.467-30.700 s, "But out here ... every spring") and the
end trimmed. Its baked-in audio carries the old music, which now jumps at that cut. So the audio is rebuilt from
stems: the VO (gain only) and the SFX cues of v2, cut exactly like the client's edit, plus a new bed from Mixkit
"Running Out of Time" (77) laid continuously over the new timeline (the only music edit is a bar-length skip
inside the track's quiet breakdown, so the beat never breaks). Picture is copied untouched.
"""
import re, subprocess
run = lambda *a: subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)
R = "../roughcut/"
CUT = (27.467, 30.700)                     # removed from the v2 timeline
DUR = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "assets/edit.mp4"],
                           capture_output=True, text=True).stdout)
V2DUR = 55.947
new = lambda t: t if t < CUT[0] else t - (CUT[1] - CUT[0])

# ---- SFX stem on the v2 timeline from the v2 composition's cue list ----
cues = re.findall(r'<audio id="fx\d+" src="([^"]+)" data-start="([\d.]+)" data-duration="([\d.]+)" data-track-index="\d+" data-volume="([\d.]+)"',
                  open(R + "index.html").read())
ins, fc = [], []
for k, (src, st, du, vol) in enumerate(cues):
    ins += ["-i", R + src]
    ms = int(float(st) * 1000)
    fc.append(f"[{k}:a]atrim=0:{du},aformat=sample_rates=48000:channel_layouts=stereo,volume={vol},adelay={ms}|{ms}[s{k}]")
fc.append("".join(f"[s{k}]" for k in range(len(cues))) + f"amix=inputs={len(cues)}:normalize=0,apad=whole_dur={V2DUR},atrim=0:{V2DUR}[o]")
run(*ins, "-filter_complex", ";".join(fc), "-map", "[o]", "assets/sfx_v2.wav")

# ---- cut VO + SFX stems exactly like the client's edit (10 ms fades at the join) ----
def cut(src, out):
    a, b = CUT
    run("-i", src, "-filter_complex",
        f"[0:a]atrim=0:{a},asetpts=PTS-STARTPTS,afade=t=out:st={a - 0.01}:d=0.01[x];"
        f"[0:a]atrim={b},asetpts=PTS-STARTPTS,afade=t=in:d=0.01[y];[x][y]concat=n=2:v=0:a=1,atrim=0:{DUR}[o]", "-map", "[o]", out)
cut(R + "assets/vo.wav", "assets/vo_edit.wav")
cut("assets/sfx_v2.wav", "assets/sfx_edit.wav")

# ---- new music bed on the new timeline ----
BEAT = 0.4644                                  # 129.2 bpm
OFF1 = 20.036                                  # new t -> track t + OFF1: slam (14.80) on a beat, breakdown (47.3) at the cut
JUMP_AT, JUMP = 31.0, 8 * BEAT                 # skip 2 bars inside the breakdown so the full section returns on "Pinecrest"
SLAM, LIFT, DARK, WARM, HIT = 14.80, (23.25, 27.26), (27.467, new(40.25)), new(40.25), new(54.93)
g = -14 - float(re.findall(r"I:\s+(-?[\d.]+) LUFS", subprocess.run(["ffmpeg", "-ss", "35", "-t", "20", "-i", "assets/m77.mp3", "-af",
                "ebur128=framelog=quiet", "-f", "null", "-"], capture_output=True, text=True).stderr)[-1])
x = 0.04                                       # crossfade at the in-track skip
p1 = f"[0:a]atrim={OFF1}:{OFF1 + JUMP_AT + x},asetpts=PTS-STARTPTS[p1]"
p2 = f"[0:a]atrim={OFF1 + JUMP_AT + JUMP}:{OFF1 + JUMP + DUR + 1},asetpts=PTS-STARTPTS[p2]"
auto = (f"lowpass=f=700:enable='lt(t,14.2)',lowpass=f=1600:enable='between(t,{DARK[0]},{DARK[1]})',"
        f"volume='if(lt(t,14.2),0.8,if(lt(t,{SLAM}),0,if(between(t,{LIFT[0]},{LIFT[1]}),1.19,1)))':eval=frame")
fc = [p1, p2, f"[p1][p2]acrossfade=d={x}:c1=tri:c2=tri,aresample=48000,aformat=channel_layouts=stereo,volume={g:.2f}dB,{auto},"
      f"afade=t=out:st={HIT + 0.15:.3f}:d={DUR - HIT - 0.15:.3f},apad=whole_dur={DUR},atrim=0:{DUR}[mus]",
      "[1:a]aformat=channel_layouts=stereo[sc]",
      "[mus]volume=0.24[m];[m][sc]sidechaincompress=threshold=0.08:ratio=2.5:attack=15:release=250:makeup=1[bed]"]
run("-i", "assets/m77.mp3", "-i", "assets/vo_edit.wav", "-filter_complex", ";".join(fc), "-map", "[bed]", "-ar", "48000", "assets/music_edit.wav")

# ---- mix, level to -14 LUFS (2-pass linear), mux with the untouched picture ----
mix = "[0:a][1:a][2:a]amix=inputs=3:normalize=0,alimiter=limit=0.89:level=false"
log = subprocess.run(["ffmpeg", "-i", "assets/vo_edit.wav", "-i", "assets/sfx_edit.wav", "-i", "assets/music_edit.wav", "-filter_complex",
                      f"{mix},loudnorm=I=-14:TP=-1:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
gain = -14 - float(re.findall(r'"input_i" : "(-?[\d.]+)"', log)[0])
run("-i", "assets/vo_edit.wav", "-i", "assets/sfx_edit.wav", "-i", "assets/music_edit.wav", "-filter_complex",
    f"[0:a][1:a][2:a]amix=inputs=3:normalize=0,volume={gain:.2f}dB,alimiter=limit=0.84:level=false[a]", "-map", "[a]", "assets/mix.wav")
run("-i", "assets/edit.mp4", "-i", "assets/mix.wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
    "-movflags", "+faststart", "-shortest", "../pinecrest-roughcut-9x16-v3.mp4")
print(len(cues), "sfx cues; mix gain", round(gain, 2), "dB")
