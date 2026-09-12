# Contributing to the workshop

Start with [artifact governance](docs/governance.md) and
[submission requirements](docs/requirements.md). The workshop is a research
workspace; passing repository CI does not establish task difficulty or readiness.

Python 3.12, Git, and Make are sufficient for repository checks. No Harbor,
Docker, model credentials, or Python package installation is required.

```bash
make artifacts       # read-only local inventory
# Review and stage only the intended paths with git add.
make check           # staged artifact gate plus offline unit tests
make hooks           # install the repository-local pre-commit gate once
```

`make` uses `.venv/bin/python` when present, otherwise `python3`. Override with
`make check PYTHON=/path/to/python3.12`. The hook checks staged artifacts only;
run the full test suite before committing tooling changes. Hook installation
refuses to replace a different configured hooks directory.

Use focused semantic commits such as `chore(hygiene): ...`, `ci: ...`,
`feat(probes): ...`, or `docs(research): ...`. Keep probe implementation and
measured research outcomes reviewable. Avoid `git add .` in a shared checkout.

GitHub Actions runs `make check` on pushes and pull requests, with monthly
Dependabot updates for action versions. A newly cloned repository must run
`make hooks` to enable its local hook. There is currently no configured Git
remote; hosted CI starts only when the repository is pushed to GitHub.
