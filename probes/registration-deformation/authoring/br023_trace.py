"""Export textual Sol trace evidence without image blobs or raw configurations."""
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'runs/br023-sol-registration'


def text_blocks(value):
    """Return only actual text blocks, not image/base64 representations."""
    if isinstance(value, str):
        try:
            parsed = ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return value if len(value) < 200_000 and 'base64,' not in value else '[non-text payload omitted]'
        if isinstance(parsed, (dict, list)):
            return text_blocks(parsed)
        return value
    if isinstance(value, list):
        return '\n'.join(filter(None, [text_blocks(x) for x in value]))
    if isinstance(value, dict):
        if value.get('type') in ['image', 'image_url', 'input_image']:
            return ''
        if value.get('type') in ['text', 'input_text', 'output_text']:
            return value.get('text', '')
        return '\n'.join(text_blocks(value[k]) for k in ['content', 'results', 'text', 'output'] if k in value)
    return ''


def main():
    paths = list((ROOT / 'runs/br023-deform-2d-sol-xhigh-v1-20260916').glob('*/agent/trajectory.json'))
    assert len(paths) == 1
    trace = paths[0]
    data = json.loads(trace.read_text())
    dest = OUT / 'trace'
    dest.mkdir(exist_ok=True)
    index = []
    for step in data['steps']:
        number = step['step_id']
        record = {'step': number, 'source': step.get('source'), 'files': []}
        message = step.get('message')
        if message:
            value = message if isinstance(message, str) else text_blocks(message)
            path = dest / f'step{number:03d}-message.txt'
            path.write_text(value)
            record['files'].append(str(path.relative_to(ROOT)))
        for i, call in enumerate(step.get('tool_calls', [])):
            # Retain only the requested tool and authored arguments. Do not
            # introspect unrelated config/env files or serialize observations.
            path = dest / f'step{number:03d}-call{i}.json'
            path.write_text(json.dumps(call, indent=2) + '\n')
            record['files'].append(str(path.relative_to(ROOT)))
        if step.get('observation'):
            path = dest / f'step{number:03d}-output.txt'
            path.write_text(text_blocks(step['observation']))
            record['files'].append(str(path.relative_to(ROOT)))
        index.append(record)
    receipt = {'trajectory_path': str(trace.relative_to(ROOT)),
               'trajectory_sha256': hashlib.sha256(trace.read_bytes()).hexdigest(),
               'steps': index}
    (OUT / 'trace-index.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'trajectory': receipt['trajectory_path'], 'steps': len(index), 'export': str(dest)}))


if __name__ == '__main__':
    main()
