/* Optional browser regression check for a built offline Task Explorer.
 * PLAYWRIGHT_MODULE may point to an existing Playwright installation.
 * Usage: node tests/task_explorer_ui.cjs runs/task-explorer/index.html [report.json]
 * Does not install dependencies, fetch resources, or run external benchmarks.
 */
const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const {resolve,dirname}=require('path');
const {pathToFileURL}=require('url');
const fs=require('fs');
const assert=require('assert/strict');
(async()=>{
  const file=resolve(process.argv[2] || 'runs/task-explorer/index.html');
  const browser=await chromium.launch({channel:'chrome',headless:true});
  const errors=[],requests=[];
  try {
    const page=await browser.newPage({viewport:{width:1010,height:1324}});
    page.on('pageerror',e=>errors.push(e.message));
    page.on('request',r=>{if(/^https?:/.test(r.url()))requests.push(r.url())});
    await page.goto(pathToFileURL(file).href);
    const data=await page.evaluate(()=>JSON.parse(document.querySelector('#data').textContent));
    const go=async(hash,id,section='overview')=>{
      await page.evaluate(hash=>{location.hash=hash},hash);
      await page.waitForFunction(({id,section})=>document.querySelector('.task-detail')?.dataset.brief===id && document.querySelector(`[data-tab="${section}"][aria-selected="true"]`),{id,section});
    };
    // Every imported source record survives its old URL and keeps its source identity.
    let records=0,conditions=0,images=0;
    for(const repo of data.inventory.repositories) for(const item of repo.items){
      await go(`${repo.id}/task/${encodeURIComponent(item.id)}/${item.condition_index||0}/sources`,item.brief_id,'sources');
      await page.waitForFunction(id=>document.querySelector('.provenance code')?.textContent===id,item.id);
      assert.equal(await page.locator('.selected-source > a').getAttribute('href'),item.url);
      assert.equal(await page.locator('.provenance').getAttribute('open'),null,'Technical IDs must be collapsed');
      records++;
    }
    for(const e of data.entries){
      for(let n=0;n<e.variants.length;n++){
        await go(`${e.id}/${n}/brief`,e.id);
        if(e.variants.length>1){
          await page.waitForFunction(n=>document.querySelector('[data-condition][aria-pressed=true]')?.dataset.condition===String(n),n);
        }
        conditions++;
      }
      if(Object.values(e.visuals).some(x=>/<img\b/.test(x))){
        await page.locator('[data-tab="examples"]').click();
        assert.equal(await page.locator('[data-visible-role]').getAttribute('data-visible-role'),'input');
        for(const role of ['input','helpers','answer']){
          await page.locator(`[data-visual="${role}"]`).click();
          for(const image of await page.locator('.visual-content img').all()){
            await image.evaluate(e=>e.decode());assert.ok(await image.evaluate(e=>e.naturalWidth>0));images++;
          }
        }
      } else {
        assert.equal(await page.locator('[data-tab="examples"]').count(),0,'No repeated text pretending to be an image');
      }
    }
    const clinical='healthagentbench-trial-matching',case29='clinical_trial_matching_task_29';
    await go(`healthagentbench/task/${case29}/0/catalogue`,clinical);
    await page.waitForFunction(id=>document.querySelector(`[data-entry="${id}"][aria-pressed=true]`),case29);
    assert.equal(await page.locator('[data-definition]').count(),15,'Cases should not be repeated task rows');
    assert.equal(await page.locator('[data-entry]').count(),9);
    assert.equal(await page.locator('[data-definition="healthagentbench-trial-matching"]').count(),1);
    assert.equal(await page.locator('#task-picker').count(),0);
    assert.equal(await page.locator('.catalogue-glance').count(),0);
    assert.ok(!await page.locator('body').innerText().then(x=>x.includes('Task at a glance')));
    assert.ok((await page.locator('.case-facts').innerText()).includes('407 candidate trials'));
    assert.equal(await page.locator('.provenance').count(),0,'Technical IDs do not occupy the overview');
    const heading=await page.locator('.detail-heading h2').innerText();
    await page.locator('[data-entry="clinical_trial_matching_task_27"]').click();
    assert.equal(await page.locator('.detail-heading h2').innerText(),heading);
    assert.ok((await page.locator('.case-facts').innerText()).includes('451 candidate trials'));
    await page.goBack();
    await page.waitForFunction(()=>document.querySelector('.case-facts')?.textContent.includes('407 candidate trials'));
    await page.reload();
    await page.waitForFunction(()=>document.querySelector('.case-facts')?.textContent.includes('407 candidate trials'));
    await page.locator('[data-tab="requirements"]').click();
    assert.ok((await page.locator('#task-panel').innerText()).includes('recall@50'));
    await page.locator('[data-tab="overview"]').click();
    if(process.env.TASK_EXPLORER_SCREENSHOTS){
      fs.mkdirSync(process.env.TASK_EXPLORER_SCREENSHOTS,{recursive:true});
      await page.screenshot({path:resolve(process.env.TASK_EXPLORER_SCREENSHOTS,'catalogue-desktop.png'),fullPage:true});
    }
    // Search looks at task/case meaning, never arbitrary hash fragments in source URLs.
    await page.locator('#search').fill('bcbb8085');assert.equal(await page.locator('[data-group]').count(),0);
    await page.locator('#search').fill(case29);
    assert.equal(await page.locator('[data-definition]').count(),1);
    await page.locator('[data-definition]').click();
    assert.equal(await page.locator('[data-entry]').count(),9,'The complete case set stays reachable');
    await page.locator('#search').fill('');
    await go('abra/catalogue/oracle_annotation','abra');
    assert.equal(await page.locator('[data-condition="1"]').getAttribute('aria-pressed'),'true');
    await page.locator('[data-tab="examples"]').click();await page.locator('[data-visual="answer"]').click();
    await page.locator('[data-tab="overview"]').click();await page.locator('[data-condition="0"]').click();
    await page.locator('[data-tab="examples"]').click();
    assert.equal(await page.locator('[data-visible-role]').getAttribute('data-visible-role'),'input');
    await go('automedbench/task/lite-case-TSG_00000040/0/examples','automedbench-tsg','examples');
    assert.ok((await page.locator('.scope-note').innerText()).includes('TSG_00000001'));
    // The same legacy case link remains readable at the comment's viewport and on mobile.
    for(const width of [1010,390]){
      await page.setViewportSize({width,height:width===390?844:1324});
      for(const [hash,id,section] of [
        [`healthagentbench/task/${case29}/0/catalogue`,clinical,'overview'],
        ['automedbench-full-tsg-multiorgan-seg-task/1/brief','automedbench-full-tsg-multiorgan-seg-task','overview'],
        ['bcer/0/examples','bcer','examples'],
        ['rexmle/0/sources','rexmle','sources']]){
        await go(hash,id,section);
        assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,hash+' overflows');
      }
      if(width===390 && process.env.TASK_EXPLORER_SCREENSHOTS){
        await go(`healthagentbench/task/${case29}/0/catalogue`,clinical);
        await page.screenshot({path:resolve(process.env.TASK_EXPLORER_SCREENSHOTS,'catalogue-mobile.png'),fullPage:true});
      }
    }
    assert.deepEqual(errors,[]);assert.deepEqual(requests,[]);
    const result={briefs:data.entries.length,sourceRecords:records,conditions,nativeImagesDecoded:images,groupedTaskList:'pass',caseDifferences:'pass',legacyLinksAndBack:'pass',collapsedProvenance:'pass',search:'pass',referenceReveal:'pass',mobile:'pass',pageErrors:errors,remoteRequests:requests};
    if(process.argv[3]){const p=resolve(process.argv[3]);fs.mkdirSync(dirname(p),{recursive:true});fs.writeFileSync(p,JSON.stringify(result,null,2)+'\n')}
    console.log(JSON.stringify(result));
  } finally {await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
