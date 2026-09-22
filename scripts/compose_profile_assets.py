"""Compose one continuous GitHub profile page.

Same field as the current banner: #061018 opening into #0d3b3a and #12352c.
One PNG, so GitHub cannot insert a dark gap between panels. Addresses are
drawn in the art (underlined), not as markdown links.
"""
from __future__ import annotations

import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets"
FONT_DIR = ROOT / "fonts"
OUT.mkdir(exist_ok=True)
FONT_DIR.mkdir(exist_ok=True)

W = 1280
S = 2
MARGIN = 112
MEASURE = W - MARGIN * 2

NAVY = (6, 16, 24)       # #061018
TEAL = (13, 59, 58)      # #0d3b3a
EMERALD = (18, 53, 44)   # #12352c
INK = (246, 248, 246)

SERIF = "InstrumentSerif-Regular.ttf"
SERIF_I = "InstrumentSerif-Italic.ttf"
SANS = "SourceSans3-Regular.ttf"

FONT_URLS = {
    SERIF: "https://cdn.jsdelivr.net/fontsource/fonts/instrument-serif@5.2.5/latin-400-normal.ttf",
    SERIF_I: "https://cdn.jsdelivr.net/fontsource/fonts/instrument-serif@5.2.5/latin-400-italic.ttf",
    "Fraunces-SemiBold.ttf": "https://cdn.jsdelivr.net/fontsource/fonts/fraunces@5.2.5/latin-600-normal.ttf",
    "Fraunces-Regular.ttf": "https://cdn.jsdelivr.net/fontsource/fonts/fraunces@5.2.5/latin-400-normal.ttf",
    SANS: "https://cdn.jsdelivr.net/fontsource/fonts/source-sans-3@5.2.5/latin-400-normal.ttf",
    "SourceSans3-Semibold.ttf": "https://cdn.jsdelivr.net/fontsource/fonts/source-sans-3@5.2.5/latin-600-normal.ttf",
}

# Sizes are 1× pixels on the 1280 canvas.
NAME_PX = 92
ROLE_PX = 34
SECTION_PX = 48
PRODUCT_PX = 44
BODY_PX = 34
URL_PX = 30


def ensure_fonts() -> None:
    for name, url in FONT_URLS.items():
        path = FONT_DIR / name
        if path.exists() and path.stat().st_size > 10_000:
            continue
        print(f"downloading {name}…")
        urllib.request.urlretrieve(url, path)


def font(name: str, size_1x: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_DIR / name), size_1x * S)


