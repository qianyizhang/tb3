# Proposal: migrate the workshop to tb3-medical

Status: investigation and proposed decisions, 2026-09-20. No migration executed.
Working assumptions: a medical research workbench with a presentation layer,
retaining this repository's Git history. These are recommendations, not recorded
user selections. This document does not supersede current artifact ownership.

## Recommendation

Make **semantic task groups the unit of ownership**, **experiments the unit of
comparison**, and **attempts the unit of execution evidence**. Keep chronological
round IDs as provenance. Each group should bring together its question, lessons,
data selection, reusable task construction, instructions, evaluator, and visual
review. A common index should make every existing result discoverable through
that structure.

Simplify aggressively: retire non-medical research from the active tree, remove
obsolete generators and duplicate navigation, and replace copied run/collect
scripts with a small common orchestration layer for future experiments. Preserve
historical inputs and outcomes without keeping every historical interface alive.

Use a staged restructure of the current repository. A permanent metadata overlay
would leave most duplication intact; a fresh repository would add evidence and
history transfer work before improving the workflow. An overlay is useful only
as the first migration step. A clean medical-only export can be added later if
distribution size becomes a separate objective.

## What the inspection found

The [inventory](tb3-medical-inventory.json) records the counted paths and method.
Baseline HEAD: `70aaea059f3463fc3193cd83f1ec3fd8a4d5166f`, branch `main`.
Untracked BR-041–043 work was inspected for context but excluded from tracked
file totals. It remains under its existing owners; files changed during this
survey, so the migration must refresh its inventory before making changes.

| Observation | Migration implication |
| --- | --- |
| 2,784 tracked files, about 148.1 MiB of working-file content; 1,862 files under `probes/` | Directory organization and retained task fixtures dominate the tree. |
| 20 clearly non-medical probe roots contain 1,056 tracked files, about 24.6 MiB | Retiring these alone removes about 38% of tracked file entries. This excludes mixed revision folders and associated documents. |
| 168 catalog ideas, 151 trial imports, 16 review records; newest imported trial started September 15 | The catalog is useful infrastructure but does not cover the later medical studies as a current experiment index. |
| 101 of those 151 trial imports belong to the 20 non-medical roots | A default medical view should not inherit the old catalog's center of gravity. Keep excluded outcomes recoverable. |
| Six medical Markdown chapters, six source-linked cards, six guided tours | Reuse these as the presentation foundation. Longitudinal reading and recent coronary work need corresponding coverage. |
| `BR-025` identifies both cardiac reconstruction and vessel curation | Round IDs are aliases, not globally unique experiment keys. |
| `scripts/tb3.py` plans the original submission matrix; actual recent trials use bespoke scripts | A generic runner exists only in part. Future orchestration must account for the real run/collect/review workflow. |
| `scripts/check_site_med.py` hardcodes six chapters/cards; current Pages workflow publishes only `site/index.html` | Adding a group currently requires editing presentation infrastructure; the publication entry point is stale for the pivot. |
| Medical figure export reads `site/*-figures.json`, provenance, and `site_med/data/segmentation_assets.js` | The old presentation contains live medical dependencies. It cannot be archived wholesale yet. |
| About 41 GiB in ignored `runs/`, 2.2 GiB in `.cache/`, 199 MiB in `.git` | Active-tree cleanup and disk reclamation are separate operations. Git does not preserve ignored trial evidence. |

The counts are a local snapshot, not a content-validity audit. In particular,
rounds, cases, conditions, controls, attempts, and clinical judgments are different
denominators. The new index should expose them separately.

Relevant current authorities: [governance](../governance.md),
[catalog contract](../catalog.md), [medical content contract](../../site_med/README.md),
[editorial decisions](../../site_med/editorial/README.md),
[round chronology](../research-rounds.md), and
[submission boundary](../submission.md).

## Refine the proposed direction

1. **Trackability before file movement.** Build a complete inventory and identity
   map first. Moving folders alone will not connect a model attempt to its exact
   input condition, scorer, later diagnosis, and presentation.
2. **Group by reusable task question.** Use modality, organ, dataset, and clinical
   context as tags. These are useful browsing axes but poor exclusive ownership
   boundaries: registration spans modalities; one CT source serves several tasks.
3. **Archive whole historical dependency sets.** Non-medical code, related tests,
   catalog records, docs, licenses, and required fixtures travel together. Split
   mixed records by reference, preserving originals; do not use a BR-number cutoff.
4. **Remove interfaces more aggressively than evidence.** Old launchers, duplicate
   generators, abandoned scaffolds, and stale navigation have ongoing maintenance
   cost. Frozen bytes and concise negative results retain research value even when
   their task is retired.
