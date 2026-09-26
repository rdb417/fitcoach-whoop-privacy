"""Picture sources for each shot.

`get_plate(src, w, h)` returns an object with `.frame(t) -> float32 HxWx3`
(0..1, pre-grade) for source time t.

Real footage wins: footage/raw/<src>.mp4, then footage/generated/<src>.mp4.
Otherwise a procedural placeholder is drawn. Placeholders are deliberately
generic (no real hardware) and render at half resolution; the compositor
upscales them and the grain hides the softness.
"""
import json
import subprocess

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

from . import config as C

# ------------------------------------------------------------------ helpers


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def fbm_texture(shape, beta=2.2, seed=0):
    """Periodic fractal noise via spectral synthesis, normalised to 0..1."""
    rng = np.random.default_rng(seed)
    h, w = shape
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.fftfreq(w)[None, :]
    f = np.sqrt(fx * fx + fy * fy)
    f[0, 0] = 1
    spec = (rng.normal(size=shape) + 1j * rng.normal(size=shape)) / f ** (beta / 2)
    spec[0, 0] = 0
    n = np.real(np.fft.ifft2(spec))
    n = (n - n.min()) / (n.max() - n.min())
    return n.astype(np.float32)


_TEX = {}


def tex(name, shape=(512, 512), beta=2.2, seed=0):
    k = (name, shape, beta, seed)
    if k not in _TEX:
        _TEX[k] = fbm_texture(shape, beta, seed)
    return _TEX[k]


def sample(t, rows, cols):
    """Bilinear wrap-around sample of texture t at float pixel coords."""
    return ndimage.map_coordinates(t, [rows, cols], order=1, mode="grid-wrap").astype(np.float32)


class Grid:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.a = w / h
        self.y = np.linspace(-1, 1, h, dtype=np.float32)[:, None]
        self.x = np.linspace(-self.a, self.a, w, dtype=np.float32)[None, :]
        self.px = 2.0 / h

    def X(self):
        return np.broadcast_to(self.x, (self.h, self.w))

    def Y(self):
        return np.broadcast_to(self.y, (self.h, self.w))


HEAT_STOPS = np.array([0.0, 0.12, 0.3, 0.5, 0.72, 0.9, 1.1])
HEAT_RGB = np.array([
    (0.0, 0.0, 0.0), (0.18, 0.02, 0.0), (0.62, 0.12, 0.01),
    (0.91, 0.45, 0.17), (1.0, 0.72, 0.36), (1.0, 0.92, 0.72), (1.0, 1.0, 0.96),
])


def heatmap(v):
    out = np.empty(v.shape + (3,), np.float32)
    for c in range(3):
        out[..., c] = np.interp(v, HEAT_STOPS, HEAT_RGB[:, c])
    return out


def blur(img, sigma):
    """Fast wide blur: downsample 4x, gaussian, upsample."""
    h, w = img.shape[:2]
    k = 4
    hh, ww = h // k * k, w // k * k
    small = img[:hh, :ww].reshape(hh // k, k, ww // k, k, -1).mean(axis=(1, 3))
    small = ndimage.gaussian_filter(small, (sigma / k, sigma / k, 0))
    big = ndimage.zoom(small, (h / small.shape[0], w / small.shape[1], 1), order=1)
    return big[:h, :w].astype(np.float32)


def bloom(img, sigma=18, amt=0.5, thresh=0.6):
    hi = np.clip(img - thresh, 0, None)
    return img + amt * blur(hi, sigma)


def vignette(g, strength=0.5):
    r = np.sqrt((g.x / g.a) ** 2 + g.y ** 2)
    return (1 - strength * smoothstep(0.5, 1.5, r))[..., None]


def capsule(g, p0, p1, r):
    """Anti-aliased coverage of a capsule between points p0 and p1."""
    (x0, y0), (x1, y1) = p0, p1
    X, Y = g.x, g.y
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy + 1e-9
    t = np.clip(((X - x0) * dx + (Y - y0) * dy) / L2, 0, 1)
    d = np.sqrt((X - x0 - t * dx) ** 2 + (Y - y0 - t * dy) ** 2)
    return np.clip((r - d) / g.px + 0.5, 0, 1)


def draw_poly_mask(g, polys, ss=2):
    """Polygons in normalised coords -> AA coverage mask (supersampled)."""
    im = Image.new("L", (g.w * ss, g.h * ss), 0)
    d = ImageDraw.Draw(im)
    for poly in polys:
        pts = [((x + g.a) / (2 * g.a) * g.w * ss, (y + 1) / 2 * g.h * ss) for x, y in poly]
        d.polygon(pts, fill=255)
    im = im.resize((g.w, g.h), Image.BOX)
    return np.asarray(im, np.float32) / 255.0


def over(dst, rgb, alpha):
    a = alpha[..., None] if alpha.ndim == 2 else alpha
    return dst * (1 - a) + rgb * a


# ------------------------------------------------------------------ footage


class FootagePlate:
    """Decodes a real clip once into memory at output res (cover-fit)."""

    def __init__(self, path, w, h, fx=0.5, fy=0.5, t_max=None):
        self.path, self.w, self.h = path, w, h
        info = json.loads(subprocess.check_output([
            "ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
            "stream=width,height:format=duration", "-of", "json", str(path)]))
        sw, sh = info["streams"][0]["width"], info["streams"][0]["height"]
        s = max(w / sw, h / sh)
        cw, ch = int(round(sw * s)), int(round(sh * s))
        ox, oy = int((cw - w) * fx), int((ch - h) * fy)
        vf = f"fps={C.FPS},scale={cw}:{ch}:flags=lanczos,crop={w}:{h}:{ox}:{oy},format=rgb24"
        cmd = ["ffmpeg", "-v", "error", "-i", str(path)]
        if t_max:
            cmd += ["-t", str(t_max)]
        cmd += ["-vf", vf, "-f", "rawvideo", "-"]
        raw = subprocess.check_output(cmd)
        self.frames = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)

    def frame(self, t):
        i = int(np.clip(round(t * C.FPS), 0, len(self.frames) - 1))
        return self.frames[i].astype(np.float32) / 255.0


