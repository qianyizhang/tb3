# BR-020 — registration across CT reconstructions

Status: completed; Terra/high passed and this snapshot is retired.
[Results and trace analysis](BR-020-results.md), [freeze](../evidence/br020-freeze.json) and
[author audit](../evidence/br020-author-audit.json). This is a new user-authorized follow-up to the two retired
[BR-019 conditions](BR-019-results.md), not a change to their frozen evidence.

## Request and hypothesis

Source: the same local [research task](codex://threads/01a0a845-7c2d-7992-a662-24d52831af90).
After asking how the agent solved BR-019 and how to increase difficulty, the
user accepted the proposed different-reconstruction pilot with “go ahead”.
The earlier request explicitly authorized author testing followed by a
delegated benchmark. The complete visible user messages are available here;
there is no external conversation retrieval gap.

BR-019 permits almost exact intensity matching. This follow-up asks whether
using a target rendered from a genuinely different reconstruction of the same
CT acquisition removes that shortcut enough to challenge registration. It
retains ordinary numerical libraries, a 1,800-second agent limit, and physical
acceptance at RMS <=3 mm and maximum <=5 mm over a 7x7 image grid. No solver
ban, shorter reasoning limit, or added workflow is the difficulty mechanism.

## Predeclared bounded experiment

1. Curate one public, licensed clinical CT pair with different reconstruction
   kernels. Verify patient, study, frame of reference, acquisition identifiers
   and times, orientation, pixel spacing and all slice positions. A shared
   study alone is insufficient evidence of the same acquisition. Retain
   acquisition ambiguities explicitly; do not admit an unverified pair.
2. Choose one visually interpretable oblique thoracic/cardiac-region plane.
   Record the author-selected landmarks and clinical limitations. No claim of
   expert-certified standard cardiac plane is made.
3. Provide reconstruction A as a volume, and a windowed thin-plane target
   sampled from reconstruction B. Preserve native reconstruction differences.
   Provide necessary volume coordinates and target pixel spacing, but strip
   target position, orientation and source-instance identifiers. Private
   geometry and reconstruction B stay outside the agent image.
4. Use the unmodified BR-019 public-input numerical baseline, then independently
   grade its geometry. Compare the two reconstructions at the true pose to
   establish that exact image equality is gone. A matched same-reconstruction
   author control separates source/geometry defects from registration issues.
5. Freeze only after interpolation, geometry, wrong-answer, metadata and
   public-input checks pass. Run one matched oracle, nop and Terra/high attempt
   using the existing isolated Harbor setup. Delegate execution supervision,
   not task hints. No retries or automatic stronger-model escalation.
6. Inspect the actual solve trace and replay the submitted pose. A healthy pass
   retires this snapshot. A normal miss is only a local diagnostic and needs
   validity review. An infrastructure error or timeout is not a model failure.

This one-pair pilot cannot estimate success rates or isolate kernel effects
from all patient/plane differences relative to BR-019. Same-patient different
acquisition and CT/MR remain future experiments: respiratory or cardiac motion
can invalidate a single rigid ground truth.

## Source research

- [TCIA NLST collection](https://www.cancerimagingarchive.net/collection/nlst/):
  CT is available under CC BY 4.0; the former access embargo was lifted in
  September 2021. Only a bounded pair is needed, not the full collection.
- [NBIA API guide](https://wiki.cancerimagingarchive.net/display/Public/NBIA%2BSearch%2BREST%2BAPI%2BGuide):
  NLST has a separate API host. Live unversioned basic endpoints returned HTTP
  500; `/services/v1/getPatientByCollectionAndModality` works. This is a retrieval
  issue, not a data-access restriction or experimental result.
- [Paired reconstruction research](https://doi.org/10.1002/mp.17028):
  Krishnan et al. describe NLST soft/sharp reconstructions from the same
  projection data. This motivates screening; it does not establish that an
  arbitrary local pair has matching geometry.

Raw downloads, API responses, local conversion outputs and subsequent runtime
artifacts stay under ignored `runs/br020-registration/`. No new model trial
is admitted by source plausibility alone.

## Author feasibility observations before model launch

Selected NLST subject 120547, first complete B30f/B50f pair returned for the
first catalogue subject. Selection preceded plane construction or solving.
All 139 native slice positions, orientations and spacings match. Patient,
study, frame of reference, acquisition number (2) and exposure settings match.
The scans are 512x512x139 at 0.6953125x0.6953125x2 mm. Dates/times of acquisition
were removed: common projection acquisition is strongly supported by these
fields and image agreement, not independently proven from projection IDs.
After identical mild smoothing, volume correlation is 0.999840. This evidence
supports a geometry benchmark across reconstruction kernels; it is not a
validated cross-acquisition experiment.

The 192x192 target has 0.9 mm pixels and uses a visually selected apex-side
direction. It is a noncontrast chest CT example, not an expert-certified
cardiac diagnostic view. The public volume is an axis-aligned native-grid
B30f crop, without labels or target pose. The target is sampled from B50f.
At the hidden true pose, B30f versus B50f has image RMS 13.762 gray levels,
correlation 0.963451, and 44.46% identical pixels (including clipped background).
Thus exact texture equality is removed, while anatomical correspondence is
preserved to the level supported by the source audit.

The unchanged BR-019 baseline with 64 starts misses both this target and a
matched B30f target (60.87 / 61.03 mm RMS). Increasing only its `--starts` to
512 recovers both: cross-kernel 0.034306 mm RMS / 0.048141 mm maximum in
26.36 s; matched control 0.000238 / 0.000375 mm in 26.26 s. Both original
misses and follow-ups are retained. This was adaptive author feasibility
work before the model trial, not independent evidence that kernel changes
increase difficulty. The baseline reads only the three public input files;
it does not receive landmarks, target pose, source identifiers or the other
reconstruction. Its solver time excludes author reasoning.

An additional replay in the public-only Linux image passed with 0.031113 mm
RMS / 0.043968 mm maximum in 24.41 s. That disposable container had no network
or host mounts. The frozen task includes neither that solver nor its output.
Nine acceptance controls pass as intended, 204 interpolation samples agree
with an independent interpolator, and every target pixel maps inside the
public volume. PNG metadata is empty; the volume archive contains only HU and
its required voxel-to-LPS geometry. Source identifiers are retained privately.
