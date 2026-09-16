# BR-019 — Recover an oblique CT slice pose

Captured 2026-09-16 from the user's new request in the
[owning task](codex://threads/01a0a845-7c2d-7992-a662-24d52831af90): curate a real CT,
generate a useful landmark-oriented planar section, recover its pose with
tolerance, author-test feasibility and leakage, then delegate a benchmark.
The proposed progression is partial view, another acquisition of the same
patient, and another modality. No historical conversation retrieval was needed.

**Completed:** [Both Terra/high attempts passed](BR-019-results.md), with four
healthy matched controls. Full and partial snapshots are retired as difficulty
candidates. [Candidate card](../../catalog/ideas/slice-to-volume-registration.json).
The pretrial hypothesis and contract below are retained unchanged.

## Task and hypothesis (before model results)

This is **rigid slice-to-volume registration**, not radiographic projection
registration. Recover a pixel-to-patient transform for a supplied oblique
section. A thin reslice is still MPR; the distinction is anatomical obliquity
and inverse localization rather than selecting a reconstructed axial index.

The compact deliverable is one 4-by-4 rigid matrix, with explicit pixel centres,
millimetres, LPS patient coordinates, column/row directions and image spacing.
For pixel column `u` and row `v`, the mapping is
`patient_LPS = T @ [u*sx, v*sy, 0, 1]`. This is a six-degree-of-freedom image
pose. An unbounded plane alone has only three degrees of freedom, but does not
specify in-plane rotation or the origin of the exported image. A 3-by-4 camera
projection matrix would describe a different forward problem.
The first experiment uses one same-acquisition cardiac-region CT crop and an
apex-oriented oblique section. It is a geometric feasibility experiment, not
an expert-approved standard cardiac view or a diagnostic task.

H1: finding the correct alignment from the image is the conceptual crux;
coordinate handling and subsequent refinement should be independently testable.
A normal model pass retires that exact condition as a difficulty candidate.
A failure needs a valid task, healthy controls, normal completion, trajectory
review and an identifiable alignment/coordinate error.

Predeclared conditions: R01 full section; R02 a crop retaining a substantial
cardiac region, with its own origin and no crop offset disclosed. Freeze both
before any model run. Author-test both first. Run one Terra/high diagnostic
per admitted condition; no retries or automatic Sol escalation. These are
feasibility diagnostics, not the six standard final-submission trials.

Acceptance: RMS physical point error <= 3 mm and maximum <= 5 mm over a 7-by-7
grid spanning the supplied image, inclusive. Matrix must be finite, rigid and
right-handed. Report centre error and normal angle separately. Do not score
raw matrix entries, Euler angles or intensity similarity as geometric truth.
These are engineering tolerances for a 1.5 mm source grid, not validated
clinical tolerances. Partial-view scores cover only the observed field.

## Research and source screen

- [SLIV-Reg, 2024](https://arxiv.org/html/2410.18683v1): Table 1 reports poor
  random-initialization baselines on CT/MRI slice localization and much better
  learned feature matching. Its discussion identifies initialization as a
  problem and its experiments remove rotation-revealing image borders. This
  is external algorithm evidence, not a prior Terra/Sol failure, and some
  compared methods were designed for projection images.
- [Cardiac plane prediction, 2021](https://pmc.ncbi.nlm.nih.gov/articles/PMC8242184/):
  expert-defined long/short-axis planes provide the eventual clinical target.
  A whole-heart mask alone does not certify a mitral-valve or four-chamber plane.
- [TotalSegmentator small v2.0.1](https://zenodo.org/records/10047263): local
  source receipts and CC BY 4.0 notices are available. Screen eight retained
  CTs; exclude truncated hearts and select a visible full cardiac region.
  Preserve original voxel values and patient geometry in the supplied crop.
- [Official MM-WHS page](https://zmiclab.github.io/zxh/0/mmwhs/): useful cardiac
  substructure labels, but explicit no-third-party-dissemination terms and a
  registration form. Do not use mirrors to evade those terms. Not selected.
- [Learn2Reg](https://arxiv.org/html/2112.04489v2): candidate for later
  paired intra-patient MR/CT or inspiratory/expiratory CT experiments. The
  challenge site returned HTTP 403 during this screen; no pair admitted yet.
  The paper confirms that the paired abdominal data and lung CT pairs have
  already undergone affine alignment. Shared image coordinates must not be
  mistaken for a recovered transformation; organ masks are not dense
  correspondence truth. The additional 90 training MR/CT scans are unpaired.
- [AI-CVM/Cardiac-CT](https://huggingface.co/datasets/AI-CVM/Cardiac-CT): promising
  chamber labels, but the current card requires gated contact sharing, declares
  CC BY-NC-ND 4.0, and says public release is pending despite other release
  language. Not admitted or downloaded; no redistribution assumption.

## Author pilot and admission

Eight retained source CTs were visually screened. s0915 supplies a complete
heart region; s0965 has truncated coverage. The final public input is an
axis-aligned 180-cubed CT crop at 1.5 mm spacing, with unchanged source HU
values. R01 is 192-by-192 at 0.9 mm/pixel. R02 is a 128-by-128 crop at the same
spacing. Both are within the source volume at all corners. The initial
unfrozen preparation rejected out-of-volume corners; centre/FOV were corrected
before creating any task snapshot or running a model.

The author solver reads only the public arrays and geometry, starting at the
volume centre with 64 broad orientations. R01 passes at 0.000431 mm RMS in
4.62 s of numerical execution; R02 at 0.000559 mm in 3.59 s. These times exclude
authoring and are not model-effort comparisons. The same-source pixel matching
is extremely informative. Neither result establishes submillimetre clinical
accuracy. The solver was authored with knowledge of the task design; its code
has no truth, mask, anatomical landmark or generation-seed input. A blind model
trial is the independent discovery check.

All fourteen geometric controls behave as expected (seven per condition),
and an independently implemented interpolator agrees at 204 test locations.
PNG metadata are empty, NPY contains image samples only, and NPZ keys are
exactly `hu` and `voxel_to_lps`. Target pose, labels, generator and crop offsets
are absent from the agent build context. Both conditions were frozen together
before delegated model execution. [Freeze](../evidence/br019-freeze.json).
An additional twelve post-freeze boundary/malformed-output checks pass, without
changing the verifier: 2.99 mm translation accepted, 3.01 mm rejected, and NaN,
empty, wrong-shaped and reflected transforms rejected for each condition.
[Author audit](../evidence/br019-author-audit.json).
An isolated Linux replay used the actual public-only R01 agent image, copied
in just the author solver, and had no host mounts or hidden files. It also
passes at 0.000431 mm RMS in 4.51 s. This confirms feasible execution in the
benchmark environment; it does not establish that the model will discover
the method. The disposable control container was removed afterward.

## Controls and information boundary

Only cropped CT samples plus voxel-to-LPS geometry, target PNG/array, target
pixel spacing, the forward sampling convention and attribution reach the
agent. CT geometry is necessary input. Target pose, landmarks, generation
code/seed, crop offsets, labels, filenames revealing location, verifier and
oracle stay out of the image. Public source retrieval is permitted; the
newly authored target pose is not a published source annotation.

Author feasibility must run a solver that consumes only public inputs, with
no truth-derived initialization. Its result is graded afterward. Separately
check exact truth, a small accepted perturbation, large translation, mirrored
image axes, RAS/LPS confusion, non-rigid matrices and absent output. Audit PNG
metadata, NPZ keys, archive members and frozen Docker COPY/ADD boundaries.
Use an independent point-mapping verifier and separately implemented sampler
check, not just the same rendering function for generation and acceptance.

Same-volume rendering preserves matching texture and interpolation artifacts;
success establishes localization feasibility, not anatomical understanding or
cross-acquisition robustness. Report this explicitly instead of trying to
ban valid registration algorithms.

## Later progression

Partial field of view is a clean first change. Different acquisitions require
known patient pairing, cardiac/respiratory phase review and independent
landmarks: deformation can make one rigid pose inadequate. Cross-modality is
a separate identification/metric problem, and sharing the same dataset does
not establish paired subjects. Admit those stages only with an adequate
transform model and independent correspondence truth; do not label deformable
anatomy a failed rigid registration. No such trials are authorized by this
document alone.
