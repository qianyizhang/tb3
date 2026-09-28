# Separate bone and soft tissue with dual-energy CT

Recover two material-density maps from paired synthetic photon-count sinograms.
The saved result supports inspection of the source operation; the active generic
scorer does not evaluate the complete two-material output contract.

## Value

Two spectra weight material attenuation differently. The task first estimates
one tissue and one bone line integral for each ray, then reconstructs each
material map. Calibration, units and preserving both material identities matter.

## Given

### Original data

One synthetic parallel-beam phantom, not an acquired patient scan.
`raw_data.npz` contains float64 `sinogram_low` and `sinogram_high`, each
`(1,128,180)`: case, detector bin, projection angle. Angles are 0 through 179
degrees. Observed counts range from **23,369 to 1,003,718** at low energy and
**115,531 to 1,504,357** at high energy. Values are photon counts, not HU.

### Supplied helpers

The raw archive also supplies two spectra and two mass-attenuation curves,
`(1,2,131)`, over 20–150 keV in 1 keV bins. Simplified Gaussian spectra peak at
55 and 90 keV, cut off above 80 and 140 keV, and sum to approximately 1 million
and 1.5 million incident photons per ray. Density-map pixels are **0.1 cm** wide.

The released attenuation coefficients, in cm²/g, exactly match the source's
linearly interpolated approximate tables. They are not exact NIST ICRU-44 values:
at 20 keV the released tissue/bone values are 0.770/3.200, versus NIST
0.823/4.001. The audit retains the released calibration unchanged.
L2 adds an approach; L3 also adds software design.

### Callable tools

Python numerical dependencies. The local audit used existing packages to replay
forward fixtures, saved-intermediate filtered backprojection and score controls.
It did not run material optimization, an agent, dataset generation or installation.

### Reference-only material

`data/ground_truth.npz` contains tissue and bone maps `(1,128,128)` in g/cm³,
plus their sinograms `(1,128,180)` in g/cm². They describe geometric regions,
not annotated patient anatomy. The published phantom fixture equals these maps.
Actual L1/L2/L3 file seeding copies **this complete truth archive** with `data/`.
A reader-facing reveal therefore does not establish a private evaluator boundary.

## Task specification

For each ray and energy, add the products of material line integral and mass
attenuation, exponentiate the negative sum, multiply by each supplied spectrum,
and sum over energy. The source generator samples Poisson counts from this
expectation. The full generator was inspected but not executed.

The source inverse uses a nonnegative Newton-style update for the two material
line integrals. Its executable Hessian includes second derivatives of expected
counts. Each material sinogram is divided by the **0.1 cm** pixel width before
ramp-filtered backprojection; reconstructed negative densities are clipped to
zero. No synthetic optimization trajectory is claimed by this audit.

## Expected output

Separate tissue and bone density maps. Native `main.py` writes
`output/reconstructed_maps.npz` with both maps and both material sinograms.
The released saved archive has a leading singleton case axis. The active generic
end-to-end harness instead requires a single `output/reconstruction.npy` and
matches a squeezed array to a reference by shape and key ranking.

## Evaluation

Both saved maps reproduce **exactly** from the saved material sinograms through
the source backprojection wrapper with scikit-image 0.25.2 and nonnegative
clipping. This is saved-intermediate replay, not fresh material decomposition.

Native metrics evaluate both maps inside the truth-derived body mask:
**8,797/16,384 pixels**, where tissue plus bone density exceeds 0.01 g/cm³.
The native NCC is cosine similarity without mean centering; NRMSE is divided by
each reference's range inside that mask.

| Saved map | Native NCC | Native NRMSE |
| --- | ---: | ---: |
| Tissue | 0.9980 | 0.0620 |
| Bone | 0.9886 | 0.0404 |
| Mean of the two material scores | 0.9933 | 0.0512 |

These are newly replayed scores. No `evaluation/metrics.json` or pass thresholds
are listed in the pinned source tree or asset manifest. There are no shipped
historical metrics against which to verify these values, and no benchmark pass.

