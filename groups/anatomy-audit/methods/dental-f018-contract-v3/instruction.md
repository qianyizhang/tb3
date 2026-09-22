# Segment a dental cone-beam CT

The target is `/app/data/ct.nii.gz`; the complete label-ID dictionary is
`/app/data/labels.json`. Produce `/app/answer/segmentation.nii.gz`, a single
integer-label NIfTI on exactly the target's native voxel grid. Preserve dimensions,
affine, qform and sform. Use background 0 and only the supplied IDs. Save
`/app/answer/method.md` describing your method, uncertainties and omissions.

## Coordinates, scale and encoding — contract version 3

For semantic labeling in this package, the three native NIfTI array indices
`(i,j,k)` increase toward **Right, Posterior, Inferior**, respectively. These are
patient-side label names, independent of screen orientation. This mapping is
authoritative for this task. The stored direction metadata is not authoritative
for assigning those names; preserve it to maintain the required output grid.
Do not infer anatomical side from the affine or screen-left.

For standard native reads, `nibabel_array[i,j,k]` corresponds to
`SimpleITK_array[k,j,i]`. Label the index axes and displayed anatomical directions
on views you create. Internal flips, transposes, crops or resampling are allowed,
but record their inverse and return the final mask to the original target grid.
Use nearest-neighbor interpolation for integer masks. Apply spatial transforms
consistently to any supplied example image and its annotation.

The input is a single 3D CBCT channel, represented in HU on a 0.3 mm isotropic
grid. Check the actual file and use values after its stored scaling is applied.
Display windows do not change the measurement scale. Record any normalization,
clipping or resampling. Intensity alone does not define a tissue class.

The dictionary has 77 foreground classes plus background, with sparse IDs.
Do not renumber IDs to a contiguous range. Tooth identities follow FDI notation:
quadrants 1/2/3/4 are upper-right/upper-left/lower-left/lower-right; positions 1–8
run from central incisor to third molar. Pulp ID = corresponding tooth ID +100.
Preserve missing positions rather than numbering teeth by their visible order.
Main canal IDs are 3/4; small canal IDs are 103/104/105. ID 150 is not an output
class. No list of structures present in the target is supplied.

## Operational annotation rules

These rules make the requested output explicit. They are task conventions; the
original reference annotations may contain uncertain boundaries or inconsistencies.
Follow the rules and document unresolved interpretations in your method note.
They do not imply that any particular condition below occurs in this target.

| Structure | Requested extent and boundary |
| --- | --- |
| Natural teeth | Mineralized natural tooth tissue, including supported retained roots and impacted or partially imaged teeth. Preserve the anatomical FDI slot. Separately labeled pulp and prosthetic material replace the tooth label at their voxels. A complete tooth object for geometry evaluation is its tooth-tissue plus pulp union. |
| Pulp | The anatomical internal chamber and root-canal compartment, rather than a diagnosis of viable pulp tissue. Include occupied portions when their endodontic compartment is supported by visible morphology and continuity, even if their contents are bright. This includes supported filling/post contents inside that compartment; it does not include the surrounding natural hard tissue, an external prosthetic crown, or an implant. Do not invent an obliterated or unresolvable compartment solely from an expected tooth shape. End at the supported apical opening. |
| Jawbones | The cortical and enclosed cancellous/marrow compartments of the named jaw, excluding separately labeled teeth, pulp, canals and restorations. Exclude distinct empty sockets, air spaces and neighboring facial or cervical bones. At an indistinct interface use the best-supported anatomical boundary; do not expand the jaw label through unrelated touching bone. |
| Inferior alveolar canals | The supported intrabony canal volume, excluding its corticated wall and extraosseous nerves. Include the intrabony course to its mandibular and mental openings. Beyond the anterior junction, assign the identifiable incisive continuation to the corresponding incisive label. |
| Incisive and lingual canals | The supported intrabony tract, including its imaged opening, excluding bone walls and extraosseous tissue. Include distinguishable branches or separate components belonging to the named tract. No fixed diameter or component count is required. At a junction, assign voxels by the course they belong to and use one non-overlapping partition at the branch point. |
| Maxillary sinuses | The anatomical cavity within the bony boundary, including supported non-air contents such as fluid or thickened lining. Exclude the bony wall and septa. Stop at the ostium rather than spreading into the nasal cavity. |
| Pharynx | The imaged pharyngeal air lumen. Exclude its soft-tissue wall and separate oral/nasal cavities, using their anatomical openings as boundaries. Do not extend beyond the field of view or into other connected spaces merely because they contain air. |
| Crown and bridge | Prosthetic coronal structures. Use Crown for a standalone coronal unit; use Bridge for a connected replacement span, including its pontic and connected retainers. Preserve distinguishable natural tissue below these structures under its tooth ID. Bright enamel alone does not establish a prosthesis. |
| Implant | An implanted supporting body and directly associated abutment; a distinguishable prosthetic coronal unit or span keeps its Crown/Bridge label. An implant does not acquire a natural-tooth or pulp ID. |
| Unlisted anatomy/material | Do not invent new IDs. Keep distinguishable non-endodontic filling material or other unsupported categories in background and document the limitation. If boundaries cannot be separated reliably, make a supported assignment under these definitions and explain the ambiguity. |

Labels are mutually exclusive. Within a supported endodontic compartment use its
pulp ID for its contents. Elsewhere, identifiable prosthetic material takes its
restoration ID; natural tooth tissue takes its FDI ID; named canals and cavities
take their respective IDs; surrounding jawbone takes the jaw ID. A contact or
partial-volume voxel receives the best-supported single class under these rules.

For a short indistinct interval, a conservative continuation is allowed when
supported by the visible course on adjacent slices and anatomy in other planes.
Do not force continuity across a long unsupported region or add components merely
because they are typical. Image artifacts and streaks are not anatomical structures.

## Coverage, uncertainty and evaluation

Segment represented anatomy within the actual imaged field of view, including
supported truncated structures. The dataset-wide dictionary does not mean every
label occurs. Do not extrapolate beyond the image. An unused label can indicate
absence, truncation or inability to resolve it; state the reason where possible.

Evaluation uses a withheld original dense reference. No ignored regions or
abstention exemption are provided: omitted reference voxels count as misses and
extra predicted voxels count as errors. Uncertainty notes remain useful for
interpretation but do not alter the numeric score. Agreement involving ambiguous
annotation conventions is descriptive, not an automatic clinical correctness verdict.

The custom evaluation reports active-label macro Dice (both-empty labels omitted;
one-empty labels score zero), per-tooth and pooled pulp Dice, main and small canals
separately, jaws, air spaces, and both restoration subtype and pooled geometry.
Whole-tooth shape is also matched independently of FDI identity, with unmatched
objects scored zero; tooth identity is reported separately. Canal surface distances
are in millimetres, with missing-side distances marked unavailable. There is no
clinical pass/fail threshold. Unknown IDs, fractional/nonfinite labels or a wrong
voxel grid invalidate the submitted mask. These are custom task metrics rather
than a claim of official challenge-score equivalence.

Choose your method using the installed local tools. You have up to two hours,
4 CPUs and no GPU. External websites/data and pretrained model weights are
unavailable. No prior solutions, target annotation, evaluation feedback or other
attempt's results are provided. Save the target output before finishing.
