# Anatomy experiments — results, trace analysis and current verdict

[**Open the earlier-trial presentation**](../runs/anatomy-history-presentation/index.html) ·
[Per-trial trace analysis](anatomy-traces.md) ·
[Absorbed-tissue experiment](research-rounds/BR-017-results.md)

**BR-017 M02 remains the strongest failure-backed lead in this anatomy series.**
The earlier BR-013 A02 identity miss is a compact secondary diagnostic, weakened
by subsequent passes with an exact class inventory, source CT or proposed names.
No robust, low-resource Sol-failure task is established yet.

## Earlier trials at a glance

| Task | Model | Outcome | Agent time | Output tokens |
| --- | --- | --- | ---: | ---: |
| BR-013 A01 · ordinary anonymous organs | Sol/xhigh | 13/13 | 73.36 s | 2,035 |
| BR-013 A02 · atypical anonymous organs | Sol/xhigh | **9/11** | 157.58 s | 5,015 |
| BR-013 A02 · same frozen task | Terra/max | **10/11** | 176.29 s | 7,838 |
| BR-013 A03 · misleading names on A02 geometry | Sol/xhigh | Both corrected; no false repairs | 88.85 s | 2,306 |
| BR-014 I01 · A02 with exact present-class inventory | Sol/xhigh | 11/11 | 75.58 s | 2,602 |
| BR-014 F01 · four substantial organ fragments | Sol/xhigh | 15/15 | 222.65 s | 6,620 |
| BR-015 C01 · A02 with source CT | Sol/xhigh | 11/11 | 136.16 s | 5,150 |
| BR-015 V01 · eight abdominal veins with CT | Sol/xhigh | 8/8 | 98.12 s | 2,852 |

Seven Sol attempts and one conditional Terra follow-up; no retries. Fourteen
oracle/no-op controls behaved as expected. Each model had 1,800 seconds and four
CPUs/4 GiB. The table contains distinct completed attempts, not a success-rate
sample; Terra was selected after Sol failed.

## Why the earlier miss is interesting

In A02, **o197 is an intact 43.4 mL source pancreas** and o277 is duodenum.
Both Sol and Terra call o197 gallbladder; Sol additionally calls o277 pancreas.
All masks retain source voxels and shared coordinates. There is no planted
micro-defect or exact boundary judgment.

The task permits unused labels: 11 objects are assigned from 13 possible
classes. Sol's wrong mapping forms a coherent but incorrect inventory. It
inspects several views, calculates principal axes and prints depth-collapsing
ASCII projections. Its planned surface-distance calculation fails at a SciPy
import and is not replaced.

```text
A02: same atypical central geometry, broad vocabulary, no CT
  Sol 9/11; Terra 10/11
  ├─ A03: proposed names to audit → Sol corrects both swaps
  ├─ I01: exact present-class inventory → Sol 11/11
  └─ C01: source CT + previews/helper → Sol 11/11
```

Each branch is a new condition and fresh session. The branches preserve the
central geometry but change information or the requested decision. They
suggest inventory/evidence uncertainty matters; they do not identify a causal
mechanism or establish a general anatomical deficit.

## What the traces add

- **Ordinary recognition:** spatial anchors reduce the problem to a small
  ambiguous group; focused views finish the mapping.
- **Misleading names:** Sol rejects the supplied pancreas/duodenum swap using
  the enclosing-loop relationship. Incorrect names did not force anchoring.
- **Fragment ownership:** Sol replaces failed SciPy code with NumPy distances
  and voxel-overlap counts, then groups the four pieces correctly. Native
  cross-organ overlap provides an exclusion clue; this is not a pure visual test.
- **CT rescue:** intensity measurements and focused views precede the correct
  compact-pancreas identification. The failed coronal command was not rerun.
- **Vessel identity:** prepared previews and spatial measurements suffice. Its
  public claim of an “endpoint check” is not evidence of an executed endpoint
  or graph algorithm; none appears in the commands.

The presentation provides a walkthrough for every trial, exact returned images,
pseudocode and public excerpts. Its [trace index](evidence/anatomy-trace-index.json)
verifies 103 step anchors and result/trajectory/answer hashes. The 113 files in
the earlier frozen manifests are unchanged. One unmanifested local Python
bytecode cache is recorded separately and retained.

## Candidate verdict

| Candidate | Current judgment | Reason |
| --- | --- | --- |
| **BR-017 M02: partial absorption, broad audit** | **Primary research lead** | Reviewed detection miss on 21.04 mL with CT and all labels present; clean negative control; exact small output. 404 s / 10,593 output tokens / estimated $1.011. |
| **BR-013 A02: atypical identity, uncertain inventory** | **Secondary diagnostic** | Both models miss the same whole organ, with a shorter Sol run. Mask-only identifiability is unresolved and three contextual follow-ups pass. 158 s / 5,015 output tokens / estimated $0.304. |
| A01, A03, I01, fragment F01, C01, V01 | Retired as hard Sol candidates | Each completed with a clean pass under its tested contract. |
| BR-017 M01, N01, focused F01 | Controls / retired passed conditions | Their passes help interpret the original broad-audit miss. |
| Earlier BR-004 micro-boundary cases | Historical evidence; do not promote | Earlier task-validity concerns remain; this series does not resolve them. |

M02's **focused two-mask version passed with identical evidence**. Preserve the
original broad scope in its failure claim. The useful remaining hypothesis is
an incomplete ownership audit across plausible neighboring masks. One failed
attempt does not establish reliable failure, and these results do not establish
a clinician-versus-model performance gap.

## Scope and sources

The masks were supplied. The agents identified existing objects or audited
their ownership; they did not segment raw CT from scratch. No specialist medical
inference model or new training was invoked in the observed tools.

BR-010/011/012 contain reassessment, baseline screens and source curation; they
add no model trials. BR-016 is a separate aneurysm experiment with its own
[report](research-rounds/BR-016-results.md) and verdict. Historical protocols,
source fixtures, raw runs and frozen grades remain preserved.

[BR-013 results](research-rounds/BR-013-results.md) ·
[BR-014 results](research-rounds/BR-014-results.md) ·
[BR-015 results](research-rounds/BR-015-results.md) ·
[Rebuild this presentation](../probes/revisions/anatomy-history/authoring/README.md)
