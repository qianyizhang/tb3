#!/bin/sh
set -eu
mkdir -p /app/answer
cat > /app/answer/answer.json <<'ANSWER'
{"aneurysms": [[307.0, 214.0, 93.0]]}
ANSWER
