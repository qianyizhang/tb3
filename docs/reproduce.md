# Reproduction and presentation

Set up the installed package through the [workflow](workflow.md). Supported
operations depend on the selected experiment. Canonical metadata does not imply
that every historical task can be rerun. This guide owns the **experiment support
and verification checklist**; each group's methods page owns its coverage and
backfill work. Experiment configs and selected-input manifests remain the
executable authority. The [migration inventory](migration/native-experiment-inventory.md)
is a historical snapshot, not the current backlog.

## Experiment support and verification

These are independently checkable capabilities, not maturity stages. For each
operation, distinguish **implementation support** (what can be invoked, with which
inputs) from **verification evidence** (what was actually checked, when, where and
against which criterion). A retained historical replay can have good proof without
a maintained command; a maintained command can exist without execution proof.
Use precise descriptions and linked receipts rather than one global percentage or
"fully reproducible" label. Product badges remain defined in
[the status vocabulary](status-vocabulary.md).

| Item | Support to document | Evidence needed to mark the selected scope complete |
| --- | --- | --- |
| 1. Evidence and interpretation | Stable experiment/protocol, conditions, attempt and observation identities where they exist, sources, group finding and limitations | Reconciled records and source links; distinguish scaffold, author pilot, model attempt and review. Being linked to a finding does not establish validity or replication. |
| 2. Input and environment recovery | Selected task/scorer/reference/answer files, origins, access/terms, runtime requirements and recovery instructions | Receipt naming exact recovered files and hashes, checked environment and missing items. File presence alone is not verified recovery; a source URL is not availability. |
| 3. Task preparation | Maintained preparation command or explicitly authored task files; solver-visible inputs separated from private references | Preparation into a fresh destination, checked task bytes and coordinate/data contracts. State whether this restores a frozen task or rebuilds it from upstream data. |
| 4. Execution and collection | Task configuration, launcher/runtime, conditions, controls and supported result collector | Selected task and result format validated; attempt identity, interruption/error handling and observations retained. A shared collector does not establish a runnable family recipe. |
| 5. Saved-output scoring replay | Maintained scorer and invocation for named saved answers/references | Receipt identifying scorer/input hashes, original observation, metric comparison criterion and discrepancies. Replay is a new observation of the same attempt, not another model run. |
| 6. Inspection and derived artifacts | Authored story/figures, native-data viewer, or regeneration command, naming which of these exists | Checked source links and the geometry/measurement invariants of the selected view. Viewing retained figures is separate from regenerating them from raw data. |
| 7. Portable export | Selected-input recipe, licenses/notices, explicit origins and standalone instructions | Fresh destination, manifest verification and the selected operation exercised outside the source checkout. State same-machine versus independent-machine scope. A replay package need not include a model runtime. |
| 8. Fresh execution verification | An explicitly selected task/setup and new attempt; distinguish control, deterministic author method and model execution | Receipt for an actual new execution, with runtime/config, outcomes and the agreed comparison criterion. A preview, saved-answer replay or historical completed attempt is not proof of a fresh execution of the migrated recipe. |

Record scientific/reference assessment separately. Technical replay may faithfully
reproduce a flawed scorer; missing local inputs do not automatically invalidate an
old conclusion. Fresh stochastic model outputs need not match exactly. Exact-byte
checks apply to frozen inputs; scoring equivalence applies to named metrics and
tolerances, not a promise of identical future model behavior.

## Current coverage and gradual backfill

Baseline checked 2026-09-21: all 38 canonical experiments have protocols and group
finding references; all seven groups have stories. Attempt records are not present
for every historical entry. The group lists below enumerate every experiment and
separate retained evidence from maintained methods and scoped proof.

| Group-owned checklist | Experiments | First suggested reusable scope |
| --- | ---: | --- |
| [Anatomical landmarks](../groups/anatomical-landmarks/methods/README.md) | 4 | BR-040: retain the verified CT/MRI replay baseline; distinguish frozen-task restoration from upstream preparation |
| [Anatomy audit](../groups/anatomy-audit/methods/README.md) | 10 | BR-017: broad/pair-focused supplied-mask audit |
| [Cardiac motion](../groups/cardiac-motion/methods/README.md) | 7 | BR-035: supplied-mask construction and strain checks; BR-034 clinical tracking is separate |
| [Lesion localization](../groups/lesion-localization/methods/README.md) | 1 | BR-016: saved localization scoring with source-assisted negative case identified |
| [Longitudinal reading](../groups/longitudinal-reading/methods/README.md) | 2 | BR-037: mechanical report contract and separately identified measurement audit |
| [Registration](../groups/registration/methods/README.md) | 7 | BR-024/028: paired physical-error scoring; preserve separate visual adjudication |
| [Tubular anatomy](../groups/tubular-anatomy/methods/README.md) | 7 | BR-041/042: saved geometry scoring and existing review receipts; preserve identity disputes |

