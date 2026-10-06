# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow>=12", "numpy>=2"]
# ///
"""Render assets/fedgbt-method-results.gif from the thesis supplement CSVs."""

import argparse
import csv
import functools
import subprocess
from collections.abc import Iterable
from pathlib import Path
from typing import NamedTuple

import numpy as np
from PIL import Image, ImageDraw, ImageFont, features

# Chrome block shared with sibling GIF renderers; keep identical.
W, H, M, FPS = 840, 480, 24, 10
BG, INK, MUTED, FAINT = "#0d1117", "#e6edf3", "#8b949e", "#6e7681"
RULE, CELL, ACCENT, HARM = "#30363d", "#21262d", "#3987e5", "#e66767"
GAIN = ACCENT
CONTENT = (24, 80, 816, 416)
FONTS = {
    "serif": ("/usr/share/fonts/stix-fonts/STIX2Text-Regular.otf", "STIXGeneral.ttf"),
    "italic": (
        "/usr/share/fonts/stix-fonts/STIX2Text-Italic.otf",
        "STIXGeneralItalic.ttf",
    ),
    "label": (
        "/usr/share/fonts/adobe-source-code-pro/SourceCodePro-Medium.otf",
        "DejaVuSansMono.ttf",
    ),
    "value": (
        "/usr/share/fonts/adobe-source-code-pro/SourceCodePro-Regular.otf",
        "DejaVuSansMono.ttf",
    ),
}


@functools.cache
def font(role: str, size: int) -> ImageFont.FreeTypeFont:
    path, fallback = FONTS[role]
    if not Path(path).exists():
        import matplotlib  # type: ignore[import-not-found, unused-ignore]

        path = str(Path(matplotlib.get_data_path()) / "fonts" / "ttf" / fallback)
    raqm = features.check("raqm")
    layout = ImageFont.Layout.RAQM if raqm else ImageFont.Layout.BASIC
    return ImageFont.truetype(path, size, layout_engine=layout)


def caps(
    d: ImageDraw.ImageDraw,
    x: float,
    y: int,
    text: str,
    *,
    right: bool = False,
    fill: str = MUTED,
    size: int = 13,
    tracking: int = 1,
) -> float:
    f = font("label", size)
    text = text.upper()
    width = sum(f.getlength(c) for c in text) + tracking * (len(text) - 1)
    if right:
        x -= width
    for c in text:
        d.text((x, y), c, font=f, fill=fill, anchor="ls")
        x += f.getlength(c) + tracking
    return width


def value(
    d: ImageDraw.ImageDraw,
    x: float,
    y: int,
    text: str,
    *,
    right: bool = False,
    size: int = 20,
    fill: str = INK,
) -> None:
    anchor = "rs" if right else "ls"
    d.text((x, y), text, font=font("value", size), fill=fill, anchor=anchor)


def headline(
    d: ImageDraw.ImageDraw, runs: list[tuple[str, bool]], max_width: float
) -> None:
    fonts = [font("italic" if italic else "serif", 28) for _, italic in runs]
    widths = [f.getlength(text) for (text, _), f in zip(runs, fonts, strict=True)]
    if sum(widths) > max_width:
        raise ValueError(f"headline is {sum(widths):.0f} px, over {max_width:.0f}")
    x: float = M
    for (text, _), f, w in zip(runs, fonts, widths, strict=True):
        d.text((x, 48), text, font=f, fill=INK, anchor="ls")
        x += w


def hairline(
    d: ImageDraw.ImageDraw, x0: int, y0: int, x1: int, y1: int, fill: str = RULE
) -> None:
    d.line([(x0, y0), (x1, y1)], fill=fill, width=1)


def corner_ticks(
    d: ImageDraw.ImageDraw, box: tuple[int, int, int, int], length: int = 6
) -> None:
    x0, y0, x1, y1 = box
    for x, y, sx, sy in (
        (x0, y0, 1, 1),
        (x1, y0, -1, 1),
        (x0, y1, 1, -1),
        (x1, y1, -1, -1),
    ):
        hairline(d, x, y, x + sx * (length - 1), y)
        hairline(d, x, y, x, y + sy * (length - 1))


