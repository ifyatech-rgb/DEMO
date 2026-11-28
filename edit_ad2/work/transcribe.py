import json, sys
from faster_whisper import WhisperModel
m = WhisperModel("medium.en", device="cpu", compute_type="int8")
import soundfile as sf
audio, _ = sf.read(sys.argv[1], dtype="float32")   # decoded here: faster-whisper's own loader clashes with the installed PyAV
segs, info = m.transcribe(audio, word_timestamps=True, beam_size=5, vad_filter=False,
                          initial_prompt="Attention roofing companies. Door knocking, Angi, roofers, retainer, estimates, North Carolina, exclusive, qualified homeowner, appointment setting.")
words = []
for s in segs:
    for w in s.words: words.append({"text": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3), "p": round(w.probability, 3)})
json.dump(words, open(sys.argv[2], "w"), indent=1)
with open(sys.argv[3], "w") as f:
    for w in words: f.write(f"{w['start']:7.3f} {w['end']:7.3f}  {w['text']}  ({w['p']})\n")
print(len(words), "words")
