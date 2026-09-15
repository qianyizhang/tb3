"""Collect one result per frozen patient task; keep performance and validity apart."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import csv
import hashlib
import html
import importlib.util
import json
import statistics

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / 'runs/br004-sol'
PLAN = ROOT / 'docs/evidence/br004-sol-freeze.json'
TASK_KINDS = {
    'case-74': 'Limited-coverage control',
    'case-19': 'Thoracic-abnormality control',
    'case-83': 'Kidney-pole omission',
    'case-46': 'Scoped pathology control',
    'case-28': 'Local rib-identity exchange',
    'case-61': 'Inferior heart omission',
    'case-95': 'Pathology control',
    'case-32': 'Small kidney extension',
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def elapsed(obj):
    if not obj or not obj.get('started_at') or not obj.get('finished_at'):
        return None
    return (datetime.fromisoformat(obj['finished_at']) - datetime.fromisoformat(obj['started_at'])).total_seconds()

def result_for(case_id, phase):
    job = ROOT / 'runs' / f'br004-sol-{case_id.split("-")[1]}-{phase}-v1-20260915'
    paths = list(job.glob('*/result.json'))
    assert len(paths) <= 1, 'More than one trial violates the declared protocol'
    if not paths:
        return None, None
    return paths[0], json.loads(paths[0].read_text())

def collect(plan):
    rows = []
    review_path = ROOT / 'docs/evidence/br004-sol-reviews.json'
    reviews = json.loads(review_path.read_text()).get('reviews', {}) if review_path.exists() else {}
    for task in plan['tasks']:
        row = {key: task[key] for key in ['task_id', 'case_id', 'focus_label_count', 'expected_positive_labels', 'source_truth_hold']}
        row['task_kind'] = TASK_KINDS[task['case_id']]
        row['task_bytes_unchanged_from_terra'] = task['task_bytes_unchanged']
        row['review_exclusions'] = task['review_exclusions']
        row['post_trial_source_truth_hold'] = False
        row['controls'] = {}
        for phase in ['oracle', 'nop']:
            path, result = result_for(task['case_id'], phase)
            if result:
                row['controls'][phase] = {'result_path': str(path.relative_to(ROOT)), 'result_sha256': sha(path),
                                         'reward': (result.get('verifier_result') or {}).get('rewards', {}).get('reward'),
                                         'exception_type': (result.get('exception_info') or {}).get('exception_type'),
                                         'total_seconds': elapsed(result),
                                         'task_checksum': result['task_checksum']}
                wanted = 1 if phase == 'oracle' else task['nop_expected_reward']
                assert row['controls'][phase]['reward'] == wanted and not result.get('exception_info')
        row['controls_total_seconds'] = sum(c['total_seconds'] for c in row['controls'].values()) if len(row['controls']) == 2 else None
        path, result = result_for(task['case_id'], 'sol-xhigh')
        row['execution'] = 'pending'
        if result:
            exception = (result.get('exception_info') or {}).get('exception_type')
            row.update(execution='timeout' if exception == 'AgentTimeoutError' else 'execution_error' if exception else 'completed',
                       exception_type=exception, result_path=str(path.relative_to(ROOT)), result_sha256=sha(path),
                       task_checksum=result['task_checksum'], model=result['config']['agent'].get('model_name'),
                       reasoning_effort=result['config']['agent'].get('kwargs', {}).get('reasoning_effort'),
                       agent_version=(result.get('agent_info') or {}).get('version'),
                       started_at=result['started_at'], finished_at=result['finished_at'],
                       agent_started_at=(result.get('agent_execution') or {}).get('started_at'),
                       agent_finished_at=(result.get('agent_execution') or {}).get('finished_at'),
                       agent_seconds=elapsed(result.get('agent_execution')), total_seconds=elapsed(result),
                       environment_setup_seconds=elapsed(result.get('environment_setup')),
                       agent_setup_seconds=elapsed(result.get('agent_setup')), verifier_seconds=elapsed(result.get('verifier')),
                       raw_reward=(result.get('verifier_result') or {}).get('rewards', {}).get('reward'))
            assert len(row['controls']) == 2
            assert all(c['task_checksum'] == row['task_checksum'] for c in row['controls'].values())
            usage = result.get('agent_result') or {}
            row['input_tokens'] = usage.get('n_input_tokens')
            row['cached_input_tokens'] = usage.get('n_cache_tokens')
            row['output_tokens'] = usage.get('n_output_tokens')
            row['uncached_input_tokens'] = (row['input_tokens'] - row['cached_input_tokens']
                                            if row['input_tokens'] is not None and row['cached_input_tokens'] is not None else None)
            assert row['uncached_input_tokens'] is None or row['uncached_input_tokens'] >= 0
            row['estimated_cost_usd'] = usage.get('cost_usd')
            row['client_error_events'] = []
            client_log = path.parent / 'agent/codex.txt'
            if client_log.exists():
                for line in client_log.read_text().splitlines():
                    try:
                        event = json.loads(line)
                    except ValueError:
                        continue
                    item = event.get('item') or {}
                    if event.get('type') == 'error' or item.get('type') == 'error':
                        row['client_error_events'].append(event.get('message') or item.get('message'))
            row['transport_recovery_observed'] = any(
                message and any(term in message.lower() for term in ['reconnecting', 'websocket', 'https transport'])
                for message in row['client_error_events'])
            row['reasoning_output_tokens'] = None
            row['token_accounting'] = {'basis': 'Harbor agent_result; matched legacy runtime event when available'}
            legacy = record_usage = None
            runtime_contexts = []
            for session_path in sorted((path.parent / 'agent/sessions').rglob('*.jsonl')):
                for line in session_path.read_text().splitlines():
                    try:
                        event = json.loads(line)
                    except ValueError:
                        continue
                    payload = event.get('payload') or {}
                    if event.get('type') == 'turn_context':
                        context = {key: payload[key] for key in ['model', 'effort', 'reasoning_effort'] if key in payload}
                        if context and context not in runtime_contexts:
                            runtime_contexts.append(context)
                    if event.get('type') == 'event_msg' and payload.get('type') == 'token_count':
                        candidate = (payload.get('info') or {}).get('total_token_usage') or {}
                        if all(candidate.get(runtime) == row.get(field) for runtime, field in
                               [('input_tokens', 'input_tokens'), ('cached_input_tokens', 'cached_input_tokens'), ('output_tokens', 'output_tokens')]):
                            legacy = {'timestamp': event.get('timestamp'), 'usage': candidate,
                                      'path': str(session_path.relative_to(ROOT)), 'sha256': sha(session_path)}
                    elif event.get('type') == 'token_usage_record':
                        record_usage = payload.get('thread_token_usage')
            if legacy:
                row['reasoning_output_tokens'] = legacy['usage'].get('reasoning_output_tokens')
                row['token_accounting']['matching_legacy_event'] = legacy
            row['runtime_model_contexts'] = runtime_contexts
            row['runtime_contexts_match_requested'] = bool(runtime_contexts) and all(
                c.get('model', '').removeprefix('openai/') == 'gpt-5.6-sol'
                and c.get('effort', c.get('reasoning_effort')) == 'xhigh' for c in runtime_contexts)
            if runtime_contexts:
                assert row['runtime_contexts_match_requested'], 'Runtime model configuration mismatch'
            if record_usage:
                row['token_accounting']['last_record_stream_usage'] = record_usage
                row['token_accounting']['record_stream_differs_from_harbor'] = any(
                    record_usage.get(key) != row.get(key) for key in ['input_tokens', 'cached_input_tokens', 'output_tokens'])
            details_path = path.parent / 'verifier/details.json'
            row['grade'] = json.loads(details_path.read_text()) if details_path.exists() else None
            row['grade_sha256'] = sha(details_path) if details_path.exists() else None
            if row['grade'] and row['grade'].get('cases'):
                grade = row['grade']['cases'][0]
                row['finding_diagnostics'] = {'expected_labels': grade['expected_positive_labels'],
                                              'positive_labels_named': grade['expected_positive_labels'] - len(grade['missing']),
                                              'positive_labels_located': len(grade['located']),
                                              'missing': grade['missing'], 'extra': grade['extra'], 'bad_points': grade['bad_points']}
            answer = path.parent / 'artifacts/app/answer/findings.json'
            row['artifact_exists'] = answer.exists()
            if answer.exists():
                row.update(artifact_path=str(answer.relative_to(ROOT)), artifact_sha256=sha(answer),
                           artifact_equals_starter=answer.read_bytes() == (ROOT / task['task_path'] / 'environment/findings.json').read_bytes())
                try:
                    def unique(pairs):
                        value = {}
                        for key, item in pairs:
                            if key in value:
                                raise ValueError('duplicate JSON key')
                            value[key] = item
                        return value
                    if answer.stat().st_size > 200000:
                        raise ValueError('answer exceeds 200 KB')
                    prediction = json.loads(answer.read_text(), object_pairs_hook=unique)
                    row['submission'] = prediction
                    tests = ROOT / task['task_path'] / 'tests'
                    spec = importlib.util.spec_from_file_location('task_scoring', tests / 'scoring.py')
                    scoring = importlib.util.module_from_spec(spec); spec.loader.exec_module(scoring)
                    truth = json.loads((tests / 'expected.json').read_text())
                    regions = np.load(tests / 'regions.npz', allow_pickle=False)
                    reproduced = scoring.score(prediction, truth, regions)
                    wanted = {f['label']: f['region_key'] for f in truth['cases'][0]['findings']}
                    distances = {}
                    for f in prediction['cases'][0]['findings']:
                        if f['label'] not in wanted:
                            continue
                        point = np.asarray(f.get('point_lps_mm', []), dtype=float)
                        if point.shape == (3,) and np.isfinite(point).all():
                            distances.setdefault(f['label'], []).append(float(np.sqrt(np.sum((regions[wanted[f['label']]] - point) ** 2, axis=1)).min()))
                    row['nearest_discrepancy_distance_mm'] = distances
                except Exception as exc:
                    reproduced = {'passed': False, 'execution_error': str(exc)}
                row['independent_rescore_matches'] = reproduced == row['grade']
                assert row['independent_rescore_matches'], task['case_id']
            trajectory = path.parent / 'agent/trajectory.json'
            row['tool_wrappers'] = row['image_review_wrappers'] = None
            row['seconds_to_first_image_review'] = row['observed_image_blocks'] = None
            if trajectory.exists():
                trace = json.loads(trajectory.read_text())
                calls = [call for step in trace.get('steps', []) for call in step.get('tool_calls', [])]
                row['tool_wrappers'] = len(calls)
                row['image_review_wrappers'] = sum('view_image' in json.dumps(call) for call in calls)
                first_image = next((step.get('timestamp') for step in trace.get('steps', [])
                                    if any('view_image' in json.dumps(call) for call in step.get('tool_calls', []))), None)
                if first_image and row['agent_started_at']:
                    row['seconds_to_first_image_review'] = (datetime.fromisoformat(first_image) - datetime.fromisoformat(row['agent_started_at'])).total_seconds()
                row['observed_image_blocks'] = sum(json.dumps(step.get('observation', {})).count('data:image/') for step in trace.get('steps', []))
                row['trajectory_sha256'] = sha(trajectory)
            row['raw_outcome'] = ('pass' if row['raw_reward'] == 1 else 'miss') if row['execution'] == 'completed' else row['execution']
            row['validity'] = ('source truth hold' if row['source_truth_hold'] else 'review required' if row['raw_outcome'] == 'miss' else
                               'execution excluded' if row['execution'] != 'completed' else 'completed raw pass')
            if task['case_id'] in reviews:
                row['authored_review'] = reviews[task['case_id']]
                row['validity'] = reviews[task['case_id']]['validity']
                row['post_trial_source_truth_hold'] = bool(reviews[task['case_id']].get('source_truth_hold') and not row['source_truth_hold'])
        rows.append(row)
    return rows

def render(summary):
    rows = summary['rows']
    table, details = [], []
    for row in rows:
        cid = row['case_id']
        def show(key, fmt):
            value = row.get(key)
            return '—' if value is None else format(value, fmt)
        table.append(f'''<tr><td><a href="#{cid}">{cid}</a><small>{row['task_kind']}</small></td>
<td>{row.get('raw_outcome', 'pending')}<small>{row.get('validity', '')}</small></td>
<td>{show('agent_seconds', ',.1f')}</td><td>{show('output_tokens', ',')}</td>
<td>{show('uncached_input_tokens', ',')}</td><td>{show('cached_input_tokens', ',')}</td>
<td>{show('estimated_cost_usd', '.3f')}</td></tr>''')
        figures = ''
        for path in sorted((ROOT / 'runs/br004-v1/evidence-images').glob(cid + '-*.png')):
            figures += f'<figure><img src="../br004-v1/evidence-images/{html.escape(path.name)}" alt="CT, source and submitted annotations"><figcaption>Author comparison: {html.escape(path.stem)}</figcaption></figure>'
        review_path = ROOT / f'docs/evidence/br004-sol-{cid}-review.json'
        if review_path.exists():
            reviewed = json.loads(review_path.read_text())
            image_path = reviewed.get('author_viewed_image')
            if image_path:
                caption = reviewed.get('author_viewed_image_kind', 'Image actually delivered to Sol, retained from its completed trace.')
                figures += f'<figure><img loading="lazy" src="../../{html.escape(image_path)}" alt="Reviewed image evidence"><figcaption>{html.escape(caption)}</figcaption></figure>'
        details.append(f'<details id="{cid}"><summary>{cid}: exact result and retained evidence</summary>{figures}<pre>{html.escape(json.dumps(row, indent=2))}</pre></details>')
    totals = summary['observed_totals']
    page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BR-004 · Corrected-scope Sol follow-up</title><style>
:root{color-scheme:dark;font:16px/1.6 system-ui;background:#10191e;color:#e1edf2}body{max-width:1250px;margin:auto;padding:32px 24px}h1{line-height:1.2}a{color:#91dfcd}small{display:block;color:#a7bac4;font-size:12px}.note{padding:18px;background:#1a2c35;border-left:3px solid #91dfcd;margin:22px 0}table{border-collapse:collapse;width:100%;font-size:14px}td,th{padding:12px;text-align:left;border-bottom:1px solid #344a55}.table{overflow:auto}details{margin:18px 0;border:1px solid #344a55;padding:18px;border-radius:8px}summary{cursor:pointer}pre{overflow:auto;font-size:12px}img{max-width:100%}figure{margin:20px 0}figcaption{font-size:12px;color:#a7bac4}</style>
<p>BR-004 / ONE ATTEMPT PER TASK</p><h1>Corrected-scope Sol follow-up</h1>'''
    page += f'<p>Sol / xhigh · sequential · 30-minute allowance · {summary["completed_attempts"]}/4 finished</p>'
    page += f'<p><b>{totals["raw_passes"]} passes · {totals["reviewed_genuine_misses"]} reviewed misses · {totals["source_truth_holds"]} source holds · {totals["execution_exclusions"]} execution exclusions</b><br>{totals["agent_seconds"]/60:.1f} agent minutes · {totals["output_tokens"]:,} output tokens · ${totals["estimated_cost_usd"]:.3f} estimated cost</p>'
    page += '<div class="note">Cases 32 and 83 use the exact earlier Terra task bytes. Cases 46-v2 and 61-v2 publish exclusions for unresolved source regions; their CT/SEG data and planted errors are unchanged. These revised tasks cannot isolate a model effect from a scope change. A single attempt measures an outcome, not a failure probability.</div>'
    page += '<p><a href="../../docs/research-rounds/BR-004-sol-followup.md">Frozen protocol</a> · <a href="../../docs/evidence/br004-sol-freeze.json">Freeze</a> · <a href="benchmark.csv">CSV</a> · <a href="benchmark.json">Full JSON</a> · <a href="../br004-single/report.html">Earlier Terra screen</a></p>'
    if summary.get('conclusion'):
        page += '<div class="note">' + html.escape(summary['conclusion']) + '</div>'
    page += '<h2>Observed resources</h2><p>Agent seconds exclude setup and grading. Cached input is reported separately from uncached input. Reasoning is included in output. Cost is Harbor’s estimate.</p><div class="table"><table><thead><tr><th>Task</th><th>Outcome</th><th>Agent seconds</th><th>Output tokens</th><th>Uncached input</th><th>Cached input</th><th>Est. USD</th></tr></thead><tbody>' + ''.join(table) + '</tbody></table></div>'
    page += '<h2>Terra comparison</h2><pre>' + html.escape(json.dumps(summary['terra_comparison'], indent=2)) + '</pre>'
    page += '<h2>Inspectable evidence</h2>' + ''.join(details)
    page += '<h2>Measurement limits</h2><ul>' + ''.join('<li>' + html.escape(x) + '</li>' for x in summary['limitations']) + '</ul></html>'
    (OUT / 'report.html').write_text(page)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--final', action='store_true')
    args = parser.parse_args()
    plan = json.loads(PLAN.read_text())
    assert sha(Path(__file__).with_name('build.py')) == plan['builder_sha256']
    assert sha(ROOT / plan['protocol_path']) == plan['protocol_sha256']
    assert sha(ROOT / plan['author_controls_path']) == plan['author_controls_sha256']
    for task in plan['tasks']:
        for prefix in ['task_path', 'execution_snapshot']:
            assert all(sha(ROOT / task[prefix] / name) == value for name, value in task['files'].items())
    rows = collect(plan)
    complete = [r for r in rows if r['execution'] != 'pending']
    timed = [r for r in complete if r.get('agent_finished_at') and r.get('agent_started_at')]
    sequential = all(a['agent_finished_at'] <= b['agent_started_at'] for a, b in zip(timed, timed[1:]))
    assert sequential
    for row in complete:
        assert row['model'] == 'openai/gpt-5.6-sol' and row['reasoning_effort'] == 'xhigh'
    summary = {'round': 'BR-004', 'condition': 'sol-corrected-scope-v1', 'captured_at': datetime.now(timezone.utc).isoformat(),
               'freeze_sha256': sha(PLAN), 'rows': rows, 'completed_attempts': len(complete),
               'model_attempts_per_task': 1, 'frozen_files_unchanged': True, 'model_execution_sequential': sequential,
               'limitations': ['One attempt per task; no success probability or causal optimization estimate.',
                   'Only 32 and 83 use identical task bytes across Terra and Sol. The 46/61 comparison also changes audit scope.',
                   'Source regions excluded in 46/61 remain anatomically unadjudicated. New in-scope allegations require review.',
                   'Input includes cached input; reasoning is included in output. Costs are estimates, not invoices.',
                   'Reasoning tokens use a legacy runtime counter matching Harbor totals. Other record-stream totals are retained separately.',
                   'Timeouts and execution errors are not genuine model failures.',
                   'CPU/RAM limits are fixed; actual CPU-seconds and peak memory were not measured.',
                   'Trials are sequential within this study; host load and provider latency were not experimentally isolated.',
                   'Client transport recovery is retained per row. Such wall times include connection disruption; token/cost values remain the reported client/harness scope.',
                   'No specialist clinical certification or confirmed postoperative cohort.']}
    totals = {'finished_attempts': len(complete), 'normally_completed': sum(r['execution'] == 'completed' for r in complete),
              'raw_passes': sum(r['raw_outcome'] == 'pass' for r in complete), 'raw_misses': sum(r['raw_outcome'] == 'miss' for r in complete),
              'reviewed_genuine_misses': sum(r.get('authored_review', {}).get('outcome') == 'genuine_failure' for r in complete),
              'source_truth_holds': sum(r['source_truth_hold'] or r['post_trial_source_truth_hold'] for r in complete),
              'execution_exclusions': sum(r['execution'] != 'completed' for r in complete)}
    for field in ['agent_seconds', 'total_seconds', 'input_tokens', 'cached_input_tokens', 'uncached_input_tokens',
                  'output_tokens', 'reasoning_output_tokens', 'estimated_cost_usd', 'controls_total_seconds']:
        values = [r[field] for r in complete if r.get(field) is not None]
        totals[field] = sum(values)
        totals[field + '_available_attempts'] = len(values)
    summary['observed_totals'] = totals
    events = json.loads((OUT / 'execution-events.json').read_text())
    end = next((e for e in reversed(events) if e.get('status') == 'all_four_model_attempts_finished'), None)
    if end:
        summary['benchmark_wall_seconds'] = (datetime.fromisoformat(end['at']) - datetime.fromisoformat(events[0]['at'])).total_seconds()
    prior = json.loads((ROOT / 'docs/evidence/br004-single-patient-summary.json').read_text())
    comparison = []
    for row in rows:
        old = next(r for r in prior['rows'] if r['case_id'] == row['case_id'])
        checksum_equal = row.get('task_checksum') == old['task_checksum'] if row.get('task_checksum') else None
        if row['task_bytes_unchanged_from_terra'] and checksum_equal is not None:
            assert checksum_equal, 'Unchanged cross-model tasks must share a Harbor checksum'
        comparison.append({'case_id': row['case_id'], 'task_bytes_identical': row['task_bytes_unchanged_from_terra'],
                           'harbor_task_checksums_equal': checksum_equal,
                           'terra_outcome': old['raw_outcome'], 'terra_validity': old['validity'],
                           'terra_agent_seconds': old['agent_seconds'], 'terra_output_tokens': old['output_tokens'],
                           'terra_estimated_cost_usd': old['estimated_cost_usd'], 'sol_outcome': row.get('raw_outcome', 'pending'),
                           'sol_agent_seconds': row.get('agent_seconds'), 'sol_output_tokens': row.get('output_tokens'),
                           'sol_estimated_cost_usd': row.get('estimated_cost_usd')})
    summary['terra_comparison'] = comparison
    conclusion_path = OUT / 'conclusion.txt'
    if conclusion_path.exists():
        summary['conclusion'] = conclusion_path.read_text().strip()
    (OUT / 'benchmark.json').write_text(json.dumps(summary, indent=2) + '\n')
    fields = ['task_id', 'case_id', 'task_kind', 'expected_positive_labels', 'focus_label_count', 'execution', 'raw_outcome', 'validity',
              'raw_reward', 'agent_seconds', 'total_seconds', 'controls_total_seconds', 'environment_setup_seconds', 'agent_setup_seconds',
              'verifier_seconds', 'input_tokens', 'cached_input_tokens', 'uncached_input_tokens', 'output_tokens', 'reasoning_output_tokens',
              'estimated_cost_usd', 'tool_wrappers', 'image_review_wrappers', 'seconds_to_first_image_review', 'observed_image_blocks',
              'source_truth_hold', 'post_trial_source_truth_hold', 'task_bytes_unchanged_from_terra', 'result_path']
    fields.insert(-1, 'transport_recovery_observed')
    with (OUT / 'benchmark.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)
    render(summary)
    if args.final:
        assert len(complete) == 4 and end, 'All four attempts must finish'
        assert all(r.get('authored_review') for r in complete), 'Every outcome needs authored review'
        final = ROOT / 'docs/evidence/br004-sol-summary.json'
        assert not final.exists(), 'Preserve final evidence once written'
        final.write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps([{'case': r['case_id'], 'outcome': r.get('raw_outcome', 'pending'), 'seconds': r.get('agent_seconds'), 'output_tokens': r.get('output_tokens')} for r in rows]))


if __name__ == '__main__':
    main()
