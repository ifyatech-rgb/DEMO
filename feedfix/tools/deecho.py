"""Remove a fixed slap-back echo (x = s + a*s[n-D]) from the voice by inverse filtering y[n] = x[n] - a*y[n-D].
D is found from the cepstrum, a by a grid search that minimises the echo's cepstral peak.
Usage: deecho.py IN.wav OUT.wav"""
import sys, numpy as np, soundfile as sf
from scipy.signal import lfilter
x2, sr = sf.read(sys.argv[1], dtype="float64", always_2d=True)
def cep(x):
    L = sr * 4; acc = None
    for s in range(0, len(x) - L, L):
        X = np.fft.rfft(x[s:s + L] * np.hanning(L)); c = np.fft.irfft(np.log(np.abs(X) + 1e-9))
        acc = np.abs(c) if acc is None else acc + np.abs(c)
    return acc
mono = x2.mean(1)
c = cep(mono); lo, hi = int(0.03 * sr), int(0.05 * sr)
D = lo + int(np.argmax(c[lo:hi]))
def peak(y):
    cc = cep(y); return cc[D - 2:D + 3].max() / np.median(cc[int(0.012 * sr):int(0.4 * sr)])
def apply(x, a, D):
    den = np.zeros(D + 1); den[0] = 1; den[D] = a
    return lfilter([1.0], den, x)
best = min(((peak(apply(mono, a, D)), a) for a in np.arange(-0.8, 0.8, 0.05)))
a = best[1]
for fine in np.arange(a - 0.05, a + 0.05, 0.01):
    p = peak(apply(mono, fine, D))
    if p < best[0]: best = (p, fine)
p0, a = peak(mono), best[1]
print(f"echo delay {D / sr * 1000:.2f} ms ({D} samples), strength a = {a:.2f}; echo peak {p0:.1f}x -> {best[0]:.1f}x")
y = np.stack([apply(x2[:, ch], a, D) for ch in range(x2.shape[1])], 1)
sf.write(sys.argv[2], y.astype(np.float32), sr)
