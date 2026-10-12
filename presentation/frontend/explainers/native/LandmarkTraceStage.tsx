import { useEffect, useLayoutEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import type { LandmarkTracePayload, LandmarkTracePoint } from '../../contracts.generated';
import type { NativeStageProps } from './types';
import { boxEdges, insideCrop, nearestSample, planeCorners, rasPoint } from './landmark-geometry';
import styles from './landmark-trace.module.css';

type Network = {
  update: () => void;
  reset: () => void;
  dispose: () => void;
  committed: () => boolean;
};
const titles = ['Sagittal · i / L', 'Coronal · j / A', 'Axial · k / S'];
const format = (p: number[]) => p.map((v) => v.toFixed(1)).join(', ');

export function LandmarkTraceStage({
  payload,
  stateId,
  chapterId,
  referenceShown,
  onReady,
}: NativeStageProps<LandmarkTracePayload>) {
  const { input, observed, reference } = payload;
  const [inspectionId, setInspectionId] = useState(stateId);
  const state = observed.states.find((s) => s.id === (inspectionId ?? stateId));
  const inspectionOptions = observed.states.filter((s) =>
    chapterId === 'search'
      ? s.kind === 'region' && s.trace_step <= 17
      : chapterId === 'projection'
        ? s.trace_step >= 18 && s.trace_step <= 24
        : chapterId === 'levels'
          ? s.trace_step >= 26 && s.trace_step <= 33
          : chapterId === 'centres'
            ? s.kind === 'points' && s.trace_step >= 34 && s.trace_step <= 37
            : false,
  );
  useEffect(() => {
    setInspectionId(stateId);
  }, [stateId, chapterId]);
  const saved = chapterId === 'output' || chapterId === 'reference' || state?.kind === 'saved';
  const visiblePoints = saved ? observed.points : state?.kind === 'points' ? state.points : [];
  const [selectedName, setSelectedName] = useState('T4');
  const [positions, setPositions] = useState(() => input.shape.map((s) => Math.floor(s / 2)));
  const [raw, setRaw] = useState<Uint8Array | null>(null);
  const [fallback, setFallback] = useState(false);
  const [error, setError] = useState('');
  const [ready, setReady] = useState(false);
  const [capture, setCapture] = useState(false);
  const host = useRef<HTMLDivElement>(null);
  const slices = useRef<Array<HTMLCanvasElement | null>>([]);
  const textures = useRef<Array<HTMLCanvasElement | null>>([]);
  const network = useRef<Network | null>(null);
  const callback = useRef(onReady);
  callback.current = onReady;
  useLayoutEffect(() => {
    setCapture(!!host.current?.closest('[data-explainer-export-frame]'));
  }, []);
  const current = useRef({ positions, state, visiblePoints, referenceShown, selectedName });
  current.current = { positions, state, visiblePoints, referenceShown, selectedName };
  const delivered = payload.delivered_images.find((image) => image.step === state?.delivered_step);
  const selected = visiblePoints.find((p) => p.name === selectedName);
  const truth = referenceShown ? reference.points.find((p) => p.name === selectedName) : undefined;

  // Chapter transitions choose a recorded discrete inspection, never interpolate a search.
  useEffect(() => {
    const point = saved
      ? observed.points.find((p) => p.name === 'T4')
      : (state?.points.find((p) => p.ijk) ?? state?.points[0]);
    setSelectedName(point?.name ?? 'T4');
    const centre =
      state?.center_ijk ??
      (state?.bounds
        ? state.bounds[0].map((v, a) => (v + state.bounds![1][a]) / 2 - 0.5)
        : point?.ijk);
    setPositions(
      (centre ?? input.shape.map((s) => Math.floor(s / 2))).map((v, a) =>
        Math.max(0, Math.min(input.shape[a] - 1, Math.round(v))),
      ),
    );
  }, [stateId, chapterId, input, state, saved, observed.points]);

  useEffect(() => {
    let cancelled = false;
    setRaw(null);
    setError('');
    setReady(false);
    setFallback(false);
    callback.current(false);
    const compressed = Uint8Array.from(atob(input.volume), (c) => c.charCodeAt(0));
    void new Response(new Blob([compressed]).stream().pipeThrough(new DecompressionStream('gzip')))
      .arrayBuffer()
      .then((buffer) => {
        if (cancelled) return;
        const bytes = new Uint8Array(buffer);
        if (bytes.length !== input.preview_shape.reduce((a, b) => a * b, 1))
          throw Error('Preview dimensions do not match retained array');
        setRaw(bytes);
      })
      .catch((e: unknown) => {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : 'Preview decoding unavailable');
          setFallback(true);
        }
      });
    return () => {
      cancelled = true;
      callback.current(false);
    };
  }, [input]);

  useEffect(() => {
    if (!raw || !host.current) return;
    let renderer: THREE.WebGLRenderer | null = null;
    let orbit: OrbitControls | null = null;
    let observer: ResizeObserver | null = null;
    const scene = new THREE.Scene();
    const textureList: THREE.CanvasTexture[] = [];
    const dynamic = new THREE.Group();
    const labelNodes: Array<{ node: HTMLSpanElement; point: THREE.Vector3; offset: number }> = [];
    const centre = rasPoint(
      input.affine,
      input.shape.map((s) => (s - 1) / 2),
    );
    const world = (p: number[]) => {
      const r = rasPoint(input.affine, p);
      return new THREE.Vector3(r[0] - centre[0], r[2] - centre[2], -(r[1] - centre[1]));
    };
    const disposeObject = (object: THREE.Object3D) =>
      object.traverse((o) => {
        if (o instanceof THREE.Mesh || o instanceof THREE.Line) {
          o.geometry.dispose();
          (Array.isArray(o.material) ? o.material : [o.material]).forEach((m: THREE.Material) =>
            m.dispose(),
          );
        }
      });
    const clear = () => {
      disposeObject(dynamic);
      dynamic.clear();
      labelNodes.splice(0).forEach(({ node }) => node.remove());
    };
    const dispose = () => {
      observer?.disconnect();
      orbit?.dispose();
      clear();
      disposeObject(scene);
      textureList.forEach((t) => t.dispose());
      renderer?.dispose();
      renderer?.domElement.remove();
    };
    try {
      if (new URLSearchParams(location.search).has('no3d')) throw Error('2D context requested');
      renderer = new THREE.WebGLRenderer({ antialias: true });
      renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5));
      renderer.setClearColor(0x101b24);
      renderer.outputColorSpace = THREE.SRGBColorSpace;
      host.current.appendChild(renderer.domElement);
      const camera = new THREE.OrthographicCamera(-500, 500, 500, -500, 1, 4000);
      orbit = new OrbitControls(camera, renderer.domElement);
      orbit.enableDamping = false;
      orbit.enablePan = false;
      orbit.enabled = !host.current.closest('[data-explainer-export-frame]');
      orbit.minZoom = 0.6;
      orbit.maxZoom = 3;
      const draw = () => {
        renderer!.render(scene, camera);
        labelNodes.forEach(({ node, point, offset }) => {
          const p = point.clone().project(camera);
          node.style.left = `${((p.x + 1) * host.current!.clientWidth) / 2}px`;
          node.style.top = `${Math.max(12, Math.min(host.current!.clientHeight - 12, ((1 - p.y) * host.current!.clientHeight) / 2 + offset))}px`;
        });
      };
      orbit.addEventListener('change', draw);
      const line = (points: number[][], color: number, dashed = false) => {
        const result = new THREE.LineSegments(
          new THREE.BufferGeometry().setFromPoints(points.map(world)),
          dashed
            ? new THREE.LineDashedMaterial({
                color,
                dashSize: 6,
                gapSize: 4,
                depthTest: false,
                depthWrite: false,
                transparent: true,
                opacity: 1,
              })
            : new THREE.LineBasicMaterial({
                color,
                depthTest: false,
                depthWrite: false,
                transparent: true,
                opacity: 1,
              }),
        );
        result.computeLineDistances();
        result.renderOrder = 25;
        dynamic.add(result);
      };
      const label = (text: string, p: number[], color: string, offset = 0) => {
        const node = document.createElement('span');
        node.className = styles.label;
        node.textContent = text;
        node.style.color = color;
        host.current!.append(node);
        labelNodes.push({ node, point: world(p), offset });
      };
      const planes = [0, 1, 2].map((a) => {
        const texture = new THREE.CanvasTexture(textures.current[a]!);
        texture.colorSpace = THREE.SRGBColorSpace;
        textureList.push(texture);
        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute('uv', new THREE.Float32BufferAttribute([0, 1, 1, 1, 1, 0, 0, 0], 2));
        geometry.setIndex([0, 1, 2, 0, 2, 3]);
        const mesh = new THREE.Mesh(
          geometry,
          new THREE.MeshBasicMaterial({
            map: texture,
            side: THREE.DoubleSide,
            transparent: true,
            opacity: 0.8,
          }),
        );
        scene.add(mesh);
        return mesh;
      });
      scene.add(dynamic);
      const marker = (
        p: LandmarkTracePoint,
        color: number,
        referencePoint: boolean,
        text?: string | null,
        offset = 0,
      ) => {
        if (!p.ijk) return;
        if (!insideCrop(p.ijk, input.shape) && p.name !== reference.wrong_level.claimed_name)
          return;
        const pos = world(p.ijk);
        const geometry = referencePoint
          ? new THREE.RingGeometry(4, 5.5, 24)
          : new THREE.CircleGeometry(4.5, 20);
        const mesh = new THREE.Mesh(
          geometry,
          new THREE.MeshBasicMaterial({
            color,
            side: THREE.DoubleSide,
            depthTest: false,
            depthWrite: false,
            transparent: true,
            opacity: 1,
          }),
        );
        mesh.position.copy(pos);
        mesh.quaternion.copy(camera.quaternion);
        mesh.renderOrder = 30;
        dynamic.add(mesh);
        if (text !== null)
          label(
            text ?? `${p.name}${referencePoint ? ' ref' : saved ? ' saved' : ' centre'}`,
            p.ijk,
            referencePoint ? '#f5bc62' : '#31d1b6',
            offset,
          );
      };
      const update = () => {
        clear();
        const value = current.current;
        line(boxEdges([[-0.5, -0.5, -0.5], input.shape.map((s) => s - 0.5)]), 0x607786);
        planes.forEach((mesh, a) => {
          const sample =
            input.preview_indices[a][nearestSample(input.preview_indices[a], value.positions[a])];
          mesh.geometry.setAttribute(
            'position',
            new THREE.Float32BufferAttribute(
              planeCorners(a, sample, input.shape).flatMap((p) => world(p).toArray()),
              3,
            ),
          );
          mesh.geometry.computeBoundingSphere();
          textureList[a].needsUpdate = true;
        });
        if (value.state?.bounds) {
          line(boxEdges(value.state.bounds.map((p) => p.map((v) => v - 0.5))), 0x67d6ef);
          label(
            value.state.kind === 'slab' ? 'Recorded inspection slab' : 'Recorded inspection bounds',
            value.state.bounds[1].map((v) => v - 0.5),
            '#67d6ef',
          );
        }
        if (value.state?.center_ijk) {
          const p = value.state.center_ijk;
          line(
            [0, 1, 2].flatMap((axis) => {
              const low = [...p],
                high = [...p];
              const size = 8 / input.spacing[axis];
              low[axis] -= size;
              high[axis] += size;
              return [low, high];
            }),
            0x67d6ef,
          );
          label(
            `Requested inspection centre${value.state.radius_mm === null ? '' : value.state.radius_mm === 0 ? ' · whole orthogonal planes' : ` · r=${value.state.radius_mm} mm`}`,
            p,
            '#67d6ef',
          );
        }
        if (value.state?.levels.length) {
          value.state.levels.forEach((k) => {
            const p = planeCorners(value.state?.axis ?? 2, k, input.shape);
            line(
              p.flatMap((v, i) => [v, p[(i + 1) % 4]]),
              0x67d6ef,
            );
          });
          label(
            'Recorded candidate levels',
            [input.shape[0] - 0.5, -0.5, Math.max(...value.state.levels)],
            '#67d6ef',
          );
        }
        value.visiblePoints
          .filter((p) => p.name === value.selectedName)
          .forEach((p) =>
            marker(
              p,
              0x31d1b6,
              false,
              value.referenceShown && value.selectedName === reference.wrong_level.claimed_name
                ? `${p.name} saved / ${reference.wrong_level.matched_name} reference`
                : undefined,
              13,
            ),
          );
        if (value.referenceShown) {
          reference.points
            .filter((p) => p.name === value.selectedName)
            .forEach((p) => marker(p, 0xf5bc62, true, undefined, -16));
          if (value.selectedName === reference.wrong_level.claimed_name) {
            marker(
              {
                name: reference.wrong_level.matched_name,
                status: 'observed',
                ijk: reference.wrong_level.matched_ijk,
              },
              0xf5bc62,
              true,
              null,
            );
            const top = reference.wrong_level.outside_ijk[2] + 18;
            line(
              boxEdges([
                [-0.5, -0.5, input.shape[2] - 0.5],
                [input.shape[0] - 0.5, input.shape[1] - 0.5, top],
              ]),
              0xf5bc62,
              true,
            );
            label('Excluded context · no CT pixels', [0, 0, top], '#f5bc62', 35);
          }
        }
        draw();
      };
      const fit = () => {
        const w = host.current!.clientWidth,
          h = host.current!.clientHeight;
        if (!w || !h) return;
        renderer!.setSize(w, h);
        const ratio = w / h;
        const extent = Math.max(440, 440 / ratio);
        camera.left = -extent * ratio;
        camera.right = extent * ratio;
        camera.top = extent;
        camera.bottom = -extent;
        camera.updateProjectionMatrix();
        draw();
      };
      const reset = () => {
        camera.position.set(850, 520, 1000);
        camera.zoom = 1;
        camera.updateProjectionMatrix();
        orbit!.target.set(0, 0, 0);
        orbit!.update();
        fit();
        update();
      };
      const key = (event: KeyboardEvent) => {
        if (host.current?.closest('[data-explainer-export-frame]')) return;
        if (event.key === 'Home') {
          event.preventDefault();
          reset();
          return;
        }
        if (!['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(event.key)) return;
        event.preventDefault();
        const s = new THREE.Spherical().setFromVector3(camera.position.clone().sub(orbit!.target));
        if (event.key === 'ArrowLeft') s.theta -= 0.12;
        if (event.key === 'ArrowRight') s.theta += 0.12;
        if (event.key === 'ArrowUp') s.phi = Math.max(0.1, s.phi - 0.12);
        if (event.key === 'ArrowDown') s.phi = Math.min(Math.PI - 0.1, s.phi + 0.12);
        camera.position.setFromSpherical(s).add(orbit!.target);
        orbit!.update();
        update();
      };
      host.current.addEventListener('keydown', key);
      const element = host.current;
      observer = new ResizeObserver(fit);
      observer.observe(element);
      network.current = {
        update,
        reset,
        committed: () =>
          !!renderer?.domElement.isConnected && element.clientWidth > 0 && element.clientHeight > 0,
        dispose: () => {
          element.removeEventListener('keydown', key);
          dispose();
        },
      };
      reset();
      setFallback(false);
    } catch {
      dispose();
      network.current = null;
      setFallback(true);
    }
    return () => {
      network.current?.dispose();
      network.current = null;
    };
  }, [raw, input, reference, saved]);

  useLayoutEffect(() => {
    if (!raw) return;
    [0, 1, 2].forEach((axis) => {
      const remaining = [0, 1, 2].filter((a) => a !== axis),
        hAxis = remaining[0],
        vAxis = remaining[1];
      const ratio =
        (input.shape[hAxis] * input.spacing[hAxis]) / (input.shape[vAxis] * input.spacing[vAxis]);
      const w = Math.round(220 * Math.min(1, ratio)),
        h = Math.round(220 / Math.max(1, ratio));
      const slice = nearestSample(input.preview_indices[axis], positions[axis]);
      for (const [canvas, decorated] of [
        [textures.current[axis], false],
        [slices.current[axis], true],
      ] as const) {
        const ctx = canvas?.getContext('2d');
        if (!canvas || !ctx) continue;
        canvas.width = w;
        canvas.height = h;
        const pixels = ctx.createImageData(w, h);
        for (let y = 0; y < h; y++)
          for (let x = 0; x < w; x++) {
            const p = [0, 0, 0];
            p[axis] = slice;
            p[hAxis] = nearestSample(
              input.preview_indices[hAxis],
              ((x + 0.5) * input.shape[hAxis]) / w - 0.5,
            );
            p[vAxis] = nearestSample(
              input.preview_indices[vAxis],
              input.shape[vAxis] - 0.5 - ((y + 0.5) * input.shape[vAxis]) / h,
            );
            const g = raw[(p[0] * input.preview_shape[1] + p[1]) * input.preview_shape[2] + p[2]];
            pixels.data.set([g, g, g, 255], (y * w + x) * 4);
          }
        ctx.putImageData(pixels, 0, 0);
        if (!decorated) continue;
        const xy = (p: number[]) => [
          ((p[hAxis] + 0.5) / input.shape[hAxis]) * w,
          ((input.shape[vAxis] - 0.5 - p[vAxis]) / input.shape[vAxis]) * h,
        ];
        ctx.strokeStyle = '#a6bfce';
        ctx.lineWidth = 0.7;
        const [cx, cy] = xy(positions);
        ctx.beginPath();
        ctx.moveTo(cx, 0);
        ctx.lineTo(cx, h);
        ctx.moveTo(0, cy);
        ctx.lineTo(w, cy);
        ctx.stroke();
        if (state?.bounds) {
          const [x0, y0] = xy(state.bounds[0].map((v) => v - 0.5)),
            [x1, y1] = xy(state.bounds[1].map((v) => v - 0.5));
          ctx.strokeStyle = '#67d6ef';
          ctx.lineWidth = 1.5;
          ctx.strokeRect(x0, y1, x1 - x0, y0 - y1);
        }
        if (state?.center_ijk) {
          const [x, y] = xy(state.center_ijk);
          ctx.strokeStyle = '#67d6ef';
          ctx.lineWidth = 1.5;
          ctx.beginPath();
          ctx.moveTo(x - 6, y);
          ctx.lineTo(x + 6, y);
          ctx.moveTo(x, y - 6);
          ctx.lineTo(x, y + 6);
          ctx.stroke();
        }
        if (state?.levels.length && axis !== (state.axis ?? 2)) {
          ctx.strokeStyle = '#67d6ef';
          state.levels.forEach((k) => {
            const p = [...positions];
            p[state.axis ?? 2] = k;
            const [x, y] = xy(p);
            ctx.beginPath();
            if (hAxis === (state.axis ?? 2)) {
              ctx.moveTo(x, 0);
              ctx.lineTo(x, h);
            } else {
              ctx.moveTo(0, y);
              ctx.lineTo(w, y);
            }
            ctx.stroke();
          });
        }
        const mark = (point: LandmarkTracePoint, amber: boolean) => {
          if (!point.ijk || !insideCrop(point.ijk, input.shape)) return;
          const halfWidth = input.shape[axis] / input.preview_shape[axis] / 2;
          if (Math.abs(point.ijk[axis] - input.preview_indices[axis][slice]) > halfWidth) return;
          const [x, y] = xy(point.ijk);
          ctx.strokeStyle = ctx.fillStyle = amber ? '#f5bc62' : '#31d1b6';
          ctx.lineWidth = 1.8;
          ctx.setLineDash(amber ? [2, 2] : []);
          ctx.beginPath();
          ctx.arc(x, y, 4, 0, Math.PI * 2);
          if (amber) ctx.stroke();
          else ctx.fill();
          ctx.setLineDash([]);
          ctx.font = '9px sans-serif';
          ctx.fillText(point.name, x + 6, y - 5);
        };
        visiblePoints.filter((p) => p.name === selectedName).forEach((p) => mark(p, false));
        if (referenceShown) {
          reference.points.filter((p) => p.name === selectedName).forEach((p) => mark(p, true));
          if (selectedName === reference.wrong_level.claimed_name)
            mark(
              {
                name: reference.wrong_level.matched_name,
                status: 'observed',
                ijk: reference.wrong_level.matched_ijk,
              },
              true,
            );
        }
      }
    });
    network.current?.update();
  }, [raw, input, positions, state, visiblePoints, selectedName, referenceShown, reference]);

  useEffect(() => {
    let cancelled = false;
    let frame = 0;
    setReady(false);
    callback.current(false);
    if (!raw && !error) return;
    const images = [delivered?.src, fallback ? input.poster : undefined].filter(
      (src): src is string => !!src,
    );
    void Promise.all(
      images.map(
        (src) =>
          new Promise<void>((resolve, reject) => {
            const image = new Image();
            image.onload = () => {
              void image.decode().then(resolve, reject);
            };
            image.onerror = () => reject(Error('Retained image failed to load'));
            image.src = src;
          }),
      ),
    )
      .then(() => {
        frame = requestAnimationFrame(() => {
          if (cancelled) return;
          network.current?.update();
          if (network.current && !network.current.committed()) return;
          if (!raw && !fallback) return;
          setReady(true);
          callback.current(true);
        });
      })
      .catch((e: unknown) => {
        if (!cancelled) setError(e instanceof Error ? e.message : 'Image unavailable');
      });
    return () => {
      cancelled = true;
      cancelAnimationFrame(frame);
    };
  }, [
    raw,
    error,
    delivered,
    fallback,
    input.poster,
    state,
    positions,
    selectedName,
    referenceShown,
  ]);

  const choose = (name: string) => {
    setSelectedName(name);
    const point = visiblePoints.find((p) => p.name === name);
    if (point?.ijk && insideCrop(point.ijk, input.shape))
      setPositions(
        point.ijk.map((v, a) => Math.min(input.shape[a] - 1, Math.max(0, Math.round(v)))),
      );
  };
  return (
    <section
      className={styles.stage}
      data-native-ready={String(ready)}
      data-native-renderer={fallback ? 'poster' : 'webgl'}
      data-native-state={state?.id ?? 'input'}
      data-reference-visible={String(referenceShown)}
      data-native-shape={input.shape.join(',')}
      data-native-saved-visible={String(saved)}
      data-native-selected-name={visiblePoints.length ? selectedName : ''}
      data-native-selected-status={selected?.status ?? ''}
      data-native-selected-ijk={selected?.ijk?.join(',') ?? ''}
      data-native-selected-ras={selected?.ijk ? rasPoint(input.affine, selected.ijk).join(',') : ''}
      data-native-point-count={visiblePoints.filter((p) => p.ijk && p.name === selectedName).length}
      data-native-inspection-count={
        (state?.bounds ? 1 : 0) + (state?.center_ijk ? 1 : 0) + (state?.levels.length ?? 0)
      }
      data-native-reference-count={
        referenceShown
          ? reference.points.filter(
              (p) =>
                p.ijk &&
                p.name === selectedName &&
                (insideCrop(p.ijk, input.shape) || p.name === reference.wrong_level.claimed_name),
            ).length + (selectedName === reference.wrong_level.claimed_name ? 1 : 0)
          : 0
      }
      data-native-reference-outside={
        referenceShown && truth?.ijk && !insideCrop(truth.ijk, input.shape) ? truth.name : ''
      }
      data-native-reader-ijk={positions.join(',')}
      data-native-reader-samples={positions
        .map((v, a) => input.preview_indices[a][nearestSample(input.preview_indices[a], v)])
        .join(',')}
    >
      <div className={styles.workbench}>
        <div className={styles.card}>
          <header className={styles.heading}>
            <strong>Whole supplied CT crop</strong>
            <span>{input.shape.join(' × ')} · native L / A / S</span>
          </header>
          <div className={styles.sceneWrap}>
            <div
              className={styles.scene}
              ref={host}
              tabIndex={capture ? -1 : 0}
              role="img"
              aria-label="CT crop in physical RAS coordinates. Arrow keys orbit; Home resets."
            />
            {fallback && (
              <div className={styles.poster}>
                <img src={input.poster} alt="Derived whole supplied CT crop context" />
                <span>2D fallback · source crop context</span>
              </div>
            )}
            {!raw && !fallback && <p className={styles.loading}>Decoding bounded CT preview…</p>}
          </div>
          <div className={styles.controls}>
            <button
              type="button"
              onClick={() => network.current?.reset()}
              disabled={fallback || capture}
            >
              Reset orbit
            </button>
            <span>Arrow keys orbit · Home resets</span>
          </div>
          <p className={styles.note}>
            Physical scale preserved · {input.preview_window_hu.join(' to ')} HU fixed preview
            window. Reader slices use explicitly mapped nearest native samples.
          </p>
          <div className={styles.legend}>
            <span className={styles.readerKey}>Reader MPR</span>
            <span className={styles.inspectKey}>Recorded inspection</span>
            {visiblePoints.length > 0 && (
              <span className={styles.savedKey}>{saved ? 'Saved point' : 'Solver centre'}</span>
            )}
            {referenceShown && (
              <span className={styles.referenceKey}>Reference · open / dashed</span>
            )}
          </div>
        </div>
        <div className={`${styles.card} ${styles.operation}`}>
          <header className={styles.heading}>
            <strong>
              {saved
                ? 'Saved named output'
                : (state?.label ?? 'Receive crop and landmark definitions')}
            </strong>
            <span>
              {state
                ? `Recorded step ${state.trace_step}`
                : `${input.names.length} requested names`}
            </span>
          </header>
          {inspectionOptions.length > 0 && (
            <label className={styles.inspection}>
              Recorded inspection
              <select
                aria-label="Recorded inspection"
                disabled={capture}
                value={state?.id ?? ''}
                onChange={(e) => setInspectionId(e.target.value)}
              >
                {inspectionOptions.map((s) => (
                  <option key={s.id} value={s.id}>
                    Step {s.trace_step} · {s.label}
                  </option>
                ))}
              </select>
            </label>
          )}
          <p className={styles.description}>
            {state?.description ??
              'The reader can inspect the supplied crop. No submitted locations are shown before the saved output.'}
          </p>
          {delivered ? (
            <figure className={styles.delivered}>
              <a href={delivered.src} target="_blank" rel="noreferrer">
                <img
                  src={delivered.src}
                  alt={`Exact recorded delivered image at step ${delivered.step}`}
                />
              </a>
              <figcaption>
                Recorded delivered PNG · step {delivered.step} · click to inspect
                <br />
                {delivered.path} · separate from reader-generated MPR
              </figcaption>
            </figure>
          ) : (
            <p className={styles.empty}>No delivered image for this discrete state.</p>
          )}
          {visiblePoints.length > 0 && (
            <div className={styles.selection}>
              <label>
                {saved ? 'Saved name' : 'Solver-computed centre'}{' '}
                <select
                  aria-label={saved ? 'Saved name' : 'Solver-computed centre'}
                  disabled={capture}
                  value={selectedName}
                  onChange={(e) => choose(e.target.value)}
                >
                  {visiblePoints.map((p) => (
                    <option key={p.name}>{p.name}</option>
                  ))}
                </select>
              </label>
              <strong>
                {selected?.name ?? selectedName} · {selected?.status ?? 'No point in this state'}
              </strong>
              {selected?.ijk && (
                <>
                  <code>native [{format(selected.ijk)}]</code>
                  <code>RAS [{format(rasPoint(input.affine, selected.ijk))}] mm</code>
                </>
              )}
              <span className={styles.definition}>
                {input.names.find((n) => n.name === selectedName)?.definition}
              </span>
              {!saved && <span>Intensity-weighted solver observation; not ground truth.</span>}
            </div>
          )}
          {referenceShown && (
            <div className={styles.reference}>
              <strong>
                Reference {selectedName} · {truth?.status ?? 'no named reference'}
              </strong>
              {truth?.ijk && !insideCrop(truth.ijk, input.shape) && (
                <span>Outside supplied crop · no input CT pixels at this reference location.</span>
              )}
              {truth?.ijk && (
                <>
                  <code>native [{format(truth.ijk)}]</code>
                  <code>RAS [{format(rasPoint(input.affine, truth.ijk))}] mm</code>
                </>
              )}
              {selectedName === reference.wrong_level.claimed_name && (
                <p>
                  Saved {reference.wrong_level.claimed_name} is{' '}
                  {reference.wrong_level.separation_mm.toFixed(3)} mm from source{' '}
                  {reference.wrong_level.matched_name}. True {reference.wrong_level.outside_name}:
                  k={reference.wrong_level.outside_ijk[2]} beyond supplied k=0–{input.shape[2] - 1};
                  dashed context has no image pixels.
                </p>
              )}
              {reference.frozen.errors_mm[selectedName] !== undefined && (
                <span>
                  Frozen named error: {reference.frozen.errors_mm[selectedName].toFixed(2)} mm
                </span>
              )}
            </div>
          )}
          {state?.bounds && (
            <code className={styles.bounds}>
              Recorded native cell bounds (half-open) [{format(state.bounds[0])}] → [
              {format(state.bounds[1])}]
            </code>
          )}
          {state?.levels.length ? (
            <p className={styles.note}>Recorded axial levels: {state.levels.join(', ')}</p>
          ) : null}
        </div>
      </div>
      <div className={styles.slices}>
        {[0, 1, 2].map((axis) => {
          const sampled =
            input.preview_indices[axis][
              nearestSample(input.preview_indices[axis], positions[axis])
            ];
          return (
            <div className={styles.card} key={axis}>
              <header className={styles.heading}>
                <strong>{titles[axis]}</strong>
                <span>Reader-generated MPR</span>
              </header>
              <div className={styles.sliceImage}>
                <canvas
                  ref={(node) => {
                    slices.current[axis] = node;
                  }}
                  aria-label={`${titles[axis]} reader CT slice`}
                />
                <canvas
                  hidden
                  ref={(node) => {
                    textures.current[axis] = node;
                  }}
                />
              </div>
              <label className={styles.slider}>
                Requested {['i', 'j', 'k'][axis]}={positions[axis]} · sampled {sampled}
                <input
                  aria-label={`Native ${['i', 'j', 'k'][axis]} slice`}
                  type="range"
                  disabled={capture}
                  min={0}
                  max={input.shape[axis] - 1}
                  value={positions[axis]}
                  onChange={(e) =>
                    setPositions((p) => p.map((v, a) => (a === axis ? Number(e.target.value) : v)))
                  }
                />
                <span>
                  RAS {['x', 'y', 'z'][axis]}=
                  {rasPoint(
                    input.affine,
                    positions.map((v, a) => (a === axis ? sampled : v)),
                  )[axis].toFixed(2)}{' '}
                  mm
                </span>
              </label>
            </div>
          );
        })}
      </div>
      {error && (
        <p className={styles.note} role="status">
          {error}. Retained poster remains source context; no generated slice is claimed available.
        </p>
      )}
    </section>
  );
}
