import type { StoryPlan } from '../types';
/** Absolute integer frames; no previous state, playing flag or clock dependence. */
export function sampleStory(plan: StoryPlan, requested: number) {
  if (!Number.isSafeInteger(requested)) throw new RangeError('Expected integer story frame');
  const frame = Math.max(0, Math.min(plan.durationFrames - 1, requested));
  const index = plan.beats.findIndex((b) => frame >= b.startFrame && frame < b.endFrame);
  if (index < 0) throw new Error('Timeline contains a gap');
  const common = {
    frame,
    index,
    beatId: plan.beats[index].id,
    caption: plan.beats[index].caption,
    narration: plan.beats[index].narration,
  };
  const beat = plan.beats[index];
  const progress = (frame - beat.startFrame) / Math.max(1, beat.endFrame - beat.startFrame - 1);
  const eased = progress * progress * (3 - 2 * progress);
  const channel = (pair: readonly number[]) => pair[0] + (pair[1] - pair[0]) * eased;
  switch (plan.recipe) {
    case 'route-unfold-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        context: channel(b.context),
        route: channel(b.route),
        ribbon: channel(b.ribbon),
        cursor: channel(b.cursor),
        unfold: channel(b.unfold),
        output: channel(b.output),
      });
    }
    case 'topology-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        focus: channel(b.channels.focus),
        trace: channel(b.channels.trace),
        inventory: channel(b.channels.inventory),
      });
    }
    case 'correspondence-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        transform: channel(b.channels.transform),
        query: channel(b.channels.query),
        residual: channel(b.channels.residual),
      });
    }
    case 'shape-material-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        phase: channel(b.channels.phase),
        markers: channel(b.channels.markers),
        alternative: channel(b.channels.alternative),
      });
    }
    case 'longitudinal-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        visits: channel(b.channels.visits),
        links: channel(b.channels.links),
        coverage: channel(b.channels.coverage),
      });
    }
    case 'multiscale-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        viewport: channel(b.channels.viewport),
        selections: channel(b.channels.selections),
        coverage: channel(b.channels.coverage),
        outputs: channel(b.channels.outputs),
      });
    }
    case 'inverse-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        observations: channel(b.channels.observations),
        reconstruction: channel(b.channels.reconstruction),
        residual: channel(b.channels.residual),
      });
    }
    case 'anatomy-audit-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        focus: channel(b.channels.focus),
        evidence: channel(b.channels.evidence),
        output: channel(b.channels.output),
      });
    }
    case 'local-edit-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        domain: channel(b.channels.domain),
        correction: channel(b.channels.correction),
        control: channel(b.channels.control),
      });
    }
  }
}
export type StoryState = ReturnType<typeof sampleStory>;
export type RouteState = Extract<StoryState, { recipe: 'route-unfold-v1' }>;
