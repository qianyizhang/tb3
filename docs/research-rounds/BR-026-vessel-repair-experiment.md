# BR-026 — vessel repair feasibility experiment

Authorized on 2026-09-16 by the user's “yes, go expeirent,” continuing
[vessel source curation](BR-025-vessel-connectivity.md). The original BR-025
identifier was concurrently reused by cardiac-reconstruction work. Preserve
both historical notes; this experiment owns BR-026, `probes/vessel-repair/`,
`docs/evidence/br026-*`, and ignored `runs/br026-vessel-repair/` only.

## Plan recorded before experiment outcomes

- First test a disclosed synthetic feasibility fixture, using the already
  checksum-verified TopCoW MRA 007 reference and a small local deletion from
  its right Pcom. The image is not altered. A mask generated this way is not
  a published segmentation-model error.
- Use MRA 012, whose right Pcom is annotated absent and left Pcom present,
  as an unchanged-mask control with the same task instructions. Keep the
  broad CoW review region and native geometry available; no hidden CTA
  evidence may be required to solve the offered MRA.
- Inspect native image sections through the selected repair region and
  quantify source-signal support. This is an engineering source review,
  not independent expert clinical adjudication or a congenital-absence claim.
- Compare public-input mask closing and image-guided repair baselines before
  running agents. Establish reference/oracle acceptance, unchanged-input
  failure on the defect, unchanged-input success on the control, and failure
  of connect-all, erase-region, thin-bridge and collateral-damage controls.
- Freeze local topology, centerline/geometry, and preservation criteria before
  any model output. Tolerances are engineering feasibility choices. Validate
  them with acceptable non-identical repairs, not only an exact reference copy.
- Prepare two separate small tasks, each one region and one output mask.
  The condition identity is not disclosed in the instructions. Native source
  masks/graphs, authoring code and verifier stay out of the agent image.
- Run matched Docker oracle/nop controls, followed by one fresh Terra/high
  diagnostic per valid condition with the usual 1800-second allowance, public
  network and ordinary numerical packages. Nop must return zero for the
  defect (missing artifact also fails); separately test a delivered unchanged
  mask to establish the correct-control behavior. No automatic retries.
- Even if a baseline makes these cases easy, the two agent runs may complete
  the requested feasibility diagnostic; report them as calibration and retire
  difficulty claims after clean passes. Do not increase defects or tighten
  thresholds to manufacture failure. No conditional Sol escalation in this
  first experiment, and no full segmentation training/container downloads.
- Audit normal completion, delivered masks, same-snapshot checksums,
  verifier replay, model/effort trace metadata, and public-source retrieval.
  Distinguish fixture validity, task result and image-reasoning support.

Sources and usage terms are retained in BR-025 and its curation receipt. This
local experiment does not publish data or establish commercial reuse rights.

## Authoring observations and calibration before model runs

The component-only baseline could not detect the gap: both proposed masks
remain globally connected. Its first outputs and code are retained locally.
A revised baseline skeletonizes only the supplied mask and proposes nearby
endpoint pairs. It does not read the private labels, nodes, generator or
reference. Mask-only local closing still leaves the connection broken;
the image-guided version restores full reference centerline coverage and
0.925 local Dice. The unchanged control has no qualifying endpoint pair.

The original 1 mm³ collateral-addition limit rejected that image-guided
repair solely for 1.216 mm³ of extra foreground outside the private 3 mm
repair neighborhood. The additions remain within 0.6 mm of reference
foreground. Before any model run, increase the collateral addition/deletion
allowance to 2 mm³, retaining the separate 1 mm³ cap on distant foreground.
This is explicit authoring calibration on the development fixture, not an
independent clinically validated threshold. Retain the earlier scores.
Centerline coverage is weighted by physical segment length; attachment
checks allow 0.6 mm neighborhoods instead of requiring exact endpoint voxels.

The source-scaled MRA values must be preserved exactly. An initial unfrozen
build rounded them to int16; it was archived and replaced with a crop retaining
the source stored samples, slope and intercept. Reloaded physical intensities
are checked for exact equality with the source crop. No rounded-input trial
was run. Native axial/coronal/sagittal slices at the deleted segment were
visually inspected; its median signal is 242.5 versus 71.0 in the nearby
background. This is image support for an annotation-backed synthetic repair,
not independent expert adjudication.

## Completed disposition

[Results](BR-026-results.md): both fresh Terra/high attempts completed normally.
V01 passes with 198/200 deleted voxels recovered and no collateral edits;
V02 fails preservation after 244 additions but preserves the absent right Pcom.
Its added structure follows image signal beside L-ACA and has no independent
clinical adjudication. Retain the frozen score, without claiming a confirmed
anatomical error. The ordinary image-guided baseline passes both conditions.
Four Docker controls and 20 author observations validate the frozen checks;
artifact replay and source-exposure review are complete. Gap difficulty is
retired, the reference disagreement is held, and no further trial is queued.
