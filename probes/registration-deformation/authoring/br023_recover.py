"""Recover inline Python literally from recorded command events; never execute it."""
import ast
import hashlib
import json
from pathlib import Path
import re
import shlex

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'runs/br023-sol-registration'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    logs = list((ROOT / 'runs/br023-deform-2d-sol-xhigh-v1-20260916').glob('*/agent/codex.txt'))
    assert len(logs) == 1
    log = logs[0]
    records = []
    destination = OUT / 'recovered'
    destination.mkdir(exist_ok=True)
    for line in log.read_text().splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get('type') != 'item.completed':
            continue
        item = event.get('item', {})
        if item.get('type') != 'command_execution':
            continue
        command = shlex.split(item['command'])
        assert command[:2] == ['/bin/bash', '-lc'] and len(command) == 3
        bodies = re.findall(r"<<'PY'\n(.*?)\nPY(?:\n|$)", command[2], re.S)
        for i, body in enumerate(bodies):
            ast.parse(body)
            path = destination / f'{item["id"]}-{i}.py'
            path.write_text(body + '\n')
            stdout = destination / f'{item["id"]}.txt'
            stdout.write_text(item.get('aggregated_output', ''))
            records.append({'item': item['id'], 'exit_code': item.get('exit_code'),
                            'path': str(path.relative_to(ROOT)), 'sha256': sha(path),
                            'output_path': str(stdout.relative_to(ROOT)), 'output_sha256': sha(stdout)})
    receipt = {'log_path': str(log.relative_to(ROOT)), 'log_sha256': sha(log), 'scripts': records}
    (OUT / 'recovery.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'scripts': len(records), 'destination': str(destination)}))


if __name__ == '__main__':
    main()
