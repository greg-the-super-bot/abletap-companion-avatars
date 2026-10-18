# AbleTap claims register — abletap.io

Public copy on abletap.io must match this file. Same format as the shared
register (`_brain/CLAIMS-REGISTER.md`), read by `scripts/check_claims.py`.
Update THIS FILE FIRST when what we can say changes.

## What we can say (Chris, 2026-10-18)
- AbleTap is coming soon; families join the waitlist. No pre-order, no price, no App Store listing yet.
- Streaming: Disney+, Hulu, Paramount+ and Prime Video may be named **in plain text only** (no logos, no badges). They are the services that pass on the TV box today.
- Never name Netflix or YouTube as working, Roku or Fire TV as supported, or compare AbleTap with TouchChat or Proloquo2Go.
- No "Works with" badges.
- Ava and the companions are not live conversation yet: never "talk to Ava", "talks with you" or "live".
- No health/medical app category or pre-order schema.

```yaml
# machine-readable — consumed by check_claims.py
allowed_prices: []
banned_patterns:
  - "netflix"
  - "youtube"
  - "roku"
  - "fire ?tv"
  - "touchchat"
  - "proloquo"
  - "works with"
  - "talk to (ava|sunny|alex|buzz|grace)"
  - "talks with you"
  - "ava is live"
  - "preorder"
  - "pre-order"
  - "healthapplication"
  - "medicalapplication"
allowed_contexts:
  - "do not claim abletap works with every streaming service"
scan_globs: ["**/*.html", "**/*.js", "**/*.txt"]
```