# ------------------------------------------------------------------ placeholders


class Proc:
    """Base for procedural plates: render at half res."""
    scale = 0.5

    def __init__(self, w, h):
        self.W, self.H = w, h
        self.g = Grid(int(w * self.scale), int(h * self.scale))

    def frame(self, t):
        return self.draw(max(0.0, t))


class Black(Proc):
    def draw(self, t):
        return np.zeros((self.g.h, self.g.w, 3), np.float32) + np.array(C.BG, np.float32) / 255


class Flame(Proc):
    """Generic engine plume. mode: engine_fire | gimbal | liftoff."""

    def __init__(self, w, h, mode):
        super().__init__(w, h)
        self.mode = mode
        g = self.g
        self.vertical = g.a < 1 or mode == "liftoff"
        self.turb = tex("flame", (256, 1024), 2.0, 1)
        self.smoke = tex("smoke", (512, 512), 2.6, 2)

    def draw(self, t):
        g = self.g
        X, Y = g.X(), g.Y()
        m = self.mode
        ignite = 0.5 if m == "engine_fire" else -10
        on = smoothstep(ignite, ignite + 0.7, t)
        angle = 0.0
        if m == "gimbal":
            angle = np.radians(7) * np.sin(2 * np.pi * t / 1.7)
        if self.vertical:
            ox, oy = 0.0, (-0.45 if m != "liftoff" else -0.15)
            dirx, diry = np.sin(angle), np.cos(angle)  # pointing down
        else:
            ox, oy = -g.a * 0.62, -0.05
            dirx, diry = np.cos(angle), np.sin(angle)  # pointing right
        # shake on ignition
        if m == "engine_fire":
            k = on * 0.012
            ox += k * np.sin(t * 91.0)
            oy += k * np.cos(t * 77.0)
        u = (X - ox) * dirx + (Y - oy) * diry
        v = -(X - ox) * diry + (Y - oy) * dirx
        L = 2.4 * on + 1e-3
        r = 0.07 + 0.22 * np.clip(u, 0, None)
        ahead = smoothstep(-0.02, 0.04, u)
        rows = (v / r) * 40 + 128
        cols = (u * 260 - t * 900) % 1024
        n1 = sample(self.turb, rows, cols)
        n2 = sample(self.turb, rows * 1.9 + 50, (u * 520 - t * 1500) % 1024)
        turb = 0.55 * n1 + 0.45 * n2
        core = np.exp(-(v / r) ** 2 * 2.2)
        heat = core * np.exp(-np.clip(u, 0, None) / (L * 0.55)) * (0.35 + 1.25 * turb) * ahead
        # shock diamonds near the nozzle
        diam = np.cos(2 * np.pi * u / 0.23) ** 12 * np.exp(-(v / (0.35 * r)) ** 2) * np.exp(-u / 0.9)
        heat = heat * 1.15 + 0.55 * diam * ahead * on
        heat *= on
        flash = np.exp(-((t - ignite) / 0.12) ** 2) if m == "engine_fire" else 0
        img = heatmap(np.clip(heat, 0, 1.1))
        glow = np.exp(-np.clip(u, 0, None) / 1.4) * np.exp(-(v / 1.2) ** 2)
        # smoke lit by the flame
        sm = sample(self.smoke, (Y * 180 + t * 12) % 512, (X * 180 - t * 30) % 512)
        smoke_l = (sm ** 2) * glow * on * 0.35
        img += smoke_l[..., None] * np.array([0.9, 0.42, 0.16])
        img += (flash * 0.6 * glow)[..., None] * np.array([1.0, 0.7, 0.4])
        # nozzle bell (generic cone), dark with warm rim
        bell = []
        if self.vertical:
            bell = [[(ox - 0.06, oy - 0.22), (ox + 0.06, oy - 0.22), (ox + 0.11, oy + 0.01), (ox - 0.11, oy + 0.01)]]
        else:
            bell = [[(ox - 0.22, oy - 0.06), (ox - 0.22, oy + 0.06), (ox + 0.01, oy + 0.11), (ox + 0.01, oy - 0.11)]]
        bm = draw_poly_mask(g, bell)
        rim = np.clip(bm - ndimage.shift(bm, (-2 * diry, -2 * dirx), order=1), 0, 1) * on
        img = over(img, np.array([0.03, 0.028, 0.026]), bm)
        img += rim[..., None] * np.array([0.9, 0.5, 0.2]) * 0.8
        if m == "liftoff":
            # vehicle body above the nozzle, climbing out of frame; sky tracks down
            body = [[(ox - 0.13, -1.2), (ox + 0.13, -1.2), (ox + 0.13, oy - 0.2), (ox - 0.13, oy - 0.2)]]
            bmask = draw_poly_mask(g, body)
            shade = 0.05 + 0.12 * np.clip(1 - np.abs(X - ox - 0.04) / 0.13, 0, 1)
            under = np.exp(-np.clip(oy - 0.2 - Y, 0, None) / 0.25) * 0.5
            col = shade[..., None] * np.array([1, 0.97, 0.93]) + under[..., None] * np.array([1, 0.55, 0.22])
            sky = (0.02 + 0.05 * smoothstep(-1, 1.2, Y))[..., None] * np.array([0.55, 0.6, 0.8])
            base = sky + img * 0  # sky under everything
            billow = sample(self.smoke, (Y * 140 - t * 220) % 512, (X * 140) % 512)
            cloud = smoothstep(0.35, 1.0, Y - t * 0.12 + 0.2 * billow) * (0.25 + 0.6 * billow)
            cloudcol = cloud[..., None] * (np.array([0.35, 0.3, 0.27]) + 0.9 * np.exp(-np.abs(X) / 0.5)[..., None] * np.array([0.9, 0.45, 0.15]))
            img = base + cloudcol + img
            img = over(img, col, bmask)
        img = bloom(img, 22, 0.55, 0.55)
        return img * vignette(g, 0.55)


