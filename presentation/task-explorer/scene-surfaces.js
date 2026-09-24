import * as THREE from 'three';

// Retained scene recipes produce triangles in a shared physical frame. Three
// owns the camera, lighting and depth buffer. The visible Canvas owns labels
// and remains the fallback when WebGL2 is unavailable.
export const SceneSurfaces = (() => {
  let stage;

  function geometry(faces) {
    const triangles = faces.reduce((sum, face) => sum + face.points.length - 2, 0);
    const positions = new Float32Array(triangles * 9);
    const normals = new Float32Array(triangles * 9);
    const colors = new Float32Array(triangles * 9);
    let cursor = 0;
    faces.forEach((face) => {
      const color = new THREE.Color(face.color);
      for (let i = 1; i < face.points.length - 1; i++)
        for (const index of [0, i, i + 1]) {
          positions.set(face.points[index], cursor);
          normals.set(face.normals?.[index] || [0, 0, 1], cursor);
          colors.set(color.toArray(), cursor);
          cursor += 3;
        }
    });
    const result = new THREE.BufferGeometry();
    result.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    result.setAttribute('normal', new THREE.BufferAttribute(normals, 3));
    result.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    return result;
  }

  function create() {
    const canvas = document.createElement('canvas');
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
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.15;
    const scene = new THREE.Scene();
    const pitch = new THREE.Group();
    const yaw = new THREE.Group();
    pitch.add(yaw);
    scene.add(pitch);
    scene.add(new THREE.HemisphereLight(0xffffff, 0xb1b2a8, 1.25));
    const key = new THREE.DirectionalLight(0xffffff, 1.55);
    key.position.set(-3, 5, 7);
    scene.add(key);
    const rim = new THREE.DirectionalLight(0xe4eff0, 0.45);
    rim.position.set(4, 1, -4);
    scene.add(rim);
    const camera = new THREE.PerspectiveCamera(32, 1, 0.1, 60);
    camera.position.set(0, 0, 7);
    camera.lookAt(0, 0, 0);
    const material = new THREE.MeshStandardMaterial({
      vertexColors: true,
      roughness: 0.88,
      metalness: 0,
      side: THREE.DoubleSide,
    });
    const backdropMaterial = new THREE.MeshBasicMaterial({
      vertexColors: true,
      side: THREE.DoubleSide,
      depthTest: false,
      depthWrite: false,
    });
    const flatMaterial = new THREE.MeshBasicMaterial({
      vertexColors: true,
      side: THREE.DoubleSide,
    });
    const cache = new Map();
    const clear = (model) => {
      const meshes = cache.get(model);
      if (!meshes) return;
      meshes.forEach((mesh) => {
        yaw.remove(mesh);
        mesh.geometry.dispose();
        if (
          mesh.material !== material &&
          mesh.material !== backdropMaterial &&
          mesh.material !== flatMaterial
        )
          mesh.material.dispose();
      });
      cache.delete(model);
    };
    canvas.addEventListener('webglcontextlost', (event) => {
      event.preventDefault();
      stage = null;
    });
    return {
      clear,
      paint(ctx, model, view) {
        if (gl.isContextLost()) return false;
        const { width, height, ratio, zoom, cy, sy, cx, sx } = view;
        renderer.setSize(
          Math.max(1, Math.round(width * ratio)),
          Math.max(1, Math.round(height * ratio)),
          false,
        );
        camera.aspect = width / height;
        camera.fov = (2 * Math.atan(height / (14 * zoom)) * 180) / Math.PI;
        camera.updateProjectionMatrix();
        yaw.rotation.y = Math.atan2(sy, cy);
        pitch.rotation.x = Math.atan2(sx, cx);
        if (!cache.has(model)) {
          const meshes = [];
          for (const [faces, faceMaterial, order] of [
            [
              model.primitives.filter((p) => p.type === 'face' && p.backdrop && p.alpha === 1),
              backdropMaterial,
              -1,
            ],
            [
              model.primitives.filter(
                (p) => p.type === 'face' && p.surface && p.alpha === 1 && !p.backdrop,
              ),
              material,
              0,
            ],
            [
              model.primitives.filter(
                (p) => p.type === 'face' && !p.surface && p.alpha === 1 && !p.backdrop,
              ),
              flatMaterial,
              0,
            ],
          ]) {
            if (!faces.length) continue;
            const mesh = new THREE.Mesh(geometry(faces), faceMaterial);
            mesh.renderOrder = order;
            meshes.push(mesh);
            yaw.add(mesh);
          }
          for (const face of model.primitives.filter((p) => p.type === 'face' && p.alpha < 1)) {
            const transparentMaterial = new THREE.MeshBasicMaterial({
              vertexColors: true,
              side: THREE.DoubleSide,
              transparent: true,
              opacity: face.alpha,
              depthWrite: false,
            });
            const center = face.points[0].map(
              (_, axis) =>
                face.points.reduce((sum, point) => sum + point[axis], 0) / face.points.length,
            );
            const faceGeometry = geometry([face]);
            faceGeometry.translate(-center[0], -center[1], -center[2]);
            const mesh = new THREE.Mesh(faceGeometry, transparentMaterial);
            mesh.position.set(...center);
            mesh.renderOrder = 1;
            meshes.push(mesh);
            yaw.add(mesh);
          }
          cache.set(model, meshes);
          if (cache.size > 6) clear(cache.keys().next().value);
        }
        for (const [cached, meshes] of cache)
          meshes.forEach((mesh) => (mesh.visible = cached === model));
        renderer.render(scene, camera);
        ctx.drawImage(canvas, 0, 0, width, height);
        return true;
      },
    };
  }
  return {
    draw(ctx, model, view) {
      if (stage === undefined) {
        try {
          stage = create();
        } catch {
          stage = null;
        }
      }
      return stage?.paint(ctx, model, view) || false;
    },
    release(model) {
      stage?.clear(model);
    },
  };
})();
