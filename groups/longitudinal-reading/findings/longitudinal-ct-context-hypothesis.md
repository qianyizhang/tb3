# Does broad clinical context help this paired-CT task?

**Supplying verified broad clinical context did not improve lesion recovery in
this fresh attempt:** the same 3/22 instances, 1/7 links and 2/15 exact events were
recovered. The separate CT-only probe already inferred metastatic malignancy and
listed melanoma as a possibility. Residual omissions include explicit benign
interpretation of a reference-positive focus and a demonstrated rendering gap.
This weakens missing broad diagnosis as the sole explanation for this case;
it does not rule out effects of detailed clinical reports or run-to-run variation.

This is a user-selected diagnostic study on the second selected case, with one
CT-only context-inference session and one independent context-supplied lesion
session, both Astra medium. The earlier image-only lesion attempt remains the
comparator. [Predeclared design](../methods/longitudinal-ct-context-v1/protocol.md),
[exact inference prompt](../methods/longitudinal-ct-context-v1/inference-instruction.md),
[exact supplied-context lesion prompt](../methods/longitudinal-ct-context-v1/supplied-instruction.md),
[preparation provenance](../examples/longitudinal-ct-context-preparation.json).

## What context was actually available?

The released patient CSV gives age 44, recorded sex female and a 121-day interval.
The age field's reference date is unspecified. The
[source paper](https://www.nature.com/articles/s41597-026-07466-y) establishes
metastatic malignant melanoma and systemic therapy at the cohort level; the
[release card](https://fdat.uni-tuebingen.de/records/qe950-g4h94) describes staging
and longitudinal therapy-response assessment. Both are weaker than an individual
clinical report. Surgery, regimen and treatment start/stop dates are unavailable.

Only those verified broad facts entered the lesion rerun. The context-inference
output did not. No source identity, organs, lesion counts/descriptions, locations,
growth, response, labels or event facts entered either input. Diagnosis changes
the clinical prior intentionally; the boundary excludes direct target annotation,
not every piece of information relevant to recognition.

The source card says annotators used clinical reports. Our intervention restores
only a small portion of potential clinical context. It cannot test the effect of
unreleased lesion descriptions, pathology or detailed clinical reports.

## CT-only context inference

Attempt `attempt-0a8df9d2ca4a4034` finished normally in **3m27s**, with 14 image
observation blocks and valid structured output. These are image/montage blocks,
not a count of distinct native slices. The schema-only reward is not a diagnostic
accuracy score. The model inspected headers, sampled axial and coronal surveys,
focused liver/groin series and lung windows, using NiBabel, NumPy and Pillow.

| Field | Agent output | Evidence interpretation |
| --- | --- | --- |
| Broad diagnosis | Inferred suspected metastatic malignancy involving liver; confidence 0.91 | Compatible with the source diagnosis and visible reference-positive disease. Histology is not established. |
| Specific primary diagnosis | Unknown; melanoma listed among compatible alternatives | The relevant diagnosis entered its differential without being supplied. This is not exact identification or proof of image-only identifiability. |
| Age | Unknown; adult skeletal appearance noted | Appropriate distinction between appearance and the unrevealed numeric age 44. |
| Recorded sex | Unknown | No demographic record in the inputs; anatomy alone does not establish a recorded field. |
| Interval | Unknown | Headers lack acquisition dates; growth and spatial affine origins do not establish 121 days. |
| Baseline purpose | Unknown exact indication; staging/restaging/surveillance among alternatives | Broad oncologic context is plausible; a requisition or clinical report is absent. |
| Follow-up purpose | Unknown exact indication; reassessment/response assessment among alternatives | Compatible possibilities, not a known ordering indication. |
| Systemic treatment | Unknown | Correctly avoids equating worsening image appearance with a particular treatment history or regimen. |
| Surgical context | Inferred probable prior right inguinal/local intervention; confidence 0.76 | Scar-like changes were cited; surgery type, indication and timing were explicitly unestablished. No source surgical record permits adjudication. |

The quoted confidence numbers are the model's assessments, not measured
calibration. Seven fields were marked unknown and two inferred. This is not a
2/9 accuracy score: exact hidden metadata were not assumed CT-identifiable.
The model's approximate baseline liver evidence point `(185,315,430)` is 1.381 mm
from GT4; its follow-up point `(155,250,542)` lies inside GT4. These post-hoc
coordinate checks support evidence consistency, not exhaustive detection or
clinical adjudication. The suggested surgical context remains unverified.

Its acquisition discussion described apparently little IV enhancement and a
possible PET/CT acquisition. These were qualified image-based suggestions. The
release's typical protocol is not sufficient to adjudicate the exact acquisition
phase or whether this patient had accompanying PET data.

## Context-supplied lesion result

Attempt `attempt-81ee755346d04be7` completed normally in **12m27s**, with 82 image
observation blocks, no execution exception, valid output files and exact
independent score replay. It stopped well before its two-hour ceiling. Only the
clinical-context block and its instruction to use that context changed; CTs,
reference labels, scientific scorer, runtime and configured resources matched
the original case02 attempt.

| Measure | Previous image-only | Context supplied |
| --- | ---: | ---: |
| Strict detected instances | 3/22 | 3/22 |
| Instance false positives / false negatives | 0 / 19 | 0 / 19 |
| Detection F1 | 0.240 | 0.240 |
| Baseline foreground Dice | 0.7991 | 0.7395 |
| Follow-up foreground Dice | 0.8913 | 0.8760 |
| Equal-GT-instance macro Dice | 0.1073 | 0.1104 |
| Correct links, end to end | 1/7 | 1/7 |
| Correct exact event groups, end to end | 2/15 | 2/15 |
| Persistent groups recovered | 1/7 | 1/7 |
| Newly appearing groups recovered | 1/8 | 1/8 |

Both attempts matched **GT4 at baseline, GT4 at follow-up and GT13 at follow-up**.
There were no gains or losses in the detected reference identities. Both recovered
the one eligible link and two eligible event groups correctly, conditional on
their detected endpoints; that does not establish complete association ability.
This case contains no merger or disappearance reference groups.

The tiny macro-Dice increase is a contouring trade-off, not better discovery.
GT13 Dice improved from 0.579 to 0.735, while GT4 Dice decreased from 0.869 to
0.799 at baseline and 0.912 to 0.896 at follow-up. Zero instance false positives
does not mean zero extra tissue in the masks. All 11 instances <=1 mL remain
missed; localization stays 1/9 for >1–10 mL and 2/2 for >10 mL. The two large
instances are the same lesion at two visits, not two independent patients.

## What the trace supports

The new attempt used sampled axial overviews, denser local views and targeted
orthogonal reconstructions. It selected manual axial polygon/ellipse contours,
fit closed splines, interpolated signed-distance fields between slices and
rasterized them on native grids. A limited intensity rule removed peripheral
air near the follow-up lesion. This differs from the original attempt's
ellipse-envelope/intensity-threshold construction, and helps explain changing
overlap without changing which lesions were selected. No added pretrained model
was used.

**Explicit recognition/inclusion disagreement:** the report excludes baseline
`(190,199,406)` and follow-up `(182,165,524)` as a small, sharply defined,
similar-appearing cyst-like or vascular focus. Both exact native points are
**inside source GT2**. Their GT volumes are 0.982 and 0.823 mL, respectively,
and both remain entirely uncovered. This is documented rejection of a noticed
reference target. It is not merely a failure to search for that target, but
reference agreement does not adjudicate whether the focus is clinically malignant.

![Explicit rejection of reference GT2 at both visits](/Users/zhangqy/pkgs/tb3/.local/longitudinal-ct-context-v1/comparison/explicit-gt2-rejection.png)

Cyan solid contours show source GT2; orange solid would show the new prediction,
which is absent here. These native CT views are centered on the agent's reported
points, with HU [-160,240]. They were created after the trial and were never
solver inputs. These views show the rejected focus; they do not independently
establish benignity or malignancy.

**A search/review coverage gap:** all explicit retained axial rendering commands
generate 217 distinct baseline planes and 224 follow-up planes, some cropped.
None intersects the bone reference GT7's axial extent: baseline k=562–564,
follow-up k=658–659. The retained orthogonal crops also exclude these z ranges.
The dedicated bone-window views cover only k=325–490 and k=465–575, respectively.
No whole-volume candidate detector compensates for this gap: masks are built
only around the selected manual contours. Thus this target was skipped by the
retained visual-review method; these omissions do not measure recognition of a
displayed bone target. Slice presence elsewhere still does not prove attention.

**The previously excluded GT14 remains unresolved:** it is not detected in either
attempt. The old dominant mask incidentally covered 11.1% of its voxels; the new
masks cover 0%. The new report does not explicitly reassess this particular
focus, so calling it a second documented vessel rejection would overstate the
trace. The new thigh exclusion is 331 mm from the nearest reference target and
does not explain any of the actual GT omissions.

![Previously excluded GT14 remains absent as a separate instance](/Users/zhangqy/pkgs/tb3/.local/longitudinal-ct-context-v1/comparison/gt14-comparison.png)

Cyan solid: GT; purple solid: original image-only prediction; orange solid:
context-supplied prediction. Numbers are the respective local instance IDs.
Native follow-up k=534/536/538, i right and j down, HU [-160,240]. GT-selected
views are author-only and are not an exhaustive false-positive review.

## Attribution and next distinction

The original solver had only cleaned CTs, with no clinical record or demographic
CSV to read. Its missing exact context was an input limitation. The inference
probe nevertheless recognized a malignant pattern and named melanoma as a
possibility, so lack of any oncologic interpretation is an incomplete explanation.
The new lesion attempt received the verified diagnosis/context in its initial
prompt, but its public messages and report do not explicitly discuss melanoma or
how that context affected decisions. Delivery is verified; actual internal use
cannot be inferred from the absence of discussion. This is a test of context
availability, not proof that the model reasoned effectively with every field.

The supported result is **no detection/association improvement when broad context
was supplied**, alongside continued candidate-recognition and visual-coverage
limitations. It does not establish that clinical context never helps, that all
misses share one cause, or that GT is clinically wrong. Exact history often cannot
be reconstructed from CT, and the unavailable individual clinical reports may
contain information our no-target-hint condition deliberately cannot restore.

Assistant recommendation: retain broad clinical background as an explicit task
condition. For further attribution, separate a coverage-controlled review from a
localized candidate-judgment task requiring an explicit explanation of how the
supplied context affects acceptance. Those would be separate diagnostic controls,
with disclosed localization assistance and reference-adjudication limits. No
additional model attempt is selected or launched by this recommendation.

## Provenance and verification

Both fresh conditions used the exact existing solver image and CT hashes. Each
had new native oracle/no-op controls with expected rewards, live isolation checks,
unchanged frozen payloads, separate sessions and no retries or continuations.
The context inference output was never supplied to the lesion session. Both
saved validators reproduced their original results exactly. Observed tool and
transport records show no external dataset retrieval; this cannot exclude
unseen prior training on public data. Clinical interpretation remains unadjudicated.

Inference digest `e86b2cee2e85ab108157c9c827d9253f5b8d6f7659e35ca0fa8f0d24ffca23a7`;
supplied-context digest `ffdf321ba2637b46484309d8ec2c39fdffd5234b99e3152842c245a25a149215`.

[Machine-readable comparison and trace evidence](evidence/longitudinal-ct-context-comparison.json)
· [Context inference evidence](evidence/longitudinal-ct-context-inference.json)
· [Exact inferred context](/Users/zhangqy/pkgs/tb3/.local/attempts/attempt-0a8df9d2ca4a4034/job/task__Rzm9L2L/artifacts/app/answer/context.json)
· [Exact supplied-context agent report](/Users/zhangqy/pkgs/tb3/.local/attempts/attempt-81ee755346d04be7/job/task__5btJU8Q/artifacts/app/answer/report.md)
· [Recovery/analysis method](../methods/longitudinal-ct-context-v1/README.md).

CT source: Longitudinal-CT v3, Küstner, Peisen, Gatidis et al., University Hospital
Tübingen / FDAT, CC BY-NC 4.0. Generated media remain local with source hashes.
