"""Build the offline, read-only catalog workbench without browser dependencies."""

from __future__ import annotations

import copy
import json
import os
from pathlib import Path, PurePosixPath
from urllib.parse import quote, urlsplit


def _evidence_href(value: object, output: Path, root: Path) -> str | None:
    """Only link to a path confined to the workspace, including through symlinks."""
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        return None
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        return None
    try:
        target = (root / value).resolve()
    except (OSError, RuntimeError, ValueError):
        return None
    if not target.is_relative_to(root):
        return None
    return quote(os.path.relpath(target, output.parent), safe="/")


def _source_href(value: object) -> str | None:
    if not isinstance(value, str) or any(ord(char) < 32 for char in value):
        return None
    try:
        parsed = urlsplit(value)
        if parsed.scheme.lower() in {"http", "https"} and parsed.hostname:
            return value
    except ValueError:
        pass
    return None


def render_report(data: dict, output: Path, root: Path) -> None:
    """Write an interactive report; source data and catalog files are never edited."""
    output, root = Path(output).resolve(), Path(root).resolve()
    report = copy.deepcopy(data)
    for idea in report.get("ideas", []):
        idea["evidence_links"] = [
            {"path": path, "href": _evidence_href(path, output, root)}
            for path in idea.get("evidence", [])
        ]
        for source in idea.get("sources", []):
            source["href"] = _source_href(source.get("url"))
    for trial in report.get("trials", []):
        for evidence in trial.get("evidence", []):
            evidence["href"] = _evidence_href(evidence.get("path"), output, root)
        review = trial.get("review")
        if review:
            review["evidence_links"] = [
                {"path": path, "href": _evidence_href(path, output, root)}
                for path in review.get("evidence", [])
            ]
    payload = json.dumps(report, ensure_ascii=False, allow_nan=False).replace("<", "\\u003c")
    payload = payload.replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(_HTML.replace("__CATALOG_DATA__", payload), encoding="utf-8")


