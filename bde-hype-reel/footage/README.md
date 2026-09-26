# Footage drop-in

Name each clip after its source id and drop it in `raw/` (stock) or
`generated/` (AI). `.mp4`, `.mov` or `.webm`. The renderer uses it
automatically in place of the procedural placeholder. 4K sources strongly
preferred: the 9:16 master centre-crops from 16:9.

| Source id | Used in shots | What it should be | Suggested origin |
|---|---|---|---|
| `engine_fire` | 1, 3 (and cutdown 1) | Engine static fire from black. Flame should appear ~0.5s in. Shot 3 re-uses it punched in 1.7x | AI, or stock cropped tight on flame only |
| `launch_pad` | 2 | Empty pad at dusk, wide, locked off | Stock |
| `gimbal` | 5 | Engine gimballing under thrust | AI (real test footage = identifiable engine) |
| `drill` | 6 | Geothermal drill bit into rock, slow push-in | AI |
| `battery` | 7 | Battery cycling rig, charge filling | Stock "battery production" or AI |
| `quantum` | 8 | Gold dilution refrigerator, slow orbit | AI |
| `robot` | 9 | Unbranded humanoid taking steps | AI |
| `forge` | 10 | Press slamming hot metal, sparks. Impact at **1.25s** into the clip (lands on the 23.75s downbeat) | Stock (Pexels forging) |
| `ingot` | 12 | Single glowing ingot on black, heat shimmer | Stock "molten metal" or AI |
| `docking` | 13 | Two unbranded craft docking. Contact at **3.4s** into the clip | AI |
| `liftoff` | 14 | Liftoff, tracking up | AI, or stock framed on plume only |

Timing knobs live in `reel/edl.py`: `src_in` (in-point), `zoom`, `focus`
(per-format reframe centre), `fx` (9:16 crop centre), `remap` (speed ramp).
Log every clip in `../licenses/LICENSES.md` before export.
