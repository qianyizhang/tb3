# Feedback ledger: explain-medical-evidence

- Current skill version: `1.1.1`
- Canonical source: `skills/explain-medical-evidence/`

## Active lessons

- MED-EXPLAIN-2026-001: v1.1.0 restores explicit inspection and adds trace-review
  completion criteria. Behavioral improvement and the independent driver-model
  effect remain unmeasured; check future real invocations before claiming recovery.

## Entry format

### MED-EXPLAIN-YYYY-NNN

- Date:
- Source task or artifact:
- Invoked skill version:
- Kind: `user_feedback | caveat | footgun | inefficiency | success_pattern`
- Scope:
- Observation:
- Evidence:
- Candidate change:
- Status: `open | accepted | resolved | declined | superseded`
- Resolved in version:

## History

### MED-EXPLAIN-2026-001

- Date: 2026-09-23
- Source task or artifact: [Regression investigation](codex://threads/01a0ccbc-553f-73b2-ae3c-978057811f8a);
  canonical record `discussion-trace-analysis-regression-2026-09-23`.
- Invoked skill version: `1.0.1`
- Kind: `user_feedback`
- Scope: Trace methodology, visual inspection, failure/efficiency attribution and
  compact presentation.
- Observation: The user reported a worse analysis after skill consolidation and
  a driver-model switch, and requested tables, visual detail, flowgraphs,
  pseudocode and concise bullets. They accepted the repair with “seems correct,
  go fix”.
- Evidence: Git diff `8035485..2693e1d` removed explicit inspection, alternative
  testing and compact-format instructions. The WSI trace turn opened zero images;
  the older dedicated CT analysis opened four. WSI retained useful diagnostics
  and whole-trace hashes but lacked claim-to-step locators. Different tasks,
  contexts and models prevent causal attribution to either change alone.
- Candidate change: Restore common inspection/alternative checks; add method
  reconstruction, exposure levels, claim locators, measured efficiency and an
  explanation-quality check. Preserve concise mode routing and frozen evidence.
- Follow-up direction: The user pointed to
  [Consolidate research skills](codex://threads/01a0c710-a53a-7740-9d27-601f8cd9f07f),
  where they had accepted proportional reference-fitness checks, and explicitly
  required context, instructions and GT to remain live failure explanations.
  v1.1.0 adds concrete checks and counterevidence/status requirements, separates
  failed stage from cause, and restores the full question-to-visual perspective
  table in the shared rulebook.
- Status: `resolved` — instruction repair; behavioral recovery not yet established.
- Resolved in version: `1.1.0`
