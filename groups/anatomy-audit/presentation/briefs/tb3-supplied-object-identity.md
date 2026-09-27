# Name supplied anatomical objects

Name supplied anatomical objects.

## Value

Separates anatomical naming from construction of organ boundaries.

## Given

### Original data

Anonymous abdominal objects in a shared patient frame. BR-013 A01/A02 supply
independent binary masks, an overview, object IDs and a label vocabulary. The
mask files preserve overlaps and map voxel indices to physical LPS millimetres;
the surface rendering is a preview. These conditions supply no CT.

### Supplied helpers

Shape, relative placement, patient orientation and a ready scene viewer are
already supplied. The condition determines the label inventory and image help:

| Condition | Supplied assistance | Remaining work |
| --- | --- | --- |
| BR-013 A01/A02 | Vocabulary; each label may be used at most once; some labels may be unused | Name every supplied object; unused labels imply neither disease nor missing annotation |
| BR-014 I01 | Exact inventory for the unchanged A02 objects | Identify which object receives each supplied name |
| BR-014 F01 | Retained fragments in the shared scene; repeated labels allowed | Assign a source-specific anatomical identity to every fragment |
| BR-015 C01 | Original CT plus the A02 objects and broad vocabulary | Use image context to resolve object identity |
| BR-015 V01 | Native CT, overlapping venous context and an exact eight-name branch inventory | Identify only the eight targets; do not assign a name to the context mask |

### Callable tools

The original abdominal conditions include Python, NumPy, Pillow and a scene
loader/renderer. Later CT-supported conditions add their declared image tools.
Each frozen task retains its exact environment and access contract.

### Reference-only material

The expected ID-to-label key belongs to the separate evaluator. Source names
revealed by the teaching story are reader-facing metadata, not supplied
recognition answers. The retained s1233 teaching assembly uses seven of the
source anatomy classes; A01 also uses source s1233 but supplies 13 objects.
Teaching IDs, display smoothing and the subset are not the frozen task data.

## Task specification

Assign anatomical identities to the supplied IDs without changing masks,
reconstructing missing boundaries or diagnosing the patient. Follow the
condition's vocabulary and whether repeated labels are allowed. BR-013 A03 is a
separate proposed-label audit: it returns only changed identities.

## Expected output

Write `answer.json` with `assignments`, each containing `object_id` and `label`;
include every target object exactly once. V01's overlapping context mask is not
a target. Labels must match the condition's
vocabulary. The separate A03 audit uses `corrections` and omits unchanged objects.

## Evaluation

The recognition scorer checks missing/extra IDs and exact labels, and reports
correct identities over all supplied objects. Keep anatomical disputes and
fragmented-object conventions explicit; this explainer asserts no model result.

## Difficulty

Global arrangement, exact inventory and source CT can resolve otherwise ambiguous shapes. Fragmented objects require the source-specific identity convention.

## Coverage

The experiment index preserves case, contract, assistance and execution boundaries.
An experiment record is not an execution count; grouping does not pool scores.

## Sources

- [BR-013 — Prioritize upper-abdominal identity reasoning](../../experiments/br013/protocol.md)
- [BR-014 — Label inventory and fragmented organ identity](../../experiments/br014/protocol.md)
- [BR-015 — Clinical evidence and anatomical identity](../../experiments/br015/protocol.md)
