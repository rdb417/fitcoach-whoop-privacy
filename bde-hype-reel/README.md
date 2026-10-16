# BDE.VC hype reel

45s master and 15s cutdown, 16:9 and 9:16, for LinkedIn first.

**Status: v0 animatic.** Type, motion, grade, sound design, loudness and
every export are final-pipeline. The footage is procedural placeholder
plates, because this build environment cannot reach Pexels or an AI video
generator. Drop real clips into `footage/` and re-render; nothing else changes.

## Render

```bash
pip install numpy scipy pillow pyloudnorm fonttools   # plus ffmpeg on PATH
python3 render.py            # all deliverables into out/ (about 25 min on 4 cores)
python3 render.py master:16x9  # a single job
python3 qc.py                # checks and writes out/QC.md
```

## Deliverables (`out/`)

| File | Spec |
|---|---|
| `master_16x9.mp4` | 45s, 1920x1080, thin 2:1 letterbox, captions burned in |
| `master_9x16.mp4` | 45s, 1080x1920, type inside the centre 1080x1420 |
| `master_16x9_textless.mp4`, `master_9x16_textless.mp4` | Clean versions, identical frames under the type |
| `cutdown_16x9.mp4`, `cutdown_9x16.mp4` | 15s |
| `thumbnail_first_frame.png` | Literal first frame, as specified (it is black: see note) |
| `thumbnail_hero_16x9.png`, `thumbnail_hero_9x16.png` | BDE monogram frame, the recommended LinkedIn cover |

All: H.264 High, yuv420p, BT.709, 30fps, AAC 256k 48kHz, -14 LUFS integrated,
true peak at or under -1 dBTP, `+faststart`.

"Captions burned in": the reel has no dialogue, so the text cards are the
captions. They carry the full message with sound off.

## Layout

```
reel/config.py    brand colours, fonts, per-format sizes and safe areas
reel/edl.py       master + cutdown timelines, card copy, per-shot framing
reel/typeset.py   markup (*gold italic*), layout, rise / slam / fade motion
reel/plates.py    footage loader + procedural placeholder plates
reel/compose.py   grade, reframe, scrim, type, grain, letterbox, encode
reel/audio.py     placeholder score + SFX, ducking, silence beat, loudness
fonts/            Playfair Display Black / Black Italic, Bebas Neue (+ OFL)
footage/          drop real clips here (see footage/README.md)
audio/music/      drop the licensed track here as track.wav
licenses/         licence log for every asset
```

## Craft decisions worth knowing

- **Beat grid.** Placeholder music is 96 BPM so each 2.5s shot is exactly 4
  beats; the three BDE letters land on beats 12 to 14 and shot 5 on beat 16.
  The cutdown uses 100 BPM so its 1.2s shots are 2 beats.
- **Motion.** Plain words rise from a clip mask (ease-out expo, 60ms word
  stagger). Gold words slam from 150% with blur (220ms, ease-out cubic, no
  overshoot). Gold slams are timed to the hit: "harder." lands with the press
  at 23.75, "early." with docking contact at 32.9, "Dominant" with the final
  impact at 39.6.
- **Silence beat.** 25.0 to 27.0 (cutdown 8.0 to 9.0) is written as digital
  zero after loudness processing, so no reverb tail or room tone survives.
  Picture there is pure black with grain switched off.
- **Grade.** Blacks crushed (3.5% lift removed, gamma 1.1), blues desaturated
  via a blue-dominance mask, highlights pushed toward the #E8742C heat accent,
  soft shoulder, luma-weighted film grain. Type is composited after the grade
  so the golds stay on-brand.
- **Legibility.** Lower-third scrim plus a soft shadow under type on footage.
  Headline 104px (16:9) / 116px (9:16); `bde.vc` 92px / 100px.
