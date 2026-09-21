Source: `docs/research-rounds/BR-042-v4-plan.md`; original SHA-256: `a83c7960d30f72eb54b8ba446bcf2aa53b72bcbc09db99bffd5553d4d3ed1dfb`.
Repository source locators below are provenance; they are not required runtime inputs.

# BR-042 V4 — bounded all-vessel reconstruction, Astra/xhigh

Status: prepared and offline-checked; **not launched**. User requested a committed checkpoint before repository restructuring and an explicit go-ahead before this experiment. No model or Docker control job was started during preparation.

## What changes

The public instruction (repository source locator: `../../probes/vessel-geometry/authoring/br042_v4/instruction.md`) keeps coronary trees first, including branches without dedicated categories, then major noncoronary trunks and named branches. Exhaustive fine peripheral pulmonary arborization, tiny unnamed tributaries and terminal twigs are outside the required workload. This defines scope without claiming those vessels are clinically irrelevant.

Generic category rules clarify zero/one/multiple courses per category, distinguish geometric bifurcation from category change, and require origin/course/territory evidence. No case-specific branch count, location, failure feedback, tracing code or extraction recipe is supplied. The model chooses its method. A valid preliminary answer and concise method/inventory are required by 30 minutes; approximately the final 10 minutes are reserved for validation and delivery.

Broader vessel reconstruction remains an explicit human-review outcome. Clinical relevance is not reduced to the 14 benchmark categories. Automated coronary geometry and labeling, broader image support and anatomy, and execution/completion are reported separately.

## Frozen comparison and interpretation limits

Same native CTA, private reference, evaluator and source notice as V3; only public instruction and task version identifier change. One fresh Astra/xhigh attempt, one hour agent wall time, 2 CPUs, 8 GiB RAM, no GPU, no retries. Fresh oracle/no-op controls must complete successfully on the identical task before model exposure. Setup/transport failures remain infrastructure evidence; partial artifacts are not normal-completion scores. Setup and verifier time are separate from agent wall time, so total command duration can exceed one hour.

This is an outcome-informed revision on a previously used public development case, not held-out capability estimation. Compare against V3 as a changed-spec experiment, not a pure rerun or isolated reasoning-effort comparison. Do not give the target model author-side reports or case-specific review findings.

**Unresolved naming policy:** generic category cardinality is clarified, but V4 does not invent or assert universal PDA daughter-label inheritance. The source protocol permits selected bifurcating and multiple courses; it does not independently adjudicate every ambiguous course in this case. See [ImageCAS-X Appendix B](https://arxiv.org/html/2608.30404v1#A2). No GT labels or scores were changed. A future formal inheritance policy requires unrelated-case validation and its own version. Flag uncertain reference/identity disagreements separately rather than declaring them clinically wrong solely from label mismatch.

## Ready command, after user go-ahead

From the repository root:

```bash
.venv-br030/bin/python probes/vessel-geometry/authoring/br042_v4/run.py --run
```

Without `--run`, the same command performs offline readiness checks only. It validates task/config hashes, checks local Harbor executable presence and runs private oracle, all-zero-label and split-same-category scoring controls. These checks do not contact the model or launch Docker and do not certify live provider/network health. Repeated readiness checks leave frozen inputs unchanged.

The launch command runs fresh Docker oracle and no-op controls, stops before the model if either fails, and then launches exactly one fresh `openai/gpt-6-astra` / `xhigh` attempt. It creates an exclusive event journal, refuses existing jobs, and provides no automatic retry or setup-recovery loop. A failed launch needs explicit diagnosis and a separately authorized new attempt, not rerunning this command.

## Local dependencies and migration handoff

- Frozen task: `runs/br042-all-vessels-v4/tasks/all-vessels/`.
- Local launch configs: `runs/br042-all-vessels-v4/configs/`; host routing/auth setup retained from the earlier functioning harness. Configs are permission 0600 and stay local; no credentials are committed.
- Event journal after launch: `runs/br042-all-vessels-v4/events.jsonl`; phase logs alongside it.
- Job names: `br042-all-vessels-{oracle,nop,astra-xhigh}-v4-attempt1` under `runs/`.
- Frozen task/config digests: freeze (repository source locator: `../evidence/br042-v4-freeze.json`); public-surface audit: input audit (repository source locator: `../evidence/br042-v4-input-audit.json`).
- Local runtimes: `.venv-br030` (Python 3.12 plus imaging/scoring dependencies), `.venv` (model Harbor), `.venv-validation` (control Harbor), Docker/Colima and existing authorized provider setup.
- Preparation source: `prepare.py` in the same authoring directory. It requires the retained V3 task and V2 local harness config, refuses overwriting V4, and never launches jobs. Do not reprepare the existing freeze.

Git preserves the authoring code, instructions and concise evidence, **not** ignored raw runs, CTA data, frozen local task directories or environments. The restructure must preserve those local dependencies and historical runs. If paths change, update the author-side launcher/manifest deliberately and rerun readiness before the go-ahead; do not modify frozen public/reference bytes or silently regenerate prior evidence.

## Review after completion

Use the unchanged evaluator for coronary metrics. Inspect all-vessel outputs against the source CTA, report name/connection/extent uncertainty, and review deadline delivery plus executable-code reproducibility. Record the preliminary checkpoint from retained trajectory evidence if available; lack of a retained intermediate checkpoint must be reported as unverified rather than inferred from final files. Inventory self-report alone does not establish clinical completeness. No broad-vessel correctness score is claimed without independent annotation/adjudication.