5. **Author insights; generate indexes and measurements.** A results table can be
   generated. Explaining what changed our understanding requires an authored
   synthesis with explicit links to supporting and contradicting evidence.

## Proposed semantic groups

Start with seven groups backed by existing work. Do not create empty groups for
every BR-043 proposal. Each experiment has one primary owner and optional tags
or cross-links into other groups.

| Group | Existing material to organize | Shared methods and presentation |
| --- | --- | --- |
| `anatomy-audit` | Medical portions of BR-003/004; BR-010–015/017; DICOM label/anatomy probes | Label identity, omissions and ownership, matched mask contrasts, native CT overlay, scope comparison |
| `lesion-localization` | BR-016 aneurysm work | Lesion/source-region truth, negative cases, detection versus localization, point/mask overlays and native slice tours |
| `registration` | BR-019–024/028; three registration probe families | Coordinate/transform contract, frozen correspondence metrics, image-context contrasts, paired slice/volume inspection |
| `tubular-anatomy` | Vessel BR-025/026/030/033/041/042; vessel, airway and brain-routing probes | Connectivity, path geometry, branch identity and completeness; CPR and native image overlays. Keep distinct coronary/airway/brain protocols. |
| `cardiac-motion` | Cardiac BR-025/027/029/031/032/034/035 | Geometry, cavity function, material motion and input-condition contrasts; time-series and moving-surface review |
| `anatomical-landmarks` | BR-036/038–040 | Native voxel/world mapping, identity versus spatial error, out-of-field targets, point review and coverage plots |
| `longitudinal-reading` | BR-037; BR-018 as a parked source-design reference | Visit/sequence assembly, evidence citations, reproducible measurement, qualitative review and paired-visit inspection |

The group boundary should follow what can actually share preparation, scoring
and review. Split tubular anatomy later if its adapters become substantially
different; do not prematurely build a universal vascular/airway evaluator.
Likewise, retain synthetic cardiac material truth and clinical cavity references
as distinct experiment conditions within the same group.

### Target layout

This is the destination, not a request to move frozen trees immediately.

```text
README.md                         # tb3-medical purpose and three entry paths
AGENTS.md                         # small repo-wide working contract
groups/
  tubular-anatomy/
    group.json                    # identity, question, tags, entry points
    README.md                     # accumulated findings, contrasts, limitations
    AGENTS.md                     # authoring/review instructions for this group
    sources.json                  # selected source/sample references and rationale
    methods/                      # reusable preparation, scoring and baselines
    views/                        # domain-specific review adapters
    examples/                     # small licensed or synthetic examples
    experiments/
      coronary-image-only/
        experiment.json           # identity, conditions, protocols, artifact refs
        protocol.md
        evidence/                 # concise immutable receipts, manifests, reviews
        results.md                # authored interpretation of this experiment
    presentation/
      story.md                    # audience-facing article, authored once
      figures/                    # portable figures and source manifests
      tour.json                   # group story for shared viewer/export tooling
datasets/                         # source/version/terms manifests and fetch recipes
src/tb3_medical/                   # small CLI, adapters, artifact resolver, index
presentation/                     # shared viewer, templates, media export only
tests/                            # common contracts and selected adapter tests
docs/                             # workflow, evidence rules, migration decisions
archive/
  README.md                       # tracked recovery instructions
  manifest.json                   # tracked old-path -> retained-location mapping
  legacy/                         # ignored recovered legacy checkout/payload
runs/                             # ignored execution outputs, existing paths first
.cache/                           # ignored rebuildable material
```

Use validated JSON manifests for continuity with the existing receipts and
standard-library tooling. Small groups can omit unused directories. A new
configuration language is unnecessary for this migration.

The group owns its selected samples, task methods, bespoke instructions and
visual explanations. The dataset registry owns shared source identity and
retrieval facts; large scan bytes remain in local storage. This prevents copying
ImageCAS or VerSe for every experiment while preserving a self-contained group
entry point. Group authoring instructions must not be included automatically in
solver packets: those can contain answers, source identities and review findings.

## A small common evidence model

Use stable IDs that do not depend on the current filesystem location. For
example, `tubular-anatomy/coronary-image-only` can carry legacy alias `BR-041`.
Map vessel and cardiac BR-025 to different IDs with their full original source
paths. Preserve old filenames and aliases in the migration map.

| Record | Required information |
| --- | --- |
| Group | Question, owner/entry points, applicable methods, source references, accumulated findings |
| Experiment | Stable ID, legacy aliases, hypothesis, protocol, case selection, conditions, task/scorer/source revisions, lifecycle state |
| Attempt | Unique ID, experiment + condition + case, model/reasoning/harness, task and scorer digests with algorithm names, start/end, execution health, outputs and metric references |
| Artifact/source reference | Role, digest, original and current locator, availability, derivation, source terms, solver visibility |

