"""Synthesize an original, royalty-free cinematic score that follows the VSL's sections.

Usage: make_score.py OUT.wav DURATION DROP LIFT BUILD PEAK SETTLE
  0..DROP      tense, low (A minor drone, heartbeat pulse, sparse low piano)
  DROP..LIFT   music drops out (a short reverse swell in its last 0.6 s leads into LIFT)
  LIFT..BUILD  warm lift (C major pads, soft kick)
  BUILD..PEAK  builds (hats, claps, arpeggio, more drive)
  PEAK..SETTLE fullest
  SETTLE..end  settles (pads + soft piano), fades out
"""
import sys, wave
import numpy as np

SR = 44100
out_path = sys.argv[1]
DUR, DROP, LIFT, BUILD, PEAK, SETTLE = map(float, sys.argv[2:8])
N = int(DUR * SR); L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(11)
BPM = 96; beat = 60 / BPM

def midi(m): return 440 * 2 ** ((m - 69) / 12)
def add(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR); j = min(N, i + len(sig))
    if i >= N or j <= i: return
    s = sig[: j - i] * gain
    L[i:j] += s * (1 - max(pan, 0)); R[i:j] += s * (1 + min(pan, 0))
def env(n, a, d, sus=0.0):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * (sus + (1 - sus) * np.exp(-t / d))
def lowpass(x, fc):
    a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); acc = 0.0
    for k in range(len(x)): acc = (1 - a) * x[k] + a * acc; y[k] = acc
    return y
