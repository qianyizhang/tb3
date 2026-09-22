# Dental segmentation instruction revision — draft, not dispatchable

Follow-up, 2026-09-22: the user authorized using best judgment to select general
operational rules and run a fresh F018 pair. The implemented
[trial instruction](../dental-f018-contract-v3/instruction.md) and
[protocol](../dental-f018-contract-v3/README.md) are separate. They retain the
reference-adjudication limits listed here; this source-audit draft is not a solver
input and is not a retroactive edit to v2.

This is a proposed successor to the completed v2 experiment, not a replacement
for its frozen prompt. It introduces no tools, trials or data exposure. Its
[source audit](../../findings/dental-dataset-contract-audit.md) separates confirmed
release behavior from unadjudicated annotation choices.

The following reusable text is target-blind. Before use, the author must populate
the package manifest and resolve the decision table below. Do not put target GT,
prior outputs, scores, scan-specific observations or diagnostic thresholds into
the solver packet.

## Proposed common solver text

Segment the supplied dental CBCT using the supplied label dictionary. Produce a
single integer-label NIfTI on the exact native target grid, and a method note
describing your approach and uncertainties. Background is 0. The manifest lists
the allowed input/output paths, file fingerprints, dimensions, spacing, permitted
resources, annotation policy version and evaluation policy version.

**Coordinates.** For this reviewed native package, increasing NIfTI voxel-array
indices `(i,j,k)` mean Right, Posterior, Inferior under the dataset's semantic
label convention. These are patient-side label names, independent of screen
orientation. The stored NIfTI direction metadata is not authoritative for
anatomical naming; preserve it to retain the required output grid. Do not
canonicalize the file on the assumption that its header defines anatomical side.

For standard native reads:

```text
nibabel_array[i, j, k] == SimpleITK_array[k, j, i]

NIfTI axis 0 / i increases toward dataset Right
NIfTI axis 1 / j increases toward dataset Posterior
NIfTI axis 2 / k increases toward dataset Inferior
```

If you reorient, crop or resample internally, retain the exact forward and inverse
transforms. Use the same spatial transform for a supplied reference image and its
annotation. Return the result to the target's native index grid before saving.
Use nearest-neighbor interpolation for integer labels. Preserve target dimensions,
affine, qform and sform. Label native indices and displayed direction arrows on
diagnostic views. The publisher orientation script is optional preprocessing,
not a required correction to perform on these already reviewed inputs.

**Input and label encoding.** The input is one 3D CBCT channel on the released
0.3 mm isotropic grid; verify the supplied manifest against the actual file.
Express physical lengths in millimetres, not unqualified voxel counts. Use the values
after the reader applies stored NIfTI scaling. These are the released
HU-represented values; a display window is not a new measurement scale. Record
any normalization or clipping. No single intensity value determines a tissue
class across all scans or treatments.

The dictionary defines 77 foreground classes plus background, with sparse IDs.
Do not renumber to a contiguous range. Tooth IDs are FDI identities, and each
tooth's pulp label is its tooth ID +100. Main canal IDs are 3/4; small canals
103/104/105. Evaluation-only pooled pulp ID 150 is not a valid output label.
Assign FDI identity from anatomy, preserving missing positions; do not renumber
the visible teeth just to make a consecutive sequence.

**Coverage.** Segment represented anatomy within the actual field of view.
Structures can be absent or truncated; the dictionary does not imply that every
ID occurs. Do not extrapolate beyond the image. A reference scan is an example
of annotation conventions, not a mandatory target inventory, universal intensity
calibration or guaranteed geometric fit. Its coverage note lists which boundary
rules it illustrates.

**Annotation conventions.** Follow the accompanying versioned boundary table.
It explicitly defines pulp in treated/occupied spaces; natural tooth versus
prosthesis ownership; jaw, sinus and pharynx boundaries; canal walls, endpoints,
junctions and uncertain gaps; multiple/accessory components; and unlisted
materials or anatomy. All labels are mutually exclusive. Intensity or class
names alone must not substitute for that table.

