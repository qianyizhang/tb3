const DATA = JSON.parse(document.getElementById('data').textContent);
const entries = DATA.entries;
const inventory = DATA.inventory.repositories || [];
const byId = new Map(entries.map(e => [e.id, e]));
const el = id => document.getElementById(id);
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const groupId = e => e.repository_id || e.id;
const groups = entries.filter((e, i) => entries.findIndex(x => groupId(x) === groupId(e)) === i);
const repoInventory = id => inventory.find(r => r.id === (byId.get(id)?.repository_id || id));
const repoEntry = e => groups.find(g => groupId(g) === groupId(e));
const groupEntries = e => entries.filter(x => groupId(x) === groupId(e));
const itemsFor = e => (repoInventory(e.id)?.items || []).filter(i => i.brief_id === e.id);
const htmlField = (e, key) => e.html?.[key] || `<p>${esc(e[key])}</p>`;
const textMatch = (value, query) => JSON.stringify(value).toLowerCase().includes(query);
const itemMatch = (i, query) => textMatch([i.id,i.title,i.family,i.definition,i.condition,i.case_context?.label,i.case_context?.facts],query);
const briefMatch = (e, query) => textMatch([e.title,e.nav_group,e.nav_label,DATA.task_families?.[e.task_family]?.title,e.goal,e.raw,e.helpers,e.output,e.repo],query) || itemsFor(e).some(i => itemMatch(i,query));
const hasExample = e => Object.values(e.visuals).some(s => /<img\b/.test(s));
const isCase = i => i.kind === 'case';
const compareItems = (a,b) => a.id.localeCompare(b.id,undefined,{numeric:true});
const currentItem = () => itemsFor(byId.get(selected)).find(i => i.id === selectedItem);
let selected = entries[0].id, selectedItem = '', condition = 0, tab = 'overview', visual = 'input', selectedSource = '';
const familyState = new Map(), listScroll = new Map();
const familyKey = e => groupId(e)+'/'+e.nav_group;
function revealFamily() {
  const e=byId.get(selected);
  if(e.nav_group) familyState.set(familyKey(e),true);
}

const familyConfig = e => DATA.task_families?.[e.task_family];
const familyMembers = e => e.task_family ? groupEntries(e).filter(x=>x.task_family===e.task_family) : [e];
function taskUnits(list) {
  const units=new Map();
  for(const e of list) {
    const id=e.task_family || e.id;
    if(!units.has(id)) units.set(id,{id,entry:e,members:[],title:familyConfig(e)?.title || e.nav_label || e.title});
    const unit=units.get(id);unit.members.push(e);
    if(e.id===selected) unit.entry=e;
  }
  return [...units.values()];
}
function chooseVariant(id) {
  const previous=byId.get(selected),next=byId.get(id),name=previous.variants[condition].name;
  selected=id;selectedItem='';selectedSource='';visual='input';
  condition=Math.max(0,next.variants.findIndex(v=>v.name===name));
  clearIncompatibleSearch(next);
  if(tab==='examples' && !hasExample(next)) tab='overview';
  revealFamily();saveRoute();render();el('task-variant')?.focus();
}

