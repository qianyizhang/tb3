import { useEffect, useLayoutEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { MarchingCubes } from 'three/addons/objects/MarchingCubes.js';
import type { CtTracePayload } from '../../contracts.generated';
import type { NativeStageProps } from './types';
import styles from './ct-trace.module.css';

type Mode = 'image' | 'silhouette' | 'difference';
type Plane = THREE.Mesh<THREE.BufferGeometry, THREE.MeshBasicMaterial>;
interface Drawing {
  update: () => void;
  reset: () => void;
  key: (key: string) => boolean;
  dispose: () => void;
  committed: () => boolean;
}
const axes = ['Sagittal · native i', 'Coronal · native j', 'Axial · native k'];

function planeGeometry(points: THREE.Vector3[], resolution: number) {
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute(
    'position',
    new THREE.Float32BufferAttribute(
      points.flatMap((p) => p.toArray()),
      3,
    ),
  );
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
function outline(points: THREE.Vector3[], dashed = false) {
  const line = new THREE.Line(
    new THREE.BufferGeometry().setFromPoints([...points, points[0]]),
    dashed
      ? new THREE.LineDashedMaterial({
          color: 0xbc7211,
          dashSize: 7,
          gapSize: 5,
          depthTest: false,
          depthWrite: false,
          transparent: true,
          opacity: 1,
        })
      : new THREE.LineBasicMaterial({
          color: 0x087e83,
          depthTest: false,
          depthWrite: false,
          transparent: true,
          opacity: 1,
        }),
  );
  line.computeLineDistances();
  line.renderOrder = 20;
  return line;
}

export function CtTraceStage({
  payload,
  stateId,
  chapterId,
  referenceShown,
  onReady,
}: NativeStageProps<CtTracePayload>) {
  const [mode, setMode] = useState<Mode>(stateId === 'coarse' ? 'silhouette' : 'image');
  const [positions, setPositions] = useState(() =>
    [0, 1, 2].map(() => Math.floor(payload.input.preview_size / 2)),
  );
  const [showContext, setShowContext] = useState(true);
  const [showShell, setShowShell] = useState(true);
  const [webgl, setWebgl] = useState(false);
  const [ready, setReady] = useState(false);
  const [message, setMessage] = useState('Loading retained CT preview…');
  const [generation, setGeneration] = useState(0);
  const host = useRef<HTMLDivElement>(null);
  const canvases = useRef<Array<HTMLCanvasElement | null>>([]);
  const bytes = useRef<Uint8Array | null>(null);
  const initialized = useRef(false);
  const drawing = useRef<Drawing | null>(null);
  const callback = useRef(onReady);
  callback.current = onReady;
  const state = payload.observed.states.find((item) => item.id === stateId);
  const current = useRef({ state, referenceShown, positions, showContext, showShell });
  current.current = { state, referenceShown, positions, showContext, showShell };
  const input = payload.input;
  const target = mode === 'silhouette' ? input.target_silhouette : input.target;
  const comparison = state
    ? mode === 'silhouette'
      ? state.silhouette
      : mode === 'difference'
        ? state.difference
        : state.image
    : null;

  useEffect(() => {
    let cancelled = false;
    initialized.current = false;
    callback.current(false);
    setReady(false);
    const n = input.preview_size;
    const maximum = input.shape.map((size) => size - 1);
    const centre = input.affine
      .slice(0, 3)
      .map(
        (row) =>
          row[3] +
          row.slice(0, 3).reduce((sum, value, axis) => sum + (value * maximum[axis]) / 2, 0),
      );
    const scenePoint = (p: number[]) =>
      new THREE.Vector3(p[0] - centre[0], p[2] - centre[2], -(p[1] - centre[1]));
    const voxel = (i: number, j: number, k: number) =>
      scenePoint(
        input.affine.slice(0, 3).map((row) => row[0] * i + row[1] * j + row[2] * k + row[3]),
      );
    const corners = (pose: number[][]) =>
      [
        [0, 0],
        [171.9, 0],
        [171.9, 171.9],
        [0, 171.9],
      ].map(([u, v]) =>
        scenePoint(pose.slice(0, 3).map((row) => row[0] * u + row[1] * v + row[3])),
      );
    const contextPoints = (axis: number, position: number) => {
      const v = (position * maximum[axis]) / (n - 1);
      const [i, j, k] = maximum;
      return axis === 0
        ? [voxel(v, 0, k), voxel(v, j, k), voxel(v, j, 0), voxel(v, 0, 0)]
        : axis === 1
          ? [voxel(0, v, k), voxel(i, v, k), voxel(i, v, 0), voxel(0, v, 0)]
          : [voxel(0, 0, v), voxel(i, 0, v), voxel(i, j, v), voxel(0, j, v)];
    };
    let cleanup = () => {};
    async function boot() {
      try {
        const compressed = Uint8Array.from(atob(input.preview_base64_gzip), (c) => c.charCodeAt(0));
        const decoded = new Uint8Array(
          await new Response(
            new Blob([compressed]).stream().pipeThrough(new DecompressionStream('gzip')),
          ).arrayBuffer(),
        );
        if (decoded.length !== n ** 3) throw Error('Unexpected CT preview dimensions');
        if (cancelled) return;
        bytes.current = decoded;
      } catch {
        if (cancelled) return;
        setMessage('CT preview decoding unavailable. Retained static context images remain below.');
        initialized.current = true;
        setGeneration((value) => value + 1);
        return;
      }
      let renderer: THREE.WebGLRenderer | null = null;
      let scene: THREE.Scene | null = null;
      let observer: ResizeObserver | null = null;
      let orbit: OrbitControls | null = null;
      const textures: THREE.Texture[] = [];
      const labels: Array<{ node: HTMLSpanElement; position: THREE.Vector3 }> = [];
      const dispose = () => {
        observer?.disconnect();
        orbit?.dispose();
        scene?.traverse((object) => {
          if (object instanceof THREE.Mesh || object instanceof THREE.Line) {
            object.geometry.dispose();
            const materials = Array.isArray(object.material) ? object.material : [object.material];
            materials.forEach((material: THREE.Material) => material.dispose());
          }
        });
        labels.forEach(({ node }) => node.remove());
        textures.forEach((texture) => texture.dispose());
        renderer?.dispose();
        renderer?.domElement.remove();
      };
      cleanup = dispose;
      try {
        if (new URLSearchParams(location.search).has('no3d'))
          throw Error('Static context requested');
        renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
        renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5));
        renderer.setClearColor(0xfcfcf9);
        renderer.outputColorSpace = THREE.SRGBColorSpace;
        if (!host.current) throw Error('Stage unmounted');
        host.current.append(renderer.domElement);
        scene = new THREE.Scene();
        const camera = new THREE.OrthographicCamera(-205, 205, 190, -190, 1, 1600);
        orbit = new OrbitControls(camera, renderer.domElement);
        orbit.enableDamping = false;
        orbit.enablePan = false;
        orbit.minZoom = 0.65;
        orbit.maxZoom = 2.8;
        const draw = () => {
          if (!cancelled && renderer && scene) {
            renderer.render(scene, camera);
            labels.forEach(({ node, position }) => {
              const point = position.clone().project(camera);
              node.style.left = `${(point.x * 0.5 + 0.5) * host.current!.clientWidth}px`;
              node.style.top = `${(-point.y * 0.5 + 0.5) * host.current!.clientHeight}px`;
            });
          }
        };
        orbit.addEventListener('change', draw);
        scene.add(new THREE.AmbientLight(0xffffff, 2.3));
        const light = new THREE.DirectionalLight(0xffffff, 2);
        light.position.set(250, 450, 350);
        scene.add(light);
        for (const [label, position] of [
          ['L', [158, 0, 0]],
          ['R', [-158, 0, 0]],
          ['S', [0, 158, 0]],
          ['I', [0, -158, 0]],
          ['P', [0, 0, -158]],
          ['A', [0, 0, 158]],
        ] as const) {
          const node = document.createElement('span');
          node.className = styles.axisLabel;
          node.textContent = label;
          host.current.append(node);
          labels.push({ node, position: new THREE.Vector3(...position) });
        }
        const context: Plane[] = [];
        for (let axis = 0; axis < 3; axis++) {
          const canvas = canvases.current[axis];
          if (!canvas) throw Error('Missing context canvas');
          const texture = new THREE.CanvasTexture(canvas);
          textures.push(texture);
          texture.colorSpace = THREE.SRGBColorSpace;
          const mesh = new THREE.Mesh(
            planeGeometry(contextPoints(axis, current.current.positions[axis]), n),
            new THREE.MeshBasicMaterial({
              map: texture,
              side: THREE.DoubleSide,
              transparent: true,
              opacity: 0.65,
              depthWrite: false,
            }),
          );
          mesh.renderOrder = 2;
          context.push(mesh);
          scene.add(mesh);
        }
        // Marching-cubes samples use x→reversed i, y→k, z→j as in the retained prototype.
        const marchingMaterial = new THREE.MeshPhongMaterial({
          color: 0xa4b7aa,
          transparent: true,
          opacity: 0.11,
          depthWrite: false,
          side: THREE.DoubleSide,
          shininess: 12,
        });
        const marching = new MarchingCubes(n, marchingMaterial, false, false, 180000);
        const [low, high] = input.preview_window_hu;
        marching.isolation = (255 * (-350 - low)) / (high - low);
        for (let z = 0; z < n; z++)
          for (let y = 0; y < n; y++)
            for (let x = 0; x < n; x++)
              marching.field[x + n * (y + n * z)] = bytes.current![(n - 1 - x) * n * n + z * n + y];
        marching.update();
        const original = marching.geometry.getAttribute('position');
        const points = new Float32Array(marching.count * 3);
        for (let index = 0; index < marching.count; index++) {
          const p = voxel(
            ((n - 1 - (n * (original.getX(index) + 1)) / 2) * maximum[0]) / (n - 1),
            (((n * (original.getZ(index) + 1)) / 2) * maximum[1]) / (n - 1),
            (((n * (original.getY(index) + 1)) / 2) * maximum[2]) / (n - 1),
          );
          points.set(p.toArray(), index * 3);
        }
        const shellGeometry = new THREE.BufferGeometry();
        shellGeometry.setAttribute('position', new THREE.BufferAttribute(points, 3));
        shellGeometry.computeVertexNormals();
        marching.geometry.dispose();
        const shell = new THREE.Mesh(shellGeometry, marchingMaterial);
        shell.renderOrder = 1;
        scene.add(shell);
        const cube = [
          [0, 0, 0],
          [maximum[0], 0, 0],
          [maximum[0], maximum[1], 0],
          [0, maximum[1], 0],
          [0, 0, maximum[2]],
          [maximum[0], 0, maximum[2]],
          maximum,
          [0, maximum[1], maximum[2]],
        ].map(([i, j, k]) => voxel(i, j, k));
        const edges = [0, 1, 1, 2, 2, 3, 3, 0, 4, 5, 5, 6, 6, 7, 7, 4, 0, 4, 1, 5, 2, 6, 3, 7].map(
          (index) => cube[index],
        );
        scene.add(
          new THREE.LineSegments(
            new THREE.BufferGeometry().setFromPoints(edges),
            new THREE.LineBasicMaterial({ color: 0xa6b3aa, transparent: true, opacity: 0.55 }),
          ),
        );
        const textureById = new Map<string, THREE.Texture>();
        for (const item of payload.observed.states) {
          const texture = await new THREE.TextureLoader().loadAsync(item.image);
          if (cancelled) {
            texture.dispose();
            return;
          }
          texture.colorSpace = THREE.SRGBColorSpace;
          texture.minFilter = THREE.LinearFilter;
          textures.push(texture);
          textureById.set(item.id, texture);
        }
        const empty = [
          new THREE.Vector3(),
          new THREE.Vector3(),
          new THREE.Vector3(),
          new THREE.Vector3(),
        ];
        const candidate = new THREE.Mesh(
          planeGeometry(empty, 192),
          new THREE.MeshBasicMaterial({
            side: THREE.DoubleSide,
            depthWrite: false,
            transparent: true,
            opacity: 1,
          }),
        );
        candidate.renderOrder = 10;
        const candidateLine = outline(empty);
        // Reference geometry is created only after consent, and removed on concealment.
        let referenceLine: THREE.Line | null = null;
        scene.add(candidate, candidateLine);
        const update = () => {
          const selected = current.current;
          context.forEach((mesh, axis) => {
            mesh.visible = selected.showContext;
            mesh.geometry.dispose();
            mesh.geometry = planeGeometry(contextPoints(axis, selected.positions[axis]), n);
            if (mesh.material.map) mesh.material.map.needsUpdate = true;
          });
          shell.visible = selected.showShell;
          candidate.visible = candidateLine.visible = !!selected.state;
          if (selected.state) {
            const pts = corners(selected.state.pose);
            candidate.geometry.dispose();
            candidate.geometry = planeGeometry(pts, 192);
            candidate.material.map = textureById.get(selected.state.id) ?? null;
            candidate.material.needsUpdate = true;
            candidateLine.geometry.dispose();
            candidateLine.geometry = new THREE.BufferGeometry().setFromPoints([...pts, pts[0]]);
          }
          if (selected.referenceShown && !referenceLine) {
            referenceLine = outline(corners(payload.reference.pose), true);
            scene!.add(referenceLine);
          } else if (!selected.referenceShown && referenceLine) {
            scene!.remove(referenceLine);
            referenceLine.geometry.dispose();
            (referenceLine.material as THREE.Material).dispose();
            referenceLine = null;
          }
          draw();
        };
        const reset = () => {
          camera.position.set(420, 280, 380);
          camera.zoom = 1;
          camera.updateProjectionMatrix();
          orbit!.target.set(0, 0, 0);
          orbit!.update();
          draw();
        };
        const resize = () => {
          if (!host.current || !renderer) return;
          const width = host.current.clientWidth,
            height = host.current.clientHeight;
          if (!width || !height) return;
          renderer.setSize(width, height);
          const aspect = width / height,
            extent = Math.max(210, 255 / aspect);
          camera.left = -extent * aspect;
          camera.right = extent * aspect;
          camera.top = extent;
          camera.bottom = -extent;
          camera.updateProjectionMatrix();
          draw();
        };
        observer = new ResizeObserver(resize);
        observer.observe(host.current);
        drawing.current = {
          update,
          reset,
          dispose,
          committed: () =>
            !!renderer &&
            renderer.domElement.isConnected &&
            renderer.domElement.parentElement === host.current &&
            !!host.current &&
            host.current.clientWidth > 0 &&
            host.current.clientHeight > 0 &&
            renderer.domElement.width > 0 &&
            renderer.domElement.height > 0,
          key: (key) => {
            if (key === 'Home') {
              reset();
              return true;
            }
            if (!['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(key)) return false;
            const s = new THREE.Spherical().setFromVector3(
              camera.position.clone().sub(orbit!.target),
            );
            if (key === 'ArrowLeft') s.theta -= 0.12;
            if (key === 'ArrowRight') s.theta += 0.12;
            if (key === 'ArrowUp') s.phi = Math.max(0.1, s.phi - 0.12);
            if (key === 'ArrowDown') s.phi = Math.min(Math.PI - 0.1, s.phi + 0.12);
            camera.position.setFromSpherical(s).add(orbit!.target);
            orbit!.update();
            draw();
            return true;
          },
        };
        reset();
        resize();
        update();
        setWebgl(true);
        setMessage('');
      } catch {
        dispose();
        cleanup = () => {};
        drawing.current = null;
        if (cancelled) return;
        setMessage('3D unavailable. Native CT slices and retained comparisons remain usable.');
      }
      if (!cancelled) {
        initialized.current = true;
        setGeneration((value) => value + 1);
      }
    }
    void boot();
    return () => {
      cancelled = true;
      cleanup();
      drawing.current = null;
      bytes.current = null;
      initialized.current = false;
      callback.current(false);
    };
  }, [payload, input]);

  useLayoutEffect(() => {
    const n = input.preview_size;
    const volume = bytes.current;
    if (volume)
      canvases.current.forEach((canvas, axis) => {
        const context = canvas?.getContext('2d');
        if (!context) return;
        const pixels = context.createImageData(n, n);
        for (let v = 0; v < n; v++)
          for (let u = 0; u < n; u++) {
            const p =
              axis === 0
                ? [positions[axis], u, n - 1 - v]
                : axis === 1
                  ? [u, positions[axis], n - 1 - v]
                  : [u, v, positions[axis]];
            const value = volume[p[0] * n * n + p[1] * n + p[2]],
              q = (v * n + u) * 4;
            pixels.data[q] = pixels.data[q + 1] = pixels.data[q + 2] = value;
            pixels.data[q + 3] = 255;
          }
        context.putImageData(pixels, 0, 0);
      });
    drawing.current?.update();
  }, [generation, positions, referenceShown, state, showContext, showShell, input]);

  useEffect(() => {
    let cancelled = false;
    let frame = 0;
    setReady(false);
    callback.current(false);
    if (!generation || !initialized.current) return;
    const sources = [target, comparison, ...(!bytes.current ? input.slice_previews : [])].filter(
      (src): src is string => !!src,
    );
    void Promise.all(
      sources.map(
        (src) =>
          new Promise<void>((resolve, reject) => {
            const image = new Image();
            image.onload = () => {
              void image.decode().then(resolve, reject);
            };
            image.onerror = () => reject(Error('Retained comparison image could not load'));
            image.src = src;
          }),
      ),
    )
      .then(() => {
        if (cancelled) return;
        frame = requestAnimationFrame(() => {
          if (cancelled) return;
          drawing.current?.update();
          if (drawing.current && !drawing.current.committed()) {
            setMessage(
              'CT canvas is detached or has no drawable size. This stage is not capture-ready.',
            );
            return;
          }
          setReady(true);
          callback.current(true);
        });
      })
      .catch(() => {
        if (!cancelled)
          setMessage(
            'A retained comparison image could not load. This stage is not capture-ready.',
          );
      });
    return () => {
      cancelled = true;
      cancelAnimationFrame(frame);
    };
  }, [generation, target, comparison, input, chapterId, referenceShown]);

  return (
    <section
      className={styles.stage}
      data-native-ready={ready ? 'true' : 'false'}
      data-native-state={stateId ?? 'input'}
      data-native-reference={referenceShown ? 'shown' : 'hidden'}
    >
      <div className={styles.workbench}>
        <div className={styles.card}>
          <div className={styles.heading}>Whole supplied CT crop · LPS millimetres</div>
          <div
            className={styles.volume}
            tabIndex={webgl ? 0 : -1}
            role="img"
            aria-label="Native CT volume and selected section. Arrow keys orbit; Home resets the view."
            onKeyDown={(event) => {
              if (drawing.current?.key(event.key)) event.preventDefault();
            }}
          >
            {/* React owns the overlay; Three.js exclusively owns this empty mount.
                An empty message string must never clear the imperative canvas/labels. */}
            <div ref={host} style={{ position: 'absolute', inset: 0 }} />
            {message ? (
              <p className={styles.message} role="status">
                {message}
              </p>
            ) : null}
          </div>
          <div className={styles.controls}>
            <button type="button" disabled={!webgl} onClick={() => drawing.current?.reset()}>
              Reset view
            </button>
            <label>
              <input
                type="checkbox"
                checked={showContext}
                disabled={!webgl}
                onChange={(event) => setShowContext(event.target.checked)}
              />{' '}
              CT planes
            </label>
            <label>
              <input
                type="checkbox"
                checked={showShell}
                disabled={!webgl}
                onChange={(event) => setShowShell(event.target.checked)}
              />{' '}
              Context shell
            </label>
          </div>
          <p className={styles.caption}>
            Drag to orbit · arrows orbit · Home resets. Pale shell: −350 HU spatial context, not
            organ segmentation. Scene axes display LPS as L / S / −P.
          </p>
          <div className={styles.legend}>
            <span className={styles.candidateKey}>Teal solid: selected candidate</span>
            {referenceShown && (
              <span className={styles.referenceKey}>Amber dashed: evaluator reference</span>
            )}
          </div>
        </div>
        <div className={styles.card}>
          <div className={styles.heading}>Target and discrete recorded candidate</div>
          <div className={styles.comparisons}>
            <figure>
              <img
                src={target}
                alt={
                  mode === 'silhouette'
                    ? 'Target smoothed foreground'
                    : 'Supplied target CT section'
                }
              />
              <figcaption>
                Given target{mode === 'silhouette' ? ' · smoothed foreground' : ''}
              </figcaption>
            </figure>
            <figure>
              {comparison ? (
                <img
                  src={comparison}
                  alt={
                    mode === 'difference'
                      ? 'Absolute target-candidate difference amplified four times'
                      : `Selected candidate ${mode}`
                  }
                />
              ) : (
                <div className={styles.unknown}>Position unknown</div>
              )}
              <figcaption>
                {!state
                  ? 'No candidate location is supplied'
                  : mode === 'difference'
                    ? 'Absolute difference ×4'
                    : `Candidate · step ${state.trace_step}`}
              </figcaption>
            </figure>
          </div>
          <div className={styles.controls}>
            {(['image', 'silhouette', 'difference'] as const).map((value) => (
              <button
                type="button"
                key={value}
                aria-pressed={mode === value}
                disabled={!state && value !== 'image'}
                onClick={() => setMode(value)}
              >
                {value[0].toUpperCase() + value.slice(1)}
              </button>
            ))}
          </div>
          <p className={styles.caption}>
            {state?.role ??
              'Target pixels are supplied; its location is unknown. Reader CT planes are context controls.'}
          </p>
          {mode === 'silhouette' && (
            <p className={styles.caption}>
              Teaching reconstruction of foreground shape; not an organ mask or exact replay of the
              search objective.
            </p>
          )}
          {mode === 'difference' && (
            <p className={styles.caption}>
              Grayscale difference ×4, clipped at 255. Display gain is separate from physical
              scoring.
            </p>
          )}
          {state && (
            <details>
              <summary>Selected slice_to_lps matrix · mm</summary>
              <pre className={styles.matrix}>
                {state.pose
                  .map((row) => row.map((value) => value.toFixed(6).padStart(12)).join(' '))
                  .join('\n')}
              </pre>
            </details>
          )}
        </div>
      </div>
      <div className={styles.slices}>
        {axes.map((label, axis) => (
          <div className={styles.card} key={label}>
            <div className={styles.heading}>{label}</div>
            <canvas
              ref={(node) => {
                canvases.current[axis] = node;
              }}
              width={input.preview_size}
              height={input.preview_size}
              className={styles.sliceCanvas}
              aria-label={`${label} CT context slice`}
            />
            {!bytes.current && input.slice_previews[axis] && (
              <img
                className={styles.staticSlice}
                src={input.slice_previews[axis]}
                alt={`${label} retained static CT context`}
              />
            )}
            <label className={styles.slider}>
              Native voxel{' '}
              {((positions[axis] * (input.shape[axis] - 1)) / (input.preview_size - 1)).toFixed(1)}{' '}
              / {input.shape[axis] - 1}
              <input
                type="range"
                min={0}
                max={input.preview_size - 1}
                value={positions[axis]}
                disabled={!bytes.current}
                aria-label={`${label} position`}
                onChange={(event) =>
                  setPositions((previous) =>
                    previous.map((position, index) =>
                      index === axis ? Number(event.target.value) : position,
                    ),
                  )
                }
              />
            </label>
          </div>
        ))}
      </div>
      <p className={styles.caption}>
        Preview: {input.preview_size}³ samples of the supplied {input.shape.join(' × ')} crop;
        context window {input.preview_window_hu.join(' to ')} HU. This crop is not the entire
        original scan. Reader controls do not represent recorded agent actions.
      </p>
    </section>
  );
}
