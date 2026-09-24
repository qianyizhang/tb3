import { AnatomyAssets } from './anatomy';
import type { VisualEntry } from './types';
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
export const taskSceneMode = (e: VisualEntry) => {
  const d = e.illustration;
  if (STATIC_KINDS.has(d?.kind)) return 'static';
  if (
    d?.kind === 'segment' &&
    d.target &&
    !AnatomyAssets.get(d.subject || 'generic')?.some((part) => part.id === d.target) &&
    !AnatomyAssets.has(d.target)
  )
    return 'static';
  return '3d';
};
