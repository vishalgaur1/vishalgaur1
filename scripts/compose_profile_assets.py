"""Compose editorial film-title PNG panels for the GitHub profile README.

Identity: ink on warm paper — poster typography, no glass / neon / skill pills.
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

# Warm paper + ink (reads as a physical title board on GitHub dark chrome)
PAPER = (243, 237, 226)
PAPER_EDGE = (232, 224, 210)
INK = (24, 20, 16)
INK_SOFT = (78, 68, 56)
RULE = (24, 20, 16)

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


def paper_canvas(height: int, seed: int = 1) -> Image.Image:
    """Flat cream panel with faint grain — no gradient blobs."""
    rng = random.Random(seed)
    img = Image.new("RGB", (W, height), PAPER)
    px = img.load()
    for y in range(height):
        edge = min(y, height - 1 - y, 18) / 18.0
        for x in range(W):
            edge_x = min(x, W - 1 - x, 18) / 18.0
            t = min(edge, edge_x)
            base = PAPER if t > 0.85 else tuple(
                int(PAPER[i] + (PAPER_EDGE[i] - PAPER[i]) * (1 - t) * 0.55) for i in range(3)
            )
            n = rng.randint(-5, 5)
            px[x, y] = tuple(max(0, min(255, base[i] + n)) for i in range(3))
    return img


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt) -> tuple[int, int]:
    b = draw.textbbox((0, 0), text, font=fnt)
    return b[2] - b[0], b[3] - b[1]


def hairline(draw: ImageDraw.ImageDraw, y: int, x0: int = 72, x1: int | None = None, width: int = 1) -> None:
    if x1 is None:
        x1 = W - 72
    draw.line([(x0, y), (x1, y)], fill=RULE, width=width)


def save_rgb(img: Image.Image, path: Path) -> None:
    if img.mode != "RGB":
        img = img.convert("RGB")
    img.save(path, "PNG", optimize=True)
    print(f"wrote {path.name} {img.size} {path.stat().st_size // 1024}KB")


def make_hero() -> None:
    """Dramatic full-width title board — name bottom-heavy, one craft line."""
    h = 520
    img = paper_canvas(h, seed=7)
    draw = ImageDraw.Draw(img)

    meta = font("SourceSans3-Semibold.ttf", 15)
    name_f = font("InstrumentSerif-Regular.ttf", 92)
    role_f = font("InstrumentSerif-Italic.ttf", 28)
    craft_f = font("SourceSans3-Regular.ttf", 22)

    # top meta row — film slate feel
    draw.text((72, 48), "BENGALURU", font=meta, fill=INK_SOFT)
    right = "NEUOPTIC · VOXORYL"
    rw, _ = text_size(draw, right, meta)
    draw.text((W - 72 - rw, 48), right, font=meta, fill=INK_SOFT)
    hairline(draw, 78)

    # bottom-heavy name block
    name = "Vishal Gaur"
    nw, nh = text_size(draw, name, name_f)
    name_y = h - 210
    draw.text((72, name_y), name, font=name_f, fill=INK)

    role = "Co-founder & Director, NeuOptic"
    draw.text((72, name_y + nh + 8), role, font=role_f, fill=INK_SOFT)

    hairline(draw, name_y + nh + 56, x1=72 + min(nw, 420))

    craft = "Product interfaces end-to-end — AR, ops platforms, local AI."
    draw.text((72, name_y + nh + 72), craft, font=craft_f, fill=INK)

    save_rgb(img, OUT / "hero.png")


def make_neuoptic() -> None:
    """Flat typographic contents strip — not a nested card grid."""
    h = 300
    img = paper_canvas(h, seed=19)
    draw = ImageDraw.Draw(img)

    mark_f = font("Fraunces-SemiBold.ttf", 36)
    lead_f = font("InstrumentSerif-Italic.ttf", 24)
    item_f = font("SourceSans3-Semibold.ttf", 20)
    desc_f = font("SourceSans3-Regular.ttf", 18)

    draw.text((72, 44), "NeuOptic", font=mark_f, fill=INK)
    draw.text((72, 96), "Practical tools for real businesses.", font=lead_f, fill=INK_SOFT)
    hairline(draw, 148)

    entries = [
        ("Arvi", "Web AR catalogues for showrooms — light, phone-smooth."),
        ("NeoEngine", "Staff ops & ERP — reminders, workflows, attendance, payroll."),
    ]

    y = 168
    for title, desc in entries:
        draw.text((72, y), title, font=item_f, fill=INK)
        tw, _ = text_size(draw, title, item_f)
        # dotted leader toward description
        dots_x0 = 72 + tw + 16
        dots_x1 = 340
        for x in range(dots_x0, dots_x1, 8):
            draw.point((x, y + 12), fill=INK_SOFT)
        draw.text((dots_x1 + 12, y), desc, font=desc_f, fill=INK_SOFT)
        y += 48

    save_rgb(img, OUT / "neuoptic.png")


def make_voxoryl() -> None:
    """Bold wordmark + one plain sentence."""
    h = 220
    img = paper_canvas(h, seed=31)
    draw = ImageDraw.Draw(img)

    mark_f = font("Fraunces-SemiBold.ttf", 64)
    body_f = font("SourceSans3-Regular.ttf", 22)
    meta_f = font("SourceSans3-Regular.ttf", 15)

    draw.text((72, 48), "VOXORYL", font=mark_f, fill=INK)
    hairline(draw, 128, x1=320)
    draw.text(
        (72, 148),
        "Local-first voice desktop companion — on-device reasoning, private memory.",
        font=body_f,
        fill=INK,
    )
    draw.text((72, 182), "Say “Hey Voxy”.  ·  vox-OR-ill", font=meta_f, fill=INK_SOFT)

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
