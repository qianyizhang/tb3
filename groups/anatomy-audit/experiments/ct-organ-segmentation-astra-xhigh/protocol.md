# CT-only ten-organ segmentation: one Astra/xhigh pilot

The user requested an experiment that tests segmentation and organ labelling from
CT alone, with a challenging case, complete reference labels for a finite scope,
fair instructions and no answer leakage. Source task:
codex://threads/01a0c38d-fcff-7670-9ac7-80d0ca352c35. This is an exploratory
capability study, not clinical validation or submission qualification.

Preparation status at handoff: packet, scorer, offline controls and isolation
evidence passed independent parent review. Execution status is recorded in the
native attempt and evaluation records rather than maintained in this protocol.

The single attempt completed normally on 2026-09-21; independent replay exactly
reproduces the frozen scores. See the
[result and interpretation](../../findings/ct-organ-segmentation-astra-xhigh.md).
No further attempt is planned within this pilot.

## Source, admission and reference limits

The selected source is member `s1233` in `Totalsegmentator_dataset_small_v201.zip`,
TotalSegmentator v2.0.1, Zenodo record 10047263. The tracked source manifest pins
the original CT to SHA-256
`5352376d8fd9c0ab582a7fca1443f28762a66b9782d59c645b976771587c0cfc`; it also
pins each source mask. Image data are retained with CC BY 4.0 terms and label/code
material with Apache 2.0 terms. Preserve both notices. The current concept release
is newer;
this experiment deliberately identifies the exact v2.0.1 bytes rather than
claiming to use the latest TotalSegmentator dataset.

The source paper reports that annotations were created or refined under physician
supervision and that all examinations were manually reviewed and corrected when
needed. The v2 maintainers say public labels were improved but may still contain
errors, and specifically warn about colon/small-bowel quality. The pilot excludes
those classes. These facts support a human-reviewed research reference, not
perfect contours or independent clinical adjudication.

Before any model result, eight retained cases were screened for the same fixed
taxonomy. The initial morphology-outlier candidate was rejected because its small
duodenum could be under-annotation. Case s1233 was admitted for the bounded pilot:
the CT is 265 x 265 x 401 at 1.5 mm isotropic spacing with RAS affine; all ten masks
are binary, nonempty, internal to the field of view and 6-connected. Fresh private
triplanar review found anatomically plausible identities and extents, including a
broad duodenal course. Source masks overlap at 57 voxels, so reference and answer
remain separate binary masks. The case is challenging through small-organ CT-only
segmentation; no abnormality claim is made.

## Fixed taxonomy and output convention

The ten targets are spleen; patient-right and patient-left kidney; gallbladder;
liver; stomach; pancreas; patient-right and patient-left adrenal gland; and
duodenum. Every other voxel is outside the target taxonomy. Right and left use
patient anatomy and the supplied RAS affine, not screen position.

Each target is a whole-organ semantic region. For stomach, gallbladder and
duodenum, mark the organ envelope as one region, including the contained lumen or
contents inside that envelope; do not label adjacent bowel. Kidney masks cover the
renal organ region but exclude separately classed cyst regions. Pancreas and
adrenals do not include adjacent vessels, fat or kidney. These dataset-wide
conventions make the task interpretable without revealing case measurements.

The answer contains ten binary NIfTI files named by generic numeric IDs. Every
file must preserve the CT shape and affine. Independent masks may overlap; the
solver must not resolve overlap by assigning a voxel to only one class. A method
note records the approach and uncertainty.

## Solver condition, budget and isolation

One fresh Codex / `openai/gpt-6-astra` / `xhigh` attempt; 7,200 agent seconds,
four CPUs, 12 GiB configured memory cap, no GPU, no automatic retry, continuation
or extension. The host Docker VM has about 7.74 GiB total memory, so the configured
cap is not a guaranteed allocation. The 20% account reserve is retained and reset
credits are not used.
No thresholds, task bytes or case choice may change in response to the output.

Solver inputs are the original CT voxel array on its native grid, with descriptive
NIfTI text/extensions removed but qform/sform codes and affine retained; a fixed
taxonomy with generic file IDs; and the output/orientation/coverage convention.
The solver does not receive masks, GT-derived counts or crops, source/case IDs,
metadata, pathology hints, source URLs, selection results, prior experiment
findings, scorer code/formula, thresholds, reference QC images or evaluator files.

The scientific runtime provides NumPy, SciPy, NiBabel, scikit-image and Pillow,
plus normal shell tools. It is assembled from installed libraries only and has no
TotalSegmentator/nnU-Net package, medical model weights or dataset cache. A future
pretrained-segmenter condition requires a different experiment. The main container
has no source, repository, GT or Docker socket mount. Harbor supplies its normal
per-attempt log bind mounts. An internal network reaches a CONNECT proxy limited
to the model service; direct internet, source hosts and host proxy access are
tested before launch. This bounds observed access but does not prove that public
cases were absent from model training.

## Private evaluation and controls

The primary recorded reward is arithmetic macro Dice over all ten correct semantic
IDs. Report every per-organ Dice. A separate label-agnostic maximum-weight
one-to-one assignment reports matched-organ macro Dice and its label confusion;
only positive-overlap matched pairs count toward identity accuracy, so an all-empty
answer cannot appear semantically correct. Also report foreground-union Dice,
precision, recall, false-positive and false-negative voxels. Missing files,
nonbinary values, unknown mask filenames or geometry mismatch are invalid and
score zero.