def chrome(
    runs: list[tuple[str, bool]], kicker: str, foot_left: str, foot_right: str
) -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    kicker_width = caps(d, W - M, 48, kicker, right=True)
    headline(d, runs, W - 3 * M - kicker_width)
    hairline(d, M, 64, W - M, 64)
    hairline(d, M, 432, W - M, 432)
    footer = caps(d, M, 456, foot_left) + caps(d, W - M, 456, foot_right, right=True)
    if footer > W - 3 * M:
        raise ValueError(f"footer is {footer:.0f} px, over {W - 3 * M}")
    return img


def encode_gif(
    frames: Iterable[Image.Image], out: Path, colours: int, max_bytes: int
) -> int:
    graph = (
        f"[0:v]split[a][b];[a]palettegen=max_colors={colours}:stats_mode=full[p];"
        "[b][p]paletteuse=dither=none:diff_mode=rectangle"
    )
    cmd = [
        "ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pixel_format", "rgb24",
        "-video_size", f"{W}x{H}", "-framerate", str(FPS), "-i", "-",
        "-filter_complex", graph, "-loop", "0", "-final_delay", "250", str(out),
    ]  # fmt: skip
    out.parent.mkdir(parents=True, exist_ok=True)
    raw = b"".join(frame.convert("RGB").tobytes() for frame in frames)
    subprocess.run(cmd, input=raw, check=True)
    size = out.stat().st_size
    if size > max_bytes:
        raise ValueError(f"{out} is {size:,} B, over the {max_bytes:,} B cap")
    return size


SPECTRUM = "spectrum-fremtpl2freq-rate-multipliers.csv"
SELECTION = "selection-fremtpl2freq-rate-multipliers.csv"
LEVELS = ("1", "2", "3")
SILOS, BINS = 10, 8
KICKER = "MSC THESIS · UCL 2026"
METHOD_HEAD = [("Ten insurers grow the ", False), ("same", True), (" tree", False)]
HARM_HEAD = [("Sharing hurts as claim rates ", False), ("diverge", True)]
FIX_HEAD = [
    ("Here one ", False),
    ("intercept", True),
    (" per insurer undoes the harm", False),
]
METHOD_FOOT = (
    "ILLUSTRATIVE HISTOGRAMS · FEDERATED XGBOOST",
    "NO RAW RECORD LEAVES A SILO",
)
RESULTS_FOOT = (
    "FREMTPL2 · RATE MULTIPLIERS · 10 INSURERS",
    "PTS OF DEVIANCE EXPLAINED VS LOCAL-ONLY",
)
CAPTIONS = {
    112: ("EACH INSURER SUMS", "GRADIENTS AND", "HESSIANS PER BIN"),
    210: ("COORDINATOR ADDS", "THE SUMS, RETURNS", "THE TOTALS"),
    330: ("EACH INSURER SCORES", "THE TOTALS, GROWS", "THE SAME SPLIT"),
}
A_MID, A_PX, C_MID, C_PX, TREE_Y = 124, 24, 324, 16, 352
B_MID, B_PX = 228, 48
PX_PER_PT, ZERO_Y, TICK_Y = 12, 178, 400
POSTER_HOLD, HARM_HOLD, EASE_FRAMES = 5, 20, 8


Label = tuple[int, int, str, str]


class Cell(NamedTuple):
    heterogeneity: str
    fed: tuple[float, ...]
    recal: tuple[float, ...]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def mean(cell: str) -> float:
    return float(cell.split(" ", 1)[0])


def gains(rows: list[dict[str, str]], arm: str) -> tuple[float, ...]:
    return tuple(round(mean(r[arm]) - mean(r["Local-only (%PDE)"]), 2) for r in rows)


def load(csv_dir: Path) -> list[Cell]:
    spectrum = [r for r in read(csv_dir / SPECTRUM) if r["Silo"].isdigit()]
    index = {r["Level"]: r["Heterogeneity"] for r in read(csv_dir / SELECTION)}
    cells = []
    for level in LEVELS:
        rows = [r for r in spectrum if r["Level"] == level]
        rows.sort(key=lambda r: int(r["Silo"]))
        if [int(r["Silo"]) for r in rows] != list(range(SILOS)):
            raise ValueError(f"level {level}: expected silos 0 to {SILOS - 1}")
        fed = gains(rows, "Federated global (%PDE)")
        recal = gains(rows, "Recalibrated global (%PDE)")
        cells.append(Cell(index[level], fed, recal))
    return cells


