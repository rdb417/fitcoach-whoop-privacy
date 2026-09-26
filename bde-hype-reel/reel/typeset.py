"""Text cards: markup parsing, layout, and the two permitted motions.

Motions (no bounces, spins or typewriter):
  rise   words rise into place from behind a clip mask (ease-out expo)
  slam   word lands from 150% scale with blur (ease-out cubic, no overshoot)
  fade   plain opacity, used only for the end card
Plain runs rise, gold italic runs slam, unless an element overrides `anim`.
"""
import re
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from . import config as C

RISE_DUR = 0.55
SLAM_DUR = 0.22
FADE_DUR = 0.45
WORD_STAGGER = 0.06
EXIT_DUR = 0.13
TRACK_LABEL = 0.26  # em
TRACK_URL = 0.10


@lru_cache(maxsize=None)
def font(path, size):
    return ImageFont.truetype(str(path), size)


def ease_out_expo(p):
    return 1.0 if p >= 1 else 1 - 2 ** (-10 * p)


def ease_out_cubic(p):
    return 1 - (1 - p) ** 3


def clamp01(x):
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def parse_markup(text):
    """'We go in *deep.*' -> [('We', False), ('go', False), ('in', False), ('deep.', True)]"""
    words = []
    for part in re.split(r"(\*[^*]+\*)", text):
        if not part:
            continue
        gold = part.startswith("*") and part.endswith("*")
        for w in part.strip("*").split():
            words.append((w, gold))
    return words


# ---------------------------------------------------------------- glyph fills

def _gold_fill(mask, top, bottom):
    """Vertical gold gradient: highlight at cap height, base gold, darker foot."""
    h = mask.size[1]
    y = np.arange(h, dtype=np.float32)[:, None]
    p = np.clip((y - top) / max(1, bottom - top), 0, 1)
    hi, g = np.array(C.GOLD_HI, np.float32), np.array(C.GOLD, np.float32)
    lo = g * 0.80
    col = np.where(p < 0.5, hi + (g - hi) * (p / 0.5), g + (lo - g) * ((p - 0.5) / 0.5))
    rgb = np.broadcast_to(col.reshape(h, 1, 3), (h, mask.size[0], 3))
    a = np.asarray(mask, np.uint8)[..., None]
    return Image.fromarray(np.concatenate([rgb.astype(np.uint8), a], axis=2), "RGBA")


def _solid_fill(mask, rgb):
    im = Image.new("RGBA", mask.size, rgb + (0,))
    im.putalpha(mask)
    return im


class Glyphs:
    """A rendered run of text: RGBA image plus the layout box it occupies.

    `box` is (x0, y0) offset of the image relative to the pen origin at the
    top of the line (so the image can carry padding for italics and blur)."""

    def __init__(self, text, fnt, gold, tracking=0.0, color=C.OFF_WHITE):
        self.text = text
        asc, desc = fnt.getmetrics()
        self.asc, self.desc = asc, desc
        size = fnt.size
        track = tracking * size
        if tracking:
            adv = sum(fnt.getlength(ch) for ch in text) + track * (len(text) - 1)
        else:
            adv = fnt.getlength(text)
        self.advance = adv
        pad = int(size * 0.35)
        w, h = int(adv + 2 * pad), int(asc + desc + 2 * pad)
        mask = Image.new("L", (w, h), 0)
        d = ImageDraw.Draw(mask)
        if tracking:
            x = pad
            for ch in text:
                d.text((x, pad), ch, font=fnt, fill=255)
                x += fnt.getlength(ch) + track
        else:
            d.text((pad, pad), text, font=fnt, fill=255)
        # cap-height region for the gradient
        bb = fnt.getbbox("H")
        self.img = (_gold_fill(mask, pad + bb[1], pad + asc) if gold
                    else _solid_fill(mask, color))
        self.pad = pad


# ---------------------------------------------------------------- layout

ROLE_FONT = {
    "head": ("head", None), "head_xl": ("head_xl", None), "mono": ("mono", None),
    "label": ("label", TRACK_LABEL), "label_sm": ("label_sm", TRACK_LABEL),
    "url": ("url", TRACK_URL),
}


class Sprite:
    def __init__(self, img, x, y, anim, t0, clip=None, travel=0):
        self.img, self.x, self.y = img, x, y
        self.anim, self.t0, self.clip, self.travel = anim, t0, clip, travel
        self.w, self.h = img.size


