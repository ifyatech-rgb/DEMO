"""Split the finished ad's audio into voice and everything else (music + SFX) with Demucs htdemucs_ft's vocals
model (weights: huggingface.co/adefossez/HTDemucs-ft, 04573f0d.safetensors).
Usage: separate.py MODEL.safetensors IN.wav OUT_VOICE.wav OUT_REST.wav"""
import json, sys
from fractions import Fraction
import numpy as np, soundfile as sf, torch
from safetensors import safe_open
from safetensors.torch import load_file
from demucs.htdemucs import HTDemucs
from demucs.apply import apply_model

mp, inp, out_v, out_r = sys.argv[1:5]
meta = safe_open(mp, "pt").metadata()
kw = json.loads(meta["kwargs"])
for k, v in list(kw.items()):
    if isinstance(v, dict) and v.get("_type") == "fraction": kw[k] = Fraction(v["numerator"], v["denominator"])
model = HTDemucs(**kw); model.load_state_dict(load_file(mp)); model.eval()
wav, sr = sf.read(inp, dtype="float32", always_2d=True); assert sr == 44100
x = torch.from_numpy(wav.T.copy())
ref = x.mean(0); x_n = (x - ref.mean()) / ref.std()
torch.set_num_threads(8)
with torch.no_grad():
    est = apply_model(model, x_n[None], shifts=1, split=True, overlap=0.25, progress=False)[0]
est = est * ref.std() + ref.mean()
voc = est[model.sources.index("vocals")].numpy().T
sf.write(out_v, voc, sr); sf.write(out_r, wav - voc, sr)
print("done", voc.shape)