function compactLabel(i, e) {
  if (i.case_context?.label) return i.case_context.label;
  if (i.id.startsWith('clinical_trial_matching_task_')) return 'Case ' + i.id.split('_').at(-1);
  if (i.id.startsWith('ct_abnormality_')) return i.id.replace('ct_abnormality_','');
  if (i.id.startsWith('tumor_area_selection_')) return 'Slide ' + Number(i.id.split('_').at(-1));
  if (i.id.startsWith('xray_report_correction_case_')) return 'Case ' + Number(i.id.split('_').at(-1));
  if (i.id.startsWith('lite-case-')) return i.id.slice(10);
  if (i.kind === 'gallery entry') return 'Gallery';
  if (i.kind === 'code package') return 'Domain branch';
  if (i.id.startsWith('full-release-')) return 'Full release';
  if (i.id.startsWith('lite-release-')) return 'Lite release';
  if (itemsFor(e).length > 1 && new Set(itemsFor(e).map(x => x.condition_index || 0)).size > 1)
    return e.variants[i.condition_index || 0].name;
  return i.title;
}
function edition(e) {
  if (e.id.startsWith('automedbench-full-')) return 'Full release';
  if (e.id === 'automedbench-tsg') return 'Lite release';
  if (e.id === 'automedbench') return 'Domain branch';
  return '';
}
function sourceLink(url, label='Open source ↗') {
  return `<a href="${esc(url)}" target="_blank" rel="noopener noreferrer">${esc(label)}</a>`;
}
function box(label, body, klass='') {
  return `<section class="box ${klass}"><h3>${esc(label)}</h3>${body}</section>`;
}
function selectItem(id) {
  const item = repoInventory(selected)?.items.find(i => i.id === id);
  if (!item) return;
  selected = item.brief_id; selectedItem = item.id; selectedSource = ''; condition = item.condition_index || 0; visual = 'input';
}
function canonicalTab(value) {
  return ({brief:'overview',catalogue:'overview',contract:'requirements'})[value] || value || 'overview';
}
function route() {
  const [path,query=''] = location.hash.slice(1).split('?'), previousSource=selectedSource;
  const parts = path.split('/');
  selected = byId.has(parts[0]) ? parts[0] : entries[0].id;
  selectedItem = ''; condition = 0;
  let requested;
  if (parts[1] === 'task' || parts[1] === 'catalogue') {
    try { selectItem(decodeURIComponent(parts[2] || '')); } catch { /* Keep a valid default for a malformed hash. */ }
    requested = parts[1] === 'task' ? parts[3] : undefined;
    tab = canonicalTab(parts[1] === 'task' ? parts[4] : 'overview');
  } else {
    requested = parts[1]; tab = canonicalTab(parts[2]);
  }
  const e = byId.get(selected), n = Number(requested);
  clearIncompatibleSearch(e);
  if (requested !== undefined && Number.isInteger(n)) condition = Math.max(0,Math.min(n,e.variants.length-1));
  if (!['overview','requirements','examples','sources'].includes(tab) || (tab === 'examples' && !hasExample(e))) tab = 'overview';
  const requestedSource=new URLSearchParams(query).get('source');
  selectedSource=tab==='sources' && e.sources.some(([,path])=>DATA.local_sources?.[path]?.sha256===requestedSource)?requestedSource:'';
  visual = 'input'; revealFamily(); render();
  if(selectedSource) el('source-heading')?.focus();
  else if(previousSource) document.querySelector(`[data-source="${CSS.escape(previousSource)}"], [data-notice="${CSS.escape(previousSource)}"]`)?.focus();
}
function clearIncompatibleSearch(e) {
  if (!briefMatch(e,el('search').value.trim().toLowerCase())) el('search').value='';
}
function saveRoute(replace=false) {
  const e = byId.get(selected), item = currentItem();
  const path = item ? `${groupId(e)}/task/${encodeURIComponent(item.id)}/${condition}/${tab}` : `${selected}/${condition}/${tab}`;
  history[replace?'replaceState':'pushState'](null,'','#'+path+(selectedSource && tab==='sources'?'?source='+selectedSource:''));
}
function chooseDefinition(id) {
  selected=id; selectedItem=''; selectedSource=''; condition=0; tab='overview'; visual='input'; revealFamily(); saveRoute(); render();
  document.querySelector(`[data-definition="${CSS.escape(id)}"]`)?.focus();
}
function chooseGroup(id) {
  const first = groupEntries(byId.get(id)).find(e => briefMatch(e,el('search').value.trim().toLowerCase()));
  chooseDefinition(first?.id || id);
  document.querySelector(`[data-group="${CSS.escape(id)}"]`)?.focus();
}
function navigation() {
  const query=el('search').value.trim().toLowerCase(), active=groupId(byId.get(selected));
  const matches=groups.filter(g=>groupEntries(g).some(e=>briefMatch(e,query)));
  el('nav').innerHTML=matches.map(g=>{
    const count=taskUnits(groupEntries(g)).length,variants=groupEntries(g).length;
    const caption=repoInventory(g.id)?`${count} tasks${count===variants?'':` · ${variants} variants`}`:'Internal example';
    return `<button class="navitem" data-group="${esc(g.id)}" aria-current="${active===groupId(g)}"><strong>${esc(g.repo)}</strong><small>${caption}</small></button>`;
  }).join('') || '<p class="empty">No matching tasks.</p>';
  el('nav').querySelectorAll('[data-group]').forEach(b=>b.onclick=()=>chooseGroup(b.dataset.group));
}
function taskList(e, matches) {
  const searching=Boolean(el('search').value.trim()),units=taskUnits(matches);
  const families=new Map();
  for(const unit of taskUnits(groupEntries(e))) if(unit.entry.nav_group) {
    const name=unit.entry.nav_group;
    if(!families.has(name)) families.set(name,[]);
    families.get(name).push(unit);
  }
  const item=unit=>{
    const x=unit.entry,memberCount=familyMembers(x).length,tags=[];
    const cases=itemsFor(x).filter(isCase);
    if(memberCount>1) tags.push(memberCount+' variants');
    else {
      if(edition(x)) tags.push(edition(x));
      if(cases.length) tags.push(cases.length+(cases.length===1?' case':' cases'));
    }
    if(unit.members.some(hasExample)) tags.push('Image example');
    return `<button class="task-item" data-definition="${esc(x.id)}" data-task="${esc(unit.id)}" aria-pressed="${unit.members.some(y=>y.id===selected)}"><strong>${esc(unit.title)}</strong>${tags.length?`<small>${tags.map(esc).join(' · ')}</small>`:''}</button>`;
  };
  const seen=new Set(),rows=[];
  for(const unit of units) {
    const x=unit.entry,family=families.get(x.nav_group);
    if(!family || family.length<2) {rows.push(item(unit));continue;}
    if(seen.has(x.nav_group)) continue;
    seen.add(x.nav_group);
    const children=units.filter(y=>y.entry.nav_group===x.nav_group),key=familyKey(x);
    const open=searching || (familyState.get(key) ?? children.some(y=>y.members.some(z=>z.id===selected)));
    rows.push(`<details class="task-family" data-family="${esc(key)}" ${open?'open':''}><summary><span>${esc(x.nav_group)}</span><small>${children.length}</small></summary><div class="family-tasks">${children.map(item).join('')}</div></details>`);
  }
  return `<nav class="task-list" data-repository="${esc(groupId(e))}" aria-label="Tasks in this repository"><div class="list-heading">${searching?'Matching tasks':'Tasks'} <span>${units.length}</span></div>${rows.join('') || '<p class="empty">No tasks match this search in this repository.</p>'}</nav>`;
}

