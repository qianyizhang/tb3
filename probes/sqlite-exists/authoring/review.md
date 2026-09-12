# Authoring review

The environment is the actual SQLite 3.53.0 GitHub-mirror amalgamation. Native
builds witnessed the forum incident: the broken source returned `2` matching
rows and `1` final LIMIT/OFFSET row; the 3.53.1 source returned `2` and `0`.

The upstream correction is only two compact hunks in `existsToJoin`: do not
apply EXISTS-to-JOIN to a parent SELECT with OFFSET, and do not recursively
rewrite the newly attached predicate. The independent verifier rebuilds the
delivered `sqlite3.c` as `tbrunner`, checks default and optimizer-disabled SQL
results against a small Python row-set reference, and has no plan-shape gate.

This is an authentic source regression but likely a direct repair. It is not
accepted as difficult without a Terra/high trajectory review. Do not add
arbitrary SQL variants or internal traces to manufacture failures.

## Pre-freeze verifier corrections

Before Docker/model validation, the verifier was corrected to rebuild and run
the submitted source as `tbrunner`, including each SQL subprocess. Its temporary
root is now traversable and owned by that account. The verifier requires that
account when invoked as root, protects the reward file before candidate code,
and accepts any regular non-symlink source up to 64 MiB rather than assuming an
amalgamation's exact byte size. The prior `uncorrelated_control` was actually
correlated; it now uses an EXISTS predicate independent of the outer row.

The image now matches the warmed Python/g++ layer used by the Ninja probe and
uses a trusted `build.py`, avoiding a separate build-tool installation. These
are authoring/security corrections, not model results.

The pinned static runner passed 21 of 22 checks. The sole expected failure is
the four required human-authored README sections; this feasibility probe does
not fabricate them. See `authoring/evidence/static-20260912.json`.

The first real Docker oracle returned zero because the image did not contain the external patch utility used by solve.sh. The oracle now applies the same attributed two-hunk patch with a checked Python script; no task defect or verifier criterion changed. The failed control is retained as sqlite-oracle-20260912, not a model trial.
