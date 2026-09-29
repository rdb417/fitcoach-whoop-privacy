"""Frame compositor: plate -> grade -> reframe -> scrim -> type -> grain -> bars.

One pass per (cut, format) writes both the captioned and the textless
encode, so the two are guaranteed frame-identical underneath the type.
"""
import json
import subprocess
import time

import numpy as np
from PIL import Image, ImageFilter

from . import config as C
from .edl import CUTS
from .plates import get_plate, smoothstep
from .typeset import Card, ease_out_expo, clamp01
from .lineart import Chrome

# ------------------------------------------------------------------ grade

HEAT = np.array(C.HEAT, np.float32) / 255


def grade(img):
    """Crushed blacks, warm highlights, desaturated blues, soft shoulder."""
    x = np.clip((img - 0.035) / 0.965, 0, None) ** 1.1
    r, g, b = x[..., 0], x[..., 1], x[..., 2]
    Y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    blue = np.clip((b - np.maximum(r, g)) * 4, 0, 1)[..., None]
    x = x + (Y[..., None] - x) * (0.12 + 0.6 * blue)       # global -12% sat, blues much more
    hi = smoothstep(0.45, 1.0, Y)[..., None]
    x = x + hi * (HEAT - Y[..., None]) * 0.10               # warm highlights toward heat accent
    x = np.where(x < 0.8, x, 0.8 + 0.2 * (1 - np.exp(-(x - 0.8) / 0.2)))
    return np.clip(x, 0, 1)


class Grain:
    def __init__(self, w, h, n=8, seed=3):
        rng = np.random.default_rng(seed)
        self.frames = []
        for _ in range(n):
            g = rng.standard_normal((h, w)).astype(np.float32)
            g = np.asarray(Image.fromarray(((g * 40) + 128).clip(0, 255).astype(np.uint8))
                           .filter(ImageFilter.GaussianBlur(0.6)), np.float32)
            self.frames.append((g - 128) / 40 / 0.55)

    def apply(self, img, amt, idx):
        if amt <= 0:
            return img
        g = self.frames[idx % len(self.frames)]
        l = img[..., 1:2] / 255
        w = 0.25 + 3.0 * l * (1 - l)
        return img + (g[..., None] * w * 6.5 * amt)


# ------------------------------------------------------------------ inset

GOLD = np.array(C.GOLD, np.float32)
BG = np.array(C.BG, np.float32)
INSET_REVEAL = 0.5


def inset_frame(pic, box, W, H, t, dur):
    """Place a picture in a window on the black card. The window opens from a
    clip mask (bottom edge rises, ease-out expo) and carries a gold hairline."""
    x0, y0, x1, y1 = box
    h = y1 - y0
    out = np.empty((H, W, 3), np.float32)
    out[:] = BG
    p = ease_out_expo(clamp01(t / INSET_REVEAL))
    top = int(round(h * (1 - p)))
    if top < h:
        out[y0 + top:y1, x0:x1] = pic[top:]
    a = clamp01(t / INSET_REVEAL) * 0.7
    if a > 0:
        yt = y0 + top
        for (ya, yb, xa, xb) in ((yt, yt + 1, x0 - 1, x1 + 1), (y1, y1 + 1, x0 - 1, x1 + 1),
                                 (yt, y1 + 1, x0 - 1, x0), (yt, y1 + 1, x1, x1 + 1)):
            if yb > ya:
                out[ya:yb, xa:xb] = out[ya:yb, xa:xb] * (1 - a) + GOLD * a
    return out


# ------------------------------------------------------------------ encode

def encoder(path, w, h, wav):
    cmd = ["ffmpeg", "-v", "error", "-y",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(C.FPS), "-i", "-",
           "-i", str(wav), "-map", "0:v", "-map", "1:a",
           "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
           "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high",
           "-maxrate", "16M", "-bufsize", "32M", "-g", "60",
           "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-c:a", "aac", "-b:a", "256k", "-ar", str(C.SR),
           "-movflags", "+faststart", "-shortest", str(path)]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE)


# ------------------------------------------------------------------ render

