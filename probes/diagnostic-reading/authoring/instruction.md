# Diagnostic reading exercise

Interpret the supplied examination as a retrospective radiology reading exercise.
Inspect the available images and pre-exam context. Write a concise radiology
report covering the examination, including important incidental findings.
There may be no acute abnormality, one finding, or multiple findings.

Save `answer.json` with these fields:

- `findings`: list of objects containing `observation`, `location`, `certainty`
  (`present`, `possible`, or `indeterminate`), and `evidence` (image filename,
  view/slice or physical coordinates, and relevant measurements).
- `impression`: prioritized list of conclusions, preserving uncertainty and
  distinguishing visible findings from suspected causes.
- `limitations`: missing context, unavailable comparisons or technical limits
  that materially affect the interpretation.
- `evidence_summary`: a short explanation linking the principal conclusions
  to visible evidence, including a relevant alternative when warranted.

Use the complete examination; overview sheets are navigation aids and may miss
small findings. Available CT tooling supports window/level and individual
physical slices. Coordinate convention is RAS millimetres (x increases toward
patient right, y anterior, z superior). Generated images carry orientation marks.

Provide evidence-based explanations, not a transcript of private internal
reasoning. Do not infer a definitive disease, temporal change or cause beyond
the available evidence. Do not search for the case or a source report online.
The task does not supply an expected diagnosis or target list.
