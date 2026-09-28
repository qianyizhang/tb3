# Imaging101 CARS numerical teaching pack

Source: AI4ImagingLab/imaging-101-release at
`dc2f668939b21e8312e22529615def610f8611df`; data revision
`a9de559b54849a25988a8a0d8a5e869063a5a7a3` on
[Hugging Face](https://huggingface.co/datasets/starpacker52/imaging-101).
MIT terms are retained in DATA-LICENSE.txt. Exact hashes, staging and scoring
are in [the source audit](../../external-tasks/sources/imaging101-cars-audit.json).

`inputs.json` preserves all 200 source samples with their wavenumber axis and
metadata. No resampling or image synthesis. `reference.json` carries the clean
synthetic spectrum and true parameters, revealed explicitly to the reader.
This display boundary is **not** the released solver boundary: L1/L2/L3 seed the
whole data directory, including ground_truth.npz. L2's approach also names 2400 K.

`contract.json` contains the upstream saved fit, reproduced metrics and two
bounded forward evaluations at 2000 and 2800 K with other parameters fixed.
Those curves are teaching diagnostics, not optimization iterates or agent outputs.
The saved fit is 2391.5641794510043 K, not a new solve. Forward calls emitted
retained NumPy warnings; outputs were finite and source-reference reproduction
agreed within 1.34e-11. No scalar confidence interval is inferred.

Plot x is wavenumber 2280 to 2330 cm^-1, y is dimensionless max-normalized intensity.
Measured points are dark green, saved fit is solid orange, reference is dashed
purple, diagnostic forward curves are blue. Residuals compare saved fit minus
measured at the same source index. Every color has a local key.

No external benchmark or inverse solver was run. Missing pass thresholds stay
missing. One synthetic nonmedical case does not establish capability performance.
