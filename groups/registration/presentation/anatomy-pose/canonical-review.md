# Canonical native-trace renderer review

**Codex assistant review, 2026-10-12:** `tb3-oblique-pose` now binds
[`br019-native-trace`](../stories/br019-native-trace.story.md). This covers one retained
BR-019 cardiac-r01 full-view calibration condition.
The [original story](../stories/rigid-correspondence.story.md), frozen result and historical
acceptance remain unchanged. This is renderer regression, not new task acceptance.

## Pinned local evidence

- Review: `.local/anatomy-pose/migration-review-v2/review-ct.json`
  SHA-256 `015fca8261cda4171ee6f5c577e84bf070acb28ed60a98e018ed9b2b569024b5`.
- Export: `.local/anatomy-pose/migration-review-v2/batch/br019-native-trace/`; 912 frames, 24 fps, 38 seconds,
  1280×720. Full decoding, normal-rate playback and three seeks passed.
- Collector: `.local/anatomy-pose/migration-review-v2/collection-ct/review.json`.
- Integrated browser witness: `.local/anatomy-pose/migration-review-v2/batch/browser-witness.json`
  SHA-256 `4634d5044d016ad8b94f453ec437bba9a037de3db74d86d37da6a474e9c44c5d`.
- Exact visually inspected PNG paths/hashes, observations and limits are in
  `.local/anatomy-pose/migration-review-v2/inspection-ct.json` and the review record.

The integrated matrix passed both locales, native/keyboard controls, reference
reveal/reset, entry switching, 390-pixel layout and actual no-WebGL fallback,
with zero page errors or remote requests. Chinese navigation explicitly labels
English source prose and figure annotations. Visual inspection covered decisive
canonical states, selected decoded-video samples, mobile and fallback surfaces;
it does not claim a human inspected every video frame.

The shared implementation snapshot passed `make check PYTHON=python3.12`
(522 Python tests plus repository gates) and `make js-check`
(165 canonical stories / 311,994 deterministic frames, plus the existing JS checks).
Generated media, source arrays and raw evidence remain local.

The first canonical render stalled while decoding hidden lazy evidence images.
That attempt remains at `.local/anatomy-pose/migration-review-v1/batch/`.
Capture now starts image loading before decoding; the successful fresh export
uses v2. Capture also reuses geometry within each discrete chapter; interactive
reset still restores controls. No continuous solving trajectory is invented.

Original ledger SHA-256 before and after both regressions:
`b49bd1ef3d95de7f87de3891c8bb3f22356d0da00087e984f31a6282b1bff3ef`.

Reopen this renderer review if its story, source assets, geometry, shared reader
or exporter changes. Missing local media is a recovery gap, not permission to
reconstruct purported solver observations or change the original score.
