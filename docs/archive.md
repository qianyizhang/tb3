# Research archive

[Final report](report.html) · [Selected task](submission.md) · [Reproduction](reproduce.md)

The research is closed. This index exposes detail progressively; historical
“active”, “next action” and “pending” wording records the state at the time,
not a current instruction. Original snapshots and evidence remain at stable
paths so hashes, source receipts and reviewed outcomes keep their meaning.

## Start with the selected result

| Question | Retained record |
| --- | --- |
| What did the solver receive? | [Original case-32 instruction](../probes/revisions/br004-single/tasks/dicom-audit-32/instruction.md) |
| Why choose it? | [Cross-model selection analysis](../catalog/analyses/br004-sol-followup.md) |
| What happened in each trial? | [Terra review](evidence/br004-single-case-32-review.json), [Sol review](evidence/br004-sol-case-32-review.json) |
| Were conditions controlled? | [Single-patient protocol](research-rounds/BR-004-single-patient-benchmark.md), [Sol protocol](research-rounds/BR-004-sol-followup.md) |
| Which bytes were trialed? | [Single-patient freeze](evidence/br004-single-patient-freeze.json), [Sol freeze](evidence/br004-sol-freeze.json) |
| What about controls and other cases? | [Terra screen](evidence/br004-single-patient-summary.json), [Sol screen](evidence/br004-sol-summary.json), [47 author scoring controls](evidence/br004-sol-author-controls.json) |
| Where is the clean submission? | [Submission handoff and qualification boundary](submission.md) |

## Milestones and original rounds

| Report milestone | Detailed records |
| --- | --- |
| Search and calibration | [Initial research](research.md), [benchmark-backed survey](research-benchmark-backed.md), [BR-001 scientific pilots](research-brainstorm-experiments-20260914.md), [BR-002 Sol/Astra results](research-rounds/BR-002-results.md) |
| Scaffolding audit and correction | [20-task audit](research-specification-audit-20260915.md), [BR-005 retest](research-rounds/BR-005-results.md), [BR-007 Clipper follow-up](research-rounds/BR-007-results.md) |
| Work-history and anatomy | [BR-003](research-rounds/BR-003-work-history.md), [BR-004 batch review](../catalog/analyses/br004-anatomy-audit.md), [single-patient screen](../catalog/analyses/br004-single-patient.md) |
| Final research selection | [BR-004 Sol follow-up](../catalog/analyses/br004-sol-followup.md), [case-83 alternative](../catalog/analyses/br004-single-case-83.md) |
| Parallel Xiangqi branch | [BR-006 player](research-rounds/BR-006-results.md), [BR-008 library](research-rounds/BR-008-results.md), [BR-009 sustained server](research-rounds/BR-009-results.md) |

[Closed round register](research-rounds.md) preserves all nine IDs.
[Historical ledger](ledger.md) retains early setup attempts, original local
identifiers and later summaries. It is an audit record, not another maintained
final report. Source inventories, case variants, controls and model attempts
have different denominators and must not be pooled as a model ranking.

<details>
<summary>Candidate sourcing and retired directions</summary>

- [Sourcing methodology](research-sourcing-methodology.md)
- [100-card task bank](research-broad-task-bank.md), [its complete screen](research-screening-20260912.md), [12-record second search](research-candidate-search-r2-20260912.md)
- [Short-horizon survey](research-short-horizon.md), [earlier next-candidate list](research-next-candidates.md)
- [Build](research-build-candidates.md), [runtime](research-runtime-candidates.md), [mathematics](research-math-candidates.md), [numerical](research-numerical-candidates.md) searches
- [Geometry proposal](research-geometry-candidate.md), [geometry review](geometry-review.md), [earlier harder screen](harder-screen.md)

These are historical research records. The stopped security direction remains
closed. No published task is presented as an original workshop submission.

</details>

<details>
<summary>Machine-readable records and frozen packages</summary>

| Location | Meaning |
| --- | --- |
| `docs/evidence/` | Concise plans, controls, source receipts, reviews and freezes |
| `catalog/ideas/` | Historical candidate rationale and dispositions |
| `catalog/trials/` | Allowlisted imports of individual raw trial results |
| `catalog/reviews/` | Append-only authored reviews, bound to evidence hashes |
| `catalog/analyses/` | Detailed interpretations and exclusions |
| `probes/` and `probes/revisions/` | Original task, verifier, oracle, source and license inputs |

See [the catalog reference](catalog.md) for search and review semantics. Its
raw failure-candidate classification is not the same as a reviewed genuine
failure. Original records remain unchanged when a later condition succeeds.

</details>

<details>
<summary>Operations and original assignment</summary>

- [Original take-home](task.md) and [pinned submission requirements](requirements.md)
- [Reproduction guide](reproduce.md) and [historical machine setup](setup.md)
- [Consolidated operating history](archive/operations.md): CLI repair, geometry pickup and former round template
- [Artifact governance](governance.md) and [contributing/checks](../CONTRIBUTING.md)

The original requirements are preserved. Closing the investigation does not
waive a missing submission check or turn a pilot into a qualifying trial.

</details>

## Retention and cleanup

The closeout replaces the long README with a short entry point, writes one final
HTML report, consolidates spent operating notes, closes the round register and
removes active-work framing from archive navigation. The report owns synthesis;
original protocols and reviews continue to own their evidence.

| Material | Closeout treatment |
| --- | --- |
| Original protocols, freezes, results and reviews | Retained at original paths; no retrospective reward or task change |
| CLI repair, geometry pickup, round template | Consolidated into `archive/operations.md`; inbound links updated |
| Ledger and candidate searches | Retained as historical detail, removed from primary reading path |
| Generated catalog and raw traces | Local-only in `runs/`; not embedded in the interview report |
| Pre-cleanup authored state | Local recovery archive plus file hashes in `runs/archive-closeout/` |
| Runtime environments and caches | Retained while submission work is active; no blanket cleanup |

The embedded report illustration is an attributed author reconstruction; its
[provenance receipt](report-figure.json) records the exact bytes. It is the only
image included in the report and is not represented as a pilot screenshot.

Git history preserves previous tracked versions. The local recovery archive
also includes the uncommitted research files present at closeout start. Neither
is an off-machine backup of raw runs. There was no publication, remote backup,
GitHub read-only archival or raw-evidence deletion in this cleanup.

## Closeout verification — 2026-09-15

- Python 3.12.13: `make check` passed the staged artifact gate and all 61 offline tests.
- A clean Git export plus the staged presentation changes also passed the gate
  and all 61 tests, with all 2,102 tracked files matching the working inputs.
- All 1,862 pre-cleanup task/evidence files in the protected path groups remained
  byte-identical. Frozen input formatting was preserved as part of those bytes.
- All 151 catalog trial records had current local evidence; no authored review
  was stale. Both original case-32 result and submission hashes matched.
- 273 relative links across 16 presentation/changed documents resolved. Desktop
  and phone-width browser checks found no horizontal page overflow; all fifteen
  report disclosures expanded/collapsed, and the embedded image loaded.

Detailed check logs, the pre-cleanup authored snapshot and the raw-file checksum
inventory are retained locally in `runs/archive-closeout/`. These are archive
integrity checks, not additional task trials or submission qualification.
