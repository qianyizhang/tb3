# Harder candidate screen — 2026-09-12

Purpose: find credible candidates worth later Sol trials by observing Terra/high solve or fail real tasks. A Terra failure does not establish a Sol failure. The earlier cache probe passed and stays unchanged as calibration.

## Current scope: non-security, short horizon

The user explicitly reinforced these constraints on 2026-09-12:

- **Stay away from security tasks.** Do not select vulnerability discovery,
  exploitation, authentication/authorization, sandbox escape, protocol attacks,
  or other security-focused work. Do not resume the stopped security research
  or launch adversarial trials in this survey. Historical evidence stays intact.
- **Go for hard but less complex tasks, especially short-horizon tasks.** Prefer
  one concrete mathematical, scientific, data, or hardware invariant; one small
  deliverable; a compact fixture; and verification in seconds. Difficulty should
  come from a conceptual crux, not repository size, lengthy workflows, obscure
  setup, arbitrary restrictions, or reduced reasoning time.
- Diversify both field and task type. A new language around another compact
  bug fix is not sufficient diversity. Screen constructive certificates,
  reconstruction, optimization, and numerical correctness as well as repairs.

The [benchmark-backed survey](research-benchmark-backed.md) now owns selection.
The [short-horizon survey](research-short-horizon.md) records a completed bounded
screen and its dispositions. The existing 1,800-second diagnostic allowance
remains; a short task horizon does not mean manufacturing timeout failures.

## Predeclared procedure

1. Screen incident reports and executable specifications for interacting mechanisms, efficient reproduction, and overlap with the pinned TB3 inventory.
2. Implement a small number of materially distinct candidates. Keep source provenance and complete public behavior contracts. Avoid slow builds, arbitrary restrictions, and hidden requirements added after seeing a model solution.
3. Independently review the verifier; run oracle and nop in real Docker. Freeze each task tree before the model sees it.
4. Run one fresh Codex Terra/high trial per ready candidate, with 1,800 seconds available for reasoning. Inspect the completed verifier and trajectory. Infrastructure failures and timeouts are excluded.
5. For a genuine failure, reproduce the failing behavior independently and check specification fairness. Then use a fresh same-snapshot Terra trial to test whether the failure repeats. Retain all passes, failures, and excluded attempts.
6. Consider Sol only after a substantive, reproducible failure survives that review. These diagnostic runs do not satisfy the assignment's six final trials.

All model trials use Harbor 0.14, Docker, ChatGPT subscription authentication, and the explicit local proxy documented in [setup.md](setup.md). Oracle/nop use Harbor 0.18. Research/authoring subagents use Terra/high. Raw trajectories stay under ignored `runs/`; sanitized summaries and failure examples are retained in this repository.

## Candidate decisions

| Direction | Evidence and decision before trials |
| --- | --- |
| Nested Dremel record assembly | Implement a pure-Python repair probe at the decoded leaf-stream boundary: repeated ancestors, optional parents, sibling alignment, and independent page boundaries. Apache documents this reader boundary; real readers have failed on nested schemas. The interface deliberately receives decoded levels rather than whole Parquet files. It is an incident-inspired extraction, **not** a reproduction of a specific upstream patch. Difficulty remains unknown. |
| Ninja dynamic dependencies | Actual Ninja scheduler regression reproduced, oracle1/nop0, Terra/high pass. Retire this snapshot. Public-fix discoverability remains a concern for any later promotion. |
| SQLite correlated EXISTS | Actual 3.53.0 optimizer regression reproduced against3.53.1, oracle1/nop0, Terra/high pass. The accepted repair is compact; retire this snapshot. |
| Clipper2 Rust PolyTree joins | A firsthand porting account identifies three interacting horizontal-join mistakes. The historical parent fails9/14 upstream tests; the fixed version passes14/14 in Docker. Pickup review corrected order/normalization grading; final oracle1/nop0 and Terra/high reward1 completed. Retire this snapshot. |

## Additional searched leads

Primary sources retrieved 2026-09-12; these records distinguish source reports from local reproduction.

