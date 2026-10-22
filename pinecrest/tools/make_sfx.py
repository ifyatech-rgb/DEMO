"""Synthesize the ad's sound effects (deterministic, royalty-free). Writes assets/sfx-<name>.wav."""
import wave
import numpy as np

SR = 44100
rng = np.random.default_rng(21)
def t_(d): return np.arange(int(d * SR)) / SR
def save(name, x, stereo_width=0.0):
    x = x / (np.abs(x).max() + 1e-9) * 0.9
    l = x; r = np.roll(x, int(stereo_width * SR)) if stereo_width else x
    st = np.stack([l, r], 1)
    with wave.open(f"assets/sfx-{name}.wav", "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype("<i2").tobytes())
def lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR); y = np.zeros_like(x); acc = 0.0
    for i in range(len(x)): acc = (1 - a) * x[i] + a * acc; y[i] = acc
    return y
def hp(x, fc): return x - lp(x, fc)
def noise(d): return rng.standard_normal(int(d * SR))

# Warning beep: two short square beeps.
t = t_(0.5); beep = np.sign(np.sin(2 * np.pi * 1320 * t)) * 0.5
beep *= ((t < 0.12) | ((t > 0.2) & (t < 0.32))).astype(float)
save("beep", lp(beep, 6000))
# Ice hit: bright crunchy transient + glassy partials.
t = t_(0.6)
ice = hp(noise(0.6), 2500) * np.exp(-t * 30) + sum(np.sin(2 * np.pi * f * t) * np.exp(-t * k) for f, k in ((2350, 14), (3620, 18), (5100, 22))) * 0.4
save("ice", ice)
# Crack: sharp split + splintering tail.
t = t_(0.5); crack = hp(noise(0.5), 1200) * np.exp(-t * 45)
for k in range(6): i = int((0.02 + k * 0.025) * SR); crack[i:i + 600] += hp(rng.standard_normal(600), 1800) * np.exp(-np.arange(600) / 120) * 0.8
save("crack", crack)
# Wood creak: slow friction, pitch wandering.
t = t_(0.9); f = 180 + 60 * np.sin(2 * np.pi * 1.3 * t) + 30 * t
creak = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * (0.6 + 0.4 * rng.random(len(t)))
creak = lp(creak, 1800) * np.minimum(1, t / 0.08) * np.minimum(1, (0.9 - t) / 0.2)
save("creak", creak)
# Water drip: falling-pitch "plip" with a small echo.
t = t_(0.7); f = 1600 * np.exp(-t * 18) + 650
drip = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 22)
drip += np.roll(drip, int(0.18 * SR)) * 0.35
save("drip", drip)
# Thunder rumble: low filtered noise with a crack at the front.
t = t_(3.0); th = lp(noise(3.0), 180) * (np.minimum(1, t / 0.05) * np.exp(-t * 1.1)) * 6
th[: int(0.25 * SR)] += hp(noise(0.25), 800) * np.exp(-t_(0.25) * 18) * 0.6
save("thunder", th, 0.012)
# Hail on a roof: dense random ticks for 2.4 s.
d = 2.4; hail = np.zeros(int(d * SR))
for _ in range(900):
    i = rng.integers(0, len(hail) - 900); amp = rng.uniform(0.2, 1.0)
    hail[i:i + 900] += hp(rng.standard_normal(900), 3000) * np.exp(-np.arange(900) / rng.uniform(40, 120)) * amp
hail *= np.minimum(1, t_(d) / 0.3) * np.minimum(1, (d - t_(d)) / 0.4)
save("hail", hail, 0.008)
# Pen scribble: band-limited noise bursts in a writing rhythm.
d = 0.9; t = t_(d); sc = lp(hp(noise(d), 1500), 6000)
sc *= (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 7 * t + 2 * np.sin(2 * np.pi * 3 * t)))) * np.minimum(1, (d - t) / 0.1)
save("scribble", sc)
# Car peel-out: tyre screech (rising band noise) over an engine rev.
d = 1.6; t = t_(d)
eng = sum(np.sin(2 * np.pi * np.cumsum(55 + 90 * t ** 0.8) * h / SR) / h for h in range(1, 6))
scr = np.sin(2 * np.pi * np.cumsum(900 + 500 * t + 80 * np.sin(2 * np.pi * 11 * t)) / SR) * (0.6 + 0.4 * rng.random(len(t)))
peel = eng * 0.6 + lp(scr, 4000) * 0.5
peel *= np.minimum(1, t / 0.05) * np.minimum(1, (d - t) / 0.7)
save("peel", peel, 0.01)
# Ladder footsteps: three metallic taps.
d = 1.0; lad = np.zeros(int(d * SR))
for k, s in enumerate((0.0, 0.32, 0.64)):
    tt = t_(0.25); hit = sum(np.sin(2 * np.pi * f * tt) * np.exp(-tt * 25) for f in (520, 1270, 2210)) + hp(noise(0.25), 2000) * np.exp(-tt * 60)
    i = int(s * SR); lad[i:i + len(hit)] += hit * (1 - 0.15 * k)
save("ladder", lad)
# Camera shutter: two-stage mechanical click.
t = t_(0.25); sh = np.zeros(len(t))
for s, g in ((0.0, 1.0), (0.07, 0.7)):
    i = int(s * SR); n = int(0.03 * SR); sh[i:i + n] += hp(rng.standard_normal(n), 2500) * np.exp(-np.arange(n) / 200) * g
save("shutter", sh)
# Soft warm hit: low sine thump + gentle body.
t = t_(1.2); warm = np.sin(2 * np.pi * np.cumsum(70 + 40 * np.exp(-t * 12)) / SR) * np.exp(-t * 3.5) + lp(noise(1.2), 400) * np.exp(-t * 6) * 0.3
save("warm", warm)
print("sfx ok")
