"""Execute the frozen public-input component plan in isolated task containers."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'runs/br023-sol-registration'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    plan_path = OUT / 'component-plan.json'
    plan = json.loads(plan_path.read_text())
    parser = argparse.ArgumentParser()
    parser.add_argument('--condition', required=True, choices=[x['name'] for x in plan['conditions']])
    args = parser.parse_args()
    for path, expected in plan['source_files'].items():
        assert sha(ROOT / path) == expected, f'Frozen component source changed: {path}'
    assert plan['image'].startswith('sha256:')
    folder = OUT / 'components'
    folder.mkdir(exist_ok=True)
    receipt_path = OUT / 'component-execution.json'
    previous = json.loads(receipt_path.read_text()) if receipt_path.exists() else None
    if previous:
        assert previous['component_plan_sha256'] == sha(plan_path)
    receipts = previous['conditions'] if previous else []
    for case in [x for x in plan['conditions'] if x['name'] == args.condition]:
        destination = folder / case['name']
        destination.mkdir(exist_ok=False)
        command = ['docker', 'run', '--rm', '--network', 'none', '--cpus', '4', '--memory', '4g',
                   '-v', f'{OUT / "recovered"}:/recovered:ro',
                   '-v', f'{ROOT / plan["entrypoint"]}:/runner.py:ro',
                   '-v', f'{destination}:/output', plan['image'], 'python', '/runner.py',
                   '--variant', case['name']]
        start = time.time()
        with (destination / 'execution.log').open('w') as log:
            proc = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        receipt = {'condition': case['name'], 'exit_code': proc.returncode,
                   'elapsed_seconds': time.time() - start, 'network': 'none',
                   'private_labels_mounted': False, 'cpu_limit': 4, 'memory_limit': '4g',
                   'command': command, 'files': {str(p.relative_to(ROOT)): sha(p)
                                               for p in destination.rglob('*') if p.is_file()}}
        receipts.append(receipt)
        receipt_path.write_text(json.dumps({
            'component_plan_sha256': sha(plan_path), 'conditions': receipts}, indent=2) + '\n')
        print(json.dumps({k: receipt[k] for k in ['condition', 'exit_code', 'elapsed_seconds']}), flush=True)
        assert proc.returncode == 0, 'Preserve failed execution; do not silently retry or overwrite'


if __name__ == '__main__':
    main()