class LaunchPad(Proc):
    def __init__(self, w, h):
        super().__init__(w, h)
        g = self.g
        a = g.a
        tx = a * 0.28 if a > 1 else 0.18
        polys = [[(tx - 0.045, 0.42), (tx + 0.045, 0.42), (tx + 0.03, -0.55), (tx - 0.03, -0.55)],
                 [(tx - 0.012, -0.55), (tx + 0.012, -0.55), (tx + 0.006, -0.72), (tx - 0.006, -0.72)],
                 [(-a, 0.40), (a, 0.40), (a, 1.0), (-a, 1.0)],
                 [(tx - 0.30, 0.36), (tx + 0.22, 0.36), (tx + 0.25, 0.42), (tx - 0.33, 0.42)]]
        self.sil = draw_poly_mask(g, polys, 3)
        # lattice: cut small windows out of the tower for a truss read
        win = []
        for k in range(22):
            y0 = -0.53 + k * 0.043
            win.append([(tx - 0.02, y0), (tx + 0.02, y0 + 0.02), (tx - 0.02, y0 + 0.04)])
        self.win = draw_poly_mask(g, win, 3)
        self.haze = tex("haze", (512, 512), 3.0, 3)
        self.tx = tx

    def draw(self, t):
        g = self.g
        Y, X = g.Y(), g.X()
        horizon = 0.40
        sky = np.empty((g.h, g.w, 3), np.float32)
        p = smoothstep(-1.0, horizon, Y)
        top = np.array([0.018, 0.022, 0.04])
        mid = np.array([0.10, 0.085, 0.10])
        low = np.array([0.62, 0.33, 0.15])
        sky[:] = top + (mid - top) * smoothstep(0, 0.6, p)[..., None] + (low - mid) * smoothstep(0.6, 1.0, p)[..., None]
        sun = np.exp(-(((X + g.a * 0.35) / 0.9) ** 2 + ((Y - horizon) / 0.12) ** 2))
        sky += sun[..., None] * np.array([0.5, 0.25, 0.08])
        hz = sample(self.haze, (Y * 60) % 512, (X * 60 + t * 3) % 512)
        sky *= (0.9 + 0.2 * hz)[..., None]
        sil = np.clip(self.sil - self.win * 0.85 * (Y < 0.35), 0, 1)
        img = over(sky, np.array([0.012, 0.011, 0.012]), sil)
        # warning lights on the tower
        for k, yy in enumerate((-0.7, -0.3, 0.1)):
            blink = 0.6 + 0.4 * np.sin(t * 2.0 + k)
            d = ((X - self.tx) ** 2 + (Y - yy) ** 2)
            img += (np.exp(-d / 0.00008) * 1.4 + np.exp(-d / 0.003) * 0.12)[..., None] * np.array([1.0, 0.35, 0.12]) * blink
        return img * vignette(g, 0.45)


