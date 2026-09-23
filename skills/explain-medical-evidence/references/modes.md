# Explanation modes

Read the sections matching the request. Shared inspection and explanation checks
in SKILL.md apply throughout. These are decision prompts, not fixed report lengths.

## Task, context and reference fitness

Do a proportional fitness check whenever interpreting a score, including inside
comparisons and syntheses. Reuse an existing pinned check only when its inputs,
instructions, scorer and reference still apply. Start with the actual frozen
solver-visible package and source annotation protocol, not the author's intended
task. Deepen the audit when contradictions, unexplained mismatches or missing
information could change the conclusion.

| Alternative cause | Concrete check | Evidence that would discriminate it |
| --- | --- | --- |
| Missing context or unidentifiable target | What could the solver know? Did annotators have reports, diagnoses, timepoints, another modality or conventions withheld from the solver? Could the same input reasonably admit different scored answers? | Source annotation protocol, supplied files and access trace; compare required information with available information. A context-supplied control is a proposed new condition, not implicit launch permission. |
| Instruction/specification problem | Are target scope, inclusion policy, identities, coordinates, uncertainty and label meanings clear? Does the scorer require an unstated or conflicting rule? | Exact instruction/scorer clauses and the agent's observable interpretation; neutral examples or counterexamples that expose the mismatch. |
| GT/reference or scorer problem | Check source/version, sample identity, registration/orientation, label mapping, coverage/exclusions, annotation granularity and scorer implementation. Is unannotated tissue being treated as negative? | Native consistency views, provenance and independent counterevidence; a reproducible transform/scoring defect or appropriately adjudicated reference discrepancy. |
| Data/tool/runtime problem | Was needed information acquired and delivered without loss, truncation or conversion error? | Input metadata, tool outputs and intermediate artifacts at the affected stage. |

For a material alternative, record supporting evidence, counterevidence and the
missing observation that would resolve it. “No defect demonstrated” is not “GT
verified correct”. Missing context may constrain the endpoint without making the
whole task impossible; reserve impossibility claims for an established information
gap or contradiction. Conversely, do not dismiss demonstrated agent errors merely
because another part of the task is ambiguous.

Report **reference disagreement**, **supported agent error**, **task-boundary
limitation** and **reference/scorer defect** distinctly; causes may coexist. Mark
attributions as observed (direct artifact/action), supported (counterchecks favor
it), plausible (not isolated), unresolved (material evidence missing), or refuted
(a check contradicts it). Do not assign invented causal percentages.

Retain frozen outcomes. Record reproduced technical defects through the repository
issue/review workflow with proof and affected scope. Clinical/reference disputes
remain under review for appropriate adjudication; a plausible discrepancy does not
authorize relabeling. Diagnostic recomputation remains separate from official scores.

## Result or result versus GT

Lead with task/condition and the smallest sufficient score table. Explain each main
metric's object, denominator, direction and blind spot. Pair aggregate numbers with
source views that explain representative behavior and consequential errors when
available. Distinguish official GT comparison from post-hoc anatomical judgment.

## Trace and failure attribution

Start from the final output and work backward to consequential decisions. Explain
the reconstructed method as input → selection/transform → intermediate → output.
Use compact bullets for a linear sequence, a flowgraph for branching/comparison,
and pseudocode for a calculation that explains the result. Include relevant
thresholds, coordinate transforms, candidate rejection and cleanup operations;
omit routine command chronology. Compare intermediate and final artifacts when
that can test whether a particular operation caused the observed error.

Locate losses with a task-appropriate stage funnel, for example:

```text
input delivered → search → candidate generated → accepted
                → geometry/identity → valid output → reference agreement
```

Adapt or omit inapplicable stages; label counts and denominators only when observed.
Pair the funnel with localized real-data evidence. The failed stage locates the
observable loss; the shared fitness checks determine whether context, instructions,
reference, runtime or agent behavior can explain it. Do not silently equate these.

### Inspect exposure and decisions

Choose source-derived views that distinguish the leading explanations: for example,
a missed target in its solver-displayed crop, a retained/rejected candidate, or a
before/after mask. Include a successful comparison when it helps discriminate the
mechanism. A whole-image overview may locate a problem without resolving it.

Keep these evidence levels separate:

| Level | Evidence needed | Inference limit |
| --- | --- | --- |
| Generated | Crop/script/ledger and geometry | Image delivery not established |
| Delivered | Display request and successful image/tool observation | Target discernibility not established |
| Discernible | Inspect the actual view, crop, scale/window and target coordinates | Attention or recognition not established |
| Explicit decision | Localized observable statement/action and resulting artifact | Stated rationale is not proof of clinical correctness |

Do not infer cognition from the final score or crop containment. A localized
rejected candidate supports a different claim from an unmarked target or an
uninspected region. Missing display evidence is an uncertainty, not proof that a
view was never seen. State selected-view coverage rather than implying a full audit.

### Attribute the outcome

For each material mechanism, retain a compact evidence chain:

```text
claim → attempt + trace step/line + artifact
      → observed operation/result → alternatives → confidence/limit
      → next discriminating check, if unresolved
```

Pin source identities and hashes in the receipt; give step IDs/timestamps or file
lines beside claims so readers can find the evidence. Keep raw traces linked, not
copied wholesale into the report. For mutable logs, pin the observed prefix.

Test the relevant alternatives below. Do not force every layer into every case:

| Candidate explanation | Evidence to inspect |
| --- | --- |
| Task/context/reference limitation | Shared fitness check, exact package and source protocol; evidence for and against |
| Runtime or tool failure | Failed/lossy operation and its downstream artifact |
| Search omission | Delivered views and coverage at useful scale |
| Recognition or candidate rejection | Localized observable decision, candidate artifact and reference comparison |
| Geometry/identity/output error | Intermediate transforms, masks/IDs and contract checks |

Prefer a compact attribution table:

| Outcome / stage | Decisive evidence + locator | Attribution + status | Counterevidence / unresolved alternative | Next check |
| --- | --- | --- | --- | --- |

Keep claim strength proportional to the evidence. A downstream score may reflect
missing upstream inputs rather than a separately demonstrated capability failure.

### Explain inefficiency separately

Identify measured repetition, failed operations, corrections or discarded work and
their consequence. State the unit and denominator: repeated crops, correction
commands, elapsed time or overwritten candidates. Manual work, many tool calls or
long duration alone do not prove waste. Label proposed faster methods as untested
unless a comparable measurement supports the claimed benefit.

### Compact calculation example

For a tissue-mask lookup, this may explain a residual mismatch more clearly than
a long narrative; use only when the saved code and points support it:

```text
submitted_code = mask[predicted_center]
scored_code    = mask[matched_reference_center]
centers across a boundary → localization match + compartment mismatch
```

Place the relevant boundary view and exact lookup locator beside the explanation.
Distinguish the computed mismatch from any unresolved biological interpretation.

## Multi-run comparison

Create a condition matrix before comparing outcomes: task/reference digest,
solver-visible inputs, tools, model/effort, runtime, scorer and execution status.
Declare comparability. Use deltas only for shared endpoints; keep nonshared
diagnostics in separate columns. Do not turn one run per condition into a causal
model or effort ranking.

## Synthesis or audit

Preserve each experiment's endpoint and review status. Group compatible evidence;
do not average unlike tasks. For data/GT audits, distinguish official reference,
independent source evidence, plausible discrepancy and adjudicated correction.
End with what can be concluded now and the observation that would change it.
