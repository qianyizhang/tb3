# Design record: migration to tb3-medical

Implementation began after explicit authorization on 2026-09-20. The
[first-pass closeout](status.md) records the initial foundation; the later
[native implementation closeout](native-closeout.md) records the installed workflow.
See the [migration index](README.md) for their order and remaining integration boundary. The investigation narrative below
is retained as the decision record; its baseline counts and future tense are historical.

Status: seven design decisions locked through the user interview on 2026-09-20;
see the decision record below. No migration executed. Direction: a medical
research workbench with a presentation layer, retaining this repository's Git
history. This document does not supersede current artifact ownership or authorize
new model trials.

## Recommendation

Make **semantic task groups the unit of ownership**, **experiments the unit of
comparison**, and **attempts the unit of execution evidence**. Keep chronological
round IDs as provenance. Each group should bring together its question, lessons,
data selection, reusable task construction, instructions, evaluator, and visual
review. A common index should make every existing result discoverable through
that structure.

Support the full path from recurring discussion to a clean deliverable:
**idea and decision → experiment → attempt → evaluation → finding → export**.
Later discoveries can revise the validity of evaluations and findings without
rewriting what actually ran. Ideas need not become experiments, and useful
experiments need not become submissions.

The active research objective is learning about medical agent capabilities.
Informative successes, exploratory visualizations and carefully qualified studies
without a reliable pass/fail endpoint belong here. Benchmark-backed failures are
a useful source of ideas, not an admission requirement for every experiment.
Apply difficulty and submission qualification gates when promoting a task toward
that purpose.

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
    ideas/                        # concise durable cards and decision history
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
        reviews/                  # scoped issues, evaluations and finding revisions
    presentation/
      story.md                    # audience-facing article, authored once
      figures/                    # portable figures and source manifests
      tour.json                   # group story for shared viewer/export tooling
datasets/                         # source/version/terms manifests and fetch recipes
discussions/                      # concise cross-group discussion capture and links
exports/                          # tracked selection recipes and package manifests
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

## Recurring discussions and a decision backlog