class Drill(Proc):
    def __init__(self, w, h):
        super().__init__(w, h)
        g = self.g
        n = tex("rock", (512, 512), 2.4, 4)
        n2 = tex("rock2", (512, 512), 1.6, 5)
        hgt = 0.7 * n + 0.3 * n2
        gy, gx = np.gradient(hgt)
        self.shade = np.clip(0.5 + 18 * (gx * 0.6 - gy * 0.8), 0, 1)
        self.alb = 0.35 + 0.65 * n2
        self.dust = tex("dust", (512, 512), 2.0, 6)

    def draw(self, t):
        g = self.g
        z = 1 + 0.035 * t
        X, Y = g.X() / z, g.Y() / z
        rows, cols = (Y * 200) % 512, (X * 200) % 512
        shade = sample(self.shade, rows, cols)
        alb = sample(self.alb, rows, cols)
        light = np.exp(-((X + 0.3) ** 2 + (Y + 0.5) ** 2) / 1.8)
        rock = (shade * alb * (0.18 + 0.4 * light))[..., None] * np.array([0.72, 0.6, 0.5])
        tip_y = 0.12 + 0.03 * t
        bw = 0.16
        # bore glow where the bit meets rock
        d = np.sqrt((X / 1.6) ** 2 + (Y - tip_y) ** 2)
        glow = np.exp(-d / 0.09) * (0.8 + 0.2 * np.sin(t * 13))
        rock += glow[..., None] * np.array([1.0, 0.45, 0.15]) * 0.9
        # bit: cylinder from top edge to tip with rotating helical flutes
        inside = np.clip((bw - np.abs(X)) / g.px + 0.5, 0, 1) * (Y < tip_y)
        cone = np.clip((0.08 - np.abs(X) - (Y - tip_y) * 0.9) / g.px + 0.5, 0, 1) * (Y >= tip_y) * (Y < tip_y + 0.08)
        body = np.clip(inside + cone, 0, 1)
        cyl = np.sqrt(np.clip(1 - (X / bw) ** 2, 0, 1))
        flute = 0.5 + 0.5 * np.sin((Y * 14 + np.arcsin(np.clip(X / bw, -1, 1)) * 2) - t * 9)
        metal = (0.05 + 0.25 * cyl * (0.5 + 0.5 * flute) * (0.4 + 0.6 * light))[..., None] * np.array([0.8, 0.78, 0.75])
        metal += (np.exp(-(Y - tip_y) ** 2 / 0.01) * cyl)[..., None] * np.array([0.9, 0.4, 0.1]) * 0.6
        img = over(rock, metal, body)
        # drifting dust and heat haze
        du = sample(self.dust, (Y * 120 - t * 40) % 512, (X * 120 + t * 25) % 512)
        img += (smoothstep(0.55, 1, du) * np.exp(-d / 0.4) * 0.35)[..., None] * np.array([0.8, 0.55, 0.35])
        img = bloom(img, 16, 0.5, 0.45)
        return img * vignette(g, 0.6)


class Battery(Proc):
    def __init__(self, w, h):
        super().__init__(w, h)
        g = self.g
        self.n = 5 if g.a > 1 else 3
        self.cw = 0.19 if g.a > 1 else 0.2
        span = self.n * self.cw * 1.9
        self.xs = [(-span / 2 + (i + 0.5) * span / self.n) for i in range(self.n)]

    def draw(self, t):
        g = self.g
        X, Y = g.X(), g.Y()
        img = np.zeros((g.h, g.w, 3), np.float32)
        img += (0.012 + 0.02 * np.exp(-(X ** 2) / 1.5) * smoothstep(1, -1, Y))[..., None] * np.array([1, 0.9, 0.8])
        top, bot = -0.55, 0.55
        for i, cx in enumerate(self.xs):
            r = self.cw / 2
            xn = (X - cx) / r
            inside = np.clip((1 - np.abs(xn)) * r / g.px + 0.5, 0, 1) * np.clip((Y - top) / g.px, 0, 1) * np.clip((bot - Y) / g.px, 0, 1)
            cyl = np.sqrt(np.clip(1 - xn ** 2, 0, 1))
            spec = np.exp(-((xn - 0.45) / 0.12) ** 2)
            body = (0.03 + 0.08 * cyl + 0.25 * spec)[..., None] * np.array([0.8, 0.82, 0.85])
            # charge window with rising fill
            level = np.clip(0.08 + (t * 0.3 + 0.07 * i) % 1.0, 0, 1)
            fy = bot - 0.06 - level * (bot - top - 0.12)
            win = (np.abs(xn) < 0.3) * (Y > top + 0.06) * (Y < bot - 0.06)
            fill = win * (Y > fy)
            heatv = 0.55 + 0.25 * smoothstep(bot, fy, Y)
            fc = heatmap(heatv) * fill[..., None] * (0.6 + 0.4 * cyl)[..., None]
            meniscus = win * np.exp(-((Y - fy) / 0.006) ** 2) * 1.5
            body = body * (1 - win[..., None] * 0.7) + fc + meniscus[..., None] * np.array([1, 0.9, 0.7])
            img = over(img, body, inside)
            # cap
            cap = np.clip((1 - ((X - cx) / (r * 0.5)) ** 2 - ((Y - top + 0.02) / 0.02) ** 2) * 6, 0, 1)
            img = over(img, np.array([0.35, 0.33, 0.3]), cap)
            # cable up out of frame
            cab = capsule(g, (cx, top - 0.02), (cx + 0.05 * np.sin(i), -1.1), 0.007)
            img = over(img, np.array([0.05, 0.045, 0.04]), cab)
        # floor reflection about y = bot
        fr = int(round((bot + 1) / 2 * g.h))
        rows = np.arange(fr, g.h)
        src = np.clip(2 * fr - rows, 0, g.h - 1)
        img[fr:] = img[fr:] * 0.3 + img[src] * 0.14
        img = bloom(img, 14, 0.55, 0.5)
        return img * vignette(g, 0.5)


