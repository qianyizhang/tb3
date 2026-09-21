Source: `docs/research-rounds/BR-034-preserved-control-amendment.md`; original SHA-256: `0ce4f74b2ca495ef91ccff3ab47cc28c5fd7758eea6616680422597db478b515`.
Repository source locators below are provenance; they are not required runtime inputs.

# Supplementary preserved-function replay control

Added after the primary Sol attempt was dispatched and before inspecting any
model output. This is an additive check, with no changes to the frozen primary
task, thresholds, source case or prompt, and no feedback to the running model.

The primary and second patient both have mildly reduced reference EF. To avoid
treating an always-reduced diagnostic label as discrimination, the earliest
compact screened case with preserved reference EF is added as a negative
control: `exam_8d864b48907a4e1c / recording_5dfce0e6687b9ef4`, 26 native
annotated frames, reference EF 55.73%. Images, calibration and its initial
surface are supplied only to the frozen executable after the trial. Reference
surface, timestamp, source/archive and coordinate checks passed. Preparation
and all file hashes are retained in `runs/br034-pathological-echo/
preserved-control-freeze.json`.

This small selected negative control does not establish clinical sensitivity
or specificity. Since it was added after dispatch, report it as supplementary
rather than retroactively part of the original preregistered model reward.

## Input-quality correction before trial completion

Visual review and an explicit sector-coverage calculation found 17.78% of the
initial surface vertices, and 7.94% across all frames, outside the acquired
sector in that proposed negative control. It is retained as a rejected
candidate and is not used for a diagnostic discrimination claim.

The replacement is already-screened `exam_2a7bdab4857947fe /
recording_020bed77ed11234b`, with reference EF 60.29% and 48 consecutive
annotated native frames. Only 0.21% of initial vertices (0.0086% overall) fall
outside the sector. Its separate preparation and hashes are recorded in
`preserved-control-v2-freeze.json`; the original receipt remains untouched.
This decision uses input/reference quality only, before model completion and
without replay outcomes. The primary and original hidden reduced-function
patient both have zero reference vertices outside their acquired sectors.