Keep protocols, receipts, reviews and source artifacts as authorities; the index
is a projection of them. Do not invent complete normalized metadata for older
runs: use explicit unknowns and source pointers. Importers must retain their
version and source digest and must never overwrite authored review history.

Separate these dimensions:

- **Lifecycle:** proposed, curated, ready, running, reviewed, retired.
- **Execution:** completed, setup error, agent error, timeout, interrupted.
- **Evaluation:** pass/fail per frozen endpoint, mechanical-only, qualitative,
  or unscored; retain the actual metrics and denominators.
- **Interpretation:** reviewed miss, reference ambiguity, scorer defect,
  source-assisted observation, diagnostic correction, pending adjudication.
- **Availability:** portable, restorable, local-only, missing, or access-blocked.

A timeout can have useful saved output without becoming a completed model result.
An author correction is a derived diagnostic artifact, not a successful model
attempt. BR-037's mechanical checks cannot become a clinical pass rate. Reuse
the existing catalog's careful classification and allowlisting behavior while
adding adapters for medical result receipts and linking raw Harbor attempts.

Avoid double-counting the same attempt imported from a Harbor result and a
round receipt. Preserve original attempt IDs where available; record explicit
cross-source identity mappings otherwise. Each authorized setup recovery gets a
new execution ID and a `recovery_of` link. Repeated evaluations of one saved
output are evaluations, not additional model attempts.

## Future orchestration

Build a thin CLI around existing preparation/scoring/review adapters. Keep Harbor
as an execution adapter where appropriate. No scheduler, hosted database or
experiment service is needed for the first migration.

Illustrative command contract; these commands do not exist yet:

```text
med list / med show <experiment>
med new <group> <experiment>
med doctor <experiment>
med prepare <experiment> <condition>
med validate <experiment> <condition>
med freeze <experiment> <condition>
med plan <experiment>                 # exact runs, resources, inputs, destinations
med run <plan>                       # explicit execution, matched control gates
med collect <attempt>                # idempotent import, all outcomes retained
med review <attempt>                 # opens output, truth and independent diagnostics
med present <group>                  # portable story, tables, figures and tour
```

The common layer should own identity, artifact resolution, freeze checks, control
gates, attempt allocation, process receipts, failure classification and reporting.
The group adapter should own medical preparation, its endpoint definitions and
its view. Start with the repeated patterns demonstrated by BR-041/042, rather
than designing a generalized pipeline language.

Use an exclusive per-experiment run lock and unique output directories. A crash
or retry must never overwrite an existing attempt or silently spend another model
attempt. Record planned and realized configuration, including assistance and
information supplied. Re-check frozen bytes before and after execution. A model
run is explicit; listing, checking, collecting and presenting never launches one.

Preparation should distinguish data retrieval, deterministic derived-data build,
task assembly and freeze. Future public-input packaging should resolve only
declared solver-visible artifacts; references and review overlays stay evaluator-
only. Old experiment scripts are not executed merely to discover their metadata:
some perform writes at import/module scope.

Keep shared lightweight check dependencies separate from medical geometry,
inference, Harbor, and media-export environments. Record reproducible dependency
profiles for new work and the old environment receipts for replay. Do not merge
all `.venv-*` requirements into one large environment or remove old environments
until their recovery requirements have been assessed.

## Presentation and accumulated insight

Each group should answer five questions: what capability is being tested, what
the agent receives, which contrasts have been tried, what the evidence supports,
and what remains uncertain. Its experiment table should include unsuccessful
curation and retired ideas, with details collapsed by default.

Use two reading depths: a 3–5 minute capability story, then protocols, attempts,
traces and reproduction. Keep a group-level findings table with the claim,
supporting experiments, counterexamples and limitations. Generate numeric tables
from source-linked measurements; author the synthesis. Across groups, offer
filters for anatomy, modality, dataset, assistance, model and evaluation status.

Use `site_med`'s corrected Markdown/cards/tours as the migration source. Move
them into group ownership, with a shared rendering/export layer. Preserve static
fallbacks, caption, alt text, attribution, coordinate conventions, model exposure
and source hashes. Keep the portable content export suitable for the previously
chosen Astro destination; an Astro rebuild is not a prerequisite for the pivot.

Extract figure/provenance inputs from `site/` before retiring its HTML shell.
Update exporters to consume canonical group assets, then prove the derived bytes
and measurements match. Replace hardcoded six-chapter discovery with manifest
discovery. Defer any remote publication or repository rename until local links,
the new entry point and retained legacy links have been checked.

