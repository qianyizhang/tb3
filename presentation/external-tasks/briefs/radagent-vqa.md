# Answer a multiple-choice question about chest CT

Use a chest CT volume and specialist tools to select the answer to a medical question.

## Value

A focused question tests whether tool-derived evidence can support a specific finding, independently of whole-report writing.

## Given

### Original data

A CT-RATE volume paired with a VQA question and answer options.

### Supplied helpers

The question constrains the target finding. The toolbox can supply anatomy masks, selected slices and model-derived findings on demand.

### Callable tools

Whole-volume and slice VQA, disease classification, anatomy/effusion segmentation, slice selection and windowing; availability depends on the agent variant and model assets.

### Reference-only material

Evaluation targets are references, not extra solver inputs. Local filesystem visibility has not been audited by running this external task.

## Task specification

Use a chest CT volume and specialist tools to select the answer to a medical question.

## Expected output

A final multiple-choice answer with a retained trace of the agent’s tool interactions.

## Evaluation

Use the linked task’s evaluator and its reference data. This survey has not executed that evaluator or established a reproduced score.

## Visual explanation

### Workflow

- Chest CT + question/options
- Gather and reconcile tool evidence
- Selected answer + tool trace

### Input

**Contract view; native sample not yet illustrated.** A CT-RATE volume paired with a VQA question and answer options.

### Supplied helpers

**Given material, not an answer reveal.** The question constrains the target finding. The toolbox can supply anatomy masks, selected slices and model-derived findings on demand.

### Reference or output

**Expected artifact, not an actual prediction.** A final multiple-choice answer with a retained trace of the agent’s tool interactions.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Source condition | The question constrains the target finding. The toolbox can supply anatomy masks, selected slices and model-derived findings on demand. | Choose useful tools, resolve disagreement between their findings and connect the evidence to the exact question. |

## Difficulty

Choose useful tools, resolve disagreement between their findings and connect the evidence to the exact question.

## Sources

- [Repository setup and VQA data paths](https://github.com/eth-medical-ai-lab/rad-agent/blob/9e9d32936ce24676cba32c81605720fe74a5da5a/README.md)

## Coverage

A shared definition brief for the linked catalogue entries. Case identities and source conditions remain in the catalogue; this is not a claim to enumerate all generated or external cases.

## Gaps

CT-RATE access and model weights require separate setup. The VQA-specific submission parser/scorer has not been audited here; no native VQA case or agent run is illustrated.
