#!/bin/sh
# Executed non-security, short-horizon diagnostic commands, from repository root.
# Job names identify the retained attempts; do not reuse them for a new attempt.
set -eu
docker build --build-arg http_proxy=http://192.168.5.2:10808 --build-arg https_proxy=http://192.168.5.2:10808 -t tb3-homology-basis-env probes/homology-basis/environment
docker build --build-arg http_proxy=http://192.168.5.2:10808 --build-arg https_proxy=http://192.168.5.2:10808 -t tb3-homology-basis-tests probes/homology-basis/tests
.venv-validation/bin/harbor run -p probes/homology-basis --env docker --agent oracle --n-attempts 1 --n-concurrent 1 --yes -o runs --job-name homology-oracle-20260912
.venv-validation/bin/harbor run -p probes/homology-basis --env docker --agent nop --n-attempts 1 --n-concurrent 1 --yes -o runs --job-name homology-nop-20260912
# Only after matching healthy oracle 1 / nop 0 and the task freeze check:
.venv/bin/harbor run -p probes/homology-basis --env docker --agent codex --model openai/gpt-5.6-terra --ak reasoning_effort=high --ae CODEX_FORCE_AUTH_JSON=1 --ae http_proxy=http://192.168.5.2:10808 --ae https_proxy=http://192.168.5.2:10808 --ae HTTP_PROXY=http://192.168.5.2:10808 --ae HTTPS_PROXY=http://192.168.5.2:10808 --ae NO_PROXY=localhost,127.0.0.1 --n-attempts 1 --n-concurrent 1 -o runs --job-name homology-terra-high-20260912
