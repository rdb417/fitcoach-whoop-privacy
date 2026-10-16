#!/usr/bin/env python3
"""Generate the reel's remaining footage with Google Veo (Gemini API).

    python3 veo.py --dry-run            # show plan and cost, spend nothing
    python3 veo.py                      # generate every missing shot
    python3 veo.py liftoff docking      # only these
    python3 veo.py --takes 1 --tier standard

Reads the key from GEMINI_API_KEY (set it as an environment variable in the
cloud environment settings, never in chat or in this repo). Takes land in
footage/generated/takes/<id>_<n>.mp4; pick one and copy it to
footage/generated/<id>.mp4 (or pass --promote to use take 1 automatically).
Every generation is appended to licenses/LICENSES.md.
"""
import argparse
import datetime as dt
import json
import os
import shutil
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
TAKES = ROOT / "footage" / "generated" / "takes"
LOG = ROOT / "licenses" / "LICENSES.md"
API = "https://generativelanguage.googleapis.com/v1beta"

# Per-second prices (USD) for 1080p video from Google's pricing page as surfaced
# in search, Sept 2026; verify before large runs. Used only for the cost cap.
PRICE = {"fast": 0.12, "standard": 0.40}
MODEL_HINT = {"fast": "veo-3.1-fast", "standard": "veo-3.1-generate"}

NEG = ("text, captions, subtitles, watermark, logo, brand name, flag, insignia, mission patch, "
       "letters, numbers, people, faces, cartoon, CGI look, oversaturated")

# Shots still on footage in the hybrid cut. `note` is what the edit needs.
SHOTS = {
    "engine_fire": dict(
        prompt=("Photorealistic cinematic shot of an unbranded rocket engine static fire test at night, "
                "starting in near darkness, then ignition: a bright orange-white exhaust plume erupts "
                "horizontally from a dark engine bell mounted on a test stand, violent heat shimmer, "
                "shock diamonds in the plume, billowing lit smoke, slight camera shake, anamorphic lens, "
                "warm golden highlights, deep black shadows."),
        note="Ignition should happen within the first second (edit uses it at 0.5s)."),
    "launch_pad": dict(
        prompt=("Photorealistic wide locked-off shot of an empty coastal rocket launch pad at dusk, "
                "a lone steel launch tower silhouetted against a deep orange horizon fading to dark blue, "
                "calm, still, a few red warning lights, faint haze, no vehicle on the pad, cinematic, "
                "anamorphic lens."),
        note="Still and quiet; 2s used."),
    "ingot": dict(
        prompt=("Photorealistic macro shot of a single glowing red-hot metal ingot resting on a black "
                "surface in total darkness, intense orange and yellow glow, heat shimmer rising above it, "
                "slow push-in, shallow depth of field, cinematic, deep black background."),
        note="Single ingot on black; 2.5s used."),
    "docking": dict(
        prompt=("Photorealistic cinematic shot of two unbranded white spacecraft modules approaching each "
                "other in low Earth orbit, the curve of the Earth below, slow deliberate approach, the "
                "docking rings make soft contact and latches engage, golden sunlight glinting on the hulls, "
                "black space, anamorphic lens."),
        note="Contact at about 3.4s (edit expects it at src 3.4s; adjust src_in if not)."),
    "liftoff": dict(
        prompt=("Photorealistic cinematic shot of an unbranded white orbital rocket lifting off from a "
                "coastal launch pad at dusk, camera tilting up to follow it, huge exhaust plume and rolling "
                "steam clouds lit orange, warm golden light, anamorphic lens, no markings on the vehicle."),
        note="Tracking up; 4s used."),
}


def key():
    k = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not k:
        sys.exit("No GEMINI_API_KEY in the environment. Add it in the cloud environment settings "
                 "(Edit environment -> environment variables) and start a new session.")
    return k


def find_model(s, tier):
    r = s.get(f"{API}/models", params={"pageSize": 1000}, timeout=30)
    r.raise_for_status()
    names = [m["name"].split("/", 1)[1] for m in r.json().get("models", [])
             if "predictLongRunning" in m.get("supportedGenerationMethods", [])]
    veo = sorted(n for n in names if n.startswith("veo"))
    hint = MODEL_HINT[tier]
    pick = [n for n in veo if n.startswith(hint)]
    if not pick:
        sys.exit(f"No model matching {hint!r}. Veo models on this key: {veo}")
    return sorted(pick, key=lambda n: ("preview" in n, n))[0]  # prefer GA over preview


