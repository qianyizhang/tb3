import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const D = JSON.parse(document.getElementById('data').textContent);
const $ = (s) => document.querySelector(s);
const phaseData = [
  {
    short: 'Receive the mask',
    title: 'Almost perfect overlap can still hide a broken route.',
    steps: [7, 9],
    copy: 'The solver received a real MRA crop, a proposed binary vessel mask and a broad editable region. It could repair a supported defect or return the mask unchanged. The location of the authored deletion was not supplied.',
    lesson:
      'Given: MRA + proposed mask + editable region → return: one corrected mask on the same grid.',
  },
  {
    short: 'Find missing signal',
    title: 'Look for bright structure that the mask does not contain.',
    steps: [12, 14, 17, 18, 20, 21, 23, 25, 26],
    copy: 'After inspecting projections and slice montages, the solver measured bright, unmasked components. It reviewed six large candidates and their spatial relation to the mask. The component near (66, 76, 15) became the repair candidate.',
    lesson:
      'Brightness suggests candidates. The three-dimensional attachments determine whether a candidate bridges a local gap.',
  },
  {
    short: 'Grow the candidate',
    title: 'Follow one connected component as its threshold changes.',
    steps: [28],
    copy: 'The solver kept the same seed and tested nine intensity thresholds. At 250, the component contains 89 voxels; at 165 it contains 198. Move the control below to reproduce those recorded alternatives.',
    lesson:
      'candidate = connected component at the seed of (image ≥ threshold) AND NOT mask AND editable region',
  },
  {
    short: 'Check both ends',
    title: 'A bridge needs two local attachments.',
    steps: [29],
    copy: 'At threshold 165, the solver checked which candidate voxels touched the original mask. They form two separated patches: 32 voxels at one end and 33 at the other. The amber cubes mark those exact contact voxels.',
    lesson:
      'These are candidate-to-mask contacts in 3D, using 26-neighbor adjacency—not intersections in a projection.',
  },
  {
    short: 'Save a bounded edit',
    title: 'Add this component. Preserve everything else.',
    steps: [31],
    copy: 'The saved answer is the original mask union the selected 198-voxel component. The solver checked binary values, unchanged voxels outside the editable region, and the output’s shape and affine after reloading the NIfTI.',
    lesson:
      'The teal region is now the actual saved output minus the original mask. No original foreground was removed.',
  },
  {
    short: 'Reveal the check',
    title: 'The local route passes, with no collateral edits.',
    steps: [31],
    copy: 'The private reference reveals a 200-voxel authored gap in the right posterior communicating artery. The saved answer recovers 198, restores the tested local route and preserves the surrounding mask. Two missed boundary voxels appear in magenta.',
    lesson:
      'All frozen checks pass. Exact reference replication was not required; local geometry and preservation were.',
  },
];
let phase = 0,
  thresholdIndex = 8,
  axis = 2,
  positions = [...D.seed],
  focus = false;
let volume, mask, editable, scene, camera, renderer, controls, fullMesh, localMesh, roiBox;
let additions,
  contacts,
  residuals,
  ready = false;
const dims = D.shape;
const flat = (i, j, k) => (i * dims[1] + j) * dims[2] + k;
const unflat = (q) => {
  const k = q % dims[2],
    j = Math.floor(q / dims[2]) % dims[1];
  return [Math.floor(q / (dims[1] * dims[2])), j, k];
};
const centre = D.affine
  .slice(0, 3)
  .map((r) => r[3] + r.slice(0, 3).reduce((s, v, i) => s + (v * (dims[i] - 1)) / 2, 0));
