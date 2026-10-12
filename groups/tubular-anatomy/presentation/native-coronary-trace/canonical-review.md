# Canonical native coronary review

**Codex assistant review, 2026-10-12:** entry `ours` now binds
[`br030-native-trace`](../stories/br030-native-trace.story.md), implemented in
`8ca0d637`. This covers one retained BR-030 Terra/high development attempt.
The [original story](../stories/route-unfold-teaching-v1.story.md), frozen score
and historical acceptance ledger remain unchanged.

## Verified scope

- **Native context:** the whole supplied 366×319×205 CTA crop retains its affine
  and L/A/S directions. Its 128×112×103 indexed preview is context; a 70×70×55
  native-resolution detail preserves local CT sampling. Detail display bytes were
  independently matched to source CT. The rest of the source scan was not supplied.
- **Recorded process:** three exact delivered montages, their native plane ranges,
  printed alternatives, the eventual step-38 fourteen-point ridge and original
  saved repair. The repair adds 103 voxels, removes none and changes none outside
  the binary editable region. No intermediate repair mask is invented.
- **Saved geometry:** 371 original RAS route points, eight 371×65 CPR arrays and
  the complete 36,128-vertex / 72,248-face mesh. Each CPR sample links to retained
  source RAS and HU. Independent source sampling has p99 error 0.001617431640625 HU;
  maximum centre/offset geometry error is 0.00000844176459 mm. No scorer was rerun.
- **Frozen outcome:** repair, route and mesh pass; original reward remains **0**
  because the CPR distance axis is inconsistent. Its endpoint is 184.80925341171147
  mm versus saved-polyline length 175.91775513587936 mm. The retained author
  correction changes only `arc_mm` and passes separately. It is a later
  intervention, not another agent success or a revised original score.
- **Visuals and interaction:** all seven chapter stills and selected decoded-video
  samples inspected. Native detail, translucent edit tint, montage and final
  reference cards fit above the footer. Both locales, native-plane/detail controls,
  CPR angle/route/offset controls, source-coordinate linkage, keyboard navigation,
  reference reveal/reset, 390-pixel layouts and no-WebGL fallback passed.
- **Video:** 1176 frames at 24 fps, 49 seconds, 1280×720; full decoding, normal-rate
  playback to completion and three seeks passed. These discrete holds are not a
  continuous agent screen recording. CPR and mesh views are reader reconstructions;
  no solver-viewed images of those outputs were retained.
- **Shared regression:** five native adapters passed the fresh preflight and ten
  Explorer navigation checks, with zero page errors or remote requests. Existing
  CT, MRA, landmark and MRI videos were not rerendered. The final coronary package
  has its own source-bound browser witness.

## Pinned local evidence

- Review: `.local/anatomy-pose/coronary/canonical-v2/review.json`
  SHA-256 `f92519f6c1be8df0e0abb0b849285c7b2a95d442879eb5ee748718e755ccb323`.
- Collector: `.local/anatomy-pose/coronary/canonical-v2/collection/review.json`
  SHA-256 `0461d3d3d8f59a6d68e2d11cdbfec2b39694e430af700581ef7b0243f0cf6cdf`.
- Browser witness: `.local/anatomy-pose/coronary/canonical-v2/batch/browser-witness.json`
  SHA-256 `82e90ad8b93669c5d73fd7461a2b3db4732dc0333f17bf6745127e412c3ebf2d`.
- Five-adapter preflight: `.local/anatomy-pose/coronary/matrix-preflight-v4/preflight-matrix.json`
  SHA-256 `10ab96f0ca75b57ba9c5536481ee5b188c5d2cf961bd83d43f282f1c222c6f84`.
- Exact inspected images, observations and limits:
  `.local/anatomy-pose/coronary/canonical-v2/inspection.json`.
- Export: `.local/anatomy-pose/coronary/canonical-v2/batch/br030-native-trace/`.
- Raw package and independent checks: `.local/anatomy-pose/coronary/br030-20261012-v3/`.

The final isolated staged snapshot passed `make check PYTHON=python3.12`:
**541 Python tests**, records, documentation, contracts, types, Ruff and workflow
checks. `make js-check` passed **168 stories / 315,522 deterministic frames** and
native geometry tests. Earlier gate attempts exposed stale story-binding assertions,
a Markdown coordinate interpreted as a link, and formatting; all were corrected.
The README correction required a fresh source-pinned export. Its chapter stills
and browser screenshots match the prior inspected export exactly; decoded-video
samples were inspected again. Mechanical collection retains its pending-review
status; this separate record reports the assistant's scoped inspection.

Five exact disposable validation checkouts were removed with a retained receipt at
`.local/anatomy-pose/coronary/disposed-validation-snapshots.json`. Logs, raw sources,
package versions, preflights and media remain local. The original ledger SHA-256 is
`b49bd1ef3d95de7f87de3891c8bb3f22356d0da00087e984f31a6282b1bff3ef`.

## Limits and reopening

Case 1 is a training-split development fixture with substantial supplied helpers.
Mask-derived references are related geometry evidence; a geometry-only author
baseline also passes. This does not establish clinical accuracy, lesion-specific
stenosis/plaque truth, population difficulty or difficult anatomical discrimination.
Chinese navigation discloses the English manuscript and recorded annotations.
No-WebGL mode retains MPR, CPR and a context poster; the full 3D mesh requires WebGL.

Reopen on manuscript, source, geometry, shared reader or exporter changes.
No new trial, runtime installation, scorer execution, regrade, clinical
adjudication, push or publication occurred. Existing research reopening conditions
in [the idea](../../ideas/idea-coronary-route-cpr.md) remain unchanged.

This pass used `complete-explainers` 1.2.0. Reusable lesson: inspect a native local
view beside the whole-volume context before freezing the export, and run docs and
format checks before freezing source fingerprints. Opaque permission overlays can
hide the evidence that the local view is meant to explain.
