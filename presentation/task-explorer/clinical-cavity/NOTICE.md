# EchoXFlow clinical cavity teaching assets

Elias Stenhede et al. EchoXFlow.
https://huggingface.co/datasets/Ahus-AIM/EchoXFlow
https://github.com/Ahus-AIM/EchoXFlow
Data and labels: CC BY-NC-SA 4.0; see DATA-LICENSE.txt.

Derived locally from three selected recordings and retained BR-034 outputs.
Changes: published (-X,Z,Y) convention, initial-surface PCA coordinates,
1 mm Cartesian resampling and crop, orthogonal sections, float32 display
positions and float64 original-volume integration. Local axes are not RAS/LPS.
Source images remain unchanged from the audited prepared inputs. Source arrays
are not distributed here. All frames retain a fixed public-input coordinate scale.

The supplied initial surface is public assistance. reference.json is private
source annotation revealed for the reader, not additional solver input. It is
operator/software derived, not independently adjudicated cardiology, material
motion or etiology. Source archive hashes match; publisher per-array serialization
versus raw C-order hashes remains unresolved. Pretraining exposure is unknown.
One model attempt and retained executable replays are not independent model trials.
This teaching build executes no solver, flow fitting or model and changes no scores.

Rebuild into a fresh local destination with:
.venv-br034/bin/python scripts/build_clinical_cavity_assets.py --out NEW_DIRECTORY
