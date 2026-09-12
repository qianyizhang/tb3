#!/bin/sh
# Non-security geometry diagnostic only. Run from the tb3 repository root.
# Prewarm Docker builds using this Mac's existing network proxy; it is not
# written into either task Dockerfile. Each job name denotes one attempt.
set -eu
docker build --build-arg http_proxy=http://192.168.5.2:10808 --build-arg https_proxy=http://192.168.5.2:10808 -t tb3-clipper-polytree-tests-pickup probes/clipper-polytree/tests
docker build -t tb3-clipper-polytree-env-pickup probes/clipper-polytree/environment
.venv-validation/bin/harbor run -p probes/clipper-polytree --env docker --agent oracle --n-attempts 1 --n-concurrent 1 --yes --ae http_proxy=http://192.168.5.2:10808 --ae https_proxy=http://192.168.5.2:10808 --ae HTTP_PROXY=http://192.168.5.2:10808 --ae HTTPS_PROXY=http://192.168.5.2:10808 --ae NO_PROXY=localhost,127.0.0.1 -o runs --job-name clipper-oracle-v3-20260912
.venv-validation/bin/harbor run -p probes/clipper-polytree --env docker --agent nop --n-attempts 1 --n-concurrent 1 --yes -o runs --job-name clipper-nop-v3-20260912
# Launch only after same-snapshot oracle 1 / nop 0 with no exceptions.
.venv/bin/harbor run -p probes/clipper-polytree --env docker --agent codex --model openai/gpt-5.6-terra --ak reasoning_effort=high --ae CODEX_FORCE_AUTH_JSON=1 --ae http_proxy=http://192.168.5.2:10808 --ae https_proxy=http://192.168.5.2:10808 --ae HTTP_PROXY=http://192.168.5.2:10808 --ae HTTPS_PROXY=http://192.168.5.2:10808 --ae NO_PROXY=localhost,127.0.0.1 --n-attempts 1 --n-concurrent 1 -o runs --job-name clipper-terra-high-v3-20260912
