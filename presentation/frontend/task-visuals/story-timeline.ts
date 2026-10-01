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
    case 'imaging101-eht-original-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        view: b.channels.view[0] + (b.channels.view[1] - b.channels.view[0]) * progress,
        reference: channel(b.channels.reference),
      });
    }
    case 'imaging101-eht-features-dynamic-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        view: b.channels.view[0] + (b.channels.view[1] - b.channels.view[0]) * progress,
        reference: channel(b.channels.reference),
      });
    }
    case 'imaging101-eht-dynamic-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        view: b.channels.view[0] + (b.channels.view[1] - b.channels.view[0]) * progress,
        reference: channel(b.channels.reference),
      });
    }
    case 'imaging101-eht-uq-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        view: b.channels.view[0] + (b.channels.view[1] - b.channels.view[0]) * progress,
        reference: channel(b.channels.reference),
      });
    }
    case 'imaging101-dti-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        view: b.channels.view[0] + (b.channels.view[1] - b.channels.view[0]) * progress,
        reference: channel(b.channels.reference),
      });
    }
    case 'imaging101-deflectometry-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        view: b.channels.view[0] + (b.channels.view[1] - b.channels.view[0]) * progress,
        reference: channel(b.channels.reference),
      });
    }
    case 'imaging101-fan-beam-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        view: b.channels.view[0] + (b.channels.view[1] - b.channels.view[0]) * progress,
        reference: channel(b.channels.reference),
      });
    }
    case 'imaging101-dual-energy-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        view: b.channels.view[0] + (b.channels.view[1] - b.channels.view[0]) * progress,
        reference: channel(b.channels.reference),
      });
    }
    case 'imaging101-ptychography-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        view: b.channels.view[0] + (b.channels.view[1] - b.channels.view[0]) * progress,
        reference: channel(b.channels.reference),
      });
    }
    case 'imaging101-nlos-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        view: b.channels.view[0] + (b.channels.view[1] - b.channels.view[0]) * progress,
        reference: channel(b.channels.reference),
      });
    }
    case 'imaging101-cars-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        view: b.channels.view[0] + (b.channels.view[1] - b.channels.view[0]) * progress,
        reference: channel(b.channels.reference),
      });
    }
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
    case 'cardiac-contour-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        phase: b.channels.phase[0] + (b.channels.phase[1] - b.channels.phase[0]) * progress,
        helper: channel(b.channels.helper),
        output: channel(b.channels.output),
        reference: channel(b.channels.reference),
      });
    }
    case 'cardiac-real-echo-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        phase: b.channels.phase[0] + (b.channels.phase[1] - b.channels.phase[0]) * progress,
        planes: channel(b.channels.planes),
        output: channel(b.channels.output),
        alternative: channel(b.channels.alternative),
        review: channel(b.channels.review),
        control: channel(b.channels.control),
      });
    }
    case 'cardiac-mask-mechanics-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        phase: b.channels.phase[0] + (b.channels.phase[1] - b.channels.phase[0]) * progress,
        condition: channel(b.channels.condition),
        output: channel(b.channels.output),
        reference: channel(b.channels.reference),
        clinical: channel(b.channels.clinical),
      });
    }
    case 'report-reading-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        phase: b.channels.phase[0] + (b.channels.phase[1] - b.channels.phase[0]) * progress,
        helper: channel(b.channels.helper),
        output: channel(b.channels.output),
        reference: channel(b.channels.reference),
      });
    }
    case 'automed-kidney-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        view: b.channels.view[0] + (b.channels.view[1] - b.channels.view[0]) * progress,
        helper: channel(b.channels.helper),
        step: channel(b.channels.step),
        reference: channel(b.channels.reference),
        fixture: channel(b.channels.fixture),
      });
    }
    case 'bcer-brain-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        view: channel(b.channels.view),
      });
    }
    case 'bcer-prostate-registration-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        view: channel(b.channels.view),
        moving: channel(b.channels.moving),
        operation: channel(b.channels.operation),
        swap: channel(b.channels.swap),
      });
    }
    case 'abra-longitudinal-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        baseline: channel(b.channels.baseline),
        followup: channel(b.channels.followup),
        task: channel(b.channels.task),
        reference: channel(b.channels.reference),
      });
    }
    case 'rexmle-dentex-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        box: channel(b.channels.box),
        labels: channel(b.channels.labels),
        reference: channel(b.channels.reference),
      });
    }
    case 'rex-isles22-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        slice: channel(b.channels.slice),
        flair: channel(b.channels.flair),
        reference: channel(b.channels.reference),
      });
    }
    case 'rexmle-neurips-cellseg-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        helper: channel(b.channels.helper),
        instance: channel(b.channels.instance),
        metric: channel(b.channels.metric),
      });
    }
    case 'rex-panther-task1-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        grid: channel(b.channels.grid),
        reference: channel(b.channels.reference),
      });
    }
    case 'rex-panther-task2-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        grid: channel(b.channels.grid),
        reference: channel(b.channels.reference),
      });
    }
    case 'rexmle-puma-track1-task1-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        helper: channel(b.channels.helper),
        focus: channel(b.channels.focus),
        metric: channel(b.channels.metric),
      });
    }
    case 'rexmle-puma-track1-task2-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        helper: channel(b.channels.helper),
        focus: channel(b.channels.focus),
        metric: channel(b.channels.metric),
      });
    }
    case 'rexmle-puma-track2-task2-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        helper: channel(b.channels.helper),
        focus: channel(b.channels.focus),
        metric: channel(b.channels.metric),
      });
    }
    case 'rex-seg-a-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        slice: channel(b.channels.slice),
        reference: channel(b.channels.reference),
      });
    }
    case 'rex-topbrain-ct-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        slice: channel(b.channels.slice),
        reference: channel(b.channels.reference),
      });
    }
    case 'rex-topbrain-mr-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        slice: channel(b.channels.slice),
        reference: channel(b.channels.reference),
      });
    }
    case 'rex-topcow-mr-seg-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        slice: channel(b.channels.slice),
        reference: channel(b.channels.reference),
      });
    }
    case 'rex-topcow-ct-box-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        slice: channel(b.channels.slice),
        step: channel(b.channels.step),
        reference: channel(b.channels.reference),
      });
    }
    case 'rex-topcow-mr-box-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        slice: channel(b.channels.slice),
        step: channel(b.channels.step),
        reference: channel(b.channels.reference),
      });
    }
    case 'rex-topcow-ct-edges-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        slice: channel(b.channels.slice),
        step: channel(b.channels.step),
        reference: channel(b.channels.reference),
      });
    }
    case 'rex-topcow-mr-edges-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        slice: channel(b.channels.slice),
        step: channel(b.channels.step),
        reference: channel(b.channels.reference),
      });
    }
    case 'automed-full-bccd-detection-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        scan: channel(b.channels.scan),
        format: channel(b.channels.format),
        reference: channel(b.channels.reference),
      });
    }
    case 'automed-full-dentex-detection-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        scan: channel(b.channels.scan),
        format: channel(b.channels.format),
        reference: channel(b.channels.reference),
      });
    }
    case 'automed-full-grazpedwri-detection-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        scan: channel(b.channels.scan),
        format: channel(b.channels.format),
        reference: channel(b.channels.reference),
      });
    }
    case 'automed-full-vindr-cxr-detection-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        scan: channel(b.channels.scan),
        format: channel(b.channels.format),
        reference: channel(b.channels.reference),
      });
    }
    case 'automed-full-aeropath-seg-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        slice: channel(b.channels.slice),
        format: channel(b.channels.format),
        reference: channel(b.channels.reference),
      });
    }
    case 'automed-full-colon-seg-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        slice: channel(b.channels.slice),
        format: channel(b.channels.format),
        reference: channel(b.channels.reference),
      });
    }
    case 'automed-full-feta-seg-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        slice: channel(b.channels.slice),
        format: channel(b.channels.format),
        reference: channel(b.channels.reference),
      });
    }
    case 'automed-full-heart-seg-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        slice: channel(b.channels.slice),
        format: channel(b.channels.format),
        reference: channel(b.channels.reference),
      });
    }
    case 'automed-full-hepaticvessel-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        view: channel(b.channels.view),
        class: channel(b.channels.class),
        reference: channel(b.channels.reference),
      });
    }
    case 'automed-full-kidney-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        view: channel(b.channels.view),
        class: channel(b.channels.class),
        reference: channel(b.channels.reference),
      });
    }
    case 'automed-full-liver-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        view: channel(b.channels.view),
        class: channel(b.channels.class),
        reference: channel(b.channels.reference),
      });
    }
    case 'automed-full-pancreas-oar-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        view: channel(b.channels.view),
        class: channel(b.channels.class),
        reference: channel(b.channels.reference),
      });
    }
    case 'automed-full-pancreas-seg-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        slice: channel(b.channels.slice),
        helper: channel(b.channels.helper),
        output: channel(b.channels.output),
      });
    }
    case 'automed-full-panther-t1-seg-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        slice: channel(b.channels.slice),
        helper: channel(b.channels.helper),
        output: channel(b.channels.output),
      });
    }
    case 'automed-full-panther-t2-seg-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        slice: channel(b.channels.slice),
        helper: channel(b.channels.helper),
        output: channel(b.channels.output),
      });
    }
    case 'automed-full-prostate-seg-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        slice: channel(b.channels.slice),
        helper: channel(b.channels.helper),
        output: channel(b.channels.output),
      });
    }
    case 'automed-full-spleen-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        view: channel(b.channels.view),
        label: channel(b.channels.label),
        reference: channel(b.channels.reference),
      });
    }
    case 'automed-full-tsg-multiorgan-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        view: channel(b.channels.view),
        label: channel(b.channels.label),
        reference: channel(b.channels.reference),
      });
    }
    case 'healthagentbench-ct-findings-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        cursor: channel(b.channels.cursor),
        detail: channel(b.channels.detail),
        reference: channel(b.channels.reference),
      });
    }
    case 'radagent-report-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        cursor: channel(b.channels.cursor),
        detail: channel(b.channels.detail),
        reference: channel(b.channels.reference),
      });
    }
    case 'healthagentbench-tumor-tiles-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        cursor: channel(b.channels.cursor),
        detail: channel(b.channels.detail),
        reference: channel(b.channels.reference),
      });
    }
    case 'healthagentbench-cxr-correction-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        cursor: channel(b.channels.cursor),
        detail: channel(b.channels.detail),
        reference: channel(b.channels.reference),
      });
    }
    case 'abra-viewer-control-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        progress: channel(b.channels.progress),
        detail: channel(b.channels.detail),
        reference: channel(b.channels.reference),
      });
    }
    case 'abra-metadata-qa-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        progress: channel(b.channels.progress),
        detail: channel(b.channels.detail),
        reference: channel(b.channels.reference),
      });
    }
    case 'abra-vision-probe-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        progress: channel(b.channels.progress),
        detail: channel(b.channels.detail),
        reference: channel(b.channels.reference),
      });
    }
    case 'abra-birads-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        progress: channel(b.channels.progress),
        detail: channel(b.channels.detail),
        reference: channel(b.channels.reference),
      });
    }
    case 'radagent-vqa-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        progress: channel(b.channels.progress),
        detail: channel(b.channels.detail),
        reference: channel(b.channels.reference),
      });
    }
    case 'rex-ldct-iqa-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        progress: channel(b.channels.progress),
        detail: channel(b.channels.detail),
        reference: channel(b.channels.reference),
      });
    }
    case 'automed-brain-cls-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        progress: channel(b.channels.progress),
        detail: channel(b.channels.detail),
        reference: channel(b.channels.reference),
      });
    }
    case 'automed-pneumonia-cls-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        progress: channel(b.channels.progress),
        detail: channel(b.channels.detail),
        reference: channel(b.channels.reference),
      });
    }
    case 'automed-crc-cls-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        progress: channel(b.channels.progress),
        detail: channel(b.channels.detail),
        reference: channel(b.channels.reference),
      });
    }
    case 'automed-pcam-cls-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        progress: channel(b.channels.progress),
        detail: channel(b.channels.detail),
        reference: channel(b.channels.reference),
      });
    }
    case 'automed-skin-lesion-cls-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        progress: channel(b.channels.progress),
        detail: channel(b.channels.detail),
        reference: channel(b.channels.reference),
      });
    }
    case 'automed-chexpert-report-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        progress: channel(b.channels.progress),
        detail: channel(b.channels.detail),
        reference: channel(b.channels.reference),
      });
    }
    case 'automed-iu-xray-report-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        progress: channel(b.channels.progress),
        detail: channel(b.channels.detail),
        reference: channel(b.channels.reference),
      });
    }
    case 'automed-mimic-report-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        progress: channel(b.channels.progress),
        detail: channel(b.channels.detail),
        reference: channel(b.channels.reference),
      });
    }
    case 'automed-pathology-caption-100-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        progress: channel(b.channels.progress),
        detail: channel(b.channels.detail),
        reference: channel(b.channels.reference),
      });
    }
    case 'automed-pathology-caption-500-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        progress: channel(b.channels.progress),
        detail: channel(b.channels.detail),
        reference: channel(b.channels.reference),
      });
    }
    case 'automed-medframeqa-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        progress: channel(b.channels.progress),
        detail: channel(b.channels.detail),
        reference: channel(b.channels.reference),
      });
    }
    case 'automed-medxpert-mm-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        progress: channel(b.channels.progress),
        detail: channel(b.channels.detail),
        reference: channel(b.channels.reference),
      });
    }
    case 'automed-pathvqa-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        progress: channel(b.channels.progress),
        detail: channel(b.channels.detail),
        reference: channel(b.channels.reference),
      });
    }
    case 'automed-slake-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        progress: channel(b.channels.progress),
        detail: channel(b.channels.detail),
        reference: channel(b.channels.reference),
      });
    }
    case 'automed-kvasir-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        progress: channel(b.channels.progress),
        detail: channel(b.channels.detail),
        reference: channel(b.channels.reference),
      });
    }
    case 'automed-omni-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        progress: channel(b.channels.progress),
        detail: channel(b.channels.detail),
        reference: channel(b.channels.reference),
      });
    }
    case 'automed-vqa-rad-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        progress: channel(b.channels.progress),
        detail: channel(b.channels.detail),
        reference: channel(b.channels.reference),
      });
    }
    case 'bcer-denoise-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        progress: channel(b.channels.progress),
        detail: channel(b.channels.detail),
        reference: channel(b.channels.reference),
      });
    }
    case 'bcer-superres-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        progress: channel(b.channels.progress),
        detail: channel(b.channels.detail),
        reference: channel(b.channels.reference),
      });
    }
    case 'bcer-grappa-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        progress: channel(b.channels.progress),
        detail: channel(b.channels.detail),
        reference: channel(b.channels.reference),
      });
    }
    case 'imaging101-poisson-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        progress: channel(b.channels.progress),
        detail: channel(b.channels.detail),
        reference: channel(b.channels.reference),
      });
    }
    case 'imaging-eit-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        progress: channel(b.channels.progress),
        detail: channel(b.channels.detail),
        reference: channel(b.channels.reference),
      });
    }
    case 'imaging-dynamic-mri-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        progress: channel(b.channels.progress),
        detail: channel(b.channels.detail),
        reference: channel(b.channels.reference),
      });
    }
    case 'bcer-brain-grade-v1':
    case 'bcer-cardiac-full-v1':
    case 'bcer-brain-full-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        progress: channel(b.channels.progress),
        detail: channel(b.channels.detail),
        reference: channel(b.channels.reference),
      });
    }
    case 'cardiac-material-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        phase: b.channels.phase[0] + (b.channels.phase[1] - b.channels.phase[0]) * progress,
        helper: channel(b.channels.helper),
        output: channel(b.channels.output),
        reference: channel(b.channels.reference),
      });
    }
    case 'cardiac-anchor-v1': {
      const b = plan.beats[index];
      return Object.freeze({
        ...common,
        recipe: plan.recipe,
        scene: b.scene,
        phase: b.channels.phase[0] + (b.channels.phase[1] - b.channels.phase[0]) * progress,
        helper: channel(b.channels.helper),
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