The actual generic scorer selects `ground_truth.npz:tissue_map` for any
128×128 output, including a submitted bone map. For a 128×180 output it selects
`bone_sinogram`; a stacked `(2,128,128)` output fails reference matching.
Tissue truth alone and bone-sinogram truth alone each receive generic NCC **1**
and MSE **0**, despite neither being the complete requested pair of density maps.
Native NPZ alone fails the generic filename check. The separate non-filesystem
fallback looks for the absent `ground_truth.npy` and reports that error.

Controls also delimit native metrics: halving both true density maps leaves
native mean NCC **1** but gives mean NRMSE **0.3058**. Erasing bone gives mean NCC
**0.5**. Adding density only outside the truth body leaves native scores unchanged;
the generic whole-image score changes. These are scope checks, not corrections
to retained scores or a claim of clinical validity.

## Visual explanation

### Workflow

- Inspect paired native count sinograms and their supplied spectra.
- Follow spectral attenuation at selected rays of the saved material estimate.
- Trace saved material sinograms through pixel conversion and backprojection.
- Compare both saved maps with explicitly revealed synthetic truth.
- Inspect actual truth staging and shape-dependent score controls.

### Input

**Native source views.** Paired count sinograms retain detector-bin
and angle axes. Photon counts, material line integrals and reconstructed
densities are separate quantities with separate scales.

### Supplied helpers

**Released calibration, not a clinical scanner model.** Preserve actual spectra,
approximate coefficients, 1 mm pixels and parallel-beam geometry. Forward checks
at saved rays do not constitute an optimization trace.

### Reference or output

**Saved output and synthetic truth remain separate.** Show both material
identities and matched density scales. Disclose the solver-visible truth archive
when presenting a reader reveal.

## Conditions

| Condition | Supplied help | Work remaining |
| --- | --- | --- |
| L1 · README | README, requirements and complete data directory, including both truth maps and sinograms. | Implement decomposition and reconstruction; this packet does not establish hidden-reference evaluation. |
| L2 · + approach | L1 plus an algorithmic approach. | Implement the numerical method and resolve executable details. |
| L3 · + design | L2 plus software design. | Implement the specified interfaces; source and evaluation directories are not seeded by the local runner. |

## Difficulty

Both materials attenuate both spectra. The inverse depends on their distinct
energy responses, count noise and calibration. A single-map or correlation-only
score can overlook an incomplete output or incorrect density scale.

## Sources

- [Pinned task README](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/ct_dual_energy/README.md)
- [Pinned source solver](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/ct_dual_energy/src/solvers.py)
- [Pinned active scorer](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/evaluation_harness/reference_scoring.py)
- [Pinned numeric assets](https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/ct_dual_energy)
- [Canonical story](../stories/imaging101-dual-energy.story.md)
- [Source and numerical audit](../sources/imaging101-dual-energy-audit.json)
- [NIST tissue mass attenuation](https://physics.nist.gov/PhysRefData/XrayMassCoef/ComTab/tissue.html)
- [NIST cortical bone mass attenuation](https://physics.nist.gov/PhysRefData/XrayMassCoef/ComTab/bone.html)
- [Cited upstream simulator](https://github.com/gjadick/dex-ct-sim/tree/d247c0b36053adfe63d36d74e8be08a2903cf280)

## Coverage

One synthetic 128×128 phantom and saved reconstruction. Twelve task source files,
60 shared files and ten numeric/metadata assets are verified. The cited upstream
simulator uses Siddon ray tracing and fan-beam reconstruction; this benchmark's
parallel-beam adaptation is not claimed to be equivalent. Benchmark and upstream
MIT notices retain their respective copyright holders.

## Gaps

The canonical story illustrates this pinned source condition. The small
`solvers_decompose.npz` fixture was unavailable after bounded TLS/connect-timeout
attempts; material optimization was not executed. All measurements, truth, saved
results and forward fixtures needed for the explainer are available. No fresh
agent result, private-reference validity, benchmark pass or patient accuracy is
established. Original arrays remain unchanged.
