#!/usr/bin/env python3
"""Render every deliverable.

    python3 render.py                 # all jobs, in parallel
    python3 render.py master:16x9     # one job
    python3 render.py --audio-only    # rebuild audio, remux into existing videos
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


def remux(job):
    """Swap in freshly built audio without re-rendering picture."""
    import subprocess
    cut = job.split(":")[0]
    for k in ("text", "clean"):
        p = JOBS[job].get(k)
        if p and p.exists():
            tmp = p.with_suffix(".tmp.mp4")
            subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", str(p), "-i", str(BUILD / f"{cut}.wav"),
                                   "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k",
                                   "-ar", "48000", "-movflags", "+faststart", "-shortest", str(tmp)])
            tmp.replace(p)
            print("remuxed", p.name, flush=True)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    BUILD.mkdir(exist_ok=True)
    args = sys.argv[1:]
    audio_only = "--audio-only" in args
    jobs = [a for a in args if not a.startswith("--")] or list(JOBS)
    for cut in sorted({j.split(":")[0] for j in jobs}):
        info = audio.write(cut, BUILD / f"{cut}.wav")
        (BUILD / f"audio_{cut}.json").write_text(json.dumps(info, indent=1))
        print(f"audio {cut}: {info}", flush=True)
    if audio_only:
        for j in jobs:
            remux(j)
        sys.exit(0)
    with Pool(min(4, len(jobs))) as pool:
        for j in pool.imap_unordered(run, jobs):
            print("DONE", j, flush=True)
