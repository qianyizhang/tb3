# Route-resampling pilot: next-session handoff

The integrated pilot is implemented and polished in commit
`750498629bb07c970a563cd7d2cc67006f1170ba` on `main`. On 2026-09-25 the user
reviewed the result as “this is much much better” and requested cleanup, commit
and this handoff. Preserve that visual direction. Remaining catalogue migration
has not been executed. The concrete continuation assignment below replaces the
earlier vague request to choose a reuse case.

## Full picture before choosing the next batch

The [complete candidate map](../../../presentation/EXPLAINER-CANDIDATES.md) lists
**all 205 entries across 145 task families**, grouped by operation: 46 internal
TB3 entries and 159 external entries. One has migrated to the scripted pipeline;
204 remain planning candidates. It includes existing recipe/state, source brief,
task-versus-study role, counts and proposed rollout. The coronary pair below is
the recommended first reuse test, not the whole project.

## Proposed first batch: two distinct coronary tasks

**Recommended deliverable:** integrated scripted explanations for
`tb3-named-coronary` and `tb3-coronary-inventory`, each with its own HTML, MP4,
poster, captions, transcript and acceptance evidence. The user approved the pilot's
appearance, then asked for meaningful continuation work. This is the concrete
recommended next scope; this handoff update does not itself migrate either entry.

The product difference must be visible:

| Existing task | Given | Explanation must show | Final teaching output |
| --- | --- | --- | --- |
| [Named artery](../presentation/briefs/tb3-named-coronary.md) | CTA and target name; no supplied centerline/mask | Follow one requested course; distinguish target identity from path geometry | One requested centerline in patient coordinates |
| [Branch inventory](../presentation/briefs/tb3-coronary-inventory.md) | CTA and generic taxonomy; no case-specific branch list or geometry | Discover branches, separate them, assign identities and expose unresolved branches | Inventory linked to labeled centerline polylines |

This is substantive reuse work. At present, the compiler and DTO accept only
`route-unfold-v1`/`tb3-route-kit-v1`; the player mounts `createRoutePrefab` for every
plan. The heading, scope, legend, output panel and fallback are resampling-specific.
The exporter writes `route-unfold.mp4`; the browser test assumes frame 791.
Changing only story captions would produce the wrong explanation for these tasks.

### Implementation sequence

1. **Ground both stories in the existing contracts.** Read the linked briefs and
   retained BR041/BR042 protocols, including the selected revision's coordinate
   convention. Write two canonical group stories: named-target tracing versus
   inventory discovery. Include input, operation, output and difficulty beats.
   Keep teaching illustrations distinct from model inference or scored results;
   preserve native input/helpers and the existing reference reveal.
2. **Add the smallest second typed recipe.** Extend `explanation_stories.py` and
   `presentation_contracts.py` with a discriminated route-discovery plan and
   validated recipe-specific channels. Regenerate TS contracts. Keep existing
   route-unfold scripts compatible and avoid arbitrary untyped channel bags.
   Add a small recipe dispatch shared by player, output view and fallback; keep
   the existing stage, absolute-frame clock and export composition.
3. **Build branch selection and inventory visuals.** Reuse stage and asset-loading
   infrastructure. Inspect existing anatomy/graph assets before creating a new
   fixture. If the route fixture cannot represent the required branch operations,
   add one small provenance-labeled teaching graph with stable branch IDs and
   explicit coordinates, rather than pretending it is patient anatomy. Do not
   label the generic phantom RCA as though that identity were validated. A selected
   branch must drive its line, output row and label from the same data. Named-target
   and inventory stories need different reveal logic and different final outputs.
4. **Remove concrete pilot assumptions.** Make heading, scope, legend and output
   description story/recipe-owned; render a centerline or inventory panel instead
   of the CPR raster. Provide a matching static fallback. Generalize the export
   filename and browser acceptance inputs to the selected story's duration and
   recipe, retaining compatibility for the delivered route pilot. Test multi-story
   asset binding so a story cannot silently render another story's prefab.
5. **Bind exactly the two entries and deliver.** Add explicit `story_id` bindings
   for these two catalogue IDs. Generate a fresh full Explorer and separate
   standalone exports. Capture meaningful stills first, inspect readability, then
   render both MP4s. Produce a concise comparison showing the task distinction,
   source receipts and acceptance results. Commit owned changes after checks and
   stop for review of this pair.

### Acceptance that makes the work meaningful

- A viewer can tell **a known target with an unknown course** from **an unknown
  branch inventory with unknown courses** without reading implementation details.
- Every displayed branch/row/highlight agrees with the fixture's branch ID and
  coordinates. Missing or uncertain identity is not silently marked correct.
- Each canonical script drives HTML, subtitles, transcript, stills and MP4. Changing
  a caption and duration changes every projection and its beat boundaries.
- Random/reverse seeks, final frame, pause/replay, switching between all three
  scripted stories, mobile, localization, reduced motion and GPU fallback pass.
  Recipe-specific tests derive bounds from the plan; no copied 792-frame assumption.
- The original `ours` pilot and unbound legacy entries keep their behavior. Full
  presentation checks and `make check PYTHON=python3.12` pass; exporter receipts
  identify exact assets/source revision and outputs. No new model run is required.

### Later catalogue work

After reviewing this pair, group the remaining catalogue by the actual operation
and output it needs, not merely by illustration kind. Record entry IDs, reusable
recipe/assets, missing assets and source limitations, then migrate one coherent
family per reviewable batch. Repair/control, registration and motion need their
own operation semantics; do not force them through the route-discovery recipe.
The next session's deliverable is the two working explainers above, not a second
status memo or a catalogue-wide rewrite.

### Ready-to-use next-session prompt

The user can use this prompt to authorize the recommended implementation:

> Read groups/tubular-anatomy/history/2026-09-25-route-resampling-pilot.md and
> presentation/EXPLAINERS.md. Implement the next assignment in that handoff:
> distinct named-coronary and coronary-inventory explainers using the existing
> stage, player and media exporter. Remove the specific single-pilot assumptions
> needed by those two stories; preserve the approved route-resampling pilot and
> other work. Deliver the integrated Explorer, two HTML/MP4 exports and acceptance
> evidence, then commit and stop for review before migrating further families.
> Inspect current status and preserve later commits; do not reset to the handoff.

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
