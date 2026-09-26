#!/usr/bin/env python3
"""Render every deliverable.

    python3 render.py                 # all jobs, in parallel
    python3 render.py master:16x9     # one job
Outputs land in out/. Then run `python3 qc.py`.
"""
import json
import sys
from multiprocessing import Pool

from reel import audio, config as C
from reel.compose import render

OUT, BUILD = C.OUT, C.BUILD

JOBS = {
    "master:16x9": dict(text=OUT / "master_16x9.mp4", clean=OUT / "master_16x9_textless.mp4",
                        stills={(0.0, "text"): OUT / "thumbnail_first_frame.png",
                                (8.9, "text"): OUT / "thumbnail_hero_16x9.png"}),
    "master:9x16": dict(text=OUT / "master_9x16.mp4", clean=OUT / "master_9x16_textless.mp4",
                        stills={(0.0, "text"): OUT / "thumbnail_first_frame_9x16.png",
                                (8.9, "text"): OUT / "thumbnail_hero_9x16.png"}),
    "cutdown:16x9": dict(text=OUT / "cutdown_16x9.mp4"),
    "cutdown:9x16": dict(text=OUT / "cutdown_9x16.mp4"),
}


def run(job):
    cut, fmt = job.split(":")
    spec = JOBS[job]
    wav = BUILD / f"{cut}.wav"
    outputs = {k: spec.get(k) for k in ("text", "clean") if spec.get(k)}
    man = render(cut, fmt, wav, outputs, stills=spec.get("stills"),
                 log=lambda m: print(m, flush=True))
    (BUILD / f"manifest_{cut}_{fmt}.json").write_text(json.dumps(man, indent=1))
    return job


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    BUILD.mkdir(exist_ok=True)
    jobs = sys.argv[1:] or list(JOBS)
    for cut in sorted({j.split(":")[0] for j in jobs}):
        info = audio.write(cut, BUILD / f"{cut}.wav")
        (BUILD / f"audio_{cut}.json").write_text(json.dumps(info, indent=1))
        print(f"audio {cut}: {info}", flush=True)
    with Pool(min(4, len(jobs))) as pool:
        for j in pool.imap_unordered(run, jobs):
            print("DONE", j, flush=True)
