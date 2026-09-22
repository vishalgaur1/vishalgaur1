"""Compose a full-width editorial GitHub profile — one masthead, not a card stack.

1280-wide PNGs, GitHub dark grounds (#0d1117 / #161b22).
Name ≥ 96px, body ≥ 32px. No glass, glow, pills, or cream panels.
Destinations are set in the art; the README links the whole image.
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
X = 80
RIGHT = W - 80
MEASURE = RIGHT - X  # 1120

# GitHub dark. Type is the github fg scale — high contrast, not cream paper.
PAGE = (13, 17, 23)       # #0d1117
PLATE = (22, 27, 34)      # #161b22
INK = (240, 246, 252)     # #f0f6fc
BODY = (230, 237, 243)    # #e6edf3
META = (201, 209, 217)    # #c9d1d9
RULE = (139, 148, 158)    # #8b949e

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
    """Draw so the ink bounds start at top_left. Returns ink box (l, t, r, b)."""
    l, t, r, b = ink_bbox(draw, text, fnt)
    x, y = top_left
    draw.text((x - l, y - t), text, font=fnt, fill=fill)
    return (x, y, x + (r - l), y + (b - t))


def fit_size(draw: ImageDraw.ImageDraw, font_name: str, text: str, max_w: int, lo: int, hi: int) -> int:
    best = lo
    found = False
    while lo <= hi:
        mid = (lo + hi) // 2
        w, _ = ink_size(draw, text, font(font_name, mid))
        if w <= max_w:
            best = mid
            found = True
            lo = mid + 1
        else:
            hi = mid - 1
    if not found:
        raise SystemExit(f"{text!r} does not fit at {best}px within {max_w}px")
    return best


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


def save_rgb(img: Image.Image, path: Path) -> None:
    if img.mode != "RGB":
        img = img.convert("RGB")
    img.save(path, "PNG", optimize=True)
    print(f"wrote {path.name} {img.size[0]}x{img.size[1]} {path.stat().st_size // 1024}KB")


def make_hero(scratch: ImageDraw.ImageDraw) -> None:
    """Full-bleed nameplate. The name spans the measure; no inset card."""
    h = 720
    img = Image.new("RGB", (W, h), PLATE)
    draw = ImageDraw.Draw(img)

    name = "Vishal Gaur"
    role = "Co-founder & Director, NeuOptic"
    craft = "Product interfaces end-to-end — AR, ops platforms, local AI."

    name_px = fit_size(scratch, "InstrumentSerif-Regular.ttf", name, MEASURE, 96, 360)
    craft_px = fit_size(scratch, "SourceSans3-Regular.ttf", craft, MEASURE, 36, 48)
    role_px = 56
    meta_px = 32
    url_px = 26

    name_f = font("InstrumentSerif-Regular.ttf", name_px)
    role_f = font("InstrumentSerif-Italic.ttf", role_px)
    craft_f = font("SourceSans3-Regular.ttf", craft_px)
    meta_f = font("SourceSans3-Regular.ttf", meta_px)
    url_f = font("SourceSans3-Regular.ttf", url_px)

    _, name_h = ink_size(scratch, name, name_f)
    _, role_h = ink_size(scratch, role, role_f)
    _, craft_h = ink_size(scratch, craft, craft_f)
    _, meta_h = ink_size(scratch, "Bengaluru", meta_f)

    # One lockup, centered in the 720 frame — footer sits with the type, not in a hole.
    gap_name_rule = 36
    rule_w = 2
    gap_rule_role = 40
    gap_role_craft = 32
    gap_craft_footer = 56
    stack_h = (
        name_h
        + gap_name_rule
        + rule_w
        + gap_rule_role
        + role_h
        + gap_role_craft
        + craft_h
        + gap_craft_footer
        + meta_h
    )
    name_top = max(72, (h - stack_h) // 2)

    name_box = draw_ink(draw, (X, name_top), name, name_f, INK)
    rule_y = name_box[3] + gap_name_rule
    draw.rectangle((X, rule_y, RIGHT, rule_y + rule_w), fill=BODY)

    role_box = draw_ink(draw, (X, rule_y + rule_w + gap_rule_role), role, role_f, BODY)
    craft_box = draw_ink(draw, (X, role_box[3] + gap_role_craft), craft, craft_f, BODY)

    footer_top = craft_box[3] + gap_craft_footer
    meta_box = draw_ink(draw, (X, footer_top), "Bengaluru", meta_f, META)
    url = "neuoptic.in"
    url_w, url_h = ink_size(scratch, url, url_f)
    draw_ink(draw, (RIGHT - url_w, footer_top + max(0, (meta_h - url_h) // 2)), url, url_f, META)

    assert name_px >= 96, name_px
    assert role_px >= 32 and craft_px >= 32
    assert name_box[2] <= RIGHT + 1
    assert craft_box[2] <= RIGHT + 1
    assert name_box[1] >= 64
    assert craft_box[3] + 48 <= meta_box[1], f"craft/footer collision {craft_box[3]} {meta_box[1]}"
    assert role_box[1] - (rule_y + rule_w) >= 32
    print(
        f"hero name {name_px}px role {role_px}px craft {craft_px}px "
        f"ink-top {name_box[1]} craft-bottom {craft_box[3]}"
    )
    save_rgb(img, OUT / "hero.png")


def make_contents(scratch: ImageDraw.ImageDraw) -> None:
    """Horizontal index: NeuOptic, then Arvi and NeoEngine side by side.

    Page-colored ground — a typeset band, not a second nameplate.
    """
    kicker_px = 64
    title_px = 104
    desc_px = 36
    url_px = 26
    gutter = 48
    col_w = (MEASURE - gutter) // 2
    col2_x = X + col_w + gutter

    kicker_f = font("Fraunces-SemiBold.ttf", kicker_px)
    title_f = font("InstrumentSerif-Regular.ttf", title_px)
    desc_f = font("SourceSans3-Regular.ttf", desc_px)
    url_f = font("SourceSans3-Regular.ttf", url_px)

    # Hand-broken so each column is two full lines, not a stranded last word.
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
    wrapped = [lines for _, lines in entries]
    for lines in wrapped:
        for line in lines:
            lw, _ = ink_size(scratch, line, desc_f)
            assert lw <= col_w, f"{line!r} is {lw}px in a {col_w}px column"

    title_h = max(ink_size(scratch, title, title_f)[1] for title, _ in entries)
    line_h = ink_size(scratch, "Ag", desc_f)[1]
    desc_h = max(len(lines) * line_h + (len(lines) - 1) * 12 for lines in wrapped)
    kicker_h = ink_size(scratch, "NeuOptic", kicker_f)[1]

    top = 64
    gap_after_kicker = 22
    gap_after_rule = 36
    gap_title_desc = 22
    bottom = 64
    h = (
        top
        + kicker_h
        + gap_after_kicker
        + 1
        + gap_after_rule
        + title_h
        + gap_title_desc
        + desc_h
        + bottom
    )

    img = Image.new("RGB", (W, h), PAGE)
    draw = ImageDraw.Draw(img)

    kicker = draw_ink(draw, (X, top), "NeuOptic", kicker_f, INK)
    url = "neuoptic.in"
    url_w, url_h = ink_size(scratch, url, url_f)
    url_y = kicker[1] + max(0, (kicker_h - url_h) // 2)
    draw_ink(draw, (RIGHT - url_w, url_y), url, url_f, META)

    rule_y = kicker[3] + gap_after_kicker
    draw.line([(X, rule_y), (RIGHT, rule_y)], fill=RULE, width=1)

    title_top = rule_y + gap_after_rule
    desc_top = title_top + title_h + gap_title_desc
    split_x = X + col_w + gutter // 2
    draw.line([(split_x, title_top), (split_x, title_top + title_h + gap_title_desc + desc_h)], fill=RULE, width=1)

    bottoms = []
    for (title, _), lines, col_x in zip(entries, wrapped, (X, col2_x)):
        title_box = draw_ink(draw, (col_x, title_top), title, title_f, INK)
        assert title_box[2] <= col_x + col_w, f"{title} overflows column"
        box = draw_lines(draw, (col_x, desc_top), lines, desc_f, BODY, 12)
        assert box[2] <= col_x + col_w + 2, f"desc overflows: {lines}"
        bottoms.append(box[3])

    assert kicker_px >= 32 and title_px >= 32 and desc_px >= 32
    assert max(bottoms) <= h - 48
    print(f"contents {W}x{h} titles {title_px}px body {desc_px}px cols {col_w}px")
    print("  " + " | ".join(" / ".join(lines) for lines in wrapped))
    save_rgb(img, OUT / "contents.png")


def make_voxoryl(scratch: ImageDraw.ImageDraw) -> None:
    """Large word, one sentence. No rule, no second plate."""
    word = "VOXORYL"
    # One sentence, broken to the measure so the line can stay large.
    sentence_lines = [
        "Local-first voice desktop companion —",
        "on-device reasoning, private memory.",
    ]
    url = "github.com/vishalgaur1/VOXORYL"

    word_px = fit_size(scratch, "Fraunces-SemiBold.ttf", word, MEASURE, 96, 320)
    sent_px = 64
    url_px = 26

    word_f = font("Fraunces-SemiBold.ttf", word_px)
    sent_f = font("SourceSans3-Regular.ttf", sent_px)
    url_f = font("SourceSans3-Regular.ttf", url_px)

    for line in sentence_lines:
        sw, _ = ink_size(scratch, line, sent_f)
        assert sw <= MEASURE, f"sentence line {sw}px > {MEASURE}"

    word_h = ink_size(scratch, word, word_f)[1]
    sent_line_h = ink_size(scratch, sentence_lines[0], sent_f)[1]
    sent_gap = 14
    sent_h = sent_line_h * 2 + sent_gap
    url_h = ink_size(scratch, url, url_f)[1]

    top = 80
    gap_word = 40
    gap_url = 28
    bottom = 72
    h = top + word_h + gap_word + sent_h + gap_url + url_h + bottom

    img = Image.new("RGB", (W, h), PAGE)
    draw = ImageDraw.Draw(img)

    word_box = draw_ink(draw, (X, top), word, word_f, INK)
    sent_box = draw_lines(draw, (X, word_box[3] + gap_word), sentence_lines, sent_f, BODY, sent_gap)
    draw_ink(draw, (X, sent_box[3] + gap_url), url, url_f, META)

    assert word_px >= 96 and sent_px >= 32
    assert word_box[2] <= RIGHT + 1
    assert sent_box[2] <= RIGHT + 1
    assert sent_box[1] - word_box[3] >= 28
    print(f"voxoryl word {word_px}px sentence {sent_px}px canvas {W}x{h}")
    save_rgb(img, OUT / "voxoryl.png")


def retire_stale() -> None:
    for stale in (
        "neuoptic.png",
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
    scratch_img = Image.new("RGB", (8, 8))
    scratch = ImageDraw.Draw(scratch_img)
    make_hero(scratch)
    make_contents(scratch)
    make_voxoryl(scratch)
    retire_stale()


if __name__ == "__main__":
    main()