The reusable scopes are assistant recommendations, not newly selected scientific
studies. The user requested consolidation and gradual backfill in
[the source discussion](../discussions/experiment-support-backfill-2026-09-21.md).
The first backfill enumerates existing evidence, support, proof and concrete gaps.
It does not infer that all eight items are required for every historical experiment.

Work one selected scope at a time:

1. Inspect existing receipts and recover the exact inputs for the intended operation.
   Record concrete missing items; do not reconstruct unknown historical settings.
2. Extract only the preparation/scoring helpers that will actually be reused.
   Compare saved outputs first and append proof without changing old scores.
3. Add inspection or export support when the intended use requires it. Reuse shared
   collection and presentation instead of porting duplicate historical runners.
4. Verify fresh execution only when separately authorized and the runtime and
   applicable controls are ready. Recovery, replay and documentation do not require
   a new model run.

In the owning methods page, check off a bounded deliverable only with a source or
receipt and its scope/date. Keep missing, not checked, unsupported, and deliberately
historical work explicit in prose. Update that page when support changes; append
new observations rather than rewriting dated proof. Reopen historical-only recipes
when an actual reuse need selects them. No blanket conversion, new status system,
automatic background campaign or extra approval queue is introduced.

## Saved CT/MRI output replay

The maintained BR-040 landmark method supports three cases: `ct-full`, `ct-partial`
and `mri32-full`. Restore the exact local inputs named in its
[input manifest](../groups/anatomical-landmarks/experiments/br040/inputs.json).
Source locators explain provenance; the CLI does not search old directories as a
fallback or download missing data.

```sh
uv run med prepare anatomical-landmarks-br040 --case ct-partial
uv run med prepare anatomical-landmarks-br040 --case ct-partial --execute
uv run med replay anatomical-landmarks-br040 --case ct-partial
```

`prepare` previews unless `--execute` is supplied. `replay` rescores saved answers
and appends a scoring observation for the same attempt, including its comparison
criterion. It writes a receipt; it is not a new execution. The
[native implementation closeout](migration/native-closeout.md) records exact
agreement for six retained CT/MRI outputs. That proof covers saved-output scoring,
not fresh Docker execution or repeatable model behavior.

For a native-plane review image, install the optional imaging dependencies:

```sh
uv sync --locked --extra imaging
.venv/bin/med view anatomical-landmarks-br040 --case ct-partial
```

Use [exports and submission](submission.md) to build and verify the standalone
MRI replay package. Other historical methods remain source evidence under
`probes/` and their linked protocols. Their old authoring runners are not supported
daily commands; importing some of them can mutate artifacts.

## Portable stories and local tours

```sh
uv run med present
uv run med present --serve
uv run med check --assets
```

`present` writes the portable index to `.local/site/`; `--serve` starts a local
server at `http://127.0.0.1:8765`. It does not publish. Group stories and retained
figures work without raw scans. The index includes the Task Explorer, with a
return link to the workbench. `med brief build` still creates an independent
single-file Explorer. Selected small text sources can be inspected within its
Sources panel; omitted local inputs remain explicitly unavailable. Retained
preview images carry their own source notices and usage restrictions.

Index filters and the selected record are retained in the URL. Chapter navigation
opens the rendered chapters, including heading fragments. `check --assets` additionally verifies selected
figure extraction inputs when those are available.

For presentation changes, use the optional browser regression command after
setting up the declared Node/Playwright dependencies in the [media guide](../presentation/tours/TOOL.md):

```sh
make presentation-check
# With Playwright's bundled Chromium instead of installed Chrome:
PLAYWRIGHT_CHANNEL=chromium make presentation-check
```

This builds a fresh portable view under `.local/presentation-check/` and checks
chapter links, source navigation, URL history, keyboard focus, mobile layout and
tour selection ordering. It needs no scans, inference or media rendering. Missing
optional previews are tested as explicit unavailable states. The separate
presentation CI workflow provisions its declared browser and runs the same checks
for changes to presentation inputs; the ordinary `make check` remains Python-only.

For guided tours, first restore the exact derived inputs in
[presentation/tours/inputs.json](../presentation/tours/inputs.json), then run:

```sh
uv run med media prepare
uv run med media check
uv run med present --serve --local-media
```

This restores and checks the retained derived snapshot, not every original raw
scan preprocessing step. Missing inputs produce an operation-specific error.
After installing the imaging extra, `.venv/bin/med media optimize` generates
lossless player assets. Optional still/video rendering uses the separately declared
Node/Playwright setup, with FFmpeg for video, in the
[media guide](../presentation/tours/TOOL.md). No personal dependency cache is required.

## Recovery boundaries

Historical files may refer to `site/`, `site_med/`, `catalog/` or retired scripts.
Use [archive recovery](../archive/README.md) to inspect their original context;
use the commands above for the current presentation. Do not run an old generator
to repair a historical link.

Raw runs, environments and generated media remain local. Missing input files,
mutable historical Docker tags, dataset access/licensing and independent backup
are separate recovery concerns. A successful file restore or saved-output replay
does not establish clinical validity or submission readiness.
