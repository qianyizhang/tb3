/* Dataset pages consume authored records; they never fetch scans or run tools. */
function datasetLinks(entry) {
  const sources=(DATA.datasets?.records || []).filter(d=>d.task_ids.includes(entry.id));
  return sources.length?`<div class="dataset-links"><span>Learn about the data</span>${sources.map(d=>`<a href="#datasets/${encodeURIComponent(d.id)}">${esc(d.title)} →</a>`).join('')}</div>`:'';
}
function datasetMode(active) {
  document.body.classList.toggle('dataset-mode',active);
  document.querySelector('.shell>aside').hidden=active;
}
function datasetDiagram(d) {
  // A structural diagram, never invented anatomy or a measured patient result.
  return `<figure class="dataset-diagram"><figcaption>How to read this dataset <span>Conceptual structure</span></figcaption><div class="dataset-flow"><section><svg viewBox="0 0 160 105" role="img" aria-label="Stack of source image planes"><g fill="#e9f3f3" stroke="#347d83" stroke-width="2"><path d="M20 62 86 25 140 55 74 92Z"/><path d="M20 48 86 11 140 41 74 78Z"/><path d="M20 34 86 0 140 27 74 64Z"/></g><path d="m44 35 40-21 34 17-42 21Z" fill="none" stroke="#347d83" stroke-dasharray="4 3"/></svg><h3>Original data</h3><p>${esc(d.image_description)}</p></section><div class="dataset-arrow" aria-hidden="true">+</div><section><svg viewBox="0 0 160 105" role="img" aria-label="Annotations linked to data"><g fill="none" stroke="#a66a29" stroke-width="2"><rect x="29" y="8" width="105" height="84" rx="8"/><path d="M49 30h65M49 51h65M49 72h65"/><circle cx="39" cy="30" r="3"/><circle cx="39" cy="51" r="3"/><circle cx="39" cy="72" r="3"/></g></svg><h3>Annotations / reference</h3><p>${esc(d.annotation_description)}</p></section></div><p class="dataset-unit"><strong>One sample:</strong> ${esc(d.sample_unit)}. Repeated views and conditions may reuse that sample.</p></figure>`;
}
function datasetSnapshot(d) {
  const snapshot=DATA.datasets?.previews?.[d.id];
  if(!snapshot) return '<p class="dataset-no-example">No frozen sample has been documented for this source.</p>';
  const panels=snapshot.panels,inputs=panels.filter(p=>p.role==='input'),references=panels.filter(p=>p.role==='reference');
  const panel=p=>`<figure class="snapshot-panel" data-snapshot-role="${esc(p.role)}">${p.image_url?`<button class="snapshot-image" data-snapshot-enlarge="${panels.indexOf(p)}" aria-label="Enlarge ${esc(snapshot.sample_id)} ${esc(p.role)} snapshot"><img loading="lazy" src="${p.image_url}" alt="${esc(snapshot.sample_id+' · '+p.role+' · '+p.caption)}"><span>Enlarge snapshot ↗</span></button>`:p.text?`<pre class="snapshot-text">${esc(p.text)}</pre>`:`<p class="snapshot-missing">Frozen image unavailable in this build: <code>${esc(p.path)}</code>. Recover the pinned snapshot; this is not an empty scan.</p>`}<figcaption>${esc(p.caption)}</figcaption></figure>`;
  const state={'paired':'Sample + reference','input-only':'Sample available · paired GT unavailable','reference-only':'Reference available · image unavailable','unavailable':'Source screen · imaging not acquired'}[snapshot.status];
  return `<section class="dataset-snapshot" data-snapshot-status="${esc(snapshot.status)}"><div class="snapshot-heading"><div><div class="eyebrow">Frozen source snapshot</div><h2>${esc(snapshot.sample_id)}</h2></div><span class="snapshot-state">${esc(state)}</span></div><p>${esc(snapshot.summary)}</p>${inputs.length?inputs.map(panel).join(''):panels.filter(p=>p.role==='metadata').length?panels.filter(p=>p.role==='metadata').map(panel).join(''):'<div class="snapshot-missing">The source MRI image was not retained. The actual available annotations can be inspected below.</div>'}${references.length?`<details class="dataset-reference"><summary>Reveal ground truth / source reference</summary><p class="snapshot-reference-note">${esc(snapshot.reference_note)}</p>${references.map(panel).join('')}</details>`:`<p class="snapshot-reference-note"><strong>Ground-truth availability:</strong> ${esc(snapshot.reference_note)}</p>`}<details class="snapshot-provenance"><summary>Snapshot provenance and exact source files</summary><p>These frozen views preserve the stated selection and reference qualifications. Opening this page does not run a model or change task inputs.</p><ul>${snapshot.sources.map(x=>`<li><code>${esc(x.path)}</code><br><small>SHA-256 ${esc(x.sha256)}</small></li>`).join('')}</ul></details><dialog id="dataset-image-dialog" class="snapshot-dialog"><div class="snapshot-dialog-toolbar"><label>Zoom <input id="snapshot-zoom" type="range" min="100" max="250" value="100" step="25"></label><button id="snapshot-close">Close</button></div><div class="snapshot-dialog-image"><img id="snapshot-large" alt=""></div><p id="snapshot-large-caption"></p></dialog></section>`;
}
function bindDatasetSnapshots(d) {
  const snapshot=DATA.datasets?.previews?.[d.id],dialog=el('dataset-image-dialog');
  if(!snapshot || !dialog) return;
  document.querySelectorAll('[data-snapshot-enlarge]').forEach(button=>button.onclick=()=>{
    const panel=snapshot.panels[Number(button.dataset.snapshotEnlarge)];
    el('snapshot-large').src=panel.image_url;el('snapshot-large').alt=panel.caption;
    el('snapshot-large-caption').textContent=panel.caption;
    el('snapshot-zoom').value=100;el('snapshot-large').style.width='100%';dialog.showModal();
  });
  el('snapshot-close').onclick=()=>dialog.close();
  el('snapshot-zoom').oninput=event=>el('snapshot-large').style.width=event.target.value+'%';
  dialog.onclick=event=>{if(event.target===dialog)dialog.close()};
}
function datasetDetail(d) {
  const samples=d.sample_sets.map(s=>`<section class="dataset-sample"><div><h3>${esc(s.label)}</h3><span class="dataset-role">${esc(s.role)}</span></div><p class="sample-identities">${s.sample_ids.map(id=>`<code>${esc(id)}</code>`).join(' ')}</p><p>${esc(s.note)}</p><details><summary>Selection provenance</summary><p><code>${esc(s.receipt.path)}${esc(s.receipt.pointer)}</code></p><p class="fine">Receipt SHA-256 <code>${esc(s.receipt.sha256)}</code></p></details></section>`).join('');
  const tasks=d.task_ids.map(id=>byId.get(id)).filter(Boolean);
  const links=(d.links || []).filter(x=>/^https?:\/\//.test(x.path));
  return `<article class="dataset-detail" data-dataset="${esc(d.id)}"><div class="eyebrow">Dataset · ${esc(d.modality)}</div><h1>${esc(d.title)}</h1><p class="dataset-lead">${esc(d.summary)}</p>${datasetSnapshot(d)}<details class="dataset-structure"><summary>Understand the data structure</summary>${datasetDiagram(d)}</details><section class="dataset-reference-scope"><h2>What the reference can establish</h2><p>${esc(d.reference_note)}</p></section><section><h2>Selected samples &amp; their use</h2><p class="fine">Selections can overlap. These are documented source selections, not a count of independent patients or successful trials.</p>${samples}</section><section><h2>Tasks using or explaining this source</h2>${tasks.length?`<div class="dataset-task-links">${tasks.map(e=>`<a href="#${esc(e.id)}/0/overview">${esc(e.title)} →</a>`).join('')}</div>`:'<p>Source review only; no task brief is linked.</p>'}<details><summary>${d.experiments.length} linked experiment records</summary><ul>${d.experiments.map(e=>`<li>${esc(e.title)} <code>${esc(e.id)}</code></li>`).join('')}</ul></details></section><section class="dataset-recovery"><h2>Release, access &amp; recovery</h2><p>${esc(d.version_note)}</p><p>${esc(d.terms_note)}</p>${d.access_note?`<p>${esc(d.access_note)}</p>`:''}${links.map(l=>`<p>${sourceLink(l.path,l.label+' ↗')}</p>`).join('')}${d.documentation_gaps?.length?`<h3>Open documentation or reference gaps</h3><ul>${d.documentation_gaps.map(g=>`<li>${esc(g)}</li>`).join('')}</ul>`:''}<p class="fine">Receipt links were checked when this page was built. Local scan availability is checked only by the explicit dataset audit, not by opening this page.</p><details><summary>Dataset record · ${esc(d.record_path)}</summary><pre class="dataset-record"></pre><a id="dataset-download" download="${esc(d.id)}.json">Download dataset record</a></details></section></article>`;
}
function renderDatasets() {
  if(typeof disposeTaskScene === 'function') disposeTaskScene();
  datasetMode(true);
  const raw=location.hash.slice(1).split('?')[0].split('/')[1] || '';
  let id='';try{id=decodeURIComponent(raw)}catch{/* Invalid route gets a visible empty state. */}
  const records=DATA.datasets?.records || [],d=records.find(x=>x.id===id);
  document.title=(d?d.title:'Datasets')+' · Task Explorer';
  el('main').innerHTML=`<div class="dataset-top"><a href="#${esc(selected || entries[0].id)}/0/overview">← Task explorer</a><a href="#datasets">All datasets</a></div><div class="dataset-workspace"><aside class="dataset-sidebar"><label for="dataset-search">FIND A DATASET OR SAMPLE</label><input id="dataset-search" type="search" placeholder="Name, modality, sample ID…"><nav id="dataset-nav" aria-label="Datasets"></nav></aside><div id="dataset-content">${d?datasetDetail(d):id?'<h1>Dataset not found</h1><p>Choose a source from the dataset list.</p>':`<div class="dataset-intro"><div class="eyebrow">Learn the data before the task</div><h1>Datasets</h1><p>Explore the images, annotations and selected samples behind the work.</p><p>${records.length} sources · ${DATA.datasets?.coverage.experiments || 0} linked medical experiment records.</p><p class="fine">${esc(DATA.datasets?.coverage.scope || '')}</p><div class="dataset-glossary"><section><h2>Image</h2><p>The acquired scan or generated input. Geometry and coordinates are part of the data.</p></section><section><h2>Annotation</h2><p>A mask marks voxels; a landmark marks a point; a correspondence links observations. Each has its own limits.</p></section><section><h2>Task use</h2><p>A reference can be hidden for scoring or supplied as help. The task condition decides which.</p></section></div><div class="dataset-cards">${records.map(r=>`<a href="#datasets/${esc(r.id)}">${DATA.datasets?.previews?.[r.id]?.panels.find(p=>p.role==='input' && p.image_url)?`<img loading="lazy" class="dataset-card-preview" src="${DATA.datasets.previews[r.id].panels.find(p=>p.role==='input' && p.image_url).image_url}" alt="${esc(r.title)} source snapshot">`:''}<span>${esc(r.modality)}</span><h2>${esc(r.title)}</h2><p>${esc(r.summary)}</p></a>`).join('')}</div></div>`}</div></div>`;
  const nav=()=>{
    const query=el('dataset-search').value.trim().toLowerCase();
    const matches=records.filter(r=>JSON.stringify([r.title,r.modality,r.summary,r.sample_sets.map(s=>s.sample_ids)]).toLowerCase().includes(query));
    el('dataset-nav').innerHTML=matches.length?matches.map(r=>`<a href="#datasets/${esc(r.id)}" ${r.id===id?'aria-current="page"':''}>${esc(r.title)}<small>${esc(r.modality)}</small></a>`).join(''):'<p>No matching dataset or sample.</p>';
  };el('dataset-search').oninput=nav;nav();
  if(d){
    bindDatasetSnapshots(d);
    const record={...d};delete record.task_ids;delete record.experiments;delete record.record_path;
    const raw=JSON.stringify(record,null,2);el('main').querySelector('.dataset-record').textContent=raw;
    el('dataset-download').href='data:application/json;charset=utf-8,'+encodeURIComponent(raw+'\n');
  }
}