## Keep, archive, deprecate, remove

| Material | Proposed treatment |
| --- | --- |
| Medical protocols, results, concise reviews and source records | Keep; assign group ownership. Preserve failures and task-validity caveats. |
| Frozen medical task inputs, scorers, necessary fixtures/licenses | Keep exact bytes or a verified restorable package with an explicit availability level. Keep what the supported clean-checkout path requires in Git. |
| Current medical Markdown, cards, scientific figures and tour source | Consolidate under groups and shared presentation. Retain hashes and attribution. |
| Catalog importer, review invalidation and evidence allowlist logic | Reuse in common core; import historical records through explicit adapters. |
| 20 non-medical probe roots in the inventory | Archive with their dependent records, tests, locks and fixtures; remove from active tracking after recovery is verified. |
| `probes/revisions/br005`, `br007` and mixed early rounds/ledgers/catalog | Classify at file/record level. BR-003 includes both medical and non-medical work. Preserve complete historical originals. |
| `tests/test_clipper_geometry.py`, `tests/test_homology_verifier.py` | Move with the retired task families; stop running them in medical CI. |
| Original assignment, hard-task search docs, submission-matrix planner | Archive as interview/submission history after extracting reusable utilities. Keep a short pointer to the separately owned submission repository. |
| `scripts/build_site_med.py` and unused legacy CSS/JS/navigation | Retire. It embeds superseded prose and is explicitly outside current medical content validation. Check consumers before deleting shared assets. |
| `site/` shell, old builders/launchers and related tests | Deprecate after medical assets/native viewing functions have replacements. Preserve the original interview publication in the legacy snapshot. |
| Copied per-model `run_*`, `collect_*`, plotting scripts | Keep historical versions recoverable; stop cloning them for new experiments. Replace active use with group adapters and declarative model conditions. |
| BR-018 unfinished standalone scaffolding | Park its useful source notes under longitudinal reading; archive unused code unless a concrete future experiment needs it. |
| Superseded generated indexes, duplicate manifests, unused active helper code | Remove after reference checks; recoverable Git history is enough for ordinary obsolete tooling. |
| Ignored raw runs, downloaded references and existing local environments | Inventory and preserve separately. They are not part of the non-medical untracking operation. |

Avoid two permanent catalogs, two active article trees, or two runnable entry
points for one supported workflow. A compatibility shim needs a named consumer
and a removal milestone. Historical snapshots do not require perpetual modern
runtime support; their reproducibility level must be stated honestly.

## Archiving without losing the record

Recommended interpretation of “archive + gitignore + untrack”:

1. After active owners finish or identify a stable handoff, record the pre-pivot
   commit, intended archive paths, dirty/untracked exclusions and relevant local
   dependencies. Do not include unrelated unfinished work in a migration commit.
2. Preserve a named Git snapshot and verified Git bundle for tracked history.
   Separately inventory and back up required ignored/untracked evidence. A tag or
   bundle cannot recover bytes Git never stored.
3. Keep a small tracked `archive/README.md` and `archive/manifest.json`: original
   path, digest, reason, archive snapshot/location, dependency group, recovery
   recipe and supported reproduction level. Store recovered legacy payload under
   ignored `archive/legacy/` or in a sibling legacy checkout. A same-disk copy is
   convenient recovery, not a durable backup.
4. Resolve all dependencies of the supported medical tree first. Preserve original
   hash-bound receipts unchanged; use an external old-path-to-artifact resolver
   and record the relocation. Updating a presentation link is different from
   rewriting a historical freeze or changing an old review's evidence digest.
5. Review an exact untracking manifest and perform one scoped removal from the
   index. If files have already been copied to the ignored archive, stage their
   removal at the original paths. If keeping files in place, `git rm --cached`
   removes only tracking. Do not use a blanket `git rm --cached .` or blanket
   ignores for `docs/`, `probes/`, evidence JSON, or archives generally.
6. Validate a clean checkout without ignored content. Separately restore one
   complete legacy dependency set from its recorded source and verify hashes.

