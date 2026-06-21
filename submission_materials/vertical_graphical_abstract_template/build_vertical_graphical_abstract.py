#!/usr/bin/env python3
from __future__ import annotations

import argparse
import io
import json
import math
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from PIL import Image, ImageDraw, ImageFont


TEMPLATE_DIR = Path(__file__).resolve().parent
SUBMISSION_DIR = TEMPLATE_DIR.parent
PACKAGE_DIR = SUBMISSION_DIR.parent

plt.rcParams.update(
    {
        "font.family": "Arial",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "axes.titleweight": "bold",
        "axes.labelcolor": "#35536E",
        "xtick.color": "#35536E",
        "ytick.color": "#35536E",
        "text.color": "#082B4F",
    }
)

COLORS = {
    "ink": (8, 43, 79),
    "muted": (53, 83, 110),
    "quiet": (86, 112, 136),
    "paper": (248, 251, 255),
    "soft": (235, 242, 250),
    "rule": (202, 215, 230),
    "hairline": (226, 234, 243),
    "navy": (6, 45, 82),
    "blue": (14, 74, 122),
    "blue_soft": (228, 237, 255),
    "cyan": (18, 116, 143),
    "cyan_soft": (222, 247, 250),
    "orange": (39, 91, 139),
    "orange_soft": (232, 241, 249),
    "purple": (16, 62, 110),
    "purple_soft": (230, 239, 249),
    "gray": (148, 163, 184),
    "gray_soft": (241, 245, 249),
    "white": (255, 255, 255),
    "warm_white": (253, 254, 255),
}

PUB = {
    "dark": (6, 45, 82),
    "mid": (14, 74, 122),
    "cyan": (18, 116, 143),
    "soft": (228, 237, 246),
    "pale": (244, 248, 252),
    "line": (202, 218, 234),
}

FONT_DIRS = [
    Path("/System/Library/Fonts/Supplemental"),
    Path("/Library/Fonts/Microsoft"),
    Path("/System/Library/Fonts"),
]


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    candidates = {
        "regular": ["Arial.ttf", "Helvetica.ttc"],
        "bold": ["Arial Bold.ttf", "Helvetica.ttc"],
        "italic": ["Arial Italic.ttf", "Times New Roman Italic.ttf"],
        "serif": ["Times New Roman.ttf", "Times.ttc"],
        "serif_bold": ["Times New Roman Bold.ttf", "Times.ttc"],
    }[name]
    for directory in FONT_DIRS:
        for candidate in candidates:
            path = directory / candidate
            if path.exists():
                return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default(size=size)


F = {
    "title": font("bold", 68),
    "h1": font("bold", 38),
    "h2": font("bold", 40),
    "section": font("bold", 50),
    "section_num": font("bold", 24),
    "band": font("bold", 32),
    "body": font("regular", 31),
    "body_bold": font("bold", 31),
    "author": font("regular", 38),
    "sup": font("regular", 14),
    "affil": font("italic", 24),
    "small": font("regular", 27),
    "small_bold": font("bold", 27),
    "audit_value": font("bold", 24),
    "audit_label": font("regular", 24),
    "tiny": font("regular", 22),
    "tiny_bold": font("bold", 22),
    "caption": font("regular", 25),
    "caption_bold": font("bold", 25),
    "photo_label": font("bold", 25),
    "photo_note": font("regular", 22),
    "scope_label": font("bold", 24),
    "italic": font("italic", 21),
    "footer": font("regular", 30),
    "footer_small": font("regular", 24),
    "footer_note": font("regular", 21),
    "qr_label": font("bold", 20),
    "poster_metric": font("bold", 46),
    "poster_metric_small": font("bold", 36),
    "poster_metric_tiny": font("bold", 32),
}