def check(cells: list[Cell]) -> None:
    harmed = [sum(v < 0 for v in c.fed) for c in cells]
    if harmed != [0, 5, 7]:
        raise ValueError(f"harmed counts {harmed}, thesis Table 5.1 has [0, 5, 7]")
    if min(cells[-1].fed) != -16.21:
        raise ValueError(f"worst gain {min(cells[-1].fed)}, thesis has -16.21")
    if min(min(c.recal) for c in cells) <= 0:
        raise ValueError("a recalibrated gain is not above local-only")
    if [c.heterogeneity for c in cells] != ["0.004", "0.014", "0.048"]:
        raise ValueError("heterogeneity levels differ from thesis Table 5.1")


def signed(v: float) -> str:
    return f"{v:+.2f}".replace("-", "\u2212")


def illustrative_sums() -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(7)
    scale = rng.uniform(0.6, 1.4, (SILOS, 1))
    profile = np.tanh(3 * (np.linspace(0, 1, BINS) - 0.65))
    g = scale * (profile + rng.normal(0, 0.45, (SILOS, BINS)))
    h = scale * rng.uniform(0.6, 1.4, (SILOS, BINS))
    return g, h


def best_cut(g: np.ndarray, h: np.ndarray, lam: float = 1.0) -> int:
    gl, hl = np.cumsum(g)[:-1], np.cumsum(h)[:-1]
    gt, ht = g.sum(), h.sum()
    gain = gl**2 / (hl + lam) + (gt - gl) ** 2 / (ht - hl + lam) - gt**2 / (ht + lam)
    return int(np.argmax(gain)) + 1


def col_x(k: int) -> int:
    return 228 + 60 * k


def centre(k: int) -> int:
    return col_x(k) + 23


TRUNK = (centre(0) + centre(SILOS - 1)) // 2
B_X = TRUNK - (24 * BINS - 7) // 2


def histogram(
    d: ImageDraw.ImageDraw,
    x0: int,
    mid: int,
    values: np.ndarray,
    scale: float,
    fill: str,
    pitch: int = 6,
    width: int = 4,
) -> None:
    for b, v in enumerate(values):
        h = round(float(v) * scale)
        if h == 0:
            continue
        y0, y1 = (mid - h, mid - 1) if h > 0 else (mid + 1, mid - h)
        x = x0 + pitch * b
        d.rectangle((x, y0, x + width - 1, y1), fill=fill)


def digits(
    d: ImageDraw.ImageDraw, y: int, xs: list[int], active: int | None = None
) -> None:
    for k, x in enumerate(xs):
        caps(d, x - 4, y, str(k), fill=INK if k == active else MUTED)


def arrow(d: ImageDraw.ImageDraw, x: int, y: int, fill: str) -> None:
    d.polygon([(x - 3, y - 3), (x + 3, y - 3), (x, y)], fill=fill)


def up_path(d: ImageDraw.ImageDraw, k: int, fill: str = FAINT) -> None:
    hairline(d, centre(k), 152, centre(k), 160, fill)
    hairline(d, centre(k), 160, TRUNK, 160, fill)
    hairline(d, TRUNK, 160, TRUNK, 175, fill)
    arrow(d, TRUNK, 176, fill)


def down_bus(d: ImageDraw.ImageDraw, fill: str = FAINT) -> None:
    hairline(d, TRUNK, 280, TRUNK, 296, fill)
    hairline(d, centre(0), 296, centre(SILOS - 1), 296, fill)
    for k in range(SILOS):
        hairline(d, centre(k), 296, centre(k), 303, fill)
        arrow(d, centre(k), 304, fill)


def tree(d: ImageDraw.ImageDraw, cx: int, grown: bool) -> None:
    if not grown:
        d.rectangle((cx - 4, TREE_Y, cx + 3, TREE_Y + 7), fill=RULE)
        return
    hairline(d, cx, TREE_Y + 8, cx, TREE_Y + 15, FAINT)
    hairline(d, cx - 12, TREE_Y + 16, cx + 12, TREE_Y + 16, FAINT)
    for x in (cx - 12, cx + 12):
        hairline(d, x, TREE_Y + 16, x, TREE_Y + 21, FAINT)
        d.rectangle((x - 4, TREE_Y + 22, x + 3, TREE_Y + 29), fill=INK)
    d.rectangle((cx - 4, TREE_Y, cx + 3, TREE_Y + 7), fill=INK)


