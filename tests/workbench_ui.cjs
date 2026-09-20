/* Browser checks against a fresh portable site. Loopback only; no restored scans needed. */
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const http = require('node:http');
const path = require('node:path');

(async () => {
  const root = path.resolve(process.argv[2] || '.local/presentation-check');
  const server = http.createServer(async (request,response) => {
    const name = decodeURIComponent(new URL(request.url,'http://localhost').pathname);
    const target = path.resolve(root,'.' + (name.endsWith('/') ? name + 'index.html' : name));
    if (!target.startsWith(root + path.sep)) {response.writeHead(404);response.end();return;}
    try {
      const data = await fs.readFile(target);
      const types = {'.html':'text/html','.json':'application/json','.js':'text/javascript','.css':'text/css','.png':'image/png','.svg':'image/svg+xml'};
      response.writeHead(200,{'Content-Type':types[path.extname(target)] || 'text/plain'});
      response.end(data);
    } catch {response.writeHead(404);response.end();}
  });
  await new Promise(resolve => server.listen(0,'127.0.0.1',resolve));
  const base = `http://127.0.0.1:${server.address().port}/`;
  let browser;
  try {
    const channel = process.env.PLAYWRIGHT_CHANNEL || 'chrome';
    browser = await chromium.launch({headless:true,...(channel === 'chromium' ? {} : {channel})});
    const page = await browser.newPage({viewport:{width:1280,height:900}});
    const errors = [], remoteRequests = [];
    page.on('pageerror',error => errors.push(error.message));
    page.on('request',request => {if (/^https?:/.test(request.url()) && !request.url().startsWith(base)) remoteRequests.push(request.url());});
    const data = JSON.parse(await fs.readFile(path.join(root,'records.json'),'utf8'));
    const groups = data.records.filter(row => row.kind === 'group');
    await page.goto(base);
    await page.waitForFunction(count => document.querySelectorAll('.group-card').length === count,groups.length);
    assert.equal(await page.locator('#task-explorer-link').getAttribute('href'),'task-explorer/index.html');

    const target = data.records.find(row => row.kind === 'experiment' && row.current.assessment === 'not_assessed') || data.records.find(row => row.kind === 'experiment');
    const status = 'assessment:' + target.current.assessment;
    await page.locator('#kind').selectOption('experiment');
    await page.locator('#group').selectOption(target.group_id);
    await page.locator('#status').selectOption(status);
    await page.locator('#search').fill(target.id);
    await page.locator(`[id="${target.id}"] > summary`).click();
    const query = new URL(page.url()).searchParams;
    for (const [key,value] of Object.entries({kind:'experiment',group:target.group_id,status,q:target.id,record:target.id})) assert.equal(query.get(key),value,key);
    await page.reload();
    await page.waitForFunction(id => document.getElementById(id)?.open,target.id);
    assert.equal(await page.locator('#status').inputValue(),status);
    assert.equal(await page.locator('#search').inputValue(),target.id);
    await page.screenshot({path:path.join(root,'workbench-desktop.png'),fullPage:true});

    // Filter changes have history entries, and Back restores the selected record.
    await page.locator('#group').selectOption('');
    await page.goBack();
    await page.waitForFunction(({id,group}) => document.getElementById(id)?.open && document.querySelector('#group').value === group,{id:target.id,group:target.group_id});
    await page.locator('#task-explorer-link').click();
    await page.waitForSelector('.task-detail');
    const home = page.locator('a[href="../index.html"]');
    assert.ok(await home.count(),'Integrated Explorer has a usable home link');
    await home.first().click();
    await page.waitForSelector('.group-card');

    // Closing an older open card must preserve the most recently selected one.
    const cards = page.locator('#records > details.record');
    const firstId = await cards.nth(0).getAttribute('id');
    const secondId = await cards.nth(1).getAttribute('id');
    await cards.nth(0).locator(':scope > summary').click();
    await cards.nth(1).locator(':scope > summary').click();
    await page.locator(`[id="${firstId}"] > summary`).click();
    assert.equal(new URL(page.url()).searchParams.get('record'),secondId);
    await page.reload();
    await page.waitForFunction(id => document.getElementById(id)?.open,secondId);

    let chapterLinks = 0;
    for (const group of groups) {
      await page.goto(base + group.story_url);
      assert.equal(await page.locator('a[href*="/story.md"]').count(),0,'Chapter links stay rendered');
      for (const href of await page.locator('a[href]').evaluateAll(links => links.map(link => link.getAttribute('href')))) {
        const url = new URL(href,page.url());
        if (!url.pathname.startsWith('/stories/') || !url.pathname.endsWith('.html')) continue;
        chapterLinks++;
        const response = await page.request.get(url.href);
        assert.equal(response.status(),200);
        if (url.hash) assert.ok((await response.text()).includes(`id="${decodeURIComponent(url.hash.slice(1))}"`),'Chapter fragment exists');
      }
    }
    assert.ok(chapterLinks > 0);
    await page.goto(base);
    await page.waitForSelector('.group-card');
    await page.setViewportSize({width:390,height:844});
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth),false);
    await page.screenshot({path:path.join(root,'workbench-mobile.png'),fullPage:false});
    assert.deepEqual(errors,[]);assert.deepEqual(remoteRequests,[]);
    const report = {groups:groups.length,chapterLinks,filterReloadAndBack:'pass',selectedRecord:'pass',multipleRecordClose:'pass',explorerRoundTrip:'pass',mobile:'pass',pageErrors:errors,remoteRequests};
    await fs.writeFile(path.join(root,'workbench-qa.json'),JSON.stringify(report,null,2)+'\n');
    console.log(JSON.stringify(report));
  } finally {
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
})().catch(error => {console.error(error);process.exitCode=1;});
