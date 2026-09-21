+++
schema_version = 2
kind = "idea"
id = "agent-prompted-segmentation"
group_id = "anatomy-audit"
title = "Agent-guided segmentation with local promptable models"
idea_state = "exploring"
source = "codex://threads/01a0c423-5d0a-7ee3-97b4-66939a8c9e20"
+++

# Agent-guided segmentation with local promptable models

Can a general agent improve dense medical segmentation by selecting and correcting prompts to a frozen local segmenter, beyond fixed prompting and agent-only geometry?

## Prior findings

Research proposal, 2026-09-21. The user requested candidate models for this Mac
and benchmark suggestions. The priorities below are assistant recommendations;
no model installation, weight/data download or trial is authorized by this note.

The [CT-only organ study](ct-organ-segmentation-from-scan.md) is the closest
starting point. [Astra/xhigh](../findings/ct-organ-segmentation-astra-xhigh.md)
achieved macro Dice 0.7380 with all ten matched identities correct, using sparse
visual contours and interpolation. [Its method audit](../findings/ct-organ-methodology-astra-xhigh.md)
reproduced the final masks and found limited systematic image-boundary fitting.
[Sol/xhigh](../findings/ct-organ-segmentation-sol-xhigh.md) also had substantial
localization errors. A promptable segmenter might improve contours, but cannot be
assumed to repair a prompt placed on the wrong anatomy.

The [dental trace audit](../findings/dental-trace-root-causes.md) separates an
unresolved orientation/annotation contract from real pulp, canal and tooth-shape
errors. Its original low semantic scores are unsuitable as an uncomplicated
before/after baseline. Preserve those results and review state.

## Local feasibility and model shortlist

Read-only host inspection reports Apple M5 Pro, 64 GiB unified memory, macOS
26.6.2 and approximately 435 GiB available disk. The repository's active Python
3.12 environment has none of torch, coremltools, mlx, sam2 or segment_anything.
This is an environment-specific observation, not a scan of every local runtime.
No inference was tested; Mac latency, peak memory and numerical parity are unknown.

