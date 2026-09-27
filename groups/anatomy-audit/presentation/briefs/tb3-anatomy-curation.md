# Curate anatomy before claiming a difficult task

The retained BR-012 author screen produced five candidate cards from six VerSe
patients and seven volumes. **Zero hard tasks were admitted; zero model trials
were run.** Unusual source anatomy is not automatically an annotation error.

## Value

Establish whether available geometry, source conventions and references support
a well-defined answer before using model performance to test a hypothesis.

## Given

### Original data

Seven unchanged vertebral masks, seven centroid JSON files and seven source PNG
previews: 406 upper/lower, 547, 585, 581, 642 and 823. Their 145 annotated instances
include three repeated identities across the overlapping 406 scans. Full CT volumes,
rib/sacral masks and validated fracture grades were not acquired for this screen.

### Supplied helpers

Author access to source labels, the source paper and its supplementary table.
The multiset baseline receives the label inventory. The fixed-12-thoracic baseline
receives the true top anchor and can extend through L6. This is privileged author
assistance; no blind solver packet was frozen here.

### Callable tools

Local array/affine inspection, full-mask centroid and volume measurements, and
source preview inspection. Historical authoring modules are not rerun on import.
The new teaching builder verifies source hashes and measurements independently.

### Reference-only material

Source vertebral names, segmented counts, assumed anatomical structure and
curation decisions. Reader reveal exposes these references explicitly. Source
labels are not independent clinical adjudication or proof of a unique mask-only key.

## Task specification

Screen source suitability, geometric shortcuts and alternative naming conventions.
Preserve physical LPS millimetres and each scan's native frame. The 406 scans
overlap but have not been validated for fusion. The source's assumed segment
structure must not be conflated with segmented counts.

## Expected output

| Card | Source | Retained decision and reopening condition |
| --- | --- | --- |
| C01 | 547 / 585 | Both have 25 objects, but source partitions are 7C/13T/5L and 7C/12T/6L. Needs anonymous rib context or independent proof that supplied facet geometry uniquely resolves the convention. Cross-patient and sampling differences remain. |
| C02 | 406 | Preservation candidate. T10 volume is 13.79 mL versus T9 37.49 and T11 45.17 mL; posthoc size flagging cannot separate faithful anatomy from error. Upper C1 mask lacks a centroid entry; cause unresolved. |
| C03 | 823 | Typical-numbering calibration only. Both ordering baselines recover 24/24; no pathology-free certification. |
| C04 | 642 | Reserve: C5-C7 + 11T + 6L, cropped upper cervical coverage, about 3 mm left-right sampling, missing contextual masks. Needs anchor, morphology and nomenclature checks. |
| C05 | 581 | Reject an exact mask-only key. Explicit source ambiguity and omission policy for partly sacral-fused vertebrae preclude inventing a missing-object error. An uncertainty task needs an acceptable-answer set. |

## Evaluation

Supplied-multiset height ordering recovers **145/145 instances, 7/7 volumes**.
Fixed-12-thoracic ordering with the true top anchor recovers **128/145, 4/7 volumes**:
547 has 19/25; 585 has 25/25; 642 has 14/20. These are author screens,
not model trials, independent clinical validation or population estimates.

## Difficulty

A baseline error does not prove identifiability or difficulty. The proposed
typical/unusual by faithful/error control matrix remains incomplete: no errors
were injected, no disease gold was added, and no independent blind expert review
or grader was executed. Reopen only with qualified context, acceptable answers
and verified controls; the separate BR-011 I2 prototype remains calibration work.

## Coverage

The story shows sampled source boundary voxel centres, not meshes or clinical CT.
All measurements use full occupancy. Quantization is at most 0.05 mm per axis;
all 104,100 retained teaching points are checked against source occupancy and
boundary membership. A proper LPS display rotation preserves handedness. Separate
scans are independently fitted; comparison does not imply registration.
The T9-T11 view is explicitly focused. Original sources and scores remain unchanged.

VerSe source data and this derivative use CC BY-SA 4.0. See the source notice for
attribution, exact terms, hashes, derivation and limits.

## Sources

- [BR-012 protocol](../../experiments/br012/protocol.md)
- [Retained curation report](../../../../docs/research-rounds/BR-012-anatomy-curation.md)
- [Retained measurements and source receipts](../../../../docs/evidence/br012-curation.json)
- [Teaching provenance and license](../../../../presentation/task-explorer/anatomy-curation/NOTICE.md)
- [VerSe source](https://github.com/anjany/verse)
- [Liebl, Schinz et al. source paper](https://doi.org/10.1038/s41597-021-01060-0)
