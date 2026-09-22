# Exports and submission ownership

Medical capability research is the active purpose of this repository. Exporting
selected work produces a research draft; submission qualification is a separate
assessment against a named, dated target profile. The closed interview's trial
matrix and failure-first selection rules are not gates on ordinary research.

## Build an independent research draft

Recipes select immutable Git bytes or explicit local artifacts with hashes. Restore
only the selected inputs and choose a destination that does not already exist:

```sh
uv run med export exports/recipes/landmarks-mri-v2.json /fresh/destination
uv run med verify-package /fresh/destination
python3.12 /fresh/destination/replay.py
```

The [MRI recipe](../exports/recipes/landmarks-mri-v2.json) includes task files,
source notices, two saved model outputs, oracle output and standalone replay code.
Its replay needs neither the source checkout nor NumPy, Docker, network or inference.
Package verification checks the declared executable bits on POSIX systems as
well as the exact file inventory and content hashes; other platforms explicitly
report that executable modes were not checked.
The original implementation receipt is indexed in the
[recovery manifest](../archive/manifest.json) as `docs/migration/native-closeout.md`. The package retains a historical mutable Docker tag, so saved-output replay
is not proof of a rebuilt execution environment.

Flagged evidence can be included in a research draft only with `--include-flagged`;
its reasons and scope travel with the package. Every export begins as a draft.
A successful export, verification or control run does not promote it automatically.

## Qualification and handoff

Before claiming submission readiness, check the target's then-current task format,
licenses/access, authorship requirements, runtime/profile and required trials.
Record what was checked and what remains incomplete in the destination package.
The [2026-09-12 requirements snapshot](archive/README.md#retired-guidance-and-recovery) is historical reference,
not a current upstream specification. This documentation audit did not refresh
external submission requirements.

During preparation, the recipe and lineage record belong here. After an explicit
handoff, the destination is independently maintained; later fixes require deliberate
backports rather than automatic synchronization. Never overwrite an existing export.

The existing `dicom-anatomy-audit` sibling repository has separate ownership.
Its README, evaluation records and evidence own package-specific commands, current
selection and qualification. It is not included in this clone, and a sibling path
must be resolved from the owner's checkout, not assumed relative to a Codex worktree.

The former contents of this page were a dated **case-32 handoff**, already superseded
by later anatomical work. Exact original bytes and recovery locations are retained
as `docs/submission.md` at commit
`f5b2ced2d85e13e325bf535d444b574fedd9dd39` in the
[archive manifest](../archive/manifest.json). See [recovery instructions](../archive/README.md).
Those reported checks and package commits are not a verified current status of the
sibling repository. Current medical findings belong to the
[anatomy-audit group](../groups/anatomy-audit/README.md).
