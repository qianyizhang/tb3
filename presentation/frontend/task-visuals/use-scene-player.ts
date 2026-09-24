import { useEffect, useRef, useState } from 'react';
import type { StoryPlan } from '../types';
import { sampleStory, type StoryState } from './story-timeline';
import { createRoutePrefab } from './route-prefab';
import { TaskSceneModels } from './recipes';
import { SceneStage } from './stage';
import type { Point, SceneModel, Stage, VisualEntry } from './types';

const DURATIONS = [2600, 4200, 3200];
const STARTS = [0, DURATIONS[0], DURATIONS[0] + DURATIONS[1]];
const TOTAL_MS = DURATIONS.reduce((sum, duration) => sum + duration, 0);
const INITIAL_YAW = -0.24,
  INITIAL_PITCH = 0.14;
interface PlayerState {
  storyState?: StoryState;
  stage: Stage;
  playing: boolean;
  fallback: boolean;
}
export interface PlayerActions {
  seekFrame(frame: number, canonical?: boolean): void;
  selectBeat(index: number): void;
  select(stage: Stage): void;
  toggle(): void;
  reset(): void;
  rotate(dx: number, dy: number): void;
  drag(active: boolean): void;
}
const INITIAL: PlayerState = { stage: 0, playing: false, fallback: false };

