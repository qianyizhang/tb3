"""Freeze the reviewed absorption conditions and adversarial scorer controls."""
import copy
import gzip
import json
from pathlib import Path
import shutil
import tarfile

import numpy as np
from common import ROOT, OUT, sha, write, freeze_task
from scoring import score

HERE = Path(__file__).parent

INSTRUCTION = '''# Audit mixed anatomical content in abdominal masks

The proposed label of each object is in /app/data/scene.json. Inspect the CT
and masks for substantial tissue from a different named organ included under
that proposed label. An erroneous inclusion may encompass a whole organ or
only part of it, so a correct label elsewhere does not rule out an error.
Report every affected host mask and the anatomical identity of the included
tissue. The number of findings is unspecified and may be zero.

Only substantial inclusions (at least 5 mL of another organ) are in scope.
Ordinary thin contour differences, native mask overlaps, incomplete scan
coverage and missing class names alone are not reportable findings. A label
need not occur separately. Do not infer surgery or disease. The combined class
portal_vein_and_splenic_vein is intentionally one vessel group. Class spellings
are in /app/data/vocabulary.json.

For each finding, provide one representative physical LPS point within the
wrongly included tissue. The evaluator accepts a point within 3 mm of a voxel
centre in that region. Choose a clear internal point; you do not need to
reconstruct its boundary or quantify its volume precisely. Report the HOST
object ID, not the ID of any remaining correctly labeled donor tissue.

Write /app/answer/answer.json as:
{"findings":[{"object_id":"o123","included_label":"class_name","point_lps_mm":[1.0,2.0,3.0]}]}

Use {"findings":[]} if no inclusion is present. Include each host/class pair
once and no prose fields. Missing, extra or wrong host/class findings fail;
localization is graded with the stated tolerance. Correct portions need no
finding. The starter answer is invalid until you write your decision.

## Data and inspection tools

All masks and original CT samples share physical LPS millimetres: +x patient
left, +y posterior and +z superior. Each object NPZ holds mask (binary),
affine_lps ([i,j,k,1] to LPS) and surface_lps (boundary voxel centres). Independent
masks may overlap. The CT NPZ holds hu (int16 Hounsfield units) and affine_lps.
The arrays are authoritative; PNGs are previews. No original reference masks
or clinical diagnosis are supplied. Object IDs, order and colours are arbitrary.

Start with overview.png, ct-overview.png and ct-<object_id>.png in /app/data/.
Every target has a ready axial/coronal/sagittal CT outline preview. Python,
NumPy and Pillow are installed. Additional calculations and tools are allowed.

```sh
python /app/inspect_scene.py
python /app/inspect_scene.py --objects o123,o456 --yaw 75 --pitch 20 --out /app/focus.png
python /app/inspect_ct.py --objects o123 --plane axial --out /app/ct-focus.png
python /app/inspect_ct.py --objects o123 --plane coronal --no-overlay --out /app/ct-plain.png
```

Replace example IDs with actual ones from scene.json. load_scene() from
inspect_scene.py gives the masks, transforms and proposed labels. The CT helper
supports axial/coronal/sagittal views, --positions for comma-separated physical
plane coordinates, --span for field of view in mm, --level/--width for windowing
(default 50/400), and --no-overlay. Without positions it shows five slices
through the selected objects. For negative lists, --positions=-195,-185 works.
No external source/patient matching is needed. See /app/SOURCE_NOTICE.md for
attribution. Decide whether each supplied mask includes the wrong anatomy.
'''