def method_stage() -> Image.Image:
    img = chrome(METHOD_HEAD, KICKER, *METHOD_FOOT)
    d = ImageDraw.Draw(img)
    for y, lines in CAPTIONS.items():
        for i, line in enumerate(lines):
            caps(d, M, y + 18 * i, line)
    for k in range(SILOS):
        up_path(d, k)
        hairline(d, col_x(k), A_MID, col_x(k) + 45, A_MID)
        hairline(d, col_x(k), C_MID, col_x(k) + 45, C_MID)
    down_bus(d)
    hairline(d, B_X, B_MID, B_X + 24 * BINS - 7, B_MID)
    corner_ticks(d, (B_X - 12, 180, B_X + 24 * BINS + 5, 276))
    digits(d, TICK_Y, [centre(k) for k in range(SILOS)])
    return img


def method_frame(
    stage: Image.Image,
    g: np.ndarray,
    scales: tuple[float, float, float],
    *,
    upto: int = 0,
    active: int | None = None,
    sending: bool = False,
    returned: bool = False,
    cut: int | None = None,
    chosen: bool = False,
    grown: bool = False,
) -> Image.Image:
    img = stage.copy()
    d = ImageDraw.Draw(img)
    digits(d, 92, [centre(k) for k in range(SILOS)], active)
    if active is not None:
        up_path(d, active, INK)
    if sending:
        down_bus(d, ACCENT)
    for k in range(SILOS):
        fill = INK if k == active else MUTED
        histogram(d, col_x(k), A_MID, g[k], scales[0], fill)
        if returned:
            histogram(d, col_x(k), C_MID, g.sum(0), scales[2], ACCENT)
        tree(d, centre(k), grown)
    summed = g[:upto].sum(0)
    histogram(d, B_X, B_MID, summed, scales[1], ACCENT, pitch=24, width=18)
    if cut is None:
        return img
    marker = INK if chosen else MUTED
    for k in range(SILOS):
        x = col_x(k) + 6 * cut - 1
        hairline(d, x, C_MID - 16, x, C_MID + 18, marker)
        if grown:
            hairline(d, x, A_MID - 25, x, A_MID + 25, INK)
    return img


def method_frames() -> list[Image.Image]:
    g, h = illustrative_sums()
    total = g.sum(0)
    running = np.abs(np.cumsum(g, axis=0)).max()
    scales = (A_PX / np.abs(g).max(), B_PX / running, C_PX / np.abs(total).max())
    best = best_cut(total, h.sum(0))
    frame = functools.partial(method_frame, method_stage(), g, scales, upto=SILOS)
    frames = [frame(upto=0)] * 4
    frames += [frame(upto=k + 1, active=k) for k in range(SILOS)]
    frames += [frame(sending=True)] * 2
    frames += [frame(sending=True, returned=True)] * 2
    frames += [frame(returned=True, cut=c) for c in range(1, BINS)]
    frames += [frame(returned=True, cut=best, chosen=True)] * 4
    frames += [frame(returned=True, cut=best, chosen=True, grown=True)] * 10
    return frames


def panel_x(i: int) -> int:
    return M + 272 * i


def bar_x(i: int, k: int) -> int:
    return panel_x(i) + 8 + 24 * k


def bar_px(v: float) -> int:
    if v == 0:
        return 0
    return int(np.sign(v)) * max(2, round(abs(v) * PX_PER_PT))