The user-provided example is
[Propose next medical tasks](codex://threads/01a0bde4-e30d-71c3-8ae4-19d377aee51d).
Its initial request produced six candidates in
[BR-043](../research-rounds/BR-043-medical-next-tasks.md); the next request asked
for real data or symbolic visuals explaining inputs, expected outputs and
difficulty. At inspection, the visual follow-up was still in progress. Treat
that as an ongoing discussion, not six approved experiments or finished visuals.

Capture one concise discussion note linking the source task/turns and affected
idea IDs. Maintain one durable card per idea across later discussions; do not
create a new candidate merely because the conversation restarted. Cross-group
ideas have one primary owner plus tags. IDs survive moves or changes in title.
Capture is automatic at substantive milestones: a useful researched finding,
explanation, decision or blocker. Passing suggestions do not each become cards.

Each card needs:

- **Question and task:** input, expected output, conceptual challenge and intended
  scoring approach, in a few sentences.
- **What is already known:** relevant local experiments, sources checked with
  dates, findings, access/reference gaps, and links to reusable visual explanations.
- **Current disposition:** exploring, selected, parked, rejected, superseded or
  promoted; a reason and the next action or specific condition for reopening.
- **Decision history:** dated decision, rationale, who made it, source task/turn,
  and what it supersedes. Distinguish an assistant recommendation, user decision,
  and evidence-based review; a shortlist recommendation is not user selection.
- **Relations:** experiments it produced, alternatives/duplicates, and any open
  issue that undermines its premise. Unknown source provenance stays unknown.

Use a short current summary with linked chronological entries, not copied chat
transcripts. Existing `catalog/ideas` becomes this backlog through migration;
it must not remain a second active queue. Backfill only evidenced decisions.
The existing curate operation overwrites current notes/status, so preserving
decision history requires an explicit change, not just a directory move.

On returning to an idea, search titles, aliases, tags and prior decisions first;
surface what was learned, why it stopped, and what would make it worth reopening.
Research only the new question, changed source, stale access fact or unresolved
gap. This avoids repeated source screening without treating old findings as
permanently current. An invalidated supporting finding should flag the idea's
premise for reconsideration rather than silently making it a fresh recommendation.

Retain useful explanations with their card: actual-data versus schematic label,
source/derivation, static fallback and a durable artifact reference. A temporary
conversation visualization path alone is insufficient; migrate or reproducibly
package the selected artifact when its owner finishes. A requested visual can
remain `pending`. Asking for explanation does not select the idea for execution.

For BR-043, the intended capture is one discussion linking six distinct ideas,
their source-access/adjudication blockers, and the requested visual guide. Keep
the current proposals and active visual work under their existing owner's control.

Acceptance: reopening the coronary-identity idea retrieves the previous proposal,
supporting evidence, current reference caveats and explanation without repeating
the full source search. A later park/select decision appends to the same card.

## A small common evidence model

Use stable IDs that do not depend on the current filesystem location. For
example, `tubular-anatomy/coronary-image-only` can carry legacy alias `BR-041`.
Map vessel and cardiac BR-025 to different IDs with their full original source
paths. Preserve old filenames and aliases in the migration map.

| Record | Required information |
| --- | --- |
| Group | Question, owner/entry points, applicable methods, source references, accumulated findings |
| Idea / decision | Stable idea ID, concise question, researched facts, current disposition, rationale, source discussion, dated decisions and reopening conditions |
| Experiment | Stable ID, legacy aliases, hypothesis, protocol, case selection, conditions, task/scorer/source revisions, lifecycle state |
| Attempt | Unique ID, experiment + condition + case, model/reasoning/harness, task and scorer digests with algorithm names, start/end, execution health, outputs and metric references |
| Evaluation / finding / issue | Exact output and evaluator/reference versions, endpoint values, scoped validity judgment, supporting dependencies, issue/review history and superseding records |
| Artifact/source reference | Role, digest, original and current locator, availability, derivation, source terms, solver visibility |
| Export recipe / manifest | Selected revisions and dependency closure, target profile/version, source-to-package mapping, transformations, checks, qualification gaps and source-validity snapshot |

Keep protocols, receipts, reviews and source artifacts as authorities; the index
is a projection of them. Do not invent complete normalized metadata for older
runs: use explicit unknowns and source pointers. Importers must retain their
version and source digest and must never overwrite authored review history.

Separate these dimensions:

- **Lifecycle:** proposed, curated, ready, running, reviewed, retired.
- **Execution:** completed, setup error, agent error, timeout, interrupted.
- **Progress:** planned versus started attempts; expected versus observed cases,
  conditions and outputs. No result file does not prove an attempt never started.
- **Evaluation:** pass/fail per frozen endpoint, mechanical-only, qualitative,
  or unscored; retain the actual metrics and denominators.
- **Interpretation:** reviewed miss, reference ambiguity, scorer defect,
  source-assisted observation, diagnostic correction, pending adjudication.
- **Availability:** portable, restorable, local-only, missing, or access-blocked.
- **Validity:** unreviewed, supported, under review, qualified, invalidated or
  superseded, scoped to the affected endpoint/finding. This can change after
  execution without changing the execution record.

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

These are small files and explicit ID references, not a requirement for a workflow
service or graph database. Historical observations stay immutable; lightweight
review entries explain changes to the current view.

## Incomplete work, defects and conclusion revision

`need-fix` should be a computed work-queue label tied to an open issue, not an
alternative to “completed” or a replacement for the original result. An experiment
can have completed attempts, incomplete conditions, and an invalidated conclusion
at the same time. An idea can be parked while its premise needs correction.

Track the planned matrix and actual attempts independently. Include started runs
without `result.json`, interrupted collection, missing outputs and unfinished
reviews. Record the last known stage and artifact completeness; do not equate a
quiet job with failure while another owner may still be writing. Partial outputs
can receive clearly marked diagnostic evaluations. Completing collection from a
finished run is different from restarting a model. A resumed execution records
its prior state and continuity; it is not an independent fresh repetition.

The current catalog detects stale reviews when source hashes or classifications
change. It cannot detect a newly discovered logical flaw in unchanged source
bytes. Add an explicit issue/review path:

1. **Record the issue:** defect or uncertainty, evidence, affected source/task/
   scorer/output versions and cases/endpoints, discovery time, owner, required
   repair, and whether the impact is suspected or confirmed.
2. **Mark dependent findings:** suspected impact becomes `under review`; confirmed
   impact qualifies or invalidates the affected claim. Unaffected endpoints keep
   their support. Keep the original numerical score labeled with its evaluator.
3. **Propagate by references:** flag dependent group summaries, idea rationales,
   article claims, comparison tables and exports. Current summary/qualification
   counts exclude unresolved or invalidated evidence for the affected endpoint
   and show those exclusions and denominators explicitly; historical rows remain
   inspectable. Old publication snapshots retain a linked correction notice.
4. **Repair as a new revision:** preserve old task/reference/scorer bytes. If only
   the scorer was wrong, reevaluate the same saved output with a new evaluator
   revision; that is not a new model attempt. If the delivered input or task
   contract was faulty, create a corrected task revision and mark any required
   fresh trials as pending. Do not silently relabel an old attempt as that task.
5. **Re-adjudicate:** retain original and revised evaluations, control/replay
   evidence and the reviewer decision. Fixing code or closing the issue does not
   automatically restore a finding. Reinstatement needs an explicit review that
   also accounts for other unresolved dependencies.

Agents may invalidate claims affected by reproducibly demonstrated technical
defects without waiting for a separate user verdict; record the reproducer,
scope and visible correction. Anatomical or reference disputes become `under
review` and require appropriate adjudication. The user is not treated as the
default clinical adjudicator. Reinstatement also needs an explicit evidence-
backed review, which may be agent-authored for a technically verifiable repair.

A small findings record needs a stable claim ID, scope, supporting evaluation or
artifact IDs, current validity and review references. Track consequential numeric
or interpretive claims, not every prose sentence. Record dependency versions so
semantic invalidation works even when no file hash changes. New exports must
refresh this view; an existing immutable export can be flagged as withdrawn or
superseded by a separate notice without rewriting its files.

The [BR-033 scope audit](../evidence/br033-scope-audit.json) is a concrete migration
example: two airway controls passed their narrow endpoint checks but remained
detached from parent trees. Preserve those passes while withdrawing any claim
that they establish whole-tree repair. Separately, the
[BR-042 branch review](../research-rounds/BR-042-v3-branch-review.md) raises a
reference-identity/convention question; it does not establish that the ground
truth is wrong. The system must support unresolved review as well as confirmed
invalidation.

Acceptance: introduce a simulated scorer defect against saved fixture outputs;
the affected finding disappears from current supported comparisons, dependent
ideas/stories/exports are flagged, unrelated endpoints remain, and the original
run and score remain visible. A corrected replay adds an evaluation without
incrementing the model-attempt count.

## Future orchestration

Build a thin CLI around existing preparation/scoring/review adapters. Keep Harbor
as an execution adapter where appropriate. No scheduler, hosted database or
experiment service is needed for the first migration.

Illustrative command contract; these commands do not exist yet:

```text
med list / med show <experiment>
med ideas search <query>             # prior research, decisions, explanations
med new <group> <experiment>
med doctor <experiment>
med prepare <experiment> <condition>
med validate <experiment> <condition>
med freeze <experiment> <condition>
med plan <experiment>                 # exact runs, resources, inputs, destinations
med run <plan>                       # explicit execution, matched control gates
med collect <attempt>                # idempotent import, all outcomes retained
med review <attempt>                 # opens output, truth and independent diagnostics
med issues / med review-impact       # repair queue and affected findings
med present <group>                  # portable story, tables, figures and tour
med export plan / build / check      # explicit selected clean package
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

## Reproducibility contract

User decision: strive to make experiments reproducible by building on the existing
TB3/Harbor task structure, Dockerfiles and declared artifacts. Use that structure
as the execution contract; add artifact preservation, version recording and replay
checks around it instead of creating another runner framework.

Distinguish what can actually be reproduced:

| Capability | Expected guarantee |
| --- | --- |
| Read | Inspect the protocol, supplied information, observations, reviews and portable figures from a clean checkout. |
| Restore and replay | Recover exact frozen task/reference bytes and saved outputs, run the recorded evaluator, reconcile metrics under its declared comparison rules, and rebuild the supported views. No model call is needed. |
| Rerun | Launch a fresh attempt under the recorded task, harness, model settings, resource limits and assistance policy, subject to provider/model availability. This produces a new attempt, not a guarantee of the previous answer or score. |
| Rebuild preparation | Recreate the packet or derived data from preserved upstream inputs, pinned preparation code and recorded transforms/seeds where applicable. Preserve the original packet even when preparation cannot be repeated exactly. |

For new runnable experiments and historical experiments designated supported,
target restore/replay and rerun readiness by default. Record preparation rebuild
support independently: some inputs are expert annotations or external predictions,
not outputs we can regenerate ourselves. Index all older medical work, backfill
selected useful experiments deeply, and expose explicit reproducibility gaps for
the rest. An exploratory or qualitative study can reproduce its inputs, outputs
and review procedure without claiming an objective clinical score.

There are concrete gaps despite the existing Docker packaging:

- [BR-030 packaging](../../probes/vessel-geometry/authoring/package_task.py)
  assembles its frozen task under ignored `runs/`. Its tracked script does not
  contain the image, prediction, reference or oracle payload it copies.
- [BR-041 preparation](../../probes/vessel-geometry/authoring/br041/prepare.py)
  reads the earlier BR-030 runtime task and geometry. Restoring the finished
  BR-041 packet and rebuilding that packet have different dependency sets.
- [Longitudinal packaging](../../probes/longitudinal-reading/authoring/package.py)
  packages mechanical checks but records separately held grounding. Replaying
  those checks alone does not recreate the scientific review.
- Existing Dockerfiles use a base-image tag and explicit top-level package
  versions. Preserve resolved dependencies, image identity and platform for new
  freezes; a tag alone is mutable. Docker documents digest pinning for a fixed
  base image in its [build guidance](https://docs.docker.com/build/building/best-practices/#pin-base-image-versions).

Each supported experiment needs an artifact manifest covering the frozen task,
evaluator/reference, saved outputs, required review/viewer inputs, preparation
sources when supported, and portable execution configuration. Give each artifact
a role, digest, size, restore location and visibility. Record harness/agent versions,
dependency locks or preserved images, OS/architecture and any relevant accelerator
requirements. Do not archive credentials; document how to supply them separately.
Do not rewrite historical Dockerfiles or hashes to retrofit stronger pinning.

Artifact bundles should restore by manifest rather than by the old laptop's
absolute paths. Reuse shared source bytes by digest where practical. A manifest
or download URL is not a backup: independently recoverable storage and a successful
restore check are required before claiming protection against loss of this machine.
The storage location is configurable; none has been selected or verified by this
planning work, and no upload is implied.

Acceptance is a recovery drill: materialize the supported experiment in a fresh
location without access to the original `runs/` or authoring environments; verify
hashes, run the recorded controls and saved-output evaluation, and rebuild its
designated viewer. Record the checked environment, date, results and any missing
dependencies. Distinguish declared capability from verified capability. Preserve
the original score and comparison rules when numerical portability differences
need investigation. A successful rebuild does not by itself qualify a TB3 task.

## Build clean repositories from research

Make clean packaging an explicit, reproducible export capability. It is separate
from exporting articles to Astro and from archiving the old workbench. Select
experiments, cases, conditions and task revisions by ID; do not copy whichever
files happen to be newest under `runs/`.

A tracked export recipe pins the source commit plus required artifact digests,
target format/upstream revision, selected tasks, included evidence, and any
packaging transformations. Build into a fresh destination and emit a manifest
mapping source artifacts to packaged files, exact hashes, omitted local material,
reproduction steps, checks and remaining qualification work. Never overwrite an
existing hand-maintained submission repository as a rebuild side effect.

During preparation the export is a reproducible generated package. At explicit
handoff it becomes independently owned. Subsequent fixes belong to that repository;
retain lineage and support deliberate backports into the workbench. Do not add
automatic bidirectional synchronization or regenerate over post-handoff edits.

Provide two operations:

- **Exact snapshot export:** assemble the selected frozen inputs and evidence
  without changing their bytes. Resolve required ignored artifacts from recorded
  locations; fail with an explicit missing-artifact list when they cannot be
  restored. Do not launch inference or new model runs to fill gaps implicitly.
- **Adapted submission export:** make required format, dependency or instruction
  changes in a new package revision, recording a source-to-package delta. Old
  trials remain evidence of the original revision. Packaging checks and replay
  can establish specific equivalences, but cannot silently turn old observations
  into qualifying trials on changed task bytes.

Export each selected task with its own complete runnable dependency set: inputs,
environment, verifier, solution, licenses and concise provenance. No imports,
symlinks, absolute paths or runtime reads into the workbench may be needed. Keep
solver-visible inputs separate from evaluator references. Shared authoring code
may generate packages, but each emitted task must have the dependencies required
by the selected target profile. Copy only reviewed portable receipts and selected
outputs; private runtime configuration and full trajectories are not default
submission contents.

Distinguish **package reproducibility**, **evidence validity**, and **submission
qualification**. A draft clean repository can exist while qualification trials
or required human-authored sections are missing; list those gaps in its evaluation
status. A submission-ready designation requires the selected current profile's
gates and no unresolved validity issue affecting its claimed results. A research
snapshot may deliberately include incomplete or invalidated studies, labeled as
such; it cannot advertise them as qualifying evidence.

At actual TB3 export time, inspect and pin the then-applicable upstream format
and requirements. The [requirements record](../requirements.md) is a historical
pin, not proof of current eligibility. [The submission handoff](../submission.md)
defines the existing sibling package's separate ownership; this proposal neither
changes it nor asserts its current qualification status.

Validate the exported tree without the source checkout, ignored run folders or
authoring environments: inspect the file inventory and metadata, run target
static checks, exercise controls/replay where possible, and retain explicit
unrun/blocked gates. New model attempts, remote repository creation and submission
are separate actions, never hidden side effects of package generation.

Acceptance: rebuild a representative medical package from a pinned recipe,
compare deterministic payload hashes, and validate it in isolation. Missing
required data produces an actionable gap; altered task bytes produce a new
revision; a newly invalidated finding flags all recorded exports that depend
on it. The exported repository remains independently usable.

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

The daily interaction is Codex for authoring/orchestration and a searchable,
read-only browser index with rich viewers. Editing cards, changing status and
launching runs through a new web application are outside this design. Interactive
scan/geometry controls remain part of the viewers.

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
| Idea cards, researched source notes, decision histories and useful explanations | Keep under group ownership with source discussion links. Deduplicate recurring discussions by stable idea ID; preserve decisions and reopening conditions. |
| Medical protocols, results, concise reviews and source records | Keep; assign group ownership. Preserve failures and task-validity caveats. |
| Partial runs and later-invalidated results | Preserve their available evidence and scoped review history; flag need-fix work and exclude invalid claims from current supported findings. |
| Frozen medical task inputs, scorers, necessary fixtures/licenses | Keep exact bytes or a verified restorable package with an explicit availability level. Keep what the supported clean-checkout path requires in Git. |
| Current medical Markdown, cards, scientific figures and tour source | Consolidate under groups and shared presentation. Retain hashes and attribution. |
| Catalog importer, review invalidation and evidence allowlist logic | Reuse in common core; import historical records through explicit adapters. |
| Clean-package recipes and retained export manifests | Keep small tracked records. Generated repositories live at explicit destinations, with separate owners and no implicit rebuild over later edits. |
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
| 0. Baseline and disposition | Inventory, archive/recovery manifest, idea/experiment identity map, active-owner handoff | Every proposed removal has a disposition and dependency owner; BR-025 collision is resolved without altering historical IDs; required local evidence and potential package dependencies have recovery plans. |
| 1. Prove one group | Add idea/decision capture, group/experiment manifests, evaluations/findings and common list/show/collect/present contracts; use existing frozen outputs | One entry point reaches prior decisions, protocol, planned/observed attempts, interpretation and visual review. Imported rows reconcile; scoped invalidation is demonstrated without a model run. |
| 2. Consolidate medical groups | Index all historical medical work; deeply backfill selected useful experiments, group backlogs, issue links, stories and shared assets | Every retained idea/experiment has one primary owner; completeness, validity, availability and declared/verified reproducibility are explicit; six existing chapters remain traceable; BR-043 is captured after owner handoff. |
| 3. Retire old surfaces | Remove superseded generators/navigation, retire non-medical families and their tests, update artifact policy and docs | No supported check, viewer or active claim depends on removed paths. Recovery drill passes. Current CI is medical/common-tooling only. |
| 4. New-experiment workflow | Implement reusable prepare/validate/freeze/plan/run/collect/review adapters and scaffolding | A small synthetic/offline fixture exercises planning, control gating, attempt identity, failed/interrupted execution and import. No paid trial is required to validate orchestration. |
| 5. Clean-repository export | Add pinned selection recipes, exact/adapted packaging, manifests and target validation profiles | A representative medical package rebuilds and checks without the workbench; package changes, missing gates and invalidated source claims remain explicit. No existing submission checkout is overwritten. |
| 6. Identity and distribution | Change repository title/README, optional directory/remote rename, new presentation entry point and publication configuration | Clean checkout opens the medical index and static stories; remote/base-path assumptions are checked; old history remains reachable. Publish only as a separate intended action. |

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
- Retrieve an existing idea by a later discussion's wording, preserve separate
  recommendation/user-decision provenance, and surface prior findings and visuals.
- Exercise incomplete collection, scoped invalidation and corrected reevaluation;
  verify dependent stories, ideas and exports become flagged while original
  records and unaffected endpoints remain intact.
- Build a pinned export in isolation and verify complete task dependencies,
  source-to-package mappings, no overwritten destination, and explicit remaining
  qualification gates. Validate a missing-artifact path as well as the happy path.
- Clean-checkout portable checks and missing-data behavior; offline replay of
  representative saved outputs when inputs are available. Missing runtime data
  must remain an availability limitation, not a new model result.
- A recovery drill for each experiment promoted to supported status: restore its
  required artifacts outside the original runtime tree, replay scores/controls
  and rebuild designated views. Record gaps instead of inferring reproducibility
  from the presence of Dockerfiles alone.
- One real interaction check for native slice/CPR/landmark viewing and media
  export after moving those tools, including coordinates and source overlays.
- Stage only intended paths, then run Python 3.12 `make check` with the updated
  artifact policy; validate the staged tree in isolation. Do not use user-owned
  dirty files to make a supposedly portable checkout pass.

Root guidance must be rewritten as part of the pivot: distinguish the closed
interview investigation from ongoing authorized medical work. Keep the frozen-
evidence and no-security boundaries, preserve the separate submission ownership,
and remove both the original assignment's qualification matrix and the failure-
backed-only admission rule as default gates for exploratory medical experiments.
Historical next steps stay historical.

## Agreed direction and first implementation scope

The user endorsed the plan and then answered the seven-question decision interview.
These choices are locked; do not request the same decisions again absent a new
material conflict. Article export and runnable task export are separate capabilities.

| Decision | User answer | Locked consequence |
| --- | --- | --- |
| D01 Research admission | Recommendation accepted | Capability learning is primary; retain informative successes and qualified exploratory work. TB3 difficulty/qualification gates apply to submission promotion. |
| D02 Discussion capture | Recommendation accepted | Automatically capture substantive findings, explanations, decisions and blockers in concise durable cards; distinguish recommendations from user decisions. |
| D03 Daily interface | Recommendation accepted | Codex authoring/orchestration plus a searchable read-only browser index and rich viewers; no editing web application. |
| D04 Historical depth | Recommendation accepted | Index all medical work; fully normalize and support replay for selected useful experiments. Preserve explicit limits on historical coverage. |
| D05 Reproducibility | Yes; strive for reproducible experiments using the TB3-backed setup | Build on task specs, Dockerfiles and artifacts. Add recoverable frozen payloads, dependency/runtime records and recovery/replay checks; fresh model attempts need not reproduce an identical answer. |
| D06 Validity authority | Recommendation accepted | Agents can invalidate reproduced technical defects with evidence and visible corrections; clinical/reference disputes require appropriate adjudication. Reinstatement needs explicit evidence-backed review. |
| D07 Export ownership | Recommendation accepted | Generated/rebuildable during preparation; independently maintained after explicit handoff, with lineage and deliberate backports rather than automatic two-way synchronization. |

The interview is complete. Artifact storage destinations and per-experiment
support gaps remain implementation inputs to resolve and verify, not reasons to
reopen these architectural choices. The user's answers settle the design; the
requested pre-implementation interview does not itself start migration.

An initial implementation slice should establish the identity map, one complete
group including its idea/decision backlog and validity reviews, the archive
manifest/recovery path, and a new medical root guide. Defer
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

The requirements refinement read the linked task's completed proposal and ongoing
visual-explanation request. Source turns: `01a0bde4-e489-7be3-b2b9-b9ffeda9ccf8`
and `01a0be05-62a4-7831-aaaa-483355cb178a`. No request was sent to that task and its
files were not edited. BR-043 and the visual guide remain under their existing
owner. The original inventory remains dated survey evidence, not a refreshed
snapshot; newer concurrent experiment revisions are outside its counts.
