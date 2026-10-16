"""Gold line-art sector cards: strokes that draw themselves on, then move.

Each motif is drawn in local units (u, v), roughly -1..1, v pointing down,
and mapped into the frame above the lower-third card. Three stroke weights:
  hi   bright gold highlight (the eye goes here)
  mid  base gold
  dim  gold at low intensity (structure, context)
Plates here are graphics, not footage: the compositor skips the grade so the
golds stay exactly on-brand.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from . import config as C
from .typeset import _Glyphs, font, ease_out_expo, ease_out_cubic, clamp01

SS = 2  # supersampling
BG = np.array(C.BG, np.float32) / 255
COL = {
    "hi": np.array(C.GOLD_HI, np.float32) / 255,
    "mid": np.array(C.GOLD, np.float32) / 255,
    "dim": np.array(C.GOLD, np.float32) / 255 * 0.36,
}
WIDTH = {"hi": 2.6, "mid": 2.1, "dim": 1.6}  # px at output resolution
LAYOUT = {"16x9": (0.0, -0.17, 0.52), "9x16": (0.0, -0.16, 0.40)}  # cx, cy, scale


def ease_io(p):
    p = clamp01(p)
    return p * p * (3 - 2 * p)


def draw_on(t, t0, dur=0.6):
    return ease_out_cubic(clamp01((t - t0) / dur))


def ellipse(cx, cy, rx, ry, a0=0.0, a1=2 * np.pi, n=72, phase=0.0):
    a = np.linspace(a0, a1, n) + phase
    return np.stack([cx + rx * np.cos(a), cy + ry * np.sin(a)], 1)


def line(p0, p1):
    return np.array([p0, p1], np.float64)


def quad(p0, c, p1, n=24):
    s = np.linspace(0, 1, n)[:, None]
    p0, c, p1 = map(np.asarray, (p0, c, p1))
    return (1 - s) ** 2 * p0 + 2 * (1 - s) * s * c + s * s * p1


def rotate(pts, ang, pivot):
    c, s = np.cos(ang), np.sin(ang)
    d = pts - pivot
    return np.stack([d[:, 0] * c - d[:, 1] * s, d[:, 0] * s + d[:, 1] * c], 1) + pivot


def partial(pts, p):
    """Prefix of a polyline covering fraction p of its length."""
    if p >= 1:
        return pts
    if p <= 0:
        return pts[:1]
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    cum = np.concatenate([[0], np.cumsum(seg)])
    L = cum[-1] * p
    i = np.searchsorted(cum, L) - 1
    i = max(0, min(i, len(seg) - 1))
    f = (L - cum[i]) / max(seg[i], 1e-9)
    return np.vstack([pts[: i + 1], pts[i] + (pts[i + 1] - pts[i]) * f])


def dashes(pts, dash, gap, offset):
    """Split a polyline into dash sub-polylines, pattern shifted by offset."""
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    cum = np.concatenate([[0], np.cumsum(seg)])
    L, period = cum[-1], dash + gap
    out = []
    s = -(offset % period)
    while s < L:
        a, b = max(s, 0), min(s + dash, L)
        if b > a:
            ts = np.linspace(a, b, 6)
            out.append(np.stack([np.interp(ts, cum, pts[:, 0]), np.interp(ts, cum, pts[:, 1])], 1))
        s += period
    return out


# ------------------------------------------------------------------ motifs
# Each returns a list of (points, weight). t is local shot time in seconds.


def m_thrust(t):
    S = []
    ang = 0.07 * np.sin(2 * np.pi * t / 1.7)
    piv = np.array([0.0, -0.95])
    R = lambda p: rotate(p, ang, piv)  # noqa: E731
    d = draw_on(t, 0.0, 0.55)
    S.append((R(partial(quad((-0.12, -0.95), (-0.16, -0.45), (-0.42, -0.15)), d)), "mid"))
    S.append((R(partial(quad((0.12, -0.95), (0.16, -0.45), (0.42, -0.15)), d)), "mid"))
    S.append((R(partial(ellipse(0, -0.95, 0.12, 0.03), d)), "mid"))
    S.append((R(partial(ellipse(0, -0.15, 0.42, 0.075), d)), "hi"))
    for k in (-0.5, -0.25):  # cooling rings on the bell
        w = 0.12 + (0.42 - 0.12) * ((k + 0.95) / 0.8) ** 1.6
        S.append((R(partial(ellipse(0, k, w, w * 0.18, 0, np.pi), d)), "dim"))
    S.append((R(partial(line((-0.2, -1.12), (-0.12, -0.95)), d)), "dim"))
    S.append((R(partial(line((0.2, -1.12), (0.12, -0.95)), d)), "dim"))
    e = draw_on(t, 0.3, 0.6)
    for i, x in enumerate(np.linspace(-0.38, 0.38, 13)):
        p = np.array([[x, -0.12], [x * 2.4, 1.05]])
        pts = R(partial(np.linspace(p[0], p[1], 20), e))
        S.append((pts, "dim"))
        if e >= 1:
            for dsh in dashes(R(np.linspace(p[0], p[1], 20)), 0.10, 0.16, t * 2.2 + i * 0.07):
                S.append((dsh, "hi" if abs(x) < 0.2 else "mid"))
    if e > 0.5:
        for j, v in enumerate((0.05, 0.3, 0.55, 0.8)):
            w = 0.1 * (1 - j * 0.18) * (0.85 + 0.15 * np.sin(t * 20 + j))
            h = 0.09
            S.append((R(np.array([[0, v - h], [w, v], [0, v + h], [-w, v], [0, v - h]])), "hi"))
    return S


def m_deep(t):
    S = []
    d_s = draw_on(t, 0.0, 0.5)
    S.append((partial(line((-1.3, -0.72), (1.3, -0.72)), d_s), "mid"))
    depth = -0.72 + 1.5 * ease_io((t - 0.3) / 2.0)
    for k in range(7):
        v0 = -0.5 + k * 0.2
        u = np.linspace(-1.3, 1.3, 90)
        v = v0 + 0.03 * np.sin(u * 3 + k) + 0.018 * np.sin(u * 7.3 + 2 * k)
        pts = partial(np.stack([u, v], 1), draw_on(t, 0.05 * k, 0.6))
        S.append((pts, "mid" if depth > v0 else "dim"))
    # drill string, bit, and rotating flute ticks
    S.append((line((-0.03, -1.15), (-0.03, depth - 0.12)), "mid"))
    S.append((line((0.03, -1.15), (0.03, depth - 0.12)), "mid"))
    S.append((np.array([[-0.07, depth - 0.12], [0.07, depth - 0.12], [0, depth], [-0.07, depth - 0.12]]), "hi"))
    for k in range(12):
        v = -1.1 + ((k * 0.14 + t * 0.9) % 1.7)
        if v < depth - 0.14:
            S.append((line((-0.03, v), (0.03, v + 0.05)), "hi"))
    # heat reservoir below, rings pulse once the bit gets close
    near = clamp01((depth - 0.1) / 0.6)
    for r in range(3):
        rad = 0.25 + 0.2 * r + 0.06 * np.sin(t * 4 - r)
        S.append((ellipse(0, 1.0, rad, rad * 0.35, np.pi, 2 * np.pi), "hi" if near > 0.5 and r == 0 else "dim"))
    return S


def m_storage(t):
    S = []
    xs = np.linspace(-0.76, 0.76, 5)
    for i, x in enumerate(xs):
        d = draw_on(t, 0.06 * i, 0.55)
        w, top, bot = 0.12, -0.72, 0.72
        body = np.array([[x - w, top], [x + w, top], [x + w, bot], [x - w, bot], [x - w, top]])
        S.append((partial(body, d), "mid"))
        S.append((partial(np.array([[x - 0.05, top], [x - 0.05, top - 0.06], [x + 0.05, top - 0.06], [x + 0.05, top]]), d), "mid"))
        target = (0.62, 0.74, 0.86, 0.95, 1.0)[i]
        lvl = target * ease_io((t - 0.4 - 0.08 * i) / 1.6)
        n = int(lvl * 18)
        for k in range(n):
            v = bot - 0.05 - k * 0.075
            S.append((line((x - w + 0.03, v), (x + w - 0.03, v)), "dim"))
        if lvl > 0:
            v = bot - 0.05 - lvl * 18 * 0.075
            S.append((line((x - w + 0.02, v), (x + w - 0.02, v)), "hi"))
    # bus bar linking the cells
    S.append((partial(line((-0.9, -0.84), (0.9, -0.84)), draw_on(t, 0.4, 0.6)), "dim"))
    return S


def m_entangled(t):
    S = []
    tiers = [(-0.82, 0.78), (-0.5, 0.64), (-0.18, 0.5), (0.14, 0.4), (0.44, 0.3)]
    rot = 0.35 * t
    for k, (v, rx) in enumerate(tiers):
        d = draw_on(t, 0.07 * k, 0.5)
        S.append((partial(ellipse(0, v, rx, rx * 0.17), d), "mid"))
        S.append((partial(ellipse(0, v + 0.035, rx, rx * 0.17, 0, np.pi), d), "dim"))
        if k < len(tiers) - 1 and d >= 1:
            v1, rx1 = tiers[k + 1]
            for j in range(6):
                a = rot + j * np.pi / 3 + k * 0.4
                front = np.sin(a) > 0
                p0 = (rx * 0.85 * np.cos(a), v + 0.035 + rx * 0.17 * np.sin(a) * 0.85)
                p1 = (rx1 * 0.85 * np.cos(a), v1 + rx1 * 0.17 * np.sin(a) * 0.85)
                S.append((line(p0, p1), "mid" if front else "dim"))
    h = draw_on(t, 0.45, 0.8)
    v = np.linspace(-0.82, 0.95, 160)
    for ph, w in ((0.0, "hi"), (np.pi, "mid")):
        u = 0.13 * np.sin(v * 9 - t * 3 + ph)
        S.append((partial(np.stack([u, v], 1), h), w))
    if h >= 1:
        for k in range(-2, 20):
            vv = (k * np.pi + t * 3) / 9
            if -0.82 < vv < 0.95:
                S.append((ellipse(0, vv, 0.022, 0.022, n=16), "hi"))
    return S


def _pose(t):
    ph = 2 * np.pi * 0.8 * t
    hip = np.array([0.0, 0.02 + 0.015 * np.cos(2 * ph)])
    T, Sh = 0.42, 0.40
    segs, joints = [], []
    for off in (0.0, np.pi):
        ah = 0.45 * np.sin(ph + off)
        ak = 0.6 * max(0.0, np.sin(ph + off + 1.3))
        knee = hip + T * np.array([np.sin(ah), np.cos(ah)])
        foot = knee + Sh * np.array([np.sin(ah - ak), np.cos(ah - ak)])
        segs += [(hip, knee), (knee, foot), (foot, foot + np.array([0.1, 0.0]))]
        joints += [knee]
        sh = hip + np.array([0.0, -0.58])
        a_s = -0.38 * np.sin(ph + off)
        el = sh + 0.3 * np.array([np.sin(a_s), np.cos(a_s)])
        wr = el + 0.27 * np.array([np.sin(a_s + 0.5), np.cos(a_s + 0.5)])
        segs += [(sh, el), (el, wr)]
        joints += [el]
    sh = hip + np.array([0.0, -0.58])
    torso = np.array([hip + [-0.07, 0], hip + [0.08, 0], sh + [0.13, 0], sh + [-0.11, 0], hip + [-0.07, 0]])
    head = np.array([sh + [-0.07, -0.08], sh + [0.09, -0.08], sh + [0.1, -0.26], sh + [-0.07, -0.26], sh + [-0.07, -0.08]])
    visor = (sh + [0.01, -0.19], sh + [0.1, -0.19])
    return segs, joints, torso, head, visor, hip


def m_moves(t):
    S = []
    S.append((partial(line((-1.3, 0.86), (1.3, 0.86)), draw_on(t, 0.0, 0.5)), "dim"))
    for k in range(14):
        u = 1.3 - ((k * 0.2 + t * 0.55) % 2.6)
        S.append((line((u, 0.86), (u - 0.04, 0.92)), "dim"))
    a = draw_on(t, 0.15, 0.5)
    for lag, w in ((0.24, "dim"), (0.12, "dim"), (0.0, None)):
        segs, joints, torso, head, visor, hip = _pose(max(0.0, t - lag))
        if w:
            if a >= 1:
                for p0, p1 in segs:
                    S.append((line(p0, p1), w))
            continue
        for p0, p1 in segs:
            S.append((partial(line(p0, p1), a), "hi"))
        S.append((partial(torso, a), "mid"))
        S.append((partial(head, a), "mid"))
        S.append((line(*visor), "hi" if a >= 1 else "dim"))
        for j in joints + [hip]:
            S.append((ellipse(j[0], j[1], 0.03, 0.03, n=16), "mid"))
    return S


HIT = 1.25


def m_harder(t):
    S = []
    d = draw_on(t, 0.0, 0.5)
    dt = t - HIT
    sq = 1.0 if dt < 0 else 1 - 0.3 * clamp01(dt / 0.05)
    bw, bh = 0.34 / np.sqrt(sq), 0.12 * sq
    base = 0.42
    anvil = np.array([[-0.55, base], [0.55, base], [0.4, base + 0.12], [0.5, base + 0.5], [-0.5, base + 0.5], [-0.4, base + 0.12], [-0.55, base]])
    S.append((partial(anvil, d), "mid"))
    S.append((partial(line((-1.2, base + 0.5), (1.2, base + 0.5)), d), "dim"))
    billet = np.array([[-bw, base], [bw, base], [bw, base - 2 * bh], [-bw, base - 2 * bh], [-bw, base]])
    S.append((partial(billet, d), "hi"))
    for x in (-0.82, 0.82):
        S.append((partial(line((x, -1.15), (x, base + 0.5)), d), "dim"))
    ram_v = (base - 2 * bh) - (0.95 * (1 - ease_io((t + 0.0) / HIT) ** 3) if dt < 0 else 0.25 * ease_io((dt - 0.15) / 1.0))
    ram = np.array([[-0.62, -1.2], [0.62, -1.2], [0.62, ram_v], [-0.62, ram_v], [-0.62, -1.2]])
    S.append((partial(ram, d), "mid"))
    S.append((line((-0.62, ram_v - 0.05), (0.62, ram_v - 0.05)), "dim"))
    if dt >= 0:
        rng = np.random.default_rng(5)
        n = 36
        ang = rng.uniform(-np.pi * 0.95, -np.pi * 0.05, n)
        spd = rng.uniform(0.8, 2.2, n)
        life = rng.uniform(0.4, 1.0, n)
        side = rng.choice([-1, 1], n)
        for a_, s_, l_, sd in zip(ang, spd, life, side):
            if dt > l_:
                continue
            o = np.array([sd * bw, base - bh])
            v = np.array([np.cos(a_) * sd * -1 * 1.2, np.sin(a_)]) * s_
            p1 = o + v * dt + np.array([0, 1.6]) * dt * dt
            p0 = o + v * max(0, dt - 0.06) + np.array([0, 1.6]) * max(0, dt - 0.06) ** 2
            S.append((np.array([p0, p1]), "hi"))
        for r in range(2):
            rr = 0.3 + (dt - r * 0.08) * 2.2
            if 0.3 < rr < 1.6:
                S.append((ellipse(0, base, rr, rr * 0.18), "mid" if rr < 0.9 else "dim"))
    return S


MOTIFS = {"thrust": m_thrust, "deep": m_deep, "storage": m_storage,
          "entangled": m_entangled, "moves": m_moves, "harder": m_harder}


class LinePlate:
    graphic = True

    def __init__(self, motif, w, h, fmt):
        self.fn, self.w, self.h = MOTIFS[motif], w, h
        self.cx, self.cy, self.s = LAYOUT[fmt]
        self.a = w / h

    def _px(self, pts):
        x = self.cx + pts[:, 0] * self.s
        y = self.cy + pts[:, 1] * self.s
        return list(zip((x + self.a) / (2 * self.a) * self.w * SS, (y + 1) / 2 * self.h * SS))

    def frame(self, t):
        masks = {k: Image.new("L", (self.w * SS, self.h * SS), 0) for k in COL}
        draws = {k: ImageDraw.Draw(m) for k, m in masks.items()}
        for pts, weight in self.fn(t):
            if len(pts) < 2:
                continue
            draws[weight].line(self._px(np.asarray(pts, np.float64)), fill=255,
                               width=max(1, int(round(WIDTH[weight] * SS))), joint="curve")
        out = np.zeros((self.h, self.w, 3), np.float32) + BG
        hi = None
        for k in ("dim", "mid", "hi"):
            m = masks[k].resize((self.w, self.h), Image.BOX)
            if k == "hi":
                hi = m
            a = np.asarray(m, np.float32)[..., None] / 255
            out = out * (1 - a) + COL[k] * a
        glow = np.asarray(hi.filter(ImageFilter.GaussianBlur(7)), np.float32)[..., None] / 255
        out = out + COL["hi"] * glow * 0.55
        return np.clip(out, 0, 1)


class GoldPlate:
    """Full-bleed gold flood with a soft vertical sheen."""
    graphic = True

    def __init__(self, w, h):
        y = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
        hi, g = COL["hi"], COL["mid"]
        sheen = np.exp(-((y - 0.3) / 0.35) ** 2)
        self.img = np.broadcast_to(g + (hi - g) * sheen * 0.8, (h, w, 3)).astype(np.float32)

    def frame(self, t):
        return self.img


# ------------------------------------------------------------------ chrome


class Chrome:
    """Sector label (top-left), counter (top-right) and BDE bug (bottom-right)."""

    def __init__(self, fmt, label, idx, total, shot_dur):
        F = C.FORMATS[fmt]
        W, H = F["w"], F["h"]
        x0, y0, x1, y1 = F["safe"]
        top = y0 + (38 if F["bars"] else 0)
        size = F["label_sm"]
        fl = font(C.FONT_LABEL, size)
        self.img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        lab = _Glyphs(label.upper(), fl, False, 0.26)
        cnt = _Glyphs(f"{idx:02d} / {total:02d}", fl, False, 0.26, color=C.GOLD)
        bug = _Glyphs("BDE", font(C.FONT_HEAD, int(size * 1.25)), True)
        self.img.alpha_composite(lab.img, (int(x0 - lab.pad), int(top - lab.pad)))
        self.img.alpha_composite(cnt.img, (int(x1 - cnt.advance - cnt.pad), int(top - cnt.pad)))
        by = (y1 - (22 if F["bars"] else 0)) - (bug.asc + bug.desc)
        self.img.alpha_composite(bug.img, (int(x1 - bug.advance - bug.pad), int(by - bug.pad)))
        self.dur = shot_dur

    def render(self, t):
        a = ease_out_expo(clamp01(t / 0.35)) * clamp01((self.dur - t) / 0.13)
        if a >= 1:
            return self.img
        im = self.img.copy()
        im.putalpha(self.img.getchannel("A").point(lambda v: int(v * a)))
        return im
