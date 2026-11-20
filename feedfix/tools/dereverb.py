"""Take the room echo off the separated voice with anvuew's MelBand-RoFormer de-reverb model (mono-trained, SDR 20.4;
huggingface.co/anvuew/dereverb_mel_band_roformer), run with the MelBandRoformer code bundled in audio-separator.
The downloaded files are loaded safely: tensors only (torch weights_only) and a safe YAML loader.
Usage: dereverb.py MODEL.ckpt CONFIG.yaml IN.wav OUT_DRY.wav"""
import inspect, sys
import soundfile as sf, torch, yaml
from audio_separator.separator.uvr_lib_v5.roformer.mel_band_roformer import MelBandRoformer

class TupleSafeLoader(yaml.SafeLoader): pass
TupleSafeLoader.add_constructor("tag:yaml.org,2002:python/tuple", lambda l, n: tuple(l.construct_sequence(n)))

ckpt, cfgp, inp, outp = sys.argv[1:5]
cfg = yaml.load(open(cfgp), Loader=TupleSafeLoader)
ok = set(inspect.signature(MelBandRoformer.__init__).parameters)
mcfg = {k: v for k, v in cfg["model"].items() if k in ok}
mcfg["flash_attn"] = False
model = MelBandRoformer(**mcfg)
sd = torch.load(ckpt, map_location="cpu", weights_only=True)
sd = sd.get("state_dict", sd)
missing, unexpected = model.load_state_dict(sd, strict=False)
print("missing", len(missing), "unexpected", len(unexpected))
model.eval(); torch.set_num_threads(8)

wav, sr = sf.read(inp, dtype="float32", always_2d=True); assert sr == 44100
x = torch.from_numpy(wav.T.copy())                      # (2, T)
C = cfg["audio"]["chunk_size"]; step = C // 2
T = x.shape[1]; pad = (step - (T - C) % step) % step if T > C else C - T
xp = torch.nn.functional.pad(x, (step, pad + step))
out = torch.zeros_like(xp); acc = torch.zeros(xp.shape[1])
win = torch.hann_window(C, periodic=False).clamp_min(1e-3)
with torch.no_grad():
    for s in range(0, xp.shape[1] - C + 1, step):
        y = model(xp[None, :, s:s + C])
        y = y.reshape(-1, 2, C)[0] if y.dim() == 4 else y[0]
        out[:, s:s + C] += y * win; acc[s:s + C] += win
dry = (out / acc)[:, step:step + T].numpy().T
sf.write(outp, dry, sr); print("done", dry.shape)
