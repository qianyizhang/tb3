# Designing medical capability research

Start with `uv run med list QUERY`, the owning group's README and AGENTS.md, and
its existing ideas and findings. Capture useful discussion in an existing idea
card or a new stable ID, with the source task, prior findings, decisions and
reopening condition. Use the [workflow](workflow.md) to record accepted decisions
separately from assistant recommendations.

## State what the study can teach

Name the medical task and what the agent must infer or produce. Describe supplied
information explicitly: an image alone, a segmentation, branch geometry, an atlas,
a prior report and an expert reference are different conditions. A small exploratory
study can be valuable without being difficult enough for a benchmark submission.

Choose observable outputs and comparisons that address the question. Specify
coordinates, units, field of view, available targets and acceptance semantics.
Keep the task fair; removing conventions or ordinary tools creates ambiguity,
not evidence of a missing capability. Inspect the complete solver-visible package
for hints, bundled answers and reference assistance before interpreting a result.

## Establish the reference and feasible evaluation

Record the exact source/version, sample selection, access and redistribution
terms, preprocessing and limitations in the group and experiment. A paper, public
benchmark or old source receipt is a lead until the selected inputs and reference
are actually available and suitable. Missing data and uncertain reference validity
are different problems.

Use independent scoring where possible, with a correct author solution and
incorrect controls that exercise the intended distinction. For medical images,
check the coordinate and geometry contract and whether the reference supports the
claimed anatomical interpretation. An oracle pass and no-op fail establish a
useful control contrast; they do not establish task difficulty or clinical validity.
Keep reference disputes under review until appropriately adjudicated.

A diagnostic run may precede controls when explicitly authorized. Define its
question, model/effort, inputs, tool/reference access, attempt budget and stopping
condition. `med run` generates the task snapshot and execution receipts; authors
do not need to maintain a separate freeze or plan record by hand. Historical
launchers and archived next actions do not authorize a new run.

## Interpret and retain the result

Distinguish what happened from what it supports: completed scoring, partial work,
a timeout, an infrastructure error, source assistance and a defective reference
are not interchangeable outcomes. A small or selected comparison does not establish
a population rate or causal explanation. Trace inspection describes observed
access and actions; absence of observed retrieval does not prove isolation.

Preserve original task bytes, outputs and scores. A corrected scorer, diagnostic
trim or later visual review adds an observation or assessment; it does not replace
the frozen outcome. Record concrete defects and scoped reassessments through the
[review workflow](workflow.md#review-conclusions). A code fix alone cannot restore
a conclusion. Explain successes and limitations together in the group finding
and story, with links to the supporting experiment and a static visual fallback.

For colored image overlays, supply a visible legend with the same colors and line
styles as the overlays; label the reference, prediction and prompt separately.

These guidelines retain lessons from the dated
[specification/scaffolding audit](../archive/README.md#recover-retired-files) and
[archived source-screening method](../archive/manifest.json), while
replacing the closed assignment's failure-first selection goal. Their old counts,
model matrix and proposed next actions are historical. Submission-specific
requirements are assessed only at [promotion](submission.md).
