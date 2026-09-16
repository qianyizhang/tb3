"""Allowlisted BR-023 receipts; independently regrade every new submission."""
import json
from pathlib import Path
from collect import read, sha, seconds
from br023_run_trials import verify
from score import score

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'runs/br023-sol-registration'


def main():
    plan = read(OUT / 'plan.json')
    assert sha(ROOT / plan['protocol_path']) == plan['protocol_sha256']
    assert sha(ROOT / 'runs/br021-deformable/freeze.json') == plan['original_freeze_sha256']
    assert (OUT / 'plan.json').read_bytes() == (ROOT / 'docs/evidence/br023-plan.json').read_bytes()
    for path, expected in plan['prior_results_sha256'].items():
        assert sha(ROOT / path) == expected
    for task in read(ROOT / 'runs/br021-deformable/freeze.json')['tasks']:
        verify(task)
    task = plan['task']
    truth = read(ROOT / task['task_path'] / 'tests/truth.json')
    instruction = (ROOT / task['task_path'] / 'instruction.md').read_text().strip()
    rows = []
    for phase in ['oracle', 'nop', 'sol-xhigh']:
        paths = list((ROOT / 'runs' / f'br023-deform-2d-{phase}-v1-20260916').glob('*/result.json'))
        assert len(paths) == 1
        file = paths[0]
        result = read(file)
        assert result.get('finished_at')
        exception = result.get('exception_info') or {}
        metrics = file.parent / 'verifier/metrics.json'
        answer = file.parent / 'artifacts/app/answer/points.json'
        grade = read(metrics) if metrics.exists() else None
        regrade = score(read(answer) if answer.exists() else {}, truth)
        if grade:
            assert grade['reward'] == regrade['reward']
            for key in ['rms_mm', 'max_mm']:
                if key in regrade:
                    assert abs(grade[key] - regrade[key]) < 1e-6
        usage = result.get('agent_result') or {}
        row = {
            'task': 'deform-2d', 'phase': phase,
            'result_path': str(file.relative_to(ROOT)), 'result_sha256': sha(file),
            'task_checksum': result['task_checksum'],
            'execution': 'timeout' if exception.get('exception_type') == 'AgentTimeoutError' else 'execution_error' if exception else 'completed',
            'exception_type': exception.get('exception_type'),
            'reward': (result.get('verifier_result') or {}).get('rewards', {}).get('reward'),
            'grade': grade, 'independent_replay_matches': bool(grade),
            'started_at': result.get('started_at'), 'finished_at': result.get('finished_at'),
            'agent_seconds': seconds(result.get('agent_execution')), 'total_seconds': seconds(result),
            'input_tokens': usage.get('n_input_tokens'), 'cached_input_tokens': usage.get('n_cache_tokens'),
            'output_tokens': usage.get('n_output_tokens'), 'estimated_cost_usd': usage.get('cost_usd'),
        }
        if answer.exists():
            row.update(answer_path=str(answer.relative_to(ROOT)), answer_sha256=sha(answer))
        if metrics.exists():
            row['grade_sha256'] = sha(metrics)
        if phase.startswith('sol-'):
            contexts, sessions, seen = [], [], False
            for session in sorted((file.parent / 'agent/sessions').rglob('*.jsonl')):
                sessions.append({'path': str(session.relative_to(ROOT)), 'sha256': sha(session)})
                for line in session.read_text().splitlines():
                    try:
                        event = json.loads(line)
                    except ValueError:
                        continue
                    payload = event.get('payload') or {}
                    if event.get('type') == 'turn_context':
                        context = {k: payload[k] for k in ['model', 'effort', 'reasoning_effort'] if k in payload}
                        if context and context not in contexts:
                            contexts.append(context)
                    if event.get('type') == 'response_item' and payload.get('role') == 'user':
                        content = payload.get('content', [])
                        if isinstance(content, list):
                            seen |= any(instruction in x.get('text', '') for x in content if isinstance(x, dict))
            config = result['config']['agent']
            row.update(requested_model=config['model_name'], requested_effort=config['kwargs']['reasoning_effort'],
                       runtime_contexts=contexts, session_files=sessions, frozen_instruction_seen=seen,
                       runtime_matches_request=bool(contexts) and all(
                           c.get('model', '').removeprefix('openai/') == 'gpt-5.6-sol'
                           and c.get('effort', c.get('reasoning_effort')) == 'xhigh' for c in contexts))
            if row['execution'] == 'completed':
                assert row['runtime_matches_request'] and seen
        rows.append(row)
    assert len({r['task_checksum'] for r in rows}) == 1
    assert rows[0]['reward'] == 1 and rows[1]['reward'] == 0
    audit = read(OUT / 'bench-audit.json')
    assert audit['status'].startswith('completed') and audit['completed_at']
    assert audit['runner_exit_code'] == 0
    assert audit['plan_protocol_freeze_and_task_membership_unchanged']
    assert audit['plan_sha256'] == sha(OUT / 'plan.json')
    for phase in ['sol-xhigh']:
        check = audit['replications'][phase]
        assert check['frozen_task_membership_unchanged']
        assert check['image_audit']['public_files_match_plan']
        row = next(r for r in rows if r['phase'] == phase)
        assert check['result']['result_sha256'] == row['result_sha256']
    original = next(r for r in read(ROOT / 'docs/evidence/br021-results.json')['rows']
                    if r['task'] == 'deform-2d' and r['phase'] == 'terra-high')
    assert original['task_checksum'] == rows[0]['task_checksum']
    assert sha(ROOT / original['answer_path']) == original['answer_sha256']
    assert sha(ROOT / original['result_path']) == original['result_sha256']
    receipt = {
        'round': 'BR-023', 'plan_sha256': sha(OUT / 'plan.json'),
        'protocol_sha256': plan['protocol_sha256'],
        'original_freeze_sha256': plan['original_freeze_sha256'],
        'original_frozen_2d_and_3d_files_and_membership_unchanged': True,
        'retrospective_selected_attempt': original,
        'historical_terra_replications': [r for r in read(ROOT / 'docs/evidence/br022-results.json')['prospective_rows']
                                          if r['phase'].startswith('terra-')],
        'prospective_rows': rows, 'bench_audit': audit,
        'bench_audit_sha256': sha(OUT / 'bench-audit.json'),
        'limitations': [
            'One Sol/xhigh attempt on one selected case does not estimate success rate or isolate model ability from effort and strategy differences.',
            'The fresh Sol agent receives no prior answers, hints or author counterfactuals; later component interventions are separate author-run work.',
            'Truth is used only in independent grading and explicitly privileged geometric/objective diagnostics.',
            'Public annotations permit possible training contamination; image and recorded-trace audits cannot exclude it.',
            'Eight sparse points and engineering 3/5 mm tolerances do not establish dense-field or clinical validity.',
        ],
    }
    for path in [OUT / 'results.json', ROOT / 'docs/evidence/br023-results.json']:
        path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps([{k: r.get(k) for k in ['phase', 'execution', 'reward', 'grade', 'agent_seconds']} for r in rows], indent=2))


if __name__ == '__main__':
    main()
