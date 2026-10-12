# Native-context presentation enhancement

**Active goal, authorized by the user on 2026-10-12:** after cleaning up and
making scoped commits for the two Anatomy trials, apply the same approach to
the rest of the presentation. The user specifically asked for a connection to
the whole CT volume and a real task-solving trace explaining the process.

## Scope and baseline

The live `med explainer queue` on 2026-10-12 reports **205 catalogue entries,
154 core, 154 previously reviewed core, and 51 excluded from automatic work**.
There are zero ready, resolution or deferred items under the earlier completion
standard. That is not completion of this new enhancement goal.

Use [EXPLAINER-SCOPE.json](EXPLAINER-SCOPE.json) for membership and priority,
and [EXPLAINER-LEDGER.json](EXPLAINER-LEDGER.json) for existing acceptance and
source history. Do not reopen excluded/nonmedical work or overwrite old
acceptance receipts. This plan defines the new pass, not another acceptance
registry. Attach new renderer/evidence reviews to exact source snapshots using
the existing review machinery and group-owned findings.

| Order | Core group | Entries | First emphasis |
| --- | --- | --- | --- |
| P0 | Existing TB3 research | 45 | Real retained runs and source context; link finding to canonical task |
| P1 | Clinical structure | 41 | Anatomy, geometry, localization and segmentation operations |
| P1 | Clinical reading | 31 | Image evidence, candidate decisions and explicit uncertainty |
| P2 | Image formation | 37 | Actual operator/input/output relationships and selected dependencies |

Entry coverage is separate from condition coverage. Each review must identify
which actual conditions and attempts it shows; one retained attempt does not
explain every condition of an entry.

## Two reference implementations

- [CT registration](../groups/registration/findings/br019-full-view-trace.md):
  whole solver-visible crop, native coordinate section placement, selected wrong
  and coarse poses, actual saved answer, image comparison and reference reveal.
- [MRA vessel repair](../groups/tubular-anatomy/findings/br026-gap-trace.md):
  full network to local detail, native image slices, nine logged thresholds,
  two contact patches, bounded edit and reproduced frozen evaluation.

These local standalone prototypes establish useful interaction/evidence patterns.
Their canonical migrations are now separately regression-reviewed; they do not
increment historical completion counts. Their group-owned source, derivation receipts and reusable
browser checks are retained; raw patient volumes and generated media stay local.

## Completion criteria for each applicable entry

1. **Evidence inventory:** actual input, supplied helpers, output, reference,
   trace/intermediates and their roles/hashes; explicitly identify absent artifacts.
2. **Context:** connect the decisive view to the full supplied volume, slide,
   time series or other task input. A supplied crop is not the original full scan.
3. **Process:** explain consequential observed operations using real retained
   tool actions where available. Reconstructed states are labeled. Do not invent
   cognition, continuous trajectories, patient images, predictions or scores.
4. **Interaction:** controls expose a meaningful variable or comparison and share
   the same scientific data/model as the displayed measurements. Separate reader
   controls from recorded agent actions; keep references behind explicit reveal.
5. **Interpretation:** preserve frozen results, task/reference disputes and
   condition limits. No new trial, clinical claim or difficulty promotion follows
   from an improved explanation.
6. **Integration:** use the canonical story/compiler, shared reader/player and
   selected asset packaging. Avoid expanding the prototypes into 154 independent
   applications or importing the entire visual library for one example.
7. **Verification:** inspect decisive views and reference states; check native
   coordinates/numerical claims, mobile/keyboard/fallback behavior, provenance,
   asset closure and the repository gates for the owned staged snapshot.

For entries without a retained model run, explain the supported task mechanism
and label the absent run. Follow the existing bounded source-resolution policy
before symbolic fallback; retain the top warning and acquisition route. Missing
evidence can limit a trace claim without blocking a truthful task explanation.
Do not count a symbolic demonstration as a real solving trace.

## Work sequence

1. Finish two focused prototype commits, preserving unrelated work and local raw
   evidence. Retain build/check commands with each source implementation.
2. Inventory the 154 core entries against the criteria above, joining the current
   scope, ledger, canonical stories, group findings and available run pointers.
   Save reproducible inventory output locally; do not infer availability from titles.
3. Integrate one native-context/trace vertical slice with the existing framework,
   starting from `tb3-oblique-pose` and `tb3-vessel-connection-repair`. Preserve the
   prototypes as references until the canonical versions are visually checked.
4. Continue P0, prioritizing distinct capabilities with retained traces—named
   landmarks, longitudinal comparison, coronary routes, and whole-slide search—
   after checking actual source availability and existing audits.
5. Extend family adapters across P1/P2, review one entry at a time and commit
   bounded changes. Preserve entry-specific geometry and evidence boundaries.

The `complete-explainers` skill permits two bounded workers for independent
production. The main agent owns shared contracts, catalogue/ledger bindings,
integration and acceptance; workers own disjoint entry artifacts. Keep browser
rendering serial initially and preserve concurrent changes. Do not install
medical runtimes, launch new model trials, publish or push as a side effect.

