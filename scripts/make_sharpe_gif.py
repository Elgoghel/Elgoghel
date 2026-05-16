"""Render the Sharpe distribution chart as an animated GIF for the profile README.

Animation timeline (3.0s total, 25 fps = 75 frames):
  0.0-1.5s : bars grow from 0 to final width
  1.6s     : per-bar Sharpe numbers fade in
  1.8s     : seed 11 (median) fills green
  2.0s     : seed 19 (best) fills red, SPY benchmark label appears
  2.0s     : "<- median" label appears
  2.3s     : "<- best of 5, cherry-picked" label appears
  3.0s     : final hold frame (repeated to extend the static portion)

Output: assets/sharpe-anim.gif
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# --- chart data (matches paper Table 6.2) ---
SEEDS = [
    ("seed  7", 1.79, "neutral"),
    ("seed 11", 1.73, "median"),
    ("seed 13", 1.49, "neutral"),
    ("seed 17", 1.33, "neutral"),
    ("seed 19", 1.99, "best"),
]
SPY = ("SPY", 1.87, "benchmark")

# --- styling (mirrors the SVG version) ---
W, H = 820, 230
BG = (13, 17, 23)          # GitHub dark
GRAY_BAR = (110, 118, 129)
GREEN = (63, 185, 80)
RED = (248, 81, 73)
BLUE = (88, 166, 255)
DIVIDER = (48, 54, 61)
TEXT = (156, 163, 175)

BAR_X = 100
BAR_H = 14
BAR_SCALE = 200  # pixels per Sharpe unit

ROW_YS = {
    "seed  7": 40, "seed 11": 64, "seed 13": 88, "seed 17": 112, "seed 19": 136,
    "SPY": 184,
}
LABEL_YS = {k: y + 12 for k, y in ROW_YS.items()}

# --- font ---
def load_font(size=14):
    candidates = [
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/CascadiaCode.ttf",
        "C:/Windows/Fonts/cour.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

FONT = load_font(14)
FONT_BOLD = load_font(14)

# --- animation timing ---
DUR_GROW = 2.5
T_NUMS_FADE = 2.6
DUR_NUMS_FADE = 0.4
T_MEDIAN_GREEN = 2.8
DUR_FILL = 0.6
T_BEST_RED = 3.0
T_LBL_MED = 3.0
T_LBL_BENCH = 3.0
T_LBL_BEST = 3.3
DUR_LBL = 0.5

TOTAL = 4.0
FPS = 60

def ease_out(t):
    """Sinusoidal ease-in-out: smoother than cubic ease-out."""
    import math
    return 0.5 - 0.5 * math.cos(math.pi * t)

def clamp01(x):
    return max(0.0, min(1.0, x))

def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def render_frame(t):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img, "RGBA")

    # title
    d.text((20, 8), "Sharpe ratio, 2024 OOS, every seed:", fill=TEXT, font=FONT_BOLD)

    # bars
    grow_t = ease_out(clamp01(t / DUR_GROW))

    for label, sharpe, kind in SEEDS:
        y = ROW_YS[label]
        full_w = int(sharpe * BAR_SCALE / 2 * 4)  # scale: 200 * (sharpe/2.0) * 4 = ... wait
        # Bar widths: scale=200/Sharpe_unit so 1.79 -> 358
        full_w = int(sharpe * BAR_SCALE)
        cur_w = int(full_w * grow_t)

        # fill color based on time
        if kind == "median" and t >= T_MEDIAN_GREEN:
            fill_t = clamp01((t - T_MEDIAN_GREEN) / DUR_FILL)
            color = lerp_color(GRAY_BAR, GREEN, fill_t)
        elif kind == "best" and t >= T_BEST_RED:
            fill_t = clamp01((t - T_BEST_RED) / DUR_FILL)
            color = lerp_color(GRAY_BAR, RED, fill_t)
        else:
            color = GRAY_BAR

        d.text((20, y - 4), label, fill=TEXT, font=FONT)
        if cur_w > 0:
            d.rectangle([BAR_X, y, BAR_X + cur_w, y + BAR_H], fill=color)

        # number fades in
        if t >= T_NUMS_FADE:
            opacity = clamp01((t - T_NUMS_FADE) / DUR_NUMS_FADE)
            alpha = int(255 * opacity)
            num_color = TEXT + (alpha,)
            d.text((510, y - 4), f"{sharpe:.2f}", fill=num_color, font=FONT)

    # median label
    if t >= T_LBL_MED:
        opacity = clamp01((t - T_LBL_MED) / DUR_LBL)
        alpha = int(255 * opacity)
        d.text((565, ROW_YS["seed 11"] - 4), "← median", fill=GREEN + (alpha,), font=FONT)

    # best label
    if t >= T_LBL_BEST:
        opacity = clamp01((t - T_LBL_BEST) / DUR_LBL)
        alpha = int(255 * opacity)
        d.text((565, ROW_YS["seed 19"] - 4), "← best of 5, cherry-picked", fill=RED + (alpha,), font=FONT)

    # divider
    d.line([(20, 170), (790, 170)], fill=DIVIDER, width=1)

    # SPY row
    label, sharpe, kind = SPY
    y = ROW_YS["SPY"]
    full_w = int(sharpe * BAR_SCALE)
    cur_w = int(full_w * grow_t)
    d.text((20, y - 4), label, fill=TEXT, font=FONT)
    if cur_w > 0:
        # blue with 60% opacity equivalent baked in
        spy_blue = lerp_color(BG, BLUE, 0.6)
        d.rectangle([BAR_X, y, BAR_X + cur_w, y + BAR_H], fill=spy_blue)
    if t >= T_NUMS_FADE:
        opacity = clamp01((t - T_NUMS_FADE) / DUR_NUMS_FADE)
        alpha = int(255 * opacity)
        d.text((510, y - 4), f"{sharpe:.2f}", fill=TEXT + (alpha,), font=FONT)
    if t >= T_LBL_BENCH:
        opacity = clamp01((t - T_LBL_BENCH) / DUR_LBL)
        alpha = int(255 * opacity)
        d.text((565, y - 4), "← benchmark", fill=BLUE + (alpha,), font=FONT)

    return img

def main():
    out_dir = Path(__file__).parent.parent / "assets"
    out_dir.mkdir(exist_ok=True)
    out = out_dir / "sharpe-anim.gif"

    n_frames = int(TOTAL * FPS)
    frames = []
    for i in range(n_frames):
        t = i / FPS
        frames.append(render_frame(t))
    # add a long hold frame
    hold_frames = [render_frame(TOTAL)] * 50  # ~2 second hold
    frames.extend(hold_frames)

    durations = [1000 // FPS] * n_frames + [40] * 50
    # final frame extra long
    durations[-1] = 3000

    frames[0].save(
        out,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=True,
        disposal=2,
    )
    print(f"Wrote {out} ({out.stat().st_size // 1024} KB, {len(frames)} frames)")

if __name__ == "__main__":
    main()
