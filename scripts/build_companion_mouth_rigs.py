#!/usr/bin/env python3
"""Build deterministic mouth-overlay rigs for all AbleTap companions."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT_ROOT = ROOT / "assets/companion-mouth-test"
STATES = ("micro", "small", "open", "o", "smile")
DISPLAY_STATES = ("closed", "micro", "small", "open", "o", "smile")
DEFAULT_CYCLE = ("closed", "micro", "small", "open", "small", "micro", "o", "micro", "small", "smile")
DURATIONS = (550, 90, 100, 110, 90, 90, 120, 90, 100, 500)

CHARACTERS = {
    "ava": {
        "base": ROOT / "assets/masters/ava.png",
        "raw": ROOT / "assets/ava-mouth-test/raw",
        "rawPattern": "ava-{state}.png",
        "bbox": (500, 650, 760, 850),
    },
    "sunny": {
        "base": ROOT / "assets/masters/sunny.png",
        "raw": OUT_ROOT / "raw/sunny",
        "rawPattern": "{state}.png",
        "bbox": (500, 650, 760, 845),
    },
    "alex": {
        "base": ROOT / "assets/masters/alex.png",
        "raw": OUT_ROOT / "raw/alex",
        "rawPattern": "{state}.png",
        "bbox": (500, 620, 760, 825),
    },
    "buzz": {
        "base": ROOT / "assets/masters/buzz.png",
        "raw": OUT_ROOT / "raw/buzz",
        "rawPattern": "{state}.png",
        "bbox": (500, 650, 760, 850),
    },
    "grace": {
        "base": ROOT / "assets/masters/grace.png",
        "raw": OUT_ROOT / "raw/grace",
        "rawPattern": "{state}.png",
        "bbox": (500, 655, 760, 850),
    },
}

FEATHER_RADIUS = 12


def mask_for(size: tuple[int, int], bbox: tuple[int, int, int, int]) -> Image.Image:
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).ellipse(bbox, fill=255)
    return mask.filter(ImageFilter.GaussianBlur(FEATHER_RADIUS))


def metrics(base: Image.Image, candidate: Image.Image, outside: np.ndarray) -> dict:
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
    validation = {"version": 1, "characters": {}}
    review_rows: list[tuple[str, Image.Image]] = []

    for character, config in CHARACTERS.items():
        base = Image.open(config["base"]).convert("RGB")
        mask = mask_for(base.size, config["bbox"])
        outside = np.asarray(mask) == 0
        rig_dir = OUT_ROOT / "rig" / character
        overlay_dir = OUT_ROOT / "overlays" / character
        rig_dir.mkdir(parents=True, exist_ok=True)
        overlay_dir.mkdir(parents=True, exist_ok=True)

        frames = {"closed": base}
        base.save(rig_dir / "closed.png")
        character_report = {
            "base": str(config["base"].relative_to(ROOT)),
            "canvas": list(base.size),
            "mouthBBox": list(config["bbox"]),
            "featherRadius": FEATHER_RADIUS,
            "states": {},
        }

        for state in STATES:
            raw_path = config["raw"] / config["rawPattern"].format(state=state)
            raw = Image.open(raw_path).convert("RGB")
            if raw.size != base.size:
                raise ValueError(f"{character}/{state}: expected {base.size}, got {raw.size}")
            composite = Image.composite(raw, base, mask)
            composite.save(rig_dir / f"{state}.png")
            frames[state] = composite

            overlay = raw.convert("RGBA")
            overlay.putalpha(mask)
            overlay.save(overlay_dir / f"{state}.png")

            character_report["states"][state] = {
                "rawEdit": metrics(base, raw, outside),
                "maskedComposite": metrics(base, composite, outside),
                "frame": str((rig_dir / f"{state}.png").relative_to(ROOT)),
                "overlay": str((overlay_dir / f"{state}.png").relative_to(ROOT)),
            }

        cycle_frames = [frames[state] for state in DEFAULT_CYCLE]
        cycle_frames[0].save(
            rig_dir / f"{character}-mouth-cycle.gif",
            save_all=True,
            append_images=cycle_frames[1:],
            duration=DURATIONS,
            loop=0,
            disposal=2,
            optimize=False,
        )

        thumbs = [frames[state].resize((220, 220), Image.Resampling.LANCZOS) for state in DISPLAY_STATES]
        row = Image.new("RGB", (220 * len(thumbs), 250), "#f8f4ec")
        for index, thumb in enumerate(thumbs):
            row.paste(thumb, (index * 220, 0))
        ImageDraw.Draw(row).text((12, 228), character.title(), fill="#211f1b", font=ImageFont.load_default())
        row.save(rig_dir / f"{character}-mouth-strip.png")
        review_rows.append((character, row))
        validation["characters"][character] = character_report

    sheet = Image.new("RGB", (1320, 250 * len(review_rows)), "#f8f4ec")
    for index, (_, row) in enumerate(review_rows):
        sheet.paste(row, (0, index * 250))
    sheet.save(OUT_ROOT / "all-companion-mouth-shapes.png")
    (OUT_ROOT / "validation.json").write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        character: {
            state: report["maskedComposite"]["outsideChangedPixels"]
            for state, report in data["states"].items()
        }
        for character, data in validation["characters"].items()
    }, indent=2))


if __name__ == "__main__":
    main()
