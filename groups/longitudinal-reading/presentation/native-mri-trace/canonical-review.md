# Canonical native longitudinal MRI review

**Codex assistant review, 2026-10-12:** `tb3-longitudinal-mri` now binds
[`br037-native-trace`](../stories/br037-native-trace.story.md), implemented in
`3233f151`. This covers one retained BR-037 P03 neutral Terra/high attempt.
The [original story](../stories/longitudinal-mri.story.md), frozen scores and
historical acceptance ledger remain unchanged.

## Verified scope

- **Input context:** metadata for all 122 supplied volumes; sixteen selected dynamic
  previews across day 0 and day 34. Each visit preserves its own affine, spacing,
  explicit native sample indices and display window. No registration or calibrated
  signal comparison is implied. Disconnected scouts remain separate files.
- **Recorded process:** three exact delivered PNGs and selected logged planes,
  projection slabs, focus windows, computational ROIs and saved citations. Original
  step-18 side labels remain beside the later correction caveat. Later saved images
  differ from delivered bytes and are not substituted. Inspection centres and saved
  citations retain their one-voxel distinctions; all file citation phases are zero.
- **Measurement limits:** saved component voxel-edge extents are 21.25119972229004
  and 20 mm, a prior-audit change of −5.887666%. Source FTV rises 73.8%; raw source
  diameter falls 16.7%, with unresolved units. These are different endpoints.
  Frozen contract success leaves clinical accuracy unscored. The conditional
  smaller forecast, confidence 0.43, remains a solver claim; an always-smaller
  baseline also matches all three neutral future directions.
- **Video:** 1176 frames at 24 fps, 49 seconds, 1280×720. Full decoding,
  normal-rate playback to completion and three seeks passed. All seven chapter
  stills and selected decoded-video samples were inspected. Discrete holds do not
  represent continuous agent motion or human inspection of every video frame.
- **Reader:** both locales, visit/dynamic/native-plane controls, keyboard orbit,
  reference reveal/reset, 390-pixel layouts and actual no-WebGL fallback passed.
  Capture cards fit above the result/footer. Chinese navigation identifies English
  manuscript/figure text. Exact figures open separately at original resolution;
  video thumbnails are compact overviews. Zero page errors or remote requests.
- **Shared regression:** a fresh four-adapter preflight covered CT registration,
  MRA repair, CT landmarks and MRI with eight Explorer navigation checks. Existing
  videos were not rerendered; their previous decode/playback reviews remain separate.

## Pinned local evidence

- Review: `.local/anatomy-pose/mri/canonical-v1/review.json`
  SHA-256 `2705d5e208be4c333593ab834d1e40fa725599d01dc75f9b6dd048109e0ef1e6`.
- Collector: `.local/anatomy-pose/mri/canonical-v1/collection/review.json`
  SHA-256 `85398c5a8d62fa69fcaa6dcf50d706b6bad4dcf71d00e819ac1ff1402c73c359`.
- Browser witness: `.local/anatomy-pose/mri/canonical-v1/batch/browser-witness.json`
  SHA-256 `45742226f34c9d458993f140b069480b47452081d68dee23b559d248b0eeb564`.
- Four-adapter preflight: `.local/anatomy-pose/mri/matrix-preflight-v1/preflight-matrix.json`
  SHA-256 `71797c5c4da746e34a5788ac95c8ff51b54812be87ef31dcaf4ab0ba9592e1de`.
- Exact inspected images, observations and limits: `.local/anatomy-pose/mri/canonical-v1/inspection.json`.
- Export: `.local/anatomy-pose/mri/canonical-v1/batch/br037-native-trace/`.

The isolated staged implementation passed `make check PYTHON=python3.12`
(**534 Python tests** plus repository gates). `make js-check` passed
**167 stories / 314,346 deterministic frames** and native geometry checks.
The exact temporary validation checkout was removed with a retained receipt at
`.local/anatomy-pose/mri/disposed-validation-snapshot.json`; logs, raw sources,
preflights, package versions and media remain local.

Preflight still inspection found a reference-scene control overlap and redundant
saved-position readouts. Capture-only controls/readouts were compacted before the
frozen final export. Display-window labels were rounded without changing source
values. This pass used `complete-explainers` 1.2.0: preflight the independent visit
controls and all capture cards before an expensive frozen video export.

Original ledger SHA-256 before and after regression:
`b49bd1ef3d95de7f87de3891c8bb3f22356d0da00087e984f31a6282b1bff3ef`.

Reopen on changes to the manuscript, selected sources, geometry, shared reader or
exporter. This review covers one condition, not all four retained BR-037 attempts.
No trial, new measurement execution, clinical adjudication, score revision or
publication occurred. Unresolved source diameter units and clinical measurement
validity retain their existing reopening conditions.
