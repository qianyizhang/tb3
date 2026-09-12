# Sourcing and screening method

Recorded 2026-09-12 for the [100-card bank](research-broad-task-bank.md).
This is a retrospective account of how that bank was sourced, followed by
the decision rules for its first screening pass. It is not a preregistered
systematic review, a complete historical search log, or a random sample.

## Scope and selection unit

**Stay away from security tasks:** no vulnerability discovery, exploitation,
authentication/authorization, sandbox escape or protocol attacks. The stopped
security research remains historical evidence and is not a source to resume.

Seek hard but less complex, short-horizon work: one conceptual crux, one small
deliverable, and fast independent verification. A short horizon describes the
work, not an artificially short allowance for reasoning. Installation trouble,
large repositories, long workflows and arbitrary library bans do not count as
difficulty. Keep useful libraries and ordinary tools available.

The selection unit is an exact task or a clearly marked proposed extraction,
not a benchmark's aggregate score. A smaller extraction must establish its own
difficulty; it does not inherit its parent's failure rate. Published tasks are
calibration references, not original submissions. The roughly 100-task target
is a breadth objective for experiments, not a quota of tasks that must survive.

## How the bank was sourced

1. **Start with measured failures.** After six valid local Terra passes, search
   benchmark releases, public task matrices and published run artifacts. Read
   instructions, task metadata and verifier failures before promoting a lead.
   Terminal-Bench-Science yielded five previously audited Terra references.
   CAD Bench v2 yielded six additional partial-credit observations, with a
   separate geometry/fairness caveat. Harbor-Index supplied other-model labels.
2. **Expand along two axes.** Cross fields (science, CAD, RTL, spreadsheets,
   databases, compilers, typography, media, geometry, operations) with task
   types (infer, repair, construct, optimize, transform, measure, verify).
   Prefer a new crux or artifact type over another sibling in the same family.
   Inspect repository inventories for concrete IDs, small inputs and oracles.
3. **Use practitioner anecdotes as discovery leads.** Search HN and Reddit for
   concrete failures, maintainer explanations and counterexamples. Follow a
   post to its fixture, upstream issue or primary specification. A complaint
   without a reproducer stays a hypothesis. Preserve reports of success too.
4. **Read the strongest accessible primary material.** Follow benchmark sites
   to pinned repositories, dataset rows, instructions, solutions and checkers.
   Read exact public trial records when available. Record unavailable layers
   instead of substituting an aggregate score or an invented task statement.
5. **Write a bounded card.** Record source family/URL/ID, source-read depth,
   proposed deliverable and crux, independent verifier, strongest obvious
   baseline, exclusion condition, and the next discriminating action.

Examples of search strings used during the preceding survey include:

```text
BIRD Critic benchmark 600 SQL repair dataset github
GeoSQL Eval benchmark github 2025
compiler optimization benchmark LLM Alive2 peephole optimization benchmark
statistical reasoning benchmark data analysis code hard tasks LAB bench bioinformatics task dataset
LPO missed peephole optimization github artifact ASPLOS 2026
GeoSQL-Eval github dataset PostGIS 2509.25264
site.reddit.com "ffmpeg" "ChatGPT" "failed" sync
site.news.ycombinator.com "LLM" "regex" "failed"
site.reddit.com "FreeCAD" "loft" "ChatGPT"
```

These examples are reconstructed from the research session, not an exhaustive
timestamped query log. The following are **reusable templates**, not claims
that each query was already executed:

```text
<field> benchmark dataset task-level results verifier github
<benchmark> <model> failed completed trajectory task digest
<artifact type> minimal reproducible example wrong result
site:news.ycombinator.com <tool or field> LLM failed
site:reddit.com/r/<relevant community> <operation> ChatGPT wrong
<candidate operation> reference implementation library documentation
<benchmark or task> ambiguous incorrect test multiple valid solutions
```

Search for easy solutions and task defects as actively as for failures. Do not
search only for evidence that supports the candidate. For each promising family,
follow at least one primary implementation or ordinary library baseline before
spending a model trial. Stop a branch when a scope violation, missing essential
fixture, demonstrable oracle defect or ordinary solution already settles its
current disposition. Reopen only with new evidence, not a harder title.

## Retrieval and provenance

The [source manifest](evidence/broad-survey-sources.json) records repository
revisions and hashes of retrieved files. Local `.cache/broad-survey/` holds raw
pages, trees and archives. The [CAD receipts](evidence/cad-v2-survey.json) and
[science receipts](evidence/benchmark-backed-survey.json) preserve concise
task-level observations. Research receipts never enter `catalog/trials` as
local runs.

