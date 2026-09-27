import {
  airwayCases,
  airwayMasks,
  airwayOutput,
  airwayReference,
  airwayColors,
  airwayDisplay,
  airwayBounds,
  airwayCaseIndex,
  airwayReturned,
  airwayReveal,
  airwayRouteIndex,
  airwaySliceIndex,
  airwayAngleIndex,
} from './airway-repair';
import * as THREE from 'three';
import {
  respiratory,
  respiratoryOutput,
  respiratoryReference,
  respiratoryColors,
  planePoint,
  respiratoryPlacement,
  focusQuery,
  isRespiratoryCloseup,
  type CTPlane,
} from './respiratory';
import rawHero from '../../assets/teaching-fixtures/route-unfold-v1/geometry.json?raw';
import { graph, rigid, traceEdges, type IndexedMesh } from './operation-fixtures';
import {
  curationLayouts,
  curationRows,
  curationColor,
  curationScanName,
  type CurationState,
} from './anatomy-curation';
import type { NativeContent } from './stage';
import type { ScenePoint, Annotation } from './types';
import {
  screenGeometry,
  screenDisplay,
  screenKey,
  screenRows,
  screenBounds,
  screenColor,
  type ScreenKey,
} from './mask-screen';
import {
  prototypeObjects,
  prototypePoints,
  prototypeDisplay,
  prototypeRows,
} from './prototype-identity';

