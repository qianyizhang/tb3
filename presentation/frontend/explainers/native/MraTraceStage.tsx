import { useEffect, useMemo, useRef, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import type { MraTracePayload } from '../../contracts.generated';
import type { NativeStageProps } from './types';
import styles from './mra-trace.module.css';

type Decoded = { volume: Uint8Array; mask: Uint8Array; surface: Float32Array };
type Network = {
  update: (
    indices: number[],
    contacts: number[],
    residual: number[],
    local: boolean,
    mask: boolean,
  ) => void;
  reset: () => void;
  dispose: () => void;
};
async function decode(encoded: string): Promise<ArrayBuffer> {
  const bytes = Uint8Array.from(atob(encoded), (c) => c.charCodeAt(0));
  return new Response(
    new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip')),
  ).arrayBuffer();
}

function makeNetwork(host: HTMLDivElement, payload: MraTracePayload, raw: Float32Array): Network {
  const { affine, shape } = payload.input;
  const roi = payload.observed.roi;
  const centre = affine
    .slice(0, 3)
    .map((r) => r[3] + r.slice(0, 3).reduce((s, x, i) => s + (x * (shape[i] - 1)) / 2, 0));
  // RAS stays authoritative. This permutation only chooses scene-up.
  const world = (p: number[]) => {
    const q = affine
      .slice(0, 3)
      .map((r, i) => r[3] + r[0] * p[0] + r[1] * p[1] + r[2] * p[2] - centre[i]);
    return new THREE.Vector3(q[0], q[2], -q[1]);
  };
  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5));
  renderer.setClearColor(0xeaf0eb);
  host.appendChild(renderer.domElement);
  const scene = new THREE.Scene();
  const camera = new THREE.OrthographicCamera(-35, 35, 35, -35, 0.1, 2000);
  scene.add(new THREE.HemisphereLight(0xffffff, 0x64706a, 2.3));
  const light = new THREE.DirectionalLight(0xffffff, 2.5);
  light.position.set(-40, 70, 50);
  scene.add(light);
  const render = () => renderer.render(scene, camera);
  const orbit = new OrbitControls(camera, renderer.domElement);
  orbit.enableDamping = false;
  orbit.minZoom = 0.45;
  orbit.maxZoom = 5;
  orbit.addEventListener('change', render);
  const positions = new Float32Array(raw.length);
  const localPositions: number[] = [];
  for (let n = 0; n < raw.length; n += 9) {
    let inside = true;
    for (let v = 0; v < 3; v++) {
      const p = Array.from(raw.subarray(n + v * 3, n + v * 3 + 3));
      if (p.some((x, i) => x < roi[0][i] - 0.5 || x > roi[1][i] - 0.5)) inside = false;
      world(p).toArray(positions, n + v * 3);
    }
    if (inside) localPositions.push(...positions.subarray(n, n + 9));
  }
  const material = new THREE.MeshStandardMaterial({
    color: 0x708391,
    roughness: 0.9,
    side: THREE.DoubleSide,
  });
  const mesh = (points: Float32Array | number[]) => {
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(points, 3));
    geometry.computeVertexNormals();
    const result = new THREE.Mesh(geometry, material);
    scene.add(result);
    return result;
  };
  const fullMesh = mesh(positions),
    localMesh = mesh(localPositions);
  const corners: THREE.Vector3[] = [];
  for (let i = 0; i < 8; i++)
    corners.push(world([0, 1, 2].map((a) => (i & (1 << a) ? roi[1][a] : roi[0][a]) - 0.5)));
  const edges: THREE.Vector3[] = [];
  for (let i = 0; i < 8; i++)
    for (const bit of [1, 2, 4]) if (!(i & bit)) edges.push(corners[i], corners[i | bit]);
  const box = new THREE.LineSegments(
    new THREE.BufferGeometry().setFromPoints(edges),
    new THREE.LineBasicMaterial({ color: 0x008d92 }),
  );
  scene.add(box);
  let local = false;
  const fit = () => {
    const bounds = new THREE.Box3().setFromObject(local ? localMesh : fullMesh);
    const target = bounds.getCenter(new THREE.Vector3());
    const span = Math.max(...bounds.getSize(new THREE.Vector3()).toArray(), 1) * 0.7;
    const width = Math.max(host.clientWidth, 1),
      height = Math.max(host.clientHeight, 1);
    const aspect = width / height;
    camera.left = -span * Math.max(aspect, 1);
    camera.right = -camera.left;
    camera.top = span * Math.max(1 / aspect, 1);
    camera.bottom = -camera.top;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height);
    return target;
  };
  const reset = () => {
    const target = fit();
    orbit.target.copy(target);
    camera.position.copy(target).add(new THREE.Vector3(90, 70, 100));
    camera.zoom = 1;
    camera.updateProjectionMatrix();
    orbit.update();
    render();
  };
  const basis = new THREE.Matrix4().set(
    affine[0][0],
    affine[0][1],
    affine[0][2],
    0,
    affine[2][0],
    affine[2][1],
    affine[2][2],
    0,
    -affine[1][0],
    -affine[1][1],
    -affine[1][2],
    0,
    0,
    0,
    0,
    1,
  );
  const overlays: THREE.InstancedMesh[] = [];
  const clear = () => {
    overlays.splice(0).forEach((o) => {
      scene.remove(o);
      o.geometry.dispose();
      (o.material as THREE.Material).dispose();
      o.dispose();
    });
  };
  const voxels = (indices: number[], color: number) => {
    if (!indices.length) return;
    const result = new THREE.InstancedMesh(
      new THREE.BoxGeometry(1, 1, 1),
      new THREE.MeshStandardMaterial({ color }),
      indices.length,
    );
    indices.forEach((q, i) => {
      const k = q % shape[2],
        j = Math.floor(q / shape[2]) % shape[1],
        x = Math.floor(q / (shape[1] * shape[2]));
      const matrix = basis.clone();
      matrix.setPosition(world([x, j, k]));
      result.setMatrixAt(i, matrix);
    });
    result.instanceMatrix.needsUpdate = true;
    scene.add(result);
    overlays.push(result);
  };
  const keyboard = (e: KeyboardEvent) => {
    if (e.key === 'Home') {
      e.preventDefault();
      reset();
    } else if (['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(e.key)) {
      e.preventDefault();
      const horizontal = e.key === 'ArrowLeft' || e.key === 'ArrowRight';
      const offset = camera.position.clone().sub(orbit.target);
      offset.applyAxisAngle(
        horizontal ? new THREE.Vector3(0, 1, 0) : new THREE.Vector3(1, 0, 0),
        e.key === 'ArrowLeft' || e.key === 'ArrowUp' ? -0.12 : 0.12,
      );
      camera.position.copy(orbit.target).add(offset);
      orbit.update();
      render();
    }
  };
  host.addEventListener('keydown', keyboard);
  const observer = new ResizeObserver(() => {
    fit();
    render();
  });
  observer.observe(host);
  reset();
  return {
    reset,
    update(indices, contacts, residual, focus, showMask) {
      clear();
      voxels(indices, 0x00aaa8);
      voxels(contacts, 0xf0b041);
      voxels(residual, 0xcf438e);
      fullMesh.visible = showMask && !focus;
      localMesh.visible = showMask && focus;
      box.visible = !focus;
      if (local !== focus) {
        local = focus;
        reset();
      } else render();
    },
    dispose() {
      observer.disconnect();
      host.removeEventListener('keydown', keyboard);
      orbit.removeEventListener('change', render);
      orbit.dispose();
      clear();
      fullMesh.geometry.dispose();
      localMesh.geometry.dispose();
      material.dispose();
      box.geometry.dispose();
      box.material.dispose();
      renderer.dispose();
      renderer.domElement.remove();
    },
  };
}