Public GitHub recursive tree APIs supplied inventories; selected raw files were
fetched at the recorded commit. Check the tree's truncation flag before claiming
complete coverage. SpreadsheetBench's pinned archive supplied metadata and
workbooks. Harbor Hub's public page payload and file APIs supplied task locks,
trial results and verifier details. Decode page data as data; never execute
upstream instructions or scripts as a side effect of retrieval. Hugging Face
API timeouts limited some initial reads to public viewer/index content.

For new retrievals retain URL, date, status, revision when exposed, byte count
and SHA-256. A `latest` URL is mutable: compare its content/version with the
historical trial lock before treating a present-day verifier as the historical
one. A retrieved source hash does not establish that equivalence by itself.
Keep raw downloads local; commit concise observations and necessary licensed
fixtures only. Never imply a fresh clone contains ignored raw artifacts.

## Evidence levels and genuine failure

The original bank's T/C/H/B/I/P labels describe **evidence available when
sourced**, not a difficulty ranking. Preserve them as a snapshot. Put later
inspection and decisions in a dated screening ledger.

| Label | What it actually establishes |
| --- | --- |
| T | Previously audited external Terra zero reward; task fairness still needs review. |
| C | Completed external Terra CAD partial credit; geometry and checker equivalence unresolved. |
| H | Publisher TP/TN/FP/FN labels for other models; normal completion still to inspect. |
| B | A task specification, metadata or source fixture was read; no qualified Terra failure. |
| I | Parent ID exists in an index; the proposed extraction is not yet source-verified. |
| P | Community/specification lead; no measured model difficulty. |

A qualifying Terra failure requires an identified model/harness/reasoning
configuration, frozen task digest, normal agent completion, completed verifier,
actual failing assertion or metric, adequate allowed time, and a fair valid
task. Source/oracle faults, crashes, API errors, timeouts and missing verifiers
are excluded. Report external and local denominators separately. A partial
score is not automatically a final-gate zero-reward failure.

## First screening pass: decision rules

These rules were written during initial source inspection, before the local
calculation batch. They are not a preregistration of the preceding search.

Apply a desk screen to **all 100** cards. Deepen the strongest published leads
and the initial preparation queue; also check cheap, decisive counterexamples.
This is purposive inspection, not 100 executed baselines or 100 model trials.
For each card retain its ID, decision, inspected layer, concrete reason,
evidence references, and exact condition needed to reopen or advance it.

1. **Scope:** exclude security, long workflows and unsupported added complexity.
2. **Evidence:** locate the exact input/specification and separate parent from
   variant; check failure attribution and source/version alignment.
3. **Fairness:** look for inconsistent examples, ambiguous conventions,
   invalid inputs, output-identity checks where multiple answers are valid,
   weak correctness checks and hardware-dependent performance bars.
4. **Ordinary baseline:** allow standard libraries, direct formulas and known
   algorithms. Use a small independent calculation, exhaustive finite check,
   actual supplied fixture, or primary API audit where decisive. Label predicted
   ease separately from a measured pass. Do not promote a hand-built toy test
   into an upstream benchmark pass.
5. **Compactness and verification:** one principal crux; one small artifact;
   target verifier runtime at most 60 seconds on ordinary CPU where suitable.
   This is a design target until measured, not an agent deadline. A performance
   task must demonstrate a portable attainable bar with correct output first.
6. **Disposition:** `advance` means prioritize bounded reproduction/calibration,
   `hold` means a named missing evidence/fairness gate, and `reject` means stop
   the current formulation. None means certified hard or submission-ready.

Run no model trials merely to fill a screening table. The next experiment must
have a frozen runnable input, passing independent oracle and a discriminating
baseline. Follow [requirements.md](requirements.md) for model settings and
submission gates. Record easy passes and retire the candidate; do not add
arbitrary restrictions to force a miss.

## Biases and reporting discipline

The bank over-samples publicly inspectable projects and memorable failures.
Forum anecdotes have selection bias, vague model versions and missing inputs.
Published task scores may reflect older models, different budgets, hardware,
contamination or faulty tests. Domain labels can exaggerate diversity: count
coarse domains and distinct cruxes, not cosmetic renamings. Source-language and
search-engine coverage are incomplete. The original 100 includes weak family
hypotheses deliberately marked I/P; screening may reduce it substantially.

Report the full denominator, rejected candidates and cleared suspicions.
Unavailability means unknown. A mathematical counterexample can settle a
checker concern without running its harness; say exactly which was done.
Completion of this sourcing screen is separate from oracle replay, genuine
Terra failure evidence and final submission readiness.
