# Feedback ledger: video-explainer

- Current skill version: `0.2.1`
- Canonical source: `skills/video-explainer/`

## Active lessons

Canonical stories own their words and timing. Select this mode before reading
the standalone storyboard procedure, and resolve repository contracts from the
active workspace. Version equality does not prove installed-copy equality.

## History

Add material feedback here with date, source task/artifact, invoked skill
version, observation, evidence, proposed change and resolution. Do not record
patient data or routine success.

### VIDEO-2026-001

- Date: 2026-09-26
- Source: `discussion-workflow-reuse-review-2026-09-26` and
  [repair task](codex://threads/01a0dbcd-df2c-7953-be9f-8a667b837d0c).
- Invoked skill version: `0.1.0` (reviewed instruction version; no video invocation).
- Kind: `footgun`
- Observation: Canonical routing was appended after standalone instructions,
  absent from the installed copy under the same version, and linked outside the
  skill using a path that would break after installation.
- Evidence: The retained survey records both file hashes and link resolution.
- Resolution: v0.2.0 routes first, discovers the workspace contract and preserves
  the standalone workflow. A consistency check verifies complete mirror trees.
- Status: `resolved` for instruction and packaging defects; fresh agent behavior
  is not inferred from those checks.
