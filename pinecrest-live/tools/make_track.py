"""Synthesize an original, royalty-free driving music bed whose mood follows the ad's sections.

Usage: make_track.py OUT.wav DURATION SECTIONS_JSON
SECTIONS_JSON: [[start, mood], ...] with mood in tense | drop | lift | dark | warm | build.
"""
import json, sys, wave
import numpy as np

SR = 44100
out, DUR, secs = sys.argv[1], float(sys.argv[2]), json.loads(sys.argv[3])
N = int(DUR * SR); L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(3)
BPM = 110; beat = 60 / BPM; bar = 4 * beat

def midi(m): return 440 * 2 ** ((m - 69) / 12)
def add(sig, t, g=1.0, pan=0.0):
    i = int(t * SR); j = min(N, i + len(sig))
    if i >= N or j <= i: return
    s = sig[: j - i] * g; L[i:j] += s * (1 - max(pan, 0)); R[i:j] += s * (1 + min(pan, 0))
def tt(d): return np.arange(int(d * SR)) / SR
def env(d, a, k): t = tt(d); return np.minimum(1, t / a) * np.exp(-t * k)
def saw(f, d, a=0.005, k=6, harm=8):
    t = tt(d); return sum(np.sin(2 * np.pi * f * h * t) / h for h in range(1, harm)) * env(d, a, k)
def sine(f, d, a=0.005, k=6): return np.sin(2 * np.pi * f * tt(d)) * env(d, a, k)
def pad(notes, d, bright=0.4):
    t = tt(d); s = sum(np.sin(2 * np.pi * midi(m) * 2 ** (det / 12) * h * t) / h ** (2.3 - bright)
                       for m in notes for det in (-0.07, 0, 0.06) for h in range(1, 5))
    return s * np.minimum(1, t / 0.4) * np.minimum(1, (d - t) / 0.4) / (3 * len(notes))
def kick(): t = tt(0.4); return np.sin(2 * np.pi * np.cumsum(48 + 110 * np.exp(-t * 30)) / SR) * np.exp(-t * 8)
def snare(): t = tt(0.3); return (rng.standard_normal(len(t)) * 0.7 + np.sin(2 * np.pi * 190 * t)) * np.exp(-t * 18)
def hat(k=60): x = rng.standard_normal(int(0.08 * SR)); return np.diff(x, prepend=0) * env(0.08, 0.001, k)
def tom(f): t = tt(0.5); return np.sin(2 * np.pi * np.cumsum(f * (1 + 0.6 * np.exp(-t * 20))) / SR) * np.exp(-t * 7)

MINOR = [[45, 52, 57, 60], [41, 48, 53, 57], [43, 50, 55, 59], [40, 47, 52, 56]]   # Am F G E
MAJOR = [[48, 55, 60, 64], [43, 50, 55, 62], [45, 52, 57, 64], [41, 48, 53, 60]]   # C G Am F
def mood_at(t):
    m = secs[0][1]
    for s, mm in secs:
        if t >= s: m = mm
    return m

t, b = 0.0, 0
while t < DUR:
    m = mood_at(t)
    if m == "drop": t += beat; continue
    ch = (MINOR if m in ("tense", "dark") else MAJOR)[b % 4]
    lvl = {"tense": 0.85, "dark": 0.7, "lift": 0.9, "warm": 0.95, "build": 1.0}[m]
    add(pad(ch, beat * 4 + 0.4, 0.25 if m == "dark" else 0.45), t, 0.32 * lvl)
    for q in range(4):
        bt = t + q * beat
        if bt >= DUR or mood_at(bt) == "drop": continue
        mq = mood_at(bt)
        add(kick(), bt, 0.9 * lvl)
        for e in range(2):   # driving eighth-note bass
            add(saw(midi(ch[0] - 12), beat / 2, 0.004, 9), bt + e * beat / 2, 0.16 * lvl)
            add(sine(midi(ch[0] - 24), beat / 2, 0.004, 7), bt + e * beat / 2, 0.45 * lvl)
        if mq in ("tense", "lift", "warm", "build"): add(hat(), bt + beat / 2, 0.28 * lvl, 0.3)
        if mq in ("warm", "build", "lift"):
            add(hat(120), bt + beat / 4, 0.12, -0.3); add(hat(120), bt + 3 * beat / 4, 0.12, -0.3)
            if q in (1, 3): add(snare(), bt, 0.35 * lvl)
            arp = ch + [ch[1] + 12]
            for e in range(2): add(sine(midi(arp[(q * 2 + e) % 5] + 12), beat / 2, 0.002, 10), bt + e * beat / 2, 0.11, 0.35 if e else -0.35)
        if mq == "tense" and q == 3: add(tom(110), bt + beat / 2, 0.35)
        if mq == "dark" and q in (1, 3): add(tom(70), bt, 0.4)
        if mq == "build": add(hat(200), bt + beat / 8, 0.08)
    t += bar if all(mood_at(t + x) != "drop" for x in (0, bar - 0.01)) else beat
    b += 1

# Build: rising filtered noise in the last section.
for s, m in secs:
    if m == "build":
        n = int((DUR - s) * SR); x = np.diff(rng.standard_normal(n), prepend=0) * np.linspace(0, 0.08, n); add(x, s)
st = np.stack([L, R], 1)
fade = int(0.6 * SR); st[-fade:] *= np.linspace(1, 0, fade)[:, None]
st = np.tanh(st * 1.3); st /= np.abs(st).max() / 0.9
with wave.open(out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype("<i2").tobytes())
print("track", DUR)
