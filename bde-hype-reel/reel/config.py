"""Brand constants, formats and paths. Single place to tweak the look."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "fonts"
FOOTAGE = ROOT / "footage"
AUDIO = ROOT / "audio"
BUILD = ROOT / "build"
OUT = ROOT / "out"

FPS = 30
SR = 48000  # audio sample rate


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


GOLD = hex_rgb("#C9A84C")
GOLD_HI = hex_rgb("#EBCB74")
OFF_WHITE = hex_rgb("#F5F0E8")
BG = hex_rgb("#060606")
HEAT = hex_rgb("#E8742C")  # footage grade / placeholder plates only, never type

FONT_HEAD = FONTS / "PlayfairDisplay-Black.ttf"
FONT_HEAD_IT = FONTS / "PlayfairDisplay-BlackItalic.ttf"
FONT_LABEL = FONTS / "BebasNeue-Regular.ttf"

# Output formats. `pic` is the picture area (inside letterbox bars).
# `safe` is where text may live. `lower` is the y of the bottom edge of
# lower-third text blocks. Sizes are px at output resolution.
FORMATS = {
    "16x9": dict(
        w=1920, h=1080,
        bars=60,                      # thin 2:1 letterbox
        safe=(160, 60, 1760, 1020),   # x0, y0, x1, y1
        lower=930,
        head=104, head_xl=150, mono=330, label=44, label_sm=36, url=92,
        gap=26,
        inset=(480, 130, 1440, 670),  # 960x540 window on black, card below
        inset_lower=930,
    ),
    "9x16": dict(
        w=1080, h=1920,
        bars=0,
        safe=(80, 250, 1000, 1670),   # centre 1080x1420, minus side margin
        lower=1560,
        head=116, head_xl=170, mono=300, label=48, label_sm=38, url=100,
        gap=30,
        inset=(120, 290, 960, 1340),  # 840x1050 (4:5) window on black
        inset_lower=1640,
    ),
}
