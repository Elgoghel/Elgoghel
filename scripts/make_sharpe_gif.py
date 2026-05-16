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
W_OUT, H_OUT = 820, 230
SS = 3  # supersample factor: render at 3x then downsample for smooth anti-aliased edges
W, H = W_OUT * SS, H_OUT * SS
BG = (13, 17, 23)          # GitHub dark
GRAY_BAR = (110, 118, 129)
GREEN = (63, 185, 80)
RED = (248, 81, 73)
BLUE = (88, 166, 255)
DIVIDER = (48, 54, 61)
TEXT = (156, 163, 175)

BAR_X = 100 * SS
BAR_H = 14 * SS
BAR_SCALE = 200 * SS  # pixels per Sharpe unit

ROW_YS = {
    "seed  7": 40 * SS, "seed 11": 64 * SS, "seed 13": 88 * SS, "seed 17": 112 * SS, "seed 19": 136 * SS,
    "SPY": 184 * SS,
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

FONT = load_font(14 * SS)
FONT_BOLD = load_font(14 * SS)

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

    d.text((20 * SS, 8 * SS), "Sharpe ratio, 2024 OOS, every seed:", fill=TEXT, font=FONT_BOLD)

    grow_t = ease_out(clamp01(t / DUR_GROW))

    for label, sharpe, kind in SEEDS:
        y = ROW_YS[label]
        full_w = sharpe * BAR_SCALE  # float; high-res
        cur_w = full_w * grow_t

        if kind == "median" and t >= T_MEDIAN_GREEN:
            fill_t = clamp01((t - T_MEDIAN_GREEN) / DUR_FILL)
            color = lerp_color(GRAY_BAR, GREEN, fill_t)
        elif kind == "best" and t >= T_BEST_RED:
            fill_t = clamp01((t - T_BEST_RED) / DUR_FILL)
            color = lerp_color(GRAY_BAR, RED, fill_t)
        else:
            color = GRAY_BAR

        d.text((20 * SS, (y - 4)), label, fill=TEXT, font=FONT)
        if cur_w > 0:
            d.rectangle([BAR_X, y, BAR_X + cur_w, y + BAR_H], fill=color)

        if t >= T_NUMS_FADE:
            opacity = clamp01((t - T_NUMS_FADE) / DUR_NUMS_FADE)
            alpha = int(255 * opacity)
            num_color = TEXT + (alpha,)
            d.text((510 * SS, y - 4), f"{sharpe:.2f}", fill=num_color, font=FONT)

    if t >= T_LBL_MED:
        opacity = clamp01((t - T_LBL_MED) / DUR_LBL)
        alpha = int(255 * opacity)
        d.text((565 * SS, ROW_YS["seed 11"] - 4), "← median", fill=GREEN + (alpha,), font=FONT)

    if t >= T_LBL_BEST:
        opacity = clamp01((t - T_LBL_BEST) / DUR_LBL)
        alpha = int(255 * opacity)
        d.text((565 * SS, ROW_YS["seed 19"] - 4), "← best of 5, cherry-picked", fill=RED + (alpha,), font=FONT)

    d.line([(20 * SS, 170 * SS), (790 * SS, 170 * SS)], fill=DIVIDER, width=SS)

    label, sharpe, kind = SPY
    y = ROW_YS["SPY"]
    full_w = sharpe * BAR_SCALE
    cur_w = full_w * grow_t
    d.text((20 * SS, y - 4), label, fill=TEXT, font=FONT)
    if cur_w > 0:
        spy_blue = lerp_color(BG, BLUE, 0.6)
        d.rectangle([BAR_X, y, BAR_X + cur_w, y + BAR_H], fill=spy_blue)
    if t >= T_NUMS_FADE:
        opacity = clamp01((t - T_NUMS_FADE) / DUR_NUMS_FADE)
        alpha = int(255 * opacity)
        d.text((510 * SS, y - 4), f"{sharpe:.2f}", fill=TEXT + (alpha,), font=FONT)
    if t >= T_LBL_BENCH:
        opacity = clamp01((t - T_LBL_BENCH) / DUR_LBL)
        alpha = int(255 * opacity)
        d.text((565 * SS, y - 4), "← benchmark", fill=BLUE + (alpha,), font=FONT)

    # downsample with high-quality filter for smooth sub-pixel anti-aliased edges
    return img.resize((W_OUT, H_OUT), Image.LANCZOS)

def main():
    out_dir = Path(__file__).parent.parent / "assets"
    out_dir.mkdir(exist_ok=True)
    out = out_dir / "sharpe-anim.webp"

    n_frames = int(TOTAL * FPS)
    frames = []
    for i in range(n_frames):
        t = i / FPS
        frames.append(render_frame(t))
    # single hold frame extended to 4s via duration; WebP handles long single-frame durations cleanly
    frames.append(render_frame(TOTAL))

    durations = [1000 // FPS] * n_frames + [4000]

    frames[0].save(
        out,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        quality=80,
        method=6,  # best quality/size tradeoff (slowest encode)
    )
    print(f"Wrote {out} ({out.stat().st_size // 1024} KB, {len(frames)} frames)")

if __name__ == "__main__":
    main()
