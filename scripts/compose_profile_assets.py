"""Compose dark editorial PNG panels for the GitHub profile README.

Identity: warm cream type on GitHub-dark surfaces — serif title boards,
no paper bricks, no cyan glass, no skill pills.
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

# GitHub dark chrome + warm type only (not cream panels)
CANVAS = (13, 17, 23)       # #0d1117
SURFACE = (22, 27, 34)      # #161b22
SURFACE_HI = (28, 33, 40)   # slight lift
BORDER = (48, 54, 61)       # #30363d
CREAM = (232, 226, 214)     # warm off-white for type
CREAM_DIM = (168, 160, 148)
RULE = (48, 54, 61)
INK_MUTED = (125, 133, 144)  # #7d8590-ish

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
    # faint grain on canvas
    for y in range(height):
        for x in range(W):
            n = rng.randint(-3, 3)
            px[x, y] = tuple(max(0, min(255, CANVAS[i] + n)) for i in range(3))

    draw = ImageDraw.Draw(img)
    pad = 28
    box = (pad, pad, W - pad, height - pad)
    draw.rounded_rectangle(box, radius=12, fill=SURFACE, outline=BORDER, width=1)
    # soft inner top edge (print board, not glass)
    x0, y0, x1, y1 = box
    draw.line([(x0 + 14, y0 + 1), (x1 - 14, y0 + 1)], fill=SURFACE_HI, width=1)
    return img


def text_bbox(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fnt) -> tuple[int, int, int, int]:
    return draw.textbbox(xy, text, font=fnt)


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt) -> tuple[int, int]:
    b = draw.textbbox((0, 0), text, font=fnt)
    return b[2] - b[0], b[3] - b[1]


def hairline(draw: ImageDraw.ImageDraw, y: int, x0: int = 72, x1: int | None = None, width: int = 1) -> None:
    if x1 is None:
        x1 = W - 72
    draw.line([(x0, y), (x1, y)], fill=RULE, width=width)


def draw_footer_links(draw: ImageDraw.ImageDraw, y: int, labels: list[str], fnt) -> None:
    """Bake destinations as cream type — no blue markdown under the card."""
    sep = "  ·  "
    line = sep.join(labels)
    draw.text((72, y), line, font=fnt, fill=INK_MUTED)


def save_rgb(img: Image.Image, path: Path) -> None:
    if img.mode != "RGB":
        img = img.convert("RGB")
    img.save(path, "PNG", optimize=True)
    print(f"wrote {path.name} {img.size} {path.stat().st_size // 1024}KB")


def make_hero() -> None:
    """Title board — cream serif on dark surface; no descender collision."""
    h = 540
    img = dark_canvas(h, seed=7)
    draw = ImageDraw.Draw(img)

    meta = font("SourceSans3-Semibold.ttf", 15)
    # Slightly smaller name + absolute ink bbox leading = crisp gap under descenders
    name_f = font("InstrumentSerif-Regular.ttf", 72)
    role_f = font("InstrumentSerif-Italic.ttf", 26)
    craft_f = font("SourceSans3-Regular.ttf", 20)
    foot_f = font("SourceSans3-Regular.ttf", 15)

    draw.text((72, 56), "BENGALURU", font=meta, fill=CREAM_DIM)
    right = "NEUOPTIC · VOXORYL"
    rw, _ = text_size(draw, right, meta)
    draw.text((W - 72 - rw, 56), right, font=meta, fill=CREAM_DIM)
    hairline(draw, 86)

    # Bottom-up stack so craft never collides with baked destinations
    foot_labels = ["neuoptic.in", "NeoEngine", "LinkedIn", "Email"]
    foot_line = "  ·  ".join(foot_labels)
    foot_h = text_bbox(draw, (0, 0), foot_line, foot_f)[3]
    foot_y = h - 48 - foot_h

    craft = "Product interfaces end-to-end — AR, ops platforms, local AI."
    craft_h = text_bbox(draw, (0, 0), craft, craft_f)[3]
    craft_y = foot_y - 28 - craft_h

    rule_y = craft_y - 18

    role = "Co-founder & Director, NeuOptic"
    role_h = text_bbox(draw, (0, 0), role, role_f)[3]
    role_y = rule_y - 20 - role_h

    name = "Vishal Gaur"
    # Place name so its ink bottom sits a full editorial gap above the role ink top
    name_probe = text_bbox(draw, (0, 0), name, name_f)
    name_ink_bottom_offset = name_probe[3]
    name_ink_top_offset = name_probe[1]
    role_ink_top_at = text_bbox(draw, (0, role_y), role, role_f)[1]
    name_bottom_target = role_ink_top_at - 52
    name_y = name_bottom_target - name_ink_bottom_offset
    # Keep name below the top rule with breathing room
    name_y = max(name_y, 118 - name_ink_top_offset)

    draw.text((72, name_y), name, font=name_f, fill=CREAM)
    draw.text((72, role_y), role, font=role_f, fill=CREAM_DIM)
    hairline(draw, rule_y, x1=72 + 360)
    draw.text((72, craft_y), craft, font=craft_f, fill=CREAM)
    draw_footer_links(draw, foot_y, foot_labels, foot_f)

    # Sanity: name descenders must clear role; craft must clear footer
    nb = text_bbox(draw, (72, name_y), name, name_f)
    rb = text_bbox(draw, (72, role_y), role, role_f)
    cb = text_bbox(draw, (72, craft_y), craft, craft_f)
    fb = text_bbox(draw, (72, foot_y), foot_line, foot_f)
    assert rb[1] - nb[3] >= 36, f"name/role gap too tight: {rb[1] - nb[3]}"
    assert fb[1] - cb[3] >= 16, f"craft/footer gap too tight: {fb[1] - cb[3]}"

    save_rgb(img, OUT / "hero.png")


def make_neuoptic() -> None:
    """Flat typographic contents strip on dark surface."""
    h = 320
    img = dark_canvas(h, seed=19)
    draw = ImageDraw.Draw(img)

    mark_f = font("Fraunces-SemiBold.ttf", 34)
    lead_f = font("InstrumentSerif-Italic.ttf", 22)
    item_f = font("SourceSans3-Semibold.ttf", 19)
    desc_f = font("SourceSans3-Regular.ttf", 17)
    foot_f = font("SourceSans3-Regular.ttf", 15)

    draw.text((72, 52), "NeuOptic", font=mark_f, fill=CREAM)
    mark_bottom = text_bbox(draw, (72, 52), "NeuOptic", mark_f)[3]
    lead_y = mark_bottom + 14
    draw.text((72, lead_y), "Practical tools for real businesses.", font=lead_f, fill=CREAM_DIM)
    lead_bottom = text_bbox(draw, (72, lead_y), "Practical tools for real businesses.", lead_f)[3]
    hairline(draw, lead_bottom + 16)

    entries = [
        ("Arvi", "Web AR catalogues for showrooms — light, phone-smooth."),
        ("NeoEngine", "Staff ops & ERP — reminders, workflows, attendance, payroll."),
    ]

    y = lead_bottom + 36
    for title, desc in entries:
        draw.text((72, y), title, font=item_f, fill=CREAM)
        tw, _ = text_size(draw, title, item_f)
        dots_x0 = 72 + tw + 16
        dots_x1 = 340
        for x in range(dots_x0, dots_x1, 8):
            draw.point((x, y + 11), fill=BORDER)
        draw.text((dots_x1 + 12, y), desc, font=desc_f, fill=CREAM_DIM)
        y += 44

    draw_footer_links(draw, h - 54, ["Arvi", "NeoEngine", "NeuOptic"], foot_f)

    save_rgb(img, OUT / "neuoptic.png")


def make_voxoryl() -> None:
    """Bold wordmark + one plain sentence on dark surface."""
    h = 240
    img = dark_canvas(h, seed=31)
    draw = ImageDraw.Draw(img)

    mark_f = font("Fraunces-SemiBold.ttf", 56)
    body_f = font("SourceSans3-Regular.ttf", 20)
    meta_f = font("SourceSans3-Regular.ttf", 15)
    foot_f = font("SourceSans3-Regular.ttf", 15)

    draw.text((72, 52), "VOXORYL", font=mark_f, fill=CREAM)
    mark_bottom = text_bbox(draw, (72, 52), "VOXORYL", mark_f)[3]
    hairline(draw, mark_bottom + 14, x1=300)

    body_y = mark_bottom + 30
    body = "Local-first voice desktop companion — on-device reasoning, private memory."
    draw.text((72, body_y), body, font=body_f, fill=CREAM)
    body_bottom = text_bbox(draw, (72, body_y), body, body_f)[3]
    draw.text((72, body_bottom + 10), 'Say “Hey Voxy”.  ·  vox-OR-ill', font=meta_f, fill=CREAM_DIM)

    draw_footer_links(draw, h - 52, ["GitHub", "Site"], foot_f)

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
