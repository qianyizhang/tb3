#!/bin/sh
set -eu
mkdir -p /app/answer
cat > /app/answer/answer.json <<'ANSWER'
{"aneurysms": []}
ANSWER
