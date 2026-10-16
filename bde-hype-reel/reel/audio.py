"""Sound: placeholder score + SFX, ducking, silence beat, loudness.

Everything here is synthesised from scratch (no third-party samples), so it
carries no licence obligations. When a licensed track is supplied at
audio/music/track.wav (or .mp3/.flac/.m4a), it replaces the synthesised
music bus; `MUSIC_OFFSET` picks where in the track the edit starts.
"""
import subprocess

import numpy as np
import pyloudnorm as pyln
from scipy import signal
from scipy.io import wavfile
from scipy.ndimage import minimum_filter1d

from . import config as C
from .edl import MASTER_BPM, CUT_BPM

SR = C.SR
RNG = np.random.default_rng(7)
TARGET_LUFS = -14.0
CEILING_DB = -2.5  # true-peak ceiling (4x oversampled); AAC adds up to ~1.3 dB on transients
MUSIC_OFFSET = {"master": 0.0, "cutdown": 0.0}


# ------------------------------------------------------------------ primitives

def tt(dur):
    return np.arange(int(dur * SR)) / SR


def noise(dur, stereo=True):
    n = RNG.standard_normal((int(dur * SR), 2 if stereo else 1)).astype(np.float32)
    return n


def filt(x, kind, f, order=4):
    sos = signal.butter(order, f, kind, fs=SR, output="sos")
    return signal.sosfilt(sos, x, axis=0).astype(np.float32)


def st(x):
    return np.stack([x, x], axis=1).astype(np.float32) if x.ndim == 1 else x


def sine_sweep(t, f):
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def kick(heavy=False):
    t = tt(0.6 if heavy else 0.45)
    f = 44 + (140 if heavy else 110) * np.exp(-t / 0.035)
    body = sine_sweep(t, f) * np.exp(-t / (0.26 if heavy else 0.17))
    click = filt(noise(0.006, False)[:, 0], "bandpass", [1500, 5000], 2) * np.hanning(int(0.006 * SR))
    body[: len(click)] += click * 0.2
    body[:96] *= np.linspace(0, 1, 96)  # 2ms attack: no codec ringing on the onset
    return st(np.tanh(body * 1.6) * 0.9)


def hat():
    t = tt(0.06)
    return filt(noise(0.06), "highpass", 7000) * np.exp(-t / 0.018)[:, None] * 0.12


def sub_drop(big=False):
    dur = 3.2 if big else 2.2
    t = tt(dur)
    f = 26 + (84 if big else 62) * np.exp(-t / (0.6 if big else 0.4))
    env = np.exp(-t / (1.3 if big else 0.8)) * (1 - np.exp(-t / 0.004))
    return st(np.tanh(sine_sweep(t, f) * env * 1.8) * (1.0 if big else 0.8))


def impact(big=False):
    dur = 3.0
    t = tt(dur)
    thump = np.sin(2 * np.pi * 48 * t) * np.exp(-t / 0.3)
    burst = filt(noise(dur), "bandpass", [60, 3500]) * np.exp(-t / 0.06)[:, None] * 0.6
    tail = filt(noise(dur), "lowpass", 1400) * np.exp(-t / 0.9)[:, None] * 0.12
    out = st(thump) + burst + tail
    return np.tanh(out * (1.6 if big else 1.2)) * 0.9


def roar(dur):
    n = noise(dur)
    brown = np.cumsum(n, axis=0)
    brown -= filt(brown, "lowpass", 8)  # remove DC drift
    brown /= np.abs(brown).max() + 1e-9
    body = filt(brown, "lowpass", 700) * 2.2
    rumble = filt(noise(dur), "bandpass", [25, 90]) * 1.2
    crack_src = (RNG.random((len(n), 2)) > 0.9985).astype(np.float32) * RNG.standard_normal((len(n), 2))
    crack = filt(crack_src, "bandpass", [300, 3000]) * 1.5
    hiss = filt(noise(dur), "bandpass", [1500, 6000]) * 0.08
    t = tt(dur)
    am = 1 + 0.15 * filt(RNG.standard_normal(len(t)).astype(np.float32), "lowpass", 6, 2) * 8
    x = (body + rumble + crack + hiss) * am[:, None]
    x /= np.abs(x).max() + 1e-9
    return np.tanh(x * 1.5) * 0.9


def whoosh(dur=1.1):
    t = tt(dur)
    n = noise(dur)
    out = np.zeros_like(n)
    # time-varying bandpass via overlapped chunks
    hop = 1024
    win = np.hanning(2 * hop)[:, None]
    for i in range(0, len(t) - 2 * hop, hop):
        fc = 180 + 1400 * np.sin(np.pi * i / len(t)) ** 2
        seg = filt(n[i:i + 2 * hop], "bandpass", [fc * 0.6, fc * 1.6], 2)
        out[i:i + 2 * hop] += seg * win
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 2
    pan = np.clip(t / dur, 0, 1)
    out[:, 0] *= env * (1 - 0.5 * pan)
    out[:, 1] *= env * (0.5 + 0.5 * pan)
    return out * 0.9


