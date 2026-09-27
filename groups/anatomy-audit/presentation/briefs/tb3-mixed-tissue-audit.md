# Find foreign tissue inside a named mask

Audit a proposed organ mask for substantial included tissue from another organ,
then report its host ID, anatomical class and one physical witness.

## Value

Tests whether an agent notices tissue assigned inside the wrong named structure.

## Given

### Original data

Native abdominal CT and proposed named masks from retained TotalSegmentator case
`s1233`, with voxel-to-LPS affines. Positive LPS axes point left, posterior and
superior; coordinates are millimetres. Arrays are authoritative; PNGs are previews.

### Supplied helpers

The broad M02 task supplies 13 masks, a vocabulary, a scene index and ready 3D and
triplanar CT previews. Masks can overlap. Object IDs and colours are arbitrary.

### Callable tools

Python, NumPy, Pillow, `inspect_scene.py` and `inspect_ct.py` are supplied; additional
calculations and tools are allowed. No external source/patient matching is needed.

### Reference-only material

Original source masks, injected-region lineage and the oracle point are private
evaluator material, absent from the solver environment. The integrated teaching
story uses three **oracle-centred crops** and explicitly reveals the injected region
and point later. That selected view is neither blind search nor a full-volume audit;
it must not be given to a solver as task input.

## Task specification

Report every affected host mask containing at least **5 mL** of another organ.
The number of findings is unspecified and may be zero. A separate correct label
does not rule out foreign tissue inside another mask. Missing class names alone,
thin contour differences, native overlaps and incomplete scan coverage are outside
scope. Do not infer disease or surgery.

## Expected output

Write `answer.json` with one `findings` list. Each finding has `object_id` (the host,
not a remaining donor), `included_label` and three finite `point_lps_mm` numbers.
Return `{"findings":[]}` for an unchanged control. Do not add prose fields or
duplicate host/class pairs. No contours or exact volume estimates are required.

## Evaluation

The private key requires exact host/class pairs and a point within **3 mm** of a
voxel centre in the injected tissue. Extra, missing or duplicate findings fail;
detection, identity and localization are reported separately. The key establishes
synthetic voxel lineage, not clinical contour accuracy.

## Difficulty

Pure-organ recognition is insufficient: the agent must inspect mixed ownership
within one named mask against the CT. All class names remain present in M02.

## Coverage

| Condition | Data and deliverable boundary |
|---|---|
| M01: whole absorption | Pancreas joins duodenum; its separate label disappears, giving an absence cue. |
| M02: partial absorption | 6,233 source-pancreas voxels (**21.04 mL**) join duodenum; **38.38 mL** remains separately labeled. Audit all 13 masks. |
| N01: unchanged | Original source masks; expected findings list is empty. |
| F01: focused | Byte-identical M02 public data and key; audit only pancreas and duodenum, with other masks as context. |

The CT and aggregate foreground are unchanged by the label reassignment. The
construction is synthetic. These conditions remain separate; this teaching story
does not report a new model result or pool earlier scores.

## Sources

- [BR-017 — Substantial anatomy absorbed into an adjacent label](../../experiments/br017/protocol.md)
- [Frozen M02 contract](../../../../docs/evidence/br017-abdomen-m02-freeze.json)
- [Independent source/voxel audit](../../../../docs/evidence/br017-audit.json)
- [Teaching slice provenance and terms](../../../../presentation/task-explorer/mixed-tissue/NOTICE.md)
