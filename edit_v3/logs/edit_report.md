# HRP ad 1, light-touch edit

**Output:** `out/ad1_light_4x5_1080x1350.mp4`. H.264 High, 1080x1350, 30 fps, CRF 17, AAC 192k, faststart.

**Checks:**
- **Duration:** 39.30 s (source 39.30 s).
- **Loudness:** -13.9 LUFS, true peak -1.7 dBTP.
- **Words:** re-transcribed and diffed against the source, all there in order. Whisper wrote "5 to 10" as "5-10" and heard "getting" as "doing" this pass; the audio itself is unedited.
- **Busy check:** a frame every 1 s in `logs/contact_1s.png`. At most one added element at a time: speaker, or one cutaway, or the end card. The captions and the header line are replacements for old baked text, not extra elements.

## What changed
- **Captions:** one style (Montserrat Black, white, black stroke, active word yellow), up to 3 words, one line, in the old bottom caption bar only. That bar is painted black first, so nothing stacks.
- **Header:**
  - The old header line is hidden.
  - "NO ESTIMATE = NO PAY" (static) appears only where "NO LEADS = NO PAY" used to be: 2.77–13.30 s and 28.53–33.50 s.
  - Nothing else goes in the header.
- **Red CTA pill** (36.2 s →): covered by the last cutaway and the end card.
- **4 cutaways, 1.5 s each, covering the area above the captions.** There's no `./broll/` folder and no Pexels key, so they're simple animations:
  - shared leads into a trash can (3.30 s);
  - phone, "Call connected" (17.87 s);
  - calendar filling with estimates (23.10 s);
  - NC map with a lock, "One roofer per area" (35.80 s).
- **End card, last 2 s:** "TAP SEND MESSAGE" on navy.
- **Audio:** voice only (separated from the baked-in music, de-reverbed, denoised, EQ, de-esser, compressor, loudnorm to -14). No music, no sound effects.

## Judgment calls to check
- **Old full-screen graphics removed.** The source has more baked graphics than the 4 you asked for:
  - handshake cards at 6.33–7.67 s and 32.17–33.53 s;
  - the green "homeowners who can afford it" house card at 8.50–10.67 s;
  - money emojis over his face at 11.92–13.53 s;
  - the last 0.43 s of the old calendar card (24.60–25.03 s).

  Keeping them would have meant 8 full-screen moments and clutter on his face. Those stretches now show clean footage of him from nearby moments, at the same framing, with 3-frame blends at the joins. His lips won't match the words there (1.3–2.2 s each). Say the word and I'll put the original graphics back.
- **Cutaway placement:** the cutaways cover the speaker area and header, not the caption bar, so the captions keep running in the same spot.