def riser(dur=1.0):
    t = tt(dur)
    n = filt(noise(dur), "highpass", 800)
    tone = np.sin(2 * np.pi * np.cumsum(200 + 900 * (t / dur) ** 2) / SR)
    env = (t / dur) ** 2.5
    return (n * 0.25 + st(tone) * 0.12) * env[:, None]


def press_slam():
    pre = 0.6
    dur = pre + 2.5
    t = tt(dur)
    out = np.zeros((len(t), 2), np.float32)
    hiss = filt(noise(pre), "bandpass", [1800, 7000]) * (tt(pre) / pre)[:, None] ** 2 * 0.25
    out[: len(hiss)] += hiss
    i0 = int(pre * SR)
    th = tt(dur - pre)
    thump = np.sin(2 * np.pi * 40 * th) * np.exp(-th / 0.35) * 1.2
    clang = sum(np.sin(2 * np.pi * f * th + k) * np.exp(-th / d) * a for k, (f, d, a) in enumerate(
        [(183, 0.9, 0.3), (441, 0.6, 0.25), (817, 0.45, 0.18), (1297, 0.3, 0.12), (2211, 0.2, 0.08)]))
    burst = filt(noise(dur - pre), "bandpass", [100, 5000]) * np.exp(-th / 0.04)[:, None]
    out[i0:] += st(thump + clang) + burst
    return np.tanh(out * 1.4) * 0.95, pre


def clunk():
    t = tt(1.2)
    x = np.sin(2 * np.pi * 92 * t) * np.exp(-t / 0.12)
    x += sum(np.sin(2 * np.pi * f * t) * np.exp(-t / 0.28) * a for f, a in [(310, 0.2), (742, 0.12), (1187, 0.06)])
    latch = np.zeros_like(t)
    j = int(0.09 * SR)
    latch[j:j + 200] = RNG.standard_normal(200) * np.exp(-np.arange(200) / 40) * 0.3
    return filt(st(x + latch), "lowpass", 2500) * 0.8


# ------------------------------------------------------------------ music bus

def drone(dur, swell=None):
    """Low D drone with an optional filter swell. swell=(t0, t1) seconds."""
    t = tt(dur)
    lfo = 0.85 + 0.15 * np.sin(2 * np.pi * 0.11 * t)
    low = (np.sin(2 * np.pi * 36.71 * t) * 0.7 + np.sin(2 * np.pi * 55.0 * t) * 0.35)
    saw = np.zeros_like(t)
    for f, a in [(73.42, 0.5), (73.8, 0.4), (110.0, 0.25), (146.83, 0.2), (174.61, 0.15), (220.0, 0.12)]:
        saw += a * signal.sawtooth(2 * np.pi * f * t + RNG.uniform(0, 6))
    cutoff = np.full_like(t, 260.0)
    amp = np.ones_like(t)
    if swell:
        s0, s1 = swell
        p = np.clip((t - s0) / (s1 - s0), 0, 1)
        cutoff = 260 + 2600 * p ** 2
        amp = 0.6 + 0.8 * p ** 1.5
    # block-wise time-varying lowpass
    out = np.zeros_like(t)
    hop = 2048
    zi = None
    for i in range(0, len(t), hop):
        sos = signal.butter(2, float(cutoff[i]), "lowpass", fs=SR, output="sos")
        if zi is None:
            zi = signal.sosfilt_zi(sos) * 0
        out[i:i + hop], zi = signal.sosfilt(sos, saw[i:i + hop], zi=zi)
    x = (low * 0.55 + out * 0.35 * amp) * lfo
    stereo = np.stack([x, np.roll(x, 240)], axis=1)
    return stereo.astype(np.float32) * 0.5


def beat_section(t0, t1, bpm, total):
    buf = np.zeros((int(total * SR), 2), np.float32)
    beat = 60.0 / bpm
    n = int(round((t1 - t0) / beat))
    for k in range(n):
        tb = t0 + k * beat
        add(buf, kick(), tb, 0.9)
        add(buf, hat(), tb + beat / 2, 1.0)
        if k % 2 == 0:
            tb_ = tt(beat * 1.9)
            bass = np.tanh(np.sin(2 * np.pi * 36.71 * tb_) * 2) * np.exp(-tb_ / 0.5) * 0.35
            add(buf, st(bass), tb, 1.0)
    return buf


# ------------------------------------------------------------------ mixing

