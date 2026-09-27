import * as THREE from 'three';
import { content } from './operation-prefabs';
import type { NativeContent } from './stage';
import {
  cavityCases,
  cavityColors as colors,
  cavitySelection,
  cavityFrameLabel,
  decodeCavity,
  type CavityKey,
  type CavityMesh,
} from './clinical-cavity';

/** Rotate local (X,Y,Z) to display (X,Z,-Y), without registration or framewise rescaling. */
const display = (p: number[], shift = 0) => [p[0] + shift, p[2], -p[1]];
export function createClinicalCavityPrefab(parent: THREE.Group): NativeContent {
  const c = content(parent, 'clinical-cavity-v1');
  const built = (Object.keys(cavityCases) as CavityKey[]).map((key) => {
    const data = cavityCases[key],
      initial = decodeCavity(data.initial);
    const geometry = {
      vertices: Array.from({ length: data.initial.vertices }, (_, i) =>
        display(Array.from(initial.frames[0].subarray(i * 3, i * 3 + 3))),
      ),
      faces: Array.from({ length: initial.faces.length / 3 }, (_, i) =>
        Array.from(initial.faces.subarray(i * 3, i * 3 + 3)),
      ),
    };
    const helper = c.mesh(geometry, colors.helper);
    const output = c.mesh(geometry, colors.output);
    const reference = c.mesh(geometry, colors.reference);
    const planes = data.planes.map((plane) => {
      const frames = plane.frames.map((frame) => {
        const gray = Uint8Array.from(atob(frame.gray_u8), (x) => x.charCodeAt(0));
        const rgba = new Uint8Array(gray.length * 4);
        gray.forEach((v, i) => rgba.set([v, v, v, 255], i * 4));
        return rgba;
      });
      const object = c.imagePlane(
        {
          ...plane,
          ...plane.frames[0],
          origin_world_mm: plane.origin_mm,
          dx_world_mm: plane.dx_mm,
          dy_world_mm: plane.dy_mm,
        },
        display,
      );
      object.material.opacity = 0.86;
      return { object, frames };
    });
    return { key, data, helper, output, reference, planes };
  });
  function updateMesh(
    object: THREE.Mesh<THREE.BufferGeometry, THREE.MeshStandardMaterial>,
    mesh: CavityMesh,
    frame: number,
    shift: number,
  ) {
    const values = decodeCavity(mesh).frames[frame];
    const target = object.geometry.getAttribute('position') as THREE.BufferAttribute;
    for (let i = 0; i < mesh.vertices; i++)
      target.setXYZ(i, values[i * 3] + shift, values[i * 3 + 2], -values[i * 3 + 1]);
    target.needsUpdate = true;
    object.geometry.computeVertexNormals();
    object.geometry.computeBoundingSphere();
  }
  let last = '';
  return {
    update(state) {
      c.alive();
      if (state.recipe !== 'clinical-cavity-v1') throw Error('Wrong cavity state');
      const s = cavitySelection(state),
        pair = ['reference', 'patient', 'preserved', 'judgment', 'output'].includes(state.scene);
      const cacheKey = `${s.key}:${s.outputKey}:${s.frame}:${s.imageFrame}:${pair}:${s.reveal}:${state.helper > 0.5}:${state.output > 0.5}`;
      if (last !== cacheKey) {
        last = cacheKey;
        built.forEach((b) => {
          const active = b.key === s.key;
          b.helper.visible = active && state.helper > 0.5;
          b.output.visible = active && state.output > 0.5;
          b.reference.visible = active && s.reveal;
          b.planes.forEach((p) => {
            p.object.visible = active && state.output <= 0.5 && !pair;
          });
          if (!active) return;
          const shift = pair ? 58 : 0;
          updateMesh(b.output, s.output, s.frame, -shift);
          updateMesh(b.reference, s.reference, s.refFrame, shift);
          b.planes.forEach((p) => {
            (p.object.material.map as THREE.DataTexture).image.data = p.frames[s.imageFrame];
            p.object.material.map!.needsUpdate = true;
          });
        });
      }
      const [lo, hi] = s.data.bounds_mm,
        shift = pair ? 58 : 0;
      const box = new THREE.Box3(
        new THREE.Vector3(lo[0] - shift, lo[2], -hi[1]),
        new THREE.Vector3(hi[0] + shift, hi[2], -lo[1]),
      );
      const project = c.fit(box, 2.35);
      const annotations = pair
        ? [{ p: project([0, hi[2] + 5, 0]), text: cavityFrameLabel(state), color: '#4a5960' }]
        : [];
      if (state.output > 0.5)
        annotations.push({
          p: project([-shift, lo[2] - 5, 0]),
          text: `${state.scene === 'judgment' ? 'Static helper control' : 'Saved output'} · ${s.output.volume_ml[s.frame].toFixed(1)} mL`,
          color: '#09838d',
        });
      if (s.reveal)
        annotations.push({
          p: project([shift, lo[2] - 5, 0]),
          text: `Private reference · ${s.reference.volume_ml[s.refFrame].toFixed(1)} mL`,
          color: '#95620f',
        });
      return annotations;
    },
    dispose: c.dispose,
  };
}
