import * as THREE from 'three';
import rawGeometry from '../../assets/teaching-fixtures/route-unfold-v1/geometry.json?raw';
import rawRoute from '../../assets/teaching-fixtures/route-unfold-v1/route.json?raw';
import sampledImage from '../../assets/teaching-fixtures/route-unfold-v1/cpr-sampled.png?inline';
import fixturePoster from '../../assets/teaching-fixtures/route-unfold-v1/phantom-projection.png?inline';
import { createRouteSampler } from './route-correspondence';
import type { StoryState } from './story-timeline';
import type { Annotation, ScenePoint } from './types';
interface MeshData {
  vertices: number[][];
  normals: number[][];
  faces: number[][];
}
interface GeometryData {
  schema: number;
  units: string;
  frame: string;
  hero: MeshData;
  selected: MeshData;
  ribbon: MeshData;
}
interface RouteData {
  frame: string;
  points: number[][];
  normals: number[][];
  u_m: number[];
  sample_values: number[][];
  anchors: Record<string, number[]>;
}
// Immutable retained bytes are validated and hashed by the Python build projection.
const geometry = JSON.parse(rawGeometry) as GeometryData;
const route = JSON.parse(rawRoute) as RouteData;
export const routeSampler = createRouteSampler(route);
export { sampledImage, fixturePoster };

