#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export UV_CACHE_DIR="${UV_CACHE_DIR:-${TMPDIR:-/tmp}/tb3-uv-cache}"
upstream=.cache/terminal-bench
revision=e2995b93b0a46edee7bc9942ea5622411a6d5bb9
if [[ ! -d "$upstream/.git" ]]; then
  git clone --filter=blob:none --sparse https://github.com/harbor-framework/terminal-bench.git "$upstream"
  git -C "$upstream" checkout --detach "$revision"
  git -C "$upstream" sparse-checkout set .github docs scripts
fi
if [[ "$(git -C "$upstream" rev-parse HEAD)" != "$revision" ]]; then
  echo 'Upstream checkout differs from configs/upstream-lock.json; inspect before repinning.' >&2
  exit 1
fi
uv venv --allow-existing --python 3.12 .venv
uv pip sync --python .venv/bin/python configs/harbor-trials.lock.txt
uv venv --allow-existing --python 3.12 .venv-validation
uv pip sync --python .venv-validation/bin/python configs/harbor-validation.lock.txt
.venv/bin/harbor --version
.venv-validation/bin/harbor --version
printf '%s\n' 'Harbor installed. Docker engine is a separate host prerequisite; see docs/setup.md.'
