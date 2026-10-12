import { useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import type { CoronaryTracePayload } from '../../contracts.generated';
import type { NativeStageProps } from './types';
import {
  boundaryIndices,
  boxEdges,
  cprPixelIndex,
  fromFlat,
  inCrop,
  nativePoint,
  nearestSample,
  planeCorners,
  rasPoint,
} from './coronary-geometry';
import styles from './coronary-trace.module.css';

type Decoded = {
  volume: Uint8Array;
  detail: Uint8Array;
  hu: Float32Array;
  source: Float32Array;
  vertices: Float32Array;
  faces: Uint32Array;
};
type Drawing = {
  update: () => void;
  reset: () => void;
  dispose: () => void;
  committed: () => boolean;
};
const fmt = (p: number[]) => p.map((v) => v.toFixed(3)).join(', ');
const axes = ['Sagittal · i / L', 'Coronal · j / A', 'Axial · k / S'];
async function unpack(encoded: string): Promise<ArrayBuffer> {
  const bytes = Uint8Array.from(atob(encoded), (c) => c.charCodeAt(0));
  return new Response(
    new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip')),
  ).arrayBuffer();
}

export function CoronaryTraceStage({
  payload,
  stateId,
  chapterId,
  referenceShown,
  onReady,
}: NativeStageProps<CoronaryTracePayload>) {
  const { input, observed, reference } = payload;
  const [inspectionId, setInspectionId] = useState(stateId);
  const state = observed.states.find((s) => s.id === (inspectionId ?? stateId));
  const [axis, setAxis] = useState(2);
  const [localDetail, setLocalDetail] = useState(false);
  const [positions, setPositions] = useState(input.shape.map((s) => Math.floor(s / 2)));
  const [angle, setAngle] = useState(0),
    [column, setColumn] = useState(0),
    [offset, setOffset] = useState(32);
  const [decoded, setDecoded] = useState<Decoded | null>(null);
  const [fallback, setFallback] = useState(false),
    [ready, setReady] = useState(false),
    [capture, setCapture] = useState(false);
  const [error, setError] = useState('');
  const host = useRef<HTMLDivElement>(null),
    slice = useRef<HTMLCanvasElement>(null),
    cpr = useRef<HTMLCanvasElement>(null);
  const sources = useRef<Array<HTMLCanvasElement | null>>([]);
  const drawing = useRef<Drawing | null>(null),
    callback = useRef(onReady);
  callback.current = onReady;
  const saved = ['route', 'cpr', 'output', 'reference'].includes(chapterId);
  const cprVisible = ['cpr', 'output', 'reference'].includes(chapterId);
  const meshVisible = ['output', 'reference'].includes(chapterId);
  const bridgeVisible = (chapterId === 'contacts' && (state?.trace_step ?? 0) >= 38) || saved;
  const pixel = cprPixelIndex(observed.cpr.shape, angle, column, offset);
  const sourceRas =
    decoded && cprVisible ? Array.from(decoded.source.subarray(pixel * 3, pixel * 3 + 3)) : null;
  const sourceNative = sourceRas ? nativePoint(input.affine, sourceRas) : null;
  const delivered = payload.delivered_images.find((image) => image.step === state?.delivered_step);
  const inspectOptions =
    chapterId === 'search' ? observed.states.filter((s) => s.kind === 'planes') : [];
  const mask = useMemo(() => new Set(input.mask_indices), [input]);
  const editable = useMemo(() => new Set(input.editable_indices), [input]);
  const additions = useMemo(() => new Set(observed.added_indices), [observed]);
  const removed = useMemo(() => new Set(observed.removed_indices), [observed]);
  const current = useRef({
    state,
    positions,
    saved,
    bridgeVisible,
    meshVisible,
    cprVisible,
    sourceRas,
    localDetail,
    angle,
    column,
  });
  current.current = {
    state,
    positions,
    saved,
    bridgeVisible,
    meshVisible,
    cprVisible,
    sourceRas,
    localDetail,
    angle,
    column,
  };
  useLayoutEffect(() => {
    setCapture(!!host.current?.closest('[data-explainer-export-frame]'));
  }, []);
  useEffect(() => {
    setInspectionId(stateId);
    setLocalDetail(['search', 'contacts', 'route'].includes(chapterId));
    setAngle(0);
    setColumn(0);
    setOffset(Math.floor(observed.cpr.shape[2] / 2));
  }, [stateId, chapterId, observed.cpr.shape]);
  useEffect(() => {
    const p = (
      state?.center_ijk ??
      (chapterId === 'route' ? nativePoint(input.affine, input.review_ras) : undefined) ??
      (state?.bounds
        ? state.bounds[0].map((v, a) => (v + state.bounds![1][a]) / 2 - 0.5)
        : undefined) ??
      input.shape.map((s) => Math.floor(s / 2))
    ).slice();
    if (state?.axis !== null && state?.axis !== undefined && state.levels.length) {
      p[state.axis] = state.levels[0];
      setAxis(state.axis);
    }
    setPositions(p.map((v, a) => Math.max(0, Math.min(input.shape[a] - 1, Math.round(v)))));
  }, [state, input, chapterId]);
  useEffect(() => {
    if (localDetail)
      setPositions((p) =>
        p.map((v, a) =>
          Math.max(
            input.detail_origin[a],
            Math.min(input.detail_origin[a] + input.detail_shape[a] - 1, v),
          ),
        ),
      );
  }, [localDetail, input]);
  // Reader CPR navigation links retained source coordinates; it does not rerun sampling.
  useEffect(() => {
    if (!decoded || !cprVisible) return;
    const p = nativePoint(
      input.affine,
      Array.from(decoded.source.subarray(pixel * 3, pixel * 3 + 3)),
    );
    if (inCrop(p, input.shape))
      setPositions(p.map((v, a) => Math.max(0, Math.min(input.shape[a] - 1, Math.round(v)))));
  }, [decoded, cprVisible, pixel, input]);
  useEffect(() => {
    let cancelled = false;
    setDecoded(null);
    setReady(false);
    setError('');
    callback.current(false);
    void Promise.all([
      unpack(input.volume),
      unpack(input.detail_volume),
      unpack(observed.cpr.hu),
      unpack(observed.cpr.source_ras_mm),
      unpack(observed.mesh.vertices),
      unpack(observed.mesh.faces),
    ])
      .then(([v, detail, h, s, m, f]) => {
        if (cancelled) return;
        const result = {
          volume: new Uint8Array(v),
          detail: new Uint8Array(detail),
          hu: new Float32Array(h),
          source: new Float32Array(s),
          vertices: new Float32Array(m),
          faces: new Uint32Array(f),
        };
        const count = observed.cpr.shape.reduce((a, b) => a * b, 1);
        if (
          result.volume.length !== input.preview_shape.reduce((a, b) => a * b, 1) ||
          result.detail.length !== input.detail_shape.reduce((a, b) => a * b, 1) ||
          result.hu.length !== count ||
          result.source.length !== count * 3 ||
          result.vertices.length !== observed.mesh.vertex_count * 3 ||
          result.faces.length !== observed.mesh.face_count * 3
        )
          throw Error('Retained array dimensions mismatch');
        setDecoded(result);
      })
      .catch((e: unknown) => {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : 'Retained arrays unavailable');
          setFallback(true);
        }
      });
    return () => {
      cancelled = true;
      callback.current(false);
    };
  }, [input, observed]);

  useEffect(() => {
    if (!decoded || !host.current) return;
    const element = host.current;
    let renderer: THREE.WebGLRenderer | null = null,
      orbit: OrbitControls | null = null,
      observer: ResizeObserver | null = null;
    const scene = new THREE.Scene(),
      dynamic = new THREE.Group();
    scene.add(dynamic);
    const textures: THREE.CanvasTexture[] = [];
    const centre = rasPoint(
      input.affine,
      input.shape.map((s) => (s - 1) / 2),
    );
    const rasScene = (p: number[]) =>
      new THREE.Vector3(p[0] - centre[0], p[2] - centre[2], -(p[1] - centre[1]));
    const nativeScene = (p: number[]) => rasScene(rasPoint(input.affine, p));
    const disposeObjects = (group: THREE.Object3D) =>
      group.traverse((o) => {
        if (o instanceof THREE.Mesh || o instanceof THREE.Line) {
          o.geometry.dispose();
          (Array.isArray(o.material) ? o.material : [o.material]).forEach((m: THREE.Material) =>
            m.dispose(),
          );
          if (o instanceof THREE.InstancedMesh) o.dispose();
        }
      });
    const clear = () => {
      disposeObjects(dynamic);
      dynamic.clear();
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
      if (new URLSearchParams(location.search).has('no3d')) throw Error('2D context requested');
      renderer = new THREE.WebGLRenderer({ antialias: true });
      renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5));
      renderer.setClearColor(0x111e28);
      renderer.outputColorSpace = THREE.SRGBColorSpace;
      element.append(renderer.domElement);
      const camera = new THREE.OrthographicCamera(-120, 120, 120, -120, 0.1, 2000);
      orbit = new OrbitControls(camera, renderer.domElement);
      orbit.enableDamping = false;
      orbit.enablePan = false;
      orbit.enabled = !element.closest('[data-explainer-export-frame]');
      const render = () => renderer!.render(scene, camera);
      orbit.addEventListener('change', render);
      const planes = [0, 1, 2].map((a) => {
        const texture = new THREE.CanvasTexture(sources.current[a]!);
        texture.colorSpace = THREE.SRGBColorSpace;
        textures.push(texture);
        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute('uv', new THREE.Float32BufferAttribute([0, 1, 1, 1, 1, 0, 0, 0], 2));
        geometry.setIndex([0, 1, 2, 0, 2, 3]);
        const mesh = new THREE.Mesh(
          geometry,
          new THREE.MeshBasicMaterial({
            map: texture,
            side: THREE.DoubleSide,
            transparent: true,
            opacity: 0.55,
            depthWrite: false,
          }),
        );
        scene.add(mesh);
        return mesh;
      });
      const basis = new THREE.Matrix4().set(
        input.affine[0][0],
        input.affine[0][1],
        input.affine[0][2],
        0,
        input.affine[2][0],
        input.affine[2][1],
        input.affine[2][2],
        0,
        -input.affine[1][0],
        -input.affine[1][1],
        -input.affine[1][2],
        0,
        0,
        0,
        0,
        1,
      );
      const voxels = (indices: number[], color: number, opacity: number) => {
        const mesh = new THREE.InstancedMesh(
          new THREE.BoxGeometry(1, 1, 1),
          new THREE.MeshBasicMaterial({
            color,
            transparent: opacity < 1,
            opacity,
            depthWrite: opacity === 1,
            side: THREE.DoubleSide,
          }),
          indices.length,
        );
        indices.forEach((flat, n) => {
          const matrix = basis.clone();
          matrix.setPosition(nativeScene(fromFlat(flat, input.shape)));
          mesh.setMatrixAt(n, matrix);
        });
        mesh.instanceMatrix.needsUpdate = true;
        scene.add(mesh);
        return mesh;
      };
      const proposed = voxels(input.mask_indices, 0xff2828, 0.5);
      const editableBoundary = voxels(
        boundaryIndices(input.editable_indices, input.shape),
        0x45b85f,
        0.16,
      );
      const added = voxels(observed.added_indices, 0x31d1b6, 1),
        removedMesh = voxels(observed.removed_indices, 0xdb5ba9, 1);
      added.visible = removedMesh.visible = false;
      for (const voxels of [added, removedMesh]) {
        const material = voxels.material as THREE.MeshBasicMaterial;
        material.transparent = true;
        material.depthWrite = false;
        material.depthTest = false;
        voxels.renderOrder = 40;
      }
      const vertices = new Float32Array(decoded.vertices.length);
      for (let n = 0; n < vertices.length; n += 3)
        rasScene(Array.from(decoded.vertices.subarray(n, n + 3))).toArray(vertices, n);
      const geometry = new THREE.BufferGeometry();
      geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
      geometry.setIndex(new THREE.BufferAttribute(decoded.faces, 1));
      geometry.computeVertexNormals();
      const mesh = new THREE.Mesh(
        geometry,
        new THREE.MeshPhongMaterial({
          color: 0xb9cbd2,
          side: THREE.DoubleSide,
          transparent: true,
          opacity: 0.65,
          shininess: 30,
        }),
      );
      mesh.visible = false;
      scene.add(mesh, new THREE.AmbientLight(0xffffff, 2));
      const light = new THREE.DirectionalLight(0xffffff, 2);
      light.position.set(80, 160, 120);
      scene.add(light);
      const segments = (points: THREE.Vector3[], color: number, dashed = false) => {
        const line = new THREE.LineSegments(
          new THREE.BufferGeometry().setFromPoints(points),
          dashed
            ? new THREE.LineDashedMaterial({
                color,
                dashSize: 2,
                gapSize: 1,
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
              }),
        );
        line.computeLineDistances();
        line.renderOrder = 40;
        dynamic.add(line);
      };
      const path = (points: number[][], color: number, native: boolean) => {
        const line = new THREE.Line(
          new THREE.BufferGeometry().setFromPoints(points.map(native ? nativeScene : rasScene)),
          new THREE.LineBasicMaterial({
            color,
            transparent: true,
            opacity: 1,
            depthTest: false,
            depthWrite: false,
          }),
        );
        line.renderOrder = 45;
        dynamic.add(line);
      };
      const pin = (p: number[], color: number) => {
        const pos = rasScene(p),
          size = 2;
        segments(
          [
            new THREE.Vector3(pos.x - size, pos.y, pos.z),
            new THREE.Vector3(pos.x + size, pos.y, pos.z),
            new THREE.Vector3(pos.x, pos.y - size, pos.z),
            new THREE.Vector3(pos.x, pos.y + size, pos.z),
          ],
          color,
        );
      };
      const update = () => {
        clear();
        const value = current.current;
        segments(boxEdges([[0, 0, 0], input.shape]).map(nativeScene), 0x65818f);
        planes.forEach((p, a) => {
          const sampled =
            input.preview_indices[a][nearestSample(input.preview_indices[a], value.positions[a])];
          p.geometry.setAttribute(
            'position',
            new THREE.Float32BufferAttribute(
              planeCorners(a, sampled, input.shape).flatMap((p) => nativeScene(p).toArray()),
              3,
            ),
          );
          p.geometry.computeBoundingSphere();
          textures[a].needsUpdate = true;
        });
        if (value.localDetail)
          segments(
            boxEdges([
              input.detail_origin,
              input.detail_origin.map((v, a) => v + input.detail_shape[a]),
            ]).map(nativeScene),
            0x549ccc,
            true,
          );
        if (value.state?.bounds) segments(boxEdges(value.state.bounds).map(nativeScene), 0x67d6ef);
        if (value.state?.axis !== null && value.state?.axis !== undefined)
          value.state.levels.forEach((k) => {
            const points = planeCorners(value.state!.axis!, k, input.shape);
            segments(
              points.flatMap((p, n) => [nativeScene(p), nativeScene(points[(n + 1) % 4])]),
              0x67d6ef,
            );
          });
        if (value.state?.center_ijk) pin(rasPoint(input.affine, value.state.center_ijk), 0x67d6ef);
        pin(input.start_ras, 0xf4df82);
        pin(input.end_ras, 0xf4df82);
        pin(input.review_ras, 0x45b85f);
        if (value.bridgeVisible) path(observed.bridge_ijk, 0xd592ee, true);
        if (value.saved) path(observed.centerline_ras, 0x31d1b6, false);
        if (value.cprVisible && !value.meshVisible) {
          const [, rows, offsets] = observed.cpr.shape;
          const sourcePoint = (row: number, offset: number) => {
            const q = cprPixelIndex(observed.cpr.shape, value.angle, row, offset) * 3;
            return Array.from(decoded.source.subarray(q, q + 3));
          };
          // Retained curved-plane coordinates, not a new sample or synthetic unfolding.
          path(
            Array.from({ length: rows }, (_, row) => sourcePoint(row, 0)),
            0xf5bc62,
            false,
          );
          path(
            Array.from({ length: rows }, (_, row) => sourcePoint(row, offsets - 1)),
            0xf5bc62,
            false,
          );
          path(
            Array.from({ length: offsets }, (_, offset) => sourcePoint(value.column, offset)),
            0xf5bc62,
            false,
          );
        }
        if (
          value.cprVisible &&
          value.sourceRas &&
          inCrop(nativePoint(input.affine, value.sourceRas), input.shape)
        )
          pin(value.sourceRas, 0xf5bc62);
        added.visible = removedMesh.visible = value.saved;
        mesh.visible = value.meshVisible;
        proposed.visible = !value.meshVisible;
        editableBoundary.visible = true;
        render();
      };
      const fit = () => {
        const w = element.clientWidth,
          h = element.clientHeight;
        if (!w || !h) return;
        renderer!.setSize(w, h);
        const extent = Math.max(...input.shape.map((s, a) => s * input.spacing[a])) * 0.69,
          aspect = w / h;
        camera.left = -extent * Math.max(1, aspect);
        camera.right = -camera.left;
        camera.top = extent * Math.max(1, 1 / aspect);
        camera.bottom = -camera.top;
        camera.updateProjectionMatrix();
        render();
      };
      const reset = () => {
        camera.position.set(230, 170, 260);
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
  }, [decoded, input, observed]);

  useLayoutEffect(() => {
    if (!decoded) return;
    [0, 1, 2].forEach((a) => {
      const other = [0, 1, 2].filter((n) => n !== a),
        ha = other[0],
        va = other[1];
      const ratio = (input.shape[ha] * input.spacing[ha]) / (input.shape[va] * input.spacing[va]);
      const w = Math.round(280 * Math.min(1, ratio)),
        h = Math.round(280 / Math.max(1, ratio));
      const canvas = sources.current[a],
        ctx = canvas?.getContext('2d');
      if (!canvas || !ctx) return;
      canvas.width = w;
      canvas.height = h;
      const image = ctx.createImageData(w, h),
        sample = nearestSample(input.preview_indices[a], positions[a]);
      for (let y = 0; y < h; y++)
        for (let x = 0; x < w; x++) {
          const p = [0, 0, 0];
          p[a] = sample;
          p[ha] = nearestSample(input.preview_indices[ha], ((x + 0.5) * input.shape[ha]) / w - 0.5);
          p[va] = nearestSample(
            input.preview_indices[va],
            input.shape[va] - 0.5 - ((y + 0.5) * input.shape[va]) / h,
          );
          const g =
            decoded.volume[(p[0] * input.preview_shape[1] + p[1]) * input.preview_shape[2] + p[2]];
          image.data.set([g, g, g, 255], (y * w + x) * 4);
        }
      ctx.putImageData(image, 0, 0);
      if (a !== axis || !slice.current) return;
      const d = slice.current;
      const sideShape = localDetail ? input.detail_shape : input.shape;
      const sideOrigin = localDetail ? input.detail_origin : [0, 0, 0];
      const sideRatio = (sideShape[ha] * input.spacing[ha]) / (sideShape[va] * input.spacing[va]);
      const dw = Math.round(280 * Math.min(1, sideRatio)),
        dh = Math.round(280 / Math.max(1, sideRatio));
      d.width = dw;
      d.height = dh;
      const dc = d.getContext('2d');
      if (!dc) return;
      const sampled = localDetail
        ? Math.max(sideOrigin[a], Math.min(sideOrigin[a] + sideShape[a] - 1, positions[a]))
        : input.preview_indices[a][sample];
      const nativePixel = (x: number, y: number) => {
        const p = [0, 0, 0];
        p[a] = sampled;
        p[ha] =
          sideOrigin[ha] +
          Math.min(sideShape[ha] - 1, Math.floor(((x + 0.5) * sideShape[ha]) / dw));
        p[va] =
          sideOrigin[va] +
          Math.max(0, Math.floor(sideShape[va] - ((y + 0.5) * sideShape[va]) / dh));
        return p;
      };
      if (localDetail) {
        const pixels = dc.createImageData(dw, dh);
        for (let y = 0; y < dh; y++)
          for (let x = 0; x < dw; x++) {
            const p = nativePixel(x, y).map((v, a) => v - sideOrigin[a]);
            const g = decoded.detail[(p[0] * sideShape[1] + p[1]) * sideShape[2] + p[2]];
            pixels.data.set([g, g, g, 255], (y * dw + x) * 4);
          }
        dc.putImageData(pixels, 0, 0);
      } else dc.drawImage(canvas, 0, 0, dw, dh);
      const xy = (p: number[]) => [
        ((p[ha] - sideOrigin[ha] + 0.5) / sideShape[ha]) * dw,
        ((sideOrigin[va] + sideShape[va] - 0.5 - p[va]) / sideShape[va]) * dh,
      ];
      // Exact native binary membership at the displayed plane, with no invented repair states.
      for (let y = 0; y < dh; y++)
        for (let x = 0; x < dw; x++) {
          const p = nativePixel(x, y);
          const flat = (p[0] * input.shape[1] + p[1]) * input.shape[2] + p[2];
          let color = mask.has(flat) ? '#ff2828' : editable.has(flat) ? '#45b85f' : null;
          if (saved && removed.has(flat)) color = '#db5ba9';
          if (saved && additions.has(flat)) color = '#31d1b6';
          if (color) {
            dc.globalAlpha = color === '#45b85f' ? 0.2 : color === '#ff2828' ? 0.65 : 1;
            dc.fillStyle = color;
            dc.fillRect(x, y, 1, 1);
          }
        }
      dc.globalAlpha = 1;
      if (bridgeVisible)
        for (const p of observed.bridge_ijk) {
          if (Math.abs(p[a] - sampled) > 0.5) continue;
          const [x, y] = xy(p);
          dc.fillStyle = '#d592ee';
          dc.fillRect(x - 1.5, y - 1.5, 3, 3);
        }
      const cross = (p: number[], color: string) => {
        const [x, y] = xy(p);
        dc.strokeStyle = color;
        dc.lineWidth = 1.6;
        dc.beginPath();
        dc.moveTo(x - 4, y);
        dc.lineTo(x + 4, y);
        dc.moveTo(x, y - 4);
        dc.lineTo(x, y + 4);
        dc.stroke();
      };
      if (state?.bounds) {
        const [x0, y0] = xy(state.bounds[0].map((v) => v - 0.5)),
          [x1, y1] = xy(state.bounds[1].map((v) => v - 0.5));
        dc.strokeStyle = '#67d6ef';
        dc.lineWidth = 1.5;
        dc.strokeRect(x0, y1, x1 - x0, y0 - y1);
      }
      if (state?.center_ijk) cross(state.center_ijk, '#67d6ef');
      if (state?.axis !== null && state?.axis !== undefined && state.axis !== axis)
        state.levels.forEach((k) => {
          const p = [...positions];
          p[state.axis!] = k;
          const [x, y] = xy(p);
          dc.strokeStyle = '#67d6ef';
          dc.lineWidth = 0.5;
          dc.beginPath();
          if (state.axis === ha) {
            dc.moveTo(x, 0);
            dc.lineTo(x, dh);
          } else {
            dc.moveTo(0, y);
            dc.lineTo(dw, y);
          }
          dc.stroke();
        });
      if (saved) {
        dc.strokeStyle = '#31d1b6';
        dc.lineWidth = 1.5;
        const points = observed.centerline_ras.map((p) => nativePoint(input.affine, p));
        for (let n = 1; n < points.length; n++) {
          if (
            Math.abs(points[n][a] - sampled) >
            (localDetail ? 0.5 : input.shape[a] / input.preview_shape[a] / 2)
          )
            continue;
          const [x0, y0] = xy(points[n - 1]),
            [x1, y1] = xy(points[n]);
          dc.beginPath();
          dc.moveTo(x0, y0);
          dc.lineTo(x1, y1);
          dc.stroke();
        }
      }
      if (sourceNative && inCrop(sourceNative, input.shape)) cross(sourceNative, '#f5bc62');
    });
    if (cprVisible && cpr.current) {
      const canvas = cpr.current,
        ctx = canvas.getContext('2d');
      if (ctx) {
        const [, columns, offsets] = observed.cpr.shape;
        canvas.width = columns;
        canvas.height = offsets;
        const image = ctx.createImageData(columns, offsets),
          [low, high] = input.preview_window;
        for (let y = 0; y < offsets; y++)
          for (let x = 0; x < columns; x++) {
            const value = decoded.hu[cprPixelIndex(observed.cpr.shape, angle, x, offsets - 1 - y)],
              g = Math.max(0, Math.min(255, Math.round(((value - low) * 255) / (high - low))));
            image.data.set([g, g, g, 255], (y * columns + x) * 4);
          }
        ctx.putImageData(image, 0, 0);
        ctx.strokeStyle = '#f5bc62';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(column + 0.5, 0);
        ctx.lineTo(column + 0.5, offsets);
        ctx.moveTo(0, offsets - 1 - offset + 0.5);
        ctx.lineTo(columns, offsets - 1 - offset + 0.5);
        ctx.stroke();
      }
    }
    drawing.current?.update();
  }, [
    decoded,
    input,
    observed,
    localDetail,
    bridgeVisible,
    positions,
    axis,
    state,
    mask,
    editable,
    additions,
    removed,
    saved,
    cprVisible,
    angle,
    column,
    offset,
    pixel,
  ]);

  useEffect(() => {
    let cancelled = false,
      frame = 0;
    setReady(false);
    callback.current(false);
    if (!decoded && !error) return;
    const imageSources = [delivered?.src, fallback ? input.poster : undefined].filter(
      (s): s is string => !!s,
    );
    void Promise.all(
      imageSources.map(
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
    input.poster,
    state,
    positions,
    axis,
    saved,
    meshVisible,
    cprVisible,
    angle,
    column,
    offset,
    referenceShown,
    localDetail,
  ]);
  const sampled = localDetail
    ? positions[axis]
    : input.preview_indices[axis][nearestSample(input.preview_indices[axis], positions[axis])];
  return (
    <section
      className={styles.stage}
      data-native-ready={String(ready)}
      data-native-renderer={fallback ? 'poster' : 'webgl'}
      data-native-state={state?.id ?? 'input'}
      data-reference-visible={String(referenceShown)}
      data-native-shape={input.shape.join(',')}
      data-native-detail-visible={String(localDetail)}
      data-native-affine={JSON.stringify(input.affine)}
      data-native-axis={axis}
      data-native-slice={positions[axis]}
      data-native-sampled-index={sampled}
      data-native-reader-ijk={positions.join(',')}
      data-native-additions={saved ? observed.added_indices.length : 0}
      data-native-removed-count={saved ? observed.removed_indices.length : 0}
      data-native-route-count={saved ? observed.centerline_ras.length : 0}
      data-native-bridge-count={bridgeVisible ? observed.bridge_ijk.length : 0}
      data-native-mesh-visible={String(meshVisible)}
      data-native-mesh-vertices={meshVisible ? observed.mesh.vertex_count : 0}
      data-native-cpr-visible={String(cprVisible)}
      data-native-cpr-angle={cprVisible ? observed.cpr.angles_deg[angle] : ''}
      data-native-cpr-row={cprVisible ? column : ''}
      data-native-cpr-offset-mm={cprVisible ? observed.cpr.offsets_mm[offset] : ''}
      data-native-selected-source-ras={sourceRas?.join(',') ?? ''}
      data-native-selected-source-ijk={sourceNative?.join(',') ?? ''}
      data-native-corrected-arc={referenceShown ? reference.corrected_arc_mm.at(-1) : ''}
      data-native-original-arc={cprVisible ? observed.cpr.arc_mm.at(-1) : ''}
      data-native-saved-visible={String(saved)}
      data-native-cpr-column={cprVisible ? offset : ''}
    >
      <div className={styles.inventory}>
        <strong>Whole supplied CTA crop · {input.shape.join(' × ')} · native L / A / S</strong>
        <span>
          Supplied prediction, exact binary edit region and two route anchors; the rest of the
          source scan was not supplied.
        </span>
      </div>
      <div className={styles.grid}>
        <div className={styles.card} data-native-card="true">
          <header className={styles.heading}>
            <strong>
              {meshVisible ? 'Original saved full mesh' : 'Native crop and supplied helpers'}
            </strong>
            <span>RAS mm · physical scale</span>
          </header>
          <div className={styles.sceneWrap}>
            <div
              ref={host}
              className={styles.scene}
              tabIndex={capture ? -1 : 0}
              role="img"
              aria-label="Native coronary CT crop. Arrow keys orbit; Home resets."
            />
            {fallback && (
              <div className={styles.poster}>
                <img src={input.poster} alt="Whole supplied CTA crop context poster" />
                <span>2D fallback · native MPR and original CPR remain usable</span>
              </div>
            )}
            {!decoded && !fallback && (
              <p className={styles.loading}>Decoding native crop and retained output arrays…</p>
            )}
          </div>
          <div className={styles.legend}>
            <span className={styles.maskKey}>Supplied mask</span>
            {localDetail && <span className={styles.detailKey}>Reader detail</span>}
            <span className={styles.editKey}>Binary edit region / tint</span>
            <span className={styles.inspectionKey}>Logged inspection</span>
            {bridgeVisible && <span className={styles.bridgeKey}>Chosen 14-point bridge</span>}
            {saved && <span className={styles.savedKey}>Saved edits / route</span>}
            {cprVisible && <span className={styles.cprKey}>CPR source / strip</span>}
          </div>
          <p className={styles.note}>
            CT preview {input.preview_window.join(' to ')} HU; nearest mapped native samples. Yellow
            crosses are supplied start/end anchors.
            {meshVisible &&
              ` Full saved surface: ${observed.mesh.vertex_count.toLocaleString()} vertices / ${observed.mesh.face_count.toLocaleString()} faces.`}
          </p>
          <button
            className={styles.reset}
            disabled={capture || fallback}
            type="button"
            onClick={() => drawing.current?.reset()}
          >
            Reset orbit · arrows / Home
          </button>
        </div>
        <div className={`${styles.card} ${styles.operation}`} data-native-card="true">
          <header className={styles.heading}>
            <strong>{state?.label ?? 'Receive supplied crop'}</strong>
            <span>{state ? `Recorded step ${state.trace_step}` : 'Input'}</span>
          </header>
          {inspectOptions.length > 0 && (
            <label className={styles.control}>
              Recorded inspection
              <select
                disabled={capture}
                aria-label="Coronary recorded inspection"
                value={state?.id ?? ''}
                onChange={(e) => setInspectionId(e.target.value)}
              >
                {inspectOptions.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.label}
                  </option>
                ))}
              </select>
            </label>
          )}
          <p className={styles.description}>{state?.description}</p>
          {delivered && (
            <figure className={styles.delivered}>
              <a href={delivered.src} target="_blank" rel="noreferrer" tabIndex={capture ? -1 : 0}>
                <img
                  src={delivered.src}
                  alt={`Exact delivered coronary PNG step ${delivered.step}`}
                />
              </a>
              <figcaption>
                Exact delivered montage · step {delivered.step} · click to inspect. Red
                supplied-mask pixels / green editable non-mask pixels; montage display window
                −200..500 HU.
              </figcaption>
            </figure>
          )}
          {state?.bounds && (
            <code className={styles.readout}>
              Logged native cells [{state.bounds[0].join(',')}] → [{state.bounds[1].join(',')})
            </code>
          )}
          {state?.center_ijk && (
            <code className={styles.readout}>
              Logged centre [{fmt(state.center_ijk)}] · RAS [
              {fmt(rasPoint(input.affine, state.center_ijk))}] mm
            </code>
          )}
          {saved && !cprVisible && (
            <p className={styles.note}>
              {observed.added_indices.length} original additions / {observed.removed_indices.length}{' '}
              removals; {observed.centerline_ras.length} saved RAS route points. No intermediate
              repaired masks were retained.
            </p>
          )}
          {cprVisible && (
            <div className={styles.cprPanel}>
              <strong>Original saved CPR · reader source linkage</strong>
              <canvas
                ref={cpr}
                className={styles.cprCanvas}
                aria-label="Original CPR HU strip. Click selects route column and offset."
                tabIndex={capture ? -1 : 0}
                onClick={(e) => {
                  if (capture) return;
                  const r = e.currentTarget.getBoundingClientRect();
                  setColumn(
                    Math.max(
                      0,
                      Math.min(
                        observed.cpr.shape[1] - 1,
                        Math.floor(((e.clientX - r.left) / r.width) * observed.cpr.shape[1]),
                      ),
                    ),
                  );
                  setOffset(
                    Math.max(
                      0,
                      Math.min(
                        observed.cpr.shape[2] - 1,
                        observed.cpr.shape[2] -
                          1 -
                          Math.floor(((e.clientY - r.top) / r.height) * observed.cpr.shape[2]),
                      ),
                    ),
                  );
                }}
              />
              <div className={styles.cprControls}>
                <label>
                  Angle
                  <select
                    disabled={capture}
                    aria-label="CPR angle"
                    value={angle}
                    onChange={(e) => setAngle(Number(e.target.value))}
                  >
                    {observed.cpr.angles_deg.map((a, n) => (
                      <option key={a} value={n}>
                        {a}°
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  Route column {column}
                  <input
                    disabled={capture}
                    aria-label="CPR route index"
                    type="range"
                    min={0}
                    max={observed.cpr.shape[1] - 1}
                    value={column}
                    onChange={(e) => setColumn(Number(e.target.value))}
                  />
                </label>
                <label>
                  Offset {observed.cpr.offsets_mm[offset].toFixed(2)} mm
                  <input
                    disabled={capture}
                    aria-label="CPR offset index"
                    type="range"
                    min={0}
                    max={observed.cpr.shape[2] - 1}
                    value={offset}
                    onChange={(e) => setOffset(Number(e.target.value))}
                  />
                </label>
              </div>
              {sourceRas && sourceNative && (
                <div className={styles.link}>
                  <code>Source RAS [{fmt(sourceRas)}] mm</code>
                  <code>
                    Native [{fmt(sourceNative)}] · {decoded?.hu[pixel].toFixed(2)} HU
                  </code>
                  {!inCrop(sourceNative, input.shape) && (
                    <span>Outside supplied crop: no native input pixels here.</span>
                  )}
                </div>
              )}
              <p className={styles.arc}>
                Original arc[{column}] {observed.cpr.arc_mm[column].toFixed(3)} mm · endpoint{' '}
                {observed.cpr.arc_mm.at(-1)?.toFixed(3)} mm.
                {referenceShown && (
                  <>
                    {' '}
                    Separate author-corrected arc[{column}]{' '}
                    {reference.corrected_arc_mm[column].toFixed(3)} mm · endpoint{' '}
                    {reference.corrected_arc_mm.at(-1)?.toFixed(3)} mm. Original remains preserved.
                  </>
                )}
              </p>
              <span className={styles.note}>
                No CPR or mesh screenshot was delivered to the solver.
              </span>
            </div>
          )}
        </div>
        <div className={styles.card} data-native-card="true">
          <header className={styles.heading}>
            <strong>{localDetail ? 'Native CT detail' : axes[axis]}</strong>
            <span>Reader-generated native MPR</span>
          </header>
          <div className={styles.slice}>
            <canvas
              ref={slice}
              aria-label="Coronary native CT slice with exact supplied mask membership"
            />
            {[0, 1, 2].map((a) => (
              <canvas
                key={a}
                hidden
                ref={(node) => {
                  sources.current[a] = node;
                }}
              />
            ))}
          </div>
          {!capture && ['search', 'contacts', 'route'].includes(chapterId) && (
            <label className={styles.control}>
              <input
                type="checkbox"
                aria-label="Native CT detail"
                checked={localDetail}
                onChange={(e) => setLocalDetail(e.target.checked)}
              />
              Native CT detail
            </label>
          )}
          <label className={styles.control}>
            Native axis
            <select
              disabled={capture}
              aria-label="Coronary native slice axis"
              value={axis}
              onChange={(e) => setAxis(Number(e.target.value))}
            >
              {axes.map((a, n) => (
                <option key={a} value={n}>
                  {a}
                </option>
              ))}
            </select>
          </label>
          <label className={styles.slider}>
            Requested {['i', 'j', 'k'][axis]}={positions[axis]} · sampled {sampled}
            <input
              disabled={capture}
              aria-label="Coronary native slice index"
              type="range"
              min={localDetail ? input.detail_origin[axis] : 0}
              max={
                localDetail
                  ? input.detail_origin[axis] + input.detail_shape[axis] - 1
                  : input.shape[axis] - 1
              }
              value={positions[axis]}
              onChange={(e) =>
                setPositions((p) => p.map((v, a) => (a === axis ? Number(e.target.value) : v)))
              }
            />
            <span>
              RAS [
              {fmt(
                rasPoint(
                  input.affine,
                  positions.map((v, a) => (a === axis ? sampled : v)),
                ),
              )}
              ] mm
            </span>
          </label>
          {state?.axis === axis && state.levels.length > 0 && (
            <label className={styles.control}>
              Logged plane
              <select
                disabled={capture}
                aria-label="Coronary recorded plane"
                value={state.levels.includes(positions[axis]) ? positions[axis] : ''}
                onChange={(e) =>
                  setPositions((p) => p.map((v, a) => (a === axis ? Number(e.target.value) : v)))
                }
              >
                <option value="" disabled>
                  Reader selection
                </option>
                {state.levels.map((k) => (
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
          {error}. Poster is retained context; unavailable arrays are not reconstructed.
        </p>
      )}
    </section>
  );
}
