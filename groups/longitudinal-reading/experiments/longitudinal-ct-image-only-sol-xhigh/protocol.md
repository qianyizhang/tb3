# Image-only longitudinal CT — Sol xhigh

Model: `openai/gpt-5.6-sol`; reasoning effort: `xhigh`.

## Frozen question and user selection

Can an agent discover and segment lesions in two full CT volumes, then recover
longitudinal identity and events without any masks or case-specific lesion hints?
The user selected this hardest condition on 2026-09-22 and explicitly requested
Astra medium and Sol xhigh. This is one exploratory patient-pair comparison, not
population validation or promotion. The earlier marked-target recommendation was
superseded by the user selection (decision-af91b921939e40bd).

## Inputs, reference and boundaries

Both conditions share one exact frozen task. Solver input is only the full native
CT pair, neutral filenames and the generic instruction/format example. No source
patient ID, dataset name, location hints, counts, masks, patient metadata or event
expectations enter the solver image. NIfTI free-text fields/extensions are scrubbed;
voxel values and geometry are unchanged. Installed NumPy/SciPy/nibabel/skimage and
Codex are available, with no additional pretrained weights or downloads.

Private author provenance: Longitudinal-CT v3 reviewed case 0a09c8844b, selected
before inference for interpretable images, native mask alignment and clear CSV
linking flags. Source masks and graph remain unchanged in a separate verifier.
This pair contains persistence and merging; it cannot test new/disappearing events.
The four-pair acquisition, source terms, geometry and defacing caveats are recorded
in ../../examples/longitudinal-ct-review-20260922.md. The source aims for exhaustive
malignant-lesion annotations without a minimum size cutoff. Suspected annotation
disputes require review, while frozen numerical FP labels remain unchanged.

## Execution and controls

One fresh attempt per condition, no automatic retries, resume, example masks or
feedback from the other condition. Astra medium runs first; Sol xhigh runs second
because Docker has four host CPUs and about 7.74 GiB actual RAM. Each agent may
use 7200 seconds; Docker ceilings are 4 CPUs/12 GiB/0 GPUs, not guaranteed physical
allocation. The verifier has 600 seconds. Native med freeze/run/collection retains
all execution evidence. Check account usage before each dispatch; no reset credits
are authorized. All preparation, images, masks and raw runs stay in .local.

Check exact-reference oracle success and no-op failure on the final digest. Local
synthetic checks cover ID permutation, wrong links with correct masks, tiny masks
with correct localization, missed/extra lesions, empty output, new/disappearing
events and malformed outputs. Check solver-only files, private-path absence,
internal networking and transport restriction before inference; record live image,
mount/network/capability inspection and transport access logs during each run.

## Independent endpoints, fixed before inference

- Detection/localization: one-to-one match when a predicted mask centroid is inside
  a reference lesion or within 3 mm of its labeled voxel centers in physical space.
  Maximize match count then spatial similarity; report visit-specific TP/FP/FN,
  precision/recall/F1 and centroid error. This exploratory tolerance is fixed before
  output inspection. Also report IoU matching sensitivity at .10, .25 and .50.
- Segmentation: foreground Dice and GT-macro best one-to-one instance Dice (misses
  zero), plus localization-anchored and detected-only instance Dice. False positives
  are retained in foreground agreement and detection precision.
- Links: compare cross-visit edges after detection-based ID mapping, with arbitrary
  local mask IDs. Report end-to-end P/R/F1; separate conditional scores restricted
  to fully detected GT endpoints with explicit eligible/total denominators.
- Events: exact typed lesion-group P/R/F1, per event class and conditional on all
  members being detected. `unresolved` makes no correspondence claim. Absent event
  classes have undefined recall, not perfect scores.
- Contract validation is separate. Harbor reward=1 means required artifacts are
  well formed, not clinical success. Invalid events retain valid mask metrics;
  partial/timeout/infrastructure outcomes are distinguished from complete attempts.

Frozen scores will be independently replayed on saved predictions. Review useful
native image evidence and annotation disputes separately; do not alter frozen GT
or tune the scorer after seeing an answer. No universal composite/pass threshold
is defined, and this pair cannot establish general medical-agent capability.

## Findings

Both authorized fresh attempts completed normally. All original metrics replay
exactly from saved outputs. See [the comparison](../../findings/longitudinal-ct-image-only-comparison.md)
and [exact evidence](../../findings/evidence/longitudinal-ct-image-only-comparison.json).
Astra localized 2/6 reference instances; Sol submitted empty masks and localized
0/6. Artifact validity is separate from these scientific outcomes. The instance
convention review below remains open.

## Instance convention question recorded during first attempt

At 00:22 UTC, after Astra had independently described the abdominal region as
confluent, a private geometry check found that baseline GT labels 1, 2 and 4
form one 6-connected component. This does not establish radiologic confluence or
prove an annotation defect. It raises a convention question for the generic
instruction “A confluent region is one instance.” Both experiments are marked
needs review for instance/event interpretation; no frozen bytes or scores change.
Sol will run the identical task with diagnostic origin because this question was
known before its dispatch. No Astra output, GT clue or updated instruction reaches
Sol. Foreground overlap remains descriptive, and original fine-instance metrics
will be reported with this caveat pending appropriate adjudication.
