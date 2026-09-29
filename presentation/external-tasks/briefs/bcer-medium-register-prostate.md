# Map diffusion prostate MRI into the T2w grid

**Real PI-CAI source inputs are available; no BCER `medium_register_prostate` transform, resampled patient image or independent alignment reference is retained.** Obtain source images through [PI-CAI](https://zenodo.org/records/6624726); a task-specific result would require a run of the [pinned BCER workflow](https://github.com/Albertlongzi/BCER/tree/d10816712793a9e27f2e70640f9afc06f08a0c5c).

## Given

### Original data

The task requires **T2w plus ADC or DWI_highb**. The explainer uses actual native planes from representative PI-CAI case `10001_1000001`: T2w **640 × 640 × 21** at about **0.3 × 0.3 × 3.6 mm**, ADC and high-b DWI each **120 × 128 × 21** at **2 × 2 × 3.6 mm**. The frames are LPS millimeters. Original MHA and prepared NIfTI voxel arrays match in the retained audit, with header-representation differences below 1e-5 mm. This case came from a prior `long_prostate_full` input audit; it is not an official medium-task split or result.

### Supplied helpers

The case manifest, runtime state, typed artifact references and registered tools are **supplied helpers**. `identify_sequences` resolves paths, then `register_to_reference` receives fixed **T2w** and moving **ADC and/or DWI_highb**. The condition has no supplied answer mask or independent registration target. Swapping fixed and moving can produce structurally valid files in the wrong output space.

### Reference-only material

No independent alignment reference, matching saved transform or resampled patient output is retained. The actual native inputs are representative public PI-CAI data, not private target outputs.

## Task specification

The registration tool defaults to **`method=identity`**, meaning physical-space header resampling, and **`interpolation=linear`** for continuous MRI. At each T2w target voxel, the T2w affine yields an LPS point; the inverse moving affine yields a diffusion-grid coordinate; linear interpolation samples that position. A retained non-anatomical witness at LPS **(−24.99, 30.57, −1.65) mm** maps near T2w voxel **(319.5, 319.5, 10)** and diffusion voxel **(59.93, 63.93, 10)**. This coordinate relation does **not** establish anatomical alignment. Rigid and affine mutual-information modes are supported by the tool but were not run here.

## Expected output

The registry expects `transform_path` and `resampled_path`, successful `identify_sequences` and `register_to_reference` stages, path existence and a nonempty resampled NIfTI. Both output slots remain **empty** in this explanation.

## Evaluation

The structural evaluator has no independent landmark, prostate boundary or lesion reference and cannot measure registration accuracy.

## Visual explanation

### Workflow

Persistent source-gap notice → three actual unregistered native images → fixed/moving selection → one shared LPS point on two grids → symbolic identity resampling stencil → empty output slots and fixed/moving swap counterexample → limits. The symbolic grid contains no patient MRI pixels. No model, registration, benchmark judge or visual acceptance run is claimed.

The retained [BCER source audit](../sources/bcer-workflow-audit.json) verifies **15 source files and 7 data/manifest files**; the [resolution receipt](../sources/bcer-medium-register-prostate-resolution.json) binds the medium task and representative input. PI-CAI input use is CC-BY-NC-4.0 for this local noncommercial interpretation.

## Sources

- [Pinned BCER task registry](https://github.com/Albertlongzi/BCER/blob/d10816712793a9e27f2e70640f9afc06f08a0c5c/configs/tasks_registry.json)
- [Pinned registration tool](https://github.com/Albertlongzi/BCER/blob/d10816712793a9e27f2e70640f9afc06f08a0c5c/tools/registration.py)
- [Pinned evaluator](https://github.com/Albertlongzi/BCER/blob/d10816712793a9e27f2e70640f9afc06f08a0c5c/benchmark/benchmark_runner.py)
- [PI-CAI source and terms](https://zenodo.org/records/6624726)