function world(p) {
  const q = D.affine
    .slice(0, 3)
    .map((r, i) => r[3] + r[0] * p[0] + r[1] * p[1] + r[2] * p[2] - centre[i]);
  return new THREE.Vector3(q[0], q[2], -q[1]);
}
const basis = new THREE.Matrix4().set(
  D.affine[0][0],
  D.affine[0][1],
  D.affine[0][2],
  0,
  D.affine[2][0],
  D.affine[2][1],
  D.affine[2][2],
  0,
  -D.affine[1][0],
  -D.affine[1][1],
  -D.affine[1][2],
  0,
  0,
  0,
  0,
  1,
);
const escape = (s) =>
  String(s).replace(
    /[&<>"']/g,
    (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c],
  );
async function decompress(data, Type = Uint8Array) {
  const raw = Uint8Array.from(atob(data), (c) => c.charCodeAt(0));
  const stream = new Blob([raw]).stream().pipeThrough(new DecompressionStream('gzip'));
  return new Type(await new Response(stream).arrayBuffer());
}
function selected() {
  return D.states[thresholdIndex];
}
function activeIndices() {
  return phase === 0 || !$('#add-visible').checked ? [] : phase >= 4 ? D.added : selected().indices;
}
function render() {
  if (renderer) renderer.render(scene, camera);
}
function cameraFit() {
  if (!renderer) return;
  const host = $('#scene'),
    aspect = host.clientWidth / host.clientHeight;
  const extent = focus ? Math.max(7.3, 8.2 / aspect) : Math.max(33, 34 / aspect);
  camera.left = -extent * aspect;
  camera.right = extent * aspect;
  camera.top = extent;
  camera.bottom = -extent;
  camera.updateProjectionMatrix();
  renderer.setSize(host.clientWidth, host.clientHeight);
  render();
}
function setView(local) {
  focus = local;
  $('#overview').setAttribute('aria-pressed', String(!focus));
  $('#focus').setAttribute('aria-pressed', String(focus));
  $('#orientation').textContent = !renderer
    ? 'STATIC MRA PROJECTION'
    : focus
      ? 'LOCAL DETAIL · full NIfTI geometry'
      : 'WHOLE SUPPLIED CROP · patient coordinates';
  $('#scene-title').textContent = !renderer
    ? '01 / SOURCE MRA PROJECTION'
    : focus
      ? '01 / LOCAL REPAIR SITE'
      : '01 / THE WHOLE VESSEL MASK';
  $('#scene-caption').textContent = !renderer
    ? 'Static native-grid maximum intensity projection of the entire supplied MRA crop. The slice panels retain candidate overlays and inspection controls.'
    : focus
      ? 'Reader-selected detail around the logged seed, using exact voxel faces and the full NIfTI affine. Surfaces end at the crop boundary; these cut edges are not anatomical vessel endings. Switch to Whole crop to locate this region.'
      : 'Entire supplied 187 × 132 × 53 MRA crop. Exact voxel faces, with physical spacing and the full NIfTI affine. No smoothing or invented branches. The outlined box locates the reader’s detail view.';
  if (!renderer || !controls) return;
  const target = focus ? world(D.seed) : new THREE.Vector3();
  controls.target.copy(target);
  camera.position.copy(target).add(new THREE.Vector3(0, 90, 36));
  camera.zoom = 1;
  fullMesh.visible = !focus;
  localMesh.visible = focus;
  roiBox.visible = !focus && phase > 0;
  controls.update();
  cameraFit();
  syncState();
}
function voxels(indices, color) {
  const geometry = new THREE.BoxGeometry(1, 1, 1);
  const material = new THREE.MeshStandardMaterial({ color, roughness: 0.75 });
  const mesh = new THREE.InstancedMesh(geometry, material, Math.max(indices.length, 1));
  mesh.count = indices.length;
  indices.forEach((q, i) => {
    const mat = basis.clone();
    mat.setPosition(world(unflat(q)));
    mesh.setMatrixAt(i, mat);
  });
  mesh.instanceMatrix.needsUpdate = true;
  mesh.computeBoundingSphere();
  return mesh;
}
function removeMesh(mesh) {
  if (!mesh) return;
  scene.remove(mesh);
  mesh.geometry.dispose();
  mesh.material.dispose();
}
function updateGeometry() {
  if (!renderer || !scene || !roiBox) return;
  removeMesh(additions);
  removeMesh(contacts);
  removeMesh(residuals);
  const contactIndices = phase === 3 && $('#add-visible').checked ? selected().contacts.flat() : [];
  const cs = new Set(contactIndices);
  additions = voxels(
    activeIndices().filter((x) => !cs.has(x)),
    0x009fa5,
  );
  scene.add(additions);
  contacts = voxels(contactIndices, 0xe7ab42);
  scene.add(contacts);
  residuals = voxels(phase === 5 ? D.residual : [], 0xcf438e);
  scene.add(residuals);
  roiBox.visible = !focus && phase > 0;
  render();
}
function drawSlices() {
  if (!volume) return;
  const detail = $('#detail').checked,
    remaining = [0, 1, 2].filter((x) => x !== axis);
  const horizontal = remaining[0],
    vertical = remaining[1];
  const lo = detail ? D.roi[0] : [0, 0, 0],
    hi = detail ? D.roi[1] : dims;
  const width = hi[horizontal] - lo[horizontal],
    height = hi[vertical] - lo[vertical];
  const actualRatio = (width * D.spacing[horizontal]) / (height * D.spacing[vertical]);
  const candidates = new Set(activeIndices()),
    contactSet = new Set(
      phase === 3 && $('#add-visible').checked ? selected().contacts.flat() : [],
    ),
    rem = new Set(phase === 5 ? D.residual : []);
  const originalVisible = $('#mask-visible').checked;
  for (const id of ['source', 'overlay']) {
    const canvas = $('#' + id);
    canvas.width = 450;
    canvas.height = 450;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#0e171b';
    ctx.fillRect(0, 0, 450, 450);
    const buffer = document.createElement('canvas');
    buffer.width = width;
    buffer.height = height;
    const bctx = buffer.getContext('2d'),
      pixels = bctx.createImageData(width, height);
    for (let y = 0; y < height; y++)
      for (let x = 0; x < width; x++) {
        const p = [...positions];
        p[horizontal] = x + lo[horizontal];
        p[vertical] = hi[vertical] - 1 - y;
        const q = flat(...p),
          g = volume[q],
          o = (y * width + x) * 4;
        let rgb = [g, g, g];
        if (id === 'overlay') {
          const boundary =
            mask[q] &&
            [
              [-1, 0],
              [1, 0],
              [0, -1],
              [0, 1],
            ].some(([a, b]) => {
              const n = [...p];
              n[horizontal] += a;
              n[vertical] += b;
              return n.some((v, k) => v < 0 || v >= dims[k]) || !mask[flat(...n)];
            });
          if (originalVisible && boundary) rgb = [123, 174, 208];
          if (candidates.has(q)) rgb = [0, 200, 193];
          if (contactSet.has(q)) rgb = [240, 176, 65];
          if (rem.has(q)) rgb = [241, 80, 169];
        }
        pixels.data.set([...rgb, 255], o);
      }
    bctx.putImageData(pixels, 0, 0);
    const w = actualRatio > 1 ? 410 : 410 * actualRatio,
      h = actualRatio > 1 ? 410 / actualRatio : 410;
    ctx.imageSmoothingEnabled = false;
    ctx.drawImage(buffer, (450 - w) / 2, (450 - h) / 2, w, h);
    ctx.fillStyle = '#e5eeeb';
    ctx.font = '14px ui-monospace';
    ctx.textAlign = 'center';
    const lr = axis === 0 ? ['A', 'P'] : ['R', 'L'],
      tb = axis === 2 ? ['P', 'A'] : ['S', 'I'];
    ctx.fillText(tb[0], 225, 15);
    ctx.fillText(tb[1], 225, 446);
    ctx.fillText(lr[0], 12, 230);
    ctx.fillText(lr[1], 438, 230);
  }
  $('#slice').max = String(dims[axis] - 1);
  $('#slice').value = String(positions[axis]);
  $('#slice-label').textContent =
    `${['i', 'j', 'k'][axis]} = ${positions[axis]} / ${dims[axis] - 1}`;
  $('#overlay-label').textContent =
    phase === 0
      ? 'Proposed mask outline'
      : phase === 3
        ? 'Candidate + two contact patches'
        : phase === 5
          ? 'Saved edit + reference residual'
          : 'Original outline + additions';
  syncState();
}
function syncState() {
  window.vesselViewer = {
    ready,
    phase,
    threshold: selected().threshold,
    count: activeIndices().length,
    positions: [...positions],
    axis,
    focus,
    webgl: !!renderer,
    referenceVisible: phase === 5,
    contactSizes: phase === 3 ? selected().contacts.map((x) => x.length) : [],
  };
}
function updateReadout() {
  let html = '';
  if (phase === 0)
    html = `<strong>${D.source_voxels.toLocaleString()}</strong> original foreground voxels<br>Edits must stay within the supplied review region.`;
  else if (phase === 1)
    html =
      '<strong>6</strong> candidate groups visually reviewed<br>The selected seed is one of them—not simply the largest.';
  else if (phase === 2)
    html = `<strong>${selected().count}</strong> voxels at threshold ${selected().threshold}<br>Reconstructed from the native source and logged seed.`;
  else if (phase === 3)
    html =
      '<strong>32 + 33</strong> touching candidate voxels<br>Two distinct patches; 26-neighbor connectivity.';
  else if (phase === 4)
    html = '<strong>198 added · 0 removed</strong><br>Saved mask and original affine preserved.';
  else
    html =
      '<strong>198 / 200 recovered</strong><br>0 unrelated additions · 0 deletions · local route PASS';
  $('#readout').innerHTML = html;
  $('#threshold-value').textContent = selected().threshold;
  $('#voxel-count').textContent = selected().count;
  $('#threshold-note').textContent =
    selected().threshold === 165
      ? 'This is the threshold used in the saved answer.'
      : 'Exploratory threshold from the recorded scan; the submitted answer used 165.';
}
function setPhase(next) {
  if (!ready) return;
  phase = Math.max(0, Math.min(5, next));
  const p = phaseData[phase];
  thresholdIndex = phase === 1 || phase === 2 ? 8 : 2;
  $('#threshold').value = String(thresholdIndex);
  $('#title').textContent = p.title;
  $('#copy').textContent = p.copy;
  $('#lesson').textContent = p.lesson;
  $('#locator').textContent =
    phase === 5
      ? '06 / FROZEN EVALUATION'
      : `${String(phase + 1).padStart(2, '0')} / TRACE STEPS ${p.steps.join(', ')}`;
  $('#previous').disabled = phase === 0;
  $('#next').disabled = phase === 5;
  document
    .querySelectorAll('[data-phase]')
    .forEach((b) => b.setAttribute('aria-pressed', String(+b.dataset.phase === phase)));
  $('#threshold-panel').hidden = phase !== 2;
  $('#contacts-panel').hidden = phase !== 3;
  $('#score').hidden = phase !== 5;
  $('#addition-key').hidden = phase === 0;
  $('#contact-key').hidden = phase !== 3;
  $('#reference-key').hidden = phase !== 5;
  $('#add-control').hidden = phase === 0;
  $('#add-visible').checked = true;
  $('#missed').hidden = phase !== 5;
  $('#detail').checked = phase > 0;
  positions = [...D.seed];
  $('#trace').innerHTML = D.trace
    .filter((t) => p.steps.includes(t.step))
    .map(
      (t) =>
        `<details><summary>Step ${t.step} · ${escape(t.time)} · recorded tool call & output</summary><pre>${escape(t.call)}</pre><pre>${escape(t.output)}</pre></details>`,
    )
    .join('');
  const deliveredSteps = phase === 0 ? [10, 11] : phase === 1 ? [13, 15, 19, 22, 24, 27] : [];
  $('#delivered').innerHTML = D.delivered
    .filter((x) => deliveredSteps.includes(x.step))
    .map(
      (x) =>
        `<a href="${x.file}" target="_blank" rel="noopener">Original delivered image · step ${x.step}</a>`,
    )
    .join('');
  updateReadout();
  drawSlices();
  updateGeometry();
  setView(phase > 0);
  syncState();
}
function createNetwork(raw) {
  const all = new Float32Array(raw.length),
    local = [];
  for (let n = 0; n < raw.length; n += 9) {
    let inside = true;
    for (let v = 0; v < 3; v++) {
      const p = Array.from(raw.slice(n + v * 3, n + v * 3 + 3));
      if (p.some((x, i) => x < D.roi[0][i] - 0.5 || x > D.roi[1][i] - 0.5)) inside = false;
      world(p).toArray(all, n + v * 3);
    }
    if (inside) local.push(...all.slice(n, n + 9));
  }
  function mesh(positions) {
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    g.computeVertexNormals();
    return new THREE.Mesh(
      g,
      new THREE.MeshStandardMaterial({ color: 0x708391, roughness: 0.9, side: THREE.DoubleSide }),
    );
  }
  fullMesh = mesh(all);
  localMesh = mesh(local);
  scene.add(fullMesh, localMesh);
}
async function boot() {
  [volume, mask, editable] = await Promise.all([
    decompress(D.volume),
    decompress(D.mask),
    decompress(D.editable),
  ]);
  try {
    if (new URLSearchParams(location.search).has('no3d')) throw new Error('Requested static view');
    const host = $('#scene');
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
    renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5));
    renderer.setClearColor(0xeaf0eb);
    host.appendChild(renderer.domElement);
    scene = new THREE.Scene();
    camera = new THREE.OrthographicCamera(-35, 35, 35, -35, 0.1, 1000);
    scene.add(new THREE.HemisphereLight(0xffffff, 0x64706a, 2.3));
    const light = new THREE.DirectionalLight(0xffffff, 2.5);
    light.position.set(-40, 70, 50);
    scene.add(light);
    createNetwork(await decompress(D.surface, Float32Array));
    const lo = D.roi[0].map((v) => v - 0.5),
      hi = D.roi[1].map((v) => v - 0.5),
      corners = [];
    for (let i = 0; i < 8; i++)
      corners.push(world([i & 1 ? hi[0] : lo[0], i & 2 ? hi[1] : lo[1], i & 4 ? hi[2] : lo[2]]));
    const lines = [];
    for (let i = 0; i < 8; i++)
      for (const bit of [1, 2, 4]) if (!(i & bit)) lines.push(corners[i], corners[i | bit]);
    roiBox = new THREE.LineSegments(
      new THREE.BufferGeometry().setFromPoints(lines),
      new THREE.LineBasicMaterial({ color: 0x008d92 }),
    );
    scene.add(roiBox);
    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = false;
    controls.minZoom = 0.45;
    controls.maxZoom = 5;
    controls.addEventListener('change', render);
    new ResizeObserver(cameraFit).observe(host);
    host.addEventListener('keydown', (e) => {
      if (e.key === 'Home') {
        setView(focus);
        e.preventDefault();
      } else if (['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(e.key)) {
        const v = camera.position.clone().sub(controls.target);
        v.applyAxisAngle(
          e.key === 'ArrowLeft' || e.key === 'ArrowRight'
            ? new THREE.Vector3(0, 1, 0)
            : new THREE.Vector3(1, 0, 0),
          e.key === 'ArrowLeft' || e.key === 'ArrowUp' ? -0.12 : 0.12,
        );
        camera.position.copy(controls.target).add(v);
        controls.update();
        e.preventDefault();
      }
    });
    $('#loading').hidden = true;
  } catch (error) {
    if (renderer) {
      renderer.dispose();
      renderer.domElement.remove();
      renderer = null;
    }
    $('#scene').nextElementSibling.hidden = true;
    $('.card .legend').hidden = true;
    $('#loading').innerHTML =
      `<div><img src="${D.mip}" alt="Native MRA maximum intensity projection; static 3D fallback" style="max-width:90%;max-height:290px;image-rendering:pixelated"><p>3D unavailable. Native MRA projection shown.<br>Slice inspection and trace controls remain available.</p></div>`;
  }
  ready = true;
  setPhase(0);
  window.vesselGeometry = {
    seedScene: world(D.seed).toArray(),
    affine: D.affine,
    sourceShape: dims,
    surfaceVertices: D.surface_vertices,
  };
}
$('#phases').innerHTML = phaseData
  .map(
    (p, i) =>
      `<button data-phase="${i}" aria-pressed="${i === 0}"><small>0${i + 1}</small>${p.short}</button>`,
  )
  .join('');
