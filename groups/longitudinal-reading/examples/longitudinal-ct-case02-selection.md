# Why a second, liver-dominant Longitudinal-CT case

2026-09-22 · actor: assistant · [Source request](codex://threads/01a0c4d1-741f-76e3-9023-1064e5a9a0c5)

## What the source changes in our interpretation

The [v3 dataset card](https://fdat.uni-tuebingen.de/records/qe950-g4h94) says that
lesion identification used CT **and clinical examination reports**. Our retained
image-only contract withholds reports. Thus source agreement cannot automatically
be interpreted as CT-only diagnostic truth. The source's `target_lesion` flag is
not an exhaustive-lesion inclusion filter, and propagated/backpropagated points
are registration outputs rather than manual evidence of absence.

The [paper](https://www.nature.com/articles/s41597-026-07466-y) describes exhaustive
annotation without a minimum size, expert consensus review, anatomical matching,
and organ-specific display windows. It reports 4,079 baseline and 3,103 follow-up
lesions in 300 pairs. These properties motivate inspecting all reference labels,
keeping small lesions and scoring lesion recovery separately from total overlap.
The published nnU-Net baseline is not a directly comparable agent baseline:
different training, population and evaluation context preclude ranking from it.

Pinned release remains v3 (`qe950-g4h94`), not a switch to a different annotation
revision. The live API still advertises archive size 51,047,900,775 bytes and MD5
`cde33aed3ed708065f5a1970b5079098`. It declares CC BY-NC 4.0; that exact release
license governs retention, rather than the paper's shorter license description.
Attribution: Küstner, Peisen, Gatidis and collaborators, University Hospital
Tübingen. Raw images and derived figures remain local.

## Transparent metadata selection before download/inference

All 300 retained patient CSVs were checked against the pinned ZIP member size and
CRC. They contain 4,638 longitudinal rows: 2,506 persistent, 1,407 disappearing,
559 new and 166 merging members. Deduplicating follow-up merger destinations
reproduces 4,079 baseline and 3,103 follow-up instances. Row counts and per-visit
instances are different units. Of 300 patients, 288 have every link explicitly
clear and 252 have exactly one acquisition at each visit.

To add a different challenge beyond the first nodal-merger pair, require:

- One native volume per visit, every link explicitly clear.
- 4–15 reference instances at each visit, persistence and new appearances.
- At least three lung/liver rows and no merger, avoiding the earlier confluence issue.

Six cases qualify. After descriptive metadata exploration, rank by larger minimum
present-lesion volume, then larger new-lesion volume, then patient ID. This favors
less extreme tiny-target ambiguity while preserving a substantial multi-lesion
challenge. The ranking was fixed before downloading the new CTs or model execution.
It is purposive development selection, not a random cohort or a claimed optimal
case. Full candidate details and CSV hashes are in the selection receipt.

| Rank | Patient | BL/FU labels | Persistent/new/disappearing groups | Minimum mL |
| --- | --- | ---: | --- | ---: |
| 1 | `bcbe3365e6` | 7/15 | 7/8/0 | 0.148 |
| 2 | `eae27d77ca` | 5/11 | 5/6/0 | 0.085 |
| 3 | `9dcb88e013` | 6/6 | 5/1/1 | 0.059 |
| 4 | `95b3019dea` | 4/5 | 4/1/0 | 0.059 |
| 5 | `96da2f590c` | 6/7 | 6/1/0 | 0.026 |
| 6 | `31c8f1568c` | 8/13 | 8/5/0 | 0.014 |

## Downloaded candidate and author sanity review

Selected `bcbe3365e6`, 121-day interval. Seven members totaling 278,434,401
compressed bytes were acquired with bounded HTTP ranges. Each decompressed size
and CRC matched; SHA-256 digests were retained. The 51 GB archive was not fully
downloaded and its full MD5 was not verified. Source CSV, both CTs, both masks and
both center JSONs remain in `.local/longitudinal-ct-case02/raw/`. Only cleaned CTs
will enter the solver.

The 15 longitudinal rows comprise twelve liver, two nodal and one skeletal
reference. All 22 present mask labels agree with the CSV IDs/volumes, and each
mask matches its CT's shape and affine. Shapes are 512×512×615 and 512×512×743;
voxel spacing is 0.9765625 mm in-plane and **2.0/2.5 mm through-plane**, despite
the source's typical 3 mm protocol. Use file geometry, not a paper default.
No labels touch one another under 6-connectivity or meet a volume boundary.

The native max-area views of all 22 labels were inspected. No obvious defacing
overlap was observed at these targets. Many liver lesions are subtle against
surrounding tissue. One large persistent liver label grows from 58.9 to 369.0 mL;
it accounts for 84.6% and 94.9% of total reference volume, respectively.
Equal-lesion and predeclared size-stratified scores will show whether the
smaller/new targets were recovered. There are 11 visit-level instances <=1 mL,
nine >1 to 10 mL and two >10 mL. These are
annotation-derived measurements, not treatment response conclusions.

The original follow-up label 13 has two 6-connected components (1,207 voxels
and a one-voxel satellite); retain both and
the original ID. This technical detail does not establish two clinical lesions
or justify relabeling. A max-area slice review is not clinical adjudication of
all 3D boundaries, malignancy or whether a new label was previously invisible.

![Baseline CT and reference labels](../../../.local/longitudinal-ct-case02/review/baseline-1.png)

[Follow-up labels 1–8](../../../.local/longitudinal-ct-case02/review/followup-1.png)
· [Follow-up labels 9–15](../../../.local/longitudinal-ct-case02/review/followup-2.png).
Cyan solid contours are GT. Native i points right and j down; slices/crops are
GT-selected author views, never solver input. The fixed 90 mm crops do not show
the entire largest follow-up mass; the full CT/mask is retained for evaluation.

![Native reference volume profile](../../../.local/longitudinal-ct-case02/review/volume-profile.png)

## Frozen task choice

The [protocol](../experiments/longitudinal-ct-case02-astra-medium/protocol.md)
retains the exact [v2 instruction](../methods/longitudinal-ct-image-only-v2/instruction.md)
and scientific scorer. Only the patient data/private references change. The agent
receives no disease, organ, count, location or event hints, source identifier,
clinical report, mask, previous trace or score. One fresh Astra-medium attempt
is selected, following separate oracle/no-op controls. No localized follow-up is
implicitly authorized. Primary and per-event metrics remain separate.

[Selection, source hashes and technical review receipt](longitudinal-ct-case02-selection.json).
