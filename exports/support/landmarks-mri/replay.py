"""Replay retained MRI outputs using the exact frozen scorer; no network or inference."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
manifest = json.loads((ROOT / 'manifest.json').read_text())
for record in manifest['files']:
    path = ROOT / record['destination']
    assert path.resolve().is_relative_to(ROOT), 'Package path escapes root'
    with path.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    assert digest == record['sha256'], record['destination']
spec = importlib.util.spec_from_file_location('frozen_scorer', ROOT / 'tasks/mri32-full/tests/score.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
truth = json.loads((ROOT / 'tasks/mri32-full/tests/truth.json').read_text())
expected = json.loads((ROOT / 'evidence/expected.json').read_text())
results = {}
for name in ('oracle', 'terra-high', 'sol-xhigh'):
    answer = json.loads((ROOT / 'evidence' / (name + '.json')).read_text())
    result = module.score(answer, truth)
    if name == 'oracle':
        assert result['reward'] == 1 and result['accepted_count'] == 32
    else:
        assert result == expected[name], name
    results[name] = {key: result[key] for key in ('reward', 'accepted_count', 'total', 'mean_mm')}
assert module.score(None, truth)['reward'] == 0
results['empty-output-control'] = {'reward': 0}
print(json.dumps({'scope': 'Saved-output replay, including saved oracle and synthetic empty-output control; no new Docker/model trial', 'results': results}, indent=2))