class Quantum(Proc):
    def __init__(self, w, h):
        super().__init__(w, h)
        k = 1.0 if self.g.a > 1 else 0.78
        self.tiers = [(y * k, r * k) for y, r in
                      [(-0.78, 0.46), (-0.42, 0.38), (-0.08, 0.30), (0.22, 0.23), (0.48, 0.16)]]
        self.brush = tex("brush", (64, 1024), 1.2, 7)

    def draw(self, t):
        g = self.g
        X, Y = g.X(), g.Y()
        orbit = 0.22 * t
        img = np.zeros((g.h, g.w, 3), np.float32)
        img += (0.015 + 0.05 * np.exp(-((X - 0.8) ** 2 + (Y + 0.2) ** 2) / 1.2))[..., None] * np.array([0.9, 0.7, 0.45])
        gold = np.array([0.79, 0.62, 0.28])
        copper = np.array([0.72, 0.38, 0.2])

        def rods(front):
            nonlocal img
            for k in range(len(self.tiers) - 1):
                (y0, r0), (y1, r1) = self.tiers[k], self.tiers[k + 1]
                for j in range(6):
                    th = orbit + j * np.pi / 3 + k * 0.3
                    z = np.sin(th)
                    if (z > 0) != front:
                        continue
                    xa, xb = r0 * 0.8 * np.cos(th), r1 * 0.8 * np.cos(th)
                    m = capsule(g, (xa, y0 + 0.03), (xb, y1), 0.008)
                    lum = 0.35 + 0.65 * (0.5 + 0.5 * z)
                    img = over(img, gold * lum, m * (0.6 + 0.4 * front))
                    # coiled cable beside the rod
                    yy = np.clip((Y - y0) / (y1 - y0), 0, 1)
                    cx = xa + (xb - xa) * yy + 0.02 * np.cos(th + 1.2) + 0.008 * np.sin(yy * 40 + j)
                    cm = np.clip((0.005 - np.abs(X - cx)) / g.px + 0.5, 0, 1) * (Y > y0) * (Y < y1)
                    img = over(img, copper * lum, cm * (0.5 + 0.5 * front))

        rods(False)
        for (yc, r) in self.tiers:
            ry = r * 0.16
            thick = 0.035
            xn = X / r
            side = (np.abs(xn) < 1) * (Y > yc) * (Y < yc + thick + ry * np.sqrt(np.clip(1 - xn ** 2, 0, 1)))
            topf = np.clip((1 - xn ** 2 - ((Y - yc) / ry) ** 2) * 8, 0, 1)
            aa = np.clip((1 - np.abs(xn)) * r / g.px + 0.5, 0, 1)
            br = sample(self.brush, np.full_like(X, 10.0) + Y * 5, ((np.arcsin(np.clip(xn, -1, 1)) + orbit) * 160) % 1024)
            spec = np.exp(-((xn - 0.55) / 0.18) ** 2)
            shade = 0.25 + 0.45 * (0.5 + 0.5 * xn) + 0.9 * spec
            sc = gold * (shade * (0.8 + 0.4 * br))[..., None]
            img = over(img, sc * 0.85, side * aa)
            img = over(img, gold * (0.55 + 0.45 * br)[..., None] * 1.1, topf)
        rods(True)
        img = bloom(img, 18, 0.6, 0.5)
        return img * vignette(g, 0.55)


