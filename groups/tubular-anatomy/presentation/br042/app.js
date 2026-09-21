'use strict';
const DATA = JSON.parse(document.getElementById('dataset').textContent);
const $ = id => document.getElementById(id);
const state = {model: DATA.models.length - 1, pos: [256, 256, 137], zoom: 1, showModel: false, showRef: false, includeZero: true, angle: -.22, tilt: -.25};
let volume = null;
const percent = v => (v * 100).toFixed(1);
const time = s => {s = Math.round(s); return (s >= 3600 ? `${Math.floor(s/3600)}h ` : '') + `${Math.floor(s/60)%60}m`;};
const modes = [
  {id: 'axial', a: 0, b: 1, c: 2, left: 'R', right: 'L', top: 'A', bottom: 'P'},
  {id: 'coronal', a: 0, b: 2, c: 1, left: 'R', right: 'L', top: 'S', bottom: 'I'},
  {id: 'sagittal', a: 1, b: 2, c: 0, left: 'P', right: 'A', top: 'S', bottom: 'I'}
];
const sourceCanvases = new Map();
function drawComparison() {
  const weight = $('weight').value, tolerance = $('tolerance').value, scope = $('scope').value;
  const selected = DATA.models.filter(m => scope === 'all' || (scope === 'v3' ? m.revision === 'V3' : m.status.startsWith('Completed')));
  $('metric-note').textContent = (weight === 'macro' ? 'Each present category counts equally. This exposes short-branch omissions; the pass additionally requires every category ≥80% at 1 mm.' : 'Each millimeter counts equally. Long main arteries dominate this aggregate; complete-tree passing uses category means and floors.') + (tolerance === '2' ? ' 2 mm is diagnostic only.' : '');
  $('comparison').innerHTML = selected.map(m => {
    const g = percent(m.metrics.geometry[`${weight}_recall_${tolerance}mm`]);
    const l = percent(m.metrics.labeled[`${weight}_recall_${tolerance}mm`]);
    return `<div class="result-row"><div class="result-label"><b>${m.title}</b><span>${m.status} · ${m.metrics.polylines} courses</span></div><div class="bars"><div class="bar" style="width:${g}%"><b>${g}%</b></div><div class="bar labeled" style="width:${l}%"><b>${l}%</b></div></div><div class="result-time">${time(m.seconds)}<small>${m.id === 'resumed' ? 'combined wall time' : 'actual wall time'}</small></div></div>`;
  }).join('');
}
function drawBranches() {
  const model = DATA.models[state.model];
  $('branch-grid').innerHTML = Object.entries(model.metrics.per_reference_category).map(([key, m]) => `<button class="branch${m.geometry_recall_1mm < .8 ? ' alert' : ''}" data-branch="${key}" title="Reveal reference and focus ${DATA.labels[key]}"><b>${DATA.labels[key]}</b><small>${m.reference_length_mm.toFixed(1)} mm reference</small><span>${percent(m.geometry_recall_1mm)}% geometry</span><span class="lb">${percent(m.labeled_recall_1mm)}% label</span></button>`).join('');
  document.querySelectorAll('[data-branch]').forEach(b => b.addEventListener('click', () => focusBranch(b.dataset.branch)));
  $('answer-download').href = model.answer;
  $('answer-download').textContent = `Exact answer · ${model.metrics.polylines} courses ↗`;
}
function drawFunnel() {
  const sensitivity = Number($('funnel-mode').value), f = DATA.funnel.results[sensitivity];
  const stages = ['skeleton', 'after_existing_path_exclusion', 'after_size_filter', 'accepted_components'];
  const headings = ['Branch', 'Raw skeleton', 'Exclude near existing paths', 'Component size 6–2499', 'Parent gap <2.2 mm', 'Actual final output'];
  let html = '<div class="funnel-grid">' + headings.map(x => `<div class="funnel-cell header">${x}</div>`).join('');
  for (const [name, label] of [['D2', '5'], ['OM1', '6'], ['OM2', '7']]) {
    const vals = stages.map(s => f.branches[name][s].coverage_1mm);
    vals.push(DATA.models.at(-1).metrics.per_reference_category[label].geometry_recall_1mm);
    html += `<div class="funnel-cell"><b>${name}</b><small>1 mm coverage</small></div>` + vals.map(v => `<div class="funnel-cell value ${v < .01 ? 'zero' : v > .8 ? 'good' : ''}">${percent(v)}<span>%</span></div>`).join('');
  }
  $('funnel').innerHTML = html + '</div>';
  $('funnel-note').textContent = sensitivity ? 'Post-hoc sensitivity, not a solver result: lowering vesselness yields 100% raw OM1 coverage, but most of it joins a 6586-voxel component rejected by the size cap. Accepted components rise from 17 to 37. The actual final output column remains the unchanged original answer.' : 'Exact recreation of the saved default candidate set: 17 accepted components. D2 survives the algorithm then is withheld in review. OM1 disappears in size and parent-gap filtering. The final column is submitted geometry, not candidate coverage.';
}
function focusBranch(key) {
  state.pos = DATA.branches[key].slice();
  state.zoom = 4; $('zoom').value = '4';
  state.showRef = true; $('show-reference').checked = true;
  state.showModel = true; $('show-model').checked = true;
  const notes = {'5': 'D2: default accepted candidates cover 87.8% at 1 mm; final resumed geometry covers 3.1%. The reference locates the withheld course.', '6': 'OM1: raw skeleton has nearby fragments; the saved component filters remove them. Final resumed coverage is 0%.', '7': 'OM2: final resumed geometry covers 57.2%, assigned OM1. Compare with V3 Astra/medium, which recovers the full reference geometry.', '10': 'R-PDA: the reference includes multiple courses. One is called an inferior RV branch (category 0) in the resumed output. Keep category 0 visible; identity remains under review.'};
  $('focus-note').textContent = `Reference-assisted focus · ${DATA.labels[key]}. ` + (notes[key] || 'This location is selected using evaluator coordinates after the model run.');
  syncPosition(); render();
}
function syncPosition() {
  ['x','y','z'].forEach((id,i) => {$(id).value = state.pos[i]; $(`${id}-read`).textContent = `${id.toUpperCase()} ${state.pos[i]} / ${DATA.shape[i]-1}`;});
  const ras = DATA.affine.slice(0,3).map(row => row[0]*state.pos[0] + row[1]*state.pos[1] + row[2]*state.pos[2] + row[3]);
  $('position').textContent = `Native XYZ [${state.pos.join(', ')}] · RAS [${ras.map(x=>x.toFixed(2)).join(', ')}] mm`;
}
function transform(mode, canvas) {
  const width = DATA.shape[mode.a] * DATA.spacing[mode.a], height = DATA.shape[mode.b] * DATA.spacing[mode.b];
  const scale = Math.min((canvas.width-46)/width, (canvas.height-46)/height) * state.zoom;
  const sx = scale * DATA.spacing[mode.a], sy = scale * DATA.spacing[mode.b];
  const cx = state.zoom === 1 ? (DATA.shape[mode.a]-1)/2 : state.pos[mode.a];
  const cy = state.zoom === 1 ? (DATA.shape[mode.b]-1)/2 : state.pos[mode.b];
  return {sx, sy, cx, cy, x: p => canvas.width/2 + (p[mode.a]-cx)*sx, y: p => canvas.height/2 - (p[mode.b]-cy)*sy};
}
function curveGroups() {
  const groups = [];
  if (state.showModel) groups.push({curves: DATA.models[state.model].curves, color: '#ffb15f', kind: 'model'});
  if (state.showRef) groups.push({curves: DATA.reference, color: '#57dbe5', kind: 'reference'});
  return groups;
}
function drawPlane(mode) {
  const canvas = $(mode.id), ctx = canvas.getContext('2d');
  const na = DATA.shape[mode.a], nb = DATA.shape[mode.b], t = transform(mode, canvas);
  ctx.fillStyle = '#050c12'; ctx.fillRect(0,0,canvas.width,canvas.height);
  if (!volume) return;
  let cache = sourceCanvases.get(mode.id);
  if (!cache || cache.slice !== state.pos[mode.c]) {
    const off = document.createElement('canvas'); off.width = na; off.height = nb;
    const oc = off.getContext('2d'), pixels = oc.createImageData(na, nb), p = [0,0,0]; p[mode.c] = state.pos[mode.c];
    for (let b=0;b<nb;b++) for (let a=0;a<na;a++) {
      p[mode.a]=a; p[mode.b]=nb-1-b;
      const v=volume[p[0]+512*(p[1]+512*p[2])], k=(a+na*b)*4;
      pixels.data[k]=pixels.data[k+1]=pixels.data[k+2]=v; pixels.data[k+3]=255;
    }
    oc.putImageData(pixels,0,0); cache={canvas:off,slice:state.pos[mode.c]}; sourceCanvases.set(mode.id,cache);
  }
  ctx.imageSmoothingEnabled = false;
  const corner = [0,0,0]; corner[mode.b] = nb-1;
  ctx.drawImage(cache.canvas,t.x(corner)-t.sx/2,t.y(corner)-t.sy/2,na*t.sx,nb*t.sy);
  const half = .75 / DATA.spacing[mode.c], lo=state.pos[mode.c]-half, hi=state.pos[mode.c]+half;
  ctx.lineWidth=2.2;
  for(const group of curveGroups()) {
    ctx.strokeStyle=group.color; ctx.beginPath();
    for(const curve of group.curves) for(let i=1;i<curve.p.length;i++) {
      if(group.kind==='model' && !state.includeZero && curve.labels[i]===0 && curve.labels[i-1]===0) continue;
      const p=curve.p[i-1], q=curve.p[i], dz=q[mode.c]-p[mode.c];
      let s0=0,s1=1;
      if(Math.abs(dz)<1e-9) {if(p[mode.c]<lo||p[mode.c]>hi) continue;}
      else {const a=(lo-p[mode.c])/dz,b=(hi-p[mode.c])/dz;s0=Math.max(0,Math.min(a,b));s1=Math.min(1,Math.max(a,b));if(s0>s1)continue;}
      const start=p.map((v,j)=>v+s0*(q[j]-v)),end=p.map((v,j)=>v+s1*(q[j]-v));
      ctx.moveTo(t.x(start),t.y(start));ctx.lineTo(t.x(end),t.y(end));
    }
    ctx.stroke();
  }
  ctx.strokeStyle='#e3dca199';ctx.lineWidth=1;ctx.setLineDash([4,5]);ctx.beginPath();
  ctx.moveTo(t.x(state.pos),0);ctx.lineTo(t.x(state.pos),canvas.height);ctx.moveTo(0,t.y(state.pos));ctx.lineTo(canvas.width,t.y(state.pos));ctx.stroke();ctx.setLineDash([]);
  ctx.font='13px system-ui';ctx.fillStyle='#98d0d6';ctx.textAlign='center';ctx.fillText(mode.top,canvas.width/2,18);ctx.fillText(mode.bottom,canvas.width/2,canvas.height-10);ctx.fillText(mode.left,14,canvas.height/2);ctx.fillText(mode.right,canvas.width-14,canvas.height/2);
  // Fixed physical scale bar.
  const mm=state.zoom===4?5:20, length=mm*t.sx/DATA.spacing[mode.a];
  ctx.strokeStyle='#e0eeee';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(25,canvas.height-26);ctx.lineTo(25+length,canvas.height-26);ctx.stroke();ctx.textAlign='left';ctx.font='11px system-ui';ctx.fillText(`${mm} mm`,25,canvas.height-34);
}
function drawTree() {
  const canvas=$('tree'), ctx=canvas.getContext('2d');ctx.fillStyle='#050c12';ctx.fillRect(0,0,canvas.width,canvas.height);
  const groups=curveGroups();
  if(!groups.length) {ctx.fillStyle='#8099a2';ctx.textAlign='center';ctx.font='17px system-ui';ctx.fillText('Input only',canvas.width/2,canvas.height/2-8);ctx.font='12px system-ui';ctx.fillText('Reveal a model or the reference to inspect centerlines.',canvas.width/2,canvas.height/2+20);return;}
  const co=Math.cos(state.angle),si=Math.sin(state.angle),ct=Math.cos(state.tilt),st=Math.sin(state.tilt);
  const projected=groups.map(g=>({...g,curves:g.curves.map(c=>({...c,p:c.p.map(p=>{const x=p[0]*DATA.spacing[0],y=p[1]*DATA.spacing[1],z=p[2]*DATA.spacing[2];const xx=co*x-si*y,yy=si*x+co*y;return [xx,ct*z-st*yy,st*z+ct*yy];})}))}));
  let xmin=Infinity,xmax=-Infinity,ymin=Infinity,ymax=-Infinity;
  for(const g of projected)for(const c of g.curves)for(const p of c.p){xmin=Math.min(xmin,p[0]);xmax=Math.max(xmax,p[0]);ymin=Math.min(ymin,p[1]);ymax=Math.max(ymax,p[1]);}
  const scale=Math.min((canvas.width-60)/(xmax-xmin),(canvas.height-65)/(ymax-ymin)),mx=(xmin+xmax)/2,my=(ymin+ymax)/2;
  for(const g of projected){ctx.strokeStyle=g.color;ctx.globalAlpha=g.kind==='reference'?.95:.7;ctx.lineWidth=g.kind==='reference'?2.1:1.5;ctx.beginPath();for(const c of g.curves)for(let i=1;i<c.p.length;i++){if(g.kind==='model'&&!state.includeZero&&c.labels[i]===0&&c.labels[i-1]===0)continue;const p=c.p[i-1],q=c.p[i];ctx.moveTo(canvas.width/2+(p[0]-mx)*scale,canvas.height/2-(p[1]-my)*scale);ctx.lineTo(canvas.width/2+(q[0]-mx)*scale,canvas.height/2-(q[1]-my)*scale);}ctx.stroke();}
  ctx.globalAlpha=1;ctx.fillStyle='#829da6';ctx.textAlign='left';ctx.font='11px system-ui';ctx.fillText('Rotatable projection · no CT surface / no correctness coloring',18,canvas.height-14);
}
function render(){modes.forEach(drawPlane);drawTree();}
$('model').innerHTML=DATA.models.map((m,i)=>`<option value="${i}">${m.title} · ${m.status}</option>`).join('');$('model').value=state.model;
$('model').addEventListener('change',()=>{state.model=Number($('model').value);drawBranches();render();});
for(const id of ['scope','weight','tolerance'])$(id).addEventListener('change',drawComparison);
$('funnel-mode').addEventListener('change',drawFunnel);
for(const [id,field] of [['show-model','showModel'],['show-reference','showRef'],['include-zero','includeZero']])$(id).addEventListener('change',()=>{state[field]=$(id).checked;render();});
$('zoom').addEventListener('change',()=>{state.zoom=Number($('zoom').value);render();});
['x','y','z'].forEach((id,i)=>$(id).addEventListener('input',()=>{state.pos[i]=Number($(id).value);syncPosition();render();}));
$('reset').addEventListener('click',()=>{state.pos=[256,256,137];state.zoom=1;state.showModel=false;state.showRef=false;state.includeZero=true;state.angle=-.22;state.tilt=-.25;$('zoom').value='1';$('show-model').checked=$('show-reference').checked=false;$('include-zero').checked=true;$('focus-note').textContent='No reference-guided focus selected.';syncPosition();render();});
document.querySelectorAll('[data-focus]').forEach(b=>b.addEventListener('click',()=>focusBranch(b.dataset.focus)));
for(const mode of modes)$(mode.id).addEventListener('pointerdown',e=>{const canvas=$(mode.id),r=canvas.getBoundingClientRect(),t=transform(mode,canvas);const px=(e.clientX-r.left)*canvas.width/r.width,py=(e.clientY-r.top)*canvas.height/r.height;state.pos[mode.a]=Math.max(0,Math.min(DATA.shape[mode.a]-1,Math.round(t.cx+(px-canvas.width/2)/t.sx)));state.pos[mode.b]=Math.max(0,Math.min(DATA.shape[mode.b]-1,Math.round(t.cy-(py-canvas.height/2)/t.sy)));syncPosition();render();});
let drag=null;
$('tree').addEventListener('pointerdown',e=>{drag=[e.clientX,e.clientY];$('tree').setPointerCapture(e.pointerId);});
$('tree').addEventListener('pointermove',e=>{if(!drag)return;state.angle+=(e.clientX-drag[0])*.012;state.tilt+=(e.clientY-drag[1])*.008;drag=[e.clientX,e.clientY];drawTree();});
$('tree').addEventListener('pointerup',()=>drag=null);$('tree').addEventListener('pointercancel',()=>drag=null);
drawComparison();drawBranches();drawFunnel();syncPosition();render();
(async()=>{try{const encoded=$('volume').textContent.trim(),binary=atob(encoded),bytes=Uint8Array.from(binary,c=>c.charCodeAt(0));const stream=new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'));volume=new Uint8Array(await new Response(stream).arrayBuffer());if(volume.length!==512*512*275)throw new Error('Display cache length mismatch');$('volume-status').textContent='Native CTA ready · 512 × 512 × 275 · input-only view until overlays are revealed';document.body.dataset.ready='true';render();}catch(error){$('volume-status').textContent='The native volume could not load in this browser. Open in a current Chrome/Safari browser; the report and result tables remain available. '+error.message;document.body.dataset.ready='error';console.error(error);}})();
