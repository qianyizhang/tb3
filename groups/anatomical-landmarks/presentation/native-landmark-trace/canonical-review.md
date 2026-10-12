# Canonical native landmark trace review

**Codex assistant review, 2026-10-12:** `tb3-named-landmarks` now binds
[`br039-native-trace`](../stories/br039-native-trace.story.md), implemented in
`13bacfb4`. This covers one retained Terra/high partial-CT attempt on VerSe
sub-verse823. The [original story](../stories/named-landmarks.story.md), all frozen
results and the historical acceptance ledger remain unchanged.

## Verified scope

- **Native context:** full supplied 512×512×920 crop, physical RAS geometry,
  coarse preview with explicit native sample indices, thirty recorded inspection
  states and ten exact delivered PNGs. Original full-scan cranial pixels are absent.
- **Process:** requested long views, sagittal planes and projections, fourteen
  axial levels, logged weighted centres, saved coordinates/statuses and explicit
  private-reference reveal. Reader controls remain distinct from recorded actions.
- **Interpretation:** saved T4 is 2.142412 mm from source T5; true source T4 lies
  outside the crop. Near-coincident point labels are grouped without shifting
  coordinates. Frozen visible localization remains 1/13 within 5 mm, 2/13 within
  10 mm and 5/13 within 20 mm; outside false-observed is 1/11, absent is 0/2.
  This reader comparison does not change scores or adjudicate clinical truth.
- **Video:** 1176 frames at 24 fps, 49 seconds, 1280×720; full decoding,
  normal-rate playback to completion and three seeks passed. Decisive states and
  selected decoded-video samples were visually inspected, not every video frame.
- **Reader:** both locales, native/keyboard controls, reference reveal/reset,
  entry switching, 390-pixel layout and actual no-WebGL fallback passed. Slice
  readouts fit above the reference result/footer. Chinese navigation explicitly
  identifies English manuscript and figure text. Zero page errors/remote requests.
- **Shared regression:** CT and MRA exports were freshly rendered and fully decoded
  in the same batch; both passed the integrated interaction matrix and their
  reference stills were inspected. Their earlier normal-playback reviews remain
  separate historical receipts.

## Pinned local evidence

- Review: `.local/anatomy-pose/landmarks/canonical-v2/review.json`
  SHA-256 `af92337ac1209ce4cc638b59cb6946edbb78cfee2a2617d7ab579f002f4f6fed`.
- Export: `.local/anatomy-pose/landmarks/canonical-v2/batch/br039-native-trace/`.
- Collector: `.local/anatomy-pose/landmarks/canonical-v2/collection/review.json`
  SHA-256 `696107f151fee09ac18e2a1faf84232fb02f7d22f286a992488258597d3490d0`.
- Browser witness: `.local/anatomy-pose/landmarks/canonical-v2/batch/browser-witness.json`
  SHA-256 `25413a9f78793e1518cebf823ba406d3861caf1cfceca62229ff353ba99e0821`.
- Exact inspected images, observations and limits: `.local/anatomy-pose/landmarks/canonical-v2/inspection.json`.

The final isolated staged implementation passed `make check PYTHON=python3.12`
(**527 Python tests** plus repository gates); `make js-check` passed
**166 stories / 313,170 deterministic frames** and the existing JS checks.
Logs remain under `.local/anatomy-pose/landmarks/`; disposable staged checkouts
were removed with an exact-path receipt. Raw evidence and generated media remain local.

The earlier `canonical-v1` review failed its capture layout assertion; retained
preflight inspection also found ambiguous dropdown labels. Capture-only slice
height and explicit accessible names were corrected before the successful fresh
v2 export. The reference chapter heading was made neutral before reveal.
This pass used `complete-explainers` 1.2.0: run interaction/layout preflight before
freezing an expensive video batch, then require the fresh batch-bound witness.

Original ledger SHA-256 before and after regression:
`b49bd1ef3d95de7f87de3891c8bb3f22356d0da00087e984f31a6282b1bff3ef`.

Reopen on changes to the manuscript, selected source assets, geometry, shared
reader or exporter. This review covers one condition, not the entry's eleven model
attempts. Missing local artifacts require source recovery; they do not authorize
invented solver observations, clinical conclusions or replacement scores.
