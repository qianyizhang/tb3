# BR-015 — Clinical evidence and anatomical identity

Historical selection/protocol record. [Current presentation and verdict](../anatomy-experiments.md) · [Trace analysis](../anatomy-traces.md).

**Status: complete; two Sol/xhigh passes, both conditions retired.**
[Results and interpretation](BR-015-results.md) ·
[Source and outcome audit](../evidence/br015-reviews.json).

On 2026-09-15 the user requested
continued investigation toward a task Sol/xhigh fails and a clinician can solve.
The user offered sampled reviews based on relevant experience. Message text is
retained in this conversation; individual message IDs were not captured.

## Declared candidates and decision rules

1. **C01: CT-supported atypical identity.** Start from the actual BR013-A02
   Sol/Terra failure, preserve its 11 objects and 13 possible classes, and add
   the original CT with working multiplanar/overlay tools. Preserve the key,
   masks, IDs, 3-D viewer and limits. One fresh Sol/xhigh attempt after freeze
   and oracle/nop controls. A pass retires this strengthened condition. A miss
   needs source and solver-visible-evidence review before promotion.
2. **V01: vascular identity by connections.** Inspect specialist-annotated
   abdominal vascular data for branch-level identity keys and substantial
   anatomical variation. Do not run if labels only distinguish artery/vein,
   if phases are unregistered, or if branch nomenclature remains ambiguous.
3. **R01: user review sample.** Prepare a compact packet with CT, anonymous
   overlays, clear instructions and an answer form. Keep reference answers and
   model outcomes separate. Previously discussed cases are familiarity-exposed
   reviews of evidence sufficiency, not blind demonstrations of human accuracy.
   New source cases should be identified as new, without showing their answers.

The target requires both a normal model failure and evidence of human
solvability. Published expert annotations support the reference; an actual
review of the same input supports task inferability. Neither substitutes for
the other. Do not call an author's own judgment an independent clinician result.

One attempt per frozen model task, zero retries, 1,800 seconds, four CPUs/4 GiB.
Record exact grading, tokens, agent/total time and runtime provenance. No time
restriction, missing software, tiny pixel edit or hidden diagnosis is a source
of difficulty. Keep all previous runs/frozen tasks unchanged. No automatic
Terra trials this round: current target is Sol/xhigh and clinical review.

## Source leads

- [TotalSegmentator](https://zenodo.org/records/10047263): retained source CT
  for the local failure. Original labels are not a documented surgical history.
- [ColonVessels](https://zenodo.org/records/17407158) and its
  [data paper](https://doi.org/10.1038/s41597-026-07303-2): surgeon-authored,
  senior-surgeon-verified vessel masks. Inspect real files: the article describes
  both per-structure anatomy and binary foreground labels, so do not assume
  branch identities exist. Arterial and venous scans were not registered.
- [Postoperative pancreas study](https://pubmed.ncbi.nlm.nih.gov/41307673/):
  relevant clinical morphology, but availability of the cited IMPACT resource
  has not been established. Do not invent postoperative context for local cases.

These external studies concern specialist segmentation models and expert data;
their errors are not Sol/xhigh outcomes.

## V01 admission before model results

Actual Slicer NRRD headers contain named branch masks, despite the article's
binary-label summary. Inspecting the first archive patient, pat_016, found 28
nonempty arterial sublabels and 24 nonempty venous sublabels. The absent Henle
trunk mask is excluded. Original compressed mask members were fetched with ZIP
CRC verification; header-only inspection did not claim full-file verification.

Admit one eight-target venous recognition diagnostic, using source segment
numbers 1, 2, 3, 5, 6, 7, 12 and 21 in the same venous phase. Each target is over
1.5 mL and spans more than 50 mm along at least one axis. Preserve full target
voxels, the surrounding venous mask and native CT sampling; crop only empty
mask margins and CT coverage outside the venous bounding box plus 20 mm. Supply
the exact eight names and explicit terminology. No fabricated lesions, splits,
swaps, clinical histories or forced tiny-boundary judgments.

This is a new source patient, with reviewer questions for o307, o609 and o570.
The author key is separate from the review packet. The published source supports
the reference identities, but template metadata still marks segments
in-progress; treat that as an unresolved source-review caveat rather than
inventing a second validation. One Sol/xhigh trial follows matched controls.
Retire a pass; hold any miss until source fidelity and the user's sampled
inferability review have been examined. An eight-class mapping is a compact
deliverable; no broader full-tree labeling task is added if this one passes.

## Disposition

C01 passed 11/11; V01 passed 8/8. Each had one normal Sol/xhigh completion after
matched oracle/nop controls. No Terra trial was run. The user declined to assign
the three review targets after seeing the packet, explained that the task was
beyond their experience, and authorized proceeding with author judgment. Record
zero completed human reviews; neither a human failure score nor clinician
solvability follows. V01's model outcome was disclosed after that decision.

The later source-access screen is recorded in the results. It did not admit
another task or trigger an additional model attempt. Prior admission text and
all frozen task bytes are preserved.