Controls on identical reference bytes:

- exact oracle: semantic and matched Dice 1;
- no output and all-empty masks: score 0 with no identity evidence;
- right/left kidney exchange: foreground and matched geometry 1 but semantic and
  identity measures decrease;
- cyclic ID permutation: geometry remains 1 while semantic identity collapses;
- fixed translation and one-voxel erosion: identity remains attached to names but
  geometry/coverage decrease;
- unknown file, nonbinary mask and wrong grid: rejected.

No clinical threshold is invented. A continuous Harbor reward other than zero or
one remains unclassified in native collection and is interpreted from the retained
metric JSON. Oracle/no-op Harbor lifecycles must pass on the frozen task before the
model launch.

The first offline control loader created evaluator-only Python bytecode under
`tests/__pycache__` before the native freeze. It is therefore part of the retained
task digest, but it is absent from the solver image and does not encode reference
arrays or observed model output. The maintained control loader now executes the
scorer source without writing bytecode; a fresh preparation remains byte-for-byte
unchanged across the complete offline control suite.

## Reproduction and operations

The tracked selected-source manifest lists the archive URL and MD5 plus the exact
paths, sizes and SHA-256 hashes of the eleven required members. It also retains
both license texts. Recover only those members from the pinned archive, then
prepare into a fresh destination:

```sh
curl -L -o /tmp/Totalsegmentator_dataset_small_v201.zip \
  https://zenodo.org/records/10047263/files/Totalsegmentator_dataset_small_v201.zip
.venv-br003/bin/python groups/anatomy-audit/experiments/ct-organ-segmentation-astra-xhigh/authoring/recover_source.py \
  --archive /tmp/Totalsegmentator_dataset_small_v201.zip \
  --output /tmp/ct-organ-selected-source
.venv-br003/bin/python groups/anatomy-audit/experiments/ct-organ-segmentation-astra-xhigh/authoring/prepare.py \
  --source /tmp/ct-organ-selected-source \
  --output /tmp/ct-organ-reproduction/task
.venv-br003/bin/python groups/anatomy-audit/experiments/ct-organ-segmentation-astra-xhigh/authoring/controls.py \
  --task /tmp/ct-organ-reproduction/task \
  --output /tmp/ct-organ-reproduction/scorer-controls.json
```

Preparation refuses a populated destination, checks all source hashes, revalidates
array/grid/coverage/overlap properties and writes a hash receipt. Re-score any
answer without Harbor or a writable `/logs` mount:

```sh
.venv-br003/bin/python groups/anatomy-audit/experiments/ct-organ-segmentation-astra-xhigh/authoring/replay_score.py \
  --task /tmp/ct-organ-reproduction/task \
  --answer /path/to/answer/masks \
  --output /tmp/ct-organ-reproduction/metrics.json
```

The frozen execution images are local evidence and are not stored in Git. Their
linux/arm64 content identities and dependency versions are tracked in
`source/runtime-manifest.json`. The supported exact-environment route is Docker
image transfer: on the originating machine, tag the pinned runtime with the
manifest's portable tag, use `docker save` for the four pinned images, and compute a
SHA-256 of the archive. On the receiving linux/arm64 host, verify that out-of-band
archive hash, use `docker load`, and require every `docker image inspect --format
'{{.Id}}'` value to equal the runtime manifest before execution. The archive itself
is not retained by Git, so this establishes a supported transfer procedure rather
than independent recovery from public packages.

```sh
docker tag sha256:3de5f01c3d98a0ed47c9c6ac2ef202807e2761e0ece826d0b514c994f033f107 \
  tb3-ct-organ-runtime-source:v1
docker save -o /tmp/tb3-ct-organ-linux-arm64.tar \
  tb3-ct-organ-runtime-source:v1 tb3-ct-organ-runtime:v1 \
  tb3-ct-organ-transport:v1 tb3-ct-organ-solver:v1 \
  tb3-ct-organ-evaluator:v1
shasum -a 256 /tmp/tb3-ct-organ-linux-arm64.tar
# Transfer the archive plus the printed SHA-256, then on the receiver:
shasum -a 256 /path/to/tb3-ct-organ-linux-arm64.tar
docker load -i /path/to/tb3-ct-organ-linux-arm64.tar
```

For a fresh same-platform rebuild after transferring only the pinned source
runtime, load and tag it as `tb3-ct-organ-runtime-source:v1`, then run:

```sh
.venv-br003/bin/python groups/anatomy-audit/experiments/ct-organ-segmentation-astra-xhigh/authoring/build_images.py \
  --base /tmp/ct-organ-reproduction \
  --source-runtime tb3-ct-organ-runtime-source:v1
```

The build script verifies the transferred runtime identity and audits scientific
packages before building and pinning the solver, transport and evaluator. A fresh
build is functional environment preparation; only verified transfer of all four
frozen image identities reproduces the exact execution environment. Runtime image
build/pinning and network preflight remain separate from model execution.

The default task and operational ledger live under
`.local/ct-organ-segmentation-astra-xhigh/`. Native `med run` creates the freeze,
attempt and observation records. Preserve setup failures, partial work and normal
negative results separately. No remote publication or broad cohort expansion is
authorized by this pilot.
