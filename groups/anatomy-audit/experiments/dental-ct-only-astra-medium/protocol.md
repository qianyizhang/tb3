# CT-only dental segmentation: one Astra/medium attempt

**Closed — 2026-09-22 closeout (assistant).** The authorized attempt and saved-output
review are complete; see the [final finding](../../findings/dental-ct-only-astra-medium.md).
The dated preparation and supervision instructions below are retained history,
not an active queue or authorization to dispatch again. Original scores and
reference-review issues remain unchanged.

Authorized by the user in codex://threads/01a0c25e-4b08-7552-8379-90a2b50ad40f
on 2026-09-21: regenerate the GT from original CT, without methodological or
scoring hints, and babysit/report progress. This supersedes the earlier proposed
mask-correction task. It is a new exploratory study, not submission qualification.

## Condition and limits

One independent `openai/gpt-6-astra`, reasoning `medium`, Codex 0.155.1 attempt on
F_018. Assistant-selected ceiling: 7200 seconds agent execution, four CPUs,
12 GiB memory, no GPU, no automatic retry/continuation/extension. The original CT
array and affine are unchanged; descriptive NIfTI text fields/extensions are
removed and its name is `ct.nii.gz`. The F_018 **official viewer** CT/GT pair is
used together because its geometry differs from the archived image header.
Input provenance and exact equality are in the local preparation receipt.

Solver inputs: original CT voxels, complete dataset-wide semantic label mapping,
and neutral output contract. No original patient/case/dataset names, GT-derived
counts, known findings, visual annotations, prior reviews, segmentation algorithm
suggestions, scoring formula/thresholds, GT file, or evaluator code. No inherited
conversation or other model result. The answer is a full-grid integer NIfTI plus
method/uncertainty notes. The mapping is necessary task specification, not a hint
about which labels occur in this case. No corrupted/input masks are supplied.

## Isolation and evaluator

Fresh scientific runtime copies only installed libraries from an existing image,
not its /app or datasets. Solver build context contains CT + semantic IDs only.
Evaluator and oracle references stay in separate task directories/images;
Harbor separate-verifier mode starts after solver completion. There is no host
repository or Docker socket mount. Containers drop Linux capabilities. A Docker
internal network blocks direct egress; a separate CONNECT proxy permits only
chatgpt.com, api.openai.com and auth.openai.com port 443. Built-in web search is
disabled by the CLI wrapper. This custom enforcement uses Harbor's `public`
network-mode declaration because Docker's built-in allowlist is unsupported;
actual restricted topology must be checked by network inspect and live probes.
The proxy routes via the user's existing transport, and logs host decisions only.
No credentials are placed in authored records. Model authentication uses the
existing account via Harbor's standard auth injection.

Preflight must prove reference paths absent, no repository/socket mounts,
dataset hosts rejected, direct internet/host-proxy connection rejected, and model
transport available. Capture live model container topology after launch too.
This establishes bounded access controls, not absence from model pretraining or
immunity to every possible covert channel. Audit actual tool/transport traces.

Private frozen metric: per-class voxel Dice for all 77 nonbackground classes;
exclude classes empty in both GT and prediction, score false-positive-only
classes as zero, arithmetic macro average across the remaining classes. Also
report every class, geometry validity and foreground occupancy Dice. No clinical
pass threshold; continuous reward is not a binary benchmark verdict. Clinical
GT completeness is unadjudicated. Validate exact-reference=1, empty=0, missing
output=0, wrong-grid/unknown-label rejection. Test oracle and nop through the
actual Harbor lifecycle before the model. Keep GT and scores out of the attempt.
No operator changes to the model's output or methodological messages mid-run.

## Supervision

A thread heartbeat checks every 15 minutes and reports concise observed progress,
meaningful changes, completion or failure. No scored feedback is returned to the
solver. Read-only process/log checks are allowed; bounded infrastructure repairs
before inference are allowed. After model work begins, do not create a fresh
replacement or add time without user authorization. Preserve interrupted work.
Quota reserve: stop only the verified owned run if reported account remaining
reaches 20%; initial account remaining was 95%. Polling is approximate. Never
redeem reset credits or purchase quota.

Raw preparation, image IDs, isolation receipt, control logs, launch state and
operator handoff are under `.local/dental-ct-only-astra-medium/`. Common `med run`
creates canonical freezes/attempts and collects results under `.local/attempts/`.
No F_002 trial is launched because its reference acquisition remains incomplete.

## Launch observations (assistant, 2026-09-21)

The frozen task passed private scorer controls and actual Harbor oracle/nop
controls. An initial invocation failed authentication before any model output;
Docker's preservation of host credential ownership conflicted with dropped
capabilities. An offline login-status probe reproduced the defect and verified a
temporary-file permissions repair. Its original error remains retained. A second
invocation with identical task digest began actual Astra/medium work at about
08:59:14 UTC. This is one model attempt plus one pre-inference infrastructure
failure. No solver input, runtime image, network restriction or scorer changed.
The active heartbeat and full operational handoff are recorded locally. No result
or clinical-performance claim is made while the attempt is running.