class Robot(Proc):
    def draw(self, t):
        g = self.g
        X, Y = g.X(), g.Y()
        img = np.zeros((g.h, g.w, 3), np.float32)
        # hall: floor gradient + back light + vertical light strips
        img += (0.03 + 0.16 * np.exp(-((X - 0.1) ** 2 / 0.8 + (Y + 0.1) ** 2 / 0.25)))[..., None] * np.array([1.0, 0.8, 0.6])
        for sx in (-1.3, -0.7, 0.9, 1.5):
            img += (np.exp(-((X - sx) / 0.01) ** 2) * smoothstep(0.4, -0.9, Y) * 0.3)[..., None] * np.array([1, 0.85, 0.7])
        floor = smoothstep(0.5, 0.56, Y)
        img = img * (1 - floor[..., None]) + floor[..., None] * (0.02 + 0.05 * np.exp(-(X - 0.1) ** 2 / 0.3))[..., None] * np.array([1, 0.8, 0.6])
        # walk cycle, side view
        s = 0.62
        ph = 2 * np.pi * 0.75 * t
        hx = -0.1 + 0.07 * t if g.a > 1 else -0.02 + 0.03 * t
        hy = 0.02 + 0.012 * np.cos(2 * ph)
        T, S = 0.28 * s * 1.6, 0.27 * s * 1.6
        cov = np.zeros((g.h, g.w), np.float32)
        parts = []
        for side, off in ((0, 0.0), (1, np.pi)):
            a_h = 0.42 * np.sin(ph + off)
            a_k = 0.55 * max(0.0, np.sin(ph + off + 1.3))
            kx, ky = hx + T * np.sin(a_h), hy + T * np.cos(a_h)
            fx, fy = kx + S * np.sin(a_h - a_k), ky + S * np.cos(a_h - a_k)
            parts += [((hx, hy), (kx, ky), 0.035), ((kx, ky), (fx, fy), 0.03), ((fx - 0.02, fy + 0.02), (fx + 0.06, fy + 0.02), 0.018)]
            a_s = -0.35 * np.sin(ph + off)
            shx, shy = hx + 0.01, hy - 0.42 * s * 1.6 + 0.04
            ex, ey = shx + 0.2 * np.sin(a_s), shy + 0.2 * np.cos(a_s)
            wx, wy = ex + 0.18 * np.sin(a_s + 0.4), ey + 0.18 * np.cos(a_s + 0.4)
            parts += [((shx, shy), (ex, ey), 0.028), ((ex, ey), (wx, wy), 0.024)]
        top = hy - 0.42 * s * 1.6
        parts += [((hx, hy - 0.02), (hx + 0.01, hy - 0.06), 0.05)]
        for p0, p1, r in parts:
            cov = np.maximum(cov, capsule(g, p0, p1, r))
        # mechanical torso (trapezoid) and boxy helmet: reads as a machine, no face
        torso = [[(hx - 0.075, top + 0.02), (hx + 0.095, top + 0.02), (hx + 0.06, hy - 0.05), (hx - 0.05, hy - 0.05)]]
        head = [[(hx - 0.035, top - 0.13), (hx + 0.06, top - 0.13), (hx + 0.065, top - 0.03), (hx - 0.035, top - 0.03)]]
        cov = np.maximum(cov, draw_poly_mask(g, torso + head, 3))
        visor = capsule(g, (hx + 0.015, top - 0.085), (hx + 0.062, top - 0.085), 0.006)
        joints = np.zeros_like(cov)
        for (p0, p1, r) in parts[:-1]:
            joints = np.maximum(joints, capsule(g, p1, p1, r * 0.55))
        # rim light from behind-right
        sh = ndimage.shift(cov, (2, -3), order=1)
        rim = np.clip(cov - sh, 0, 1)
        img = over(img, np.array([0.015, 0.014, 0.013]), cov)
        img += rim[..., None] * np.array([1.0, 0.82, 0.6]) * 1.6
        jr = np.clip(joints - ndimage.shift(joints, (1, -1), order=1), 0, 1)
        img += jr[..., None] * np.array([0.8, 0.62, 0.35]) * 0.6
        img += visor[..., None] * np.array([1.0, 0.72, 0.3]) * 1.2
        # contact shadow
        img *= (1 - 0.6 * np.exp(-((X - hx) / 0.25) ** 2 - ((Y - 0.56) / 0.02) ** 2))[..., None]
        img = bloom(img, 12, 0.4, 0.4)
        return img * vignette(g, 0.55)


