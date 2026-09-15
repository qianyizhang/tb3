# BR-017 — Anatomy under the wrong label

**Sol missed a 21.04 mL pancreatic inclusion during a broad audit. A fresh,
focused audit found it using the same data.** Whole absorption and the unchanged
control also passed. Each condition received one Sol/xhigh trial.

[**Open the visual presentation**](../../runs/br017-absorption/review/index.html) ·
[How each Sol trial worked](BR-017-traces.md) ·
[Earlier trials and current candidate ranking](../anatomy-experiments.md) ·
[Protocol](BR-017-absorbed-anatomy.md) ·
[Measured results](../evidence/br017-results.json) ·
[Authoring and reproduction](../../probes/revisions/br017/authoring/README.md)

## The experiment

Supply existing organ masks, proposed names, full CT and rendering helpers.
Ask the agent to find masks containing **at least 5 mL of another organ**.
A finding contains the host ID, included organ name and one physical point,
accepted within 3 mm of an included-region voxel centre. Exact host/class pairs
are required; missing, extra or duplicate findings fail.

All conditions use TotalSegmentator case `s1233` (local case 28). A synthetic
transfer reassigns source-pancreas tissue to the duodenum label. Original CT
and aggregate foreground are preserved, and the other 11 masks are unchanged.

| Condition | Tissue newly assigned to duodenum | Separate pancreas | Audit scope | Result |
| --- | ---: | ---: | --- | --- |
| **M02 · Partial absorption** | **21.04 mL** | **38.38 mL** | All 13 masks | **Miss: empty findings** |
| M01 · Whole absorption | 59.35 mL | Absent | All 12 masks | Pass: correct inclusion and point |
| N01 · Unchanged control | None | 59.42 mL | All 13 masks | Pass: no false findings |
| F01 · Focused partial audit | Same as M02 | Same as M02 | Pancreas and duodenum | Pass: correct inclusion and point |

![Identical CT before and after partial label reassignment](../../runs/br017-absorption/review/partial-absorption-compact.png)

The partial transfer spans **45 × 37.5 × 67.5 mm** and forms one connected
region. All 13 label names remain present and the enlarged duodenum is still
one connected mask. M02 fails detection before point scoring is reached.
The presentation lets you toggle original, reassigned and transferred-region
views on identical axial/coronal planes; this author illustration was not
supplied to Sol.

F01 preserves every M02 public image, array, CT sample, helper and key byte.
Only `instruction.md` and `task.toml` change. Its scope explicitly directs
attention to the affected pair. It was declared after M02/M01 outcomes and
before N01's result, then run after N01 passed.

## What the traces reveal

| Trial | Observable approach | How the decision develops |
| --- | --- | --- |
| M02 | Broad numerical screen plus targeted three-plane pancreas/duodenum views | Accepts the local appearance, sweeps the remaining anatomy, reports no inclusion. |
| M01 | Missing pancreas prompts a search in neighboring masks | Identifies pancreatic gland plus duodenal loop inside one host; quantifies a substantial subset and validates an interior point. |
| N01 | Broad screen initially asserts two errors | Additional intensity measurements and paired views precede a reversal; final answer correctly clears the case. |
| F01 | Two-mask geometry, rotated 3-D views and finer interface sheets | Continues checking after global shapes look coherent; identifies wrongly assigned pancreatic head/uncinate tissue and validates a point. |

The [per-trial analysis](BR-017-traces.md) provides the ordered stages,
pseudocode, public-message excerpts and actual returned image sheets, with
86 trace-step anchors checked against the frozen records.

Sol combined **code-based measurement, image inspection and anatomical
assessment**. No specialist medical inference model or new training was invoked
in these traces. The segmentations were already supplied; the agent audited
their anatomical ownership. Geometry establishes properties such as volume and
connectivity, while the image-based assessments supply the organ interpretation.

The focused pass is consistent with audit coverage or allocation of attention
contributing to the broad miss. It weakens a claim of general anatomical
inability. One fresh run with an explicit scope hint cannot isolate the cause;
run-to-run variation remains possible. M01 additionally changes both the
missing-label cue and inclusion size, so those effects cannot be separated.

## Resources

| Trial | Agent time | Total trial time | Images returned | Commands | Output tokens | Estimated cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| M02 | 404.39 s | 468.53 s | 27 | 23 | 10,593 | $1.011 |
| M01 | 348.73 s | 412.32 s | 26 | 26 | 15,102 | $1.120 |
| N01 | 453.39 s | 517.29 s | 31 | 29 | 11,864 | $1.260 |
| F01 | 351.18 s | 420.67 s | 17 | 24 | 12,009 | $0.932 |

| Trial | Input tokens | Included cached input | Included reasoning output |
| --- | ---: | ---: | ---: |
| M02 | 1,148,305 | 1,053,824 | 6,003 |
| M01 | 1,229,817 | 1,139,200 | 9,198 |
| N01 | 1,656,389 | 1,556,224 | 6,645 |
| F01 | 947,867 | 861,056 | 6,973 |

Totals: **25.96 agent minutes, 49,568 output tokens, estimated $4.324**.
Input includes repeated context and cache; output includes reasoning. Costs
are harness estimates. Agent time excludes setup/verification; total includes
them. Images count returned payloads, not tiles inside a sheet. Recovered tool
errors remain included in command counts and resource totals.

F01 used 13% less agent time and 17% fewer input tokens than M02, but produced
13% more output. Neither image count nor this single comparison establishes a
general efficiency recipe.

## Verification and scope

All four sessions completed normally with `gpt-5.6-sol`, `xhigh` and Codex
0.154.0. Each had 1,800 seconds, four CPUs, 4 GiB RAM and zero retries. Actual
CPU/RAM peaks were not measured. Every run recovered from unavailable SciPy;
some also corrected missing utilities or cropped-array alignment errors.

- All eight matched oracle/no-op Docker controls behaved as expected.
- Thirty-six unique authored scoring controls cover points, thresholds,
  incorrect findings and malformed answers. F01 inherits M02's 15 records.
- Independent source-grid reconstruction verifies CT, label lineage and frozen
  inputs; grading replay agrees with every result.
- Accepted model points are 0.00046 mm (M01) and 0.016 mm (F01) from included
  source-voxel centres. All four final answers score in approximately 0.57–6.37 ms.

This is a synthetic source-mask experiment with one attempt per condition,
not a population failure-rate estimate. Source contour accuracy and clinical
performance were not established. The pancreatic remnant retains three tiny
native-overlap islands (22 voxels total, under 26-neighbor connectivity); a
geometric shortcut has not been ruled out exhaustively.

The round is complete. Retain M02 as the broad-audit detection miss and retire
the three passing task conditions. This presentation adds analysis without new
model trials or changes to frozen tasks.

[Source/voxel audit](../evidence/br017-audit.json) ·
[All-trial checks](../evidence/br017-reviews.json) ·
[Trace index](../evidence/br017-trace-index.json) ·
[Dataset and license](https://zenodo.org/records/10047263)