def _wrap(items, widths, space, maxw, prefer=()):
    """Split items into lines no wider than maxw. Two-line splits prefer a
    break at a style boundary (before a gold word), else the most balanced."""
    total = sum(widths) + space * (len(items) - 1)
    if total <= maxw or len(items) == 1:
        return [list(range(len(items)))]
    for i in prefer:
        a = sum(widths[:i]) + space * (i - 1)
        b = sum(widths[i:]) + space * (len(items) - i - 1)
        if max(a, b) <= maxw and min(a, b) > 0.3 * max(a, b):
            return [list(range(i)), list(range(i, len(items)))]
    best, best_i = None, None
    for i in range(1, len(items)):
        a = sum(widths[:i]) + space * (i - 1)
        b = sum(widths[i:]) + space * (len(items) - i - 1)
        m = max(a, b)
        if m <= maxw and (best is None or m < best):
            best, best_i = m, i
    if best_i is not None:
        return [list(range(best_i)), list(range(best_i, len(items)))]
    lines, cur, cw = [], [], 0
    for i, wd in enumerate(widths):
        if cur and cw + space + wd > maxw:
            lines.append(cur)
            cur, cw = [], 0
        cw = wd if not cur else cw + space + wd
        cur.append(i)
    lines.append(cur)
    return lines


