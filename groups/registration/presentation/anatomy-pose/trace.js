import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { MarchingCubes } from 'three/addons/objects/MarchingCubes.js';

const DATA = JSON.parse(document.querySelector('#trace-data').textContent);
const $ = (s) => document.querySelector(s);
const phases = [
  {
    short: 'Receive the inputs',
    title: 'The picture is real. Its position is missing.',
    steps: [7, 9, 10, 11],
    state: null,
    copy: 'The solver inspected the supplied forward renderer, CT dimensions and coordinate matrix, then viewed the target and an axial CT slice. It had the entire 180³ crop, not merely a few screenshots. The target’s pose was absent.',
    mechanism: 'Given: CT + target + spacing + forward renderer → return: one pixel-to-LPS matrix.',
  },
  {
    short: 'A wrong first match',
    title: 'A plausible cardiac-looking section can be the wrong cut.',
    steps: [13, 17, 19, 20, 21, 22, 23, 25],
    state: 'early',
    copy: 'The solver searched six pose parameters using differential evolution, then refined an intensity mismatch. The recorded step-17 pose produces this convincing but wrong image. Later intensity and edge-search variants also failed to find the final match.',
    mechanism: 'Selected state: step 17, after Powell refinement. Not the final submitted answer.',
  },
  {
    short: 'Use the whole volume',
    title: 'A finite section has to fit inside the acquired CT.',
    steps: [29, 35, 36, 40, 41],
    state: 'bounded',
    copy: 'The task disclosed that every target sample lies inside the crop. The solver converted that fact into orientation-dependent bounds on the section centre. This pruned impossible poses, but the later step-41 intensity-smoothed result was still wrong.',
    mechanism:
      'For a proposed orientation: corner reach → allowed centre box → search only within that box.',
  },
  {
    short: 'Find a coarse match',
    title: 'First line up the large body–lung pattern.',
    steps: [42, 43],
    state: 'coarse',
    copy: 'The solver changed the global-search objective to a smoothed foreground silhouette: target > 5, Gaussian σ = 2 pixels, compared with a soft threshold of the predicted image. Of eight logged restarts, seed 6 had the lowest reported silhouette objective. Its reconstructed pose is shown here.',
    mechanism:
      'Coarse shape gives a useful starting region. This display is reconstructed from rounded logged parameters.',
  },
  {
    short: 'Refine the texture',
    title: 'Then use every pixel to tighten the pose.',
    steps: [43, 45],
    state: 'final',
    copy: 'Starting from that coarse candidate, full-resolution intensity least squares took eight reported function evaluations. The solver wrote pose.json, rendered it with the supplied forward model, and checked the image and matrix. The saved answer reproduces 36,808 of 36,864 target pixels exactly.',
    mechanism: '56 differing pixels · maximum intensity difference 1 · rigid, right-handed output.',
  },
  {
    short: 'Reveal reference check',
    title: 'The evaluator checks physical positions, not visual similarity.',
    steps: [45],
    state: 'final',
    copy: 'The hidden reference maps the same 7 × 7 image grid into patient space. Both the RMS and maximum point-error limits passed. The amber reference outline nearly coincides with the teal submitted section because the geometric disagreement is far below this display’s resolution.',
    mechanism:
      'Frozen result: 0.000477 mm RMS / 0.000744 mm maximum. These are engineering scores, not clinical precision.',
  },
];
let phase = 0,
  mode = 'image',
  ready = false,
  renderer,
  camera,
  scene,
  orbit,
  candidate,
  candidateOutline,
  referenceOutline,
  shell;
let selectedPose = null;
const contexts = [],
  positions = [45, 45, 45],
  textures = [],
  renderCanvases = [],
  axisNodes = [];
const half = (179 * 1.5) / 2;
const centre = DATA.affine.map((row) => row[3] + 89.5 * (row[0] + row[1] + row[2])).slice(0, 3);
const toScene = (p) => new THREE.Vector3(p[0] - centre[0], p[2] - centre[2], -(p[1] - centre[1]));
const voxel = (i, j, k) =>
  toScene(DATA.affine.slice(0, 3).map((row) => row[0] * i + row[1] * j + row[2] * k + row[3]));