/** React owns UI state. The effect owns the GPU and a single on-demand animation clock. */
export function useScenePlayer(entry: VisualEntry, plan?: StoryPlan) {
  const root = useRef<HTMLDivElement>(null);
  const canvas = useRef<HTMLCanvasElement>(null);
  const annotations = useRef<HTMLDivElement>(null);
  const actions = useRef<PlayerActions | null>(null);
  const pointer = useRef<Point | null>(null);
  const [state, setState] = useState<PlayerState>(() => ({
    ...INITIAL,
    storyState: plan ? sampleStory(plan, 0) : undefined,
  }));
  useEffect(() => {
    const player = root.current,
      surface = canvas.current,
      labels = annotations.current;
    if (!player || !surface || !labels) return;
    const totalMs = plan ? (plan.durationFrames / plan.fps) * 1000 : TOTAL_MS;
    const storyFrame = () =>
      Math.min(plan!.durationFrames - 1, Math.floor((elapsed / 1000) * plan!.fps + 1e-8));
    let disposed = false,
      playing = false,
      visible = false,
      dragging = false,
      failed = false;
    let stage: Stage = 0,
      elapsed = 0,
      frame = 0,
      last = 0;
    const initialPitch = [
      'dynamic_mesh',
      'cardiac_material',
      'cardiac_contours',
      'cardiac_anchors',
    ].includes(entry.illustration.kind)
      ? 0.38
      : INITIAL_PITCH;
    let yaw = INITIAL_YAW,
      pitch = initialPitch,
      width = 0,
      height = 0;
    let model: SceneModel | null = null,
      modelStage = -1;
    let view: ReturnType<typeof SceneStage.create> = null;
    const sync = () => {
      if (!disposed)
        setState({
          stage,
          playing,
          fallback: failed,
          storyState: plan ? sampleStory(plan, storyFrame()) : undefined,
        });
    };
    const cancel = () => {
      if (frame) cancelAnimationFrame(frame);
      frame = 0;
      last = 0;
    };
    const fallback = () => {
      if (disposed || failed) return;
      failed = true;
      playing = false;
      cancel();
      sync();
      player.dataset.surfaceRenderer = plan ? 'poster' : 'svg';
      player.dataset.rendered = 'true';
    };
    const render = () => {
      if (disposed || failed || !view || !width || !height) return;
      if (plan) {
        const state = sampleStory(plan, storyFrame());
        if (!view.drawNative(state, { width, height, yaw, pitch })) return fallback();
        player.dataset.frame = String(state.frame);
        sync();
      } else {
        if (!model || modelStage !== stage || (playing && TaskSceneModels.animated(entry, stage))) {
          const progress = Math.max(0, Math.min(1, (elapsed - STARTS[stage]) / DURATIONS[stage]));
          model = TaskSceneModels.build(entry, stage, elapsed / 1000, progress);
          modelStage = stage;
        }
        if (!view.draw(model, { width, height, yaw, pitch })) return fallback();
      }
      // Capture diagnostics are not React state; no component renders per animation frame.
      player.dataset.surfaceRenderer = 'webgl';
      player.dataset.rendered = 'true';
      player.dataset.texturesReady = String(view.texturesReady);
      player.dataset.geometryUpdates = String(view.stats.updates);
      player.dataset.geometryRebuilds = String(view.stats.rebuilds);
      player.dataset.gpuGeometries = String(view.stats.geometries);
      player.dataset.nativeRoots = String(view.stats.nativeRoots);
    };
    const select = (next: Stage) => {
      stage = next;
      model = null;
    };
    const tick = (now: number) => {
      frame = 0;
      if (disposed || failed || !playing || !visible || document.hidden || dragging) {
        last = 0;
        return;
      }
      elapsed = Math.min(totalMs, elapsed + (last ? Math.min(80, now - last) : 0));
      last = now;
      const next = elapsed < STARTS[1] ? 0 : elapsed < STARTS[2] ? 1 : 2;
      if (!plan && stage !== next) {
        select(next);
        sync();
      }
      if (elapsed === totalMs) {
        playing = false;
        sync();
      }
      render();
      if (playing) frame = requestAnimationFrame(tick);
    };
    const start = () => {
      if (!frame && playing && visible && !document.hidden && !disposed && !failed && !dragging)
        frame = requestAnimationFrame(tick);
    };
    const pause = () => {
      playing = false;
      cancel();
      sync();
    };
    try {
      view = SceneStage.create(surface, labels, render, fallback);
      if (plan) view?.installNative(createRoutePrefab);
    } catch (error) {
      console.warn('3D task scene unavailable:', error);
      view?.dispose();
      view = null;
    }
    if (!view) {
      fallback();
      return;
    }
    sync();
    const seekFrame = (requested: number, canonical = false) => {
      if (
        !plan ||
        !Number.isSafeInteger(requested) ||
        requested < 0 ||
        requested >= plan.durationFrames
      )
        throw new RangeError('Invalid story frame');
      if (failed) throw new Error('WebGL capture unavailable');
      pause();
      elapsed = (requested / plan.fps) * 1000;
      if (canonical) {
        yaw = INITIAL_YAW;
        pitch = initialPitch;
      }
      const rect = surface.getBoundingClientRect();
      width = Math.round(rect.width);
      height = Math.round(rect.height);
      sync();
      render();
    };
    actions.current = {
      seekFrame,
      selectBeat(index) {
        if (!plan?.beats[index]) throw new RangeError('Invalid beat');
        seekFrame(plan.beats[index].startFrame);
      },
      select(next) {
        pause();
        elapsed = STARTS[next] + (next === 1 ? DURATIONS[1] * 0.45 : 0);
        select(next);
        sync();
        render();
      },
      toggle() {
        if (playing) return pause();
        if (
          (!plan && stage === 2) ||
          (plan && storyFrame() === plan.durationFrames - 1) ||
          elapsed >= totalMs
        ) {
          elapsed = 0;
          select(0);
        }
        playing = true;
        sync();
        render();
        start();
      },
      reset() {
        pause();
        yaw = INITIAL_YAW;
        pitch = initialPitch;
        elapsed = 0;
        select(0);
        sync();
        render();
      },
      rotate(dx, dy) {
        pause();
        yaw += dx;
        pitch = Math.max(-1.1, Math.min(1.1, pitch + dy));
        render();
      },
      drag(active) {
        dragging = active;
        if (active) pause();
      },
    };
    const resize = new ResizeObserver(() => {
      const rect = surface.getBoundingClientRect();
      width = Math.round(rect.width);
      height = Math.round(rect.height);
      render();
    });
    resize.observe(surface);
    const observer = new IntersectionObserver(([item]) => {
      visible = item.isIntersecting;
      if (visible) start();
      else cancel();
    });
    observer.observe(surface);
    const visibility = () => (document.hidden ? cancel() : start());
    document.addEventListener('visibilitychange', visibility);
    const media = matchMedia('(prefers-reduced-motion: reduce)');
    const preference = () => {
      if (media.matches) pause();
    };
    media.addEventListener('change', preference);
    return () => {
      disposed = true;
      cancel();
      actions.current = null;
      pointer.current = null;
      resize.disconnect();
      observer.disconnect();
      document.removeEventListener('visibilitychange', visibility);
      media.removeEventListener('change', preference);
      view?.dispose();
      model = null;
    };
  }, [entry, plan]);
  return { root, canvas, annotations, actions, pointer, ...state };
}