def pad(notes, length, bright=0.5):
    n = int(length * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for m in notes:
        for det in (-0.08, 0.0, 0.07):
            f = midi(m) * 2 ** (det / 12)
            s += sum(np.sin(2 * np.pi * f * h * t + h) / h ** (2.2 - bright) for h in range(1, 6))
    fade = np.minimum(1, t / 0.9) * np.minimum(1, (length - t) / 0.9)
    return s * fade / (len(notes) * 3)
def piano(m, length=2.0):
    n = int(length * SR); t = np.arange(n) / SR; f = midi(m)
    s = sum(np.sin(2 * np.pi * f * h * t) * np.exp(-t * (1.5 + h * 0.8)) / h for h in range(1, 7))
    return s * np.minimum(1, t / 0.004)
def kick(g=1.0):
    n = int(0.4 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * np.cumsum(45 + 70 * np.exp(-t * 28)) / SR) * np.exp(-t * 8) * g
def noise_hit(length, d, hp=True):
    n = int(length * SR); x = rng.standard_normal(n)
    if hp: x = np.diff(x, prepend=0)
    return x * env(n, 0.001, d)
def pulse(m, length):  # soft sub "heartbeat"
    n = int(length * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * midi(m) * t) * env(n, 0.01, 0.18)

bar = 4 * beat
MINOR = [[45, 52, 57, 60], [41, 48, 53, 57], [45, 52, 57, 60], [40, 47, 52, 56]]   # Am F Am E
MAJOR = [[48, 55, 60, 64], [43, 50, 55, 59], [45, 52, 57, 60], [41, 48, 53, 57]]   # C G Am F

# Problem section: drone + heartbeat + sparse low piano, slowly opening.
t, b = 0.0, 0
while t < DROP - 0.05:
    ln = min(2 * bar, DROP - t)
    prog = t / DROP
    add(pad([c - 12 for c in MINOR[b % 4][:2]] + MINOR[b % 4][2:3], ln + 0.8, 0.2 + 0.4 * prog), t, 0.55)
    k = 0.0
    while k < ln - 0.01:
        add(pulse(MINOR[b % 4][0] - 12, 0.5), t + k, 0.55); add(pulse(MINOR[b % 4][0] - 12, 0.5), t + k + 0.28, 0.3)
        k += 2 * beat
    for q in (0, 3, 5):
        if q * beat < ln: add(piano(MINOR[b % 4][q % 4] + 12, 2.5), t + q * beat, 0.10 + 0.06 * prog, 0.3 if q % 2 else -0.3)
    t += 2 * bar; b += 1

# Lift .. end: major progression, layers keyed to the section.
t, b = LIFT, 0
while t < DUR:
    ch = MAJOR[b % 4]
    ln = min(bar, DUR - t)
    lvl = 0.75 if t < BUILD else (0.9 if t < PEAK else (1.0 if t < SETTLE else 0.7))
    add(pad(ch, ln + 0.9, 0.5 if t < SETTLE else 0.3), t, 0.5 * lvl)
    add(pad([ch[0] - 12], ln + 0.5, 0.2), t, 0.35 * lvl)
    for q in range(4):
        bt = t + q * beat
        if bt >= DUR: break
        if t < SETTLE:
            if q in (0, 2) or t >= BUILD: add(kick(0.8 if t < BUILD else 1.0), bt, 0.55 * lvl)
            if t >= BUILD:
                add(noise_hit(0.08, 0.02), bt + beat / 2, 0.10 * lvl, 0.3)
                if q in (1, 3): add(noise_hit(0.25, 0.08, False), bt, 0.12 * lvl, -0.1)
            if t >= PEAK:
                add(noise_hit(0.05, 0.012), bt + beat / 4, 0.06, -0.3); add(noise_hit(0.05, 0.012), bt + 3 * beat / 4, 0.06, 0.3)
        arp = ch + [ch[1] + 12]
        if t >= BUILD and t < SETTLE:
            for e in range(2):
                add(piano(arp[(q * 2 + e) % 5] + 12, 0.8), bt + e * beat / 2, 0.09 * lvl, 0.35 if e else -0.35)
        elif q in (0, 2):
            add(piano(arp[q % 5] + 12, 2.0), bt, 0.10 * lvl, 0.2)
    t += bar; b += 1

# Simple stereo reverb (exponential-noise impulse response).
ir_n = int(2.2 * SR); ir_t = np.arange(ir_n) / SR
def verb(x, seed):
    ir = np.random.default_rng(seed).standard_normal(ir_n) * np.exp(-ir_t * 3.2); ir[0] = 0
    nfft = 1 << int(np.ceil(np.log2(len(x) + ir_n)))
    return np.fft.irfft(np.fft.rfft(x, nfft) * np.fft.rfft(ir, nfft), nfft)[: len(x)] / 30
L, R = L + 0.35 * verb(L, 1), R + 0.35 * verb(R, 2)
# Silence for the drop (the problem-section tail is cut, not faded); fades at the ends.
i0, i1 = int(DROP * SR), int((DROP + 0.12) * SR)
g = np.ones(N); g[i0:i1] = np.linspace(1, 0, i1 - i0); g[i1:int(LIFT * SR)] = 0
g[: int(0.8 * SR)] *= np.linspace(0, 1, int(0.8 * SR)); g[-int(3 * SR):] *= np.linspace(1, 0, int(3 * SR))
# Section levels: low under the problem, lifting through the steps, peak at the results, easing for the close.
pts = [(0, 0.5), (DROP, 0.62), (LIFT, 0.72), (BUILD, 0.82), (PEAK, 1.0), (SETTLE, 0.95), (SETTLE + 2, 0.7), (DUR, 0.7)]
lvl = np.interp(np.arange(N) / SR, [p[0] for p in pts], [p[1] for p in pts])
L, R = L * g * lvl, R * g * lvl
# A short reverse swell in the last 0.6 s of the drop pulls into the lift.
sw = int(0.6 * SR)
x = lowpass(rng.standard_normal(sw), 2500) * np.linspace(0, 1, sw) ** 3
add(x * 0.2, LIFT - 0.6)
st = np.stack([L, R], 1)
st = np.tanh(st * 1.1); st /= np.abs(st).max() / 0.9  # level curve survives: one global normalisation
with wave.open(out_path, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype("<i2").tobytes())
print("score", DUR, "s")
