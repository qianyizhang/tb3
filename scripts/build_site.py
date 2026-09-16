#!/usr/bin/env python3
"""Bundle the tracked interview chapters into one offline GitHub Pages entry point.

Standard library only. Reads site/content; never reads or writes trial evidence.
Use --check to verify the committed output without writing it.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = {
    'overview': 'Overview',
    'boundaries': 'Boundary errors',
    'anatomy': 'Organ identity',
    'absorption': 'Tissue ownership',
    'aneurysm': 'Aneurysm localization',
    'registration': 'Registration',
    'vessels': 'Vessels & airways',
}


def load_chapters(local_scans=None):
    chapters = {key: (ROOT / 'site/content' / (key + '.html')).read_text() for key in CHAPTERS}
    css = (ROOT / 'site/report.css').read_text()
    viewer = (ROOT / 'site/aneurysm.js').read_text()
    figures = (ROOT / 'site/aneurysm-figures.json').read_text()
    registration = (ROOT / 'site/registration-figures.json').read_text()
    registration_viewer = (ROOT / 'site/registration.js').read_text()
    vessels = (ROOT / 'site/vessel-figures.json').read_text()
    vessel_viewer = (ROOT / 'site/vessels.js').read_text()
    for key, chapter in chapters.items():
        chapter = chapter.replace('<link rel="stylesheet" href="../report.css">', '<style data-report-theme>' + css + '</style>')
        chapter = chapter.replace('__SCAN_FIGURES__', figures)
        chapter = chapter.replace('<script src="../aneurysm.js"></script>', '<script>' + viewer + '</script>')
        chapter = chapter.replace('__REGISTRATION_FIGURES__', registration)
        chapter = chapter.replace('<script src="../registration.js"></script>', '<script>' + registration_viewer + '</script>')
        chapter = chapter.replace('__VESSEL_FIGURES__', vessels)
        chapter = chapter.replace('<script src="../vessels.js"></script>', '<script>' + vessel_viewer + '</script>')
        if local_scans is not None:
            config = json.dumps(local_scans).replace('<', '\\u003c')
            chapter = chapter.replace('<script id="local-scans" type="application/json">null</script>', '<script id="local-scans" type="application/json">' + config + '</script>')
        chapters[key] = chapter
    return chapters


def build(local_scans=None):
    chapters = load_chapters(local_scans)
    # Raw-text JSON must not prematurely terminate its containing script.
    payload = json.dumps(chapters, ensure_ascii=False).replace('<', '\\u003c')
    navigation = ''.join(f'<a href="#{key}" data-chapter="{key}">{label}</a>' for key, label in CHAPTERS.items())
    return '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Finding a hard task · TB3 research</title>
<meta name="description" content="An agent-assisted benchmark investigation: findings, experiments, trace walkthroughs and evidence.">
<style>
*{box-sizing:border-box}html,body{margin:0;height:100%;background:#f6f4ee;color:#172b32;font-family:system-ui,sans-serif}body{display:flex;flex-direction:column}header{padding:12px 24px;border-bottom:1px solid #ccd4d1;background:#fffefa}header p{margin:0 0 8px;font-size:11px;letter-spacing:.12em;color:#54696d}nav{display:flex;flex-wrap:wrap;gap:6px 22px}nav a{color:#006e65;font-size:13px;padding:5px 0;text-decoration:none;border-bottom:2px solid transparent}nav a[aria-current]{border-color:#006e65;font-weight:700}a:focus-visible{outline:3px solid #b36c16;outline-offset:3px}iframe{width:100%;flex:1;min-height:0;border:0;background:#f6f4ee}.skip{position:absolute;left:-10000px}.skip:focus{left:10px;top:10px;background:white;padding:10px}noscript{padding:32px}@media(max-width:600px){header{padding:10px 16px}nav{gap:3px 15px}nav a{font-size:12px}}@media print{body{height:auto;display:block}header{display:none}iframe{display:block;height:var(--print-height,100vh);overflow:visible}}
.masthead{display:flex;justify-content:space-between;align-items:center;gap:16px}.masthead p{margin:0}.reader-tools{display:flex;gap:12px;align-items:center;font-size:11px;color:#54696d}.reader-tools button{font:inherit;color:#006e65;background:none;border:0;padding:3px;cursor:pointer}.mode{color:#006e65}header nav{margin-top:7px}dialog{max-width:520px;border:1px solid #ccd4d1;border-radius:9px;padding:26px;background:#fffefa;color:#172b32;line-height:1.6}dialog::backdrop{background:#172b3270}dialog h2{font:400 28px Georgia,serif;margin-top:0}dialog dt{font-weight:650}dialog dd{margin:0 0 12px;color:#54696d;font-size:14px}dialog button{padding:7px 14px;cursor:pointer}button:focus-visible,summary:focus-visible{outline:3px solid #b36c16;outline-offset:3px}@media(max-width:600px){.mode{display:none}header p{font-size:10px}}
</style></head><body>
<a class="skip" href="#reader">Skip to selected study</a>
<header><div class="masthead"><p>TB3 / FINDING A HARD TASK</p><div class="reader-tools"><span class="mode">''' + ('Local · full scan explorer' if local_scans is not None else 'Offline-ready report') + '''</span><button id="guide-open">Reading guide</button></div></div><nav aria-label="Study navigation">''' + navigation + '''</nav></header>
<iframe id="reader" title="Research overview"></iframe>
<dialog id="guide"><h2>A short reading guide</h2><p>The studies ask whether general coding agents can solve small, demanding tasks. Each page separates the task, the observed result, and what it can tell us.</p><dl><dt>Mask or segmentation</dt><dd>A set of image pixels labeled as one organ or structure.</dd><dt>Voxel</dt><dd>A three-dimensional image pixel. A coordinate such as [166,273,84] picks one voxel.</dd><dt>CT / MRA</dt><dd>CT uses X-rays to show anatomy. MRA is an MRI technique used here to show brain vessels.</dd><dt>Reference</dt><dd>The source annotation used to grade an answer. Its limits are stated in each study.</dd><dt>Trace</dt><dd>The recorded commands, images, and public messages from an agent attempt.</dd><dt>Sol/xhigh and Terra/max</dt><dd>Model and reasoning-effort settings. Each case was attempted once unless stated otherwise.</dd><dt>Control</dt><dd>A known answer used to check the grader. “Oracle” means the reference solution; “no-op” means leaving the task untouched.</dd></dl><button id="guide-close">Close guide</button></dialog>
<noscript>This bundled report needs JavaScript for chapter navigation. Written evidence is available in the <a href="https://github.com/qianyizhang/tb3/blob/main/docs/archive.md">repository archive</a>.</noscript>
<script id="chapters" type="application/json">''' + payload + '''</script>
<script>
const chapters=JSON.parse(document.getElementById('chapters').textContent);
const reader=document.getElementById('reader');let active='';
document.getElementById('guide-open').onclick=()=>document.getElementById('guide').showModal();
document.getElementById('guide-close').onclick=()=>document.getElementById('guide').close();
function navigate(hash){if(location.hash.slice(1)===hash)route();else location.hash=hash}
document.querySelector('header nav').onclick=event=>{const a=event.target.closest('[data-chapter]');if(a){event.preventDefault();navigate(a.dataset.chapter)}};
document.querySelector('.skip').onclick=event=>{event.preventDefault();reader.focus()};
function route(){
 let hash=location.hash.slice(1);try{hash=decodeURIComponent(hash)}catch{}
 const [requested,...parts]=hash.split('/');
 const key=Object.hasOwn(chapters,requested)?requested:'overview';
 const anchor=parts.join('/');
 document.querySelectorAll('[data-chapter]').forEach(a=>{if(a.dataset.chapter===key)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current')});
 reader.title=document.querySelector(`[data-chapter="${key}"]`).textContent;
 document.title=reader.title+' · TB3 research';
 function position(){if(anchor){const target=reader.contentDocument.getElementById(anchor);if(target){const tab=reader.contentDocument.querySelector(`[aria-controls="${CSS.escape(anchor)}"][role="tab"]`);if(target.hidden&&tab)tab.click();target.scrollIntoView()}}else reader.contentWindow.scrollTo(0,0)}
 if(active===key){position();return}
 active=key;
 reader.onload=()=>{
  const doc=reader.contentDocument;
  doc.addEventListener('click',event=>{
   const a=event.target.closest('a');if(!a)return;
   const href=a.getAttribute('href')||'';
   if(href.startsWith('#study=')){event.preventDefault();navigate(href.slice(7))}
   else if(href.startsWith('#')){event.preventDefault();navigate(active+'/'+href.slice(1))}
   else if(href.startsWith('data:image/')){
    event.preventDefault();
    const dialog=doc.createElement('dialog');dialog.style.cssText='padding:18px;background:#f6f4ee;border:1px solid #54696d;max-width:95vw;max-height:95vh';
    const close=doc.createElement('button');close.textContent='Close image';close.onclick=()=>dialog.close();
    const image=doc.createElement('img');image.src=href;image.alt=a.querySelector('img')?.alt||'Evidence image';image.style.cssText='display:block;max-width:90vw;max-height:80vh;object-fit:contain';
    dialog.append(close,image);doc.body.append(dialog);dialog.addEventListener('close',()=>dialog.remove());dialog.showModal();
   }
   else if(href.startsWith('https:')){a.target='_blank';a.rel='noopener noreferrer'}
  });
  // Keep local chapter anchors stable after deferred images acquire dimensions.
  for(const img of doc.images){if(!img.complete)img.addEventListener('load',()=>{if(anchor)position()},{once:true})}
  position();
 };
 reader.srcdoc=chapters[key];
}
addEventListener('hashchange',route);route();
addEventListener('beforeprint',()=>{document.documentElement.style.setProperty('--print-height',reader.contentDocument.documentElement.scrollHeight+'px')});
</script></body></html>
'''


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args=parser.parse_args()
    output=ROOT/'site/index.html'
    text=build()
    if args.check:
        if not output.exists() or output.read_text()!=text:
            raise SystemExit('site/index.html is stale: run python3 scripts/build_site.py')
        print(f'{len(CHAPTERS)} bundled chapters match their tracked sources.')
    else:
        output.write_text(text)
        print(f'Built site/index.html ({len(text.encode()):,} bytes); no runtime assets required.')


if __name__=='__main__':
    main()
