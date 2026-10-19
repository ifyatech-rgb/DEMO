"""Synthesize an original, royalty-free driving music bed (128 BPM, I-V-vi-IV in C).

Usage: make_music.py OUT.wav DURATION [RISE_START]  (RISE_START: lift ~+2.5 dB from here to the end)"""
import numpy as np, wave, sys
SR = 44100; BPM = 128; DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 44.0
RISE = float(sys.argv[3]) if len(sys.argv) > 3 else None
beat = 60 / BPM; N = int(SR * DUR); out = np.zeros((N, 2))
t_all = np.arange(N) / SR
def add(sig, start, pan=0.0, gain=1.0):
    i = int(start * SR); j = min(N, i + len(sig))
    if i >= N: return
    s = sig[: j - i] * gain
    out[i:j, 0] += s * (1 - max(pan, 0)); out[i:j, 1] += s * (1 + min(pan, 0))
def env(n, a=0.005, d=0.2):
    t = np.arange(n) / SR; return np.minimum(1, t / a) * np.exp(-t / d)
def kick():
    n = int(0.35 * SR); t = np.arange(n) / SR
    f = 50 + 110 * np.exp(-t * 30); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 9)
rng = np.random.default_rng(7)
def hat(d=0.04):
    n = int(0.12 * SR); x = rng.standard_normal(n); x = np.diff(x, prepend=0)
    return x * env(n, 0.001, d) * 0.35
def clap():
    n = int(0.25 * SR); x = rng.standard_normal(n); return x * env(n, 0.002, 0.07) * 0.4
def tone(freq, length, kind="saw", a=0.01, d=0.3):
    n = int(length * SR); t = np.arange(n) / SR
    if kind == "saw":
        s = sum(np.sin(2 * np.pi * freq * k * t) / k for k in range(1, 8))
    else:
        s = np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(4 * np.pi * freq * t)
    return s * env(n, a, d)
def midi(m): return 440 * 2 ** ((m - 69) / 12)
chords = [[60, 64, 67], [55, 59, 62], [57, 60, 64], [53, 57, 60]]  # C G Am F
bass = [36, 31, 33, 29]
bar = 4 * beat; t = 0.0; b = 0
while t < DUR:
    c = chords[b % 4]
    for k in range(4):
        add(kick(), t + k * beat, gain=0.9)
        add(hat(), t + k * beat + beat / 2, pan=0.3, gain=0.8)
        add(hat(0.015), t + k * beat + beat / 4, pan=-0.3, gain=0.4)
        add(hat(0.015), t + k * beat + 3 * beat / 4, pan=-0.3, gain=0.4)
        if k in (1, 3): add(clap(), t + k * beat, gain=0.6)
    for k in range(8):  # driving eighth-note bass
        add(tone(midi(bass[b % 4]), beat / 2, "saw", 0.004, 0.11), t + k * beat / 2, gain=0.09)
        add(tone(midi(bass[b % 4]), beat / 2, "sine", 0.004, 0.14), t + k * beat / 2, gain=0.5)
    for k in range(4):  # chord stabs
        for m in c: add(tone(midi(m + 12), beat * 0.45, "saw", 0.005, 0.09), t + k * beat + beat / 2, gain=0.05)
    arp = c + [c[0] + 12]
    for k in range(16):  # pluck arpeggio
        add(tone(midi(arp[k % 4] + 12), beat / 4, "sine", 0.002, 0.08), t + k * beat / 4, pan=(0.4 if k % 2 else -0.4), gain=0.12)
    t += bar; b += 1
if RISE is not None:  # riser noise into the ending, plus an extra hat layer
    n = int((DUR - RISE) * SR); x = rng.standard_normal(n); x = np.diff(x, prepend=0)
    add(x * np.linspace(0, 0.12, n), RISE)
fade = int(1.0 * SR); out[-fade:] *= np.linspace(1, 0, fade)[:, None]
out[: int(0.3 * SR)] *= np.linspace(0, 1, int(0.3 * SR))[:, None]
out = np.tanh(out * 1.2); out /= np.abs(out).max() / 0.89
if RISE is not None:  # bed sits at 0.75, ramps to 1.0 (~+2.5 dB) over the ending
    g = np.full(N, 0.75); i = int(RISE * SR); j = min(N, i + int(3 * SR))
    g[i:j] = np.linspace(0.75, 1.0, j - i); g[j:] = 1.0; out *= g[:, None]
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((out * 32767).astype("<i2").tobytes())
