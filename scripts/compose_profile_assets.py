"""Compose one continuous GitHub profile page.

Navy (#061018) → teal (#0d3b3a) → emerald (#12352c). One PNG so GitHub
cannot insert a dark gap between panels. Addresses are drawn in the art
(underlined), not as markdown links.

Display face: Libre Baskerville (normal book proportions).
Body: Source Sans 3.

Instrument Serif was the vertical-stretch culprit (V glyph h/w ≈ 1.48).
Libre Baskerville measures ≈ 0.98. Hi-res canvas is always downscaled with
a uniform factor on X and Y — never a non-square resize.
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
S = 2  # supersample; downscale must stay uniform
MARGIN = 112
MEASURE = W - MARGIN * 2

NAVY = (6, 16, 24)       # #061018
TEAL = (13, 59, 58)      # #0d3b3a
EMERALD = (18, 53, 44)   # #12352c
INK = (246, 248, 246)

SERIF = "LibreBaskerville-Regular.ttf"
SERIF_I = "LibreBaskerville-Italic.ttf"
SANS = "SourceSans3-Regular.ttf"

FONT_URLS = {
    SERIF: "https://cdn.jsdelivr.net/fontsource/fonts/libre-baskerville@5.2.5/latin-400-normal.ttf",
    SERIF_I: "https://cdn.jsdelivr.net/fontsource/fonts/libre-baskerville@5.2.5/latin-400-italic.ttf",
    SANS: "https://cdn.jsdelivr.net/fontsource/fonts/source-sans-3@5.2.5/latin-400-normal.ttf",
    "SourceSans3-Semibold.ttf": "https://cdn.jsdelivr.net/fontsource/fonts/source-sans-3@5.2.5/latin-600-normal.ttf",
}

# Readable 1× sizes — not tiny, not huge.
NAME_PX = 62
ROLE_PX = 26
SECTION_PX = 32
PRODUCT_PX = 30
BODY_PX = 27
URL_PX = 23
LINE_GAP = 12


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
    return lines


def save_rgb(img: Image.Image, path: Path) -> None:
    """Uniform downscale only — same factor on width and height."""
    src_w, src_h = img.size
    assert src_w == W * S, f"unexpected width {src_w}"
    assert src_h % S == 0, f"height {src_h} not divisible by S={S}"
    out_w, out_h = src_w // S, src_h // S
    assert out_w == W
    scale_x = out_w / src_w
    scale_y = out_h / src_h
    assert abs(scale_x - scale_y) < 1e-9, (scale_x, scale_y)
    img = img.resize((out_w, out_h), Image.Resampling.LANCZOS)
    img.save(path, "PNG", optimize=True)
    print(f"wrote {path.name} {img.size[0]}x{img.size[1]} {path.stat().st_size // 1024}KB  scale={scale_x}")


def compose(metrics: ImageDraw.ImageDraw) -> Image.Image:
    assert 56 <= NAME_PX <= 72
    assert 24 <= BODY_PX <= 32
    assert 22 <= ROLE_PX <= 30
    assert 20 <= URL_PX <= 28
    assert 10 <= LINE_GAP <= 16

    name_f = font(SERIF, NAME_PX)
    role_f = font(SERIF_I, ROLE_PX)
    section_f = font(SERIF_I, SECTION_PX)
    product_f = font(SERIF, PRODUCT_PX)
    body_f = font(SANS, BODY_PX)
    url_f = font(SANS, URL_PX)

    # Guard: reject tall condensed display faces (Instrument Serif trap).
    v_l, v_t, v_r, v_b = ink_box(metrics, "V", name_f)
    v_aspect = (v_b - v_t) / max(1, v_r - v_l)
    print(f"display V aspect h/w={v_aspect:.2f} (want ~0.9-1.15)")
    assert 0.85 <= v_aspect <= 1.20, f"display face looks stretched: V h/w={v_aspect:.2f}"

    max_w = MEASURE * S
    x = MARGIN * S

    paragraphs = {
        "who": (
            "I design product interfaces and build the systems behind them — "
            "both the screens people use and the backend that runs them."
        ),
        "intro": (
            "NeuOptic makes practical software for real businesses."
        ),
        "arvi": (
            "Arvi — web AR catalogues for restaurants, furniture, textiles, "
            "and more, powered by a custom 3D rendering stack. Light enough "
            "for phones; live with real shops and their customers."
        ),
        "neo": (
            "NeoEngine — staff operations: reminders, workflows, attendance, "
            "and payroll for business owners."
        ),
        "voxy": (
            "VOXORYL (short name: Voxy, pronounced vox-OR-ill) is an open-source "
            "voice assistant for your PC. It runs locally on your machine, keeps "
            "memory private, and can open apps and help control the computer with your voice."
        ),
        "why": (
            "The products are live. Real users. Paying customers. "
            "I build systems that ship and stay up."
        ),
        "now": "Links if you want to dig in.",
    }
    wrapped: dict[str, list[str]] = {}
    for key, text in paragraphs.items():
        wrapped[key] = wrap(metrics, text, body_f, max_w)
    print("lines:")
    for key, lines in wrapped.items():
        for line in lines:
            print(f"  {key}: {line}")

    ops: list[tuple] = [
        ("gap", 84),
        ("text", ("Vishal Gaur", name_f, 14)),
        ("text", ("Co-founder at NeuOptic · Bengaluru", role_f, 20)),
        ("rule", 64),
        ("gap", 56),
        ("para", "who"),
        ("gap", 52),
        ("text", ("NeuOptic", section_f, 16)),
        ("para", "intro"),
        ("gap", 28),
        ("para", "arvi"),
        ("gap", 22),
        ("para", "neo"),
        ("gap", 12),
        ("url", "engine.neolab.in"),
        ("gap", 52),
        ("text", ("VOXORYL", section_f, 16)),
        ("para", "voxy"),
        ("gap", 52),
        ("para", "why"),
        ("gap", 64),
        ("text", ("Links", section_f, 16)),
        ("para", "now"),
        ("gap", 32),
        ("dest", ("VOXORYL", "github.com/vishalgaur1/VOXORYL")),
        ("gap", 26),
        ("dest", ("Site", "vishalgaur1.github.io/VOXORYL")),
        ("gap", 26),
        ("dest", ("NeuOptic", "neuoptic.in")),
        ("gap", 96),
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
            y += 3 * S + 8 * S
        elif op == "text":
            text, fnt, after = payload
            ensure_fit(text, fnt)
            y += text_h(text, fnt) + after * S
        elif op == "para":
            lines = wrapped[payload]
            for i, line in enumerate(lines):
                y += text_h(line, body_f)
                if i < len(lines) - 1:
                    y += LINE_GAP * S
        elif op == "url":
            ensure_fit(payload, url_f)
            y += text_h(payload, url_f) + 12 * S
        elif op == "dest":
            label, url = payload
            ensure_fit(label, product_f)
            ensure_fit(url, url_f)
            y += text_h(label, product_f) + 10 * S
            y += text_h(url, url_f) + 12 * S
        else:
            raise SystemExit(op)

    # Pad to a multiple of S so the uniform 1/S downscale stays pixel-exact
    # on both axes (odd FreeType glyph heights can otherwise leave an odd canvas).
    height = y + (S - (y % S)) % S
    img = make_field(W * S, height)
    draw = ImageDraw.Draw(img)
    y = 0
    line_gap = LINE_GAP * S

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
            for i, line in enumerate(wrapped[payload]):
                _, h = draw_ink(draw, x, y, line, body_f)
                y += h
                if i < len(wrapped[payload]) - 1:
                    y += line_gap
            continue
        if op == "url":
            w, h = draw_ink(draw, x, y, payload, url_f)
            uy = y + h + 5 * S
            draw.rectangle([x, uy, x + w, uy + 2 * S], fill=INK)
            y += h + 12 * S
            continue
        if op == "dest":
            label, url = payload
            _, h = draw_ink(draw, x, y, label, product_f)
            y += h + 10 * S
            w, h = draw_ink(draw, x, y, url, url_f)
            uy = y + h + 5 * S
            draw.rectangle([x, uy, x + w, uy + 2 * S], fill=INK)
            y += h + 12 * S
            continue

    if y > height:
        raise SystemExit(f"paint cursor {y} > padded height {height}")
    # Trailing pad (0..S-1 px) is empty field — intentional.

    tl = img.getpixel((4, 4))
    br = img.getpixel((W * S - 8, height - 8))
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