class Card:
    """All sprites for one shot's text, laid out for one format."""

    def __init__(self, elements, fmt_name, layout, shot_dur, hold=False):
        F = C.FORMATS[fmt_name]
        self.F, self.fmt = F, fmt_name
        self.W, self.H = F["w"], F["h"]
        self.shot_dur, self.hold, self.layout = shot_dur, hold, layout
        sx0, sy0, sx1, sy1 = F["safe"]
        maxw = sx1 - sx0
        self.sprites = []

        # Pass 1: build lines per element with local geometry.
        blocks = []  # (element, [line]) ; line = dict(runs=[(Glyphs, xoff, anim, word_idx)], w, h, asc)
        for el in elements:
            role = el["role"]
            key, tracking = ROLE_FONT[role]
            size = F[key]
            if role in ("label", "label_sm", "url"):
                fnt = font(C.FONT_LABEL, size)
                text = el["text"].upper() if role != "url" else el["text"].upper()
                if " · " in text:
                    items = text.split(" · ")
                    joiner = " · "
                else:
                    items, joiner = [text], ""
                gl = [Glyphs(it, fnt, False, tracking) for it in items]
                jg = Glyphs(joiner.strip(), fnt, False, tracking) if joiner else None
                sp = size * 0.42
                jw = (jg.advance + 2 * sp) if jg else 0
                rows = _wrap(items, [g.advance for g in gl], jw, maxw)
                lines = []
                for row in rows:
                    runs, x = [], 0
                    for k, i in enumerate(row):
                        if k:
                            runs.append((jg, x + sp, "sep", i))
                            x += jw
                        runs.append((gl[i], x, None, i))
                        x += gl[i].advance
                    lines.append(dict(runs=runs, w=x, asc=gl[0].asc, h=int(size * 1.25)))
                blocks.append((el, lines, fnt))
                continue

            words = parse_markup(el["text"])
            f_r = font(C.FONT_HEAD, size)
            f_i = font(C.FONT_HEAD_IT, size)
            gls = [Glyphs(w, f_i if g else f_r, g) for w, g in words]
            sp = f_r.getlength(" ")
            if role == "mono" and el.get("anim") == "letters":
                letters = list(el["text"])
                gls = [Glyphs(ch, f_r, True) for ch in letters]
                # use true kerned advances from the full word
                xs = [f_r.getlength(el["text"][:i]) for i in range(len(letters))]
                runs = [(g, xs[i], None, i) for i, g in enumerate(gls)]
                lines = [dict(runs=runs, w=f_r.getlength(el["text"]), asc=gls[0].asc,
                              h=int(size * 0.95))]
                blocks.append((el, lines, f_r))
                continue
            if role == "mono":
                gls = [Glyphs(el["text"], f_r, True)]
                words = [(el["text"], True)]
            prefer = [i for i in range(1, len(words)) if words[i][1] != words[i - 1][1]]
            rows = _wrap(words, [g.advance for g in gls], sp, maxw, prefer)
            lines = []
            for row in rows:
                runs, x = [], 0
                for k, i in enumerate(row):
                    if k:
                        x += sp
                    runs.append((gls[i], x, None, i))
                    x += gls[i].advance
                lh = int(size * (0.95 if role == "mono" else 1.12))
                lines.append(dict(runs=runs, w=x, asc=gls[row[0]].asc, h=lh))
            blocks.append((el, lines, f_r))

        # Pass 2: vertical placement.
        gap = F["gap"]
        heights = [sum(l["h"] for l in ls) for _, ls, _ in blocks]
        gaps = []
        for i in range(len(blocks) - 1):
            r0, r1 = blocks[i][0]["role"], blocks[i + 1][0]["role"]
            g = gap
            if layout == "end":
                g = int(gap * 1.6)
            if "mono" in (r0, r1) and layout != "end":
                g = int(gap * 1.4)
            gaps.append(g)
        total = sum(heights) + sum(gaps)
        if layout == "lower":
            y = F["lower"] - total
        else:
            y = (sy0 + sy1) / 2 - total / 2 if self.fmt == "9x16" else self.H / 2 - total / 2
        y = int(y)

        # Pass 3: sprites with animation timing.
        for bi, (el, lines, fnt) in enumerate(blocks):
            role = el["role"]
            anim_over = el.get("anim")
            stagger = el.get("stagger", 0.25)
            words = parse_markup(el["text"]) if role in ("head", "head_xl", "mono") else None
            # reading-order segment index for each word (contiguous same-style runs)
            seg_of, seg = {}, -1
            if words:
                prev = None
                for i, (_, g) in enumerate(words):
                    if g != prev:
                        seg += 1
                        prev = g
                    seg_of[i] = seg
            word_in_seg = {}
            for li, line in enumerate(lines):
                lx = (self.W - line["w"]) / 2
                clip = (0, y - 6, self.W, y + line["h"] + int(line["h"] * 0.25))
                for (g, xoff, tag, idx) in line["runs"]:
                    x = lx + xoff - g.pad
                    top = y + (line["h"] - (g.asc + g.desc)) / 2 - g.pad
                    if role == "mono" and anim_over == "letters":
                        t0 = el["letters_at"][idx]
                        anim = "slam"
                    elif role in ("label", "label_sm", "url"):
                        anim = anim_over or "rise"
                        t0 = el["at"] + (0.04 * idx if anim == "rise" else 0)
                    else:
                        gold = words[idx][1] if words else True
                        anim = anim_over or ("slam" if gold else "rise")
                        s = seg_of.get(idx, 0)
                        k = word_in_seg.setdefault(s, 0)
                        word_in_seg[s] += 1
                        t0 = el["at"] + s * stagger + (WORD_STAGGER * k if anim == "rise" else 0)
                    self.sprites.append(Sprite(g.img, int(round(x)), int(round(top)), anim, t0,
                                               clip=clip, travel=line["h"]))
                y += line["h"]
            if bi < len(gaps):
                y += gaps[bi]

    # ------------------------------------------------------------ render
    def render(self, t):
        """RGBA canvas for local time t, or None if nothing visible."""
        exit_a = 1.0
        if not self.hold:
            exit_a = clamp01((self.shot_dur - t) / EXIT_DUR)
        if exit_a <= 0:
            return None
        rise_dur = min(RISE_DUR, self.shot_dur * 0.3)
        canvas = None
        for s in self.sprites:
            dt = t - s.t0
            if dt < 0:
                continue
            if canvas is None:
                canvas = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
            img, x, y, alpha = s.img, s.x, s.y, exit_a
            clip = None
            if s.anim == "rise":
                p = ease_out_expo(clamp01(dt / rise_dur))
                y = s.y + int(round((1 - p) * s.travel * 1.05))
                clip = s.clip
            elif s.anim == "slam":
                p = clamp01(dt / SLAM_DUR)
                e = ease_out_cubic(p)
                sc = 1.5 - 0.5 * e
                blur = 16 * (1 - e) ** 1.4
                alpha *= clamp01(dt / 0.07)
                if p < 1:
                    w, h = int(s.w * sc), int(s.h * sc)
                    img = img.resize((w, h), Image.BILINEAR)
                    if blur > 0.4:
                        img = img.filter(ImageFilter.GaussianBlur(blur))
                    x = s.x + (s.w - w) // 2
                    y = s.y + (s.h - h) // 2
            elif s.anim == "fade":
                alpha *= ease_out_cubic(clamp01(dt / FADE_DUR))
            if alpha < 1:
                a = img.getchannel("A").point(lambda v, k=alpha: int(v * k))
                img = img.copy()
                img.putalpha(a)
            _paste(canvas, img, x, y, clip)
        return canvas


def _paste(canvas, img, x, y, clip=None):
    W, H = canvas.size
    cx0, cy0, cx1, cy1 = clip if clip else (0, 0, W, H)
    cx0, cy0, cx1, cy1 = max(0, cx0), max(0, cy0), min(W, cx1), min(H, cy1)
    x0, y0 = max(x, cx0), max(y, cy0)
    x1, y1 = min(x + img.size[0], cx1), min(y + img.size[1], cy1)
    if x1 <= x0 or y1 <= y0:
        return
    part = img.crop((x0 - x, y0 - y, x1 - x, y1 - y))
    canvas.alpha_composite(part, dest=(int(x0), int(y0)))
