# tb3-medical collaboration

Read CONTRIBUTING.md and docs/governance.md. The closed interview investigation
is historical; authorized medical capability research is the current purpose.
Informative successes, source research, visual explanations and qualified partial
studies are useful. Submission difficulty gates apply only when promoting a task.
Do not launch trials, install runtimes or publish as a side effect of maintenance.
Do not pursue security research or resume the archived security work.

## Ownership and daily work

- Inspect Git status and active task ownership first. Preserve concurrent probe,
  freeze, runtime and result writers. Stage explicit paths; make focused commits.
- Start with `uv run med list QUERY`. Groups own their questions,
  ideas, decisions, methods, experiments, findings and presentation. Read the
  group's AGENTS.md. Shared code belongs in src/tb3_medical and presentation.
- For requests to use a seg tool, SAM or LiteMedSAM, start with
  [the segmentation rulebook](docs/segmentation-tools.md) and its solver skill.
  Colored overlays need legends with matching colors and line styles.
- Capture substantive discussion findings and useful explanations in a concise
  existing idea card or a new stable ID. Retain source task links, prior findings,
  visual references, decisions and reopening conditions. Append decisions with
  the actual actor; an assistant recommendation is not a user decision. Search
  before repeating research. The historical round register remains provenance.
- Preserve frozen task bytes, original outcomes and evidence hashes. A partial
  attempt, timeout, infrastructure failure or bad reference is not a model failure.
  Append new observations, evaluations and reviews; never rewrite a score to fit
  a corrected conclusion. Use dependency links so issues flag affected findings,
  ideas, stories and exports. Correcting code does not reinstate evidence.
- Agents may invalidate reproduced technical defects with retained proof.
  Clinical/reference disputes stay under review pending appropriate adjudication.
  Do not infer population or causal claims from one exploratory comparison.
- Historical probes are replay adapters and retained snapshots. Do not execute
  their authoring modules on import; some mutate artifacts. New work uses group
  experiments and the common CLI. No model run is implied by an idea or plan.

## Reproduction, exports and checks

Before any authorized Codex model launch, read the
[local Codex launch rulebook](docs/workflow.md#local-codex-launch-rulebook).
This Mac's working Harbor route requires explicit login and container proxy
settings via `med run --agent-env-file .local/runtime/codex-agent-env.json`.
Inspect the existing local profile or a successful run's `agents[].env`; never
print credential contents or silently substitute an empty environment, API-key
auth, another model or another client. Host and container Codex versions differ.
When routing changes or fails, verify a bounded toy through the same Harbor image,
auth and proxy route before launching the medical task. Missing credentials,
401 responses and stale-client model errors are infrastructure observations,
not proof of account-wide model unavailability or model failure. Do not repeat an
unchanged failed launch. Astra/medium and GPT-6 Sol/xhigh both passed the documented
Harbor toy on 2026-09-23; recheck when the runtime or route changes.

Keep raw runs, credentials, environments, generated reports and media local.
Track concise allowlisted records and required fixtures/licenses. Record missing
artifacts explicitly. Dockerfiles alone do not prove recovery or replay.
The existing sibling submission has separate ownership (docs/submission.md).
Build new exports into fresh destinations; draft packaging is not qualification.
After explicit handoff an export is independently maintained, with deliberate
backports. Do not rename this checkout or touch remote settings without a request.

Run `make check PYTHON=python3.12` after staging intended changes and before
committing tooling. The artifact gate reads the Git index. Check a clean staged
or committed tree when unrelated changes are present. Never delete raw evidence
or regenerate historical freezes as part of hygiene.
