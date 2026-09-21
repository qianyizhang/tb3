# Narrow Mac slice calibration

2026-09-21. [User authorization](codex://threads/01a0c423-5d0a-7ee3-97b4-66939a8c9e20):
download SAM 2.1 Small and LiteMedSAM and run sampled, narrow experiments in this
task, without spawning the previous agent workflow. Direct local inference only;
no general-agent trial, Docker harness, training or publishing.

## Fixed scope before model outputs

- One retained CT, TotalSegmentator v2.0.1 s1233. Verify original source hashes
  against the prior CT experiment's selected-source manifest.
- Six targets: liver, right kidney, gallbladder, pancreas, right adrenal, duodenum.
- Three axial slices per organ, selected at 25%, 50%, 75% of its nonempty-slice
  index list using nearest integer (NumPy rounding). No result-based selection.
- Two identical prompt conditions for both models: reference bounding rectangle
  expanded by 2 pixels (3 mm) or 10 pixels (15 mm), clipped to the image.
- Full axial slices, fixed CT window [-160, 240] HU, replicated grayscale RGB.
  Retain native index convention: image x=i, y=j, slice=k. No spatial resampling
  of the reference. Model-specific input resizing/normalization follows upstream.
- SAM2: official sam2.1_hiera_small.pt and sam2.1_hiera_s.yaml, single mask output
  with default stability fallback, no CUDA hole/sprinkle postprocessing.
- LiteMedSAM: official lite_medsam.pth, TinyViT 256, box prompt, logits resized
  before thresholding at zero. No added connected-component or contour cleanup.
- Both use PyTorch FP32/eval/inference mode, four CPU threads, sequential MPS
  execution. One warmup then synchronized encode/prompt timings. Two middle-slice
  samples (liver and right adrenal) are also run on CPU for a backend check.

This yields 72 primary predictions and 8 CPU predictions. Measure 2D Dice,
precision/recall, 2D HD95 in mm and encoding/decoder latency. Preserve masks,
box coordinates, source/model/code hashes and package versions. Memory reporting
distinguishes process peak RSS from sampled Metal allocator readings.

## Interpretation

Reference-derived slices and boxes deliberately supply localization. This is a
tool calibration, not an autonomous or leakage-free generalization benchmark.
Known public development case; weight training overlap is unverified. Eighteen
organ-slice pairs are correlated samples from one patient. Their scores cannot be
compared directly to the earlier full-volume CT-only agent macro Dice. CPU/MPS
agreement on two samples cannot establish global numerical equivalence. Narrow
box sensitivity does not establish interactive correction or 3D propagation.

## Bounded backend follow-up

After the 72 primary predictions and 8 prespecified CPU checks, SAM2's loose-box
right-adrenal middle sample had CPU/MPS mask-to-mask Dice 0.5381. LiteMedSAM's four
CPU/MPS pairs were pixel-identical. To resolve whether the device explained the
primary comparison, repeat SAM2 on CPU for the same fixed 18 samples and two boxes
(36 additional predictions). This is a post-result backend diagnostic; retain the
original MPS outputs, sample selection, prompt conditions and scores unchanged.

## Reproduction

Local workspace: `.local/sam-lite-bench-20260921/`; runtime and weights remain local.
The retained script has `prepare` and `run` commands. LiteMedSAM's upstream
TinyViT module is not included by its packaging; run the script from the upstream
LiteMedSAM checkout using Python `runpy.run_path`, which permits its normal module
import without modifying sys.path or upstream files. Exact commands and versions
are retained with the result receipt. No historical authoring module is executed.

The measured environment used torch 2.10.0, torchvision 0.25.0, NumPy 2.2.6 and
timm 1.0.15. `requirements-resolved.txt` and `provisioning.json` under the local
workspace record the complete dependency versions, official checkpoint URLs,
weight hashes and exact upstream commits. SAM2 was installed with
`SAM2_BUILD_CUDA=0`; the two source packages were installed without their broad
optional development/training dependencies. Both upstream tracked trees remain
unchanged.

Executed command pattern, from the upstream LiteMedSAM directory:

```sh
/Users/zhangqy/pkgs/tb3/.local/sam-lite-bench-20260921/.venv/bin/python -u -c \
  'import runpy; runpy.run_path("/Users/zhangqy/pkgs/tb3/groups/anatomy-audit/experiments/sam-litemedsam-slice-calibration/bench.py", run_name="__main__")' \
  run --model lite --device mps
```

Use `--model sam2` for SAM2 and `--device cpu --subset` for the prespecified CPU
checks; the supplementary SAM2 CPU run omitted `--subset`. Inference deliberately
refuses existing output directories. Retain the completed local workspace rather
than deleting outputs for a rerun. `summarize.py` replays existing masks without
inference and regenerates only derived summary figures.

## Completion

[Results and limits](../../findings/sam-litemedsam-slice-calibration.md): all
requested local calibration conditions and the bounded backend check completed.
No larger agent experiment was started. Keep the study diagnostic and the original
CT-only agent evidence separate.
