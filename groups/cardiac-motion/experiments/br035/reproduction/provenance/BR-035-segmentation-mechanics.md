Source: `docs/research-rounds/BR-035-segmentation-mechanics.md`; original SHA-256: `d36a2652ac2170583d2cd9d088833d04e4ce449475c04e916d0620568d65ea3b`.
Repository source locators below are provenance; they are not required runtime inputs.

# BR-035 — Segmentation supplied, geometry and mechanics separated

The user accepted the proposed paired test with “sounds worthy of test” on
2026-09-16 in task 01a0a967-f33c-70a0-b661-d8919246b13b. This authorizes two
fresh Sol/xhigh attempts, one per input condition, and unchanged-code clinical
replays. This round owns `authoring/segmentation_mechanics`, `runs/br035-*`,
this protocol, a results document and `docs/evidence/br035-*`. Prior frozen
experiments and the authored interview publication remain unchanged.

## Question and conditions

Can an agent build a consistent deforming volumetric mesh when segmentation is
supplied? Compare A: full-cycle binary myocardial masks, with B: exactly those
masks plus registered ultrasound volumes. Use the already audited STRAUS healthy
simulation (30 phases, biventricular myocardium) for material motion references.
Masks are independently rasterized from each phase on a 1.5 mm grid: no moving
vertex IDs, source mesh, regional labels, displacement or strain is supplied.
The agent constructs its own tetrahedral mesh, shared across phases, and computes
F, Green–Lagrange E and J. Initial anatomy is supplied by masks, not a reference
mesh. Ordinary meshing/registration libraries and computation are allowed.

Two fresh sessions, identical task wording except the image-availability flag,
30 minutes each, 4 CPUs/8 GB, no score feedback or retries. All task bytes and
both inputs freeze before either session. Outcome differences are descriptive:
one fresh attempt per condition does not isolate the causal value of texture.

## Evaluation, frozen before model execution

The primary construction reward requires valid finite mesh/fields, mean 3D mask
Dice >=0.90, mean relative myocardial volume error <=5%, zero nonpositive element
Jacobians, and F/E/J agreement with independent recomputation (absolute 1e-4).
Report per-frame Dice, volume error, signed J distribution and mesh size.

Material reconstruction is a separate diagnostic: evaluate at fixed reference
cell centroids via barycentric interpolation through the agent's initial mesh.
Report coverage, full-body and LV motion RMSE, and longitudinal/circumferential/
radial engineering-strain MAE on reference anatomical directions. Report regional
peak/timing errors where coverage is sufficient. Research targets: coverage>=95%,
motion RMSE<=2 mm, directional strain/peak MAE<=5 percentage points and peak timing
<=2 frames (reference values within 0.5 pp of the extremum count as ties). No
per-frame rigid realignment. Missing probes remain reported and prevent a
complete diagnostic pass. Different material maps can fit identical masks;
these targets assess closeness to this simulator, not uniquely identifiable
patient truth. Mask-only mechanics accuracy is not required for the construction
reward. The agent must discuss non-identifiability and model assumptions.

Independent analytic controls cover rigid/finite affine strain, evaluator
invariance to mesh vertex permutation, and a cylinder with boundary-preserving
z-dependent twist: identical occupancy can coexist with different strain.
Exact source motion is a privileged oracle, not a legal segmentation-only
solution. Empty output and static source geometry are negative controls. Oracle
and no-output Docker checks must pass for each task before its model launch.

## Clinical replay and limits

Before model launch, freeze 1.5 mm cavity masks and registered images for BR-034's
clearer primary clinical case. Each unchanged executable accepts the same input
schema with `mask_semantics=lv_cavity`; run it without network access, 4 CPUs/8 GB,
and a five-minute limit. Evaluate mask fit, volumes and EF against the clinical
surface-derived reference. EF error<=3 pp is a geometry-preservation check, since
all-phase cavity segmentation already encodes the volume curve. These cases do
not provide epicardial boundaries or material-motion truth. Any cavity deformation
strain is mathematical, not validated myocardial strain, and must be described
as such. No disease-cause or diagnostic-benefit claim follows.

Public source exposure remains unknown. Review traces for external reference
retrieval and retain raw receipts, infrastructure failures and the submitted
code. No publication, further trial, or extra patient acquisition is implied.

Sources: [STRAUS](https://humanheart-project.creatis.insa-lyon.fr/multimodalityStraus.html),
[EACVI/ASE definitions](https://academic.oup.com/ehjcimaging/article/16/1/1/2403449),
[EchoXFlow](https://huggingface.co/datasets/Ahus-AIM/EchoXFlow).