| Priority | Candidate | Evidence and proposed use |
| --- | --- | --- |
| First general model | SAM 2.1 Small, with Base+ as a later capacity comparison | [Apple's FP16 Core ML release](https://huggingface.co/apple/coreml-sam2.1-small) provides an image-segmentation route. For slice/video propagation use the full [official SAM2 predictor](https://github.com/facebookresearch/sam2), whose [MPS backend](https://github.com/facebookresearch/sam2/blob/main/demo/backend/server/inference/predictor.py) is explicitly preliminary. The [installation guide](https://github.com/facebookresearch/sam2/blob/main/INSTALL.md) permits skipping the CUDA extension; this changes hole/sprinkle postprocessing. Pin that choice. Do not assume Apple's encoder/decoder packages include the full video-memory pipeline. |
| First medical comparator | LiteMedSAM | The [author release](https://github.com/bowang-lab/MedSAM/tree/LiteMedSAM) replaces the image encoder with TinyViT. Its [inference script](https://github.com/bowang-lab/MedSAM/blob/LiteMedSAM/CVPR24_LiteMedSAM_infer.py) defaults to CPU, uses 256-pixel input and box prompts, and propagates boxes slice by slice. CPU is a credible starting route; MPS is unverified. Cropping may preserve small-structure detail, but every crop must be image-derived and mapped back to native coordinates. Box revision is the supported interaction; do not assume calibrated negative-click behavior. |
| First lesion-volume candidate | Efficient MedSAM2 Small/Tiny | [Official CPU inference](https://github.com/bowang-lab/MedSAM2/blob/main/eff_medsam2_infer_CT_lesion_npz_recist.py) loads eff_medsam2_small_FLARE25_RECIST_baseline.pt or the tiny equivalent. It expands a RECIST-derived prompt across CT slices. This checkpoint is a FLARE25 lesion baseline, not demonstrated universal organ/dental segmentation. The supplied demonstration reads GT; build a separate image/prompt-only adapter before any blind task. |
| Second-stage medical propagation | MedSAM2 | The [author repository](https://github.com/bowang-lab/MedSAM2) provides 3D/video segmentation and the [model card](https://huggingface.co/wanglab/MedSAM2) lists general, CT-lesion, MRI-lesion and heart-ultrasound weights. Installation documentation targets Linux/CUDA; Mac execution needs a feasibility check. Record checkpoint-specific terms: code and weight terms differ, and the model card restricts weights to research/education. |
| Optional text-prompt experiment | SAM 3 / 3.1 | [Meta](https://github.com/facebookresearch/sam3) provides text/exemplar segmentation; SAM 3.1 adds joint multi-object tracking. Official setup requires CUDA and checkpoint access. [sam3.cpp](https://github.com/PABannier/sam3.cpp) is an independent CPU/Metal implementation advertising SAM 3 support, not verified SAM 3.1 parity. Treat it as a separate port-validation task before medical comparison; ordinary-image concept recognition does not establish CT anatomy recognition. |

[nnInteractive](https://github.com/MIC-DKFZ/nnInteractive) is scientifically
relevant for native 3D corrections, but its [official Napari integration](https://github.com/MIC-DKFZ/napari-nninteractive)
recommends remote inference on Macs because CPU/MPS 3D convolutions are too slow
for practical use. Defer it for an entirely local first pilot.

Include [TotalSegmentator](https://github.com/wasserth/TotalSegmentator) as a
specialist baseline for the abdominal task: its documentation explicitly supports
M-series Macs with --device mps. It is automatic semantic segmentation, a different
interface from SAM. Verify exact checkpoint/split overlap before interpreting its
performance on the TotalSegmentator source cohort; do not use its prediction as GT.

## Proposed benchmarks, in order

1. **Abdominal organ prompting and correction.** Reuse s1233 only for development
   and a descriptive bridge to the frozen ten-organ result. After feasibility,
   curate five additional cases and retain the same taxonomy, including large
   organs as preservation checks and pancreas/adrenals/duodenum as difficult
   targets. Measure semantic and matched Dice, per-organ surface distance in mm,
   omissions, corrections, elapsed time and tool cost. A surface-Dice tolerance
   must be fixed before evaluation; it is not a clinical acceptance threshold.
2. **CT lesion: one mark to a full 3D mask.** Efficient MedSAM2 is a close fit.
   Use a disjoint, manually reviewed lesion cohort with dense masks and declared
   sparse-prompt provenance. A supplied RECIST mark tests propagation/refinement;
   an agent-created mark also tests localization. Keep those conditions separate.
   The [FLARE RECIST-to-3D source](https://huggingface.co/datasets/FLARE-MedFM/FLARE-Task1-PancancerRECIST-to-3D)
   is a lead, not an admitted holdout for weights trained on that collection.
   Measure volume error, Dice, surface error and off-target leakage.
3. **Ultrasound propagation and drift correction.** SAM2, then MedSAM2 if its
   local backend works. [CAMUS](https://www.creatis.insa-lyon.fr/Challenge/camus/evaluation.html)
   supplies ED/ES references; those do not establish accuracy on intermediate
   frames. [TED](https://humanheart-project.creatis.insa-lyon.fr/ted.html) provides
   98 fully annotated A4C cycles, making it a better candidate for frame-selection
   and correction experiments. Score framewise contours and drift, with correction
   count; smoothness alone can reward a consistently wrong mask. No local TED
   download or checkpoint-overlap audit was performed.
4. **Later: dental instances and vessel topology.** Start dental work with
   whole-tooth instances, then assess numbering separately after the orientation
   contract is adjudicated; pulp/canals need higher-resolution evaluation.
   [TopCoW](https://topcow24.grand-challenge.org/assessment/) supports Dice,
   centerline overlap and connectivity checks for vessels. Follow the existing
   [vessel idea](../../tubular-anatomy/ideas/idea-vessel-connectivity-repair.md):
   its synthetic gap is calibration, and the disputed natural structure remains
   under review. Admit a new natural prediction error before reopening that study.

## Comparison that tests complementarity

Use a frozen segmenter and a small tool interface: show native slices, segment
with supported prompts, propagate where supported, inspect overlays and save masks.
Run the accelerator service natively on macOS, with an isolated solver-facing
interface exposing only admitted scans, prompts and predictions. Keep GT and
evaluator feedback outside it. Cache image embeddings and record all transforms,
prompts, checkpoint hashes, backend, precision and postprocessing.

Compare fresh agent-only segmentation with an image-only one-shot agent prompt
plus fixed segmentation/propagation, and iterative agent-guided corrections using
that same initial prompt and segmenter state. Include a deterministic correction
schedule under the same interaction allowance to distinguish adaptive selection
from merely spending more calls. For a first pilot, propose up to five corrective
interactions per target, counting boxes, points and propagation work separately.
Report paired case-level gains and regressions, not only a pooled voxel score.
An expert/GT-prompted calibration arm estimates tool potential and must remain
outside the autonomous ranking. Score intermediate masks privately after the run;
never return GT-derived best slices, boxes, clicks or stopping signals to the agent.

Backend smoke checks should cover coordinate round trips, full-grid mask export,
CPU/accelerator comparison on fixed prompts, latency and peak memory before any
new agent run. Training overlap is separate from runtime leakage: unknown overlap
permits a qualified tool-value pilot, not a clean unseen-data generalization claim.

[MedSAM-Agent](https://github.com/CUHK-AIM-Group/MedSAM-Agent) is direct related
work: it trains a multimodal model for iterative segmenter prompting, and releases
base code/model with CUDA-based setup. Its remaining trajectory/data releases are
listed as pending. Our proposed question is whether the existing general agents
gain this capability from a frozen tool without segmentation-specific training.
Published results motivate the test; they do not predict our local outcome.

## Decision and reopening

2026-09-21 — **assistant recommendation:** begin with SAM 2.1 Small and LiteMedSAM
on the abdominal development fixture, then select the volume-capable path for a
small paired study. Keep Efficient MedSAM2 as the lesion-focused next option.
The user's request authorizes research and proposal capture only. Reopen execution
after model provisioning and a bounded pilot are requested, with accepted data,
reference conventions, backend checks and checkpoint provenance recorded in new
experiments. Original standalone-agent results remain unchanged.

### Narrow model verification — 2026-09-21

The user then authorized downloading the two first candidates and sampled local
verification, explicitly excluding the previous spawned-agent process. The
[completed calibration](../findings/sam-litemedsam-slice-calibration.md) used one
CT, six organs, three slices per organ and two reference-derived box sizes.
LiteMedSAM MPS mean Dice was 0.8334/0.8524 (tight/loose), versus SAM2 MPS
0.7745/0.5165; a same-sample CPU diagnostic gave SAM2 0.7905/0.5593. Warm image
encoding medians were 42.5 ms and 134.5 ms respectively. SAM2 backend differences
remain explicit; four LiteMedSAM CPU/MPS check masks matched exactly.

Assistant recommendation: prioritize LiteMedSAM as the abdominal box-to-mask
tool; duodenum/multiple separated regions remain a useful correction case.
This supports local feasibility and conditional mask quality, not agent
complementarity or blind 3D performance. The accepted narrow work is complete;
no larger agent experiment or additional download was started.

### Reusable tool closeout — 2026-09-21

The user requested a concise rulebook and skill so later “seg tool” / “SAM” hints
can reuse LiteMedSAM, and asked for overlay legends with matching colors.
The [rulebook](../../../docs/segmentation-tools.md) now routes those requests to
the [solver skill](../../../src/tb3_medical/skills/litemedsam/SKILL.md), also
installed in the local Codex skills folder. The adapter reads only an explicit
image and boxes. A two-mask MPS smoke check exactly matched saved predictions;
both installed Harbor versions accepted the task skill configuration. The
[packaging receipt](../findings/evidence/litemedsam-skill-verification.json) retains
that narrower validation scope. No container runtime or general-agent trial ran.

Task-bound `environment.skills_dir` lets a new tb3 task carry the skill in its
frozen payload without changing the launcher. Runtime/weights still need explicit
provisioning inside that task. Future trials must retain the tool condition and
separate agent-selected prompts from reference-box calibration. Existing frozen
agent tasks and original calibration bytes remain unchanged. New overlay copies
have matching-color legends; this is a presentation revision, not new evidence.

The user subsequently clarified that skill discovery must describe execution
inside the solver environment, rather than requests to set up an experiment.
The skill now advertises mask creation/refinement directly, without requiring SAM
to be named in the task. Author setup guidance and the Mac runtime locator remain
in the rulebook. This wording revision leaves the inference adapter and recorded
smoke-test results unchanged; the prior receipt's skill digest identifies its
original tested revision.
