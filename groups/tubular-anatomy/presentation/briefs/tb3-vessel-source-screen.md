# Curate vessel connectivity tasks

Four TopCoW MRA cases support an author source screen for local vessel repair.
**BR-025 admitted no defect fixture and ran no model trial.** Its output is a
candidate panel with explicit admission gaps.

## Value

Check whether images, annotations and controls support a defensible local
connection task before measuring an agent's behavior.

## Given

### Original data

Four complete public training MRA volumes: `004`, `007`, `009`, `012`, selected
after screening twelve edge-label files. Displayed projections use source Circle
of Willis boxes. CTA labels were checked; CTA images were not reviewed.

### Supplied helpers

The author has multiclass masks, boxes, edge labels and mask-derived graphs.
These are curation inputs, not a frozen solver packet.

### Callable tools

Read-only native-affine inspection and local measurements. No inference is required.

### Reference-only material

Reveal orange right-Pcom, teal left-Pcom and blue other vessel annotations.
Pcom means posterior communicating artery. The native slice extent is selected
from annotations for author inspection. Graphs are not independent truth.

## Task specification

Preserve the source annotation configurations and possible control roles:

| Case | Left / right Pcom label | Candidate role |
| --- | --- | --- |
| 004 | Absent / present | Unchanged right-only |
| 007 | Present / present | Broken connection source |
| 009 | Absent / absent | False bridge source |
| 012 | Present / absent | Unchanged left-only |

Annotation absence is not a diagnosis. Projection overlap does not establish 3D
attachment; class mistakes that disappear on merging labels are not binary defects.

## Expected output

Four `source_candidate_only` records; **zero admitted defects and trials**.
No natural faulty prediction or numeric verifier thresholds were obtained.

The proposed future task gives MRA, a proposed binary mask and a broad editable
region → `corrected_mask.nii.gz`, same grid, preserved outside. Reconnect,
disconnect and unchanged remain possible. No answer labels or GT-shaped corridor.

## Evaluation

Four image/mask grids match. Present Pcom labels have one 26-connected component
and touch expected parent labels. All 146 node entries lie within **0.334601 mm**
of source foreground voxel centres. These checks do not adjudicate anatomy or
validate every graph edge.

## Difficulty

No model difficulty is established. Admission needs reproducible prediction
provenance, native-image review, adjudication and oracle, unchanged and wrong-bridge
controls. Local attachment, geometry and collateral edits need separate checks.

## Coverage

Twelve MRA edge files; four selected MRA pairs. Public-source exposure remains a
limitation. Later BR-026 synthetic feasibility is separate. Source terms require
attribution and noncommercial use; commercial redistribution needs permission.

## Sources

- [Retained BR-025 study](../../experiments/br025/protocol.md)
- [Original task design](../../../../docs/research-rounds/BR-025-vessel-connectivity.md)
- [Original curation receipt](../../../../docs/evidence/br025-curation.json)
- [Current source audit](../sources/vessel-source-audit.json)
- [Teaching derivation and terms](../../../../presentation/task-explorer/vessel-source/NOTICE.md)
- [TopCoW source release](https://zenodo.org/records/15692630)
- [Mask-derived graph release](https://zenodo.org/records/17358162)
