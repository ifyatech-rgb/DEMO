# High Roof Partners — Ad 1 edit report

**Final runtime: 26.73 s** (target 26–30, never over 30). 30 fps, 802 frames. First spoken word at **0.000 s**.

## Exports (out/)

| File | Result |
|---|---|
| `ad1_feed_4x5_1080x1350.mp4` | H.264 High, 1080x1350, 30 fps, yuv420p, AAC 48 kHz, faststart, 26.73 s |
| `ad1_reels_9x16_1080x1920.mp4` | H.264 High, 1080x1920, 30 fps, yuv420p, AAC 48 kHz, faststart, 26.73 s |
| `thumb_4x5.png` | 1080x1350, frame at 14.30 s (mouth shut, eyes on camera) + "NO ESTIMATE = NO PAY" |
| `voice_only_test.wav` | processed voice only, 48 kHz |

## Loudness (ffmpeg ebur128)

| File | Integrated | True peak | Pass |
|---|---|---|---|
| Feed 4:5 | **-14.0 LUFS** | **-2.0 dBTP** | yes |
| Reels 9:16 | **-14.0 LUFS** | **-2.0 dBTP** | yes |
| Voice only | **-14.0 LUFS** | **-2.3 dBTP** | yes |

SFX sit **17.9 dB under the voice** (loudest 400 ms window vs median speech).

## Cut list (also in `logs/cutlist.txt`)

| # | Part | Source audio | Output | Text |
|---|---|---|---|---|
| 0 | hook | 0.00–2.44 | 0.00–2.43 | Roofers getting 5 to 10 roofs per month? |
| 1 | problem | 2.57–4.54 | 2.23–4.20 | Stop buying garbage, Angi leads. |
| 2 | offer | 4.62–8.96 | 4.00–8.33 | Don't pay me anything unless you get face-to-face meetings with high-intent homeowners |
| 3 | offer | 10.53–13.26 | 8.27–11.00 | No monthly retainers, only pay per estimate. |
| 4 | how | 13.15–14.28 | 10.80–11.93 | Here's how it works. |
| 5 | how | 14.18–18.66 | 11.73–16.23 | My team and I generate exclusive homeowner leads for your company, call them ourselves |
| 6 | how | 22.81–23.44 | 16.13–16.77 | and book them |
| 7 | how | 23.87–28.12 | 16.70–20.97 | into your calendar so you don't have to waste any time at all sifting through all the dirt. |
| 8 | scarcity | 36.17–39.28 | 20.83–23.93 | we only work with one roofing contractor per area. |
| 9 | CTA | 33.35–35.88 | 23.73–26.30 | click the button below to see if your area is available, |

**Removed:**
- "who can actually afford a roof" (an unprovable claim).
- "to make sure that they're motivated buyers and financially qualified to get a roof" (financially qualified, as you asked).
- "directly".
- The whole repeated "If you want us to get you high-intent homeowner estimates and only pay us when you're face-to-face with them" passage.
- The leading "as" before the scarcity line.

**Reordered:** scarcity now comes before the CTA. Every pause over 0.25 s is cut. Each joint has room-tone pads with a cross-fade of up to 6 frames. Click check: the largest sample jump at every joint is ≤ 1.13× the voice's own 99.9th percentile, so there are no pops.

The cut after "call them ourselves → and book them" works cleanly without a pickup line.

## Fallbacks used

1. **Clean source:** no `clean.mp4` was provided, so I used the crop strategy. The cut uses only the source's 1080x928 picture area (y 211–1139). No pixel from the old caption or header bars is ever placed in the output. The old graphics burned into the picture area were handled three ways:
   - The six takeover cards and the money-emoji rain are covered by new full-screen cards.
   - The old red "CHECK IF YOUR AREA IS AVAILABLE" banner sits under a new navy lower strip and the end card.
   - 4 frames (23.83–23.88 s) are replaced with the nearest clean frame.

   Automated check over all 802 frames: **0 frames show old burned-in text** (`logs/oldtext_check.json`).
