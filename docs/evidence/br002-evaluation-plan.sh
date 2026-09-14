#!/bin/sh
# BR-002 recorded command pattern. Job names are immutable; do not rerun them.
# Source fixtures/freezes and docs/research-rounds/BR-002-execution.md own scope.
set -eu

control() {
    slug=$1 key=$2 version=$3 agent=$4
    .venv-validation/bin/harbor run -p "probes/$slug" --env docker \
      --agent "$agent" --n-attempts 1 --n-concurrent 1 --yes -o runs \
      --job-name "br002-$key-$agent-$version-20260914"
}

diagnostic() {
    slug=$1 key=$2 version=$3 model=$4 label=$5
    .venv/bin/harbor run -p "probes/$slug" --env docker --agent codex \
      --model "$model" --ak reasoning_effort=max \
      --ae CODEX_FORCE_AUTH_JSON=1 \
      --ae http_proxy=http://192.168.5.2:10808 \
      --ae https_proxy=http://192.168.5.2:10808 \
      --ae HTTP_PROXY=http://192.168.5.2:10808 \
      --ae HTTPS_PROXY=http://192.168.5.2:10808 \
      --ae NO_PROXY=localhost,127.0.0.1 \
      --n-attempts 1 --n-concurrent 1 -o runs \
      --job-name "br002-$key-$label-max-$version-20260914"
}

# Build each agent/verifier Dockerfile first with the existing explicit build
# proxy. Validate fixtures and inspect matching controls, then save its freeze
# before invoking diagnostic. The result receipts establish which commands ran.
# Score/actuator v1 controls preceded final source-cache relocation; retain them.

control rf-wave-compose rf v1 oracle
control rf-wave-compose rf v1 nop
diagnostic rf-wave-compose rf v1 openai/gpt-5.6-sol sol
diagnostic rf-wave-compose rf v1 openai/gpt-6-astra astra

control score-sounding-events score v2 oracle
control score-sounding-events score v2 nop
diagnostic score-sounding-events score v2 openai/gpt-5.6-sol sol
diagnostic score-sounding-events score v2 openai/gpt-6-astra astra

control actuator-memory actuator v2 oracle
control actuator-memory actuator v2 nop
diagnostic actuator-memory actuator v2 openai/gpt-5.6-sol sol
diagnostic actuator-memory actuator v2 openai/gpt-6-astra astra

control moving-frame-velocity frame v1 oracle
control moving-frame-velocity frame v1 nop
diagnostic moving-frame-velocity frame v1 openai/gpt-5.6-sol sol
diagnostic moving-frame-velocity frame v1 openai/gpt-6-astra astra
