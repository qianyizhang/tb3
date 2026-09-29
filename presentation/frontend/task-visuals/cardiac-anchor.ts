import sourceRaw from '../../task-explorer/cardiac-anchor/source.json?raw';
import outputRaw from '../../task-explorer/cardiac-anchor/output.json?raw';
import referenceRaw from '../../task-explorer/cardiac-anchor/reference.json?raw';

export type CardiacAnchorState = {
  recipe: 'cardiac-anchor-v1';
  scene:
    | 'inputs'
    | 'anchors'
    | 'tracking-one'
    | 'tracking-two'
    | 'surface'
    | 'reference'
    | 'comparison'
    | 'limits';
  phase: number;
  helper: number;
  output: number;
  reference: number;
};
export type Condition = 'one' | 'two';
export const anchorSource = JSON.parse(sourceRaw) as {
  frame_count: number;
  shape_hw: [number, number];
  display_wh: [number, number];
  spacing_mm_per_native_pixel: number;
  views: { source_plane_1based: number; assumed_degrees: number; frames: string[] }[];
  anchors: Record<Condition, Record<string, string>>;
};
export const anchorOutput = JSON.parse(outputRaw) as {
  conditions: Record<
    Condition,
    {
      input_mask_boundaries: string[][];
      withheld_plane8_mesh_sections: string[];
      volume_ml: number[];
      mesh_rings_mm: number[][][][];
    }
  >;
};
export const anchorReference = JSON.parse(referenceRaw) as {
  selected: Record<
    string,
    {
      image: string;
      boundary: string;
      source_plane_1based: number;
      frame_1based: number;
    }
  >;
  dense_volume_ml: number[];
  dense_ef_percent: number;
};
export const anchorFrame = (phase: number) => Math.min(29, Math.max(0, Math.round(phase * 29)));
export const anchorCondition = (scene: CardiacAnchorState['scene']): Condition =>
  scene === 'tracking-two' ? 'two' : 'one';
export const anchorColors = { helper: '#89a6e6', output: '#22d7e0', reference: '#ffbe4b' };
