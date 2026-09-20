# Task Brief authoring rules

Accepted by the user on 2026-09-21 in [the design discussion](../../discussions/task-brief-format.md).
A **Task Brief** explains one task definition; the **Task Explorer** makes definitions,
assistance conditions and cases navigable. Write for technical readers without
specialist medical knowledge. Use the same format for existing and proposed tasks.

## Content contract

Start from the [Markdown template](brief-template.md). Its headings are the small
renderer interface, grouped into six reader questions:

1. **Task and value:** a concrete action and a short clinical/scientific motivation.
2. **Given:** original data, supplied helpers, callable tools and reference-only material.
3. **Contract:** required actions, meaningful constraints and permitted assistance.
4. **Deliverable:** a concrete output shape/example and the actual scoring scope.
5. **Visual explanation:** input, helper overlay and a reference/output reveal.
6. **Difficulty and evidence:** work remaining after assistance, sources and gaps.

Aim for a 60–90 second first read (about 150–250 words plus visuals). Put full
schemas, methods and result analysis behind links or expandable sections. Explain
necessary terminology where it appears. Clinical motivation is not a claim of
clinical validity. A model score is not required for a brief to be useful.

Keep the exact solver prompt and scorer authoritative. Reader-only answer reveals
must not become solver inputs. Proposed briefs explicitly identify unresolved
references, scoring and resources; their presence never launches a trial.

## Assistance and variants

Describe what is actually supplied, including derived artifacts: masks, crops,
landmarks, answer lists, algorithms, code, checkpoints and tool-generated outputs.
Separate pre-supplied files from callable tools and evaluator-only references.
If source staging was not inspected, say so rather than assuming data is hidden.

One common brief covers repeated cases. The catalogue lists repository → family
→ definition → condition → case as available. Give meaningful changes in the
contract their own definition or condition. Every imported case remains reachable;
do not treat one illustrated case as exhaustive coverage. Source-published counts,
imported identifiers, authored briefs and available media are distinct coverage facts.

## Visual contract

- Start with input. Supplied-helper views are separately selectable. Reference
  answers and actual predictions appear only after an explicit reader reveal.
- Use a native/source-derived example when available. Identify any post-hoc crop,
  selected plane or camera, especially when it reduces the localization problem.
- Label reference, illustrative output and actual agent prediction separately.
  Preserve orientation/physical aspect; avoid caliper claims on explanatory layouts.
- Describe why assistance makes the task easier and what remains difficult.
  Evidence supports a difficulty claim; a conceptual drawing alone does not.
- Retain figure source, caption, attribution, relevant terms and derivation.
  Reuse existing tours as optional modules; keep a useful static fallback.
- Missing assets stay explicit. Dataset acquisition and model execution are
  separate actions. When the user requests sample acquisition, fetch bounded
  individual cases, retain source terms and checksums, and label exact task cases
  versus representative examples. Downloading inputs does not authorize model runs.

## Small authoring surface

- The brief Markdown owns its explanatory content. The collection `catalog.json`
  owns navigation metadata and points to it; it does not duplicate the prose.
  A brief ID identifies a definition. An optional `repository_id` connects several
  distinct briefs to the same imported repository inventory (`--repository-id`
  when scaffolding). Inventory rows point to their shared `brief_id` when authored.
- A collection can set `require_brief_coverage: true` once its imported inventory
  is backfilled. Checks then reject unlinked entries, cross-repository brief links
  and invalid condition indices. This guarantees an explanation, not a native image.
- Keep the sidebar grouped by repository and list each shared task definition once.
  Put repeated cases beneath their task, with short labels and only sourced differences
  (for example candidate-pool size). Never infer a clinical description from a case ID.
  Selecting a case must retain its source and condition across reload/back navigation.
- Show one task explanation with Overview, Requirements, optional Example and Sources
  sections. Do not repeat it in a separate catalogue preview, or mark every record with
  a universal availability badge. Omit summaries that only restate their title.
- Keep family/definition IDs, source conditions, counts and revisions in expandable
  provenance. Surface details that change the reader's understanding of the selected
  task. Missing examples do not need a repeated pseudo-visual made from the input text.
- The optional `Cases` brief section explains what varies between cases and which
  inputs have actually been imported. Inventory `case_context` facts are specific to
  one source record and carry their own source URL. Repository introductions remain
  small navigation metadata; substantive task explanations stay in Markdown.
- Shared explanations across releases must label their scope. Similar task names
  do not establish identical data, model guidance or scoring. Keep the exact source
  link visible, and call out any unresolved difference next to the shared brief.
- Internal briefs live with the group's presentation. External survey briefs
  live with their source discussion. Existing evidence cards and frozen protocols
  remain source records; link them rather than modifying historical outcomes.
- `proposed: true` in a catalogue entry labels an unfinished task definition.
  This is a content qualifier, not a new experiment assessment/status system.
- The inventory records source IDs, source URLs/revisions and coverage limitations.
  It need not contain native datasets or materialize generated benchmark tasks.

```sh
# Scaffold only; creates a proposed brief and navigation entry, never an experiment.
med brief new my-task --title "Locate a named landmark" \
  --repository "Our work" --family "Landmarks" \
  --destination groups/anatomical-landmarks/presentation/briefs/my-task.md

# Standalone HTML; inputs and images are embedded, no server or remote assets required.
med brief build --output runs/task-explorer/index.html
med brief check
```

The default collection is `discussions/medical-agent-repository-survey/catalog.json`;
use `--catalog` on each brief subcommand for another repository-owned collection.
The reusable `author-task-brief` skill discovers this rulebook; keep domain-specific
rules here. It does not copy this file into user-level skill storage.

Check rendered input/helper/reveal states, condition switching, navigation and
mobile layout after renderer changes. Offline checks cover source resolution,
stable identities and build safety. They do not certify anatomical correctness,
reference quality or reproduction of an external benchmark.
