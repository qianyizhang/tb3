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
OUT = ROOT / 'runs/br004-single'
PLAN = ROOT / 'docs/evidence/br004-single-patient-freeze.json'
TASK_KINDS = {
    'case-74': 'Limited-coverage control',
    'case-19': 'Thoracic-abnormality control',
    'case-83': 'Kidney-pole omission',
    'case-46': 'Pathology control; source hold',
    'case-28': 'Local rib-identity exchange',
    'case-61': 'Heart-apex omission',
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
    job = ROOT / 'runs' / f'br004-single-{case_id.split("-")[1]}-{phase}-v1-20260915'
    paths = list(job.glob('*/result.json'))
    assert len(paths) <= 1, 'More than one trial violates the declared protocol'
    if not paths:
        return None, None
    return paths[0], json.loads(paths[0].read_text())

def collect(plan):
    rows = []
    review_path = ROOT / 'docs/evidence/br004-single-patient-reviews.json'
    reviews = json.loads(review_path.read_text()).get('reviews', {}) if review_path.exists() else {}
    for task in plan['tasks']:
        row = {key: task[key] for key in ['task_id', 'case_id', 'focus_label_count', 'expected_positive_labels', 'source_truth_hold']}
        row['task_kind'] = TASK_KINDS[task['case_id']]
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
        path, result = result_for(task['case_id'], 'terra-max')
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
            row['reasoning_output_tokens'] = None
            row['token_accounting'] = {'basis': 'Harbor agent_result; matched legacy runtime event when available'}
            legacy = record_usage = None
            for session_path in sorted((path.parent / 'agent/sessions').rglob('*.jsonl')):
                for line in session_path.read_text().splitlines():
                    try:
                        event = json.loads(line)
                    except ValueError:
                        continue
                    payload = event.get('payload') or {}
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
                            distances[f['label']] = float(np.sqrt(np.sum((regions[wanted[f['label']]] - point) ** 2, axis=1)).min())
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
    rows = summary['rows']; lines = []
    def number(value):
        return '—' if value is None else f'{value:,.0f}'
    def seconds(value):
        return '—' if value is None else f'{value / 60:.2f} min'
    for row in rows:
        state = row.get('raw_outcome', 'pending')
        cost = '—' if row.get('estimated_cost_usd') is None else f'${row["estimated_cost_usd"]:.3f}'
        lines.append(f'<tr class="{state}" onclick="document.getElementById(\'{row["case_id"]}\').open=true;document.getElementById(\'{row["case_id"]}\').scrollIntoView()"><td>{row["case_id"]}<small>{row["task_kind"]}</small></td><td>{row["expected_positive_labels"]}</td><td>{state}<small>{row.get("validity", "")}</small></td><td>{seconds(row.get("agent_seconds"))}</td><td>{number(row.get("output_tokens"))}</td><td>{number(row.get("input_tokens"))}<small>{number(row.get("cached_input_tokens"))} cached</small></td><td>{cost}</td></tr>')
    completed = [r for r in rows if r['execution'] != 'pending']
    details = []
    for row in rows:
        body = html.escape(json.dumps(row, indent=2))
        evidence = ''
        for path in sorted((ROOT / 'runs/br004-v1/evidence-images').glob(row['case_id'] + '-*.png')):
            evidence += f'<p>Author comparison: CT, source mask, and submitted task mask — {html.escape(path.stem)}.</p><img style="max-width:100%;height:auto" src="../br004-v1/evidence-images/{html.escape(path.name)}" alt="CT and mask comparison">'
        if row['case_id'] == 'case-83' and row.get('authored_review'):
            evidence += '<p>A coronal contact sheet actually viewed by Terra; this is retained from its trace.</p><img style="max-width:100%;height:auto" src="review/case-83-terra-kidney-coronal.png" alt="Kidney coronal views received by Terra">'
        if row['case_id'] == 'case-61' and row.get('authored_review'):
            evidence += '<p>Reported original-source regions viewed by Terra. These require source adjudication; they do not identify the planted inferior heart omission.</p><img style="max-width:100%;height:auto" src="review/case-61-terra-step-51-0.png" alt="Reported original liver gap"><img style="max-width:100%;height:auto" src="review/case-61-terra-step-59-0.png" alt="Reported original heart component">'
        if row['case_id'] == 'case-32' and row.get('authored_review'):
            evidence += '<p>Targeted kidney contact sheet actually viewed by Terra, retained from the completed trace.</p><img style="max-width:100%;height:auto" src="review/case-32-terra-kidneys-0.png" alt="Kidney views received by Terra">'
        details.append(f'<details id="{row["case_id"]}"><summary>{row["case_id"]}: {row.get("raw_outcome", "pending")}</summary>{evidence}<pre>{body}</pre></details>')
    plot_rows = [{'case': r['case_id'], 'x': r.get('output_tokens'), 'y': r.get('agent_seconds'), 'status': r.get('raw_outcome'), 'hold': r['source_truth_hold'] or r['post_trial_source_truth_hold']} for r in completed]
    plot_json = json.dumps(plot_rows).replace('<', '\\u003c')
    page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BR-004 · One patient per task</title><style>
:root{color-scheme:dark;font:16px/1.6 system-ui;background:#0c141a;color:#dfebf3}body{max-width:1200px;margin:0 auto;padding:32px 24px}h1{font-size:36px;letter-spacing:-1px;line-height:1.2}a{color:#78ddca}small{display:block;color:#a2b4c1;font-size:12px}.note{background:#1a2934;border-left:3px solid #78ddca;padding:18px 24px;margin:24px 0}table{border-collapse:collapse;width:100%;font-size:14px}th,td{text-align:left;padding:13px 12px;border-bottom:1px solid #2b3d49}tr{cursor:pointer}tr:hover{background:#1e2f3b}.pass td:nth-child(3){color:#79d8b9}.miss td:nth-child(3){color:#ff9296}.timeout td:nth-child(3){color:#e3c379}.pending{color:#889ca9}details{margin:16px 0;border:1px solid #2d414f;border-radius:10px;padding:16px}summary{cursor:pointer}pre{font-size:12px;overflow:auto;background:#0a1117;padding:16px}svg{width:100%;height:auto;background:#13202a;border-radius:12px}svg text{font-family:system-ui;fill:#b6c7d4;font-size:13px}.table{overflow-x:auto}.tag{color:#78ddca;font-size:13px;letter-spacing:.12em}</style>
<div class="tag">BR-004 / SINGLE-PATIENT CONDITION / ONE ATTEMPT EACH</div><h1>Difficulty and resource use,<br>one patient at a time.</h1>'''
    page += f'<p>{len(completed)}/8 attempts finished · Terra / max · sequential · 30-minute allowance per task</p>'
    totals = summary['observed_totals']
    page += f'<p><b>{totals["raw_passes"]} raw passes · {totals["reviewed_genuine_misses"]} reviewed misses · {totals["source_truth_holds"]} source hold(s)</b><br>{totals["agent_seconds"] / 60:.1f} agent minutes · {totals["output_tokens"]:,} output tokens · ${totals["estimated_cost_usd"]:.2f} estimated model cost across finished attempts.</p>'
    page += '<div class="note"><b>How to read this benchmark.</b> Success is the frozen exact-label and spatial-witness grade. A completed miss needs source/trace review before it counts as a genuine failure. Timeouts are excluded. Case-46 has a source-truth hold declared before testing; case-61 has an additional hold after review of its reported source regions. One trial is an observation, not a reliable success probability.</div>'
    page += '<p><a href="../../docs/research-rounds/BR-004-single-patient-benchmark.md">Protocol</a> · <a href="../../docs/evidence/br004-single-patient-freeze.json">Freeze</a> · <a href="benchmark.csv">Download CSV</a> · <a href="benchmark.json">Full JSON</a> · <a href="../br004-v1/report.html">Earlier batch timeout</a></p>'
    if len(completed) == 8:
        page += '<div class="note"><b>Best observed lead: case-32, the small kidney extension.</b> A reviewed miss in 10.21 agent minutes, 23,713 output tokens and about $0.857 estimated cost. It used 36% less time and 28% fewer output tokens than the other reviewed miss, case-83. The two source holds remain excluded from difficulty claims. <a href="../../catalog/analyses/br004-single-patient.md">Read the analysis and proposed next contrast</a>.</div>'
        page += f'<p>Whole sequential benchmark: {summary["benchmark_wall_seconds"] / 60:.1f} minutes from first control launch to final trial completion; includes {totals["controls_total_seconds"] / 60:.1f} minutes in oracle/nop controls. Model cost excludes these non-model controls and the earlier batch.</p>'
    page += '<h2>Observed outcomes</h2><p>Tokens are harness-reported. Cached input is included in total input. Cost is the Harbor estimate. Click a row for the exact grade and provenance.</p><div class="table"><table><thead><tr><th>Task</th><th>Planted labels</th><th>Raw outcome</th><th>Agent time</th><th>Output tokens</th><th>Input tokens</th><th>Est. cost</th></tr></thead><tbody>'+''.join(lines)+'</tbody></table></div>'
    page += '<h2>Time versus output tokens</h2><p>Green: completed pass. Red: completed raw miss; see its review status. Amber: timeout. Purple outline: source hold (predeclared or discovered during review). Lower-left means fewer resources; only a valid completed miss can support the desired difficulty claim.</p><svg id="plot" viewBox="0 0 960 460"></svg>'
    page += '<h2>Exact results</h2>'+''.join(details)
    page += '<script>const rows='+plot_json+''';const svg=document.getElementById('plot');const ns='http://www.w3.org/2000/svg';function el(t,a,txt){const e=document.createElementNS(ns,t);Object.entries(a).forEach(([k,v])=>e.setAttribute(k,v));if(txt)e.textContent=txt;svg.append(e);return e}const data=rows.filter(r=>r.x!=null&&r.y!=null);const xm=Math.max(1000,...data.map(r=>r.x))*1.12,ym=Math.max(60,...data.map(r=>r.y))*1.12;for(let i=0;i<5;i++){const x=70+i*205,y=390-i*85;el('line',{x1:70,y1:y,x2:890,y2:y,stroke:'#2b3d49'});el('text',{x:60,y:y+4,'text-anchor':'end'},(i*ym/4/60).toFixed(1));el('text',{x,y:418,'text-anchor':'middle'},(i*xm/4/1000).toFixed(1)+'k')}el('text',{x:460,y:450,'text-anchor':'middle'},'Output tokens');el('text',{x:14,y:230,transform:'rotate(-90 14 230)','text-anchor':'middle'},'Agent minutes');data.forEach(r=>{const x=70+r.x/xm*820,y=390-r.y/ym*340;const c=el('circle',{cx:x,cy:y,r:7,fill:r.status==='pass'?'#79d8b9':r.status==='miss'?'#ff9296':'#e3c379',stroke:r.hold?'#c99eff':'none','stroke-width':3});c.onclick=()=>{const d=document.getElementById(r.case);d.open=true;d.scrollIntoView()};el('text',{x:x+10,y:y-8},r.case)})</script></html>'''
    (OUT / 'report.html').write_text(page)

def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--final', action='store_true'); args = parser.parse_args()
    plan = json.loads(PLAN.read_text()); rows = collect(plan)
    assert sha(Path(__file__).with_name('build.py')) == plan['builder_sha256']
    assert sha(ROOT / 'docs/research-rounds/BR-004-single-patient-benchmark.md') == plan['protocol_sha256']
    complete = [r for r in rows if r['execution'] != 'pending']
    for task in plan['tasks']:
        for prefix in ['task_path', 'execution_snapshot']:
            assert all(sha(ROOT / task[prefix] / name) == value for name, value in task['files'].items())
    timed = [r for r in complete if r.get('agent_finished_at') and r.get('agent_started_at')]
    sequential = all(a['agent_finished_at'] <= b['agent_started_at'] for a, b in zip(timed, timed[1:]))
    assert sequential
    summary = {'round': 'BR-004', 'condition': 'single-patient-v1', 'captured_at': datetime.now(timezone.utc).isoformat(),
               'freeze_sha256': sha(PLAN), 'rows': rows, 'completed_attempts': len(complete),
               'model_attempts_per_task': 1, 'frozen_files_unchanged': True, 'model_execution_sequential': sequential,
               'limitations': ['One attempt per task; no success-probability or causal optimization estimate.',
                              'Case-46 source-truth hold predeclared; all completed misses require review.',
                              'Input includes cached input. Missing usage is unavailable. Estimated cost is not an invoice.',
                              'Reasoning output is included in output, and reported only from a runtime counter matching Harbor totals. Other record-stream totals may differ; retain them without mixing scopes.',
                              'Timeout time is censored; unfinished artifact grades are not considered final findings.',
                              'Time to first image is a trace-derived interval, not a direct measurement of rendering CPU time. Image blocks may include repeated views.',
                              'CPU/RAM limits are fixed; actual CPU-seconds and peak resident memory were not measured.',
                              'No specialist clinical certification or confirmed postoperative cohort.']}
    summary['observed_totals'] = {
        'finished_attempts': len(complete),
        'normally_completed': sum(r['execution'] == 'completed' for r in complete),
        'raw_passes': sum(r['raw_outcome'] == 'pass' for r in complete),
        'raw_misses': sum(r['raw_outcome'] == 'miss' for r in complete),
        'reviewed_genuine_misses': sum(r.get('authored_review', {}).get('outcome') == 'genuine_failure' for r in complete),
        'source_truth_holds': sum(r['source_truth_hold'] or r['post_trial_source_truth_hold'] for r in complete),
        'predeclared_source_truth_holds': sum(r['source_truth_hold'] for r in complete),
        'post_trial_source_truth_holds': sum(r['post_trial_source_truth_hold'] for r in complete),
        'execution_exclusions': sum(r['execution'] != 'completed' for r in complete),
    }
    for field in ['agent_seconds', 'total_seconds', 'input_tokens', 'cached_input_tokens',
                  'uncached_input_tokens', 'output_tokens', 'reasoning_output_tokens', 'estimated_cost_usd', 'controls_total_seconds']:
        values = [r[field] for r in complete if r.get(field) is not None]
        summary['observed_totals'][field] = sum(values)
        summary['observed_totals'][field + '_available_attempts'] = len(values)
        summary['observed_totals'][field + '_median'] = statistics.median(values) if values else None
    events = json.loads((OUT / 'execution-events.json').read_text())
    final_event = next((e for e in reversed(events) if e.get('status') == 'finished' and e.get('case_id') == 'case-32' and e.get('phase') == 'terra-max'), None)
    if len(complete) == 8 and final_event:
        summary['benchmark_wall_seconds'] = (datetime.fromisoformat(final_event['at']) - datetime.fromisoformat(events[0]['at'])).total_seconds()
        summary['benchmark_wall_definition'] = 'First control launch to final model trial completion, including sequential controls and setup; excludes report authoring and earlier batch.'
    prior_path = ROOT / 'runs/br004-anatomy-terra-max-v1-20260915/dicom-anatomy-audit__cZPMKGf/result.json'
    prior = json.loads(prior_path.read_text()); usage = prior.get('agent_result') or {}
    summary['prior_batch'] = {'interpretation': 'Eight-patient timeout with unchanged empty starter; cost context only, not an accuracy baseline.',
                              'result_path': str(prior_path.relative_to(ROOT)), 'result_sha256': sha(prior_path),
                              'agent_seconds': elapsed(prior.get('agent_execution')), 'total_seconds': elapsed(prior),
                              'input_tokens': usage.get('n_input_tokens'), 'cached_input_tokens': usage.get('n_cache_tokens'),
                              'output_tokens': usage.get('n_output_tokens'), 'estimated_cost_usd': usage.get('cost_usd')}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'benchmark.json').write_text(json.dumps(summary, indent=2) + '\n')
    fields = ['task_id','case_id','task_kind','expected_positive_labels','focus_label_count','execution','raw_outcome','validity','raw_reward','agent_seconds','total_seconds','controls_total_seconds','environment_setup_seconds','agent_setup_seconds','verifier_seconds','input_tokens','cached_input_tokens','uncached_input_tokens','output_tokens','reasoning_output_tokens','estimated_cost_usd','tool_wrappers','image_review_wrappers','seconds_to_first_image_review','observed_image_blocks','source_truth_hold','post_trial_source_truth_hold','result_path']
    with (OUT / 'benchmark.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore'); writer.writeheader(); writer.writerows(rows)
    render(summary)
    if args.final:
        assert len(complete) == 8, 'Final summary requires all eight attempts'
        (ROOT / 'docs/evidence/br004-single-patient-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps([{'case': r['case_id'], 'outcome': r.get('raw_outcome', 'pending'), 'seconds': r.get('agent_seconds'), 'output_tokens': r.get('output_tokens')} for r in rows]))

if __name__ == '__main__':
    main()
