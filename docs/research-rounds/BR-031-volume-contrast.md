# BR-031 — prospective observation-depth contrast

Declared while the first L1 Terra trial is still running, before any model L1
score exists. If both normally completed L1 Terra/high and Sol/xhigh attempts
miss complete geometry/mechanics acceptance, add one fresh Sol/xhigh trial
with the 30 native 3D ultrasound volumes. Keep the initial mesh, four videos,
output contract, tolerance thresholds, resources and independent reference
identical. Run matching oracle/nop controls on the new frozen task first.

This conditional extension follows the observed initial plane coverage: only
14.39% of material vertices lie within 1.5 mm of any supplied plane inside its
image bounds (LV 16.48%, RV/unassigned 11.11%). Proximity does not prove image
correspondence quality or observability, but it motivates a controlled addition
of information. No reference future mesh, strain or author solution is added.

The extra volumes are copied from the same already-downloaded STRAUS sequence,
without geometric/intensity alteration, with exact native array shape, spacing,
and canonical-to-native mapping specified. The agent can use full volume or
multiplanar methods and ordinary libraries. This is a new observation condition,
not a retry of the same input or a change to failed acceptance thresholds.

The original four withheld scoring planes are contained in the added 3D volume.
Their metric therefore becomes an off-plane cross-section diagnostic in L1V;
it is NOT unseen-view generalization in that condition. Material positions,
strain and reference segmentations remain evaluator-only. Report this distinction
wherever L1 and L1V are compared.

One attempt per condition cannot isolate input effects from strategy variability.
If the added data do not rescue the result, do not claim an intrinsic agent
ceiling, a uniquely solvable benchmark, or a clinical reconstruction failure.
Stages 2–4 and output tracks 6–8 remain outside this bounded screen.
