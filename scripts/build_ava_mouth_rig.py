#!/usr/bin/env python3
"""Build deterministic Ava mouth overlays and measure face stability."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
BASE_PATH = ROOT / "assets/masters/ava.png"
RAW_DIR = ROOT / "assets/ava-mouth-test/raw"
RIG_DIR = ROOT / "assets/ava-mouth-test/rig"
OVERLAY_DIR = ROOT / "assets/ava-mouth-test/overlays"
REPORT_PATH = ROOT / "assets/ava-mouth-test/validation.json"
STATES = ("micro", "small", "open", "wide", "o", "smile")
DISPLAY_STATES = ("closed", "micro", "small", "open", "o", "smile")
DEFAULT_CYCLE = ("closed", "micro", "small", "open", "small", "micro", "o", "micro", "small", "smile")

# Tight full-resolution mouth edit area on the 1254px approved master.
MOUTH_BBOX = (500, 650, 760, 850)
FEATHER_RADIUS = 12


def build_mask(size: tuple[int, int]) -> Image.Image:
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse(MOUTH_BBOX, fill=255)
    return mask.filter(ImageFilter.GaussianBlur(FEATHER_RADIUS))


def changed_metrics(base: Image.Image, candidate: Image.Image, outside: np.ndarray) -> dict:
    base_np = np.asarray(base, dtype=np.int16)
    candidate_np = np.asarray(candidate, dtype=np.int16)
    delta = np.abs(candidate_np - base_np)
    changed = np.any(delta > 0, axis=2)
    outside_delta = delta[outside]
    return {
        "outsideChangedPixels": int(np.count_nonzero(changed & outside)),
        "outsidePixelCount": int(np.count_nonzero(outside)),
        "outsideChangedPercent": round(100 * np.count_nonzero(changed & outside) / np.count_nonzero(outside), 4),
        "outsideMeanAbsoluteChannelDelta": round(float(outside_delta.mean()), 4),
        "fullDifferenceBBox": ImageChops.difference(base, candidate).getbbox(),
    }


def main() -> None:
    RIG_DIR.mkdir(parents=True, exist_ok=True)
    OVERLAY_DIR.mkdir(parents=True, exist_ok=True)

    base = Image.open(BASE_PATH).convert("RGB")
    mask = build_mask(base.size)
    mask_np = np.asarray(mask)
    outside = mask_np == 0

    base.save(RIG_DIR / "ava-closed.png")
    frames_by_state = {"closed": base}
    validation = {
        "base": str(BASE_PATH.relative_to(ROOT)),
        "canvas": list(base.size),
        "mouthBBox": list(MOUTH_BBOX),
        "featherRadius": FEATHER_RADIUS,
        "states": {},
    }

    for state in STATES:
        raw = Image.open(RAW_DIR / f"ava-{state}.png").convert("RGB")
        if raw.size != base.size:
            raise ValueError(f"{state}: expected {base.size}, got {raw.size}")

        composite = Image.composite(raw, base, mask)
        composite.save(RIG_DIR / f"ava-{state}.png")

        overlay = raw.convert("RGBA")
        overlay.putalpha(mask)
        overlay.save(OVERLAY_DIR / f"ava-{state}-overlay.png")
        frames_by_state[state] = composite

        validation["states"][state] = {
            "rawEdit": changed_metrics(base, raw, outside),
            "maskedComposite": changed_metrics(base, composite, outside),
            "overlay": str((OVERLAY_DIR / f"ava-{state}-overlay.png").relative_to(ROOT)),
            "frame": str((RIG_DIR / f"ava-{state}.png").relative_to(ROOT)),
        }

    cycle_frames = [frames_by_state[state] for state in DEFAULT_CYCLE]
    durations = [550, 90, 100, 110, 90, 90, 120, 90, 100, 500]
    cycle_frames[0].save(
        RIG_DIR / "ava-mouth-cycle.gif",
        save_all=True,
        append_images=cycle_frames[1:],
        duration=durations,
        loop=0,
        disposal=2,
        optimize=False,
    )

    thumbs = [frames_by_state[state].resize((256, 256), Image.Resampling.LANCZOS) for state in DISPLAY_STATES]
    strip = Image.new("RGB", (256 * len(thumbs), 256), "white")
    for index, thumb in enumerate(thumbs):
        strip.paste(thumb, (index * 256, 0))
    strip.save(RIG_DIR / "ava-mouth-strip.png")

    REPORT_PATH.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
