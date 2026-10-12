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
They are not yet canonical player migrations and do not increment historical
completion counts. Their group-owned source, derivation receipts and reusable
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
assembles two **unbound** migration drafts from pinned local assets:
[CT](../groups/registration/presentation/drafts/br019-native-trace.story.md) and
[MRA](../groups/tubular-anatomy/presentation/drafts/br026-native-trace.story.md).
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
  groups/registration/presentation/drafts/br019-native-trace.story.md \
  --output .local/anatomy-pose/NEW-native-ct.json
uv run --no-sync python -m tb3_medical.explainers.native_trace \
  groups/tubular-anatomy/presentation/drafts/br026-native-trace.story.md \
  --output .local/anatomy-pose/NEW-native-mra.json
```

These drafts are not bound into `med story` or the Explorer yet. Next, add the
Python-owned browser contract and shared native-trace reader, connect it to the
existing frame player/selected exporter, and verify source/reference resets,
native geometry, captured frames, mobile and fallback views. Only then change
the two leaf bindings and append new renderer reviews. Existing synthetic
operation stories and acceptance receipts remain intact.

Prototype commits: `75171dc2` (CT registration) and `0e1d1a92` (MRA repair).
The isolated staged snapshots passed all repository gate targets, including
505 Python tests each. Validation needed three existing ignored archival Markdown
dependencies and an empty local scratch directory; those dependencies were not
committed. All three retained browser checks passed, covering native geometry,
recorded controls, keyboard/mobile views and static fallbacks. Validation logs and
the dependency hash receipt remain under `.local/anatomy-pose/`.

The goal is active. Baseline inventory, prototype cleanup and source verification
are complete; canonical integration and the remaining enhancement pass are not.
The first declared-source inventory is complete. Next, integrate a shared
native-trace adapter grounded in the two prototypes, then investigate undeclared
sources and expand the reviewed family adapters. Existing 154/154
review status must never be presented as this new goal's completion status.