function coverage(e) {
  const inv=repoInventory(e.id);
  return inv?`<details class="coverage"><summary>Coverage &amp; source revisions</summary><p>${esc(inv.coverage)}</p><p class="fine">${inv.items.length} indexed source records · observed ${esc(inv.observed_on)} · revision <code>${esc(inv.commit)}</code>. Records include repeated cases and overlapping releases.</p></details>`:'';
}
function caseSelector(e) {
  const cases=itemsFor(e).filter(isCase).sort(compareItems);
  if (!cases.length) return '';
  const item=currentItem(),note=e.case_note!=='Not yet specified.'?htmlField(e,'case_note'):'';
  const facts=item?.case_context?.facts || [];
  return `<section class="case-selector" aria-label="Cases"><div class="case-heading"><h3>${cases.length} cases</h3><span>Shared task; different inputs</span></div><div class="case-buttons">${cases.map(i=>`<button class="case-button" data-entry="${esc(i.id)}" aria-pressed="${i.id===selectedItem}">${esc(compactLabel(i,e))}</button>`).join('')}</div>${facts.length?`<p class="case-facts">${facts.map(f=>`<strong>${esc(f.value)}</strong> ${esc(f.label.toLowerCase())}`).join(' · ')} ${item.case_context.source?sourceLink(item.case_context.source,'Pool manifest ↗'):''}</p>`:''}${note?`<div class="case-note">${note}</div>`:''}${item?`<div class="case-source">${sourceLink(item.url,'Open '+compactLabel(item,e)+' source ↗')}</div>`:''}</section>`;
}
function sourceScope(e) {
  const item=currentItem();
  if (!item?.brief_scope_note) return '';
  return `<p class="scope-note">Selected source: ${esc(compactLabel(item,e))}. This overview describes the ${esc(edition(e)||'shared task')}; exact data and recipes can differ. <button class="text-button" data-tab="sources">Source details</button></p>`;
}
function assistance(e) {
  // Single-condition tasks already describe their help and remaining work once.
  if (e.variants.length<2) return '';
  const v=e.variants[condition];
  return `<section class="assistance"><h3>Assistance condition</h3><div class="variants">${e.variants.map((x,i)=>`<button class="variant" data-condition="${i}" aria-pressed="${i===condition}">${esc(x.name)}</button>`).join('')}</div><div class="condition"><p><strong>Given</strong>${esc(v.helper)}</p><p><strong>Remaining work</strong>${esc(v.remaining)}</p></div></section>`;
}
function taskPicture(e) {
  const d=e.illustration;
  if(d) return `<figure class="task-picture conceptual" data-illustration="${esc(d.kind)}"><figcaption><span class="drawing-label">Conceptual illustration</span><span>Drawn, not a dataset sample</span></figcaption><div class="picture-pair"><section><h4>Input</h4>${taskArt(e)}<p>${esc(d.input)}</p></section><div class="picture-arrow" aria-hidden="true">→</div><section><h4>Expected output</h4>${taskArt(e,true)}<p>${esc(d.output)}</p></section></div><p class="picture-caption">${esc(d.caption)}</p></figure>`;
  const illustrated=e.example_case_id?itemsFor(e).find(i=>i.id===e.example_case_id):null;
  const exampleLabel=illustrated?' · '+compactLabel(illustrated,e):'';
  return /<img\b/.test(e.visuals.input)?`<figure class="task-picture native-preview"><figcaption><span class="drawing-label">Source-derived example${esc(exampleLabel)}</span><button class="text-button" data-example-open>Inspect example →</button></figcaption><div class="native-input">${e.visuals.input}</div>${imageNotice(e)}</figure>`:e.missing_media?.length?`<div class="preview-unavailable">${e.visuals.input}${imageNotice(e)}</div>`:'';
}
function imageNotice(e) {
  const notice=e.sources.find(([label])=>label==='Preview image notices');
  const source=notice && DATA.local_sources?.[notice[1]];
  return source?.sha256?`<p class="fine"><button class="text-button" data-notice="${source.sha256}">Image attribution, terms and derivation</button></p>`:'';
}

