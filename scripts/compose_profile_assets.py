"""Compose dark editorial PNG panels for the GitHub profile README.

High-contrast type on GitHub-dark surfaces. Sized HARD for ~900px README
width: body ≥ 36px on a 1280 canvas (~25px on screen). No baked link rows —
README uses whole-image <a> only.
"""
from __future__ import annotations

import random
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets"
FONT_DIR = ROOT / "fonts"
OUT.mkdir(exist_ok=True)
FONT_DIR.mkdir(exist_ok=True)

W = 1280
# Inner content inset (generous; panel chrome sits outside this)
PAD = 48
CONTENT_X = 88
CONTENT_RIGHT = W - 88

# GitHub dark chrome + high-contrast type
CANVAS = (13, 17, 23)       # #0d1117
SURFACE = (22, 27, 34)      # #161b22
SURFACE_HI = (28, 33, 40)
BORDER = (48, 54, 61)       # #30363d
CREAM = (232, 226, 214)     # primary titles
INK = (230, 237, 243)       # #e6edf3 body / secondary
INK_SOFT = (210, 218, 226)  # meta only
RULE = (48, 54, 61)

FONT_URLS = {
    "InstrumentSerif-Regular.ttf": (
        "https://cdn.jsdelivr.net/fontsource/fonts/instrument-serif@5.2.5/latin-400-normal.ttf"
    ),
    "InstrumentSerif-Italic.ttf": (
        "https://cdn.jsdelivr.net/fontsource/fonts/instrument-serif@5.2.5/latin-400-italic.ttf"
    ),
    "Fraunces-SemiBold.ttf": (
        "https://cdn.jsdelivr.net/fontsource/fonts/fraunces@5.2.5/latin-600-normal.ttf"
    ),
    "Fraunces-Regular.ttf": (
        "https://cdn.jsdelivr.net/fontsource/fonts/fraunces@5.2.5/latin-400-normal.ttf"
    ),
    "SourceSans3-Regular.ttf": (
        "https://cdn.jsdelivr.net/fontsource/fonts/source-sans-3@5.2.5/latin-400-normal.ttf"
    ),
    "SourceSans3-Semibold.ttf": (
        "https://cdn.jsdelivr.net/fontsource/fonts/source-sans-3@5.2.5/latin-600-normal.ttf"
    ),
}


def ensure_fonts() -> None:
    for name, url in FONT_URLS.items():
        path = FONT_DIR / name
        if path.exists() and path.stat().st_size > 10_000:
            continue
        print(f"downloading {name}…")
        urllib.request.urlretrieve(url, path)


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_DIR / name), size)


def dark_canvas(height: int, seed: int = 1) -> Image.Image:
    """GitHub-dark field + inset surface panel with #30363d border."""
    rng = random.Random(seed)
    img = Image.new("RGB", (W, height), CANVAS)
    px = img.load()
    for y in range(height):
        for x in range(W):
            n = rng.randint(-3, 3)
            px[x, y] = tuple(max(0, min(255, CANVAS[i] + n)) for i in range(3))

    draw = ImageDraw.Draw(img)
    box = (PAD, PAD, W - PAD, height - PAD)
    draw.rounded_rectangle(box, radius=12, fill=SURFACE, outline=BORDER, width=1)
    x0, y0, x1, y1 = box
    draw.line([(x0 + 14, y0 + 1), (x1 - 14, y0 + 1)], fill=SURFACE_HI, width=1)
    return img


def text_bbox(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fnt) -> tuple[int, int, int, int]:
    return draw.textbbox(xy, text, font=fnt)


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt) -> tuple[int, int]:
    b = draw.textbbox((0, 0), text, font=fnt)
    return b[2] - b[0], b[3] - b[1]


def hairline(draw: ImageDraw.ImageDraw, y: int, x0: int = CONTENT_X, x1: int | None = None, width: int = 1) -> None:
    if x1 is None:
        x1 = CONTENT_RIGHT
    draw.line([(x0, y), (x1, y)], fill=RULE, width=width)


