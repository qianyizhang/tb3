# Working on tb3-medical

Use Python 3.12, Git and Make for portable checks; they require no Harbor, Docker,
credentials or downloads. Start with [the workflow](docs/workflow.md) and
[artifact ownership](docs/governance.md). The approved [migration design](docs/migration/tb3-medical.md)
records the architectural decisions.

```sh
python3.12 scripts/med list --kind group
python3.12 scripts/med list 'landmark'
python3.12 scripts/med show anatomical-landmarks-br040
python3.12 scripts/med validate
make check PYTHON=python3.12
```

Inspect status and other tasks before editing. Stage explicit paths and use
focused Conventional Commits. `make check` includes the staged artifact gate,
offline tests and portable presentation checks. A dirty experiment owned by
another task must not be staged to make your checks pass. Validate the intended
Git tree independently before closeout. `make hooks` installs the local staged
artifact gate and refuses to overwrite another configured hooks directory.

The CLI distinguishes inspection from actions. Only `run` launches a trial;
`prepare --execute` runs a declared authoring command. Neither is part of CI.
New experiments start disabled until inputs, reference validity, licensing,
independent scoring and controls are reviewed. Packages are drafts until the
then-current target requirements are explicitly checked.
