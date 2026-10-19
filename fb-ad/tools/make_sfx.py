"""Synthesize the SFX the bundled library lacks: an alarm/siren hit and a cash-register ka-ching."""
import numpy as np, wave
SR = 44100
def save(path, x):
    x = x / np.abs(x).max() * 0.9
    st = np.stack([x, x], 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype("<i2").tobytes())
t = np.arange(int(0.9 * SR)) / SR
# Siren: two fast rising "whoops" with a square-ish tone, over a low thump.
f = 650 + 750 * ((t * 2.6) % 1) ** 0.7
ph = 2 * np.pi * np.cumsum(f) / SR
siren = np.tanh(3 * np.sin(ph)) * np.minimum(1, t / 0.01) * np.exp(-np.maximum(0, t - 0.55) * 8)
thump = np.sin(2 * np.pi * np.cumsum(45 + 90 * np.exp(-t * 25)) / SR) * np.exp(-t * 7)
save("assets/sfx-siren.wav", 0.55 * siren + 0.8 * thump)
# Ka-ching: drawer click, then two bright bell strikes.
t = np.arange(int(1.1 * SR)) / SR
rng = np.random.default_rng(3)
click = rng.standard_normal(len(t)) * np.exp(-t * 120) * 0.6
def bell(start, base):
    tt = np.maximum(0, t - start); on = (t >= start)
    return on * sum(a * np.sin(2 * np.pi * base * r * tt) * np.exp(-tt * d)
                    for r, a, d in [(1, 1, 5), (2.76, 0.5, 7), (5.4, 0.25, 10), (8.93, 0.12, 14)])
save("assets/sfx-kaching.wav", click + bell(0.07, 1568) * 0.7 + bell(0.16, 2093) * 0.6)
