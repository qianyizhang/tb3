# Acquire inputs — registration-br024

The fully materialized handoff package is the supported exact-input route. It
contains every file listed in manifest.json, including solver data, evaluator-only
references and saved answers. Transfer the entire package to the reproducing agent;
do not give that agent only this repository's code or the author's local cache.
Run `python reproduce.py verify --root PACKAGE` after transfer. It checks every
required file's size, SHA-256 and executable mode before evaluation.

From the workbench, `med bundle registration-br024 NEW_DIRECTORY --include-flagged` creates the
handoff from the declared inputs. `--input-root PACKAGE` can restore artifact
inputs from a previously handed-off package. Large data remain outside Git.
The package can be copied between machines without the original workspace.

## Upstream data references


These locators are retained source records, not a live availability check.

- https://creativecommons.org/licenses/by/4.0/
- https://doi.org/10.5281/zenodo.3835682
- https://learn2reg.grand-challenge.org/Datasets/

These source locators document original acquisition and terms. They are not claimed
to reconstruct task-specific annotations/preprocessing by themselves. If the exact
prepared handoff is unavailable, report the missing manifest entries and recover
that bundle before claiming reproduction. Do not substitute another patient or
silently regenerate a different fixture. Original hashes remain authoritative.
Source access and redistribution restrictions travel with the data; this local
research handoff is not a public release or clinical/submission certification.
