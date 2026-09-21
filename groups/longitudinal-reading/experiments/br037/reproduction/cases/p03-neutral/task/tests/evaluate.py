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
    from score import validate
    result = validate(load(answer/'assessment.json'), load(here/'manifest.json'))
    if not (answer/'report.md').exists():
        result['contract_pass'] = False
        result['errors'].append('Missing report.md')
except (OSError, ValueError, KeyError, TypeError) as exc:
    result = {'contract_pass':False,'errors':[str(exc)],'clinical_accuracy':'Not scored'}
print(json.dumps(result, allow_nan=False))
