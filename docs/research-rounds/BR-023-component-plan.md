# BR-023 — fixed component interventions

Fixed after observing the Sol pass and its completed solver/decision trace,
before executing or grading these new variants. This is a post-trace mechanism
investigation, not a prospective model comparison. The user-authorized
[protocol](BR-023-sol-registration.md) caps the investigation at four component
changes.

## Observed implementation

The final submission copies the first setting printed by command `item_26`:
translation-only Powell refinement around eight public-derived voxel starts,
with patch radii 5/7/9 pixels, weights .4/.35/.25, and ±3 voxel bounds per axis.
The model rounds world coordinates to two decimals. It previously explored
local affine patches but does not use their extra basis parameters in this
final stage. q04's starting point evolved from raw highest-NCC candidate
[126,79,118], to the third-ranked chosen candidate [146,84,103], then to
neighborhood-informed [139,86,105]. All are recorded model choices from public
images, not author-selected label-based initializations.

## Conditions, fixed now

| Condition | Change from final stage | Question |
| --- | --- | --- |
| Final-stage replay | Literal item_26 first setting, instrumented only | Does the recovered calculation reproduce the submitted coordinates? |
| Earlier chosen q04 | Only q04 start becomes [146,84,103] | Did the later neighborhood-informed reseeding matter beyond the initial candidate override? |
| Raw highest-NCC q04 | Only q04 start becomes [126,79,118] | What happens if q04 follows the coarse correlation ranking? |
| Single small patch | Radii/weights become [5]/[1.0], same starts and optimizer | Is the final multiscale score necessary once the correspondence region is chosen? |
| Stop before final refinement | Return the eight final starts in world coordinates | What does the last refinement add, conditional on earlier matching and refinements? |

All other settings remain identical, including clipping, interpolation,
normalization, world conversion, rounding and query order. Powell is
deterministic here; no random seeds are introduced. Each condition runs once
in the retained initial Sol image, no network, four CPUs, 4 GB RAM, only
read-only recovered code and entrypoint mounts plus a dedicated output mount.
No ground truth or verifier directory is mounted. Every condition is retained.

This replay covers the final numerical stage. It does not replay the model's
visual reasoning or independently regenerate its earlier choices. The two q04
changes are conditional interventions on its start; they do not simulate all
downstream decisions an autonomous agent would make after choosing another
candidate. Stopping at the final starts retains information from previous
refinements, so it is not a no-optimization baseline for the whole task.

Require replay agreement with the submitted two-decimal coordinates before
interpreting these changes. Retain and report any mismatch; do not tune the
solver using private scores. Hidden labels enter only independent grading and
explicit geometric diagnostics such as distance to the final search box.

Also regrade the already recorded local-affine exploration at each of its
three regularization settings (.05/.2/1), retaining all settings. These are
descriptive stage comparisons: their starts and patch scores differ from the
final stage, so they do not isolate an affine-model effect. Inspect the trace
for how surrounding matches informed q04. Do not convert its narrative of
unique correspondence into a validated uncertainty estimate.
