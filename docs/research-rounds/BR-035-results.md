# Supplied segmentation enables mesh construction; strain recovery remains partial

[Open the Segmentation → Mechanics Lab](http://127.0.0.1:8772/index.html).
Two fresh Sol/xhigh attempts built their own moving tetrahedral meshes from
full-cycle segmentations and computed finite strain correctly. Both pass the
frozen construction checks. Both miss the separate local radial-strain target.
Their unchanged executables also preserve the supplied clinical cavity geometry
and EF. This is a selected research pilot, not clinical validation.

The [frozen protocol](BR-035-segmentation-mechanics.md) retains the input conditions,
thresholds and timing. [Detailed evidence](../evidence/br035-segmentation-mechanics-results.json)
retains controls, independent regrades, submitted-artifact hashes and clinical
replay receipts. Prior cardiac experiments remain unchanged.

## What Sol received and constructed

Both conditions received 30 complete binary 3D myocardial-wall segmentations on
a 1.5 mm physical grid. The second also received registered ultrasound. The source
is the already audited public [STRAUS simulation](https://humanheart-project.creatis.insa-lyon.fr/multimodalityStraus.html).
No original mesh, tracked vertex IDs, AHA labels, displacement or reference strain
was supplied. Future geometry was intentionally supplied through the masks;
material motion remained private. The initial mesh was constructed by Sol.

Each solver used 63,326 vertices at voxel-cell corners. The mask-only solver
split each occupied voxel into five tetrahedra (233,865 total); the ultrasound
solver used six (280,638). Both registered signed-distance fields and regularized
the deformation, then matched each supplied mask's centroid and total volume.
The ultrasound solver additionally used a smoothed texture residual, capped at
2 mm and projected tangent to the reference boundary. Code inspection confirms
that ultrasound was actually used in that condition.

Sol authored both reconstruction executables, their meshes and interpretations.
The author prepared the observations, froze the verifier, ran the experiments,
independently scored the artifacts and built the viewer. Viewer strain colors
are recomputed from submitted coordinates, not invented or copied from truth.
They show minimum principal Green–Lagrange strain; the directional error scores
below use engineering strain on the source anatomical axes, a distinct quantity.

## Independent synthetic results

| Component | Masks alone | Masks + ultrasound |
| --- | ---: | ---: |
| Agent time, normal completion | 21.55 min | 13.26 min |
| Construction reward | Pass | Pass |
| Mean full-volume mask Dice | 0.9461 | 0.9328 |
| Worst-frame mask Dice | 0.9151 | 0.9061 |
| Reference-volume material coverage | 98.06% | 98.06% |
| Material motion RMSE | 1.615 mm | 1.717 mm |
| LV material motion RMSE | 1.227 mm | 1.057 mm |
| Longitudinal strain MAE | 2.87 pp | 2.90 pp |
| Circumferential strain MAE | 3.51 pp | 3.22 pp |
| Radial strain MAE | **7.37 pp** | **5.45 pp** |
| Regional peak MAE, L / C / R | 3.41 / 1.86 / 3.30 pp | 3.65 / 1.77 / 4.02 pp |
| Regional peak timing, L / C / R | 0.12 / 0.12 / 0.29 frames | 0.12 / 0.18 / 0.24 frames |
| Inverted elements | 0 | 0 |
| Minimum J | 0.0546 | 0.1877 |

Both retain exact mask-derived total volume to numerical precision, by explicit
volume correction. Both calculate F, Green–Lagrange E and J correctly: maximum
absolute discrepancies with independent recomputation are below 2.3e-7, versus
the 1e-4 tolerance. Geometry plus these calculation checks determine the primary
construction reward; resemblance to a particular simulator's material motion is
a separate diagnostic.

Both pass the 2 mm motion target, the longitudinal/circumferential 5 pp targets,
and all regional peak/timing targets. Both miss only the radial MAE target among
the material gates. Region averaging can cancel local differences; passing
regional peaks does not erase a local radial-strain mismatch. Neither result
establishes clinical strain accuracy.

In this pair, the ultrasound solver has lower radial error and better LV motion,
but slightly worse whole-heart motion and mask fit. This is a descriptive
comparison of two independently designed solutions, not an isolated causal test
of adding texture to one fixed algorithm. Both conditions have identical masks,
calibration, verifier and source-oracle bytes, and identical material coverage.
The ultrasound solver's own 0.9483 inverse-map Dice diagnostic is a different
quantity from the independent piecewise-tetrahedral Dice of 0.9328 above.

Material probes are source cell centroids, located barycentrically in each
submitted initial mesh. Scores are volume weighted over covered reference tissue;
LV coverage is 98.58%, and per-region coverage is retained. These values are not
directly comparable to BR-031's nodal RMSE on a supplied source mesh. No per-frame
alignment or target-motion feedback was given to either attempt.

## Mesh-quality qualifications

The frozen checks pass, but both voxel-derived models have six nonmanifold
boundary edges (four incident boundary triangles rather than two), compared with
none in the source mesh. The frozen gate checks duplicate/degenerate tetrahedra,
face incidence, orientation and field correctness; it did not require a manifold
boundary-edge graph. This posthoc finding limits a blanket claim of mesh validity.

At the worst phase, the fraction of modeled reference tissue volume with J<0.2
is 0.1653% for masks alone and 0.0014% for masks plus ultrasound; the source has
none. These are posthoc engineering distortion indicators, not clinical cutoffs.
Report the small affected volume fraction alongside the extreme minimum, rather
than portraying the whole mesh as collapsed. The mask-only model independently
noticed near-collapsed elements and increased regularization before submission.

Positive determinants alone do not certify global injectivity, self-intersection
freedom or active-force equilibrium. A future acceptance contract should add
explicit boundary-manifold and calibrated distortion checks. No frozen threshold
or score has been changed to accommodate the completed results.

## Unchanged-code clinical transfer

Both executables were replayed without network access on the clearer clinical
LV cavity case from BR-034, now supplied with all-phase segmentations. The
1.5 mm mask conversion changes reference EF from 45.3064% to 45.3313%; average
mask-versus-source-surface volume discrepancy is 0.0954%.

| Clinical transfer | Masks alone | Masks + ultrasound |
| --- | ---: | ---: |
| Runtime, 4 CPUs / 8 GB | 40.66 s | 30.15 s |
| Mean mask Dice | 0.9807 | 0.9806 |
| EF from submitted tetrahedral volumes | 45.3313% | 45.3313% |
| EF error versus clinical source surface | 0.0249 pp | 0.0249 pp |
| Construction checks | Pass | Pass |
| Myocardial strain supported | Correctly reports false | Correctly reports false |

All-phase cavity masks already encode EF, and both methods explicitly normalize
their predicted volume to those masks. This is successful geometry preservation
and executable transfer, not independent EF discovery or diagnosis. It should not
be presented as a like-for-like accuracy improvement over the previous raw-image
tracking task. No epicardial boundary or material-motion reference exists for
this clinical case. Both correctly state that cavity deformation is not myocardial
strain. Both also carry a minor incorrect boilerplate limitation saying timestamps
are absent, although the clinical metadata supplies them; no strain rate was
requested, and this does not affect the EF calculation. Submitted files are
preserved unchanged.

An initial attempt to rebuild a replay image with networking disabled missed the
dependency cache and failed before any solver ran. The unchanged Dockerfiles
rebuilt successfully using their original build settings, with all build steps
cached. Replay image index IDs differ from initial trial image IDs; no byte-identical
image claim is made. Public input inventories and the six pinned package versions
were independently checked, and clinical execution itself remained network-disabled.
The failure is retained as infrastructure evidence, not a model outcome.

## Controls, interpretation and next acceptance criteria

The privileged source-motion oracle gets Dice 1.0, motion error below 1e-12 mm
and exact strain agreement. A static source mesh has Dice 0.704 and motion error
6.00 mm and fails construction. Its directional strain errors are 4.11/6.49/11.27
pp. Both Docker oracle/no-output pairs return the expected rewards 1/0. The local
regrades match the model-container scores. Analytic checks cover rigid zero
strain, finite affine strain, vertex-permutation invariance, exact tetrahedron
membership and material-probe location.

An analytic cylindrical domain with z-dependent twist retains exactly the same
segmentation as an untwisted cylinder while having different strain. Thus even
perfect shape agreement does not uniquely recover material correspondence.
These results support the narrower conclusion: **Sol can construct an effective
segmentation-driven 4D mesh and compute its strain; independently correct material
strain and fully satisfactory mesh quality remain additional requirements.**

For a future benchmark, keep three decisions separate: geometry preservation and
numerical correctness; mesh-quality plausibility; and agreement with an independent
material-motion reference. The 5 pp targets are research diagnostics, not clinical
normal ranges or calibrated clinical tolerances. Mask-only uncertainty should be
reported rather than scored as failure to recover uniquely unobservable motion.

This is one synthetic case, two fresh attempts and one selected clinical transfer.
The original source is known to the author; public pretraining exposure remains
unknown. Runtime traces match the requested Sol/xhigh configuration, contain the
frozen instructions and show no external-source retrieval or delegation candidates.
Those observations do not establish provider internals or training-corpus exclusion.
