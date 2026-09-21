# F_002: original-CT-only Astra/medium

**Closed — 2026-09-22 closeout (assistant).** The authorized attempt and saved-output
review are complete; see the [final finding](../../findings/dental-f002-astra-medium.md).
The dated preparation and supervision instructions below are retained history,
not an active queue or authorization to dispatch again. Original scores and
reference-review issues remain unchanged.

User authorization, 2026-09-21: run Astra-xhigh on F018 and Astra-medium on F002,
preparing F002 with GT from the now-complete archive. Source task:
codex://threads/01a0c25e-4b08-7552-8379-90a2b50ad40f.

One fresh Codex 0.155.1 / openai/gpt-6-astra / medium attempt, up to 7200 agent
seconds, 4 CPUs, 12 GiB configured memory ceiling, no GPU, no automatic retries
or continuations. Actual Docker VM has 4 CPUs and about 7.7 GiB total memory;
these are sequential runs to avoid sharing the machine. F018 first, F002 after
terminal boundary review. Expected maxima are ceilings, not instructions to spend
unused time. Nothing from a previous model conversation or result is inherited.

The input is only original CT voxel data and its native affine, with descriptive
NIfTI text removed, renamed ct.nii.gz; plus the full dataset-wide semantic map and
neutral output contract. No case identity, per-case findings/counts, GT, score,
method suggestions, prior outcome or reference-convention hint reaches the solver.
The prior prompt, installed libraries and fixed private scoring formula are reused.
The original answer and every score are preserved. No output editing is allowed.

F018 uses exactly the previous viewer-based frozen task bytes, digest
5b82cd7964f6102486b1e4503e4c3e11611d21f75f164b536d32ba249d2bf928, to isolate reasoning
effort from fixture changes. Archive CT and GT arrays were confirmed equal to
that viewer pair, but the archive's z-affine differs. F002 uses its internally
aligned archive CT/GT pair, without changing the stored affine. Extraction reads
only selected ZIP members and checks their CRCs; it does not validate all 29 GB.
Source hashes, pair validation and QC are retained in .local/dental-followups-20260921/
and .local/dental-f002-astra-medium/.

The earlier experiment raised a source-header/semantic laterality question.
This remains unresolved; these are explicitly diagnostic exploratory runs.
Do not claim anatomical correctness/failure from identity disagreement alone,
or fix orientation by consulting GT before the solver. The primary metric remains
unaltered per-label macro Dice; any post-hoc permutation is reported separately.
Scorer controls for the identical F018 task remain retained. New F002 oracle/nop
and malformed-output controls must pass before its model run.

Separate private evaluator; solver network is internal and reaches only a
restricted model-service CONNECT proxy. Runtime images are pinned by identity.
No public dataset access, web search, repository/Docker-socket mount or shared
solver history. Verify actual container networks and mount scope. Retain transport
and tool traces; absence of observed retrieval is not proof about pretraining.

Use the babysit skill and the current task heartbeat. Check account usage every
15 minutes approximately; reserve 20% remaining, no resets or purchased quota.
Before F002, recheck the first run's terminal state, absence of live solver, exact
inputs and available quota. If a run has an infrastructure issue, preserve it and
review before any further dispatch. No extra attempts after inference begins.
Stop only verified owned processes on user stop or resource exhaustion; preserve
partial artifacts. Handoff and per-run operator state are local and contain
current process/trial identities. Final review independently replays private
scoring, audits access, reports actual elapsed/tokens and pauses the monitor after
both runs are terminal. No publication or submission is authorized.
