/* Source-derived review atlases. A display cursor never modifies saved geometry. */
(() => {
  'use strict';
  const data = JSON.parse(document.getElementById('vessel-data').textContent);
  const $ = id => document.getElementById(id);
  for (const key of ['brain', 'airway']) {
    $(key + '-figure').src = data.figures[key];
    $(key + '-enlarge').href = data.figures[key];
  }
  const b = data.brain, images = {};
  const keys = ['cpr', 'cprBefore', 'cprAfter', 'cprChanges', 'sections'];
  const position = $('route-position'), angle = $('cpr-angle'), overlay = $('cpr-overlay');
  position.max = b.arc.length - 1;
  position.value = b.initial;
  function draw() {
    const i = Number(position.value), a = Number(angle.value), tile = b.tile_height;
    const canvas = $('vessel-cpr'), ctx = canvas.getContext('2d');
    canvas.width = b.arc.length; canvas.height = tile;
    ctx.drawImage(images.cpr, 0, a * tile, canvas.width, tile, 0, 0, canvas.width, tile);
    const key = {before: 'cprBefore', after: 'cprAfter', changes: 'cprChanges'}[overlay.value];
    if (key) ctx.drawImage(images[key], 0, a * tile, canvas.width, tile, 0, 0, canvas.width, tile);
    ctx.fillStyle = '#ffdf79'; ctx.fillRect(i, 0, 1, tile);
    const section = $('vessel-section'); section.width = tile; section.height = tile;
    section.getContext('2d').drawImage(images.sections, 0, i * tile, tile, tile, 0, 0, tile, tile);
    $('cpr-angle-value').textContent = b.angles_deg[a] + '°';
    $('route-distance').textContent = b.arc[i].toFixed(2) + ' / ' + b.arc.at(-1).toFixed(2) + ' mm';
    canvas.setAttribute('aria-label', 'Brain MRA CPR at ' + b.angles_deg[a] + ' degrees, ' + overlay.options[overlay.selectedIndex].text);
    section.setAttribute('aria-label', 'Cross-section at ' + b.arc[i].toFixed(2) + ' millimeters from the basilar anchor');
  }
  Promise.all(keys.map(key => new Promise((resolve, reject) => {
    const img = new Image(); img.onload = () => { images[key] = img; resolve(); };
    img.onerror = reject; img.src = b[key];
  }))).then(() => {
    $('vessel-controls').disabled = false;
    $('vessel-load-status').textContent = 'All views are embedded; no scan download is needed.';
    [position, angle, overlay].forEach(control => control.addEventListener('input', draw));
    $('jump-gap').addEventListener('click', () => { position.value = b.initial; draw(); });
    $('vessel-cpr').addEventListener('click', event => {
      const box = event.currentTarget.getBoundingClientRect();
      position.value = Math.max(0, Math.min(b.arc.length - 1, Math.round((event.clientX - box.left) / box.width * (b.arc.length - 1))));
      draw();
    });
    draw();
  }).catch(() => { $('vessel-load-status').textContent = 'The embedded images could not be decoded. The written results and evidence panels remain available.'; });
})();
