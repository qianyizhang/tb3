/* Execute the production player with deferred source loads; no scans or browser required. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const deferred = () => {
  let resolve, reject;
  const promise = new Promise((yes, no) => { resolve = yes; reject = no; });
  return {promise, resolve, reject};
};
async function fixture() {
  const pending = new Map(), localeLoads = new Map(), elements = new Map();
  const element = id => {
    if (!elements.has(id)) elements.set(id, {
      value: '', textContent: '', disabled: true, style: {}, children: [], dataset: {},
      classList: {toggle() {}}, setAttribute() {}, getContext: () => ({}),
      replaceChildren(...children) { this.children = children; },
    });
    return elements.get(id);
  };
  const boards = Object.fromEntries(['segmentation','vessels','cardiac','landmarks'].map(id => [id, {
    title: id, duration: 10, steps: [{at:0,title:id,caption:id}],
  }]));
  const fetch = async url => {
    if (url === 'storyboards.json') return {json:async () => boards};
    if (url === 'web/manifest.json') return {ok:false};
    if (url.startsWith('locales/')) {
      if (localeLoads.has(url)) return localeLoads.get(url).promise;
      return {ok:true, json:async () => ({labels:{}, stories:{}})};
    }
    const request = deferred(); pending.set(url, request);
    return request.promise;
  };
  const context = {
    fetch, structuredClone, Map, WeakMap, URLSearchParams, console,
    document: {getElementById:element, documentElement:{lang:'en'}, querySelectorAll:() => [], createElement:() => element(Symbol()), fonts:{ready:Promise.resolve()}},
    window: {}, location:{search:''}, requestAnimationFrame() {},
    Image: class {async decode() {}},
  };
  const source = fs.readFileSync(path.join(__dirname,'../presentation/tours/tour.js'),'utf8');
  const app = await vm.runInNewContext(`(async () => { ${source}\nui = () => {}; return window.tourApp; })()`, context);
  const complete = (id, value) => pending.get(`data/${id}.json`).resolve({json:async () => value});
  complete('segmentation',{frames:[]}); await app.ready;
  return {app,pending,localeLoads,complete,context,elements};
}
(async () => {
  const f = await fixture();
  const older = f.app.select('vessels'), newer = f.app.select('cardiac');
  f.complete('cardiac',{masks:[]}); await newer;
  f.complete('vessels',{cpr:[],cuts:[]}); await older;
  assert.equal(f.app.getState().id,'cardiac','Slower old success must not replace latest selection');

  const oldFailure = f.app.select('landmarks');
  await f.app.select('cardiac');
  f.pending.get('data/landmarks.json').reject(Error('stale load'));
  await oldFailure;
  assert.equal(f.app.getState().id,'cardiac','Stale failure is ignored');
  assert.match(f.elements.get('status').textContent,/Ready/);
  const currentFailure = f.app.select('landmarks');
  f.pending.get('data/landmarks.json').reject(Error('current load'));
  await assert.rejects(currentFailure,/current load/);

  const zh = deferred(), en = deferred();
  f.localeLoads.set('locales/zh-CN.json',zh);f.localeLoads.set('locales/en.json',en);
  const oldLocale = f.app.configure({locale:'zh-CN'});
  const newLocale = f.app.configure({locale:'en'});
  // A tour selected while a language request is pending remains the requested tour.
  await f.app.select('vessels');
  en.resolve({ok:true,json:async () => ({labels:{},stories:{}})});await newLocale;
  zh.resolve({ok:true,json:async () => ({labels:{},stories:{}})});await oldLocale;
  assert.equal(f.app.getState().locale,'en');
  assert.equal(f.app.getState().id,'vessels');
  assert.equal(f.context.document.documentElement.lang,'en');
  assert.equal(f.elements.get('language').value,'en');
  console.log('Tour state: latest success, stale/current errors, locale ordering and current tour passed.');
})().catch(error => {console.error(error);process.exitCode=1;});
