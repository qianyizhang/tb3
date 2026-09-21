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
    from score import score
    result = score(load(answer/'landmarks.json'), load(here/'truth.json'))
except (OSError, ValueError, KeyError, TypeError) as exc:
    result = {'reward':0,'error':str(exc)}
print(json.dumps(result, allow_nan=False))