def add(buf, x, at, gain=1.0):
    i = int(round(at * SR))
    if i >= len(buf):
        return
    j = min(len(buf), i + len(x))
    buf[i:j] += x[: j - i] * gain


def place(buf, x, t0, t1=None, gain=1.0, fade_in=0.02, fade_out=0.02):
    """Place x at t0, hard-trimmed at t1 with short fades (no tails past t1)."""
    if t1 is not None:
        x = x[: int((t1 - t0) * SR)].copy()
    else:
        x = x.copy()
    fi, fo = int(fade_in * SR), int(fade_out * SR)
    if fi:
        x[:fi] *= np.linspace(0, 1, fi)[:, None]
    if fo:
        x[-fo:] *= np.linspace(1, 0, fo)[:, None]
    add(buf, x, t0, gain)


def duck_env(total, hits, depth=0.7, release=0.4):
    t = tt(total)
    env = np.ones_like(t)
    for h in hits:
        d = t - h
        m = (d >= -0.01)
        env = np.minimum(env, np.where(m, 1 - depth * np.exp(-np.clip(d, 0, None) / release), 1))
    return env[:, None].astype(np.float32)


TRACK_BPM = 99.0  # measured on the supplied track; it is stretched onto each cut's grid
# Per cut: (target BPM, [(timeline start, timeline end, fade in, fade out), ...]).
# The first section starts `lead` seconds before the first grid downbeat so the
# track's groove lands on a kick exactly at `lock`; later sections re-enter on a kick.
TRACK_PLAN = {
    "master": dict(bpm=MASTER_BPM, lock=10.0, groove_from=8.0,
                   sections=[(3.0, 25.0, 1.0, 0.0), (27.0, 45.0, 0.0, 3.0)]),
    "cutdown": dict(bpm=CUT_BPM, lock=2.0, groove_from=8.0,
                    sections=[(2.0, 8.0, 0.02, 0.0), (9.0, 15.0, 0.0, 2.0)]),
}


def find_track():
    for ext in (".wav", ".flac", ".mp3", ".m4a", ".aif", ".aiff"):
        p = C.AUDIO / "music" / f"track{ext}"
        if p.exists():
            return p
    return None


def kicks(x):
    """Times (s) of low-end onsets, i.e. kicks, in a stereo float buffer."""
    mono = x.mean(axis=1)
    lo = np.abs(filt(mono, "lowpass", 120))
    hop = 240
    env = lo[: len(lo) // hop * hop].reshape(-1, hop).mean(axis=1)
    on = np.maximum(0, np.diff(env, prepend=env[0]))
    pk, _ = signal.find_peaks(on, height=np.percentile(on, 97), distance=int(0.3 * SR / hop))
    return pk * hop / SR


def load_track(cut, total):
    p = find_track()
    if p is None:
        return None, None
    plan = TRACK_PLAN[cut]
    tempo = plan["bpm"] / TRACK_BPM
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(p), "-af", f"atempo={tempo:.5f}",
                                   "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"])
    x = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
    k = kicks(x)
    groove = plan["groove_from"] / tempo
    first = k[k >= groove - 0.05][0]
    out = np.zeros((int(total * SR), 2), np.float32)
    src = None
    for i, (t0, t1, fi, fo) in enumerate(plan["sections"]):
        if i == 0:
            src = first - (plan["lock"] - t0)
        else:
            want = src_end
            src = k[np.argmin(np.abs(k - want))]  # re-enter on the nearest kick
        seg = x[int(src * SR): int((src + t1 - t0) * SR)].copy()
        n = len(seg)
        if fi:
            m = min(n, int(fi * SR))
            seg[:m] *= np.linspace(0, 1, m)[:, None]
        if fo:
            m = min(n, int(fo * SR))
            seg[-m:] *= np.linspace(1, 0, m)[:, None]
        else:
            seg[-96:] *= np.linspace(1, 0, 96)[:, None]  # 2 ms, no click at a hard stop
        a = int(t0 * SR)
        out[a:a + n] = seg[: len(out) - a]
        src_end = src + (t1 - t0) + (plan["sections"][i + 1][0] - t1 if i + 1 < len(plan["sections"]) else 0)
    return out, p


# ------------------------------------------------------------------ cue sheets

