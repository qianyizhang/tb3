"""Build the local presentation from authored analysis and verified frozen traces.

No model calls. Generated media/report stay in runs/; the compact trace index
and Markdown analysis expose source anchors without copying raw sessions.
"""
import ast
import base64
import hashlib
import html
import json
from pathlib import Path

from common import ROOT, OUT

HERE = Path(__file__).parent
DEST = OUT / 'review'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def escaped(value):
    return html.escape(str(value), quote=True)


def data_url(path):
    return 'data:image/png;base64,' + base64.b64encode(path.read_bytes()).decode()


def main():
    authored = json.loads((HERE / 'presentation.json').read_text())
    result_path = ROOT / 'docs/evidence/br017-results.json'
    results = json.loads(result_path.read_text())
    reviews = json.loads((ROOT / 'docs/evidence/br017-reviews.json').read_text())
    rows = {r['task']: r for r in results['rows'] if r['phase'] == 'sol-xhigh'}
    reviewed = {r['task']: r for r in reviews['tasks']}
    assert len(rows) == len(authored['trials']) == 4
    assert results['task_files_unchanged']
    DEST.mkdir(parents=True, exist_ok=True)
    trace_index = {'basis': authored['basis'], 'results_sha256': digest(result_path),
                   'authored_analysis_sha256': digest(HERE / 'presentation.json'), 'trials': []}
    md = ['# BR-017 — How Sol worked through each case', '',
          '[Experiment summary](BR-017-results.md) · [Interactive presentation](../../runs/br017-absorption/review/index.html)', '',
          authored['basis'], '',
          'Generated from the [authored analysis](../../probes/revisions/br017/authoring/presentation.json). '
          'Step numbers refer to each frozen trajectory; the [trace index](../evidence/br017-trace-index.json) records paths and hashes.', '',
          '## The shared workflow', '',
          'The agent was supplied with existing segmentations, proposed organ names, physical coordinates, full CT and rendering helpers. '
          'It combined Python measurements with image inspection and anatomical assessments, then wrote a small JSON answer. '
          'No specialist medical inference model or new training was invoked in these traces. The source masks were already provided.', '',
          '```text', 'Supplied masks + CT + proposed names', '                ↓',
          'Python measurements ⇄ targeted image sheets', '                ↓',
          'Anatomical assessment → further checks or revision', '                ↓',
          'Host + included organ + interior point (or empty list)', '```', '',
          'Measurements answer questions such as “is this connected?” or “is this subset larger than 5 mL?” '
          'They do not establish which organ owns the tissue. That judgment appears in the agent’s image-based assessments.', '']
    cards, table, details = [], [], []
    for trial in authored['trials']:
        key = 'abdomen-' + trial['id']; row = rows[key]; review = reviewed[key]
        assert row['execution'] == 'completed' and row['exception_type'] is None
        assert row['runtime_matches_request'] and row['session_file_count'] == 1
        assert bool(row['reward']) == (trial['verdict'] == 'Pass')
        raw = ROOT / row['result_path']; trajectory_path = raw.parent / 'agent/trajectory.json'
        assert digest(trajectory_path) == row['trajectory_sha256']
        assert digest(raw) == row['result_sha256']
        trajectory = json.loads(trajectory_path.read_text())
        steps = {s['step_id']: s for s in trajectory['steps']}
        anchors = sorted({n for stage in trial['stages'] for n in stage['steps']})
        assert all(n in steps for n in anchors)
        assert trial['quote'] in steps[trial['quote_step']]['message']
        # Cross-check public progress against the command/event logger.
        events = []
        for line in (raw.parent / 'agent/codex.txt').read_text().splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                continue
            item = event.get('item', {})
            if event.get('type') == 'item.completed' and item.get('type') in ('command_execution', 'agent_message'):
                events.append(item)
        assert any(trial['quote'] in e.get('text', '') for e in events)
        for measure in trial['measurements']:
            assert measure['contains'] in events[measure['item']]['aggregated_output']
        img = trial['image']; image_step = steps[img['step']]
        assert img['path'] in json.dumps(image_step['tool_calls'])
        payloads = []
        for observation in image_step['observation']['results']:
            blocks = ast.literal_eval(observation['content'])
            payloads.extend(b['image_url'] for b in blocks if b.get('type') == 'input_image')
        url = payloads[img['index']]
        assert url.startswith('data:image/png;base64,')
        image_bytes = base64.b64decode(url.partition(',')[2], validate=True)
        image_path = DEST / f"trace-{trial['id']}.png"
        image_path.write_bytes(image_bytes)
        trajectory_rel = str(trajectory_path.relative_to(ROOT))
        trace_index['trials'].append({
            'task': key, 'trajectory_path': trajectory_rel,
            'trajectory_sha256': row['trajectory_sha256'], 'steps': anchors,
            'public_quote_step': trial['quote_step'],
            'displayed_image': {'step': img['step'], 'index_within_returned_images': img['index'],
                                'solver_path': img['path'], 'local_path': str(image_path.relative_to(ROOT)),
                                'sha256': hashlib.sha256(image_bytes).hexdigest()},
            'command_count': review['command_count'],
            'images_returned': review['images_returned_as_input_image']})
        ident = trial['id'].upper(); verdict = trial['verdict']; cls = 'miss' if verdict == 'Miss' else 'pass'
        stats = f"{row['agent_seconds']:.0f} s · {review['images_returned_as_input_image']} images · {row['output_tokens']:,} output tokens"
        stages = ''.join(f'<li><h4>{escaped(s["title"])}</h4><p>{escaped(s["text"])}</p>'
                         f'<span class="anchor">Trace steps {", ".join(map(str, s["steps"]))}</span></li>' for s in trial['stages'])
        code = '\n'.join(trial['pseudocode'])
        answer = json.dumps(row['answer'], indent=2)
        cards.append(f'''<article id="{trial['id']}" class="trial" role="tabpanel" aria-labelledby="tab-{trial['id']}" {'hidden' if cards else ''}>
          <div class="trial-heading"><div><span class="eyebrow">{ident} / {escaped(trial['subtitle'])}</span><h3>{escaped(trial['headline'])}</h3></div><span class="badge {cls}">{verdict}</span></div>
          <p class="setup">{escaped(trial['setup'])}</p><div class="small stats">{stats}</div>
          <div class="trial-grid"><ol class="stages">{stages}</ol><aside>
            <figure class="trace-image"><button class="image-button" aria-label="Enlarge actual {ident} image sheet"><img src="{url}" alt="{escaped(img['caption'])}" loading="lazy"></button><figcaption>{escaped(img['caption'])}<br><span class="anchor">Step {img['step']} · click to enlarge</span></figcaption></figure>
            <blockquote>{escaped(trial['quote'])}<cite>{escaped(trial['quote_label'])} · step {trial['quote_step']}</cite></blockquote>
            <details><summary>Workflow in pseudocode</summary><p class="small">Reconstruction of observable actions.</p><pre>{escaped(code)}</pre></details>
            <details><summary>Final answer and tool recoveries</summary><pre>{escaped(answer)}</pre><p>{escaped(trial['recovery'])}</p></details>
          </aside></div><div class="interpretation"><span class="eyebrow">Interpretation</span><p>{escaped(trial['interpretation'])}</p></div>
          <details class="source"><summary>Trace provenance</summary><p>Steps refer to this completed trajectory. The displayed sheet is decoded directly from a returned image payload, with no new annotation.</p><code>{escaped(trajectory_rel)}</code><p class="hash">SHA-256 {row['trajectory_sha256']}</p></details></article>''')
        table.append(f'<tr data-trial="{trial["id"]}"><th>{ident}<span>{escaped(trial["title"])}</span></th><td><span class="badge {cls}">{verdict}</span></td><td>{row["agent_seconds"]:.1f} s</td><td>{review["images_returned_as_input_image"]}</td><td>{review["command_count"]}</td><td>{row["output_tokens"]:,}</td><td>${row["estimated_cost_usd"]:.3f}</td></tr>')
        details.append(f'<tr><th>{ident}</th><td>{row["total_seconds"]:.2f} s</td><td>{row["input_tokens"]:,}</td><td>{row["cached_input_tokens"]:,}</td><td>{row["reasoning_output_tokens"]:,}</td></tr>')
        md += [f'## {ident} · {trial["title"]} · {verdict}', '', f'**{trial["headline"]}.** {trial["setup"]}', '', stats + '.', '']
        for stage in trial['stages']:
            md += [f'### {stage["title"]}', '', stage['text'] + f' (Steps {", ".join(map(str, stage["steps"]))}.)', '']
        md += [f'> {trial["quote"]}', '', f'*Public message, step {trial["quote_step"]}.*', '',
               '```text', code, '```', '', '**Interpretation.** ' + trial['interpretation'], '',
               '**Tool recovery.** ' + trial['recovery'], '',
               f'[Actual returned image sheet](../../{image_path.relative_to(ROOT)}) · [Raw trajectory](../../{trajectory_rel})', '',
               'Final answer:', '', '```json', answer, '```', '']
    trace_path = ROOT / 'docs/evidence/br017-trace-index.json'
    trace_path.write_text(json.dumps(trace_index, indent=2) + '\n')
    (ROOT / 'docs/research-rounds/BR-017-traces.md').write_text('\n'.join(md))
    assets = {f'{plane}-{state}': data_url(DEST / f'{plane}-{state}.png')
              for plane in ['axial', 'coronal'] for state in ['before', 'after', 'region']}
    replacements = {'TRIALS': '\n'.join(cards), 'ROWS': '\n'.join(table),
                    'DETAIL_ROWS': '\n'.join(details), 'ASSETS': json.dumps(assets),
                    'INITIAL_IMAGE': assets['axial-after'],
                    'TOTAL_TIME': f"{sum(r['agent_seconds'] for r in rows.values()) / 60:.2f}",
                    'TOTAL_OUTPUT': f"{sum(r['output_tokens'] for r in rows.values()):,}",
                    'TOTAL_COST': f"{sum(r['estimated_cost_usd'] for r in rows.values()):.3f}"}
    output = (HERE / 'presentation.html').read_text()
    for key, value in replacements.items():
        assert '{{' + key + '}}' in output
        output = output.replace('{{' + key + '}}', value)
    assert '{{' not in output
    (DEST / 'index.html').write_text(output)
    print(json.dumps({'presentation': str(DEST / 'index.html'), 'trials': len(cards),
                      'verified_anchors': sum(len(t['steps']) for t in trace_index['trials']),
                      'output_bytes': len(output.encode()), 'new_model_calls': 0}))


if __name__ == '__main__':
    main()
