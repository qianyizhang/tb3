# BR-023 — Sol/xhigh registration strategy and component effects

Status: protocol fixed before the new model attempt.

## Request and unchanged task

In the owning [research task](codex://threads/01a0a845-7c2d-7992-a662-24d52831af90),
the user asked: “try another with sol-xhigh and investigate its approach, and
their impact on the success”. Exact message IDs are not exposed. This authorizes
one fresh Sol/xhigh attempt on the frozen BR-021 2D respiratory-correspondence
task, plus a bounded investigation of its actual strategy. It does not reopen
the retired task as a reliable-difficulty claim or authorize new patient curation.

Keep the same eight queries, source view and nominal frame, destination CT,
public prompt, numerical tools/network access, 4 CPUs / 4 GB RAM, 1,800-second
agent limit, and RMS ≤3 mm / maximum ≤5 mm acceptance. No earlier answers,
solver code, analysis, debugging hints or follow-ups enter the model session.
The selected model is `openai/gpt-5.6-sol`, reasoning effort `xhigh`, one attempt,
zero automatic retries. Run matched oracle/nop controls first. Infrastructure
errors or timeouts are separate outcomes, with no automatic replacement trial.

## Predeclared analysis

1. Audit the initial image, frozen task membership, model/effort runtime context,
   source/annotation access, downloaded tools and normal completion. Independently
   regrade the final submitted coordinates. Distinguish use of installed numerical
   libraries from downloading a task-specific solver or reference annotations.
2. Reconstruct the executed solver and decision sequence from the retained trace.
   Recover available intermediate candidates, parameters, similarity scores and
   visual selection decisions. Classify initialization/search support, image
   context, local motion model and final verification. Separate observations
   from explanations inferred from them.
3. Before any new counterfactual solver outcomes, freeze a second-stage intervention
   specification based on the observed implementation. Include an exact replay
   where technically possible and at most four single-component changes. Prefer
   removal of a component actually used by the model (for example local deformation,
   large context, broad initialization or visual candidate override), keeping other
   settings and candidate-selection rules unchanged. Do not add a new competing
   solver family or tune parameters until hidden scores improve. If a manual
   decision cannot be reconstructed faithfully, report that limitation.
4. All recovered solvers and counterfactuals execute with public inputs only, no
   network and no private-label mounts. Hidden labels enter grading and explicit
   offline geometric/objective diagnostics only. Keep every fixed intervention
   outcome. A replay mismatch limits causal claims and must be resolved or reported
   before interpreting component effects.
5. Compare the Sol trajectory and component effects with the recorded Terra
   trajectories from BR-021/022. Do not treat one Sol attempt versus selected and
   repeated Terra attempts as a controlled estimate of relative model ability:
   model, effort and strategy differ, and only one patient is represented.

The component selection is necessarily post-trace and may be informed by the
known original outcome. The second-stage freeze prevents subsequent selection
of favorable counterfactual results; it does not make those hypotheses fully
prospective. Author-run interventions are not additional autonomous agent runs.
No additional model attempts or stronger-model escalation are scheduled.

## Ownership

New raw jobs and analysis belong under `runs/br023-*`; new code uses
`probes/registration-deformation/authoring/br023_*`. New authored plans, results
and allowlisted receipts use `docs/research-rounds/BR-023-*` and
`docs/evidence/br023-*`. Preserve all BR-019/020/021/022 freezes, reports, receipts
and raw evidence; do not edit the closed interview site or sibling submission.
