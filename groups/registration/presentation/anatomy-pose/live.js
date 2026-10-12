const $ = (s) => document.querySelector(s);
const sliders = [...document.querySelectorAll('[data-axis]')];
const calm = matchMedia('(prefers-reduced-motion: reduce)');
let pose = [...INITIAL],
  target = [...INITIAL],
  revealed = false,
  touring = false,
  visible = true,
  frame = 0,
  last = 0,
  elapsed = 0,
  tourIndex = -1;
const presets = {
  initial: INITIAL,
  translation: [12, -8, 98, ...REFERENCE.slice(3)],
  spin: inPlaneTurn(25),
  match: REFERENCE,
};
const screen = (p) => k.iso(p, PROJ);
const polygon = (points) =>
  'M' +
  points
    .map((p) =>
      screen(p)
        .map((x) => x.toFixed(2))
        .join(','),
    )
    .join('L') +
  'Z';
function draw() {
  $('#carriage').setAttribute('transform', k.translateAlong(PROJ, [pose[0], 0, 0]));
  $('#stage').setAttribute('transform', k.translateAlong(PROJ, [0, pose[1], 0]));
  $('#lift').innerHTML =
    k.solidSvg(k.slabOf({ x: -7, y: -7, w: 14, d: 14, r: 1 }, 47, pose[2] - 53, PROJ, 4, 0.5), {
      tone: 'mid',
    }) +
    k.solidSvg(k.slabOf({ x: -10, y: -10, w: 20, d: 20, r: 1 }, pose[2] - 6, 2, PROJ, 4, 0.4), {
      tone: 'mid',
    });
  $('#section').innerHTML = renderSection(pose, PROJ, k);
  const m = metrics(pose);
  $('[data-readout]').textContent = revealed
    ? `${m.rms.toFixed(2)} mm RMS · ${m.max.toFixed(2)} mm max`
    : 'Synthetic section · reference hidden';
  for (const [key, unit] of [
    ['rms', 'mm'],
    ['max', 'mm'],
    ['centre', 'mm'],
    ['normal', '°'],
  ])
    $('#' + key).textContent = m[key].toFixed(2) + (unit === '°' ? '°' : ' mm');
  $('#verdict').textContent = m.pass ? 'WITHIN BOUNDS' : 'OUTSIDE BOUNDS';
  $('#matrix').textContent =
    'Illustrative slice_to_lps\n\n' +
    transform(pose)
      .map((row) =>
        row.map((v) => (Math.abs(v) < 0.00005 ? 0 : v).toFixed(4).padStart(9)).join(' '),
      )
      .join('\n');
  sliders.forEach((el, i) => {
    const unit = i < 3 ? 'mm' : '°';
    $('#' + el.id + '-value').textContent = pose[i].toFixed(1) + (unit === '°' ? '°' : ' mm');
    el.value = String(target[i]);
    el.setAttribute('aria-valuetext', target[i].toFixed(1) + ' ' + unit);
  });
  window.poseDemo = {
    pose: [...pose],
    target: [...target],
    metrics: m,
    matrix: transform(pose),
    revealed,
    touring,
  };
}
const lessons = {
  initial: [
    'Place the whole picture, not just its centre.',
    'Move a control and watch the section follow. Then reveal the teaching reference to see how the 49 grid points compare.',
  ],
  translation: [
    'Right orientation. Wrong location.',
    'All 49 pixels shift together. Here the slice axes match the reference, but a translation still gives every sample the same physical error.',
  ],
  spin: [
    'Right plane. Wrong pixel direction.',
    'The centre and normal are exactly right, but the image is spun 25° inside its own plane. The edge pixels land in the wrong places. A plane is not yet an image pose.',
  ],
  match: [
    'Every sampled pixel has its place.',
    'At the teaching reference, both errors are zero. In the real task, you must infer this pose from the images; the evaluator’s reference is hidden.',
  ],
};
function explain(name) {
  $('#lesson-title').textContent = lessons[name][0];
  $('#lesson-copy').textContent = lessons[name][1];
}
function setPreset(name) {
  target = [...presets[name]];
  explain(name);
  if (calm.matches) {
    pose = [...target];
    draw();
  } else run();
}
function stopTour() {
  touring = false;
  $('#tour').textContent = 'Play tour';
  $('#tour').setAttribute('aria-pressed', 'false');
}
function tick(now) {
  frame = 0;
  if (!visible || document.hidden) return;
  const dt = last ? Math.min((now - last) / 1000, 1 / 30) : 1 / 60;
  last = now;
  if (touring && !calm.matches) {
    elapsed += dt;
    const index = Math.floor(elapsed / 5) % 3;
    if (index !== tourIndex) {
      tourIndex = index;
      const name = ['translation', 'spin', 'initial'][index];
      target = [...presets[name]];
      explain(name);
    }
  }
  pose = pose.map((v, i) =>
    Math.abs(target[i] - v) < 0.002 ? target[i] : v + (target[i] - v) * (1 - Math.exp(-dt / 0.22)),
  );
  draw();
  if (touring || pose.some((v, i) => v !== target[i])) frame = requestAnimationFrame(tick);
}
function run() {
  if (!frame && visible && !document.hidden) {
    last = 0;
    frame = requestAnimationFrame(tick);
  }
}
sliders.forEach((el, i) =>
  el.addEventListener('input', () => {
    stopTour();
    target[i] = Number(el.value);
    if (calm.matches) {
      pose = [...target];
      draw();
    } else run();
  }),
);
document.querySelectorAll('[data-preset]').forEach((el) =>
  el.addEventListener('click', () => {
    stopTour();
    setPreset(el.dataset.preset);
  }),
);
$('#reveal').addEventListener('click', () => {
  revealed = !revealed;
  $('#reference').toggleAttribute('hidden', !revealed);
  $('#score').hidden = !revealed;
  $('#reveal').textContent = revealed ? 'Hide teaching reference' : 'Reveal teaching reference';
  $('#reveal').setAttribute('aria-expanded', String(revealed));
  draw();
});
$('#match').addEventListener('click', () => {
  stopTour();
  setPreset('match');
});
$('#tour').addEventListener('click', () => {
  if (touring) stopTour();
  else if (calm.matches) {
    setPreset('translation');
    $('#lesson-copy').textContent +=
      ' Reduced motion is enabled, so the tour shows one still pose.';
  } else {
    touring = true;
    elapsed = 0;
    tourIndex = -1;
    $('#tour').textContent = 'Pause tour';
    $('#tour').setAttribute('aria-pressed', 'true');
    run();
  }
});
$('#theme').addEventListener(
  'click',
  () => (document.body.dataset.theme = document.body.dataset.theme === 'light' ? 'dark' : 'light'),
);
$('#download').addEventListener('click', () => {
  const url = URL.createObjectURL(
    new Blob([JSON.stringify({ slice_to_lps: transform(pose) }, null, 2)], {
      type: 'application/json',
    }),
  );
  const a = document.createElement('a');
  a.href = url;
  a.download = 'illustrative-pose.json';
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
});
new IntersectionObserver((entries) => {
  visible = entries.at(-1).isIntersecting;
  if (visible) run();
}).observe($('.workbench'));
document.addEventListener('visibilitychange', () => {
  if (!document.hidden) run();
});
calm.addEventListener('change', () => {
  if (calm.matches) {
    stopTour();
    pose = [...target];
    draw();
  }
});
const referenceCorners = [
  [-40, -40, 0],
  [40, -40, 0],
  [40, 40, 0],
  [-40, 40, 0],
].map((p) => point(REFERENCE, p));
$('#reference').innerHTML =
  `<path d="${polygon(referenceCorners)}" fill="none" stroke="var(--anatomy-mid)" stroke-width="1.3" stroke-dasharray="5 4"/>` +
  GRID.map(([u, v]) => {
    const p = screen(point(REFERENCE, [u - 40, v - 40, 0]));
    return `<rect x="${p[0] - 1.7}" y="${p[1] - 1.7}" width="3.4" height="3.4" fill="var(--anatomy-card)" stroke="var(--anatomy-hi)" stroke-width=".6"/>`;
  }).join('');
draw();

let untouched = true;
for (const event of ['pointerdown', 'keydown'])
  document.addEventListener(
    event,
    () => {
      untouched = false;
    },
    { once: true },
  );
setTimeout(() => {
  if (untouched && !calm.matches) {
    touring = true;
    $('#tour').textContent = 'Pause tour';
    $('#tour').setAttribute('aria-pressed', 'true');
    run();
  }
}, 6000);
$('.workbench').addEventListener('pointerenter', () => {
  if (touring) stopTour();
});
