---
name: litemedsam
description: Create or refine medical-image segmentation masks with the environment's LiteMedSAM tool, using image inspection, bounding-box prompts, and mask review.
---

# LiteMedSAM

Turn an inspected medical image and explicit boxes into candidate binary masks.
The agent supplies localization and semantic identity; this model supplies contours.
Use this capability when completing a task that needs segmentation masks, even
if the task does not explicitly name LiteMedSAM. Follow the task's tool-access
rules and requested scope.

## Run

Use the bundled `scripts/segment.py` with Python 3.12. It launches the provisioned
runtime automatically. `LITEMEDSAM_ROOT` names a directory containing
`.venv/bin/python`, `vendor/LiteMedSAM/`, and `weights/lite_medsam.pth`.
The default is `/opt/litemedsam`; use the runtime location supplied by the environment.

```sh
python3 /path/to/litemedsam/scripts/segment.py \
  --runtime /path/to/runtime --image /path/to/slice.png \
  --boxes /path/to/boxes.json --output /path/to/NEW-result --device cpu
```

`boxes.json` is `[[x0,y0,x1,y1], ...]` in **original image pixels**, with upper
bounds exclusive. For example `[[20,30,100,120]]`. Input is an 8-bit grayscale
or RGB PNG; output is `masks.npy` (N,H,W boolean), individual binary PNGs, and
`receipt.json` with boxes, input/checkpoint/code hashes, backend and timings.
Multiple boxes on one image reuse its embedding. Output directories must be new.
The script verifies the pinned checkpoint before loading it.

On Apple Silicon use `--device mps` when available. Linux containers use
`--device cpu`; Docker cannot access the host's MPS backend. Device
failure stops the call rather than silently substituting another backend.

## Image and prompt contract

- Inspect the actual pixels before choosing boxes. Enclose the desired structure
  with a little context; avoid including unrelated organs where possible.
- For CT, explicitly window to uint8 and record the HU window and voxel-to-image
  mapping. A useful abdominal starting window is [-160, 240] HU, not a universal
  modality setting. No automatic NIfTI orientation or intensity conversion occurs.
- Coordinates are x=column, y=row. When displaying `volume[:, :, k].T`, x=i,
  y=j; transpose a returned mask back before placing it into that volume slice.
  Preserve the original affine and spacing. Record any crop or resampling transform.
- Inspect outputs for leakage, missing components and implausible shape. Log
  revised boxes as new calls. Model scores are not calibrated correctness scores.
  A 2D box mask does not establish 3D consistency or anatomical identity.
- Use only solver-visible inputs. Reference-derived prompts are calibration,
  not autonomous localization; do not seek evaluator masks to improve a prompt.

## Show and retain

Save the image/box provenance and masks. For colored overlays, include a visible
legend with swatches or line samples in the **exact overlay colors**. Match line
styles too; label reference, prediction and prompt separately, including when a
reference is unavailable. Do not rely on color names in a prose caption alone.
