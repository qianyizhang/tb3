# BR-019 native trace → canonical player

**Inspected 2026-10-12.** `tb3-oblique-pose` currently uses the synthetic
`rigid-correspondence` / `correspondence-v1` story. The real-trace prototype at
commit `75171dc2` supplies a separate six-phase retained-run explanation; preserve
the synthetic transform witness as an operation example rather than relabeling
its interpolated transform as a solver trajectory.

## Evidence and local payload

Task root: `runs/br019-registration/tasks/cardiac-r01/`.
Run root: `runs/br019-cardiac-r01-terra-high-v1-20260916/cardiac-r01__7yuEb55/`.
Attempt: `attempt-0b9d524174a3e1a9e4bb4901`, Terra/high, 575.77 recorded seconds.
Paths below are relative to those roots; sizes are current local file bytes.

| Role | Exact source | Bytes / native contract |
| --- | --- | --- |
| Solver input | task `environment/data/volume.npz` | 7,446,106; `hu` 180³; `voxel_to_lps` 4×4; 1.5 mm |
| Target / conventions | task `environment/data/target.npy`, `image.json`, `instruction.md` | 36,992 / 245 / 2,146; 192², 0.9 mm/pixel; top-left pixel centre is transform translation |
| Observed tools | run `agent/trajectory.json` | 188,747; selected excerpts retain calls, outputs and timestamps |
| Saved output | run `artifacts/app/answer/pose.json` | 291; full-precision `slice_to_lps`, not the rounded printed matrix |
| Private geometry / evaluator | task `tests/truth.json`, `tests/score.py` | 512 / 2,117; generating pose; 7×7 physical grid |
| Frozen result | run `verifier/metrics.json` | 165; RMS 0.0004770594910662992 mm; maximum 0.0007442100175445693 mm |

The [source finding](../../findings/br019-full-view-trace.md),
[workbench manifest](../../findings/evidence/br019-full-view-trace.json) and
[derivation receipt](../../findings/evidence/br019-trace-visuals.json) retain
source hashes and dependencies. No new attempt is needed to migrate this evidence.

`prepare_trace.py` derives `.local/anatomy-pose/trace/data.json` (**916,686 B**):
90³ C-order uint8 CT preview (729,000 decoded B; 499,025 gzip B), affine, target,
three static context previews, four poses and image/silhouette/difference panels,
25 trace excerpts, four delivered-image pointers, frozen metrics and reference
pose. The standalone `index.html` is **1,533,384 B**. Delivered files are
`delivered-step-{10,11,18,26}-1.png`; they must accompany the payload.

Payload state keys are `id, trace_step, pose, image, silhouette, difference, role,
diagnostic`; trace keys are `step, timestamp, calls, output` (`calls` is a list).
Top-level reference/score keys are `reference_pose, frozen_metrics`;
`delivered_images` items use `step, path`. The compressed preview key is
`preview_base64_gzip`; its dimensions/window are `preview_size, preview_window_hu`.
All nine source pins and the recipe pin match current bytes; local `receipt.json`
is identical to the tracked derivation receipt. No stale pin was found. The receipt
does not pin generated `data.json`, PNGs or HTML; canonical assembly needs output
hashes as well as source hashes.

## Chapter / frame / control mapping

Use six discrete chapters at 24 fps, **144 frames per chapter, 192 for the third / 912 total** in the unbound
migration draft. Frames provide reading time; never interpolate poses
between recorded states. Bind the whole chapter interval to the stated state.

| Frames | Chapter | Actual trace steps | State and meaningful interaction |
| --- | --- | --- | --- |
| 0–143 | Receive inputs | 7, 9, 10, 11 | No target plane location; target plus whole supplied CT crop; three independent native context sliders |
| 144–287 | Wrong first match | 13, 17, 19–23, 25 | `early`: step-17 printed pose; native image / difference comparison; delivered step-18 render is pixel-identical |
| 288–479 | Fit inside volume | 29, 35, 36, 40, 41 | `bounded`: step-41 printed pose; section corners placed using volume affine; explain orientation-dependent centre bounds |
| 480–623 | Coarse silhouette | 42, 43 | `coarse`: seed-6 ZYZ rotation and centre parameters, mapped with step-29 bounds; silhouette default, image/difference alternatives |
| 624–767 | Refine and save | 43, 45 | `final`: saved answer; image / silhouette / difference; show 36,808/36,864 exact pixels, 56 differences, maximum difference 1 |
| 768–911 | Reveal evaluator | 45 plus frozen evaluation | Same saved pose; explicit reader reference reveal; amber dashed reference boundary and physical-grid scores |

Keep orbit/reset, CT planes, plane visibility and comparison mode independent of
recorded actions. CT sliders address preview indices 0–89, mapped to native
centres `index × 179/89`; the full crop's outer-centre span is 268.5 mm. Candidate
plane corners are `(0,0)`, `(171.9,0)`, `(171.9,171.9)`, `(0,171.9)` mm in slice
space. LPS→scene permutation is display-only. Candidate teal solid / reference
amber dashed need a matching legend. No-WebGL fallback retains target/candidate
panels, static context, chapter changes, trace excerpts and reader controls.

## Shared view contract and migration gaps

- **Common envelope:** typed native-trace asset descriptor with identity, input /
  helper / output / private-reference roles, source SHA-256 pins, selected asset
  closure, attempt/condition, derivation recipe, coordinate convention, dimensions,
  affine, window and fallback. Canonical compiler owns validation and packaging;
  generated payloads stay local. Do not import patient payloads into the universal
  frontend bundle or include the whole Anatomy library.
- **Discrete chapter state:** stable chapter ID, frames, trace step IDs, selected
  state ID or null, explicit reference-reveal flag, caption/interpretation. Shared
  reader owns timeline and accessible controls; CT adapter owns native plane
  drawing, preview decompression and image modes.
- **Geometry payload:** preserve existing four matrices and derived panels; label
  rounded intermediate logs as reconstructed. CT preview is display-only; native
  reslices use HU and trilinear interpolation, -150..350 HU. Context uses
  -1000..500 HU; -350 HU shell is spatial context, not organ segmentation.
- **Reference boundary:** prototype payload contains reference pose and post-hoc
  intermediate RMS/max diagnostics before reveal. Canonical UI must gate every
  reference-derived readout, not just the final outline/score. Asset packaging
  does not turn hidden browser data into solver access control.
- **Closure:** both source notice/data license and Three.js MIT notice must travel
  with selected assets. CT prototype receipt does not pin its supplied forward
  renderer or license/notice; add explicit dependency pins when assembling the
  canonical package. Do not run this preparation module on import: its top level
  writes local derivatives.
- **Coverage limit:** this is one R01 same-acquisition crop; BR-019 alternatives
  and BR-020 reconstruction conditions remain separate. The entire original CT,
  continuous optimizer states, clinical reference and causal ablation are absent.

Existing checks: `check_trace.mts` and local `browser-check.json`,
`preparation-check.json`. Canonical verification must add asset closure and
reference reset on chapter/entry transitions to the retained native-corner,
all-axis, keyboard, 390 px and no-WebGL checks. Historical acceptance and scores
remain unchanged; this mapping does not record migrated acceptance.