def render(cut_name, fmt, wav, outputs, stills=None, log=print):
    """outputs: dict(text=path|None, clean=path|None). stills: {t: path}."""
    cut = CUTS[cut_name]
    F = C.FORMATS[fmt]
    W, H, bars = F["w"], F["h"], F["bars"]
    grain = Grain(W, H)
    ys = np.arange(H, dtype=np.float32)[:, None, None]
    scrim = 1 - 0.5 * smoothstep(F["lower"] - 420, F["lower"] + 60, ys)
    enc = {k: encoder(p, W, H, wav) for k, p in outputs.items() if p}
    stills = dict(stills or {})
    plates, manifest = {}, []
    total_f = int(round(cut["duration"] * C.FPS))
    t_start = time.time()
    for sh in cut["shots"]:
        f0, f1 = int(round(sh["t0"] * C.FPS)), int(round(sh["t1"] * C.FPS))
        src = sh["src"]
        inset = F["inset"] if sh.get("inset") else None
        tw, th = (inset[2] - inset[0], inset[3] - inset[1]) if inset else (W, H)
        dur_ = sh["t1"] - sh["t0"]
        if sh.get("remap"):
            ts_ = [sh["remap"](k / C.FPS) for k in range(int(dur_ * C.FPS) + 1)]
            t_range = (min(ts_), max(ts_))
        else:
            t_range = (sh.get("src_in", 0.0), sh.get("src_in", 0.0) + dur_)
        # one plate per shot: footage decodes only its window, freed after the shot
        plates.clear()
        plate, origin = get_plate(src, tw, th, fx=sh.get("fx", 0.5), t_range=t_range)
        manifest.append(dict(shot=sh["n"], t0=sh["t0"], t1=sh["t1"], src=src, origin=origin))
        dur = sh["t1"] - sh["t0"]
        layout = sh.get("layout", "lower")
        card = (Card(sh["card"], fmt, layout, dur, hold=(layout == "end"),
                     lower=F["inset_lower"] if inset else None,
                     ink=C.BG if sh.get("ink") == "bg" else None) if sh.get("card") else None)
        ch = sh.get("chrome")
        chrome = Chrome(fmt, ch["label"], ch["idx"], ch["total"], dur) if ch else None
        focus = sh.get("focus", {}).get(fmt, (0.5, 0.5))
        for f in range(f0, f1):
            tl = (f - f0) / C.FPS
            ts = sh["remap"](tl) if sh.get("remap") else sh.get("src_in", 0.0) + tl
            fr = plate.frame(ts)
            if not getattr(plate, "graphic", False):
                fr = grade(fr)
            ph, pw = fr.shape[:2]
            im = Image.fromarray((fr * 255 + 0.5).astype(np.uint8))
            shake = sh.get("shake", 0.0)
            z = sh.get("zoom", 1.0) * (1 + 0.025 * shake)
            if inset:
                z *= 1 + 0.05 * tl / dur  # slow push inside the window
            dx = dy = 0.0
            if shake:
                s0 = sh.get("shake_at", 0.35)
                ramp = smoothstep(s0, s0 + 0.35, ts) if src == "engine_fire" else 1.0
                a = shake * 0.006 * pw * ramp
                dx = a * (np.sin(tl * 53.1) + 0.6 * np.sin(tl * 97.3 + 1))
                dy = a * (np.sin(tl * 61.7 + 2) + 0.6 * np.sin(tl * 83.9))
            bw, bh = pw / z, ph / z
            cx = np.clip(focus[0] * pw + dx, bw / 2, pw - bw / 2)
            cy = np.clip(focus[1] * ph + dy, bh / 2, ph - bh / 2)
            if (pw, ph) != (tw, th) or z != 1.0:
                im = im.resize((tw, th), Image.BICUBIC, box=(cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2))
            base = np.asarray(im, np.float32)
            if inset:
                base = inset_frame(base, inset, W, H, tl, dur)
            gamt = sh.get("grain", 1.0)

            frames = {}
            if "clean" in enc:
                frames["clean"] = base
            if "text" in enc:
                img = base
                txt = card.render(tl) if card else None
                if chrome is not None:
                    cr = chrome.render(tl)
                    if txt is None:
                        txt = cr
                    else:
                        txt = cr.copy()
                        txt.alpha_composite(card.render(tl))
                if card and layout == "lower" and not inset and not getattr(plate, "graphic", False):
                    img = img * scrim
                if txt is not None:
                    a = np.asarray(txt.getchannel("A"), np.float32) / 255
                    if layout == "lower" and not inset:
                        sh_a = np.asarray(txt.getchannel("A").filter(ImageFilter.GaussianBlur(9)), np.float32) / 255
                        sh_a = np.roll(sh_a, 3, axis=0)
                        img = img * (1 - 0.6 * sh_a[..., None])
                    rgb = np.asarray(txt.convert("RGB"), np.float32)
                    img = img * (1 - a[..., None]) + rgb * a[..., None]
                frames["text"] = img
            for k, img in frames.items():
                out = np.clip(grain.apply(img, gamt, f), 0, 255).astype(np.uint8)
                if bars:
                    out[:bars] = 0
                    out[-bars:] = 0
                enc[k].stdin.write(out.tobytes())
                for ts_, p in list(stills.items()):
                    key = ts_[0] if isinstance(ts_, tuple) else ts_
                    want = ts_[1] if isinstance(ts_, tuple) else "text"
                    if want == k and int(round(key * C.FPS)) == f:
                        Image.fromarray(out).save(p)
                        stills.pop(ts_)
        el = time.time() - t_start
        log(f"[{cut_name} {fmt}] shot {sh['n']:>2} done  frame {f1}/{total_f}  {el:5.0f}s  ({origin})")
    for p in enc.values():
        p.stdin.close()
        p.wait()
    return manifest
