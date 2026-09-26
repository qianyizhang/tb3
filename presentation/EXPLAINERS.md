# Canonical task explainers

The operation library preserves the original `ours` route pilot and adds explicit
spatial and planar stories. [The candidate map](EXPLAINER-CANDIDATES.md) and
[per-entry ledger](EXPLAINER-LEDGER.json) use all **205 entries** as the denominator.
A bound story is not automatically accepted; unresolved entries remain visible.

## Owners

- Internal canonical scripts live in `groups/<group>/presentation/stories/`.
  External task scripts live beside their briefs in
  `presentation/external-tasks/stories/`. Scripts own captions, narration, scope,
  sequencing and integer frame timing. Scientific briefs/protocols remain authoritative.
- `explanation_stories.py` retains the v1 route parser and adds closed v2 models
  discriminated by recipe. It checks continuity, source locators, provenance,
  recipe dependencies and hashes before projection. No validator acquires data.
- Python presentation contracts still generate browser DTOs. Bindings are explicit
  `illustration.story_id` values, including nested WSI collections.
- [The retained pack index](assets/teaching-prefabs.json) references the existing
  route owner, seven selected mathematical fixture packs and the existing anatomy
  owner. Topology checks the original route hash; anatomy checks its common source
  case/frame and exact parts/notices. No evaluator reference pack is supported.
- `story-timeline.ts` returns an immutable, recipe-discriminated absolute state.
  `use-scene-player.ts` owns the single clock, seek, visibility, reduced motion and
  cleanup for both spatial and planar content.
- `stage.ts` remains the camera, lights, renderer, projection and disposal owner.
  New spatial content uses its existing native seam. Planar stories use DOM/SVG
  without creating WebGL. Recipe dispatch precedes legacy mode selection.
- `TaskVisual.tsx` composes chapters, stage, output, current caption, matching
  legend and transcript. No-GPU spatial views derive from the same fixture and
  plan. Planar stories remain interactive without a GPU. Chinese controls retain
  the explicit English-source note.

## Integrated operations

| Recipe | Distinction preserved |
| --- | --- |
| Route v1 | Original synthetic sampling ribbon; not full BR030 |
| Topology | Selected connected path vs seven-edge inventory; teaching graph is not CTA input |
| Rigid correspondence | One transform, P1–P3 fit, P4–P5 held-out checks, absent P6 and deformation boundary |
| Multiscale | Twelve supplied slots, coordinate navigation, and six-code coverage are separate stories |
| Local edit | Bounded correction, unsupported source-evidence gate, valid unchanged control |
| Shape/material | Identical analytic shells with two material maps; calculation/sparse/volume conditions distinct |
| Longitudinal | Explicit match/new/unobserved relations; actual CT task supplies no candidate locations |
| Anatomy audit | Existing seven-part s1233 assembly; label/witness schema and clean-control semantics |
| CT/MRI | Separate Radon/FFT measurements and image outputs; toy vs task dimensions/assistance explicit |

## Build and export

Use the existing environments and exporter. Generated media, review frames and
receipts stay in fresh local destinations; nothing here launches tasks or publishes.

```sh
UV_CACHE_DIR=/tmp/tb3-uv-cache npm run frontend:build
npm run media -- --story=topology-path --output=.local/explainers/NEW-STILLS --stills-only
npm run media -- --story=topology-path --output=.local/explainers/NEW-VIDEO
```

Each export contains interactive single-file HTML, the canonical script and plan,
first/chapter/poster frames, VTT/SRT, transcript and a receipt. Full export adds
silent H.264 MP4 at the script's fps. V1 retains `route-unfold.mp4`; v2 filenames use
story IDs. The capture bridge exists only in the dedicated export entry.

Capture seeks the exact integer frame and waits for React commit, fonts, HTML and
SVG image decoding before screenshotting the complete 1280×720 root. Receipts pin
source/asset/frontend/lock hashes, dirty files, OS, browser, renderer and outputs.
These are local rendering receipts, not scientific evidence or cross-GPU equality.

## Checks and visual acceptance

```sh
.venv/bin/python -m unittest discover -s tests -p 'test_explanation*.py' -v
node tests/scene_player.cjs
node tests/explanation_story.cjs
node tests/explanation_expansion.cjs
.venv-br030/bin/python tests/expansion_fixture_numerics.py -v
node tests/explanation_expansion_browser.cjs REVIEW-DIR EXPLORER-HTML
node tests/explanation_story_browser.cjs ROUTE-EXPORT-DIR EXPLORER-HTML
make presentation-check
make check PYTHON=python3.12
```

Browser commands use the disposable repository harness outside the restricted
macOS command sandbox. The expansion matrix exercises actual `file://` pages,
English and Chinese-source fallback, first/decisive/ending frames, narrow screens,
no-GPU mode, repeated seeks and navigation. Exact sampled states are required.
The composed DOM must match exactly on repeated seeks. A documented raster allowance
covers at most 2,048 of 921,600 pixels differing by one channel level at Chromium
SVG antialias/translucent-fill edges. V1 retains its existing 16-pixel / 8-level
raster allowance; displaced content is a failure.

Inspect the resulting scenes in addition to tests. Keep per-entry observations,
before/after frames, source boundaries and unresolved dependencies in the ledger
and local acceptance report. A legacy diagram or passing build is not migration
completion. Do not remove scientific conditions or frozen outcomes for uniformity.
