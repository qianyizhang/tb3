---
schema: 2
id: automedbench-full-medframeqa-task
title: "Link medical frames to a multiple-choice contract"
locale: en
purpose: "Explain native upstream frames and Full option/scoring boundaries without an answer."
scope: "Mixed input teaching; exact Full mapping absent; source gold/reasoning and private reference excluded."
recipe: automed-medframeqa-v1
asset_pack: retained-automed-medframeqa-v1
source_class: source-derived-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/automedbench-full-medframeqa-task.md
- presentation/external-tasks/sources/automedbench-full-medframeqa-task-resolution.json
- scripts/build_automed_medframeqa_assets.py
---

# Input

```beat
id: input
scene: input
frames: 288
caption: "Full join absent · huggingface.co/datasets/SuhaoYu1020/MedFrameQA"
narration: "Two byte-identical upstream public test JPEG frames are retained, but no exact Full question is mapped. Source slot order is not video time or DICOM slice order. Display pixels do not establish HU or physical geometry."
visual: "Own-colored input contract; native upstream frames and no answer or reference."
channels:
  progress: [0, 0]
  detail: [0, 1]
  reference: [0, 0]
```

# Helper

```beat
id: helper
scene: helper
frames: 288
caption: "Six source options do not map to five Full tokens"
narration: "The source example has six options. Full accepts A through E and its list normalizer drops a sixth slot. Inspect this compatibility gap without copying the source question, gold answer or reasoning into the pack."
visual: "Own-colored helper contract; native upstream frames and no answer or reference."
channels:
  progress: [0, 0]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Operation

```beat
id: operation
scene: operation
frames: 288
caption: "Pass every supplied frame to the declared method"
narration: "Lite fixes LLaVA-Med and Standard supplies bounded candidates. Prompt and loader must receive every listed frame. Public-gold calibration is a separate assistance boundary, not evidence of held-out performance. No model or helper executes here."
visual: "Own-colored operation contract; native upstream frames and no answer or reference."
channels:
  progress: [0, 1]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Output

```beat
id: output
scene: output
frames: 288
caption: "Six answer fields remain unset"
narration: "The answer record requires matching question identifier, option label and text, raw model output, model name and numeric runtime. All values remain unset, and no private reference or patient answer is displayed."
visual: "Own-colored output contract; native upstream frames and no answer or reference."
channels:
  progress: [0, 0]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Limits

```beat
id: limits
scene: limits
frames: 288
caption: "Count questions, not frames or videos"
narration: "Accuracy counts all supplied question identifiers, including missing and invalid predictions. Strict all-file format and graded half-valid submission are distinct. Workflow uses active weights; no score or clinical interpretation is claimed."
visual: "Own-colored limits contract; native upstream frames and no answer or reference."
channels:
  progress: [0, 0]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```
