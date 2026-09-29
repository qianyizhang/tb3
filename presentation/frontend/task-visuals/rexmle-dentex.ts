import sourceRaw from '../../task-explorer/rexmle-dentex/source.json?raw';
import outputRaw from '../../task-explorer/rexmle-dentex/output.json?raw';
import referenceRaw from '../../task-explorer/rexmle-dentex/reference.json?raw';
import imageUrl from '../../task-explorer/rexmle-dentex/train_266.png?url';

export type RexDentexSceneName = 'input' | 'localize' | 'encode' | 'reference' | 'audit';
export type RexDentexState = {
  recipe: 'rexmle-dentex-v1';
  scene: RexDentexSceneName;
  box: number;
  labels: number;
  reference: number;
};

export type DentexBox = {
  annotation_id: number;
  bbox: [number, number, number, number];
  category_id_1: number;
  category_id_2: number;
  category_id_3: number;
};

export const dentexSource = JSON.parse(sourceRaw) as {
  role: string;
  image: string;
  source_image_id: number;
  rex_image_id: string;
  width_px: number;
  height_px: number;
  rex_path: string;
  split: { public_train: number; private_label_test: number; method: string };
  notice: { label: string; text: string; url: string; link_label: string };
};
export const dentexOutput = JSON.parse(outputRaw) as {
  role: string;
  status: 'not-retained';
  submission_csv: string;
  example_row: { image_id: string; predictions_json: string };
  bbox_format: string;
  box_fields: string[];
  model_prediction: null;
  ap: null;
};
export const dentexReference = JSON.parse(referenceRaw) as {
  role: string;
  boxes: DentexBox[];
  category_names_by_source_id: Record<
    'categories_1' | 'categories_2' | 'categories_3',
    Record<string, string>
  >;
  scorer_caveat: {
    source_ids: Record<string, number[]>;
    grader_declared_ids: Record<string, number[]>;
    status: string;
  };
};
export const dentexImage = imageUrl;
export const dentexRevealed = (state: RexDentexState) =>
  state.scene === 'reference' && state.reference > 0.5;
