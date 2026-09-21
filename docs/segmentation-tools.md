# Segmentation tool rulebook

When the user asks to add a **seg tool**, **SAM**, or **LiteMedSAM** to a medical
experiment, start with LiteMedSAM for box-to-mask work. Preserve an explicitly
requested model choice. This setup preference does not authorize a new agent trial.

The [solver skill](../src/tb3_medical/skills/litemedsam/SKILL.md) is the canonical
source for the executable adapter, image/box contract and coordinate cautions.
A copy is installed at `~/.codex/skills/litemedsam`; refresh it after source edits.

## On this Mac

Reuse `.local/sam-lite-bench-20260921/`: `.venv/`, `vendor/LiteMedSAM/`, and
`weights/lite_medsam.pth`. No fresh download is needed.

```sh
python3.12 src/tb3_medical/skills/litemedsam/scripts/segment.py \
  --runtime .local/sam-lite-bench-20260921 \
  --image /absolute/path/slice.png --boxes /absolute/path/boxes.json \
  --output /absolute/path/NEW-result --device mps
```

Use approved execution when the sandbox prevents Metal access. CPU is an explicit
alternative. Multiple boxes on one image reuse its embedding. Record the HU
window, slice/crop mapping, box provenance and emitted receipt. Keep outputs local.

## Supply it through Harbor / tb3

**Supported without changing `med run`.** Checked against installed Harbor 0.14.0
and 0.18.0 on 2026-09-21: `environment.skills_dir` reaches the Codex adapter, which
registers skills in `$HOME/.agents/skills`. This task-bound route also includes
the skill bytes in tb3's frozen task digest.

For a **new task revision**, copy only the canonical skill folder to
`task/environment/skills/litemedsam/`. In the task's Dockerfile:

```dockerfile
COPY skills/ /skills/
ENV LITEMEDSAM_ROOT=/opt/litemedsam
```

Add `skills_dir = "/skills"` to the existing `[environment]` table in `task.toml`.
Provide `/opt/litemedsam/.venv/bin/python`, `vendor/LiteMedSAM/` and
`weights/lite_medsam.pth` in that image. Build Linux dependencies; do not copy a
macOS virtualenv. Mac-hosted Docker uses CPU, since MPS is host-only. Pin the image,
source commit, dependency versions and checkpoint hash. Check one image+box call
inside the actual image before launching an agent.

The tested [upstream source](https://github.com/bowang-lab/MedSAM/tree/LiteMedSAM)
commit is `b0fab476e54e631dd412b25e0db9fdf2a2b0f54c`. The local
`requirements-resolved.txt` and `provisioning.json` retain dependencies and URLs.
The checkpoint SHA-256 is
`79d8c9dca6db4d69d3f905579e5250af05e859fff9c1f543e89a513c3028ce76`;
the adapter rejects a different checkpoint. Retain the upstream Apache-2.0 license
and checkpoint provenance with provisioned assets.

Harbor also supports job-level `--skill /path/to/litemedsam` or `agents[].skills`
in its job config. tb3 exposes no corresponding CLI flag. Prefer the task-bound
route: an external job skill requires separate hashing/binding. See
[task skills](https://docs.harborframework.com/core-concepts/tasks/skills) and
[job skills](https://docs.harborframework.com/core-concepts/jobs/skills).

State in solver instructions that LiteMedSAM is available and point to
`/skills/litemedsam/SKILL.md`. Keep evaluator masks, selection manifests, benchmark
scripts and findings out of the solver payload. Record **agent + LiteMedSAM** as
the condition; distinguish agent-chosen prompts from oracle boxes. Preserve old
frozen tasks. No Linux build or agent trial is claimed by this packaging work.

## Evidence and illustrations

The [narrow calibration](../groups/anatomy-audit/findings/sam-litemedsam-slice-calibration.md)
supports this initial choice on one abdominal CT with reference-derived prompts,
not autonomous localization or unseen-case/3D performance. SAM 2.1 Small remains
available as a comparator, with its CPU/MPS discrepancy explicit.

Every colored overlay should include swatches or line samples using the exact
overlay colors and styles. Label prediction, reference (if available) and prompt;
give white reference lines readable contrast. Use one shared palette for drawing
and legends. Retain original masks, scores and figures; legend revisions are
separate derived artifacts.
