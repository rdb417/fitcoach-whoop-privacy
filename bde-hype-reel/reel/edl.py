"""Edit decision lists for the master (45s) and cutdown (15s).

Times are seconds on the output timeline. Card element `at` times are
relative to the shot start. Markup: *word* = gold italic, " / " = line break.

Each shot names a `src` (a footage id). The renderer looks for
footage/raw/<src>.mp4 then footage/generated/<src>.mp4; if neither exists it
falls back to the procedural placeholder of the same name (reel/plates.py).
`src_in` is the in-point in that source, `remap` optionally warps time,
`zoom` punches in (1.0 = full frame), `fx` is the 9:16 crop centre (0..1).
"""

MASTER_BPM = 96.0   # placeholder track; 2.5s shots = 4 beats
CUT_BPM = 100.0     # cutdown placeholder; 1.2s shots = 2 beats


def E(text, role="head", at=0.0, anim=None, **kw):
    return dict(text=text, role=role, at=at, anim=anim, **kw)


MASTER = dict(
    name="master",
    duration=45.0,
    shots=[
        dict(n=1, t0=0.0, t1=3.0, src="engine_fire", src_in=0.58, shake=1.0, fx=0.6, shake_at=1.05),  # Veo take ignites at 1.08s
        dict(n=2, t0=3.0, t1=5.0, src="launch_pad", src_in=0.0,
             card=[E("Most funds wait.", at=0.2)]),
        dict(n=3, t0=5.0, t1=7.0, src="engine_fire", src_in=3.0, zoom=1.7, shake=0.5,
             focus={"16x9": (0.66, 0.5), "9x16": (0.5, 0.5)},
             card=[E("We *don't.*", at=0.05, stagger=0.3)]),
        dict(n=4, t0=7.0, t1=10.0, src="black", layout="center",
             card=[E("BDE", role="mono", anim="letters", letters_at=[0.5, 1.125, 1.75]),
                   E("Hard Tech · Deep Tech", role="label", at=2.375)]),
        dict(n=5, t0=10.0, t1=12.5, src="line:thrust",
             chrome=dict(label="Space", idx=1, total=6),
             card=[E("Full thrust.", at=0.1)]),
        dict(n=6, t0=12.5, t1=15.0, src="line:deep",
             chrome=dict(label="Geothermal", idx=2, total=6),
             card=[E("We go in *deep.*", at=0.1, stagger=0.625)]),
        dict(n=7, t0=15.0, t1=17.5, src="battery", src_in=5.0, inset=True,
             chrome=dict(label="Energy Storage", idx=3, total=6),
             card=[E("*Serious* staying power.", at=0.1, stagger=0.625)]),
        dict(n=8, t0=17.5, t1=20.0, src="quantum", src_in=3.0, inset=True,
             chrome=dict(label="Quantum", idx=4, total=6),
             card=[E("Deeply *entangled.*", at=0.1, stagger=0.625)]),
        dict(n=9, t0=20.0, t1=22.5, src="robot", src_in=6.0, inset=True,
             chrome=dict(label="Physical AI", idx=5, total=6),
             card=[E("It *moves.*", at=0.1, stagger=0.625)]),
        # press hits at src 1.25s = 23.75 on the timeline (a downbeat)
        dict(n=10, t0=22.5, t1=25.0, src="line:harder",
             chrome=dict(label="Industry", idx=6, total=6),
             card=[E("Built *harder.*", at=0.1, stagger=1.15)]),
        dict(n=11, t0=25.0, t1=27.0, src="black", grain=0.0),
        dict(n=12, t0=27.0, t1=29.5, src="ingot", src_in=0.0,
             card=[E("*Atoms.*", at=0.05)]),
        # docking contact at src 3.4s = 32.9 on the timeline
        dict(n=13, t0=29.5, t1=35.0, src="docking", src_in=0.0,
             card=[E("Never pull out *early.*", at=1.4, stagger=2.0)]),
        dict(n=14, t0=35.0, t1=39.0, src="liftoff", src_in=3.5,
             card=[E("All the way.", at=0.5)]),
        # 15: black, then the frame floods gold as "Dominant" slams on the final hit
        dict(n=15, t0=39.0, t1=39.6, src="black", layout="center",
             card=[E("The World’s Most", role="head", at=0.1),
                   E("*Dominant*", role="head_xl", at=9.0),
                   E("Seed Fund", role="head", at=9.0)]),
        dict(n=15, t0=39.6, t1=42.0, src="gold", layout="center", ink="bg",
             card=[E("The World’s Most", role="head", at=0.0, anim="hold"),
                   E("*Dominant*", role="head_xl", at=0.0),
                   E("Seed Fund", role="head", at=0.45)]),
        dict(n=16, t0=42.0, t1=45.0, src="black", layout="end",
             card=[E("Space · Quantum · Energy · Physical AI · Industry",
                     role="label_sm", at=0.0, anim="fade"),
                   E("BDE", role="mono", at=0.0, anim="fade"),
                   E("bde.vc", role="url", at=0.0, anim="fade")]),
    ],
)


