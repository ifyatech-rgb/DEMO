"""Exports A/B (+ the D voice test already written) and the QA checks from step 11. Writes logs/qa.json."""
import json, re, subprocess
import numpy as np, soundfile as sf
run = lambda *a: subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)
tl = json.load(open("work/timeline.json")); plan = json.load(open("work/plan.json")); DUR = tl["dur"]
EXPORTS = {"ad1_feed_4x5_1080x1350.mp4": "work/overlay_45.mp4", "ad1_reels_9x16_1080x1920.mp4": "work/overlay_916.mp4"}
for out, src in EXPORTS.items():
    run("-i", src, "-i", "work/final_mix.wav", "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-profile:v", "high", "-crf", "17", "-preset", "slow",
        "-r", "30", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", "-t", f"{DUR:.3f}", f"out/{out}")
qa = {}
for out in list(EXPORTS) + ["voice_only_test.wav"]:
    p = f"out/{out}"
    pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,codec_name,profile,width,height,r_frame_rate,pix_fmt,sample_rate,bit_rate:format=duration",
                                    "-of", "json", p], capture_output=True, text=True).stdout)
    r = subprocess.run(["ffmpeg", "-i", p, "-af", "ebur128=peak=true:framelog=quiet", "-f", "null", "-"], capture_output=True, text=True).stderr
    I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1]); TP = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r)[-1])
    qa[out] = {"duration": float(pr["format"]["duration"]), "streams": pr["streams"], "lufs": I, "true_peak": TP,
               "loudness_pass": abs(I + 14) <= 0.5 and TP < -1.0}
# contact sheets: one frame per second
for out, tag in (("ad1_feed_4x5_1080x1350.mp4", "45"), ("ad1_reels_9x16_1080x1920.mp4", "916")):
    w = 216
    run("-i", f"out/{out}", "-vf", f"fps=1,scale={w}:-1,drawtext=text='%{{pts\\:hms}}':x=6:y=6:fontsize=18:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=7x4",
        "-frames:v", "1", f"logs/contact_{tag}.png")
# clicks at every audio joint: max sample-to-sample jump around each joint vs the voice's own typical max jump
x, sr = sf.read("work/final_mix.wav", always_2d=True); m = x.mean(1)
d = np.abs(np.diff(m)); ref = np.percentile(d, 99.9)
joints = []
for k, s in enumerate(tl["segs"][1:], 1):
    t0 = s["T"]; t1 = s["T"] + tl["segs"][k - 1]["xf"]
    a, b = int((t0 - 0.02) * sr), int((t1 + 0.02) * sr)
    joints.append({"t": round(t0, 3), "max_jump_vs_p99.9": round(float(d[a:b].max() / ref), 2)})
qa["joints"] = joints; qa["clicks_pass"] = all(j["max_jump_vs_p99.9"] < 1.5 for j in joints)
# first spoken word and the longest unchanged shot
qa["first_word_s"] = tl["words"][0]["t"]
events = sorted({0.0, DUR} | {round(s["vin"], 3) for s in tl["segs"]} | {round(k[0], 3) for k in plan["cam"]}
                | {round(c[1], 3) for c in plan["cards"]} | {round(c[2], 3) for c in plan["cards"]})
qa["longest_static_s"] = round(max(b - a for a, b in zip(events, events[1:])), 2)
qa["runtime_s"] = DUR
json.dump(qa, open("logs/qa.json", "w"), indent=1)
for k, v in qa.items():
    if isinstance(v, dict): print(k, {kk: vv for kk, vv in v.items() if kk != "streams"})
print("first word", qa["first_word_s"], "| longest static", qa["longest_static_s"], "| clicks pass", qa["clicks_pass"], "| runtime", DUR)
print("joints", joints)