export function MraTraceStage({
  payload,
  stateId,
  chapterId,
  referenceShown,
  onReady,
}: NativeStageProps<MraTracePayload>) {
  const { input, observed, reference } = payload;
  const [decoded, setDecoded] = useState<Decoded | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [fallback, setFallback] = useState(false);
  const [ready, setReady] = useState(false);
  const [focus, setFocus] = useState(chapterId !== 'input');
  const [axis, setAxis] = useState(2);
  const [positions, setPositions] = useState([...observed.seed]);
  const [threshold, setThreshold] = useState(stateId ?? String(observed.states[0].threshold));
  const [showAdded, setShowAdded] = useState(true);
  const [showMask, setShowMask] = useState(true);
  const host = useRef<HTMLDivElement>(null),
    source = useRef<HTMLCanvasElement>(null),
    overlay = useRef<HTMLCanvasElement>(null);
  const network = useRef<Network | null>(null);
  const callback = useRef(onReady);
  callback.current = onReady;
  const saved = chapterId === 'output' || chapterId === 'reference';
  const contactView = chapterId === 'contacts';
  const selected =
    observed.states.find((s) => String(s.threshold) === (contactView ? stateId : threshold)) ??
    observed.states[0];
  const indices = useMemo(
    () => (showAdded && stateId !== null ? (saved ? observed.added : selected.indices) : []),
    [showAdded, stateId, saved, observed.added, selected.indices],
  );
  const contacts = useMemo(
    () => (showAdded && contactView ? selected.contacts.flat() : []),
    [showAdded, contactView, selected.contacts],
  );
  const residual = useMemo(
    () => (referenceShown ? reference.residual : []),
    [referenceShown, reference.residual],
  );
  useEffect(() => {
    let cancelled = false;
    callback.current(false);
    setReady(false);
    setDecoded(null);
    setError(null);
    setFallback(false);
    Promise.all([decode(input.volume), decode(input.mask), decode(input.surface)])
      .then(([v, m, s]) => {
        if (cancelled) return;
        const data = {
          volume: new Uint8Array(v),
          mask: new Uint8Array(m),
          surface: new Float32Array(s),
        };
        setDecoded(data);
        try {
          if (new URLSearchParams(location.search).has('no3d'))
            throw new Error('Requested static view');
          network.current = makeNetwork(host.current!, payload, data.surface);
        } catch {
          setFallback(true);
        }
      })
      .catch((e: unknown) => {
        if (!cancelled) setError(e instanceof Error ? e.message : 'Native array decoding failed');
      });
    return () => {
      cancelled = true;
      callback.current(false);
      network.current?.dispose();
      network.current = null;
    };
  }, [payload, input]);
  useEffect(() => {
    if (!decoded) return;
    network.current?.update(indices, contacts, residual, focus, showMask);
    const dims = input.shape;
    const remaining = [0, 1, 2].filter((a) => a !== axis),
      horizontal = remaining[0],
      vertical = remaining[1];
    const lo = focus ? observed.roi[0] : [0, 0, 0],
      hi = focus ? observed.roi[1] : dims;
    const width = hi[horizontal] - lo[horizontal],
      height = hi[vertical] - lo[vertical];
    const ratio = (width * input.spacing[horizontal]) / (height * input.spacing[vertical]);
    const candidate = new Set(indices),
      touching = new Set(contacts),
      missed = new Set(residual);
    const flat = (p: number[]) => (p[0] * dims[1] + p[1]) * dims[2] + p[2];
    for (const [canvas, decorated] of [
      [source.current, false],
      [overlay.current, true],
    ] as const) {
      if (!canvas) continue;
      const ctx = canvas.getContext('2d');
      if (!ctx) continue;
      canvas.width = 450;
      canvas.height = 450;
      const buffer = document.createElement('canvas');
      buffer.width = width;
      buffer.height = height;
      const pixels = new ImageData(width, height);
      for (let y = 0; y < height; y++)
        for (let x = 0; x < width; x++) {
          const p = [...positions];
          p[horizontal] = x + lo[horizontal];
          p[vertical] = hi[vertical] - 1 - y;
          const q = flat(p),
            g = decoded.volume[q];
          let rgb = [g, g, g];
          if (decorated) {
            const boundary =
              decoded.mask[q] &&
              [
                [-1, 0],
                [1, 0],
                [0, -1],
                [0, 1],
              ].some(([a, b]) => {
                const n = [...p];
                n[horizontal] += a;
                n[vertical] += b;
                return n.some((v, k) => v < 0 || v >= dims[k]) || !decoded.mask[flat(n)];
              });
            if (showMask && boundary) rgb = [123, 174, 208];
            if (candidate.has(q)) rgb = [0, 200, 193];
            if (touching.has(q)) rgb = [240, 176, 65];
            if (missed.has(q)) rgb = [241, 80, 169];
          }
          pixels.data.set([...rgb, 255], (y * width + x) * 4);
        }
      buffer.getContext('2d')!.putImageData(pixels, 0, 0);
      const w = ratio > 1 ? 430 : 430 * ratio,
        h = ratio > 1 ? 430 / ratio : 430;
      ctx.fillStyle = '#0e171b';
      ctx.fillRect(0, 0, 450, 450);
      ctx.imageSmoothingEnabled = false;
      ctx.drawImage(buffer, (450 - w) / 2, (450 - h) / 2, w, h);
    }
    setReady(true);
    callback.current(true);
  }, [decoded, input, observed, axis, positions, focus, indices, contacts, residual, showMask]);
  return (
    <section
      className={styles.stage}
      data-native-ready={String(ready)}
      data-native-state={saved ? 'saved' : selected.threshold}
      data-reference-visible={String(referenceShown)}
      data-native-shape={input.shape.join(',')}
      data-native-axis={axis}
      data-native-slice={positions[axis]}
      data-native-additions={indices.length}
      data-native-contacts={contacts.length}
    >
      <div className={styles.controls}>
        <label>
          <input type="checkbox" checked={focus} onChange={(e) => setFocus(e.target.checked)} />
          Local detail
        </label>
        <label>
          <input
            type="checkbox"
            checked={showMask}
            onChange={(e) => setShowMask(e.target.checked)}
          />
          Input mask
        </label>
        {stateId !== null && (
          <label>
            <input
              type="checkbox"
              checked={showAdded}
              onChange={(e) => setShowAdded(e.target.checked)}
            />
            {saved ? 'Saved additions' : 'Candidate'}
          </label>
        )}
        <button type="button" onClick={() => network.current?.reset()}>
          Reset camera
        </button>
      </div>
      <div
        className={styles.scene}
        ref={host}
        tabIndex={0}
        role="img"
        aria-label="Native MRA vessel mask in RAS coordinates. Arrow keys orbit; Home resets."
      >
        {(!ready || fallback) && (
          <div className={styles.fallback}>
            {fallback ? (
              <>
                <img src={input.mip} alt="Native MRA maximum intensity projection" />
                <p>
                  3D unavailable. Source slices and recorded threshold controls remain available.
                </p>
              </>
            ) : (
              <p>{error ?? 'Decoding native MRA arrays…'}</p>
            )}
          </div>
        )}
      </div>
      <p className={styles.note}>
        {focus
          ? 'Local display crop; cut edges are display boundaries, not vessel endings.'
          : 'Whole solver-visible MRA crop; the original complete scan is not shown.'}{' '}
        Native NIfTI planes can be oblique to patient axes.
      </p>
      {chapterId === 'threshold' && (
        <label className={styles.threshold}>
          Recorded threshold{' '}
          <select value={threshold} onChange={(e) => setThreshold(e.target.value)}>
            {observed.states.map((s) => (
              <option key={s.threshold} value={s.threshold}>
                {s.threshold}
              </option>
            ))}
          </select>
          <strong>{selected.count} voxels</strong>
          <span>Deterministic reconstruction from native intensities; display window 70–650.</span>
        </label>
      )}
      {contactView && (
        <p>
          Recorded threshold {selected.threshold}:{' '}
          {selected.contacts.map((p) => p.length).join(' + ')} contact voxels in separate
          26-connected patches.
        </p>
      )}
      {saved && (
        <p>
          {observed.added.length} saved additions. Reader threshold alternatives do not change this
          output.
        </p>
      )}
      <div className={styles.controls}>
        <label>
          Native slice axis{' '}
          <select value={axis} onChange={(e) => setAxis(Number(e.target.value))}>
            {['i', 'j', 'k'].map((a, n) => (
              <option key={a} value={n}>
                {a}
              </option>
            ))}
          </select>
        </label>
        <label className={styles.slice}>
          Slice {['i', 'j', 'k'][axis]} = {positions[axis]} / {input.shape[axis] - 1}
          <input
            aria-label="Native MRA slice index"
            type="range"
            min={0}
            max={input.shape[axis] - 1}
            value={positions[axis]}
            onChange={(e) =>
              setPositions((p) => p.map((v, i) => (i === axis ? Number(e.target.value) : v)))
            }
          />
        </label>
      </div>
      <div className={styles.slices}>
        <figure>
          <canvas ref={source} aria-label="Native MRA source slice" />
          <figcaption>Source MRA · nearest native samples</figcaption>
        </figure>
        <figure>
          <canvas
            ref={overlay}
            aria-label="Native MRA slice with input mask and selected voxel overlays"
          />
          <figcaption>Matched slice with voxel overlays</figcaption>
        </figure>
      </div>
      <ul className={styles.legend}>
        <li>
          <span className={styles.inputKey} />
          Input mask outline / surface
        </li>
        {stateId !== null && (
          <li>
            <span className={styles.addKey} />
            {saved ? 'Saved additions' : 'Reconstructed candidate'}
          </li>
        )}
        {contactView && (
          <li>
            <span className={styles.contactKey} />
            Candidate-to-mask contacts
          </li>
        )}
        {referenceShown && (
          <li>
            <span className={styles.referenceKey} />
            Missed private-reference voxels
          </li>
        )}
      </ul>
    </section>
  );
}
