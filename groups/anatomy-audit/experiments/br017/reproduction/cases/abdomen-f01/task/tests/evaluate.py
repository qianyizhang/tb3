"""Portable path adapter for the unchanged task scorer; no authoring imports."""
import argparse
import json
from pathlib import Path
p = argparse.ArgumentParser()
p.add_argument('--answer', type=Path, required=True)
a = p.parse_args()
answer = a.answer.resolve()
here = Path(__file__).resolve().parent
def load(path):
    return json.loads(path.read_text())
try:
    from scoring import score, read_json
    result = score(read_json(answer/'answer.json'), read_json(here/'expected.json'), here)
except (OSError, ValueError, KeyError, TypeError) as exc:
    result = {'passed':False,'error':str(exc)}
print(json.dumps(result, allow_nan=False))
