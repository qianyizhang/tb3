# Refractive deflectometry source views

Benchmark revision: `dc2f668939b21e8312e22529615def610f8611df`.
Dataset revision: `a9de559b54849a25988a8a0d8a5e869063a5a7a3`.
[Source audit](../../external-tasks/sources/imaging101-deflectometry-audit.json)
retains source/asset hashes, original attribution, contracts and fixed controls.
The task cites Wang, Chen and Heidrich, Optics Express 2021; the upstream tree
at `df23bef16ed92d597f9d9397f313de54e9d4015a` has no license file. Read
DATA-LICENSE.txt and BENCHMARK-LICENSE.txt together.

Camera panels are exact crops from the pinned notebook's embedded PNG figures,
not extracted raw camera arrays. Inputs use cell10's upper two measurement panels;
modeled outputs use cells9/10's upper modeled panels. Crop boxes are in the JSON.
Both original figures are 555x788 pixels; the source already normalized, masked,
rendered and resampled the 768x768 camera views. Extracted panels are 113/114
pixels wide and 113/114 pixels high. Display them as rendered views, never as
raw intensity or measurement samples. The repeated lower figure is excluded:
the source saves a complete two-camera figure twice. There are two cameras.
Original notebook bytes and complete extracted figures remain local unchanged.

The 32x32 four-step fringe demonstration is a separate synthetic source fixture.
Four selected pixels retain their exact intensities, axis, camera, mean,
squared modulation and atan2 phase. Image displays use fixed 50..150 intensity
and -pi..pi phase scales with 8-bit grayscale quantization. No native-camera
phase, valid map, screen intersection or optical fit is recovered from these controls.

Lens sections show the analytical spherical sag used by the source with k=0
and no polynomial terms, at aperture radius12.7mm. Axes are declared millimeters
in the lens-local frame. Initial and saved sections are discrete states, never
invented optimizer iterates. Eight saved parameters and all21 recorded losses
retain their source values. Loss is pre-update full-grid masked component MSE;
43.0513um displacement is a separately retained valid-pixel source metric.

Manufacturer radii/thickness and their section are isolated in reference.json.
They mount only after an explicit reader reveal with dashed purple styling.
This is a presentation boundary: L1-L3 actually seed truth and the prescription.
The custom scorer ignores pose; generic scoring rejects a correct three-vector.
No pass thresholds are supplied. The raw archive remains unavailable; source
figures do not establish raw-data recovery, fresh optical fitting or agent skill.
