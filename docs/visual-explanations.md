# Visual explanation rulebook

Choose the view by the question, not by the available plotting tool.

| Reader question | Best first view | What it must not imply |
| --- | --- | --- |
| What is the task? | Small symbolic SVG/flowchart | Measured performance or patient evidence |
| What does success look like? | Input → expected-output example | That a demonstration is a measured result or solver-visible reference |
| How good was the result? | Metric table/chart plus native matched view | Comparability or clinical validity not established by the evidence |
| Why did it fail? | Stage funnel plus localized real-data evidence | That the failed stage proves an agent limitation; context, instructions and reference remain candidate causes |
| How did runs differ? | Matched small multiples on identical planes/crops | That unlike conditions support a causal ranking |
| Is GT questionable? | GT consistency view, source provenance and counterevidence | That disagreement alone proves a reference defect |
| What did the agent do? | Phase timeline, artifact DAG and concise pseudocode | That selected steps cover the whole trace or reveal hidden cognition |

A stage funnel shows where an observable loss occurs; use measured counts and
denominators, or label it qualitative. An artifact DAG shows derivation between
saved states; a timeline shows order or duration. Choose the view that answers the
question rather than producing all three. For a disputed reference, show the
relevant source alongside GT and independent counterevidence at matching geometry;
label annotation gaps and adjudication status explicitly.

Use a three-level explanation when the material supports it:

```text
concept / relationship  ->  measure / comparison  ->  actual result and reference
compact SVG                 table or chart            source-derived inspection
```

Do not manufacture all three levels when one view answers the question.

## Source-derived views

- Identify input, prediction, reference and post-hoc diagnostic roles separately.
- State modality, plane, coordinate convention, crop/resampling/window and view
  selection when consequential. A selected crop can remove the search problem.
- Use the exact overlay colors and line styles in a visible legend. Do not rely
  on a prose color name or color alone.
- Keep scores outside the pixels unless a short label materially aids inspection.
- Preserve figure source, derivation and attribution. Mark unavailable GT rather
  than substituting a conceptual drawing.

## Symbolic drawings

Use diagrams for ownership, flow, correspondence or abstraction. Keep labels short;
put nuance in the caption. A symbolic organ, mask or graph is not a dataset sample.

## Semantic emphasis

Use color plus a redundant symbol or label:

| Meaning | Suggested color | Redundant cue |
| --- | --- | --- |
| Net positive / retained | green `#2E7D32` | `+`, upward marker or “improved” |
| Net negative / regression | red `#C62828` | `−`, downward marker or “worse” |
| Warning / unresolved | amber `#F9A825` | `!`, hatch or “review” |
| Neutral / reference | blue-gray | solid/dashed role label |

Medical overlays may need another palette. Anatomical identity and semantic outcome
colors must not silently compete; provide separate legends when both are present.

## Caption contract

A concise caption should answer only what is needed:

```text
What is shown · role · coordinates/view · derivation · decisive caveat
```

Avoid paragraphs inside figures. Prefer one-line labels, a small legend and a
caption beside or below the visual. Inspect the final rendered size, not only the
source SVG or plotting code.
