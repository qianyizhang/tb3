# TB3 task-idea research ledger

Retrieved 2026-09-12. This records the initial shortlist and its completed cache calibration. “Estimate” means design judgment, not measured result. The active follow-up is the [harder candidate screen](harder-screen.md).

## What the sources establish

| Source (firsthand / primary) | Factual record | Design inference for this shortlist |
| --- | --- | --- |
| [TB author discussion #224](https://github.com/harbor-framework/terminal-bench/discussions/224) | **Fact:** a TB reviewer argues for authentic, legible work, outcome-based tests, an oracle that investigates, and explicit reward-hack testing. | Use a compact incident-shaped goal, hidden behavioral fixtures, and an oracle that diagnoses the supplied code rather than writing a magic patch. Do not manufacture difficulty from format, permissions, or slow builds. |
| [TB issue #1429](https://github.com/harbor-framework/terminal-bench/issues/1429) | **Fact:** the reporter demonstrated that the separate verifier could still award a task after unrelated files in the agent container were deleted; the agent container is gone before verification. | Grade only declared artifacts and their behavior. Do not make unverifiable claims about preserving arbitrary agent-container state. |
| [TB CDC proposal #1467](https://github.com/harbor-framework/terminal-bench/discussions/1467) | **Fact:** the proposal specifies idempotency and primary-key migration; a reply demonstrates a functionally passing full in-memory rebuild that the reviewer considers unacceptable for a production CDC pipeline. | A stateful-pipeline idea needs an observable incremental/provenance contract, or a hidden stream alone may permit a semantically shallow rebuild. This is a warning, not evidence that every CDC task is weak. |
| [Lean issue #13449](https://github.com/leanprover/lean4/issues/13449) | **Fact:** the reporter gives a self-contained reproduction where Lake replays a cached result after a text-file input changes; a fresh build exposes the failing test. The report describes CI cache reuse as amplifying the problem. | The incident supports a small cache-soundness task: fingerprints must include declared non-source inputs and invalidate on both byte changes and membership changes while unrelated targets remain cache hits. |
| [Go issue #71988](https://github.com/golang/go/issues/71988) | **Fact:** the Go security issue says HTTP/1 chunked encoding requires CRLF, while the implementation accepted bare LF in chunk-size lines; it identifies a request-smuggling composition risk and CVE-2025-22871. | A narrow byte-stream parser repair can be real and deterministic if it proves message boundaries, rejected malformed frames, valid trailers, and pipelined-byte preservation. It must not be reduced to a single regex check. |
| [SQLite WAL-recovery forum thread](https://sqlite.org/forum/info/d33843ff0dfdf9fd) | **Fact:** a user reports WAL recovery notices after multi-process use; SQLite contributors explain that recovery of WAL frames is normally a warning and can follow a crash/power/storage failure, and that a later open needs write access to finish recovery. | A snapshot/export task should distinguish a valid WAL-backed database from corruption. The task can require a standalone, read-only snapshot without assuming that a recovery notice means data loss. |
| [Bazel issue #9213](https://github.com/bazelbuild/bazel/issues/9213) | **Fact:** the reporter and a coworker hit a stale-cache build failure after an APT update; a clean expunge repaired it, while a fresh clone worked. The report calls it cache poisoning but cannot reduce it from a clean state. | This corroborates the paid-work reality of cache invalidation, but its environment-dependent reproduction makes it a poor direct TB fixture. Use the Lean-style deterministic reproduction instead. |
| [Git’s maintained racy-git regression test](https://github.com/git/git/blob/master/t/t0010-racy-git.sh) | **Fact:** upstream Git maintains dedicated “racy git” trials, reflecting the case where filesystem metadata cannot safely prove content freshness. | A simulated worktree-status cache is possible, but modeling filesystem timestamp resolution risks turning the task into a synthetic corner case; keep it below the primary choices. |

The [SQLite WAL documentation](https://www.sqlite.org/wal.html) and [SQLite recovery documentation](https://www.sqlite.org/recovery.html) are supporting specification sources, rather than additional incident entries. They are useful when turning the WAL idea into a fixture.

## Ranked candidates

Scores are 1–5 (higher is better) except cheat risk. “Fast test” is a rough verifier/oracle runtime after the image exists; it excludes Docker build and any later agent trial.

| Rank | Candidate | Realism | Meaningful difficulty | Fast oracle/verifier feasibility | Cheat risk | Fast test estimate | Why it belongs here |
| ---: | --- | ---: | ---: | ---: | --- | --- | --- |
| 1 | **Declared external-input cache repair — feasibility only** | 5 | 2 | 5 | Medium, controllable | 3–8 s | A working mini build runner wrongly keys only source code. The repair must retain cache hits for unchanged/unrelated targets but rebuild when a declared file changes, is added by a glob, or is deleted. That is the same failure shape as Lean’s report, with a deterministic local fixture, but the direct diagnosis and small patch put it below the TB3 difficulty bar. |
| 2 | **Strict HTTP/1 chunked-frame parser repair** | 5 | 4 | 5 | Low | <1 s | Patch a small proxy/parser so its byte cursor cannot desynchronize across valid chunks, extensions, trailers, malformed bare LF, and a following pipelined request. The source is a real public security bug, and a pure byte oracle can be exhaustive for a bounded grammar. |
| 3 | **SQLite WAL standalone snapshot exporter** | 5 | 3 | 5 | Low–medium | 1–3 s | Repair a supplied exporter that copies only the main database and silently loses committed WAL-resident rows. Hidden databases can hold readers that block checkpointing; grading opens the produced snapshot read-only and checks query results plus absence of sidecars. |
| 4 | **Racy-worktree status-cache repair (simulated metadata)** | 3 | 4 | 5 | Low | <1 s | Repair an application-side index whose stat shortcut misses a content replacement with identical recorded metadata. Hidden tests use deterministic synthetic stat records, avoiding host timestamp flakiness. It has genuine Git lineage, but the simulation weakens authenticity. |

## Similarity screen against current merged task names

This screen started from the local terminal-bench tree (`git ls-tree --name-only HEAD tasks/`). The full current instructions for `batched-eval-parity` and `wal-recovery-ordering` were then read from the local Git object store. The selected cache probe has no direct name match and is materially narrower than the adjacent systems tasks below.

| Existing task name | Similarity risk to external-input cache repair | Boundary that keeps the candidate distinct |
| --- | --- | --- |
| `wal-recovery-ordering`, `mvcc-lsm-compaction`, `live-database-cutover` | Low | `wal-recovery-ordering` specifically requires concurrent durable-LSN-prefix acknowledgment, crash snapshots, detached mutable values, and order-independent recovery. The candidate is build-result freshness over declared filesystem inputs, with no recovery, compaction, migration, or live service. |
| `distributed-dedup`, `payments-pipeline-fix`, `session-window-debug` | Low | Those names indicate event/stream correctness. The candidate’s only state is a local cache manifest and its observable hit/rebuild behavior. |
| `pretrain-shard-corruption` | Low–medium | Both can involve stale or incorrect data, but this task never repairs a dataset or trains/evaluates a model. It repairs provenance of a deterministic build input set. |
| `batched-eval-parity` | Low | The task repairs local-model evaluation so packed and padded batches agree across few-shot resolution, scoring spans, calibration, generation stops, metrics, input order, and prefix-cache reuse. The probe only keys deterministic filesystem inputs; it has no model, batching, scoring, or evaluation-parity behavior. |

### Top recommendation: declared external-input cache repair

Build a small, preexisting Python build runner with two or three targets. Each target has source, a declared file/glob input set, target-local configuration, and a deterministic output. The broken cache metadata records only the source/config digest. The user-visible symptom is a stale successful output after an input data file changes; the agent is told the cache contract, including that unchanged and unrelated targets must still be cache hits. The correct repair needs a stable digest over the declared input **path set and bytes**, with an explicit missing/deleted-file representation.

The hidden verifier should copy the submitted artifact into a fresh scratch project and exercise: unchanged rebuilds, byte mutation, glob addition, glob deletion, unrelated-file mutation, and two targets sharing one input. It should compare outputs to a fresh reference build and assert the externally visible per-target `hit`/`rebuilt` result. The implemented probe also freezes the prior cache and output artifacts before an expected hit, so its unprivileged runner cannot pass by rewriting the artifact while claiming reuse. Keep hidden fixtures in the verifier image and re-execute the artifact; do not grade source shape or trust a report file.

**Why first for a feasibility probe:** it has an authentic incident, a compact and deterministic fixture, and a fast no-build verifier. It is the least likely choice to spend hours on before learning whether the core behavior is sound. It is not a TB3 difficulty candidate on its own: a competent engineer can trace the omitted digest inputs and make a small direct repair. The likely authoring risk is overspecifying the cache API; write the contract in user terms, then make the oracle inspect the existing runner and repair it by the same path an engineer would take.

### Difficulty calibration after the probe

The implemented probe should remain a verifier and setup check. Its extra behavioral cases protect the contract; they do not create meaningful TB3 difficulty. Do not add contrived timestamps, hashes, formats, or random hidden edge cases in an attempt to make it harder.

The next candidate needs an authentic multi-step diagnosis. A credible shape would be a real build/package incident where a generated interface or packaging manifest has stale provenance across at least a generator, a downstream consumer, and an incremental cache, while an independent fixture can still run in under a minute. The agent would need to distinguish bad dependency discovery from a stale cache entry and preserve an observable incremental-work contract. This direction is **not yet promoted**: the two scoped searches for a Ninja/generated-header or packaging-provenance incident did not yield an independently inspectable primary reproducer during this pass. Keep the current cache idea feasibility-only until that source and a human-realistic failure chain are in hand.

### Candidate-specific cautions

- **HTTP parser:** keep the task a repair to a realistic existing parser, rather than “write HTTP/1.” Validity tests must cover byte consumption and a second pipelined message. Do not present it as a security exploitation task or expose a real service.
- **WAL snapshot:** use SQLite’s standard library and a frozen database generator. The goal is a portable snapshot with correct query results, not a byte-identical `.db`; byte identity would reject legitimate implementations.
- **Racy worktree cache:** only pursue after reviewers agree that the synthetic metadata fixture still reads as paid engineering work. A host-filesystem reproduction is too fragile for TB3.

## Rejected for this pass

| Rejected direction | Reason |
| --- | --- |
| Primary-key-changing SQLite CDC mirror | The TB proposal itself shows that a full replay/rebuild can satisfy a naive final-state oracle while violating the intended incremental production behavior. It also estimates 5.5 expert hours, contrary to the goal of fast idea validation. Revisit only if a concrete incremental/provenance obligation is naturally observable. |
| General SQLite corruption salvage | SQLite’s recovery tooling addresses a broad class of damage. A tiny fixture tends to become either a contrived byte puzzle or an underspecified miniature recovery engine; neither is a good first TB3 build. |
| Direct Bazel/apt-cache reproduction | The firsthand report explicitly cannot reproduce from a clean state and depends on host toolchain/cache history. That is unsuitable for a stable, portable benchmark image. |
| Git internals against the installed system Git | Real Git regressions are valuable, but pinning behavior across Git versions and filesystem semantics would make the task environment-sensitive. The simulated status-cache candidate is only a fallback. |

## Measured pilot result

The frozen cache probe completed a real Harbor/Docker Codex run with `openai/gpt-5.6-terra`, high reasoning, on 2026-09-12: **reward 1, 10/10 verifier cases, no exception**, approximately 145 seconds including setup and teardown. Terra added the missing path/byte fingerprint and exercised visible mutations. The prior DNS and direct-ChatGPT transport failures are excluded from model outcomes. See [trial summary](evidence/trial-summary.json) and [ledger](ledger.md).

Disposition: retain this as a setup/calibration fixture; do not promote it to a TB3 difficulty candidate or spend Sol/Opus trials on it. The other ideas are untested design proposals, not demonstrated hard tasks.