def master_mix():
    T = 45.0
    mus = np.zeros((int(T * SR), 2), np.float32)
    sfx = np.zeros_like(mus)
    # music
    place(mus, drone(22.0), 3.0, 25.0, 0.8, fade_in=1.0, fade_out=0.01)
    mus += beat_section(10.0, 25.0, MASTER_BPM, T) * 0.9
    place(mus, riser(1.0), 24.0, 25.0, 0.8, fade_out=0.005)
    place(mus, drone(18.0, swell=(2.5, 12.6)), 27.0, 45.0, 0.9, fade_in=0.01, fade_out=3.0)
    # sfx
    ign = 0.5
    place(sfx, roar(2.5), ign, 3.0, 0.9, fade_in=0.03, fade_out=0.03)
    add(sfx, sub_drop(), ign, 0.9)
    place(sfx, roar(2.0), 5.0, 7.0, 0.8, fade_in=0.01, fade_out=0.05)
    add(sfx, impact(), 5.35, 0.9)
    add(sfx, sub_drop(), 5.35, 0.7)
    add(sfx, whoosh(1.1), 6.6, 0.7)
    for tl in (7.5, 8.125, 8.75):
        add(sfx, kick(heavy=True), tl, 1.0)
    ps, pre = press_slam()
    add(sfx, ps, 23.75 - pre, 1.0)
    add(sfx, sub_drop(big=True), 27.0, 1.1)
    add(sfx, impact(big=True), 27.0, 0.6)
    add(sfx, clunk(), 32.9, 0.9)
    place(sfx, roar(4.0), 35.0, 39.0, 0.55, fade_in=0.08, fade_out=0.4)
    add(sfx, impact(big=True), 39.6, 1.0)
    add(sfx, sub_drop(big=True), 39.6, 0.9)
    duck = duck_env(T, [ign, 5.0, 5.35, 23.75, 27.0, 39.6])
    return T, mus, sfx, duck, [(25.0, 27.0)], [(0.0, ign)]


def cutdown_mix():
    T = 15.0
    mus = np.zeros((int(T * SR), 2), np.float32)
    sfx = np.zeros_like(mus)
    place(mus, drone(6.0), 2.0, 8.0, 0.7, fade_in=0.3, fade_out=0.01)
    mus += beat_section(2.0, 8.0, CUT_BPM, T) * 0.9
    place(mus, riser(0.6), 7.4, 8.0, 0.8, fade_out=0.005)
    place(mus, drone(6.0, swell=(0.0, 3.5)), 9.0, 15.0, 0.9, fade_in=0.01, fade_out=2.0)
    ign = 0.25
    place(sfx, roar(1.75), ign, 2.0, 0.9, fade_in=0.03, fade_out=0.03)
    add(sfx, sub_drop(), ign, 0.9)
    add(sfx, sub_drop(big=True), 9.0, 1.1)
    add(sfx, impact(big=True), 9.0, 0.6)
    add(sfx, whoosh(1.0), 10.5, 0.6)
    add(sfx, clunk(), 11.6, 0.9)
    add(sfx, impact(big=True), 12.5, 0.9)
    add(sfx, sub_drop(), 12.5, 0.8)
    duck = duck_env(T, [ign, 9.0, 12.5])
    return T, mus, sfx, duck, [(8.0, 9.0)], [(0.0, ign)]


MIXES = {"master": master_mix, "cutdown": cutdown_mix}


# ------------------------------------------------------------------ master bus

def limiter(x, ceiling_db=CEILING_DB, look=0.005, release=0.08):
    ceil = 10 ** (ceiling_db / 20)
    up = signal.resample_poly(x, 4, 1, axis=0)
    peak = np.abs(up).max(axis=1).reshape(-1, 4).max(axis=1)[: len(x)]
    need = np.minimum(1.0, ceil / np.maximum(peak, 1e-9))
    w = int(look * SR)
    g = minimum_filter1d(need, size=2 * w + 1)
    # smooth release (attack is handled by the lookahead window)
    a = np.exp(-1 / (release * SR))
    g = signal.lfilter([1 - a], [1, -a], g - 1) + 1
    g = np.minimum(g, minimum_filter1d(need, size=2 * w + 1))
    return x * g[:, None]


def build(cut):
    T, mus, sfx, duck, silences, pre = MIXES[cut]()
    track, track_path = load_track(cut, T)
    if track is not None:
        mus = track
    mix = mus * duck + sfx
    # the silence beat is true digital silence: no room tone, no tails
    for a, b in silences + pre:
        mix[int(a * SR): int(b * SR)] = 0.0
    meter = pyln.Meter(SR)
    for _ in range(3):
        lufs = meter.integrated_loudness(mix)
        mix = limiter(mix * 10 ** ((TARGET_LUFS - lufs) / 20))
    for a, b in silences + pre:
        mix[int(a * SR): int(b * SR)] = 0.0
    lufs = meter.integrated_loudness(mix)
    tp = np.abs(signal.resample_poly(mix, 4, 1, axis=0)).max()
    return mix.astype(np.float32), dict(lufs=round(float(lufs), 2), true_peak_db=round(float(20 * np.log10(tp)), 2),
                                        silences=silences, music=str(track_path) if track_path else "synth placeholder")


def write(cut, path):
    mix, info = build(cut)
    wavfile.write(str(path), SR, mix)
    return info
