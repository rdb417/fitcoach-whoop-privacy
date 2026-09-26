# QC report

| file | video | duration | loudness | true peak | silence-beat peak | size | result |
|---|---|---|---|---|---|---|---|
| master_16x9.mp4 | h264 1920x1080 @30 | 45.00s | -14.1 LUFS | -2.2 dBTP | -240 dBFS | 41.1 MB | PASS |
| master_9x16.mp4 | h264 1080x1920 @30 | 45.00s | -14.1 LUFS | -2.2 dBTP | -240 dBFS | 60.1 MB | PASS |
| master_16x9_textless.mp4 | h264 1920x1080 @30 | 45.00s | -14.1 LUFS | -2.2 dBTP | -240 dBFS | 46.1 MB | PASS |
| master_9x16_textless.mp4 | h264 1080x1920 @30 | 45.00s | -14.1 LUFS | -2.2 dBTP | -240 dBFS | 64.6 MB | PASS |
| cutdown_16x9.mp4 | h264 1920x1080 @30 | 15.00s | -14.0 LUFS | -2.4 dBTP | -240 dBFS | 13.0 MB | PASS |
| cutdown_9x16.mp4 | h264 1080x1920 @30 | 15.00s | -14.0 LUFS | -2.4 dBTP | -240 dBFS | 19.2 MB | PASS |

- Em dashes / double hyphens in on-screen text: none
- Cards over 5 words: none
- Silence-beat peak is measured inside the black beat after AAC decode; < -80 dBFS passes.

## Plate sources

**cutdown_16x9**: 1=engine_fire (placeholder), 5=gimbal (placeholder), 6=drill (placeholder), 7=battery (placeholder), 8=quantum (placeholder), 9=robot (placeholder), 12=ingot (placeholder), 13=docking (placeholder)

**cutdown_9x16**: 1=engine_fire (placeholder), 5=gimbal (placeholder), 6=drill (placeholder), 7=battery (placeholder), 8=quantum (placeholder), 9=robot (placeholder), 12=ingot (placeholder), 13=docking (placeholder)

**master_16x9**: 1=engine_fire (placeholder), 2=launch_pad (placeholder), 3=engine_fire (placeholder), 5=gimbal (placeholder), 6=drill (placeholder), 7=battery (placeholder), 8=quantum (placeholder), 9=robot (placeholder), 10=forge (placeholder), 12=ingot (placeholder), 13=docking (placeholder), 14=liftoff (placeholder)

**master_9x16**: 1=engine_fire (placeholder), 2=launch_pad (placeholder), 3=engine_fire (placeholder), 5=gimbal (placeholder), 6=drill (placeholder), 7=battery (placeholder), 8=quantum (placeholder), 9=robot (placeholder), 10=forge (placeholder), 12=ingot (placeholder), 13=docking (placeholder), 14=liftoff (placeholder)

