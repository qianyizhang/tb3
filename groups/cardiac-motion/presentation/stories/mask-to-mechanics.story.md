---
schema: 2
id: mask-to-mechanics
title: 'A moving wall mask is not a material-motion map'
locale: en
purpose: Explain BR-035's actual all-phase mask inputs, answer-owned fixed tetrahedral mesh,
  saved local tensor fields and separately revealed simulator material diagnostics.
scope: One STRAUS synthetic wall case, two original saved answers, and one distinct clinical LV cavity transfer.
recipe: cardiac-mask-mechanics-v1
asset_pack: retained-mask-mechanics-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- groups/cardiac-motion/presentation/briefs/tb3-mask-to-mechanics.md
- groups/cardiac-motion/presentation/sources/mask-mechanics-audit.json
- groups/cardiac-motion/presentation/sources/mask-mechanics-resolution.json
- docs/evidence/br035-segmentation-mechanics-results.json
- scripts/build_mask_mechanics_assets.py
---

# The mask gives a wall at each phase, not a tracked tissue point

## Start with the thirty supplied masks

```beat
id: input-masks
scene: input-masks
frames: 150
caption: Thirty independent myocardial-wall masks are the entire masks-only input
narration: This STRAUS simulator case supplies a binary wall mask at each of thirty phases.
  The three native orthogonal slices stay in one calibrated frame at one point five
  millimetres per voxel. Orange is supplied occupancy. The masks contain no persistent
  vertex IDs, initial tetrahedral mesh, anatomical directions or tracked points.
visual: Replay actual axial, coronal and sagittal wall-mask slices with fixed slice
  coordinates and native 1.5 mm scale. No ultrasound, saved mesh or private reference.
channels:
  phase: [0, 1]
  condition: [0, 0]
  output: [0, 0]
  reference: [0, 0]
  clinical: [0, 0]
```

## Add appearance only in the second condition

```beat
id: input-images
scene: input-images
frames: 120
caption: Registered ultrasound adds appearance, not motion truth
narration: The second task condition gives exactly the same wall masks plus registered
  ultrasound on the same grid. Grayscale is appearance. It is not a supplied displacement,
  strain field or material correspondence. The masks-only solver never received these pixels.
visual: Reveal the actual registered ultrasound beneath the same orange masks on three
  calibrated native slices; keep output and private simulator reference hidden.
channels:
  phase: [0.3103448275862069, 0.3103448275862069]
  condition: [1, 1]
  output: [0, 0]
  reference: [0, 0]
  clinical: [0, 0]
cut: intentional-cut
```

## Give the answer its own initial mesh

```beat
id: mesh-construction
scene: mesh-construction
frames: 144
caption: Frame-zero occupancy becomes an answer-owned tetrahedral mesh
narration: The masks-only saved answer builds sixty-three thousand three hundred twenty-six
  vertices and two hundred thirty-three thousand eight hundred sixty-five tetrahedra from
  the first mask. Five cells per occupied voxel fix the topology. The cyan sampled vertex
  cloud and highlighted tetrahedron come from that submitted answer, not from a hidden
  source mesh. One in ninety-six vertices is drawn for display only.
visual: Hold phase zero, pair actual input slices with fixed-camera sampled saved vertices
  and one highlighted answer-owned cell. Do not show the private simulator mesh.
channels:
  phase: [0, 0]
  condition: [0, 0]
  output: [1, 1]
  reference: [0, 0]
  clinical: [0, 0]
cut: intentional-cut
```

## Keep connectivity while the wall changes

```beat
id: fixed-connectivity
scene: fixed-connectivity
frames: 180
caption: Shared vertex indices are a proposed tissue map
narration: The submitted mesh preserves tetrahedron indices across all thirty phases.
  Source masks constrain occupied shape; the answer chooses how each mesh vertex moves
  between phases. A persistent index is a hypothesized material correspondence, not
  evidence that the simulator tissue point was tracked.
visual: Animate two supplied mask slices beside the sampled saved moving mesh and the
  same highlighted tetrahedron. Keep camera, slice locations and millimetre scale fixed.
channels:
  phase: [0, 1]
  condition: [0, 0]
  output: [1, 1]
  reference: [0, 0]
  clinical: [0, 0]
cut: intentional-cut
```

## Inspect one saved cell's tensor arithmetic

```beat
id: deformation-gradient
scene: deformation-gradient
frames: 168
caption: F, E and J are computed on the answer's chosen correspondence
narration: Four saved vertices make three reference edge columns Dm and current columns
  Ds. The stored deformation gradient F equals Ds times inverse Dm. Full Green–Lagrange
  E equals one half of F transpose F minus identity, and J is determinant F. These
  dimensionless fields are checked against the saved vertices. Positive J tests local
  orientation; it does not prove tissue identity or global injectivity.
visual: Show the same answer tetrahedron at phase zero and current phase at one fixed
  local millimetre zoom, beside its actual saved three-by-three F/E arrays and J.
channels:
  phase: [0, 0.6206896551724138]
  condition: [0, 0]
  output: [1, 1]
  reference: [0, 0]
  clinical: [0, 0]
cut: intentional-cut
```

