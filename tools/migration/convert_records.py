"""One-time conversion for the native workbench; never imported by the app."""
import collections
import json
from pathlib import Path
import subprocess

from tb3_medical import core as c

root = Path.cwd()
old = {}
tracked = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', '077cfdca8abc2f66be6682a46e32b476391aed5a'], text=True).splitlines()
for name in tracked:
    if not name.startswith(('groups/', 'datasets/', 'discussions/', 'exports/records/')) or not name.endswith('.json'):
        continue
    if any(x in {'figures', 'methods', 'examples', 'sources'} for x in Path(name).parts):
        continue
    row = json.loads(subprocess.check_output(['git', 'show', '077cfdca8abc2f66be6682a46e32b476391aed5a:' + name]))
    if isinstance(row, dict) and row.get('kind') in c.KINDS:
        old[row['id']] = (root / name, row)


def owners(key, seen=None):
    seen = set() if seen is None else seen
    if key in seen or key not in old:
        return set()
    seen.add(key)
    row = old[key][1]
    if row['kind'] == 'experiment':
        return {key}
    if row.get('experiment_id'):
        return {row['experiment_id']}
    found = set()
    for dep in row.get('depends_on', []):
        found |= owners(dep, seen)
    if row.get('target_id'):
        found |= owners(row['target_id'], seen)
    return found


def compact(value):
    if isinstance(value, dict):
        return {k: compact(v) for k, v in value.items() if v is not None}
    if isinstance(value, list):
        return [compact(v) for v in value if v is not None]
    return value


def idea_state(value):
    return {'rejected': 'dropped', 'superseded': 'parked', 'promoted': 'selected'}.get(value, value if value in {'exploring','selected','parked','dropped'} else 'exploring')

relocations = {}
converted = []
for key, (path, source) in old.items():
    row = dict(source)
    row['schema_version'] = 2
    kind = row['kind']
    for field in ('validity', 'depends_on', 'aliases'):
        row.pop(field, None)
    if source.get('aliases'):
        row['historical_ids'] = source['aliases']
    target = path
    if kind == 'experiment':
        row.pop('lifecycle', None)
        row['historical'] = not bool(source.get('task_path'))
        row['assessment'] = 'not_assessed'
        if source.get('lifecycle') == 'parked':
            row['experiment_stage'] = 'parked'
        if source.get('task_path'):
            row['experiment_stage'] = 'active'
        row['protocol'] = 'protocol.md'
        protocol = path.parent / 'protocol.md'
        if not protocol.exists():
            text = f"# {row['title']}\n\n{row.get('question', '')}\n\n"
            text += row.pop('notes', '') + '\n\n'
            text += '## Retained protocol and observations\n\n'
            text += '\n'.join(f"- [{x['label']}]({Path('../../../../..') / x['path']})" for x in row.get('links', [])) + '\n'
            protocol.write_text(text)
        row.pop('question', None)
        row.pop('reproducibility', None)
        target = path.with_suffix('.toml')
    elif kind == 'idea':
        row['idea_state'] = idea_state(row.pop('disposition', 'exploring'))
        body = '# ' + row['title'] + '\n\n'
        for field in ('question', 'prior_findings', 'notes', 'reopen_when'):
            value = row.pop(field, None)
            if value:
                body += '## ' + field.replace('_', ' ').capitalize() + '\n\n' + (value if isinstance(value, str) else json.dumps(value, indent=2)) + '\n\n'
        row['body'] = body.strip()
        row.pop('decisions', None)
        target = path.with_suffix('.md')
    elif kind == 'decision':
        row['idea_state'] = idea_state(row.pop('disposition'))
        row['accepted'] = row['actor'] == 'user'
    elif kind == 'evaluation':
        if not row.get('attempt_id'):
            origin = next((old[x][1] for x in source.get('depends_on', []) if x in old and old[x][1]['kind'] == 'evaluation'), None)
            if origin:
                row['attempt_id'] = origin['attempt_id']
                row['source_evaluation'] = origin['id']
        cls = row.pop('classification', '')
        if cls:
            row['source_classification'] = cls
        row['outcome'] = ('pass' if row.get('reward') == 1 else 'fail' if row.get('reward') == 0 else 'no_verdict') if cls not in {'incomplete','execution_error','unknown'} else 'no_verdict'
        row['execution_state'] = 'error' if cls == 'execution_error' else 'running' if cls == 'incomplete' else 'completed'
        row['partial'] = row.pop('completeness', '') == 'partial' or cls == 'incomplete'
        row.pop('qualifying_final_trial', None)
        row.setdefault('collected_at', row.get('finished_at') or row.get('started_at') or '2026-09-20T00:00:00+00:00')
    elif kind in {'group', 'finding', 'export'}:
        if kind in {'group', 'finding'}:
            gid = row['id'] if kind == 'group' else row['group_id']
            row['experiment_ids'] = sorted(k for k, (_, r) in old.items() if r['kind'] == 'experiment' and r['group_id'] == gid)
        else:
            row['experiment_ids'] = sorted(owners(key))
            row['submission_status'] = 'draft'
            row.pop('qualification', None)
    elif kind == 'review':
        exp = sorted(owners(source['target_id']))
        if not exp:
            raise ValueError(('Unknown review scope', key))
        row['experiment_id'] = exp[0]
        row['assessment'] = {'qualified':'usable','supported':'usable','invalidated':'invalidated','under_review':'needs_review'}.get(source.get('validity'), 'not_assessed')
        row['scope'] = 'Retained assessment of ' + row.pop('target_id') + '; ' + row.get('reason','')
        row.setdefault('actor', 'historical-review')
        row.setdefault('reason', row.get('notes', 'Retained authored assessment'))
    elif kind == 'plan':
        row['execution_state'] = 'running' if row.pop('planned_state', '') == 'externally_running_at_migration' else 'planned'
        row['observed_at'] = '2026-09-20T00:00:00+00:00'
        target = path.parent / 'plans' / (key + '.json')
    if target.suffix in {'.toml', '.md'}:
        row = compact(row)
    c.validate_record(row, target)
    c.atomic_write(target, row)
    if target != path:
        relocations[str(path.relative_to(root))] = str(target.relative_to(root))
        path.unlink(missing_ok=True)
    converted.append(row)

# Links in mutable authoring records follow the canonical files. Frozen source
# receipts are untouched; their original locators are historical provenance.
for path, row in c.record_paths(root):
    changed = False
    for link in row.get('links', []):
        if link['path'] in relocations:
            link['path'] = relocations[link['path']]
            changed = True
    if changed:
        c.atomic_write(path, row)

report = {
    'baseline_commit': '077cfdca8abc2f66be6682a46e32b476391aed5a',
    'records_before': len(old), 'records_after': len(converted),
    'kinds': dict(collections.Counter(r['kind'] for r in converted)),
    'ids_preserved': set(old) == {r['id'] for r in converted},
    'original_outcomes': 'Rewards, metrics, source evidence locators and hashes retained; no rescoring.',
    'historical_bytes': 'Original normalized records recoverable from baseline Git commit; raw evidence untouched.',
}
c.atomic_write(root / 'docs/migration/native-record-conversion.json', report)
print(json.dumps(report, indent=2))