/** Content lifetime only; the existing stage retains camera, renderer and projection. */
function content(parent: THREE.Group, name: string) {
  const root = new THREE.Group();
  root.name = name;
  parent.add(root);
  const geometries: THREE.BufferGeometry[] = [],
    materials: THREE.Material[] = [],
    textures: THREE.Texture[] = [];
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
  function imagePlane(plane: CTPlane, place: (p: number[]) => number[]) {
    const data = Uint8Array.from(atob(plane.gray_u8), (c) => c.charCodeAt(0));
    if (data.length !== plane.width * plane.height) throw Error('Invalid CT plane');
    const rgba = new Uint8Array(data.length * 4);
    data.forEach((v, i) => rgba.set([v, v, v, 255], i * 4));
    const texture = new THREE.DataTexture(rgba, plane.width, plane.height, THREE.RGBAFormat);
    texture.colorSpace = THREE.SRGBColorSpace;
    texture.magFilter = THREE.LinearFilter;
    texture.needsUpdate = true;
    const geometry = new THREE.BufferGeometry();
    const corners = [
      [-0.5, -0.5],
      [plane.width - 0.5, -0.5],
      [plane.width - 0.5, plane.height - 0.5],
      [-0.5, plane.height - 0.5],
    ];
    geometry.setAttribute(
      'position',
      new THREE.Float32BufferAttribute(
        corners.flatMap(([u, v]) => place(planePoint(plane, u, v))),
        3,
      ),
    );
    geometry.setAttribute('uv', new THREE.Float32BufferAttribute([0, 0, 1, 0, 1, 1, 0, 1], 2));
    geometry.setIndex([0, 1, 2, 0, 2, 3]);
    const material = new THREE.MeshBasicMaterial({
      map: texture,
      side: THREE.DoubleSide,
      toneMapped: false,
      transparent: true,
      depthWrite: false,
    });
    const object = new THREE.Mesh(geometry, material);
    root.add(object);
    geometries.push(geometry);
    materials.push(material);
    textures.push(texture);
    return object;
  }
  function line(points: number[][], color: string, dashed = false) {
    const geometry = new THREE.BufferGeometry().setFromPoints(
      points.map((p) => new THREE.Vector3(p[0], p[1], p[2])),
    );
    const material = dashed
      ? new THREE.LineDashedMaterial({ color, dashSize: 3, gapSize: 2 })
      : new THREE.LineBasicMaterial({ color });
    const line = new THREE.Line(geometry, material);
    if (dashed) line.computeLineDistances();
    root.add(line);
    geometries.push(geometry);
    materials.push(material);
    return line;
  }
  function points(vertices: number[][], color: string) {
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices.flat(), 3));
    const material = new THREE.PointsMaterial({ color, size: 2, sizeAttenuation: false });
    const cloud = new THREE.Points(geometry, material);
    root.add(cloud);
    geometries.push(geometry);
    materials.push(material);
    return cloud;
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
  function fit(box: THREE.Box3, extent = 2.35) {
    const center = box.getCenter(new THREE.Vector3()),
      size = box.getSize(new THREE.Vector3());
    const scale = extent / Math.max(size.x, size.y, size.z);
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
    imagePlane,
    line,
    points,
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
      textures.forEach((t) => t.dispose());
      root.clear();
    },
  };
}
export function createPrototypeIdentityPrefab(parent: THREE.Group): NativeContent {
  const c = content(parent, 'prototype-identity-v1');
  const clouds = prototypePoints.map((points) => c.points(points, '#8c9589'));
  const display = c.fit(new THREE.Box3().setFromObject(c.root));
  return {
    update(state) {
      c.alive();
      if (state.recipe !== 'prototype-identity-v1')
        throw Error('Prototype identity state required');
      const rows = prototypeRows(state);
      clouds.forEach((cloud, i) => {
        cloud.material.color.set(rows[i].selected ? '#307f74' : '#8c9589');
        cloud.material.transparent = true;
        cloud.material.opacity = rows[i].selected ? 1 : 0.27;
        cloud.material.size = rows[i].selected ? 2.7 : 1.5;
        cloud.material.depthWrite = rows[i].selected;
      });
      const index = rows.findIndex((r) => r.selected),
        row = rows[index];
      const anchor = display(prototypeDisplay(prototypeObjects[index].centroid_lps_mm));
      return [
        {
          p: anchor,
          anchor,
          text: row.label ? `${row.objectId}: ${row.label} · source key` : row.objectId,
          color: '#307f74',
        },
      ];
    },
    dispose: c.dispose,
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
        point.visible = state.showDeformedTarget;
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
import { identityObjects, identityRows } from './identity';

export function createIdentityPrefab(parent: THREE.Group): NativeContent {
  const c = content(parent, 'anatomy-identity-v1');
  const meshes = identityObjects().map(({ part, objectId }) => ({
    objectId,
    mesh: c.mesh(part, '#b8b5a6'),
  }));
  const display = c.fit(new THREE.Box3().setFromObject(c.root));
  const anchors = meshes.map(({ mesh }) =>
    new THREE.Box3().setFromObject(mesh).getCenter(new THREE.Vector3()).toArray(),
  );
  return {
    update(state) {
      c.alive();
      if (state.recipe !== 'anatomy-identity-v1') throw Error('Identity state required');
      const rows = identityRows(state);
      meshes.forEach(({ mesh }, index) => {
        const selected = rows[index].selected;
        mesh.material.color.set(selected ? '#307f74' : '#b8b5a6');
        mesh.material.transparent = !selected;
        mesh.material.opacity = selected ? 1 : 0.3;
        mesh.material.depthWrite = selected;
      });
      const index = rows.findIndex((row) => row.selected);
      const row = rows[index];
      return [
        {
          p: display(anchors[index]),
          anchor: display(anchors[index]),
          text: row.label ? `${row.objectId} → ${row.label} · source reveal` : row.objectId,
          color: '#307f74',
        },
      ];
    },
    dispose: c.dispose,
  };
}

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

export function createMaskScreenPrefab(parent: THREE.Group): NativeContent {
  const c = content(parent, 'mask-screen-v1');
  function makeScene(key: ScreenKey) {
    const scene = screenGeometry[key];
    const clouds = scene.objects.map((o) =>
      c.points(o.points_lps_mm.map(screenDisplay), '#8c9589'),
    );
    const centroids = scene.objects.map((o) => {
      const dot = c.marker(screenDisplay(o.centroid_lps_mm), '#b77128');
      dot.scale.setScalar((screenBounds[key as ScreenKey].span * 0.009) / 0.0018);
      return dot;
    });
    const ordered = [...scene.objects].sort((a, b) => b.centroid_lps_mm[2] - a.centroid_lps_mm[2]);
    const line = c.line(
      ordered.map((o) => screenDisplay(o.centroid_lps_mm)),
      '#b77128',
      true,
    );
    return { clouds, centroids, line };
  }
  const scenes = {
    'ribs-32': makeScene('ribs-32'),
    'ribs-74': makeScene('ribs-74'),
    'organs-32': makeScene('organs-32'),
  };
  return {
    update(state) {
      c.alive();
      if (state.recipe !== 'mask-screen-v1') throw new Error('Recipe mismatch');
      const key = screenKey(state),
        rows = screenRows(state),
        bounds = screenBounds[key];
      const display = c.fit(
        new THREE.Box3(new THREE.Vector3(...bounds.low), new THREE.Vector3(...bounds.high)),
      );
      for (const name of Object.keys(scenes) as ScreenKey[]) {
        const scene = scenes[name];
        const objects = screenGeometry[name].objects;
        scene.clouds.forEach((cloud, i) => {
          cloud.visible = name === key;
          if (!cloud.visible) return;
          const row = rows.find((r) => r.id === objects[i].id)!;
          cloud.material.color.set(screenColor(row));
          cloud.material.transparent = true;
          cloud.material.opacity = row.selected || row.wrong ? 0.95 : 0.38;
          cloud.material.size = row.selected || row.wrong ? 2.7 : 1.8;
        });
        scene.centroids.forEach((dot) => {
          dot.visible = name === key && key !== 'organs-32' && state.measure > 0;
        });
        scene.line.visible = name === key && key !== 'organs-32' && state.measure > 0;
      }
      const row = rows.find((r) => r.selected)!;
      return [
        {
          text: `${row.id.split('-').at(-1)}${row.predicted ? ' → ' + row.predicted : ''}${row.source ? ' · source: ' + row.source : ''}`,
          p: display(screenDisplay(row.centroid_lps_mm)),
          anchor: display(screenDisplay(row.centroid_lps_mm)),
          color: screenColor(row),
        },
      ];
    },
    dispose: c.dispose,
  };
}

export function createCurationPrefab(parent: THREE.Group): NativeContent {
  const c = content(parent, 'anatomy-curation-v1');
  const scenes = (Object.keys(curationLayouts) as CurationState['scene'][]).map((key) => {
    const rows = curationLayouts[key];
    const clouds = rows.map((row) => c.points(row.points, '#8c9589'));
    const bounds = new THREE.Box3().setFromPoints(
      rows.flatMap((row) => row.points.map((p) => new THREE.Vector3(...p))),
    );
    return { key, clouds, bounds };
  });
  return {
    update(state) {
      c.alive();
      if (state.recipe !== 'anatomy-curation-v1') throw new Error('Recipe mismatch');
      const rows = curationRows(state);
      const display = c.fit(scenes.find((s) => s.key === state.scene)!.bounds);
      scenes.forEach((scene) =>
        scene.clouds.forEach((cloud, i) => {
          cloud.visible = scene.key === state.scene;
          if (!cloud.visible) return;
          cloud.material.color.set(curationColor(rows[i]));
          cloud.material.transparent = true;
          cloud.material.opacity = rows[i].selected ? 1 : 0.6;
          cloud.material.size = rows[i].selected ? 2.8 : 1.8;
        }),
      );
      const row = rows.find((r) => r.selected)!;
      return [
        {
          p: display(row.centroid),
          anchor: display(row.centroid),
          text: `${curationScanName(row.key)} · ${row.source ?? row.id}`,
          color: curationColor(row),
        },
      ];
    },
    dispose: c.dispose,
  };
}

/** Real calibrated CT planes and retained point outputs; no solver animation or inferred deformation. */
export function createRespiratoryPrefab(parent: THREE.Group): NativeContent {
  const c = content(parent, 'respiratory-v1');
  const scenes = [
    'inputs',
    'frame',
    'depth',
    'output',
    'reference',
    'judgment',
    'conditions',
    'limits',
  ] as const;
  const built = scenes.map((scene) => {
    const start = c.root.children.length;
    const source = (p: number[]) => respiratoryPlacement(scene, 'source', p),
      target = (p: number[]) => respiratoryPlacement(scene, 'target', p);
    const markers = (
      positions: number[][],
      color: string,
      place: (p: number[]) => number[],
      radius: number,
    ) =>
      positions.map((p) => {
        const m = c.marker(place(p), color);
        m.scale.setScalar(radius / 0.0018);
        m.material.emissive.set(color);
        m.material.emissiveIntensity = 0.35;
        m.material.transparent = true;
        m.material.depthTest = false;
        m.renderOrder = 20;
        return m;
      });
    let depth: THREE.Mesh<THREE.BufferGeometry, THREE.MeshBasicMaterial>[] = [];
    let returned: THREE.Mesh[] = [];
    const reveal: THREE.Object3D[] = [];
    const close = isRespiratoryCloseup(scene);
    if (close) {
      respiratory.target_returned_patch.forEach(
        (plane) => (c.imagePlane(plane, target).material.opacity = 0.65),
      );
      markers(
        [respiratoryOutput.points_world_mm[focusQuery]],
        respiratoryColors.returned,
        target,
        1.4,
      );
      const gt = respiratoryReference.truth.points_world_mm[focusQuery];
      reveal.push(...markers([gt], respiratoryColors.reference, target, 1.4));
      reveal.push(
        c.line(
          [respiratoryOutput.points_world_mm[focusQuery], gt].map(target),
          respiratoryColors.reference,
        ),
      );
      for (const [a, b] of [
        [0, 1],
        [0, 2],
        [1, 2],
      ])
        reveal.push(
          c.line(
            Array.from({ length: 65 }, (_, i) => {
              const p = [...gt],
                angle = (i / 64) * Math.PI * 2;
              p[a] += 5 * Math.cos(angle);
              p[b] += 5 * Math.sin(angle);
              return target(p);
            }),
            respiratoryColors.reference,
            true,
          ),
        );
    } else if (scene === 'conditions') {
      for (const [i, view] of [respiratory.views.patient1, respiratory.views.patient3].entries()) {
        const plane = view.plane;
        const place = (p: number[]) => {
          const delta = p.map((v, j) => v - plane.origin_world_mm[j]);
          const uv = [plane.dx_world_mm, plane.dy_world_mm].map(
            (axis) => delta.reduce((n, v, j) => n + v * axis[j], 0) / 1.25,
          );
          return [
            uv[0] - (plane.width * 1.25) / 2 + (i - 0.5) * 290,
            -uv[1] + (plane.height * 1.25) / 2,
            0,
          ];
        };
        c.imagePlane(plane, place);
        markers(view.source_world_mm, respiratoryColors.query, place, 2.5);
      }
    } else {
      c.imagePlane(respiratory.views.patient3.plane, source);
      markers(respiratory.views.patient3.source_world_mm, respiratoryColors.query, source, 4.5);
      depth = respiratory.source_sections.map((plane) => c.imagePlane(plane, source));
      respiratory.target_sections.forEach(
        (plane) => (c.imagePlane(plane, target).material.opacity = 0.75),
      );
      returned = markers(
        respiratoryOutput.points_world_mm,
        respiratoryColors.returned,
        target,
        4.5,
      );
    }
    reveal.forEach((o) => {
      if (o instanceof THREE.Line) {
        o.material.transparent = true;
        o.material.depthTest = false;
        o.renderOrder = 30;
      }
    });
    const objects = c.root.children.slice(start);
    const box = new THREE.Box3();
    objects.forEach((o) => box.union(new THREE.Box3().setFromObject(o)));
    return { scene, objects, depth, returned, reveal, box };
  });
  return {
    update(state) {
      c.alive();
      if (state.recipe !== 'respiratory-v1') throw Error('Respiratory state required');
      built.forEach((item) => {
        item.objects.forEach((o) => (o.visible = item.scene === state.scene));
        if (item.scene !== state.scene) return;
        item.depth.forEach((o) => {
          o.visible = state.depth > 0;
          o.material.opacity = 0.55 * state.depth;
        });
        item.returned.forEach((o, i) => (o.visible = i < Math.floor(state.output * 8 + 1e-8)));
        item.reveal.forEach((o) => (o.visible = state.reference > 0.5));
      });
      const item = built.find((s) => s.scene === state.scene)!;
      const display = c.fit(item.box, isRespiratoryCloseup(state.scene) ? 2.35 : 3.6);
      if (state.scene === 'frame') {
        const anchor = display(
          respiratoryPlacement(
            state.scene,
            'source',
            respiratory.views.patient3.source_world_mm[focusQuery],
          ),
        );
        return [
          {
            anchor,
            p: [anchor[0], anchor[1] - 0.35, anchor[2]] as ScenePoint,
            text: 'q06 · source',
            color: respiratoryColors.query,
          },
        ];
      }
      return [];
    },
    dispose: c.dispose,
  };
}

/** Actual saved airway geometry; reveal never mutates input masks or synthesizes a repair. */
export function createAirwayRepairPrefab(parent: THREE.Group): NativeContent {
  const c = content(parent, 'airway-repair-v1');
  const built = airwayCases.map((row, index) => {
    const place = (p: readonly number[]) => airwayDisplay(p, index);
    const mapped = (m: IndexedMesh) => ({ vertices: m.vertices.map(place), faces: m.faces });
    const start = c.root.children.length;
    const original = c.mesh(mapped(airwayMasks[row.mesh_key]), airwayColors.input);
    original.material.transparent = true;
    original.material.opacity = 0.65;
    original.material.depthWrite = false;
    const added = c.mesh(mapped(airwayOutput[index].added_mesh), airwayColors.output);
    const core = c.mesh(mapped(airwayReference[index].core_mesh), airwayColors.reference);
    core.material.transparent = true;
    core.material.opacity = 0.38;
    core.material.depthWrite = false;
    const line = c.line(airwayOutput[index].route.map(place), airwayColors.output);
    const refLine = c.line(
      airwayReference[index].reference_path.map(place),
      airwayColors.reference,
      true,
    );
    for (const l of [line, refLine]) {
      l.material.depthTest = false;
      l.renderOrder = 20;
    }
    const markers = row.anchors.map((p) => {
      const m = c.marker(place(p), airwayColors.anchor);
      m.scale.setScalar(0.55 / 0.0018);
      m.material.depthTest = false;
      m.renderOrder = 22;
      return m;
    });
    const cursor = c.marker(place(airwayOutput[index].route[0]), airwayColors.output);
    cursor.scale.setScalar(0.5 / 0.0018);
    cursor.material.depthTest = false;
    cursor.renderOrder = 23;
    const sections = row.sections.map((p) => c.imagePlane(p, place));
    sections.forEach((p) => {
      p.material.opacity = 0.7;
    });
    const ribbons = airwayOutput[index].cpr.map((angle) => {
      const edges = angle.sampling_edges;
      const objects = [0, 1].map((side) =>
        c.line(
          edges.map((e) => place(e[side])),
          airwayColors.output,
        ),
      );
      objects.push(c.line(edges[Math.floor(edges.length / 2)].map(place), airwayColors.output));
      return objects;
    });
    const bounds = airwayBounds(index);
    const box = new THREE.Box3(new THREE.Vector3(...bounds.low), new THREE.Vector3(...bounds.high));
    return {
      objects: c.root.children.slice(start),
      added,
      core,
      line,
      refLine,
      markers,
      cursor,
      sections,
      ribbons,
      box,
    };
  });
  return {
    update(state) {
      c.alive();
      if (state.recipe !== 'airway-repair-v1') throw Error('Airway repair state required');
      const index = airwayCaseIndex(state);
      built.forEach((item, i) => {
        item.objects.forEach((o) => {
          o.visible = i === index;
        });
        if (i !== index) return;
        item.added.visible = airwayReturned(state);
        item.line.visible = airwayReturned(state) && !['repair', 'inspect'].includes(state.scene);
        item.core.visible = item.refLine.visible = airwayReveal(state);
        item.cursor.visible = state.scene === 'route' && airwayReturned(state);
        item.cursor.position.fromArray(
          airwayDisplay(airwayOutput[index].route[airwayRouteIndex(state)], index),
        );
        item.sections.forEach((o, j) => {
          o.visible = state.scene === 'inspect' && j === airwaySliceIndex(state);
        });
        item.ribbons.forEach((objects, j) =>
          objects.forEach((o) => {
            o.visible =
              state.scene === 'cpr' && airwayReturned(state) && j === airwayAngleIndex(state);
          }),
        );
      });
      const display = c.fit(built[index].box, 2.3);
      return airwayCases[index].anchors.map((p, j) => {
        const anchor = display(airwayDisplay(p, index));
        return {
          anchor,
          p: [anchor[0] + 0.14, anchor[1] + (j ? -0.08 : 0.08), anchor[2]] as ScenePoint,
          text: j ? 'B' : 'A',
          color: airwayColors.anchor,
        };
      });
    },
    dispose: c.dispose,
  };
}
