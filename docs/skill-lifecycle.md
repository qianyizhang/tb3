# Skill lifecycle

Repository-owned skills use semantic versions in `metadata.version` and keep a
local `references/feedback-ledger.md`. The repository copy is canonical; copies
under `~/.codex/skills` are installation mirrors, not independent histories.

Version changes describe instruction behavior:

- **Patch:** correction or clarification without a material workflow change.
- **Minor:** new mode, decision rule or materially improved workflow.
- **Major:** incompatible invocation, output or safety contract.

When condensing or consolidating a skill, review the semantic diff: preserve
required outcomes, inspection steps and claim boundaries. Moving a requirement
into a mode must not make it disappear from other applicable modes; replacing an
explicit action with a general preference is a behavior change.

Every ledger entry records the version that was actually invoked. Use
`unversioned` only for a genuinely historical invocation. Do not silently replace
it with the version containing the eventual fix.

## Material-only feedback

At closeout, a skill invocation considers whether it exposed reusable evidence:
explicit user feedback, a correctness/safety caveat, recurring footgun, material
wasted effort, instruction ambiguity, or a successful pattern worth standardizing.
Routine success creates no entry. Ledger work must not block the requested output
or broaden the task.

Each ledger keeps a short **Active lessons** section for normal invocations and an
append-only **History** for maintenance. A severe confirmed correctness or safety
issue can justify one-entry action. Other generalizations normally need repeated
independent evidence or explicit user direction. Retain resolved and declined
entries with their resolution version.

Never put patient data, credentials, bulky traces or unsupported interpretation in
a skill ledger. Link to a durable task or artifact and state only the reusable
workflow lesson. If the canonical skill source is not writable or is outside the
current task's scope, provide a compact suggested entry instead of creating a
second ledger.
