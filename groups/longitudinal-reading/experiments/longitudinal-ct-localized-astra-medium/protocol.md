# Conditional localized recognition probe — Astra medium

The user authorized this narrower test if the revised whole-volume attempt still
missed a lesion. [Source](codex://threads/01a0c4d1-741f-76e3-9023-1064e5a9a0c5).
The prospective trigger and selection rule are in the
[whole-volume v2 protocol](../longitudinal-ct-v2-astra-medium/protocol.md).

Whole-volume attempt `attempt-4749bbfb347f4809` completed normally. Independent
replay reproduced every metric exactly; reference label 3 had zero foreground
coverage at both visits. It is the selected persistent group under the declared
rule. The other reference lesions had substantial coverage and are outside this
localized probe. This selection is author-side; the solver receives no prior
trace, score, source label, disease, anatomical label, mask or guaranteed-positive
statement.

One fresh `openai/gpt-6-astra`, effort `medium`, attempt, with no retry/resume.
Same full native CT pair, pinned solver/runtime/transport, tools and two-hour cap.
The information deliberately added is a native-coordinate candidate center in
each visit, labeled R01/R02. The task asks for explicit tumor/normal-or-benign/
indeterminate judgments with image evidence, and masks/events for candidates
judged tumor. Every other finding is out of scope. Candidate points are the
reference voxel nearest the centroid; this is explicit localization assistance.

The new private reference retains only selected labels and their persistent
event. Original references and scores are unchanged. The exact v1 mask/link/event
scorer is retained as `base_score.py`; a small wrapper validates candidate
judgments and reports acceptance relative to these positive references separately.
Zero masks are valid if accompanied by valid negative/indeterminate judgments,
empty events and a report. Specificity is undefined: no negative control is
included. The updated private evaluator is built from the same existing runtime,
without installing or downloading models. A new freeze and oracle/no-op controls
precede inference; synthetic judgment-validation checks are retained.

Interpretation: recognition/segmentation after localization supports a search or
attention contribution to the whole-volume omission, while direct rejection of
the indicated structure supports an interpretation/inclusion disagreement with GT.
Acceptance with poor boundaries supports a segmentation bottleneck. The added
point also changes attention, presentation and prior belief, so this adaptive
single-group probe cannot prove that search is the sole cause. It is neither an
independent case nor a whole-volume score or clinical malignancy adjudication.
