#!/bin/sh
set -eu
mkdir -p /app/answer
cat > /app/answer/answer.json <<'ANSWER'
{"aneurysms": [[166.0, 273.0, 84.0]]}
ANSWER
