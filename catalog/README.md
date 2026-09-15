# Archived research catalog

Start with the [final report](../docs/report.html) and
[evidence archive](../docs/archive.md). Candidate statuses and `next_action`
fields retain their historical meanings; they are not an active work queue.
Records are preserved for provenance, including passes and rejected ideas.


Each `ideas/*.json` file is one authored candidate record. Keep the filename equal to its stable `id`; use tags to search across domains and mechanisms. The initial records summarize the repository's research on 2026-09-12. Source URLs are recorded leads from those notes, not newly verified reports of current upstream behavior.

`status`, `hypothesis`, `why_hard`, `next_action`, and `notes` express review decisions. `sources` retains upstream provenance; `evidence` points to repository-relative research or experiment evidence. A status such as `prototyping` describes authoring activity and does not establish model difficulty. `calibration` keeps useful setup fixtures visible without promoting them as hard tasks. Preserve rejected and parked ideas with their reasons so future searches do not repeat a completed screen.

Keep this authored review metadata separate from generated trial records. Import trial outcomes from run artifacts through the experiment tooling; do not infer a model failure from an issue report, a nop control, an infrastructure exception, or a displayed aggregate reward. Candidate notes may link measured evidence, but the trial record owns the outcome and its validity. Update review status deliberately after inspecting that evidence.

The JSON contract is `schema_version: 1`, `id`, `title`, `status`, `tags`, `hypothesis`, `why_hard`, `next_action`, `sources: [{url, note}]`, `evidence: [path]`, and `notes`. Allowed statuses are `idea`, `screening`, `prototyping`, `calibration`, `rejected`, and `parked`.
