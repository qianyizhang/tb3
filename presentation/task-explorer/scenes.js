import { TaskTeachingArt } from '../assets/teaching/task-art.js';
import { TaskTeachingStory } from '../assets/teaching/task-story.js';
import { AnatomyAssets } from './scene-anatomy.js';
import { TaskSceneModels } from './scene-models.js';
import { SceneStage } from './scene-stage.js';

const esc = (value) =>
  String(value ?? '').replace(
    /[&<>"']/g,
    (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char],
  );

// Task recipes live in scene-models.js. This module owns the accessible player.
export const TaskScenes = (() => {
  const STATIC_KINDS = new Set([
    'nuclei',
    'nodule_outline',
    'detect',
    'candidate_judgment',
    'classify',
    'multilabel',
    'report',
    'caption',
    'vqa',
    'quality',
    'tiles',
    'workflow',
    'viewer',
    'metadata',
    'records',
    'etl',
    'trials',
    'risk',
    'source_provenance',
    'denoise',
    'superres',
    'synthesis',
    'image_sequence',
    'segmenter_calibration',
    'astronomy',
    'astro_uncertainty',
    'astro_dynamic',
    'astro_features',
    'planet',
  ]);
  const DURATIONS = [2600, 4200, 3200];
  const STARTS = [0, DURATIONS[0], DURATIONS[0] + DURATIONS[1]];
  const TOTAL_MS = DURATIONS.reduce((sum, value) => sum + value, 0);
  const INITIAL_YAW = -0.24;
  const INITIAL_PITCH = 0.14;
  const clampPitch = (value) => Math.max(-1.1, Math.min(1.1, value));
  const ZH = {
    'Task at a glance': '任务概览',
    Given: '已提供',
    Input: '输入',
    'Expected output': '预期输出',
    'Study output': '研究输出',
    'Output shape': '输出形式',
    Output: '输出',
    Illustrative: '示意',
    'How to read this task': '如何阅读此任务',
    'Drag to explore in 3D': '拖动查看三维结构',
    'Illustration stage': '示意阶段',
    'Inspect input': '查看输入',
    Play: '播放',
    Pause: '暂停',
    Replay: '重播',
    Reset: '重置',
    'Play animation': '播放动画',
    'Pause animation': '暂停动画',
    'Replay illustration': '重播示意',
    'Reset illustration view': '重置视角',
    'Possible class labels': '可用类别标签',
    'About the anatomy models': '关于解剖模型',
    'Derivation and licenses': '来源与许可',
    'Conceptual · not to scale': '概念示意 · 非按比例',
    'Conceptual · not case-specific': '概念示意 · 非本例结果',
  };
  const ui = (locale, text) => (locale === 'zh-CN' ? ZH[text] || text : text);
  const languageNote = (locale) =>
    locale === 'zh-CN'
      ? '<p class="scene-language-note" lang="zh-CN">示意图细节保留英文原文。</p>'
      : '';

  function fallback(e, locale = 'en') {
    const d = e.illustration;
    return `<div class="picture-pair"><section><h4>${ui(locale, 'Input')}</h4>${TaskTeachingArt.render(e)}<p>${esc(d.input)}</p></section><div class="picture-arrow" aria-hidden="true">→</div><section><h4>${ui(locale, e.role && e.role !== 'task' ? 'Study output' : 'Expected output')}</h4>${TaskTeachingArt.render(e, true)}<p>${esc(d.output)}</p></section></div>`;
  }

  const mode = (e) => {
    const d = e.illustration;
    if (STATIC_KINDS.has(d?.kind)) return 'static';
    if (
      d?.kind === 'segment' &&
      d.target &&
      !AnatomyAssets.get(d.subject)?.some((part) => part.id === d.target) &&
      !AnatomyAssets.has(d.target)
    )
      return 'static';
    return '3d';
  };

  function staticFigure(e, locale) {
    const story = TaskTeachingStory.describe(e);
    const d = e.illustration;
    return `<div class="scene-static" data-scene="${esc(d.kind)}" data-scene-mode="static">${languageNote(locale)}<div class="scene-static-heading"><span>${ui(locale, 'How to read this task')}</span><strong lang="en">${esc(story.action)}</strong><p lang="en">${esc(story.cue)}</p></div>${fallback(e, locale)}<p class="scene-static-note" lang="en">${esc(d.caption)} <span>${ui(locale, 'Conceptual · not case-specific')}</span></p></div>`;
  }

  function figure(e, locale = 'en') {
    const d = e.illustration;
    if (!d || !TaskSceneModels.supports(d.kind)) return '';
    if (mode(e) === 'static') return staticFigure(e, locale);
    const story = TaskTeachingStory.describe(e);
    const outputLabel = e.role && e.role !== 'task' ? 'Study output' : 'Output shape';
    const storyboard = `<div class="scene-storyboard" aria-label="${ui(locale, 'Task at a glance')}"><section class="scene-story-card" data-story-step="0"><h4><span>01</span> ${ui(locale, 'Given')}</h4><div class="scene-story-art">${TaskTeachingArt.render(e)}</div><p lang="en">${esc(d.input)}</p></section><div class="scene-story-action" data-story-step="1"><span class="scene-story-action-index">02</span><span class="scene-story-arrow" aria-hidden="true">→</span><strong lang="en">${esc(story.action)}</strong><small lang="en">${esc(story.form)}</small></div><section class="scene-story-card" data-story-step="2"><h4><span>03</span> ${ui(locale, outputLabel)}<small>${ui(locale, 'Illustrative')}</small></h4><div class="scene-story-art">${TaskTeachingArt.render(e, true)}</div><p lang="en">${esc(d.output)}</p></section></div>`;
    const legend = TaskSceneModels.legend(e)
      .map(
        ([color, label, dashed]) =>
          `<span><i style="--key:${color};border-top-style:${dashed ? 'dashed' : 'solid'}"></i>${esc(label)}</span>`,
      )
      .join('');
    const anatomyNotice = TaskSceneModels.usesAnatomy(e)
      ? `<details class="scene-asset-notice"><summary>${ui(locale, 'About the anatomy models')}</summary><p lang="en">Reusable anatomy explains shape and spatial relationships. The same models are reused across tasks, rather than presented as a reconstruction or scored output for the selected case. Markers, lesions and motion remain illustrative.</p><p lang="en">Organ surfaces: Wasserthal and the TotalSegmentator contributors, University Hospital Basel. <a href="https://zenodo.org/records/10047263" target="_blank" rel="noopener">TotalSegmentator v2.0.1</a> · smoothed and simplified from public masks. Brain and dental shapes are authored schematics.</p><details><summary>${ui(locale, 'Derivation and licenses')}</summary><pre>${esc(AnatomyAssets.notice)}</pre></details></details>`
      : '';
    const labelSpace = d.labels?.length
      ? `<details class="scene-label-space"><summary>${ui(locale, 'Possible class labels')} (${d.labels.length})</summary><div>${d.labels.map((name) => `<span>${esc(name)}</span>`).join('')}</div></details>`
      : '';
    return `<div class="scene-player" data-scene="${esc(d.kind)}">${languageNote(locale)}${storyboard}<div class="scene-walkthrough-heading"><div><span class="scene-walkthrough-kicker">${ui(locale, 'How to read this task')}</span><strong lang="en">${esc(story.action)}</strong></div><p lang="en">${esc(story.cue)}</p></div><div class="scene-stage"><canvas class="scene-canvas" tabindex="0" role="img" aria-label="${esc(d.input + ' → ' + d.output + '. Conceptual 3D illustration. Drag or use arrow keys to rotate.')}" aria-describedby="scene-description">${esc(d.caption)}</canvas><div class="scene-annotations" aria-hidden="true"></div><div class="scene-corner"><span class="scene-dot"></span> <span lang="en">${esc(story.context)}</span></div><span class="scene-gesture" aria-hidden="true">${ui(locale, 'Drag to explore in 3D')}</span><span class="scene-stage-label" data-scene-stage-label>${esc(ui(locale, story.stages[0]))}</span></div><div class="scene-controls"><div class="scene-steps" role="group" aria-label="${ui(locale, 'Illustration stage')}"><button data-scene-step="0" aria-pressed="true"><small>01</small> ${ui(locale, 'Input')}</button><button data-scene-step="1" aria-pressed="false"><small>02</small> ${esc(story.action)}</button><button data-scene-step="2" aria-pressed="false"><small>03</small> ${ui(locale, e.role && e.role !== 'task' ? 'Study output' : 'Output')}</button></div><button class="scene-play" aria-label="${ui(locale, 'Play animation')}">${ui(locale, 'Play')}</button><button class="scene-reset" aria-label="${ui(locale, 'Reset illustration view')}">${ui(locale, 'Reset')}</button></div><div class="scene-explanation" id="scene-description" lang="en"><strong data-scene-title>${esc(d.input)}</strong><p>${esc(d.caption)}</p></div><div class="scene-legend" lang="en">${legend}<span>${ui(locale, 'Conceptual · not to scale')}</span></div>${labelSpace}${anatomyNotice}<div class="scene-fallback" hidden></div></div>`;
  }

  function mount(root, e, locale = 'en') {
    const player = root.querySelector('.scene-player');
    if (!player) return () => {};
    const story = TaskTeachingStory.describe(e);
    const canvas = player.querySelector('.scene-canvas');
    const labels = player.querySelector('.scene-annotations');
    const media = matchMedia('(prefers-reduced-motion: reduce)');
    let disposed = false;
    let playing = false;
    let visible = false;
    let stage = 0;
    let elapsed = 0;
    let yaw = INITIAL_YAW;
    let pitch = INITIAL_PITCH;
    let frame = 0;
    let last = 0;
    let drag = null;
    let model = null;
    let modelStage = -1;
    let width = 0;
    let height = 0;
    const buttons = [...player.querySelectorAll('[data-scene-step]')];
    const play = player.querySelector('.scene-play');
    const showFallback = () => {
      if (disposed || player.dataset.surfaceRenderer === 'svg') return;
      playing = false;
      if (frame) cancelAnimationFrame(frame);
      frame = 0;
      player.querySelector('.scene-storyboard').hidden = true;
      player.querySelector('.scene-stage').hidden = true;
      player.querySelector('.scene-controls').hidden = true;
      const view = player.querySelector('.scene-fallback');
      view.innerHTML = fallback(e, locale);
      view.hidden = false;
      player.dataset.surfaceRenderer = 'svg';
      player.dataset.rendered = 'true';
    };
    let stageView = null;
    try {
      stageView = SceneStage.create(canvas, labels, () => renderFrame(), showFallback);
    } catch (error) {
      console.warn('3D task scene unavailable:', error);
    }
    if (!stageView) {
      showFallback();
      return () => {};
    }
    const syncPlay = () => {
      play.textContent = ui(locale, playing ? 'Pause' : stage === 2 ? 'Replay' : 'Play');
      play.setAttribute(
        'aria-label',
        ui(
          locale,
          playing ? 'Pause animation' : stage === 2 ? 'Replay illustration' : 'Play animation',
        ),
      );
      player.dataset.playing = String(playing);
    };
    const setStage = (next) => {
      stage = next;
      model = null;
      player.dataset.stage = String(stage);
      player.querySelector('[data-scene-stage-label]').textContent = ui(
        locale,
        story.stages[stage],
      );
      player.querySelectorAll('[data-story-step]').forEach((item) => {
        item.dataset.active = String(Number(item.dataset.storyStep) === stage);
      });
      buttons.forEach((button, index) =>
        button.setAttribute('aria-pressed', String(index === stage)),
      );
      player.querySelector('[data-scene-title]').textContent = [
        e.illustration.input,
        story.action,
        e.illustration.output,
      ][stage];
    };
    function renderFrame() {
      if (disposed || !stageView || !width || player.dataset.surfaceRenderer === 'svg') return;
      if (!model || modelStage !== stage || (playing && TaskSceneModels.animated(e, stage))) {
        const progress = Math.max(0, Math.min(1, (elapsed - STARTS[stage]) / DURATIONS[stage]));
        model = TaskSceneModels.build(e, stage, elapsed / 1000, progress);
        modelStage = stage;
      }
      if (!stageView.draw(model, { width, height, yaw, pitch })) {
        showFallback();
        return;
      }
      player.dataset.surfaceRenderer = 'webgl';
      player.dataset.rendered = 'true';
      player.dataset.texturesReady = String(stageView.texturesReady);
      player.dataset.geometryUpdates = String(stageView.stats.updates);
      player.dataset.geometryRebuilds = String(stageView.stats.rebuilds);
    }
    const cancel = () => {
      if (frame) cancelAnimationFrame(frame);
      frame = 0;
      last = 0;
    };
    const tick = (now) => {
      frame = 0;
      if (disposed || !playing || !visible || document.hidden || drag) {
        last = 0;
        return;
      }
      elapsed = Math.min(TOTAL_MS, elapsed + (last ? Math.min(80, now - last) : 0));
      last = now;
      const next = elapsed < STARTS[1] ? 0 : elapsed < STARTS[2] ? 1 : 2;
      if (stage !== next) setStage(next);
      if (elapsed === TOTAL_MS) {
        playing = false;
        syncPlay();
      }
      renderFrame();
      if (playing) frame = requestAnimationFrame(tick);
    };
    const start = () => {
      if (!frame && playing && visible && !document.hidden && !disposed && !drag)
        frame = requestAnimationFrame(tick);
    };
    const pause = () => {
      playing = false;
      cancel();
      syncPlay();
    };
    buttons.forEach((button, index) => {
      button.onclick = () => {
        pause();
        elapsed = STARTS[index] + (index === 1 ? DURATIONS[1] * 0.45 : 0);
        setStage(index);
        syncPlay();
        renderFrame();
      };
    });
    play.onclick = () => {
      if (playing) return pause();
      if (stage === 2 || elapsed >= TOTAL_MS) {
        elapsed = 0;
        setStage(0);
      }
      playing = true;
      syncPlay();
      renderFrame();
      start();
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
      if (event.key === ' ') return play.click();
      pause();
      yaw += event.key === 'ArrowLeft' ? -0.15 : event.key === 'ArrowRight' ? 0.15 : 0;
      pitch = clampPitch(
        pitch + (event.key === 'ArrowUp' ? -0.12 : event.key === 'ArrowDown' ? 0.12 : 0),
      );
      renderFrame();
    };
    const resize = new ResizeObserver(() => {
      const rect = canvas.getBoundingClientRect();
      width = Math.round(rect.width);
      height = Math.round(rect.height);
      renderFrame();
    });
    resize.observe(canvas);
    const observer = new IntersectionObserver(([entry]) => {
      visible = entry.isIntersecting;
      if (visible) start();
      else cancel();
    });
    observer.observe(canvas);
    const visibility = () => (document.hidden ? cancel() : start());
    document.addEventListener('visibilitychange', visibility);
    const preference = () => {
      if (media.matches) pause();
    };
    media.addEventListener('change', preference);
    setStage(0);
    syncPlay();
    return () => {
      disposed = true;
      cancel();
      resize.disconnect();
      observer.disconnect();
      document.removeEventListener('visibilitychange', visibility);
      media.removeEventListener('change', preference);
      stageView.dispose();
      model = null;
    };
  }
  return { figure, mount, mode };
})();
