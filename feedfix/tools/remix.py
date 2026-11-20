"""Lower the music under the voice: steady bed -8 dB, short hits that jump above the bed (SFX) only ~-3 dB.
Usage: remix.py VOICE.wav REST.wav OUT.wav"""
import sys, numpy as np, soundfile as sf
from scipy.ndimage import median_filter
v, sr = sf.read(sys.argv[1], dtype="float32", always_2d=True); r, _ = sf.read(sys.argv[2], dtype="float32", always_2d=True)
H = sr // 50                                                   # 20 ms frames
n = len(r) // H
env = np.sqrt((r[: n * H] ** 2).mean(1).reshape(n, H).mean(1) + 1e-12)
bed = median_filter(env, size=100, mode="nearest")             # 2 s running median = the music bed
ratio = env / (bed + 1e-9)
gdb = np.interp(ratio, [1.6, 4.0], [-8.0, -3.0])               # steady music -8 dB, hits above the bed ease up to -3 dB
# smooth: fast attack (hits keep their front), slower release
g = np.empty_like(gdb); g[0] = gdb[0]
for i in range(1, n):
    a = 0.6 if gdb[i] > g[i - 1] else 0.12
    g[i] = g[i - 1] + a * (gdb[i] - g[i - 1])
gain = np.repeat(10 ** (g / 20), H)
gain = np.concatenate([gain, np.full(len(r) - len(gain), gain[-1])])[:, None]
sf.write(sys.argv[3], v + r * gain, sr)
print("music bed lowered; average gain %.1f dB" % g.mean())
