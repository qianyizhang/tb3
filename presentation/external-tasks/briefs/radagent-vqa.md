> **Symbolic illustration — matching CT-RATE VQA case and CT are absent; [request official CT-RATE access](https://huggingface.co/datasets/ibrahimhamamci/CT-RATE).**

# Answer a RadAgent chest CT multiple-choice question

Use the supplied question and available CT tools to return exactly one complete option string. This is question answering, not report generation or diagnosis demonstrated by this explainer.

## Given

### Original data

The loader reads `labels/multiple_choice/multiple_choice_{train,valid}.csv`: question→task, qid→task_id, image_id→configured CT path and answer→gt. The initial model message contains task text/path, not gt. Matching CSV/CT are absent; a fresh anonymous exact volume request returns HTTP401 GatedRepo.

### Supplied helpers

The question contains answer options. Agent variants may call whole-volume `ct_vqa_tool` or `slice_vqa_tool` on selected 2D slices; those outputs are model-derived evidence, not gold answers. V8minus removes whole-volume VQA and disease-classifier tools. No tool output is simulated as observed.

### Callable tools

Tools depend on agent variant/configuration; stop through JSON `action="final_answer"`. The source rollout limit is 60 turns. Optional model servers/assets were neither installed nor run.

### Reference-only material

CSV answer becomes scenario gt. Initial messages omit it, but host trajectory state retains the scenario. Runtime filesystem/host isolation is unaudited; no actual gt or reference asset is bundled.

## Task specification

Choose relevant tools, distinguish volume from selected-slice evidence, reconcile tool disagreements and match the exact option text. Prompt instructions explicitly preserve the option prefix: a format example like `(b) Amber token` is different from `b`, `Amber token` or `b Amber token`. This example is authored and nonclinical; it is not an original case or answer.

## Expected output

`{"action":"final_answer","answer":"<full option text including prefix>"}` plus the retained tool trajectory. Actual answer/trajectory remain empty in this pack; illustrative selections are not submitted.

## Evaluation

The pinned BaseOrchestrator VQA reward branch was located: for a completed task it strips/lowercases gt and the final parsed answer, records exact-match `vqa_correct`, and forms a base reward of exact indicator + BLEU-1 + ROUGE-L. Configured trajectory/manual-tool/tool-success terms can augment total reward. These measure string agreement or tool-use terms, not clinical validity. The main validation rollout uses `compute_reward=False`; training uses True. No correctness or reward value is shown here.

## Visual explanation

A missing CT stack and question socket feed a source-field map and optional model-tool branches. Canonical selection switches whole-volume, selected-slice and evidence-reconciliation operations. A separate nonclinical token fixture shows full-option formatting; explicit reader reveal describes evaluator rules without private values. Leaving the reference chapter/reset hides those rules. No patient findings, tool claims or performance are fabricated.

## Sources

- [Pinned loader](https://github.com/eth-medical-ai-lab/rad-agent/blob/9e9d32936ce24676cba32c81605720fe74a5da5a/radagent/agents/art_dataset.py)
- [Pinned prompt](https://github.com/eth-medical-ai-lab/rad-agent/blob/9e9d32936ce24676cba32c81605720fe74a5da5a/radagent/agents/custom_orchestrators.py)
- [Pinned VQA reward branch](https://github.com/eth-medical-ai-lab/rad-agent/blob/9e9d32936ce24676cba32c81605720fe74a5da5a/radagent/agents/base_orchestrator.py)
- [Official CT-RATE](https://huggingface.co/datasets/ibrahimhamamci/CT-RATE)
- [Resolution receipt](../sources/radagent-vqa-resolution.json)

## Gaps

Case question/options, authorized CT, tool outputs and participant result remain absent. Pure-source tests confirm direct loader default end_idx=None raises TypeError and explicit df.loc endpoints are inclusive. The CLI default end_id=5000 supplies an integer, so it avoids that direct default error. No runtime task or full NLP-metric implementation was executed. Source README links MIT, but pinned tree has no root LICENSE; data has separate gated terms.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| V8c/V8b | Question, option strings, configured model-derived tool evidence | Select tools, reconcile evidence, preserve exact option text |
| V8minus | Removes ct_vqa_tool and disease classifier | Work with remaining evidence; not equivalent assistance |

## Coverage

One symbolic workflow definition. No matching patient case, tool result, runtime-isolation claim or performance measurement.
