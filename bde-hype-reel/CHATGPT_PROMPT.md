You are my motion designer, sound designer and finishing editor. Using your Python / code environment, build a finished hype reel for BDE.VC as real MP4 files, entirely in code (Python + numpy + Pillow + scipy + ffmpeg). Work in stages, show me a contact sheet of stills after each stage, and keep going unless something blocks you.

# 1. The brand and the idea
BDE.VC is a pre-seed and seed venture fund backing hard tech and deep tech: space, quantum, energy (geothermal and storage), physical AI, and industry. Brand: black and gold, luxury restraint (Tom Ford / Magnum packaging energy). The copy runs on double meanings, but nothing on screen is ever explicit. Rule: every frame must survive a screenshot shown out of context.

Concept: a hybrid reel. Real footage only for the visceral moments (fire, a glowing ingot, docking, liftoff). The six sector beats in the middle are gold line-art cards that draw themselves on, each with a sector label and counter, like an institutional index. One gold flood card for the word "Dominant".

# 2. Inputs I will upload (check for them, do not assume internet access)
- Fonts: PlayfairDisplay[wght].ttf, PlayfairDisplay-Italic[wght].ttf, BebasNeue-Regular.ttf (free on Google Fonts). Cut static Black 900 instances with fontTools: `fonttools varLib.instancer <file> wght=900`.
- Optional footage clips named exactly: engine_fire.mp4, launch_pad.mp4, ingot.mp4, docking.mp4, liftoff.mp4, and optionally a licensed music file track.wav.
- If a clip is missing, render a procedural placeholder for it (described in section 7) so the edit is always complete. If ffmpeg is not available in your environment, tell me immediately.

# 3. Deliverables
- master_16x9.mp4 (45.0s, 1920x1080) and master_9x16.mp4 (45.0s, 1080x1920)
- master_16x9_textless.mp4 and master_9x16_textless.mp4 (identical frames, no type, no labels)
- cutdown_16x9.mp4 and cutdown_9x16.mp4 (15.0s)
- thumbnail_first_frame.png (literal first frame, which is black) and thumbnail_hero_16x9.png / _9x16.png (the BDE monogram frame at 8.9s, the one to actually use as a cover)
- QC.md (automated checks, section 10)
Encode: H.264 High, yuv420p, BT.709 tags, 30 fps, CRF 18, maxrate 16M, GOP 60, AAC 256k 48 kHz, +faststart. LinkedIn is the first platform and autoplays muted, so the text cards carry the whole message (they are the burned-in captions).
If your environment has execution-time limits, render in chunks (per shot) and concatenate, and render a 480p preview first.

# 4. Writing rules
- No em dashes or double hyphens anywhere, including on screen.
- Cards 5 words or fewer. Words marked *like this* are set in gold italic; everything else off-white.
- Typographic apostrophes (World’s).

