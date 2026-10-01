> **Matching 300-photon noisy input and truth remain absent: pinned HF raw data uses 1000 photons. Symbolic rays; source fixture expectations appear only later. [Official acquisition](https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/ct_poisson_lowdose/data).**

# Count photons without substituting a different-dose outcome

Trace transmission, count flooring and weighted reconstruction while preserving the release mismatch and evaluator boundaries.

## Value

Count-derived weighting distinguishes rays with different uncertainty; a coherent acquisition condition is needed to attribute reconstruction differences.

## Given

### Original data

Synthetic 256×256 attenuation phantom, 256 views over [0,π), 367 detector channels. Stored sinograms and count weights have shape (1,256,367); angles (1,256). The loader strips the batch dimension and SVMBIR receives (V,1,C). Parallel geometry, nominal detector/pixel spacing 1. Metadata says mm⁻¹ while README says cm⁻¹; no physical conversion inferred. Metadata declares generation seed 42. No new noise is generated. Photon counts are simulation parameters, not a patient dose in mGy or mSv.

The task metadata specifies I0=300 incident photons/ray and high-dose I0=50000. The official bounded listing confirms retained raw/truth LFS hashes differ from the benchmark manifest. Required raw SHA-256 is 631d51212a46e6b56a47f8aae87f9894f71b24510d96d1e6425c8b30291d3e2d; observed is 96cebbf96bb56a1e71ab696563a1b132f741fbf319e471abce8e4219931c0d4a. No matching 300-photon noisy input or truth recovered.

### Supplied helpers

README, metadata, plans, preprocessing, project/backproject and solver code; clean/high-dose arrays bundled. Actual L1/L2/L3 staging copies the complete data directory, including ground_truth.npz: truth is solver-visible. Evaluation fixtures and saved outputs remain outside the workspace.

A manifest-matching physics fixture has I0=300, 256 views and 367 channels. Its expected transmission is a deterministic model fixture, not a noisy acquisition. A native 16×16 bin subset is retained only in the later reader reference, without phantom or saved reconstruction images.

### Callable tools

Python/SVMBIR task scaffold; no task module/function, tool or evaluator executed and no runtime installed. Array inspection and original pure mathematical controls only.

### Reference-only material

Physics/metrics fixtures and saved reconstructions have separate source roles. Reader reveal shows expected-count fixture and evaluator rules; backward, exit and reset cover it. No participant prediction, GT image or saved reconstruction is rendered. Educational hiding does not change solver-visible truth in source staging.

## Task specification

Ax is a dimensionless line integral when attenuation and path-length units are compatible. Expected counts λ=I0 exp(−Ax); counts Y~Poisson(λ), variance λ. Source floors Y to 1, computes −log(max(Y,1)/I0) and uses floored counts as weights. Counts can exceed I0, giving negative post-log values. The post-log inverse-count variance approximation can be poor near the floor; the floored values no longer encode original zero events. Original zeros cannot be distinguished from ones after flooring.

Authored toy Ax=[0,1,3] gives expected counts [300,110.3638,14.9361]. Illustrative Y=[300,100,0] becomes [300,100,1], then [0,1.0986123,5.7037825]. These manually selected counts are not seed-42 draws or patient measurements.

Retained noisy data satisfies −log(weights/1000) across all 93952 bins. Using 300 instead shifts every ray by **−ln(1000/300)=−1.2039728043**. Do not relabel these arrays as the 300-photon condition. Plans advertise SVMBIR q-GGMRF/ICD; actual solver uses project/backproject proximal-gradient TV, normalizes weights by their maximum and clips negative estimates. No convergence or reconstruction claim. The generator's 32²/18-view/I0=10000 fallback differs from the retained fixture and cannot recover this contract.

## Expected output

Actual end-to-end output is **output/reconstruction.npy**, a real 256×256 array. A separate source archive uses recon_fbp/recon_pwls_low/recon_pwls_high. Actual participant path, image and score are null here; saved arrays and historical notebook values are not participant predictions or 300-photon task outcomes.

## Evaluation

The filesystem dispatch uses generic full-array scoring. A separate registered task-aware helper selects recon_pwls_low before recon_unweighted/recon_fbp and crops [26:230,26:230]: **41616/65536 pixels**. Cosine NCC=sum(xy)/(||x||||y||), without mean centering; range NRMSE=RMS error/(max(reference)−min(reference)), with distinct constant-reference guards: the task-local helper returns 0.0 when reference range is zero, while filesystem generic scoring returns infinity. The generic NCC adds a small denominator stabilizer. The filesystem generic path does not flux-rescale image intensity. The separate no-filesystem/Docker fallback in scorer.py instead flux-normalizes the output, uses L2-relative NRMSE with a 1e-30 denominator stabilizer and requires a .npy truth; it is not the same metric route. No backend or scorer was run here.

Original pure scaled-reference and outside-crop controls demonstrate metric limits only. Missing truth discovery can fall back to recon_fbp, which is not recovered truth. No metrics.json exists in the pinned task tree, manifest or complete HF listing; historical notebook thresholds are not installed, so no current pass/fail verdict. These are implementation boundaries, not clinical/model performance or a population denominator.

## Visual explanation

### Workflow

- Missing matched input plus symbolic parallel rays, labelled dimensionless integrals and expected photons.
- Canonical step/count controls teach floor/log/weight mechanics without inventing reconstruction.
- Empty output; later pinned expected-count subset and evaluator rules, covered on backward/exit/reset.

## Conditions

| Condition | Supplied help | Work remaining |
| --- | --- | --- |
| L1 · README | README, complete data directory, requirements. | Choose and implement reconstruction. |
| L2 · + approach | Adds an SVMBIR/q-GGMRF approach. | Resolve differences from the supplied TV implementation. |
| L3 · + design | Adds the software plan. | Resolve outdated function names and implement the method. |

## Difficulty

Weighting, regularization and the count floor can change the solution. Conflicting dose, truth and units prevent attributing saved-array differences to weighting alone.

## Coverage

One synthetic 256-pixel task; 73 source/Git pins, six numerical/metadata assets and retained official acquisition records. Four assets match the manifest; raw data and truth do not. No patient or model capability claim.

## Sources

- [Pinned task README](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/ct_poisson_lowdose/README.md)
- [Pinned scorer](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/evaluation_harness/scorer.py)
- [Official acquisition](https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/ct_poisson_lowdose/data)
- [Maintained audit](../sources/imaging101-poisson-lowdose-audit.json)
- [Resolution receipt](../sources/imaging101-ct-poisson-lowdose-resolution.json)

## Limits and attribution

AI4ImagingLab source/fixtures: MIT; full license retained. No patient findings, measured reconstruction, GT substitution, task trial or new performance result. Reopen after recovering required raw/truth hashes, or pinning a coherent revised release, and reconciling dose, units and effective evaluator.
