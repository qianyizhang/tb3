---
schema: 2
id: automedbench-full-braintumor-cls-task
title: "Classify brain MRI into source categories"
locale: en
purpose: "Explain canonical label mapping and Full evaluation boundaries."
scope: "Task-specific symbolic workflow; native MRI, Full case IDs, labels, predictions and scores absent."
recipe: automed-brain-cls-v1
asset_pack: symbolic-automed-brain-cls-v1
source_class: symbolic-protocol
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/automedbench-full-braintumor-cls-task.md
- presentation/external-tasks/sources/automedbench-full-braintumor-cls-task-resolution.json
- scripts/build_automed_brain_cls_assets.py
---

# Input

```beat
id: input
scene: input
frames: 288
caption: "MRI absent · kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset"
narration: "The required input is one image dot jpg per Full case. This empty socket means no matching MRI or frozen case ID was recovered. The official Kaggle route is linked. No patient sequence, orientation or image finding is inferred."
visual: "Dedicated input contract panel; no simulated MRI, labels or outputs."
channels:
  progress: [0, 1]
  detail: [0, 1]
  reference: [0, 0]
```

# Helper

```beat
id: helper
scene: helper
frames: 288
caption: "Taxonomy is not a checkpoint index map"
narration: "The source names glioma, meningioma, no tumor and pituitary. A checkpoint can use another order, so map its own label names to the canonical set. Lite and Standard provide method guidance, not supplied model weights or proven performance. Training folder labels are helper material only for genuine training images."
visual: "Dedicated helper contract panel; no simulated MRI, labels or outputs."
channels:
  progress: [0, 1]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Operation

```beat
id: operation
scene: operation
frames: 288
caption: "Verify mapping → infer → submit"
narration: "Select the allowed assistance condition and preserve exact case IDs. Develop and validate a method, then produce one canonical label for each case. A taxonomy token selected here illustrates mapping only; it is not an MRI assessment or model result."
visual: "Dedicated operation contract panel; no simulated MRI, labels or outputs."
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
caption: "CSV or JSON remains unsubmitted"
narration: "The CSV requires patient ID and label, or use one prediction JSON per case. Both sockets remain empty. Private reference labels are absent and remain evaluator-only. Valid present labels can pass format checks even when some predictions are missing; completeness still affects accuracy."
visual: "Dedicated output contract panel; no simulated MRI, labels or outputs."
channels:
  progress: [0, 1]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Limits

```beat
id: limits
scene: limits
frames: 288
caption: "All-case accuracy; present-class mean recall"
narration: "Accuracy divides correct labels by all supplied case IDs, counting missing predictions as wrong. Balanced accuracy averages only supported reference classes. Workflow retains the full step denominator, and overall combines workflow with configured accuracy. No accuracy, recall, rating or clinical result is measured."
visual: "Dedicated limits contract panel; no simulated MRI, labels or outputs."
channels:
  progress: [0, 1]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```