class Forge(Proc):
    HIT = 1.25

    def __init__(self, w, h):
        super().__init__(w, h)
        rng = np.random.default_rng(11)
        n = 420
        ang = rng.uniform(-np.pi, 0, n)
        spd = rng.uniform(0.6, 2.6, n)
        self.vx = np.cos(ang) * spd * rng.choice([-1, 1], n) * 1.3
        self.vy = np.sin(ang) * spd * 0.9
        self.x0 = rng.uniform(-0.25, 0.25, n)
        self.life = rng.uniform(0.35, 1.2, n)
        self.mottle = tex("mottle", (256, 256), 2.2, 12)

    def draw(self, t):
        g = self.g
        X, Y = g.X(), g.Y()
        img = np.zeros((g.h, g.w, 3), np.float32) + 0.008
        dt = t - self.HIT
        squash = 1.0 if dt < 0 else 1.0 - 0.28 * smoothstep(0, 0.05, dt)
        bw, bh = 0.3 / squash ** 0.5, 0.11 * squash
        by = 0.28
        # ram position: slow descent, fast strike, slow retreat
        if dt < 0:
            ry = by - bh - 0.9 * (1 - smoothstep(-1.25, 0, dt) ** 3)
        else:
            ry = by - bh - 0.25 * smoothstep(0.15, 1.2, dt)
        glow_amt = 1.0 + 1.8 * np.exp(-max(dt, 0) / 0.08) * (dt >= 0)
        # anvil
        anvil = draw_poly_mask(g, [[(-0.55, by + 0.11), (0.55, by + 0.11), (0.62, 1.1), (-0.62, 1.1)]])
        img = over(img, np.array([0.04, 0.037, 0.035]), anvil)
        # billet
        m = sample(self.mottle, (Y * 150) % 256, (X * 150 + t * 4) % 256)
        bill = np.clip((bw - np.abs(X)) / g.px, 0, 1) * np.clip((bh - np.abs(Y - (by + 0.11 - bh))) / g.px, 0, 1)
        edge = np.clip(np.minimum(bw - np.abs(X), bh - np.abs(Y - (by + 0.11 - bh))) / 0.05, 0, 1)
        heatv = (0.55 + 0.35 * edge + 0.1 * m)
        img = over(img, heatmap(heatv), bill)
        # ram
        ram = draw_poly_mask(g, [[(-0.5, -1.2), (0.5, -1.2), (0.5, ry), (-0.5, ry)]])
        lit = np.exp(-np.clip(ry - Y, 0, None) / 0.05) * np.exp(-np.clip(ry - (by + 0.11 - 2 * bh), 0, None) / 0.3)
        ramc = (0.035 + 0.02 * smoothstep(-0.5, 0.5, X))[..., None] * np.array([0.9, 0.9, 0.92]) + lit[..., None] * np.array([0.9, 0.35, 0.1]) * 0.8
        img = over(img, ramc, ram)
        # glow around billet
        d = np.sqrt((X / 1.5) ** 2 + (Y - by) ** 2)
        img += (np.exp(-d / 0.25) * 0.25 * glow_amt)[..., None] * np.array([1, 0.4, 0.1])
        # sparks
        if dt > 0:
            layer = Image.new("L", (g.w, g.h), 0)
            dr = ImageDraw.Draw(layer)
            alive = dt < self.life
            for x0, vx, vy, lf in zip(self.x0[alive], self.vx[alive], self.vy[alive], self.life[alive]):
                def pos(tt):
                    return (np.sign(x0) * bw + vx * tt, by - 0.02 + vy * tt + 2.2 * tt * tt)
                p1, p0 = pos(dt), pos(max(0, dt - 0.035))
                fade = 1 - dt / lf
                c = [((px + g.a) / (2 * g.a) * g.w, (py + 1) / 2 * g.h) for px, py in (p0, p1)]
                dr.line(c, fill=int(255 * fade), width=1)
            sp = np.asarray(layer, np.float32) / 255
            img += sp[..., None] * np.array([1.0, 0.75, 0.35]) * 2.0
        img = bloom(img, 16, 0.7, 0.45)
        return img * vignette(g, 0.55)


class Ingot(Proc):
    def __init__(self, w, h):
        super().__init__(w, h)
        g = self.g
        s = 1.0 if g.a > 1 else 0.8
        tw, bw, hh, dp = 0.42 * s, 0.52 * s, 0.14 * s, 0.1 * s
        cy = 0.12
        self.top = draw_poly_mask(g, [[(-tw, cy - hh - dp), (tw, cy - hh - dp), (bw, cy - hh + dp * 0.4), (-bw, cy - hh + dp * 0.4)]], 3)
        self.front = draw_poly_mask(g, [[(-bw, cy - hh + dp * 0.4), (bw, cy - hh + dp * 0.4), (bw * 1.04, cy + hh), (-bw * 1.04, cy + hh)]], 3)
        self.cy = cy
        self.mottle = tex("ingot", (256, 256), 2.0, 13)
        self.shim = tex("shimmer", (256, 256), 2.8, 14)

    def draw(self, t):
        g = self.g
        X, Y = g.X(), g.Y()
        z = 1 + 0.02 * t
        m = sample(self.mottle, (Y * 120 / z) % 256, (X * 120 / z + t * 2) % 256)
        img = np.zeros((g.h, g.w, 3), np.float32)
        edge_dark = 1 - 0.3 * smoothstep(0.25, 0.55, np.abs(X))
        img = over(img, heatmap((0.78 + 0.12 * m) * edge_dark), self.top)
        img = over(img, heatmap((0.62 + 0.12 * m) * edge_dark), self.front)
        img = bloom(img, 26, 0.9, 0.35)
        # heat shimmer: displace everything above the ingot
        n = sample(self.shim, (Y * 90 + t * 60) % 256, (X * 90) % 256) - 0.5
        amt = smoothstep(self.cy - 0.1, self.cy - 0.7, Y) * 0 + np.exp(-np.abs(Y - (self.cy - 0.35)) / 0.35)
        dy = n * 6 * amt
        rr, cc = np.mgrid[0:g.h, 0:g.w].astype(np.float32)
        for c in range(3):
            img[..., c] = ndimage.map_coordinates(img[..., c], [rr + dy, cc + dy * 0.5], order=1, mode="nearest")
        return img * vignette(g, 0.4)


