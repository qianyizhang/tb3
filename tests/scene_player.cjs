/** Run the production hook with a controlled clock and resource adapters; no browser. */
const assert = require('node:assert/strict');
const path = require('node:path');
const vm = require('node:vm');

async function main() {
  const { build } = await import('vite');
  const root = path.resolve(__dirname, '..');
  const entry = path.join(root, 'tests/virtual-player-test.ts');
  const react = path.join(root, 'tests/virtual-player-react.ts');
  const stage = path.join(root, 'tests/virtual-player-stage.ts');
  const bundles = await build({
    configFile: false,
    root,
    logLevel: 'silent',
    plugins: [
      {
        name: 'player-resource-adapters',
        enforce: 'pre',
        resolveId(id, importer) {
          if ([entry, react, stage].includes(id)) return id;
          if (id === 'react') return react;
          if (id === './stage' && importer?.endsWith('/use-scene-player.ts')) return stage;
        },
        load(id) {
          if (id === entry)
            return `
          export { useScenePlayer } from '${root}/presentation/frontend/task-visuals/use-scene-player.ts';
          export { TaskSceneModels } from '${root}/presentation/frontend/task-visuals/recipes.ts';
          export { effects } from '${react}';
          export { draws } from '${stage}';
        `;
          if (id === react)
            return `
          export const effects = [];
          export const useRef = current => ({ current });
          export const useState = initial => [typeof initial === 'function' ? initial() : initial, () => {}];
          export const useEffect = effect => effects.push(effect);
        `;
          if (id === stage)
            return `
          export const draws = [];
          export const SceneStage = { create: () => ({
            draw(model) { draws.push(model); return true; },
            stats: {}, texturesReady: true, dispose() {}
          }) };
        `;
        },
      },
    ],
    build: {
      write: false,
      minify: false,
      target: 'es2022',
      lib: { entry, name: 'PlayerTest', formats: ['iife'] },
    },
  });
  const frames = new Map();
  let nextFrame = 1;
  let resize;
  const listeners = { addEventListener() {}, removeEventListener() {} };
  const context = vm.createContext({
    console,
    document: { hidden: false, ...listeners },
    matchMedia: () => ({ matches: false, ...listeners }),
    requestAnimationFrame: (callback) => {
      const id = nextFrame++;
      frames.set(id, callback);
      return id;
    },
    cancelAnimationFrame: (id) => frames.delete(id),
    ResizeObserver: class {
      constructor(callback) {
        resize = callback;
      }
      observe() {
        resize();
      }
      disconnect() {}
    },
    IntersectionObserver: class {
      constructor(callback) {
        this.callback = callback;
      }
      observe() {
        this.callback([{ isIntersecting: true }]);
      }
      disconnect() {}
    },
  });
  vm.runInContext(
    bundles[0].output.find((item) => item.type === 'chunk' && item.isEntry).code,
    context,
  );
  const { useScenePlayer, TaskSceneModels, effects, draws } = context.PlayerTest;
  const samples = [];
  TaskSceneModels.build = (entry, stage, seconds, progress) => {
    const sample = { stage, seconds, progress };
    samples.push(sample);
    return sample;
  };
  let now = 100;
  const advance = () => {
    assert.equal(frames.size, 1, 'Only one animation frame is scheduled');
    const [id, callback] = frames.entries().next().value;
    frames.delete(id);
    callback((now += 17));
  };
  for (const kind of ['dynamic_mesh', 'cardiac_contours', 'astro_dynamic']) {
    samples.length = draws.length = 0;
    const player = useScenePlayer({ illustration: { kind } });
    player.root.current = { dataset: {} };
    player.canvas.current = { getBoundingClientRect: () => ({ width: 640, height: 480 }) };
    player.annotations.current = {};
    const dispose = effects.pop()();
    player.actions.current.toggle();
    for (let i = 0; i < 10; i++) advance();
    player.actions.current.toggle();
    assert.equal(frames.size, 0, 'Pause cancels the clock');
    const paused = samples.length;
    resize();
    assert.equal(samples.length, paused, 'Paused resize reuses the current sample');
    player.actions.current.toggle();
    let budget = 700;
    while (frames.size && budget-- > 0) advance();
    assert.ok(budget > 0, 'Playback completes in bounded time');
    assert.deepEqual(
      samples.at(-1),
      { stage: 2, seconds: 10, progress: 1 },
      kind + ': exact final sample',
    );
    assert.strictEqual(draws.at(-1), samples.at(-1), 'The final sample is drawn');
    const complete = samples.length;
    resize();
    assert.equal(samples.length, complete, 'Completed resize keeps the final sample');
    dispose();
    assert.equal(frames.size, 0, 'Disposal leaves no scheduled frame');
  }
  console.log('scene player: pause, resume, exact final sampling and disposal pass');
}
main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
