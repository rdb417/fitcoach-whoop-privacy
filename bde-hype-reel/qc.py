#!/usr/bin/env python3
"""Machine-checkable parts of the final checklist. Writes out/QC.md."""
import json
import re
import subprocess

import numpy as np

from reel import config as C
from reel.edl import CUTS

SPEC = {
    "master_16x9.mp4": ("master", 1920, 1080), "master_9x16.mp4": ("master", 1080, 1920),
    "master_16x9_textless.mp4": ("master", 1920, 1080), "master_9x16_textless.mp4": ("master", 1080, 1920),
    "cutdown_16x9.mp4": ("cutdown", 1920, 1080), "cutdown_9x16.mp4": ("cutdown", 1080, 1920),
}
SILENCE = {"master": (25.0, 27.0), "cutdown": (8.0, 9.0)}
BANNED = ["\u2014", "--"]


def probe(p):
    j = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(p)]))
    v = [s for s in j["streams"] if s["codec_type"] == "video"][0]
    a = [s for s in j["streams"] if s["codec_type"] == "audio"][0]
    return v, a, float(j["format"]["duration"]), int(j["format"]["size"])


def loud(p):
    e = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(p), "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", e)[-1])
    tp = float(re.findall(r"Peak:\s+(-?[\d.inf]+) dBFS", e)[-1])
    return I, tp


def window_peak(p, a, b):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(p), "-ss", str(a + 0.03), "-t", str(b - a - 0.06),
                                   "-ac", "2", "-f", "f32le", "-"])
    x = np.frombuffer(raw, np.float32)
    return float(20 * np.log10(np.abs(x).max() + 1e-12)) if len(x) else -999


def main():
    rows, ok_all = [], True
    for name, (cut, w, h) in SPEC.items():
        p = C.OUT / name
        if not p.exists():
            rows.append(f"| {name} | MISSING | | | | | |")
            ok_all = False
            continue
        v, a, dur, size = probe(p)
        fps = eval(v["r_frame_rate"])
        I, tp = loud(p)
        sp = window_peak(p, *SILENCE[cut])
        want = CUTS[cut]["duration"]
        checks = [v["codec_name"] == "h264", (v["width"], v["height"]) == (w, h), abs(fps - 30) < 1e-6,
                  abs(dur - want) < 0.1, abs(I + 14) <= 1.0, tp <= -1.0, sp < -80]
        ok_all &= all(checks)
        rows.append(f"| {name} | {v['codec_name']} {v['width']}x{v['height']} @{fps:g} | {dur:.2f}s | {I:.1f} LUFS | "
                    f"{tp:.1f} dBTP | {sp:.0f} dBFS | {size/1e6:.1f} MB | {'PASS' if all(checks) else 'FAIL'} |")
    txt = []
    for cut in CUTS.values():
        for sh in cut["shots"]:
            for el in sh.get("card") or []:
                txt.append(el["text"])
    dash = [t for t in txt if any(b in t for b in BANNED)]
    long_cards = [t for t in txt if len(t.replace("*", "").split()) > 5 and "·" not in t]
    md = ["# QC report", "",
          "| file | video | duration | loudness | true peak | silence-beat peak | size | result |",
          "|---|---|---|---|---|---|---|---|", *rows, "",
          f"- Em dashes / double hyphens in on-screen text: {'none' if not dash else dash}",
          f"- Cards over 5 words: {long_cards or 'none'}",
          "- Silence-beat peak is measured inside the black beat after AAC decode; < -80 dBFS passes.",
          "", "## Plate sources", ""]
    for f in sorted(C.BUILD.glob("manifest_*.json")):
        man = json.loads(f.read_text())
        md.append(f"**{f.stem.replace('manifest_', '')}**: " + ", ".join(
            f"{m['shot']}={m['src']}" + ("" if m["origin"] != "placeholder" else " (placeholder)")
            for m in man if m["src"] != "black"))
        md.append("")
    (C.OUT / "QC.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))
    print("ALL PASS" if ok_all else "SOME CHECKS FAILED")


if __name__ == "__main__":
    main()
