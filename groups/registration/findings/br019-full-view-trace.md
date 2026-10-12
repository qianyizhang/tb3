# BR-019 full-view trace: from CT volume to recovered slice pose

The retained full-view Terra/high attempt recovered a section from the same CT
crop after early intensity searches found wrong poses. Its submitted transform
passed the original geometry checks: **0.000477 mm RMS / 0.000744 mm maximum**
over 49 image-grid points. This explains a successful historical run; it does
not reopen the retired task or establish clinical precision.

## Input, output and reference boundary

- **Input:** one 180-cubed thoracic crop at 1.5 mm spacing from TotalSegmentator
  small v2.0.1 subject s0915, its voxel-to-LPS affine, and a 192-squared oblique
  section at 0.9 mm/pixel from that same acquisition.
- **Help supplied:** pixel/coordinate conventions, intensity conversion and
  a public trilinear forward renderer. The solver could render a proposed pose
  and compare it with the target.
- **Return:** `pose.json` with a finite, rigid, right-handed 4-by-4
  `slice_to_lps` transform. The translation locates the top-left pixel centre.
- **Evaluator only:** the generating transform and 7-by-7 physical point check;
  RMS <= 3 mm and maximum <= 5 mm both had to pass.
- **Boundary:** this is the entire solver-visible CT crop, not the complete
  original patient scan. The reference is not an expert-certified cardiac plane.

The [retained protocol](../../../docs/research-rounds/BR-019-slice-registration.md),
[results](../../../docs/research-rounds/BR-019-results.md) and
[author audit](../../../docs/evidence/br019-author-audit.json) establish the
historical task/controls. This analysis also reads the actual instruction,
native arrays, scorer, saved answer and trace; hashes are retained below.

## Consequential observed actions

All step numbers refer to `cardiac-r01__7yuEb55/agent/trajectory.json`, attempt
`attempt-0b9d524174a3e1a9e4bb4901`. This is a selection of consequential tool
actions, not a complete optimizer history or an account of hidden cognition.

| Phase | Trace evidence | What it establishes |
| --- | --- | --- |
| Inspect input | Steps 7, 9–11 read the forward renderer and metadata, inspect array bounds, and display target/axial images. | The solver had the full crop and its geometry. |
| Early search | Steps 13 and 17 construct a six-parameter search, differential evolution and Powell refinement; step 18 displays the resulting section. | A plausible section can be a wrong physical pose. |
| Revise search | Steps 19–25 try intensity least squares, restarts and edge terms. | The path was not one immediately successful optimization. |
| Enforce volume bounds | Step 29 constrains each orientation's section centre so its corner reach fits the acquired crop. Step 41 prints a later smoothed-intensity result. | The finite CT volume constrains translation, but this alone did not yield the final pose. |
| Match coarse silhouette | Step 42 switches to a Gaussian-smoothed `target > 5` foreground and a logistic candidate foreground; step 43 logs eight restart results. | Seed 6 has the smallest reported silhouette objective in that batch. |
| Refine and submit | Step 43 refines full-resolution intensity with eight reported function evaluations and prints the final matrix. | The saved answer preserves the resulting full-precision transform. |
| Check public render | Step 45 reports 56 differing pixels, maximum intensity difference 1, and a rigid right-handed matrix. | The submitted pose reproduces essentially the same-source target texture. |

## Reconstructed states and the preserved final result

Intermediate geometric errors below are **post-hoc diagnostics using private
reference geometry**, not observations available to the solver or overwritten
historical scores. Logged intermediate matrices/parameters have limited precision.
The displayed candidate images are freshly derived from those poses and the native
CT; no historical authoring script or optimizer was executed.

| Selected state | Pose source | RMS / maximum point error (mm) | Image intensity RMSE |
| --- | --- | --- | --- |
| First selected wrong match | Step 17 printed matrix | 129.899 / 225.985 | 46.150 |
| Later bounded wrong match | Step 41 printed matrix | 123.876 / 216.114 | 61.836 |
| Silhouette candidate | Step 43 seed 6 parameters, mapped using step 29's bounds | 0.945355 / 1.030578 | 8.162 |
| Submitted answer | Preserved `artifacts/app/answer/pose.json` | 0.000477 / 0.000744 | 0.038976 |

The native rendering of the first selected pose is pixel-identical to the PNG
actually delivered at step 18. Rendering the saved final pose reproduces
**36,808 / 36,864 exact pixels**, 56 differences, and maximum intensity difference
1 from step 45. Recomputed final geometry agrees with the frozen metrics within
1e-10 mm. Original reward and scores remain unchanged.

## Visual inspection and interpretation

The source-derived explainer lives at `.local/anatomy-pose/trace/index.html`.
Its [source recipe](../presentation/anatomy-pose/prepare_trace.py) reads retained
artifacts; [page source](../presentation/anatomy-pose/trace.html) and
[viewer](../presentation/anatomy-pose/trace.js) own the teaching presentation.

- **Inspected:** target/recovery source panels, three orthogonal native CT views,
  first wrong and coarse candidate images, and desktop/mobile rendered stages.
  The wrong candidate shows different sectional structure; the coarse/final
  candidates approach the target's body–lung arrangement and local texture.
- **Volume connection:** candidate corners use the real pose and voxel affine.
  Teal solid borders identify the candidate; the final reader reveal adds an
  amber dashed reference border. The full crop's three context planes can be
  moved independently. They are reader controls, not fabricated solver actions.
- **Derivation:** context uses a 90-cubed trilinear preview spanning all native
  outer voxel centres, window -1000 to 500 HU. Candidate images use native HU,
  the original 192-squared grid and -150 to 350 HU task window. A faint -350 HU
  threshold shell supplies spatial context, not an organ segmentation.
- **Display distinctions:** silhouette panels illustrate the recorded objective
  but use rounded candidate reslices, so they are not an exact replay of each
  internal objective evaluation. Difference mode multiplies absolute 8-bit
  differences by four; this is a display gain, not a geometry score.
- **Supported interpretation:** coarse silhouette matching located a useful
  region for intensity refinement in this observed run. Bounds/objectives and
  search restarts also changed, so this is not a controlled causal ablation.

## Alternatives and limits

The frozen instruction specifies coordinate conventions, interpolation and scoring;
retained controls and current final replay support their geometric consistency.
No new instruction/scorer defect was demonstrated. The reference is the authored
generating transform rather than clinical ground truth; no new clinical
adjudication was performed.

Early search errors are intermediate states in a normally completed successful
attempt, not separate model failures. One same-acquisition subject permits strong
exact-texture matching. Neither submillimetre numerical agreement nor the final
image establishes anatomical understanding or cross-acquisition robustness.
The full original CT scan and a complete continuous optimization history are not
shown; the crop and selected preserved states are the evidence boundary.

## Provenance and validation

- [Workbench evidence manifest](evidence/br019-full-view-trace.json).
- [Visual derivation and source hashes](evidence/br019-trace-visuals.json).
- [Original task brief](../presentation/briefs/tb3-oblique-pose.md).
- [Anatomy trial design](../presentation/anatomy-pose/design.md).

The manifest's pinned record/artifact hashes validate. The native final image and
geometry reproduce the retained values. Browser checks verify phase/reference
visibility, native-coordinate corners for all four candidate poses, CT controls
through all three axes, keyboard operation, 390 px layout and a WebGL-free fallback.
The standalone page makes no external requests. Visual and interpretive judgments
above remain separate from these technical checks.
