Source: `docs/research-rounds/BR-024-rescue-plan.md`; original SHA-256: `48638e9dfc8993f1b50bbc5c6cb64cec4ad4f2a82db58afb3924f05a799dc715`.
Repository source locators below are provenance; they are not required runtime inputs.

# BR-024 — bounded public-input feasibility rescue

Fixed after the six unchanged local-affine baseline outcomes, before these
rescue outcomes or any new model trial.

The unchanged baseline fails on all six predeclared candidates. On each
patient's first view it misses one landmark beyond 5 mm, despite matching the
remaining points reasonably. Source/reference panels show visible anatomy;
this does not by itself certify unique correspondence or solvability.

Run the already implemented BR-022 **translation-only, multiscale** variant,
unchanged from that round, on the ranked candidate list. This removes the
local affine degrees of freedom while retaining broad initialization, context
schedule 25/16/10 mm, blur, optimizer and candidate selection. Its code and
parameters predate this new-patient screen. No new score function, per-query
initialization, hand-picked output or label-based candidate ranking is added.

Use the same isolated public-input runtime, no network or label mounts. Retain
all outputs; stop on the first passing candidate per patient, pending visibility
and isolated task-image checks. Source query sets and the original ranking
remain frozen. A failure remains unqualified until a permitted method solves
the instance; it is not automatically a Sol difficulty claim.