_HTML = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<title>TB3 · Research workbench</title>
<style>
:root{--ink:#202923;--muted:#6b746e;--line:#dce2d9;--paper:#f5f7f1;--white:#fff;--green:#244d3c;--pale:#e5eee4;--amber:#956216;--amber-bg:#faf0d9;--red:#a3433d;--red-bg:#f9e9e5;--blue:#365e89;--blue-bg:#eaf0f8;--radius:14px;--mono:ui-monospace,SFMono-Regular,Consolas,monospace;--sans:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:14px/1.5 var(--sans)}button,input,select{font:inherit}button,a,input,select{touch-action:manipulation}button{cursor:pointer}button:focus-visible,a:focus-visible,input:focus-visible,select:focus-visible{outline:3px solid #8cad9a;outline-offset:3px}a{color:var(--green);text-decoration-thickness:1px;text-underline-offset:3px}button{color:inherit}h1,h2,h3,p{margin:0}h1{font-size:30px;line-height:1.15;letter-spacing:-1.1px;font-weight:650}h2{font-size:18px;letter-spacing:-.3px}h3{font-size:15px;letter-spacing:-.2px}.shell{max-width:1520px;margin:0 auto;padding:30px 36px 48px}.masthead{display:flex;align-items:flex-end;justify-content:space-between;gap:24px;margin-bottom:25px}.eyebrow{font:11px var(--mono);letter-spacing:1.6px;text-transform:uppercase;color:var(--green);margin-bottom:10px}.subtitle{color:var(--muted);margin-top:10px;max-width:690px}.snapshot{flex-shrink:0;text-align:right;color:var(--muted);font-size:12px}.local-label{color:var(--green);display:block;font-weight:600;margin-bottom:4px}.local-label:before{content:"";display:inline-block;width:7px;height:7px;background:#689276;border-radius:50%;margin-right:7px}.stats{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:12px;margin-bottom:22px}.stat{background:var(--white);border:1px solid var(--line);border-radius:var(--radius);padding:16px 18px;min-height:109px}.stat .number{font-size:29px;line-height:1.1;font-weight:600;letter-spacing:-1px;margin:4px 0 6px}.stat .label{font-size:12px;color:var(--muted)}.stat .foot{font-size:11px;color:var(--muted)}.stat.primary{background:var(--green);color:#fff;border-color:var(--green)}.stat.primary .label,.stat.primary .foot{color:#d3e1d8}.tabs{display:flex;gap:25px;border-bottom:1px solid var(--line);margin-bottom:20px}.tab{background:transparent;border:0;padding:12px 0;position:relative;color:var(--muted);font-weight:600}.tab[aria-selected="true"]{color:var(--green)}.tab[aria-selected="true"]:after{content:"";height:3px;background:var(--green);position:absolute;bottom:-1px;left:0;right:0}.tab-count{display:inline-block;margin-left:6px;padding:0 6px;background:#e7ebe4;border-radius:5px;font:11px/18px var(--mono);color:var(--muted)}.toolbar{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:16px}.search{flex:1;min-width:220px;max-width:530px;position:relative}.search:before{content:"⌕";position:absolute;font-size:22px;color:var(--muted);left:12px;top:3px}.search input{width:100%;padding:10px 13px 10px 38px;background:var(--white);border:1px solid var(--line);border-radius:9px;color:var(--ink)}select{max-width:250px;padding:10px 33px 10px 12px;border:1px solid var(--line);border-radius:9px;background:var(--white);color:var(--ink)}.quiet-button{border:1px solid var(--line);border-radius:8px;background:var(--white);padding:8px 12px;font-size:12px}.filter-chip{display:inline-flex;align-items:center;gap:7px;font:12px var(--mono);padding:8px 10px;border:1px solid #adc4b3;background:var(--pale);border-radius:8px;max-width:100%;overflow-wrap:anywhere}.filter-chip button{border:0;background:transparent;font-size:17px;line-height:1;padding:0 2px}.work-area{display:grid;grid-template-columns:minmax(0,1.2fr) minmax(355px,1fr);gap:16px;align-items:start}.panel{background:var(--white);border:1px solid var(--line);border-radius:var(--radius);overflow:hidden}.panel-heading{display:flex;justify-content:space-between;align-items:baseline;gap:12px;padding:18px 20px;border-bottom:1px solid var(--line)}.panel-heading .count{color:var(--muted);font:11px var(--mono);white-space:nowrap}.table-wrap{overflow:auto;max-height:720px}table{width:100%;border-collapse:collapse;text-align:left}th{font-size:10px;letter-spacing:.7px;text-transform:uppercase;color:var(--muted);font-weight:600;background:#f9faf7;position:sticky;top:0;z-index:1}th,td{padding:12px 15px;border-bottom:1px solid #e9ede6;vertical-align:top}tbody tr:last-child td{border-bottom:0}tbody tr.selectable:hover{background:#f5f8f2}tbody tr.selected{background:#edf3e9}.row-select{display:block;border:0;background:transparent;text-align:left;padding:0;font-weight:600;color:var(--ink);max-width:260px;overflow-wrap:anywhere}.minor{color:var(--muted);font-size:11px;margin-top:4px;overflow-wrap:anywhere}.mono{font-family:var(--mono);font-size:11px}.badge{display:inline-flex;align-items:center;gap:5px;white-space:nowrap;padding:3px 7px;border-radius:5px;font-size:10px;font-weight:600;line-height:1.3;background:#eef0eb;color:#626e65}.badge.pass{background:var(--pale);color:var(--green)}.badge.candidate,.badge.stale{background:var(--amber-bg);color:var(--amber)}.badge.error,.badge.fail{background:var(--red-bg);color:var(--red)}.badge.control{background:var(--blue-bg);color:var(--blue)}.badges{display:flex;gap:5px;flex-wrap:wrap;margin-top:7px}.detail{padding:21px}.detail-title{overflow-wrap:anywhere;font-size:20px;line-height:1.3;letter-spacing:-.45px}.detail-subtitle{margin-top:6px;color:var(--muted);font:11px/1.6 var(--mono);overflow-wrap:anywhere}.section{margin-top:21px;padding-top:18px;border-top:1px solid #e7ece3}.section-title{font-size:10px;letter-spacing:1px;text-transform:uppercase;color:var(--muted);font-weight:650;margin-bottom:10px}.definition-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px 18px}.definition-grid dt{font-size:10px;color:var(--muted);margin-bottom:3px}.definition-grid dd{margin:0;overflow-wrap:anywhere;font-size:12px}.definition-grid{margin:0}.duration-row{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:16px}.duration{border-radius:8px;padding:10px;background:#f5f7f1}.duration .duration-value{font-size:17px;font-weight:600;letter-spacing:-.5px}.duration .duration-label{font-size:10px;color:var(--muted);margin-top:2px}.note{border-radius:8px;padding:11px 13px;background:#f3f5ef;color:#5a685e;font-size:12px;line-height:1.6}.note.amber{color:#805a1d;background:var(--amber-bg)}.note.red{color:var(--red);background:var(--red-bg)}.note.green{color:var(--green);background:var(--pale)}.review-text{font-size:13px;white-space:pre-wrap;overflow-wrap:anywhere;margin:8px 0}.case-list{display:grid;gap:7px}.case{border:1px solid #e6ebe2;border-radius:8px;padding:9px 11px}.case-header{display:flex;align-items:flex-start;gap:8px}.case-name{font:11px/1.6 var(--mono);overflow-wrap:anywhere}.case-symbol{font-weight:650;width:13px;flex-shrink:0}.case-symbol.passed{color:var(--green)}.case-symbol.failed{color:var(--red)}.case pre{font:10px/1.6 var(--mono);white-space:pre-wrap;overflow-wrap:anywhere;max-height:180px;overflow:auto;background:#f7f8f4;padding:9px;border-radius:5px;margin:8px 0 0}.evidence-list{list-style:none;margin:0;padding:0;display:grid;gap:10px}.evidence-list li{min-width:0}.evidence-list a,.evidence-list .invalid-link{font-size:12px;overflow-wrap:anywhere}.evidence-list .path{display:block;color:var(--muted);font:10px/1.5 var(--mono);overflow-wrap:anywhere;margin-top:2px}.invalid-link{color:var(--muted)}.cli{font:10px/1.6 var(--mono);white-space:pre-wrap;overflow-wrap:anywhere;display:block;background:#f1f4ed;padding:11px;border-radius:7px;color:#45594b;margin-top:9px}.empty{padding:42px 28px;text-align:center;color:var(--muted)}.empty strong{display:block;font-size:15px;color:var(--ink);font-weight:550;margin-bottom:7px}.empty p{font-size:12px;max-width:360px;margin:auto}.empty .empty-symbol{font:30px var(--mono);color:#a1b39f;margin-bottom:13px}.panel-note{padding:12px 18px;border-top:1px solid var(--line);font-size:11px;color:var(--muted);background:#fafbf8}.matrix-intro{display:flex;align-items:flex-start;justify-content:space-between;gap:20px;margin-bottom:17px}.matrix-intro p{color:var(--muted);font-size:12px;max-width:650px;margin-top:6px}.legend{display:flex;align-items:center;gap:13px;flex-wrap:wrap;font-size:11px;color:var(--muted)}.legend-item{display:inline-flex;align-items:center;gap:5px}.cell-mark{display:inline-flex;justify-content:center;align-items:center;min-width:25px;height:25px;border-radius:5px;font:12px var(--mono)}.cell-mark.passed{color:var(--green);background:var(--pale)}.cell-mark.failed{color:var(--red);background:var(--red-bg)}.cell-mark.missing{color:#8c958d;background:#f2f4ef}.cell-mark.mixed{color:var(--amber);background:var(--amber-bg)}.matrix-group{margin-bottom:20px}.matrix-table{min-width:600px}.matrix-table th{position:static}.matrix-table th:first-child{min-width:220px;max-width:380px}.matrix-table td:first-child{font:11px/1.6 var(--mono);max-width:380px;overflow-wrap:anywhere}.matrix-table .trial-column{min-width:125px;max-width:170px}.matrix-trial-button{border:0;background:none;padding:0;font:11px/1.5 var(--mono);text-align:left;color:var(--green);text-transform:none;letter-spacing:0;overflow-wrap:anywhere}.matrix-table td:not(:first-child){text-align:center}.matrix-caption{font-size:11px;color:var(--muted);padding:12px 16px}.idea-layout{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(355px,1fr);gap:16px;align-items:start}.idea-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.idea-card{display:flex;flex-direction:column;align-items:flex-start;text-align:left;background:var(--white);border:1px solid var(--line);border-radius:var(--radius);padding:20px;min-height:220px;transition:border-color .15s,background .15s}.idea-card:hover{border-color:#a8bcaa}.idea-card.selected{border-color:#6d9374;background:#f0f5eb;box-shadow:0 0 0 1px #6d9374}.idea-card .card-top{display:flex;justify-content:space-between;gap:10px;align-items:center;width:100%;margin-bottom:14px}.idea-id{font:10px var(--mono);color:var(--muted);overflow-wrap:anywhere}.idea-card h3{line-height:1.4;font-size:16px;margin-bottom:9px}.idea-card p{font-size:12px;color:var(--muted);line-height:1.7;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}.tags{display:flex;gap:5px;flex-wrap:wrap;margin-top:13px}.tag{font:10px var(--mono);color:#627361;background:#eaf0e4;border-radius:4px;padding:3px 6px}.idea-card .card-bottom{font-size:10px;color:var(--muted);margin-top:auto;padding-top:17px}.prose{font-size:13px;line-height:1.7;white-space:pre-wrap;overflow-wrap:anywhere}.link-button{border:0;background:none;padding:0;text-align:left;color:var(--green);text-decoration:underline;text-underline-offset:3px;font-size:12px}.trial-links{display:flex;flex-direction:column;gap:9px}.footer{display:flex;justify-content:space-between;gap:20px;padding-top:24px;margin-top:22px;border-top:1px solid var(--line);font-size:10px;color:var(--muted);line-height:1.6}.hidden,[hidden]{display:none!important}.visually-hidden{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap}.warning-list{padding-left:17px;margin:0}.warning-list li+li{margin-top:5px}.hash{font:10px/1.6 var(--mono);overflow-wrap:anywhere;color:var(--muted)}
@media(min-width:1250px){.detail-panel{position:sticky;top:18px;max-height:calc(100vh - 36px);overflow:auto}}@media(max-width:1100px){.shell{padding:25px 22px 40px}.work-area,.idea-layout{grid-template-columns:minmax(0,1fr) minmax(330px,.85fr)}.idea-grid{grid-template-columns:1fr}.stats{gap:8px}.stat{padding:14px}.table-wrap{max-height:680px}}@media(max-width:800px){.work-area,.idea-layout{grid-template-columns:1fr}.stats{grid-template-columns:repeat(3,minmax(0,1fr))}.stat:nth-child(4),.stat:nth-child(5){min-height:94px}.masthead{align-items:flex-start}.snapshot{max-width:130px;font-size:10px}.matrix-intro{flex-direction:column;gap:13px}.idea-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.detail-panel{scroll-margin-top:16px}.table-wrap{max-height:500px}}@media(max-width:520px){.shell{padding:22px 14px 32px}h1{font-size:25px}.eyebrow{font-size:9px}.masthead{gap:12px;margin-bottom:20px}.subtitle{font-size:12px}.snapshot{max-width:97px}.stats{grid-template-columns:repeat(2,minmax(0,1fr))}.stat.primary{grid-column:1 / -1;min-height:85px;display:grid;grid-template-columns:1fr auto;gap:0 10px;align-items:center}.stat.primary .number{grid-column:2;grid-row:1 / 3;font-size:35px}.stat.primary .foot{grid-column:1}.stat{min-height:98px}.stat .number{font-size:25px}.tabs{gap:19px}.tab{font-size:12px}.toolbar{gap:8px}.search{max-width:none;flex-basis:100%}select{max-width:100%;flex:1;min-width:0;font-size:12px}.idea-grid{grid-template-columns:1fr}.idea-card{min-height:190px}.detail{padding:18px}.panel-heading{padding:16px}.footer{flex-direction:column;gap:5px}.definition-grid{gap:12px}.matrix-table th:first-child{min-width:185px}}
</style>
</head>
<body>
<main class="shell">
  <header class="masthead">
    <div><div class="eyebrow">TB3 / Task research</div><h1>Research workbench</h1><p class="subtitle">Follow ideas into trials. Inspect the evidence, understand failures, and choose the next experiment.</p></div>
    <div class="snapshot"><span class="local-label">Offline snapshot</span><span id="generated-at"></span></div>
  </header>
  <section class="stats" id="stats" aria-label="Catalog summary"></section>
  <nav class="tabs" role="tablist" aria-label="Workbench views">
    <button class="tab" id="tab-trials" role="tab" aria-selected="true" aria-controls="view-trials" data-tab="trials">Trials<span class="tab-count" id="trials-count"></span></button>
    <button class="tab" id="tab-matrix" role="tab" aria-selected="false" aria-controls="view-matrix" data-tab="matrix" tabindex="-1">Failure matrix</button>
    <button class="tab" id="tab-ideas" role="tab" aria-selected="false" aria-controls="view-ideas" data-tab="ideas" tabindex="-1">Ideas<span class="tab-count" id="ideas-count"></span></button>
  </nav>
  <section id="view-trials" role="tabpanel" aria-labelledby="tab-trials">
    <div class="toolbar">
      <label class="search"><span class="visually-hidden">Search trials</span><input id="trial-search" type="search" placeholder="Search task, model, case, or failure…" autocomplete="off"></label>
      <label><span class="visually-hidden">Trial classification</span><select id="trial-class"><option value="">All classifications</option></select></label>
      <label><span class="visually-hidden">Task snapshot</span><select id="trial-snapshot"><option value="">All task snapshots</option></select></label>
      <label><span class="visually-hidden">Review state</span><select id="trial-review"><option value="">All review states</option><option value="unreviewed">Unreviewed</option><option value="current">Current review</option><option value="stale">Stale review</option><option value="genuine">Reviewed genuine failure</option></select></label>
      <span class="filter-chip" id="task-chip" hidden><span id="task-chip-label"></span><button id="clear-task" aria-label="Clear task filter">×</button></span>
    </div>
    <div class="work-area">
      <section class="panel"><div class="panel-heading"><h2>Trial ledger</h2><span class="count" id="trial-visible-count" aria-live="polite"></span></div><div class="table-wrap" id="trial-table"></div><p class="panel-note">A completed zero-reward model run is a failure candidate. A current evidence review is required to count a genuine model failure.</p></section>
      <aside class="panel detail-panel" id="trial-detail" aria-label="Selected trial details"></aside>
    </div>
  </section>
  <section id="view-matrix" role="tabpanel" aria-labelledby="tab-matrix" hidden>
    <div class="matrix-intro"><div><h2>What actually failed?</h2><p>Verifier case outcomes, grouped by task and recorded task snapshot. Columns preserve each trial’s agent, model, and classification; a missing case means it was not observed.</p></div><div class="legend"><span class="legend-item"><span class="cell-mark passed">✓</span> Passed</span><span class="legend-item"><span class="cell-mark failed">×</span> Failed</span><span class="legend-item"><span class="cell-mark missing">—</span> Not observed</span></div></div>
    <div class="toolbar"><label class="search"><span class="visually-hidden">Search failure matrix</span><input id="matrix-search" type="search" placeholder="Filter by task or verifier case…" autocomplete="off"></label><label><span class="visually-hidden">Matrix task</span><select id="matrix-task"><option value="">All tasks</option></select></label></div>
    <div id="matrix-content"></div>
  </section>
  <section id="view-ideas" role="tabpanel" aria-labelledby="tab-ideas" hidden>
    <div class="toolbar"><label class="search"><span class="visually-hidden">Search ideas</span><input id="idea-search" type="search" placeholder="Search title, tags, or hypothesis…" autocomplete="off"></label><label><span class="visually-hidden">Idea status</span><select id="idea-status"><option value="">All statuses</option></select></label><span class="minor" id="idea-visible-count" aria-live="polite"></span></div>
    <div class="idea-layout"><div class="idea-grid" id="idea-grid"></div><aside class="panel detail-panel" id="idea-detail" aria-label="Selected idea details"></aside></div>
  </section>
  <footer class="footer"><span>Read-only report · The catalog and original run artifacts remain the evidence sources.</span><span>Generated locally · No external assets or network requests</span></footer>
</main>
<script id="catalog-data" type="application/json">__CATALOG_DATA__</script>
<script>
'use strict';
const data=JSON.parse(document.getElementById('catalog-data').textContent);
const trials=Array.isArray(data.trials)?data.trials:[], ideas=Array.isArray(data.ideas)?data.ideas:[];
const $=id=>document.getElementById(id);
const state={tab:'trials',trial:trials[0]?.id??null,idea:ideas[0]?.id??null,task:''};
const labels={control_pass:'Control pass',control_fail:'Control fail',model_pass:'Model pass',model_failure_candidate:'Failure candidate',execution_error:'Execution error',incomplete:'Incomplete',unknown:'Unknown'};
const tones={control_pass:'control',control_fail:'error',model_pass:'pass',model_failure_candidate:'candidate',execution_error:'error',incomplete:'stale',unknown:''};
const list=v=>Array.isArray(v)?v:[];
const str=v=>v===null||v===undefined||v===''?'—':String(v);
const readable=v=>str(v).replaceAll('_',' ');
function el(tag,className,text){const n=document.createElement(tag);if(className)n.className=className;if(text!==undefined)n.textContent=String(text);return n;}
function append(parent,...children){children.filter(Boolean).forEach(child=>parent.append(child));return parent;}
function badge(text,tone=''){return el('span','badge '+tone,text);}
function classBadge(t){return badge(labels[t.classification]??readable(t.classification),tones[t.classification]??'');}
function section(title,...children){return append(el('section','section'),el('h3','section-title',title),...children);}
function empty(title,body){return append(el('div','empty'),el('div','empty-symbol','◇'),el('strong','',title),el('p','',body));}
function fmtDate(value){if(!value)return '—';const d=new Date(value);return Number.isNaN(d.valueOf())?String(value):d.toLocaleString(undefined,{year:'numeric',month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'});}
function duration(value){if(value===null||value===undefined||value===''||!Number.isFinite(Number(value)))return '—';const seconds=Number(value);if(seconds<60)return seconds.toFixed(seconds<10?1:0)+'s';if(seconds<3600)return Math.floor(seconds/60)+'m '+Math.round(seconds%60)+'s';return Math.floor(seconds/3600)+'h '+Math.floor(seconds%3600/60)+'m';}
function snapshot(t){return t.task_checksum||'';}
function shortHash(value){const text=str(value);return text.length>16?text.slice(0,12)+'…':text;}
function genuine(t){return t.classification==='model_failure_candidate'&&!!t.review&&!t.review_stale&&t.review.verdict==='genuine_failure';}
function trialText(t){return [t.id,t.job,t.task_id,t.agent,t.model,t.reasoning_effort,t.backend,t.task_checksum,t.classification,t.exception_type,t.review?.failure_mode,t.review?.explanation,...list(t.cases).map(c=>c.name),...list(t.warnings)].join(' ').toLowerCase();}
function button(text,onClick,className='link-button'){const b=el('button',className,text);b.type='button';b.addEventListener('click',onClick);return b;}
function link(text,href){if(!href)return el('span','invalid-link',text);const a=el('a','',text);a.href=href;if(/^https?:/i.test(href))a.target='_blank';a.rel='noopener noreferrer';return a;}
function evidenceList(entries){if(!entries.length)return el('p','minor','No evidence paths recorded.');const ul=el('ul','evidence-list');entries.forEach(e=>{const li=el('li');append(li,link(e.label??e.path,e.href));if(e.label&&e.path!==e.label)li.append(el('span','path',e.path));if(!e.href)li.append(el('span','path','Link unavailable: path is not a safe workspace-relative file.'));if(e.sha256)li.append(el('span','path','SHA-256 '+e.sha256));ul.append(li);});return ul;}
function definitions(items){const dl=el('dl','definition-grid');for(const [label,value]of items){const d=el('div');append(d,el('dt','',label),el('dd','',str(value)));dl.append(d);}return dl;}
function showTab(name){state.tab=name;document.querySelectorAll('[data-tab]').forEach(tab=>{const active=tab.dataset.tab===name;tab.setAttribute('aria-selected',String(active));tab.tabIndex=active?0:-1;});for(const key of ['trials','matrix','ideas'])$('view-'+key).hidden=key!==name;if(name==='matrix')renderMatrix();}
function selectTrial(id,focus=false){state.trial=id;renderTrials();showTab('trials');if(focus&&window.innerWidth<800)$('trial-detail').scrollIntoView({behavior:'smooth',block:'start'});}
function showTaskTrials(task){state.task=task;$('trial-search').value='';$('trial-class').value='';$('trial-review').value='';$('trial-snapshot').value='';const t=trials.find(t=>t.task_id===task);state.trial=t?.id??null;showTab('trials');renderTrials();}
function reviewBadge(t){if(t.review_stale)return badge('Stale review','stale');if(genuine(t))return badge('Reviewed genuine failure','fail');if(t.review)return badge('Reviewed','pass');return badge('Unreviewed');}
function renderStats(){const counts=data.summary?.counts??{};const count=k=>Number(counts[k]??trials.filter(t=>t.classification===k).length);const controlPass=count('control_pass'),controlFail=count('control_fail');const specs=[['Trials',trials.length,ideas.length+' ideas in the catalog','primary'],['Failure candidates',count('model_failure_candidate'),'Model zero-reward observations',''],['Reviewed genuine failures',trials.filter(genuine).length,'Current evidence reviews only',''],['Model passes',count('model_pass'),'Successful model executions',''],['Control checks',controlPass+controlFail,controlPass+' passed · '+controlFail+' failed',''],['Execution issues',count('execution_error')+count('incomplete')+count('unknown'),count('execution_error')+' errors · '+count('incomplete')+' incomplete · '+count('unknown')+' unknown','']];const host=$('stats');host.replaceChildren();specs.forEach(([label,value,foot,cls])=>host.append(append(el('div','stat '+cls),el('div','label',label),el('div','number',value),el('div','foot',foot))));$('generated-at').textContent=fmtDate(data.generated_at);$('trials-count').textContent=trials.length;$('ideas-count').textContent=ideas.length;}
function filteredTrials(){const q=$('trial-search').value.trim().toLowerCase(),classification=$('trial-class').value,review=$('trial-review').value,taskSnapshot=$('trial-snapshot').value;return trials.filter(t=>(!q||trialText(t).includes(q))&&(!classification||t.classification===classification)&&(!taskSnapshot||snapshot(t)===taskSnapshot)&&(!state.task||t.task_id===state.task)&&(!review||(review==='unreviewed'&&!t.review)||(review==='current'&&t.review&&!t.review_stale)||(review==='stale'&&t.review_stale)||(review==='genuine'&&genuine(t))));}
function renderTrials(){const visible=filteredTrials();$('trial-visible-count').textContent=visible.length+' / '+trials.length+' trials';$('task-chip').hidden=!state.task;$('task-chip-label').textContent=state.task;if(!visible.some(t=>t.id===state.trial))state.trial=visible[0]?.id??null;const host=$('trial-table');host.replaceChildren();if(!visible.length){host.append(empty(trials.length?'No matching trials':'No trials yet',trials.length?'Try another search or clear a filter.':'Import completed and partial run artifacts to build the trial ledger.'));}else{const table=el('table');const head=el('thead'),tr=el('tr');['Task / trial','Outcome','Time'].forEach(name=>tr.append(el('th','',name)));head.append(tr);table.append(head);const body=el('tbody');visible.forEach(t=>{const row=el('tr','selectable'+(state.trial===t.id?' selected':''));const task=el('td');const select=button(str(t.task_id),()=>selectTrial(t.id,true),'row-select');select.setAttribute('aria-label','Inspect '+str(t.id));if(state.trial===t.id)select.setAttribute('aria-current','true');append(task,select,el('div','minor mono',t.id),el('div','minor',[t.agent,t.model].filter(Boolean).join(' · ')||'Agent not recorded'));if(t.task_checksum){const hash=el('div','minor mono','Snapshot '+shortHash(t.task_checksum));hash.title=t.task_checksum;task.append(hash);}const outcome=append(el('td'),classBadge(t),el('div','minor','Reward '+str(t.reward)));if(t.review)outcome.append(append(el('div','badges'),reviewBadge(t)));const time=append(el('td'),el('span','mono',duration(t.timing?.total)),el('div','minor',fmtDate(t.started_at)));append(row,task,outcome,time);row.addEventListener('click',e=>{if(!e.target.closest('button'))selectTrial(t.id,true);});body.append(row);});table.append(body);host.append(table);}renderTrialDetail(trials.find(t=>t.id===state.trial));}
function renderTrialDetail(t){const host=$('trial-detail');host.replaceChildren();if(!t){host.append(empty('Inspect a trial','Select a trial to see settings, verifier outcomes, reviews, and evidence.'));return;}const detail=el('div','detail');append(detail,el('div','eyebrow','Selected trial'),el('h2','detail-title',str(t.task_id)),el('p','detail-subtitle',t.id),append(el('div','badges'),classBadge(t),reviewBadge(t)));const timings=el('div','duration-row');for(const [name,key]of [['Total','total'],['Agent','agent'],['Verifier','verifier']])timings.append(append(el('div','duration'),el('div','duration-value',duration(t.timing?.[key])),el('div','duration-label',name)));detail.append(timings);detail.append(section('Execution',definitions([['Agent',t.agent],['Model',t.model],['Reasoning effort',t.reasoning_effort],['Backend',t.backend],['Execution mode',t.execution_mode],['Harbor version',t.harbor_version],['Task snapshot',t.task_checksum],['Reward',t.reward],['Job',t.job],['Started',fmtDate(t.started_at)],['Finished',fmtDate(t.finished_at)]])));if(t.exception_type)detail.append(section('Execution exception',el('div','note red',t.exception_type)));if(list(t.warnings).length){const ul=el('ul','warning-list');t.warnings.forEach(w=>ul.append(el('li','',w)));detail.append(section('Evidence warnings',append(el('div','note amber'),ul)));}const review=section('Evidence review');if(t.review_stale)review.append(el('div','note amber','This review is stale: its source fingerprint no longer matches the trial. It is excluded from the reviewed genuine failure count.'));if(t.review){append(review,definitions([['Verdict',readable(t.review.verdict)],['Failure mode',readable(t.review.failure_mode)],['Updated',fmtDate(t.review.updated_at)]]));if(t.review.explanation)review.append(el('p','review-text',t.review.explanation));if(t.review.next_action)append(review,el('div','section-title','Next action'),el('p','prose',t.review.next_action));if(list(t.review.evidence_links).length)review.append(section('Review evidence',evidenceList(t.review.evidence_links)));}else{review.append(el('div','note'+(t.classification==='model_failure_candidate'?' amber':''),t.classification==='model_failure_candidate'?'This zero-reward model trial is a candidate for failure analysis. Inspect task validity, execution health, and verifier evidence before assigning a verdict.':'No evidence review has been recorded for this trial.'));}review.append(el('code','cli','.venv/bin/python scripts/tb3_catalog.py review --help'));detail.append(review);const cases=section('Verifier cases · '+list(t.cases).length+' observed');if(!list(t.cases).length)cases.append(el('p','minor','No verifier case outcomes were parsed. Missing cases are not evidence of a pass or failure.'));else{const group=el('div','case-list');t.cases.forEach(c=>{const box=el('div','case');append(box,append(el('div','case-header'),el('span','case-symbol '+c.status,c.status==='passed'?'✓':'×'),el('span','case-name',c.name)));if(c.detail)box.append(el('pre','',c.detail));group.append(box);});cases.append(group);}detail.append(cases);detail.append(section('Run evidence',evidenceList(list(t.evidence))));if(t.task_sha256||t.source_sha256||t.evidence_sha256){const fingerprint=section('Evidence fingerprints');if(t.task_sha256)append(fingerprint,el('div','minor','Task SHA-256'),el('p','hash',t.task_sha256));if(t.evidence_sha256)append(fingerprint,el('div','minor','Evidence bundle SHA-256'),el('p','hash',t.evidence_sha256));if(t.source_sha256)append(fingerprint,el('div','minor','Result SHA-256'),el('p','hash',t.source_sha256));detail.append(fingerprint);}const matched=ideas.filter(i=>i.id===t.task_id);if(matched.length)detail.append(section('Related idea',...matched.map(i=>button(i.title,()=>{state.idea=i.id;$('idea-search').value='';$('idea-status').value='';renderIdeas();showTab('ideas');}))));host.append(detail);}
function renderMatrix(){
  const q=$('matrix-search').value.trim().toLowerCase(), task=$('matrix-task').value;
  const groups=new Map();
  trials.forEach(t=>{
    const taskId=t.task_id||'(task not recorded)';
    if(task&&taskId!==task)return;
    const key=JSON.stringify([taskId,snapshot(t)]);
    if(!groups.has(key))groups.set(key,{taskId,checksum:snapshot(t),trials:[]});
    groups.get(key).trials.push(t);
  });
  const host=$('matrix-content');host.replaceChildren();let rendered=0;
  for(const {taskId,checksum,trials:group} of groups.values()){
    const names=[...new Set(group.flatMap(t=>list(t.cases).map(c=>c.name)))];
    const matchingNames=names.filter(name=>!q||taskId.toLowerCase().includes(q)||String(name).toLowerCase().includes(q));
    if(q&&!taskId.toLowerCase().includes(q)&&!matchingNames.length)continue;
    rendered++;
    const panel=el('section','panel matrix-group'),heading=el('div','panel-heading');
    const title=el('div'),hash=el('div','minor mono',checksum?'Snapshot '+shortHash(checksum):'Task snapshot not recorded');
    if(checksum)hash.title=checksum;
    append(title,el('h3','',taskId),hash);
    append(heading,title,el('span','count',group.length+' trials · '+names.length+' cases'));panel.append(heading);
    if(!names.length){
      panel.append(empty('No observed verifier cases','This task has trial records but no parsed case outcomes. Inspect its run evidence.'));
    }else{
      const wrap=el('div','table-wrap'),table=el('table','matrix-table'),thead=el('thead'),top=el('tr');
      top.append(el('th','','Verifier case'));
      group.forEach(t=>{
        const th=el('th','trial-column');
        append(th,button(t.id,()=>{
          state.task='';$('trial-search').value='';$('trial-class').value='';$('trial-review').value='';$('trial-snapshot').value='';
          selectTrial(t.id);
        },'matrix-trial-button'),el('div','minor',[t.agent,t.model].filter(Boolean).join(' · ')||'Unrecorded agent'),append(el('div','badges'),classBadge(t)));
        top.append(th);
      });
      thead.append(top);table.append(thead);
      const body=el('tbody');
      matchingNames.forEach(name=>{
        const row=el('tr');row.append(el('td','',name));
        group.forEach(t=>{
          const matches=list(t.cases).filter(c=>c.name===name),statuses=[...new Set(matches.map(c=>c.status))];
          const status=statuses.length>1?'mixed':statuses[0]||'missing';
          const symbol={passed:'✓',failed:'×',missing:'—',mixed:'±'}[status]||'?';
          const td=el('td'),mark=el('span','cell-mark '+status,symbol);
          const outcome={passed:'Passed',failed:'Failed',missing:'Not observed',mixed:'Mixed outcomes across duplicate case records'}[status]||'Unknown';
          mark.title=outcome+(matches[0]?.detail?' · '+matches[0].detail:'');
          mark.setAttribute('aria-label',str(name)+': '+outcome+' in '+t.id);
          td.append(mark);row.append(td);
        });
        body.append(row);
      });
      table.append(body);wrap.append(table);
      append(panel,wrap,el('p','matrix-caption','Select a trial heading to inspect its evidence. A dash means not observed. Snapshot checksums identify recorded task versions; they do not establish execution equivalence.'));
    }
    host.append(panel);
  }
  if(!rendered)host.append(append(el('div','panel'),empty(trials.length?'No matching tasks':'No case evidence yet',trials.length?'Try another task or verifier-case search.':'Import trial results to compare verifier outcomes across runs.')));
}
function renderIdeas(){const q=$('idea-search').value.trim().toLowerCase(),status=$('idea-status').value;const visible=ideas.filter(i=>(!q||[i.id,i.title,i.hypothesis,i.why_hard,i.next_action,...list(i.tags)].join(' ').toLowerCase().includes(q))&&(!status||i.status===status));if(!visible.some(i=>i.id===state.idea))state.idea=visible[0]?.id??null;$('idea-visible-count').textContent=visible.length+' / '+ideas.length+' ideas';const host=$('idea-grid');host.replaceChildren();if(!visible.length)host.append(append(el('div','panel'),empty(ideas.length?'No matching ideas':'A place for your next hard task',ideas.length?'Try another keyword, tag, or status.':'Capture a hypothesis, why it should be hard, and the next small trial.')));visible.forEach(i=>{const card=button('',()=>{state.idea=i.id;renderIdeas();if(window.innerWidth<800)$('idea-detail').scrollIntoView({behavior:'smooth',block:'start'});},'idea-card'+(i.id===state.idea?' selected':''));card.setAttribute('aria-label','Inspect idea '+str(i.title));if(i.id===state.idea)card.setAttribute('aria-current','true');append(card,append(el('div','card-top'),el('span','idea-id',i.id),badge(readable(i.status))),el('h3','',str(i.title)),el('p','',i.hypothesis||i.why_hard||'No hypothesis recorded.'));const tags=el('div','tags');list(i.tags).forEach(tag=>tags.append(el('span','tag',tag)));card.append(tags);const count=trials.filter(t=>t.task_id===i.id).length;card.append(el('div','card-bottom',count?count+' linked trial'+(count===1?'':'s'):'No linked trials yet'));host.append(card);});renderIdeaDetail(ideas.find(i=>i.id===state.idea));}
function renderIdeaDetail(i){const host=$('idea-detail');host.replaceChildren();if(!i){host.append(empty('Inspect an idea','Select an idea to see its hypothesis, sources, and linked trials.'));return;}const detail=el('div','detail');append(detail,el('div','eyebrow','Selected idea'),el('h2','detail-title',str(i.title)),el('p','detail-subtitle',i.id),append(el('div','badges'),badge(readable(i.status))));const tags=el('div','tags');list(i.tags).forEach(t=>tags.append(button(t,()=>{$('idea-search').value=t;renderIdeas();},'tag quiet-button')));detail.append(tags);for(const [label,value]of [['Hypothesis',i.hypothesis],['Why this is hard',i.why_hard],['Next action',i.next_action]])detail.append(section(label,el('p','prose',value||'Not recorded.')));if(i.notes)detail.append(section('Notes',el('p','prose',Array.isArray(i.notes)?i.notes.join('\n'):i.notes)));const linked=trials.filter(t=>t.task_id===i.id),trialSection=section('Linked trials · '+linked.length);if(linked.length){const links=el('div','trial-links');linked.forEach(t=>links.append(append(el('div'),button(t.id,()=>{state.task='';$('trial-search').value='';$('trial-class').value='';$('trial-review').value='';$('trial-snapshot').value='';selectTrial(t.id,true);}),append(el('div','badges'),classBadge(t),reviewBadge(t)))));append(trialSection,links,button('View all trials for this idea →',()=>showTaskTrials(i.id),'link-button'));}else trialSection.append(el('p','minor','No trials with a matching task ID have been recorded.'));detail.append(trialSection);if(list(i.sources).length){const ul=el('ul','evidence-list');i.sources.forEach(s=>ul.append(append(el('li'),link(s.note||s.url,s.href),s.note?el('span','path',s.url):null)));detail.append(section('Source material',ul));}detail.append(section('Local evidence',evidenceList(list(i.evidence_links))));detail.append(section('Curate in the catalog',el('p','minor','Update structured idea records through the CLI, then regenerate this report.'),el('code','cli','.venv/bin/python scripts/tb3_catalog.py curate --help')));host.append(detail);}
function options(id,values,label=x=>x){const select=$(id);[...new Set(values.filter(Boolean))].sort().forEach(value=>{const option=el('option','',label(value));option.value=value;select.append(option);});}
options('trial-class',trials.map(t=>t.classification),x=>labels[x]??readable(x));options('idea-status',ideas.map(i=>i.status),readable);options('matrix-task',trials.map(t=>t.task_id));options('trial-snapshot',trials.map(snapshot),shortHash);
document.querySelectorAll('[data-tab]').forEach(tab=>{tab.addEventListener('click',()=>showTab(tab.dataset.tab));tab.addEventListener('keydown',event=>{if(!['ArrowLeft','ArrowRight','Home','End'].includes(event.key))return;event.preventDefault();const tabs=[...document.querySelectorAll('[data-tab]')];const current=tabs.indexOf(tab);const next=event.key==='Home'?0:event.key==='End'?tabs.length-1:(current+(event.key==='ArrowRight'?1:-1)+tabs.length)%tabs.length;showTab(tabs[next].dataset.tab);tabs[next].focus();});});
for(const id of ['trial-search','trial-class','trial-review','trial-snapshot'])$(id).addEventListener(id==='trial-search'?'input':'change',renderTrials);
for(const id of ['idea-search','idea-status'])$(id).addEventListener(id==='idea-search'?'input':'change',renderIdeas);
for(const id of ['matrix-search','matrix-task'])$(id).addEventListener(id==='matrix-search'?'input':'change',renderMatrix);
$('clear-task').addEventListener('click',()=>{state.task='';renderTrials();});
renderStats();renderTrials();renderIdeas();
</script>
</body>
</html>
'''
