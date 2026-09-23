# WSI diagnostic agent experiments

`prepare.py` checks selected source bytes against the pinned WSI receipt and builds five local Harbor tasks under `.local/wsi-agent-v1/`: HuBMAP inventory, TIGER cells with and without supplied tissue masks, CAMELYON positive-slide search, and HiESD coarse mapping. The source teaching media and reference coordinates are never supplied as GT-selected detail crops. Private references live in each task's `tests/` and `solution/` trees.

`read_slide.py` reads bounded level-0 crops from tiled TIFF/SVS images and records helper calls. The agent can also read the TIFF directly, so the ledger cannot enforce a search budget; any read-budget comparison needs a separate controlled reader. `score.py` reports bounded scientific diagnostics, while Harbor reward denotes artifact validity. No-op and oracle controls verify the task package, not model skill. Scores on these selected public examples do not establish generalization or clinical validity.

The local runtime is built from the previously validated Python runtime with pinned `imagecodecs==2026.8.16`. Solver and evaluator images must be built and pinned in task metadata before freezing. Protocols in the four experiment folders specify fixed model, effort, resource ceilings and stop conditions. Raw images, generated tasks and runtime logs remain under `.local/`.

As of 2026-09-23, the five task previews and Harbor oracle/no-op controls passed. The first two HuBMAP `gpt-6-sol` model invocations failed at auth/model routing before inference; see its protocol and `.local/wsi-agent-v1/operator-state.json`. Do not repeat the same launch without a verified model route.

The user then switched the pending diagnostic conditions to `gpt-6-astra` medium. The four Astra experiment records reuse the exact five task inputs and private scorers; the Sol attempts stay separate. A bundled host CLI smoke test passed, while isolated Harbor routing is being verified before a WSI model attempt.