def lerp(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    t = 0.0 if t < 0 else 1.0 if t > 1 else t
    return tuple(int(a[i] + (b[i] - a[i]) * t + 0.5) for i in range(3))


def field_color(tx: float, ty: float) -> tuple[int, int, int]:
    """Same wash as the current banner, given more vertical room on a long page.

    Left stays deep navy. Teal and emerald take the right, and the foot of the
    page settles further into #12352c.
    """
    end = lerp(TEAL, EMERALD, 0.28 + 0.72 * ty)
    t = tx * 0.72 + ty * 0.34
    return lerp(NAVY, end, min(1.0, t))


def make_field(w: int, h: int) -> Image.Image:
    buf = bytearray(w * h * 3)
    i = 0
    inv_w = 1.0 / (w - 1)
    inv_h = 1.0 / (h - 1)
    for y in range(h):
        ty = y * inv_h
        for x in range(w):
            r, g, b = field_color(x * inv_w, ty)
            nudge = 1 if ((x * 3 + y * 5) & 7) > 5 else 0
            buf[i] = min(255, r + nudge)
            buf[i + 1] = min(255, g + nudge)
            buf[i + 2] = min(255, b + nudge)
            i += 3
    return Image.frombytes("RGB", (w, h), bytes(buf))


def ink_box(draw: ImageDraw.ImageDraw, text: str, fnt) -> tuple[int, int, int, int]:
    return draw.textbbox((0, 0), text, font=fnt)


def ink_size(draw: ImageDraw.ImageDraw, text: str, fnt) -> tuple[int, int]:
    l, t, r, b = ink_box(draw, text, fnt)
    return r - l, b - t


def draw_ink(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, fnt) -> tuple[int, int]:
    l, t, r, b = ink_box(draw, text, fnt)
    draw.text((x - l, y - t), text, font=fnt, fill=INK)
    return r - l, b - t


def wrap(draw: ImageDraw.ImageDraw, text: str, fnt, max_w: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for word in words:
        trial = word if not cur else f"{cur} {word}"
        if ink_size(draw, trial, fnt)[0] <= max_w:
            cur = trial
        else:
            if not cur:
                raise SystemExit(f"word too wide: {word}")
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    for line in lines:
        if len(lines) > 1 and len(line) < 14:
            print(f"  short line: {line!r}")
    return lines


def save_rgb(img: Image.Image, path: Path) -> None:
    img = img.resize((W, img.size[1] // S), Image.Resampling.LANCZOS)
    img.save(path, "PNG", optimize=True)
    print(f"wrote {path.name} {img.size[0]}x{img.size[1]} {path.stat().st_size // 1024}KB")


def compose(metrics: ImageDraw.ImageDraw) -> Image.Image:
    assert 80 <= NAME_PX <= 96
    assert 28 <= BODY_PX <= 36
    assert 28 <= ROLE_PX <= 36
    assert 28 <= URL_PX <= 36

    name_f = font(SERIF, NAME_PX)
    role_f = font(SERIF_I, ROLE_PX)
    section_f = font(SERIF_I, SECTION_PX)
    product_f = font(SERIF, PRODUCT_PX)
    body_f = font(SANS, BODY_PX)
    url_f = font(SANS, URL_PX)

    max_w = MEASURE * S
    x = MARGIN * S

    paragraphs = {
        "who1": [
            "I design product interfaces and ship them.",
            "The screen someone uses, and the system under it.",
        ],
        "who2": [
            "I co-founded NeuOptic in Bengaluru.",
            "I lead the product, and I still build the frontend.",
        ],
        "arvi": "AR commerce. Web catalogues for restaurants, furniture, textiles, artifacts, and industrial goods, kept light for a phone.",
        "neo": [
            "Staff ops. Reminders, workflows, attendance, and payroll,",
            "so owners are not living in the day-to-day.",
        ],
        "voxy": "Local voice. On-device reasoning and private memory, on your computer. The short name is Voxy. Pronounced vox-OR-ill.",
        "vis1": "On-device tools that actually do things on your computer.",
        "vis2": "Practical software for real businesses. Built to be used, not only shown.",
        "now": "The repo, the site, and NeuOptic.",
    }
    wrapped: dict[str, list[str]] = {}
    for key, text in paragraphs.items():
        if isinstance(text, list):
            for line in text:
                w, _ = ink_size(metrics, line, body_f)
                if w > max_w:
                    raise SystemExit(f"overflow {w}px: {line}")
            wrapped[key] = text
        else:
            wrapped[key] = wrap(metrics, text, body_f, max_w)
    print("lines:")
    for key, lines in wrapped.items():
        for line in lines:
            print(f"  {key}: {line}")

    # (op, payload). Gaps are 1× pixels.
    ops: list[tuple] = [
        ("gap", 108),
        ("text", ("Vishal Gaur", name_f, 18)),
        ("text", ("Co-founder & Director, NeuOptic, Bengaluru", role_f, 28)),
        ("rule", 84),
        ("gap", 148),
        ("text", ("Who I am", section_f, 32)),
        ("para", "who1"),
        ("gap", 28),
        ("para", "who2"),
        ("gap", 156),
        ("text", ("What I do", section_f, 36)),
        ("text", ("Arvi", product_f, 14)),
        ("para", "arvi"),
        ("gap", 56),
        ("text", ("NeoEngine", product_f, 14)),
        ("para", "neo"),
        ("gap", 16),
        ("url", "engine.neolab.in"),
        ("gap", 56),
        ("text", ("VOXORYL", product_f, 14)),
        ("para", "voxy"),
        ("gap", 156),
        ("text", ("Vision", section_f, 32)),
        ("para", "vis1"),
        ("gap", 28),
        ("para", "vis2"),
        ("gap", 156),
        ("text", ("Now", section_f, 32)),
        ("para", "now"),
        ("gap", 52),
        ("dest", ("VOXORYL", "github.com/vishalgaur1/VOXORYL")),
        ("gap", 44),
        ("dest", ("Site", "vishalgaur1.github.io/VOXORYL")),
        ("gap", 44),
        ("dest", ("NeuOptic", "neuoptic.in")),
        ("gap", 156),
    ]

    def text_h(text: str, fnt) -> int:
        return ink_size(metrics, text, fnt)[1]

    def ensure_fit(text: str, fnt) -> None:
        w, _ = ink_size(metrics, text, fnt)
        if w > max_w:
            raise SystemExit(f"overflow {w}px: {text}")

    y = 0
    for op, payload in ops:
        if op == "gap":
            y += payload * S
        elif op == "rule":
            y += 3 * S
            y += 8 * S
        elif op == "text":
            text, fnt, after = payload
            ensure_fit(text, fnt)
            y += text_h(text, fnt) + after * S
        elif op == "para":
            lines = wrapped[payload]
            for i, line in enumerate(lines):
                y += text_h(line, body_f)
                if i < len(lines) - 1:
                    y += 16 * S
        elif op == "url":
            ensure_fit(payload, url_f)
            y += text_h(payload, url_f) + 14 * S
        elif op == "dest":
            label, url = payload
            ensure_fit(label, product_f)
            ensure_fit(url, url_f)
            y += text_h(label, product_f) + 12 * S
            y += text_h(url, url_f) + 14 * S
        else:
            raise SystemExit(op)

    height = y
    img = make_field(W * S, height)
    draw = ImageDraw.Draw(img)
    y = 0
    line_gap = 16 * S

    for op, payload in ops:
        if op == "gap":
            y += payload * S
            continue
        if op == "rule":
            draw.rectangle([x, y, x + payload * S, y + 2 * S], fill=INK)
            y += 3 * S + 8 * S
            continue
        if op == "text":
            text, fnt, after = payload
            _, h = draw_ink(draw, x, y, text, fnt)
            y += h + after * S
            continue
        if op == "para":
            lines = wrapped[payload]
            for i, line in enumerate(lines):
                _, h = draw_ink(draw, x, y, line, body_f)
                y += h
                if i < len(lines) - 1:
                    y += line_gap
            continue
        if op == "url":
            w, h = draw_ink(draw, x, y, payload, url_f)
            uy = y + h + 6 * S
            draw.rectangle([x, uy, x + w, uy + 2 * S], fill=INK)
            y += h + 14 * S
            continue
        if op == "dest":
            label, url = payload
            _, h = draw_ink(draw, x, y, label, product_f)
            y += h + 12 * S
            w, h = draw_ink(draw, x, y, url, url_f)
            uy = y + h + 6 * S
            draw.rectangle([x, uy, x + w, uy + 2 * S], fill=INK)
            y += h + 14 * S
            continue

    if y != height:
        raise SystemExit(f"paint cursor {y} != measured {height}")

    tl = img.getpixel((4, 4))
    br = img.getpixel((W * S - 8, height - 8))
    # Grain nudge is at most +1, so navy stays in family.
    assert tl[0] <= 12 and tl[1] <= 24 and tl[2] <= 32, tl
    assert br[1] > tl[1] + 20, (tl, br)
    print(f"canvas {W}x{height // S}  corners tl={tl} br={br}")
    return img


def retire_stale() -> None:
    for stale in (
        "banner.png",
        "hero.png",
        "neuoptic.png",
        "voxoryl.png",
        "featured.png",
        "focus.png",
        "footer.png",
        "divider.svg",
        "typing-voxoryl.png",
        "typing-voxoryl.svg",
    ):
        p = OUT / stale
        if p.exists():
            p.unlink()
            print(f"removed {stale}")


def main() -> None:
    ensure_fonts()
    scratch = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    img = compose(scratch)
    save_rgb(img, OUT / "profile.png")
    retire_stale()


if __name__ == "__main__":
    main()
