"""Estimate tempo and beat phase of an audio file (onset envelope + autocorrelation). Usage: beats.py FILE [START DUR]"""
import subprocess, sys, numpy as np
f = sys.argv[1]; ss = sys.argv[2] if len(sys.argv) > 2 else "0"; dur = sys.argv[3] if len(sys.argv) > 3 else "60"
SR, HOP = 22050, 256
raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", ss, "-t", dur, "-i", f, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
x = np.frombuffer(raw, np.float32)
fr = np.lib.stride_tricks.sliding_window_view(x, 1024)[::HOP] * np.hanning(1024)
mag = np.log1p(np.abs(np.fft.rfft(fr, axis=1)) * 10)
onset = np.maximum(0, np.diff(mag, axis=0)).sum(1); onset -= onset.mean()
fps = SR / HOP
ac = np.correlate(onset, onset, "full")[len(onset) - 1:]
lags = np.arange(len(ac)); bpm_l = 60 * fps / np.maximum(lags, 1)
ok = (bpm_l > 70) & (bpm_l < 180)
lag = lags[ok][np.argmax(ac[ok])]; bpm = 60 * fps / lag
ph = max(range(int(lag)), key=lambda p: onset[p::int(lag)].sum())
print(f"bpm {bpm:.2f}  beat period {lag / fps:.4f}s  first beat {float(ss) + ph / fps:.3f}s")