def controls(key, oracle, folder):
    trials = [('oracle', oracle, True), ('invalid_starter', {'findings': None}, False),
              ('empty', {'findings': []}, not key['findings'])]
    if key['findings']:
        row = oracle['findings'][0]
        with np.load(folder / 'region-0.npz') as z:
            p = np.argwhere(z['mask']); a = z['affine_lps']
            q = np.sum(p[:, None, :] * a[None, :3, :3], axis=2) + a[:3, 3]
        def point_answer(point):
            answer = copy.deepcopy(oracle); answer['findings'][0]['point_lps_mm'] = point
            return answer
        trials.append(('alternate_interior_point', point_answer(q[len(q)//3].tolist()), True))
        edge = q[np.argmax(q[:, 0])]
        trials += [('within_3mm', point_answer((edge + [3., 0., 0.]).tolist()), True),
                   ('outside_3mm', point_answer((edge + [3.01, 0., 0.]).tolist()), False),
                   ('distant_point', point_answer((edge + [1000., 0., 0.]).tolist()), False),
                   ('nonfinite_point', point_answer([float('nan'), 0, 0]), False),
                   ('boolean_coordinate', point_answer([True, 0, 0]), False)]
        wrong = copy.deepcopy(oracle); wrong['findings'][0]['included_label'] = 'stomach'
        trials.append(('wrong_class', wrong, False))
        wrong = copy.deepcopy(oracle); wrong['findings'][0]['object_id'] = next(x for x in key['objects'] if x != row['object_id'])
        trials.append(('wrong_host', wrong, False))
        trials.append(('duplicate', {'findings': [row, row]}, False))
    extra = {'object_id': next(iter(key['objects'])), 'included_label': 'spleen', 'point_lps_mm': [0., 0., 0.]}
    trials += [('false_positive', {'findings': oracle['findings'] + [extra]}, False),
               ('prose_field', {**oracle, 'explanation': 'extra'}, False),
               ('malformed_finding', {'findings': [{}]}, False)]
    result = [{'name': n, 'expected': e, 'grade': score(a, key, folder)} for n, a, e in trials]
    assert all(r['expected'] == r['grade']['passed'] for r in result)
    return result


def main():
    screen = json.loads((OUT / 'author/screen.json').read_text())
    for record in screen['tasks']:
        name = record['task']; data = OUT / 'build' / name; private = OUT / 'author' / name
        assert all(sha(data / p) == h for p, h in record['public_files'].items())
        assert all(sha(private / p) == h for p, h in record['private_files'].items())
        task = OUT / 'tasks' / name
        assert not task.exists() and not (OUT / 'freezes' / f'{name}.json').exists()
        for sub in ['environment', 'tests', 'solution']:
            (task / sub).mkdir(parents=True)
        env = task / 'environment'; tests = task / 'tests'
        key = json.loads((private / 'expected.json').read_text())
        oracle = json.loads((private / 'answer.json').read_text())
        checks = controls(key, oracle, private)
        shutil.copyfile(private / 'expected.json', tests / 'expected.json')
        for region in private.glob('region-*.npz'):
            shutil.copyfile(region, tests / region.name)
        shutil.copyfile(private / 'answer.json', task / 'solution/answer.json')
        write(env / 'answer.json', {'findings': None})
        shutil.copyfile(HERE / 'scoring.py', tests / 'scoring.py')
        viewer = (ROOT / 'probes/revisions/br013/authoring/inspect_scene.py').read_text()
        viewer = viewer.replace('q=p@basis;c=centers@basis', 'q=np.sum(p[:,:,None]*basis[None,:,:],axis=1);c=np.sum(centers[:,:,None]*basis[None,:,:],axis=1)')
        (env / 'inspect_scene.py').write_text(viewer)
        shutil.copyfile(HERE / 'inspect_ct.py', env / 'inspect_ct.py')
        license_dir = ROOT / 'runs/br015-clinical/tasks/abdomen-c01/environment'
        for fn in ['DATA-LICENSE.txt', 'LABEL-LICENSE.txt']:
            shutil.copyfile(license_dir / fn, env / fn)
        (env / 'SOURCE_NOTICE.md').write_text('Derived from TotalSegmentator small v2.0.1, Wasserthal / University Hospital Basel.\nhttps://zenodo.org/records/10047263\nData CC BY 4.0; taxonomy Apache 2.0.\nResearch annotation-audit fixture: mask membership may include a substantial simulated neighboring-organ inclusion. Native source CT, scale, orientation, aggregate foreground and unmodified mask voxels are retained. Anonymous IDs and derived previews added. This is not a documented disease or surgical case. No reference mask is distributed in the agent environment.\n')
        (env / 'Dockerfile').write_text('FROM python:3.12-slim-bookworm\nRUN pip install --no-cache-dir numpy==2.2.6 pillow==11.3.0\nWORKDIR /app\nADD data.tar.gz /app/data/\nCOPY answer.json /app/answer/answer.json\nCOPY inspect_scene.py inspect_ct.py SOURCE_NOTICE.md DATA-LICENSE.txt LABEL-LICENSE.txt /app/\n')
        with (env / 'data.tar.gz').open('wb') as f:
            with gzip.GzipFile(fileobj=f, filename='', mode='wb', mtime=0) as gz:
                with tarfile.open(fileobj=gz, mode='w') as tar:
                    for p in sorted(data.iterdir()):
                        info = tar.gettarinfo(str(p), p.name)
                        info.uid = info.gid = 0; info.uname = info.gname = ''; info.mtime = 0
                        with p.open('rb') as content:
                            tar.addfile(info, content)
        (task / 'instruction.md').write_text(INSTRUCTION)
        toml = (ROOT / 'runs/br015-clinical/tasks/abdomen-c01/task.toml').read_text()
        toml = toml.replace('abdomen-c01', name).replace('Infer or audit anatomical identities from intact anonymous 3-D masks.', 'Audit substantial wrong-organ inclusion in CT-supported labeled masks.')
        toml = toml.replace('expert_time_estimate_hours = 0.25\n', '')
        (task / 'task.toml').write_text(toml)
        (tests / 'Dockerfile').write_text('FROM python:3.12-slim-bookworm\nRUN pip install --no-cache-dir numpy==2.2.6\nCOPY . /verifier/\nRUN mkdir -p /app/answer /tests && cp /verifier/test.sh /tests/test.sh && chmod 755 /tests/test.sh\nWORKDIR /app\nCMD ["/tests/test.sh"]\n')
        (tests / 'test.sh').write_text('#!/bin/sh\nset -eu\npython /verifier/verifier.py\n')
        (tests / 'verifier.py').write_text('''import json,time
from pathlib import Path
from scoring import score,read_json
start=time.monotonic();out=Path('/logs/verifier');out.mkdir(parents=True,exist_ok=True)
(out/'reward.txt').write_text('0\\n')
try: result=score(read_json('/app/answer/answer.json'),read_json('/verifier/expected.json'),Path('/verifier'))
except Exception as e: result={'passed':False,'error':str(e)}
result['grading_seconds']=time.monotonic()-start
(out/'details.json').write_text(json.dumps(result,indent=2)+'\\n')
(out/'reward.txt').write_text('1\\n' if result['passed'] else '0\\n')
print(json.dumps(result))
''')
        (task / 'solution/solve.sh').write_text('#!/bin/sh\nset -eu\ncp /solution/answer.json /app/answer/answer.json\n')
        freeze_task(task, {'case': 28, 'mode': 'inclusion_audit',
                          'source_screen_sha256': sha(OUT / 'author/screen.json'),
                          'object_count': record['object_count'], 'finding_count': len(key['findings']),
                          'included_volume_ml': record['included_volume_ml'],
                          'remaining_pancreas_ml': record['remaining_pancreas_ml'],
                          'foreground_union_exact': True, 'ct_samples_exact': record['ct_samples_exact'],
                          'controls': checks,
                          'admission': 'Substantial synthetic inclusion with original CT; exact host/class plus 3 mm point tolerance. Diagnostic only; not clinician validated.'})
        print(json.dumps({'task': name, 'archive_bytes': (env / 'data.tar.gz').stat().st_size,
                          'author_controls': len(checks), 'findings': len(key['findings'])}), flush=True)


if __name__ == '__main__':
    main()
