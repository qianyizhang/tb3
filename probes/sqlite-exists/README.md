# SQLite EXISTS/OFFSET feasibility probe

This is an untested authoring probe from the SQLite 3.53.0 regression reported
at https://sqlite.org/forum/info/2c43f36255a630e3. The environment contains
the actual 3.53.0 amalgamation (`sqlite3.c`, `sqlite3.h`, and `shell.c`) from
the official GitHub mirror tag `version-3.53.0`.

The forum report identifies the first bad canonical check-in as
`aa54d7a0ca03a4df516f25e66ff3c4801be07a7b`. The upstream correction appears
in 3.53.1 and canonical check-in `1dd3c6a5e5`; the source comparison changes
`src/select.c` and `test/existsexpr.test`.

Native evidence must distinguish the broken 3.53.0 output from the patched
reference before Docker, Harbor, or agent trials are recorded. The task remains
a feasibility probe until an independent reviewer assesses whether the repair
is too direct for TB3.
