import { readFileSync, writeFileSync, mkdirSync, copyFileSync } from 'node:fs';
import { resolve, dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { execFileSync } from 'node:child_process';
import * as model from './model.mjs';
import { renderSection } from './geometry.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(HERE, '../../../..');
const SKILL = resolve(ROOT, '.local/anatomy-skill-trial');
const OUT = resolve(ROOT, '.local/anatomy-pose');
const PIN = 'e28bc3f2f91d4a27f3f60edf2207e05596e5f77d';
if (execFileSync('git', ['-C', SKILL, 'rev-parse', 'HEAD'], { encoding: 'utf8' }).trim() !== PIN)
  throw Error('Anatomy revision differs from the inspected skill');
const k = await import(pathToFileURL(join(SKILL, 'kit/iso-kit.mjs')));
const { kitScript } = await import(pathToFileURL(join(SKILL, 'scripts/inline-kit.mjs')));
mkdirSync(OUT, { recursive: true });
const P = k.fitProjection(
  [
    [-130, -88, -20],
    [130, 88, -20],
    [-85, -70, 145],
    [85, 70, 145],
  ],
  800,
  540,
  { pad: 48, azimuth: 48, elevation: 32 },
);
let count = 0;
const slab = (x, y, w, d, z, h, tone = 'mid', r = 1.5) => {
  count++;
  return k.solidSvg(k.slabOf({ x, y, w, d, r }, z, h, P, 5, Math.min(0.6, h / 3)), { tone });
};
const dots = (points, z) =>
  k.dotsSvg(
    points.map(([x, y]) => k.iso([x, y, z], P)),
    { size: 0.6, tone: 'mid' },
  );
let base = `<path class="iso-halo" d="${k.haloOf({ x: -130, y: -88, w: 260, d: 176, r: 9 }, -20, 8, P)}"/>`;
for (const x of [-115, 100])
  for (const y of [-73, 58]) {
    base += slab(x, y, 16, 16, -20, 5, 'lo', 3) + slab(x + 2, y + 2, 12, 12, -15, 4, 'lo', 2);
  }
base += slab(-130, -88, 260, 176, -11, 11, 'lo', 8);
base += k.lineSvg(k.planOutline({ x: -124, y: -82, w: 248, d: 164, r: 5 }, 0.1, P), {
  tone: 'faint',
});
for (const x of [-119, 119])
  for (const y of [-77, 77]) {
    base += slab(x - 1.9, y - 1.9, 3.8, 3.8, 0, 0.6, 'lo', 0.6) + dots([[x, y]], 0.7);
  }
for (const y of [-65, 39]) {
  base += slab(-105, y, 210, 7, 0, 6);
  base += slab(-99, y + 2, 198, 3, 6, 1, 'hi', 0.2);
  for (const x of [-111, 105]) {
    base +=
      slab(x, y - 4, 6, 15, 0, 10) +
      dots(
        [
          [x + 3, y],
          [x + 3, y + 7],
        ],
        10,
      );
  }
}
for (const y of [-79, 66]) {
  base += slab(-100, y, 200, 7, 0, 0.6, 'lo', 0.5);
  for (let x = -96; x <= 96; x += 4) {
    const length = x % 20 === 0 ? 5 : 2.5;
    base += k.lineSvg(k.lineOnTop([x, y], [x, y + length], 0.65, P), {
      tone: x % 20 === 0 ? 'mid' : 'lo',
    });
  }
}
base += slab(-118, 48, 13, 11, 0, 1, 'mid', 1);
base += k.faceTextSvg(k.topMatrix([-111.5, 55], 1.1, P, 'x'), 'LPS', {
  size: 3.4,
  tone: 'mid',
  anchor: 'middle',
});
let carriage = '';
for (const x of [-47, 39]) for (const y of [-65, 39]) carriage += slab(x, y, 8, 7, 7, 4, 'mid');
carriage += slab(-54, -69, 108, 122, 11, 7, 'mid', 3);
for (const x of [-38, 32]) {
  carriage += slab(x, -55, 6, 95, 18, 5, 'mid');
  for (const y of [-61, 40])
    carriage += slab(x - 3, y, 12, 6, 18, 9, 'mid') + dots([[x + 3, y + 3]], 27);
}
for (const x of [-46, 46]) for (const y of [-60, 44]) carriage += dots([[x, y]], 18);
let stage = '';
for (const x of [-38, 32]) for (const y of [-25, 17]) stage += slab(x, y, 6, 8, 23, 4);
stage += slab(-44, -32, 88, 64, 27, 7, 'mid', 3);
stage += slab(-14, -14, 28, 28, 34, 13, 'mid', 2);
stage += k.lineSvg(k.planOutline({ x: -11, y: -11, w: 22, d: 22, r: 1 }, 47, P), { tone: 'faint' });
for (const x of [-36, 36]) for (const y of [-24, 24]) stage += dots([[x, y]], 34);
let controls = '';
for (const [x, y, z] of [
  [104, -11, 0],
  [-7, 74, 0],
  [-94, 3, 0],
]) {
  controls +=
    slab(x - 7, y - 6, 14, 12, z, 6, 'mid') + slab(x - 9, y - 8, 18, 16, z + 6, 5, 'mid', 2);
  for (const dx of [-5, 3]) controls += slab(x + dx, y - 8, 2, 16, z + 11, 0.5, 'lo', 0.3);
}
const staticBody =
  base +
  `<g id="carriage" transform="${k.translateAlong(P, [model.INITIAL[0], 0, 0])}">${carriage}<g id="stage" transform="${k.translateAlong(P, [0, model.INITIAL[1], 0])}">${stage}<g id="lift">${slab(-7, -7, 14, 14, 47, model.INITIAL[2] - 53)}${slab(-10, -10, 20, 20, model.INITIAL[2] - 6, 2)}</g></g></g><g id="section">${renderSection(model.INITIAL, P, k)}</g><g id="reference" hidden></g>` +
  controls;
const svg = k.figureSvg({
  width: 800,
  height: 540,
  label:
    'Conceptual slice-pose positioning bench. The section moves in six degrees of freedom above two sliding carriages. This is a drawn teaching instrument, not a CT scanner.',
  body: staticBody,
});
const specs = [
  ['Left / right', 'x', -20, 20, 'mm'],
  ['Posterior / anterior', 'y', -20, 20, 'mm'],
  ['Superior / inferior', 'z', 70, 106, 'mm'],
  ['Tilt X', 'rx', -25, 25, '°'],
  ['Tilt Y', 'ry', -25, 25, '°'],
  ['Spin Z', 'rz', -30, 45, '°'],
];
const sliders = specs
  .map(
    ([name, id, min, max, unit], i) =>
      `<label class="control" for="${id}"><span>${name}</span><output id="${id}-value">${model.INITIAL[i]}${unit}</output><input id="${id}" data-axis="${i}" type="range" min="${min}" max="${max}" step="1" value="${model.INITIAL[i]}" aria-label="${name}" aria-valuetext="${model.INITIAL[i]} ${unit}"></label>`,
  )
  .join('');
const card = k.plateHtml({
  fig: 'FIG. 01 / INTERACTIVE',
  title: 'The slice-pose bench',
  hint: 'Move the six controls',
  readout: 'Synthetic geometry · 1 mm / pixel',
  keys: [
    { mark: 'lit', label: 'Solid platen: your proposed section' },
    { mark: 'mid', label: 'Reference outline: appears on reveal' },
  ],
  caption:
    'Conceptual illustration · drawn, not a dataset sample. The instrument carries a synthetic 81 × 81 pixel section. Its mechanical supports are illustrative; the pose and point-error calculations are exact for this synthetic example.',
  body: `<div class="iso-stage">${svg}</div>`,
});
const body = `<noscript><p>This is the static preview. Enable JavaScript for the six pose controls and reference reveal.</p></noscript><header><div class="eyebrow">TB3 / REGISTRATION LAB <span>ANATOMY SKILL TRIAL</span></div><h1>Where does this slice belong?</h1><p class="deck">A CT slice is a small picture with a position in a larger world.<br>Recover <strong>where it sits</strong> and <strong>which way its pixels point</strong>.</p><div class="top-actions"><span class="pill">01 &nbsp; Oblique slice → 3D pose</span><button id="theme">Switch theme</button></div></header><div class="workbench"><div>${card}<div class="lesson"><span class="step">TRY THIS</span><h2 id="lesson-title">Place the whole picture, not just its centre.</h2><p id="lesson-copy">Move a control and watch the section follow. Then reveal the teaching reference to see why a plausible-looking plane can still put pixels in the wrong places.</p><div class="presets"><button data-preset="translation">Correct orientation, wrong location</button><button data-preset="spin">Correct plane, wrong pixel direction</button><button data-preset="initial">Reset</button></div></div></div><aside><div class="panel-heading"><h2>Six degrees of freedom</h2><button id="tour" aria-pressed="false">Play tour</button></div><p class="small">Three moves set the centre. Three rotations set the pixel directions. Sliders also work with arrow keys.</p><div class="controls">${sliders}</div><button id="reveal" class="primary" aria-expanded="false">Reveal teaching reference</button><section id="score" hidden><div class="score-heading"><span>POINT ERROR · 49 SAMPLES</span><strong id="verdict"></strong></div><div class="metrics"><div><strong id="rms"></strong><span>RMS · limit 3 mm</span></div><div><strong id="max"></strong><span>Maximum · limit 5 mm</span></div><div><strong id="centre"></strong><span>Centre offset</span></div><div><strong id="normal"></strong><span>Normal angle</span></div></div><button id="match">Move to the reference</button><p class="small">These are the historical task’s engineering bounds, applied here to synthetic points. Both distance limits must pass.</p></section></aside></div><section class="explanation"><article><span class="step">01 / GIVEN</span><h2>A volume. A section. A coordinate system.</h2><p>The real task supplies a CT crop, a section from that same acquisition, pixel spacing, voxel-to-patient geometry, and a forward renderer. The hidden section pose is what you must recover.</p></article><article><span class="step">02 / RETURN</span><h2>One 4 × 4 matrix.</h2><p>The matrix maps each image pixel into patient coordinates in millimetres. Its translation is the <strong>top-left pixel centre</strong>, not the centre of the image. The two are different.</p></article><article><span class="step">03 / CHECK</span><h2>Compare points, not appearances.</h2><p>The evaluator maps a 7 × 7 grid through both transforms. RMS error must be ≤ 3 mm and the worst point ≤ 5 mm. A high image-similarity score alone does not pass.</p></article></section><details><summary>Inspect the live matrix and coordinate convention</summary><div class="matrix-layout"><pre id="matrix"></pre><div><p><code>patient_LPS = T × [u·sx, v·sy, 0, 1]</code></p><p>u = column; v = row; (0,0) = top-left pixel centre.<br>+x = patient left; +y = posterior; +z = superior.</p><p>This demo uses sx = sy = 1 mm. Rotation order: Rz · Ry · Rx. The three basis vectors remain orthonormal and right-handed by construction.</p><button id="download">Download this illustrative pose.json</button></div></div></details><details><summary>What the real task showed, and what this figure does not show</summary><p>The tested full-view and cropped same-acquisition snapshots both passed and were retired as difficulty candidates. Same-source texture is very informative; that success does not establish anatomical understanding or robustness across acquisitions.</p><p>The phantom printed on the platen is only a visual orientation cue. This page does not reslice a CT, run a registration algorithm, recreate a historical prediction, or provide clinical evidence. The synthetic reference is reader-only teaching material.</p><p>The real R01 image was 192 × 192 pixels at 0.9 mm/pixel. This demonstration uses 81 × 81 at 1 mm/pixel so the pose mapping is easy to inspect. The graphic’s camera and instrument dimensions are illustrative.</p></details><details><summary>Sources, skill, and reproducible build</summary><ul><li><a href="task-instruction.txt">Frozen R01 task instruction</a> · <a href="task-scorer.txt">retained scoring code</a></li><li><a href="protocol.txt">BR-019 authored protocol</a> · <a href="outcome.txt">historical results</a></li><li><a href="https://github.com/wheresryan22/anatomy/tree/${PIN}">Anatomy skill and kit</a>, Ryan, MIT · revision ${PIN.slice(0, 12)} · <a href="ANATOMY-LICENSE.txt">license</a></li><li>Build: <code>node groups/registration/presentation/anatomy-pose/build.mjs</code></li></ul><p>Source files remain authoritative. This standalone teaching page is a local trial, separate from the canonical Task Explorer.</p></details><footer><span>TB3 · KNOW THE FRAME, THEN FIND THE MATCH</span><span>SVG / OFFLINE / NO MODEL RUN</span></footer>`;
const css = `.iso-page{margin:32px auto 50px;width:min(1220px,100% - 64px)}header{padding:10px 0 30px}.eyebrow,.step,footer,.score-heading{font:10px/1.5 var(--anatomy-mono);letter-spacing:1.5px}.eyebrow{display:flex;justify-content:space-between;color:var(--anatomy-muted)}h1{font-size:clamp(32px,4vw,54px);font-weight:530;letter-spacing:-2px;line-height:1.1;color:var(--anatomy-strong);margin:28px 0 16px}.deck{font-size:17px;line-height:1.6}.top-actions,.panel-heading{display:flex;justify-content:space-between;align-items:center;gap:12px}.pill{font:11px var(--anatomy-mono);border:1px solid var(--anatomy-faint);border-radius:20px;padding:8px 13px}.workbench{display:grid;grid-template-columns:minmax(0,1fr) 302px;gap:26px;align-items:start}.iso-figure{margin:0}.iso-plate{border-radius:12px}.iso-plate-corner{font-size:9px}.iso-legend{font-size:11px}.iso-caption{line-height:1.65}.iso-stage{padding:10px 0}.iso-svg{overflow:hidden}aside{border:1px solid var(--anatomy-faint);border-radius:12px;padding:20px;background:var(--anatomy-card)}h2{font-size:16px;font-weight:550;color:var(--anatomy-strong);line-height:1.35}.panel-heading h2{margin:0}.small{font-size:11px;line-height:1.65}.controls{margin:22px 0}.control{display:grid;grid-template-columns:1fr auto;gap:8px;margin:16px 0;font-size:11px}.control output{font-family:var(--anatomy-mono);color:var(--anatomy-strong)}input[type=range]{grid-column:1/-1;width:100%;margin:0;height:16px;accent-color:var(--anatomy-strong)}button{font:inherit;font-size:11px;line-height:1.4;border:1px solid var(--anatomy-faint);border-radius:6px;background:transparent;color:var(--anatomy-strong);padding:8px 11px;cursor:pointer}button:hover{background:var(--anatomy-faint)}button:focus-visible,input:focus-visible,summary:focus-visible{outline:2px solid var(--anatomy-strong);outline-offset:4px}.primary{width:100%;background:var(--anatomy-strong);color:var(--anatomy-card);padding:12px}.primary:hover{background:var(--anatomy-mid)}.lesson{margin-top:25px;padding:0 4px}.lesson h2{font-size:21px;margin:8px 0}.lesson p{font-size:13px;max-width:660px}.presets{display:flex;gap:7px;flex-wrap:wrap}.metrics{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin:18px 0}.metrics strong{font:20px var(--anatomy-mono);display:block;color:var(--anatomy-strong)}.metrics span{font-size:10px}.score-heading{display:flex;justify-content:space-between;letter-spacing:.3px;font-size:9px}#score{margin-top:24px;padding-top:20px;border-top:1px solid var(--anatomy-faint)}.explanation{display:grid;grid-template-columns:repeat(3,1fr);gap:30px;margin:42px 0 28px;padding-top:25px;border-top:1px solid var(--anatomy-faint)}.explanation h2{font-size:19px;margin:10px 0}.explanation p{font-size:13px}details{border-top:1px solid var(--anatomy-faint);padding:15px 0;font-size:13px}summary{cursor:pointer;color:var(--anatomy-strong)}details p{max-width:900px}a{color:inherit;text-underline-offset:3px}.matrix-layout{display:grid;grid-template-columns:1fr 1.2fr;gap:25px;padding-top:14px}pre{overflow:auto;font:12px/1.8 var(--anatomy-mono);padding:18px;border:1px solid var(--anatomy-faint);border-radius:8px;color:var(--anatomy-strong)}code{font-size:11px;overflow-wrap:anywhere}footer{display:flex;justify-content:space-between;gap:20px;border-top:1px solid var(--anatomy-faint);padding-top:25px;margin-top:25px;color:var(--anatomy-muted);font-size:9px}[hidden]{display:none!important}@media(max-width:800px){.iso-page{width:calc(100% - 32px);margin-top:20px}.workbench{grid-template-columns:1fr}.explanation{grid-template-columns:1fr;gap:10px}.matrix-layout{grid-template-columns:1fr;gap:4px}.eyebrow{font-size:8px;letter-spacing:.6px}aside{padding:20px}.controls{display:grid;grid-template-columns:1fr 1fr;gap:0 18px}.iso-plate-corner{font-size:7px}.iso-keys{gap:8px}.top-actions{margin-top:20px}.deck{font-size:15px}.iso-legend{font-size:10px}footer{font-size:8px;letter-spacing:.4px}}`;
const modelCode = readFileSync(join(HERE, 'model.mjs'), 'utf8').replace(/^export /gm, '');
const geometryCode = readFileSync(join(HERE, 'geometry.mjs'), 'utf8')
  .replace(/^import .*;$/gm, '')
  .replace(/^export /gm, '');
const live = readFileSync(join(HERE, 'live.js'), 'utf8');
for (const theme of ['light', 'dark']) {
  const html = k
    .pageHtml({
      title: 'Where does this slice belong? · Anatomy × TB3',
      theme,
      width: 1220,
      body,
      script:
        kitScript() +
        `\nconst k={iso,depthOf,slabOf,solidSvg,translateAlong};\nconst PROJ=${JSON.stringify(P)};\n` +
        modelCode +
        '\n' +
        geometryCode +
        '\n' +
        live,
    })
    .replace('</style>', css + '</style>')
    .replace(
      '<head>',
      '<head><!-- Anatomy kit attribution\n' +
        readFileSync(join(SKILL, 'LICENSE'), 'utf8') +
        '\n-->',
    );
  writeFileSync(join(OUT, theme === 'light' ? 'index.html' : 'dark.html'), html);
}
writeFileSync(
  join(OUT, 'instrument-static.svg'),
  k.figureSvg({
    width: 800,
    height: 540,
    label: 'Slice pose bench, static base and positioning carriages',
    body: staticBody,
    standalone: 'light',
  }),
);
for (const [from, to] of [
  ['runs/br019-registration/tasks/cardiac-r01/instruction.md', 'task-instruction.txt'],
  ['runs/br019-registration/tasks/cardiac-r01/tests/score.py', 'task-scorer.txt'],
  ['docs/research-rounds/BR-019-slice-registration.md', 'protocol.txt'],
  ['docs/research-rounds/BR-019-results.md', 'outcome.txt'],
])
  copyFileSync(join(ROOT, from), join(OUT, to));
copyFileSync(join(SKILL, 'LICENSE'), join(OUT, 'ANATOMY-LICENSE.txt'));
console.log(JSON.stringify({ output: OUT, staticSolids: count, anatomyRevision: PIN }));
