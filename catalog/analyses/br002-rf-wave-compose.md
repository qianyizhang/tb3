# RF composition calibration

BR-002/D02's [matching natural pair](../../docs/evidence/br002-rf-summary.json)
passes all 32 cases under Sol/max and Astra/max. Codex CLI 0.154.0 is recorded
for both; same task checksum and healthy oracle/nop. Both submitted functions
preserve wave metadata, apply physical voltage/current continuity and encode
the target S matrix. Sol uses impedance matrices; Astra directly solves a
four-incident-wave system. No hypothesis-supporting miss occurs.

The [strong library baseline](../../docs/evidence/br002-rf-author-controls.json)
also solves all cases. Eight physical circuit pairs each have four correlated
encodings and sixteen frequencies. Two successful model attempts do not prove
universal ease or estimate a capability difference. Retire this freeze without
extra restrictions or ablations under the [plan](../../docs/research-rounds/BR-002-execution.md).

The [source audit](../../docs/evidence/br002-source-receipts.json) separately
finds source 047's Sol miss on a media-generated line, a surface removed in this
extraction. Do not relabel the original source or inherit its failure rate.
