# BR-012 — Curate real anatomy before model trials

**Status: curation complete. Six real patients inspected; no hard task admitted
and no model trials.** Retain one recognition pair, one structural preservation
candidate, and one calibration control. Keep one patient in reserve and reject
one ambiguous exact-label case. The interview submission is unchanged.

## Request and bounded method

On 2026-09-15 the user requested “go ahead, do a round of curation then,”
following [BR-011](BR-011-unlabeled-anatomy.md). The source message is retained
in the current conversation; its separate message ID was not captured.

Inspect primary-source variant/pathology annotations and a small selection of
real 3-D segmentation volumes. Start with VerSe because its published benchmark
documents labeling failures on anatomical variants; those results concern
specialized imaging models, not local Sol/Terra trials. Preserve the existing
unlabeled-organ prototype as a separate calibration condition.

Selection targets, declared before acquisition: a typical control, a documented
enumeration variant, a documented structural variant, a pathology example if
case-level evidence is obtainable, and an explicitly ambiguous negative example.
Acquire only the metadata and selected masks/previews needed for this screen.
Do not download a whole CT cohort or tune selection against model outcomes.

For every candidate record: source/label convention, actual visible objects,
what a solver must infer, cheap-baseline result, information missing from masks,
deterministic grading contract, and admit/hold/reject decision. Separately assess
source fidelity, mask-only identifiability, and expected difficulty. A planted
answer or a published label is not proof of a uniquely inferable answer.

No one-voxel edits, fabricated clinical histories, or rare-looking selection
without source evidence. Anatomy and annotation error remain separate axes.
Public inputs must preserve shared orientation and scale. Reviewer-only source
labels and clinical evidence must not leak into a future blind task packet.

## Result and recommendation

Prioritize **unlabeled regional identity**, using the equal-count pair below.
Ordinary whole-instance label permutations remain poor difficulty candidates:
sorting the objects by physical height and assigning the supplied label multiset
recovers **145/145 mask-value identities across all seven volumes**. This includes the
visibly asymmetric spine. Removing the names changes the problem; it does not
automatically make the remaining problem identifiable.