document
  .querySelectorAll('[data-phase]')
  .forEach((b) => b.addEventListener('click', () => setPhase(+b.dataset.phase)));
$('#previous').onclick = () => setPhase(phase - 1);
$('#next').onclick = () => setPhase(phase + 1);
$('#overview').onclick = () => setView(false);
$('#focus').onclick = () => setView(true);
$('#reset').onclick = () => setView(focus);
$('#axis').onchange = (e) => {
  axis = +e.target.value;
  drawSlices();
};
$('#slice').oninput = (e) => {
  positions[axis] = +e.target.value;
  drawSlices();
};
$('#detail').onchange = drawSlices;
$('#mask-visible').onchange = drawSlices;
$('#add-visible').onchange = () => {
  drawSlices();
  updateGeometry();
};
let missedIndex = 0;
$('#missed').onclick = () => {
  positions = unflat(D.residual[missedIndex++ % D.residual.length]);
  drawSlices();
};
$('#site').onclick = () => {
  positions = [...D.seed];
  drawSlices();
};
function changeThreshold(i) {
  thresholdIndex = i;
  $('#threshold').value = String(i);
  updateReadout();
  drawSlices();
  updateGeometry();
  syncState();
}
$('#threshold').oninput = (e) => changeThreshold(+e.target.value);
$('#chosen').onclick = () => changeThreshold(2);
boot().catch((e) => {
  $('#loading').textContent = 'Unable to load local volume: ' + e.message;
});