def submit(s, model, prompt, params):
    """Start a generation; if the API rejects an optional field, drop it and retry."""
    params = dict(params)
    while True:
        body = {"instances": [{"prompt": prompt}], "parameters": params}
        r = s.post(f"{API}/models/{model}:predictLongRunning", json=body, timeout=60)
        if r.ok:
            return r.json()["name"], params
        msg = r.text
        dropped = next((f for f in ("generateAudio", "negativePrompt", "resolution", "durationSeconds")
                        if f in params and f in msg), None)
        if r.status_code == 400 and dropped:
            print(f"    API rejected {dropped}; retrying without it")
            params.pop(dropped)
            continue
        raise RuntimeError(f"submit failed {r.status_code}: {msg[:500]}")


def find_uri(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "uri" and isinstance(v, str):
                return v
            u = find_uri(v)
            if u:
                return u
    elif isinstance(obj, list):
        for v in obj:
            u = find_uri(v)
            if u:
                return u
    return None


def wait(s, op, timeout=900):
    t0 = time.time()
    while time.time() - t0 < timeout:
        r = s.get(f"{API}/{op}", timeout=30)
        r.raise_for_status()
        j = r.json()
        if j.get("done"):
            if "error" in j:
                raise RuntimeError(f"generation failed: {j['error']}")
            uri = find_uri(j.get("response", {}))
            if not uri:
                raise RuntimeError(f"no video in response (filtered?): {json.dumps(j)[:600]}")
            return uri, j
        time.sleep(10)
    raise TimeoutError(op)


def log(entries):
    lines = ["", f"### Veo generations {dt.date.today().isoformat()}", "",
             "| Source id | Take | Model | Operation | Params | Prompt |", "|---|---|---|---|---|---|"]
    for e in entries:
        lines.append(f"| `{e['id']}` | {e['take']} | {e['model']} | `{e['op']}` | "
                     f"`{json.dumps(e['params'])}` | {e['prompt']} |")
    lines += ["", "Licence: generated with Google Veo via the Gemini API under Google's terms for "
              "generated content (outputs carry an invisible SynthID watermark). Each take must still "
              "be checked frame by frame for logos, text, faces and look-alike real hardware.", ""]
    with open(LOG, "a") as f:
        f.write("\n".join(lines))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*", help=f"subset of {list(SHOTS)}")
    ap.add_argument("--tier", choices=list(PRICE), default="fast")
    ap.add_argument("--takes", type=int, default=2)
    ap.add_argument("--seconds", type=int, default=8)
    ap.add_argument("--cap", type=float, default=16.0, help="refuse to run above this estimated USD")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--promote", action="store_true", help="copy take 1 to footage/generated/<id>.mp4")
    ap.add_argument("--force", action="store_true", help="regenerate even if takes exist")
    a = ap.parse_args()

    ids = a.ids or list(SHOTS)
    todo = [(i, n) for i in ids for n in range(1, a.takes + 1)
            if a.force or not (TAKES / f"{i}_{n}.mp4").exists()]
    cost = len(todo) * a.seconds * PRICE[a.tier]
    print(f"{len(todo)} clip(s) x {a.seconds}s on Veo 3.1 {a.tier} at ${PRICE[a.tier]:.2f}/s "
          f"= about ${cost:.2f} (cap ${a.cap:.2f})")
    for i, n in todo:
        print(f"  {i} take {n}: {SHOTS[i]['note']}")
    if a.dry_run or not todo:
        return
    if cost > a.cap:
        sys.exit("Estimated cost exceeds --cap; raise it deliberately if intended.")

    s = requests.Session()
    s.headers["x-goog-api-key"] = key()
    model = find_model(s, a.tier)
    print(f"model: {model}")
    params = {"aspectRatio": "16:9", "resolution": "1080p", "durationSeconds": a.seconds,
              "negativePrompt": NEG, "generateAudio": False}
    TAKES.mkdir(parents=True, exist_ok=True)
    pending, done = [], []
    for i, n in todo:  # submit all, then poll: generations run in parallel server-side
        op, used = submit(s, model, SHOTS[i]["prompt"], params)
        print(f"  submitted {i} take {n}: {op}")
        pending.append((i, n, op, used))
    for i, n, op, used in pending:
        try:
            uri, _ = wait(s, op)
            out = TAKES / f"{i}_{n}.mp4"
            with s.get(uri, stream=True, timeout=300, allow_redirects=True) as r:
                r.raise_for_status()
                with open(out, "wb") as f:
                    for chunk in r.iter_content(1 << 20):
                        f.write(chunk)
            print(f"  saved {out.relative_to(ROOT)}")
            done.append(dict(id=i, take=n, model=model, op=op, params=used, prompt=SHOTS[i]["prompt"]))
            if a.promote and n == 1:
                shutil.copy(out, ROOT / "footage" / "generated" / f"{i}.mp4")
        except Exception as e:  # keep going; one filtered prompt shouldn't sink the batch
            print(f"  FAILED {i} take {n}: {e}")
    if done:
        log(done)
    print(f"{len(done)}/{len(pending)} generated.")


if __name__ == "__main__":
    main()
