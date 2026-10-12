import { useEffect, useLayoutEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import type { MriTracePayload } from '../../contracts.generated';
import type { NativeStageProps } from './types';
import {
  bboxCells,
  boxEdges,
  cellSpans,
  nearestSample,
  planeCorners,
  rasPoint,
} from './mri-geometry';
import styles from './mri-trace.module.css';

type Drawing = {
  update: () => void;
  reset: () => void;
  dispose: () => void;
  committed: () => boolean;
};
const fmt = (p: number[]) => p.map((v) => v.toFixed(2)).join(', ');
const axisNames = ['Sagittal · i / R', 'Coronal · j / A', 'Axial · k / S'];

export function MriTraceStage({
  payload,
  stateId,
  chapterId,
  referenceShown,
  onReady,
}: NativeStageProps<MriTracePayload>) {
  const { input, observed } = payload;
  const state = observed.states.find((s) => s.id === stateId);
  const [visitId, setVisitId] = useState(input.visits[0].id);
  const visit = input.visits.find((v) => v.id === visitId) ?? input.visits[0];
  const [ordinal, setOrdinal] = useState(0);
  const series = visit.series.find((s) => s.ordinal === ordinal);
  const [axis, setAxis] = useState(2);
  const [positions, setPositions] = useState(visit.shape.map((s) => Math.floor(s / 2)));
  const [decoded, setDecoded] = useState<Uint8Array | null>(null);
  const [fallback, setFallback] = useState(false);
  const [error, setError] = useState('');
  const [ready, setReady] = useState(false);
  const [capture, setCapture] = useState(false);
  const host = useRef<HTMLDivElement>(null);
  const canvases = useRef<Array<HTMLCanvasElement | null>>([]);
  const decorated = useRef<HTMLCanvasElement>(null);
  const drawing = useRef<Drawing | null>(null);
  const callback = useRef(onReady);
  callback.current = onReady;
  const measurementVisible =
    chapterId === 'measurement' || chapterId === 'output' || chapterId === 'reference';
  const savedVisible = chapterId === 'output' || chapterId === 'reference';
  const inspection =
    state?.views.filter((v) => v.visit === visit.id && v.series_id === series?.id) ?? [];
  const recordedSeries = [
    ...new Set(state?.views.filter((v) => v.visit === visit.id).map((v) => v.series_id) ?? []),
  ];
  const measurement = measurementVisible
    ? observed.measurements.find((m) => m.visit === visit.id)
    : undefined;
  const citations = savedVisible ? observed.citations.filter((c) => c.visit === visit.id) : [];
  const delivered = payload.delivered_images.find((image) => image.step === state?.delivered_step);
  const current = useRef({ positions, inspection, measurement, citations, axis });
  current.current = { positions, inspection, measurement, citations, axis };
  useLayoutEffect(() => {
    setCapture(!!host.current?.closest('[data-explainer-export-frame]'));
  }, []);
  useEffect(() => {
    setVisitId(
      measurementVisible
        ? (input.visits[1]?.id ?? input.visits[0].id)
        : (state?.views[0]?.visit ?? input.visits[0].id),
    );
  }, [stateId, state, input.visits, measurementVisible]);
  useEffect(() => {
    const view = state?.views.find((v) => v.visit === visit.id);
    setOrdinal(
      visit.series.find((s) => s.id === (view?.series_id ?? measurement?.series_id))?.ordinal ?? 0,
    );
    const p = (
      view?.center_ijk ??
      (measurement
        ? measurement.bbox_min.map((v, a) => (v + measurement.bbox_max[a]) / 2)
        : undefined) ??
      view?.bounds?.[0].map((v, a) => (v + view.bounds![1][a]) / 2 - 0.5) ??
      visit.shape.map((s) => Math.floor(s / 2))
    ).slice();
    if (view?.axis !== null && view?.axis !== undefined && view.levels.length) {
      p[view.axis] = view.levels[0];
      setAxis(view.axis);
    }
    setPositions(p.map((v, a) => Math.max(0, Math.min(visit.shape[a] - 1, Math.round(v)))));
  }, [state, visit, measurement]);
  useEffect(() => {
    let cancelled = false;
    setDecoded(null);
    setReady(false);
    callback.current(false);
    setError('');
    if (!series) {
      setError('Selected ordinal unavailable for this visit');
      setFallback(true);
      return;
    }
    void Promise.resolve()
      .then(async () => {
        const zipped = Uint8Array.from(atob(series.volume), (c) => c.charCodeAt(0));
        const bytes = new Uint8Array(
          await new Response(
            new Blob([zipped]).stream().pipeThrough(new DecompressionStream('gzip')),
          ).arrayBuffer(),
        );
        if (bytes.length !== visit.preview_shape.reduce((a, b) => a * b, 1))
          throw Error('Native preview byte count mismatch');
        if (!cancelled) setDecoded(bytes);
      })
      .catch((e: unknown) => {
        if (!cancelled) {
          setFallback(true);
          setError(e instanceof Error ? e.message : 'Native preview unavailable');
        }
      });
    return () => {
      cancelled = true;
      callback.current(false);
    };
  }, [series, visit]);

  useEffect(() => {
    if (!decoded || !host.current) return;
    const element = host.current;
    let renderer: THREE.WebGLRenderer | null = null;
    let orbit: OrbitControls | null = null;
    let observer: ResizeObserver | null = null;
    const scene = new THREE.Scene(),
      overlays = new THREE.Group();
    scene.add(overlays);
    const textures: THREE.CanvasTexture[] = [];
    const centre = rasPoint(
      visit.affine,
      visit.shape.map((s) => (s - 1) / 2),
    );
    const world = (p: number[]) => {
      const r = rasPoint(visit.affine, p);
      return new THREE.Vector3(r[0] - centre[0], r[2] - centre[2], -(r[1] - centre[1]));
    };
    const disposeObjects = (group: THREE.Object3D) =>
      group.traverse((o) => {
        if (o instanceof THREE.Mesh || o instanceof THREE.Line) {
          o.geometry.dispose();
          (Array.isArray(o.material) ? o.material : [o.material]).forEach((m: THREE.Material) =>
            m.dispose(),
          );
        }
      });
    const clear = () => {
      disposeObjects(overlays);
      overlays.clear();
    };
    const dispose = () => {
      observer?.disconnect();
      orbit?.dispose();
      clear();
      disposeObjects(scene);
      textures.forEach((t) => t.dispose());
      renderer?.dispose();
      renderer?.domElement.remove();
    };
    try {
      if (new URLSearchParams(location.search).has('no3d')) throw Error('2D fallback requested');
      renderer = new THREE.WebGLRenderer({ antialias: true });
      renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5));
      renderer.setClearColor(0x111e28);
      renderer.outputColorSpace = THREE.SRGBColorSpace;
      element.append(renderer.domElement);
      const camera = new THREE.OrthographicCamera(-300, 300, 250, -250, 1, 3000);
      orbit = new OrbitControls(camera, renderer.domElement);
      orbit.enableDamping = false;
      orbit.enablePan = false;
      orbit.enabled = !element.closest('[data-explainer-export-frame]');
      const render = () => renderer!.render(scene, camera);
      orbit.addEventListener('change', render);
      const planes = [0, 1, 2].map((a) => {
        const texture = new THREE.CanvasTexture(canvases.current[a]!);
        texture.colorSpace = THREE.SRGBColorSpace;
        textures.push(texture);
        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute('uv', new THREE.Float32BufferAttribute([0, 1, 1, 1, 1, 0, 0, 0], 2));
        geometry.setIndex([0, 1, 2, 0, 2, 3]);
        const plane = new THREE.Mesh(
          geometry,
          new THREE.MeshBasicMaterial({
            map: texture,
            side: THREE.DoubleSide,
            transparent: true,
            opacity: 0.8,
          }),
        );
        scene.add(plane);
        return plane;
      });
      const lines = (points: number[][], color: number, dashed = false) => {
        const material = dashed
          ? new THREE.LineDashedMaterial({
              color,
              dashSize: 4,
              gapSize: 3,
              transparent: true,
              opacity: 1,
              depthTest: false,
              depthWrite: false,
            })
          : new THREE.LineBasicMaterial({
              color,
              transparent: true,
              opacity: 1,
              depthTest: false,
              depthWrite: false,
            });
        const line = new THREE.LineSegments(
          new THREE.BufferGeometry().setFromPoints(points.map(world)),
          material,
        );
        line.computeLineDistances();
        line.renderOrder = 30;
        overlays.add(line);
      };
      const cross = (p: number[], color: number) =>
        lines(
          [0, 1, 2].flatMap((a) => {
            const low = [...p],
              high = [...p];
            low[a] -= 5 / visit.spacing[a];
            high[a] += 5 / visit.spacing[a];
            return [low, high];
          }),
          color,
        );
      const update = () => {
        clear();
        const value = current.current;
        lines(boxEdges([[0, 0, 0], visit.shape]), 0x607a8b);
        planes.forEach((plane, a) => {
          const p =
            visit.preview_indices[a][nearestSample(visit.preview_indices[a], value.positions[a])];
          plane.geometry.setAttribute(
            'position',
            new THREE.Float32BufferAttribute(
              planeCorners(a, p, visit.shape).flatMap((p) => world(p).toArray()),
              3,
            ),
          );
          plane.geometry.computeBoundingSphere();
          textures[a].needsUpdate = true;
        });
        value.inspection.forEach((v) => {
          if (v.bounds) lines(boxEdges(v.bounds), 0x67d6ef);
          if (v.center_ijk) cross(v.center_ijk, 0x67d6ef);
          if (v.axis !== null)
            v.levels.forEach((k) => {
              const points = planeCorners(v.axis!, k, visit.shape);
              lines(
                points.flatMap((p, i) => [p, points[(i + 1) % 4]]),
                0x67d6ef,
              );
            });
        });
        if (value.measurement)
          lines(
            boxEdges(bboxCells(value.measurement.bbox_min, value.measurement.bbox_max)),
            0x31d1b6,
          );
        value.citations.forEach((c) => cross(c.ijk, 0xf0b36b));
        render();
      };
      const fit = () => {
        const w = element.clientWidth,
          h = element.clientHeight;
        if (!w || !h) return;
        renderer!.setSize(w, h);
        const extent = Math.max(...visit.shape.map((s, a) => s * visit.spacing[a])) * 0.72;
        const aspect = w / h;
        camera.left = -extent * Math.max(1, aspect);
        camera.right = -camera.left;
        camera.top = extent * Math.max(1, 1 / aspect);
        camera.bottom = -camera.top;
        camera.updateProjectionMatrix();
        render();
      };
      const reset = () => {
        camera.position.set(650, 420, 700);
        camera.zoom = 1;
        camera.updateProjectionMatrix();
        orbit!.target.set(0, 0, 0);
        orbit!.update();
        fit();
        update();
      };
      const key = (e: KeyboardEvent) => {
        if (element.closest('[data-explainer-export-frame]')) return;
        if (e.key === 'Home') {
          e.preventDefault();
          reset();
          return;
        }
        if (!['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(e.key)) return;
        e.preventDefault();
        const s = new THREE.Spherical().setFromVector3(camera.position);
        if (e.key === 'ArrowLeft') s.theta -= 0.12;
        if (e.key === 'ArrowRight') s.theta += 0.12;
        if (e.key === 'ArrowUp') s.phi = Math.max(0.1, s.phi - 0.12);
        if (e.key === 'ArrowDown') s.phi = Math.min(Math.PI - 0.1, s.phi + 0.12);
        camera.position.setFromSpherical(s);
        orbit!.update();
        update();
      };
      element.addEventListener('keydown', key);
      observer = new ResizeObserver(fit);
      observer.observe(element);
      drawing.current = {
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
      drawing.current = null;
      setFallback(true);
    }
    return () => {
      drawing.current?.dispose();
      drawing.current = null;
    };
  }, [decoded, visit]);

  useLayoutEffect(() => {
    if (!decoded) return;
    [0, 1, 2].forEach((a) => {
      const other = [0, 1, 2].filter((n) => n !== a),
        ha = other[0],
        va = other[1];
      const ratio = (visit.shape[ha] * visit.spacing[ha]) / (visit.shape[va] * visit.spacing[va]);
      const w = Math.round(260 * Math.min(1, ratio)),
        h = Math.round(260 / Math.max(1, ratio));
      const canvas = canvases.current[a],
        ctx = canvas?.getContext('2d');
      if (!canvas || !ctx) return;
      canvas.width = w;
      canvas.height = h;
      const pixels = ctx.createImageData(w, h);
      const sample = nearestSample(visit.preview_indices[a], positions[a]);
      for (let y = 0; y < h; y++)
        for (let x = 0; x < w; x++) {
          const p = [0, 0, 0];
          p[a] = sample;
          p[ha] = nearestSample(visit.preview_indices[ha], ((x + 0.5) * visit.shape[ha]) / w - 0.5);
          p[va] = nearestSample(
            visit.preview_indices[va],
            visit.shape[va] - 0.5 - ((y + 0.5) * visit.shape[va]) / h,
          );
          const g = decoded[(p[0] * visit.preview_shape[1] + p[1]) * visit.preview_shape[2] + p[2]];
          pixels.data.set([g, g, g, 255], (y * w + x) * 4);
        }
      ctx.putImageData(pixels, 0, 0);
      if (a !== axis || !decorated.current) return;
      const d = decorated.current;
      d.width = w;
      d.height = h;
      const dc = d.getContext('2d');
      if (!dc) return;
      dc.drawImage(canvas, 0, 0);
      const xy = (p: number[]) => [
        ((p[ha] + 0.5) / visit.shape[ha]) * w,
        ((visit.shape[va] - 0.5 - p[va]) / visit.shape[va]) * h,
      ];
      const rectangle = (bounds: number[][], color: string, dashed: boolean) => {
        const [x0, y0] = xy(bounds[0].map((v) => v - 0.5)),
          [x1, y1] = xy(bounds[1].map((v) => v - 0.5));
        dc.strokeStyle = color;
        dc.lineWidth = 1.7;
        dc.setLineDash(dashed ? [3, 2] : []);
        dc.strokeRect(x0, y1, x1 - x0, y0 - y1);
        dc.setLineDash([]);
      };
      const point = (p: number[], color: string) => {
        const [x, y] = xy(p);
        dc.strokeStyle = color;
        dc.lineWidth = 1.5;
        dc.beginPath();
        dc.moveTo(x - 5, y);
        dc.lineTo(x + 5, y);
        dc.moveTo(x, y - 5);
        dc.lineTo(x, y + 5);
        dc.stroke();
      };
      inspection.forEach((v) => {
        if (v.bounds) rectangle(v.bounds, '#67d6ef', false);
        if (v.center_ijk) point(v.center_ijk, '#67d6ef');
        if (v.axis !== null && v.axis !== axis)
          v.levels.forEach((k) => {
            const p = [...positions];
            p[v.axis!] = k;
            const [x, y] = xy(p);
            dc.strokeStyle = '#67d6ef';
            dc.beginPath();
            if (ha === v.axis) {
              dc.moveTo(x, 0);
              dc.lineTo(x, h);
            } else {
              dc.moveTo(0, y);
              dc.lineTo(w, y);
            }
            dc.stroke();
          });
      });
      const sampled = visit.preview_indices[a][sample];
      if (
        measurement &&
        sampled >= measurement.bbox_min[a] - 0.5 &&
        sampled <= measurement.bbox_max[a] + 0.5
      )
        rectangle(bboxCells(measurement.bbox_min, measurement.bbox_max), '#31d1b6', false);
      citations
        .filter((c) => nearestSample(visit.preview_indices[a], c.ijk[a]) === sample)
        .forEach((c) => point(c.ijk, '#f0b36b'));
    });
    drawing.current?.update();
  }, [decoded, visit, positions, axis, inspection, measurement, citations]);

  useEffect(() => {
    let cancelled = false,
      frame = 0;
    setReady(false);
    callback.current(false);
    if (!decoded && !error) return;
    const sources = [delivered?.src, fallback ? visit.poster : undefined].filter(
      (v): v is string => !!v,
    );
    void Promise.all(
      sources.map(
        (src) =>
          new Promise<void>((resolve, reject) => {
            const image = new Image();
            image.onload = () => {
              void image.decode().then(resolve, reject);
            };
            image.onerror = () => reject(Error('Retained image unavailable'));
            image.src = src;
          }),
      ),
    )
      .then(() => {
        frame = requestAnimationFrame(() => {
          if (cancelled) return;
          drawing.current?.update();
          if (drawing.current && !drawing.current.committed()) return;
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
    decoded,
    error,
    delivered,
    fallback,
    visit.poster,
    positions,
    axis,
    stateId,
    measurementVisible,
    savedVisible,
    referenceShown,
  ]);

  const sampled =
    visit.preview_indices[axis][nearestSample(visit.preview_indices[axis], positions[axis])];
  const spans = measurement
    ? cellSpans(bboxCells(measurement.bbox_min, measurement.bbox_max), visit.spacing)
    : [];
  return (
    <section
      className={styles.stage}
      data-native-ready={String(ready)}
      data-native-renderer={fallback ? 'poster' : 'webgl'}
      data-native-state={stateId ?? 'input'}
      data-reference-visible={String(referenceShown)}
      data-native-visit={visit.id}
      data-native-series={series?.id ?? ''}
      data-native-ordinal={ordinal}
      data-native-phase={0}
      data-native-shape={visit.shape.join(',')}
      data-native-affine={JSON.stringify(visit.affine)}
      data-native-axis={axis}
      data-native-slice={positions[axis]}
      data-native-sampled-index={sampled}
      data-native-sampled-ijk={positions
        .map((v, a) => visit.preview_indices[a][nearestSample(visit.preview_indices[a], v)])
        .join(',')}
      data-native-reader-ijk={positions.join(',')}
      data-native-reader-ras={rasPoint(visit.affine, positions).join(',')}
      data-native-inspection-count={inspection.length}
      data-native-bbox-visible={String(measurementVisible && !!measurement)}
      data-native-bbox-min={measurement?.bbox_min.join(',') ?? ''}
      data-native-bbox-max={measurement?.bbox_max.join(',') ?? ''}
      data-native-bbox-spans-mm={spans.join(',')}
      data-native-citation-count={citations.length}
      data-native-registered="false"
    >
      <div className={styles.inventory}>
        <strong>
          {input.inventory.length} supplied volumes ·{' '}
          {input.visits
            .map((v) => `${v.id}: ${input.inventory.filter((item) => item.visit === v.id).length}`)
            .join(' / ')}
        </strong>
        <span>
          16 selected dynamics · independent visit grids · disconnected scouts are separate files.
        </span>
      </div>
      <div className={styles.grid}>
        <div className={styles.card}>
          <header className={styles.heading}>
            <strong>Whole selected MRI volume</strong>
            <span>
              {visit.id} · day {visit.day} · {visit.shape.join(' × ')}
            </span>
          </header>
          <div className={styles.controls}>
            <label>
              Visit{' '}
              <select
                disabled={capture}
                aria-label="MRI visit"
                value={visit.id}
                onChange={(e) => setVisitId(e.target.value)}
              >
                {input.visits.map((v) => (
                  <option key={v.id} value={v.id}>
                    {v.id} · day {v.day}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Dynamic ordinal{' '}
              <select
                disabled={capture}
                aria-label="MRI dynamic ordinal"
                value={ordinal}
                onChange={(e) => setOrdinal(Number(e.target.value))}
              >
                {visit.series.map((s) => (
                  <option key={s.id} value={s.ordinal}>
                    {s.ordinal} · {s.id}
                  </option>
                ))}
              </select>
            </label>
            <span>Every file phase 0</span>
          </div>
          <div className={styles.sceneWrap}>
            <div
              ref={host}
              className={styles.scene}
              tabIndex={capture ? -1 : 0}
              role="img"
              aria-label={`${visit.id} whole MRI in its native RAS grid. Arrow keys orbit; Home resets.`}
            />
            {fallback && (
              <div className={styles.poster}>
                <img
                  src={visit.poster}
                  alt={`${visit.id} supplied whole-volume MRI context poster`}
                />
                <span>3D unavailable · native MPR remains available when decoded</span>
              </div>
            )}
            {!decoded && !fallback && (
              <p className={styles.loading}>Decoding selected native MRI preview…</p>
            )}
          </div>
          <div className={styles.legend}>
            <span className={styles.readerKey}>Reader MPR</span>
            {inspection.length > 0 && (
              <span className={styles.inspectionKey}>Logged inspection</span>
            )}
            {measurement && <span className={styles.bboxKey}>Saved bbox extent</span>}
            {savedVisible && <span className={styles.citationKey}>Saved citation</span>}
          </div>
          <p className={styles.note}>
            Visit window {visit.preview_window.map((v) => Number(v.toFixed(1))).join('–')} ·
            uncalibrated MRI signal. Native scale; visits are not registered.
          </p>
          <button
            className={styles.reset}
            type="button"
            disabled={capture || fallback}
            onClick={() => drawing.current?.reset()}
          >
            Reset orbit · arrows / Home
          </button>
        </div>
        <div className={`${styles.card} ${styles.operation}`}>
          <header className={styles.heading}>
            <strong>{state?.label ?? 'Receive independent visit volumes'}</strong>
            <span>{state ? `Recorded step ${state.trace_step}` : 'Input inventory'}</span>
          </header>
          <p className={styles.description}>{state?.description}</p>
          {recordedSeries.length > 1 && (
            <p className={styles.note}>
              Recorded for {visit.id}: {recordedSeries.join(', ')}.
            </p>
          )}
          {recordedSeries.length > 0 && inspection.length === 0 && (
            <p className={styles.note}>
              This ordinal has no recorded inspection in this state; the native MPR is a reader
              selection.
            </p>
          )}
          {delivered && (
            <figure className={styles.delivered}>
              <a href={delivered.src} target="_blank" rel="noreferrer" tabIndex={capture ? -1 : 0}>
                <img
                  src={delivered.src}
                  alt={`Exact delivered MRI PNG at step ${delivered.step}`}
                />
              </a>
              <figcaption>
                Exact delivered PNG · step {delivered.step} · click to inspect. Reader MPR below is
                separate.
                {delivered.step === 18 && (
                  <strong>
                    {' '}
                    Original labels predate step-20 laterality correction; pixels unchanged.
                  </strong>
                )}
              </figcaption>
            </figure>
          )}
          {(!capture || !savedVisible) &&
            inspection.map((v, n) => (
              <div className={styles.readout} key={n}>
                <strong>
                  {v.visit} · logged {v.series_id}
                </strong>
                {v.center_ijk && (
                  <>
                    <code>
                      {savedVisible ? 'Saved citation native' : 'Focus native'} [{fmt(v.center_ijk)}
                      ]
                    </code>
                    <code>RAS [{fmt(rasPoint(visit.affine, v.center_ijk))}] mm</code>
                  </>
                )}
                {v.bounds && (
                  <code>
                    Inspection cells [{v.bounds[0].join(',')}] → [{v.bounds[1].join(',')})
                  </code>
                )}
                {v.levels.length > 0 && (
                  <span>
                    Logged {['i', 'j', 'k'][v.axis ?? 2]} planes: {v.levels.join(', ')}
                  </span>
                )}
              </div>
            ))}
          {measurement && (
            <div className={styles.measurement}>
              <strong>
                {visit.id} {measurement.series_id} saved 30% component bbox · not a mask
              </strong>
              <code>
                Inclusive [{measurement.bbox_min.join(',')}]..[{measurement.bbox_max.join(',')}]
              </code>
              <span>Voxel-edge spans {spans.map((v) => v.toFixed(3)).join(' × ')} mm</span>
              <span>
                Maximum {Math.max(...spans).toFixed(3)} mm · reported {measurement.reported_mm} mm
              </span>
              <span className={styles.comparison}>
                {observed.measurements
                  .map((m) => {
                    const frame = input.visits.find((v) => v.id === m.visit);
                    const size = frame
                      ? Math.max(...cellSpans(bboxCells(m.bbox_min, m.bbox_max), frame.spacing))
                      : m.diameter_mm;
                    return `${m.visit} ${size.toFixed(3)} mm`;
                  })
                  .join(' / ')}{' '}
                · separate native-grid extents
              </span>
            </div>
          )}
          {savedVisible && (
            <div className={styles.saved}>
              {citations.map((c, n) => (
                <div key={n}>
                  <strong>
                    {c.series_id} · phase {c.phase} · citation
                  </strong>
                  <code>
                    [{c.ijk.join(',')}] · RAS [{fmt(rasPoint(visit.affine, c.ijk))}] mm
                  </code>
                </div>
              ))}
              <p>
                Retained forecast: {observed.forecast.direction} · confidence{' '}
                {observed.forecast.confidence}. Solver claim; no clinical endorsement.
              </p>
              <details>
                <summary>Retained account and evidence</summary>
                <p>{observed.summary}</p>
                <p>{observed.impression}</p>
                <p>{observed.forecast.basis}</p>
                <pre>{observed.evidence}</pre>
              </details>
            </div>
          )}
          {referenceShown && (
            <p className={styles.reference}>
              Existing audit component spans:{' '}
              {payload.reference.audit_diameters_mm.map((v) => v.toFixed(3)).join(' → ')} mm (
              {payload.reference.audit_change_percent.toFixed(2)}%). Source diameter units:{' '}
              {payload.reference.diameter_unit}. Clinical accuracy:{' '}
              {payload.reference.clinical_accuracy}.
            </p>
          )}
          {chapterId === 'input' && (
            <details className={styles.fullInventory}>
              <summary>Inspect all {input.inventory.length} supplied volume records</summary>
              <ul>
                {input.inventory.map((item) => (
                  <li key={`${item.visit}/${item.id}`}>
                    <strong>
                      {item.visit} / {item.id}
                    </strong>{' '}
                    · {item.description} · {item.shape.join('×')} · {item.phase_count} phase(s)
                    <code>RAS affine {item.affine.map((r) => r.join(', ')).join(' / ')}</code>
                  </li>
                ))}
              </ul>
            </details>
          )}
        </div>
        <div className={styles.card}>
          <header className={styles.heading}>
            <strong>{axisNames[axis]}</strong>
            <span>Reader-generated MPR</span>
          </header>
          <div className={styles.slice}>
            <canvas
              ref={decorated}
              aria-label={`${visit.id} ${series?.id ?? 'unavailable'} native MRI slice`}
            />
            {[0, 1, 2].map((a) => (
              <canvas
                key={a}
                hidden
                ref={(node) => {
                  canvases.current[a] = node;
                }}
              />
            ))}
          </div>
          <label className={styles.axis}>
            Native axis{' '}
            <select
              disabled={capture}
              aria-label="MRI native slice axis"
              value={axis}
              onChange={(e) => setAxis(Number(e.target.value))}
            >
              {axisNames.map((n, a) => (
                <option key={a} value={a}>
                  {n}
                </option>
              ))}
            </select>
          </label>
          <label className={styles.slider}>
            Requested {['i', 'j', 'k'][axis]}={positions[axis]} · sampled {sampled}
            <input
              disabled={capture}
              aria-label="MRI native slice index"
              type="range"
              min={0}
              max={visit.shape[axis] - 1}
              value={positions[axis]}
              onChange={(e) =>
                setPositions((p) => p.map((v, a) => (a === axis ? Number(e.target.value) : v)))
              }
            />
            <span>
              RAS [
              {fmt(
                rasPoint(
                  visit.affine,
                  positions.map((v, a) => (a === axis ? sampled : v)),
                ),
              )}
              ] mm
            </span>
          </label>
          {!capture && inspection.some((v) => v.levels.length) && (
            <label className={styles.axis}>
              Logged plane{' '}
              <select
                disabled={capture}
                aria-label="MRI recorded inspection plane"
                value={
                  inspection.flatMap((v) => v.levels).includes(positions[axis])
                    ? positions[axis]
                    : ''
                }
                onChange={(e) =>
                  setPositions((p) => p.map((v, a) => (a === axis ? Number(e.target.value) : v)))
                }
              >
                <option value="" disabled>
                  Reader selection
                </option>
                {inspection
                  .filter((v) => v.axis === axis)
                  .flatMap((v) => v.levels)
                  .map((k) => (
                    <option key={k} value={k}>
                      {k}
                    </option>
                  ))}
              </select>
            </label>
          )}
        </div>
      </div>
      {error && (
        <p className={styles.error} role="status">
          {error}. Retained poster is context only; unavailable preview slices are not
          reconstructed.
        </p>
      )}
    </section>
  );
}
