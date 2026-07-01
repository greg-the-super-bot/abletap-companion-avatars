# AbleTap Companion Avatars — Review Package

This package contains a first visual pass for the five locked AbleTap companions:

- Ava — calm default, purple
- Sunny — bright and upbeat, gold
- Alex — steady male professional in his 40s, coral/peach
- Buzz — friendly and upbeat, teal
- Grace — gentle, lavender

## Deliverables

- `assets/masters/` — 1254 × 1254 generated PNG masters
- `assets/app-512/` — 512 × 512 app/web review exports
- `assets/thumbs-256/` — 256 × 256 small-target review exports
- `prototype/index.html` — local browser demo using free client-side speech plus a simple mouth-warp effect
- `prototype/ava-mouth-test.html` — validated five-frame Ava mouth-swap proof
- `prototype/mouth-rigs.html` — validated mouth-rig review for all five companions
- `assets/companion-mouth-test/rig/` — active frames and animated loops for all five companions
- `assets/companion-mouth-test/overlays/` — transparent mouth-only overlays for all five companions
- `assets/companion-mouth-test/validation.json` — measured stability for all 25 edited states
- `assets/ava-mouth-test/rig/ava-mouth-cycle.gif` — closed → open → wide → O → smile loop
- `assets/ava-mouth-test/overlays/` — full-canvas transparent mouth-only overlays
- `assets/ava-mouth-test/validation.json` — measured raw-edit and masked-composite stability
- `docs/PRODUCTION-HANDOFF.md` — requirements for converting the approved art into a real mouth rig
- `docs/GENERATION-PROMPTS.md` — prompt record for reproducibility
- `manifest.json` — asset names, roles, colors, and production status

## Current status

The five portraits are suitable for visual review and small-size accessibility checks. Ava now has a working five-state proof rig. The other four portraits do not yet have separate mouth layers.

The Ava proof uses pixel-aligned overlays composited onto the untouched approved base. Raw generative edits changed subtle pixels across the image, so they are not used directly. The masked final frames measure zero changed pixels outside the mouth mask.

## Run the prototype

From this folder:

```sh
python3 -m http.server 8080
```

Then open `http://localhost:8080/prototype/`.
