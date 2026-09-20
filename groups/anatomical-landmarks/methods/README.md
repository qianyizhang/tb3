# Maintained methods

The native CT/MRI implementation is `tb3_medical.landmarks`, with pure-Python
scorers in `score_ct` and `score_mri`. BR-040 declares three cases and its exact
input manifest. Use `med prepare`, `med replay` and `med view`; see
[the workflow](../../../docs/workflow.md).

Original task/scorer sources linked by group.json remain historical evidence.
Do not import their authoring scripts into the active package or rewrite frozen
bytes to match a new implementation.
