import * as THREE from 'three';
import type { Annotation, Face, Point, SceneModel, SceneView, Line } from './types';
type SurfaceMesh = THREE.Mesh<
  THREE.BufferGeometry,
  THREE.MeshBasicMaterial | THREE.MeshStandardMaterial
>;
type Lines = THREE.LineSegments<
  THREE.BufferGeometry,
  THREE.LineBasicMaterial | THREE.LineDashedMaterial
>;
interface Renderables {
  backdrop?: SurfaceMesh;
  surface?: SurfaceMesh;
  flat?: SurfaceMesh;
  transparent: SurfaceMesh[];
  lines: Map<string, Lines>;
  dots: SurfaceMesh[];
  images: SurfaceMesh[];
}
import { TaskTeachingArt } from '../../assets/teaching/task-art.js';

// The one browser renderer for teaching scenes. Scene recipes still own task
// geometry; Three owns projection, surfaces, lines, image planes and depth.
export const SceneStage = {
  create(
    canvas: HTMLCanvasElement,
    labelsRoot: HTMLElement,
    onChange: () => void,
    onLost: () => void,
  ) {
    const gl = canvas.getContext('webgl2', {
      alpha: true,
      antialias: true,
      preserveDrawingBuffer: true,
    });
    if (!gl) return null;
    const renderer = new THREE.WebGLRenderer({
      canvas,
      context: gl,
      alpha: true,
      antialias: true,
      preserveDrawingBuffer: true,
    });
    renderer.setClearColor(0xffffff, 0);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.05;
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
    const scene = new THREE.Scene();
    const pitch = new THREE.Group();
    const yaw = new THREE.Group();
    pitch.add(yaw);
    scene.add(pitch);
    scene.add(new THREE.HemisphereLight(0xffffff, 0xc2bdb2, 1.6));
    const key = new THREE.DirectionalLight(0xfff7e8, 2.0);
    key.position.set(-3, 5, 5);
    scene.add(key);
    const rim = new THREE.DirectionalLight(0xe4eff0, 0.45);
    rim.position.set(4, 1, -4);
    scene.add(rim);
    const camera = new THREE.PerspectiveCamera(32, 1, 0.1, 60);
    camera.position.set(0, 0, 7);
    const surfaceMaterial = new THREE.MeshStandardMaterial({
      vertexColors: true,
      roughness: 0.64,
      metalness: 0,
      side: THREE.DoubleSide,
    });
    const flatMaterial = new THREE.MeshBasicMaterial({
      vertexColors: true,
      side: THREE.DoubleSide,
    });
    const backdropMaterial = new THREE.MeshBasicMaterial({
      vertexColors: true,
      side: THREE.DoubleSide,
      depthTest: false,
      depthWrite: false,
    });
    const dotGeometry = new THREE.SphereGeometry(1, 14, 10);
    const materialCache = new Map<string, THREE.MeshBasicMaterial>();
    const textures = new Map<string, { image: HTMLImageElement; map: THREE.Texture }>();
    const objects: {
      object: THREE.Object3D;
      geometry: THREE.BufferGeometry | null;
      material: THREE.Material | null;
    }[] = [];
    let renderables: Renderables | null = null;
    let rebuilds = 0;
    let updates = 0;
    const leaders = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    leaders.classList.add('scene-leaders');
    leaders.setAttribute('aria-hidden', 'true');
    labelsRoot.append(leaders);
    let currentModel: SceneModel | null = null;
    let width = 0;
    let height = 0;
    let disposed = false;
    const colorCache = new Map<string, number[]>();
    const rgb = (hex: string) => {
      if (!colorCache.has(hex)) colorCache.set(hex, new THREE.Color(hex).toArray());
      return colorCache.get(hex)!;
    };
    const point = (p: Point) => new THREE.Vector3(p[0], p[1], p[2]);
    const own = <T extends THREE.Object3D>(
      object: T,
      geometry: THREE.BufferGeometry | null = null,
      material: THREE.Material | null = null,
    ): T => {
      yaw.add(object);
      objects.push({ object, geometry, material });
      return object;
    };
    const releaseModel = () => {
      for (const { object, geometry, material } of objects) {
        yaw.remove(object);
        geometry?.dispose();
        material?.dispose();
      }
      objects.length = 0;
      currentModel = null;
      renderables = null;
    };
    const faceGeometry = (faces: Pick<Face, 'points' | 'color' | 'normals'>[], uv = false) => {
      const count = faces.reduce((sum, face) => sum + face.points.length - 2, 0);
      const positions = new Float32Array(count * 9);
      const normals = new Float32Array(count * 9);
      const colors = new Float32Array(count * 9);
      const uvs = uv ? new Float32Array(count * 6) : null;
      let cursor = 0;
      for (const face of faces) {
        const color = rgb(face.color);
        for (let i = 1; i < face.points.length - 1; i++) {
          for (const index of [0, i, i + 1]) {
            positions.set(face.points[index], cursor * 3);
            normals.set(face.normals?.[index] || [0, 0, 1], cursor * 3);
            colors.set(color, cursor * 3);
            if (uvs)
              uvs.set(
                [
                  [0, 1],
                  [1, 1],
                  [1, 0],
                  [0, 0],
                ][index],
                cursor * 2,
              );
            cursor++;
          }
        }
      }
      const geometry = new THREE.BufferGeometry();
      geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
      geometry.setAttribute('normal', new THREE.BufferAttribute(normals, 3));
      geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
      if (uvs) geometry.setAttribute('uv', new THREE.BufferAttribute(uvs, 2));
      return geometry;
    };
    const updateFaces = (
      geometry: THREE.BufferGeometry,
      faces: Pick<Face, 'points' | 'color' | 'normals'>[],
      offset = [0, 0, 0],
    ) => {
      const positions = geometry.getAttribute('position');
      const normals = geometry.getAttribute('normal');
      const colors = geometry.getAttribute('color');
      let cursor = 0;
      let positionsChanged = false;
      let normalsChanged = false;
      let colorsChanged = false;
      for (const face of faces) {
        const color = rgb(face.color || '#ffffff');
        for (let i = 1; i < face.points.length - 1; i++)
          for (const index of [0, i, i + 1]) {
            const p = face.points[index];
            const x = Math.fround(p[0] - offset[0]),
              y = Math.fround(p[1] - offset[1]),
              z = Math.fround(p[2] - offset[2]);
            if (
              positions.getX(cursor) !== x ||
              positions.getY(cursor) !== y ||
              positions.getZ(cursor) !== z
            ) {
              positions.setXYZ(cursor, x, y, z);
              positionsChanged = true;
            }
            const n = face.normals?.[index] || [0, 0, 1];
            if (
              normals.getX(cursor) !== Math.fround(n[0]) ||
              normals.getY(cursor) !== Math.fround(n[1]) ||
              normals.getZ(cursor) !== Math.fround(n[2])
            ) {
              normals.setXYZ(cursor, n[0], n[1], n[2]);
              normalsChanged = true;
            }
            if (
              colors.getX(cursor) !== Math.fround(color[0]) ||
              colors.getY(cursor) !== Math.fround(color[1]) ||
              colors.getZ(cursor) !== Math.fround(color[2])
            ) {
              colors.setXYZ(cursor, color[0], color[1], color[2]);
              colorsChanged = true;
            }
            cursor++;
          }
      }
      if (positionsChanged) {
        positions.needsUpdate = true;
        geometry.computeBoundingSphere();
      }
      if (normalsChanged) normals.needsUpdate = true;
      if (colorsChanged) colors.needsUpdate = true;
    };
    const addFaces = (
      faces: Face[],
      material: THREE.MeshBasicMaterial | THREE.MeshStandardMaterial,
      renderOrder = 0,
    ) => {
      if (!faces.length) return;
      const geometry = faceGeometry(faces);
      const mesh = own(new THREE.Mesh(geometry, material), geometry);
      mesh.renderOrder = renderOrder;
      return mesh;
    };
    const collect = (model: SceneModel) => {
      const faces = model.primitives.filter((item) => item.type === 'face');
      const lines = new Map<string, { items: Line[]; dash: boolean; alpha: number }>();
      for (const item of model.primitives.filter((primitive) => primitive.type === 'line')) {
        const key = `${Boolean(item.dash)}:${item.alpha}`;
        if (!lines.has(key))
          lines.set(key, { items: [], dash: Boolean(item.dash), alpha: item.alpha });
        lines.get(key)!.items.push(item);
      }
      return {
        backdrop: faces.filter((item) => item.backdrop && item.alpha === 1),
        surface: faces.filter((item) => item.surface && item.alpha === 1 && !item.backdrop),
        flat: faces.filter((item) => !item.surface && item.alpha === 1 && !item.backdrop),
        transparent: faces.filter((item) => item.alpha < 1),
        lines,
        dots: model.primitives.filter((item) => item.type === 'dot'),
        images: model.primitives.filter((item) => item.type === 'image'),
      };
    };
    const sameLayout = (previous: SceneModel, next: SceneModel) => {
      if (previous.primitives.length !== next.primitives.length) return false;
      return previous.primitives.every((item, i) => {
        const other = next.primitives[i];
        if (item.type !== other.type || item.points.length !== other.points.length) return false;
        if (item.type === 'face' && other.type === 'face')
          return (
            item.surface === other.surface &&
            item.backdrop === other.backdrop &&
            item.alpha === other.alpha
          );
        if (item.type === 'line' && other.type === 'line')
          return item.dash === other.dash && item.alpha === other.alpha;
        if (item.type === 'image' && other.type === 'image') return item.subject === other.subject;
        if (item.type === 'dot' && other.type === 'dot') return item.color === other.color;
        return true;
      });
    };
    const texture = (subject: string) => {
      if (!textures.has(subject)) {
        const image = new Image();
        const map = new THREE.Texture();
        map.colorSpace = THREE.SRGBColorSpace;
        image.onload = () => {
          if (disposed) return;
          // WebGL texture uploads from SVG-backed HTMLImageElements are not
          // portable. Rasterize the authored SVG locally before GPU upload.
          const bitmap = document.createElement('canvas');
          bitmap.width = 512;
          bitmap.height = 304;
          bitmap.getContext('2d')!.drawImage(image, 0, 0, bitmap.width, bitmap.height);
          map.image = bitmap;
          map.needsUpdate = true;
          onChange();
        };
        image.src =
          'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(TaskTeachingArt.scan(subject));
        textures.set(subject, { image, map });
      }
      return textures.get(subject)!.map;
    };
    const build = (model: SceneModel) => {
      releaseModel();
      const groups = collect(model);
      renderables = {
        backdrop: addFaces(groups.backdrop, backdropMaterial, -1),
        surface: addFaces(groups.surface, surfaceMaterial),
        flat: addFaces(groups.flat, flatMaterial),
        transparent: [],
        lines: new Map(),
        dots: [],
        images: [],
      };
      for (const face of groups.transparent) {
        const center = face.points[0].map(
          (_, axis) => face.points.reduce((sum, p) => sum + p[axis], 0) / face.points.length,
        );
        const geometry = faceGeometry([face]);
        geometry.translate(-center[0], -center[1], -center[2]);
        const material = new THREE.MeshBasicMaterial({
          vertexColors: true,
          side: THREE.DoubleSide,
          transparent: true,
          opacity: face.alpha,
          depthWrite: false,
        });
        const mesh = own(new THREE.Mesh(geometry, material), geometry, material);
        mesh.position.set(center[0], center[1], center[2]);
        mesh.renderOrder = 1;
        renderables!.transparent.push(mesh);
      }
      for (const [key, { items, dash, alpha }] of groups.lines) {
        const positions = new Float32Array(items.length * 6);
        const colors = new Float32Array(items.length * 6);
        items.forEach((item, i) => {
          positions.set(item.points[0], i * 6);
          positions.set(item.points[1], i * 6 + 3);
          const color = rgb(item.color);
          colors.set(color, i * 6);
          colors.set(color, i * 6 + 3);
        });
        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        const material = dash
          ? new THREE.LineDashedMaterial({
              vertexColors: true,
              dashSize: 0.055,
              gapSize: 0.04,
              transparent: true,
              opacity: alpha,
              depthTest: false,
            })
          : new THREE.LineBasicMaterial({
              vertexColors: true,
              transparent: true,
              opacity: alpha,
              depthTest: false,
            });
        const line = new THREE.LineSegments(geometry, material);
        if (dash) line.computeLineDistances();
        line.renderOrder = 2;
        own(line, geometry, material);
        renderables!.lines.set(key, line);
      }
      for (const item of groups.dots) {
        if (!materialCache.has(item.color))
          materialCache.set(
            item.color,
            new THREE.MeshBasicMaterial({ color: item.color, depthTest: false }),
          );
        const dot = new THREE.Mesh(dotGeometry, materialCache.get(item.color));
        dot.position.copy(point(item.points[0]));
        dot.scale.setScalar(item.radius);
        dot.renderOrder = 3;
        own(dot);
        renderables!.dots.push(dot);
      }
      for (const item of groups.images) {
        const geometry = faceGeometry([{ ...item, color: '#ffffff' }], true);
        const material = new THREE.MeshBasicMaterial({
          map: texture(item.subject),
          side: THREE.DoubleSide,
          transparent: true,
          depthWrite: false,
          toneMapped: false,
        });
        const image = own(new THREE.Mesh(geometry, material), geometry, material);
        image.renderOrder = 1;
        renderables!.images.push(image);
      }
      currentModel = model;
      rebuilds++;
    };
    const update = (model: SceneModel) => {
      const groups = collect(model);
      for (const name of ['backdrop', 'surface', 'flat'] as const)
        if (renderables![name]) updateFaces(renderables![name]!.geometry, groups[name]);
      groups.transparent.forEach((face, i) => {
        const mesh = renderables!.transparent[i];
        const center = face.points[0].map(
          (_, axis) => face.points.reduce((sum, p) => sum + p[axis], 0) / face.points.length,
        );
        updateFaces(mesh.geometry, [face], center);
        mesh.position.set(center[0], center[1], center[2]);
      });
      for (const [key, { items, dash }] of groups.lines) {
        const line = renderables!.lines.get(key)!;
        const positions = line.geometry.getAttribute('position');
        const colors = line.geometry.getAttribute('color');
        items.forEach((item, i) => {
          positions.setXYZ(i * 2, item.points[0][0], item.points[0][1], item.points[0][2]);
          positions.setXYZ(i * 2 + 1, item.points[1][0], item.points[1][1], item.points[1][2]);
          const color = rgb(item.color);
          colors.setXYZ(i * 2, color[0], color[1], color[2]);
          colors.setXYZ(i * 2 + 1, color[0], color[1], color[2]);
        });
        positions.needsUpdate = true;
        colors.needsUpdate = true;
        line.geometry.computeBoundingSphere();
        if (dash) line.computeLineDistances();
      }
      groups.dots.forEach((item, i) => {
        renderables!.dots[i].position.copy(point(item.points[0]));
        renderables!.dots[i].scale.setScalar(item.radius);
      });
      groups.images.forEach((item, i) =>
        updateFaces(renderables!.images[i].geometry, [{ ...item, color: '#ffffff' }]),
      );
      currentModel = model;
      updates++;
    };
    const project = (p: Point) => {
      const v = point(p).applyMatrix4(yaw.matrixWorld).project(camera);
      return [(v.x + 1) * width * 0.5, (1 - v.y) * height * 0.5];
    };
    const paintLabels = (labels: Annotation[]) => {
      let annotations = [...labelsRoot.querySelectorAll<HTMLElement>('.scene-annotation')];
      if (annotations.length !== labels.length) {
        annotations.forEach((item) => item.remove());
        annotations = labels.map(() => {
          const item = document.createElement('span');
          item.className = 'scene-annotation';
          labelsRoot.append(item);
          return item;
        });
      }
      leaders.replaceChildren();
      leaders.setAttribute('viewBox', `0 0 ${width} ${height}`);
      const last = { left: 12, right: 12 };
      labels.forEach((label, i) => {
        const el = annotations[i];
        if (el.textContent !== label.text) el.textContent = label.text;
        el.className = 'scene-annotation';
        el.style.color = label.color;
        const [x, y] = project(label.p);
        const side = x < width / 2 ? 'left' : 'right';
        const external = Boolean(label.anchor);
        const left = external
          ? side === 'left'
            ? 12
            : width - el.offsetWidth - 12
          : Math.max(8, Math.min(width - el.offsetWidth - 8, x - el.offsetWidth / 2));
        const top = Math.max(
          24,
          Math.min(height - el.offsetHeight - 42, external ? Math.max(last[side], y - 14) : y - 10),
        );
        if (external) last[side] = top + el.offsetHeight + 8;
        el.style.transform = `translate(${Math.round(left)}px, ${Math.round(top)}px)`;
        if (external) {
          const [ax, ay] = project(label.anchor!);
          const endX = side === 'left' ? left + el.offsetWidth + 5 : left - 5;
          const endY = top + el.offsetHeight / 2;
          const line = document.createElementNS('http://www.w3.org/2000/svg', 'path');
          line.setAttribute('d', `M ${ax} ${ay} L ${endX} ${endY}`);
          line.setAttribute('stroke', label.color);
          leaders.append(line);
          const dot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
          dot.setAttribute('cx', String(ax));
          dot.setAttribute('cy', String(ay));
          dot.setAttribute('r', '2.5');
          dot.setAttribute('fill', label.color);
          leaders.append(dot);
        }
      });
    };
    const contextLost = (event: Event) => {
      event.preventDefault();
      onLost();
    };
    canvas.addEventListener('webglcontextlost', contextLost);
    return {
      draw(model: SceneModel, view: SceneView) {
        if (disposed || gl.isContextLost()) return false;
        if (width !== view.width || height !== view.height) {
          width = view.width;
          height = view.height;
          renderer.setSize(width, height, false);
          camera.aspect = width / height;
          const zoom = Math.min(width / 4.1, height / 2.8);
          camera.fov = (2 * Math.atan(height / (14 * zoom)) * 180) / Math.PI;
          camera.updateProjectionMatrix();
        }
        yaw.rotation.y = view.yaw;
        pitch.rotation.x = view.pitch;
        if (model !== currentModel) {
          if (currentModel && sameLayout(currentModel, model)) update(model);
          else build(model);
        }
        scene.updateMatrixWorld(true);
        camera.updateMatrixWorld(true);
        renderer.render(scene, camera);
        paintLabels(model.labels);
        return true;
      },
      get texturesReady() {
        return [...textures.values()].every(
          ({ image }) => image.complete && image.naturalWidth > 0,
        );
      },
      get stats() {
        return { rebuilds, updates };
      },
      dispose() {
        disposed = true;
        canvas.removeEventListener('webglcontextlost', contextLost);
        releaseModel();
        for (const { image, map } of textures.values()) {
          image.onload = null;
          map.dispose();
        }
        textures.clear();
        for (const material of materialCache.values()) material.dispose();
        dotGeometry.dispose();
        surfaceMaterial.dispose();
        flatMaterial.dispose();
        backdropMaterial.dispose();
        try {
          renderer.dispose();
        } catch {
          /* A lost context has already released GPU resources. */
        }
        labelsRoot.replaceChildren();
      },
    };
  },
};
