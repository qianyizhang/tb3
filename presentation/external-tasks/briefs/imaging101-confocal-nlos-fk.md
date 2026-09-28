# Reconstruct an object hidden around a corner

Implement confocal f-k migration from timed relay-wall measurements to a 3D
reflectivity volume. The pinned release supplies one measurement cube and a saved
reconstruction; this explanation audits those artifacts without a fresh full-size solve.

## Value

Time of flight constrains indirect light paths. Calibration, array order and the
Stolt frequency map connect those measurements to a spatial reconstruction.

## Given

### Original data

`raw_data.npz:meas` is float32 `(128,128,2048)` in `(y,x,time)` order,
with observed counts from 0 to 42. The wall spans 2 m × 2 m; each time bin is
32 ps. Source metadata attributes the cube to an outdoor scene with a 10 minute
exposure. The original MAT-to-NPZ conversion receipt was not acquired.

### Supplied helpers

Wall size, bin width, float64 `(128,128)` `tofgrid` delays in picoseconds,
and a metadata file specifying a 512-bin crop. The README calls `tofgrid`
float32, but the acquired array is float64. L2 adds approach prose and L3 adds
software design. All three local levels also copy the baseline reconstruction.

### Callable tools

The released task uses Python, NumPy and SciPy. End-to-end, function-level and
planning modes are separate. This review intercepts installation commands and
executes only selected seeding, scoring, three histograms and a small operator fixture.

### Reference-only material

There is no independent scene ground truth. `baseline_reference.npz` contains
`reconstruction` `(1,512,128,128)`. Its batch-zero array is exactly equal to both
saved `reconstruction.npz:fk` and `fk_reference.npy`.

The selected released `LocalRunner.start` copies the entire data directory,
including this baseline, for L1–L3. Every external command was intercepted during
the reproduction. Docker source mounts the whole task read-only at `/workspace_src`;
that path was inspected, not executed. Reader reference reveal is a display choice,
not a hidden-reference evaluation claim.

## Task specification

For each histogram, circularly roll by `-floor(tofgrid / 32 ps)`, retain the first
512 bins and transpose to `(time,y,x)`. The three illustrated native points
`(32,32)`, `(64,64)` and `(96,96)` shift by −748, −816 and −903 bins.

The source operator applies square-root amplitude/depth weighting, pads 2×,
takes a 3D FFT, samples the Stolt map with linear interpolation, applies a positive
frequency mask and Jacobian, then inverse-transforms and squares the magnitude.
The full input inverse was not executed. The published `(16,8,8)` solver fixture
agrees within `4.62e-14` absolute difference; this is a bounded operator check.

Source display axes use inclusive endpoints: x,y −1 to1 m and z0 to2.4576 m after
cropping. Metadata's 9.8304 m depth range describes the original 2048 bins.
Forward-model half-bin centers are a separate convention.

## Expected output

Active local end-to-end scoring expects `output/reconstruction.npy`, one real
numeric volume `(512,128,128)`; a singleton batch axis is squeezed. A 2D maximum
projection fails shape matching. The task-native saved archive instead uses key `fk`.

## Evaluation

The active generic scorer selects `evaluation/reference_outputs/reconstruction.npz`
ahead of the baseline file, uses cosine NCC and range-normalized RMSE, and retains
amplitude. Selected saved-output replays establish:

| Diagnostic | Generic NCC | Generic NRMSE | Interpretation |
| --- | ---: | ---: | --- |
| Saved array | 1 | 0 | Identical stored arrays |
| Copied baseline | 1 | 0 | Visible-reference no-op control |
| Half amplitude | 1 | 0.020574 | Correlation alone does not check scale |
| Front projection | — | — | Shape error: 128×128 versus 512×128×128 |

Native `main.py` centers NCC and max-normalizes each volume first. Its half-amplitude
control gives NCC1 / NRMSE0. These are different metric conventions.

The retained metric file reports NCC≈1, NRMSE0 and 19.6 seconds. That runtime is
historical, not measured here. It has no pass boundary keys. `main.py` could write
0.9 / 0.1 boundaries on execution, but it was not run or used to replace the original
record. Current pass status remains unavailable. No fresh solver or agent success.

## Visual explanation

### Workflow

- Native wall-count map and three exact timed histograms.
- Calibration roll/crop, Stolt samples and saved-volume projections.
- Explicit baseline reveal, copied-input boundary, metric controls and limits.

### Input

**Actual source arrays.** A sum over recorded time at every wall pixel and exact
histograms. The count map is not a photograph of the hidden scene.

### Supplied helpers

**Given calibration and guidance.** Three exact shifts, physical scales and
analytic operator samples are labeled separately from the saved reconstruction.

### Reference or output

**Saved source output and explicit baseline reveal.** Front/top/side maxima retain
all native projection pixels and state the collapsed axis. Square-root contrast
and 8-bit RGB are display transforms. Baseline values equal the saved volume.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| L1 · README | README, requirements, complete data/ including baseline. | Choose and implement an algorithm; reference is exposed. |
| L2 · + approach | Same packet plus approach.md. | Design and implement; reference is exposed. |
| L3 · + design | Same packet plus design.md. | Implement specified details; reference is exposed. |

## Difficulty

Very weak indirect light and timing errors can place a surface at the wrong depth.

## Sources

- [Pinned task README](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/confocal-nlos-fk/README.md)
- [Evaluation modes and assistance](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/README.md)
- [Source and replay audit](../sources/imaging101-nlos-audit.json)
- [Canonical story](../stories/imaging101-nlos.story.md)
- [Derived asset provenance and terms](../../task-explorer/imaging101-nlos/NOTICE.md)
- [Original code and dataset terms](https://github.com/computational-imaging/nlos-fk/blob/d34d49fed5a86f4ebddf85d461cff6923de5367d/LICENSE)

## Coverage

One scientific task definition across L1/L2/L3 assistance. This collection includes non-medical astronomy, optics and Earth-science tasks as well as medical imaging.

## Gaps

Independent ground truth, capture-conversion lineage, fresh full-size reconstruction
and benchmark pass remain unestablished. The saved peak lies in the last depth plane.
Original MATLAB swaps lateral axes and removes the final eleven depth planes before
output; the released Python adaptation does not. Original-author byte equivalence
and independent scene-depth accuracy are therefore not claimed.

Original Stanford academic/non-commercial data terms are retained separately from
the benchmark MIT label. No model run, runtime installation or historical rewrite.
