# Route-resampling pilot: next-session handoff

The integrated pilot is implemented and polished in commit
`750498629bb07c970a563cd7d2cc67006f1170ba` on `main`. On 2026-09-25 the user
reviewed the result as “this is much much better” and requested cleanup, commit
and this handoff. Preserve that visual direction. Remaining catalogue migration
has not been authorized; select the next bounded scope with the user.

## Start here

1. Inspect current Git status and ownership. Preserve later commits and local work.
   Read repository/group instructions, contribution rules and governance.
2. Read [the maintained explainer contract](../../../presentation/EXPLAINERS.md)
   and [canonical script](../presentation/stories/route-unfold-teaching-v1.story.md).
3. Open the latest local HTML/MP4 and acceptance report listed below. They are
   actual integrated renders, not the downloaded kit's reference render.
4. Establish the next task with the user. A distinct route/graph explanation is
   the recommended small reuse test; this is an assistant recommendation, not
   a user decision to migrate it or the catalogue.

Suggested next-session prompt:

> Read groups/tubular-anatomy/history/2026-09-25-route-resampling-pilot.md and
> presentation/EXPLAINERS.md. Inspect the current checkout without resetting it.
> Review the committed pilot and latest local artifacts. Recommend one bounded
> next route/graph reuse case, explain the required changes and acceptance, and
> agree that scope with me before implementing further catalogue migration.

## Reconciliation and scope

The checkout already matched pinned baseline
`24e4de7a4ec15165dec23eeadc5abbc9124ab710`; all 15 source blobs watched by the
downloaded handoff matched. No reset or history rewrite was needed. The existing
typed task-visuals feature, legacy recipes and three-stage behavior were preserved.
Only catalogue entry `ours` explicitly binds to `route-unfold-teaching-v1`.
Native input/helpers, full BR030 contract and post-run reference reveal remain.

The pilot explains **one synthetic route-conditioned sampling ribbon**. It does
not establish local mask repair, eight CT planes, closed mesh production, full
BR030 verification or clinical validity. Fixture coordinates are metres; actual
task outputs use millimetres. No model trial or medical-data acquisition occurred.

The original package remains at
`/Users/zhangqy/Downloads/tb3-codex-handoff-24e4de7/`. Its START-HERE/CODEX-HANDOFF
describe the completed assignment; do not blindly reapply it to the newer checkout.

## Architecture to preserve

- **Canonical source:** the group script owns copy, six beats, 24 fps and 792
  frames. `src/tb3_medical/explanation_stories.py` validates and derives the plan,
  HTML, subtitles and transcript. Python DTOs generate the TypeScript contract.
- **Assets:** `presentation/assets/teaching-prefabs.json` indexes the original
  retained fixture subset. Indexed JSON is the single runtime geometry path;
  NPZ is for numerical checks. Original manifest, script and retained asset bytes
  remain unchanged. Omitted redundant GLBs are documented in the fixture README.
- **Rendering:** existing `stage.ts` owns renderer/camera/labels/disposal;
  `route-prefab.ts` uses its narrow native-content seam. One sample index links
  the 3D cross-line, scalar profile and image column. The tree stays fixed.
- **Playback:** existing `use-scene-player.ts` owns the clock; pure
  `story-timeline.ts` evaluates absolute frames. `TaskVisual.tsx` composes both
  Explorer and standalone output. Do not add another engine/player/clock.
- **Export:** existing `scripts/export_med_tours.cjs --story=…` dispatches through
  `story_export_source.cjs` and the existing browser/pipe encoder. The dedicated
  export entry captures the full React frame with `?capture=1`, including DOM,
  SVG leaders, image and caption. Legacy `--only=…` remains supported.
- **Cleanup:** consolidated CSS/player state; capitalized chapters; one-time
  readiness initialization; poster selected from output visibility; stricter
  asset-index completeness and stale-plan checks; NUL-delimited Git paths in receipts.

## Local delivery and evidence

All paths below are relative to `/Users/zhangqy/pkgs/tb3/`; generated artifacts
are intentionally local and untracked. Do not delete earlier evidence as cleanup.

Latest output root: `.local/explainers/route-unfold-teaching-v1/20260925-polish/`.

| File under that root | Purpose |
| --- | --- |
| `REVIEW.md` | Review summary and evidence navigation |
| `delivery/index.html` | Portable interactive integrated view |
| `delivery/route-unfold.mp4` | Silent H.264, 1280×720, 24 fps, 792 frames, 33.000 s |
| `delivery/poster.png`, six beat PNGs | Integrated visual review |
| `delivery/plan.json`, `canonical.story.md`, captions and transcript | Canonical projections |
| `delivery/receipt.json`, `browser-acceptance.json`, `media-check.json` | Sources, rendering and decode evidence |
| `explorer.html`, `site/`, `presentation-qa/` | Full Explorer and site acceptance artifacts |
| `make-check.log`, `presentation-check.log`, `numerical.json` | Fresh verification |

Fresh checks passed: **163 Python tests**, index artifact policy, records/docs,
mypy, DTO consistency, Ruff and workflow lint; frontend/JavaScript checks; full
presentation suite with **205 briefs, 437 conditions, 200 illustrations** and 25
decoded native images; pilot browser lifecycle/seek/mobile/localization tests.
No browser errors or remote requests. Full MP4 decode passed.
Numerical checks cover 18,624 samples (max scalar error `1.3124e-5`) and 4,800
ribbon vertices (max error `1.3788e-7 m`); display raster error is zero.

The export predates the implementation commit: its receipt correctly identifies
baseline `24e4de7` plus 55 dirty-source hashes. Every hash was verified against
the staged bytes committed as `7504986`; do not relabel it as a clean-commit render.
MP4 SHA-256: `c95f171956a03068dd2455c91dc6d5c2a64a33bd46b7561fad421b7719d89bc0`.
Canonical script SHA-256: `daf9263b2eb0222775f2992953aae96912211f5a9ec3c3845a9d91f23a711187`.

Earlier `.local/explainers/route-unfold-teaching-v1/20260925-pilot/` retains the
baseline receipt, legacy tour export and canonical copy/duration mutation witness.
Its review describes the earlier output; use the polished delivery for appearance.

## Reproduce and known limits

Use existing environments; export to a fresh destination. Commands from repo root:

```sh
export UV_CACHE_DIR=/private/tmp/tb3-uv-cache
export PATH="$PWD/.venv/bin:$PATH"
npm run frontend:build
npm run media -- --story=route-unfold-teaching-v1 --output=.local/explainers/NEW-EXPORT
python -m tb3_medical.cli brief build --output=.local/explainers/NEW-EXPLORER.html
node tests/explanation_story_browser.cjs .local/explainers/NEW-EXPORT .local/explainers/NEW-EXPLORER.html
.venv-medical/bin/python tests/route_fixture_numerics.py
make presentation-check
make check PYTHON=python3.12
```

Browser-launching commands on this Mac require approved execution outside the
restricted command sandbox from the first launch; use the existing disposable
browser harness. Ordinary checks stay sandboxed. No runtime installation is needed.
Stage only owned files before the index-aware check and commit; preserve later work.

Hidden-document events and GPU-loss/unavailable checks are simulated. Physical tab
hiding is not claimed. Fallback uses the supplied fixture-derived poster and
canonical transcript; context loss persists until remount. Repeated seek checks
allow at most 16 changed pixels of 921,600, with channel delta ≤8/255. Pixel identity
across hardware is not claimed. The compiler/recipe remain intentionally bounded
to this pilot; expand their contracts only for a concrete, separately scoped use.