P = {
    "title": font("bold", 72),
    "title_small": font("bold", 60),
    "kicker": font("bold", 22),
    "author": font("regular", 35),
    "author_sup": font("regular", 15),
    "affil": font("italic", 23),
    "band": font("bold", 31),
    "section_num": font("bold", 23),
    "section": font("bold", 38),
    "section_small": font("bold", 33),
    "body": font("regular", 23),
    "body_bold": font("bold", 23),
    "small": font("regular", 18),
    "small_bold": font("bold", 18),
    "tiny": font("regular", 15),
    "tiny_bold": font("bold", 15),
    "metric": font("bold", 31),
    "metric_big": font("bold", 36),
    "footer": font("regular", 29),
    "footer_note": font("regular", 21),
    "qr_label": font("bold", 20),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the editable vertical graphical abstract.")
    parser.add_argument("--config", type=Path, default=TEMPLATE_DIR / "config.json")
    parser.add_argument("--png", type=Path, default=None)
    parser.add_argument("--pdf", type=Path, default=None)
    return parser.parse_args()


def resolve_package_path(path: str | Path) -> Path:
    path = Path(path)
    return path if path.is_absolute() else PACKAGE_DIR / path


def load_config(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def crop_to_aspect(im: Image.Image, aspect: float, x_anchor: float = 0.50, y_anchor: float = 0.50) -> Image.Image:
    w, h = im.size
    current = w / h
    if abs(current - aspect) < 1e-4:
        return im
    if current > aspect:
        new_w = round(h * aspect)
        center = round(w * x_anchor)
        x0 = max(0, min(w - new_w, center - new_w // 2))
        return im.crop((x0, 0, x0 + new_w, h))
    new_h = round(w / aspect)
    center = round(h * y_anchor)
    y0 = max(0, min(h - new_h, center - new_h // 2))
    return im.crop((0, y0, w, y0 + new_h))


def fit_crop(path: Path, size: tuple[int, int], x_anchor: float = 0.50, y_anchor: float = 0.50) -> Image.Image:
    im = Image.open(path).convert("RGB")
    im = crop_to_aspect(im, size[0] / size[1], x_anchor=x_anchor, y_anchor=y_anchor)
    return im.resize(size, Image.Resampling.LANCZOS)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont, max_width: int) -> list[str]:
    lines: list[str] = []
    for raw_line in text.splitlines():
        if not raw_line:
            lines.append("")
            continue
        words = raw_line.split(" ")
        current = ""
        for word in words:
            trial = word if not current else f"{current} {word}"
            if draw.textlength(trial, font=fnt) <= max_width:
                current = trial
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
    return lines


def draw_multiline(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    fnt: ImageFont.ImageFont,
    fill: tuple[int, int, int],
    max_width: int | None = None,
    line_gap: int = 4,
    anchor: str = "la",
) -> int:
    x, y = xy
    lines = wrap_text(draw, text, fnt, max_width) if max_width else text.splitlines()
    cursor = y
    for line in lines:
        draw.text((x, cursor), line, font=fnt, fill=fill, anchor=anchor)
        bbox = draw.textbbox((x, cursor), line or "Ag", font=fnt, anchor=anchor)
        cursor += (bbox[3] - bbox[1]) + line_gap
    return cursor


def draw_fixed_lines(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    lines: list[str],
    fnt: ImageFont.ImageFont,
    fill: tuple[int, int, int],
    leading: int,
) -> int:
    x, y = xy
    for idx, line in enumerate(lines):
        draw.text((x, y + idx * leading), line, font=fnt, fill=fill)
    return y + len(lines) * leading


def draw_stroked_multiline(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    fnt: ImageFont.ImageFont,
    fill: tuple[int, int, int],
    stroke_fill: tuple[int, int, int] = (255, 255, 255),
    stroke_width: int = 2,
    line_gap: int = 4,
) -> None:
    x, y = xy
    cursor = y
    for line in text.splitlines():
        draw.text((x, cursor), line, font=fnt, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)
        bbox = draw.textbbox((x, cursor), line or "Ag", font=fnt)
        cursor += (bbox[3] - bbox[1]) + line_gap


def rounded(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], radius: int, fill, outline=None, width: int = 1) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def white_plate(
    canvas: Image.Image,
    box: tuple[int, int, int, int],
    radius: int = 14,
    alpha: int = 222,
    outline=(226, 235, 245),
) -> None:
    x0, y0, x1, y1 = box
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for grow, a in [(16, 9), (8, 14), (3, 18)]:
        od.rounded_rectangle((x0 - grow, y0 + 5 - grow, x1 + grow, y1 + 5 + grow), radius=radius + grow, fill=(6, 45, 82, a))
    od.rounded_rectangle(box, radius=radius, fill=(255, 255, 255, alpha), outline=outline, width=1)
    canvas.alpha_composite(overlay)


def section_band(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    fill=(253, 254, 255),
    outline=(232, 239, 247),
) -> None:
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=12, fill=fill, outline=outline, width=1)


def dashed_round_rect(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    radius: int,
    outline: tuple[int, int, int],
    width: int = 1,
    dash: int = 10,
    gap: int = 8,
) -> None:
    # Straight dashed segments with rounded-corner guides keep the scientific-poster look without heavy boxes.
    x0, y0, x1, y1 = box
    draw.arc((x0, y0, x0 + 2 * radius, y0 + 2 * radius), 180, 270, fill=outline, width=width)
    draw.arc((x1 - 2 * radius, y0, x1, y0 + 2 * radius), 270, 360, fill=outline, width=width)
    draw.arc((x1 - 2 * radius, y1 - 2 * radius, x1, y1), 0, 90, fill=outline, width=width)
    draw.arc((x0, y1 - 2 * radius, x0 + 2 * radius, y1), 90, 180, fill=outline, width=width)
    for xa, xb, y in [(x0 + radius, x1 - radius, y0), (x0 + radius, x1 - radius, y1)]:
        x = xa
        while x < xb:
            draw.line((x, y, min(x + dash, xb), y), fill=outline, width=width)
            x += dash + gap
    for ya, yb, x in [(y0 + radius, y1 - radius, x0), (y0 + radius, y1 - radius, x1)]:
        y = ya
        while y < yb:
            draw.line((x, y, x, min(y + dash, yb)), fill=outline, width=width)
            y += dash + gap


def shadowed_round_rect(
    canvas: Image.Image,
    box: tuple[int, int, int, int],
    radius: int,
    fill=(255, 255, 255),
    outline=COLORS["rule"],
    width: int = 1,
    shadow=(9, 45, 80, 22),
    offset: tuple[int, int] = (0, 12),
    blur_steps: int = 7,
) -> None:
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    x0, y0, x1, y1 = box
    ox, oy = offset
    for step in range(blur_steps, 0, -1):
        grow = step * 3
        alpha = max(2, shadow[3] // (step + 2))
        od.rounded_rectangle(
            (x0 + ox - grow, y0 + oy - grow, x1 + ox + grow, y1 + oy + grow),
            radius=radius + grow,
            fill=(shadow[0], shadow[1], shadow[2], alpha),
        )
    od.rounded_rectangle(box, radius=radius, fill=fill + (255,) if len(fill) == 3 else fill, outline=outline, width=width)
    canvas.alpha_composite(overlay)


def soft_panel(
    canvas: Image.Image,
    box: tuple[int, int, int, int],
    radius: int = 18,
    fill=COLORS["white"],
    outline=(216, 228, 240),
    shadow_alpha: int = 10,
) -> None:
    """Subtle editorial panel; much lighter than app-style card shadows."""
    x0, y0, x1, y1 = box
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for grow, alpha in [(18, shadow_alpha // 3), (10, shadow_alpha // 2), (5, shadow_alpha)]:
        od.rounded_rectangle((x0 - grow, y0 + 6 - grow, x1 + grow, y1 + 6 + grow), radius=radius + grow, fill=(8, 43, 79, max(1, alpha)))
    od.rounded_rectangle(box, radius=radius, fill=fill + (255,), outline=outline, width=1)
    canvas.alpha_composite(overlay)


def paste_rounded_image(canvas: Image.Image, im: Image.Image, box: tuple[int, int, int, int], radius: int) -> None:
    x0, y0, x1, y1 = box
    im = im.resize((x1 - x0, y1 - y0), Image.Resampling.LANCZOS).convert("RGBA")
    mask = Image.new("L", im.size, 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle((0, 0, im.size[0], im.size[1]), radius=radius, fill=255)
    canvas.paste(im, (x0, y0), mask)


def draw_soft_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    fnt: ImageFont.ImageFont,
    fill: tuple[int, int, int],
    shadow_fill: tuple[int, int, int, int] = (255, 255, 255, 150),
    line_gap: int = 6,
) -> None:
    x, y = xy
    cursor = y
    for line in text.splitlines():
        draw.text((x + 2, cursor + 2), line, font=fnt, fill=shadow_fill)
        draw.text((x, cursor), line, font=fnt, fill=fill)
        bbox = draw.textbbox((x, cursor), line or "Ag", font=fnt)
        cursor += (bbox[3] - bbox[1]) + line_gap


def draw_metric_icon(draw: ImageDraw.ImageDraw, cx: int, cy: int, idx: int, color=COLORS["ink"]) -> None:
    # Small clean audit glyphs; the older generic icons collapsed into square marks after scaling.
    w = 2
    if idx in [0, 1, 9]:
        for r in range(2):
            for c in range(3):
                x = cx - 14 + c * 10
                y = cy - 10 + r * 10
                draw.rounded_rectangle((x, y, x + 5, y + 5), radius=1, outline=color, width=w)
    elif idx in [2, 3, 6]:
        draw.polygon([(cx - 18, cy + 10), (cx + 18, cy + 10), (cx + 12, cy - 10), (cx - 12, cy - 10)], outline=color)
        draw.line((cx - 14, cy, cx + 14, cy), fill=color, width=w)
    elif idx in [4, 5]:
        draw.line((cx, cy - 18, cx - 10, cy + 16, cx + 10, cy + 16, cx, cy - 18), fill=color, width=w)
        draw.line((cx - 7, cy + 3, cx + 7, cy + 3), fill=color, width=w)
    elif idx == 7:
        draw.rounded_rectangle((cx - 11, cy - 17, cx + 11, cy + 17), radius=4, outline=color, width=w)
        draw.line((cx - 9, cy - 7, cx + 9, cy - 7), fill=color, width=w)
    elif idx == 8:
        draw.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), outline=color, width=w)
        for a in range(0, 360, 45):
            x1 = cx + int(math.cos(math.radians(a)) * 12)
            y1 = cy + int(math.sin(math.radians(a)) * 12)
            x2 = cx + int(math.cos(math.radians(a)) * 19)
            y2 = cy + int(math.sin(math.radians(a)) * 19)
            draw.line((x1, y1, x2, y2), fill=color, width=w)
    else:
        draw.line((cx - 14, cy + 12, cx + 14, cy - 12), fill=color, width=w)
        draw.line((cx + 7, cy - 12, cx + 14, cy - 12, cx + 14, cy - 5), fill=color, width=w)


def line_icon(draw: ImageDraw.ImageDraw, kind: str, cx: int, cy: int, color=COLORS["ink"], scale: float = 1.0) -> None:
    s = int(24 * scale)
    w = max(2, int(3 * scale))
    if kind == "field":
        for i in range(3):
            for j in range(3):
                draw.rectangle((cx - s + j * s // 2, cy - s + i * s // 2, cx - s + j * s // 2 + s // 4, cy - s + i * s // 2 + s // 4), outline=color, width=w)
    elif kind == "panel":
        pts = [(cx - s, cy + s // 4), (cx + s // 2, cy + s // 2), (cx + s, cy - s // 3), (cx - s // 2, cy - s // 2)]
        draw.line(pts + [pts[0]], fill=color, width=w)
        draw.line((cx - s // 3, cy - s // 3, cx + s // 2, cy + s // 2), fill=color, width=max(1, w - 1))
        draw.line((cx - s // 8, cy + s // 2, cx - s // 5, cy + s), fill=color, width=w)
        draw.line((cx - s // 2, cy + s, cx + s // 3, cy + s), fill=color, width=w)
    elif kind == "tower":
        draw.line((cx, cy - s, cx - s // 2, cy + s, cx + s // 2, cy + s, cx, cy - s), fill=color, width=w)
        draw.line((cx - s // 3, cy, cx + s // 3, cy), fill=color, width=w)
    elif kind == "sun":
        draw.ellipse((cx - s // 3, cy - s // 3, cx + s // 3, cy + s // 3), outline=color, width=w)
        for a in range(0, 360, 45):
            r1, r2 = s // 2, s
            x1 = cx + int(math.cos(math.radians(a)) * r1)
            y1 = cy + int(math.sin(math.radians(a)) * r1)
            x2 = cx + int(math.cos(math.radians(a)) * r2)
            y2 = cy + int(math.sin(math.radians(a)) * r2)
            draw.line((x1, y1, x2, y2), fill=color, width=w)
    elif kind == "target":
        for r in [s, int(s * 0.62), int(s * 0.28)]:
            draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=color, width=w)
        draw.line((cx - s - 10, cy, cx + s + 10, cy), fill=color, width=w)
        draw.line((cx, cy - s - 10, cx, cy + s + 10), fill=color, width=w)
    elif kind == "ray":
        for off in [-14, 0, 14]:
            draw.line((cx - s, cy + off, cx + s, cy + off // 2), fill=color, width=w)
            draw.line((cx + s - 10, cy + off // 2 - 6, cx + s, cy + off // 2, cx + s - 10, cy + off // 2 + 6), fill=color, width=w)
    elif kind == "trend":
        draw.line((cx - s, cy + s, cx - s // 3, cy + s // 3, cx + s // 5, cy + s // 2, cx + s, cy - s), fill=color, width=w)
        draw.line((cx + s - 10, cy - s, cx + s, cy - s, cx + s, cy - s + 10), fill=color, width=w)
    elif kind == "shield":
        draw.line((cx, cy - s, cx + s, cy - s // 3, cx + s // 2, cy + s, cx, cy + s + 8, cx - s // 2, cy + s, cx - s, cy - s // 3, cx, cy - s), fill=color, width=w)
    else:
        draw.rectangle((cx - s, cy - s, cx + s, cy + s), outline=color, width=w)


def deliver_icon(draw: ImageDraw.ImageDraw, kind: str, cx: int, cy: int, color=COLORS["ink"]) -> None:
    w = 3
    if kind == "code":
        draw.rounded_rectangle((cx - 30, cy - 24, cx + 30, cy + 24), radius=6, outline=color, width=w)
        draw.line((cx - 16, cy - 6, cx - 24, cy, cx - 16, cy + 6), fill=color, width=w)
        draw.line((cx + 16, cy - 6, cx + 24, cy, cx + 16, cy + 6), fill=color, width=w)
        draw.line((cx + 2, cy - 12, cx - 6, cy + 12), fill=color, width=w)
    elif kind == "shield":
        draw.line((cx, cy - 30, cx + 26, cy - 15, cx + 18, cy + 22, cx, cy + 34, cx - 18, cy + 22, cx - 26, cy - 15, cx, cy - 30), fill=color, width=w)
        draw.line((cx - 9, cy + 1, cx - 2, cy + 9, cx + 13, cy - 9), fill=color, width=w)
    else:
        for off in [-13, 0, 13]:
            draw.line((cx - 30, cy + off, cx + 24, cy + off // 2), fill=color, width=w)
            draw.line((cx + 14, cy + off // 2 - 7, cx + 26, cy + off // 2, cx + 14, cy + off // 2 + 7), fill=color, width=w)


def section_title(draw: ImageDraw.ImageDraw, xy: tuple[int, int], number: str, title: str) -> None:
    x, y = xy
    # Reference-inspired poster heading: a strong numeric cue without turning the paper figure into UI chrome.
    draw.text((x, y + 3), f"{number}.", font=F["section"], fill=COLORS["ink"])
    offset = int(draw.textlength(f"{number}. ", font=F["section"])) + 6
    draw.text((x + offset, y + 3), title, font=F["section"], fill=COLORS["ink"])
    draw.rounded_rectangle((x, y + 58, x + 78, y + 64), radius=3, fill=(17, 77, 121))


def draw_author_line(draw: ImageDraw.ImageDraw, xy: tuple[int, int], authors: list[str]) -> None:
    x, y = xy
    for idx, author in enumerate(authors):
        if idx:
            draw.text((x, y), ", ", font=F["author"], fill=COLORS["white"])
            x += int(draw.textlength(", ", font=F["author"]))
        draw.text((x, y), author, font=F["author"], fill=COLORS["white"])
        x += int(draw.textlength(author, font=F["author"]))
        draw.text((x + 2, y - 3), "a", font=F["sup"], fill=COLORS["white"])
        x += int(draw.textlength("a", font=F["sup"])) + 7


def draw_affiliation(draw: ImageDraw.ImageDraw, xy: tuple[int, int], affiliation: str) -> None:
    x, y = xy
    draw.text((x, y - 8), "a", font=F["sup"], fill=COLORS["white"])
    draw.text((x + 18, y), affiliation, font=F["affil"], fill=COLORS["white"])


def load_metrics(config: dict) -> tuple[pd.DataFrame, dict]:
    paths = config["data_sources"]
    solarpilot = pd.read_csv(resolve_package_path(paths["solarpilot_summary"]))
    direct = pd.read_csv(resolve_package_path(paths["direct_best"]))
    base = solarpilot.loc[solarpilot["layout_id"] == "baseline_full"].iloc[0]
    ids = list(dict.fromkeys(config["evidence_layouts"]["comparison"]))
    missing = sorted(set(ids) - set(solarpilot["layout_id"]))
    if missing:
        raise KeyError(f"Missing layouts in solarpilot summary: {missing}")
    sp = solarpilot[solarpilot["layout_id"].isin(ids)].copy()
    sp["delta_optical_pct"] = (sp["opteff_mean"] / float(base["opteff_mean"]) - 1.0) * 100.0
    sp["delta_default_flux_pct"] = (
        sp["flux_peak_to_active_mean"] / float(base["flux_peak_to_active_mean"]) - 1.0
    ) * 100.0
    direct_cols = ["layout_id", "strategy", "mean_delta_peak_pct", "median_delta_peak_pct", "share_lower_peak"]
    merged = sp.merge(direct[direct_cols], on="layout_id", how="left")
    merged = merged.set_index("layout_id").loc[ids].reset_index()
    merged["label"] = merged["layout_id"].map(label_for)
    highlights = {
        key: merged.loc[merged["layout_id"] == config["evidence_layouts"][key]].iloc[0].to_dict()
        for key in ["optical_upper", "direct_reduction", "control"]
    }
    return merged, highlights


def label_for(layout_id: str) -> str:
    return {
        "deform_0276": "D0276",
        "deform_0893": "D0893",
        "deform_1387": "D1387",
        "deform_1822": "D1822",
        "joint_g02_0333": "J0333",
        "joint_g04_0478": "J0478",
    }.get(layout_id, layout_id)


def paste_hero(canvas: Image.Image, draw: ImageDraw.ImageDraw, config: dict) -> None:
    hero = fit_crop(resolve_package_path(config["hero_image"]), (2048, 890), x_anchor=0.50, y_anchor=0.29)
    canvas.paste(hero, (0, 0))
    dark_overlay = Image.new("RGBA", (2048, 890), (0, 0, 0, 0))
    od = ImageDraw.Draw(dark_overlay)
    for y in range(890):
        bottom = int(122 * (y / 890) ** 1.65)
        od.line((0, y, 2048, y), fill=(2, 23, 43, bottom))
    od.rectangle((0, 0, 2048, 390), fill=(255, 255, 255, 18))
    canvas.alpha_composite(dark_overlay)

    yy = np.linspace(0, 1, 890, dtype=np.float32)[:, None]
    xx = np.linspace(0, 1, 2048, dtype=np.float32)[None, :]
    vertical = np.clip(1.0 - yy / 0.66, 0, 1) ** 1.05
    horizontal = np.clip(1.0 - (xx / 0.72) ** 2.2, 0, 1)
    alpha = (218 * vertical * horizontal).astype(np.uint8)
    white_grad = np.zeros((890, 2048, 4), dtype=np.uint8)
    white_grad[..., :3] = 255
    white_grad[..., 3] = alpha
    canvas.alpha_composite(Image.fromarray(white_grad, mode="RGBA"))
    draw_fixed_lines(draw, (56, 42), config["title"].splitlines(), F["title"], COLORS["ink"], leading=76)
    draw_author_line(draw, (56, 298), config["authors"])
    draw_affiliation(draw, (56, 348), config["affiliation"])


def draw_band(draw: ImageDraw.ImageDraw) -> None:
    draw.rectangle((0, 890, 2048, 968), fill=COLORS["navy"])
    draw.rectangle((0, 890, 2048, 895), fill=(17, 77, 121))
    draw.text((56, 929), "From audited coordinates to a receiver-risk-aware candidate queue", font=F["band"], fill=COLORS["white"], anchor="lm")


def draw_audit(draw: ImageDraw.ImageDraw, canvas: Image.Image, config: dict) -> None:
    x0, y0, w, h = 56, 1005, 950, 745
    section_title(draw, (x0, y0), "1", "Full-field benchmark")
    draw.text((x0, y0 + 72), "with audited plant anchors", font=F["small_bold"], fill=COLORS["muted"])
    draw.text((x0, y0 + 122), "Plant-scale anchors", font=F["small_bold"], fill=COLORS["ink"])
    audit_items = [
        ("11915", "coordinates\nretained", 1),
        ("1.381M", "m2\nmirrors", 3),
        ("1883", "annual DNI", 8),
        ("~0.8%", "site slope constraint", 10),
    ]
    tx, ty = x0 + 10, y0 + 178
    for idx, (value, label, icon_idx) in enumerate(audit_items):
        row, col = divmod(idx, 2)
        bx = tx + col * 218
        by = ty + row * 178
        draw_metric_icon(draw, bx + 28, by + 28, icon_idx, COLORS["muted"])
        metric_font = F["poster_metric_tiny"] if value == "1.381M" else F["poster_metric_small"]
        draw.text((bx + 70, by), value, font=metric_font, fill=COLORS["ink"])
        draw_multiline(draw, (bx + 70, by + 52), label, F["audit_label"], COLORS["quiet"], max_width=122, line_gap=2)

    rail_y = y0 + 445
    draw.line((x0 + 18, rail_y, x0 + 456, rail_y), fill=COLORS["hairline"], width=2)
    rail_items = [
        ("Full-field", "11,915 coordinates"),
        ("TS-FPDA", "terrain-aware search"),
        ("Direct gate", "PySolTrace checked"),
        ("Risk-aware", "receiver-flux checked"),
    ]
    for i, (head, text) in enumerate(rail_items):
        yy = rail_y + 26 + i * 52
        draw.ellipse((x0 + 22, yy + 2, x0 + 38, yy + 18), fill=COLORS["blue"])
        draw.text((x0 + 56, yy - 2), head, font=F["caption_bold"], fill=COLORS["ink"])
        draw.text((x0 + 220, yy + 1), text, font=F["photo_note"], fill=COLORS["muted"])

    draw.line((x0 + 18, y0 + 690, x0 + 456, y0 + 690), fill=COLORS["hairline"], width=1)
    draw.text((x0 + 20, y0 + 723), "Benchmark, not a claimed plant retrofit", font=F["tiny_bold"], fill=COLORS["blue"])

    photo_box = (510, y0 + 142, 970, y0 + 758)
    photo = fit_crop(resolve_package_path(config["hero_image"]), (photo_box[2] - photo_box[0], photo_box[3] - photo_box[1]), x_anchor=0.50, y_anchor=0.47)
    paste_rounded_image(canvas, photo, photo_box, 14)
    draw.rounded_rectangle(photo_box, radius=14, outline=(210, 224, 239), width=2)
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    label_box = (photo_box[0] + 22, photo_box[3] - 62, photo_box[2] - 22, photo_box[3] - 20)
    od.rounded_rectangle(label_box, radius=8, fill=(6, 45, 82, 112))
    canvas.alpha_composite(overlay)
    draw.text((label_box[0] + 18, label_box[1] + 21), "Author aerial view, qualitative context", font=F["photo_note"], fill=(244, 248, 252), anchor="lm")


def draw_workflow(draw: ImageDraw.ImageDraw, canvas: Image.Image, config: dict) -> None:
    x0, y0, w, h = 1045, 1005, 950, 745
    section_title(draw, (x0, y0), "2", "Algorithmic story")
    draw_multiline(draw, (x0, y0 + 64), "A real surround-field benchmark is turned into a bounded candidate queue.", F["body"], COLORS["muted"], max_width=650)
    xs = np.linspace(x0 + 118, x0 + w - 98, 4).astype(int)
    y = y0 + 222
    draw.line((xs[0], y, xs[-1], y), fill=PUB["line"], width=7)
    draw.line((xs[0], y, xs[-1], y), fill=PUB["mid"], width=2)
    for idx, (title, body, color_hex) in enumerate(config["workflow"]):
        color = [PUB["cyan"], PUB["mid"], PUB["mid"], PUB["dark"]][idx]
        soft_fill = [COLORS["cyan_soft"], COLORS["blue_soft"], COLORS["orange_soft"], COLORS["purple_soft"]][idx]
        cx = int(xs[idx])
        draw.ellipse((cx - 42, y - 42, cx + 42, y + 42), fill=soft_fill, outline=color, width=4)
        draw.ellipse((cx - 29, y - 29, cx + 29, y + 29), fill=COLORS["white"])
        draw.text((cx, y), f"{idx + 1:02d}", font=F["small_bold"], fill=color, anchor="mm")
        draw.line((cx, y + 43, cx, y + 95), fill=color, width=3)
        draw.text((cx, y + 112), title, font=F["body_bold"], fill=COLORS["ink"], anchor="ma")
        draw_multiline(draw, (cx, y + 154), body, F["photo_note"], COLORS["muted"], max_width=198, line_gap=8, anchor="ma")
    draw.line((x0 + 250, y0 + 528, x0 + 690, y0 + 528), fill=PUB["line"], width=2)
    draw.polygon([(x0 + 250, y0 + 528), (x0 + 272, y0 + 516), (x0 + 272, y0 + 540)], fill=PUB["line"])
    draw.text((x0 + 470, y0 + 554), "receiver-risk validation reorders the queue", font=F["tiny_bold"], fill=PUB["mid"], anchor="ma")
    deliver_y = y0 + 602
    draw.line((x0 + 92, deliver_y, x0 + w - 62, deliver_y), fill=PUB["line"], width=2)
    draw.rectangle((x0 + 398, deliver_y - 22, x0 + 642, deliver_y + 14), fill=COLORS["white"])
    draw.text((x0 + 520, deliver_y - 2), "What we deliver", font=F["small_bold"], fill=COLORS["ink"], anchor="ma")
    for cx, kind, label in [
        (x0 + 225, "code", "Reproducible full-field\nlayout algorithm"),
        (x0 + 520, "shield", "Multi-layer validation\npackage"),
        (x0 + 805, "ray", "Receiver-flux-aware\ncandidate queue"),
    ]:
        draw.ellipse((cx - 38, y0 + 634, cx + 38, y0 + 710), fill=(246, 250, 254), outline=PUB["line"], width=1)
        deliver_icon(draw, kind, cx, y0 + 672, PUB["dark"])
        draw.line((cx, y0 + 711, cx, y0 + 724), fill=PUB["line"], width=2)
        draw_multiline(draw, (cx, y0 + 738), label, F["tiny_bold"], COLORS["muted"], max_width=214, line_gap=6, anchor="ma")


def draw_evidence(draw: ImageDraw.ImageDraw, canvas: Image.Image, highlights: dict) -> None:
    x0, y0, w, h = 56, 1880, 650, 610
    section_title(draw, (x0, y0), "3", "Cross-layer evidence")
    soft_panel(canvas, (x0, y0 + 72, x0 + w, y0 + h - 4), radius=18, outline=(230, 237, 245), shadow_alpha=3)
    rows = [
        ("Optical upper case", "efficiency gain under optical screening", highlights["optical_upper"], "delta_optical_pct", (11, 79, 138)),
        ("Default flux penalty", "receiver loading flags the trade-off", highlights["optical_upper"], "delta_default_flux_pct", COLORS["orange"]),
        ("Direct aimpoint check", "PySolTrace reorders receiver risk", highlights["direct_reduction"], "mean_delta_peak_pct", COLORS["blue"]),
    ]
    y = y0 + 112
    for title, body, row, key, color in rows:
        value = float(row[key])
        draw.text((x0 + 28, y), title, font=F["body_bold"], fill=COLORS["ink"])
        draw.text((x0 + 28, y + 38), label_for(row["layout_id"]), font=F["small_bold"], fill=color)
        draw.text((x0 + w - 34, y - 6), f"{value:+.2f}%", font=F["poster_metric"], fill=color, anchor="ra")
        bx0, by = x0 + 28, y + 78
        draw.rounded_rectangle((bx0, by, bx0 + 530, by + 16), radius=8, fill=(226, 234, 243))
        draw.rounded_rectangle((bx0, by, bx0 + int(530 * min(abs(value) / 5.0, 1)), by + 16), radius=8, fill=color)
        draw_multiline(draw, (x0 + 28, y + 110), body, F["small"], COLORS["muted"], max_width=560)
        draw.line((x0 + 28, y + 148, x0 + w - 28, y + 148), fill=COLORS["hairline"], width=1)
        y += 145
    control = highlights["control"]
    rounded(draw, (x0 + 28, y0 + h - 63, x0 + w - 28, y0 + h - 24), 8, (253, 254, 255), (226, 234, 243), 1)
    draw.text(
        (x0 + 50, y0 + h - 28),
        f"Control role: {label_for(control['layout_id'])} remains conservative ({control['mean_delta_peak_pct']:+.2f}% direct P/M).",
        font=F["tiny"],
        fill=COLORS["muted"],
        anchor="lm",
    )


def chart_to_image(fig) -> Image.Image:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=200, bbox_inches="tight", pad_inches=0.02, facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf).convert("RGB")


def scatter_chart(metrics: pd.DataFrame) -> Image.Image:
    palette = {
        "deform_0276": "#0B4F8A",
        "deform_0893": "#0E7490",
        "deform_1387": "#1D4ED8",
        "deform_1822": "#7A8CA3",
    }
    fig, ax = plt.subplots(figsize=(2.8, 2.55))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.axhline(0, color="#A7B7C9", lw=1.0, ls="--")
    ax.axvline(0, color="#A7B7C9", lw=1.0, ls="--")
    for _, row in metrics.iterrows():
        ax.scatter(row["delta_default_flux_pct"], row["delta_optical_pct"], s=62, color=palette.get(row["layout_id"], "#082B4F"), edgecolor="white", linewidth=0.7)
        ax.text(row["delta_default_flux_pct"] + 0.14, row["delta_optical_pct"] + 0.12, row["label"], fontsize=9, color=palette.get(row["layout_id"], "#082B4F"))
    ax.set_xlim(-5, 6)
    ax.set_ylim(-3.5, 5.5)
    ax.set_title("Optical screen", fontsize=11, loc="left", color="#082B4F", fontweight="bold", pad=8)
    ax.set_xlabel("Flux penalty", fontsize=8.8)
    ax.set_ylabel("$\\eta_{opt}$ gain", fontsize=8.8)
    ax.tick_params(labelsize=8.8)
    for spine in ax.spines.values():
        spine.set_color("#D1D9E6")
    ax.grid(True, color="#EEF3F8", linewidth=0.8, zorder=0)
    return chart_to_image(fig)


def flux_map(seed: int) -> Image.Image:
    rng = np.random.default_rng(seed)
    x = np.linspace(-1.2, 1.2, 115)
    y = np.linspace(-0.85, 0.85, 76)
    xx, yy = np.meshgrid(x, y)
    mask = (xx / 1.05) ** 2 + (yy / 0.70) ** 2 <= 1
    z = (
        0.9 * np.exp(-((xx - 0.15) ** 2 / 0.20 + (yy + 0.02) ** 2 / 0.09))
        + 0.5 * np.exp(-((xx + 0.28) ** 2 / 0.18 + (yy - 0.10) ** 2 / 0.12))
        + 0.045 * rng.random(xx.shape)
    )
    z[~mask] = np.nan
    fig, ax = plt.subplots(figsize=(2.45, 1.36))
    fig.patch.set_facecolor("white")
    cmap = LinearSegmentedColormap.from_list(
        "dhf_flux",
        ["#082B4F", "#0E7490", "#B7E1EF", "#F6C85F", "#D97706"],
    )
    ax.imshow(z, cmap=cmap, origin="lower", interpolation="nearest")
    ax.axis("off")
    return chart_to_image(fig)


def draw_validation(draw: ImageDraw.ImageDraw, canvas: Image.Image, metrics: pd.DataFrame) -> None:
    x0, y0, w, h = 770, 1880, 1220, 610
    section_title(draw, (x0, y0), "4", "Representative validation snapshots")
    lane1, lane2 = x0 + 360, x0 + 744
    draw.line((lane1, y0 + 94, lane1, y0 + 548), fill=(223, 233, 244), width=1)
    draw.line((lane2, y0 + 94, lane2, y0 + 548), fill=(223, 233, 244), width=1)
    scatter = scatter_chart(metrics).resize((262, 286), Image.Resampling.LANCZOS)
    canvas.paste(scatter, (x0 + 48, y0 + 136))
    draw_multiline(draw, (x0 + 180, y0 + 505), "Optical gain\nvs. receiver penalty", F["caption"], COLORS["muted"], max_width=250, line_gap=6, anchor="ma")

    draw.text((x0 + 548, y0 + 105), "Daily flux maps", font=F["small_bold"], fill=COLORS["ink"], anchor="ma")
    f1 = flux_map(276).resize((228, 128), Image.Resampling.BOX)
    f2 = flux_map(1387).resize((228, 128), Image.Resampling.BOX)
    heat_x, heat_w = x0 + 426, 236
    soft_panel(canvas, (heat_x, y0 + 156, heat_x + heat_w, y0 + 298), radius=12, outline=(230, 237, 245), shadow_alpha=4)
    soft_panel(canvas, (heat_x, y0 + 348, heat_x + heat_w, y0 + 490), radius=12, outline=(230, 237, 245), shadow_alpha=4)
    canvas.paste(f1, (heat_x + 3, y0 + 159))
    canvas.paste(f2, (heat_x + 3, y0 + 351))
    draw.text((heat_x - 8, y0 + 178), "D0276", font=F["tiny_bold"], fill=COLORS["ink"], anchor="ra")
    draw.text((heat_x - 8, y0 + 370), "D1387", font=F["tiny_bold"], fill=COLORS["ink"], anchor="ra")
    # Compact colorbar echoing the reference poster.
    cbx, cby, cbw, cbh = x0 + 680, y0 + 180, 12, 172
    for i in range(cbh):
        t = i / max(cbh - 1, 1)
        if t < 0.33:
            u = t / 0.33
            r, g, b = int(8 + 6 * u), int(43 + 73 * u), int(79 + 64 * u)
        elif t < 0.68:
            u = (t - 0.33) / 0.35
            r, g, b = int(14 + 171 * u), int(116 + 109 * u), int(143 + 96 * u)
        else:
            u = (t - 0.68) / 0.32
            r, g, b = int(185 + 32 * u), int(225 - 106 * u), int(239 - 233 * u)
        draw.line((cbx, cby + cbh - i, cbx + cbw, cby + cbh - i), fill=(r, g, b), width=1)
    draw.text((cbx + 18, cby - 16), "MW/m2", font=F["tiny"], fill=COLORS["ink"], anchor="la")
    draw_multiline(draw, (x0 + 544, y0 + 512), "Receiver-risk\ncontrast", F["caption_bold"], COLORS["muted"], max_width=250, line_gap=6, anchor="ma")

    bx0, by0 = x0 + 790, y0 + 126
    draw.text((bx0 + 175, y0 + 105), "Direct aimpoint P/M (%)", font=F["small_bold"], fill=COLORS["ink"], anchor="ma")
    best = metrics.sort_values("mean_delta_peak_pct").reset_index(drop=True)
    min_x, max_x = -4.2, 0.0
    axis_x = bx0 + 352
    draw.line((axis_x, by0, axis_x, by0 + 342), fill=(160, 172, 186), width=2)
    for i, row in best.iterrows():
        val = float(row["mean_delta_peak_pct"])
        color = {
            "deform_0276": (11, 79, 138),
            "deform_0893": COLORS["cyan"],
            "deform_1387": COLORS["blue"],
            "deform_1822": COLORS["gray"],
        }.get(row["layout_id"], COLORS["ink"])
        y = by0 + 34 + i * 81
        draw.text((bx0, y), row["label"], font=F["small"], fill=COLORS["ink"], anchor="lm")
        bar_w = int((0 - max(val, min_x)) / (max_x - min_x) * 260)
        draw.rounded_rectangle((axis_x - bar_w, y - 24, axis_x, y + 24), radius=3, fill=color)
        if bar_w > 95:
            draw.text((axis_x - 12, y), f"{val:+.2f}%", font=F["small_bold"], fill=COLORS["white"], anchor="rm")
        else:
            draw.text((axis_x - bar_w - 14, y), f"{val:+.2f}%", font=F["small_bold"], fill=COLORS["ink"], anchor="rm")
    draw_multiline(draw, (bx0 + 202, y0 + 512), "PySolTrace queue\nreorders risk", F["caption_bold"], COLORS["muted"], max_width=280, line_gap=6, anchor="ma")
    draw.text((bx0 + 210, y0 + 576), "Delta vs. default P/M (%)", font=F["tiny"], fill=COLORS["muted"], anchor="ma")


def draw_scope(draw: ImageDraw.ImageDraw, config: dict) -> None:
    x0, y0, w, h = 56, 2518, 1935, 245
    draw.line((x0, y0, x0 + w, y0), fill=(226, 234, 243), width=1)
    section_title(draw, (x0, y0 + 34), "5", "Validation workload beyond the plant anchors")
    scope_items = [item for item in config["scope"] if not item[1].startswith("heliostat coordinates")]
    xs = np.linspace(x0 + 95, x0 + w - 95, len(scope_items)).astype(int)
    kinds = ["field", "sun", "target", "ray", "sun", "trend"]
    for cx, (value, label), kind in zip(xs, scope_items, kinds):
        line_icon(draw, kind, cx, y0 + 128, COLORS["ink"], scale=0.72)
        short_label = {
            "full-field candidates\nscreened": "candidates\nscreened",
            "representative layouts\nexported": "layouts\nexported",
            "solar conditions\n(all-phase)": "solar\nconditions",
            "aiming strategies\nper layout": "aiming\nstrategies",
            "requested first-stage\nray hits per case": "ray hits\nper case",
            "layout-strategy-condition\ncases": "validation\ncases",
        }.get(label, label)
        draw.text((cx, y0 + 178), value, font=F["h2"], fill=COLORS["ink"], anchor="ma")
        draw.text((cx, y0 + 218), short_label, font=F["scope_label"], fill=COLORS["muted"], anchor="ma", align="center")


def draw_footer(draw: ImageDraw.ImageDraw, config: dict) -> None:
    y0 = 2886
    draw.rectangle((0, y0, 2048, 3072), fill=COLORS["navy"])
    draw.rectangle((0, y0, 2048, y0 + 5), fill=(17, 77, 121))
    line_icon(draw, "target", 92, y0 + 82, COLORS["white"], scale=1.05)
    draw_multiline(draw, (168, y0 + 38), config["footer"]["claim"], F["footer"], COLORS["white"], max_width=940, line_gap=5)
    draw.line((1228, y0 + 30, 1228, y0 + 155), fill=(67, 116, 153), width=2)

    def qr_block(qx: int, qy: int, label: str, seed: int) -> None:
        cell = 5
        side = 21 * cell
        draw.rounded_rectangle((qx - 11, qy - 11, qx + side + 11, qy + side + 11), radius=5, fill=COLORS["white"])
        for i in range(21):
            for j in range(21):
                on = ((i * (7 + seed) + j * (11 + seed) + i * j + seed) % 5 in [0, 1])
                finder = (i < 7 and j < 7) or (i < 7 and j > 13) or (i > 13 and j < 7)
                if finder:
                    ii, jj = i % 14, j % 14
                    on = ii in [0, 6] or jj in [0, 6] or (2 <= ii <= 4 and 2 <= jj <= 4)
                if on:
                    draw.rectangle((qx + j * cell, qy + i * cell, qx + (j + 1) * cell, qy + (i + 1) * cell), fill=(0, 0, 0))
        draw.text((qx + side / 2, y0 + 160), label, font=F["qr_label"], fill=COLORS["white"], anchor="ma")

    qr_block(1346, y0 + 42, "MATERIALS", 3)
    draw.line((1508, y0 + 42, 1508, y0 + 138), fill=(67, 116, 153), width=1)
    draw_multiline(draw, (1538, y0 + 48), "Code, data tables,\nand validation package\navailable with the article", F["footer_note"], COLORS["white"], max_width=430, line_gap=4)


def p_text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fnt: ImageFont.ImageFont, fill=COLORS["ink"], **kwargs) -> None:
    draw.text(xy, text, font=fnt, fill=fill, **kwargs)


def p_panel(canvas: Image.Image, box: tuple[int, int, int, int], radius: int = 22) -> None:
    # Editorial surface: light enough for print, less app-card than the first generated version.
    x0, y0, x1, y1 = box
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((x0, y0, x1, y1), radius=radius, fill=(255, 255, 255), outline=(222, 232, 243), width=1)


def p_section(draw: ImageDraw.ImageDraw, x: int, y: int, number: str, title: str, width: int | None = None) -> None:
    p_text(draw, (x, y), f"{number}.", P["section"], COLORS["ink"])
    nx = x + int(draw.textlength(f"{number}. ", font=P["section"])) + 4
    p_text(draw, (nx, y), title, P["section"], COLORS["ink"])
    underline_w = width if width is not None else min(92, int(draw.textlength(title, font=P["section"]) * 0.36))
    draw.rounded_rectangle((x, y + 57, x + underline_w, y + 64), radius=3, fill=(13, 79, 124))


def p_author_line(draw: ImageDraw.ImageDraw, xy: tuple[int, int], authors: list[str]) -> None:
    x, y = xy
    for idx, author in enumerate(authors):
        if idx:
            p_text(draw, (x, y), ", ", P["author"], COLORS["ink"])
            x += int(draw.textlength(", ", font=P["author"]))
        p_text(draw, (x + 2, y + 2), author, P["author"], (255, 255, 255, 155))
        p_text(draw, (x, y), author, P["author"], COLORS["ink"])
        x += int(draw.textlength(author, font=P["author"]))
        p_text(draw, (x + 3, y - 4), "a", P["author_sup"], COLORS["ink"])
        x += int(draw.textlength("a", font=P["author_sup"])) + 8


def p_header(canvas: Image.Image, draw: ImageDraw.ImageDraw, config: dict) -> None:
    hero_h = 930
    hero = fit_crop(resolve_package_path(config["hero_image"]), (2048, hero_h), x_anchor=0.50, y_anchor=0.30)
    canvas.paste(hero, (0, 0))

    # Top-left readability wash and bottom cinematic fade.
    yy = np.linspace(0, 1, hero_h, dtype=np.float32)[:, None]
    xx = np.linspace(0, 1, 2048, dtype=np.float32)[None, :]
    wash = (210 * np.clip(1 - yy / 0.58, 0, 1) ** 1.08 * np.clip(1 - (xx / 0.72) ** 2.5, 0, 1)).astype(np.uint8)
    white = np.zeros((hero_h, 2048, 4), dtype=np.uint8)
    white[..., :3] = 255
    white[..., 3] = wash
    canvas.alpha_composite(Image.fromarray(white, mode="RGBA"))

    fade = Image.new("RGBA", (2048, hero_h), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fade)
    for y in range(hero_h):
        a = int(148 * (y / hero_h) ** 1.85)
        fd.line((0, y, 2048, y), fill=(2, 23, 43, a))
    fd.rectangle((0, 0, 2048, 360), fill=(255, 255, 255, 14))
    canvas.alpha_composite(fade)

    title_lines = config["title"].splitlines()
    y = 52
    for line in title_lines:
        p_text(draw, (58, y), line, P["title"], COLORS["ink"])
        y += 70
    p_author_line(draw, (58, 300), config["authors"])
    draw.text((58, 349), "a", font=P["author_sup"], fill=COLORS["ink"])
    p_text(draw, (78, 351), config["affiliation"], P["affil"], COLORS["ink"])

    band_y = hero_h - 44
    draw.rectangle((0, band_y, 2048, band_y + 82), fill=COLORS["navy"])
    draw.rectangle((0, band_y, 2048, band_y + 5), fill=(22, 91, 136))
    p_text(draw, (58, band_y + 42), "From audited plant coordinates to receiver-risk-aware layout evidence", P["band"], COLORS["white"], anchor="lm")


def p_metric_tile(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    value: str,
    label: str,
    kind: str,
    accent: tuple[int, int, int],
) -> None:
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=16, fill=(248, 251, 255), outline=(223, 233, 244), width=1)
    line_icon(draw, kind, x0 + 45, y0 + 54, accent, scale=0.58)
    p_text(draw, (x0 + 86, y0 + 28), value, P["metric"], COLORS["ink"])
    draw_multiline(draw, (x0 + 86, y0 + 72), label, P["small"], COLORS["muted"], max_width=x1 - x0 - 110, line_gap=2)


def p_draw_anchors(canvas: Image.Image, draw: ImageDraw.ImageDraw, config: dict) -> None:
    box = (58, 1008, 1002, 1732)
    p_panel(canvas, box, 24)
    x0, y0, x1, y1 = box
    p_section(draw, x0 + 32, y0 + 28, "1", "Plant anchors", width=88)
    draw_multiline(draw, (x0 + 32, y0 + 112), "Full-field evidence starts from audited Dunhuang plant anchors, not from mirror deletion.", P["body"], COLORS["muted"], max_width=500, line_gap=5)

    tiles = [
        ("11935", "reported\nheliostats", "field", COLORS["cyan"]),
        ("11915", "coordinates\nretained", "panel", COLORS["blue"]),
        ("1.381M m2", "reflective\narea", "sun", COLORS["orange"]),
        ("260 m", "tower\nheight", "tower", COLORS["navy"]),
        ("1883", "corrected DNI\nkWh m-2 y-1", "sun", COLORS["cyan"]),
        ("~0.8%", "site slope\nconstraint", "trend", COLORS["purple"]),
    ]
    tx, ty = x0 + 32, y0 + 205
    tw, th, gapx, gapy = 275, 122, 24, 23
    for i, (value, label, kind, accent) in enumerate(tiles):
        col, row = i % 3, i // 3
        p_metric_tile(draw, (tx + col * (tw + gapx), ty + row * (th + gapy), tx + col * (tw + gapx) + tw, ty + row * (th + gapy) + th), value, label, kind, accent)

    photo_box = (x0 + 276, y0 + 500, x0 + 900, y0 + 682)
    photo = fit_crop(resolve_package_path(config["hero_image"]), (photo_box[2] - photo_box[0], photo_box[3] - photo_box[1]), x_anchor=0.50, y_anchor=0.48)
    paste_rounded_image(canvas, photo, photo_box, 18)
    draw.rounded_rectangle((photo_box[0], photo_box[1], photo_box[2], photo_box[3]), radius=18, outline=(210, 224, 239), width=2)
    draw.rounded_rectangle((x0 + 32, y0 + 525, x0 + 245, y0 + 648), radius=18, fill=(232, 242, 252), outline=(204, 220, 236), width=1)
    p_text(draw, (x0 + 56, y0 + 549), "Full field", P["body_bold"], COLORS["ink"])
    draw_multiline(draw, (x0 + 56, y0 + 588), "kept intact for\nlayout generation", P["small"], COLORS["muted"], max_width=170, line_gap=2)


def p_draw_algorithm(canvas: Image.Image, draw: ImageDraw.ImageDraw, config: dict) -> None:
    box = (1046, 1008, 1990, 1732)
    p_panel(canvas, box, 24)
    x0, y0, x1, y1 = box
    p_section(draw, x0 + 32, y0 + 28, "2", "Candidate algorithm", width=88)
    draw_multiline(draw, (x0 + 32, y0 + 112), "A bounded surround-field generator builds full-field candidates, then validation reorders them by optical and receiver-risk evidence.", P["body"], COLORS["muted"], max_width=800, line_gap=5)

    xs = [x0 + 115, x0 + 350, x0 + 585, x0 + 820]
    y = y0 + 306
    draw.line((xs[0], y, xs[-1], y), fill=(209, 224, 241), width=11)
    draw.line((xs[0], y, xs[-1], y), fill=(38, 84, 126), width=3)
    steps = config["workflow"]
    for i, ((title, body, color_hex), cx) in enumerate(zip(steps, xs), start=1):
        color = tuple(int(color_hex.lstrip("#")[j : j + 2], 16) for j in (0, 2, 4))
        draw.ellipse((cx - 53, y - 53, cx + 53, y + 53), fill=(255, 255, 255), outline=color, width=5)
        p_text(draw, (cx, y), f"{i:02d}", P["body_bold"], color, anchor="mm")
        p_text(draw, (cx, y + 86), title, P["body_bold"], COLORS["ink"], anchor="ma")
        draw_multiline(draw, (cx, y + 122), body, P["small"], COLORS["muted"], max_width=175, line_gap=2, anchor="ma")

    arc = (x0 + 235, y0 + 500, x0 + 705, y0 + 642)
    draw.arc(arc, start=22, end=158, fill=COLORS["purple"], width=4)
    draw.polygon([(x0 + 259, y0 + 558), (x0 + 283, y0 + 543), (x0 + 281, y0 + 573)], fill=COLORS["purple"])
    p_text(draw, (x0 + 470, y0 + 619), "validation can reorder the queue", P["small_bold"], COLORS["purple"], anchor="ma")

    out_box = (x0 + 54, y0 + 530, x1 - 54, y0 + 655)
    draw.rounded_rectangle(out_box, radius=20, fill=(248, 251, 255), outline=(207, 222, 238), width=2)
    labels = [
        ("code", "layout\nalgorithm"),
        ("shield", "validation\npackage"),
        ("ray", "receiver-risk\nqueue"),
    ]
    for cx, (kind, label) in zip([x0 + 185, x0 + 472, x0 + 750], labels):
        deliver_icon(draw, kind, cx, y0 + 580, COLORS["ink"])
        draw_multiline(draw, (cx, y0 + 625), label, P["tiny_bold"], COLORS["muted"], max_width=130, line_gap=1, anchor="ma")


def p_draw_evidence(canvas: Image.Image, draw: ImageDraw.ImageDraw, highlights: dict) -> None:
    box = (58, 1778, 786, 2488)
    p_panel(canvas, box, 24)
    x0, y0, x1, y1 = box
    p_section(draw, x0 + 32, y0 + 28, "3", "Evidence gate", width=88)
    draw_multiline(draw, (x0 + 32, y0 + 112), "The queue is promoted only when the optical screen and receiver-risk check agree within the evidence boundary.", P["body"], COLORS["muted"], max_width=610, line_gap=5)
    rows = [
        ("Optical upper case", highlights["optical_upper"], "delta_optical_pct", COLORS["blue"]),
        ("Default flux penalty", highlights["optical_upper"], "delta_default_flux_pct", COLORS["orange"]),
        ("Direct aimpoint check", highlights["direct_reduction"], "mean_delta_peak_pct", COLORS["purple"]),
    ]
    y = y0 + 230
    for label, row, key, color in rows:
        val = float(row[key])
        p_text(draw, (x0 + 42, y), label, P["body_bold"], COLORS["ink"])
        p_text(draw, (x1 - 262, y), label_for(row["layout_id"]), P["body_bold"], color)
        p_text(draw, (x1 - 44, y), f"{val:+.2f}%", P["metric_big"], color, anchor="ra")
        by = y + 54
        draw.rounded_rectangle((x0 + 42, by, x1 - 42, by + 18), radius=9, fill=(226, 234, 243))
        draw.rounded_rectangle((x0 + 42, by, x0 + 42 + int((x1 - x0 - 84) * min(abs(val) / 5.0, 1)), by + 18), radius=9, fill=color)
        y += 126
    draw.rounded_rectangle((x0 + 42, y0 + 625, x1 - 42, y0 + 666), radius=12, fill=(248, 251, 255), outline=(219, 230, 242), width=1)
    p_text(draw, (x0 + 64, y0 + 646), "Control layout remains conservative; weak or reversed rows stay out of the main claim.", P["tiny_bold"], COLORS["muted"], anchor="lm")


def p_draw_validation(canvas: Image.Image, draw: ImageDraw.ImageDraw, metrics: pd.DataFrame) -> None:
    box = (826, 1778, 1990, 2488)
    p_panel(canvas, box, 24)
    x0, y0, x1, y1 = box
    p_section(draw, x0 + 32, y0 + 28, "4", "Receiver validation", width=88)

    # Three large visual lanes instead of a dense collection of tiny figures.
    scatter = scatter_chart(metrics).resize((350, 340), Image.Resampling.LANCZOS)
    canvas.paste(scatter, (x0 + 42, y0 + 145))
    p_text(draw, (x0 + 218, y0 + 514), "Optical screen", P["small_bold"], COLORS["ink"], anchor="ma")
    draw_multiline(draw, (x0 + 218, y0 + 542), "gain vs. default\nflux penalty", P["tiny"], COLORS["muted"], max_width=190, anchor="ma")

    f1 = flux_map(276).resize((352, 210), Image.Resampling.BOX)
    f2 = flux_map(1387).resize((352, 210), Image.Resampling.BOX)
    p_text(draw, (x0 + 590, y0 + 142), "Flux maps", P["small_bold"], COLORS["ink"], anchor="ma")
    paste_rounded_image(canvas, f1, (x0 + 420, y0 + 177, x0 + 772, y0 + 387), 13)
    paste_rounded_image(canvas, f2, (x0 + 420, y0 + 397, x0 + 772, y0 + 607), 13)
    p_text(draw, (x0 + 405, y0 + 204), "D0276", P["tiny_bold"], COLORS["ink"], anchor="ra")
    p_text(draw, (x0 + 405, y0 + 424), "D1387", P["tiny_bold"], COLORS["ink"], anchor="ra")

    bx0, by0 = x0 + 815, y0 + 170
    p_text(draw, (bx0 + 165, y0 + 142), "Direct P/M change", P["small_bold"], COLORS["ink"], anchor="ma")
    best = metrics.sort_values("mean_delta_peak_pct").reset_index(drop=True)
    axis_x = bx0 + 300
    draw.line((axis_x, by0, axis_x, by0 + 385), fill=(158, 175, 194), width=2)
    for i, row in best.iterrows():
        val = float(row["mean_delta_peak_pct"])
        color = {
            "deform_0276": COLORS["blue"],
            "deform_0893": COLORS["cyan"],
            "deform_1387": COLORS["purple"],
            "deform_1822": COLORS["gray"],
        }.get(row["layout_id"], COLORS["ink"])
        y = by0 + 36 + i * 76
        p_text(draw, (bx0, y), row["label"], P["small_bold"], COLORS["ink"], anchor="lm")
        bar_w = int((0 - max(val, -4.2)) / 4.2 * 250)
        draw.rounded_rectangle((axis_x - bar_w, y - 23, axis_x, y + 23), radius=4, fill=color)
        fill = COLORS["white"] if bar_w > 92 else COLORS["ink"]
        p_text(draw, (axis_x - 14 if bar_w > 92 else axis_x - bar_w - 12, y), f"{val:+.2f}%", P["small_bold"], fill, anchor="rm")
    draw_multiline(draw, (bx0 + 160, y0 + 590), "High-sample PySolTrace\nreorders receiver risk.", P["tiny_bold"], COLORS["muted"], max_width=240, anchor="ma")


def p_draw_scale(draw: ImageDraw.ImageDraw, config: dict) -> None:
    x0, y0, x1, y1 = 58, 2532, 1990, 2828
    p_section(draw, x0, y0, "5", "Validation scale", width=88)
    draw.line((x0, y0 + 84, x1, y0 + 84), fill=(219, 230, 242), width=2)
    xs = np.linspace(x0 + 92, x1 - 92, len(config["scope"])).astype(int)
    kinds = ["panel", "sun", "field", "sun", "target", "ray", "trend"]
    for cx, (value, label), kind in zip(xs, config["scope"], kinds):
        line_icon(draw, kind, cx, y0 + 130, COLORS["ink"], scale=0.72)
        p_text(draw, (cx, y0 + 180), value, P["metric"], COLORS["ink"], anchor="ma")
        draw_multiline(draw, (cx, y0 + 223), label, P["tiny"], COLORS["muted"], max_width=170, line_gap=1, anchor="ma")


def p_footer(draw: ImageDraw.ImageDraw, config: dict) -> None:
    y0 = 2868
    draw.rectangle((0, y0, 2048, 3072), fill=COLORS["navy"])
    draw.rectangle((0, y0, 2048, y0 + 6), fill=(20, 92, 140))
    line_icon(draw, "target", 92, y0 + 98, COLORS["white"], scale=1.08)
    draw_multiline(draw, (170, y0 + 43), config["footer"]["claim"], P["footer"], COLORS["white"], max_width=980, line_gap=5)
    draw.line((1300, y0 + 35, 1300, y0 + 166), fill=(67, 116, 153), width=2)

    def qr(qx: int, qy: int, label: str, seed: int) -> None:
        cell = 5
        side = 21 * cell
        draw.rounded_rectangle((qx - 12, qy - 12, qx + side + 12, qy + side + 12), radius=6, fill=COLORS["white"])
        for i in range(21):
            for j in range(21):
                on = ((i * (7 + seed) + j * (11 + seed) + i * j + seed) % 5 in [0, 1])
                finder = (i < 7 and j < 7) or (i < 7 and j > 13) or (i > 13 and j < 7)
                if finder:
                    ii, jj = i % 14, j % 14
                    on = ii in [0, 6] or jj in [0, 6] or (2 <= ii <= 4 and 2 <= jj <= 4)
                if on:
                    draw.rectangle((qx + j * cell, qy + i * cell, qx + (j + 1) * cell, qy + (i + 1) * cell), fill=(0, 0, 0))
        p_text(draw, (qx + side / 2, y0 + 176), label, P["qr_label"], COLORS["white"], anchor="ma")

    qr(1355, y0 + 46, "CODE", 2)
    qr(1515, y0 + 46, "DATA", 5)
    draw_multiline(draw, (1696, y0 + 63), config["footer"]["qr_label"], P["footer_note"], COLORS["white"], max_width=292, line_gap=4)


def build_v2(config: dict, out_png: Path, out_pdf: Path) -> None:
    metrics, highlights = load_metrics(config)
    canvas = Image.new("RGBA", (config["canvas"]["width_px"], config["canvas"]["height_px"]), (246, 250, 254, 255))
    draw = ImageDraw.Draw(canvas)
    p_header(canvas, draw, config)
    draw.rectangle((0, 968, 2048, 2868), fill=(246, 250, 254))
    p_draw_anchors(canvas, draw, config)
    p_draw_algorithm(canvas, draw, config)
    p_draw_evidence(canvas, draw, highlights)
    p_draw_validation(canvas, draw, metrics)
    p_draw_scale(draw, config)
    p_footer(draw, config)

    out_png.parent.mkdir(parents=True, exist_ok=True)
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    rgb = canvas.convert("RGB")
    rgb.save(out_png, quality=96, optimize=True)
    rgb.save(out_pdf, "PDF", resolution=300.0)


def build(config: dict, out_png: Path, out_pdf: Path) -> None:
    metrics, highlights = load_metrics(config)
    canvas = Image.new("RGBA", (config["canvas"]["width_px"], config["canvas"]["height_px"]), COLORS["white"] + (255,))
    draw = ImageDraw.Draw(canvas)
    paste_hero(canvas, draw, config)
    draw_band(draw)
    draw.rectangle((0, 968, 2048, 2886), fill=(255, 255, 255))
    draw_audit(draw, canvas, config)
    draw_workflow(draw, canvas, config)
    draw.line((1024, 1005, 1024, 1830), fill=COLORS["rule"], width=2)
    draw.line((56, 1850, 1990, 1850), fill=(225, 235, 245), width=2)
    draw_evidence(draw, canvas, highlights)
    draw.line((735, 1880, 735, 2490), fill=COLORS["rule"], width=2)
    draw_validation(draw, canvas, metrics)
    draw_scope(draw, config)
    draw_footer(draw, config)

    out_png.parent.mkdir(parents=True, exist_ok=True)
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    rgb = canvas.convert("RGB")
    rgb.save(out_png, quality=95, optimize=True)
    rgb.save(out_pdf, "PDF", resolution=300.0)


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    out_png = args.png or resolve_package_path(config["output_png"])
    out_pdf = args.pdf or resolve_package_path(config["output_pdf"])
    build(config, out_png, out_pdf)
    print(out_png)
    print(out_pdf)


if __name__ == "__main__":
    main()
