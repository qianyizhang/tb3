# BR-004 case-83: completed local-omission miss


Terra completed normally, rewrote and validated its report, and returned no
findings. The frozen grader identifies exactly one missed label, `kidney_left`,
with no extras or point-format/localization-only problem. Matching oracle/nop
controls and an independent re-score agree. The author inspected the fixed
CT/source/task comparison before the final result: kidney tissue remains visible
where the task mask stops. The 215-voxel omission retains mask Dice 0.980 but
extends beyond the allowed fine boundary band.

The model's axial selection is based on the submitted mask's occupied slices,
82–113; the source mask extends to slice 116. Of the 215 changed voxels, 108
lie above slice 113. This is an inspection risk, **not a proven sole cause**:
the trace also contains padded coronal kidney views covering the omitted region.
The actual viewed image is retained at
`runs/br004-single/review/case-83-terra-kidney-coronal.png`; the corresponding
private source comparison is in the original BR-004 visual report. The supplied
reader returns float32 CT intensities, so the renderer's window arithmetic does
not have an int16 multiplication overflow.

Classify this as a genuine **local controlled-omission miss in a completed
trial**, without claiming a general deficit in anatomical knowledge. Source/CT
review is by the task author, not independent specialist clinical certification.
No unrelated source defect was alleged in the final report. At 15.92 minutes
and 32,744 output tokens, it is evidence of difficulty but still costly.


The [stable case receipt](../../docs/evidence/br004-single-case-83-review.json) retains hashes and exact grading. One attempt was made; no repeat or final qualification is claimed.
