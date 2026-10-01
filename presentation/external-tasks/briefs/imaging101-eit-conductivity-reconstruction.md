# Reconstruct conductivity from boundary voltages

Implement a computational method to reconstruct conductivity from boundary voltages.

> **Actual gap:** Native synthetic input; source truth is solver-visible and output/reference scale unresolved. No participant reconstruction. [Official pinned acquisition](https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/eit_conductivity_reconstruction).

## Value

This imaging problem tests the computational step between acquired measurements and an interpretable image or physical-property map.

## Given

### Original data

Matching **native synthetic** voltages are retained, not patient measurements: the 119,474-byte `raw_data.npz` is byte-matched to the pinned HF LFS object. BP/GREIT adjacent-drive protocols contain **208 ordered pairs**; opposite-drive JAC has **192**, not an interchangeable denominator. Native geometry is **376 nodes × 3 coordinates, 686 triangular elements × 3 indices and 16 point electrodes**. Raw arrays omit the README leading batch axis. No participant reconstruction is retained.

### Supplied helpers

Source point-electrode layout, excitation patterns and a conductivity forward model. L1 includes README/data/requirements; L2 adds approach; L3 adds software design. README units are **m, V and S/m**, but point-node ±1 FEM right-hand sides do not establish finite contact impedance, electrode area, AC frequency or calibrated injected current.

### Callable tools

Python and the task’s numerical/model dependencies. End-to-end, function-level and planning modes assess different work.

### Reference-only material

Native raw_data.npz contains anomaly conductivities; data/ground_truth.npz is also copied with the visible data directory. This is not an established blind inversion condition. Reader reveal hides the source truth only from the teaching view.

## Task specification

Preserve each ordered row `[N,M,excitation]`: voltage is potential(N) minus potential(M) for that excitation. **Ground node 16 fixes additive potential gauge**, separate from the homogeneous baseline `v0`; it is not a conductivity reference. Independent authored arithmetic illustrates gauge cancellation only; no FEM/forward/inverse computation runs.

Canonical controls inspect pairing, sign/gauge, inverse assumptions and spatial domain. BP uses `(v1-v0)/sign(v0.real)` and source main multiplies 192; JAC/GREIT use absolute baseline normalization. Source JAC/GREIT use p 0.5/lambda 0.01. `δV ≈ J δσ` is a local linearization, not a verified guarantee for the source high-contrast anomalies. **376-node BP, 686-element JAC and 32× 32 GREIT grid** are distinct domains; voltage row index never selects a reconstructed pixel. Difference estimates are not automatically calibrated absolute S/m conductivity.

## Expected output

Generic output/reconstruction.npy is one real numeric array. Task main instead saves BP 376-node and JAC 686-element difference arrays plus GREIT 32× 32 grid NPZ; output domain and absolute versus difference scale must be chosen explicitly.

## Evaluation

Generic scorer compares same-shape arrays over **all numeric array entries**: range-normalized RMSE (infinite for zero truth range) and uncentered cosine NCC with 1e-30 denominator epsilon. This differs from source flux-normalized relative L2 error and centered NCC; GREIT source metrics are skipped. Native ground_truth.npz has six float64 arrays shaped (1,686). Generic preparation squeezes only ndim > 2, preserving this leading singleton. Output (1,686) lexically selects bp_perm_anomaly absolute conductivity; output (686,) matches none of the six arrays. For the incomplete retained tree only, discovery could fall through to saved reconstruction_bp.npy (376,) then shape mismatch; Output (376,) can match saved BP reconstruction, not conductivity truth. The full official tree lists ground_truth_bp.npy, ground_truth_greit.npy and ground_truth_jac_dynamic.npy before saved reconstructions. Newly acquired official NPY bytes match revision-pinned LFS SHA/size: float64/C-order BP delta (376,), GREIT element delta (686,) and JAC element delta (686,). NPY loading returns its array unconditionally: after the NPZ nonmatch, complete-tree discovery takes ground_truth_bp.npy first even for (686,), then shape-mismatch rather than search later shape-compatible files. Output (376,) instead resolves BP delta truth when these full-tree files are staged. No-filesystem scorer instead requires ground_truth.npy under reference_outputs or data; the pinned tree lists neither. Actual reference behavior depends on staged files and filesystem route, not a guaranteed truth or privacy contract. Source task NCC centers arrays; nested saved source metrics are not generic pass/fail thresholds. No scorer or solver was executed.

## Visual explanation

### Workflow

- Electrical voltages measured at boundary electrodes
- Reconstruct conductivity from boundary voltages
- A 2D electrical-conductivity map

### Input

**Native synthetic source input.** BP circular FEM mesh: 376 nodes, 686 triangles, 16 point electrodes, 208 ordered background/anomaly voltage pairs. Opposite-drive JAC has 192 measurements. Actual raw arrays omit README leading batch dimensions.

### Supplied helpers

**Given material, not an answer reveal.** Electrode layout, excitation patterns and a conductivity forward model. The assistance level can add an approach and software design.

### Reference or output

**Expected artifact, not an actual prediction.** Generic output/reconstruction.npy is one real numeric array. Task main instead saves BP 376-node and JAC 686-element difference arrays plus GREIT 32× 32 grid NPZ; output domain and absolute versus difference scale must be chosen explicitly.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| L1 · README | README, data description and method hints. | Choose and implement a workable algorithm. |
| L2 · + approach | A proposed algorithmic approach is added. | Design the software and implement the method. |
| L3 · + design | Approach and software design are added. | Implement the specified design and numerical details. |

## Difficulty

Small voltage errors can create large interior changes; boundary geometry and regularization matter.

## Sources

- [Pinned task README](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/eit_conductivity_reconstruction/README.md)
- [Evaluation modes and assistance](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/README.md)

## Coverage

One scientific task definition across L1/L2/L3 assistance. This collection includes non-medical astronomy, optics and Earth-science tasks as well as medical imaging.

## Gaps

Native synthetic voltages are available; anomaly conductivities are solver-visible, README batch axes differ, and generic reference/output scaling is unresolved. No participant reconstruction or metric is shown. Choose blind inversion or method reproduction; sequester anomaly truth for blind condition; pin reference key, absolute versus delta conductivity, domain and scale before scoring.

## Retained preparation boundary

Original acquisition objects remain historical and unchanged; actual UTC attempts describe retained-byte validation only, with no new GET. Native array geometry/voltage rows are copied exactly for display, not generated by a forward solver. Source anomaly summaries appear only after explicit reader request in the helper chapter, reset before paint on backward replay or exit; shared global reset remount applies. This educational coverage does not sequester the original solver-visible truth. No conductivity map, metric, evaluator verdict or patient finding is shown.
