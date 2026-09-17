"""Package reviewed local exams; references stay outside solver directories."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil

HERE = Path(__file__).resolve().parent
SAFE_CONTEXT = {'age', 'sex', 'indication', 'technique', 'available_comparisons'}


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def prepare(manifest, out):
    cases = json.loads(Path(manifest).read_text())
    if not isinstance(cases, list) or not cases:
        raise ValueError('Expected a nonempty list of reviewed cases')
    seen_cases, seen_patients = set(), set()
    for case in cases:
        cid, patient = case['case_id'], case['patient_key']
        if not re.fullmatch(r'C\d{3}', cid) or cid in seen_cases:
            raise ValueError('Case IDs must be unique anonymous C001-style IDs')
        if not patient or patient in seen_patients:
            raise ValueError('Duplicate or missing patient key')
        seen_cases.add(cid)
        seen_patients.add(patient)
        for field in ['technical_review_complete', 'solver_metadata_review_complete',
                      'rights_review_complete']:
            if case.get(field) is not True:
                raise ValueError(f'{cid}: missing completed review: {field}')
        if case['reference_kind'] != 'clinical_radiologist_report':
            raise ValueError('This condition requires an original clinical report')
        if not case['source_url'] or not case['source_revision']:
            raise ValueError('Source and pinned revision required')
        if not isinstance(case.get('context', {}), dict):
            raise ValueError('Context must be a dictionary')
        if set(case.get('context', {})) - SAFE_CONTEXT:
            raise ValueError('Context contains fields outside the allowlist')
        report = Path(case['report_path'])
        if not report.is_absolute() or not report.is_file() or not report.read_text().strip():
            raise ValueError('Missing nonempty local report')
        if not case['images']:
            raise ValueError('No exam images')
        for entry in case['images']:
            path = Path(entry['path'])
            if not path.is_absolute() or not path.is_file() or path.stat().st_size == 0:
                raise ValueError('Missing nonempty local image')
            if not path.name.endswith(('.nii.gz', '.nii', '.png')):
                raise ValueError('Unsupported image format')
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    reference = out / 'reference'
    reference.mkdir()
    receipts = []
    for case in cases:
        cid = case['case_id']
        solver = out / 'solver' / cid
        solver.mkdir(parents=True)
        mapping = []
        for i, entry in enumerate(case['images'], 1):
            source = Path(entry['path'])
            suffix = '.nii.gz' if source.name.endswith('.nii.gz') else source.suffix
            target = solver / f'image-{i:02d}{suffix}'
            shutil.copyfile(source, target)
            mapping.append({'source_path': str(source), 'solver_name': target.name,
                            'sha256': sha(target)})
        shutil.copyfile(HERE / 'instruction.md', solver / 'instruction.md')
        shutil.copyfile(HERE / 'inspect_ct.py', solver / 'inspect_ct.py')
        (solver / 'tools.md').write_text(
            'CT: python inspect_ct.py image-01.nii.gz --info\n'
            'Render: python inspect_ct.py image-01.nii.gz --plane axial '
            '--positions 0,10,20 --level -600 --width 1500 --out views/lung.png\n'
            'Use --help for options. Positions are physical RAS millimetres; '
            'consult --info for actual coverage. Open rendered PNG files with '
            'your image-viewing tool. PNG examination images can be opened '
            'directly. Rendering alone does not display an image to you.\n')
        write(solver / 'context.json', case.get('context', {}))
        report = reference / f'{cid}-report.txt'
        shutil.copyfile(case['report_path'], report)
        receipts.append({**case, 'images': mapping, 'report_sha256': sha(report),
                         'solver_files': {p.name: sha(p) for p in sorted(solver.iterdir())}})
    write(reference / 'manifest.json', receipts)
    write(reference / 'freeze.json', {
        'status': 'packaged_pending_case_claim_ledger_and_runtime_controls',
        'files': {str(p.relative_to(out)): sha(p) for p in sorted(out.rglob('*'))
                  if p.is_file()},
    })
    return receipts


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    receipts = prepare(args.manifest, args.out)
    print(json.dumps({'packaged': len(receipts), 'output': str(args.out),
                      'ready_for_trial': False}))