function overview(e) {
  const help=e.variants.length<2?box('Supplied help',htmlField(e,'helpers'),'helper'):'';
  return `<div class="task-context"><h3>Why it matters</h3>${htmlField(e,'value')}</div>${taskPicture(e)}<div class="overview-contract">${box('Input',htmlField(e,'raw'))}${help}${box('Deliverable',htmlField(e,'output'),'deliverable')}</div>${assistance(e)}<section class="difficulty"><h3>What makes it difficult</h3>${htmlField(e,'challenge')}</section>${caseSelector(e)}`;
}
function requirements(e) {
  return `<div class="requirements">${box('Task rules',htmlField(e,'spec'))}${box('Environment & callable tools',htmlField(e,'tools'))}${box('How success is checked',htmlField(e,'score'))}${box('Reference-only material',htmlField(e,'reference'))}</div>`;
}
function examples(e) {
  let exampleNote='';
  if (e.example_case_id && selectedItem && selectedItem!==e.example_case_id) {
    const illustrated=itemsFor(e).find(i=>i.id===e.example_case_id);
    exampleNote=`<p class="scope-note">Illustrated example: ${esc(illustrated?compactLabel(illustrated,e):e.example_case_id)}. The selected case has no local image preview.</p>`;
  }
  return `${exampleNote}<div class="variants" aria-label="Visual reveal"><button class="variant" data-visual="input" aria-pressed="${visual==='input'}">Input</button><button class="variant" data-visual="helpers" aria-pressed="${visual==='helpers'}">Supplied helpers</button><button class="variant" data-visual="answer" aria-pressed="${visual==='answer'}">Reveal reference / output</button></div><div class="visual-content" data-visible-role="${visual}">${e.visuals[visual]}</div>${imageNotice(e)}`;
}
function sourceDetails(e) {
  const items=itemsFor(e),item=currentItem();
  const chooser=items.length>1?`<label class="source-picker">Source record<select id="source-picker"><option value="">Shared definition sources</option>${items.map(i=>`<option value="${esc(i.id)}" ${i.id===selectedItem?'selected':''}>${esc(compactLabel(i,e))}</option>`).join('')}</select></label>`:'';
  const active=item || (items.length===1?items[0]:null);
  const provenance=active?`<details class="provenance"><summary>Technical identifiers</summary><dl><dt>Source ID</dt><dd><code>${esc(active.id)}</code></dd><dt>Definition ID</dt><dd><code>${esc(active.definition)}</code></dd><dt>Source condition</dt><dd>${esc(active.condition)}</dd></dl></details>`:'';
  const references=e.sources.map(([label,url])=>{
    if(/^https?:/.test(url)) return `<div class="source">${sourceLink(url,label+' ↗')}</div>`;
    const source=DATA.local_sources?.[url],story=DATA.presentation_context?.story_urls?.[url];
    return `<div class="source">${source?.sha256?`<button class="text-button" data-source="${source.sha256}">${esc(label)}</button>`:esc(label)}${story?` · <a href="${esc(story)}">Read illustrated story →</a>`:''}<small>${esc(url)}</small>${source?.sha256?'':`<small>Unavailable in this copy: ${esc(source?.unavailable || 'This source is not included.')}</small>`}</div>`;
  }).join('');
  const sourceEntry=e.sources.find(([,url])=>DATA.local_sources?.[url]?.sha256===selectedSource);
  let reader='';
  if(sourceEntry){
    const [label,path]=sourceEntry,source=DATA.local_sources[path];
    reader=`<section class="source-reader" aria-labelledby="source-heading"><div class="source-actions"><button class="quiet" id="source-close">Back to references</button><a id="source-download" href="data:application/octet-stream;base64,${source.base64}" download="${esc(path.split('/').at(-1))}">Download original</a></div><h3 id="source-heading" tabindex="-1">${esc(label)}</h3><p class="fine">Exact source copy · ${source.bytes.toLocaleString()} bytes<br>SHA-256 <code>${source.sha256}</code></p><pre id="source-content" tabindex="0"></pre></section>`;
  }
  return `${reader}${chooser}${active?`<div class="selected-source">${sourceLink(active.url,'Open selected source ↗')}${active.brief_scope_note?`<p class="fine">${esc(active.brief_scope_note)}</p>`:''}${provenance}</div>`:''}<h3>Definition references</h3>${references}<details class="source-limits"><summary>Evidence &amp; remaining gaps</summary>${htmlField(e,'families')}${htmlField(e,'gap')}</details>`;
}
function taskDetail(e) {
  const tabs=[['overview','Overview'],['requirements','Requirements']];
  if (hasExample(e)) tabs.push(['examples','Example']);
  tabs.push(['sources','Sources']);
  const normalized=s=>s.toLowerCase().replace(/^(build and run a pipeline to |develop and apply a prediction method to |implement a computational method to )/,'').replace(/[.]+$/,'');
  const summary=normalized(e.goal)===normalized(e.title)?'':htmlField(e,'goal');
  const body=tab==='requirements'?requirements(e):tab==='examples'?examples(e):tab==='sources'?sourceDetails(e):overview(e);
  const family=familyConfig(e),members=familyMembers(e);
  const variantPicker=members.length>1?`<label class="task-variant-picker" for="task-variant">${esc(family.selector)}<select id="task-variant">${members.map(x=>`<option value="${esc(x.id)}" ${x.id===selected?'selected':''}>${esc(x.nav_label||x.title)}</option>`).join('')}</select></label>`:'';
  return `<article class="task-detail" data-brief="${esc(e.id)}"><div class="detail-heading">${e.proposed?'<span class="draft">Proposed</span>':''}<h2>${esc(members.length>1?family.title:e.title)}</h2>${variantPicker}${edition(e)?`<span class="edition">${esc(edition(e))}</span>`:''}${summary?`<div class="task-goal">${summary}</div>`:''}</div>${sourceScope(e)}<div class="tabs" role="tablist" aria-label="Task sections">${tabs.map(([id,label])=>`<button id="tab-${id}" data-tab="${id}" role="tab" tabindex="${tab===id?0:-1}" aria-selected="${tab===id}" aria-controls="task-panel">${label}</button>`).join('')}</div><section id="task-panel" role="tabpanel" tabindex="0" aria-labelledby="tab-${tab}">${body}</section></article>`;
}
function render() {
  const previousList=el('main').querySelector('.task-list');
  if(previousList) listScroll.set(previousList.dataset.repository,previousList.scrollTop);
  navigation();
  const e=byId.get(selected),group=repoEntry(e),inv=repoInventory(e.id),query=el('search').value.trim().toLowerCase();
  const matches=groupEntries(e).filter(x=>briefMatch(x,query));
  const visible=matches.some(x=>x.id===selected);
  const intro=DATA.repository_contexts?.[groupId(e)];
  document.title=group.repo+' · Task Explorer';
  el('main').innerHTML=`<div class="repository-heading"><h1>${esc(group.repo)}</h1>${intro?`<p>${esc(intro)}</p>`:''}</div>${inv?`<div class="catalogue-workspace">${taskList(e,matches)}${visible?taskDetail(e):'<div class="empty task-detail">Choose a matching task from the list.</div>'}</div>`:taskDetail(e)}${coverage(e)}`;
  // Text insertion preserves leading LF and CRLF that the HTML parser normalizes.
  if(el('source-content')) el('source-content').textContent=Object.values(DATA.local_sources).find(s=>s.sha256===selectedSource).content;
  const currentList=el('main').querySelector('.task-list');
  if(currentList) {
    currentList.scrollTop=listScroll.get(groupId(e)) || 0;
    const active=currentList.querySelector('.task-item[aria-pressed=true]');
    if(active?.getClientRects().length) {
      const bounds=currentList.getBoundingClientRect(),row=active.getBoundingClientRect();
      if(row.top<bounds.top) currentList.scrollTop+=row.top-bounds.top;
      else if(row.bottom>bounds.bottom) currentList.scrollTop+=row.bottom-bounds.bottom;
    }
  }
  el('main').querySelectorAll('[data-family]').forEach(d=>d.ontoggle=()=>{
    if(d.isConnected && !el('search').value.trim()) familyState.set(d.dataset.family,d.open);
  });
  el('main').querySelectorAll('[data-definition]').forEach(b=>b.onclick=()=>{chooseDefinition(b.dataset.definition);el('main').querySelector('.task-detail')?.scrollIntoView({block:'nearest'})});
  el('main').querySelectorAll('[data-tab]').forEach(b=>b.onclick=()=>{tab=b.dataset.tab;selectedSource='';saveRoute();render();el('tab-'+tab)?.focus()});
  el('main').querySelectorAll('[data-source]').forEach(b=>b.onclick=()=>{selectedSource=b.dataset.source;saveRoute();render();el('source-heading')?.focus()});
  el('main').querySelectorAll('[data-notice]').forEach(b=>b.onclick=()=>{tab='sources';selectedSource=b.dataset.notice;saveRoute();render();el('source-heading')?.focus()});
  if(el('source-close')) el('source-close').onclick=()=>{const previous=selectedSource;selectedSource='';saveRoute();render();document.querySelector(`[data-source="${CSS.escape(previous)}"]`)?.focus()};
  const tabs=[...el('main').querySelectorAll('[role="tab"]')];
  tabs.forEach((button,index)=>button.onkeydown=event=>{
    const target={ArrowRight:(index+1)%tabs.length,ArrowLeft:(index+tabs.length-1)%tabs.length,Home:0,End:tabs.length-1}[event.key];
    if(target!==undefined){event.preventDefault();tabs[target].click()}
  });
  el('main').querySelectorAll('[data-example-open]').forEach(b=>b.onclick=()=>{tab='examples';saveRoute();render();el('tab-examples')?.focus()});
  el('main').querySelectorAll('[data-entry]').forEach(b=>b.onclick=()=>{selectItem(b.dataset.entry);saveRoute();render();el('main').querySelector(`[data-entry="${CSS.escape(selectedItem)}"]`)?.focus()});
  el('main').querySelectorAll('[data-condition]').forEach(b=>b.onclick=()=>{
    condition=Number(b.dataset.condition);visual='input';
    const linked=itemsFor(e).filter(i=>(i.condition_index||0)===condition);
    if (currentItem() && (currentItem().condition_index||0)!==condition) selectedItem=linked.length===1?linked[0].id:'';
    saveRoute();render();el('main').querySelector(`[data-condition="${condition}"]`)?.focus();
  });
  el('main').querySelectorAll('[data-visual]').forEach(b=>b.onclick=()=>{visual=b.dataset.visual;render();el('main').querySelector(`[data-visual="${visual}"]`).focus()});
  const variantPicker=el('task-variant');
  if(variantPicker) variantPicker.onchange=()=>chooseVariant(variantPicker.value);
  const picker=el('source-picker');
  if (picker) picker.onchange=()=>{if(picker.value)selectItem(picker.value);else{selectedItem='';condition=0;visual='input'}saveRoute();render();el('source-picker')?.focus()};
}
el('search').oninput=()=>{
  const e=byId.get(selected),query=el('search').value.trim().toLowerCase();
  if (!briefMatch(e,query)) {
    const first=groupEntries(e).find(x=>briefMatch(x,query));
    if(first){selected=first.id;selectedItem='';condition=0;tab='overview';visual='input';revealFamily();saveRoute(true)}
  }
  render();
};
el('format').onclick=()=>el('rules').showModal();el('close').onclick=()=>el('rules').close();
// Back/forward between these hash routes emits hashchange as well as popstate.
// Render once so the second event cannot discard the focus restored by route().
window.onhashchange=route;
document.querySelector('.navnote').innerHTML=`${inventory.length} repositories · ${taskUnits(entries).length} tasks · ${entries.length} variants<br>Related variants share one task entry.`;
if(DATA.presentation_context?.home_url){
  const link=document.createElement('a');link.id='workbench-home';link.href=DATA.presentation_context.home_url;link.textContent=DATA.presentation_context.home_label || 'Experiment evidence';
  document.querySelector('header>div:last-child').prepend(link);
}
route();
