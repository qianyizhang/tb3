# Dynamic heart modeling — first working prototype

The scope is now **a deforming myocardial body**, with both ventricles and
derived tissue mechanics. The local Dynamic Heart Lab is working: 30-frame
playback, cutaway sections, three directional strain maps, material rotation,
source AHA regional curves and synchronized ultrasound views. It separates
known simulator motion from a reconstruction and from privileged controls.

[Project plan and experiment history](BR-029-dynamic-heart-modeling.md) ·
[Larger task contract](../../probes/cardiac-reconstruction/authoring/dynamic_heart/TASK.md) ·
[Code and reproduction](../../probes/cardiac-reconstruction/authoring/dynamic_heart/README.md)

## Data curated for the larger task

| Source | Verified useful evidence | Role and limits |
|---|---|---|
| [Multimodality STRAUS](https://humanheart-project.creatis.insa-lyon.fr/multimodalityStraus.html) | Public simulation database of 18 virtual cases. Downloaded the healthy case's 30 US volumes and 30 moving meshes, the LBBB case's 30 moving meshes, and RefMeshP1 anatomical axes. | Main material-motion/strain reference. 11,370 shared vertices and 47,186 tetrahedra. It is simulated biventricular mechanics, not measured human strain. |
| [FeEcho4D](https://feecho4d.github.io/Website/) | Earlier local pilot verified real fetal STIC images, LV/myocardium contours and fitted meshes. | Real-image contour/geometry track. Its fitted meshes do not establish tracked material strain or four-chamber mechanics. |
| [Four-chamber CT mesh cohort](https://zenodo.org/records/3890034) | Publisher describes 24 ED CT-derived heart-failure geometries with tetrahedral labels, ventricular fibers, coordinates and valve planes. | Appropriate geometry for a forward mechanics stage. Static anatomy and valve planes are not observed dynamic leaflets or matched ultrasound/strain truth. Metadata reviewed; no cohort archive downloaded here. |
| [cardioEM-4CH](https://github.com/MatteoSalvador/cardioEM-4CH) | Authors release code/data for pressure-volume dynamics from 400 four-chamber electromechanical simulations across 43 parameters. | Candidate for a circulation/parameter-recovery stage. It is not a matched ultrasound-to-local-strain dataset; not run here. |

The current STRAUS source totals approximately 660 MB including the second
mesh sequence and anatomical reference. All 120 case files have verified sizes
and SHA-256 receipts. Data remain local. Do not combine unrelated cohorts into
a purported patient-specific ground truth, or assume public download implies
unrestricted redistribution.

## What the prototype actually computes

The moving tetrahedra establish a persistent material map. Its deformation
gradient yields Green–Lagrange tensors, directional engineering strain and
Jacobian volume ratios. The two strain measures remain distinct, following the
[EACVI/ASE definitions](https://academic.oup.com/ehjcimaging/article/16/1/1/2403449).
These are volume-weighted material quantities, not a clinical GLS measurement.

A single initial rigid transform aligns the anatomical reference to the US
mesh within 0.0077 mm; evaluation never realigns individual frames. AHA 0 lacks
directional axes. Three positive-label tetrahedra also lack a complete basis;
they are excluded from directional statistics, leaving 99.9928% of LV tissue
volume covered. They remain in geometry/Jacobian checks. Supported reference
strain vanishes within 1.4e-15.

Independent checks cover rigid translation/rotation, identity, known affine
engineering and Green–Lagrange strain, a volume-preserving affine deformation,
and superposed rigid rotation. Errors are below 1e-12. A separate central finite
difference check validates the Jacobian derivative within 1.4e-10.

The reference itself is not exactly incompressible. Healthy myocardial volume
ranges from about 148.5 to 157.9 mL; local J has a 5th–95th percentile range of
0.911–1.012 and a full range of 0.617–1.502. A strict 1% local-volume condition
would reject the source. The first/last samples are not identical; this is
reported as a sample gap, not automatically a failed cycle closure.

## Completed reconstruction screen

The public package contains an initial volumetric mesh with anatomical axes,
120 image frames from four calibrated planes, geometry and a short task. It
contains no later meshes. Image observations are tracked from frame 1 and then
fitted to a material model. This removes initial meshing from the current task
so the difficult part is motion and mechanics.

| Method | Material RMSE | Long. / circum. / radial strain MAE, pp | Tissue volume curve error | Outcome |
|---|---:|---:|---:|---|
| Static body | 6.19 mm | 4.11 / 6.49 / 11.27 | 1.87% | Fails motion/strain |
| Best uniform scaling, privileged | 2.53 mm | 3.53 / 3.09 / 16.72 | 13.85% | Fails motion/strain |
| Best affine fit, privileged | 2.08 mm | 2.99 / 3.03 / 17.02 | 13.45% | Fails motion/strain |
| Affine fit from four videos | 3.76 mm | 2.56 / 3.53 / 16.67 | 11.91% | Fails motion/strain |
| Coupled tissue fit from four videos | 4.03 mm | 4.94 / 5.97 / 6.79 | 1.35% | Fails complete acceptance |

All listed final models have zero inverted elements. The tissue model uses
spatial regularization and a finite-Jacobian penalty. It restores much of the
missing thickening: radial strain error drops from 16.67 to 6.79 points, and
regional radial peak error from 30.02 to 8.07 points. However, material RMSE
worsens slightly, and the local deformation still has errors. Better tissue
volume is not evidence that regional physiology is correct.

The provisional targets were fixed before the initial reconstruction scores:
RMSE <=2 mm; each strain MAE <=5 pp; each direction's mean regional peak error
<=5 pp; zero inverted elements. Neither input-legal method passes all targets.
These are numerical development targets, not clinical tolerances. No independent
agent/provider trial was run, and four sparse planes do not uniquely identify
all unobserved motion. This is calibration evidence for a larger task, not an
admitted hard benchmark or a solved patient inverse problem.

The point-error split explains part of the global result: on LV-labelled
vertices, the tissue model improves RMSE from 2.31 to 1.67 mm. On RV/unassigned
vertices it worsens from 5.28 to 6.10 mm. These four planes were centered using
the initial LV geometry. This is a concrete reason to add full-volume or
additional RV observations before interpreting global recovery difficulty.

The LBBB reference provides a second simulated motion pattern with regional
timing differences. Its presence is a mechanics comparison, not evidence of
an inferred diagnosis or unseen-case reconstruction generalization.

## Bigger task and acceptance boundaries

The immediate task is to recover a material heart that explains the images
and its regional deformation. Full-volume US should anchor admission and
observability testing; sparse multiview reconstruction adds explicit model
assumptions and uncertainty. Sparse contour/geometry initialization can then
be added without conflating tracking with meshing errors.

The larger target includes four chambers, shared septal mechanics, annular
motion, fiber-dependent activation, active force balance and coupled circulation.
The CT cohort and pressure-volume simulations provide useful parts, but not a
single matched video/whole-heart/strain/valve/flow reference. Detailed valve
leaflets need a separate motion reference. A force-based stage must verify
force/energy balance and discretization convergence; a pump stage must reconcile
flow with cavity-volume change. Those outputs are not fabricated by this viewer.

No STRAUS cavity/valve-plane partition was validated here. The downloaded
geometry is myocardial tissue: its volume must not be reported as ventricular
cavity volume or EF. The earlier FeEcho4D EF remains a separate source/task.

## Artifacts, verification and corrections

- [Reference/control results](../evidence/br029-dynamic-heart-results.json),
  [tissue-fit results](../evidence/br029-dynamic-heart-tissue-results.json), and
  [integrity receipt](../evidence/br029-dynamic-heart-integrity.json).
- Local workbench: `runs/br029-dynamic-heart/workbench/index.html`, served at
  `http://127.0.0.1:8768/index.html`. The previous viewers remain at 8766/8767.
- Local corrected outputs: `analysis-v2/` and `tissue-analysis-v3/` under
  `runs/br029-dynamic-heart/`. Full element fields are in NPZ files. The exported
  `deliverables/tissue-model.npz` includes the material mesh and full F/E tensors.
- Local figure: `runs/br029-dynamic-heart/dynamic-heart-summary.png` and `.pdf`.
  These and the workbench are review artifacts containing reference answers;
  tested agents must receive only the separate public package.

The initial tissue solver exhausted its CG limit. Its output is retained;
raising only the linear-solver iteration allowance made all 87 solves converge
in 30.6 seconds. That was a numerical recovery, not a model failure claim. The
three nonlinear steps remain a fixed approximation. The first source-axis
evaluation incorrectly included three undefined directions; those original
results and executed code are retained as superseded artifacts. Current scores
exclude missing directions and assert reference-frame strain is zero. No
prediction, regularization setting or acceptance target changed for this fix.

Browser verification covered playback, phase scrubbing, cutaway rendering,
regional selection, switching strain definitions, model comparisons and hiding
the unrelated healthy videos during LBBB playback. No browser errors were
reported. Code/data receipts and public input inventories were verified. No
publication, commit, clinical deployment or alteration of the closed interview
report occurred.