def wrap_lines(draw: ImageDraw.ImageDraw, text: str, fnt, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        trial = f"{cur} {w}".strip()
        tw, _ = text_size(draw, trial, fnt)
        if tw <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def save_rgb(img: Image.Image, path: Path) -> None:
    if img.mode != "RGB":
        img = img.convert("RGB")
    img.save(path, "PNG", optimize=True)
    print(f"wrote {path.name} {img.size} {path.stat().st_size // 1024}KB")


def make_hero() -> None:
    """Title board — large type, generous top pad, no destination footer row."""
    h = 680
    img = dark_canvas(h, seed=7)
    draw = ImageDraw.Draw(img)

    # Canvas sizes → ~900px display scale ≈ 0.70
    meta = font("SourceSans3-Semibold.ttf", 30)      # ~21px on screen
    name_f = font("InstrumentSerif-Regular.ttf", 108)  # ~50% over original 72
    role_f = font("InstrumentSerif-Italic.ttf", 44)
    craft_f = font("SourceSans3-Regular.ttf", 38)    # hard bump for GitHub column

    # Generous top padding: panel edge at PAD → meta well clear of chrome
    meta_y = PAD + 64
    draw.text((CONTENT_X, meta_y), "BENGALURU", font=meta, fill=INK)
    right = "NEUOPTIC · VOXORYL"
    rw, _ = text_size(draw, right, meta)
    draw.text((CONTENT_RIGHT - rw, meta_y), right, font=meta, fill=INK)
    meta_bottom = text_bbox(draw, (CONTENT_X, meta_y), "BENGALURU", meta)[3]
    hairline(draw, meta_bottom + 32)

    name = "Vishal Gaur"
    role = "Co-founder & Director, NeuOptic"
    craft = "Product interfaces end-to-end — AR, ops platforms, local AI."

    name_y = meta_bottom + 60
    draw.text((CONTENT_X, name_y), name, font=name_f, fill=CREAM)
    name_bottom = text_bbox(draw, (CONTENT_X, name_y), name, name_f)[3]

    role_y = name_bottom + 32
    draw.text((CONTENT_X, role_y), role, font=role_f, fill=INK)
    role_bottom = text_bbox(draw, (CONTENT_X, role_y), role, role_f)[3]

    rule_y = role_bottom + 32
    hairline(draw, rule_y, x1=CONTENT_X + 460)

    craft_y = rule_y + 36
    draw.text((CONTENT_X, craft_y), craft, font=craft_f, fill=INK)
    craft_bottom = text_bbox(draw, (CONTENT_X, craft_y), craft, craft_f)[3]

    # Bottom breathing room (no link row)
    assert craft_bottom <= h - PAD - 56, f"craft too close to bottom: {craft_bottom}"
    assert role_y - name_bottom >= 28, f"name/role gap too tight"
    assert meta_y - PAD >= 56, f"meta top pad too small: {meta_y - PAD}"

    save_rgb(img, OUT / "hero.png")


def make_neuoptic() -> None:
    """Project strip — large legible rows, no link footer."""
    h = 660
    img = dark_canvas(h, seed=19)
    draw = ImageDraw.Draw(img)

    mark_f = font("Fraunces-SemiBold.ttf", 60)
    lead_f = font("InstrumentSerif-Italic.ttf", 38)
    item_f = font("SourceSans3-Semibold.ttf", 34)
    desc_f = font("SourceSans3-Regular.ttf", 32)

    title_y = PAD + 56
    draw.text((CONTENT_X, title_y), "NeuOptic", font=mark_f, fill=CREAM)
    mark_bottom = text_bbox(draw, (CONTENT_X, title_y), "NeuOptic", mark_f)[3]

    lead_y = mark_bottom + 22
    lead = "Practical tools for real businesses."
    draw.text((CONTENT_X, lead_y), lead, font=lead_f, fill=INK)
    lead_bottom = text_bbox(draw, (CONTENT_X, lead_y), lead, lead_f)[3]
    hairline(draw, lead_bottom + 32)

    entries = [
        ("Arvi", "Web AR catalogues for showrooms — light, phone-smooth."),
        ("NeoEngine", "Staff ops & ERP — reminders, workflows, attendance, payroll."),
    ]

    y = lead_bottom + 56
    max_desc = CONTENT_RIGHT - 420
    for title, desc in entries:
        draw.text((CONTENT_X, y), title, font=item_f, fill=CREAM)
        tw, th = text_size(draw, title, item_f)
        dots_x0 = CONTENT_X + tw + 20
        dots_x1 = 400
        mid_y = y + th // 2
        for x in range(dots_x0, dots_x1, 8):
            draw.point((x, mid_y), fill=BORDER)
        lines = wrap_lines(draw, desc, desc_f, max_desc)
        ly = y
        for line in lines:
            draw.text((dots_x1 + 18, ly), line, font=desc_f, fill=INK)
            ly = text_bbox(draw, (dots_x1 + 18, ly), line, desc_f)[3] + 6
        y = max(y + th, ly) + 32

    assert y <= h - PAD - 48, f"neuoptic content overflows: {y}"

    save_rgb(img, OUT / "neuoptic.png")


def make_voxoryl() -> None:
    """Bold wordmark + body — no GitHub/Site footer row."""
    h = 540
    img = dark_canvas(h, seed=31)
    draw = ImageDraw.Draw(img)

    mark_f = font("Fraunces-SemiBold.ttf", 88)
    body_f = font("SourceSans3-Regular.ttf", 38)
    meta_f = font("SourceSans3-Regular.ttf", 28)

    title_y = PAD + 56
    draw.text((CONTENT_X, title_y), "VOXORYL", font=mark_f, fill=CREAM)
    mark_bottom = text_bbox(draw, (CONTENT_X, title_y), "VOXORYL", mark_f)[3]
    hairline(draw, mark_bottom + 24, x1=CONTENT_X + 400)

    body = "Local-first voice desktop companion — on-device reasoning, private memory."
    body_y = mark_bottom + 44
    max_w = CONTENT_RIGHT - CONTENT_X
    lines = wrap_lines(draw, body, body_f, max_w)
    y = body_y
    for line in lines:
        draw.text((CONTENT_X, y), line, font=body_f, fill=INK)
        y = text_bbox(draw, (CONTENT_X, y), line, body_f)[3] + 12

    draw.text((CONTENT_X, y + 18), 'Say “Hey Voxy”.  ·  vox-OR-ill', font=meta_f, fill=INK)
    meta_bottom = text_bbox(draw, (CONTENT_X, y + 18), 'Say “Hey Voxy”.  ·  vox-OR-ill', meta_f)[3]
    assert meta_bottom <= h - PAD - 48, f"voxoryl content overflows: {meta_bottom}"

    save_rgb(img, OUT / "voxoryl.png")


def retire_stale() -> None:
    for stale in (
        "featured.png",
        "focus.png",
        "footer.png",
        "divider.svg",
        "typing-voxoryl.png",
        "typing-voxoryl.svg",
        "banner.png",
    ):
        p = OUT / stale
        if p.exists():
            p.unlink()
            print(f"removed {stale}")


def main() -> None:
    ensure_fonts()
    make_hero()
    make_neuoptic()
    make_voxoryl()
    retire_stale()


if __name__ == "__main__":
    main()
