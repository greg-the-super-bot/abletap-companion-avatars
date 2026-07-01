# Production Handoff

## Verified output

- Five matched square RGB PNG portraits at 1254 × 1254.
- Front-facing pose, direct gaze, closed-mouth base expression, and soft lower-face lighting.
- Shared rendering, framing, eye scale, shoulder crop, and circular-backdrop system.
- 512 px and 256 px review exports.
- No paid avatar/video service is required to display or animate these assets.
- Ava has six conversational full-canvas states (`closed`, `micro`, `small`, `open`, `o`, `smile`) plus transparent feathered mouth overlays. A `wide` stress-test frame is retained but excluded from the normal loop.
- Sunny, Alex, Buzz, and Grace now have the same six-state conversational rigs and transparent overlays.
- Canonical mapping: coral/peach male professional = Alex; teal androgynous companion = Buzz.
- Ava's masked final frames have zero changed pixels outside the mouth mask; see `assets/ava-mouth-test/validation.json`.

## Not yet complete

Sunny, Alex, Buzz, and Grace remain flattened RGB images without mouth layers. Ava is a validated proof rig, but still needs an in-app visual/voice timing test before production acceptance.

The raw Ava image edits re-rendered subtle pixels across the full image (more than 99% of pixels outside the mouth mask had at least a one-channel change). Those raw edits are preserved only as evidence. Production frames use only their feathered mouth regions over the untouched approved base.

## Required production conversion

For each approved character, create these five pixel-aligned mouth overlays:

1. `closed`
2. `micro-open`
3. `small-open`
4. `open`
5. `o`
6. `smile`

Every overlay must:

- use the exact master canvas dimensions;
- keep the head, eyes, nose, jaw, camera, and lighting unchanged;
- contain only the minimum lower-face pixels required for the mouth change;
- have transparent pixels outside the edited patch;
- align without a jump at 1×, 2×, and 3× display scale;
- remain readable at a 96 px avatar presentation size;
- avoid visible seams on both light and dark UI backgrounds.

Recommended source format: layered PSD, Affinity Photo document, or equivalent, plus exported transparent PNG overlays. A fully editable vector redraw is also acceptable.

## Runtime animation recommendation

Use amplitude-driven visemes rather than generating video:

- silence → `closed`
- low amplitude → `slightly-open`
- medium/high amplitude → alternate `slightly-open` and `wide-open`
- rounded vowel estimate, when available → `o`
- idle completion → `smile`, then `closed`

Rate-limit changes to roughly 8–12 frames per second and crossfade over 35–60 ms. Respect Reduce Motion by lowering the frame rate and mouth travel, not by disabling communication feedback entirely.

The avatar container must not move while speaking. This preserves stable dwell, switch, head-tracking, and eye-gaze targets.

## Acceptance gates

- Character remains recognizable at 96 px.
- No hair is cropped.
- Mouth changes do not shift the nose, chin, eyes, or head.
- No visible patch boundary at 200% zoom.
- Voice playback and mouth motion begin and end together.
- Animation stops and returns to `closed` when speech is interrupted.
- Works offline with cached/system TTS; no per-minute avatar API.
