"""Conditional post-result scope reduction; preserves every M02 evidence byte."""
import json
from pathlib import Path
import shutil
from common import ROOT, OUT, sha, freeze_task


def main():
    for name, expected in [('abdomen-m02', 0), ('abdomen-n01', 1)]:
        paths = list((ROOT / 'runs' / f'br017-{name}-sol-xhigh-v1-20260915').glob('*/result.json'))
        assert len(paths) == 1
        result = json.loads(paths[0].read_text())
        assert result['finished_at'] and not result.get('exception_info')
        assert result['verifier_result']['rewards']['reward'] == expected
    original = json.loads((OUT / 'freezes/abdomen-m02.json').read_text())['tasks'][0]
    source = ROOT / original['task_path']
    assert all(sha(source / p) == h for p, h in original['files'].items())
    task = OUT / 'tasks/abdomen-f01'; data = OUT / 'build/abdomen-f01'
    assert not task.exists() and not data.exists()
    shutil.copytree(source, task)
    shutil.copytree(OUT / 'build/abdomen-m02', data)
    instruction = (task / 'instruction.md').read_text()
    instruction = instruction.replace('# Audit mixed anatomical content in abdominal masks',
                                      '# Audit mixed anatomical content in two neighboring masks')
    instruction = instruction.replace('The proposed label of each object is in /app/data/scene.json. Inspect the CT\nand masks for substantial tissue from a different named organ included under\nthat proposed label.',
        'Audit only o327 (proposed duodenum) and o589 (proposed pancreas). The other\nmasks are available as anatomical context and are outside the reporting scope.\nThe proposed labels are in /app/data/scene.json. Inspect the CT and these two\ntarget masks for substantial tissue from any different named organ included\nunder the proposed label.')
    instruction = instruction.replace('Report every affected host mask', 'Report every affected target mask')
    (task / 'instruction.md').write_text(instruction)
    toml = (task / 'task.toml').read_text().replace('abdomen-m02', 'abdomen-f01')
    toml = toml.replace('Audit substantial wrong-organ inclusion in CT-supported labeled masks.',
                        'Audit two neighboring masks for substantial wrong-organ inclusion with CT and full anatomical context.')
    (task / 'task.toml').write_text(toml)
    differences = [p for p, h in original['files'].items() if sha(task / p) != h]
    assert set(differences) == {'instruction.md', 'task.toml'}
    assert all(sha(p) == sha(data / p.name) for p in (OUT / 'build/abdomen-m02').iterdir())
    metadata = {k: original[k] for k in ['case', 'mode', 'source_screen_sha256', 'object_count',
                 'finding_count', 'included_volume_ml', 'remaining_pancreas_ml', 'foreground_union_exact',
                 'ct_samples_exact', 'controls']}
    metadata.update(source_task='BR017-M02', audit_target_ids=['o327', 'o589'],
                    changed_files_from_m02=differences, all_public_inputs_and_key_byte_identical=True,
                    admission='Conditional scope reduction declared after M02 miss/M01 pass and before N01 result. New one-attempt condition, not an original-scope replication. No clinical adjudication.')
    freeze_task(task, metadata)
    print(json.dumps({'task': 'abdomen-f01', 'changed_files': differences,
                      'public_inputs_and_key_byte_identical': True}))


if __name__ == '__main__':
    main()
