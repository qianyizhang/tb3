# Real-scan curation and contamination limits

## Selected source

The [official EchoSlicer repository](https://github.com/echonet/3d-echo) and
[paper](https://arxiv.org/abs/2511.15946) describe real 3D scans acquired from
four consenting research-team volunteers. The release is dated 2025-11-19;
the inspected code commit is 78f7085104492d5229b1bb96b7748ad9d950e53d.
No paired reference reconstruction is supplied for this case study.

The first non-resource-fork DICOM in archive order is `dataset/A_0.dcm`:
37,488,946 bytes, SHA-256
`cfe78d709e89e9127e5ece5089c0824e677eab3eb90950876df23ff3cdbb3fc1`.
Only about 36.4 MB of the 1.1 GB archive were fetched using byte ranges. A
reader written from the inspected public format description decoded 18
uint8 volumes of shape 404×76×62 in spherical coordinates. Source FrameTime is
161.15 ms; all 18 phases remain in original order. Original DICOM and metadata
stay outside the solver package. Public downloading does not establish a
redistribution license; assets remain local.

Four supplied planes are native long-axis angles 0/90 degrees and transverse
depths 65/105 mm. Review planes are 45/135 degrees and 45/85 mm. These are
geometric slice definitions, not expert-certified standard clinical views.
They use 256² images, 0.75 mm spacing and one common rigid coordinate change.
Coordinate round trips and spherical-grid inversion are numerically checked.
The same low frame rate limits what a reconstruction can establish about timing.

## Newly found future reference source

[EchoXFlow](https://arxiv.org/abs/2605.05447), released in 2026, describes
clinical scans with separate B-mode/Doppler streams, ECG, and operator-created
or adjusted annotations. It includes dynamic LV endocardial surfaces for some
3D scans; this is closer to a real-scan geometric reference than simulated
material motion. These operator/software-derived surfaces are not independently
measured myocardial material trajectories. Sequential acquisitions still require
alignment, and some volumes are stitched across beats.

The [official data page](https://huggingface.co/datasets/Ahus-AIM/EchoXFlow)
lists CC BY-NC-SA 4.0 and public per-exam archives. Its data-card and format were
inspected; no exam or annotation was downloaded for BR-032. It could support a
separate later reference-backed study, but no such experiment was run here.

## What this study can say about leakage

Fresh solver sessions, a minimal input image, withheld planes and command
review can establish what information was supplied or visibly retrieved in a
run. They cannot establish the model's pretraining corpus. New source names,
phase windows or coordinate transforms do not erase memorized source anatomy.
BR-032 uses all native phases; no synthetic motion is added to its images.

Choosing a public real scan tests transfer from simulation to recorded images.
It does not by itself create a contamination-free holdout. Removing GT likewise
removes a scoring reference; it does not prove the images were unseen. A strong
contamination claim would require controlled never-public acquisition and release
provenance relative to the model, which this public case lacks. The user was
offered that option and explicitly chose the public real-scan case.
