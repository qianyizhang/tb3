# Task Brief and Task Explorer — accepted design

Updated 2026-09-21. Source: [current discussion](codex://threads/01a0bef4-b72c-7241-bb59-f5ca11d4db09).
The [rulebook](../presentation/task-explorer/RULEBOOK.md) is the maintained authoring authority; this file records investigation and decisions.

Prior work: [Polish site_med content flow](codex://threads/01a0b406-c06d-7a10-9816-e13087069178).

## Confirmed by the user

- Make samples first to consolidate the representation; eventually allow navigation to **all** tasks.
- Write for a technically literate reader without specialist medical knowledge.
- Cover both existing tasks and new task design; clearly mark draft/proposed material.
- Prioritize task/value, inputs and especially helper artifacts, specification, expected output, useful visuals and concise structure.

## Recommendation

Call one explanation a **Task Brief**, the browsable collection a **Task Explorer**,
and the authoring skill **author-task-brief**. The user accepted these recommendations on 2026-09-21: “all your rec”.
The brief should work before an experiment exists; a results story can follow it.

Use six recurring blocks, with task-specific visual modules:

| Block | Minimum useful content |
| --- | --- |
| Task + value | One concrete action; one sentence on clinical/scientific workflow relevance. |
| Given | Original data; supplied helpers; callable tools; reference-only material. |
| Contract | What must be done, relevant constraints, permitted assistance, success criterion. |
| Deliverable | An output example or shape; files, coordinates and units when consequential. |
| Visual explanation | Input, helper reveal and expected output; a meaningful static fallback. |
| Difficulty + sources | What work remains after help, evidence for that assessment, exact source and known gaps. |

Suggested first-read budget: 60–90 seconds, roughly 150–250 words plus the visual.
Keep exact schemas, longer methods and full evaluation details expandable.
This is an accepted default, with longer detail available separately.

## Investigation findings

Existing group `presentation/card.json` files already contain source-linked task
summaries. Group stories explain results. The shared tour player and media tool
already support bespoke visuals, translations, timing and video export. Reuse
them instead of creating another parallel set of narratives.

The current cards mix task definition and measured results and do not consistently
describe helper artifacts, who can access them, or differences between assistance
conditions. External tasks also need a usable brief without local runs or media.

Three inspected examples make the assistance distinction concrete:

- [ABRA](https://github.com/Luab/ABRA/blob/main/scripts/task_generators/tier3_oracle.py): the oracle condition supplies reference-derived contours through a tool; the ordinary annotation task supplies a slice hint and lung window. Those ask for different amounts of visual interpretation.
- [AutoMedBench](https://github.com/AutoMedBench/AutoMedBench/tree/eval_seg/eval_seg/kidney-seg-task): Lite gives a concrete checkpoint/loading example; Standard gives model-search/comparison guidance. Describe the actual tier material rather than calling either condition unassisted.
- [Imaging-101](https://github.com/AI4ImagingLab/imaging-101-release/blob/main/README.md): L1 supplies README/data/requirements, L2 adds an approach, L3 adds a design. The sparse-CT README also lists full projections and reference data; audit solver-visible staging before claiming all reference material is withheld.

The preview includes one anchor for each of the seven highlighted repositories,
12 selectable conditions across eight entries, and our BR-030 task as an internal
format check. It is not a complete catalogue. External diagrams show workflow,
not anatomical difficulty. The internal retained CPR figure is post-run material.

## Visual contract

- Start with a representative input at enough context to understand the search problem.
- Let readers toggle supplied masks, landmarks, crops, hints, model outputs or plans.
- Make expected output concrete. Distinguish an illustrative output shape, the reference answer and an actual agent prediction.
- Explain why a helper changes the work; do not assign unsupported easy/hard scores.
- For images, preserve orientation and physical proportions. Show where a crop came from when the crop itself supplies localization.
- Reuse actual assets when available; mark diagrams as conceptual. Record source, caption, derivation, attribution and which material the solver saw.
- Source restrictions or unavailable media may leave an explicit gap; a generic workflow diagram does not close a visual-evidence gap.

## Accepted implementation

1. Repository-owned rulebook plus one Markdown template. Reuse the existing card
   for the small amount of metadata the explorer needs; avoid requiring a second
   authored record of the same facts. The preview JSON is provisional content,
   not an adopted schema.
2. A thin reusable skill reads that rulebook, locates task sources and assistance
   conditions, authors the brief and curates the visual. Keep project paths and
   medical specifics out of its reusable core.
3. A shared renderer presents briefs from internal groups and an external survey
   collection. Task-specific viewers remain optional modules.
4. Add complete source inventories per repository. Accepted hierarchy: repository
   → family → definition → assistance condition → case. Display coverage and
   missing cases explicitly. Repeated cases can reuse a common explanation.
5. Extend after reviewing contrasting samples: classification, viewer annotation,
   reconstruction, trained-model workflow and our geometric repair task.

Keep the executable prompt/scorer authoritative. A reader-facing brief can reveal
answers; it must not silently become the solver packet. Proposed tasks can state
unresolved references, scoring and visuals without pretending those are complete.
Use existing vocabulary where applicable, without inventing a new status system.

## Decision record — 2026-09-21

Actor: **user**. Source: current task; response **“all your rec”**.

- One shared brief per definition, with every imported condition/case reachable.
- Input and supplied helpers first; reference/output revealed by explicit reader action.
- Repository rulebook/template plus a reusable `author-task-brief` skill.
- Executable prompts and scorers remain separately authoritative.
- Accepted names and 60–90 second default reading budget.

## Implemented artifacts

- [Canonical rulebook](../presentation/task-explorer/RULEBOOK.md) and [Markdown template](../presentation/task-explorer/brief-template.md).
- [Collection metadata](../presentation/external-tasks/catalog.json), 160 authored Markdown briefs and [source inventory](../presentation/external-tasks/inventory.json).
- `med brief new|build|check` supports proposed-brief scaffolding and standalone HTML output without running experiments.
- [Reusable skill source](../skills/author-task-brief/SKILL.md), installed into the user's Codex skills directory.
- [Internal vessel example](../groups/tubular-anatomy/presentation/briefs/br030.md) now has delivered CT and supplied-helper views, plus a separate post-run output reveal. Local media is source-derived; frozen tasks and outcomes are unchanged.
- Generated HTML: `runs/task-explorer/index.html`. The old preview content/HTML remain historical prototype material.

## Catalogue scope

284 source entries are indexed: 54 HealthAgentBench packages, 8 ABRA families,
9 BCER contracts, 133 AutoMedBench entries, 58 Imaging-101 directories,
2 RadAgent workflows and 20 ReX-MLE challenges. AutoMedBench combines 25 gallery
rows, 13 branch packages, 48 Full-release definitions, 7 packaged Lite definitions
and 40 Lite segmentation case IDs. These overlap and are not additive unique tasks.

All 284 imported entries now link to shared authored briefs. ABRA generated YAMLs
and most externally packaged patient case inventories still need materialization.
Six briefs have native/source-derived visual examples, covering five external
repositories and the internal BR-030 task.

## Sample acquisition — 2026-09-21

Actor: **user** requested a blocker explanation and searching/downloading necessary
samples. Actor: **assistant** selected bounded public examples and reused retained data.

- Downloaded 88.4 MB: Imaging-101 sparse CT arrays, ABRA LIDC CT and annotation,
  one AutoMedBench CT with five reference masks, and three PI-CAI MRI sequences.
- Rechecked and reused 37.3 MB of TopCoW 2024 CT/labels already retained locally.
- Added native input/reference views and a separate AutoMedBench multi-organ brief.
- CT-RATE unauthenticated retrieval returned HTTP 401. This affects the selected
  HealthAgentBench CT example and RadAgent’s CT-RATE data route.
- BCER inputs are a compatible representative case, not a recorded benchmark run;
  ABRA uses one source annotation, not regenerated consensus tasks; ReX-MLE split
  membership is unverified. Exact scope and source terms are in the [receipt](../presentation/external-tasks/samples.json).
- No model trials, runtime installs or publication. Actual outputs require separate
  retained trajectories or authorized runs; dataset downloads alone cannot supply them.

## Validation scope

Offline authoring checks cover source resolution, identities, Markdown-driven
builds, proposed-only scaffolding and preservation of existing files. Browser
checks cover navigation, catalogue selection, deep links, assistance conditions,
input/helper/reference reveals, search and mobile layout. Repository checks do
not certify external references, clinical validity or benchmark reproduction.

## Catalogue readability refactor — 2026-09-21

Actor: **user** flagged repeated “Task at a glance” badges, duplicate task previews
and redundant family/definition/condition/case fields, and requested concise,
meaningful context. Actor: **assistant** implemented the following presentation
choices in response; these are implementation decisions, not a new user vote.

- List each task explanation once. Repeated cases appear beneath their shared
  task; HealthAgentBench therefore has 15 task rows instead of 54 source rows.
- Use Overview, Requirements, optional Example and Sources. Remove the duplicate
  catalogue preview, universal availability badge and summaries that restate titles.
  Keep technical identifiers and source revisions in expandable provenance.
- Show case-specific facts only when sourced. The nine trial-matching manifests
  contain 301–451 candidate trials; Case 29 contains 407. Patient vignettes were
  not retrieved, so case IDs do not acquire invented clinical descriptions.
- Correct the trial-matching scoring explanation from inspected code: passing
  requires full recall among the first 50 predictions; precision/F1 are diagnostic.
  This does not enforce the prompt's stricter requirement to exclude all ineligible trials.
- Preserve all 284 source links, assistance conditions and legacy URLs. Distinguish
  an illustrated case from the selected case when their IDs differ.

Receipts: [context sources](../presentation/external-tasks/catalogue-context-sources.json)
and [refactor validation](../docs/evidence/task-explorer-catalogue-refactor-2026-09-21.json).
Reopen when reader feedback reveals remaining duplication or when actual case
inputs become available to support more useful case differences.

## Task-family audit — 2026-09-21

Actor: **user** requested grouping of repeated HealthAgentBench entries, then
asked for a full audit after noticing the same issue in AutoMedBench.
Actor: **assistant** audited the retained task briefs and consolidated navigation
by shared workflow, with an explicit dataset/target selector.

| Repository | Before | Task entries after audit | Decision |
| --- | ---: | ---: | --- |
| HealthAgentBench | 15 | 7 | Six disease targets share prediction; four error categories share record-quality checking. Three image tasks remain distinct. |
| AutoMedBench | 50 | 10 | Dataset/target variants share classification, detection, segmentation, denoising, super-resolution, CT-volume restoration, MRI-to-CT synthesis, report generation, captioning or visual question answering. |
| ReX-MLE | 19 | 13 | Combine CT/MR variants of the same target, diagnostic/radiotherapy pancreas MRI, and nucleus-label taxonomies. Keep segmentation, localization and connection classification separate. |
| ABRA | 6 | 6 | Viewer state, metadata, perception, annotation, comparison and assessment request different work. Group related entries without merging them. |
| BCER | 9 | 9 | Required tool/stage chains differ. Group single steps, focused workflows and complete workflows. |
| Imaging-101 | 58 | 58 | Different measurement models, reconstruction methods or scientific outputs remain separate; organize by imaging/scientific domain. |
| RadAgent | 2 | 2 | Full reporting and multiple-choice answering have different deliverables. |

This is consolidation of reader-facing task entries, not removal of source tasks
or a claim of identical benchmarks. All 160 authored briefs, 284 source records
and 379 assistance conditions remain reachable. Together with the internal example,
there are 106 task entries. Per-variant outputs, model guidance, metrics and release
scope stay explicit; CT/MR localization adapter differences remain in Sources.

The AutoMedBench audit keeps 3 denoising variants, 4 super-resolution variants and
3 CT-volume-restoration variants in separate task families. Segmentation groups
16 variants without treating an organ mask, separate organ/lesion masks, and a
117-label map as identical contracts. Full, Lite and domain-branch material keep
their release identity. No task packages, frozen evidence or external scores changed.

Validation is retained in [the family audit receipt](../presentation/external-tasks/task-family-audit.json).
Reopen a merge when it hides a meaningful workflow/assistance distinction; retain
exact source links and variant-specific requirements when adding future datasets.

## Visual explanation coverage — 2026-09-21

Actor: **user** requested more visual illustrations and explicitly authorized
original drawings/figurative SVG when real data could not be downloaded.
Actor: **assistant** added pictures directly to Overview: six existing source-derived
examples and 154 conceptual input/output drawings, covering every authored variant.

Drawings use task-specific representations: sampled frequency lines, projection
rays, complex optical fields, slice stacks, spatial masks, bounding boxes, cell
identities, spectral curves, record tables and history cutoffs. Dataset selectors
retain their specific labels and output requirements. Separate organ/lesion masks,
binary targets and multiple-class maps have distinct output sketches. Prediction
shows one probability per test row, not an invented longitudinal risk curve.

The optical-tomography README was reread at its pinned revision: it documents eight
complex-field views and a 308 × 256 × 256 reconstruction volume. A bounded request
for its documented raw NPZ path returned HTTP 404. The schematic uses those source
dimensions but its textures and geometry are original drawings. No new native
sample was acquired in this pass; the other diagrams do not imply that their
upstream datasets are universally unavailable.

Conceptual figures are explicitly marked as drawings, not dataset samples. They
explain structure and requested transformations without reporting a measurement,
model prediction or clinical finding. Native-data coverage remains six briefs.
The [visual coverage receipt](../presentation/external-tasks/illustration-coverage.json)
records scope and validation. Reopen individual drawings when real source samples
become available or when a task contract changes the illustrated output.

## Independent review and cleanup — 2026-09-21

Actor: **user** requested a final independent review, fixes and a focused commit.
Two read-only assistant reviewers separately checked navigation/build behavior and
illustration semantics, then inspected the corrections. Both reported their
identified issues resolved, with no remaining actionable finding in their scope.

- Search-driven selection now updates the URL. Explicit variant changes and
  restored links clear incompatible filters, so the selected task stays visible.
- Native Overview images retain their full authored selection captions. Readers
  can see when reference annotations were used to choose a plane.
- Explicit anatomical subjects replace task-ID guessing. Breast MRI, knee MRI,
  chest CT, tissue and airway drawings now reflect their actual task inputs.
- Aortic segmentation retains a branching binary tree. Spectral snapshot imaging
  shows a wavelength cube; deflectometry shows fringe views and lens parameters.
- SVG geometry lives in its own embedded script. Keyboard tabs and selector focus
  remain usable across detail updates.

The offline browser matrix passes all 160 variants, 284 source records and 379
conditions, including search/history, retained captions, keyboard navigation and
narrow layouts. Four corrected illustrations were visually inspected. Conceptual
coverage remains 154 variants, now using 59 drawing types; native coverage is six.
No trial, runtime installation or publication was part of this maintenance.


## Animated 3D illustrations — 2026-09-22

Actor: **user** requested one animated 3D illustration for each task, replacing the
ordinary Task Explorer infographics, with
[OnCo Technologies](https://onco.cc/technologies/) as the visual reference.
Source task: [Add 3D task illustrations](codex://threads/01a0c88e-4154-7cb1-b869-8f3a70e48397).

Actor: **assistant** implemented original rotating wireframe scenes with three
selectable stages, pause/play, reset and pointer/keyboard camera controls. Every
current authored variant receives a scene through its task-specific illustration
kind and explicit subject/target metadata. Source images remain inspectable with
their original captions; reference answers remain behind the Example reveal.
Reduced-motion and Canvas-unavailable readers retain static explanations. The
single-file build embeds the geometry and makes no network requests.

This changes the explanatory presentation, not the task definitions, frozen
outcomes or anatomical evidence. Reopen individual scenes when the task contract
changes, a legend becomes ambiguous, or user feedback identifies an unhelpful
geometric simplification. Validation is recorded in
[the 3D coverage receipt](../docs/evidence/task-explorer-3d-2026-09-22.json).

Actor: **user** then requested review and polish, simplification, cleanup and a
focused commit. Actor: **assistant** separated scene geometry from playback,
removed redundant mesh calculations and deferred static fallback construction.
Review corrected planar detection boxes, cavity-versus-material motion semantics,
lunar surface marks, dashed reference styles and overlapping labels. Classification
now shows a label schema without inventing a diagnosis; authored class labels remain
expandable. Geometry checks and the full offline browser matrix cover the corrected
semantics, playback, off-screen suspension and disposal when navigating away.
