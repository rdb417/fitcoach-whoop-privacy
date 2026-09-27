# QC report

| file | video | duration | loudness | true peak | silence-beat peak | size | result |
|---|---|---|---|---|---|---|---|
| master_16x9.mp4 | h264 1920x1080 @30 | 45.00s | -14.1 LUFS | -2.2 dBTP | -240 dBFS | 63.5 MB | PASS |
| master_9x16.mp4 | h264 1080x1920 @30 | 45.00s | -14.1 LUFS | -2.2 dBTP | -240 dBFS | 68.9 MB | PASS |
| master_16x9_textless.mp4 | h264 1920x1080 @30 | 45.00s | -14.1 LUFS | -2.2 dBTP | -240 dBFS | 71.7 MB | PASS |
| master_9x16_textless.mp4 | h264 1080x1920 @30 | 45.00s | -14.1 LUFS | -2.2 dBTP | -240 dBFS | 76.6 MB | PASS |
| cutdown_16x9.mp4 | h264 1920x1080 @30 | 15.00s | -14.0 LUFS | -2.4 dBTP | -240 dBFS | 19.5 MB | PASS |
| cutdown_9x16.mp4 | h264 1080x1920 @30 | 15.00s | -14.0 LUFS | -2.4 dBTP | -240 dBFS | 21.5 MB | PASS |

- Em dashes / double hyphens in on-screen text: none
- Cards over 5 words: none
- Silence-beat peak is measured inside the black beat after AAC decode; < -80 dBFS passes.

## Plate sources

**cutdown_16x9**: 1=engine_fire, 5=line:thrust, 6=line:deep, 7=line:storage, 8=quantum, 9=line:moves, 12=ingot (placeholder), 13=docking (placeholder)

**cutdown_9x16**: 1=engine_fire, 5=line:thrust, 6=line:deep, 7=line:storage, 8=quantum, 9=line:moves, 12=ingot (placeholder), 13=docking (placeholder)

**master_16x9**: 1=engine_fire, 2=launch_pad (placeholder), 3=engine_fire, 5=line:thrust, 6=line:deep, 7=line:storage, 8=quantum, 9=line:moves, 10=line:harder, 12=ingot (placeholder), 13=docking (placeholder), 14=liftoff, 15=gold

**master_9x16**: 1=engine_fire, 2=launch_pad (placeholder), 3=engine_fire, 5=line:thrust, 6=line:deep, 7=line:storage, 8=quantum, 9=line:moves, 10=line:harder, 12=ingot (placeholder), 13=docking (placeholder), 14=liftoff, 15=gold