def bar(
    d: ImageDraw.ImageDraw,
    x: int,
    h: int,
    *,
    fill: str | None = None,
    outline: str | None = None,
) -> None:
    if h == 0:
        return
    inset = 0 if outline else 1
    y0, y1 = (ZERO_Y - h, ZERO_Y - inset) if h > 0 else (ZERO_Y + inset, ZERO_Y - h)
    corners = (h > 0, h > 0, h < 0, h < 0)
    radius = min(4, abs(h) // 2)
    box = (x, y0, x + 15, y1)
    d.rounded_rectangle(box, radius, fill=fill, outline=outline, corners=corners)


def ease(t: float) -> float:
    return 4 * t**3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def results_stage(
    runs: list[tuple[str, bool]], cells: list[Cell], legend: bool
) -> Image.Image:
    img = chrome(runs, KICKER, *RESULTS_FOOT)
    d = ImageDraw.Draw(img)
    for i, cell in enumerate(cells):
        caps(d, panel_x(i), 92, f"HETEROGENEITY {cell.heterogeneity}")
        hairline(d, panel_x(i), ZERO_Y, panel_x(i) + 247, ZERO_Y, FAINT)
        digits(d, TICK_Y, [bar_x(i, k) + 8 for k in range(SILOS)])
    caps(d, bar_x(0, 0), ZERO_Y + 28, "0 = LOCAL-ONLY")
    if legend:
        caps(d, bar_x(0, 0), ZERO_Y + 46, "OUTLINE = BEFORE REFIT")
    return img


def results_frame(
    stage: Image.Image,
    heights: list[list[int]],
    counts: list[str],
    labels: list[Label],
    ghosts: list[list[int]] | None = None,
) -> Image.Image:
    img = stage.copy()
    d = ImageDraw.Draw(img)
    for i, row in enumerate(heights):
        for k, h in enumerate(row):
            if ghosts:
                bar(d, bar_x(i, k), ghosts[i][k], outline=FAINT)
            bar(d, bar_x(i, k), h, fill=GAIN if h > 0 else HARM)
        value(d, panel_x(i), 120, counts[i])
        width = font("value", 20).getlength(counts[i])
        caps(d, panel_x(i) + width + 10, 120, "HARMED")
    for x, y, anchor, text in labels:
        d.text((x, y), text, font=font("value", 20), fill=INK, anchor=anchor)
    return img


def tween(a: list[list[int]], b: list[list[int]], s: float) -> list[list[int]]:
    return [[round(p + (q - p) * s) for p, q in zip(ra, rb)] for ra, rb in zip(a, b)]


def results_frames(cells: list[Cell]) -> list[Image.Image]:
    fitted = [[bar_px(v) for v in c.fed] for c in cells]
    refit = [[bar_px(v) for v in c.recal] for c in cells]
    fed, recal = cells[-1].fed, cells[-1].recal
    worst, least = int(np.argmin(fed)), int(np.argmin(recal))
    worst_y, least_y = ZERO_Y - fitted[-1][worst], ZERO_Y - refit[-1][least] - 12
    worst_label = (bar_x(2, worst) - 6, worst_y, "rs", signed(fed[worst]))
    least_label = (bar_x(2, least) + 8, least_y, "ms", signed(recal[least]))
    before = [sum(h < 0 for h in row) for row in fitted]
    harm_stage = results_stage(HARM_HEAD, cells, legend=False)
    fix_stage = results_stage(FIX_HEAD, cells, legend=True)

    as_fitted = [str(n) for n in before]
    frames = [results_frame(harm_stage, fitted, as_fitted, [worst_label])] * HARM_HOLD
    for step in range(1, EASE_FRAMES + 1):
        heights = tween(fitted, refit, ease(step / EASE_FRAMES))
        after = [sum(h < 0 for h in row) for row in heights]
        counts = [f"{n} → {m}" for n, m in zip(before, after)]
        last = step == EASE_FRAMES
        labels: list[Label] = [worst_label, least_label] if last else [worst_label]
        frames.append(results_frame(fix_stage, heights, counts, labels, fitted))
    return frames


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_dir", type=Path, help="thesis docs/supplement directory")
    out = Path(__file__).resolve().parents[1] / "assets" / "fedgbt-method-results.gif"
    parser.add_argument("--out", type=Path, default=out)
    args = parser.parse_args()
    cells = load(args.csv_dir)
    check(cells)
    results = results_frames(cells)
    frames = [results[-1]] * POSTER_HOLD + method_frames() + results
    size = encode_gif(frames, args.out, colours=48, max_bytes=1_500_000)
    print(f"{args.out}: {size:,} B, {len(frames)} frames")


if __name__ == "__main__":
    main()
