# High Roof Partners — Ad 1 v2 (no cut, no crop) — edit report

**Runtime 39.30 s = source 39.30 s.** Every frame and every word of the source is kept, and audio and picture stay in sync. The speaker pane is the source's own pane (y 211–1139, 1080x928), placed at the same position, unscaled and uncropped.

## Exports (`edit_v2/out/`)

| File | Result |
|---|---|
| `ad1_feed_4x5_1080x1350.mp4` | H.264 High, 1080x1350, 30 fps, yuv420p, AAC 192k, faststart, **39.30 s** |
| `ad1_reels_9x16_1080x1920.mp4` | H.264 High, 1080x1920, 30 fps, same edit on a taller navy canvas, **39.30 s** |
| `thumb_4x5.png` | 1080x1350, frame at 26.9 s (mouth shut, eyes on camera) with "NO ESTIMATE = NO PAY" |
| `voice_only_test.wav` | processed voice only |

Folder note: `./edit/` already held the first (cut) version of this ad with the same output names, so this version lives in `./edit_v2/` to avoid overwriting it.

## QA results (logs/qa.json)

| Check | Result |
|---|---|
| Duration vs source (±0.1 s) | 39.30 vs 39.30, pass (both exports) |
| Size / fps | 1080x1350 and 1080x1920 at 30/1, pass |
| Loudness | **-13.9 LUFS integrated, -1.9 dBTP true peak** (both exports), pass |
| Voice only | -14.0 LUFS, -2.3 dBTP |
| Word check: export re-transcribed and diffed against the source | 138 / 138 words, same order. One difference, "getting" vs "doing" at 0.46 s, is Whisper hearing the same untouched audio two ways (the audio isn't edited). Pass. |
| Old baked-in text | None visible. Old header and caption bars are replaced. Every old full-screen graphic window and the money emojis are under new scenes, and the speaker frames shown in the bubble there are clean neighbouring frames. The red CTA pill (36.2 s→) is under the end card. "NO LEADS = NO PAY" never appears. Pass. |
| Speaker cropped / face covered | Never. Graphics stay out of the face zone (pane x 380–800, y 60–600). Type B cards sit lower-right. Pass. |
| b-roll length | max 2.50 s, pass |
| Longest pure talking head (after 2.4 s, before the end card) | 2.55 s, pass |
| Audio pops | 0 clicks above 3× the voice's 99.9th-percentile sample jump. The audio is never cut, so b-roll transitions can't pop. Pass. |
| Matte flicker | Edge-band change median 0.080 / p95 0.205 per frame on speaker frames. This is natural head and hand motion, and I saw no shimmer. Kept the matte; no fallback needed. |
| Contact sheets | `logs/contact_45_1.png`, `_2.png`, `logs/contact_916_1.png`, `_2.png` (a frame every 0.5 s). In 9:16, no text above y 269 or below y 1536. Captions are never on the face. |

## B-roll (all animated scenes: no `./broll/` clips and no `PEXELS_API_KEY`)

All 9 are original SVG/GSAP scenes. No third-party footage, so no license is needed. Each one has a slow 100→108% push, a 20% navy overlay, an orange/yellow light leak on entry, a 6-frame crossfade or whip in and out, and 1px film grain.

| # | Time | Type | Scene | On the words |
|---|---|---|---|---|
| 1 | 3.30–4.80 | A | lead cards stamped "SHARED" tipping into a trash can | "stop buying garbage, Angi leads" |
| 2 | 6.37–7.63 | A | roofer (hard hat) and homeowner handshake | "face-to-face meetings" |
| 3 | 8.53–10.63 | A | line-art house, door opens, homeowner steps out, yard sign | "homeowners who can actually afford a roof" |
| 4 | 11.92–13.53 | A | roof cross-section, shingle courses laying in | "only pay per estimate" |
| 5 | 15.35–16.95 | B | aerial neighbourhood, roofs turn new one by one | "exclusive homeowner leads" |
| 6 | 17.87–19.37 | A | phone ringing → "Call connected" | "call them ourselves" |
| 7 | 23.10–25.03 | A | week calendar fills with free-estimate slots, counter to 9, "EXAMPLE" label | "book them directly into your calendar" |
| 8 | 28.40–30.90 | B | clipboard estimate on a roof, checklist ticking | "high-intent homeowner estimates" |
| 9 | 32.20–33.50 | A | handshake (second pass) | "when you're face to face with them" |

**A/B split: 7 A, 2 B, not 50/50.** Seven of the nine beats fall on windows where the source shows its old full-screen graphics. There the speaker isn't in the source picture, so those beats have to cover the whole pane (type A, with the speaker bubble).

**Type B placement:** a card on the right 45% of the pane would cover his face (his face is centred around x 590). Type B is a rounded card in the lower-right of the pane instead, beside his chin and over the mic.

## Graphics

1. **Header zone (replaces the old top bar):** the HIGH ROOF PARTNERS wordmark, plus one claim chip at a time:
   - "🚨 ATTENTION NC ROOFERS" (0–2.5 s, the siren pulses);
   - "NO ESTIMATE = NO PAY";
   - "🔒 1 ROOFER PER AREA";
   - from "No monthly retainers" (10.68 s) on, the persistent "NO ESTIMATE = NO PAY" with a "NO RETAINERS" sub-chip.
2. **Name tag:** "PARTH | HIGH ROOF PARTNERS" from 0.6 to 3.3 s. It slides in from the left with an orange underline sweep, over the bottom of the pane. It ends at 3.3 s instead of 3.6 s, because b-roll 1 starts there.
3. **Hook slam:** "5 TO 10 ROOFS A MONTH?" slams in on "5", then shrinks into a small tag beside his head.
4. **Keyword pops beside his head:** "NO RETAINERS" on "monthly" and "EXCLUSIVE" on "exclusive", each with a 0.6 s yellow glow. "One roofer per area" is spoken during the end card, so it's the end card's lock badge.
5. **"✓ PRE-QUALIFIED HOMEOWNERS"** pops in over the "financially qualified" line (20.84 s).
6. **"WE BOOK. YOU CLOSE."** with an underline swipe at 25.15 s. This phrase isn't spoken in this ad. It sits after "into your calendar", where it fits.
7. **Calendar** (scene 7): fills slot by slot to a count of 9, labelled "EXAMPLE".
8. **North Carolina map** with pins on Charlotte, Raleigh and Greensboro, pulse rings and an NC-only label. A lock snaps onto Raleigh on the spoken "one" (37.18 s) with a "🔒 1 ROOFER PER AREA · NC ONLY" badge, a 2-frame 6px camera shake and a thud. This is part of the end card, because that line is spoken during it.
9. **Depth:** floating shingle particles in the scenes, and an orange glow ring on the speaker bubble.

**Captions:**
- **Style:** rebuilt word by word in the new bottom zone, Montserrat Black up to 66px, uppercase, white with a 6px black stroke and soft shadow.
- **Active word:** turns yellow at 110%, appearing 2 frames early.
- **Key words** ESTIMATE(S), PAY, EXCLUSIVE, RETAINERS, ONE and CALENDAR get an orange bar behind them.
- **Layout:** up to 3 words per line. Captions hide under the end card.

## End card (36.05 s → end)

The picture is dimmed to 30%, with a navy panel showing:
- the wordmark and the NC map with the lock;
- the "1 ROOFER PER AREA · NC ONLY" badge;
- "TAP SEND MESSAGE";
- "Only 1 roofer per area. Check if yours is open.";
- a bouncing arrow.

There's no fake button, and his voice continues underneath.

**It starts at 36.05 s, not 39.3 − 2.5 = 36.8 s:** the old red "CHECK IF YOUR AREA IS AVAILABLE" pill is baked into the speaker pane from 36.2 s, and starting the card 0.75 s earlier is the only way to cover it without cropping.

## Audio

- **Voice:** the source track already has the old edit's music and sound effects mixed in. I separated the voice with an AI model (MelBand-RoFormer vocals) and de-reverbed it (anvuew MelBand-RoFormer de-reverb). The timing is unchanged sample for sample.
- **Denoise fallback:** DeepFilterNet and arnndn couldn't be used, because their models download from GitHub, which is blocked from this machine. I used your last fallback, `afftdn=nr=12:nf=-30`, then your full chain: HP 90 / LP 14k, −3 dB at 300 Hz, +2.5 dB at 3.5 kHz, +1.5 dB at a 100 Hz shelf, de-esser, 3:1 at −20 dB (5/80 ms), limiter, and loudnorm to −14 / −1.5 dBTP. No reverb.
- **Music:** `./assets/music.mp3` didn't exist. You asked for background music on this ad in your previous request, so I placed the royalty-free Mixkit track #112 (Mixkit Stock Music Free License) there. It's lowpassed at 5 kHz, sidechain-ducked, **26 dB under the voice**, with a 0.5 s fade in and a 1 s fade out. Delete `edit_v2/assets/music.mp3` and re-run `work/audio.py` if you want it gone.
- **SFX:** all synthetic, with the loudest about **18 dB under the voice**. A whoosh on every b-roll in and out and on the slams, a pop on the chips and keyword pops, a ding on the calendar fill, a thud on the trash lid, the hook slam and the lock badge. Nothing plays on caption words.

## Things that can't be fixed in the edit

- **"financially qualified" is still spoken (20.84–22.06 s).** Removing it would break the no-cut rule. The screen says "PRE-QUALIFIED HOMEOWNERS" instead. Re-record the line if this claim is a problem.
- **Spoken claims not in the allowed on-screen list:** "high-intent homeowners", "who can actually afford a roof" and "motivated buyers". They stay in the audio (no cuts). None of them are amplified with graphics beyond what the brief asked for.
- **Echo:** much reduced by separation and dereverb, but not removed completely. DeepFilterNet couldn't run here. Judge it with `voice_only_test.wav`.
- **Speaker bubble during old-graphic windows:** the source has no speaker picture there. The bubble shows clean neighbouring frames played back and forth, so his lips in the bubble don't match the words in those 1–2 s stretches. At 240px it's subtle.
- **Posters behind him:** the brief asked for a light blur, so they stay faintly recognisable. A stronger blur would hide them if you prefer.

## Re-record next time (ranked)

1. **Voice in a treated room, mic 10–15 cm from his mouth.** Room echo is the one thing post can't fully remove.
2. **The qualification line, without "financially":** "…to make sure they're serious about getting a roof, and book them directly into your calendar." Also replace "who can actually afford a roof".
3. **A clean master with no burned-in graphics or captions,** shot against a plain or branded background with the mic out of the chest area. All the cover-ups (bubble frame fills, the early end card) exist only because the source has old graphics baked in.