## Retained-evidence inventory — 2026-10-12

The read-only [inventory service](../src/tb3_medical/explainers/inventory.py)
joins current core membership, leaf catalogue bindings, canonical stories,
declared source audits and explicitly linked experiment attempts.

| Locally verified availability | Core entries |
| --- | ---: |
| Canonical story file present | 154 |
| Declared source-audit receipt present | 124 |
| Explicit experiment links | 44 |
| Model result and at least one retained trace artifact present | 20 |
| Further source resolution or task-mechanism work | 134 |

These are entry counts, not independent attempts or scientifically reviewed traces.
Oracle/nop runs do not count as model traces. Missing declarations, absent local
files and unsafe paths remain distinct; asset-readiness prose cannot establish a
run. Files over 1 MiB have presence/size checks but no fresh hash claim. This first
inventory follows declared pointers, not every possible historical raw-run layout.
The 134-entry category does not prove that no trace exists elsewhere.

Reproduce the local report (generated data stays out of Git):

```sh
uv run --no-sync python -m tb3_medical.explainers.inventory \
  --output .local/anatomy-pose/core-evidence-inventory.json
```

After the two prototype migrations, prioritize named landmarks, longitudinal MRI,
respiratory correspondence and coronary paths using these retained candidates.
Whole-slide search still needs a trace-source investigation before any real-run
claim. Original acceptance receipts remain unchanged.

## Handoff boundary

The [native-trace compiler](../src/tb3_medical/explainers/native_trace.py) now
assembles two native-trace migration manuscripts from pinned local assets:
[CT](../groups/registration/presentation/stories/br019-native-trace.story.md) and
[MRA](../groups/tubular-anatomy/presentation/stories/br026-native-trace.story.md).
Each has six discrete chapters / 912 frames at 24 fps. The compiler validates
chapter-to-trace/state bindings, array lengths, native affines, source/output
hashes and the MRA edit domain. The declared saved component is independent of
reader-selected alternatives. Input, observed actions/output and private reference
are separate projections; a reference-capable chapter alone does not grant a UI
reveal. The package explicitly disclaims solver staging/privacy isolation.

The [CT mapping](../groups/registration/presentation/anatomy-pose/canonical-mapping.md)
and [MRA mapping](../groups/tubular-anatomy/presentation/anatomy-repair/canonical-mapping.md)
define adapter geometry, controls and remaining browser checks. Raw scans and
generated arrays/images are pinned but not committed. Missing assets fail by
default; explicit `--allow-missing` emits a missing-data record with no payload.
Use a fresh output path each time:

```sh
uv run --no-sync python -m tb3_medical.explainers.native_trace \
  groups/registration/presentation/stories/br019-native-trace.story.md \
  --output .local/anatomy-pose/NEW-native-ct.json
uv run --no-sync python -m tb3_medical.explainers.native_trace \
  groups/tubular-anatomy/presentation/stories/br026-native-trace.story.md \
  --output .local/anatomy-pose/NEW-native-mra.json
```

The manuscripts compile through the canonical `compile_story` path into a
Python-owned browser contract and shared native-trace reader. Both adapters use
the existing frame player and a selected offline exporter. Interactive reference
reveal is explicit and clears on backward navigation/reset; canonical capture
reveals only the authored reference chapter. Missing local assets retain the
narrative with a visible unavailable state, without substitute scans.

The two catalogue bindings select the native manuscripts following the separate
canonical motion/export and integrated Explorer regression reviews linked below.
Existing synthetic operation stories and acceptance receipts remain intact.

Prototype commits: `75171dc2` (CT registration) and `0e1d1a92` (MRA repair).
The isolated staged snapshots passed all repository gate targets, including
505 Python tests each. Validation needed three existing ignored archival Markdown
dependencies and an empty local scratch directory; those dependencies were not
committed. All three retained browser checks passed, covering native geometry,
recorded controls, keyboard/mobile views and static fallbacks. Validation logs and
the dependency hash receipt remain under `.local/anatomy-pose/`.

The goal is active. Baseline inventory and prototype cleanup are complete.
Three native adapters now have canonical integration and regression review;
151 core entries remain in the enhancement pass. Next, implement the longitudinal
MRI adapter from its retained P03 neutral source mapping, then continue source
resolution and family expansion. Existing 154/154 historical review status must
never be presented as this new goal's completion status.


## Shared native reader checkpoint — 2026-10-12

Implemented `NativeTraceReader`, CT and MRA geometry adapters, generated contracts,
canonical compilation/view composition and `native-trace-export`. Selected
packages carry source hashes, recorded deliveries and terms; they do not import
the universal scientific asset library. This is an implementation checkpoint,
not a new entry acceptance or a claim that the 154-entry enhancement is complete.