`.gitignore` does not affect files already tracked. Removing files from the index
does not erase their old commits or shrink full Git history. That matches the
recommended active-tree cleanup. A smaller history would be a separate export
or history-rewrite decision. See [Git ignore documentation](https://git-scm.com/docs/gitignore),
[index-only removal](https://git-scm.com/docs/git-rm), and
[bundle creation/verification](https://git-scm.com/docs/git-bundle).

For medical relocations, check the actual hash domain. The current runner hashes
paths relative to the task root plus their bytes, but receipts and launchers may
record repository paths. Moving a task root can preserve its content hash while
breaking those consumers. Internal path changes can change the task hash itself.
Do not “refresh” a historical freeze to accommodate a reorganization.

## Migration sequence and completion gates

| Phase | Deliverable and owned surface | Completion gate |
| --- | --- | --- |
| 0. Baseline and disposition | Inventory, archive/recovery manifest, experiment identity map, active-owner handoff | Every proposed removal has a disposition and dependency owner; BR-025 collision is resolved without altering historical IDs; required local evidence has a recovery plan. |
| 1. Prove one group | Add group/experiment manifests and common list/show/collect/present contracts for one representative family; use existing frozen outputs | One entry point reaches protocol, conditions, attempts, metrics, interpretation and visual review. Imported rows reconcile with retained receipts; no model run is required. |
| 2. Consolidate medical groups | Backfill all seven groups, dataset references, minimal common core, authoritative stories and shared assets | Every retained medical experiment has exactly one primary group; lifecycle and availability are explicit; six existing chapter measurements/figures remain traceable. |
| 3. Retire old surfaces | Remove superseded generators/navigation, retire non-medical families and their tests, update artifact policy and docs | No supported check, viewer or active claim depends on removed paths. Recovery drill passes. Current CI is medical/common-tooling only. |
| 4. New-experiment workflow | Implement reusable prepare/validate/freeze/plan/run/collect/review adapters and scaffolding | A small synthetic/offline fixture exercises planning, control gating, attempt identity, failed/interrupted execution and import. No paid trial is required to validate orchestration. |
| 5. Identity and distribution | Change repository title/README, optional directory/remote rename, new presentation entry point and publication configuration | Clean checkout opens the medical index and static stories; remote/base-path assumptions are checked; old history remains reachable. Publish only as a separate intended action. |

For Phase 1, use **BR-030/041/042 in tubular anatomy after their owners hand off**:
it exercises revisions, multiple model settings, setup exclusions, timeout output,
diagnostic corrections and several viewers. If that work remains active, use the
settled BR-036/038–040 landmark family instead. Do not migrate the active writer's
paths just to finish the pilot.

The priority is delivering a usable vertical slice, then backfilling, then
removing old infrastructure. Bound the transitional overlay to Phases 1–2;
the migration is incomplete if the old structure is still required for normal
new work after the final phase.

Required checks during implementation:

- Exact before/after digests for retained frozen tasks and evidence, preserving
  each digest algorithm's meaning; no overwritten historical attempts.
- Reconcile attempt counts, model settings, conditions and endpoint values
  between old receipts and new indexes. Account explicitly for omissions and
  unsupported legacy formats.
- Clean-checkout portable checks and missing-data behavior; offline replay of
  representative saved outputs when inputs are available. Missing runtime data
  must remain an availability limitation, not a new model result.
- One real interaction check for native slice/CPR/landmark viewing and media
  export after moving those tools, including coordinates and source overlays.
- Stage only intended paths, then run Python 3.12 `make check` with the updated
  artifact policy; validate the staged tree in isolation. Do not use user-owned
  dirty files to make a supposedly portable checkout pass.

Root guidance must be rewritten as part of the pivot: distinguish the closed
interview investigation from ongoing authorized medical work. Keep the frozen-
evidence and no-security boundaries, preserve the separate submission ownership,
and remove the original assignment's qualification matrix as the default gate
for exploratory medical experiments. Historical next steps stay historical.

## Decisions to lock before implementation

Recommended defaults are a research workbench plus showcase, current Git history,
seven initial groups, and portable group-owned content with an Astro-compatible
export. The async preference questions cover the two highest-impact choices:
workbench versus benchmark/showcase emphasis, and current history versus a fresh
medical repository. No answer is treated as approval to execute this plan.

An initial implementation slice should establish the identity map, one complete
group, the archive manifest/recovery path, and a new medical root guide. Defer
mass untracking until that slice proves the new organization works. Keep the
GitHub rename, any publication switch and local raw-data deletion outside that
initial slice.

## Investigation validation

`make check PYTHON=python3.12` passed on the existing checkout: 73 offline tests,
the existing Git-index artifact gate (2,784 files), and medical content checks
covering 153 source values and 17 assets. The content check deferred 12 local
media/evidence links; legacy HTML is explicitly excluded. These are baseline
results, not validation of an implemented migration.

Only this proposal and its inventory were added. No existing experiment files,
Git tracking, frozen bytes, remote settings, or submission workspace were changed.
The investigation did not launch trials, rebuild scans, or revalidate dataset
access and terms.
