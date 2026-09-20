# {{title}}

State the action the agent must accomplish in one sentence.

## Value

Explain the clinical or scientific workflow this supports; distinguish intended value from demonstrated benefit.

## Given

### Original data

Describe the images/data, modality, extent and format that matter.

### Supplied helpers

List supplied masks, coordinates, crops, hints, plans, checkpoints or prior outputs. Say what each removes from the agent's work.

### Callable tools

Describe available specialist tools and relevant environment or retrieval permissions.

### Reference-only material

Identify evaluator/reader-only answers. State unknown access boundaries explicitly.

## Task specification

State the requested action, meaningful constraints and assistance condition. Link the exact executable prompt when it exists.

## Expected output

Give a concrete output shape/example, including units and coordinates where consequential.

## Evaluation

Describe what the scorer checks and what it does not establish. For a proposed task, state unresolved scoring/reference questions.

## Visual explanation

### Workflow

- Original data + supplied help
- Requested action
- Expected deliverable

### Input

Add a representative input image or state the missing visual. Markdown images use paths relative to this brief.

### Supplied helpers

Add the same view with supplied assistance. Explain any reader-only crop or annotation.

### Reference or output

Add a reference or output example and label its role. It is hidden until the reader requests the reveal.

## Conditions

| Condition | Supplied help | Work remaining |
| --- | --- | --- |
| Proposed condition | Describe help | Describe the remaining work |

## Difficulty

Explain the remaining search, perception, reasoning or execution demand. Label a hypothesis as such; do not invent difficulty scores.

## Sources

Link the task prompt, relevant scorer, data/figure attribution and supporting evidence.

## Coverage

State which definition, conditions and cases this brief covers.

## Gaps

Record missing or unresolved references, visuals, source staging or cases. Use "None identified within this scope" only when justified.
