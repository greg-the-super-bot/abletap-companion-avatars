#!/usr/bin/env python3
"""Build LinkedIn Page-ready brand images for AbleTap.io."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "site" / "social" / "linkedin"
ICON = ROOT / "site" / "icons" / "abletap-icon-2026.png"
COMPANION = ROOT / "site" / "assets" / "companions" / "ava" / "closed.png"
SERIF = Path("/Volumes/Rocket_XTRM/Dev/abletap/iOS/Resources/Fonts/Fraunces_72pt-SemiBold.ttf")
SANS = Path("/Volumes/Rocket_XTRM/Dev/abletap/iOS/Resources/Fonts/AtkinsonHyperlegible-Regular.ttf")
SANS_BOLD = Path("/Volumes/Rocket_XTRM/Dev/abletap/iOS/Resources/Fonts/AtkinsonHyperlegible-Bold.ttf")

CREAM = "#FAF5EF"
INK = "#2B2236"
PLUM = "#241738"
PURPLE = "#6B4CE0"
LAVENDER = "#A98BF2"
CORAL = "#F5926A"
GOLD = "#F4B96B"
GREEN = "#2E9C84"


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size=size)


def gradient(size: tuple[int, int], colors: tuple[str, str]) -> Image.Image:
    w, h = size
    start = tuple(int(colors[0].lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))
    end = tuple(int(colors[1].lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))
    img = Image.new("RGB", size)
    draw = ImageDraw.Draw(img)
    for x in range(w):
        t = x / max(1, w - 1)
        rgb = tuple(round(start[i] * (1 - t) + end[i] * t) for i in range(3))
        draw.line((x, 0, x, h), fill=rgb)
    return img.convert("RGBA")


def circle_crop(path: Path, size: int) -> Image.Image:
    img = Image.open(path).convert("RGBA")
    img.thumbnail((size, size), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.alpha_composite(img, ((size - img.width) // 2, (size - img.height) // 2))
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
    canvas.putalpha(mask)
    return canvas


def paste_shadow(base: Image.Image, layer: Image.Image, xy: tuple[int, int], blur: int, alpha: int) -> None:
    shadow = Image.new("RGBA", layer.size, (0, 0, 0, alpha))
    shadow.putalpha(layer.getchannel("A").filter(ImageFilter.GaussianBlur(blur)))
    base.alpha_composite(shadow, (xy[0] + blur // 3, xy[1] + blur // 2))
    base.alpha_composite(layer, xy)


def build_logo() -> None:
    icon = Image.open(ICON).convert("RGBA")
    icon = icon.resize((400, 400), Image.Resampling.LANCZOS)
    icon.save(OUT / "abletap-linkedin-logo-400.png", optimize=True)


def build_cover() -> None:
    canvas = gradient((4200, 700), (CREAM, "#F7EDF7"))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, 4200, 700), fill=CREAM)
    draw.ellipse((-520, -420, 1160, 1020), fill="#EDE0FF")
    draw.ellipse((2860, -360, 4620, 980), fill="#FFE6D7")
    draw.rectangle((2640, 0, 4200, 700), fill=PLUM)

    icon = Image.open(ICON).convert("RGBA")
    icon.thumbnail((360, 360), Image.Resampling.LANCZOS)
    paste_shadow(canvas, icon, (190, 172), blur=24, alpha=85)

    serif = font(SERIF, 150)
    sans_bold = font(SANS_BOLD, 70)
    sans = font(SANS, 48)
    small = font(SANS_BOLD, 34)

    draw.text((620, 145), "AbleTap.io", fill=INK, font=serif)
    draw.text((626, 302), "Every person deserves independence.", fill=INK, font=sans_bold)
    draw.text((626, 405), "Talk, watch, call, and get help with one clear tap.", fill="#5B5167", font=sans)

    for i, (label, color) in enumerate([("AAC", PURPLE), ("Remote", CORAL), ("Companions", GREEN)]):
        x = 626 + i * 330
        draw.rounded_rectangle((x, 515, x + 280, 590), radius=38, fill=color, outline=INK, width=3)
        draw.text((x + 34, 534), label, fill="white" if color != GOLD else INK, font=small)

    ava = circle_crop(COMPANION, 320)
    ring = Image.new("RGBA", (380, 380), (0, 0, 0, 0))
    rd = ImageDraw.Draw(ring)
    rd.ellipse((0, 0, 379, 379), fill=LAVENDER)
    rd.ellipse((24, 24, 355, 355), fill=CREAM)
    ring.alpha_composite(ava, (30, 30))
    paste_shadow(canvas, ring, (3090, 145), blur=32, alpha=95)

    draw.rounded_rectangle((2880, 515, 3860, 602), radius=44, fill=CREAM, outline=GOLD, width=4)
    draw.text((2935, 535), "Built from lived family experience", fill=INK, font=small)

    rgb = canvas.convert("RGB")
    rgb.save(OUT / "abletap-linkedin-cover-4200x700.jpg", quality=91, optimize=True, progressive=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    build_logo()
    build_cover()
    (OUT / "README.md").write_text(
        "# LinkedIn Page assets\n\n"
        "Generated with `scripts/build_linkedin_assets.py` from the live AbleTap.io favicon/target mark and current site typography.\n\n"
        "- `abletap-linkedin-logo-400.png`: 400x400 Page logo.\n"
        "- `abletap-linkedin-cover-4200x700.jpg`: 4200x700 Page cover, under LinkedIn's 3 MB limit.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
