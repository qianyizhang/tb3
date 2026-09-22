# Produce a structured breast MRI assessment

Review breast MRI and submit laterality, lesion count, enhancement status and a BI-RADS category.

## Value

BI-RADS is a standardized breast-imaging assessment vocabulary. A structured output makes reporting fields directly inspectable.

## Given

### Original data

A breast MRI study containing multiple series, including images before and after contrast injection.

### Supplied helpers

Series metadata and image navigation. In the oracle condition, query_birads_model exposes prepared findings instead of requiring their visual discovery.

### Callable tools

Viewer tools and submit_birads_report; query_birads_model is added for the oracle condition.

### Reference-only material

Evaluation targets are references, not extra solver inputs. Local filesystem visibility has not been audited by running this external task.

## Task specification

Review breast MRI and submit laterality, lesion count, enhancement status and a BI-RADS category.

## Expected output

A submit_birads_report call containing laterality, lesion count, category and enhancement presence.

## Evaluation

Both conditions use birads_report_scorer against the source report fields. This is agreement with a reference, not independent validation of diagnostic quality.

## Visual explanation

### Workflow

- Breast MRI + series metadata
- Assess enhancement or query oracle
- Structured breast MRI report

### Input

**Contract view; native sample not yet illustrated.** A breast MRI study containing multiple series, including images before and after contrast injection.

### Supplied helpers

**Given material, not an answer reveal.** Series metadata and image navigation. In the oracle condition, query_birads_model exposes prepared findings instead of requiring their visual discovery.

### Reference or output

**Expected artifact, not an actual prediction.** A submit_birads_report call containing laterality, lesion count, category and enhancement presence.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Visual assessment | Series list and rendered breast MRI. | Find enhancing lesions and assign report fields. |
| Oracle findings | Prepared findings returned by query_birads_model. | Query the correct series and submit the returned fields correctly. |

## Difficulty

Compare pre- and post-contrast images and separate lesions from normal enhancement. Oracle assistance largely removes the perception step.

## Sources

- [Task generator](https://github.com/Luab/ABRA/blob/688814615dc368a66276798cb864fe9a587d7e6c/scripts/task_generators/tier4_birads.py)
- [Task generator](https://github.com/Luab/ABRA/blob/688814615dc368a66276798cb864fe9a587d7e6c/scripts/task_generators/tier3_oracle_birads.py)

## Coverage

A shared definition brief for the linked catalogue entries. Case identities and source conditions remain in the catalogue; this is not a claim to enumerate all generated or external cases.

## Gaps

Native input/helper/reference views are still missing for this definition. The contract was read from source; no external model or benchmark run was launched.
