# Second CT case: unchanged image-only instructions, new-lesion events

2026-09-22 · [Source task](codex://threads/01a0c4d1-741f-76e3-9023-1064e5a9a0c5)
· [Selection and data/GT illustrations](../examples/longitudinal-ct-case02-selection.md)
· [Protocol](../experiments/longitudinal-ct-case02-astra-medium/protocol.md)

## Question and setup

The user selected another suitable case after source/GT review and explicitly
requested one fresh Astra-medium attempt. A 300-patient CSV screen yielded six
eligible contrasts to the original nodal-merger case. Patient `bcbe3365e6` was
selected before download/model execution, with seven persistent identities and
eight new reference lesions. All 22 present instances are retained. The case is
purposively selected and supplies a second development observation, not population
accuracy or an independent model ranking.

The native pair is separated by 121 days. Source rows comprise twelve liver,
two nodal and one skeletal lesion. Distinct source IDs do not touch. One small
one-voxel satellite remains in its original follow-up ID. Geometry/label/volume
checks pass; original references are unchanged. The images are substantially
larger than the first pair (615 and 743 slices), and many liver foci are subtle.

The **exact revised v2 prompt and original scientific scorer** are retained.
The solver receives two cleaned native CTs with identical image voxels and
geometry; no GT, organ/count/event hints, disease, clinical reports, prior output
or source identity. Runtime, medium effort, tools and two-hour ceiling are the
same. One newly built data-only solver image and separate evaluator pin the new
case. Both native controls passed their expected outcomes; the exact-reference
control recovered 22 instances, 7 links and 15 typed groups at perfect overlap.

## Results

The fresh run completed normally in **17m 02s** of agent execution, with 67
retained image observations. Its output contract is valid and independent replay
reproduces every score exactly. It recovered the large persistent liver lesion
at both visits (source ID 4) and one new liver lesion (source ID 13).

| Endpoint | Result |
| --- | ---: |
| Strict localization, baseline | 1/7 |
| Strict localization, follow-up | 2/15 |
| Instance TP / FP / FN | 3 / 0 / 19 |
| Foreground Dice, baseline / follow-up | 0.7991 / 0.8913 |
| Equal-GT-instance mean Dice | 0.1073 |
| Mean Dice over the 3 matched instances | 0.7867 |
| End-to-end links recovered | 1/7 |
| Exact typed event groups | 2/15 |
| Persistent / newly appearing groups recovered | 1/7 / 1/8 |
| Conditional links / exact events | 1/1 / 2/2 eligible |

Zero instance FP means every predicted instance matched a reference under the
frozen centroid criterion; it does not mean there was no excess segmented tissue.
Foreground voxel precision was 0.839 and 0.859. The dominant lesion's Dice is
0.869 baseline and 0.912 follow-up. The new lesion's Dice is 0.579, with 50.9%
of its GT voxels covered. Thus the agent can identify, contour and associate
some lesions, but recovery is far from exhaustive and the smaller accepted
lesion also has appreciable boundary disagreement.

| Predeclared native size stratum | Localized | Equal-instance Dice |
| --- | ---: | ---: |
| <=1 mL | 0/11 | 0.000 |
| >1 to 10 mL | 1/9 | 0.064 |
| >10 mL | 2/2 | 0.891 |

These are visit-level instances. The two large instances are the same lesion
at two visits. Seventeen missed instances have zero foreground coverage; two
others have incidental coverage (F12 5.0%, F14 11.1%) without a matched instance.
The correct two event outputs do not establish complete longitudinal reasoning:
the other groups lack detected endpoints. This case shows how high total-mask
Dice can coexist with low lesion recall.

## Observable methodology and attribution

The agent inspected soft-tissue and lung windows, narrowed liver windows,
reviewed adjacent slices and sagittal/coronal reformats, and matched anatomy
rather than raw slice indices. All 22 generated broad-survey panels were
requested in the retained trajectory. Their two-slice means cover every native
axial slice within j=50:390, resized from 512×340 to 384×255 pixels. Presentation
is not proof that each small lesion was noticed; averaging and reduced display
size can suppress small or low-contrast detail. No dedicated bone-window review
is described in the final report.

For accepted lesions, the saved code specifies slice-wise elliptical envelopes,
interpolates their centers/radii with PCHIP, uses locally constrained HU thresholds
after Gaussian smoothing, selects connected tissue, fills/closes contours and
smooths the final mask. It reviews the resulting overlays and validates native
grid/affine and event-ID coverage. This is image-guided manual parameter selection
plus classical image processing, with no downloaded pretrained model.

There is direct evidence of a recognition/inclusion disagreement for one missed
target. The report excludes a focus around **follow-up (190,235,536)** because
“Tubular/branching continuation on adjacent images favors a vessel.” That native
voxel is **inside source GT14**, a new 2.379 mL liver reference. It is mostly
omitted as a separate instance; the nearby dominant mask incidentally covers
11.1% of it. This is stronger evidence than merely knowing that a survey image
contained the lesion. The exact point test and report/trace hashes are retained.

For the other missed labels, the trace does not isolate noticing from recognition.
Other reported exclusion points are outside the reference masks, so they must not
be relabeled as explanations for different GT misses. Likewise, the first case's
touching-instance ambiguity cannot explain all failures here: the new source
labels do not touch. The agent accepted the recovered small new focus despite
acknowledging a possible benign cyst, so the failure is not a uniform refusal to
include uncertain findings.

The supported conclusion is **limited exhaustive lesion recovery, with at least
one explicit recognition error relative to GT, alongside useful contouring and
correct association for selected findings**. This run does not isolate every
miss, establish clinical GT error, or show that supplying clinical reports would
fix the result. No additional point-guided trial was run.

![A recovered new lesion and two missed new targets](/Users/zhangqy/pkgs/tb3/.local/longitudinal-ct-case02/analysis/followup-4.png)

Cyan solid contours are reference and purple solid contours are saved output;
numbers are their respective local instance IDs. GT-selected native planes and
crops were generated only after inference. They do not constitute an exhaustive
false-positive review. Additional sheets:
[BL 1–4](/Users/zhangqy/pkgs/tb3/.local/longitudinal-ct-case02/analysis/baseline-1.png),
[BL 5–7](/Users/zhangqy/pkgs/tb3/.local/longitudinal-ct-case02/analysis/baseline-2.png),
[FU 1–4](/Users/zhangqy/pkgs/tb3/.local/longitudinal-ct-case02/analysis/followup-1.png),
[FU 5–8](/Users/zhangqy/pkgs/tb3/.local/longitudinal-ct-case02/analysis/followup-2.png),
[FU 9–12](/Users/zhangqy/pkgs/tb3/.local/longitudinal-ct-case02/analysis/followup-3.png).

## Interpretation boundaries

The [source card](https://fdat.uni-tuebingen.de/records/qe950-g4h94) says annotators
used clinical reports together with CT. The retained image-only task deliberately
withholds this context. Reference-positive disagreement therefore needs careful
recognition/annotation interpretation; technical review does not adjudicate
malignancy. The [paper](https://www.nature.com/articles/s41597-026-07466-y) describes
exhaustive annotation without a minimum size. All sizes remain in our evaluation.

One persistent lesion accounts for 84.6% of baseline and 94.9% of follow-up GT
volume. Report foreground Dice alongside equal-instance Dice and prospectively
declared size strata: eleven visit-level instances <=1 mL, nine >1–10 mL and two
>10 mL. The two large instances represent the same lesion at two visits.
Correct large-lesion overlap does not establish exhaustive detection. Exact typed
events and links remain separate; this case does not test merging or disappearance.

## Provenance

Frozen task digest:
`e12f6fc10c83c8dfb2bc4ca3bd4cfffc90811bdb7249ad8ddedcf55655b1083a`.
Oracle `attempt-81f13e4ef1d0421a`; no-op `attempt-0bfc98d7e82d4525`.
Model `attempt-92800845745342f4`. No retry, resume or localized follow-up is selected.
The frozen payload stayed unchanged; the model had no execution exception.
Live isolation checks passed and the trace contains delivered image payloads.
Proxy denials are retained separately, without treating them as an image-delivery
failure. This audit cannot exclude unseen training exposure to a public dataset.

[Selection receipt](../examples/longitudinal-ct-case02-selection.json)
· [Preparation and isolation receipt](../examples/longitudinal-ct-case02-preparation.json)
· [Recovery and verification method](../methods/longitudinal-ct-case02/README.md).

[Machine-readable results, size strata, trace statements and hashes](evidence/longitudinal-ct-case02-astra-medium.json)
· [Exact agent report](/Users/zhangqy/pkgs/tb3/.local/attempts/attempt-92800845745342f4/job/task__Hq6FNdV/artifacts/app/answer/report.md).
