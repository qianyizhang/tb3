"""Project the authored retrospective into an offline report; never launch trials."""
import ast
import base64
import hashlib
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).parent
OUT = ROOT / 'runs/anatomy-history-presentation'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def esc(value):
    return html.escape(str(value), quote=True)


def image_payloads(step):
    images = []
    for result in step.get('observation', {}).get('results', []):
        content = result.get('content', '')
        if 'input_image' not in content:
            continue
        images += [x['image_url'] for x in ast.literal_eval(content) if x.get('type') == 'input_image']
    return images


def main():
    analysis = json.loads((HERE / 'analysis.json').read_text())
    all_rows, receipts, controls = {}, {}, []
    for rnd in ['br013', 'br014', 'br015']:
        path = ROOT / f'docs/evidence/{rnd}-results.json'
        data = json.loads(path.read_text()); assert data['task_files_unchanged']
        receipts[rnd] = sha(path)
        for row in data['rows']:
            all_rows[(rnd, row['task'], row['phase'])] = row
            assert row['execution'] == 'completed' and row['exception_type'] is None
            if row['phase'] in ['oracle', 'nop']:
                assert row['reward'] == (1 if row['phase'] == 'oracle' else 0)
                controls.append(row)
    assert len(controls) == 14
    frozen = 0
    unmanifested_caches = []
    for pattern in ['br013-freeze.json', 'br014-*-freeze.json', 'br015-*-freeze.json']:
        for path in ROOT.glob('docs/evidence/' + pattern):
            for task in json.loads(path.read_text())['tasks']:
                folder = ROOT / task['task_path']
                current = {str(p.relative_to(folder)) for p in folder.rglob('*') if p.is_file()}
                assert set(task['files']) <= current
                for extra in sorted(current - set(task['files'])):
                    assert '/__pycache__/' in extra and extra.endswith('.pyc'), (task['task'], extra)
                    unmanifested_caches.append({'task': task['task'], 'path': str((folder / extra).relative_to(ROOT)),
                                               'sha256': sha(folder / extra), 'treatment': 'Retained local Python bytecode cache; outside the frozen input manifest.'})
                for rel, digest in task['files'].items():
                    assert sha(folder / rel) == digest, (task['task'], rel)
                    frozen += 1
    index = {'basis': analysis['basis'], 'analysis_sha256': sha(HERE / 'analysis.json'),
             'result_receipts_sha256': receipts, 'unchanged_frozen_files': frozen,
             'runtime_controls': len(controls), 'unmanifested_local_caches': unmanifested_caches, 'trials': []}
    md = ['# Anatomy identity experiments — trace walkthroughs', '',
          '[Presentation and current verdict](anatomy-experiments.md) · [Offline visual report](../runs/anatomy-history-presentation/index.html)', '',
          analysis['basis'], '',
          'Seven Sol/xhigh trials and one conditional Terra/max trial from BR-013/014/015. '
          'Images below are decoded from the exact returned payloads. The '
          '[trace index](evidence/anatomy-trace-index.json) records hashes and step anchors. '
          'No additional model trials were run for this retrospective.', '',
          '## Shared approach', '', '```text',
          'Read vocabulary + spatial measurements', '                  ↓',
          'Identify obvious organs → isolate ambiguous groups', '                  ↓',
          'Inspect shape / neighborhood; optionally write numerical probes', '                  ↓',
          'Choose identities → validate JSON coverage and label constraints', '```', '',
          'The masks were provided. These are identity/audit tasks, not segmentation from raw CT. '
          'No specialist medical inference model or new training was invoked in the observed tools. '
          'A format check can pass even when the anatomical identities are wrong.', '']
    panels, tabs, table, details, models = [], [], [], [], []
    for i, trial in enumerate(analysis['trials']):
        row = all_rows[(trial['round'], trial['task'], trial['phase'])]; models.append(row)
        assert bool(row['reward']) == (trial['verdict'] == 'Pass')
        assert row['runtime_matches_request'] and row['session_file_count'] == 1
        result = ROOT / row['result_path']; assert sha(result) == row['result_sha256']
        path = result.parent / 'agent/trajectory.json'; assert sha(path) == row['trajectory_sha256']
        assert sha(ROOT / row['answer_path']) == row['answer_sha256']
        assert json.loads((ROOT / row['answer_path']).read_text()) == row['answer']
        steps = {s['step_id']: s for s in json.loads(path.read_text())['steps']}
        anchors = sorted({n for stage in trial['stages'] for n in stage['steps']})
        assert all(n in steps for n in anchors)
        assert trial['quote'] in steps[trial['quote_step']]['message']
        events = []
        for line in (result.parent / 'agent/codex.txt').read_text().splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                continue
            item = event.get('item', {})
            if event.get('type') == 'item.completed' and item.get('type') in ['command_execution', 'agent_message']:
                events.append(item)
        assert any(trial['quote'] in e.get('text', '') for e in events)
        commands = sum(e['type'] == 'command_execution' for e in events)
        nimages = sum(len(image_payloads(s)) for s in steps.values())
        img = trial['image']; step = steps[img['step']]
        assert img['path'] in json.dumps(step['tool_calls'])
        url = image_payloads(step)[img['index']]
        assert url.startswith(('data:image/png;base64,', 'data:image/jpeg;base64,'))
        payload = base64.b64decode(url.partition(',')[2], validate=True)
        local = OUT / f"{trial['id']}.{'png' if url.startswith('data:image/png') else 'jpg'}"
        local.write_bytes(payload)
        score = row['grade']; score_text = f"{score['identities_correct']}/{score['identities_total']}"
        if trial['id'] == 'a03':
            assert score['missed_corrections'] == score['false_repairs'] == 0
            score_text = '2 corrections; 0 false repairs'
        model = 'Sol/xhigh' if trial['phase'] == 'sol-xhigh' else 'Terra/max'
        name = trial['round'].upper().replace('BR0', 'BR-0') + ' · ' + trial['task'].replace('abdomen-', '').upper()
        ident = trial['id']; cls = 'miss' if trial['verdict'] == 'Miss' else 'pass'
        stat = f"{row['agent_seconds']:.1f} s · {nimages} images · {commands} commands · {row['output_tokens']:,} output tokens"
        stages = ''.join(f'<li><h4>{esc(s["title"])}</h4><p>{esc(s["text"])}</p><span class="anchor">Steps {", ".join(map(str,s["steps"]))}</span></li>' for s in trial['stages'])
        code = '\n'.join(trial['pseudocode']); answer = json.dumps(row['answer'], indent=2)
        tabs.append(f'<button role="tab" id="tab-{ident}" aria-controls="{ident}" aria-selected="{str(i==0).lower()}" tabindex="{0 if i==0 else -1}" data-tab="{ident}">{esc(trial["title"])}<span>{name} · {model} · {trial["verdict"]}</span></button>')
        panels.append(f'''<article class="trial" id="{ident}" role="tabpanel" aria-labelledby="tab-{ident}" {'hidden' if i else ''}>
        <div class="trial-heading"><div><span class="eyebrow">{name} / {model} / {esc(trial['subtitle'])}</span><h3>{esc(trial['headline'])}</h3></div><span class="badge {cls}">{trial['verdict']}</span></div>
        <p class="setup">{esc(trial['setup'])}</p><p class="small stats">{stat} · {score_text}</p>
        <div class="trial-grid"><ol class="stages">{stages}</ol><aside><figure class="trace-image"><button class="image-button" aria-label="Enlarge {ident} trace image"><img src="{url}" alt="{esc(img['caption'])}" loading="lazy"></button><figcaption>{esc(img['caption'])}<br><span class="anchor">Returned image · step {img['step']} · click to enlarge</span></figcaption></figure><blockquote>{esc(trial['quote'])}<cite>Public progress message · step {trial['quote_step']}</cite></blockquote><details><summary>Workflow in pseudocode</summary><pre>{esc(code)}</pre></details><details><summary>Final answer and tool recovery</summary><p>{esc(trial['recovery'])}</p><pre>{esc(answer)}</pre></details></aside></div>
        <div class="interpretation"><span class="eyebrow">Interpretation</span><p>{esc(trial['interpretation'])}</p></div>
        <details class="source"><summary>Trace provenance</summary><code>{esc(path.relative_to(ROOT))}</code><p class="hash">SHA-256 {row['trajectory_sha256']}</p></details></article>''')
        table.append(f'<tr><th>{name}<span>{esc(trial["title"])}</span></th><td>{model}</td><td><span class="badge {cls}">{score_text}</span></td><td>{row["agent_seconds"]:.1f} s</td><td>{nimages}</td><td>{row["output_tokens"]:,}</td><td>${row["estimated_cost_usd"]:.3f}</td></tr>')
        details.append(f'<tr><th>{name} / {model}</th><td>{row["total_seconds"]:.2f} s</td><td>{row["input_tokens"]:,}</td><td>{row["cached_input_tokens"]:,}</td><td>{row["reasoning_output_tokens"]:,}</td></tr>')
        index['trials'].append({'round':trial['round'],'task':trial['task'],'phase':trial['phase'],
            'trajectory':str(path.relative_to(ROOT)), 'trajectory_sha256':row['trajectory_sha256'],
            'answer_sha256':row['answer_sha256'],'steps':anchors,'public_quote_step':trial['quote_step'],
            'image':{'step':img['step'],'payload_index':img['index'],'solver_path':img['path'],
                     'local_path':str(local.relative_to(ROOT)),'sha256':hashlib.sha256(payload).hexdigest()},
            'images_returned':nimages,'commands_executed':commands})
        md += [f'## {name} / {model} — {trial["title"]}', '', f'**{trial["verdict"]}: {score_text}. {trial["headline"]}.**', '',trial['setup'],'',stat+'.','']
        for stage in trial['stages']:
            md += [f'### {stage["title"]}', '',stage['text']+f' (Steps {", ".join(map(str,stage["steps"]))}.)','']
        md += ['> '+trial['quote'],'',f'*Public message, step {trial["quote_step"]}.*','','```text',code,'```','',
               '**Interpretation.** '+trial['interpretation'],'','**Tool recovery.** '+trial['recovery'],'',
               f'[Actual returned image](../{local.relative_to(ROOT)}) · [Raw trajectory](../{path.relative_to(ROOT)})','']
    assert len(models) == 8
    sol = [r for r in models if r['phase'] == 'sol-xhigh']; assert len(sol) == 7
    index['totals'] = {'sol_trials':7,'terra_trials':1,'agent_seconds':sum(r['agent_seconds'] for r in models),
                       'output_tokens':sum(r['output_tokens'] for r in models),
                       'estimated_cost_usd':sum(r['estimated_cost_usd'] for r in models)}
    (ROOT / 'docs/evidence/anatomy-trace-index.json').write_text(json.dumps(index,indent=2)+'\n')
    (ROOT / 'docs/anatomy-traces.md').write_text('\n'.join(md)+'\n')
    template = (HERE / 'presentation.html').read_text()
    # Share the visual language with BR-017 without a second CSS copy or network dependency.
    br017 = (ROOT / 'probes/revisions/br017/authoring/presentation.html').read_text()
    style = re.search(r'<style>(.*?)</style>',br017,re.S).group(1)
    replacements = {'STYLE':style,'TABS':'\n'.join(tabs),'PANELS':'\n'.join(panels),
                    'ROWS':'\n'.join(table),'DETAIL_ROWS':'\n'.join(details),
                    'PAIR_IMAGE':'data:image/png;base64,'+base64.b64encode((OUT/'a02.png').read_bytes()).decode(),
                    'TOTAL_MINUTES':f"{index['totals']['agent_seconds']/60:.2f}",
                    'TOTAL_OUTPUT':f"{index['totals']['output_tokens']:,}",
                    'TOTAL_COST':f"{index['totals']['estimated_cost_usd']:.3f}"}
    for key,value in replacements.items():
        assert '{{'+key+'}}' in template
        template=template.replace('{{'+key+'}}',value)
    assert '{{' not in template
    (OUT / 'index.html').write_text(template)
    print(json.dumps({'presentation':str(OUT/'index.html'),'trials':len(models),
                      'anchors':sum(len(t['steps']) for t in index['trials']),
                      'frozen_files':frozen,'bytes':len(template.encode()),'new_model_trials':0}))


if __name__ == '__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    main()
