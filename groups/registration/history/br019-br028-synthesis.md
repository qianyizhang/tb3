# Registration: from exact slice recovery to anatomical correspondence

> Historical session synthesis. Use [Registration](../README.md)
> for current questions and presentation. Frozen results and later visual assessment
> remain distinct; old site/run links need [historical context](../../../docs/archive/README.md).

Session synthesis, 16 September 2026. Covers BR-019–024 and BR-028; no new
model trial was run for this report. [Interactive chapter](../../../site/index.html#registration).

**The full-source 3D result is accepted on the user's visual review.** The user
inspected q06, the worst-scoring point, and adjudicated it “good enough.” Retire
BR-028 as a hard-task candidate for this intended use. Its frozen numerical
result remains 2.604 mm RMS / 6.412 mm maximum: a failure under the original
3 mm RMS / 5 mm maximum gate. These are two different judgments, both retained
in the [adjudication record](../../../docs/evidence/br028-adjudication.json). We have not moved
the reference, changed a tolerance, rescored the trial, or claimed clinical
validation. The earlier BR-024 2D-input failure remains a separate condition.

## What changed through the session

| Round | Question and observed result | What we learned |
| --- | --- | --- |
| [BR-019](../../../docs/research-rounds/BR-019-results.md) | Recover an oblique plane from its originating CT. Full and cropped views both pass Terra/high, below 0.002 mm maximum. | Exact resampling texture makes this a numerical inverse problem; it does not require understanding a clinical standard view. |
| [BR-020](../../../docs/research-rounds/BR-020-results.md) | Different B30f/B50f reconstruction kernels. Terra passes at 0.036 / 0.050 mm RMS/max. | Intensity mismatch alone did not make this selected case difficult; broad multistart search and multiscale correlation suffice. Denoising alone was not isolated as the cause. |
| [BR-021](../../../docs/research-rounds/BR-021-results.md) | Real inhale/exhale deformation. Terra passes paired 3D (1.91 / 4.22 mm) and fails single-view 2D-to-3D (12.64 / 23.80 mm). | Nonuniform anatomical motion changes the task from a single plane pose to sparse correspondence. One failure includes a composition bug. |
| [BR-022](../../../docs/research-rounds/BR-022-results.md) | Replay and investigate that failure; two fresh Terra repeats fail and pass. | Fixing the bug alone does not rescue it. Restricted searches and false image matches also matter; the original snapshot is not reliably difficult. |
| [BR-023](../../../docs/research-rounds/BR-023-results.md) | Fresh Sol/xhigh on the same 2D case passes (1.56 / 3.67 mm). | Conditional component tests show its revised q04 initialization matters; a more flexible final transform is unnecessary. |
| [BR-024](../../../docs/research-rounds/BR-024-results.md) | Screen harder respiratory cases. One admitted new patient fails Sol (12.73 / 32.20 mm) despite a passing public-input author method. | Its q04 refinement is trapped near a wrong global estimate; the correct location lies outside the final search. The other screened patient is held, with no model trial. |
| [BR-028](../../../docs/research-rounds/BR-028-results.md) | Add the full source CT to that exact case. Sol reaches 2.60 / 6.41 mm; seven points are within 2.2 mm. | A broad search using real 3D patches recovers the two large errors. The user accepts the remaining worst case visually. |

The original idea concerned landmark-oriented cardiac sections. The completed
deformation experiments use public lung vessel/airway correspondences across
breathing phases. They do not establish recovery of a clinical cardiac standard
plane, cross-modality registration, or dense deformation accuracy.

## The matched formulation contrast

BR-024 already supplied a **complete 121×189 source slice and a full
192×192×208 target CT**. The displayed patches were review crops, not the entire
input. BR-028 adds the full source CT, keeping the original slice, nominal
frame, eight query pixels, target volume, private destination annotations,
grader, and tolerances byte-identical. Independent interpolation reproduces
all 22,869 original pixels within 0.000031 HU from the added volume.

Both attempts use fresh Sol/xhigh sessions with the same 30-minute limit,
four CPUs and 4 GiB. Neither gets the other's solution, author code, labels,
hints, or grader feedback. Both finish normally; runtime is 21m 53s versus
14m 53s. The time difference is descriptive, not an estimated speedup.

| Quantity | Source slice only | Full source CT added |
| --- | ---: | ---: |
| RMS error | 12.731 mm | 2.604 mm |
| Maximum error | 32.203 mm | 6.412 mm |
| q02 | 14.780 mm | 1.891 mm |
| q04 | 32.203 mm | 1.408 mm |
| q06 | 5.821 mm | 6.412 mm |
| Frozen numerical gate | Fail | Fail |
| Later user visual adjudication | No new adjudication | Accepted |

## How the new formulation helped

### 1. It supplies information the old numerical representation could not contain

The old agent repeats its source plane into a thin slab, then fits rigid and
B-spline transforms with SimpleITK. A repeated plane allows a 3D API to operate,
but supplies no new source anatomy perpendicular to that plane.

The new agent loads the actual source CT in `register_work.py`, `local_ncc.py`
and `refine_local.py`. It can compare 3D vessel neighborhoods rather than one
cross-section, and render source anatomy in orthogonal planes. This is a direct
code observation. The inference is that neighboring branches and boundary
shape provide more constraints on which target location is the same anatomy.
We did not isolate the effect of those additional samples with an otherwise
identical solver.

### 2. It escapes the earlier search restriction

BR-024's final local q04 search allows only ±7 mm around a bad dense-field
estimate. The reference requires a 32.50 mm shift in one local axis; even the
closest allowed candidate remains 25.50 mm away. No optimizer could repair
that point within those bounds. Its visible step 68 nevertheless says the
denser fit has resolved the ambiguous landmarks.

BR-028 initially tries full-volume Demons registration, but its saved fields
disagree. It then starts a fresh, broad 3D patch search around **nominal public
source coordinates**, independently of those fields. Offsets are [-22,12],
[-24,16], [-12,18] voxels along the dataset axes. All eight manual destinations
are inside this region, checked only after execution.

The key trace transition is visible step 22: Sol reports that global fields
disagree while direct 3D patch matching gives clearer correspondences,
particularly q02 and q04. Its code corroborates the change. The most directly
supported mechanism is removal of the old search obstruction, combined with
volumetric matching; these two changes are not experimentally separated.

### 3. The decisive candidates are already present before elaborate refinement

At trace step 19, the new search's top q02 candidate is the same at all three
patch sizes, about **2.15 mm** from the reference. q04's top candidates are
about **2.44, 2.44 and 3.02 mm** away. These distances use printed coordinates
rounded to 0.1 mm and are approximate. All 120 printed candidates are retained
in the [new diagnostic receipt](../../../docs/evidence/br028-formulation-analysis.json), not
just these favorable examples.

Sol then compares local translation, affine, rigid and similarity fits, patch
sizes and intensity weights. Final q02 and q04 errors become 1.89 and 1.41 mm.
This supports a correspondence-discovery explanation: the large errors are
removed when search finds the right region, before a sophisticated final fit
could account for the improvement. It does not prove that refinement or visual
review was unnecessary for all eight final decisions.

### 4. It changes which uncertainty remains

Full-volume library registration alone does not solve the task: all four saved
Demons fields fail as complete answers, as does the later B-spline candidate.
Sol uses preinstalled SimpleITK, then its own NumPy/SciPy patch search and Powell
refinement. No new solver download or annotation lookup appears in the trace.

For q06, visible step 35 describes two nearby solutions along the same boundary.
Step 45 favors the lower candidate after local rigid/similarity comparisons.
Its submitted coordinate rounds the 13.5 mm rigid fit. Two earlier Demons
candidates were closer to the manual point (1.02 and 2.40 mm), but their complete
fields were poor elsewhere. “Closer to the manual point” does not establish
that those alternatives are anatomically superior under the user's criterion.

The user's adjudication changes the practical conclusion: the residual q06
offset is acceptable for the intended example. The numerical metric still
measures exact point proximity, while this visual judgment allows a nearby
position that appears to represent the desired anatomy. It does not establish
that the manual reference is wrong or define a new general tolerance. Because
the panels are each centered on their own point, visual similarity alone also
does not mean the coordinates coincide.

## What the evidence supports

The new formulation made useful source depth available and Sol demonstrably
used it. Its independent broad search recovered the two large errors, and
the remaining result is accepted by the user. This is a successful practical
outcome for the full-source example, with the original automated score retained.

One attempt per condition confounds added information, strategy choice and
model variability. A retained 2D author method already passes at 2.13 / 3.42 mm,
so depth was not necessary for every permitted solution. Public annotations
leave possible training contamination. These selected sparse correspondences
do not estimate general registration reliability or clinical usefulness.

For future task design, define whether the target is an exact annotated point
or an acceptable anatomical region before evaluating. Preserve the numeric
metric alongside any human acceptance. No new threshold, trial, or search is
introduced in this synthesis.

## Evidence and reproducibility

- [BR-024 trial and trace audit](../../../docs/evidence/br024-results.json),
  [search geometry and saved stages](../../../docs/evidence/br024-stage-analysis.json).
- [BR-028 trial and trace audit](../../../docs/evidence/br028-results.json),
  [saved candidate scores](../../../docs/evidence/br028-stage-analysis.json),
  [formulation analysis](../../../docs/evidence/br028-formulation-analysis.json),
  [user adjudication](../../../docs/evidence/br028-adjudication.json).
- [Read-only analysis script](../../../probes/registration-deformation/authoring/br028_formulation.py)
  extracts recorded candidates; it executes no solver.
- [Publication provenance](../../../site/registration-provenance.json) records the
  reused CT figure payload and source evidence hashes. Native arrays and raw
  sessions remain local; the self-contained report embeds derived images only.

Figure source: Learn2Reg LungCT 1.11, Hering, Murphy and van Ginneken (2020),
Radboud University Medical Center, [CC BY 4.0](https://doi.org/10.5281/zenodo.3835682).