**Uncertainty.** Follow the stated visibility/inference policy. Document unresolved
regions and alternative interpretations in the method note. A note does not
create a scoring exemption. The package must state whether any ignored region or
abstention mechanism exists; if none is declared, omitted GT voxels count as
misses. Do not invent anatomy merely to populate a label.

**Evaluation.** The package identifies the custom scorer and exact class sets.
It distinguishes tooth geometry from FDI identity, per-tooth pulp from pooled
pulp, main canals from small canals, and restoration geometry from subtype
agreement. It states both-empty and one-empty policies, distance units,
aggregation, invalid-output handling and the deadline. It does not claim
equivalence with a different public challenge scorer.

Choose your method within the package's explicit CPU/GPU, time, tool, network,
weight and reference allowances. Resource availability is not implied by what
was permitted in the original challenge.

## Required author decisions before using the draft

These are missing contract decisions, not questions the blind solver should have
to resolve by guessing. Each row needs the rule, evidence, reviewer/date,
exceptions, example coverage and evaluator treatment. Public naming alone does
not close a row.

| Policy ID | Decision to record | Current status |
| --- | --- | --- |
| A01: occupied pulp | Visible pulp, anatomical space regardless of contents, or another definition? Where do root fillings, posts and calcified/obliterated regions go? How are apical/partial-volume boundaries handled? | Unresolved |
| A02: tooth and mixed material | Hard tissue versus complete tooth; natural tissue below a prosthesis; roots without a crown; restoration/pulp/tooth/jaw precedence. | Unresolved beyond exclusive integer-map encoding |
| A03: main canals | Lumen/wall definition, endpoints at openings, mental branch/foramen treatment, incisive transition, unclear-gap interpolation. | Unresolved |
| A04: small canals | Full tract versus opening for lingual label; accessory or disconnected components; incisive start/end and junction ownership. | Unresolved |
| A05: jawbone | Cancellous/marrow inclusion, sockets and lesions, subtracting internal structures, neighboring-bone interfaces. | V2 operational rule not source-adjudicated |
| A06: sinus and pharynx | Sinus air-only versus full cavity with non-air contents, septa and ostia; pharyngeal lumen extent and neighboring connected spaces. | V2 operational rule not source-adjudicated |
| A07: restorations | Crown/bridge units and pontics; implant body/abutment/crown; posts/fillings; ordinary restorations without a dedicated class. | Unresolved |
| A08: atypical anatomy | Missing/impacted/remnant teeth; supernumerary or deciduous teeth; fractures/lesions and other unmapped tissue. | Unresolved |
| A09: uncertainty and coverage | Visible-only versus anatomical interpolation; artifact handling; annotation completeness; ignored or excluded regions, if any. | V2 penalizes all omissions; consistency with ambiguous GT remains under review |
| A10: example and source coverage | Same-version paired files; verified coordinate mapping; documented normal and edge-case coverage; no target/derivative patient overlap. | Must be populated for a future package |

If the original convention cannot be established, document a newly chosen
operational policy and have the corresponding reference assessed against it.
Do not present that choice as recovered publisher intent. Any corrected reference
or new ignored-region evaluation is a separately versioned derivative with its
own provenance, never a replacement for the original recorded result.

## Author preflight pseudocode

```text
read release manifest and paired image/label fingerprints
verify dictionary, array grid, scaling and source-update status
verify dataset-side mapping separately from stored header coordinates
verify image/mask transforms with native round-trip landmarks

for each boundary decision:
    require an explicit rule and evidence/status
    check consistency with reviewed annotation examples
    if unresolved:
        mark affected evaluation claims as under review

freeze instructions, examples, evaluator and resource conditions together
check empty-label, identity-swap and output-grid controls
keep author GT/diagnostics outside the solver packet
launch nothing without a separately authorized experiment
```

This draft is complete as an audit deliverable. It is intentionally not certified
as a fully adjudicated annotation manual or approved new trial.
