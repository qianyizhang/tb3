// One shared offscreen context draws smooth surfaces for every player. The
// visible Canvas retains labels, annotations, accessibility and a 2D fallback.
export const SceneSurfaces = (() => {
  let renderer;
  function create() {
    const canvas = document.createElement('canvas');
    const gl = canvas.getContext('webgl', {
      alpha: true,
      antialias: true,
      premultipliedAlpha: true,
      preserveDrawingBuffer: true,
    });
    if (!gl) return null;
    canvas.addEventListener('webglcontextlost', () => {
      renderer = null;
    });
    const shader = (type, source) => {
      const value = gl.createShader(type);
      gl.shaderSource(value, source);
      gl.compileShader(value);
      if (!gl.getShaderParameter(value, gl.COMPILE_STATUS)) throw Error(gl.getShaderInfoLog(value));
      return value;
    };
    const vertex = shader(
      gl.VERTEX_SHADER,
      `
      attribute vec3 position;
      attribute vec3 normal;
      attribute vec4 color;
      attribute float lit;
      uniform vec4 angles;
      uniform vec2 scale;
      varying vec3 n;
      varying vec4 material;
      varying float lighting;
      vec3 rotate(vec3 p) {
        float x = p.x * angles.x + p.z * angles.y;
        float z = -p.x * angles.y + p.z * angles.x;
        return vec3(x, p.y * angles.z - z * angles.w, p.y * angles.w + z * angles.z);
      }
      void main() {
        vec3 p = rotate(position);
        float w = 1.0 - p.z / 7.0;
        gl_Position = vec4(p.x * scale.x, p.y * scale.y + 0.04 * w, -p.z / 7.0, w);
        n = rotate(normal / max(length(normal), 0.0001));
        material = color;
        lighting = lit;
      }
    `,
    );
    const fragment = shader(
      gl.FRAGMENT_SHADER,
      `
      precision mediump float;
      varying vec3 n;
      varying vec4 material;
      varying float lighting;
      void main() {
        vec3 rgb = material.rgb;
        if (lighting > 0.5) {
          vec3 normal = n / max(length(n), 0.0001);
          if (normal.z < 0.0) normal = -normal;
          vec3 key = normalize(vec3(-0.45, 0.8, 1.0));
          float diffuse = max(dot(normal, key), 0.0);
          float fill = max(dot(normal, normalize(vec3(0.8, 0.1, 0.6))), 0.0);
          float sheen = pow(max(dot(normal, normalize(key + vec3(0.0, 0.0, 1.0))), 0.0), 28.0);
          vec3 base = mix(pow(rgb, vec3(2.2)), vec3(0.87), 0.25);
          rgb = pow(base * (0.36 + 0.50 * diffuse + 0.14 * fill) + 0.035 * sheen, vec3(1.0 / 2.2));
        }
        gl_FragColor = vec4(rgb * material.a, material.a);
      }
    `,
    );
    const program = gl.createProgram();
    gl.attachShader(program, vertex);
    gl.attachShader(program, fragment);
    gl.linkProgram(program);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS))
      throw Error(gl.getProgramInfoLog(program));
    gl.deleteShader(vertex);
    gl.deleteShader(fragment);
    gl.useProgram(program);
    const attributes = [
      ['position', 3, 0],
      ['normal', 3, 3],
      ['color', 4, 6],
      ['lit', 1, 10],
    ].map(([name, size, offset]) => [gl.getAttribLocation(program, name), size, offset]);
    const angles = gl.getUniformLocation(program, 'angles');
    const scale = gl.getUniformLocation(program, 'scale');
    const cache = new Map(),
      colors = new Map();
    const upload = (faces) => {
      const count = faces.reduce((sum, face) => sum + (face.points.length - 2) * 3, 0);
      const data = new Float32Array(count * 11);
      let cursor = 0;
      for (const face of faces) {
        if (!colors.has(face.color))
          colors.set(
            face.color,
            face.color.match(/[0-9a-f]{2}/gi).map((v) => parseInt(v, 16) / 255),
          );
        const rgb = colors.get(face.color);
        for (let i = 1; i < face.points.length - 1; i++)
          for (const index of [0, i, i + 1]) {
            data.set(face.points[index], cursor);
            data.set(face.normals?.[index] || [0, 0, 1], cursor + 3);
            data.set(rgb, cursor + 6);
            data[cursor + 9] = face.alpha;
            data[cursor + 10] = face.surface ? 1 : 0;
            cursor += 11;
          }
      }
      const buffer = gl.createBuffer();
      gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
      gl.bufferData(gl.ARRAY_BUFFER, data, gl.STATIC_DRAW);
      return { buffer, count };
    };
    const draw = ({ buffer, count }) => {
      gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
      for (const [location, size, offset] of attributes) {
        gl.enableVertexAttribArray(location);
        gl.vertexAttribPointer(location, size, gl.FLOAT, false, 44, offset * 4);
      }
      gl.drawArrays(gl.TRIANGLES, 0, count);
    };
    const drop = (model) => {
      const buffers = cache.get(model);
      if (!buffers) return;
      gl.deleteBuffer(buffers.backdrop.buffer);
      gl.deleteBuffer(buffers.opaque.buffer);
      cache.delete(model);
    };
    return {
      drop,
      paint(ctx, model, view) {
        if (gl.isContextLost()) return false;
        const { width, height, ratio, zoom, cy, sy, cx, sx } = view;
        const w = Math.round(width * ratio),
          h = Math.round(height * ratio);
        if (canvas.width !== w || canvas.height !== h) {
          canvas.width = w;
          canvas.height = h;
        }
        if (!cache.has(model)) {
          const faces = model.primitives.filter((p) => p.type === 'face');
          cache.set(model, {
            backdrop: upload(faces.filter((p) => p.backdrop)),
            opaque: upload(faces.filter((p) => !p.backdrop && p.alpha === 1)),
            transparent: faces.filter((p) => !p.backdrop && p.alpha < 1),
          });
          if (cache.size > 6) drop(cache.keys().next().value);
        }
        const buffers = cache.get(model);
        gl.viewport(0, 0, w, h);
        gl.clearColor(0, 0, 0, 0);
        gl.depthMask(true);
        gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
        gl.uniform4f(angles, cy, sy, cx, sx);
        gl.uniform2f(scale, (2 * zoom) / width, (2 * zoom) / height);
        gl.disable(gl.BLEND);
        gl.disable(gl.DEPTH_TEST);
        draw(buffers.backdrop);
        gl.clear(gl.DEPTH_BUFFER_BIT);
        gl.enable(gl.DEPTH_TEST);
        draw(buffers.opaque);
        if (buffers.transparent.length) {
          const depth = (face) =>
            face.points.reduce((sum, p) => sum + p[1] * sx + (-p[0] * sy + p[2] * cy) * cx, 0) /
            face.points.length;
          const transparent = upload([...buffers.transparent].sort((a, b) => depth(a) - depth(b)));
          gl.enable(gl.BLEND);
          gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);
          gl.depthMask(false);
          draw(transparent);
          gl.deleteBuffer(transparent.buffer);
        }
        ctx.drawImage(canvas, 0, 0, width, height);
        return true;
      },
    };
  }
  return {
    draw(ctx, model, view) {
      if (renderer === undefined) {
        try {
          renderer = create();
        } catch {
          renderer = null;
        }
      }
      return renderer?.paint(ctx, model, view) || false;
    },
    release(model) {
      renderer?.drop(model);
    },
  };
})();