/** Native content only: the existing stage owns the renderer, camera and labels. */
export function createRoutePrefab(parent: THREE.Group) {
  if (geometry.schema !== 1 || geometry.units !== 'm' || route.frame !== geometry.frame)
    throw new Error('Invalid route fixture frame');
  // Validate every retained vertex against its source sample, not just a stride assumption.
  const transverse = route.u_m.map((_, i) => i).filter((i) => i % 4 === 0);
  if (geometry.ribbon.vertices.length !== route.points.length * transverse.length)
    throw new Error('Ribbon sample count mismatch');
  const colors: number[] = [];
  route.points.forEach((c, i) =>
    transverse.forEach((j, k) => {
      const actual = geometry.ribbon.vertices[i * transverse.length + k];
      const expected = c.map((v, axis) => v + route.u_m[j] * route.normals[i][axis]);
      if (Math.hypot(...actual.map((v, axis) => v - expected[axis])) > 2e-7)
        throw new Error('Ribbon sample association mismatch');
      const v = Math.max(0, Math.min(1, route.sample_values[i][j]));
      colors.push(...new THREE.Color().setRGB(v, v, v, THREE.SRGBColorSpace).toArray());
    }),
  );
  const group = new THREE.Group();
  group.name = 'route-unfold-v1';
  parent.add(group);
  const geometries: THREE.BufferGeometry[] = [],
    materials: THREE.Material[] = [];
  const ownGeo = <T extends THREE.BufferGeometry>(g: T): T => {
    geometries.push(g);
    return g;
  };
  const ownMat = <T extends THREE.Material>(m: T): T => {
    materials.push(m);
    return m;
  };
  function mesh<T extends THREE.Material>(name: string, src: MeshData, material: T) {
    const g = ownGeo(new THREE.BufferGeometry());
    g.setAttribute('position', new THREE.Float32BufferAttribute(src.vertices.flat(), 3));
    g.setAttribute('normal', new THREE.Float32BufferAttribute(src.normals.flat(), 3));
    g.setIndex(src.faces.flat());
    g.computeBoundingSphere();
    const m = new THREE.Mesh(g, material);
    m.name = name;
    group.add(m);
    return m;
  }
  const context = mesh(
    'context',
    geometry.hero,
    ownMat(
      new THREE.MeshStandardMaterial({
        color: 0xa6a396,
        roughness: 0.82,
        transparent: true,
        depthWrite: false,
      }),
    ),
  );
  const selected = mesh(
    'selected-route',
    geometry.selected,
    ownMat(new THREE.MeshStandardMaterial({ color: 0x307f74, roughness: 0.82 })),
  );
  const ribbon = mesh(
    'sampling-ribbon',
    geometry.ribbon,
    ownMat(
      new THREE.MeshBasicMaterial({
        vertexColors: true,
        side: THREE.DoubleSide,
        transparent: true,
        depthWrite: false,
      }),
    ),
  );
  ribbon.geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
  const routeGeo = ownGeo(new THREE.BufferGeometry());
  routeGeo.setAttribute('position', new THREE.Float32BufferAttribute(route.points.flat(), 3));
  const line = new THREE.Line(
    routeGeo,
    ownMat(new THREE.LineBasicMaterial({ color: 0xb77128, depthTest: false, depthWrite: false })),
  );
  line.renderOrder = 100;
  group.add(line);
  const cursorGeo = ownGeo(new THREE.BufferGeometry());
  cursorGeo.setAttribute('position', new THREE.Float32BufferAttribute(new Float32Array(6), 3));
  const cursor = new THREE.Line(
    cursorGeo,
    ownMat(new THREE.LineBasicMaterial({ color: 0x557e93, depthTest: false, depthWrite: false })),
  );
  cursor.renderOrder = 101;
  group.add(cursor);
  const markerGeo = ownGeo(new THREE.SphereGeometry(0.0015, 16, 10));
  const markerMat = ownMat(new THREE.MeshStandardMaterial({ color: 0xb77128, roughness: 0.8 }));
  for (const id of ['inlet', 'target']) {
    const m = new THREE.Mesh(markerGeo, markerMat);
    m.position.fromArray(route.anchors[id]);
    group.add(m);
  }
  const box = new THREE.Box3().setFromBufferAttribute(
    context.geometry.getAttribute('position') as THREE.BufferAttribute,
  );
  box.expandByObject(ribbon);
  const center = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3());
  const scale = 2.3 / Math.max(size.x, size.y, size.z);
  group.scale.setScalar(scale);
  group.position.copy(center).multiplyScalar(-scale);
  const display = (p: readonly number[]): ScenePoint => {
    if (p.length !== 3 || !p.every(Number.isFinite)) throw new Error('Invalid route point');
    return [(p[0] - center.x) * scale, (p[1] - center.y) * scale, (p[2] - center.z) * scale];
  };
  let disposed = false;
  return {
    update(state: StoryState): Annotation[] {
      if (disposed) throw new Error('Disposed prefab');
      if (state.recipe !== 'route-unfold-v1') throw new Error('Route state required');
      context.material.opacity = state.context;
      selected.visible = state.route >= 0.999;
      routeGeo.setDrawRange(0, Math.floor(state.route * (route.points.length - 1)) + 1);
      line.visible = state.route > 0;
      ribbon.visible = state.ribbon > 0;
      ribbon.material.opacity = 0.78 * state.ribbon;
      cursor.visible = state.index >= 2;
      const sample = routeSampler.atDistanceFraction(state.cursor);
      const attr = cursorGeo.getAttribute('position');
      attr.setXYZ(0, ...sample.lineStart);
      attr.setXYZ(1, ...sample.lineEnd);
      attr.needsUpdate = true;
      cursorGeo.computeBoundingSphere();
      const labels: Annotation[] = ['inlet', 'target'].map((id) => ({
        p: display(route.anchors[id]),
        anchor: display(route.anchors[id]),
        text: id === 'inlet' ? 'Supplied inlet' : 'Supplied target',
        color: '#906021',
      }));
      if (state.index >= 2)
        labels.push({
          p: display(sample.center),
          anchor: display(sample.center),
          text: `Sample column ${sample.column + 1}`,
          color: '#426c82',
        });
      return labels;
    },
    dispose() {
      if (disposed) return;
      disposed = true;
      parent.remove(group);
      geometries.forEach((g) => g.dispose());
      materials.forEach((m) => m.dispose());
      group.clear();
    },
  };
}