## Compare domain sections without claiming material accuracy

```beat
id: occupancy
scene: occupancy
frames: 168
caption: The mask-and-image answer also fits the wall, with different cells
narration: The independently authored masks-plus-ultrasound answer uses six tetrahedra
  per occupied voxel. On the same fixed slices, dashed orange is supplied wall mask
  boundary and solid cyan is its saved mesh section. Its thirty-phase mean voxel-centre
  Dice is zero point nine three two eight. This measures domain fit, not material tracking;
  the two methods and tetrahedralizations differ, so this is not a controlled image ablation.
visual: Replay three same-grid source slices and the retained masks-plus-images answer's
  saved mesh sections, with source and answer colors and line styles labeled.
channels:
  phase: [0, 1]
  condition: [1, 1]
  output: [1, 1]
  reference: [0, 0]
  clinical: [0, 0]
cut: intentional-cut
```

## Show the occupancy ambiguity analytically

```beat
id: material-ambiguity
scene: material-ambiguity
frames: 144
caption: The same occupied cylinder can be untwisted or twisted
narration: In the retained analytic control, twisting each cylinder slice preserves
  exactly the same occupied domain while changing tangential motion and strain.
  Its determinant J can stay one. This is an analytic example, not a patient or
  STRAUS image. Masks alone cannot uniquely select the material map.
visual: Draw two equal cylinder silhouettes with untwisted and twisting paths; label
  identical occupancy and different material trajectories. Do not depict it as a solver result.
channels:
  phase: [0, 0]
  condition: [0, 0]
  output: [0, 0]
  reference: [0, 0]
  clinical: [0, 0]
cut: intentional-cut
```

## Reveal fixed simulator material probes

```beat
id: reference-probes
scene: reference-probes
frames: 180
caption: Private simulator paths test the saved material map
narration: The reader now sees one fixed source-cell centroid, located barycentrically
  in the answer's initial mesh and followed without later realignment. The plotted
  radial engineering strain is norm of F times the private radial direction minus one,
  in percentage points; it is not an E component. This one probe illustrates the
  comparison. Across reference-volume-weighted usable cells, masks-only radial
  error is seven point three seven percentage points, above the five-point target.
visual: Explicitly reveal private source radial strain as dashed purple against the
  saved masks-only prediction in cyan, with fixed minus-ten to fifty pp scale and
  separate aggregate coverage/error text. Keep reference absent before this chapter.
channels:
  phase: [0, 1]
  condition: [0, 0]
  output: [1, 1]
  reference: [1, 1]
  clinical: [0, 0]
cut: intentional-cut
```

## Keep clinical cavity transfer in its own domain

```beat
id: clinical-transfer
scene: clinical-transfer
frames: 168
caption: Eighteen clinical cavity masks supply geometry, not myocardial strain
narration: The unchanged program also processes eighteen real LV blood-pool masks on
  a different one point five millimetre grid, with real timestamps from zero to
  zero point seven five one seconds. Those supplied masks already encode about
  forty-five point three three percent geometric ejection fraction. The saved
  cavity volume curve reproduces geometry, while both assessments set myocardial
  strain supported to false. There is no epicardium or tissue trajectory here.
visual: Replay two actual cavity-mask slices and the saved eighteen-frame cavity
  volume curve on a fixed zero-to-one-hundred-forty-millilitre axis. No simulator
  material reference appears in this clinical scene.
channels:
  phase: [0, 1]
  condition: [0, 0]
  output: [1, 1]
  reference: [0, 0]
  clinical: [1, 1]
cut: intentional-cut
```

## State what passed and what did not

```beat
id: limits
scene: limits
frames: 144
caption: Both constructions pass; neither meets radial material diagnostic target
narration: Both original synthetic answers receive construction reward one. At the
  private reference-volume-weighted probes, their aggregate radial engineering-strain
  errors are seven point three seven and five point four five percentage points, both
  over the five-point diagnostic target. Oracle is privileged exact-source material;
  the static control fails construction. These are one simulator case and one separate
  cavity transfer, not clinical myocardial-strain validation or an image-causality test.
visual: Return to the explicitly revealed synthetic material probe comparison with
  both condition-level radial errors and coverage labeled. State the no-clinical-
  strain boundary beside it.
channels:
  phase: [0.3103448275862069, 0.3103448275862069]
  condition: [1, 1]
  output: [1, 1]
  reference: [1, 1]
  clinical: [0, 0]
cut: intentional-cut
```
