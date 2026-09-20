# Before tb3-medical

The [manifest](manifest.json) retains exact hashes and recovery locations for
1,791 retired tracked files plus six original navigation documents. The snapshot
is `pre-tb3-medical-2026-09-20` at
`51f3b1224d2069fe931ac28b06fd2ccf38c497ab`. A verified local Git bundle lives at
`.cache/migration/pre-tb3-medical.bundle`. It contains tracked history, not ignored
raw runs. Existing raw runs and environments were left in place.

Retired scope includes 20 nonmedical probe families, their early nonmedical
revisions/receipts, the unfinished BR-018 scaffold, the old catalog and old site
interfaces. Medical records, source assets, stories and relevant reviews moved
to semantic groups; original medical freezes remain byte-identical. The original
interview presentation can be recovered as a historical publication.

```sh
python3.12 scripts/med restore-legacy probes/homology-basis --destination /tmp/homology-history
python3.12 scripts/med restore-legacy site --destination /tmp/interview-history
```

Recovery uses verified ignored copies under `archive/legacy/pre-medical` or exact
Git blobs. It refuses an existing destination and never executes restored code.
In a shallow clone, fetch the snapshot/history first or import the verified bundle.
A complete historical environment may have additional dependencies described in
the restored source. Historical reproduction is not promised by file recovery.

This operation removed active tracking, not history. The bundle and archive are
same-disk recovery copies, **not an independently verified backup**. Large medical
artifacts need their recorded hashes/source locators and selected export recipes;
external artifact storage remains an explicit operational gap.
