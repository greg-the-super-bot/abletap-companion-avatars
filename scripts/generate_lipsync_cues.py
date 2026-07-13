#!/usr/bin/env python3
"""Generate deterministic, offline mouth cues for AbleTap preview voices.

Rhubarb recognizes the recorded speech and emits its standard A-H/X mouth
shapes. This script maps those shapes onto AbleTap's logical viseme vocabulary
and writes compact JSON consumed by the static site.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIO_DIR = ROOT / "site/assets/companions/audio"
OUTPUT_DIR = AUDIO_DIR / "cues"

TRANSCRIPTS = {
    "ava": "Hi, I'm Ava. Ready to watch your favorite show? Just tap the picture, and I'll start it for you.",
    "sunny": "Hi friend! I'm Sunny! You did it, yay! Let's try the next one together!",
    "alex": "Hello, I'm Alex. Let's get you connected. Tap the green button, and you'll be all set.",
    "buzz": "Hey! Buzz here. Is the app being silly again? Don't worry, I'll sort it out, no sweat.",
    "grace": "Hello dear, I'm Grace. There's no rush at all. We'll take this one gentle step at a time.",
}

# Rhubarb standard shapes -> AbleTap's ten-shape logical vocabulary.
SHAPE_MAP = {
    "X": "rest",  # silence / idle
    "A": "mbp",   # closed lips: M, B, P
    "B": "ee",    # clenched/wide teeth
    "C": "ih",    # relaxed small vowel/consonants
    "D": "ah",    # wide open vowel
    "E": "oh",    # rounded open vowel
    "F": "uw",    # tight rounded vowel
    "G": "fv",    # lower lip against upper teeth
    "H": "lth",   # tongue/teeth articulation
}


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def generate(name: str, rhubarb: Path) -> dict:
    source = AUDIO_DIR / f"{name}.mp3"
    if not source.exists():
        raise FileNotFoundError(source)

    with tempfile.TemporaryDirectory(prefix=f"abletap-{name}-") as temp:
        temp_dir = Path(temp)
        wav = temp_dir / f"{name}.wav"
        dialog = temp_dir / f"{name}.txt"
        raw_json = temp_dir / f"{name}.json"
        dialog.write_text(TRANSCRIPTS[name] + "\n", encoding="utf-8")

        run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(source), "-ar", "16000", "-ac", "1", str(wav),
        ])
        run([
            str(rhubarb), "-f", "json", "-d", str(dialog),
            "-o", str(raw_json), str(wav),
        ])
        result = json.loads(raw_json.read_text(encoding="utf-8"))

    cues = []
    for cue in result["mouthCues"]:
        logical = SHAPE_MAP.get(cue["value"], "rest")
        item = {
            "start": round(float(cue["start"]), 3),
            "end": round(float(cue["end"]), 3),
            "viseme": logical,
        }
        if cues and cues[-1]["viseme"] == logical:
            cues[-1]["end"] = item["end"]
        else:
            cues.append(item)

    return {
        "version": 1,
        "companion": name,
        "audio": f"../{name}.mp3",
        "duration": round(float(result["metadata"]["duration"]), 3),
        "lookAheadMs": 160,
        "mouthCues": cues,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rhubarb", required=True, type=Path)
    args = parser.parse_args()
    if not args.rhubarb.exists():
        parser.error(f"Rhubarb not found: {args.rhubarb}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    summary = {}
    for name in TRANSCRIPTS:
        result = generate(name, args.rhubarb)
        output = OUTPUT_DIR / f"{name}.json"
        output.write_text(json.dumps(result, separators=(",", ":")) + "\n", encoding="utf-8")
        summary[name] = {"duration": result["duration"], "cues": len(result["mouthCues"])}
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
