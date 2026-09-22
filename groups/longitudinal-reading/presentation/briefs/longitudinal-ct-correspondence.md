# Track lesions across CT visits

Locate the follow-up counterparts of marked baseline lesions and return a correspondence graph that allows several lesions to merge into one.

## Value

This isolates identity across changing images. It could support longitudinal review; clinical response assessment is outside this proposed task.

## Given

### Original data

Two native CT volumes per patient, with geometry and visit order preserved.

### Supplied helpers

Baseline lesion masks with opaque target IDs remove baseline detection. Full volumes remain available. Reader-selected slices/crops below are explanation aids, not proposed solver inputs.

### Callable tools

Proposed: viewing, multiplanar reformats, registration and measurement tools. Exact runtime and tool set are not frozen.

### Reference-only material

Follow-up masks/centers, cross-visit CSV, propagated points and this reader. The current author workspace contains GT; a solver allowlist has not been staged.

## Task specification

Find the counterparts, permit many-to-one links, and mark unresolved matches. Review coverage before declaring disappearance. No executable prompt or scorer is frozen.

## Expected output

A graph such as `B1 + B2 + B4 → F_A`, with each FU region tied to native series, zero-based voxel coordinates, RAS millimeters and evidence slices. Volume evaluation additionally requires submitted masks.

## Evaluation

Score localization, correspondence edges, events and measurement separately. Count each merged FU region once. Adjudicate uncertainty/coverage; numerical tolerances remain open. Compare with fixed registration/matching and measure both corrections and damaged correct links.

## Visual explanation

### Workflow

- Paired CT + marked baseline targets
- Inspect anatomy and resolve identity across visits
- Correspondence graph + locations + evidence

### Input

![Three actual paired CT examples](../../../../.local/longitudinal-ct-review/review/input.png)

Reader-selected axial crops from three downloaded v3 patients; not a full-volume search task. Each row uses the same physical field width across visits, but the scans are not registered. The lung FU view is centered using source registration propagation. In case A the third merging baseline member is on a lower slice, available in the local interactive reader. These are actual CT data, not synthetic anatomy.

### Supplied helpers

![Baseline mask assistance](../../../../.local/longitudinal-ct-review/review/helpers.png)

Same post-hoc views, with only the baseline manual masks revealed. Solid outlines and translucent fills use the matching ID legend printed on the sheet.

### Reference or output

![Manual reference masks at both visits](../../../../.local/longitudinal-ct-review/review/reference.png)

Manual GT reveal, not agent predictions. A: B1+B2+B4 merge into F4 (B4 is outside this axial view). B: persistent and new nodal labels coexist. C: source-labeled disappearance; comparable anatomical coverage still needs review. Source instance colors/IDs disclose identity and belong only in the reader. See the detailed review for the fourth, held-out facial example.

## Conditions

| Condition | Supplied help | Work remaining |
| --- | --- | --- |
| Proposed primary | Baseline masks + paired CT | FU localization and correspondence |
| Reference-assisted control | Both masks; independently permuted IDs | Association given candidate geometry |
| Proposed audit | Fixed matcher proposals, including correct ones | Evidence-based correction without damaging correct matches |

## Difficulty

Anatomy moves and lesion size changes. Mergers defeat a one-to-one output contract. New-lesion discovery requires separate search. Difficulty for agents is a hypothesis; no trial has run.

## Sources

- [Pinned Longitudinal-CT v3 and schema](https://fdat.uni-tuebingen.de/records/qe950-g4h94)
- [Exact release rights](https://fdat.uni-tuebingen.de/api/records/qe950-g4h94)
- [Dataset paper](https://www.nature.com/articles/s41597-026-07466-y)
- [Detailed local review and limitations](../../examples/longitudinal-ct-review-20260922.md)
- [Geometry checks and member hashes](../../examples/longitudinal-ct-review-20260922.json)

## Coverage

Four patient pairs downloaded (~424 MB); three main illustrations and one facial review exclusion. All 300 patient CSVs screened. Attribution: Küstner, Peisen, Gatidis and collaborators, University Hospital Tübingen; CC BY-NC 4.0. Derived views use windowing, selected slices/crops and reference overlays. Native data and generated sheets remain local; rebuilding elsewhere requires recovery.

## Gaps

Adjudicated disappearance coverage, uncertain/missing link handling, coordinate conversion, isolated solver staging, patient-disjoint evaluation, scorer tolerances and baseline comparison. Raw data are public training data with possible prior exposure. No agent result or clinical validation is claimed.
