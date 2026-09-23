# Revised WSI diagnostic tasks

This method prepares fresh Sol 6 xhigh conditions after the frozen Astra medium
trace/reference audit. Run `prepare.py` explicitly in the prebuilt
`tb3-wsi-agent-runtime:v1` image with this checkout mounted at `/repo`; it refuses
to replace an existing `.local/wsi-agent-v2` destination. Original task trees,
freezes, scores and raw traces remain unchanged.

The new task contracts are separate: HuBMAP reports reference recall and queues
unmatched points for review; TIGER exposes all official tissue codes and reports
both center conventions; CAMELYON groups nearby source polygons into study-defined
lesions on two positive and one negative slide; HiESD classifies fixed annotated
patches with hidden labels. The CAMELYON grouping is not the official challenge
FROC implementation. HiESD patch selection uses private annotations to define
the evaluation domain and does not measure autonomous slide search.

All slides, patches, references and runtime products stay under `.local/`. New
CAMELYON source files are checked against the publisher's MD5 manifest and their
SHA-256 digests before preparation. Every task needs a new pinned solver/evaluator
image, preview and oracle/no-op control contrast before model execution. Harbor
reward means a valid answer artifact; diagnostic measures remain separate.
