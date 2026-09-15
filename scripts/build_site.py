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
    'overview': 'Research overview',
    'boundaries': 'Earlier boundary audits',
    'anatomy': 'Anatomical identity',
    'absorption': 'Tissue ownership',
    'aneurysm': 'Aneurysm localization',
}


def build():
    chapters = {key: (ROOT / 'site/content' / (key + '.html')).read_text() for key in CHAPTERS}
    # Raw-text JSON must not prematurely terminate its containing script.
    payload = json.dumps(chapters, ensure_ascii=False).replace('<', '\\u003c')
    navigation = ''.join(f'<a href="#{key}" data-chapter="{key}">{label}</a>' for key, label in CHAPTERS.items())
    return '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Finding a hard task · TB3 research</title>
<meta name="description" content="An agent-assisted benchmark investigation: findings, experiments, trace walkthroughs and evidence.">
<style>
*{box-sizing:border-box}html,body{margin:0;height:100%;background:#f6f4ee;color:#172b32;font-family:system-ui,sans-serif}body{display:flex;flex-direction:column}header{padding:12px 24px;border-bottom:1px solid #ccd4d1;background:#fffefa}header p{margin:0 0 8px;font-size:11px;letter-spacing:.12em;color:#54696d}nav{display:flex;flex-wrap:wrap;gap:6px 22px}nav a{color:#006e65;font-size:13px;padding:5px 0;text-decoration:none;border-bottom:2px solid transparent}nav a[aria-current]{border-color:#006e65;font-weight:700}a:focus-visible{outline:3px solid #b36c16;outline-offset:3px}iframe{width:100%;flex:1;min-height:0;border:0;background:#f6f4ee}.skip{position:absolute;left:-10000px}.skip:focus{left:10px;top:10px;background:white;padding:10px}noscript{padding:32px}@media(max-width:600px){header{padding:10px 16px}nav{gap:3px 15px}nav a{font-size:12px}}@media print{body{height:auto;display:block}header{display:none}iframe{display:block;height:var(--print-height,100vh);overflow:visible}}
</style></head><body>
<a class="skip" href="#reader">Skip to selected study</a>
<header><p>TB3 / INTERVIEW RESEARCH REPORT</p><nav aria-label="Study navigation">''' + navigation + '''</nav></header>
<iframe id="reader" title="Research overview"></iframe>
<noscript>This bundled report needs JavaScript for chapter navigation. Written evidence is available in the <a href="https://github.com/qianyizhang/tb3/blob/main/docs/archive.md">repository archive</a>.</noscript>
<script id="chapters" type="application/json">''' + payload + '''</script>
<script>
const chapters=JSON.parse(document.getElementById('chapters').textContent);
const reader=document.getElementById('reader');let active='';
function route(){
 const [requested,...parts]=decodeURIComponent(location.hash.slice(1)).split('/');
 const key=Object.hasOwn(chapters,requested)?requested:'overview';
 const anchor=parts.join('/');
 document.querySelectorAll('[data-chapter]').forEach(a=>{if(a.dataset.chapter===key)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current')});
 reader.title=document.querySelector(`[data-chapter="${key}"]`).textContent;
 document.title=reader.title+' · TB3 research';
 function position(){if(anchor)reader.contentDocument.getElementById(anchor)?.scrollIntoView();else reader.contentWindow.scrollTo(0,0)}
 if(active===key){position();return}
 active=key;
 reader.onload=()=>{
  const doc=reader.contentDocument;
  doc.addEventListener('click',event=>{
   const a=event.target.closest('a');if(!a)return;
   const href=a.getAttribute('href')||'';
   if(href.startsWith('#study=')){event.preventDefault();location.hash=href.slice(7)}
   else if(href.startsWith('#')){event.preventDefault();location.hash=active+'/'+href.slice(1)}
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
        print('Five bundled chapters match their tracked sources.')
    else:
        output.write_text(text)
        print(f'Built site/index.html ({len(text.encode()):,} bytes); no runtime assets required.')


if __name__=='__main__':
    main()