def _dock_ramp(u):
    """Cutdown speed ramp for shot 13: ~4x decelerating to 1x so the
    docking contact (src 3.4s) lands at local 1.1s (timeline 11.6, a beat)."""
    uc, sc, a = 1.1, 3.4, 1.49
    if u < uc:
        d = uc - u
        return sc - d - a * d * d
    return sc + (u - uc)


CUTDOWN = dict(
    name="cutdown",
    duration=15.0,
    shots=[
        dict(n=1, t0=0.0, t1=2.0, src="engine_fire", src_in=0.83, shake=1.0, fx=0.6, shake_at=1.05),
        dict(n=5, t0=2.0, t1=3.2, src="line:thrust",
             chrome=dict(label="Space", idx=1, total=5),
             card=[E("Full thrust.", at=0.05)]),
        dict(n=6, t0=3.2, t1=4.4, src="line:deep",
             chrome=dict(label="Geothermal", idx=2, total=5),
             card=[E("We go in *deep.*", at=0.05, stagger=0.3)]),
        dict(n=7, t0=4.4, t1=5.6, src="battery", src_in=5.5, inset=True,
             chrome=dict(label="Energy Storage", idx=3, total=5),
             card=[E("*Serious* staying power.", at=0.05, stagger=0.3)]),
        dict(n=8, t0=5.6, t1=6.8, src="quantum", src_in=3.0, inset=True,
             chrome=dict(label="Quantum", idx=4, total=5),
             card=[E("Deeply *entangled.*", at=0.05, stagger=0.3)]),
        dict(n=9, t0=6.8, t1=8.0, src="robot", src_in=7.0, inset=True,
             chrome=dict(label="Physical AI", idx=5, total=5),
             card=[E("It *moves.*", at=0.05, stagger=0.3)]),
        dict(n=11, t0=8.0, t1=9.0, src="black", grain=0.0),
        dict(n=12, t0=9.0, t1=10.5, src="ingot", src_in=0.3,
             card=[E("*Atoms.*", at=0.05)]),
        dict(n=13, t0=10.5, t1=12.5, src="docking", remap=_dock_ramp,
             card=[E("Never pull out *early.*", at=0.1, stagger=1.0)]),
        dict(n=16, t0=12.5, t1=15.0, src="black", layout="end",
             card=[E("BDE", role="mono", at=0.0, anim="slam"),
                   E("bde.vc", role="url", at=0.45)]),
    ],
)

CUTS = {"master": MASTER, "cutdown": CUTDOWN}

# Inset treatment preview: footage in a gold-hairline window on the black
# card, card copy below. Set `inset=True` on any shot to use it.
INSET_PREVIEW = dict(
    name="inset_preview",
    duration=10.0,
    shots=[
        dict(n=14, t0=0.0, t1=2.5, src="liftoff", inset=True, card=[E("Full thrust.", at=0.3)]),
        dict(n=8, t0=2.5, t1=5.0, src="quantum", inset=True, card=[E("Deeply *entangled.*", at=0.3, stagger=0.625)]),
        dict(n=7, t0=5.0, t1=7.5, src="battery", inset=True, card=[E("*Serious* staying power.", at=0.3, stagger=0.625)]),
        dict(n=9, t0=7.5, t1=10.0, src="robot", inset=True, card=[E("It *moves.*", at=0.3, stagger=0.625)]),
    ],
)
CUTS["inset_preview"] = INSET_PREVIEW