`tests/native_trace_browser.mts` exercises the local selected packages using the
repository's disposable browser harness. It checks chapter states, native sliders,
MRA threshold counts/contact counts/saved-output independence, reference reset,
390 px layouts, no-WebGL controls and 1280×720 captures at frames 0/480/768.
Fresh attempts remain local under `.local/anatomy-pose/shared-reader-v4/`;
`browser-review/receipt.json` pins the packaged HTML and selected dependencies.
The earlier captures exposed two CT rendering defects: React cleared the
imperative canvas when its loading text became empty, and transparent context
planes obscured opaque candidate geometry. Separate DOM ownership and one ordered
transparent pass fix these defects without changing native coordinates.

The subsequent canonical regression review completed normal-speed playback/full
decoding, integrated Explorer entry switching and both locales, source-pinned
collection and assistant visual inspection. The original ledger is unchanged.

## Canonical migration checkpoint — 2026-10-12

**2 of 154 core entries enhanced for one retained condition each; 152 remain.**
Implementation commit: `b085fd67`. Review records:

- [CT renderer review](../groups/registration/presentation/anatomy-pose/canonical-review.md).
- [MRA renderer review](../groups/tubular-anatomy/presentation/anatomy-repair/canonical-review.md).

Both selected exports passed 912-frame full decoding, 38-second normal playback,
three seeks and the integrated locale/mobile/native-control/reference/fallback
matrix. Decisive source-backed views and decoded-video samples were inspected.
The isolated implementation snapshot passed all repository gates, including
522 Python tests; JS checks covered 165 stories and 311,994 deterministic frames.
The migrated scientific prose remains English, disclosed in Chinese navigation.

Next is [the named-landmark trace mapping](../groups/anatomical-landmarks/presentation/native-landmark-trace/canonical-mapping.md):
BR-039 partial CT, 512×512×920 supplied crop, 42 retained steps and ten delivered
images. A native landmark adapter must connect inspection slabs and submitted
points to that crop, preserve the wrong-level frozen result, and distinguish
the excluded cranial source region. This mapping has no new visual acceptance.
Large input arrays and generated deliveries must stay in selected local bundles.

Keep the active goal running. No trials, runtime installation, pushes or
publication are authorized by this enhancement workflow.

## Native landmark checkpoint — 2026-10-12

**3 of 154 core entries enhanced for one retained condition each; 151 remain.**
Implementation: `13bacfb4`. The
[landmark renderer review](../groups/anatomical-landmarks/presentation/native-landmark-trace/canonical-review.md)
pins the 49-second export, full decode, normal playback/three seeks and integrated
locale/mobile/native-control/reference/fallback witness. The same fresh batch
regressed the CT and MRA readers. The original ledger is unchanged.

The [next MRI mapping](../groups/longitudinal-reading/presentation/native-mri-trace/canonical-mapping.md)
selects P03 neutral, one of four retained BR-037 attempts. All 122 input volumes
and 134 frozen task files were checked. Three actual image deliveries differ from
final saved figures; one delivered MIP predates corrected laterality labels.
Preserve that chronology, independent visit grids, phase-zero citations versus
dynamic ordinal, component-box measurement limits and the mechanical/clinical
boundary. Next: prepare bounded native previews, exact deliveries and logged states,
then integrate a two-visit reader with explicit source-reference reveal.
No new trial, source acquisition, clinical score or publication is implied.


## Native longitudinal MRI checkpoint — 2026-10-12

**4 of 154 core entries enhanced for one retained condition each; 150 remain.**
Implementation: `3233f151`. The
[MRI renderer review](../groups/longitudinal-reading/presentation/native-mri-trace/canonical-review.md)
pins the 49-second export, complete decode, normal playback/three seeks and final
locale/mobile/native-control/reference/fallback witness. A four-adapter preflight
also checked the earlier CT, MRA and landmark readers plus Explorer switching.
The staged implementation passed 534 Python tests and all repository gates;
JS checks passed 167 stories / 314,346 deterministic frames. The original ledger
is unchanged; this is enhancement coverage, not a new historical acceptance count.

The MRI reader connects all 122 input records and sixteen selected dynamics to
three exact deliveries, independent visit geometry, logged native inspections and
saved component-box extents. Delivered and saved image revisions remain separate.
Clinical accuracy and raw source diameter units remain unresolved as documented.
The active goal continues with retained coronary-route evidence and then whole-slide
search; no new trial, runtime installation, score revision, push or publication.


The [next coronary mapping](../groups/tubular-anatomy/presentation/native-coronary-trace/canonical-mapping.md)
selects entry `ours`, the BR-030 Terra/high repair → route → CPR attempt. All 18
frozen task files and three embedded PNG deliveries were verified. The supplied
366×319×205 crop is an exact subset of the retained full source; excluded pixels
were not solver inputs. Original repair, trace and mesh pass, but the CPR distance
array differs from saved-polyline cumulative length by 8.891498 mm. The original
reward remains zero; the retained author correction and its later score are separate.
Next: extract bounded native context, exact deliveries, the original 371-point
route, source-linked CPR arrays and mesh into a typed shared adapter. No source
payload, canonical binding or visual acceptance has been added for coronary yet.
