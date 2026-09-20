# Reproduce medical work

Start with the [workflow](workflow.md) and the experiment record returned by
`python3.12 scripts/med show ID`. Historical protocols and task hashes are retained
as evidence. An experiment's availability, replay status and scientific validity
are different properties; a Dockerfile alone establishes none of them.

The [landmark MRI recipe](../exports/recipes/landmarks-mri-v2.json) selects exact
frozen task files, source notice, saved outputs and a standalone Python replay.
Build it with `python3.12 scripts/med export exports/recipes/landmarks-mri-v2.json
/fresh/destination`, then run `python3.12 replay.py` inside that destination. Missing
artifacts are listed with their expected digests in the recipe. The replay checks
saved model/oracle outputs and an empty control, without Docker, source checkout,
network or new inference. It does not certify current submission requirements.

All other historical medical experiments are indexed with their original
protocols, receipts and explicit recovery gaps. Inspect the record before running
old authoring scripts: some prepare inputs or overwrite a working task directory.
Never regenerate a historical freeze to match current code.

`make site PYTHON=python3.12` opens the current local presentation server. Guided
tours use local derived data; portable stories keep static images and attribution.
`python3.12 scripts/med assets` verifies 17 exact retained assets.
`scripts/med-media --help` describes media rendering; it never starts model trials.

Original nonmedical reproduction workflows are historical, available through
[the recovery manifest](../archive/README.md). A local Git bundle and an ignored
archive copy provide same-disk recovery. Independent off-machine backup remains
unverified. No ignored raw run or environment is deleted by this migration.