| Source | Reported behavior | Disposition |
| --- | --- | --- |
| [Apache nested encoding explanation](https://arrow.apache.org/blog/2022/10/08/arrow-parquet-encoding-part-2/) and [Parquet format](https://github.com/apache/parquet-format) | Definition/repetition levels encode parent presence and repeated ancestry separately from leaf values. | Specification basis for the nested-assembly probe; independent generation starts with original records, not the oracle's decoder. |
| [fastparquet #373](https://github.com/dask/fastparquet/issues/373) | A Spark nested schema exposes the distinction between a null struct and a null member; maintainers describe the reader's limited support. | Firsthand motivation, not a reproduced bug or claim that current releases still fail. |
| [parquet-java #3672](https://github.com/apache/parquet-java/issues/3672) | A contributor gives valid Parquet fixtures that fail through Avro-backed row reading, including nested lists and projection mismatches. | Supports the need for a native nested reader. Full Java stack deferred to keep setup small. |
| [pyelftools #564](https://github.com/eliben/pyelftools/issues/564) | Relocatable ELF can contain multiple same-name DWARF sections; relocation association uses section indexes. | Interesting real binary-layout challenge; deferred because a compact, licensed, independently expected fixture still needs work. No trial. |
| [Serenity #26773](https://github.com/SerenityOS/serenity/issues/26773) | Concrete tar inputs demonstrate fixed-width string overreads and allocation before body validation. | Reject this round: direct fixes appear narrow; a Serenity build would add cost without demonstrated reasoning difficulty. No local reproduction. |
| [DuckDB #21592](https://github.com/duckdb/duckdb/issues/21592) | A window rewrite incorrectly applies full-partition aggregation to a ROWS frame. | Reject direct version: the report identifies the missing guard; likely a small repair, while building DuckDB adds overhead. |
| [DuckDB #22075](https://github.com/duckdb/duckdb/issues/22075) | Parallel dynamic bloom-filter pushdown can undercount a grouped probe-side join; several configuration changes avoid it. | Deferred: unstable parallel reproduction and easy configuration workarounds weaken a fast, fair verifier. |
| [DuckDB #24398](https://github.com/duckdb/duckdb/issues/24398) | An IN-list rewrite can change a documented insertion-order behavior. | Deferred: needs a precise workload contract; adding explicit sorting may legitimately solve the user problem. |

Build and runtime research details are recorded in [build candidates](research-build-candidates.md) [runtime candidates](research-runtime-candidates.md), and [geometry candidate](research-geometry-candidate.md). No source report in this document is evidence of a local model failure.

## Results

| Probe | Docker controls | Terra/high | Decision |
| --- | --- | --- | --- |
| `dremel-assembly` | Oracle1, nop0; both about24s, no exception | **Pass**, reward1, no exception; 320.557s total, 255.573s agent | Retire this snapshot from difficulty selection. All 16 verifier invocations completed; stdout is an aggregate success, not structured per-case evidence. |
| `ninja-dyndep` | Corrected oracle1 in49s, nop0 in37s | **Pass**, reward1, no exception;379.766s total,308.716s agent | Retire. First two oracle failures were verifier packaging/permission faults, retained separately. |
| `sqlite-exists` | Corrected oracle1 in37s, nop0 in36s | **Pass**, reward1, no exception;204.778s total,133.447s agent | Retire. Initial oracle failure was a missing patch tool, not a model failure. |
| `clipper-polytree` | Final oracle1 in49.916s, nop0 in26.597s, no exceptions | **Pass**, reward1, no exception;494.711s total,421.371s agent | Retire. Pre-trial grading defects were fixed; no additional Sol trial. |

[Sanitized trial summary](evidence/harder-trial-summary.json) retains this earlier screen's completed attempts. The later geometry and homology attempts have separate linked summaries. The canonical runner hashes are in each `*-pilot-freeze.json`; their superseded pre-trial snapshots remain alongside them. No genuine Terra failure has been observed yet. No Sol/Opus run has started.

The Dremel trajectory implements a general schema-driven decoder, retains repetition positions across pages, merges sibling fields, and passes the supplied example. It does not obtain an online solution. A final `git diff` command fails because the image is not a Git checkout; this incidental command failure did not interrupt the agent or verifier. Its aggregate pass is valid. Promotion-only verifier improvements (immutable artifact copy and a global runtime guard) remain unnecessary for this retired difficulty snapshot; it is not adversarially qualified.

SQLite Terra repairs the containing SELECT's LIMIT/OFFSET guard and passes the normal-versus-disabled-optimizer comparisons. It does not need the oracle's entire two-hunk patch; the verifier accepts equivalent behavior. Ninja Terra repairs graph.cc and graph.h and adds local regression coverage. Its optional CMake attempt fails because CMake is absent, then the supplied bootstrap build succeeds. Both are completed model passes, not infrastructure failures.

The Ninja compiler-download slowdown was isolated from task difficulty: stale authoring build clients held an old non-proxy APT operation alive. After stopping confirmed owners and rebuilding with temporary proxy arguments, the unchanged image built in56.851s (10.1s Ninja bootstrap); proxy-free cache reuse then completed in0.084s. No proxy address was baked into task Dockerfiles. See the [network diagnostic summary](../runs/ninja-network-diagnostic-summary.md).

## Geometry pickup and next numerical lead

The non-security pickup completed the fifth valid Terra/high pass. See the
[geometry trial summary](evidence/clipper-trial-summary.json),
[grading review](geometry-review.md), and [pickup record](archive/operations.md#geometry-pickup).
The geometry semantic verifier covers three base geometries and one translation;
its historical test suite is diagnostic. No final qualification claim follows.

At the geometry pickup, the next lead was
[barycentric interpolation](research-numerical-candidates.md): limited execution
of historical numerical blocks showed that the published constructor fix leaves
incremental-node weights inconsistent. The short-horizon follow-up has now
confirmed this through unchanged full historical modules and their public class
API with real SciPy helper imports. It remains a source reproduction, not a
historical full-package build or model result; a complete repair oracle is next.

## Diverse short-horizon follow-up

The [eight-direction survey](research-short-horizon.md) explicitly excludes
security tasks and favors compact conceptual difficulty. A new constructive
topology task, `homology-basis`, passed matching Docker oracle/nop controls and
Terra/high: reward 1, no exception, 43/43 cases, 399.743 seconds total. Retire
that snapshot. See the [summary](evidence/homology-trial-summary.json) and
[trajectory review](../catalog/analyses/homology-calibration.md). Current totals:
six valid Terra passes, zero genuine failures, and two earlier infrastructure
attempts. No new Sol/Opus or adversarial trial was run.

## Benchmark-backed search supersedes the next-source recommendation

The user requested a harder search after six local passes. The
[new survey](research-benchmark-backed.md) found published Terra failures with
completed verifier assertions on compact scientific tasks. Start with these
measured failures rather than another plausible incident-inspired repair.
External evidence remains separate from all local trial counts and freezes.
