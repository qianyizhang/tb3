# H03 — Anatomical label review

BR-003, added explicitly by the user. Their clarification requires the agent to
infer anatomical expectations at test time from the full vocabulary and scan;
the public instruction supplies no organ-relation thresholds or label counts.

Five fixed packets derive from TotalSegmentator small dataset v2.0.1 subject
s1245. The source is a CT thorax with heart and all lung-lobe masks interior to
the acquired z extent. It does not establish complete rib coverage: first-rib
masks touch the superior boundary. Do not invent a universal 12-pair assertion.

Controlled packet truth is retained in tests/expected.json. One clean full scan
and one superior crop are negative controls. The crop begins above the source
heart mask and does not include the lower lobes. Three positive packets remove
the heart, exchange upper-lobe labels, or copy the left seventh-rib annotation
under the right-seventh-rib label. Only the four named focus labels are graded;
minor contour defects and unrelated anatomy are outside the contract.

All 117 names are retained, with independently permuted local DICOM Segment
Numbers. Native BINARY SEG omits empty frames; its Segment Sequence is reversed.
All images contain newly generated research UIDs and synthetic patient fields.
Source-reference read-back with highdicom reproduced every encoded voxel.
The author inspected CT orthogonal views, source-mask bounds and controlled
changes. No expert clinical review or general clinical validity is claimed.

The reference is deliberately a bounded, source-specific anatomical heuristic.
It is not a learned model or a generally safe clinical rule set. Five packets
are correlated fixtures from one source, not five independent model attempts.
The fixed-case design permits inspection and potentially case recognition;
do not interpret a failure as general medical inability or a pass as broad QA
competence. A meaningful healthy pass retires this snapshot.

Fixture production is retained in the sibling
`../../dicom-triplanar-svg/authoring/build_imaging.py`. Frozen source receipts,
license and derived-artifact hashes belong in the round evidence.
