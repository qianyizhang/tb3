import * as THREE from 'three';
import rawHero from '../../assets/teaching-fixtures/route-unfold-v1/geometry.json?raw';
import { graph, rigid, traceEdges, type IndexedMesh } from './operation-fixtures';
import type { NativeContent } from './stage';
import type { ScenePoint, Annotation } from './types';

/** Content lifetime only; the existing stage retains camera, renderer and projection. */
function content(parent: THREE.Group, name: string) {
  const root = new THREE.Group();
  root.name = name;
  parent.add(root);
  const geometries: THREE.BufferGeometry[] = [],
    materials: THREE.Material[] = [];
  function mesh(data: IndexedMesh, color: string, owner = root) {
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(data.vertices.flat(), 3));
    geometry.setIndex(data.faces.flat());
    geometry.computeVertexNormals();
    const material = new THREE.MeshStandardMaterial({ color, roughness: 0.82 });
    const mesh = new THREE.Mesh(geometry, material);
    owner.add(mesh);
    geometries.push(geometry);
    materials.push(material);
    return mesh;
  }
  function line(points: number[][], color: string) {
    const geometry = new THREE.BufferGeometry().setFromPoints(
      points.map((p) => new THREE.Vector3(p[0], p[1], p[2])),
    );
    const material = new THREE.LineBasicMaterial({ color });
    const line = new THREE.Line(geometry, material);
    root.add(line);
    geometries.push(geometry);
    materials.push(material);
    return line;
  }
  function marker(p: number[], color: string, owner = root) {
    const geometry = new THREE.SphereGeometry(0.0018, 16, 10);
    const material = new THREE.MeshStandardMaterial({ color, roughness: 0.8 });
    const object = new THREE.Mesh(geometry, material);
    object.position.fromArray(p);
    owner.add(object);
    geometries.push(geometry);
    materials.push(material);
    return object;
  }
  function fit(box: THREE.Box3) {
    const center = box.getCenter(new THREE.Vector3()),
      size = box.getSize(new THREE.Vector3());
    const scale = 2.35 / Math.max(size.x, size.y, size.z);
    root.scale.setScalar(scale);
    root.position.copy(center).multiplyScalar(-scale);
    return (p: readonly number[]): ScenePoint => [
      (p[0] - center.x) * scale,
      (p[1] - center.y) * scale,
      (p[2] - center.z) * scale,
    ];
  }
  let disposed = false;
  return {
    root,
    mesh,
    line,
    marker,
    fit,
    alive() {
      if (disposed) throw Error('Disposed prefab');
    },
    dispose() {
      if (disposed) return;
      disposed = true;
      parent.remove(root);
      geometries.forEach((g) => g.dispose());
      materials.forEach((m) => m.dispose());
      root.clear();
    },
  };
}
export function createTopologyPrefab(parent: THREE.Group): NativeContent {
  const c = content(parent, 'topology-v1');
  const hero = c.mesh((JSON.parse(rawHero) as { hero: IndexedMesh }).hero, '#c0beb0');
  hero.material.transparent = true;
  hero.material.opacity = 0.14;
  hero.material.depthWrite = false;
  const display = c.fit(new THREE.Box3().setFromObject(hero));
  const lines = graph.edges.map((edge) => ({ edge, line: c.line(edge.points, '#aaa99b') }));
  const selected = traceEdges(1).map(({ edge }) => ({
    edge,
    line: c.line(edge.points, '#b77128'),
  }));
  const cursor = c.marker(graph.nodes.inlet, '#557e93');
  return {
    update(state) {
      c.alive();
      if (state.recipe !== 'topology-v1') throw Error('Topology state required');
      const count = Math.floor(state.inventory * graph.edges.length + 1e-8);
      lines.forEach(({ line }, i) => line.material.color.set(i < count ? '#307f74' : '#aaa99b'));
      const trace = traceEdges(state.trace);
      selected.forEach(({ line }, i) => {
        const points = trace[i].points,
          attr = line.geometry.getAttribute('position');
        points.forEach((p, j) => attr.setXYZ(j, p[0], p[1], p[2]));
        attr.needsUpdate = true;
        line.geometry.setDrawRange(0, points.length);
        line.visible = points.length > 1;
      });
      const traversed = trace.filter((x) => x.points.length > 1).at(-1);
      cursor.visible = state.trace > 0;
      if (traversed) cursor.position.fromArray(traversed.points.at(-1)!);
      const names =
        state.trace > 0 ? ['inlet', graph.selected_target] : ['inlet', 'j1', 'j2', 'j3'];
      return names
        .filter((id) => state.focus > 0.5 || id === 'inlet')
        .map((id) => ({
          p: display(graph.nodes[id]),
          anchor: display(graph.nodes[id]),
          text: id,
          color: '#596453',
        }));
    },
    dispose: c.dispose,
  };
}
export function createCorrespondencePrefab(parent: THREE.Group): NativeContent {
  const c = content(parent, 'correspondence-v1');
  const movingRoot = new THREE.Group();
  c.root.add(movingRoot);
  c.mesh(rigid.geometry.moving, '#b77128', movingRoot);
  const fixed = c.mesh(rigid.geometry.fixed, '#307f74');
  fixed.material.transparent = true;
  fixed.material.opacity = 0.25;
  fixed.material.depthWrite = false;
  rigid.moving_points.forEach((p) => c.marker(p, '#b77128', movingRoot));
  rigid.fixed_points.forEach((p) => {
    const marker = c.marker(p, '#307f74');
    marker.material.wireframe = true;
    marker.scale.setScalar(1.6);
  });
  const box = new THREE.Box3().setFromObject(c.root),
    display = c.fit(box);
  // Matrix4.set accepts row-major values; fromArray would transpose this fixture.
  const matrix = new THREE.Matrix4();
  matrix.set(...(rigid.fixed_from_moving.flat() as Parameters<THREE.Matrix4['set']>));
  const translation = new THREE.Vector3(),
    rotation = new THREE.Quaternion(),
    scale = new THREE.Vector3();
  matrix.decompose(translation, rotation, scale);
  if (scale.toArray().some((v) => Math.abs(v - 1) > 1e-6)) throw Error('Expected rigid transform');
  const deformation = rigid.deformed_points.map((p) => c.marker(p, '#9b5863'));
  const identity = new THREE.Quaternion();
  return {
    update(state) {
      c.alive();
      if (state.recipe !== 'correspondence-v1') throw Error('Correspondence state required');
      deformation.forEach((point) => {
        point.visible = state.beatId === 'scope';
      });
      fixed.visible = state.transform < 0.995;
      movingRoot.position.copy(translation).multiplyScalar(state.transform);
      movingRoot.quaternion.copy(identity).slerp(rotation, state.transform);
      const labels: Annotation[] = rigid.point_ids.map((id, i) => {
        const p = new THREE.Vector3()
          .fromArray(rigid.moving_points[i])
          .applyQuaternion(movingRoot.quaternion)
          .add(movingRoot.position)
          .toArray();
        return {
          p: display(p),
          anchor: display(p),
          text: id + (rigid.held_out_ids.includes(id) ? ' · check' : ' · fit'),
          color: '#906021',
        };
      });
      return labels;
    },
    dispose: c.dispose,
  };
}

