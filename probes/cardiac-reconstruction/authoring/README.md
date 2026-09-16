# Cardiac reconstruction author pilot

Research owner: [BR-025](../../../docs/research-rounds/BR-025-cardiac-reconstruction.md).
This directory is author tooling, not a TB3 task package. There is no independent
agent trial, trained video segmentation model, or verified clinical measurement.

## Reproduce

Dependencies used: Python 3.12, NumPy 2.2.6, SciPy 1.15.3, Pillow 11.3.0. The local
`.venv-br021` already contains these; it was reused without modifying packages.
Nibabel 5.3.2 was used for source inspection only.

1. Obtain the native source ranges described in `extract_sample.py` from the
   [FeEcho4D release](https://zenodo.org/records/21322299). Confirm HTTP 206 and
   the requested Content-Range. The index is a partial central directory and
   the patient prefix is not a complete ZIP. Check the source terms before any
   redistribution; this pilot keeps patient data local.
2. Extract only the first annotated patient, validate member sizes and CRCs, and
   retain the per-member SHA-256 manifest:

   ```sh
   .venv-br021/bin/python probes/cardiac-reconstruction/authoring/extract_sample.py \
     --index runs/br025-cardiac/source/zip-index.bin \
     --prefix runs/br025-cardiac/source/native/patient001-range.zip.part \
     --output runs/br025-cardiac/source/native/Patient001
   ```

3. Run the CPU baseline and build the standalone local viewer:

   ```sh
   .venv-br021/bin/python probes/cardiac-reconstruction/authoring/pilot.py \
     --source runs/br025-cardiac/source/native/Patient001 \
     --output runs/br025-cardiac/pilot-v1
   .venv-br021/bin/python probes/cardiac-reconstruction/authoring/build_viewer.py \
     --source runs/br025-cardiac/source/native/Patient001 \
     --pilot runs/br025-cardiac/pilot-v1
   ```

   Open `runs/br025-cardiac/pilot-v1/viewer.html` directly. Optionally serve only
   that output directory on localhost. The viewer is standalone and embeds its
   imagery and data; it makes no network requests to load the patient data.

The source case and 30-frame count are deliberately fixed. Coordinates, label
mapping and frame indexing require a fresh audit before using another dataset.
The pilot interprets config ED=2 / ES=17 as one-based filename frames; the source
config does not explicitly declare its indexing convention. Phase errors are
therefore descriptive, not an expert-adjudicated acceptance result.

## Meaning of the comparisons

The baseline fits positive radial distances with angular interpolation around a
provided rotation axis. Its origin comes from plane 1 only. One/two/four/eight
view predictions are serialized before the 36-view comparator or withheld-plane
evaluation. All sparse conditions use the same eight withheld planes and all
30 frames. Each condition fits frames separately; there is no temporal denoiser.

`dense` uses the evaluation planes as inputs and therefore measures source fit,
not generalization. EF and volume errors compare with this **derived** reference.
The source's OBJ mesh is not used as a blood-pool volume oracle: local slices
show two closed cross-sectional loops, consistent with a myocardial shell, and
its native coordinates do not have an audited physical transform here.

Controls include a static mesh, a closed-form sphere for volume integration,
watertight topology/positive-volume checks, and an explicit out-of-plane
deformation that preserves the observed section while changing EF. This last
control proves geometric ambiguity; it is not a second clinically validated
heart. Fixed mesh connectivity does not establish material-point motion or strain.

The first execution reached a floating-point equality assertion in the ambiguity
control. It was corrected to a 1e-12 coordinate tolerance and rerun successfully;
no outcome thresholds or reconstruction parameters were adjusted.
