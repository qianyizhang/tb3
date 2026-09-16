# BR-021 authoring and evidence

Real respiratory deformation, with matched sparse 2D-to-3D and 3D-to-3D
correspondence tasks. See the [protocol and source review](../../../docs/research-rounds/BR-021-anatomical-deformation.md),
[frozen task hashes](../../../docs/evidence/br021-freeze.json) and
[author audit](../../../docs/evidence/br021-author-audit.json).

The private source scans, manual labels, tasks, configurations, generated
reports and model traces remain under ignored `runs/br021-deformable/` and
`runs/br021-deform-*/`. None of this directory is copied into a model image.
The 2D agent receives only the destination volume, source view and nominal
source frame/query pixels. The 3D agent additionally receives the source
volume and exact source query positions. Destination annotations and graders
are in a separate verifier image.

## Author workflow

1. `fetch_source.py` selectively retrieves the three manually annotated
   validation pairs from the official archive using the retained archive
   index. Source-page metadata, ZIP indexes and official reference CSVs are
   retained locally; this script is not a complete downloader for those
   provenance prerequisites.
2. `audit_source.py` checks downloaded hashes, image differences, manual label
   linkage, zero-based voxel conventions and privileged rigid/affine residuals.
3. `prepare.py` chooses the first nonrigid pair and an eligible oblique plane,
   then writes both public payloads and private correspondence truth. It
   refuses to overwrite earlier preparation.
4. `baseline_3d.py` and `baseline_2d.py` are the retained initial unsuccessful
   Demons/global-affine baselines. `baseline_patches.py` implements the later
   public-input local patch method. Failed output/code versions remain local.
5. `inspect_points.py` generates the actual source/manual-target image pairs
   used for author visibility review. `build.py` checks the public-input
   baselines, independently validates interpolation and exercises geometric
   wrong-answer controls before constructing separate tasks/verifiers.
6. Build each task's `environment/` image as `br021-deform-{2d,3d}-author`.
   `isolate_author.py` then runs the patch method inside each image with no
   network, only a read-only author script mount and a separate output mount.
   `freeze.py` requires both isolated answers to pass and fixes task hashes.
7. `run_trials.py deform-3d` / `deform-2d` each run oracle, nop and one fresh
   Terra/high attempt. Frozen bytes are checked before and after; retries are
   disabled. A raw existing local runtime configuration supplies credentials;
   its contents must not be exported. These commands are research trials,
   not repository hygiene checks.
8. After delegated execution and image/trace auditing, `collect.py` extracts
   allowlisted receipts, regrades answers and checks actual runtime contexts.
   `present.py` builds a local interactive CT-patch review from retained answers.

Author runtime: Python 3.12, NumPy 2.2.6, SciPy 1.15.3, Pillow 11.3.0,
Nibabel 5.3.2 and SimpleITK 2.5.2. Model images have the same numerical packages
except Nibabel, since public arrays are NPZ. The separate grader uses Python
standard-library scalar geometry only. No library ban or shortened reasoning
budget manufactures difficulty.

The transform model changed from BR-019/020. A plane can deform into a curved
surface; these tasks ask for eight corresponding physical positions, not one
projection matrix. The 2D source frame is known. Neither sparse-point success
nor this single selected case validates a dense field, clinical utility or a
general model capability. Public source annotations remain a contamination
possibility even when image isolation and recorded tool traces look clean.