2. **Matte:** the mediapipe legacy `selfie_segmentation` API isn't in mediapipe 1.2.3, so I used the current selfie-multiclass segmenter instead.
   - Refinement: guided-filter edges, a ~2 px feather and temporal smoothing.
   - Quality: no hair halo or shimmer in review. Edge-band change on speaker shots is a median of 0.058 per frame. The worst frame (18.73 s) is a real head nod, not flicker. No elliptical fallback was needed.
3. **Denoise:** DeepFilterNet and arnndn both need models from GitHub, which is blocked from this machine. DeepFilterNet's pip build also needs torchaudio, which conflicts with the stack. Echo and room tone were handled this way instead:
   - Separation: an AI model (MelBand-RoFormer) separated the voice from the baked-in music and effects. The source mix had music in it, so this step was needed anyway.
   - Dereverb: the voice was dereverbed and lightly cleaned with `afftdn`.
   - The rest of your chain then applied: HP 90, LP 14k, −3 dB at 300 Hz, +2.5 dB at 3.5 kHz, +1.5 dB at a 100 Hz shelf, de-esser, 3:1 compression at −20 dB (5/80 ms), limiter, loudnorm. No reverb.
4. **Motion graphics:**
   - **Engine:** built in HyperFrames (HTML + GSAP), not Remotion. It's the renderer already set up in this project, and it renders frame-exact.
   - **Look:** the brief's spring eases and timings are kept.
   - **Picture:** the grade, relight and framing were done in Python and OpenCV.
5. **Fonts:** Montserrat ExtraBold and Black, from the bundled woff2 files.
6. **Music:** there was no `./assets/music.mp3`, so no music was added.
7. **"NO LEADS = NO PAY":** gone. It only existed burned into the old frames, which no longer appear. The new offer reads "NO ESTIMATE = NO PAY" throughout.
8. **Graphics left out:** the handshake and the face-to-face card. The phone graphic ("WE CALL EVERY HOMEOWNER", about 1 s) fit the pacing, so it's in.

## QA results

- **Runtime:** 26.73 s. First word at 0.000 s. Longest stretch with no cut, punch-in or card change: 2.95 s (limit 4 s).
- **Exports:** probed as listed above.
- **Contact sheets** (1 frame/s, `logs/contact_45.png`, `logs/contact_916.png`):
  - no old captions, no text on the face, no black bars;
  - end card present for the last 2.5 s.
  - In 9:16, the top 14% and bottom 20% carry no text, and the lowest caption sits above y=1500.
- **Text size:** the minimum is 56 px, everywhere.
- **Contrast:** the renderer's contrast checker passes all text (orange chips use navy text).
- **Claims:** only the allowed ones: pay only when you sit down and give an estimate, no monthly retainer, exclusive, one roofer per area, North Carolina. The calendar is labelled "EXAMPLE".

## Could not do / known limits

- **Echo:** much reduced by the separation and dereverb, but a real echo-cancelling model (DeepFilterNet) couldn't run here. Judge it with `voice_only_test.wav`.
- **Mic in frame:** a 1.56× scale was the most that keeps his head in frame, so the mic still covers the centre of his chest.
- **Spoken hook:** it says "Roofers getting 5 to 10 roofs per month?", not "Attention NC roofers". The on-screen banner says "ATTENTION NC ROOFERS".

## Reshoot / re-record — ranked

1. **Re-record the voice** in a treated or soft room with the mic 10–15 cm from the mouth. Room echo is the biggest quality drag, and no tool fully removes it.
2. **Record a clean hook:** "Attention North Carolina roofers — doing 5 to 10 roofs a month?" Deliver it with energy, straight into the lens, and start it instantly.
3. **Reshoot without the mic in front of the chest** (use a lav or boom), in front of a plain or branded background. The posters and money poster are what the blur has to hide.
