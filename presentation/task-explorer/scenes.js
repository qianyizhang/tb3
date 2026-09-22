import { TaskTeachingArt } from '../assets/teaching/task-art.js';
import { TaskTeachingStory } from '../assets/teaching/task-story.js';
import { AnatomyAssets } from './scene-anatomy.js';
import { TaskSceneModels } from './scene-models.js';
import { SceneSurfaces } from './scene-surfaces.js';

const esc = (value) =>
  String(value ?? '').replace(
    /[&<>"']/g,
    (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char],
  );

// Canvas rendering and playback. Task-specific geometry lives in scene-models.js.
export const TaskScenes = (() => {
  const TAU = Math.PI * 2;
  const DURATIONS = [2600, 4200, 3200];
  const STARTS = [0, DURATIONS[0], DURATIONS[0] + DURATIONS[1]];
  const TOTAL_MS = DURATIONS.reduce((sum, value) => sum + value, 0);
  const FADE_MS = 320;
  const INITIAL_YAW = -0.24,
    INITIAL_PITCH = 0.14;
  const clampPitch = (value) => Math.max(-1.1, Math.min(1.1, value));
  function fallback(e) {
    const d = e.illustration;
    return `<div class="picture-pair"><section><h4>Input</h4>${TaskTeachingArt.render(e)}<p>${esc(d.input)}</p></section><div class="picture-arrow" aria-hidden="true">→</div><section><h4>${e.role && e.role !== 'task' ? 'Study output' : 'Expected output'}</h4>${TaskTeachingArt.render(e, true)}<p>${esc(d.output)}</p></section></div>`;
  }
  function figure(e) {
    const d = e.illustration;
    if (!d || !TaskSceneModels.supports(d.kind)) return '';
    const story = TaskTeachingStory.describe(e);
    const outputLabel = e.role && e.role !== 'task' ? 'Study output' : 'Output shape';
    const storyboard = `<div class="scene-storyboard" aria-label="Task at a glance"><section class="scene-story-card" data-story-step="0"><h4><span>01</span> Given</h4><div class="scene-story-art">${TaskTeachingArt.render(e)}</div><p>${esc(d.input)}</p></section><div class="scene-story-action" data-story-step="1"><span class="scene-story-action-index">02</span><span class="scene-story-arrow" aria-hidden="true">→</span><strong>${esc(story.action)}</strong><small>${esc(story.form)}</small></div><section class="scene-story-card" data-story-step="2"><h4><span>03</span> ${outputLabel}<small>Illustrative</small></h4><div class="scene-story-art">${TaskTeachingArt.render(e, true)}</div><p>${esc(d.output)}</p></section></div>`;
    const legend = TaskSceneModels.legend(e)
      .map(
        ([color, label, dashed]) =>
          `<span><i style="--key:${color};border-top-style:${dashed ? 'dashed' : 'solid'}"></i>${esc(label)}</span>`,
      )
      .join('');
    const anatomyNotice = TaskSceneModels.usesAnatomy(e)
      ? `<details class="scene-asset-notice"><summary>About the anatomy models</summary><p>Reusable anatomy explains shape and spatial relationships. The same models are reused across tasks, rather than presented as a reconstruction or scored output for the selected case. Markers, lesions and motion remain illustrative.</p><p>Organ surfaces: Wasserthal and the TotalSegmentator contributors, University Hospital Basel. <a href="https://zenodo.org/records/10047263" target="_blank" rel="noopener">TotalSegmentator v2.0.1</a> · smoothed and simplified from public masks. Brain and dental shapes are authored schematics.</p><details><summary>Derivation and licenses</summary><pre>${esc(AnatomyAssets.notice)}</pre></details></details>`
      : '';
    const labelSpace = d.labels?.length
      ? `<details class="scene-label-space"><summary>Possible class labels (${d.labels.length})</summary><div>${d.labels.map((name) => `<span>${esc(name)}</span>`).join('')}</div></details>`
      : '';
    return `<div class="scene-player" data-scene="${esc(d.kind)}">${storyboard}<div class="scene-walkthrough-heading"><div><span class="scene-walkthrough-kicker">How to read this task</span><strong>${esc(story.action)}</strong></div><p>${esc(story.cue)}</p></div><div class="scene-stage"><canvas class="scene-canvas" tabindex="0" role="img" aria-label="${esc(d.input + ' → ' + d.output + '. Conceptual 3D illustration. Drag or use arrow keys to rotate.')}" aria-describedby="scene-description">${esc(d.caption)}</canvas><div class="scene-corner"><span class="scene-dot"></span> <span>${esc(story.context)}</span></div><span class="scene-gesture" aria-hidden="true">Drag to explore in 3D</span><span class="scene-stage-label" data-scene-stage-label>${esc(story.stages[0])}</span></div><div class="scene-controls"><div class="scene-steps" role="group" aria-label="Illustration stage"><button data-scene-step="0" aria-pressed="true"><small>01</small> Input</button><button data-scene-step="1" aria-pressed="false"><small>02</small> ${esc(story.action)}</button><button data-scene-step="2" aria-pressed="false"><small>03</small> ${e.role && e.role !== 'task' ? 'Study output' : 'Output'}</button></div><button class="scene-play" aria-label="Pause animation">Pause</button><button class="scene-reset" aria-label="Reset illustration view">Reset</button></div><div class="scene-explanation" id="scene-description"><strong data-scene-title>${esc(d.input)}</strong><p>${esc(d.caption)}</p></div><div class="scene-legend">${legend}<span>Conceptual · not to scale</span></div>${labelSpace}${anatomyNotice}<div class="scene-fallback" hidden></div></div>`;
  }

  function mount(root, e) {
    const player = root.querySelector('.scene-player');
    if (!player) return () => {};
    const story = TaskTeachingStory.describe(e);
    const canvas = player.querySelector('canvas'),
      ctx = canvas.getContext('2d');
    if (!ctx) {
      player.querySelector('.scene-storyboard').remove();
      player.querySelector('.scene-stage').hidden = true;
      player.querySelector('.scene-controls').hidden = true;
      const view = player.querySelector('.scene-fallback');
      view.innerHTML = fallback(e);
      view.hidden = false;
      return () => {};
    }
    const media = matchMedia('(prefers-reduced-motion: reduce)');
    let playing = !media.matches,
      visible = false,
      disposed = false,
      stage = 0,
      elapsed = 0,
      yaw = INITIAL_YAW,
      pitch = INITIAL_PITCH,
      frame = 0,
      last = 0,
      lastPaint = 0,
      drag = null,
      model = null,
      modelStage = -1,
      transition = null,
      dirty = true,
      width = 0,
      height = 0;
    const buttons = [...player.querySelectorAll('[data-scene-step]')],
      play = player.querySelector('.scene-play');
    const imageTextures = new Map();
    const texture = (subject) => {
      if (!imageTextures.has(subject)) {
        const picture = new Image();
        picture.onload = () => {
          if (disposed) return;
          dirty = true;
          renderFrame();
        };
        picture.src =
          'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(TaskTeachingArt.scan(subject));
        imageTextures.set(subject, picture);
      }
      return imageTextures.get(subject);
    };
    const drawImagePlane = (picture, corners) => {
      if (!picture.complete || !picture.naturalWidth) return;
      const source = [
        [0, 0],
        [320, 0],
        [320, 190],
        [0, 190],
      ];
      for (const indices of [
        [0, 1, 2],
        [0, 2, 3],
      ]) {
        const [a, b, c] = indices.map((i) => source[i]);
        const [u, v, w] = indices.map((i) => corners[i]);
        const det = (b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1]);
        const ax = ((v[0] - u[0]) * (c[1] - a[1]) - (w[0] - u[0]) * (b[1] - a[1])) / det;
        const ay = ((v[1] - u[1]) * (c[1] - a[1]) - (w[1] - u[1]) * (b[1] - a[1])) / det;
        const bx = ((w[0] - u[0]) * (b[0] - a[0]) - (v[0] - u[0]) * (c[0] - a[0])) / det;
        const by = ((w[1] - u[1]) * (b[0] - a[0]) - (v[1] - u[1]) * (c[0] - a[0])) / det;
        ctx.save();
        ctx.beginPath();
        ctx.moveTo(u[0], u[1]);
        ctx.lineTo(v[0], v[1]);
        ctx.lineTo(w[0], w[1]);
        ctx.closePath();
        ctx.clip();
        ctx.transform(ax, ay, bx, by, u[0] - ax * a[0] - bx * a[1], u[1] - ay * a[0] - by * a[1]);
        ctx.drawImage(picture, 0, 0, 320, 190);
        ctx.restore();
      }
    };
    const setStage = (n, fade = false) => {
      transition = null;
      if (fade && stage !== n && width && !media.matches) {
        const previous = document.createElement('canvas');
        previous.width = canvas.width;
        previous.height = canvas.height;
        previous.getContext('2d').drawImage(canvas, 0, 0);
        transition = { canvas: previous, age: 0 };
      }
      stage = n;
      dirty = true;
      player.dataset.stage = String(n);
      player.querySelector('[data-scene-stage-label]').textContent = story.stages[n];
      player.querySelectorAll('[data-story-step]').forEach((item) => {
        item.dataset.active = String(Number(item.dataset.storyStep) === n);
      });
      buttons.forEach((b, i) => b.setAttribute('aria-pressed', String(i === n)));
      player.querySelector('[data-scene-title]').textContent = [
        e.illustration.input,
        story.action,
        e.illustration.output,
      ][n];
    };
    const syncPlay = () => {
      play.textContent = playing ? 'Pause' : stage === 2 ? 'Replay' : 'Play';
      play.setAttribute(
        'aria-label',
        playing ? 'Pause animation' : stage === 2 ? 'Replay illustration' : 'Play animation',
      );
      player.dataset.playing = String(playing);
    };
    const renderFrame = () => {
      if (disposed || !width) return;
      const t = elapsed / 1000,
        turn = yaw,
        cy = Math.cos(turn),
        sy = Math.sin(turn),
        cx = Math.cos(pitch),
        sx = Math.sin(pitch);
      const zoom = Math.min(width / 5.25, height / 3.5);
      const project = (p) => {
        const x = p[0] * cy + p[2] * sy,
          z = -p[0] * sy + p[2] * cy,
          y = p[1] * cx - z * sx,
          depth = p[1] * sx + z * cx,
          perspective = 7 / (7 - depth);
        return [
          width / 2 + x * zoom * perspective,
          height * 0.48 - y * zoom * perspective,
          depth,
          perspective,
        ];
      };
      ctx.clearRect(0, 0, width, height);
      const glow = ctx.createRadialGradient(
        width * 0.49,
        height * 0.45,
        0,
        width * 0.5,
        height * 0.5,
        width * 0.58,
      );
      glow.addColorStop(0, '#ffffff');
      glow.addColorStop(1, '#eff3ee');
      ctx.fillStyle = glow;
      ctx.fillRect(0, 0, width, height);
      // One quiet studio background for surfaces, image plates and evidence cards.
      // A soft contact shadow replaces decorative grids and orbital rings.
      ctx.save();
      ctx.translate(width * 0.5, height * 0.86);
      ctx.scale(1, 0.16);
      const shadow = ctx.createRadialGradient(0, 0, 0, 0, 0, width * 0.25);
      shadow.addColorStop(0, '#385c5422');
      shadow.addColorStop(0.55, '#385c5410');
      shadow.addColorStop(1, '#385c5400');
      ctx.fillStyle = shadow;
      ctx.fillRect(-width * 0.3, -width * 0.3, width * 0.6, width * 0.6);
      ctx.restore();
      const animated = TaskSceneModels.animated(e, stage);
      if (!model || modelStage !== stage || animated) {
        if (model) SceneSurfaces.release(model);
        const progress = Math.max(0, Math.min(1, (elapsed - STARTS[stage]) / DURATIONS[stage]));
        model = TaskSceneModels.build(e, stage, t, progress);
        modelStage = stage;
      }
      const accelerated = SceneSurfaces.draw(ctx, model, {
        width,
        height,
        ratio: Math.min(devicePixelRatio || 1, 2),
        zoom,
        cy,
        sy,
        cx,
        sx,
      });
      player.dataset.surfaceRenderer = accelerated ? 'webgl' : 'canvas';
      const projected = model.primitives
        .filter((item) => !accelerated || item.type !== 'face')
        .map((item) => {
          const p = item.points.map(project);
          return { ...item, p, depth: p.reduce((sum, v) => sum + v[2], 0) / p.length };
        })
        .sort((a, b) => {
          // Annotation marks stay legible on opaque forms (e.g. a vessel node
          // or a nucleus center); surface depth still determines physical occlusion.
          const layer = (item) => (item.backdrop ? -1 : item.type === 'face' ? 0 : 1);
          return layer(a) - layer(b) || a.depth - b.depth;
        });
      const brightness = new Map(),
        colors = new Map();
      const lighting = (normal) => {
        if (brightness.has(normal)) return brightness.get(normal);
        const length = Math.hypot(...normal) || 1,
          nx = (normal[0] * cy + normal[2] * sy) / length,
          nz = (-normal[0] * sy + normal[2] * cy) / length,
          ny = (normal[1] / length) * cx - nz * sx,
          depth = (normal[1] / length) * sx + nz * cx;
        const light = 0.5 + 0.5 * Math.abs(-0.38 * nx + 0.6 * ny + 0.7 * depth);
        brightness.set(normal, light);
        return light;
      };
      projected.forEach((item) => {
        if (item.type === 'image') {
          ctx.globalAlpha = item.alpha;
          drawImagePlane(texture(item.subject), item.p);
          return;
        }
        let shade = item.color;
        if (item.surface) {
          if (!colors.has(item.color))
            colors.set(
              item.color,
              item.color.match(/[0-9a-f]{2}/gi).map((n) => parseInt(n, 16)),
            );
          const rgb = colors.get(item.color),
            levels = item.normals.map(lighting),
            color = (level) =>
              `rgb(${rgb.map((n) => Math.round((n * 0.55 + 245 * 0.45) * level)).join(',')})`,
            [a, b, c] = item.p,
            low = Math.min(...levels),
            high = Math.max(...levels),
            dx1 = b[0] - a[0],
            dy1 = b[1] - a[1],
            dx2 = c[0] - a[0],
            dy2 = c[1] - a[1],
            det = dx1 * dy2 - dx2 * dy1;
          shade = color((low + high) / 2);
          if (Math.abs(det) > 0.01 && high - low > 0.01) {
            const gx = ((levels[1] - levels[0]) * dy2 - (levels[2] - levels[0]) * dy1) / det,
              gy = (dx1 * (levels[2] - levels[0]) - dx2 * (levels[1] - levels[0])) / det,
              magnitude = gx * gx + gy * gy;
            if (magnitude > 1e-10) {
              const start = (low - levels[0]) / magnitude,
                end = (high - levels[0]) / magnitude;
              const gradient = ctx.createLinearGradient(
                a[0] + gx * start,
                a[1] + gy * start,
                a[0] + gx * end,
                a[1] + gy * end,
              );
              gradient.addColorStop(0, color(low));
              gradient.addColorStop(1, color(high));
              shade = gradient;
            }
          }
        }
        ctx.globalAlpha = item.alpha;
        ctx.strokeStyle = item.color;
        ctx.fillStyle = shade;
        ctx.lineWidth = item.width || 1;
        ctx.setLineDash(item.dash ? [4, 4] : []);
        ctx.beginPath();
        if (item.type === 'dot') {
          const p = item.p[0];
          ctx.arc(p[0], p[1], Math.max(1.4, item.radius * zoom * p[3]), 0, TAU);
          if (item.radius * zoom > 2) {
            ctx.save();
            ctx.strokeStyle = '#f7faf5';
            ctx.lineWidth = 2.5;
            ctx.stroke();
            ctx.restore();
          }
          ctx.fill();
        } else {
          item.p.forEach((p, i) => (i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])));
          if (item.type === 'face') {
            ctx.closePath();
            ctx.fill();
            if (item.surface && item.alpha === 1) {
              // Close subpixel seams with the same lit material, without dense wire clutter.
              ctx.strokeStyle = shade;
              ctx.lineWidth = 0.45;
              ctx.stroke();
            }
          } else ctx.stroke();
        }
      });
      ctx.globalAlpha = 1;
      ctx.setLineDash([]);
      ctx.font = `${Math.max(10, Math.min(12, width / 47))}px system-ui,sans-serif`;
      ctx.textBaseline = 'middle';
      model.labels.forEach(({ p, text, color, anchor }) => {
        const v = project(p),
          tw = ctx.measureText(text).width,
          x = Math.max(8, Math.min(width - tw - 8, v[0] - tw / 2)),
          y = Math.max(35, Math.min(height - 18, v[1]));
        if (anchor) {
          const a = project(anchor);
          ctx.strokeStyle = color;
          ctx.lineWidth = 1.4;
          ctx.beginPath();
          ctx.moveTo(a[0], a[1]);
          ctx.lineTo(x + tw / 2, y);
          ctx.stroke();
          ctx.beginPath();
          ctx.arc(a[0], a[1], 3, 0, TAU);
          ctx.fillStyle = color;
          ctx.fill();
        }
        ctx.fillStyle = '#f6f8f2ed';
        ctx.fillRect(x - 4, y - 9, tw + 8, 18);
        ctx.fillStyle = color;
        ctx.fillText(text, x, y);
      });
      if (transition) {
        const p = Math.min(1, transition.age / FADE_MS);
        ctx.globalAlpha = 1 - p * p * (3 - 2 * p);
        ctx.drawImage(transition.canvas, 0, 0, width, height);
        ctx.globalAlpha = 1;
      }
      dirty = false;
      player.dataset.rendered = 'true';
      player.dataset.texturesReady = String(
        [...imageTextures.values()].every(
          (picture) => picture.complete && picture.naturalWidth > 0,
        ),
      );
    };
    const cancel = () => {
      if (frame) cancelAnimationFrame(frame);
      frame = 0;
      last = 0;
    };
    const tick = (now) => {
      frame = 0;
      if (disposed || (!playing && !transition) || !visible || document.hidden || drag) {
        last = 0;
        return;
      }
      const delta = last ? Math.min(80, now - last) : 0;
      last = now;
      if (playing) {
        elapsed = Math.min(TOTAL_MS, elapsed + delta);
        const next = elapsed < STARTS[1] ? 0 : elapsed < STARTS[2] ? 1 : 2;
        if (stage !== next) setStage(next, true);
        if (elapsed === TOTAL_MS) {
          playing = false;
          dirty = true;
          syncPlay();
        }
      }
      if (transition) {
        transition.age += delta;
        if (transition.age >= FADE_MS) {
          transition = null;
          dirty = true;
        }
      }
      if (now - lastPaint >= 1000 / 60 - 0.5 || !playing) {
        if (dirty || transition || TaskSceneModels.animated(e, stage)) renderFrame();
        lastPaint = now;
      }
      if (playing || transition) frame = requestAnimationFrame(tick);
    };
    const start = () => {
      if (!frame && (playing || transition) && visible && !document.hidden && !disposed && !drag)
        frame = requestAnimationFrame(tick);
    };
    const pause = () => {
      playing = false;
      transition = null;
      cancel();
      syncPlay();
    };
    buttons.forEach(
      (b, i) =>
        (b.onclick = () => {
          pause();
          setStage(i, true);
          elapsed = STARTS[i] + (i === 1 ? DURATIONS[1] * 0.45 : 0);
          syncPlay();
          renderFrame();
          start();
        }),
    );
    play.onclick = () => {
      if (playing) pause();
      else {
        if (stage === 2 || elapsed >= TOTAL_MS) {
          setStage(0, true);
          elapsed = 0;
        }
        playing = true;
        syncPlay();
        renderFrame();
        start();
      }
    };
    player.querySelector('.scene-reset').onclick = () => {
      pause();
      yaw = INITIAL_YAW;
      pitch = INITIAL_PITCH;
      elapsed = 0;
      setStage(0);
      syncPlay();
      renderFrame();
    };
    canvas.onpointerdown = (event) => {
      if (event.button !== 0) return;
      pause();
      drag = [event.clientX, event.clientY];
      canvas.setPointerCapture(event.pointerId);
      canvas.classList.add('dragging');
    };
    canvas.onpointermove = (event) => {
      if (!drag) return;
      yaw += (event.clientX - drag[0]) * 0.008;
      pitch = clampPitch(pitch + (event.clientY - drag[1]) * 0.007);
      drag = [event.clientX, event.clientY];
      renderFrame();
    };
    canvas.onpointerup =
      canvas.onpointercancel =
      canvas.onlostpointercapture =
        () => {
          drag = null;
          canvas.classList.remove('dragging');
        };
    canvas.onkeydown = (event) => {
      if (!['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', ' '].includes(event.key)) return;
      event.preventDefault();
      if (event.key === ' ') {
        play.click();
        return;
      }
      pause();
      yaw += event.key === 'ArrowLeft' ? -0.15 : event.key === 'ArrowRight' ? 0.15 : 0;
      pitch = clampPitch(
        pitch + (event.key === 'ArrowUp' ? -0.12 : event.key === 'ArrowDown' ? 0.12 : 0),
      );
      renderFrame();
    };
    const resize = new ResizeObserver(() => {
      const rect = canvas.getBoundingClientRect();
      width = rect.width;
      height = rect.height;
      const ratio = Math.min(devicePixelRatio || 1, 2);
      canvas.width = Math.round(width * ratio);
      canvas.height = Math.round(height * ratio);
      ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
      renderFrame();
    });
    resize.observe(canvas);
    const observer = new IntersectionObserver(([entry]) => {
      visible = entry.isIntersecting;
      if (visible) start();
      else cancel();
    });
    observer.observe(canvas);
    const visibility = () => {
      if (document.hidden) cancel();
      else start();
    };
    document.addEventListener('visibilitychange', visibility);
    const preference = () => {
      if (media.matches) {
        pause();
        renderFrame();
      }
    };
    media.addEventListener('change', preference);
    setStage(0);
    syncPlay();
    start();
    return () => {
      disposed = true;
      cancel();
      resize.disconnect();
      observer.disconnect();
      document.removeEventListener('visibilitychange', visibility);
      media.removeEventListener('change', preference);
      if (model) SceneSurfaces.release(model);
      imageTextures.forEach((picture) => {
        picture.onload = null;
      });
      imageTextures.clear();
      model = null;
      transition = null;
    };
  }
  return { figure, mount };
})();
