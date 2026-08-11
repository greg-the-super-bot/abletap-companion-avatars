#!/usr/bin/env python3
"""Install the verified Choice Mosaic LinkedIn exports from the repo brand kit."""

from __future__ import annotations

from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "site" / "social" / "linkedin"
BRAND_KIT = ROOT / "site" / "brand-kit"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copy2(BRAND_KIT / "profile-mark-only-400.png", OUT / "abletap-linkedin-logo-400.png")
    shutil.copy2(BRAND_KIT / "linkedin-company-cover-1128x191.png", OUT / "abletap-linkedin-cover-1128x191.png")
    (OUT / "README.md").write_text(
        "# LinkedIn Page assets\n\n"
        "Installed from the verified AbleTap Choice Mosaic brand kit.\n\n"
        "- `abletap-linkedin-logo-400.png`: 400x400 mark-only Page logo.\n"
        "- `abletap-linkedin-cover-1128x191.png`: 1128x191 Page cover.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
