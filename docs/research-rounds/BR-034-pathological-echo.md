# BR-034 — Clinical LV adaptation and functional assessment

The user rejected BR-032's poor scan and asked for a clearer, nontrivial
pathological case, testing Sol's adaptation and diagnosis with modeling. This
new experiment preserves all prior task/evidence bytes. It is authorized by
that request; one fresh Sol/xhigh attempt gets up to 30 minutes, followed by
unchanged-executable checks. No diagnostic output is used for patient care.

## Source selection before the trial

[EchoXFlow](https://huggingface.co/datasets/Ahus-AIM/EchoXFlow) contains clinical
GE Vivid E95 ultrasound with operator-created/adjusted annotations, including
dynamic LV endocardial meshes. The [paper](https://arxiv.org/abs/2605.05447)
describes acquisition in 2025–2026. Data are CC BY-NC-SA 4.0 and kept local.
The current catalog has 37,582 recording entries; this is a later release
than the paper's 37,125 count. The source code inspected is commit
`b782e0a4e3dbaadf3c88fa572710bf4254d86143`. No published pretrained model is used.

After a first-in-order examination, nine smaller archives with single-beat 3D
B-mode and linked meshes were screened. Recorded reference EFs range from
45.31% to 60.29%. The initially preferred 25–45% band yielded no case; selection
was broadened to mild dysfunction before any model run. Of the two lowest-EF
cases, the 45.31% case has visibly clearer borders in the inspected orthogonal
planes. This is a selected feasibility case, not a random prevalence sample.

Primary: `exam_5daf5517464ccc62 / recording_8aef1d9a69fc3bae`.
The native sequence has 25 frames; 18 consecutive frames at approximately
22.6 volumes/s match the annotated beat exactly. Reference EDV/ESV are
121.86/66.65 mL; reference EF is 45.31%. These are clinical surface-derived
references, not independent volumetric imaging or an etiologic diagnosis.

Held-out adaptation patient: `exam_5bed28e510bd10f0 /
recording_096b622cc35c6401`, 35 consecutive annotated frames, reference EF
47.62%. It is used only after the executable has been frozen. Its borders are
less clear, so this is a harder transfer check, not a perfectly matched pair.

Native single-beat volume data are resampled into a 1 mm Cartesian crop
determined from the initial surface alone, with 18 mm padding. The published
mesh-to-render coordinate transform is (-X,Z,Y); volume timestamps are made
relative to the documented acquisition origin. No beat stitching or synthetic
motion is added. Earlier exploratory exports with a missing axis transform
are retained under curation/ef45 and excluded. Reference/image overlays,
timestamp alignment, topology, coordinate round trips and native decoding are
checked before admission. Whole TAR hashes match publisher LFS hashes and
direct Blosc decoding agrees with Zarr. The publisher's per-array hash is not
reproduced by raw C-order byte hashing; its serialization remains unspecified
in inspected loader code. This is recorded, not silently called a hash match.

## Input and task

Sol receives the primary Cartesian B-mode volume, calibration/timestamps,
orthogonal previews and the initial LV cavity surface only. All later reference
surfaces, source identifiers, EF and diagnosis are withheld. The previous
BR-032 fixed-table solver is supplied as optional adaptation context, with its
limitation explained. Sol may replace it. An initial image-based impression is
requested before modeling, followed by an image-driven executable, dynamic
closed cavity mesh, volumes/EF, uncertainty, and a final functional assessment.

This is initialized dynamic reconstruction (Level 1), functional quantification
(Level 6), and bounded functional interpretation (part of Level 8). It does not
test raw-image segmentation from scratch or demonstrate myocardial strain,
valve flow, infarction, ischemic etiology or a diagnosis of heart failure.

## Frozen scoring and controls

Exploratory geometry gates: sampled symmetric surface mean <=3 mm, maximum
framewise surface-distance p95 <=6 mm, EF error <=8 percentage points, and
EDV/ESV relative errors <=15%. These are pilot tolerances, not clinical
certification. The initial frame is supplied, so initial-frame agreement is
not evidence of recovered geometry. Distances sample vertices, edge midpoints
and face centroids; they are not exact continuous Hausdorff distances.

The task's broad functional categories are EF <30, 30–40, >40–<54 and >=54%.
They simplify sex-dependent normal limits in the
[ASE/EACVI chamber guideline](https://asecho.org/wp-content/uploads/2016/02/2015_ChamberQuantificationREV.pdf).
The primary reference is mildly reduced/borderline by this convention.
Score the stated category against the reference separately from consistency
with the solver's own EF. Review unsupported etiologic/strain/flow claims.
An image-only impression versus a post-model impression is descriptive and
does not establish modeling's causal diagnostic benefit.

The exact reference-artifact control must pass, a static initial-surface control
must fail the dynamic/function gates, and a no-output Harbor control must fail.
Freeze protocol, task and oracle bytes before the model attempt. Retain normal
completion, infrastructure failures, artifact validity, geometry, adaptation
and diagnosis as separate outcomes. Do not adjust gates after observing Sol.

After the attempt, freeze the submitted code and run it without network or
model feedback on original input, held-out patient, repeated-initial-frame
input and a circular phase shift. All use the supplied schema and initialization
index. A still input should produce EF <=1 pp and RMS geometric motion <=0.25
mm; a phase shift should preserve the original per-phase volume curve within
2 mL mean absolute error after undoing the shift. Report surface equivalence
as well. These perturbations assess executable response, not clinical accuracy
or proof against pretraining contamination. Each replay has five minutes,
4 CPUs and 8 GB; a replay timeout is an execution limitation, not anatomical
proof of failure. The held-out patient uses the same geometric/function gates.

## Evidence limits

Both patients are public and training exposure is unknown. Recent release,
de-identified inputs and audited tool use do not establish unseen data. Clinical
annotations are operator/software-derived, may contain errors, and are not
material point trajectories. No independent cardiologist adjudication or
patient-level disease etiology is available. Single selected patients and one
agent attempt do not estimate clinical accuracy or an agent capability ceiling.
