# Imaging101 fan-beam CT source views

Benchmark: AI4ImagingLab/imaging-101-release at
`dc2f668939b21e8312e22529615def610f8611df`. Numeric release:
starpacker52/imaging-101 at `a9de559b54849a25988a8a0d8a5e869063a5a7a3`.
The [audit](../../external-tasks/sources/imaging101-fan-beam-audit.json)
pins all seven assets, task/shared sources, upstream notices and numerical controls.
BENCHMARK-LICENSE.txt, UPSTREAM-GPL-2.0.txt and DATA-LICENSE.txt retain distinct
terms. The cited curved-detector ray tracer differs from this pixel-driven source.

One synthetic 128x128 phantom. Full/short sinograms have 180/116 angle rows and
192 detector columns. Their shared linear display range is -5..55. Saved and
truth images share 0..1.6 relative attenuation. Native pixels are uint8-quantized
without resampling or clipping. Cropped normalized views retain the actual 104x104
samples and map each crop independently to 0..1; they are explicitly labeled.
All geometry is in pixels, not mm or HU, with no patient orientation implied.

Geometry follows the executed coordinate convention: column x and row y increase
right and down in the diagram, as in the native image. At angle zero the source
is (0,256), below the field; detector center is (0,-256). Source and detector
rotate together. Orange unit-pixel controls illustrate the exact 512/U mapping
and two-bin weights. They are analytical diagnostics, not optimizer iterates.
The declared half-fan angle uses detector position /256 although source-detector
separation is 512. Original angles and Parker weights remain unchanged.

Three saved images are selected without crossfading or invented reconstruction
trajectories. Both saved FBP arrays reproduce exactly at float32 precision.
The recorded 150-step data-fidelity curve is displayed as saved, including 66
increases; it excludes the TV penalty. No iterative solver or agent was run.

Truth assets live in reference.json and mount only after the reader reveal in
the reference chapter, with a dashed purple frame. This presentation boundary
is not solver privacy: actual L1-L3 local seeding includes ground_truth.npz.
The orange dashed square marks the native metric crop, never a segmentation.
Native crop-normalized scores differ from generic full-array scores. Historical
notebook boundaries are not installed: no shipped metrics.json supplies a pass.
Fixed adjoint and radius-projection controls qualify source descriptions without
changing the saved images, historical scores or claiming clinical accuracy.