# 5. Look
- Colors: gold #C9A84C, gold highlight #EBCB74, off-white #F5F0E8, background #060606, heat accent #E8742C (footage grade and placeholders only, never type).
- Type: headlines Playfair Display Black 900; gold words Playfair Display Black Italic 900 filled with a vertical gradient (highlight #EBCB74 at cap height, #C9A84C at middle, 80% of #C9A84C at the foot). Labels Bebas Neue, uppercase, tracking 0.26 em.
- Sizes. 16:9: headline 104 px, big headline 150, monogram 330, label 44, small label 36, URL 92. 9:16: 116 / 170 / 300 / 48 / 38 / 100.
- 16:9 has thin 2:1 letterbox bars (60 px black top and bottom). Safe area x 160 to 1760. Lower-third text block bottom edge at y=930.
- 9:16: no bars; all text inside the centre 1080x1420 (y 250 to 1670, x 80 to 1000). Lower-third bottom edge y=1560. Wrap long lines, preferring a break before the gold word ("Never pull out / *early.*").
- On footage: a lower-third scrim (darken by up to 50% from 420 px above the text baseline down) plus a soft shadow (text alpha blurred 9 px, offset 3 px, 60%).
- Grade (footage only, never graphics or type): remove a 3.5% black lift then gamma 1.1 (crushed blacks); global saturation -12%; blues desaturated heavily via a blue-dominance mask (b minus max(r,g), x4); highlights nudged 10% toward #E8742C; soft shoulder above 0.8.
- Film grain on everything: monochrome gaussian, slightly blurred (0.6 px), luma-weighted (strongest in midtones, light in blacks), about 6.5 levels. Grain OFF during the silence beat.
- Type is composited after the grade so golds stay exact.

# 6. Motion rules (no bounces, spins or typewriter)
- Rise: plain words rise into place from behind a clip mask (line box), ease-out expo, 0.55s (max 30% of shot), 60 ms stagger per word.
- Slam: gold words land from 150% scale with Gaussian blur 16 px falling to 0, ease-out cubic, 0.22s, alpha 0 to 1 over 70 ms, no overshoot.
- Fade: end card only, 0.45s.
- Within a card, contiguous plain runs and gold runs are "segments" animated in reading order with a per-card stagger; every card exits with a 0.13s fade unless it is the held end card.

# 7. 45s master timeline (hard cuts; beat grid 96 BPM from t=0, so every 2.5s = 4 beats)
| # | Time | Picture | Text |
|---|---|---|---|
| 1 | 0.0-3.0 | engine_fire: black, ignition at 0.5s, camera shake ramps in after ignition | none |
| 2 | 3.0-5.0 | launch_pad: empty pad at dusk, wide, still | "Most funds wait." rises at +0.2 |
| 3 | 5.0-7.0 | engine_fire reused from 3.0s in, punched in 1.7x on the plume, light shake | "We" rises, "*don't.*" slams at +0.35 on the impact |
| 4 | 7.0-10.0 | black card: gold "BDE" monogram, each letter slams on a beat at 7.5, 8.125, 8.75 | "HARD TECH · DEEP TECH" label rises at 9.375 |
| 5 | 10.0-12.5 | line art: Space | "Full thrust." |
| 6 | 12.5-15.0 | line art: Geothermal | "We go in *deep.*" (gold slams 0.625s after) |
| 7 | 15.0-17.5 | line art: Energy Storage | "*Serious* staying power." |
| 8 | 17.5-20.0 | line art: Quantum | "Deeply *entangled.*" |
| 9 | 20.0-22.5 | line art: Physical AI | "It *moves.*" |
| 10 | 22.5-25.0 | line art: Industry, press slams at 23.75 | "Built" rises, "*harder.*" slams at 23.75 |
| 11 | 25.0-27.0 | pure #060606 black, no grain | none |
| 12 | 27.0-29.5 | ingot: single glowing ingot on black, heat shimmer | "*Atoms.*" slams at +0.05 |
| 13 | 29.5-35.0 | docking: two unbranded craft, soft contact at 32.9 (3.4s into clip) | "Never pull out" rises at 30.9, "*early.*" slams on contact 32.9 |
| 14 | 35.0-39.0 | liftoff, tracking up | "All the way." rises at 35.5 |
| 15a | 39.0-39.6 | black card | "The World’s Most" rises (lay out all three lines now so nothing jumps) |
| 15b | 39.6-42.0 | full-bleed GOLD flood (#C9A84C with a soft #EBCB74 sheen near the top), all type in #060606 | "The World’s Most" held, "*Dominant*" (150 px) slams at 39.6 on the final hit, "Seed Fund" rises at 40.05 |
| 16 | 42.0-45.0 | black end card, hold 3s | "SPACE · QUANTUM · ENERGY · PHYSICAL AI · INDUSTRY" (small label), gold "BDE" monogram, "BDE.VC" (URL size), all fade in at 42.0 |

# 8. Line-art sector cards (shots 5-10)
Draw with Pillow at 2x supersampling, three stroke weights at output resolution: hi 2.6 px #EBCB74, mid 2.1 px #C9A84C, dim 1.6 px #C9A84C at 36%. Add a glow: the hi layer blurred 7 px, added at 55%. Background #060606. No grade on these. Strokes draw on (a polyline prefix growing by arc length, ease-out cubic, about 0.5-0.6s, staggered), then keep moving. Motif area sits above the lower-third card: centre y at -0.17 of half-height with scale 0.52 (16:9), -0.16 and 0.40 (9:16), in coordinates where y runs -1 to 1.
Chrome on every line-art card (text version only): sector label top-left and counter "01 / 06" top-right in Bebas small-label size (label off-white, counter gold), aligned to the safe area (16:9 at y=98); a small gold Playfair "BDE" bug bottom-right. Chrome fades in over 0.35s.
Motifs (keep them generic: no real products):
1. Space, "Full thrust.": engine bell outline (two curves plus throat and exit ellipses, two cooling rings), gimbals ±4° on a 1.7s period; 13 exhaust lines fanning out drawn dim, then bright dashes flowing down them; four shock diamonds on the axis, flickering.
2. Geothermal, "We go in *deep.*": surface line plus 7 wavy rock strata drawing on left to right; a double-line drill string descends from 0.3s to 2.3s with a triangular bit and rotating flute ticks; each stratum brightens from dim to mid as the bit passes; three heat-reservoir arcs pulse below.
3. Energy Storage, "*Serious* staying power.": five tall cell outlines with terminal caps; horizontal fill lines stack up inside each (targets 62-100%, staggered) with a bright charge line at the top of each fill; a bus bar above.
4. Quantum, "Deeply *entangled.*": dilution-refrigerator tiers as five ellipses (wide to narrow) with support rods that slowly orbit (front rods mid, back rods dim); two helical strands wind down the centre with small dots where they cross.
5. Physical AI, "It *moves.*": side-view line robot walking in place (boxy helmet with a bright visor slit, trapezoid torso, joint circles, 0.8 Hz walk cycle), two fading ghost poses behind it, ground line with ticks scrolling left.
6. Industry, "Built *harder.*": anvil, glowing billet, press frame; the ram descends and slams at local 1.25s (23.75 on the timeline), the billet squashes 30%, 36 spark strokes fly out with gravity, two impact rings expand.

# 9. Sound (synthesise everything; no samples, so no licence issues)
48 kHz stereo float. Music bus:
- Low D drone (36.7 and 55 Hz sines plus detuned saws at 73.4, 110, 146.8, 174.6, 220 Hz through a lowpass around 260 Hz, slow LFO). Enters 3.0s with a 1s fade, hard stop at 25.0.
- Beat 10.0-25.0 at 96 BPM: kick every beat (sine sweep 44 Hz + 110·e^(-t/0.035), 0.17s decay, soft 2 ms attack), hi-hat on off-beats, sub bass every 2 beats. A 1s riser into 25.0.
- 27.0-45.0: the drone returns with a filter swell (cutoff 260 to 2860 Hz, rising over 12.6s), 3s fade out at the end.
SFX: ignition roar 0.5-3.0 (brown noise + rumble + crackle) with a sub drop at 0.5; roar 5.0-7.0 and an impact + sub drop at 5.35; whoosh at 6.6; heavy kicks on the BDE letters (7.5, 8.125, 8.75); hydraulic hiss into a press slam with metallic clang at 23.75; the biggest sub drop + impact at 27.0; a soft docking clunk at 32.9; roar under music 35-39; final impact + big sub drop at 39.6.
Duck the music by 70% (0.4s release) under 0.5, 5.0, 5.35, 23.75, 27.0, 39.6.
SILENCE BEAT: 25.0-27.0 must be digital zero (no room tone, no reverb tails). Also silent before ignition (0-0.5). Zero these windows again after loudness processing.
Loudness: -14 LUFS integrated (BS.1770, e.g. pyloudnorm) with a lookahead limiter that detects on a 4x-oversampled signal, ceiling -2.5 dBTP, so the true peak stays under -1 dBTP after AAC encoding. If I upload track.wav, it replaces the synthesised music bus; keep SFX, ducking and the silence beat.

# 10. 15s cutdown (reuse the same sources, no new footage; 100 BPM grid from 2.0s so 1.2s = 2 beats)
0.0-2.0 engine_fire, ignition at 0.25 (no text) | 2.0-3.2 Space "Full thrust." | 3.2-4.4 Geothermal "We go in *deep.*" | 4.4-5.6 Storage "*Serious* staying power." | 5.6-6.8 Quantum "Deeply *entangled.*" | 6.8-8.0 Physical AI "It *moves.*" (line-art cards, counters "0x / 05") | 8.0-9.0 black + digital silence | 9.0-10.5 ingot "*Atoms.*" with big sub drop | 10.5-12.5 docking, speed-ramped from about 4x down to 1x so contact (clip 3.4s) lands at 11.6 on a beat; "Never pull out *early.*" with "early." slamming on contact | 12.5-15.0 end card: gold "BDE" slams, "BDE.VC" rises at 12.95.
Cutdown sound: drone and beat 2.0-8.0, riser into 8.0, silence 8-9, sub drop + impact at 9.0, whoosh 10.5, clunk 11.6, impact + sub drop 12.5, fade out.

# 11. Procedural placeholders (only when a clip is missing)
Render at half resolution then upscale; grade them like footage.
- engine_fire: horizontal (16:9) or vertical (9:16) plume from a dark generic nozzle; turbulent noise scrolled along the axis, blackbody color ramp through #E8742C to white, shock diamonds, lit smoke, flash on ignition.
- launch_pad: dusk gradient (deep blue-black to warm orange horizon), silhouetted lattice tower and pad, blinking red lights, haze.
- ingot: glowing trapezoid ingot on black, mottled heat texture, bloom, heat-shimmer displacement above.
- docking: starfield, Earth limb at the bottom with atmosphere glow, two generic white modules with dark solar panels, one decelerating into soft contact at 3.4s, warm sunlit edges, contact flash.
- liftoff: vertical plume under a dark vehicle body climbing out of frame, billowing clouds scrolling down, dusk sky.

# 12. QC (automate, write QC.md, fix anything that fails)
For each MP4: codec h264, exact resolution, 30 fps, duration within 0.1s, integrated loudness -14 ±1 LUFS, true peak ≤ -1 dBTP (ffmpeg ebur128 peak=true), and the silence window peak below -80 dBFS after decoding. Check the card copy for em dashes / double hyphens and cards over five words. List which shots used real footage vs placeholders.
Human checks to report on: hook visible within the first 2s with sound off; the silence beat is truly silent; no logos, faces, flags, patches or identifiable real hardware anywhere; every frame passes the screenshot test; end card held 3s with BDE.VC legible on a phone.

# 13. If I ask for AI footage prompts (for Veo, Kling or Runway; 16:9, 8s, no audio)
Negative prompt for all: "text, captions, subtitles, watermark, logo, brand name, flag, insignia, mission patch, letters, numbers, people, faces, cartoon, CGI look, oversaturated".
- engine_fire: Photorealistic cinematic shot of an unbranded rocket engine static fire test at night, starting in near darkness, then ignition: a bright orange-white exhaust plume erupts horizontally from a dark engine bell mounted on a test stand, violent heat shimmer, shock diamonds in the plume, billowing lit smoke, slight camera shake, anamorphic lens, warm golden highlights, deep black shadows.
- launch_pad: Photorealistic wide locked-off shot of an empty coastal rocket launch pad at dusk, a lone steel launch tower silhouetted against a deep orange horizon fading to dark blue, calm, still, a few red warning lights, faint haze, no vehicle on the pad, cinematic, anamorphic lens.
- ingot: Photorealistic macro shot of a single glowing red-hot metal ingot resting on a black surface in total darkness, intense orange and yellow glow, heat shimmer rising above it, slow push-in, shallow depth of field, cinematic, deep black background.
- docking: Photorealistic cinematic shot of two unbranded white spacecraft modules approaching each other in low Earth orbit, the curve of the Earth below, slow deliberate approach, the docking rings make soft contact and latches engage, golden sunlight glinting on the hulls, black space, anamorphic lens.
- liftoff: Photorealistic cinematic shot of an unbranded white orbital rocket lifting off from a coastal launch pad at dusk, camera tilting up to follow it, huge exhaust plume and rolling steam clouds lit orange, warm golden light, anamorphic lens, no markings on the vehicle.

# 14. How to work
Stage 1: fonts, type engine and motion; show me stills of every card in both formats. Stage 2: line-art cards; show stills mid-animation. Stage 3: audio; report LUFS and true peak. Stage 4: placeholders or my footage, grade, full render (preview first). Stage 5: QC and downloads. Keep the code organised in a small project (config, timeline, typesetting, line art, plates, compositor, audio, render, qc) and give me a zip of it at the end so I can re-render.
