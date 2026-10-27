"""Music bed: Mixkit "Silent Descent" (614, Eugenio Mininni, Mixkit Stock Music Free License) played straight from 0.
Its own arc fits the VSL: quiet and tense for the problem, building from ~45 s, full through the steps and results,
settling from ~128 s for the close. Automation on top: a one-beat dropout on "You're not broken. The system is."
(silence until "So we built a different one", where it slams back +1.5 dB), sidechain-ducked under the voice."""
import re, subprocess
DUR = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "assets/base.mp4"], capture_output=True, text=True).stdout)
DROP, BACK = 51.0, 53.0
g = -14 - float(re.findall(r"I:\s+(-?[\d.]+) LUFS", subprocess.run(["ffmpeg", "-i", "assets/dl/m614.mp3", "-af", "ebur128=framelog=quiet", "-f", "null", "-"],
                                                              capture_output=True, text=True).stderr)[-1])
auto = f"volume='if(between(t,{DROP},{BACK}),0,if(gt(t,{BACK}),1.19,1))':eval=frame"
fc = [f"[0:a]atrim=0:{DUR},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,volume={g:.2f}dB,{auto},"
      f"afade=t=out:st={DUR - 3:.2f}:d=3,apad=whole_dur={DUR},atrim=0:{DUR}[mus]",
      "[1:a]aformat=channel_layouts=stereo[sc]",
      "[mus]volume=0.26[m];[m][sc]sidechaincompress=threshold=0.06:ratio=3:attack=15:release=300:makeup=1[bed]"]
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "assets/dl/m614.mp3", "-i", "assets/vo.wav", "-filter_complex", ";".join(fc), "-map", "[bed]", "assets/music_bed.wav"], check=True)
o = subprocess.run(["ffmpeg", "-i", "assets/music_bed.wav", "-af", "ebur128=framelog=quiet", "-f", "null", "-"], capture_output=True, text=True).stderr
print("bed", re.findall(r"I:\s+(-?[\d.]+) LUFS", o)[-1], "LUFS")
