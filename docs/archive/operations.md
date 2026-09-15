# Historical operating records

[Research archive](../archive.md) · [Current reproduction guide](../reproduce.md)

These records preserve completed setup/pickup history and the former round
authoring template. Status statements and proposed next actions describe their
original capture dates. They are not current instructions to resume research.


## Codex CLI repair

Date: 2026-09-12

### Diagnosis

The global Node installation at `/Users/zhangqy/.nvm/versions/node/v25.9.0`
contained `@openai/codex@0.147.0`, but its platform-specific optional runtime
package, `@openai/codex-darwin-arm64`, was absent. As a result, both `codex
--version` and `codex login status` stopped before starting and reported the
missing optional dependency.

The npm configuration did not omit optional dependencies, and the machine is
`arm64` macOS.

### Repair

The official OpenAI documentation installs the CLI through npm as
`npm -g i @openai/codex@latest`. To repair the existing pinned installation
without changing its version, this command was run with optional dependencies
explicitly included:

```bash
env -u HTTPS_PROXY -u HTTP_PROXY -u ALL_PROXY \
  NPM_CONFIG_INCLUDE=optional \
  /Users/zhangqy/.nvm/versions/node/v25.9.0/bin/npm \
  install -g @openai/codex@0.147.0
```

It completed successfully, adding the missing
`@openai/codex-darwin-arm64@npm:@openai/codex@0.147.0-darwin-arm64` package.
No files under `~/.codex` were edited or removed.

### Verification

```text
codex --version       -> codex-cli 0.147.0
codex login status    -> Logged in using ChatGPT
```

The CLI emits a non-fatal warning that it cannot create PATH aliases due to an
operation-permission error. The existing NVM executable remains callable at
`/Users/zhangqy/.nvm/versions/node/v25.9.0/bin/codex`, and version and login
status both completed successfully. No model trial was part of the CLI repair; later Harbor trials are recorded in ledger.md.

Source: [Official OpenAI Codex installation example](https://developers.openai.com/cookbook/examples/codex/secure_quality_gitlab)


## Geometry pickup

Source task: `01a093fe-a6bb-7ef0-a1ca-da3b39e5aee2` (Set up tb3 and brainstorm tasks).
The source task is stopped with a platform flag; its saved files and completed
trials remain available. The user explicitly requested continuing in another
domain and excluding security tasks. Do not resume the flagged research paths
or run adversarial trials in this pickup.

Live reconciliation: no Harbor, geometry experiment, or Docker build process
was active; Docker had no running containers. Docker/Compose/Buildx and
Harbor 0.14 are available. The prior four completed Terra/high passes are
retained. Research-turn interruptions are not benchmark failures.

Scope: computational geometry. Preserve the historical Clipper2 probe, freeze
its current tree, run Harbor 0.18 oracle/nop controls, then one Harbor 0.14
Codex Terra/high diagnostic with 1,800 seconds available. Inspect result and
trajectory; repeat only if a completed failure survives independent reproduction
and task-fairness review. Sol/Opus remain reserved. No final submission is being
claimed. There is no newly authorized unlimited run budget.

Root owns trial launches and ledger/catalog writes. A read-only explorer checks
geometry task validity independently. Existing uncommitted work from the source
task is preserved.

Current state: v3 is frozen in `docs/evidence/clipper-pilot-freeze.json` after
two pre-model authoring revisions. Same-snapshot oracle 1 / nop 0 completed
without exceptions. Terra/high completed as
`runs/clipper-terra-high-v3-20260912`: reward 1, no exception, 494.711 seconds
total and 421.371 seconds of agent execution. The same-snapshot controls and
model share their recorded Harbor checksum. No containers or Harbor processes
remain active; no background supervision is scheduled. Runtime logs remain
local under `runs/`. The first launch's automatic approval rejection was
resolved by inspecting the public-source payload and explicit OpenAI subscription
destination; see `docs/evidence/clipper-launch-scope.json`.

Parallel source research is complete in `docs/research-numerical-candidates.md`.
The next numerical lead is SciPy interpolation. Limited execution of unchanged
historical numerical blocks confirms an incremental-update sign inconsistency,
with source hashes and outputs retained in docs/evidence/. Full public-API
reproduction is still needed. Neither numerical lead has a model outcome.

Disposition: preserve the geometry probe as calibration; all five tested
candidates passed Terra/high. Do not spend Sol/Opus on this snapshot. The next
action is the bounded full-interface numerical reference check, then task design
only if independent controls support it. All source-task uncommitted work remains
preserved; this pickup does not commit or publish it.

Harbor reports 4,177,944 cumulative input tokens, including 4,044,800 cached tokens,
and 13,830 output tokens for the geometry model trial. These are adapter-reported
usage counts across turns, not unique task size or a subscription invoice.
The independent [trial review](../../catalog/analyses/clipper-calibration.md) records
the actual repair, observed local-source use, and coverage limits.


## Historical round template

Copy this file to `BR-NNN-short-topic.md`; keep the template unfilled.

### Intake

- Captured date; state; previous round; scope of the current work.
- Source conversation title/URL, turn and message IDs, retrieval completeness.
- New question or hypothesis; lesson from the preceding round.
- Evidence class: discussion claim / published outcome / audited source miss /
  local fixture check / local model trial. Link receipts; leave unknowns explicit.
- Selection authority and any unresolved change to the existing run protocol.

### Candidate queue

| Local ID / catalog ID | One crux and deliverable | State | Next bounded action |
| --- | --- | --- | --- |
| … | … | … | … |

### Candidate specification — repeat per candidate

- **Task contract:** interface/artifact, semantics, input domain, permitted tools.
- **Hypothesis:** expected discriminating failure and evidence against it.
- **Source relationship:** exact source task, audit status, difference introduced
  by the extraction; do not transfer source failure rates.
- **Fixtures:** control cases, discriminating cases, independent physical or
  semantic truth, smallest witness, unresolved ambiguities.
- **Evaluation:** public metrics/thresholds, independent oracle, strong permitted
  baseline, targeted incorrect controls, runtime/validity checks.
- **Inspection:** concrete artifact behavior, executed checks or observations
  that distinguish concept, implementation, task and infrastructure failures.
- **Ablation:** one changed information condition, what it isolates and confounds.
- **Stop rule and next action:** retire/repair/advance criteria; exact evidence
  needed to proceed. Mark proposed values that still need validation.

### Execution plan — fill before running

Record each condition's freeze/digests, versions, model IDs, effort, harness,
tool/image access, network, limits, attempts/order and stopping rule. Link
oracle/nop controls and the active execution scope. Resolve differences from
the repository's diagnostic protocol explicitly; capability comparisons do
not substitute for final qualification.

### Outcomes and handoff

| Candidate / condition / freeze | Validity | Task result | Hypothesis support | Disposition / evidence |
| --- | --- | --- | --- | --- |
| … | Not run | Not observed | Unknown | … |

Report model attempts separately from fixtures and correlated representations;
retain exclusions and all passes. Link the ledger, authored reviews and raw
evidence receipts. State what the next round should preserve or change.

### Dated decisions

- Date — capture, scoped revision, execution lock, or closeout; supporting source.