The unusual-anatomy/error condition needs additional solver-visible evidence.
An abnormal shape can be faithfully segmented or produced by an annotation
error. A source edit log cannot tell a mask-only solver which explanation is true.
This round found concrete examples of that boundary, rather than a new model
failure. Keep the [BR-011 organ prototype](BR-011-unlabeled-anatomy.md#concrete-i2-prototype)
as a separate calibration exercise; this spine curation does not replace it.

## Acquired and reviewed

From the [official VerSe archives](https://github.com/anjany/verse), retrieved
seven original masks, seven centroid files, and seven author preview images for
six patients. Patient 406 has two overlapping scans. The 145 annotated instances
include three repeated anatomical identities from that patient; they are not
145 independent patients or trials.

Case-level ratings were read from pages 2–3 of the
[published supplement](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41597-021-01060-0/MediaObjects/41597_2021_1060_MOESM1_ESM.pdf).
The [final data paper](https://www.nature.com/articles/s41597-021-01060-0)
supplies the numbering and omission conventions. Relevant limitations:

- Thoracic/lumbar classification uses ribs and, in ambiguous cases, facets.
  The acquired masks contain vertebrae, not ribs or the sacrum.
- Partially sacral-fused vertebrae can be intentionally unsegmented.
- The authors explicitly identify patients 581 and 606 as ambiguous.

The paper and archive describe CC BY-SA 4.0 data. Preserve that license and
attribution for derived data; the repository's code license is separate.
Primary-source previews were visually inspected, including the 406 asymmetry
and scan overlap. This is an **author review**, not an independent blind clinical
adjudication. No new disease diagnosis was assigned.

## Candidate cards

### BR012-C01 — Same count, different anatomical partition

**Patients 547 and 585; retain as the leading recognition pair, pending context.**
Both have 25 source-labeled objects. Their reference partitions are respectively
7 cervical / 13 thoracic / 5 lumbar and 7 cervical / 12 thoracic / 6 lumbar.

- **Task:** assign names to anonymous intact instances, preserving the extra
  thoracic or lumbar identity. Use the same vocabulary and representation for
  each patient; each would be a separate trial.
- **Hypothesis:** a solver imposes a usual 12-thoracic template despite evidence
  at the regional transition. Total object count cannot choose between these
  two partitions. This does not rule out a stronger simple geometric classifier.
- **What to inspect:** the last thoracic vertebra, first lumbar vertebra, their
  posterior structures, and rib attachments in shared physical space.
- **Cheap screen:** supplied-multiset ordering gets 25/25 on each. An anchored
  fixed-12-thoracic sequence gets 19/25 on 547 and 25/25 on 585. The latter rule
  can extend to L6. It receives the true top anchor and performs no morphology
  recognition. Its failure is not a Sol/Terra result.
- **Evaluation:** exact object-ID → canonical-name mapping, plus the regional
  partition; diagnostic reporting should expose a coherent one-level shift
  separately from isolated wrong assignments. Freeze accepted nomenclature
  before running. No essay or pixel-coordinate precision is needed.
- **Admission gap:** the source's rib-dependent distinction is not fully
  available in the acquired masks. Add verified anonymous rib context or establish
  that the retained facet geometry uniquely supports the key. Do not award a
  hard failure merely for reproducing a different defensible naming convention.

This is a comparison across two different patients, not a matched intervention
on identical anatomy. Their different voxel resolutions are also a confound to
resolve before using a success split as evidence about reasoning.

### BR012-C02 — Preserve substantial asymmetric anatomy

**Patient 406; retain as a potential false-repair control, not a hard anomaly detector.**
The source table records an assumed 7/11.5/6/5 segment pattern while its
segmented-instance columns contain 7 cervical, 12 thoracic and 6 lumbar labels.
The lower scan visibly contains an asymmetric T10-region structure. These are
different source quantities; do not silently turn the fractional pattern into
an invented absent object or a newly confirmed disease diagnosis.

- **Task:** infer identities while preserving the observed asymmetric structure.
  In a later error condition, separately identify a justified instance-assignment
  defect; unusual anatomy itself must not count as the defect.
- **Hypothesis:** a solver incorrectly repairs an unfamiliar structure toward a
  normal-looking template. This has not been tested.
- **What to inspect:** the asymmetric body/posterior structure and its relation
  to the adjacent vertebrae, not a tiny boundary deviation.
- **Magnitude:** source T10 occupies **13.79 mL**; neighboring T9 and T11 occupy
  37.49 and 45.17 mL. Its volume is about one third of their mean. This descriptive
  check was added after inspection; small size already highlights the region,
  so “find the small vertebra” would not be a convincing difficulty claim.
- **Cheap screen:** source-multiset and fixed-sequence ordering both recover all
  19 identities in the lower scan, and all 9 in the upper scan.
- **Evaluation:** separate identity correctness, preservation of the valid
  unusual structure, and localization of any independently justified injected
  defect. A named disease and a precise surface contour are outside this task.
- **Admission gap:** the current mask-only inputs do not establish whether every
  unusual-looking component is faithful anatomy. The source review images are
  author evidence, not a substitute for evidence the solver receives. No error
  was injected or binary disease-versus-error key frozen in this round.

Keep the two scans separate: three identities overlap, and they have different
image grids. Their physical coordinate systems were not validated for fusion.
The upper scan also contains a C1 mask without a corresponding C1 centroid
entry. Its cause is unresolved; this scan is not an unquestioned anchor key.
The sorting denominator includes that mask-value identity and is not a count
of independently confirmed complete annotations.

### BR012-C03 — Typical numbering reference

**Patient 823; calibration only.** All 24 identities are recovered by both
ordering baselines. Use it to check representation, orientation, vocabulary and
false-positive behavior. “Typical” here describes numbering, not a certified
absence of pathology. It is not a difficulty lead.

### BR012-C04 — Compensated counts with incomplete context

**Patient 642; reserve.** Source labels show C5–C7, 11 thoracic and 6 lumbar
vertebrae. A fixed sequence gets 14/20 identities; supplied-multiset ordering
gets 20/20. Missing upper cervical coverage, absent rib/sacral masks, and about
3 mm left-right sampling make this a weaker first candidate than C01. Do not
select it merely because the fixed sequence fails. A future trial would need
an independently established anchor, adequate morphology and a frozen convention.

### BR012-C05 — Ambiguous numbering and omitted fused structure

**Patient 581; reject from exact mask-only scoring.** The source explicitly
acknowledges numbering ambiguity and records Castellvi 3b. The source table's
assumed six lumbar levels coexist with only five segmented lumbar instances.
The omission policy means that mismatch cannot be promoted into a planted or
discovered annotation error. Keep it as an author-side rejection example. A
future uncertainty task would require a separately defined acceptable answer set.

## What this means for the ultimate condition

Maintain the two axes from BR-011: typical/unusual anatomy × faithful/erroneous
annotation. This curation supplies **candidate source material**, not a completed
2×2 benchmark. C03 is a typical reference; C02 is a possible unusual-anatomy
preservation control. No error cells or verified rare-disease task were created.

For the next authoring step, first resolve C01's missing rib/facet evidence.
Then screen the expanded inputs with the same simple methods. Retire a clean
cheap solution instead of increasing object count or hiding context. For C02,
require a solver-visible relational contradiction before adding an error key;
otherwise keep it as descriptive anatomy or exclude binary quality grading.

The fracture-grading source was located through the VerSe references, but no
case-level fracture grades were acquired or validated in this bounded round.
Neither a fracture diagnosis nor a rare-disease claim is inferred from these
mask shapes. The newer [VERIDAH paper](https://arxiv.org/html/2601.14066v1)
also uses a different rib-based convention; it must not be silently mixed into
the older VerSe key. Its specialized-model results are external evidence, not
Sol/Terra outcomes for this curation.

## Evidence, resource use and checks

[Evidence receipt](../evidence/br012-curation.json) includes source URLs,
archive ETags, per-file SHA-256/CRC verification, case ratings, geometry,
every baseline prediction, source/script hashes and dispositions.

| Quantity | Result |
| --- | --- |
| Acquired source members | 21 files; 24,218,921 bytes uncompressed from ZIP |
| Validated ZIP byte ranges, including archive indices | 10,174,383 bytes |
| Author geometric screen + preview export | 11.376 seconds on this machine |
| Source-multiset height ordering | 145/145 instances; 7/7 volumes |
| Fixed 12-thoracic ordering, given true top anchor | 128/145 instances; 4/7 volumes |
| Hard tasks admitted / model attempts | 0 / 0 |
| Solver tokens, solver time, verifier timing | Not measured; no model trial or task grader ran |

The download counts exclude the separately fetched paper HTML and supplement.
ZIP CRCs and range lengths are checked. Wider floating-point source label storage
was narrowed only after verifying every value was an exact integer; original
files remain unchanged. Measurements use full source resolution. Preview points
are sampled boundary-voxel centers, quantized to 0.1 mm with a checked maximum
0.05 mm coordinate error. They do not establish connectivity or replace masks.
Reviewer-only source keys are embedded in the preview; never give it to a blind
model as a task viewer.

A second local run reproduced every non-timing screen field and the preview
bytes. All 21 acquired file hashes were rechecked. Mask/centroid identity sets
agree in six of seven volumes; the remaining C1 discrepancy is recorded above.
Preview samples were mapped back through each source affine and checked against
the corresponding original mask value. Browser checks covered patient/object
selection, context, identity hiding, rotation and a 360-pixel layout.

Raw files live under `runs/br012-curation/source/`; author outputs under
`runs/br012-curation/author/`. Re-run the local screen without network access:

```sh
.venv-br003/bin/python probes/revisions/br012/authoring/screen_verse.py \
  --source runs/br012-curation/source --output runs/br012-reproduction
```

The [range reader](../../probes/revisions/br012/authoring/fetch_verse.py) accepts
an explicit archive split and exact member names recorded in the receipt. It
refuses reads over 32 MiB; no CT volume was acquired. The
[screen](../../probes/revisions/br012/authoring/screen_verse.py) requires NumPy and
NiBabel already present in the local author environment. It installs nothing,
runs no model and does not alter historical freezes or the submission repository.
