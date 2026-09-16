# BR-030 — vessel repair to diagnostic geometry

Authorized on 2026-09-16 by the user's approval of reference adjudication and
real-error sourcing, plus a request to expand into vessel tracing, rotated
curved planar reformations (CPR) and three-dimensional meshes: “go big.”
This explicitly expands beyond the earlier two-case feasibility scope.

Own new `probes/vessel-geometry/authoring/`, `docs/evidence/br030-*` and ignored
`runs/br030-vessel-geometry/`. Preserve BR-026 snapshots and other sessions'
cardiac/registration work. Earlier brainstorm message IDs were not supplied;
the current user message and its annotated BR-026 conclusion are the source.

## Plan before new outcomes

1. Investigate the BR-026 L-ACA-adjacent disagreement using original source
   labels, source annotation rules and paired CTA/MRA. Do not relabel an
   image-supported addition as anatomically false solely because it disagrees
   with a reference. A computational paired-image review is not independent
   expert clinical adjudication; retain an expert-review packet if unresolved.
2. Obtain actual predictions from a published pretrained segmentation method,
   preserving weights, code, preprocessing, training-overlap limitations and
   the unedited output. Separate an individual checkpoint/crop experiment from
   the published full ensemble. Inspect at least the already curated cases
   before selecting a local error. Do not edit the predictions to force a gap.
3. Research data for a larger clinical workflow. Prefer named coronary or
   intracranial routes with actual image, mask and centerline/geometry evidence.
   Verify downloadable bytes and licenses, not just dataset descriptions.
4. Build a working author prototype from image and segmentation through named
   centerline paths, rotated CPR, orthogonal cross-sections and a world-space
   vessel mesh. CPR must retain a numerical mapping back to source coordinates;
   a plausible-looking picture alone is insufficient. Show a local reviewable
   result. Mesh generation alone may be easy and must not inherit difficulty.
5. Validate geometry independently: physical coordinates, route identity,
   arc-length sampling, frame continuity/rotation, interpolation, source
   round-trip, mesh surface agreement/topology and unintended changes. Use
   analytic phantoms and targeted wrong outputs in addition to source masks.
6. Freeze a larger agent task only after its offered images and reference
   support an unambiguous contract. Score repair, tracing, CPR and mesh
   separately as well as end-to-end. Where only geometry is admitted, label
   it a geometry feasibility task, not a clinical diagnostic validation.
7. If an admitted task is ready, run matched oracle/nop and one fresh
   Terra/high diagnostic with the ordinary 1800-second allowance. Preserve
   normal completion, artefacts and source exposure. No automatic promotion
   into submission or clinical accuracy claims. No failure manufactured by
   arbitrary libraries, time limits or unannounced output conventions.

The purpose of the added outputs is a useful review workflow, not complexity
for its own sake. CPR of a named major vessel is the primary downstream
deliverable; a surface mesh supplies linked spatial context. Disease grading
requires lesion-specific reference evidence and is not inferred from lumen
geometry alone.
