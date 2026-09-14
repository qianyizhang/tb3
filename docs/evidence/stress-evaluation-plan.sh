#!/bin/sh
# E05 commands, executed after E04 completion. Do not reuse job names.
set -eu
docker build --build-arg http_proxy=http://192.168.5.2:10808 --build-arg https_proxy=http://192.168.5.2:10808 -t tb3-extxyz-stress-env probes/extxyz-stress/environment
docker build --build-arg http_proxy=http://192.168.5.2:10808 --build-arg https_proxy=http://192.168.5.2:10808 -t tb3-extxyz-stress-tests probes/extxyz-stress/tests
.venv-validation/bin/harbor run -p probes/extxyz-stress --env docker --agent oracle --n-attempts 1 --n-concurrent 1 --yes -o runs --job-name stress-oracle-v1-20260914
.venv-validation/bin/harbor run -p probes/extxyz-stress --env docker --agent nop --n-attempts 1 --n-concurrent 1 --yes -o runs --job-name stress-nop-v1-20260914
# Only after matching healthy controls and docs/evidence/stress-pilot-freeze.json:
.venv/bin/harbor run -p probes/extxyz-stress --env docker --agent codex --model openai/gpt-5.6-terra --ak reasoning_effort=high --ae CODEX_FORCE_AUTH_JSON=1 --ae http_proxy=http://192.168.5.2:10808 --ae https_proxy=http://192.168.5.2:10808 --ae HTTP_PROXY=http://192.168.5.2:10808 --ae HTTPS_PROXY=http://192.168.5.2:10808 --ae NO_PROXY=localhost,127.0.0.1 --n-attempts 1 --n-concurrent 1 -o runs --job-name stress-terra-high-v1-20260914
