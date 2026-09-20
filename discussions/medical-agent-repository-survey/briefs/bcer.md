# Complete a prostate MRI processing workflow

Identify sequences, align them, segment the prostate, detect candidates, extract features and write a report.

## Value

This assembles intermediate imaging products that can support review. The inspected contract measures workflow and artifact validity.

## Given

### Original data

Prostate MRI: T2-weighted plus ADC and/or high-b-value diffusion imaging.

### Supplied helpers

A case manifest, task contract and typed artifact references organize the supplied case.

### Callable tools

A predefined collection of MRI processing tools, with controller variants and bounded recovery.

### Reference-only material

The inspected contract checks required stages and artifact invariants. It does not supply an independent anatomical accuracy comparison.

## Task specification

Run the six required stages and retain their required artifacts.

## Expected output

Prostate mask, lesion-candidate JSON, feature table and report JSON.

## Evaluation

Required-stage success plus checks such as nonempty masks, matching geometry and valid candidate JSON. These checks do not independently establish diagnostic accuracy.

## Visual explanation

### Workflow

- MRI + case manifest
- Six processing stages
- Mask + candidates + report

### Input

![Three native PI-CAI MRI sequences](../../../presentation/tours/data/task-briefs/bcer-input.png)

PI-CAI 10001_1000001: T2 anatomy, ADC diffusion map and high-b diffusion image. Different resolution and contrast illustrate sequence identification and alignment. Nearest native planes to one physical point, not a registration result.

### Supplied helpers

A locally prepared example manifest records case 10001, domain prostate and T2w/ADC/DWI availability. Original MHA files are retained; geometry-preserving NIfTI copies match BCER’s documented formats. This preparation is ours, not a released BCER run.

### Reference or output

No BCER run was launched. Mask, candidates, feature table and report would be generated outputs; downloaded MRI images do not stand in for them.

## Conditions

| Condition | Supplied help | Work remaining |
| --- | --- | --- |
| Full prostate workflow | Typed tools + case references | Choose valid calls, preserve artifact relationships and complete all stages. |

## Difficulty

A wrong sequence, spatial mismatch or broken artifact dependency can derail a later stage. This differs from recognizing anatomy without specialist tools.

## Sources

- [Task contracts](https://github.com/Albertlongzi/BCER/blob/d10816712793a9e27f2e70640f9afc06f08a0c5c/configs/tasks_registry.json)
- [Public suite template](https://github.com/Albertlongzi/BCER/blob/d10816712793a9e27f2e70640f9afc06f08a0c5c/benchmark/benchmark_suite.template.json)
- [Metrics](https://github.com/Albertlongzi/BCER/blob/d10816712793a9e27f2e70640f9afc06f08a0c5c/docs/METRICS.md)

- [Dataset and manifest instructions](https://github.com/Albertlongzi/BCER/blob/d10816712793a9e27f2e70640f9afc06f08a0c5c/docs/DATASETS.md)
- [PI-CAI public data, Twilt et al.](https://zenodo.org/records/6624726)
- [Sample download and rendering receipt](../samples.json)

## Coverage

Also: short denoising, brain segmentation, reconstruction, registration, and full brain/cardiac workflows.

## Gaps

Public sample acquisition is resolved: three sequences, about 12 MB, verified against ZIP CRCs. PI-CAI uses CC BY-NC 4.0. A BCER run is still needed for output comparisons; no fixed released BCER patient split was found.