const point = (m, u, v) => toScene(m.slice(0, 3).map((row) => row[0] * u + row[1] * v + row[3]));
const corners = (m) =>
  [
    [0, 0],
    [171.9, 0],
    [171.9, 171.9],
    [0, 171.9],
  ].map(([u, v]) => point(m, u, v));
const escape = (s) =>
  String(s).replace(
    /[&<>"']/g,
    (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c],
  );
let volumeBytes;

function makeGeometry(points, resolution = 192) {
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute(
    'position',
    new THREE.Float32BufferAttribute(
      points.flatMap((p) => p.toArray()),
      3,
    ),
  );
  // The plane corners are pixel centres, so sample the edge texel centres too.
  const low = 0.5 / resolution,
    high = 1 - low;
  geometry.setAttribute(
    'uv',
    new THREE.Float32BufferAttribute([low, high, high, high, high, low, low, low], 2),
  );
  geometry.setIndex([0, 1, 2, 0, 2, 3]);
  geometry.computeVertexNormals();
  return geometry;
}
function replaceGeometry(mesh, points, resolution = 192) {
  mesh.geometry.dispose();
  mesh.geometry = makeGeometry(points, resolution);
}
function line(points, color, dashed = false) {
  const geometry = new THREE.BufferGeometry().setFromPoints([...points, points[0]]);
  const material = dashed
    ? new THREE.LineDashedMaterial({
        color,
        dashSize: 7,
        gapSize: 5,
        depthTest: false,
        transparent: true,
      })
    : new THREE.LineBasicMaterial({ color, depthTest: false, transparent: true });
  const object = new THREE.Line(geometry, material);
  object.computeLineDistances();
  object.renderOrder = 20;
  return object;
}
function render() {
  if (!renderer) return;
  renderer.render(scene, camera);
  const width = $('#volume').clientWidth,
    height = $('#volume').clientHeight;
  for (const { node, position } of axisNodes) {
    const p = position.clone().project(camera);
    node.style.left = (p.x * 0.5 + 0.5) * width + 'px';
    node.style.top = (-p.y * 0.5 + 0.5) * height + 'px';
  }
}
function loadTexture(url) {
  return new Promise((resolve, reject) =>
    new THREE.TextureLoader().load(
      url,
      (t) => {
        t.colorSpace = THREE.SRGBColorSpace;
        t.minFilter = THREE.LinearFilter;
        resolve(t);
      },
      undefined,
      reject,
    ),
  );
}
function updateCandidate() {
  const state = DATA.states.find((s) => s.id === phases[phase].state);
  selectedPose = state?.pose ?? null;
  if (!renderer || !candidate) return;
  candidate.visible = !!state;
  candidateOutline.visible = !!state;
  if (state) {
    selectedPose = state.pose;
    const pts = corners(state.pose);
    replaceGeometry(candidate, pts);
    candidate.material.map = textures[DATA.states.indexOf(state)];
    candidate.material.needsUpdate = true;
    candidateOutline.geometry.dispose();
    candidateOutline.geometry = new THREE.BufferGeometry().setFromPoints([...pts, pts[0]]);
  } else selectedPose = null;
  referenceOutline.visible = phase === 5;
  render();
}
function updateCompare() {
  const info = phases[phase],
    state = DATA.states.find((s) => s.id === info.state);
  $('#target').src = mode === 'silhouette' ? DATA.target_silhouette : DATA.target;
  $('#target-label').textContent =
    mode === 'silhouette' ? 'Target: smoothed foreground' : 'Given: target image';
  $('#candidate').hidden = !state;
  $('#unknown').hidden = !!state;
  $('#compare-tools').hidden = !state;
  if (state) {
    $('#candidate').src =
      mode === 'silhouette'
        ? state.silhouette
        : mode === 'difference'
          ? state.difference
          : state.image;
    $('#candidate-label').textContent =
      mode === 'silhouette'
        ? 'Candidate: soft foreground'
        : mode === 'difference'
          ? 'Absolute difference ×4'
          : info.state === 'final'
            ? 'Rendered submitted pose'
            : `Rendered logged pose · step ${state.trace_step}`;
    $('#render-role').textContent =
      mode === 'silhouette'
        ? state.role +
          ' Mask display is a teaching reconstruction, not an exact rerun of the search objective.'
        : mode === 'difference'
          ? 'Absolute grayscale difference ×4, clipped at 255. This display gain is not the geometric scoring metric.'
          : state.role;
    $('#pixel-readout').textContent =
      phase === 5
        ? 'Reference check: RMS ≤ 3 mm AND maximum ≤ 5 mm over 49 points.'
        : mode === 'silhouette'
          ? 'Shape cue: black air spaces and bright foreground. This is not an organ segmentation.'
          : `Image check: ${state.diagnostic.equal_pixels.toLocaleString()} / 36,864 pixels identical · intensity RMSE ${state.diagnostic.pixel_rmse.toFixed(3)}`;
    $('#pose-matrix').textContent =
      'Selected slice_to_lps (patient millimetres)\n\n' +
      state.pose.map((row) => row.map((v) => v.toFixed(6).padStart(12)).join(' ')).join('\n');
  } else {
    $('#candidate-label').textContent = 'Find its place in the CT';
    $('#render-role').textContent =
      'Input image supplied to the solver. The CT planes at left are reader context views; the unknown target location is not shown at this phase.';
    $('#pixel-readout').textContent =
      'The target is a thin reslice, not an X-ray projection or a slab.';
    $('#pose-matrix').textContent = 'No selected pose at the input stage.';
  }
  document
    .querySelectorAll('[data-mode]')
    .forEach((el) => el.setAttribute('aria-pressed', String(el.dataset.mode === mode)));
  $('#score').hidden = phase !== 5;
  $('#reference-key').hidden = phase !== 5;
}
function setPhase(index) {
  phase = Math.max(0, Math.min(phases.length - 1, index));
  mode = phase === 3 ? 'silhouette' : 'image';
  const info = phases[phase];
  $('#phase-title').textContent = info.title;
  $('#phase-copy').textContent = info.copy;
  $('#mechanism').textContent = info.mechanism;
  $('#trace-label').textContent =
    phase === 5
      ? '06 / EVALUATOR-ONLY REFERENCE REVEAL'
      : `${String(phase + 1).padStart(2, '0')} / TRACE STEPS ${info.steps.join(', ')}`;
  $('#previous').disabled = phase === 0;
  $('#next').disabled = phase === 5;
  $('#next').textContent = phase === 4 ? 'Reveal reference check →' : 'Next phase →';
  document.querySelectorAll('[data-phase]').forEach((el) => {
    if (Number(el.dataset.phase) === phase) el.setAttribute('aria-current', 'step');
    else el.removeAttribute('aria-current');
  });
  $('#trace-excerpts').innerHTML = info.steps
    .map((sid) => {
      const record = DATA.trace.find((t) => t.step === sid);
      if (!record) return '';
      const output = record.output.length > 14000 ? record.output.slice(-14000) : record.output;
      return `<details class="trace-step"><summary>Step ${sid} · ${escape(record.timestamp)} · recorded tool call & output</summary><p class="caption">Tool call</p><pre>${escape(record.calls.join('\n\n'))}</pre><p class="caption">Observed output</p><pre>${escape(output || '(No text output.)')}</pre></details>`;
    })
    .join('');
  updateCompare();
  updateCandidate();
  publishState();
}
function publishState() {
  window.traceViewer = {
    phase,
    mode,
    ready,
    positions: [...positions],
    selectedPose,
    webgl: !!renderer,
    referenceVisible: phase === 5,
    sourceShape: DATA.shape,
  };
}
$('#steps').innerHTML = phases
  .map((p, i) => `<button data-phase="${i}"><span>0${i + 1}</span>${p.short}</button>`)
  .join('');
document
  .querySelectorAll('[data-phase]')
  .forEach((el) => el.addEventListener('click', () => setPhase(Number(el.dataset.phase))));
$('#previous').addEventListener('click', () => setPhase(phase - 1));
$('#next').addEventListener('click', () => setPhase(phase + 1));
document.querySelectorAll('[data-mode]').forEach((el) =>
  el.addEventListener('click', () => {
    mode = el.dataset.mode;
    updateCompare();
    publishState();
  }),
);

function contextPoints(axis, value) {
  const v = (value * 179) / 89;
  if (axis === 0) return [voxel(v, 0, 179), voxel(v, 179, 179), voxel(v, 179, 0), voxel(v, 0, 0)];
  if (axis === 1) return [voxel(0, v, 179), voxel(179, v, 179), voxel(179, v, 0), voxel(0, v, 0)];
  return [voxel(0, 0, v), voxel(179, 0, v), voxel(179, 179, v), voxel(0, 179, v)];
}
function updateMpr(axis) {
  if (!volumeBytes) return;
  const selected = positions[axis],
    n = 90;
  const canvas = renderCanvases[axis],
    ctx = canvas.getContext('2d'),
    pixels = ctx.createImageData(n, n);
  for (let v = 0; v < n; v++)
    for (let u = 0; u < n; u++) {
      const p =
        axis === 0
          ? [selected, u, n - 1 - v]
          : axis === 1
            ? [u, selected, n - 1 - v]
            : [u, v, selected];
      const val = volumeBytes[p[0] * n * n + p[1] * n + p[2]],
        q = (v * n + u) * 4;
      pixels.data[q] = val;
      pixels.data[q + 1] = val;
      pixels.data[q + 2] = val;
      pixels.data[q + 3] = 255;
    }
  ctx.putImageData(pixels, 0, 0);
  const display = $('#mpr-' + axis),
    dctx = display.getContext('2d');
  dctx.imageSmoothingEnabled = true;
  dctx.drawImage(canvas, 0, 0, 180, 180);
  $('#mpr-pos-' + axis).textContent = `voxel ${((selected * 179) / 89).toFixed(1)} / 179`;
  if (contexts[axis]) {
    contexts[axis].material.map.needsUpdate = true;
    replaceGeometry(contexts[axis], contextPoints(axis, selected), 90);
  }
  render();
  publishState();
}
for (let axis = 0; axis < 3; axis++) {
  const canvas = document.createElement('canvas');
  canvas.width = 90;
  canvas.height = 90;
  renderCanvases.push(canvas);
  $('#slice-' + axis).addEventListener('input', (event) => {
    positions[axis] = Number(event.target.value);
    updateMpr(axis);
  });
}
function resetCamera() {
  if (!camera) return;
  camera.position.set(420, 280, 380);
  camera.zoom = 1;
  camera.updateProjectionMatrix();
  orbit.target.set(0, 0, 0);
  orbit.update();
  render();
}
$('#reset-camera').addEventListener('click', resetCamera);
$('#show-context').addEventListener('change', (event) => {
  contexts.forEach((p) => (p.visible = event.target.checked));
  render();
});
$('#show-shell').addEventListener('change', (event) => {
  if (shell) shell.visible = event.target.checked;
  render();
});
$('#volume').addEventListener('keydown', (event) => {
  if (!camera) return;
  if (event.key === 'Home') {
    resetCamera();
    event.preventDefault();
    return;
  }
  if (!['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(event.key)) return;
  const s = new THREE.Spherical().setFromVector3(camera.position.clone().sub(orbit.target));
  if (event.key === 'ArrowLeft') s.theta -= 0.12;
  if (event.key === 'ArrowRight') s.theta += 0.12;
  if (event.key === 'ArrowUp') s.phi = Math.max(0.1, s.phi - 0.12);
  if (event.key === 'ArrowDown') s.phi = Math.min(Math.PI - 0.1, s.phi + 0.12);
  camera.position.setFromSpherical(s).add(orbit.target);
  orbit.update();
  render();
  event.preventDefault();
});

async function boot() {
  setPhase(0);
  const compressed = Uint8Array.from(atob(DATA.preview_base64_gzip), (c) => c.charCodeAt(0));
  volumeBytes = new Uint8Array(
    await new Response(
      new Blob([compressed]).stream().pipeThrough(new DecompressionStream('gzip')),
    ).arrayBuffer(),
  );
  if (volumeBytes.length !== 90 ** 3) throw Error('Unexpected CT preview size');
  for (let i = 0; i < 3; i++) updateMpr(i);
  try {
    if (new URLSearchParams(location.search).has('no3d')) throw Error('2D fallback requested');
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
    renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5));
    renderer.setClearColor(0xfcfcf9);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    $('#volume').append(renderer.domElement);
    scene = new THREE.Scene();
    camera = new THREE.OrthographicCamera(-205, 205, 190, -190, 1, 1600);
    orbit = new OrbitControls(camera, renderer.domElement);
    orbit.enableDamping = false;
    orbit.enablePan = false;
    orbit.minZoom = 0.65;
    orbit.maxZoom = 2.8;
    orbit.addEventListener('change', render);
    scene.add(new THREE.AmbientLight(0xffffff, 2.3));
    const light = new THREE.DirectionalLight(0xffffff, 2);
    light.position.set(250, 450, 350);
    scene.add(light);
    const box = new THREE.BoxGeometry(half * 2, half * 2, half * 2);
    scene.add(
      new THREE.LineSegments(
        new THREE.EdgesGeometry(box),
        new THREE.LineBasicMaterial({ color: 0xa6b3aa, transparent: true, opacity: 0.55 }),
      ),
    );
    for (let axis = 0; axis < 3; axis++) {
      const texture = new THREE.CanvasTexture(renderCanvases[axis]);
      texture.colorSpace = THREE.SRGBColorSpace;
      const mesh = new THREE.Mesh(
        makeGeometry(contextPoints(axis, positions[axis]), 90),
        new THREE.MeshBasicMaterial({
          map: texture,
          side: THREE.DoubleSide,
          transparent: true,
          opacity: 0.65,
          depthWrite: false,
        }),
      );
      mesh.renderOrder = 2;
      scene.add(mesh);
      contexts.push(mesh);
    }
    const material = new THREE.MeshPhongMaterial({
      color: 0xa4b7aa,
      transparent: true,
      opacity: 0.11,
      depthWrite: false,
      side: THREE.DoubleSide,
      shininess: 12,
    });
    shell = new MarchingCubes(90, material, false, false, 180000);
    shell.isolation = (255 * 650) / 1500;
    for (let z = 0; z < 90; z++)
      for (let y = 0; y < 90; y++)
        for (let x = 0; x < 90; x++)
          shell.field[x + 90 * (y + 90 * z)] = volumeBytes[(89 - x) * 90 * 90 + z * 90 + y];
    shell.update();
    shell.scale.setScalar((half * 90) / 89);
    shell.position.setScalar(half / 89);
    shell.renderOrder = 1;
    scene.add(shell);
    for (const state of DATA.states) textures.push(await loadTexture(state.image));
    candidate = new THREE.Mesh(
      makeGeometry(corners(DATA.states[0].pose)),
      new THREE.MeshBasicMaterial({
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 1,
        depthWrite: false,
      }),
    );
    candidate.renderOrder = 10;
    scene.add(candidate);
    candidateOutline = line(corners(DATA.states[0].pose), 0x087e83);
    scene.add(candidateOutline);
    referenceOutline = line(corners(DATA.reference_pose), 0xbc7211, true);
    scene.add(referenceOutline);
    for (const [label, p] of [
      ['L', [158, 0, 0]],
      ['R', [-158, 0, 0]],
      ['S', [0, 158, 0]],
      ['I', [0, -158, 0]],
      ['P', [0, 0, -158]],
      ['A', [0, 0, 158]],
    ]) {
      const node = document.createElement('span');
      node.textContent = label;
      $('#axis-labels').append(node);
      axisNodes.push({ node, position: new THREE.Vector3(...p) });
    }
    const resize = () => {
      const width = $('#volume').clientWidth,
        height = $('#volume').clientHeight;
      renderer.setSize(width, height);
      const aspect = width / height;
      const extent = Math.max(210, 255 / aspect);
      camera.left = -extent * aspect;
      camera.right = extent * aspect;
      camera.top = extent;
      camera.bottom = -extent;
      camera.updateProjectionMatrix();
      render();
    };
    new ResizeObserver(resize).observe($('#volume'));
    resetCamera();
    resize();
    $('#loading').hidden = true;
    updateCandidate();
    window.traceGeometry = {
      nativeCorners: DATA.states.map((s) => ({
        id: s.id,
        points: corners(s.pose).map((p) => p.toArray()),
      })),
      shellVertices: shell.count,
    };
  } catch (error) {
    if (renderer) {
      renderer.dispose();
      renderer.domElement.remove();
      renderer = null;
    }
    $('#loading').textContent =
      '3D unavailable. The CT slice controls and recorded comparisons below remain usable.';
    $('#show-context').disabled = true;
    $('#show-shell').disabled = true;
    $('#reset-camera').disabled = true;
  }
  ready = true;
  publishState();
}
boot().catch((error) => {
  $('#loading').textContent = 'Preview could not load: ' + error.message;
  console.error(error);
});
