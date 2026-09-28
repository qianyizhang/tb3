# Imaging101 confocal NLOS source views

Pinned benchmark: AI4ImagingLab/imaging-101-release
`dc2f668939b21e8312e22529615def610f8611df`; numeric assets: starpacker52/imaging-101
`a9de559b54849a25988a8a0d8a5e869063a5a7a3` on Hugging Face.
The [source audit](../../external-tasks/sources/imaging101-nlos-audit.json) retains
source hashes, original failed fetches, repaired acquisition, staging and metrics.

The benchmark attributes this case to the outdoor measurements of Lindell,
Wetzstein and O'Toole (2019), with 10 minute exposure and a 2 m square relay wall.
Capture provenance is source-attributed; no original MAT-to-NPZ conversion receipt
was acquired. Benchmark MIT terms are in BENCHMARK-LICENSE.txt. Original Stanford
academic/non-commercial code and data terms are in DATA-LICENSE.txt and remain
applicable to these derived views. They are not replaced by the benchmark label.

Inputs retain three exact 2048-bin histograms at source (y,x) indices (32,32),
(64,64), (96,96), the sum over time at every wall pixel, and a y=64 time section.
Calibration uses float64 tofgrid (README incorrectly says float32), floor(delay/32ps),
circular roll and a 512-bin crop. Data are real measurements as attributed by the
source, not generated scenes. The wall image is a sum, not a photograph of the object.

Saved-volume front/top/side views use max projections of the exact float32
(512,128,128) array. PNGs preserve native pixels with sqrt(value/global maximum)
display contrast, then 8-bit RGB quantization. No resampling, filtering or omitted
depth planes. Axis extents follow source volume_axes: x,y -1 to1 m; z0 to2.4576 m.
These inclusive endpoints differ from forward-model half-bin centers. Panels may
stretch pixels to the stated physical extents; array indices and roles stay explicit.

Reference front view is derived separately from baseline_reference.npz and shown
only in the reader reference chapter. Its values exactly equal the saved volume;
no independent ground truth is supplied. Actual released L1-L3 staging copies this
baseline into data/. A reader reveal does not establish hidden evaluation.

Stolt samples are analytic evaluations of the pinned operator mapping, with
kx=.5, ky=0, and kz=.25/.5/.75. The 16x8x8 published solver fixture was checked;
the full-size measurement inverse was not executed. MIP images are saved source
outputs, not the result of the illustrated frequency probes or a fresh agent.

Generic saved-output NCC1/NRMSE0 compares identical arrays; the baseline-copy
control gets the same scores. Half amplitude keeps NCC1 but yields NRMSE.020574.
Native main.py normalizes each volume and removes that amplitude difference.
Shipped metrics have no pass thresholds. No benchmark pass or depth accuracy is
claimed. The saved peak is in the last depth plane; the original MATLAB removes
the last11 planes and has different lateral permutations. Original-author output
equivalence is unverified. All original arrays and metric records remain unchanged.
