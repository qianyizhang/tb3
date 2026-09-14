# Sequential experiments from Brainstorm New Tasks

Requested 2026-09-14. Reference: ChatGPT conversation
`6aa74ac6-4190-83ee-9eaf-603e1ae6ab9e`, “Brainstorm New Tasks”. Its first
four specifications were retrieved; the cached final response truncates during
E05. These are proposed original extractions, not inherited benchmark failures.

## Protocol fixed before trials

Process E01–E04 sequentially, then evaluate the two reserves E05–E06. Complete
the current experiment's controls, freeze, diagnostic and interpretation before
launching another candidate. Each ready candidate gets one Harbor 0.14.0
Docker Codex / `openai/gpt-5.6-terra` / high diagnostic with 1,800 seconds.
A healthy pass retires the snapshot. A zero requires independent reproduction,
task/verifier review, and classification before at most one same-freeze repeat.
No Sol/Opus or adversarial runs belong to this round. No shorter reasoning
budget, library prohibition, or unrelated extra cases will be used to turn a
pass into a failure. Internet remains available. Model runs use the existing
explicit subscription proxy configuration in `docs/setup.md`.

Before a model run: validate fixtures and numerical tolerances; demonstrate a
strong permitted baseline; reject targeted incorrect controls; run matching
Harbor 0.18.0 oracle (1) and nop (0); retain task hash, file digests, inputs,
commands and versions. Keep raw runs under ignored `runs/`. Record execution
health, task success and support for the proposed hypothesis separately. A
syntax error does not establish a conceptual misunderstanding. Infrastructure
errors, timeouts and source/oracle faults do not count as model failures.

| ID | Deliverable and hypothesis | Independent evaluation | Initial status |
| --- | --- | --- | --- |
| E01 | Reconstruct a synthetic MR acquisition; storage order may be confused with metadata association | Canonical samples and physical landmarks generated before serialization; equivalent encodings; metadata profile audit | Retired: Terra passed 36/36 |
| E02 | RT0 face-flux velocity on a planar quadrilateral; flux may be treated as scalar velocity | Manufactured reference-coordinate values plus physical-edge quadrature | Retired: Terra passed 72/72 |
| E03 | First derivative of a separated spectral projector; arbitrary eigenbasis may be differentiated | Cross-subspace analytical VJP plus directional differences at several step sizes | Retired: Terra passed 24/24 |
| E04 | Calibrate one fixed affine two-channel instrument under clamps; observational fitting may replace intervention testing | Independent structural equations, logged measurements, held-out settings | Retired: Terra passed 20/20 |
| E05 | Canonical stress from extxyz stress/virial labels; round trip may hide physical change | Canonical tensor, determinant volume and rotated equivalents | Retired: Terra passed 36/36 |
| E06 | Derivative through one nongrazing collision; event-time dependence may be omitted | Analytical event trajectory plus directional differences with stable event count | Reserve; reproducer first |

The reference's E01 acquisition dimensions, E02 element definition, E03 open
selection gap, and E04 fixed-instrument semantics are part of the public
contract. Author hypotheses and private expected outputs stay outside agent
images. Any scoped design deviation is recorded before the corresponding
freeze. Final submission gates remain owned by `docs/requirements.md`.

## Source audit

Public release metadata was fetched at OpenMOSS/SWE-bench-Science commit
`5f7871f9f8541998a1730bd825f59d8102b58a88`. Tasks 037 (NiBabel), 036 (Parcels)
and 003 (dpdata) match the referenced subjects. Each is marked
`science_knowledge_ablation: true`. The live matrix's seven displayed
configurations are seven configurations, not repeated attempts. Its zero
Pass@1 entries are source leads until trace health, failed assertions and
historical digests are audited. The source's 5,400-second allowance and disabled
Internet are not copied into our original pilot. Raw downloaded metadata,
instructions and trace material are in `.cache/brainstorm-20260914/`.

Sources: [release](https://github.com/OpenMOSS/SWE-bench-Science/tree/5f7871f9f8541998a1730bd825f59d8102b58a88),
[task matrix](https://swescience.github.io/task-matrix/gradient/),
[DICOM dimension indices](https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.7.6.17.html),
[functional groups](https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.7.6.16.html).

Starting local denominator: six valid Terra/high passes, zero genuine failures,
two earlier infrastructure-only attempts. This round does not rewrite prior
freezes or research conclusions.

### Retrieved source receipts

The three normalized Sol/max traces are now cached and their allowlisted
receipts retained in `docs/evidence/brainstorm-source-receipts.json`. All have
agent return code 0 and completed pytest verification. MRI: 10/13 private
tests, 1,116.464 agent seconds. Ocean grid: 8/9, 1,026.770 seconds. Tensor
conversion: 3/6, 429.300 seconds. The normalized traces do not expose a
historical task checksum; current release image digests are not substituted.

The specific misses narrow the brainstorm's interpretation. MRI's failures
are redundant singleton axes, duplicate-plane rejection, and single-frame
support. The ocean-grid miss is nonfinite vector sampling at near-polar
coordinates. The tensor misses include an explicit sign option, force-column
parsing, and direct API/write-roundtrip behavior. These are published verifier
misses with normal agent completion, not proof of the proposed miniature's
failure mechanism or independently audited fairness of every source assertion.

## E01 result

[MRI summary](evidence/mr-trial-summary.json): one clean Terra/high pass,
36/36 cases, 150.284 seconds of agent execution, 206.823 seconds total.
Matching v1 oracle/nop controls returned 1/0. The immutable source still
matches its freeze. H01 is not supported. The snapshot is retired; E02 is next.
Current local denominator after E01: seven valid Terra passes, zero genuine
failures, two historical infrastructure-only attempts. The temporary automatic
approval block was resolved by inspecting the synthetic/public agent payload;
it did not execute a model attempt.

## E02 result

[Face-flux summary](evidence/quad-trial-summary.json): clean Terra/high pass,
72/72, 34.529 agent seconds and 91.451 seconds total. Matching controls returned
1/0. The agent directly implemented the declared Piola mapping; H02 is not
supported. All eight base cells and their flux/rigid-transform variants passed.
Current local denominator: eight passes, zero genuine failures, two historical
infrastructure-only attempts. E03 follows without adding difficulty to E02.

## E03 result

[Projector summary](evidence/projector-trial-summary.json): clean Terra/high
pass, 24/24, 102.691 agent seconds. The custom VJP uses only cross-subspace
gaps; H03 is not supported. Analytical, finite-difference and Linux controls
agree. Current local denominator: nine passes, zero genuine failures, two
historical infrastructure-only attempts. E04 proceeds with a separate
instrument service, fixed coefficients and unrestricted measurements.

## E04 result

[Instrument summary](evidence/instrument-trial-summary.json): clean Terra/high
pass, 20/20, 48.682 agent seconds. Its 42 recorded measurements include both
clamp directions and extra held-out-style checks; the resulting predictor
matches the structural equations. H04 is not supported. Matching service
oracle/nop controls returned 1/0. The four primary ideas are complete; the two
reserves follow. Current local denominator: ten passes, zero genuine failures,
two historical infrastructure-only attempts.

## E05 result

[Stress summary](evidence/stress-trial-summary.json): clean Terra/high pass,
36/36, 27.022 agent seconds. The direct correction uses standard Voigt order,
negative virial sign and absolute determinant volume, with no basis change.
H05 is not supported. The initial unavailable Linux package pin was corrected
and all host/Linux controls repeated before the freeze. Current local
denominator: eleven passes, zero genuine failures, two historical
infrastructure-only attempts. E06 is the final reserve in this round.
