"""Compose icy-glass PNG cards for GitHub profile README."""
from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets"
OUT.mkdir(exist_ok=True)

W = 1280
FONT_DIR = Path(r"C:\Windows\Fonts")

# Palette — icy glass on deep navy (pops on GitHub dark mode)
BG0 = (6, 10, 18)
BG1 = (12, 20, 36)
BG2 = (18, 32, 56)
ICE = (126, 200, 255)
ICE_SOFT = (168, 216, 255)
GLASS = (255, 255, 255)
TEXT = (232, 241, 255)
MUTED = (139, 163, 199)
LINE = (70, 110, 160)


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_DIR / name), size)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def base_canvas(height: int, seed: int = 1) -> Image.Image:
    """Deep navy gradient + soft icy glow + sparse grid."""
    rng = random.Random(seed)
    img = Image.new("RGB", (W, height), BG0)
    px = img.load()
    for y in range(height):
        ty = y / max(height - 1, 1)
        row = lerp(BG0, BG1, ty * 0.85)
        for x in range(W):
            tx = x / max(W - 1, 1)
            # radial icy glow top-right
            dx = (tx - 0.82) * 1.4
            dy = (ty - 0.18) * 1.6
            g = math.exp(-(dx * dx + dy * dy) * 3.2)
            c = lerp(row, BG2, g * 0.55)
            # secondary bloom left
            dx2 = (tx - 0.12) * 1.8
            dy2 = (ty - 0.75) * 1.8
            g2 = math.exp(-(dx2 * dx2 + dy2 * dy2) * 4.0)
            c = lerp(c, (20, 40, 72), g2 * 0.35)
            # film grain
            n = rng.randint(-4, 4)
            px[x, y] = tuple(max(0, min(255, c[i] + n)) for i in range(3))

    draw = ImageDraw.Draw(img, "RGBA")
    # perspective-ish grid (subtle)
    for i in range(0, W, 48):
        alpha = 18
        draw.line([(i, height // 3), (i, height)], fill=(*LINE, alpha), width=1)
    for j in range(height // 3, height, 36):
        draw.line([(0, j), (W, j)], fill=(*LINE, 14), width=1)

    # soft edge vignette
    vig = Image.new("L", (W, height), 0)
    vd = ImageDraw.Draw(vig)
    vd.ellipse((-W * 0.15, -height * 0.4, W * 1.15, height * 1.3), fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(90))
    dark = Image.new("RGB", (W, height), (2, 4, 8))
    img = Image.composite(img, dark, vig)
    return img


def glass_panel(
    img: Image.Image,
    box: tuple[int, int, int, int],
    radius: int = 28,
    fill_alpha: int = 28,
) -> None:
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    d.rounded_rectangle(box, radius=radius, fill=(*GLASS, fill_alpha))
    # top highlight
    x0, y0, x1, y1 = box
    d.rounded_rectangle(
        (x0 + 2, y0 + 2, x1 - 2, y0 + max(18, (y1 - y0) // 5)),
        radius=radius // 2,
        fill=(255, 255, 255, 18),
    )
    # icy border
    d.rounded_rectangle(box, radius=radius, outline=(*ICE, 70), width=2)
    img.alpha_composite(overlay)


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt) -> tuple[int, int]:
    b = draw.textbbox((0, 0), text, font=fnt)
    return b[2] - b[0], b[3] - b[1]


def center_text(draw, y, text, fnt, fill, spacing=0):
    w, h = text_size(draw, text, fnt)
    x = (W - w) // 2
    draw.text((x, y), text, font=fnt, fill=fill)
    return h


def draw_pill(draw, xy, label, fnt, pad_x=18, pad_y=10):
    tw, th = text_size(draw, label, fnt)
    x, y = xy
    box = (x, y, x + tw + pad_x * 2, y + th + pad_y * 2)
    # Dark glass chip + icy rim — readable on GitHub dark mode
    draw.rounded_rectangle(box, radius=999, fill=(14, 28, 48, 210), outline=(*ICE, 140), width=1)
    draw.text((x + pad_x, y + pad_y - 1), label, font=fnt, fill=ICE_SOFT)
    return box[2] - box[0], box[3] - box[1]


def save_rgb(img: Image.Image, path: Path) -> None:
    if img.mode != "RGB":
        img = img.convert("RGB")
    img.save(path, "PNG", optimize=True)
    print(f"wrote {path.name} {img.size} {path.stat().st_size // 1024}KB")


def make_hero() -> None:
    h = 380
    img = base_canvas(h, seed=11).convert("RGBA")
    glass_panel(img, (48, 48, W - 48, h - 48), radius=32, fill_alpha=22)
    draw = ImageDraw.Draw(img)

    name_f = font("segoeuib.ttf", 64)
    sub_f = font("segoeui.ttf", 26)
    craft_f = font("segoeuil.ttf", 22)
    loc_f = font("segoeui.ttf", 16)

    # accent hairline
    draw.line([(W // 2 - 40, 78), (W // 2 + 40, 78)], fill=(*ICE, 180), width=2)

    y = 110
    center_text(draw, y, "Vishal Gaur", name_f, TEXT)
    y = 190
    center_text(draw, y, "Co-founder & Director  ·  NeuOptic", sub_f, ICE_SOFT)
    y = 240
    center_text(
        draw,
        y,
        "Product interfaces end-to-end  ·  AR · ops platforms · local AI",
        craft_f,
        MUTED,
    )
    y = 290
    center_text(draw, y, "Bengaluru", loc_f, (*MUTED, 220))

    save_rgb(img, OUT / "hero.png")


def make_neuoptic() -> None:
    h = 340
    img = base_canvas(h, seed=22).convert("RGBA")
    glass_panel(img, (40, 36, W - 40, h - 36), radius=28, fill_alpha=24)
    draw = ImageDraw.Draw(img)

    title_f = font("segoeuib.ttf", 28)
    body_f = font("segoeui.ttf", 18)
    label_f = font("segoeuib.ttf", 20)
    desc_f = font("segoeui.ttf", 16)
    eyebrow_f = font("segoeuisemibold.ttf" if False else "seguisb.ttf", 14)

    draw.text((80, 58), "NEUOPTIC PRIVATE LIMITED", font=eyebrow_f, fill=ICE)
    draw.text((80, 86), "Practical tools for real businesses", font=title_f, fill=TEXT)
    draw.text(
        (80, 128),
        "Web AR catalogues and staff operations software — shipped for production use.",
        font=body_f,
        fill=MUTED,
    )

    # two product cards
    cards = [
        (
            80,
            178,
            590,
            290,
            "Arvi",
            "AR product experiences for restaurants, furniture,\nartifacts, textiles & industrial catalogues.\nIn-house 3D render engine — smooth on phones.",
        ),
        (
            620,
            178,
            1200,
            290,
            "NeoEngine",
            "Staff ops & SOP platform — reminders, workflows,\nattendance, payroll, and HR tooling\nso teams run themselves.",
        ),
    ]
    for x0, y0, x1, y1, title, desc in cards:
        glass_panel(img, (x0, y0, x1, y1), radius=18, fill_alpha=32)
        draw = ImageDraw.Draw(img)
        draw.text((x0 + 24, y0 + 18), title, font=label_f, fill=ICE_SOFT)
        draw.multiline_text((x0 + 24, y0 + 50), desc, font=desc_f, fill=MUTED, spacing=4)

    save_rgb(img, OUT / "neuoptic.png")


def make_featured() -> None:
    h = 280
    img = base_canvas(h, seed=33).convert("RGBA")
    glass_panel(img, (40, 36, W - 40, h - 36), radius=28, fill_alpha=24)
    draw = ImageDraw.Draw(img)

    eyebrow_f = font("seguisb.ttf", 14)
    title_f = font("segoeuib.ttf", 42)
    body_f = font("segoeui.ttf", 18)
    meta_f = font("segoeuil.ttf", 16)

    # icy orb accent (left)
    orb = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    od = ImageDraw.Draw(orb)
    od.ellipse((10, 10, 150, 150), fill=(60, 140, 255, 40), outline=(*ICE, 120), width=2)
    od.ellipse((40, 40, 120, 120), fill=(126, 200, 255, 55))
    od.ellipse((55, 50, 90, 85), fill=(255, 255, 255, 70))
    orb = orb.filter(ImageFilter.GaussianBlur(1))
    img.alpha_composite(orb, (70, 60))

    draw.text((260, 58), "FEATURED", font=eyebrow_f, fill=ICE)
    draw.text((260, 86), "VOXORYL", font=title_f, fill=TEXT)
    draw.text(
        (260, 150),
        "Local-first voice desktop companion — on-device reasoning,\nprivate memory, optional computer control. Say “Hey Voxy”.",
        font=body_f,
        fill=MUTED,
        spacing=6,
    )
    draw.text(
        (260, 220),
        "vox-OR-ill  ·  short name Voxy  ·  Windows & macOS",
        font=meta_f,
        fill=ICE_SOFT,
    )

    save_rgb(img, OUT / "featured.png")


def make_focus() -> None:
    h = 220
    img = base_canvas(h, seed=44).convert("RGBA")
    glass_panel(img, (40, 28, W - 40, h - 28), radius=28, fill_alpha=24)
    draw = ImageDraw.Draw(img)

    eyebrow_f = font("seguisb.ttf", 14)
    pill_f = font("segoeui.ttf", 17)

    draw.text((80, 48), "FOCUS", font=eyebrow_f, fill=ICE)

    rows = [
        ["React", "TypeScript", "UI / UX", "Full-stack", "AR / 3D on the web"],
        ["Product engineering", "Python", "Local AI", "Voice"],
    ]
    y = 92
    for row in rows:
        # measure row width for centering
        widths = []
        for label in row:
            tw, th = text_size(draw, label, pill_f)
            widths.append(tw + 18 * 2)
        total = sum(widths) + 12 * (len(row) - 1)
        x = (W - total) // 2
        row_h = 0
        for label, ww in zip(row, widths):
            _, ph = draw_pill(draw, (x, y), label, pill_f)
            row_h = max(row_h, ph)
            x += ww + 12
        y += row_h + 14

    save_rgb(img, OUT / "focus.png")


def make_footer() -> None:
    h = 160
    img = base_canvas(h, seed=55).convert("RGBA")
    glass_panel(img, (40, 24, W - 40, h - 24), radius=24, fill_alpha=30)
    draw = ImageDraw.Draw(img)

    title_f = font("segoeuib.ttf", 22)
    body_f = font("segoeui.ttf", 16)
    small_f = font("segoeuil.ttf", 14)

    # solid hairline accent so the strip never reads as "empty"
    draw.line([(100, 46), (W - 100, 46)], fill=(*ICE, 130), width=2)
    center_text(draw, 62, "Open to thoughtful product & engineering conversations", title_f, TEXT)
    center_text(draw, 100, "vishalgaur2002@gmail.com  ·  neuoptic.in  ·  LinkedIn / vishalgaur1", body_f, MUTED)
    center_text(draw, 128, "© Vishal Gaur", small_f, ICE_SOFT)

    save_rgb(img, OUT / "footer.png")


def main() -> None:
    make_hero()
    make_neuoptic()
    make_featured()
    make_focus()
    make_footer()
    # retire broken / unused assets
    for stale in ("divider.svg", "typing-voxoryl.png", "typing-voxoryl.svg", "banner.png"):
        p = OUT / stale
        if p.exists():
            p.unlink()
            print(f"removed {stale}")


if __name__ == "__main__":
    main()
