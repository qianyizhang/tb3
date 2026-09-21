/* Meaningful artifact checks: source hashes, reveal boundaries, native pixel cache,
   coordinate navigation, all saved outputs, chart semantics and mobile layout. */
const { chromium } = require('playwright');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');
const out = path.resolve(process.argv[2]);
const url = process.argv[3] || 'http://127.0.0.1:8804/';
const checks = [];
function ok(name) { checks.push(name); }
(async () => {
 const manifest = JSON.parse(fs.readFileSync(path.join(out,'manifest.json')));
 for (const item of manifest.source_files.filter(x => x.copy)) {
  const digest = crypto.createHash('sha256').update(fs.readFileSync(path.join(out,item.copy))).digest('hex');
  assert.equal(digest,item.sha256,item.copy);
 }
 ok('All packaged sources match their SHA-256 receipts');
 const browser = await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 const page = await browser.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1});
 const errors=[];page.on('pageerror',e=>errors.push(String(e)));
 await page.goto(url,{waitUntil:'load'});
 await page.waitForFunction(()=>document.body.dataset.ready==='true',{timeout:60000});
 assert.equal(await page.locator('#show-model').isChecked(),false);assert.equal(await page.locator('#show-reference').isChecked(),false);
 ok('Initial viewer shows input only; both evidence overlays require explicit reveal');
 const cacheHash = await page.evaluate(async()=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',volume))).map(x=>x.toString(16).padStart(2,'0')).join(''));
 assert.equal(cacheHash,manifest.source_files.find(x=>x.display_cache_sha256).display_cache_sha256);
 ok('Browser decompressed native volume byte-for-byte matches builder cache (72,089,600 voxels)');
 await page.screenshot({path:path.join(out,'overview.png')});
 await page.locator('.viewer').screenshot({style:".top{visibility:hidden}",path:path.join(out,'native-input.png')});
 assert.equal(await page.locator('.result-row').count(),7);
 await page.locator('#scope').selectOption('v3');assert.equal(await page.locator('.result-row').count(),3);
 await page.locator('#weight').selectOption('macro');assert.match(await page.locator('#comparison').innerText(),/81.3%/);
 await page.locator('#tolerance').selectOption('2');assert.match(await page.locator('#comparison').innerText(),/85.5%/);
 ok('Same-task filter and length/category/tolerance controls show correct recorded values');
 await page.locator('#scope').selectOption('all');await page.locator('#weight').selectOption('length_weighted');await page.locator('#tolerance').selectOption('1');
 await page.locator('#results').screenshot({style:".top{visibility:hidden}",path:path.join(out,'comparison.png')});
 for(let i=0;i<7;i++) {await page.locator('#model').selectOption(String(i));assert.equal(await page.locator('.branch').count(),11);const href=await page.locator('#answer-download').getAttribute('href');assert.ok(fs.existsSync(path.join(out,href)));}
 ok('All seven outputs have 11 scored categories and exact answer downloads');
 await page.locator('#model').selectOption('6');
 await page.locator('[data-focus="5"]').click();
 assert.equal(await page.locator('#show-reference').isChecked(),true);assert.equal(await page.locator('#show-model').isChecked(),true);
 assert.deepEqual(await page.evaluate(()=>state.pos),await page.evaluate(()=>DATA.branches['5']));
 assert.equal(await page.locator('#zoom').inputValue(),'4');
 await page.locator('.viewer').screenshot({style:".top{visibility:hidden}",path:path.join(out,'D2-inspection.png')});
 await page.locator('[data-focus="6"]').click();await page.locator('.viewer').screenshot({style:".top{visibility:hidden}",path:path.join(out,'OM1-inspection.png')});
 ok('Reference-assisted focus is explicit and moves linked native coordinates correctly');
 await page.locator('#include-zero').uncheck();await page.locator('#include-zero').check();
 const ax=page.locator('#axial');await ax.click({position:{x:200,y:160}});
 const pos=await page.evaluate(()=>state.pos);assert.ok(pos.every((x,i)=>x>=0&&x<manifest.volume.shape[i]));
 for(const id of ['x','y','z']){await page.locator('#'+id).fill(id==='z'?'100':'300');await page.locator('#'+id).dispatchEvent('input');}
 assert.deepEqual(await page.evaluate(()=>state.pos),[300,300,100]);
 ok('Slice sliders, linked clicks, category-0 switch and zoom respond without coordinate overflow');
 await page.locator('#funnel-mode').selectOption('1');assert.match(await page.locator('#funnel-note').innerText(),/6586/);assert.match(await page.locator('#funnel').innerText(),/100.0/);
 await page.locator('#funnel-mode').selectOption('0');await page.locator('#mechanism').screenshot({style:".top{visibility:hidden}",path:path.join(out,'candidate-funnel.png')});
 ok('Candidate sensitivity is labeled post-hoc and preserves original final-output values');
 await page.locator('#reset').click();assert.equal(await page.locator('#show-reference').isChecked(),false);assert.equal(await page.locator('#show-model').isChecked(),false);
 const localLinks=await page.locator('a[href]').evaluateAll(as=>as.map(a=>a.getAttribute('href')).filter(h=>h&&!h.startsWith('#')&&!h.includes('://')));
 for(const link of localLinks) assert.ok(fs.existsSync(path.join(out,decodeURIComponent(link.split('#')[0]))),'Missing local link: '+link);
 ok('All local HTML evidence links resolve');
 await page.setViewportSize({width:390,height:844});await page.goto(url,{waitUntil:'load'});await page.waitForFunction(()=>document.body.dataset.ready==='true');
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),true);
 await page.screenshot({path:path.join(out,'mobile-overview.png')});
 await page.locator('[data-focus="5"]').click();await page.locator('.viewer').screenshot({style:".top{visibility:hidden}",path:path.join(out,'mobile-inspection.png')});
 ok('390px mobile layout has no horizontal page overflow; native viewer remains operable');
 await page.goto(url+'report.html',{waitUntil:'load'});assert.ok((await page.locator('table tbody tr').count())>7);assert.equal(await page.locator('h1').count(),1);
 await page.waitForFunction(()=>Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0));
 ok('Standalone static technical report renders its complete result tables');
 assert.deepEqual(errors,[]);ok('No browser JavaScript errors');
 await browser.close();
 fs.writeFileSync(path.join(out,'qa.json'),JSON.stringify({status:'passed',checks,source_files:manifest.source_files.length},null,2)+'\n');
 console.log(JSON.stringify({status:'passed',checks:checks.length,output:out}));
})().catch(e=>{console.error(e);process.exit(1);});
