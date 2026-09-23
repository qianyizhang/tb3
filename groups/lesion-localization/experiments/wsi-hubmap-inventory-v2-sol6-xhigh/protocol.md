# HuBMAP glomerulus reference recall — Sol 6 xhigh

## Question and method

Can `openai/gpt-6-sol` at xhigh locate source-annotated glomeruli while making
its uncertain extra candidates inspectable? This is a **new task version**, not
a replay or score edit of the [Astra diagnostic](../wsi-hubmap-inventory-astra-medium/protocol.md).
The user accepted the revised design in the current task on 2026-09-23. Run one
3600-second diagnostic model attempt with no automatic retry, 4 CPUs, 12 GiB,
no GPU and the pinned isolated transport route. Route errors receive no model
verdict. An oracle pass and no-op contract failure must precede dispatch.

## Inputs and reference

The solver receives the complete PAS TIFF `aaa6a05cc`, a GT-free overview,
physical pixel scale and a coordinate crop helper. It returns level-0 centers,
optional confidence and uncertainty notes. The evaluator retains the 99 source
polygons. One-to-one matching accepts a point inside a polygon or within 50 µm
of its edge. **Reference recall is the main measure**; unmatched submitted
points are a review queue, not false positives or precision denominator. The
source does not grade sclerosis, partial profiles or clinical disease.

## Findings and limits

Pending model attempt. The original Astra run matched 86/99 and left 28
unmatched submitted points, some morphologically altered. No source GT defect
was proved. A new Sol result on this public training slide is diagnostic only;
resolve candidate inclusion with pathology adjudication before a precision or
clinical count claim. Crop-helper logs do not enforce a full read budget because
direct TIFF access remains available.
