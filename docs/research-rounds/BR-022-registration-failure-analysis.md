# BR-022 — systematic analysis of the BR-021 single-view failure

Status: analysis plan fixed before new counterfactual outcomes or model runs.

## Request and scope

In the owning [research task](codex://threads/01a0a845-7c2d-7992-a662-24d52831af90),
the user annotated the statement that one implementation-error failure does
not establish reliable difficulty, and asked: “interesting, make this more
systematic and investigate the failure mode”. Exact message IDs are not exposed.
This authorizes a bounded postmortem and fresh replications of the existing
2D task, preserving BR-021 as the original completed record.

The selected anatomy, eight queries, public source frame, 3/5 mm tolerances,
task files, normal tool access and 1,800-second budget remain fixed. No new
patient selection, difficulty tuning or stronger model is included. The
original 3D pass remains a contextual control, not a repeated condition here.

## Questions and comparisons fixed before execution

1. **Replay fidelity.** Reconstruct the model's solver from its recorded shell
   code and execute it in the original initial task image using public inputs
   only, network disabled. Preserve the recovered code and source trace hashes.
   Compare its final eight positions to the retained submission; report any
   numerical drift before making counterfactual claims. Intermediate transforms
   were not retained as original artifacts, so their recreation is also checked
   against printed original coordinates/metrics where available.
2. **Transform composition.** The B-spline was fitted against the original
   moving image, but query evaluation applies `aff(bsout(x))`. Compare the
   original mapping with the minimal consistent evaluation `bsout(x)`, keeping
   the fitted transforms and other settings unchanged. Also measure the
   mechanically different, intended two-stage variant: fit B-spline against
   the affine-resampled image and then apply `aff(bsout(x))`. This is a
   secondary structural repair, not the minimal one-line comparison.
3. **Search support and optimization.** Cross original/minimally corrected
   mapping with ±9 mm versus ±30 mm local translation bounds, keeping the
   original patch objective, orientation construction and optimizer settings.
   Primary seed 17 matches the trace; seeds 41 and 73 assess optimizer
   variability. All outcomes retained. Wider bounds at a fixed evaluation
   budget are not an exhaustive search or a guarantee of optimality.
4. **Objective and geometric adequacy.** Offline only, evaluate the agent's
   patch objective at the manual target, its actual output and optimized
   candidates. Compute the closest point in each search box to the manual
   target: this yields a geometric lower bound independent of the optimizer.
   Hidden labels may enter these diagnostics and scoring, never a permitted
   solver initialization or candidate selection. Check stage-wise errors,
   local patch stability and whether objective improvement tracks accuracy.
5. **Patch model/context controls.** Use the already passing public-input
   author solver in a 2x2 comparison: translation-only versus locally affine
   2D-to-3D patches; small (8/8/8 mm) versus existing multiscale (25/16/10 mm)
   patch context. Keep its nominal-geometry initialization, broad candidate
   search, blur schedule and candidate selection rule fixed. These diagnose
   that baseline's mechanisms; they are not one-line repairs of the model code.
6. **Fresh agent repeatability.** Run two additional independent Terra/high
   attempts on the exact frozen BR-021 2D task. Same instruction, 1,800 seconds,
   ordinary installed libraries/network, zero automatic retries, no debugging
   hints, prior solver code, earlier answers or private analysis. Use matched
   oracle/nop controls and audit runtime context, initial images, checksums,
   normal completion, external tools and reference-annotation access. Keep the
   original attempt as attempt 1; record the two prospective attempts separately.

## Interpretation rules

Report task validity, actual task outcomes and hypothesis support separately.
A composition error can be real while correcting it fails to rescue the
submission. A target outside a search box can explain an unrecoverable query;
a target inside it can still lose under an inadequate objective. Prefer the
smallest experimentally supported explanation; do not force all eight queries
into one failure category.

Public-input counterfactuals are author-run interventions on recovered code,
not new autonomous agent successes. Label-assisted diagnostics are privileged
analysis, not admissible solutions. Report all fixed seeds/conditions rather
than selecting the best hidden score. A small number of fresh attempts on one
selected case does not estimate general clinical or registration capability.
Crashes, provider errors and timeouts remain separate from completed misses.

Raw work belongs under ignored `runs/br022-registration-postmortem/` and new
`runs/br022-*` jobs. Authored extensions belong under
`probes/registration-deformation/authoring/` with `br022_` names; concise new
receipts under `docs/evidence/br022-*`. Do not alter old freezes, old result
receipts, the closed interview site or the sibling submission.

## Transform contract reference

The [SimpleITK CompositeTransform reference](https://simpleitk.org/doxygen/latest/html/classitk_1_1simple_1_1CompositeTransform.html)
defines reverse queue application: adding A then B evaluates A(B(x)). The
[registration overview](https://simpleitk.readthedocs.io/en/master/registrationOverview.html)
describes the fixed-to-moving physical-space mapping used for resampling.
The suspected defect concerns which image the B-spline was fitted against,
not simply swapping the order of two otherwise valid transforms.
