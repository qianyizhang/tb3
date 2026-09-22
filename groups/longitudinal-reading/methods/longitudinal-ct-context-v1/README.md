# CT clinical-context experiments

The [protocol](protocol.md) defines two authorized fresh Astra-medium conditions
on the already acquired second Longitudinal-CT case. Neither condition reads the
other's outputs. Source data and raw runs remain local; tracked records retain
provenance and hashes. The existing case02 image-only attempt is the comparator.

## Preparation and execution

`prepare.py` requires the verified baseline task freeze and acquired demographic
CSV. It creates a new `.local/longitudinal-ct-context-v1` root and refuses to
overwrite it. It verifies the complete baseline task manifest and patient row,
then copies the task into `inference/` and `supplied/`. No historical preparation
module is imported or run. Both reuse the pinned case02 solver image containing
only the two cleaned CTs. The supplied condition reuses the exact case02 private
evaluator; inference builds a schema-only private evaluator from the pinned
existing runtime. Pin the resulting image ID in its task TOML and image manifest
before freezing. No runtime installation or network data download is required.

`preflight.py {inference,supplied}` checks the exact image identities, file
allowlist, absence of private/host mounts, blocked data/model endpoints and
transport configuration; it writes an immutable task-file manifest before the
native controls. Run native `med run EXPERIMENT --agent oracle` and `--agent nop`
controls, inspect their rewards, and save `med run --preview --diagnostic` output
as each condition's `study.json` with its `experiment_id` and `task_digest`.

`run_condition.py {inference,supplied}` dispatches one native attempt using a
fresh model session, live ordinary-usage clearance, and a dispatch-once marker.
It refuses concurrent task containers, checks live image/mount/network/resource
isolation, retains transport observations, and does not automatically retry.
Credentials are copied temporarily for transport and removed after execution;
they are never experiment artifacts. These commands execute trials and require
explicitly selected research scope; they are not maintenance checks.

## Analysis

`audit.py {inference,supplied}` reads saved terminal evidence and counts image
observations, tool calls and permitted/blocked transport destinations. An image
observation does not prove the model attended to each displayed feature. A
source-string search is supplementary evidence, not an isolation guarantee.

`analyze_supplied.py` independently replays the frozen lesion scorer, compares
saved scores, reports predeclared GT size strata, and renders native CT/reference/
prediction views into a new analysis directory. It requires the verified case02
geometry JSON copied under the supplied condition's author-only review folder.
Clinical context does not change reference labels or scoring. The inference
validator's reward is only schema/report validity; assess the actual claims,
uncertainties and evidence separately, field by field.

`compare.py` compares immutable per-reference identities and metrics and renders
the predeclared GT14 view. `trace_review.py` retains public statements, checks
reported exclusion points against private GT, and reconstructs native slice
coverage from explicit render commands without executing model-written code.
`plot_rejection.py` illustrates the newly observed GT2 rejection at the exact
reported coordinates; it is a post-hoc author figure. Use writable local
`MPLCONFIGDIR` and `XDG_CACHE_HOME` paths for these Matplotlib renderers.

The CT-only inference condition may legitimately leave exact diagnosis, recorded
demographics, dates and treatment history unknown. The context-supplied result
tests use of a restricted background block, not access to the unreleased clinical
reports. One patient and one new lesion attempt cannot establish causal effects.