class Docking(Proc):
    CONTACT = 3.4

    def __init__(self, w, h):
        super().__init__(w, h)
        g = self.g
        rng = np.random.default_rng(21)
        self.stars = np.zeros((g.h, g.w), np.float32)
        n = int(g.w * g.h / 900)
        self.stars[rng.integers(0, g.h, n), rng.integers(0, g.w, n)] = rng.uniform(0.1, 0.6, n) ** 2
        self.clouds = tex("clouds", (512, 1024), 2.3, 22)

    def craft(self, cx, cy, s, facing):
        """Generic module: cylinder + truss + panels. facing=+1 points right."""
        f = facing
        polys_body = [[(cx - 0.22 * s * f, cy - 0.07 * s), (cx + 0.12 * s * f, cy - 0.07 * s),
                       (cx + 0.12 * s * f, cy + 0.07 * s), (cx - 0.22 * s * f, cy + 0.07 * s)],
                      [(cx + 0.12 * s * f, cy - 0.045 * s), (cx + 0.19 * s * f, cy - 0.035 * s),
                       (cx + 0.19 * s * f, cy + 0.035 * s), (cx + 0.12 * s * f, cy + 0.045 * s)]]
        panels = []
        for sgn in (-1, 1):
            y0 = cy + sgn * 0.075 * s
            y1 = cy + sgn * 0.36 * s
            for k in range(2):
                x0 = cx + (-0.17 + k * 0.13) * s * f
                panels.append([(x0, y0 + sgn * 0.02 * s), (x0 + 0.11 * s * f, y0 + sgn * 0.02 * s),
                               (x0 + 0.11 * s * f, y1), (x0, y1)])
        return polys_body, panels

    def draw(self, t):
        g = self.g
        X, Y = g.X(), g.Y()
        img = self.stars[..., None] * np.array([1, 0.97, 0.9])
        # Earth limb at the bottom
        R, cy = 3.0, 3.72 if g.a > 1 else 3.9
        dist = np.sqrt(X ** 2 + (Y - cy) ** 2)
        earth = np.clip((R - dist) / g.px + 0.5, 0, 1)
        cl = sample(self.clouds, ((Y - cy) * 160) % 512, (X * 120 + t * 4) % 1024)
        surf = np.array([0.03, 0.06, 0.12]) + smoothstep(0.5, 0.8, cl)[..., None] * np.array([0.55, 0.55, 0.55])
        sunside = smoothstep(-1.5, 1.0, -X)
        surf = surf * (0.25 + 0.85 * sunside)[..., None] + (sunside * 0.1)[..., None] * np.array([1, 0.7, 0.35])
        img = over(img, surf, earth)
        atm = np.exp(-np.abs(dist - R) / 0.02) * 0.6
        img += atm[..., None] * (np.array([0.35, 0.55, 0.9]) * 0.6 + sunside[..., None] * np.array([0.8, 0.55, 0.25]) * 0.5)
        # approach: B decelerates to soft contact, then both drift together
        s = 1.0 if g.a > 1 else 0.82
        gap_px = 0.38 * s
        p = np.clip(t / self.CONTACT, 0, 1)
        gap = gap_px * (1 - p) ** 2.2 if t < self.CONTACT else 0.0
        drift = 0.01 * t
        ax = -0.19 * s + drift
        bx = ax + 0.38 * s + gap
        yA = -0.12 + 0.004 * np.sin(t * 0.7)
        for (cx, fac) in ((ax, 1), (bx, -1)):
            body, panels = self.craft(cx, yA, s, fac)
            pm = draw_poly_mask(g, panels, 3)
            grid = 0.6 + 0.4 * ((np.sin(Y * 260) > 0.85) | (np.sin(X * 260) > 0.85))
            img = over(img, (np.array([0.05, 0.05, 0.06]) + 0.25 * sunside[..., None] * np.array([0.9, 0.7, 0.35])) * grid[..., None], pm)
            bm = draw_poly_mask(g, body, 3)
            shade = 0.35 + 0.65 * smoothstep(yA + 0.07 * s, yA - 0.07 * s, Y)
            col = shade[..., None] * np.array([0.82, 0.8, 0.77]) + (smoothstep(0.1, 1, sunside) * 0.2)[..., None] * np.array([1, 0.75, 0.35])
            img = over(img, col, bm)
        if t >= self.CONTACT:
            flash = np.exp(-(t - self.CONTACT) / 0.25) * 0.4
            d = (X - (ax + 0.19 * s)) ** 2 + (Y - yA) ** 2
            img += (np.exp(-d / 0.002) * flash)[..., None] * np.array([1, 0.85, 0.6])
        img = bloom(img, 14, 0.4, 0.6)
        return img * vignette(g, 0.35)


PROCEDURAL = {
    "black": Black,
    "engine_fire": lambda w, h: Flame(w, h, "engine_fire"),
    "gimbal": lambda w, h: Flame(w, h, "gimbal"),
    "liftoff": lambda w, h: Flame(w, h, "liftoff"),
    "launch_pad": LaunchPad,
    "drill": Drill,
    "battery": Battery,
    "quantum": Quantum,
    "robot": Robot,
    "forge": Forge,
    "ingot": Ingot,
    "docking": Docking,
}


def find_footage(src):
    for sub in ("raw", "generated"):
        for ext in (".mp4", ".mov", ".webm"):
            p = C.FOOTAGE / sub / f"{src}{ext}"
            if p.exists():
                return p
    return None


def get_plate(src, w, h, fx=0.5):
    if src != "black":
        p = find_footage(src)
        if p:
            return FootagePlate(p, w, h, fx=fx), "footage:" + str(p.relative_to(C.ROOT))
    return PROCEDURAL[src](w, h), "placeholder"