import { material, materialPosition } from './operation-fixtures';
export function createMaterialPrefab(parent: THREE.Group): NativeContent {
  const c = content(parent, 'shape-material-v1');
  const shells = [-0.055, 0.055].map((offset) => {
    const mesh = c.mesh(material.geometry.initial, '#b8b5a6');
    mesh.position.x = offset;
    mesh.material.transparent = true;
    mesh.material.opacity = 0.48;
    mesh.material.depthWrite = false;
    const markers = material.marker_uv.map((uv, i) =>
      c.marker(materialPosition(uv[0], uv[1], 0, 0), ['#307f74', '#b77128', '#557e93'][i]),
    );
    const tracks = material.marker_uv.map((_, i) =>
      c.line(
        Array.from({ length: 49 }, () => [0, 0, 0]),
        ['#307f74', '#b77128', '#557e93'][i],
      ),
    );
    return { offset, mesh, markers, tracks };
  });
  const display = c.fit(new THREE.Box3().setFromObject(c.root));
  return {
    update(state) {
      c.alive();
      if (state.recipe !== 'shape-material-v1') throw Error('Material state required');
      const phase = 1 - 0.14 * state.phase;
      shells.forEach(({ offset, mesh, markers, tracks }, side) => {
        const attr = mesh.geometry.getAttribute('position');
        material.geometry.initial.vertices.forEach(([x, y, z], i) =>
          attr.setXYZ(i, (x - 0.12 * y) * phase + (0.12 * y) / phase, y / phase, z * phase),
        );
        attr.needsUpdate = true;
        mesh.geometry.computeVertexNormals();
        const alternative = side ? state.alternative : 0;
        markers.forEach((marker, i) => {
          marker.visible = state.markers > 0;
          const uv = material.marker_uv[i],
            p = materialPosition(uv[0], uv[1], state.phase, alternative);
          p[0] += offset;
          marker.position.fromArray(p);
          const line = tracks[i];
          line.visible = state.markers > 0.1;
          const a = line.geometry.getAttribute('position');
          for (let j = 0; j < 49; j++) {
            const v = materialPosition(uv[0], uv[1], (state.phase * j) / 48, alternative);
            a.setXYZ(j, v[0] + offset, v[1], v[2]);
          }
          a.needsUpdate = true;
          line.geometry.computeBoundingSphere();
        });
      });
      return shells.map(({ offset }, i) => ({
        p: display([offset, -0.071, 0]),
        anchor: display([offset, -0.055, 0]),
        text: i ? 'Map B · same shell' : 'Map A · same shell',
        color: '#426c82',
      }));
    },
    dispose: c.dispose,
  };
}

import { AnatomyAssets } from './anatomy';
export function createAnatomyPrefab(parent: THREE.Group): NativeContent {
  const c = content(parent, 'anatomy-audit-v1');
  // AnatomyAssets fits the entire assembly once and keeps source-relative geometry.
  const parts = AnatomyAssets.get('abdomen')!;
  const meshes = parts.map((part) => ({ part, mesh: c.mesh(part, '#b8b5a6') }));
  const display = c.fit(new THREE.Box3().setFromObject(c.root));
  const selected = meshes.find((item) => item.part.id === 'kidney_left')!;
  const anchor = new THREE.Box3()
    .setFromObject(selected.mesh)
    .getCenter(new THREE.Vector3())
    .toArray();
  return {
    update(state) {
      c.alive();
      if (state.recipe !== 'anatomy-audit-v1') throw Error('Anatomy state required');
      meshes.forEach(({ part, mesh }) => {
        const focus = part.id === 'kidney_left' && state.focus > 0;
        mesh.material.color.set(focus ? '#307f74' : '#b8b5a6');
        mesh.material.transparent = !focus;
        mesh.material.opacity = focus ? 1 : 0.25;
        mesh.material.depthWrite = focus;
      });
      return state.focus > 0.5
        ? [
            {
              p: display(anchor),
              anchor: display(anchor),
              text: 'Source object: kidney_left',
              color: '#307f74',
            },
          ]
        : [];
    },
    dispose: c.dispose,
  };
}
