# Skill lifecycle

Repository-owned skills use semantic versions in `metadata.version` and keep a
local `references/feedback-ledger.md`. The repository copy is canonical; copies
under `~/.codex/skills` are installation mirrors, not independent histories.

`make skills-check` validates canonical metadata and portable resources. Workspace
contracts resolve from `workbench.toml`; links outside an installed skill break.
Compare full installed trees without changing them:

```sh
.venv/bin/python -m tb3_medical.skill_checks --installed-root ~/.codex/skills
# Add --skill NAME to select one skill.
```

Matching versions do not prove matching bytes. Inspect differences and preserve
independent feedback before mirroring. CI needs only canonical sources.

The authoring workflow has separate owners: `design-medical-study` prepares a
question and protocol; `author-task-brief` explains the task;
`explain-medical-evidence` interprets retained results; `author-task-story` creates
canonical interactive explanations; `video-explainer` exports established sources.

Evidence and video skills have maintenance review cases. Packaging checks or case
definitions do not prove agent behavior; new evaluations need their own execution
scope and receipts.

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
