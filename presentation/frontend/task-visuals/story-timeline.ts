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
    case 'rex-topcow-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        view: b.channels.view[0] + (b.channels.view[1] - b.channels.view[0]) * progress,
        reference: channel(b.channels.reference),
      });
    }
    case 'automed-multiorgan-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        view: b.channels.view[0] + (b.channels.view[1] - b.channels.view[0]) * progress,
        reference: channel(b.channels.reference),
      });
    }
    case 'bcer-workflow-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        view: b.channels.view[0] + (b.channels.view[1] - b.channels.view[0]) * progress,
      });
    }
    case 'abra-annotation-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        view: b.channels.view[0] + (b.channels.view[1] - b.channels.view[0]) * progress,
        helper: channel(b.channels.helper),
        output: channel(b.channels.output),
        reference: channel(b.channels.reference),
      });
    }
    case 'ct-context-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        view: b.channels.view[0] + (b.channels.view[1] - b.channels.view[0]) * progress,
        output: channel(b.channels.output),
        reference: channel(b.channels.reference),
      });
    }
    case 'history-sourcing-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        view: b.channels.view[0] + (b.channels.view[1] - b.channels.view[0]) * progress,
        output: channel(b.channels.output),
        reference: channel(b.channels.reference),
      });
    }
    case 'mri-importer-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        view: b.channels.view[0] + (b.channels.view[1] - b.channels.view[0]) * progress,
        output: channel(b.channels.output),
        reference: channel(b.channels.reference),
      });
    }
    case 'localized-ct-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        view: b.channels.view[0] + (b.channels.view[1] - b.channels.view[0]) * progress,
        output: channel(b.channels.output),
        reference: channel(b.channels.reference),
      });
    }
    case 'aneurysm-localization-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        view: b.channels.view[0] + (b.channels.view[1] - b.channels.view[0]) * progress,
        output: channel(b.channels.output),
        reference: channel(b.channels.reference),
      });
    }
    case 'segmentation-calibration-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        view: b.channels.view[0] + (b.channels.view[1] - b.channels.view[0]) * progress,
        condition:
          b.channels.condition[0] + (b.channels.condition[1] - b.channels.condition[0]) * progress,
        box: channel(b.channels.box),
        output: channel(b.channels.output),
        reference: channel(b.channels.reference),
      });
    }
    case 'dental-v3-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        view: b.channels.view[0] + (b.channels.view[1] - b.channels.view[0]) * progress,
        helper: channel(b.channels.helper),
        transfer: channel(b.channels.transfer),
        output: channel(b.channels.output),
        reference: channel(b.channels.reference),
        stage: b.channels.stage[0] + (b.channels.stage[1] - b.channels.stage[0]) * progress,
      });
    }
    case 'dental-v2-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        view: b.channels.view[0] + (b.channels.view[1] - b.channels.view[0]) * progress,
        helper: channel(b.channels.helper),
        transfer: channel(b.channels.transfer),
        output: channel(b.channels.output),
        reference: channel(b.channels.reference),
        stage: b.channels.stage[0] + (b.channels.stage[1] - b.channels.stage[0]) * progress,
      });
    }
    case 'dental-original-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        view: b.channels.view[0] + (b.channels.view[1] - b.channels.view[0]) * progress,
        diagnostic: channel(b.channels.diagnostic),
        gate: b.channels.gate[0] + (b.channels.gate[1] - b.channels.gate[0]) * progress,
        output: channel(b.channels.output),
        reference: channel(b.channels.reference),
      });
    }
    case 'ct-organ-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        view: b.channels.view[0] + (b.channels.view[1] - b.channels.view[0]) * progress,
        output: channel(b.channels.output),
        reference: channel(b.channels.reference),
      });
    }
    case 'named-landmarks-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        view: channel(b.channels.view),
        output: channel(b.channels.output),
        reference: channel(b.channels.reference),
      });
    }
    case 'clinical-cavity-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        // Physical phase progresses linearly; reveal channels retain smooth easing.
        phase: b.channels.phase[0] + (b.channels.phase[1] - b.channels.phase[0]) * progress,
        helper: channel(b.channels.helper),
        output: channel(b.channels.output),
        reference: channel(b.channels.reference),
      });
    }
    case 'tiger-context-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        view: channel(b.channels.view),
        reference: channel(b.channels.reference),
      });
    }
    case 'hubmap-inventory-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        view: channel(b.channels.view),
        reference: channel(b.channels.reference),
      });
    }
    case 'longitudinal-ct-revised-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        view: channel(b.channels.view),
        reference: channel(b.channels.reference),
        output: channel(b.channels.output),
      });
    }
    case 'longitudinal-ct-original-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        view: channel(b.channels.view),
        reference: channel(b.channels.reference),
        output: channel(b.channels.output),
      });
    }
    case 'longitudinal-mri-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        view: channel(b.channels.view),
        reference: channel(b.channels.reference),
        output: channel(b.channels.output),
      });
    }
    case 'topbrain-screen-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        view: channel(b.channels.view),
        reference: channel(b.channels.reference),
        output: channel(b.channels.output),
      });
    }
    case 'airway-repair-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        view: channel(b.channels.view),
        reference: channel(b.channels.reference),
        output: channel(b.channels.output),
      });
    }
    case 'vessel-source-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        scan: channel(b.channels.scan),
        reference: channel(b.channels.reference),
        output: channel(b.channels.output),
      });
    }
    case 'resect-pilot-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        view: channel(b.channels.view),
        output: channel(b.channels.output),
        reference: channel(b.channels.reference),
      });
    }
    case 'resect-correspondence-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        scan: channel(b.channels.scan),
        helper: channel(b.channels.helper),
        output: channel(b.channels.output),
        reference: channel(b.channels.reference),
      });
    }
    case 'registration-analysis-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        reference: channel(b.channels.reference),
        bounds: channel(b.channels.bounds),
        curve: channel(b.channels.curve),
      });
    }
    case 'respiratory-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        depth: channel(b.channels.depth),
        output: channel(b.channels.output),
        reference: channel(b.channels.reference),
      });
    }
    case 'anatomy-curation-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        reference: channel(b.channels.reference),
        focus: channel(b.channels.focus),
      });
    }
    case 'mask-screen-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        measure: channel(b.channels.measure),
        prediction: channel(b.channels.prediction),
        reference: channel(b.channels.reference),
        focus: channel(b.channels.focus),
      });
    }
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
        operation: plan.operation,
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
        showDeformedTarget: b.show_deformed_target,
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
        operation: plan.operation,
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
    case 'anatomy-identity-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        focus: channel(b.channels.focus),
        inventory: channel(b.channels.inventory),
        reveal: channel(b.channels.reveal),
      });
    }
    case 'prototype-identity-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        focus: channel(b.channels.focus),
        inventory: channel(b.channels.inventory),
        reveal: channel(b.channels.reveal),
      });
    }
    case 'mixed-tissue-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        conditions: channel(b.channels.conditions),
        plane: channel(b.channels.plane),
        overlay: channel(b.channels.overlay),
        reference: channel(b.channels.reference),
        witness: channel(b.channels.witness),
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
