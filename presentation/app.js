'use strict';
const $=s=>document.querySelector(s), el=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
const params=new URLSearchParams(location.search);
let rows=[];
function status(r){return r.current.need_fix?'needs review / fix':r.completeness==='partial'?'partial':r.current.disposition||r.disposition||r.classification||r.current.validity;}
function show(){
 const words=$('#search').value.toLowerCase().split(/\s+/).filter(Boolean),group=$('#group').value,kind=$('#kind').value,state=$('#status').value;
 const filtered=rows.filter(r=>(!group||r.group_id===group||r.id===group)&&(!kind||(kind==='overview'?['idea','experiment','finding'].includes(r.kind):r.kind===kind))&&words.every(w=>JSON.stringify(r).toLowerCase().includes(w))&&(!state||(state==='need_fix'?r.current.need_fix:state==='partial'?r.completeness==='partial':state==='missing_local'?r.current.availability===state:r.current.validity===state)));
 $('#records').replaceChildren();$('#count').textContent=`${filtered.length} of ${rows.length} records`;$('#empty').hidden=filtered.length>0;
 for(const r of filtered){
  const d=el('details',undefined,'record'),s=el('summary');d.id=r.id;s.append(el('span',r.kind,'type'),el('span',r.title||r.question||r.id,'record-title'),el('span',status(r),'badge'+(r.current.need_fix?' alert':'')));d.append(s);
  d.addEventListener('toggle',()=>{if(!d.open||d.dataset.loaded)return;d.dataset.loaded='1';const b=el('div',undefined,'detail');
   b.append(el('p',r.id+' · '+(r.group_id||'shared'),'meta'));
   for(const key of ['question','claim','reason','insight','prior_findings','reopen_when','notes'])if(r[key])b.append(el('p',(key==='reopen_when'?'Reopen when: ':'')+(typeof r[key]==='string'?r[key]:JSON.stringify(r[key]))));
   if(r.kind==='evaluation')b.append(el('p',`Observed reward: ${r.reward??'unavailable'} · ${r.model||r.agent||'unknown agent'} · ${r.reasoning_effort||'effort unrecorded'} · ${r.current.validity}`));
   if(r.current.missing_evidence.length)b.append(el('p',`${r.current.missing_evidence.length} local evidence files are unavailable. This is not a new model failure.`,'unavailable'));
   const decisions=rows.filter(x=>x.kind==='decision'&&x.target_id===r.id).sort((a,b)=>(a.created_at||'').localeCompare(b.created_at||''));
   for(const x of decisions)b.append(el('p',`${x.actor}: ${x.disposition} — ${x.reason}`));
   for(const x of r.portable_links||[]){if(!x.url)continue;const p=el('p'),a=el('a',x.label);a.href=x.url;p.append(a);b.append(p);}
   for(const id of r.depends_on||[]){const p=el('p'),a=el('a','Depends on '+id);a.href='?kind=&q='+encodeURIComponent(id);p.append(a);b.append(p);}
   const raw=el('details'),label=el('summary','Full record and evidence locators'),pre=el('pre',JSON.stringify(r,null,2));raw.append(label,pre);b.append(raw);d.append(b);
  });$('#records').append(d);
 }
}
fetch('records.json').then(r=>{if(!r.ok)throw Error(r.status);return r.json();}).then(data=>{
 rows=data.records;const groups=rows.filter(r=>r.kind==='group');groups.forEach((g,i)=>{const a=el('a',undefined,'group-card');a.href=g.story_url;a.append(el('span',String(i+1).padStart(2,'0'),'number'),el('h2',g.title),el('p',g.question),el('p',`${rows.filter(r=>r.kind==='experiment'&&r.group_id===g.id).length} experiments · ${rows.filter(r=>r.kind==='idea'&&r.group_id===g.id).length} ideas →`,'counts'));$('#groups').append(a);const option=el('option',g.title);option.value=g.id;$('#group').append(option);});
 $('#search').value=params.get('q')||'';if(params.has('kind'))$('#kind').value=params.get('kind');if(params.has('group'))$('#group').value=params.get('group');show();
}).catch(error=>{$('#records').textContent='Could not load the index. Serve this build over HTTP using scripts/med present --serve. '+error;});
$('#filters').addEventListener('submit',e=>e.preventDefault());for(const input of ['search','group','kind','status'])$('#'+input).addEventListener('input',show);
