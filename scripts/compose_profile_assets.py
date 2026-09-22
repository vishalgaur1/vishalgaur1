"""Compose one navy-to-emerald GitHub profile banner.

1280-wide. Deep navy #061018 into teal #0d3b3a and emerald #12352c.
The name stays in the 72–96px range. NeuOptic and VOXORYL sit on the
same gradient as compact bands, cropped apart only so each half can be
a whole-image link. No glass, glow, cards, or cream panels.
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
PAD_X = 72
X = PAD_X
RIGHT = W - PAD_X
MEASURE = RIGHT - X

# Endpoints from the brief. Midtones are blends of these, not a brighter accent.
NAVY = (6, 16, 24)       # #061018
TEAL = (13, 59, 58)      # #0d3b3a
EMERALD = (18, 53, 44)   # #12352c

INK = (244, 248, 246)
ROLE_C = (236, 244, 240)
CRAFT_C = (228, 238, 234)
BODY = (222, 234, 228)
META = (206, 222, 216)
RULE = (78, 124, 116)

# Readable on a 1280 canvas. Do not fit-to-width — that blew the name up to ~280px.
NAME_PX = 88
ROLE_PX = 36
CRAFT_PX = 32
PLACE_PX = 26
KICKER_PX = 36
TITLE_PX = 44
DESC_PX = 30
WORD_PX = 64
SENT_PX_MIN = 30
SENT_PX_MAX = 40
URL_PX = 24

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


def ink_bbox(draw: ImageDraw.ImageDraw, text: str, fnt) -> tuple[int, int, int, int]:
    return draw.textbbox((0, 0), text, font=fnt)


def ink_size(draw: ImageDraw.ImageDraw, text: str, fnt) -> tuple[int, int]:
    l, t, r, b = ink_bbox(draw, text, fnt)
    return r - l, b - t


def draw_ink(
    draw: ImageDraw.ImageDraw,
    top_left: tuple[int, int],
    text: str,
    fnt,
    fill: tuple[int, int, int],
) -> tuple[int, int, int, int]:
    """Draw so the ink bounds start at top_left. Returns the ink box."""
    l, t, r, b = ink_bbox(draw, text, fnt)
    x, y = top_left
    draw.text((x - l, y - t), text, font=fnt, fill=fill)
    return (x, y, x + (r - l), y + (b - t))


def draw_lines(
    draw: ImageDraw.ImageDraw,
    origin: tuple[int, int],
    lines: list[str],
    fnt,
    fill: tuple[int, int, int],
    gap: int,
) -> tuple[int, int, int, int]:
    x, y = origin
    bottom = y
    right = x
    top = y
    for i, line in enumerate(lines):
        box = draw_ink(draw, (x, y), line, fnt, fill)
        right = max(right, box[2])
        bottom = box[3]
        if i == 0:
            top = box[1]
        y = box[3] + gap
    return (x, top, right, bottom)


def fit_size(draw: ImageDraw.ImageDraw, font_name: str, text: str, max_w: int, lo: int, hi: int) -> int:
    best = lo
    while lo <= hi:
        mid = (lo + hi) // 2
        w, _ = ink_size(draw, text, font(font_name, mid))
        if w <= max_w:
            best = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return best


def lerp(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    t = 0.0 if t < 0 else 1.0 if t > 1 else t
    return tuple(int(a[i] + (b[i] - a[i]) * t + 0.5) for i in range(3))


def field_color(tx: float, ty: float) -> tuple[int, int, int]:
    """Left edge stays deep navy; teal and emerald take the right.

    Vertical shift is gentle so the two bands still read as one field.
    """
    end = lerp(TEAL, EMERALD, 0.30 + 0.70 * ty)
    t = tx * 0.82 + ty * 0.18
    return lerp(NAVY, end, t)


def make_field(w: int, h: int) -> Image.Image:
    buf = bytearray(w * h * 3)
    i = 0
    inv_w = 1.0 / (w - 1)
    inv_h = 1.0 / (h - 1)
    for y in range(h):
        ty = y * inv_h
        for x in range(w):
            r, g, b = field_color(x * inv_w, ty)
            # Tiny ordered dither so the dark blend does not band.
            nudge = 1 if ((x * 3 + y * 5) & 7) > 4 else 0
            buf[i] = min(255, r + nudge)
            buf[i + 1] = min(255, g + nudge)
            buf[i + 2] = min(255, b + nudge)
            i += 3
    return Image.frombytes("RGB", (w, h), bytes(buf))


def save_rgb(img: Image.Image, path: Path) -> None:
    if img.mode != "RGB":
        img = img.convert("RGB")
    img.save(path, "PNG", optimize=True)
    print(f"wrote {path.name} {img.size[0]}x{img.size[1]} {path.stat().st_size // 1024}KB")


def compose(scratch: ImageDraw.ImageDraw) -> None:
    name = "Vishal Gaur"
    role = "Co-founder & Director, NeuOptic"
    craft = "Product interfaces end-to-end — AR, ops platforms, local AI."
    place = "Bengaluru"
    kicker = "NeuOptic"
    site = "neuoptic.in"
    entries = [
        (
            "Arvi",
            [
                "Web AR catalogues for showrooms",
                "— light, phone-smooth.",
            ],
        ),
        (
            "NeoEngine",
            [
                "Staff ops & ERP — reminders,",
                "workflows, attendance, payroll.",
            ],
        ),
    ]
    word = "VOXORYL"
    sentence = [
        "Local-first voice desktop companion —",
        "on-device reasoning, private memory.",
    ]
    repo = "github.com/vishalgaur1/VOXORYL"

    name_f = font("InstrumentSerif-Regular.ttf", NAME_PX)
    role_f = font("InstrumentSerif-Italic.ttf", ROLE_PX)
    craft_f = font("SourceSans3-Regular.ttf", CRAFT_PX)
    place_f = font("SourceSans3-Regular.ttf", PLACE_PX)
    kicker_f = font("Fraunces-SemiBold.ttf", KICKER_PX)
    title_f = font("InstrumentSerif-Regular.ttf", TITLE_PX)
    desc_f = font("SourceSans3-Regular.ttf", DESC_PX)
    word_f = font("Fraunces-SemiBold.ttf", WORD_PX)
    url_f = font("SourceSans3-Regular.ttf", URL_PX)

    name_w, name_h = ink_size(scratch, name, name_f)
    role_w, role_h = ink_size(scratch, role, role_f)
    craft_w, craft_h = ink_size(scratch, craft, craft_f)
    place_w, place_h = ink_size(scratch, place, place_f)
    kicker_w, kicker_h = ink_size(scratch, kicker, kicker_f)
    site_w, site_h = ink_size(scratch, site, url_f)
    title_h = max(ink_size(scratch, title, title_f)[1] for title, _ in entries)
    desc_line_h = ink_size(scratch, "Ag", desc_f)[1]
    desc_gap = 10
    desc_h = desc_line_h * 2 + desc_gap
    word_w, word_h = ink_size(scratch, word, word_f)
    word_gap = 48
    sent_x = X + word_w + word_gap
    sent_measure = RIGHT - sent_x
    longer = max(sentence, key=len)
    sent_px = fit_size(scratch, "SourceSans3-Regular.ttf", longer, sent_measure, SENT_PX_MIN, SENT_PX_MAX)
    sent_f = font("SourceSans3-Regular.ttf", sent_px)
    sent_line_h = ink_size(scratch, sentence[0], sent_f)[1]
    sent_gap = 8
    sent_h = sent_line_h * 2 + sent_gap
    repo_w, repo_h = ink_size(scratch, repo, url_f)

    gutter = 56
    col_w = (MEASURE - gutter) // 2
    col2_x = X + col_w + gutter
    for title, lines in entries:
        tw, _ = ink_size(scratch, title, title_f)
        assert tw <= col_w, f"{title} is {tw}px in a {col_w}px column"
        for line in lines:
            lw, _ = ink_size(scratch, line, desc_f)
            assert lw <= col_w, f"{line!r} is {lw}px in a {col_w}px column"

    for line in sentence:
        sw, _ = ink_size(scratch, line, sent_f)
        assert sw <= sent_measure, f"{line!r} is {sw}px beside the word ({sent_measure}px)"
    assert repo_w <= sent_measure, f"repo url {repo_w}px > {sent_measure}px"

    assert 72 <= NAME_PX <= 96, NAME_PX
    assert name_w <= MEASURE and role_w <= MEASURE and craft_w <= MEASURE
    assert name_w + 32 + place_w <= MEASURE, "name collides with Bengaluru"
    assert kicker_w + 32 + site_w <= MEASURE, "NeuOptic collides with its url"

    # Upper band — identity and NeuOptic. Padding is real, the field is still full.
    top = 56
    gap_name_role = 16
    gap_role_craft = 12
    gap_craft_rule = 32
    gap_rule_kicker = 28
    gap_kicker_title = 24
    gap_title_desc = 12
    gap_desc_rule = 28
    gap_rule_split = 26

    y = top
    name_top = y
    y = name_top + name_h + gap_name_role
    role_top = y
    y = role_top + role_h + gap_role_craft
    craft_top = y
    y = craft_top + craft_h + gap_craft_rule
    rule1 = y
    y = rule1 + 1 + gap_rule_kicker
    kicker_top = y
    y = kicker_top + kicker_h + gap_kicker_title
    title_top = y
    desc_top = title_top + title_h + gap_title_desc
    y = desc_top + desc_h + gap_desc_rule
    rule2 = y
    split = rule2 + 1 + gap_rule_split

    # Lower band — VOXORYL beside its sentence, not a lone poster word.
    gap_split_word = 28
    sent_url_gap = 14
    bottom = 48
    block_h = sent_h + sent_url_gap + repo_h
    band_h = max(word_h, block_h)
    word_top = split + gap_split_word + max(0, (band_h - word_h) // 2)
    sent_top = split + gap_split_word + max(0, (band_h - block_h) // 2)
    h = split + gap_split_word + band_h + bottom

    img = make_field(W, h)
    draw = ImageDraw.Draw(img)

    name_box = draw_ink(draw, (X, name_top), name, name_f, INK)
    place_box = draw_ink(
        draw,
        (RIGHT - place_w, name_box[3] - place_h),
        place,
        place_f,
        META,
    )
    role_box = draw_ink(draw, (X, role_top), role, role_f, ROLE_C)
    craft_box = draw_ink(draw, (X, craft_top), craft, craft_f, CRAFT_C)
    draw.line([(X, rule1), (RIGHT, rule1)], fill=RULE, width=1)

    kicker_box = draw_ink(draw, (X, kicker_top), kicker, kicker_f, INK)
    site_box = draw_ink(
        draw,
        (RIGHT - site_w, kicker_box[3] - site_h),
        site,
        url_f,
        META,
    )

    split_x = X + col_w + gutter // 2
    draw.line([(split_x, title_top), (split_x, desc_top + desc_h)], fill=RULE, width=1)

    desc_bottoms = []
    for (title, lines), col_x in zip(entries, (X, col2_x)):
        title_box = draw_ink(draw, (col_x, title_top), title, title_f, INK)
        assert title_box[2] <= col_x + col_w
        box = draw_lines(draw, (col_x, desc_top), lines, desc_f, BODY, desc_gap)
        assert box[2] <= col_x + col_w + 1, lines
        desc_bottoms.append(box[3])

    draw.line([(X, rule2), (RIGHT, rule2)], fill=RULE, width=1)

    word_box = draw_ink(draw, (X, word_top), word, word_f, INK)
    sent_box = draw_lines(draw, (sent_x, sent_top), sentence, sent_f, BODY, sent_gap)
    repo_box = draw_ink(draw, (sent_x, sent_box[3] + sent_url_gap), repo, url_f, META)

    # Collisions and empty-void guards.
    assert name_box[2] < place_box[0] - 24
    assert role_box[1] >= name_box[3] + 12
    assert craft_box[1] >= role_box[3] + 8
    assert kicker_box[1] >= rule1 + 20
    assert kicker_box[2] < site_box[0] - 24
    assert min(desc_bottoms) >= title_top + title_h + 8
    assert word_box[2] < sent_box[0] - 24
    assert repo_box[3] <= h - 36
    assert name_box[1] >= 40
    assert split < h * 0.82, "lower band is a sliver"
    # Content should occupy the frame: padding is allowed, a poster void is not.
    assert h <= 860, f"canvas {h}px is too tall for this much copy"
    assert h >= 640, f"canvas {h}px is too short to breathe"
    content_top = name_box[1]
    content_bottom = repo_box[3]
    assert (content_bottom - content_top) >= int(h * 0.72)

    tl = img.getpixel((2, 2))
    br = img.getpixel((W - 3, h - 3))
    assert tl[2] >= tl[0] and tl[1] < 28, f"top-left is not navy {tl}"
    assert br[1] > tl[1] + 18, f"gradient did not move toward green {tl} -> {br}"

    upper = img.crop((0, 0, W, split))
    lower = img.crop((0, split, W, h))
    save_rgb(upper, OUT / "banner.png")
    save_rgb(lower, OUT / "voxoryl.png")
    print(
        f"name {NAME_PX}px ({name_w}px wide) role {ROLE_PX}px craft {CRAFT_PX}px "
        f"word {WORD_PX}px sentence {sent_px}px canvas {W}x{h} split {split}"
    )
    print(f"corners tl={tl} br={br}")
    for py in (0.05, 0.35, 0.65, 0.95):
        row = []
        for px in (0.02, 0.5, 0.98):
            row.append(img.getpixel((int(px * (W - 1)), int(py * (h - 1)))))
        print(f"  y={py:.2f} {row}")


def retire_stale() -> None:
    for stale in (
        "hero.png",
        "contents.png",
        "neuoptic.png",
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
    compose(scratch)
    retire_stale()


if __name__ == "__main__":
    main()
