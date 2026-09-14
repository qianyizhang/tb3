#!/bin/sh
# Recorded commands for E01. Do not reuse completed job names.
set -eu
# Author controls occurred before freeze; do not regenerate a frozen fixture.
# PYTHONDONTWRITEBYTECODE=1 .venv-brainstorm/bin/python -W error probes/mr-frame-association/authoring/fixtures.py
# PYTHONDONTWRITEBYTECODE=1 .venv-brainstorm/bin/python -W error probes/mr-frame-association/authoring/validate.py
docker build --build-arg http_proxy=http://192.168.5.2:10808 --build-arg https_proxy=http://192.168.5.2:10808 -t tb3-mr-frame-association-env probes/mr-frame-association/environment
docker build --build-arg http_proxy=http://192.168.5.2:10808 --build-arg https_proxy=http://192.168.5.2:10808 -t tb3-mr-frame-association-tests probes/mr-frame-association/tests
.venv-validation/bin/harbor run -p probes/mr-frame-association --env docker --agent oracle --n-attempts 1 --n-concurrent 1 --yes -o runs --job-name mr-oracle-v1-20260914
.venv-validation/bin/harbor run -p probes/mr-frame-association --env docker --agent nop --n-attempts 1 --n-concurrent 1 --yes -o runs --job-name mr-nop-v1-20260914
# Only after matching healthy controls and docs/evidence/mr-pilot-freeze.json:
.venv/bin/harbor run -p probes/mr-frame-association --env docker --agent codex --model openai/gpt-5.6-terra --ak reasoning_effort=high --ae CODEX_FORCE_AUTH_JSON=1 --ae http_proxy=http://192.168.5.2:10808 --ae https_proxy=http://192.168.5.2:10808 --ae HTTP_PROXY=http://192.168.5.2:10808 --ae HTTPS_PROXY=http://192.168.5.2:10808 --ae NO_PROXY=localhost,127.0.0.1 --n-attempts 1 --n-concurrent 1 -o runs --job-name mr-terra-high-v1-20260914
