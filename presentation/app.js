'use strict';
const $ = selector => document.querySelector(selector);
const element = (tag, text, cls) => {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (cls) node.className = cls;
  return node;
};
const params = new URLSearchParams(location.search);
let rows = [], vocabulary;
function badge(axis, code) {
  const term = vocabulary.axes[axis]?.values[code];
  if (!term) return null;
  const node = element('span', term.label, 'badge');
  node.title = term.definition;
  return node;
}
function contextBadge(code) {
  const term = vocabulary.context_badges[code];
  const node = element('span', term.label, 'badge');
  node.title = term.definition;
  return node;
}
function badges(row) {
  const nodes = [];
  for (const axis of vocabulary.display_rules[row.kind + '_primary'] || []) {
    const node = badge(axis, row.current[axis]);
    if (node) nodes.push(node);
  }
  if (row.kind === 'evaluation') nodes.push(badge('outcome', row.outcome));
  if (row.kind === 'export') nodes.push(badge('submission_status', row.submission_status));
  return nodes.filter(Boolean);
}
function show() {
  const words = $('#search').value.toLowerCase().split(/\s+/).filter(Boolean);
  const group = $('#group').value, kind = $('#kind').value, status = $('#status').value;
  const filtered = rows.filter(row => {
    if (group && row.group_id !== group && row.id !== group) return false;
    if (status === 'attention' && (row.kind !== 'experiment' || !row.current.attention)) return false;
    if (status !== 'attention' && kind && !(kind === 'overview' ? ['idea', 'experiment', 'finding'].includes(row.kind) : row.kind === kind)) return false;
    if (!words.every(word => JSON.stringify(row).toLowerCase().includes(word))) return false;
    if (status && status !== 'attention') {
      const [axis, value] = status.split(':');
      if (row.current[axis] !== value) return false;
    }
    return true;
  });
  $('#records').replaceChildren();
  $('#count').textContent = `${filtered.length} of ${rows.length} records`;
  $('#empty').hidden = filtered.length > 0;
  for (const row of filtered) {
    const detail = element('details', undefined, 'record'), summary = element('summary');
    detail.id = row.id;
    const statusBadges = element('span', undefined, 'badges');
    statusBadges.append(...badges(row));
    summary.append(element('span', row.kind, 'type'), element('span', row.title || row.id, 'record-title'), statusBadges);
    if (row.current.attention) summary.classList.add('alert');
    detail.append(summary);
    detail.addEventListener('toggle', () => {
      if (!detail.open || detail.dataset.loaded) return;
      detail.dataset.loaded = '1';
      const body = element('div', undefined, 'detail');
      body.append(element('p', row.id + ' · ' + (row.group_id || 'shared'), 'meta'));
      const contexts = ['historical', 'diagnostic'];
      for (const key of contexts) if (row[key]) body.append(contextBadge(key));
      if (row.partial || row.current.partial) body.append(contextBadge('partial'));
      const observed = row.current.observed_at || row.observed_at || row.collected_at;
      if (observed) body.append(element('p', 'Observed: ' + observed, 'meta'));
      for (const key of ['question', 'claim', 'reason', 'scope', 'body', 'insight', 'notes']) {
        if (row[key]) body.append(element('p', typeof row[key] === 'string' ? row[key] : JSON.stringify(row[key])));
      }
      if (row.current.assessment_reason) body.append(element('p', row.current.assessment_reason));
      if (row.current.assessment_scope) body.append(element('p', 'Assessed scope: ' + row.current.assessment_scope));
      if (row.kind === 'evaluation') {
        body.append(element('p', `Scorer reward: ${row.reward ?? 'not recorded'} · ${row.model || row.agent || 'role not recorded'}`));
        if (['oracle', 'nop'].includes(row.agent) && ['pass', 'fail'].includes(row.outcome)) {
          body.append(contextBadge(row.outcome === (row.agent === 'oracle' ? 'pass' : 'fail') ? 'control_expected' : 'control_unexpected'));
        }
      }
      for (const flag of row.current.review_flags) body.append(element('p', `${flag.experiment_id}: ${vocabulary.axes.assessment.values[flag.assessment].label} — ${flag.reason}`, 'unavailable'));
      const decisions = rows.filter(r => r.kind === 'decision' && r.target_id === row.id).sort((a, b) => (a.created_at || '').localeCompare(b.created_at || ''));
      for (const decision of decisions) body.append(element('p', `${decision.accepted ? 'Accepted decision' : 'Recommendation'} · ${decision.actor}: ${vocabulary.axes.idea_state.values[decision.idea_state].label} — ${decision.reason}`));
      for (const link of row.portable_links || []) {
        if (!link.url) continue;
        const paragraph = element('p'), anchor = element('a', link.label);
        anchor.href = link.url; paragraph.append(anchor); body.append(paragraph);
      }
      for (const id of row.experiment_ids || []) {
        const paragraph = element('p'), anchor = element('a', 'Experiment: ' + id);
        anchor.href = '?kind=experiment&q=' + encodeURIComponent(id); paragraph.append(anchor); body.append(paragraph);
      }
      const raw = element('details');
      raw.append(element('summary', 'Record and evidence locators'), element('pre', JSON.stringify(row, null, 2)));
      body.append(raw); detail.append(body);
    });
    $('#records').append(detail);
  }
}
fetch('records.json').then(response => {
  if (!response.ok) throw Error(response.status);
  return response.json();
}).then(data => {
  rows = data.records; vocabulary = data.vocabulary;
  const groups = rows.filter(row => row.kind === 'group');
  groups.forEach((group, index) => {
    const anchor = element('a', undefined, 'group-card'); anchor.href = group.story_url;
    anchor.append(element('span', String(index + 1).padStart(2, '0'), 'number'), element('h2', group.title), element('p', group.question), element('p', `${rows.filter(r => r.kind === 'experiment' && r.group_id === group.id).length} experiments · ${rows.filter(r => r.kind === 'idea' && r.group_id === group.id).length} ideas →`, 'counts'));
    $('#groups').append(anchor);
    const option = element('option', group.title); option.value = group.id; $('#group').append(option);
  });
  for (const [axis, definition] of Object.entries(vocabulary.axes)) {
    const optgroup = element('optgroup'); optgroup.label = axis.replaceAll('_', ' ');
    for (const [code, term] of Object.entries(definition.values)) {
      const option = element('option', term.label); option.value = axis + ':' + code; optgroup.append(option);
      $('#legend').append(element('dt', term.label), element('dd', term.definition));
    }
    $('#status').append(optgroup);
  }
  $('#search').value = params.get('q') || '';
  if (params.has('kind')) $('#kind').value = params.get('kind');
  if (params.has('group')) $('#group').value = params.get('group');
  show();
}).catch(error => { $('#records').textContent = 'Could not load the workbench: ' + error; });
$('#filters').addEventListener('submit', event => event.preventDefault());
for (const id of ['search', 'group', 'kind', 'status']) $('#' + id).addEventListener('input', show);
