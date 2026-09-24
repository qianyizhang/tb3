# Coding style

Use explicit data contracts, ordinary functions and small modules with clear
owners. Share stable infrastructure and scientific contracts; keep experimental
choices with the experiment. These rules govern new and changed maintained code,
not a mechanical rewrite of historical artifacts.

[Architecture](architecture.md) owns component boundaries;
[repository layout](repository-layout.md) owns file placement;
[CONTRIBUTING](../CONTRIBUTING.md#checks) owns commands and checks.

## Ownership and reuse

| Code | Responsibility |
| --- | --- |
| `src/tb3_medical/` | Shared records, storage, workflow, runtime adapters and presentation projection. Never import experiment or historical authoring code. |
| `groups/<group>/methods/` | Maintained scientific methods shared within a group, with explicit inputs, outputs and conventions. |
| `groups/<group>/experiments/` | Condition-specific transformations, selection rules, thresholds, prompts and analysis. Real computation may remain here. |
| `presentation/frontend/` | Browser components, state and rendering. Python owns the generated payload contracts. |
| Standalone runners and frozen history | Preserve independent execution and retained bytes; duplication here can be intentional. |

Share behavior when a future fix should affect its callers together. Scientific
extraction needs matching semantics, tests and a dependency story that preserves
past experiments. Similar code alone is insufficient: avoid helpers with branches
for experiment names or many flags. Do not import another experiment's private
implementation.

Import from the owning module, such as `storage` for publication and path policy.
Keep maintained entry points focused on arguments, dispatch and output. Keep
types with their feature, rather than a universal `models.py` or a file per class.
Use the explicit `ExperimentMethod` adapters when needed; this workbench does not
need a workflow engine, plugin registry, universal experiment base class or a
second service layer under `scripts/`.

## Data contracts

| Value | Default |
| --- | --- |
| Workbench-owned serialized schema or normalized external result | Pydantic `BaseModel` |
| Internal computed value, operation result or plan | Standard dataclass |
| Existing browser payload | Python `TypedDict` and generated TypeScript |
| Genuine key-to-value collection | `dict[K, V]` or read-only `Mapping[K, V]` |
| Unparsed external value | `object`; narrow before use |
| Extensible historical JSON/TOML record | Existing `Document` and its owning validator, until a scoped migration |
| Stateful resource with lifetime or identity | Ordinary class |

Prefer named fields over heterogeneous positional tuples. Use `Literal` or enums
for closed choices and discriminated unions when cases have different fields.
Reuse the codes in [vocabulary.json](../src/tb3_medical/vocabulary.json); do not
invent competing statuses. Keep scientific units, axis order and coordinate
frames visible in names and documentation.

A model already serving an operation does not need a duplicate dataclass. Frozen
values are useful, but nested lists, mappings and arrays remain mutable: use
immutable members or document who may mutate them. Dataclasses do not validate
field types at runtime; scientific invariants still belong to their computation.

## Parse once, project explicitly

```text
external bytes -> normalization and validation -> typed operations -> output projection
```

Keep raw evidence separate from normalized values. After normalization, use named
fields instead of repeated dictionary probes and fallback defaults for required
fields. Keep `Any` and dynamic documents at actual extensibility boundaries; casts
and aliases must not conceal an unmigrated contract.

- **Schema policy:** prefer `extra="forbid"` for new closed models. Inventory
  existing fields before migrating extensible records; retain accepted extension
  data and distinguish absent values from explicit nulls.
- **Coercion:** choose strictness deliberately, particularly for IDs, flags and
  counts. Preserve accepted historical inputs during a refactor. Tightening input
  acceptance is a separate behavior change with tests.
- **Effects:** validators check structure and invariants. File access, hashing,
  downloads, subprocesses and publication belong to explicit operations.
- **Updates:** `model_construct()` bypasses validation and `model_copy(update=...)`
  does not validate updates. Revalidate when the operation requires it. See the
  [Pydantic model API](https://docs.pydantic.dev/latest/api/base_model/).
- **Serialization:** pass models between internal operations and project at the
  persistence, digest or presentation boundary. Avoid model → dict → model chains.
  Preserve field names, nulls, list shapes and encoding wherever they affect
  consumers or identity.

Declare runtime dependencies in both `pyproject.toml` and `uv.lock`. Workbench
Pydantic models must not become dependencies of the copied reproduction runner or
separate solver runtimes. Keep browser contracts generated from their current
Python owner until a separately scoped migration removes complexity.

## Functions and effects

Prefer focused functions for transformations and orchestration. Name the effect:
`parse_trial`, `load_records`, `project_records`, `write_evaluation`. Avoid vague
new `process`, `manager`, `common` or `utils` surfaces.

Public functions have explicit parameter and return types. Normalize paths near
ingress, keep `argparse.Namespace` in the CLI, and use keyword-only options for
behavior-changing flags or easily confused arguments. Introduce a configuration
value only when its fields form a useful concept.

Separate computation from I/O where it clarifies ownership and permits direct
tests. Catch expected failures at meaningful boundaries, retain exception causes
and add context. Do not hide programming errors behind broad handlers or turn
missing evidence into successful empty results. Imports must not launch work,
parse arguments, mutate evidence or require local medical data.

## Formatting and verification

Use the repository's Ruff formatting and lint rules, strict mypy and existing
frontend tooling; do not maintain competing formatting rules or tool stacks.
Review one coherent slice with its direct consumers and tests. Run a baseline
before editing and the [required checks](../CONTRIBUTING.md#checks) afterward.
Add behavioral witnesses for changed boundaries, not tests that mirror trivial
implementation details.

Protect classifications and warnings, latest-observation selection, collection
idempotency, path policy, exclusive publication, hashes, accepted historical
fields, CLI behavior and generated payloads. A replay stays a separate observation.
For identity-sensitive refactors, retain synthetic baseline fixtures with their
source revision; do not regenerate expected outputs merely to pass a check.

Do not consolidate different policies just because helpers look similar:
`workflow.tree_digest` uses compact JSON while `harbor.digest_json` uses default
separators; `storage.inside` and `harbor.workspace_path` accept different paths.
Frozen evidence and standalone copies are not a formatting backlog. Follow
[governance](governance.md) for retained bytes and concurrent ownership.
