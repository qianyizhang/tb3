/** Integrated source/capture/locale/fallback matrix using the repository browser harness. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { pathToFileURL } = require('node:url');
const { withBrowser } = require('../presentation/tooling/browser.mts');
const { captureComposedFrame } = require('../presentation/tooling/media/capture.mts');
const folder = path.resolve(process.argv[2]),
  explorer = path.resolve(process.argv[3]);
const entryOnly = process.argv[4] === '--entry-only';
assert.ok(
  process.argv.length === 4 || (process.argv.length === 5 && entryOnly),
  'Unsupported browser matrix arguments',
);
const currentBatch = JSON.parse(fs.readFileSync(path.join(folder, 'batch.json')));
const report = {
  navigation_scope: entryOnly ? 'current-entry' : 'full-regression',
  stories: [],
  errors: [],
  remote_requests: [],
  file_protocol: true,
  navigation: [],
};
const sha = (bytes) => crypto.createHash('sha256').update(bytes).digest('hex');

const cardiacRecipes = new Set([
  'automed-brain-cls-v1',
  'rex-ldct-iqa-v1',
  'radagent-vqa-v1',
  'abra-birads-v1',
  'abra-vision-probe-v1',
  'abra-metadata-qa-v1',
  'abra-viewer-control-v1',
  'bcer-brain-full-v1',
  'bcer-cardiac-full-v1',
  'bcer-brain-grade-v1',
  'healthagentbench-cxr-correction-v1',
  'healthagentbench-tumor-tiles-v1',
  'radagent-report-v1',
  'healthagentbench-ct-findings-v1',
  'automed-full-tsg-multiorgan-v1',
  'automed-full-spleen-v1',
  'automed-full-prostate-seg-v1',
  'automed-full-panther-t2-seg-v1',
  'automed-full-panther-t1-seg-v1',
  'automed-full-pancreas-seg-v1',
  'automed-full-pancreas-oar-v1',
  'automed-full-liver-v1',
  'automed-full-kidney-v1',
  'automed-full-hepaticvessel-v1',
  'cardiac-contour-v1',
  'cardiac-anchor-v1',
  'cardiac-material-v1',
  'automed-full-heart-seg-v1',
  'automed-full-feta-seg-v1',
  'automed-full-colon-seg-v1',
  'automed-full-aeropath-seg-v1',
  'automed-full-vindr-cxr-detection-v1',
  'automed-full-grazpedwri-detection-v1',
  'automed-full-dentex-detection-v1',
  'automed-full-bccd-detection-v1',
  'rex-topcow-mr-edges-v1',
  'rex-topcow-ct-edges-v1',
  'rex-topcow-mr-box-v1',
  'rex-topcow-ct-box-v1',
  'rex-topcow-mr-seg-v1',
  'rex-topbrain-mr-v1',
  'rex-topbrain-ct-v1',
  'rex-seg-a-v1',
  'rexmle-puma-track2-task2-v1',
  'rexmle-puma-track1-task2-v1',
  'rexmle-puma-track1-task1-v1',
  'rex-panther-task2-v1',
  'rex-panther-task1-v1',
  'rexmle-neurips-cellseg-v1',
  'rex-isles22-v1',
  'rexmle-dentex-v1',
  'abra-longitudinal-v1',
  'bcer-prostate-registration-v1',
  'bcer-brain-v1',
  'automed-kidney-v1',
  'report-reading-v1',
  'cardiac-mask-mechanics-v1',
  'cardiac-real-echo-v1',
]);
if (entryOnly) {
  assert.ok(currentBatch.entries.length > 0, 'Entry-only review requires entries');
  for (const entry of currentBatch.entries)
    assert.ok(
      cardiacRecipes.has(entry.recipe),
      `Entry-only interaction coverage missing: ${entry.recipe}`,
    );
}
function cardiacSelectors(plan) {
  if (plan.recipe === 'automed-brain-cls-v1')
    return {
      scene: 'data-brain-cls-scene',
      reference: '[data-brain-cls-private-reference]',
      referenceChannel: null,
      output: '[data-brain-cls-output-schema]',
      aside: '[data-brain-cls-output]',
    };
  if (plan.recipe === 'rex-ldct-iqa-v1')
    return {
      scene: 'data-ldct-scene',
      reference: '[data-ldct-private-reference]',
      referenceChannel: null,
      output: '[data-ldct-output-schema]',
      aside: '[data-ldct-output]',
    };
  if (plan.recipe === 'radagent-vqa-v1')
    return {
      scene: 'data-radagent-vqa-scene',
      reference: '[data-radagent-vqa-reference-revealed]',
      output: '[data-radagent-vqa-illustrative-format]',
      aside: '[data-radagent-vqa-output]',
    };
  if (plan.recipe === 'abra-birads-v1')
    return {
      scene: 'data-birads-scene',
      reference: '[data-birads-reference-revealed]',
      output: '[data-birads-output-schema]',
      aside: '[data-birads-aside]',
    };
  if (plan.recipe === 'abra-vision-probe-v1')
    return {
      scene: 'data-abra-vision-probe-scene',
      reference: '[data-abra-vision-probe-reference-revealed]',
      output: '[data-abra-vision-probe-empty-output]',
      aside: '[data-abra-vision-probe-output]',
    };
  if (plan.recipe === 'abra-metadata-qa-v1')
    return {
      scene: 'data-abra-metadata-scene',
      reference: '[data-abra-metadata-comparison-revealed]',
      output: '[data-abra-metadata-empty-output]',
      aside: '[data-abra-metadata-output]',
    };
  if (plan.recipe === 'abra-viewer-control-v1')
    return {
      scene: 'data-abra-viewer-scene',
      reference: '[data-abra-private-reference]',
      referenceChannel: null,
      output: '[data-abra-output-schema]',
      aside: '[data-abra-aside]',
    };
  if (plan.recipe === 'bcer-brain-full-v1')
    return {
      scene: 'data-intb-scene',
      reference: '[data-intb-private-reference]',
      referenceChannel: null,
      output: '[data-intb-output-schema]',
      aside: '[data-intb-aside]',
    };
  if (plan.recipe === 'bcer-cardiac-full-v1')
    return {
      scene: 'data-intb-scene',
      reference: '[data-intb-private-reference]',
      referenceChannel: null,
      output: '[data-intb-output-schema]',
      aside: '[data-intb-aside]',
    };
  if (plan.recipe === 'bcer-brain-grade-v1')
    return {
      scene: 'data-intb-scene',
      reference: '[data-intb-private-reference]',
      referenceChannel: null,
      output: '[data-intb-output-schema]',
      aside: '[data-intb-aside]',
    };
  if (plan.recipe === 'healthagentbench-cxr-correction-v1')
    return {
      scene: 'data-inta-scene',
      reference: '[data-inta-reference-state="revealed"]',
      referenceChannel: null,
      output: '[data-inta-schema]',
      aside: '[data-inta-output]',
    };
  if (plan.recipe === 'healthagentbench-tumor-tiles-v1')
    return {
      scene: 'data-inta-scene',
      reference: '[data-inta-reference-state="revealed"]',
      referenceChannel: null,
      output: '[data-inta-schema]',
      aside: '[data-inta-output]',
    };
  if (plan.recipe === 'radagent-report-v1')
    return {
      scene: 'data-inta-scene',
      reference: '[data-inta-reference-state="revealed"]',
      referenceChannel: null,
      output: '[data-inta-schema]',
      aside: '[data-inta-output]',
    };
  if (plan.recipe === 'healthagentbench-ct-findings-v1')
    return {
      scene: 'data-inta-scene',
      reference: '[data-inta-reference-state="revealed"]',
      referenceChannel: null,
      output: '[data-inta-schema]',
      aside: '[data-inta-output]',
    };
  if (plan.recipe === 'automed-full-tsg-multiorgan-v1')
    return {
      scene: 'data-automed-d-scene',
      reference: '[data-automed-d-training-label]',
      referenceChannel: null,
      output: '[data-automed-d-empty-output]',
      aside: '[data-automed-d-output]',
    };
  if (plan.recipe === 'automed-full-spleen-v1')
    return {
      scene: 'data-automed-d-scene',
      reference: '[data-automed-d-training-label]',
      referenceChannel: 'reference',
      output: '[data-automed-d-empty-output]',
      aside: '[data-automed-d-output]',
    };
  if (plan.recipe === 'automed-full-prostate-seg-v1')
    return {
      scene: 'data-segc-scene',
      reference: '[data-segc-private-reference]',
      referenceChannel: null,
      output: '[data-segc-schema]',
      aside: '[data-segc-output]',
    };
  if (plan.recipe === 'automed-full-panther-t2-seg-v1')
    return {
      scene: 'data-segc-scene',
      reference: '[data-segc-private-reference]',
      referenceChannel: null,
      output: '[data-segc-schema]',
      aside: '[data-segc-output]',
    };
  if (plan.recipe === 'automed-full-panther-t1-seg-v1')
    return {
      scene: 'data-segc-scene',
      reference: '[data-segc-private-reference]',
      referenceChannel: null,
      output: '[data-segc-schema]',
      aside: '[data-segc-output]',
    };
  if (plan.recipe === 'automed-full-pancreas-seg-v1')
    return {
      scene: 'data-segc-scene',
      reference: '[data-segc-private-reference]',
      referenceChannel: null,
      output: '[data-segc-schema]',
      aside: '[data-segc-output]',
    };
  if (plan.recipe === 'automed-full-pancreas-oar-v1')
    return {
      scene: 'data-automed-b-scene',
      reference: '[data-automed-b-reference-overlay]',
      referenceChannel: null,
      output: '[data-automed-b-empty-output]',
      aside: '[data-automed-b-output]',
    };
  if (plan.recipe === 'automed-full-liver-v1')
    return {
      scene: 'data-automed-b-scene',
      reference: '[data-automed-b-reference-overlay]',
      referenceChannel: 'reference',
      output: '[data-automed-b-empty-output]',
      aside: '[data-automed-b-output]',
    };
  if (plan.recipe === 'automed-full-kidney-v1')
    return {
      scene: 'data-automed-b-scene',
      reference: '[data-automed-b-reference-overlay]',
      referenceChannel: 'reference',
      output: '[data-automed-b-empty-output]',
      aside: '[data-automed-b-output]',
    };
  if (plan.recipe === 'automed-full-hepaticvessel-v1')
    return {
      scene: 'data-automed-b-scene',
      reference: '[data-automed-b-reference-overlay]',
      referenceChannel: null,
      output: '[data-automed-b-empty-output]',
      aside: '[data-automed-b-output]',
    };
  if (plan.recipe === 'automed-full-heart-seg-v1')
    return {
      scene: 'data-sega-scene',
      reference: '[data-sega-reference]',
      referenceChannel: 'reference',
      output: '[data-sega-schema]',
      aside: '[data-sega-output]',
    };
  if (plan.recipe === 'automed-full-feta-seg-v1')
    return {
      scene: 'data-sega-scene',
      reference: '[data-sega-reference]',
      referenceChannel: null,
      output: '[data-sega-schema]',
      aside: '[data-sega-output]',
    };
  if (plan.recipe === 'automed-full-colon-seg-v1')
    return {
      scene: 'data-sega-scene',
      reference: '[data-sega-reference]',
      referenceChannel: 'reference',
      output: '[data-sega-schema]',
      aside: '[data-sega-output]',
    };
  if (plan.recipe === 'automed-full-aeropath-seg-v1')
    return {
      scene: 'data-sega-scene',
      reference: '[data-sega-reference]',
      referenceChannel: 'reference',
      output: '[data-sega-schema]',
      aside: '[data-sega-output]',
    };
  if (plan.recipe === 'automed-full-vindr-cxr-detection-v1')
    return {
      scene: 'data-detection-scene',
      reference: '[data-detection-reference]',
      referenceChannel: null,
      output: '[data-detection-output-schema]',
      aside: '[data-detection-output]',
    };
  if (plan.recipe === 'automed-full-grazpedwri-detection-v1')
    return {
      scene: 'data-detection-scene',
      reference: '[data-detection-reference]',
      referenceChannel: 'reference',
      output: '[data-detection-output-schema]',
      aside: '[data-detection-output]',
    };
  if (plan.recipe === 'automed-full-dentex-detection-v1')
    return {
      scene: 'data-detection-scene',
      reference: '[data-detection-reference]',
      referenceChannel: 'reference',
      output: '[data-detection-output-schema]',
      aside: '[data-detection-output]',
    };
  if (plan.recipe === 'automed-full-bccd-detection-v1')
    return {
      scene: 'data-detection-scene',
      reference: '[data-detection-reference]',
      referenceChannel: 'reference',
      output: '[data-detection-output-schema]',
      aside: '[data-detection-output]',
    };
  if (plan.recipe === 'rex-topcow-mr-edges-v1')
    return {
      scene: 'data-topcow-scene',
      reference: '[data-topcow-reference-panel]',
      referenceChannel: 'reference',
      output: '[data-topcow-output-schema]',
      aside: '[data-topcow-output]',
    };
  if (plan.recipe === 'rex-topcow-ct-edges-v1')
    return {
      scene: 'data-topcow-scene',
      reference: '[data-topcow-reference-panel]',
      referenceChannel: 'reference',
      output: '[data-topcow-output-schema]',
      aside: '[data-topcow-output]',
    };
  if (plan.recipe === 'rex-topcow-mr-box-v1')
    return {
      scene: 'data-topcow-scene',
      reference: '[data-topcow-reference-panel]',
      referenceChannel: 'reference',
      output: '[data-topcow-output-schema]',
      aside: '[data-topcow-output]',
    };
  if (plan.recipe === 'rex-topcow-ct-box-v1')
    return {
      scene: 'data-topcow-scene',
      reference: '[data-topcow-reference-panel]',
      referenceChannel: 'reference',
      output: '[data-topcow-output-schema]',
      aside: '[data-topcow-output]',
    };
  if (plan.recipe === 'rex-topcow-mr-seg-v1')
    return {
      scene: 'data-vascular-scene',
      reference: '[data-vascular-reference]',
      referenceChannel: 'reference',
      output: '[data-vascular-output-schema]',
      aside: '[data-vascular-output]',
    };
  if (plan.recipe === 'rex-topbrain-mr-v1')
    return {
      scene: 'data-vascular-scene',
      reference: '[data-vascular-reference]',
      referenceChannel: null,
      output: '[data-vascular-output-schema]',
      aside: '[data-vascular-output]',
    };
  if (plan.recipe === 'rex-topbrain-ct-v1')
    return {
      scene: 'data-vascular-scene',
      reference: '[data-vascular-reference]',
      referenceChannel: null,
      output: '[data-vascular-output-schema]',
      aside: '[data-vascular-output]',
    };
  if (plan.recipe === 'rex-seg-a-v1')
    return {
      scene: 'data-vascular-scene',
      reference: '[data-vascular-reference]',
      referenceChannel: null,
      output: '[data-vascular-output-schema]',
      aside: '[data-vascular-output]',
    };
  if (plan.recipe === 'rexmle-puma-track2-task2-v1')
    return {
      scene: 'data-puma-scene',
      reference: '[data-puma-private-reference]',
      referenceChannel: null,
      output: '[data-puma-empty-output]',
      aside: '[data-puma-output]',
    };
  if (plan.recipe === 'rexmle-puma-track1-task2-v1')
    return {
      scene: 'data-puma-scene',
      reference: '[data-puma-private-reference]',
      referenceChannel: null,
      output: '[data-puma-empty-output]',
      aside: '[data-puma-output]',
    };
  if (plan.recipe === 'rexmle-puma-track1-task1-v1')
    return {
      scene: 'data-puma-scene',
      reference: '[data-puma-private-reference]',
      referenceChannel: null,
      output: '[data-puma-empty-output]',
      aside: '[data-puma-output]',
    };
  if (plan.recipe === 'rex-panther-task2-v1')
    return {
      scene: 'data-panther-scene',
      reference: '[data-panther-private-reference]',
      referenceChannel: null,
      output: '[data-panther-output-schema]',
      aside: '[data-panther-output]',
    };
  if (plan.recipe === 'rex-panther-task1-v1')
    return {
      scene: 'data-panther-scene',
      reference: '[data-panther-private-reference]',
      referenceChannel: null,
      output: '[data-panther-output-schema]',
      aside: '[data-panther-output]',
    };
  if (plan.recipe === 'rexmle-neurips-cellseg-v1')
    return {
      scene: 'data-cellseg-scene',
      reference: '[data-cellseg-private-reference]',
      referenceChannel: null,
      output: '[data-cellseg-empty-test-output]',
      aside: '[data-cellseg-output]',
    };
  if (plan.recipe === 'rex-isles22-v1')
    return {
      scene: 'data-isles-scene',
      reference: '[data-isles-reference]',
      output: '[data-isles-output-schema]',
      aside: '[data-isles-output]',
    };
  if (plan.recipe === 'rexmle-dentex-v1')
    return {
      scene: 'data-dentex-scene',
      reference: '[data-dentex-reference]',
      output: '[data-dentex-output-schema]',
      aside: '[data-dentex-output]',
    };
  if (plan.recipe === 'abra-longitudinal-v1')
    return {
      scene: 'data-abra-scene',
      reference: '[data-abra-private-reference]',
      output: '[data-abra-empty-output-schema]',
      aside: '[data-abra-output]',
    };
  if (plan.recipe === 'bcer-prostate-registration-v1')
    return {
      scene: 'data-bcer-prostate-scene',
      reference: '[data-bcer-prostate-private-reference]',
      referenceChannel: null,
      output: '[data-bcer-prostate-empty-output]',
      aside: '[data-bcer-prostate-output]',
    };
  if (plan.recipe === 'bcer-brain-v1')
    return {
      scene: 'data-bcer-brain-scene',
      reference: '[data-bcer-brain-private-reference]',
      referenceChannel: null,
      output: '[data-bcer-brain-label-semantics]',
      aside: '[data-bcer-brain-output]',
    };
  if (plan.recipe === 'automed-kidney-v1')
    return {
      scene: 'data-kidney-scene',
      reference: '[data-kidney-private-reference], [data-kidney-reference-revealed]',
      output: '[data-kidney-empty-output]',
      aside: '[data-kidney-output]',
    };
  if (plan.recipe === 'report-reading-v1')
    return {
      scene: 'data-report-reading-scene',
      reference: '[data-report-reading-reference]',
      output: '[data-report-reading-answer-schema]',
      aside: '[data-report-reading-output]',
    };
  if (plan.recipe === 'cardiac-mask-mechanics-v1')
    return {
      scene: 'data-mask-mechanics-scene',
      reference: '[data-mask-mechanics-reference]',
      output:
        '[data-mask-mechanics-saved-output], [data-mask-mechanics-saved-occupancy], [data-mask-mechanics-tensor]',
      aside: '[data-mask-mechanics-output]',
    };
  if (plan.recipe === 'cardiac-real-echo-v1')
    return {
      scene: 'data-real-echo-scene',
      reference: '[data-real-echo-review]',
      output: '[data-real-echo-saved-output]',
      aside: '[data-real-echo-output]',
      referenceChannel: 'review',
    };
  if (plan.recipe === 'cardiac-material-v1')
    return {
      scene: 'data-material-scene',
      reference: '[data-material-reference]',
      output: '[data-material-output]',
      aside: '[data-material-output-panel]',
    };
  const contour = plan.recipe === 'cardiac-contour-v1';
  return {
    scene: contour ? 'data-cardiac-contour-scene' : 'data-cardiac-anchor-scene',
    reference: contour
      ? '[data-contour-reference]'
      : '[data-cardiac-anchor-reference-boundary], [data-cardiac-anchor-reference-curve]',
    output: contour ? '[data-contour-output]' : '[data-cardiac-anchor-output-boundary]',
    aside: contour ? '[data-cardiac-contour-output]' : '[data-cardiac-anchor-output]',
  };
}
async function checkSourceWarning(page, plan) {
  const config = {
    'automed-brain-cls-v1': [
      /MRI, Full IDs, private labels, checkpoint and results are absent; official acquisition requests timed out/s,
      'https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset',
      'data-brain-cls-scene',
      true,
    ],
    'rex-ldct-iqa-v1': [
      /Test images, private reader scores, submitted predictions and measured correlations are absent/s,
      'https://zenodo.org/records/7833096',
      'data-ldct-scene',
      false,
    ],
    'radagent-vqa-v1': [
      /matching CT-RATE VQA case and CT are absent/s,
      'https://huggingface.co/datasets/ibrahimhamamci/CT-RATE',
      'data-radagent-vqa-scene',
      true,
    ],
    'abra-birads-v1': [
      /matching MRI pixels.*generated report/s,
      'https://www.cancerimagingarchive.net/collection/duke-breast-cancer-mri/',
      'data-birads-scene',
      true,
    ],
    'abra-vision-probe-v1': [
      /exact task\/control PNGs and results absent/s,
      'https://github.com/Luab/ABRA/blob/688814615dc368a66276798cb864fe9a587d7e6c/README.md#2-download-datasets',
      'data-abra-vision-probe-scene',
      false,
    ],
    'abra-metadata-qa-v1': [
      /generated ABRA task and live metadata response are absent/s,
      'https://github.com/Luab/ABRA/tree/688814615dc368a66276798cb864fe9a587d7e6c',
      'data-abra-metadata-scene',
      true,
    ],
    'abra-viewer-control-v1': [
      /source CT is retained.*OHIF viewport and slice mapping are missing/s,
      'https://www.cancerimagingarchive.net/collection/lidc-idri/',
      'data-abra-viewer-scene',
      false,
    ],
    'bcer-brain-full-v1': [
      /BCER|ABRA|source|unavailable|metadata/i,
      'https://www.med.upenn.edu/cbica/brats2021/',
      'data-intb-scene',
      false,
    ],
    'bcer-cardiac-full-v1': [
      /BCER|ABRA|source|unavailable|metadata/i,
      'https://www.creatis.insa-lyon.fr/Challenge/acdc/databases.html',
      'data-intb-scene',
      false,
    ],
    'bcer-brain-grade-v1': [
      /BCER|ABRA|source|unavailable|metadata/i,
      'https://www.med.upenn.edu/cbica/brats2021/',
      'data-intb-scene',
      false,
    ],
    'healthagentbench-cxr-correction-v1': [
      /CT-RATE|MIMIC|CAMELYON|source|unavailable|gated|upstream/i,
      'https://physionet.org/content/mimic-cxr/2.1.0/',
      'data-inta-scene',
      false,
    ],
    'healthagentbench-tumor-tiles-v1': [
      /CT-RATE|MIMIC|CAMELYON|source|unavailable|gated|upstream/i,
      'https://camelyon16.grand-challenge.org/Rules/',
      'data-inta-scene',
      false,
    ],
    'radagent-report-v1': [
      /CT-RATE|MIMIC|CAMELYON|source|unavailable|gated|upstream/i,
      'https://huggingface.co/datasets/ibrahimhamamci/CT-RATE',
      'data-inta-scene',
      false,
    ],
    'healthagentbench-ct-findings-v1': [
      /CT-RATE|MIMIC|CAMELYON|source|unavailable|gated|upstream/i,
      'https://huggingface.co/datasets/ibrahimhamamci/CT-RATE',
      'data-inta-scene',
      false,
    ],
    'automed-full-tsg-multiorgan-v1': [
      /Full|MSD|TotalSegmentator|upstream/i,
      'https://zenodo.org/records/10047263',
      'data-automed-d-scene',
      false,
    ],
    'automed-full-spleen-v1': [
      /Full|MSD|TotalSegmentator|upstream/i,
      'https://msd-for-monai.s3-us-west-2.amazonaws.com/Task09_Spleen.tar',
      'data-automed-d-scene',
      false,
    ],
    'automed-full-prostate-seg-v1': [
      /Full|PanTS|PANTHER|MSD/i,
      'https://msd-for-monai.s3-us-west-2.amazonaws.com/Task05_Prostate.tar',
      'data-segc-scene',
      false,
    ],
    'automed-full-panther-t2-seg-v1': [
      /Full|PanTS|PANTHER|MSD/i,
      'https://zenodo.org/records/15192302',
      'data-segc-scene',
      false,
    ],
    'automed-full-panther-t1-seg-v1': [
      /Full|PanTS|PANTHER|MSD/i,
      'https://zenodo.org/records/15192302',
      'data-segc-scene',
      false,
    ],
    'automed-full-pancreas-seg-v1': [
      /Full|PanTS|PANTHER|MSD/i,
      'https://github.com/MrGiovanni/PanTS',
      'data-segc-scene',
      false,
    ],
    'automed-full-pancreas-oar-v1': [
      /Full|PanTS|upstream/i,
      'https://github.com/MrGiovanni/PanTS',
      'data-automed-b-scene',
      false,
    ],
    'automed-full-liver-v1': [
      /Full|PanTS|upstream/i,
      'https://msd-for-monai.s3-us-west-2.amazonaws.com/Task03_Liver.tar',
      'data-automed-b-scene',
      false,
    ],
    'automed-full-kidney-v1': [
      /Full|PanTS|upstream/i,
      'https://github.com/neheller/kits19',
      'data-automed-b-scene',
      false,
    ],
    'automed-full-hepaticvessel-v1': [
      /Full|PanTS|upstream/i,
      'https://msd-for-monai.s3-us-west-2.amazonaws.com/Task08_HepaticVessel.tar',
      'data-automed-b-scene',
      false,
    ],
    'automed-full-heart-seg-v1': [
      /Full/,
      'https://msd-for-monai.s3-us-west-2.amazonaws.com/Task02_Heart.tar',
      'data-sega-scene',
      false,
    ],
    'automed-full-feta-seg-v1': [
      /FeTA/,
      'https://zenodo.org/records/4541606',
      'data-sega-scene',
      false,
    ],
    'automed-full-colon-seg-v1': [
      /Full/,
      'https://msd-for-monai.s3-us-west-2.amazonaws.com/Task10_Colon.tar',
      'data-sega-scene',
      false,
    ],
    'automed-full-aeropath-seg-v1': [
      /Full/,
      'https://zenodo.org/records/10069289',
      'data-sega-scene',
      false,
    ],
    'automed-full-vindr-cxr-detection-v1': [
      /PhysioNet requires/,
      'https://physionet.org/content/vindr-cxr/1.0.0/',
      'data-detection-scene',
      false,
    ],
    'automed-full-grazpedwri-detection-v1': [
      /Full private/,
      'https://figshare.com/articles/dataset/GRAZPEDWRI-DX/14825193',
      'data-detection-scene',
      false,
    ],
    'automed-full-dentex-detection-v1': [
      /Full private/,
      'https://zenodo.org/records/7812323',
      'data-detection-scene',
      false,
    ],
    'automed-full-bccd-detection-v1': [
      /Full private/,
      'https://github.com/Shenggan/BCCD_Dataset',
      'data-detection-scene',
      false,
    ],
    'rex-topcow-mr-edges-v1': [
      /Exact test-partition source image/,
      'https://zenodo.org/records/15692630',
      'data-topcow-scene',
      false,
    ],
    'rex-topcow-ct-edges-v1': [
      /Exact test-partition source image/,
      'https://zenodo.org/records/15692630',
      'data-topcow-scene',
      false,
    ],
    'rex-topcow-mr-box-v1': [
      /Exact test-partition source image/,
      'https://zenodo.org/records/15692630',
      'data-topcow-scene',
      false,
    ],
    'rex-topcow-ct-box-v1': [
      /Exact test-partition source image/,
      'https://zenodo.org/records/15692630',
      'data-topcow-scene',
      false,
    ],
    'rex-topcow-mr-seg-v1': [
      /Exact source image with separately identified labels/,
      'https://zenodo.org/records/15692630',
      'data-vascular-scene',
      false,
    ],
    'rex-topbrain-mr-v1': [
      /Exact source image with separately identified labels/,
      'https://zenodo.org/records/16878417',
      'data-vascular-scene',
      false,
    ],
    'rex-topbrain-ct-v1': [
      /Exact source image with separately identified labels/,
      'https://zenodo.org/records/16878417',
      'data-vascular-scene',
      false,
    ],
    'rex-seg-a-v1': [
      /Exact source image with separately identified labels/,
      'https://figshare.com/articles/dataset/Aortic_Vessel_Tree_AVT_CTA_Datasets_and_Segmentations/14806362',
      'data-vascular-scene',
      false,
    ],
    'rexmle-puma-track2-task2-v1': [
      /Public training ROI and annotation/,
      'https://zenodo.org/records/14869398',
      'data-puma-scene',
      false,
    ],
    'rexmle-puma-track1-task2-v1': [
      /Public training ROI and annotation/,
      'https://zenodo.org/records/14869398',
      'data-puma-scene',
      false,
    ],
    'rexmle-puma-track1-task1-v1': [
      /Public training ROI and annotation/,
      'https://zenodo.org/records/14869398',
      'data-puma-scene',
      false,
    ],
    'rex-panther-task2-v1': [
      /No matching MRI or tumor mask/,
      'https://zenodo.org/records/15192302',
      'data-panther-scene',
    ],
    'rex-panther-task1-v1': [
      /No matching MRI or tumor mask/,
      'https://zenodo.org/records/15192302',
      'data-panther-scene',
    ],
    'rexmle-neurips-cellseg-v1': [
      /Real training image and labels/,
      'https://zenodo.org/records/10719375',
      'data-cellseg-scene',
      false,
    ],
    'rex-isles22-v1': [
      /Actual ISLES22 test input/,
      'https://zenodo.org/records/7960856',
      'data-isles-scene',
      false,
    ],
    'rexmle-dentex-v1': [
      /Real DENTEX image; no prediction/,
      'https://zenodo.org/records/7812323',
      'data-dentex-scene',
      false,
    ],
    'abra-longitudinal-v1': [
      /Real NLST CT; no ABRA answer/,
      'https://www.cancerimagingarchive.net/collection/nlst/',
      'data-abra-scene',
      false,
    ],
    'bcer-prostate-registration-v1': [
      /Real PI-CAI inputs; no BCER registration output/,
      'https://zenodo.org/records/6624726',
      'data-bcer-prostate-scene',
      false,
    ],
    'report-reading-v1': [
      /no CT\/report pair has been admitted/,
      'https://huggingface.co/datasets/ibrahimhamamci/CT-RATE',
      'data-report-reading-scene',
    ],
    'bcer-brain-v1': [
      /No matching four-sequence BraTS case/,
      'https://www.med.upenn.edu/cbica/brats2021/',
      'data-bcer-brain-scene',
    ],
  }[plan.recipe];
  if (!config) return;
  const player = page.locator('.scene-player');
  const warning = player.locator('[data-symbolic-source-warning]');
  assert.equal(await warning.count(), 1);
  assert.match(await warning.innerText(), config[0]);
  assert.equal(await warning.locator('a').getAttribute('href'), config[1]);
  // Viewport changes can trigger scroll anchoring between separate protocol calls.
  // Measure both rectangles in one layout snapshot so the ordering check stays strict.
  const { box, title } = await warning.evaluate((node) => {
    const heading = node.closest('.scene-player')?.querySelector('header h3');
    return {
      box: node.getBoundingClientRect().toJSON(),
      title: heading?.getBoundingClientRect().toJSON() || null,
    };
  });
  assert.ok(
    box && title && box.y + box.height <= title.y + 1,
    'source warning must precede illustration title',
  );
  assert.ok(
    await warning.evaluate(
      (e) => e.scrollWidth <= e.clientWidth + 1 && e.scrollHeight <= e.clientHeight + 1,
    ),
  );
  if (config[3] !== false) {
    assert.equal(
      await player
        .locator(`[${config[2]}] img, [${config[2]}] image, [${config[2]}] canvas`)
        .count(),
      0,
      'symbolic source contract must contain no patient raster',
    );
  }
  const detail = page.locator('.task-detail');
  if (await detail.count()) {
    assert.ok(
      await detail.evaluate((e) =>
        e.firstElementChild?.hasAttribute('data-symbolic-source-warning'),
      ),
      'warning must be first task content',
    );
  }
}
async function checkTopcowReferenceText(page, plan) {
  if (!/^rex-topcow-(ct|mr)-(box|edges)-v1$/.test(plan.recipe)) return;
  if (await page.locator('[data-topcow-reference-panel]').count()) return;
  const text = await page.locator('.scene-player').innerText();
  const forbidden = plan.recipe.includes('-box-')
    ? [
        /102\s*[×x]\s*65\s*[×x]\s*42/,
        /86,\s*113,\s*96/,
        /171\s*[×x]\s*121\s*[×x]\s*38/,
        /148,\s*158,\s*82/,
      ]
    : [/L-A1\s+(?:one|1)\b/, /3rd-A2\s+(?:zero|0)\b/, /R-Pcom\s+(?:zero|0)\b/];
  for (const pattern of forbidden)
    assert.doesNotMatch(text, pattern, `${plan.id}: private reference leaked through narration`);
}
async function checkCardiacFrame(page, plan, frame) {
  if (!cardiacRecipes.has(plan.recipe)) return;
  await checkSourceWarning(page, plan);
  const selectors = cardiacSelectors(plan);
  await checkTopcowReferenceText(page, plan);
  const beat = plan.beats.find((b) => frame >= b.startFrame && frame < b.endFrame);
  const p = (frame - beat.startFrame) / (beat.endFrame - beat.startFrame - 1);
  const ease = p * p * (3 - 2 * p);
  const reference =
    selectors.referenceChannel === null
      ? 0
      : beat.channels[selectors.referenceChannel || 'reference'][0] +
        (beat.channels[selectors.referenceChannel || 'reference'][1] -
          beat.channels[selectors.referenceChannel || 'reference'][0]) *
          ease;
  assert.equal(
    await page.locator(`[${selectors.scene}]`).getAttribute(selectors.scene),
    beat.scene,
  );
  if (reference <= 0.5)
    assert.equal(
      await page.locator(selectors.reference).count(),
      0,
      `${plan.id}: hidden reference mounted at ${frame}`,
    );
  if (frame === 0)
    assert.equal(
      await page.locator(selectors.output).count(),
      0,
      `${plan.id}: prediction visible in input`,
    );
  if (plan.recipe === 'automed-full-prostate-seg-v1') {
    const revealed = beat.scene === 'helper' && frame > (beat.startFrame + beat.endFrame - 1) / 2;
    assert.equal(
      await page.locator('[data-segc-training-helper]').count(),
      revealed ? 1 : 0,
      `${plan.id}: upstream training overlay boundary at ${frame}`,
    );
    if (!revealed)
      assert.doesNotMatch(
        await page.locator('.scene-player').innerText(),
        /source voxels/,
        `${plan.id}: training counts leaked before helper reveal`,
      );
    if (beat.scene === 'channels')
      assert.equal(await page.locator('[data-segc-source] img').count(), 2);
  }
  const output = page.locator(selectors.aside);
  assert.ok(
    await output.evaluate((e) => e.scrollHeight <= e.clientHeight + 1),
    `${plan.id}: output overflow at ${frame}`,
  );
  const box = await output.boundingBox();
  assert.ok(box && box.y + box.height <= 721, `${plan.id}: output clipped at ${frame}`);
  const stage = await page.locator('.scene-stage').boundingBox();
  assert.ok(stage && stage.y + stage.height <= 721, `${plan.id}: stage clipped at ${frame}`);
  const legend = await page.locator('.scene-legend').boundingBox();
  assert.ok(legend && legend.y + legend.height <= 720, `${plan.id}: legend clipped at ${frame}`);
  assert.ok(
    await page.locator(`[${selectors.scene}]`).evaluate((element) => {
      const box = element.getBoundingClientRect();
      const inside = (r) =>
        !r.width ||
        !r.height ||
        (r.left >= box.left - 1 &&
          r.top >= box.top - 1 &&
          r.right <= box.right + 1 &&
          r.bottom <= box.bottom + 1);
      const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT);
      while (walker.nextNode()) {
        if (!walker.currentNode.textContent.trim()) continue;
        const range = document.createRange();
        range.selectNodeContents(walker.currentNode);
        if (!Array.from(range.getClientRects()).every(inside)) return false;
      }
      return Array.from(element.querySelectorAll('svg,img')).every((node) =>
        inside(node.getBoundingClientRect()),
      );
    }),
    `${plan.id}: scene content clipped at ${frame}`,
  );
}
async function reviewCardiacInteractions(page, plan, output, label) {
  if (!cardiacRecipes.has(plan.recipe)) return;
  await checkSourceWarning(page, plan);
  const selectors = cardiacSelectors(plan);
  for (const [index, beat] of plan.beats.entries()) {
    await page.locator(`[data-story-step="${index}"]`).click();
    await page.waitForFunction(
      ([attribute, scene]) =>
        document.querySelector(`[${attribute}]`)?.getAttribute(attribute) === scene,
      [selectors.scene, beat.scene],
    );
    assert.ok(
      await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
      `${plan.id}: ${label} overflow in ${beat.scene}`,
    );
    if (
      selectors.referenceChannel === null ||
      beat.channels[selectors.referenceChannel || 'reference'][0] <= 0.5
    )
      assert.equal(
        await page.locator(selectors.reference).count(),
        0,
        `${plan.id}: ${label} early reference in ${beat.scene}`,
      );
    await checkTopcowReferenceText(page, plan);
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(output, `${label}-${beat.scene}.png`) });
  }
  if (plan.recipe === 'automed-brain-cls-v1') {
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    const step = (scene) => plan.beats.findIndex((b) => b.scene === scene);
    await page.locator(`[data-story-step="${step('helper')}"]`).click();
    const taxonomy = page.getByRole('group', { name: 'Canonical brain classification token' });
    for (const name of ['glioma', 'meningioma', 'notumor', 'pituitary']) {
      const button = taxonomy.getByRole('button', { name, exact: true });
      await button.click();
      assert.equal(await button.getAttribute('aria-pressed'), 'true');
      assert.equal(
        await page.locator('[data-brain-cls-class-selection]').innerText(),
        `Selected taxonomy token: ${name}`,
      );
      assert.match(
        await page.locator('[data-brain-cls-output]').innerText(),
        /patient_id\s+unset\s+label\s+unset/s,
      );
    }
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(output, `${label}-taxonomy.png`) });
    await page.locator(`[data-story-step="${step('operation')}"]`).click();
    const tiers = page.getByRole('group', { name: 'Brain classification assistance' });
    for (const name of ['standard', 'lite']) {
      const button = tiers.getByRole('button', { name, exact: true });
      await button.click();
      assert.equal(await button.getAttribute('aria-pressed'), 'true');
      assert.match(await page.locator('[data-brain-cls-operation]').innerText(), new RegExp(name));
      await page
        .locator('.scene-player')
        .screenshot({ path: path.join(output, `${label}-tier-${name}.png`) });
    }
    const token = page.getByRole('combobox', { name: 'Hypothetical class token' });
    for (const name of ['glioma', 'meningioma', 'notumor', 'pituitary']) {
      await token.selectOption(name.toUpperCase());
      assert.equal(
        await page.locator('[data-brain-cls-map]').innerText(),
        `Canonical spelling: ${name}`,
      );
      assert.match(
        await page.locator('[data-brain-cls-output]').innerText(),
        /patient_id\s+unset\s+label\s+unset/s,
      );
    }
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(output, `${label}-mapping.png`) });
    await page.locator(`[data-story-step="${step('output')}"]`).click();
    const formats = page.getByRole('group', { name: 'Brain classification submission format' });
    for (const name of ['json', 'csv']) {
      const button = formats.getByRole('button', { name, exact: true });
      await button.click();
      assert.equal(await button.getAttribute('aria-pressed'), 'true');
      assert.match(
        await page.locator('[data-brain-cls-format]').innerText(),
        name === 'csv' ? /predictions\.csv/ : /prediction\.json/,
      );
      assert.equal(await page.locator('[data-brain-cls-private-reference]').count(), 0);
      await page
        .locator('.scene-player')
        .screenshot({ path: path.join(output, `${label}-format-${name}.png`) });
    }
    await page.locator(`[data-story-step="${step('limits')}"]`).click();
    const metrics = page.getByRole('group', { name: 'Classification metric denominator' });
    for (const name of ['balanced accuracy', 'accuracy']) {
      const button = metrics.getByRole('button', { name, exact: true });
      await button.click();
      assert.equal(await button.getAttribute('aria-pressed'), 'true');
      assert.match(
        await page.locator('[data-brain-cls-metric]').innerText(),
        name === 'accuracy' ? /all.*(IDs|cases)/i : /supported|positive|present/i,
      );
      assert.match(await page.locator('[data-brain-cls-limits]').innerText(), /0\.\.1|0–1|0\.\.?1/);
      await page.locator('.scene-player').screenshot({
        path: path.join(output, `${label}-metric-${name.replaceAll(' ', '-')}.png`),
      });
    }
    for (const [scene, kind, content] of [
      ['output', 'formatter', /Missing cases.*at least one valid prediction/s],
      ['limits', 'grader', /S1-S3.*\.25/s],
    ]) {
      const index = step(scene);
      await page.locator(`[data-story-step="${index}"]`).click();
      const details = page.locator(`[data-brain-cls-${kind}]`);
      assert.equal(await details.count(), 0);
      await page.getByRole('button', { name: `Inspect ${kind} rules`, exact: true }).click();
      assert.match(await details.innerText(), content);
      assert.equal(await page.locator('[data-brain-cls-private-reference]').count(), 0);
      await page
        .locator('.scene-player')
        .screenshot({ path: path.join(output, `${label}-${kind}-revealed.png`) });
      await page.locator('.scene-play').click();
      await page.waitForFunction(
        (frame) =>
          Number(document.querySelector('.scene-player')?.getAttribute('data-committed-frame')) >
          frame,
        plan.beats[index].startFrame + 4,
      );
      await page.locator('.scene-play').click();
      await page.locator(`[data-story-step="${index}"]`).click();
      assert.equal(await details.count(), 0, `Backward replay must cover ${kind} rules`);
      await page.getByRole('button', { name: `Inspect ${kind} rules`, exact: true }).click();
      await page.locator('[data-story-step="0"]').click();
      assert.equal(await details.count(), 0, `Exit must cover ${kind} rules`);
    }
    await page.locator('.scene-reset').click();
    await page.waitForFunction(
      () => document.querySelector('.scene-player')?.getAttribute('data-committed-frame') === '0',
    );
    await page.locator(`[data-story-step="${step('helper')}"]`).click();
    assert.equal(
      await page.locator('[data-brain-cls-class-selection]').innerText(),
      'No taxonomy token selected',
    );
    await page.locator(`[data-story-step="${step('operation')}"]`).click();
    assert.equal(await token.inputValue(), '');
    assert.equal(
      await tiers.getByRole('button', { name: 'lite', exact: true }).getAttribute('aria-pressed'),
      'true',
    );
    await page.locator(`[data-story-step="${step('output')}"]`).click();
    assert.equal(
      await formats.getByRole('button', { name: 'csv', exact: true }).getAttribute('aria-pressed'),
      'true',
    );
    await page.locator(`[data-story-step="${step('limits')}"]`).click();
    assert.equal(
      await metrics
        .getByRole('button', { name: 'accuracy', exact: true })
        .getAttribute('aria-pressed'),
      'true',
    );
  }
  if (plan.recipe === 'rex-ldct-iqa-v1') {
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    const helper = plan.beats.findIndex((b) => b.scene === 'helper');
    const scoreLabel = page.locator('[data-ldct-training-score]');
    await page.locator(`[data-story-step="${helper}"]`).click();
    assert.equal(await scoreLabel.count(), 0);
    assert.doesNotMatch(
      await page.locator('.scene-player').innerText(),
      /\b3\.8\b/,
      'Covered training label must not leak through narration',
    );
    await page.getByRole('button', { name: 'Reveal public training label', exact: true }).click();
    assert.equal(await scoreLabel.innerText(), '3.8');
    await page.locator('.scene-play').click();
    await page.waitForFunction(
      (frame) =>
        Number(document.querySelector('.scene-player')?.getAttribute('data-committed-frame')) >
        frame,
      plan.beats[helper].startFrame + 4,
    );
    await page.locator('.scene-play').click();
    await page.locator(`[data-story-step="${helper}"]`).click();
    assert.equal(await scoreLabel.count(), 0, 'Backward replay must cover public training label');
    const partitions = page.getByRole('group', { name: 'LDCT data visibility' });
    for (const name of ['inference', 'evaluator', 'training']) {
      await partitions.getByRole('button', { name, exact: true }).click();
      assert.equal(
        await page.locator('[data-ldct-partition]').getAttribute('data-ldct-partition'),
        name,
      );
      assert.equal(await scoreLabel.count(), 0);
      if (name !== 'training')
        assert.match(await page.locator('[data-ldct-helper]').innerText(), /absent/);
      await page
        .locator('.scene-player')
        .screenshot({ path: path.join(output, `${label}-partition-${name}.png`) });
    }
    await page.getByRole('button', { name: 'Reveal public training label', exact: true }).click();
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(output, `${label}-public-training-revealed.png`) });
    await page.getByRole('button', { name: 'Hide public training label', exact: true }).click();
    assert.equal(await scoreLabel.count(), 0);
    await page.getByRole('button', { name: 'Reveal public training label', exact: true }).click();
    await page.locator('[data-story-step="0"]').click();
    assert.equal(await scoreLabel.count(), 0);
    const img = page.locator('[data-ldct-input] img');
    assert.deepEqual(await img.evaluate((e) => [e.naturalWidth, e.naturalHeight]), [512, 512]);
    assert.match(
      await page.locator('[data-ldct-input]').innerText(),
      /not.*HU window|not applied/s,
    );
    const limits = plan.beats.findIndex((b) => b.scene === 'limits');
    await page.locator(`[data-story-step="${limits}"]`).click();
    const fields = page.getByRole('group', { name: 'LDCT grader field' });
    for (const name of ['overall', 'score']) {
      await fields.getByRole('button', { name, exact: true }).click();
      assert.equal(await page.locator('[data-ldct-grader-field]').innerText(), name);
      assert.match(
        await page.locator('[data-ldct-limits]').innerText(),
        name === 'overall' ? /PLCC/ : /0\.\.3/,
      );
      await page
        .locator('.scene-player')
        .screenshot({ path: path.join(output, `${label}-grader-${name}.png`) });
    }
    await page.locator(`[data-story-step="${helper}"]`).click();
    await page.getByRole('button', { name: 'Reveal public training label', exact: true }).click();
    await page.locator('.scene-reset').click();
    await page.waitForFunction(
      () => document.querySelector('.scene-player')?.getAttribute('data-committed-frame') === '0',
    );
    assert.equal(await scoreLabel.count(), 0);
    await page.locator(`[data-story-step="${helper}"]`).click();
    assert.equal(await scoreLabel.count(), 0);
    await page.locator(`[data-story-step="${limits}"]`).click();
    assert.equal(await page.locator('[data-ldct-grader-field]').innerText(), 'score');
  }
  if (plan.recipe === 'radagent-vqa-v1') {
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    const scene = page.locator('[data-radagent-vqa-scene]');
    const op = plan.beats.findIndex((b) => b.scene === 'operation');
    await page.locator(`[data-story-step="${op}"]`).click();
    for (const [index, name] of [
      'Whole volume',
      'Selected slices',
      'Reconcile evidence',
    ].entries()) {
      const beat = plan.beats.find(
        (b) => b.scene === 'operation' && Math.round(b.channels.progress[0] * 2) === index,
      );
      const button = scene.getByRole('button', { name, exact: true });
      await button.click();
      await page.waitForFunction(
        (frame) =>
          Number(document.querySelector('.scene-player')?.getAttribute('data-committed-frame')) ===
          frame,
        beat.startFrame,
      );
      assert.equal(await button.getAttribute('aria-pressed'), 'true');
      const text = await page.locator('[data-radagent-vqa-tool-scope]').innerText();
      assert.match(
        text,
        [/Whole-volume ct_vqa_tool/, /Selected-slice slice_vqa_tool/, /Reconcile scope/][index],
      );
      assert.match(text, /Observed response: —|Tool 1 evidence: —/);
      assert.equal(await page.locator('[data-radagent-vqa-reference-revealed]').count(), 0);
      assert.equal(await page.locator('[data-radagent-vqa-illustrative-format]').count(), 0);
      assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
      await page
        .locator('.scene-player')
        .screenshot({ path: path.join(output, `${label}-scope-${index}.png`) });
    }
    const ref = plan.beats.findIndex((b) => b.scene === 'reference');
    await page.locator(`[data-story-step="${ref}"]`).click();
    const reference = page.locator('[data-radagent-vqa-reference-revealed]');
    assert.equal(await reference.count(), 1);
    assert.match(await reference.innerText(), /Validation compute_reward=False/);
    assert.equal(await reference.locator('tbody tr').count(), 4);
    assert.equal(await reference.getByText('Same full string', { exact: true }).count(), 1);
    await page.locator('[data-story-step="0"]').click();
    assert.equal(await reference.count(), 0);
    await page.locator(`[data-story-step="${ref}"]`).click();
    await page.locator('.scene-reset').click();
    await page.waitForFunction(
      () => document.querySelector('.scene-player')?.getAttribute('data-committed-frame') === '0',
    );
    assert.equal(await reference.count(), 0);
    await page.locator(`[data-story-step="${op}"]`).click();
    assert.equal(
      await scene
        .getByRole('button', { name: 'Whole volume', exact: true })
        .getAttribute('aria-pressed'),
      'true',
    );
  }
  if (plan.recipe === 'abra-birads-v1') {
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    const op = plan.beats.findIndex((b) => b.scene === 'operation');
    await page.locator(`[data-story-step="${op}"]`).click();
    const operation = page.locator('[data-birads-operation]');
    for (const [name, condition, turns] of [
      ['Visual assessment', 'visual', 20],
      ['Oracle findings', 'oracle', 10],
    ]) {
      const button = operation.getByRole('button', { name, exact: true });
      await button.click();
      assert.equal(await operation.getAttribute('data-birads-condition'), condition);
      assert.equal(await button.getAttribute('aria-pressed'), 'true');
      assert.match(await operation.innerText(), new RegExp(`${turns} turns`));
      assert.match(await operation.innerText(), /No tool call occurs here/);
      assert.equal(await page.locator('[data-birads-reference-revealed]').count(), 0);
      await page
        .locator('.scene-player')
        .screenshot({ path: path.join(output, `${label}-condition-${condition}.png`) });
    }
    await page.getByRole('button', { name: 'Follow story', exact: true }).click();
    assert.equal(await operation.getAttribute('data-birads-condition'), 'visual');
    const ref = plan.beats.findIndex((b) => b.scene === 'reference');
    await page.locator(`[data-story-step="${ref}"]`).click();
    assert.equal(await page.locator('[data-birads-reference-revealed]').count(), 0);
    await page.getByRole('button', { name: 'Reveal construction rules', exact: true }).click();
    assert.equal(await page.locator('[data-birads-reference-revealed]').count(), 1);
    assert.match(
      await page.locator('[data-birads-reference-revealed]').innerText(),
      /not.*patient|general.*code/i,
    );
    await page.getByRole('button', { name: 'Hide construction rules', exact: true }).click();
    assert.equal(await page.locator('[data-birads-reference-revealed]').count(), 0);
    await page.getByRole('button', { name: 'Reveal construction rules', exact: true }).click();
    await page.locator('[data-story-step="0"]').click();
    assert.equal(await page.locator('[data-birads-reference-revealed]').count(), 0);
    const limits = plan.beats.findIndex((b) => b.scene === 'limits');
    await page.locator(`[data-story-step="${limits}"]`).click();
    const checkbox = page.getByRole('checkbox', {
      name: 'Illustrative reference includes quadrant',
    });
    assert.match(await page.locator('[data-birads-denominator]').innerText(), /0\.90/);
    await checkbox.check();
    assert.match(await page.locator('[data-birads-denominator]').innerText(), /1\.00/);
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(output, `${label}-quadrant-denominator.png`) });
    await page.locator('.scene-reset').click();
    await page.waitForFunction(
      () => document.querySelector('.scene-player')?.getAttribute('data-committed-frame') === '0',
    );
    assert.equal(await page.locator('[data-birads-reference-revealed]').count(), 0);
    await page.locator(`[data-story-step="${limits}"]`).click();
    assert.equal(await checkbox.isChecked(), false);
    await page.locator(`[data-story-step="${op}"]`).click();
    assert.equal(await operation.getAttribute('data-birads-condition'), 'visual');
  }
  if (plan.recipe === 'abra-vision-probe-v1') {
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    await page.locator('[data-story-step="0"]').click();
    const conditions = [
      'Modality · normal',
      'Modality · replacement noise',
      'Display · lung window',
      'Display · soft tissue',
      'Display · breast MRI',
      'Display · replacement noise',
    ];
    const indices = [14, 42, 70, 98, 126];
    const pack = JSON.parse(
      fs.readFileSync(
        path.resolve('presentation/task-explorer/abra-vision-probe/previews.json'),
        'utf8',
      ),
    );
    for (const [condition, name] of conditions.entries()) {
      await page.getByRole('button', { name, exact: true }).click();
      for (const [slot, index] of indices.entries()) {
        const beat = plan.beats.find(
          (b) => b.scene === 'operation' && Math.round(b.channels.progress[0] * 5) === condition,
        );
        const frame = beat.startFrame + Math.round((slot / 4) * (beat.frames - 1));
        await page.getByRole('button', { name: `Index ${index}`, exact: true }).click();
        await page.waitForFunction(
          (frame) =>
            Number(document.querySelector('.scene-player').getAttribute('data-committed-frame')) ===
            frame,
          frame,
        );
        assert.equal(
          await page.getByRole('button', { name, exact: true }).getAttribute('aria-pressed'),
          'true',
        );
        assert.equal(
          await page
            .getByRole('button', { name: `Index ${index}`, exact: true })
            .getAttribute('aria-pressed'),
          'true',
        );
        const scene = page.locator('[data-abra-vision-probe-scene]');
        const text = await scene.innerText();
        const imgs = scene.locator('img');
        if ([2, 3].includes(condition)) {
          assert.equal(await imgs.count(), 2);
          assert.equal(await imgs.nth(0).getAttribute('src'), pack.instances[slot].lung.data_uri);
          assert.equal(await imgs.nth(1).getAttribute('src'), pack.instances[slot].soft.data_uri);
          assert.ok(text.includes(`selected index ${index}`));
        } else {
          assert.equal(await imgs.count(), 0);
          assert.match(
            text,
            condition === 0
              ? /Exact normal-modality default PNG absent/
              : condition === 4
                ? /signal intensity, not HU/
                : /not Gaussian or additive noise/,
          );
        }
        assert.equal(await page.locator('[data-abra-vision-probe-reference-revealed]').count(), 0);
        assert.equal(await page.locator('[data-abra-vision-probe-empty-output]').count(), 0);
        assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
      }
      await page
        .locator('.scene-player')
        .screenshot({ path: path.join(output, `${label}-condition-${condition}.png`) });
    }
    const ref = plan.beats.findIndex((b) => b.scene === 'reference');
    await page.locator(`[data-story-step="${ref}"]`).click();
    assert.equal(await page.locator('[data-abra-vision-probe-reference-revealed]').count(), 1);
    assert.match(
      await page.locator('[data-abra-vision-probe-reference-revealed]').innerText(),
      /not an observed answer or clinical image adjudication/,
    );
    await page.locator('[data-story-step="0"]').click();
    assert.equal(await page.locator('[data-abra-vision-probe-reference-revealed]').count(), 0);
    await page.locator(`[data-story-step="${ref}"]`).click();
    await page.locator('.scene-reset').click();
    await page.waitForFunction(
      () => document.querySelector('.scene-player')?.getAttribute('data-committed-frame') === '0',
    );
    assert.equal(await page.locator('[data-abra-vision-probe-reference-revealed]').count(), 0);
    assert.equal(
      await page
        .getByRole('button', { name: conditions[0], exact: true })
        .getAttribute('aria-pressed'),
      'true',
    );
  }
  if (plan.recipe === 'abra-metadata-qa-v1') {
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    await page.locator('[data-story-step="0"]').click();
    const pack = JSON.parse(
      fs.readFileSync(
        path.resolve('presentation/task-explorer/abra-metadata-qa/source.json'),
        'utf8',
      ),
    );
    const source = pack.source_example;
    const firstCT = source.series.find((series) => series.modality === 'CT');
    const values = [
      String(firstCT.num_instances),
      String(source.series.length),
      [...new Set(source.series.map((series) => series.modality))].sort().join(', '),
      source.study_date,
      firstCT.series_uid,
    ];
    const labels = [
      'CT instance count',
      'All-series count',
      'Distinct modalities',
      'Study date',
      'First CT series UID',
    ];
    for (const [index, name] of labels.entries()) {
      const beat = plan.beats.find(
        (b) => b.scene === 'operation' && Math.round(b.channels.progress[0] * 4) === index,
      );
      await page.getByRole('button', { name, exact: true }).click();
      await page.waitForFunction(
        (frame) =>
          Number(document.querySelector('.scene-player').getAttribute('data-committed-frame')) ===
          frame,
        beat.startFrame,
      );
      assert.equal(
        await page.getByRole('button', { name, exact: true }).getAttribute('aria-pressed'),
        'true',
      );
      assert.ok(
        (await page.locator('[data-abra-metadata-source-value]').innerText()).includes(
          values[index],
        ),
      );
      assert.equal(await page.locator('[data-abra-metadata-comparison-revealed]').count(), 0);
      assert.equal(await page.locator('[data-abra-metadata-empty-output]').count(), 0);
      assert.ok(
        await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
        `${plan.id}: ${label} query overflow`,
      );
      await page
        .locator('.scene-player')
        .screenshot({ path: path.join(output, `${label}-query-${index}.png`) });
    }
    const refIndex = plan.beats.findIndex((beat) => beat.scene === 'reference');
    await page.locator(`[data-story-step="${refIndex}"]`).click();
    assert.equal(await page.locator('[data-abra-metadata-comparison-revealed]').count(), 1);
    assert.match(
      await page.locator('[data-abra-metadata-comparison-revealed]').innerText(),
      /authored records, no patient\/model\/reference evidence/,
    );
    await page.locator('[data-story-step="0"]').click();
    assert.equal(await page.locator('[data-abra-metadata-comparison-revealed]').count(), 0);
    await page.locator(`[data-story-step="${refIndex}"]`).click();
    await page.locator('.scene-reset').click();
    await page.waitForFunction(
      () => document.querySelector('.scene-player')?.getAttribute('data-committed-frame') === '0',
    );
    assert.equal(await page.locator('[data-abra-metadata-comparison-revealed]').count(), 0);
    assert.equal(
      await page
        .getByRole('button', { name: 'CT instance count', exact: true })
        .getAttribute('aria-pressed'),
      'true',
    );
  }
  if (plan.recipe === 'abra-viewer-control-v1') {
    const operationIndex = plan.beats.findIndex((beat) => beat.scene === 'operation');
    await page.locator(`[data-story-step="${operationIndex}"]`).click();
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    const preview = page.locator('[data-abra-source-preview] img');
    const fixedImage = await preview.getAttribute('src');
    const candidate = page.locator('[data-abra-mock-index]');
    assert.equal(await candidate.innerText(), '0');
    const slider = page.locator('[data-abra-mock-control] input[type="range"]');
    await slider.focus();
    await slider.press('Home');
    await slider.press('ArrowRight');
    assert.equal(await candidate.innerText(), '1');
    await page.getByRole('button', { name: 'Stage 70 locally', exact: true }).click();
    assert.equal(await candidate.innerText(), '70');
    assert.equal(await preview.getAttribute('src'), fixedImage, 'mock control changed source CT');
    assert.equal(await page.locator('[data-abra-observed-state="absent"]').count(), 1);
    assert.match(await page.locator('[data-abra-mock-control]').innerText(), /slice_index=70/);
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(output, `${label}-symbolic-request.png`) });
    await page.getByRole('button', { name: 'Follow story', exact: true }).click();
    assert.equal(await candidate.innerText(), '0');
    await page.getByRole('button', { name: 'Stage 70 locally', exact: true }).click();
    await page.locator('[data-story-step="0"]').click();
    await page.locator(`[data-story-step="${operationIndex}"]`).click();
    assert.equal(await candidate.innerText(), '0', 'chapter unmount did not clear local override');
    await page.getByRole('button', { name: 'Stage 70 locally', exact: true }).click();
    await page.locator('.scene-reset').click();
    await page.waitForFunction(
      () => document.querySelector('.scene-player')?.getAttribute('data-committed-frame') === '0',
    );
    await page.locator(`[data-story-step="${operationIndex}"]`).click();
    assert.equal(await candidate.innerText(), '0', 'canonical reset retained local override');
    assert.equal(await preview.getAttribute('src'), fixedImage);
  }
  if (plan.recipe === 'automed-full-prostate-seg-v1') {
    const helperIndex = plan.beats.findIndex((b) => b.scene === 'helper');
    await page.locator(`[data-story-step="${helperIndex}"]`).click();
    await page.locator('[data-segc-helper-state="covered"]').waitFor();
    assert.equal(await page.locator('[data-segc-training-helper]').count(), 0);
    assert.doesNotMatch(await page.locator('.scene-player').innerText(), /source voxels/);
    await page.locator('.scene-play').click();
    await page.locator('[data-segc-training-helper]').waitFor({ timeout: 15000 });
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    assert.equal(await page.locator('[data-segc-training-helper]').count(), 1);
    assert.match(
      await page.locator('[data-segc-helper-state="revealed"]').innerText(),
      /cyan.*peripheral zone.*amber.*transition zone/s,
    );
    assert.ok(
      await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
      `${plan.id}: ${label} helper overflow`,
    );
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(output, `${label}-training-helper-revealed.png`) });
    await page.locator('.scene-reset').click();
    await page.waitForFunction(
      () => document.querySelector('.scene-player')?.getAttribute('data-committed-frame') === '0',
    );
    assert.equal(await page.locator('[data-segc-training-helper]').count(), 0);
  }
  if (plan.recipe === 'bcer-brain-full-v1') {
    const operationIndex = plan.beats.findIndex((b) => b.scene === 'operation');
    await page.locator(`[data-story-step="${operationIndex}"]`).click();
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    const panel = page.locator('[data-brain-full-focus]');
    assert.equal(await panel.getAttribute('data-brain-full-focus'), 'registration');
    await page.getByRole('button', { name: '04 Report', exact: true }).click();
    assert.match(
      await panel.innerText(),
      /does not directly read the grade classifier.*skipped conditional registration/s,
    );
    assert.match(await panel.innerText(), /VLM\/QC.*none ran/s);
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(output, `${label}-brain-report.png`) });
    await page.getByRole('button', { name: '02 Segmentation', exact: true }).click();
    assert.match(await panel.innerText(), /ellipsoid.*Missing bundle.*raise/s);
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(output, `${label}-brain-fallback.png`) });
    await page.getByRole('button', { name: '03 Features → grade', exact: true }).click();
    assert.match(await panel.innerText(), /uncalibrated.*unset/s);
    await page.getByRole('button', { name: 'Follow story focus', exact: true }).click();
    assert.equal(await panel.getAttribute('data-brain-full-focus'), 'registration');
    await page.getByRole('button', { name: '04 Report', exact: true }).click();
    await page.locator('[data-story-step="0"]').click();
    await page.locator(`[data-story-step="${operationIndex}"]`).click();
    assert.equal(await panel.getAttribute('data-brain-full-focus'), 'registration');
    assert.equal(await page.locator('[data-intb-scene] img').count(), 0);
  }
  if (plan.recipe === 'bcer-cardiac-full-v1') {
    const operationIndex = plan.beats.findIndex((b) => b.scene === 'operation');
    await page.locator(`[data-story-step="${operationIndex}"]`).click();
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    assert.equal(
      await page.locator('[data-phase-mode]').getAttribute('data-phase-mode'),
      'single_3d',
    );
    await page.getByRole('button', { name: 'Raw cine H5', exact: true }).click();
    assert.match(await page.locator('[data-cine-route]').innerText(), /Conditional reconstruction/);
    await page.getByRole('button', { name: '4D without valid ED/ES', exact: true }).click();
    assert.match(
      await page.locator('[data-phase-mode]').innerText(),
      /all frames.*LV-volume extrema/,
    );
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(output, `${label}-cine-branches.png`) });
    await page.getByRole('button', { name: '4D with valid Info.cfg ED/ES', exact: true }).click();
    assert.match(await page.locator('[data-phase-mode]').innerText(), /1-based.*zero-based/);
    await page.getByRole('button', { name: 'One 3D phase', exact: true }).click();
    assert.match(await page.locator('[data-phase-mode]').innerText(), /No temporal curve/);
    assert.match(
      await page.locator('[data-cardiac-cine-mechanism]').innerText(),
      /Parallel required artifact.*Classifier does not read feature CSV/s,
    );
    await page.getByRole('button', { name: 'Follow story focus', exact: true }).click();
    assert.equal(await page.locator('[data-cine-route]').getAttribute('data-cine-route'), 'nifti');
    await page.getByRole('button', { name: 'Raw cine H5', exact: true }).click();
    await page.locator('[data-story-step="0"]').click();
    await page.locator(`[data-story-step="${operationIndex}"]`).click();
    assert.equal(await page.locator('[data-cine-route]').getAttribute('data-cine-route'), 'nifti');
    assert.equal(
      await page.locator('[data-phase-mode]').getAttribute('data-phase-mode'),
      'single_3d',
    );
    const limitsIndex = plan.beats.findIndex((b) => b.scene === 'limits');
    await page.locator(`[data-story-step="${limitsIndex}"]`).click();
    assert.match(
      await page.locator('[data-intb-limits]').innerText(),
      /Info.cfg Group.*ground_truth_group.*does not prove answer isolation/s,
    );
    assert.equal(await page.locator('[data-intb-scene] img').count(), 0);
  }
  if (plan.recipe === 'bcer-brain-grade-v1') {
    const operationIndex = plan.beats.findIndex((b) => b.scene === 'operation');
    await page.locator(`[data-story-step="${operationIndex}"]`).click();
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    const focus = page.locator('[data-stage-focus]');
    assert.equal(await focus.getAttribute('data-stage-focus'), 'identify_sequences');
    await page.getByRole('button', { name: '4. classify brain glioma grade', exact: true }).click();
    assert.equal(await focus.getAttribute('data-stage-focus'), 'classify_brain_glioma_grade');
    assert.match(await focus.innerText(), /≥35 ml.*texture fields.*uncalibrated/s);
    assert.match(await focus.innerText(), /Predicted grade: unset/);
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(output, `${label}-grade-rule.png`) });
    await page.getByRole('button', { name: '3. extract roi features', exact: true }).click();
    assert.match(await focus.innerText(), /resampled.*spacing product/s);
    await page.getByRole('button', { name: '2. brats mri segmentation', exact: true }).click();
    assert.match(await focus.innerText(), /heuristic fallback.*Missing bundle/s);
    await page.getByRole('button', { name: 'Follow story focus', exact: true }).click();
    assert.equal(await focus.getAttribute('data-stage-focus'), 'identify_sequences');
    await page.getByRole('button', { name: '4. classify brain glioma grade', exact: true }).click();
    await page.locator('[data-story-step="0"]').click();
    assert.equal(await page.locator('[data-intb-image-state="unavailable"]').count(), 1);
    await page.locator(`[data-story-step="${operationIndex}"]`).click();
    assert.equal(await focus.getAttribute('data-stage-focus'), 'identify_sequences');
    assert.equal(await page.locator('[data-intb-scene] img').count(), 0);
  }
  if (plan.recipe === 'healthagentbench-cxr-correction-v1') {
    const operationIndex = plan.beats.findIndex((b) => b.scene === 'operation');
    await page.locator(`[data-story-step="${operationIndex}"]`).click();
    const evidenceA = page.getByRole('combobox', { name: 'Existing draft clause A evidence' });
    const editA = page.getByRole('combobox', { name: 'Existing draft clause A edit' });
    const result = page.locator('[data-inta-cxr-gate-result]').first();
    assert.match(await result.innerText(), /Needs current\/prior evidence check/);
    assert.equal(await editA.locator('option').count(), 3);
    await evidenceA.selectOption('conflict');
    assert.match(await result.innerText(), /Cannot keep/);
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(output, `${label}-clause-conflict.png`) });
    await editA.selectOption('correct');
    assert.match(await result.innerText(), /Allowed edit path.*no clinical correctness/);
    await evidenceA.selectOption('supported');
    await editA.selectOption('remove');
    assert.match(await result.innerText(), /Review deletion/);
    await page
      .getByRole('combobox', { name: 'Existing draft clause B evidence' })
      .selectOption('supported');
    assert.match(
      await page.locator('[data-inta-cxr-gate-result]').nth(1).innerText(),
      /Allowed edit path/,
    );
    await page.getByRole('button', { name: 'Reset schematic', exact: true }).click();
    assert.equal(await evidenceA.inputValue(), 'unchecked');
    assert.equal(await editA.inputValue(), 'keep');
    await evidenceA.selectOption('conflict');
    await page.locator('[data-story-step="0"]').click();
    await page.locator(`[data-story-step="${operationIndex}"]`).click();
    assert.equal(await evidenceA.inputValue(), 'unchecked');
    assert.equal(await page.locator('[data-inta-scene] img').count(), 0);
    assert.equal(await page.locator('[data-inta-reference-state="revealed"]').count(), 0);
  }
  if (plan.recipe === 'healthagentbench-tumor-tiles-v1') {
    assert.equal(await page.locator('[data-inta-scene] img').count(), 0);
    assert.doesNotMatch(await page.locator('[data-inta-scene]').innerText(), /tumor_076/);
    const inspectIndex = plan.beats.findIndex((b) => b.scene === 'inspect');
    await page.locator(`[data-story-step="${inspectIndex}"]`).click();
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    const slider = page.getByRole('slider', {
      name: 'Unclassified tile coordinate, 0 through 699',
    });
    await slider.fill('699');
    assert.equal(await page.locator('[data-inta-unclassified-cursor]').getAttribute('height'), '9');
    assert.match(
      await page.locator('[data-inta-inspect] figcaption').innerText(),
      /Cursor \(27, 24\).*x \[110592, 114688\).*y \[98304, 100352\)/,
    );
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(output, `${label}-last-grid-cell.png`) });
    await slider.fill('0');
    assert.equal(
      await page.locator('[data-inta-unclassified-cursor]').getAttribute('height'),
      '18',
    );
    assert.match(
      await page.locator('[data-inta-inspect] figcaption').innerText(),
      /Cursor \(0, 0\)/,
    );
    await slider.fill('699');
    await page.getByRole('button', { name: 'Follow story cursor', exact: true }).click();
    assert.notEqual(await slider.inputValue(), '699');
    await slider.fill('699');
    await page.locator('[data-story-step="0"]').click();
    assert.equal(await page.locator('[data-inta-original-image="absent"]').count(), 1);
    await page.locator(`[data-story-step="${inspectIndex}"]`).click();
    assert.notEqual(await slider.inputValue(), '699');
    assert.equal(await page.locator('[data-inta-reference-state="revealed"]').count(), 0);
  }
  if (plan.recipe === 'radagent-report-v1') {
    const inspectIndex = plan.beats.findIndex((b) => b.scene === 'inspect');
    await page.locator(`[data-story-step="${inspectIndex}"]`).click();
    const picker = page.getByRole('combobox', { name: 'RadAgent checklist area' });
    assert.equal(await picker.locator('option').count(), 9);
    assert.match(await page.locator('[data-inta-checklist-text]').innerText(), /airways/);
    await picker.selectOption('8');
    assert.match(
      await page.locator('[data-inta-checklist-text]').innerText(),
      /devices.*catheters/s,
    );
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(output, `${label}-checklist-devices.png`) });
    await picker.selectOption('4');
    assert.match(await page.locator('[data-inta-checklist-text]').innerText(), /contrast-enhanced/);
    await page.locator('[data-story-step="0"]').click();
    await page.locator(`[data-story-step="${inspectIndex}"]`).click();
    assert.match(await page.locator('[data-inta-checklist-text]').innerText(), /airways/);
  }
  if (plan.recipe === 'healthagentbench-ct-findings-v1') {
    const operationIndex = plan.beats.findIndex((b) => b.scene === 'operation');
    await page.locator(`[data-story-step="${operationIndex}"]`).click();
    const result = page.locator('[data-inta-rule-result]');
    assert.match(await result.innerText(), /2\/3.*returns 0/);
    const third = page.getByRole('combobox', { name: 'Hypothetical name 3 comparison' });
    await third.selectOption('match');
    assert.match(await result.innerText(), /3\/3.*returns 1/);
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(output, `${label}-hypothetical-all-match.png`) });
    await third.selectOption('mismatch');
    assert.match(await result.innerText(), /2\/3.*returns 0/);
    await page
      .getByRole('combobox', { name: 'Hypothetical name 1 comparison' })
      .selectOption('missing');
    assert.match(await result.innerText(), /1\/3.*returns 0/);
    await page.getByRole('button', { name: 'Reset illustration', exact: true }).click();
    assert.match(await result.innerText(), /2\/3.*returns 0/);
    await third.selectOption('match');
    await page.locator('[data-story-step="0"]').click();
    await page.locator(`[data-story-step="${operationIndex}"]`).click();
    assert.match(await result.innerText(), /2\/3.*returns 0/);
    assert.equal(await page.locator('[data-inta-reference-state="revealed"]').count(), 0);
  }
  if (plan.recipe === 'automed-full-tsg-multiorgan-v1') {
    const mappingIndex = plan.beats.findIndex((b) => b.scene === 'mapping');
    await page.locator(`[data-story-step="${mappingIndex}"]`).click();
    const picker = page.getByRole('combobox', { name: 'Full class mapping' });
    await picker.waitFor();
    assert.equal(await picker.locator('option').count(), 117);
    await picker.selectOption('116');
    assert.equal(await page.locator('[data-automed-d-class-id]').innerText(), '117');
    assert.equal(await page.locator('[data-automed-d-class-name]').innerText(), 'vertebrae T9');
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(output, `${label}-class-117.png`) });
    await picker.selectOption('0');
    assert.equal(await page.locator('[data-automed-d-class-id]').innerText(), '1');
    assert.equal(
      await page.locator('[data-automed-d-class-name]').innerText(),
      'adrenal gland left',
    );
    await page.getByRole('button', { name: 'Follow playback' }).click();
  }
  if (selectors.referenceChannel === null) {
    assert.equal(plan.reference_policy, 'no-reference-assets');
    await page.locator('.scene-reset').click();
    await page.waitForFunction(
      () => document.querySelector('.scene-player')?.getAttribute('data-committed-frame') === '0',
    );
    assert.equal(await page.locator(selectors.reference).count(), 0);
    assert.equal(await page.locator(selectors.output).count(), 0);
    return;
  }
  const revealIndex = plan.beats.findIndex(
    (b) => b.channels[selectors.referenceChannel || 'reference'][1] === 1,
  );
  assert.ok(revealIndex >= 0, `${plan.id}: explicit reference reveal required`);
  await page.locator('.scene-reset').click();
  await page.waitForFunction(
    () => document.querySelector('.scene-player')?.getAttribute('data-committed-frame') === '0',
  );
  assert.equal(await page.locator(selectors.reference).count(), 0);
  await page.locator(`[data-story-step="${revealIndex}"]`).click();
  if (plan.beats[revealIndex].channels[selectors.referenceChannel || 'reference'][0] <= 0.5) {
    assert.equal(await page.locator(selectors.reference).count(), 0);
    await page.locator('.scene-play').click();
    await page.locator(selectors.reference).first().waitFor();
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
  } else {
    await page.locator(selectors.reference).first().waitFor();
  }
  await page
    .locator('.scene-player')
    .screenshot({ path: path.join(output, `${label}-reference-revealed.png`) });
  await page.locator('.scene-reset').click();
  await page.waitForFunction(
    () => document.querySelector('.scene-player')?.getAttribute('data-committed-frame') === '0',
  );
  assert.equal(await page.locator(selectors.reference).count(), 0);
  assert.equal(await page.locator(selectors.output).count(), 0);
}

withBrowser(async (browser) => {
  report.browser = browser.version();
  const context = await browser.newContext({
    viewport: { width: 1280, height: 900 },
    deviceScaleFactor: 1,
    reducedMotion: 'reduce',
  });
  await context.route(/^https?:/, (route) => {
    report.remote_requests.push(route.request().url());
    return route.abort();
  });
  const page = await context.newPage();
  page.on('pageerror', (error) => report.errors.push(error.message));
  for (const id of fs
    .readdirSync(folder)
    .filter((id) => fs.existsSync(path.join(folder, id, 'plan.json')))) {
    const out = path.join(folder, id),
      plan = JSON.parse(fs.readFileSync(path.join(out, 'plan.json'))),
      row = { id, frames: [], locales: [], fallback: false };
    const receipt = JSON.parse(fs.readFileSync(path.join(out, 'receipt.json')));
    if (receipt.renderer === 'DOM/SVG planar')
      assert.equal(receipt.camera, 'Planar coordinate-preserving SVG/DOM');
    const url = pathToFileURL(path.join(out, 'index.html')).href;
    for (const locale of ['en', 'zh-CN']) {
      await page.goto(url + '?capture=1&lang=' + locale);
      await page.waitForFunction(() => window.__tb3ExplainerCapture);
      const frames = [
        0,
        plan.beats[Math.floor(plan.beats.length / 2)].endFrame - 1,
        plan.durationFrames - 1,
        ...([
          'mask-screen-v1',
          'anatomy-curation-v1',
          'ct-context-v1',
          'imaging101-eht-original-v1',
          'imaging101-eht-features-dynamic-v1',
          'imaging101-eht-dynamic-v1',
          'imaging101-eht-uq-v1',
          'imaging101-dti-v1',
          'imaging101-deflectometry-v1',
          'imaging101-fan-beam-v1',
          'imaging101-dual-energy-v1',
          'imaging101-ptychography-v1',
          'imaging101-nlos-v1',
          'imaging101-cars-v1',
          'rex-topcow-v1',
          'automed-multiorgan-v1',
          'bcer-workflow-v1',
          'abra-annotation-v1',
          'history-sourcing-v1',
          'mri-importer-v1',
          'localized-ct-v1',
          'aneurysm-localization-v1',
          'segmentation-calibration-v1',
          'dental-v3-v1',
          'dental-v2-v1',
          'dental-original-v1',
          'ct-organ-v1',
          'named-landmarks-v1',
          'cardiac-contour-v1',
          'cardiac-anchor-v1',
          'cardiac-material-v1',
          'automed-full-heart-seg-v1',
          'automed-full-feta-seg-v1',
          'automed-full-colon-seg-v1',
          'automed-full-aeropath-seg-v1',
          'automed-full-vindr-cxr-detection-v1',
          'automed-full-grazpedwri-detection-v1',
          'automed-full-dentex-detection-v1',
          'automed-full-bccd-detection-v1',
          'rex-topcow-mr-edges-v1',
          'rex-topcow-ct-edges-v1',
          'rex-topcow-mr-box-v1',
          'rex-topcow-ct-box-v1',
          'rex-topcow-mr-seg-v1',
          'rex-topbrain-mr-v1',
          'rex-topbrain-ct-v1',
          'rex-seg-a-v1',
          'rexmle-puma-track2-task2-v1',
          'rexmle-puma-track1-task2-v1',
          'rexmle-puma-track1-task1-v1',
          'rex-panther-task2-v1',
          'rex-panther-task1-v1',
          'rexmle-neurips-cellseg-v1',
          'rex-isles22-v1',
          'rexmle-dentex-v1',
          'abra-longitudinal-v1',
          'bcer-prostate-registration-v1',
          'bcer-brain-v1',
          'automed-kidney-v1',
          'report-reading-v1',
          'cardiac-mask-mechanics-v1',
          'cardiac-real-echo-v1',
          'clinical-cavity-v1',
          'respiratory-v1',
          'registration-analysis-v1',
          'resect-correspondence-v1',
          'resect-pilot-v1',
          'vessel-source-v1',
          'airway-repair-v1',
          'topbrain-screen-v1',
          'hubmap-inventory-v1',
          'tiger-context-v1',
          'longitudinal-mri-v1',
          'longitudinal-ct-original-v1',
          'longitudinal-ct-revised-v1',
        ].includes(plan.recipe)
          ? plan.beats.map((b) => b.endFrame - 1)
          : []),
      ];
      if (
        [
          'hubmap-inventory-v1',
          'tiger-context-v1',
          'longitudinal-mri-v1',
          'longitudinal-ct-original-v1',
          'longitudinal-ct-revised-v1',
        ].includes(plan.recipe)
      ) {
        for (const b of plan.beats) frames.push(b.startFrame);
      }
      if (cardiacRecipes.has(plan.recipe)) {
        for (const b of plan.beats) {
          frames.push(b.startFrame);
          const reveal = b.channels[cardiacSelectors(plan).referenceChannel || 'reference'] || [
            0, 0,
          ];
          if (reveal[0] !== reveal[1])
            frames.push(
              Math.floor((b.startFrame + b.endFrame) / 2) - 1,
              Math.floor((b.startFrame + b.endFrame) / 2),
            );
        }
      }
      if (plan.recipe === 'automed-full-prostate-seg-v1') {
        const helper = plan.beats.find((b) => b.scene === 'helper');
        frames.push(
          Math.floor((helper.startFrame + helper.endFrame) / 2) - 1,
          Math.floor((helper.startFrame + helper.endFrame) / 2),
          helper.startFrame + Math.floor(0.85 * (helper.endFrame - helper.startFrame)),
        );
      }
      if (plan.recipe === 'imaging101-eht-original-v1') {
        const selections = {
          inputs: 21,
          closures: 6,
          observables: 2,
          imaging: 4,
          outputs: 3,
          scoring: 4,
          limits: 4,
        };
        for (const b of plan.beats) {
          frames.push(b.startFrame);
          if (b.scene === 'reference') {
            frames.push(Math.floor((b.startFrame + b.endFrame) / 2) - 1);
            frames.push(Math.floor((b.startFrame + b.endFrame) / 2));
            for (const fraction of Array.from({ length: 3 }, (_, i) => 0.5 + (i + 0.5) / 6))
              frames.push(Math.floor(b.startFrame + fraction * (b.endFrame - b.startFrame)));
          } else {
            const count = selections[b.scene];
            for (let i = 0; i < count; i++)
              frames.push(
                Math.floor(b.startFrame + ((i + 0.5) / count) * (b.endFrame - b.startFrame)),
              );
          }
        }
      }
      if (plan.recipe === 'imaging101-eht-features-dynamic-v1') {
        const selections = {
          inputs: 10,
          closures: 6,
          model: 4,
          posterior: 4,
          diagnostics: 4,
          scoring: 4,
          limits: 4,
        };
        for (const b of plan.beats) {
          frames.push(b.startFrame);
          if (b.scene === 'reference') {
            frames.push(Math.floor((b.startFrame + b.endFrame) / 2) - 1);
            frames.push(Math.floor((b.startFrame + b.endFrame) / 2));
            for (const fraction of Array.from({ length: 10 }, (_, i) => 0.5 + (i + 0.5) / 20))
              frames.push(Math.floor(b.startFrame + fraction * (b.endFrame - b.startFrame)));
          } else {
            const count = selections[b.scene];
            for (let i = 0; i < count; i++)
              frames.push(
                Math.floor(b.startFrame + ((i + 0.5) / count) * (b.endFrame - b.startFrame)),
              );
          }
        }
      }
      if (plan.recipe === 'imaging101-eht-dynamic-v1') {
        const selections = {
          inputs: 12,
          operator: 4,
          temporal: 8,
          output: 12,
          diagnostics: 12,
          scoring: 4,
          limits: 4,
        };
        for (const b of plan.beats) {
          frames.push(b.startFrame);
          if (b.scene === 'reference') {
            frames.push(Math.floor((b.startFrame + b.endFrame) / 2) - 1);
            frames.push(Math.floor((b.startFrame + b.endFrame) / 2));
            for (const fraction of Array.from({ length: 12 }, (_, i) => 0.5 + (i + 0.5) / 24))
              frames.push(Math.floor(b.startFrame + fraction * (b.endFrame - b.startFrame)));
          } else {
            const count = selections[b.scene];
            for (let i = 0; i < count; i++)
              frames.push(
                Math.floor(b.startFrame + ((i + 0.5) / count) * (b.endFrame - b.startFrame)),
              );
          }
        }
      }
      if (plan.recipe === 'imaging101-eht-uq-v1') {
        const selections = {
          inputs: 100,
          closures: 5,
          prior: 2,
          samples: 8,
          output: 8,
          scoring: 5,
          limits: 4,
        };
        for (const b of plan.beats) {
          frames.push(b.startFrame);
          if (b.scene === 'reference') {
            frames.push(Math.floor((b.startFrame + b.endFrame) / 2) - 1);
            frames.push(Math.floor((b.startFrame + b.endFrame) / 2));
            for (const fraction of [0.625, 0.875])
              frames.push(Math.floor(b.startFrame + fraction * (b.endFrame - b.startFrame)));
          } else {
            const count = selections[b.scene];
            for (let i = 0; i < count; i++)
              frames.push(
                Math.floor(b.startFrame + ((i + 0.5) / count) * (b.endFrame - b.startFrame)),
              );
          }
        }
      }
      if (plan.recipe === 'imaging101-dti-v1') {
        const selections = {
          inputs: 4,
          gradients: 31,
          fit: 5,
          tensor: 5,
          output: 2,
          scoring: 6,
          limits: 4,
        };
        for (const b of plan.beats) {
          frames.push(b.startFrame);
          if (b.scene === 'reference') {
            frames.push(Math.floor((b.startFrame + b.endFrame) / 2) - 1);
            frames.push(Math.floor((b.startFrame + b.endFrame) / 2));
            for (const fraction of [0.625, 0.875])
              frames.push(Math.floor(b.startFrame + fraction * (b.endFrame - b.startFrame)));
          } else {
            const count = selections[b.scene];
            for (let i = 0; i < count; i++)
              frames.push(
                Math.floor(b.startFrame + ((i + 0.5) / count) * (b.endFrame - b.startFrame)),
              );
          }
        }
      }
      if (plan.recipe === 'imaging101-deflectometry-v1') {
        for (const b of plan.beats) {
          frames.push(b.startFrame);
          for (const fraction of [1 / 6, 1 / 2, 5 / 6])
            frames.push(Math.floor(b.startFrame + fraction * (b.endFrame - b.startFrame)));
          if (b.scene === 'phase')
            frames.push(Math.floor(b.startFrame + (3 / 8) * (b.endFrame - b.startFrame)));
          if (b.scene === 'reference') {
            frames.push(Math.floor(b.startFrame + (3 / 4) * (b.endFrame - b.startFrame)));
            frames.push(Math.floor((b.startFrame + b.endFrame) / 2) - 1);
          }
        }
      }
      if (plan.recipe === 'imaging101-fan-beam-v1') {
        for (const b of plan.beats) {
          frames.push(b.startFrame);
          for (const fraction of [1 / 6, 1 / 2, 5 / 6])
            frames.push(Math.floor(b.startFrame + fraction * (b.endFrame - b.startFrame)));
        }
      }
      if (plan.recipe === 'imaging101-dual-energy-v1') {
        for (const b of plan.beats) {
          frames.push(b.startFrame);
          for (const fraction of [1 / 6, 1 / 2, 5 / 6])
            frames.push(Math.floor(b.startFrame + fraction * (b.endFrame - b.startFrame)));
        }
      }
      if (plan.recipe === 'imaging101-ptychography-v1') {
        for (const b of plan.beats) {
          frames.push(b.startFrame);
          for (const fraction of [1 / 6, 1 / 2, 5 / 6])
            frames.push(Math.floor(b.startFrame + fraction * (b.endFrame - b.startFrame)));
        }
      }
      if (plan.recipe === 'imaging101-nlos-v1') {
        for (const b of plan.beats) {
          frames.push(b.startFrame);
          for (const fraction of [1 / 6, 1 / 2, 5 / 6])
            frames.push(Math.floor(b.startFrame + fraction * (b.endFrame - b.startFrame)));
        }
      }
      if (plan.recipe === 'imaging101-cars-v1') {
        for (const b of plan.beats) {
          frames.push(b.startFrame);
          for (const fraction of [1 / 6, 1 / 2, 5 / 6])
            frames.push(Math.floor(b.startFrame + fraction * (b.endFrame - b.startFrame)));
        }
      }
      if (plan.recipe === 'rex-topcow-v1') {
        for (const b of plan.beats) frames.push(b.startFrame);
        for (const [scene, count] of [
          ['inputs', 3],
          ['labels', 13],
          ['reference', 3],
          ['metrics', 5],
          ['topology', 2],
          ['geometry', 2],
        ]) {
          const b = plan.beats.find((b) => b.scene === scene);
          for (let i = 0; i < count; i++)
            frames.push(
              Math.floor(
                b.startFrame +
                  (scene === 'reference' ? 0.5 + (i + 0.5) / count / 2 : (i + 0.5) / count) *
                    (b.endFrame - b.startFrame),
              ),
            );
        }
      }
      if (plan.recipe === 'automed-multiorgan-v1') {
        for (const b of plan.beats) frames.push(b.startFrame);
        for (const [scene, count] of [
          ['inputs', 3],
          ['workflow', 5],
          ['remap', 5],
          ['geometry', 2],
          ['reference', 5],
          ['scoring', 2],
          ['coverage', 7],
        ]) {
          const b = plan.beats.find((b) => b.scene === scene);
          for (let i = 0; i < count; i++)
            frames.push(
              Math.floor(
                b.startFrame +
                  (scene === 'reference' ? 0.5 + (i + 0.5) / count / 2 : (i + 0.5) / count) *
                    (b.endFrame - b.startFrame),
              ),
            );
        }
      }
      if (plan.recipe === 'bcer-workflow-v1') {
        for (const b of plan.beats) frames.push(b.startFrame);
        for (const [scene, count] of [
          ['geometry', 3],
          ['dependencies', 8],
          ['artifacts', 4],
          ['metrics', 5],
        ]) {
          const b = plan.beats.find((b) => b.scene === scene);
          for (let i = 0; i < count; i++)
            frames.push(
              Math.floor(b.startFrame + ((i + 0.5) / count) * (b.endFrame - b.startFrame)),
            );
        }
      }
      if (plan.recipe === 'abra-annotation-v1') {
        for (const b of plan.beats) frames.push(b.startFrame);
        for (const [scene, count] of [
          ['navigate', 3],
          ['reference', 8],
          ['oracle', 5],
          ['scoring', 6],
        ]) {
          const b = plan.beats.find((b) => b.scene === scene);
          for (let i = 0; i < count; i++) {
            const t = (i + 0.5) / count;
            frames.push(
              Math.floor(
                b.startFrame +
                  (scene === 'reference' ? 0.5 + t / 2 : t) * (b.endFrame - b.startFrame),
              ),
            );
          }
        }
      }
      if (plan.recipe === 'ct-context-v1') {
        for (const b of plan.beats) frames.push(b.startFrame);
        for (const [scene, count] of [
          ['fields', 9],
          ['reference', 4],
        ]) {
          const b = plan.beats.find((b) => b.scene === scene);
          for (let i = 0; i < count; i++)
            frames.push(
              Math.floor(b.startFrame + ((i + 0.5) / count) * (b.endFrame - b.startFrame)),
            );
        }
      }
      if (plan.recipe === 'history-sourcing-v1') {
        for (const b of plan.beats) frames.push(b.startFrame);
        for (const [scene, count] of [
          ['excerpts', 8],
          ['candidates', 5],
          ['lineage', 4],
          ['controls', 4],
          ['reference', 4],
        ]) {
          const b = plan.beats.find((b) => b.scene === scene);
          for (let i = 0; i < count; i++)
            frames.push(
              Math.floor(b.startFrame + ((i + 0.5) / count) * (b.endFrame - b.startFrame)),
            );
        }
      }
      if (plan.recipe === 'mri-importer-v1') {
        for (const b of plan.beats) frames.push(b.startFrame);
        for (const [scene, count] of [
          ['association', 12],
          ['geometry', 8],
          ['reference', 4],
        ]) {
          const b = plan.beats.find((b) => b.scene === scene);
          for (let i = 0; i < count; i++)
            frames.push(
              Math.floor(b.startFrame + ((i + 0.5) / count) * (b.endFrame - b.startFrame)),
            );
        }
      }
      if (plan.recipe === 'localized-ct-v1') {
        for (const b of plan.beats) frames.push(b.startFrame);
        for (const [scene, count] of [
          ['axial', 4],
          ['orthogonal', 6],
          ['serial', 12],
          ['reference', 4],
        ]) {
          const b = plan.beats.find((b) => b.scene === scene);
          for (let i = 0; i < count; i++)
            frames.push(
              Math.floor(b.startFrame + ((i + 0.5) / count) * (b.endFrame - b.startFrame)),
            );
        }
      }
      if (plan.recipe === 'aneurysm-localization-v1') {
        for (const b of plan.beats) frames.push(b.startFrame);
        for (const [scene, count] of [
          ['slabs', 12],
          ['depth', 7],
          ['reference', 4],
        ]) {
          const b = plan.beats.find((b) => b.scene === scene);
          for (let i = 0; i < count; i++)
            frames.push(
              Math.floor(b.startFrame + ((i + 0.5) / count) * (b.endFrame - b.startFrame)),
            );
        }
      }
      if (plan.recipe === 'segmentation-calibration-v1') {
        for (const b of plan.beats) frames.push(b.startFrame);
        for (const scene of [
          'sampling',
          'preprocess',
          'reference',
          'sensitivity',
          'duodenum',
          'backend',
        ]) {
          const b = plan.beats.find((b) => b.scene === scene);
          for (const fraction of [0.08, 0.25, 0.42, 0.58, 0.75, 0.92])
            frames.push(Math.round(b.startFrame + fraction * (b.endFrame - b.startFrame - 1)));
        }
      }
      if (plan.recipe === 'dental-v3-v1') {
        for (const b of plan.beats) frames.push(b.startFrame);
        for (const scene of [
          'example',
          'transfer',
          'shape',
          'pulp-gain',
          'pulp-reach',
          'pulp-loss',
          'canal-crop',
          'canal-extent',
        ]) {
          const b = plan.beats.find((b) => b.scene === scene);
          for (const fraction of [0.1, 0.3, 0.5, 0.7, 0.9])
            frames.push(Math.round(b.startFrame + fraction * (b.endFrame - b.startFrame - 1)));
        }
      }
      if (plan.recipe === 'dental-v2-v1') {
        for (const b of plan.beats) frames.push(b.startFrame);
        for (const scene of [
          'example',
          'transfer',
          'identity',
          'pulp-contents',
          'pulp-clip',
          'canals',
          'small-canals',
        ]) {
          const b = plan.beats.find((b) => b.scene === scene);
          for (const fraction of [0.125, 0.375, 0.625, 0.875])
            frames.push(Math.round(b.startFrame + fraction * (b.endFrame - b.startFrame - 1)));
        }
      }
      if (plan.recipe === 'topbrain-screen-v1') {
        for (const scene of ['cohort', 'variants', 'contacts', 'calibration', 'cpr']) {
          const beat = plan.beats.find((b) => b.scene === scene);
          for (const fraction of [0, 0.25, 0.5, 0.75])
            frames.push(
              Math.round(beat.startFrame + fraction * (beat.endFrame - beat.startFrame - 1)),
            );
        }
      }
      if (['vessel-source-v1', 'airway-repair-v1'].includes(plan.recipe)) {
        const inspect = plan.beats.find((b) => b.scene === 'inspect');
        frames.push(Math.floor((inspect.startFrame + inspect.endFrame) / 2));
        if (plan.recipe === 'airway-repair-v1') {
          for (const scene of ['controls', 'cpr', 'route']) {
            const beat = plan.beats.find((b) => b.scene === scene);
            frames.push(beat.startFrame, Math.floor((beat.startFrame + beat.endFrame) / 2));
          }
        }
      }
      for (const frame of new Set(frames)) {
        const bytes = await captureComposedFrame(page, {
          frame,
          fps: plan.fps,
          width: 1280,
          height: 720,
        });
        const file = `review-${locale}-${frame}.png`;
        fs.writeFileSync(path.join(out, file), bytes);
        row.frames.push({ locale, frame, file, sha256: sha(bytes) });
        if (id === 'wsi-search') {
          const canvas = page.locator('.scene-stage svg');
          const selection = canvas.locator('g[opacity]');
          assert.equal(await selection.getAttribute('opacity'), frame === 0 ? '0' : '1');
          const tile = canvas.locator('rect[fill="#dae5e6"]');
          assert.equal(await tile.getAttribute('width'), frame === 0 ? '130' : '520');
          const returned = canvas.getByText('level-0 (2680, 2040) px', { exact: true });
          assert.equal(await returned.count(), frame === plan.durationFrames - 1 ? 1 : 0);
        }
        if (plan.recipe === 'airway-repair-v1') {
          const panel = page.locator('[data-airway-output]');
          const legend = await page.locator('.scene-legend').boundingBox();
          assert.ok(legend && legend.y + legend.height <= 720, 'Airway legend clipped');
          assert.ok(
            await panel.evaluate((e) => e.scrollHeight <= e.clientHeight),
            'Airway output overflows',
          );
          if (frame === 0) {
            assert.equal(await page.locator('[data-airway-reference-image]').count(), 0);
            assert.equal(await page.locator('[data-airway-added-slice]').count(), 0);
          }
        }
        if (plan.recipe === 'longitudinal-ct-revised-v1') {
          const legend = await page.locator('.scene-legend').boundingBox();
          assert.ok(legend && legend.y + legend.height <= 720, 'CT legend clipped');
          assert.ok(
            await page
              .locator('[data-revised-output-panel]')
              .evaluate((e) => e.scrollHeight <= e.clientHeight),
            'CT output overflows',
          );
          const figure = page.locator('[data-revised-scene]');
          assert.deepEqual(
            await figure.evaluate((svg) => {
              const box = svg.getBoundingClientRect();
              return [...svg.querySelectorAll('text')]
                .filter((t) => {
                  const b = t.getBoundingClientRect();
                  return (
                    b.left < box.left - 1 || b.right > box.right + 1 || b.bottom > box.bottom + 1
                  );
                })
                .map((t) => t.textContent);
            }),
            [],
            'CT figure label outside bounds',
          );
          if (frame === 0) {
            assert.equal(await page.locator('[data-ct-reference], [data-ct-output]').count(), 0);
            assert.equal(await page.locator('[data-ct-input]').count(), 4);
          }
          const b = plan.beats.find((b) => frame >= b.startFrame && frame < b.endFrame);
          if (b.scene === 'decisions') {
            assert.equal(await page.locator('[data-revised-point]').count(), 2);
            if (frame === b.startFrame)
              assert.equal(await page.locator('image[data-ct-reference]').count(), 0);
            if (frame === b.endFrame - 1)
              assert.equal(await page.locator('image[data-ct-reference]').count(), 2);
          }
          if (['partition', 'newfocus'].includes(b.scene) && frame === b.endFrame - 1)
            assert.ok(await page.locator('[data-revised-local-id]').count());
          if (b.scene === 'partition' && frame === b.endFrame - 1)
            assert.ok(await page.locator('image[data-ct-reference]').count());
        }
        if (plan.recipe === 'longitudinal-ct-original-v1') {
          const legend = await page.locator('.scene-legend').boundingBox();
          assert.ok(legend && legend.y + legend.height <= 720, 'CT legend clipped');
          assert.ok(
            await page
              .locator('[data-ct-output-panel]')
              .evaluate((e) => e.scrollHeight <= e.clientHeight),
            'CT output overflows',
          );
          const figure = page.locator('[data-ct-scene]');
          assert.deepEqual(
            await figure.evaluate((svg) => {
              const box = svg.getBoundingClientRect();
              return [...svg.querySelectorAll('text')]
                .filter((t) => {
                  const b = t.getBoundingClientRect();
                  return (
                    b.left < box.left - 1 || b.right > box.right + 1 || b.bottom > box.bottom + 1
                  );
                })
                .map((t) => t.textContent);
            }),
            [],
            'CT figure label outside bounds',
          );
          if (frame === 0) {
            assert.equal(await page.locator('[data-ct-reference], [data-ct-output]').count(), 0);
            assert.equal(await page.locator('[data-ct-input]').count(), 2);
          }
          const b = plan.beats.find((b) => frame >= b.startFrame && frame < b.endFrame);
          if (b.scene === 'partition' && frame === b.endFrame - 1)
            assert.ok(await page.locator('[data-ct-reference] image[data-ct-reference]').count());
        }
        if (plan.recipe === 'longitudinal-mri-v1') {
          const legend = await page.locator('.scene-legend').boundingBox();
          assert.ok(legend && legend.y + legend.height <= 720, 'MRI legend clipped');
          assert.ok(
            await page
              .locator('[data-mri-output-panel]')
              .evaluate((e) => e.scrollHeight <= e.clientHeight),
            'MRI output overflows',
          );
          const b = plan.beats.find((b) => frame >= b.startFrame && frame < b.endFrame);
          const figure = page.locator('[data-mri-scene]');
          assert.deepEqual(
            await figure.evaluate((svg) => {
              const box = svg.getBoundingClientRect();
              return [...svg.querySelectorAll('text')]
                .filter((t) => {
                  const b = t.getBoundingClientRect();
                  return (
                    b.left < box.left - 1 || b.right > box.right + 1 || b.bottom > box.bottom + 1
                  );
                })
                .map((t) => t.textContent);
            }),
            [],
            'MRI figure label outside bounds',
          );
          if (frame === 0) {
            assert.equal(await page.locator('[data-mri-reference], [data-mri-output]').count(), 0);
            assert.equal(await page.locator('[data-mri-input]').count(), 6);
          }
          if (
            frame === b.endFrame - 1 &&
            ['phases', 'sequences', 'reference', 'forecast'].includes(b.scene)
          )
            assert.ok((await page.locator('[data-mri-reference]').count()) > 0);
        }
        if (plan.recipe === 'tiger-context-v1') {
          const legend = await page.locator('.scene-legend').boundingBox();
          assert.ok(legend && legend.y + legend.height <= 720, 'TIGER legend clipped');
          assert.ok(
            await page
              .locator('[data-tiger-output]')
              .evaluate((e) => e.scrollHeight <= e.clientHeight),
            'TIGER output overflows',
          );
          const beat = plan.beats.find((b) => frame >= b.startFrame && frame < b.endFrame);
          if (
            ['inputs', 'conditions', 'output', 'limits'].includes(beat.scene) ||
            (beat.scene === 'tissue' && frame === beat.startFrame)
          ) {
            assert.equal(await page.locator('[data-tiger-reference]').count(), 0);
            assert.equal(
              await page
                .locator('[data-tiger-measurement],[data-tiger-density],[data-tiger-coordinate]')
                .count(),
              0,
            );
          }
          if (beat.scene === 'density' && frame === beat.endFrame - 1) {
            assert.equal(await page.locator('[data-tiger-density] tbody tr').count(), 3);
            assert.equal(await page.locator('[data-tiger-reference] path').count(), 175);
            assert.match(await page.locator('[data-tiger-measurement]').textContent(), /2,049.19/);
          }
        }
        if (plan.recipe === 'hubmap-inventory-v1') {
          const panel = page.locator('[data-hubmap-output]');
          const legend = await page.locator('.scene-legend').boundingBox();
          assert.ok(legend && legend.y + legend.height <= 720, 'HuBMAP legend clipped');
          assert.ok(
            await panel.evaluate((e) => e.scrollHeight <= e.clientHeight),
            'HuBMAP output overflows',
          );
          const beat = plan.beats.find((b) => frame >= b.startFrame && frame < b.endFrame);
          if (
            ['inputs', 'helpers', 'detail', 'conditions', 'limits'].includes(beat.scene) ||
            (beat.scene === 'outline' && frame === beat.startFrame)
          ) {
            assert.equal(await page.locator('[data-hubmap-reference]').count(), 0);
            assert.equal(
              await page
                .locator(
                  '[data-hubmap-measurement], [data-hubmap-worked-rows], [data-hubmap-inventory]',
                )
                .count(),
              0,
            );
          }
          if (beat.scene === 'inventory' && frame === beat.endFrame - 1) {
            assert.equal(await page.locator('[data-hubmap-reference] path').count(), 99);
            assert.equal(await page.locator('[data-hubmap-worked-rows] tbody tr').count(), 5);
          }
          if (beat.scene === 'duplicate' && frame === beat.endFrame - 1) {
            assert.match(
              await page.locator('[data-hubmap-duplicate-count]').textContent(),
              /1 unique source object/,
            );
            assert.equal(await page.locator('[data-hubmap-reference] path').count(), 2);
          }
        }
        if (plan.recipe === 'topbrain-screen-v1') {
          const panel = page.locator('[data-brain-output]');
          const legend = await page.locator('.scene-legend').boundingBox();
          assert.ok(legend && legend.y + legend.height <= 720, 'TopBrain legend clipped');
          assert.ok(
            await panel.evaluate((e) => e.scrollHeight <= e.clientHeight),
            'TopBrain output overflows',
          );
          if (frame === 0) {
            assert.equal(await page.locator('[data-brain-reference-image]').count(), 0);
            assert.equal(await page.locator('[data-brain-answer]').count(), 0);
          }
        }
        if (plan.recipe === 'vessel-source-v1') {
          const output = page.locator('[data-vessel-output]');
          assert.ok(
            await output.evaluate((e) => e.scrollHeight <= e.clientHeight),
            'Source output overflows',
          );
          const box = await output.boundingBox();
          assert.ok(box && box.y + box.height <= 720, 'Source output clipped');
          if (frame === 0) {
            assert.equal(await page.locator('[data-vessel-reference-image]').count(), 0);
            assert.equal(await page.locator('[data-vessel-answer]').count(), 0);
            assert.equal(await page.locator('[data-vessel-node]').count(), 0);
          }
        }
        if (plan.recipe === 'resect-pilot-v1') {
          const output = page.locator('[data-pilot-output]');
          assert.ok(
            await output.evaluate((e) => e.scrollHeight <= e.clientHeight),
            'Pilot output overflows',
          );
          const box = await output.boundingBox();
          assert.ok(box && box.y + box.height <= 720, 'Pilot output clipped');
          if (frame === 0) {
            assert.equal(await page.locator('[data-pilot-point="reference"]').count(), 0);
            assert.equal(await page.locator('[data-pilot-answer]').count(), 0);
          }
        }
        if (plan.recipe === 'resect-correspondence-v1') {
          const output = page.locator('[data-resect-output]');
          assert.ok(
            await output.evaluate((e) => e.scrollHeight <= e.clientHeight),
            'RESECT output overflows',
          );
          const box = await output.boundingBox();
          assert.ok(box && box.y + box.height <= 720, 'RESECT output clipped');
          if ((await output.getAttribute('data-resect-output')) === 'helpers') {
            assert.equal(
              await page.locator('[data-resect-mask-legend="mri"]').getAttribute('fill'),
              '#e65b9f',
            );
            assert.equal(
              await page.locator('[data-resect-mask-legend="us"]').getAttribute('fill'),
              '#37cdcd',
            );
          }
          if (frame === 0) assert.equal(await page.locator('[data-resect-target]').count(), 0);
        }
        if (plan.recipe === 'registration-analysis-v1') {
          const output = page.locator('[data-registration-analysis-output]');
          assert.ok(
            await output.evaluate((e) => e.scrollHeight <= e.clientHeight),
            'Analysis output overflows',
          );
          const box = await output.boundingBox();
          assert.ok(box && box.y + box.height <= 720, 'Analysis output clipped');
          if (frame === 0) assert.equal(await page.locator('[data-analysis-reference]').count(), 0);
        }
        await checkCardiacFrame(page, plan, frame);
        if (plan.recipe === 'imaging101-eht-original-v1') {
          const name = await page
            .locator('[data-original-scene]')
            .getAttribute('data-original-scene');
          const beat = plan.beats.find((b) => b.scene === name);
          const progress = (frame - beat.startFrame) / (beat.endFrame - beat.startFrame - 1);
          const revealed = name === 'scoring' || (name === 'reference' && progress > 0.5);
          assert.equal(await page.locator('[data-original-reference]').count(), revealed ? 1 : 0);
          if (name === 'imaging')
            assert.equal(await page.locator('[data-original-panel]').count(), 1);
          if (name === 'outputs')
            assert.equal(await page.locator('[data-original-panel]').count(), 2);
          if (name === 'reference' && revealed) {
            assert.equal(await page.locator('[data-original-panel]').count(), 3);
            assert.equal(
              Number(
                await page.locator('[data-original-choice]').getAttribute('data-original-choice'),
              ),
              Math.min(2, Math.max(0, Math.floor((progress - 0.5) * 6))),
            );
          }
          const choices = { closures: 6, imaging: 4, outputs: 3, scoring: 4, limits: 4 };
          if (choices[name])
            assert.equal(
              Number(
                await page.locator('[data-original-choice]').getAttribute('data-original-choice'),
              ),
              Math.min(choices[name] - 1, Math.floor(progress * choices[name])),
            );
          for (const selector of [
            '.scene-player > header',
            '[data-original-scene]',
            '[data-original-output]',
            '.scene-legend',
          ]) {
            const box = await page.locator(selector).boundingBox();
            assert.ok(
              box && box.y + box.height <= 720,
              'Static closure clipping ' + selector + ' frame ' + frame,
            );
            assert.ok(
              await page.locator(selector).evaluate((e) => {
                if (!e.hasAttribute('data-original-scene'))
                  return e.scrollHeight <= e.clientHeight && e.scrollWidth <= e.clientWidth;
                // Overflowing trailing padding does not clip content. Check rendered
                // text fragments and image bounds against the actual clipping box.
                const box = e.getBoundingClientRect();
                const inside = (r) =>
                  r.width === 0 ||
                  r.height === 0 ||
                  (r.left >= box.left &&
                    r.top >= box.top &&
                    r.right <= box.right &&
                    r.bottom <= box.bottom);
                const walker = document.createTreeWalker(e, NodeFilter.SHOW_TEXT);
                while (walker.nextNode()) {
                  if (!walker.currentNode.textContent.trim()) continue;
                  const range = document.createRange();
                  range.selectNodeContents(walker.currentNode);
                  if (!Array.from(range.getClientRects()).every(inside)) return false;
                }
                return Array.from(e.querySelectorAll('svg,img')).every((n) =>
                  inside(n.getBoundingClientRect()),
                );
              }),
              'Static closure overflow ' + selector + ' frame ' + frame,
            );
          }
        }
        if (plan.recipe === 'imaging101-eht-features-dynamic-v1') {
          const name = await page
            .locator('[data-features-scene]')
            .getAttribute('data-features-scene');
          const beat = plan.beats.find((b) => b.scene === name);
          const revealed =
            ['diagnostics', 'scoring'].includes(name) ||
            (name === 'reference' &&
              frame > beat.startFrame + (beat.endFrame - beat.startFrame - 1) / 2);
          assert.equal(await page.locator('[data-features-reference]').count(), revealed ? 1 : 0);
          if (name === 'model')
            assert.equal(await page.locator('[data-features-panel]').count(), 2);
          if (name === 'inputs') {
            const actual = Number(
              await page.locator('[data-features-epoch]').getAttribute('data-features-epoch'),
            );
            const expected = Math.min(
              9,
              Math.floor(((frame - beat.startFrame) / (beat.endFrame - beat.startFrame - 1)) * 10),
            );
            assert.equal(actual, expected, 'Displayed epoch follows source time order');
          }
          if (name === 'reference' && revealed)
            assert.equal(await page.locator('[data-features-panel]').count(), 3);
          if (name === 'reference' && revealed) {
            const actual = Number(
              await page.locator('[data-features-epoch]').getAttribute('data-features-epoch'),
            );
            const progress = (frame - beat.startFrame) / (beat.endFrame - beat.startFrame - 1);
            assert.equal(actual, Math.min(9, Math.max(0, Math.floor((progress - 0.5) * 20))));
          }
          const choices = {
            closures: 6,
            model: 4,
            posterior: 4,
            diagnostics: 4,
            scoring: 4,
            limits: 4,
          };
          if (choices[name]) {
            const actual = Number(
              await page.locator('[data-features-choice]').getAttribute('data-features-choice'),
            );
            assert.equal(
              actual,
              Math.min(
                choices[name] - 1,
                Math.floor(
                  ((frame - beat.startFrame) / (beat.endFrame - beat.startFrame - 1)) *
                    choices[name],
                ),
              ),
            );
          }
          for (const selector of [
            '.scene-player > header',
            '[data-features-scene]',
            '[data-features-output]',
            '.scene-legend',
          ]) {
            const box = await page.locator(selector).boundingBox();
            assert.ok(
              box && box.y + box.height <= 720,
              'Dynamic features clipping ' + selector + ' frame ' + frame,
            );
            assert.ok(
              await page.locator(selector).evaluate((e) => {
                if (!e.hasAttribute('data-features-scene'))
                  return e.scrollHeight <= e.clientHeight && e.scrollWidth <= e.clientWidth;
                // Overflowing trailing padding does not clip content. Check rendered
                // text fragments and image bounds against the actual clipping box.
                const box = e.getBoundingClientRect();
                const inside = (r) =>
                  r.width === 0 ||
                  r.height === 0 ||
                  (r.left >= box.left &&
                    r.top >= box.top &&
                    r.right <= box.right &&
                    r.bottom <= box.bottom);
                const walker = document.createTreeWalker(e, NodeFilter.SHOW_TEXT);
                while (walker.nextNode()) {
                  if (!walker.currentNode.textContent.trim()) continue;
                  const range = document.createRange();
                  range.selectNodeContents(walker.currentNode);
                  if (!Array.from(range.getClientRects()).every(inside)) return false;
                }
                return Array.from(e.querySelectorAll('svg,img')).every((n) =>
                  inside(n.getBoundingClientRect()),
                );
              }),
              'Dynamic features overflow ' + selector + ' frame ' + frame,
            );
          }
        }
        if (plan.recipe === 'imaging101-eht-dynamic-v1') {
          const name = await page
            .locator('[data-dynamic-scene]')
            .getAttribute('data-dynamic-scene');
          const beat = plan.beats.find((b) => b.scene === name);
          const revealed =
            ['diagnostics', 'scoring'].includes(name) ||
            (name === 'reference' &&
              frame > beat.startFrame + (beat.endFrame - beat.startFrame - 1) / 2);
          assert.equal(await page.locator('[data-dynamic-reference]').count(), revealed ? 1 : 0);
          if (name === 'output')
            assert.equal(await page.locator('[data-dynamic-panel]').count(), 2);
          if (['inputs', 'output'].includes(name)) {
            const actual = Number(
              await page.locator('[data-dynamic-epoch]').getAttribute('data-dynamic-epoch'),
            );
            const expected = Math.min(
              11,
              Math.floor(((frame - beat.startFrame) / (beat.endFrame - beat.startFrame - 1)) * 12),
            );
            assert.equal(actual, expected, 'Displayed epoch follows source time order');
          }
          if (name === 'reference' && revealed)
            assert.equal(await page.locator('[data-dynamic-panel]').count(), 3);
          for (const selector of [
            '.scene-player > header',
            '[data-dynamic-scene]',
            '[data-dynamic-output]',
            '.scene-legend',
          ]) {
            const box = await page.locator(selector).boundingBox();
            assert.ok(
              box && box.y + box.height <= 720,
              'Dynamic EHT clipping ' + selector + ' frame ' + frame,
            );
            assert.ok(
              await page.locator(selector).evaluate((e) => {
                if (!e.hasAttribute('data-dynamic-scene'))
                  return e.scrollHeight <= e.clientHeight && e.scrollWidth <= e.clientWidth;
                // Overflowing trailing padding does not clip content. Check rendered
                // text fragments and image bounds against the actual clipping box.
                const box = e.getBoundingClientRect();
                const inside = (r) =>
                  r.width === 0 ||
                  r.height === 0 ||
                  (r.left >= box.left &&
                    r.top >= box.top &&
                    r.right <= box.right &&
                    r.bottom <= box.bottom);
                const walker = document.createTreeWalker(e, NodeFilter.SHOW_TEXT);
                while (walker.nextNode()) {
                  if (!walker.currentNode.textContent.trim()) continue;
                  const range = document.createRange();
                  range.selectNodeContents(walker.currentNode);
                  if (!Array.from(range.getClientRects()).every(inside)) return false;
                }
                return Array.from(e.querySelectorAll('svg,img')).every((n) =>
                  inside(n.getBoundingClientRect()),
                );
              }),
              'Dynamic EHT overflow ' + selector + ' frame ' + frame,
            );
          }
        }
        if (plan.recipe === 'imaging101-eht-uq-v1') {
          const name = await page.locator('[data-eht-scene]').getAttribute('data-eht-scene');
          const beat = plan.beats.find((b) => b.scene === name);
          const revealed =
            name === 'reference' &&
            frame > beat.startFrame + (beat.endFrame - beat.startFrame - 1) / 2;
          assert.equal(await page.locator('[data-eht-reference]').count(), revealed ? 1 : 0);
          if (name === 'output') assert.equal(await page.locator('[data-eht-panel]').count(), 2);
          if (name === 'closures') {
            const values = await page
              .locator('[data-eht-closure-value]')
              .evaluateAll((es) => es.map((e) => Number(e.getAttribute('data-eht-closure-value'))));
            const inputs = JSON.parse(
              fs.readFileSync(
                path.join(__dirname, '../presentation/task-explorer/imaging101-eht-uq/inputs.json'),
              ),
            );
            assert.ok(Math.abs(values[0] - inputs.witnesses.phase.observed) < 1e-9);
            assert.ok(Math.abs(values[1] - inputs.witnesses.amplitude.observed) < 1e-9);
          }
          for (const selector of [
            '.scene-player > header',
            '[data-eht-scene]',
            '[data-eht-output]',
            '.scene-legend',
          ]) {
            const box = await page.locator(selector).boundingBox();
            assert.ok(
              box && box.y + box.height <= 720,
              'EHT clipping ' + selector + ' frame ' + frame,
            );
            assert.ok(
              await page.locator(selector).evaluate((e) => {
                if (!e.hasAttribute('data-eht-scene'))
                  return e.scrollHeight <= e.clientHeight && e.scrollWidth <= e.clientWidth;
                // Overflowing trailing padding does not clip content. Check rendered
                // text fragments and image bounds against the actual clipping box.
                const box = e.getBoundingClientRect();
                const inside = (r) =>
                  r.width === 0 ||
                  r.height === 0 ||
                  (r.left >= box.left &&
                    r.top >= box.top &&
                    r.right <= box.right &&
                    r.bottom <= box.bottom);
                const walker = document.createTreeWalker(e, NodeFilter.SHOW_TEXT);
                while (walker.nextNode()) {
                  if (!walker.currentNode.textContent.trim()) continue;
                  const range = document.createRange();
                  range.selectNodeContents(walker.currentNode);
                  if (!Array.from(range.getClientRects()).every(inside)) return false;
                }
                return Array.from(e.querySelectorAll('svg,img')).every((n) =>
                  inside(n.getBoundingClientRect()),
                );
              }),
              'EHT overflow ' + selector + ' frame ' + frame,
            );
          }
        }
        if (plan.recipe === 'imaging101-dti-v1') {
          const name = await page.locator('[data-dti-scene]').getAttribute('data-dti-scene');
          const beat = plan.beats.find((b) => b.scene === name);
          const revealed =
            name === 'reference' &&
            frame > beat.startFrame + (beat.endFrame - beat.startFrame - 1) / 2;
          assert.equal(await page.locator('[data-dti-reference]').count(), revealed ? 1 : 0);
          if (name === 'inputs' || name === 'output')
            assert.equal(await page.locator('[data-dti-panel]').count(), 2);
          for (const selector of [
            '.scene-player > header',
            '[data-dti-scene]',
            '[data-dti-output]',
            '.scene-legend',
          ]) {
            const box = await page.locator(selector).boundingBox();
            assert.ok(
              box && box.y + box.height <= 720,
              'DTI clipping ' + selector + ' frame ' + frame,
            );
            assert.ok(
              await page.locator(selector).evaluate((e) => {
                if (!e.hasAttribute('data-dti-scene'))
                  return e.scrollHeight <= e.clientHeight && e.scrollWidth <= e.clientWidth;
                // Overflowing trailing padding does not clip content. Check rendered
                // text fragments and image bounds against the actual clipping box.
                const box = e.getBoundingClientRect();
                const inside = (r) =>
                  r.width === 0 ||
                  r.height === 0 ||
                  (r.left >= box.left &&
                    r.top >= box.top &&
                    r.right <= box.right &&
                    r.bottom <= box.bottom);
                const walker = document.createTreeWalker(e, NodeFilter.SHOW_TEXT);
                while (walker.nextNode()) {
                  if (!walker.currentNode.textContent.trim()) continue;
                  const range = document.createRange();
                  range.selectNodeContents(walker.currentNode);
                  if (!Array.from(range.getClientRects()).every(inside)) return false;
                }
                return Array.from(e.querySelectorAll('svg,img')).every((n) =>
                  inside(n.getBoundingClientRect()),
                );
              }),
              'DTI overflow ' + selector + ' frame ' + frame,
            );
          }
        }
        if (plan.recipe === 'imaging101-deflectometry-v1') {
          const name = await page
            .locator('[data-deflectometry-scene]')
            .getAttribute('data-deflectometry-scene');
          const beat = plan.beats.find((b) => b.scene === name);
          const revealed =
            name === 'reference' &&
            frame > beat.startFrame + (beat.endFrame - beat.startFrame - 1) / 2;
          assert.equal(
            await page.locator('[data-deflectometry-reference]').count(),
            revealed ? 2 : 0,
          );
          if (name === 'inputs' || name === 'output')
            assert.equal(await page.locator('[data-deflectometry-panel]').count(), 2);
          for (const selector of [
            '.scene-player > header',
            '[data-deflectometry-scene]',
            '[data-deflectometry-aside]',
            '.scene-legend',
          ]) {
            const box = await page.locator(selector).boundingBox();
            assert.ok(
              box && box.y + box.height <= 720,
              'Deflectometry clipping ' + selector + ' frame ' + frame,
            );
            assert.ok(
              await page.locator(selector).evaluate((e) => {
                if (!e.hasAttribute('data-deflectometry-scene'))
                  return e.scrollHeight <= e.clientHeight && e.scrollWidth <= e.clientWidth;
                // Overflowing trailing padding does not clip content. Check rendered
                // text fragments and image bounds against the actual clipping box.
                const box = e.getBoundingClientRect();
                const inside = (r) =>
                  r.width === 0 ||
                  r.height === 0 ||
                  (r.left >= box.left &&
                    r.top >= box.top &&
                    r.right <= box.right &&
                    r.bottom <= box.bottom);
                const walker = document.createTreeWalker(e, NodeFilter.SHOW_TEXT);
                while (walker.nextNode()) {
                  if (!walker.currentNode.textContent.trim()) continue;
                  const range = document.createRange();
                  range.selectNodeContents(walker.currentNode);
                  if (!Array.from(range.getClientRects()).every(inside)) return false;
                }
                return Array.from(e.querySelectorAll('svg,img')).every((n) =>
                  inside(n.getBoundingClientRect()),
                );
              }),
              'Deflectometry overflow ' + selector + ' frame ' + frame,
            );
          }
        }
        if (plan.recipe === 'imaging101-fan-beam-v1') {
          const name = await page
            .locator('[data-fan-beam-scene]')
            .getAttribute('data-fan-beam-scene');
          const beat = plan.beats.find((b) => b.scene === name);
          const revealed =
            name === 'reference' &&
            frame > beat.startFrame + (beat.endFrame - beat.startFrame - 1) / 2;
          assert.equal(await page.locator('[data-fan-beam-reference]').count(), revealed ? 1 : 0);
          if (name === 'inputs' || name === 'output')
            assert.equal(
              await page.locator('[data-fan-beam-plane]').count(),
              name === 'inputs' ? 2 : 1,
            );
          for (const selector of [
            '.scene-player > header',
            '[data-fan-beam-scene]',
            '[data-fan-beam-aside]',
            '.scene-legend',
          ]) {
            const box = await page.locator(selector).boundingBox();
            assert.ok(
              box && box.y + box.height <= 720,
              'Fan-beam clipping ' + selector + ' frame ' + frame,
            );
            assert.ok(
              await page.locator(selector).evaluate((e) => {
                if (!e.hasAttribute('data-fan-beam-scene'))
                  return e.scrollHeight <= e.clientHeight && e.scrollWidth <= e.clientWidth;
                // Overflowing trailing padding does not clip content. Check rendered
                // text fragments and image bounds against the actual clipping box.
                const box = e.getBoundingClientRect();
                const inside = (r) =>
                  r.width === 0 ||
                  r.height === 0 ||
                  (r.left >= box.left &&
                    r.top >= box.top &&
                    r.right <= box.right &&
                    r.bottom <= box.bottom);
                const walker = document.createTreeWalker(e, NodeFilter.SHOW_TEXT);
                while (walker.nextNode()) {
                  if (!walker.currentNode.textContent.trim()) continue;
                  const range = document.createRange();
                  range.selectNodeContents(walker.currentNode);
                  if (!Array.from(range.getClientRects()).every(inside)) return false;
                }
                return Array.from(e.querySelectorAll('svg,img')).every((n) =>
                  inside(n.getBoundingClientRect()),
                );
              }),
              'Fan-beam overflow ' + selector + ' frame ' + frame,
            );
          }
        }
        if (plan.recipe === 'imaging101-dual-energy-v1') {
          const name = await page
            .locator('[data-dual-energy-scene]')
            .getAttribute('data-dual-energy-scene');
          const beat = plan.beats.find((b) => b.scene === name);
          const revealed =
            name === 'reference' &&
            frame > beat.startFrame + (beat.endFrame - beat.startFrame - 1) / 2;
          assert.equal(
            await page.locator('[data-dual-energy-reference]').count(),
            revealed ? 1 : 0,
          );
          if (name === 'inputs' || name === 'output')
            assert.equal(await page.locator('[data-dual-energy-plane]').count(), 2);
          for (const selector of [
            '.scene-player > header',
            '[data-dual-energy-scene]',
            '[data-dual-energy-aside]',
            '.scene-legend',
          ]) {
            const box = await page.locator(selector).boundingBox();
            assert.ok(
              box && box.y + box.height <= 720,
              'Dual-energy clipping ' + selector + ' frame ' + frame,
            );
            assert.ok(
              await page.locator(selector).evaluate((e) => {
                if (!e.hasAttribute('data-dual-energy-scene'))
                  return e.scrollHeight <= e.clientHeight && e.scrollWidth <= e.clientWidth;
                // Overflowing trailing padding does not clip content. Check rendered
                // text fragments and image bounds against the actual clipping box.
                const box = e.getBoundingClientRect();
                const inside = (r) =>
                  r.width === 0 ||
                  r.height === 0 ||
                  (r.left >= box.left &&
                    r.top >= box.top &&
                    r.right <= box.right &&
                    r.bottom <= box.bottom);
                const walker = document.createTreeWalker(e, NodeFilter.SHOW_TEXT);
                while (walker.nextNode()) {
                  if (!walker.currentNode.textContent.trim()) continue;
                  const range = document.createRange();
                  range.selectNodeContents(walker.currentNode);
                  if (!Array.from(range.getClientRects()).every(inside)) return false;
                }
                return Array.from(e.querySelectorAll('svg,img')).every((n) =>
                  inside(n.getBoundingClientRect()),
                );
              }),
              'Dual-energy overflow ' + selector + ' frame ' + frame,
            );
          }
        }
        if (plan.recipe === 'imaging101-ptychography-v1') {
          const name = await page
            .locator('[data-ptychography-scene]')
            .getAttribute('data-ptychography-scene');
          const beat = plan.beats.find((b) => b.scene === name);
          const revealed =
            name === 'reference' &&
            frame > beat.startFrame + (beat.endFrame - beat.startFrame - 1) / 2;
          assert.equal(
            await page.locator('[data-ptychography-reference]').count(),
            revealed ? 1 : 0,
          );
          if (name === 'projection')
            assert.equal(await page.locator('[data-ptychography-plane]').count(), 3);
          for (const selector of [
            '.scene-player > header',
            '[data-ptychography-scene]',
            '[data-ptychography-aside]',
            '.scene-legend',
          ]) {
            const box = await page.locator(selector).boundingBox();
            assert.ok(
              box && box.y + box.height <= 720,
              'Ptychography clipping ' + selector + ' frame ' + frame,
            );
            assert.ok(
              await page.locator(selector).evaluate((e) => {
                if (!e.hasAttribute('data-ptychography-scene'))
                  return e.scrollHeight <= e.clientHeight && e.scrollWidth <= e.clientWidth;
                // Overflowing trailing padding does not clip content. Check rendered
                // text fragments and image bounds against the actual clipping box.
                const box = e.getBoundingClientRect();
                const inside = (r) =>
                  r.width === 0 ||
                  r.height === 0 ||
                  (r.left >= box.left &&
                    r.top >= box.top &&
                    r.right <= box.right &&
                    r.bottom <= box.bottom);
                const walker = document.createTreeWalker(e, NodeFilter.SHOW_TEXT);
                while (walker.nextNode()) {
                  if (!walker.currentNode.textContent.trim()) continue;
                  const range = document.createRange();
                  range.selectNodeContents(walker.currentNode);
                  if (!Array.from(range.getClientRects()).every(inside)) return false;
                }
                return Array.from(e.querySelectorAll('svg,img')).every((n) =>
                  inside(n.getBoundingClientRect()),
                );
              }),
              'Ptychography overflow ' + selector + ' frame ' + frame,
            );
          }
        }
        if (plan.recipe === 'imaging101-nlos-v1') {
          const name = await page.locator('[data-nlos-scene]').getAttribute('data-nlos-scene');
          const beat = plan.beats.find((b) => b.scene === name);
          const revealed =
            name === 'reference' &&
            frame > beat.startFrame + (beat.endFrame - beat.startFrame - 1) / 2;
          assert.equal(await page.locator('[data-nlos-reference]').count(), revealed ? 1 : 0);
          if (name === 'stolt')
            assert.equal(await page.locator('[data-nlos-stolt-probe]').count(), 1);
          for (const selector of [
            '.scene-player > header',
            '[data-nlos-scene]',
            '[data-nlos-aside]',
            '.scene-legend',
          ]) {
            const box = await page.locator(selector).boundingBox();
            assert.ok(
              box && box.y + box.height <= 720,
              'NLOS clipping ' + selector + ' frame ' + frame,
            );
            assert.ok(
              await page.locator(selector).evaluate((e) => {
                if (!e.hasAttribute('data-nlos-scene'))
                  return e.scrollHeight <= e.clientHeight && e.scrollWidth <= e.clientWidth;
                // Overflowing trailing padding does not clip content. Check rendered
                // text fragments and image bounds against the actual clipping box.
                const box = e.getBoundingClientRect();
                const inside = (r) =>
                  r.width === 0 ||
                  r.height === 0 ||
                  (r.left >= box.left &&
                    r.top >= box.top &&
                    r.right <= box.right &&
                    r.bottom <= box.bottom);
                const walker = document.createTreeWalker(e, NodeFilter.SHOW_TEXT);
                while (walker.nextNode()) {
                  if (!walker.currentNode.textContent.trim()) continue;
                  const range = document.createRange();
                  range.selectNodeContents(walker.currentNode);
                  if (!Array.from(range.getClientRects()).every(inside)) return false;
                }
                return Array.from(e.querySelectorAll('svg,img')).every((n) =>
                  inside(n.getBoundingClientRect()),
                );
              }),
              'NLOS overflow ' + selector + ' frame ' + frame,
            );
          }
        }
        if (plan.recipe === 'imaging101-cars-v1') {
          const name = await page.locator('[data-cars-scene]').getAttribute('data-cars-scene');
          const beat = plan.beats.find((b) => b.scene === name);
          const revealed =
            name === 'reference' &&
            frame > beat.startFrame + (beat.endFrame - beat.startFrame - 1) / 2;
          assert.equal(await page.locator('[data-cars-reference]').count(), revealed ? 1 : 0);
          if (name === 'fit') assert.equal(await page.locator('[data-cars-residual]').count(), 1);
          for (const selector of [
            '.scene-player > header',
            '[data-cars-scene]',
            '[data-cars-aside]',
            '.scene-legend',
          ]) {
            const box = await page.locator(selector).boundingBox();
            assert.ok(
              box && box.y + box.height <= 720,
              'CARS clipping ' + selector + ' frame ' + frame,
            );
            assert.ok(
              await page.locator(selector).evaluate((e) => {
                if (!e.hasAttribute('data-cars-scene'))
                  return e.scrollHeight <= e.clientHeight && e.scrollWidth <= e.clientWidth;
                // Overflowing trailing padding does not clip content. Check rendered
                // text fragments and image bounds against the actual clipping box.
                const box = e.getBoundingClientRect();
                const inside = (r) =>
                  r.width === 0 ||
                  r.height === 0 ||
                  (r.left >= box.left &&
                    r.top >= box.top &&
                    r.right <= box.right &&
                    r.bottom <= box.bottom);
                const walker = document.createTreeWalker(e, NodeFilter.SHOW_TEXT);
                while (walker.nextNode()) {
                  if (!walker.currentNode.textContent.trim()) continue;
                  const range = document.createRange();
                  range.selectNodeContents(walker.currentNode);
                  if (!Array.from(range.getClientRects()).every(inside)) return false;
                }
                return Array.from(e.querySelectorAll('svg,img')).every((n) =>
                  inside(n.getBoundingClientRect()),
                );
              }),
              'CARS overflow ' + selector + ' frame ' + frame,
            );
          }
        }
        if (plan.recipe === 'rex-topcow-v1') {
          const name = await page.locator('[data-rex-scene]').getAttribute('data-rex-scene');
          const b = plan.beats.find((b) => b.scene === name);
          const revealed =
            name === 'reference' && frame > b.startFrame + (b.endFrame - b.startFrame) / 2;
          assert.equal(await page.locator('[data-rex-reference]').count(), revealed ? 2 : 0);
          assert.equal(await page.locator('[data-rex-crop]').count(), revealed ? 1 : 0);
          if (name === 'metrics')
            assert.equal(
              await page.locator('[data-rex-fixtures] tr[data-current="true"]').count(),
              1,
            );
          for (const selector of [
            '.scene-player > header',
            '[data-rex-scene]',
            '[data-rex-aside]',
            '.scene-legend',
          ]) {
            const box = await page.locator(selector).boundingBox();
            assert.ok(
              box && box.y + box.height <= 720,
              'Rex clipping ' + selector + ' frame ' + frame,
            );
            assert.ok(
              await page.locator(selector).evaluate((e) => {
                if (!e.hasAttribute('data-rex-scene'))
                  return e.scrollHeight <= e.clientHeight && e.scrollWidth <= e.clientWidth;
                // Overflowing trailing padding does not clip content. Check rendered
                // text fragments and image bounds against the actual clipping box.
                const box = e.getBoundingClientRect();
                const inside = (r) =>
                  r.width === 0 ||
                  r.height === 0 ||
                  (r.left >= box.left &&
                    r.top >= box.top &&
                    r.right <= box.right &&
                    r.bottom <= box.bottom);
                const walker = document.createTreeWalker(e, NodeFilter.SHOW_TEXT);
                while (walker.nextNode()) {
                  if (!walker.currentNode.textContent.trim()) continue;
                  const range = document.createRange();
                  range.selectNodeContents(walker.currentNode);
                  if (!Array.from(range.getClientRects()).every(inside)) return false;
                }
                return Array.from(e.querySelectorAll('svg,img')).every((n) =>
                  inside(n.getBoundingClientRect()),
                );
              }),
              'Rex overflow ' + selector + ' frame ' + frame,
            );
          }
        }
        if (plan.recipe === 'automed-multiorgan-v1') {
          const name = await page
            .locator('[data-automed-scene]')
            .getAttribute('data-automed-scene');
          const b = plan.beats.find((b) => b.scene === name);
          const revealed =
            name === 'reference' && frame > b.startFrame + (b.endFrame - b.startFrame) / 2;
          assert.equal(await page.locator('[data-automed-reference]').count(), revealed ? 5 : 0);
          if (name === 'remap')
            assert.equal(
              await page.locator('[data-automed-remap] tr[data-current="true"]').count(),
              1,
            );
          if (name === 'coverage')
            assert.equal(
              await page.locator('[data-automed-fixtures] tr[data-current="true"]').count(),
              1,
            );
          for (const selector of [
            '.scene-player > header',
            '[data-automed-scene]',
            '[data-automed-aside]',
            '.scene-legend',
          ]) {
            const box = await page.locator(selector).boundingBox();
            assert.ok(
              box && box.y + box.height <= 720,
              'Automed clipping ' + selector + ' frame ' + frame,
            );
            assert.ok(
              await page.locator(selector).evaluate((e) => {
                if (!e.hasAttribute('data-automed-scene'))
                  return e.scrollHeight <= e.clientHeight && e.scrollWidth <= e.clientWidth;
                // Overflowing trailing padding does not clip content. Check rendered
                // text fragments and image bounds against the actual clipping box.
                const box = e.getBoundingClientRect();
                const inside = (r) =>
                  r.width === 0 ||
                  r.height === 0 ||
                  (r.left >= box.left &&
                    r.top >= box.top &&
                    r.right <= box.right &&
                    r.bottom <= box.bottom);
                const walker = document.createTreeWalker(e, NodeFilter.SHOW_TEXT);
                while (walker.nextNode()) {
                  if (!walker.currentNode.textContent.trim()) continue;
                  const range = document.createRange();
                  range.selectNodeContents(walker.currentNode);
                  if (!Array.from(range.getClientRects()).every(inside)) return false;
                }
                return Array.from(e.querySelectorAll('svg,img')).every((n) =>
                  inside(n.getBoundingClientRect()),
                );
              }),
              'Automed overflow ' + selector + ' frame ' + frame,
            );
          }
        }
        if (plan.recipe === 'bcer-workflow-v1') {
          const name = await page.locator('[data-bcer-scene]').getAttribute('data-bcer-scene');
          if (name === 'geometry')
            assert.equal(await page.locator('[data-bcer-witness]').count(), 3);
          if (name === 'dependencies')
            assert.equal(await page.locator('[data-bcer-node][data-current="true"]').count(), 1);
          if (name === 'artifacts')
            assert.equal(
              await page.locator('[data-bcer-artifact][data-current="true"]').count(),
              1,
            );
          if (name === 'metrics')
            assert.equal(
              await page.locator('[data-bcer-metrics] tr[data-current="true"]').count(),
              1,
            );
          for (const selector of [
            '.scene-player > header',
            '[data-bcer-scene]',
            '[data-bcer-aside]',
            '.scene-legend',
          ]) {
            assert.ok(
              await page.locator(selector).evaluate((e) => {
                if (!e.hasAttribute('data-bcer-scene'))
                  return e.scrollHeight <= e.clientHeight && e.scrollWidth <= e.clientWidth;
                // Overflowing trailing padding does not clip content. Check rendered
                // text fragments and image bounds against the actual clipping box.
                const box = e.getBoundingClientRect();
                const inside = (r) =>
                  r.width === 0 ||
                  r.height === 0 ||
                  (r.left >= box.left &&
                    r.top >= box.top &&
                    r.right <= box.right &&
                    r.bottom <= box.bottom);
                const walker = document.createTreeWalker(e, NodeFilter.SHOW_TEXT);
                while (walker.nextNode()) {
                  if (!walker.currentNode.textContent.trim()) continue;
                  const range = document.createRange();
                  range.selectNodeContents(walker.currentNode);
                  if (!Array.from(range.getClientRects()).every(inside)) return false;
                }
                return Array.from(e.querySelectorAll('svg,img')).every((n) =>
                  inside(n.getBoundingClientRect()),
                );
              }),
              'BCER overflow ' + selector + ' frame ' + frame,
            );
            const b = await page.locator(selector).boundingBox();
            assert.ok(b && b.y + b.height <= 720, 'BCER clipping ' + selector + ' frame ' + frame);
          }
        }
        if (plan.recipe === 'abra-annotation-v1') {
          const scene = page.locator('[data-abra-scene]');
          const name = await scene.getAttribute('data-abra-scene');
          const visible = (await scene.getAttribute('data-abra-reference-visible')) === 'true';
          if (['inputs', 'navigate', 'coordinates'].includes(name))
            assert.equal(
              await page
                .locator(
                  '[data-abra-reference],[data-abra-oracle],[data-abra-output],[data-abra-native^="crop"]',
                )
                .count(),
              0,
            );
          if (name === 'reference') {
            assert.equal(await page.locator('[data-abra-reference]').count(), visible ? 2 : 0);
            assert.equal(await page.locator('[data-abra-reference-info]').count(), visible ? 1 : 0);
            assert.equal(
              await page.locator('[data-scene-inline-narration]').count(),
              visible ? 1 : 0,
            );
          }
          if (name === 'oracle' && (await page.locator('[data-abra-output]').count()))
            assert.equal(await page.locator('[data-abra-oracle]').count(), 1);
          if (name === 'scoring')
            assert.equal(
              await page.locator('[data-abra-score] tr[data-current="true"]').count(),
              1,
            );
          for (const selector of [
            '.scene-player > header',
            '[data-abra-scene]',
            '[class*="abraAside"]',
            '.scene-legend',
          ]) {
            assert.ok(
              await page
                .locator(selector)
                .evaluate(
                  (e) => e.scrollHeight <= e.clientHeight && e.scrollWidth <= e.clientWidth,
                ),
              'ABRA overflow ' + selector + ' frame ' + frame,
            );
            const b = await page.locator(selector).boundingBox();
            assert.ok(b && b.y + b.height <= 720, 'ABRA clipping ' + selector + ' frame ' + frame);
          }
        }
        if (plan.recipe === 'ct-context-v1') {
          const scene = page.locator('[data-context-scene]');
          const name = await scene.getAttribute('data-context-scene');
          const visible = (await scene.getAttribute('data-context-reference')) === 'visible';
          if (!visible) assert.equal(await page.locator('[data-context-private]').count(), 0);
          if (name === 'inputs')
            assert.equal(
              await page
                .locator('[data-context-point],[data-context-region],[data-context-output]')
                .count(),
              0,
            );
          if (name === 'liver') assert.equal(await page.locator('[data-context-point]').count(), 2);
          if (name === 'surgery')
            assert.equal(await page.locator('[data-context-region]').count(), 2);
          if (name === 'fields')
            assert.equal(
              await page.locator('[data-context-field][data-selected="true"]').count(),
              1,
            );
          if (name === 'reference')
            assert.equal(
              await page.locator('[data-scene-inline-narration]').count(),
              visible ? 1 : 0,
            );
          for (const selector of [
            '.scene-player > header',
            '[data-context-scene]',
            '[class*="contextAside"]',
            '.scene-legend',
          ]) {
            assert.ok(
              await page
                .locator(selector)
                .evaluate(
                  (e) => e.scrollHeight <= e.clientHeight && e.scrollWidth <= e.clientWidth,
                ),
              'Context overflow ' + selector + ' frame ' + frame,
            );
            const b = await page.locator(selector).boundingBox();
            assert.ok(
              b && b.y + b.height <= 720,
              'Context clipped ' + selector + ' frame ' + frame,
            );
          }
        }
        if (plan.recipe === 'history-sourcing-v1') {
          const scene = page.locator('[data-history-scene]');
          const reveal = (await scene.getAttribute('data-history-reference')) === 'visible';
          if (!reveal) assert.equal(await page.locator('[data-history-private]').count(), 0);
          if ((await scene.getAttribute('data-history-scene')) === 'reference')
            assert.equal(
              await page.locator('[data-scene-inline-narration]').count(),
              reveal ? 1 : 0,
            );
          if ((await scene.getAttribute('data-history-scene')) === 'excerpts') {
            assert.equal(await page.locator('[data-history-excerpt]').count(), 1);
            assert.ok(
              (await page.locator('[data-history-excerpt] code').last().textContent()).match(
                /[a-f0-9]{64}/,
              ),
            );
          }
          if ((await scene.getAttribute('data-history-scene')) === 'gap')
            assert.match(
              await page.locator('[data-history-untested]').textContent(),
              /No executable task. No attempt. No score./,
            );
          for (const selector of [
            '.scene-player > header',
            '[data-history-scene]',
            '[class*="historyAside"]',
            '.scene-legend',
          ]) {
            assert.ok(
              await page
                .locator(selector)
                .evaluate(
                  (e) => e.scrollHeight <= e.clientHeight && e.scrollWidth <= e.clientWidth,
                ),
              'History overflow ' + selector,
            );
            const box = await page.locator(selector).boundingBox();
            assert.ok(box && box.y + box.height <= 720, 'History clipping ' + selector);
          }
        }
        if (plan.recipe === 'mri-importer-v1') {
          const scene = page.locator('[data-mri-scene]');
          const reveal = (await scene.getAttribute('data-mri-reference')) === 'visible';
          if (!reveal) assert.equal(await page.locator('[data-mri-private]').count(), 0);
          if (frame === 0) assert.equal(await page.locator('[data-mri-output]').count(), 0);
          if ((await scene.getAttribute('data-mri-scene')) === 'reference')
            assert.equal(
              await page.locator('[data-scene-inline-narration]').count(),
              reveal ? 1 : 0,
            );
          if ((await scene.getAttribute('data-mri-scene')) === 'association') {
            const selected = page.locator('[data-mri-grid] article[data-selected="true"]');
            assert.equal(await selected.count(), 2);
            assert.equal(
              await selected.nth(0).getAttribute('data-storage'),
              await selected.nth(1).getAttribute('data-storage'),
            );
            assert.equal(
              await selected.nth(0).getAttribute('data-target'),
              await selected.nth(1).getAttribute('data-target'),
            );
          }
          for (const selector of [
            '.scene-player > header',
            '[data-mri-scene]',
            '[class*="mriAside"]',
            '.scene-legend',
          ]) {
            assert.ok(
              await page
                .locator(selector)
                .evaluate(
                  (e) => e.scrollHeight <= e.clientHeight && e.scrollWidth <= e.clientWidth,
                ),
              'MR overflow ' + selector,
            );
            const box = await page.locator(selector).boundingBox();
            assert.ok(box && box.y + box.height <= 720, 'MR clipping ' + selector);
          }
        }
        if (plan.recipe === 'localized-ct-v1') {
          const scene = page.locator('[data-localized-scene]');
          const reveal = (await scene.getAttribute('data-localized-reference')) === 'visible';
          if (!reveal) assert.equal(await page.locator('[data-localized-private]').count(), 0);
          if (frame === 0) {
            assert.equal(await page.locator('[data-localized-output]').count(), 0);
            assert.equal(await page.locator('[data-localized-point]').count(), 2);
          }
          if ((await scene.getAttribute('data-localized-scene')) === 'reference')
            assert.equal(
              await page.locator('[data-scene-inline-narration]').count(),
              reveal ? 1 : 0,
            );
          for (const selector of [
            '.scene-player > header',
            '[data-localized-scene]',
            '[class*="localizedAside"]',
            '.scene-legend',
          ]) {
            assert.ok(
              await page
                .locator(selector)
                .evaluate(
                  (e) => e.scrollHeight <= e.clientHeight && e.scrollWidth <= e.clientWidth,
                ),
              'Localized CT overflow ' + selector,
            );
            const box = await page.locator(selector).boundingBox();
            assert.ok(box && box.y + box.height <= 720, 'Localized CT clipping ' + selector);
          }
        }
        if (plan.recipe === 'aneurysm-localization-v1') {
          const scene = page.locator('[data-aneurysm-scene]');
          const reveal = (await scene.getAttribute('data-aneurysm-reference')) === 'visible';
          if (!reveal) assert.equal(await page.locator('[data-aneurysm-private]').count(), 0);
          if (frame === 0) assert.equal(await page.locator('[data-aneurysm-point]').count(), 0);
          if ((await scene.getAttribute('data-aneurysm-scene')) === 'reference')
            assert.equal(
              await page.locator('[data-scene-inline-narration]').count(),
              reveal ? 1 : 0,
            );
          for (const selector of [
            '.scene-player > header',
            '[data-aneurysm-scene]',
            '[data-aneurysm-output]',
          ]) {
            assert.ok(
              await page
                .locator(selector)
                .evaluate(
                  (e) => e.scrollHeight <= e.clientHeight && e.scrollWidth <= e.clientWidth,
                ),
              'Aneurysm overflow: ' + selector,
            );
            const box = await page.locator(selector).boundingBox();
            assert.ok(box && box.y + box.height <= 720, 'Aneurysm panel clipped: ' + selector);
          }
          for (const point of await page.locator('[data-aneurysm-point]').all())
            assert.equal(await point.getAttribute('data-depth-offset'), '0');
          const legend = await page.locator('.scene-legend').boundingBox();
          assert.ok(legend && legend.y + legend.height <= 720, 'Aneurysm legend clipped');
        }
        if (plan.recipe === 'segmentation-calibration-v1') {
          const scene = page.locator('[data-calibration-scene]');
          const reveal = (await scene.getAttribute('data-calibration-reference')) === 'visible';
          if (!reveal)
            assert.equal(
              await page
                .locator('[data-calibration-private], [data-calibration-layer="reference"]')
                .count(),
              0,
            );
          if (frame === 0) assert.equal(await page.locator('[data-calibration-layer]').count(), 0);
          if ((await scene.getAttribute('data-calibration-scene')) === 'reference')
            assert.equal(
              await page.locator('[data-scene-inline-narration]').count(),
              reveal ? 1 : 0,
            );
          for (const selector of [
            '.scene-player > header',
            '[data-calibration-scene]',
            '[data-calibration-output]',
          ]) {
            assert.ok(
              await page
                .locator(selector)
                .evaluate(
                  (e) => e.scrollHeight <= e.clientHeight && e.scrollWidth <= e.clientWidth,
                ),
              'Calibration overflow: ' + selector,
            );
            const box = await page.locator(selector).boundingBox();
            assert.ok(box && box.y + box.height <= 720, 'Calibration panel clipped: ' + selector);
          }
          const legend = await page.locator('.scene-legend').boundingBox();
          assert.ok(legend && legend.y + legend.height <= 720, 'Calibration legend clipped');
        }
        if (plan.recipe === 'dental-v3-v1') {
          const scene = page.locator('[data-dental-v3-scene]');
          const reveal = (await scene.getAttribute('data-dental-v3-reference')) === 'visible';
          if (!reveal)
            assert.equal(
              await page
                .locator('[data-dental-v3-private], [data-dental-v3-layer="reference"]')
                .count(),
              0,
            );
          if (frame === 0) assert.equal(await page.locator('[data-dental-v3-layer]').count(), 0);
          if ((await scene.getAttribute('data-dental-v3-scene')) === 'shape')
            assert.equal(
              await page.locator('[data-scene-inline-narration]').count(),
              reveal ? 1 : 0,
            );
          for (const selector of [
            '.scene-player > header',
            '[data-dental-v3-scene]',
            '[data-dental-v3-output]',
          ]) {
            assert.ok(
              await page
                .locator(selector)
                .evaluate(
                  (e) => e.scrollHeight <= e.clientHeight && e.scrollWidth <= e.clientWidth,
                ),
              'Dental v3 overflow: ' + selector,
            );
          }
          const legend = await page.locator('.scene-legend').boundingBox();
          assert.ok(legend && legend.y + legend.height <= 720, 'Dental v3 legend clipped');
          if ((await scene.getAttribute('data-dental-v3-scene')) === 'example')
            assert.equal(await page.locator('[data-dental-v3-layer="reference"]').count(), 0);
        }
        if (plan.recipe === 'dental-v2-v1') {
          const scene = page.locator('[data-dental-v2-scene]');
          const reveal = (await scene.getAttribute('data-dental-v2-reference')) === 'visible';
          if (!reveal)
            assert.equal(
              await page
                .locator('[data-dental-v2-private], [data-dental-v2-layer="reference"]')
                .count(),
              0,
            );
          if (frame === 0) assert.equal(await page.locator('[data-dental-v2-layer]').count(), 0);
          if ((await scene.getAttribute('data-dental-v2-scene')) === 'identity')
            assert.equal(
              await page.locator('[data-scene-inline-narration]').count(),
              reveal ? 1 : 0,
            );
          for (const selector of [
            '.scene-player > header',
            '[data-dental-v2-scene]',
            '[data-dental-v2-output]',
          ]) {
            assert.ok(
              await page
                .locator(selector)
                .evaluate(
                  (e) => e.scrollHeight <= e.clientHeight && e.scrollWidth <= e.clientWidth,
                ),
              'Dental v2 overflow: ' + selector,
            );
          }
          const legend = await page.locator('.scene-legend').boundingBox();
          assert.ok(legend && legend.y + legend.height <= 720, 'Dental v2 legend clipped');
          if ((await scene.getAttribute('data-dental-v2-scene')) === 'example')
            assert.equal(await page.locator('[data-dental-v2-layer="reference"]').count(), 0);
        }
        if (plan.recipe === 'dental-original-v1') {
          assert.ok(
            await page
              .locator('.scene-player > header')
              .evaluate((e) => e.scrollHeight <= e.clientHeight),
            'Dental story heading clipped',
          );
          const scene = page.locator('[data-dental-scene]');
          const reveal = (await scene.getAttribute('data-dental-reference')) === 'visible';
          if (!reveal)
            assert.equal(
              await page.locator('[data-dental-private], [data-dental-layer="reference"]').count(),
              0,
            );
          if (frame === 0) assert.equal(await page.locator('[data-dental-layer]').count(), 0);
          for (const selector of ['[data-dental-scene]', '[data-dental-output]'])
            assert.ok(
              await page.locator(selector).evaluate((e) => e.scrollHeight <= e.clientHeight),
              'Dental content overflows',
            );
          const legend = await page.locator('.scene-legend').boundingBox();
          assert.ok(legend && legend.y + legend.height <= 720, 'Dental legend clipped');
          if ((await scene.getAttribute('data-dental-scene')) === 'diagnostic') {
            const paths = async (key) =>
              page
                .locator(`[data-dental-panel="${key}"] path`)
                .evaluateAll((xs) => xs.map((x) => x.getAttribute('d')));
            assert.deepEqual(
              await paths('xhigh'),
              await paths('diagnostic'),
              'ID diagnostic moved geometry',
            );
          }
        }
        if (plan.recipe === 'ct-organ-v1') {
          const scene = page.locator('[data-ct-scene]');
          const reveal = (await scene.getAttribute('data-ct-reference')) === 'visible';
          if (!reveal)
            assert.equal(
              await page.locator('[data-ct-layer="reference"], [data-ct-private]').count(),
              0,
            );
          if (frame === 0) assert.equal(await page.locator('[data-ct-layer]').count(), 0);
          assert.ok(
            await page
              .locator('[data-ct-output]')
              .evaluate((e) => e.scrollHeight <= e.clientHeight),
            'CT output overflow',
          );
          assert.ok(
            await scene.evaluate((e) => e.scrollHeight <= e.clientHeight),
            'CT scene overflow',
          );
          const legend = await page.locator('.scene-legend').boundingBox();
          assert.ok(legend && legend.y + legend.height <= 720, 'CT legend clipped');
        }
        if (plan.recipe === 'named-landmarks-v1') {
          const panel = page.locator('[data-landmark-output]');
          assert.ok(
            await panel.evaluate((e) => e.scrollHeight <= e.clientHeight),
            'Landmark output overflows',
          );
          const legend = await page.locator('.scene-legend').boundingBox();
          assert.ok(legend && legend.y + legend.height <= 720, 'Landmark legend clipped');
          assert.ok(
            await page
              .locator('[data-landmark-scene]')
              .evaluate((e) => e.scrollHeight <= e.clientHeight),
            'Landmark scene overflows',
          );
          const revealed = (await panel.getAttribute('data-landmark-reference')) === 'visible';
          if (!revealed)
            assert.equal(
              await page
                .locator('[data-landmark-mark="reference"], [data-landmark-private]')
                .count(),
              0,
            );
          if (frame === 0) assert.equal(await page.locator('[data-landmark-mark]').count(), 0);
        }
        if (plan.recipe === 'clinical-cavity-v1') {
          const panel = page.locator('[data-cavity-output]');
          const legend = await page.locator('.scene-legend').boundingBox();
          assert.ok(legend && legend.y + legend.height <= 720, 'Cavity legend clipped');
          assert.ok(
            await panel.evaluate((e) => e.scrollHeight <= e.clientHeight),
            'Cavity output overflows',
          );
          const box = await panel.boundingBox();
          assert.ok(box && box.y + box.height <= 720, 'Cavity output clipped');
          const beat = plan.beats.find((b) => frame >= b.startFrame && frame < b.endFrame);
          const reveal = (await panel.getAttribute('data-cavity-reference')) === 'revealed';
          assert.equal(
            await panel.locator('[data-cavity-reference-section]').count(),
            reveal ? 3 : 0,
          );
          assert.equal(
            await panel.locator('[data-cavity-reference-curve]').count(),
            reveal ? 1 : 0,
          );
          if (frame === 0)
            assert.equal(await panel.locator('[data-cavity-output-section]').count(), 0);
          const selected = Number(await panel.getAttribute('data-cavity-frame'));
          const image = Number(await panel.getAttribute('data-cavity-image-frame'));
          if (beat.scene === 'static') assert.equal(image, 0);
          else if (beat.scene === 'shift') assert.equal(image, (selected - 5 + 18) % 18);
          else assert.equal(image, selected);
        }
        if (plan.recipe === 'respiratory-v1') {
          const output = page.locator('[data-respiratory-output]');
          assert.ok(
            await output.evaluate((e) => e.scrollHeight <= e.clientHeight),
            'Respiratory output overflows',
          );
          const box = await output.boundingBox();
          assert.ok(box && box.y + box.height <= 720, 'Respiratory output clipped');
        }
        if (plan.recipe === 'anatomy-curation-v1') {
          assert.ok(
            await page
              .locator('[data-curation-output]')
              .evaluate((e) => e.scrollHeight <= e.clientHeight),
            'Curation output overflows',
          );
          const box = await page.locator('[data-curation-output]').boundingBox();
          assert.ok(box && box.y + box.height <= 720, 'Curation output clipped');
          if (frame === 0)
            assert.deepEqual(await page.locator('[data-curation-reference]').allTextContents(), [
              'hidden',
              'hidden',
            ]);
        }
        if (plan.recipe === 'mask-screen-v1') {
          assert.ok(
            await page
              .locator('[data-mask-screen-output]')
              .evaluate((e) => e.scrollHeight <= e.clientHeight),
            'Author-screen output overflows',
          );
          const output = await page.locator('[data-mask-screen-output]').boundingBox();
          assert.ok(output && output.y + output.height <= 720, 'Author-screen output clipped');
        }
        if (plan.recipe === 'mixed-tissue-v1') {
          const reveal = plan.beats.find((b) => b.channels.reference[1] > 0).startFrame;
          const witness = plan.beats.find((b) => b.channels.witness[1] > 0).startFrame;
          assert.equal(
            await page.locator('[data-mixed-reference]').count(),
            frame > reveal ? 1 : 0,
          );
          assert.equal(await page.locator('[data-mixed-answer]').count(), frame > witness ? 1 : 0);
          assert.ok(
            await page
              .locator('[data-mixed-output]')
              .evaluate((e) => e.scrollHeight <= e.clientHeight),
            'Mixed-tissue content overflows',
          );
          const output = await page.locator('[data-mixed-output]').boundingBox();
          assert.ok(output && output.y + output.height <= 720, 'Mixed-tissue output clipped');
        }
        if (plan.recipe === 'anatomy-identity-v1') {
          const labels = await page.locator('[data-identity-label]').allTextContents();
          assert.equal(labels.length, 7);
          assert.equal(
            labels.every((label) => label === 'unassigned'),
            frame !== plan.durationFrames - 1,
          );
          const output = await page.locator('[data-identity-output]').boundingBox();
          assert.ok(output && output.y + output.height <= 720, 'Identity output clipped');
          assert.ok(
            await page
              .locator('[data-identity-output]')
              .evaluate((e) => e.scrollHeight <= e.clientHeight),
            'Identity output content overflows its panel',
          );
        }
        if (plan.recipe === 'prototype-identity-v1') {
          const labels = await page.locator('[data-prototype-label]').allTextContents();
          assert.equal(labels.length, 17);
          assert.equal(
            labels.every((label) => label === 'unassigned'),
            frame !== plan.durationFrames - 1,
          );
          assert.ok(
            await page
              .locator('[data-prototype-output]')
              .evaluate((e) => e.scrollHeight <= e.clientHeight),
            'Prototype output content overflows',
          );
          const output = await page.locator('[data-prototype-output]').boundingBox();
          assert.ok(output && output.y + output.height <= 720, 'Prototype output clipped');
        }
        assert.equal(
          await page.locator('.scene-player').getAttribute('data-committed-frame'),
          String(frame),
        );
        const caption = await page.locator('[data-scene-title]').boundingBox();
        assert.ok(
          caption && caption.y + caption.height <= 720,
          `${id} caption clipped in ${locale}`,
        );
      }
      const end = await captureComposedFrame(page, {
        frame: frames[2],
        fps: plan.fps,
        width: 1280,
        height: 720,
      });
      const endDom = await page.locator('.scene-player').innerHTML();
      await captureComposedFrame(page, { frame: 0, fps: plan.fps, width: 1280, height: 720 });
      const repeated = await captureComposedFrame(page, {
        frame: frames[2],
        fps: plan.fps,
        width: 1280,
        height: 720,
      });
      assert.equal(
        await page.locator('.scene-player').innerHTML(),
        endDom,
        'Repeated frame DOM must match exactly: ' + id,
      );
      if (sha(repeated) !== sha(end)) {
        // Chromium can differ by one quantization level at SVG antialias and translucent-fill edges.
        // Keep an explicit pixel bound; do not tolerate displaced geometry or text.
        const delta = await page.evaluate(
          async ([a, b]) => {
            async function pixels(src) {
              const image = new Image();
              image.src = src;
              await image.decode();
              const canvas = new OffscreenCanvas(image.width, image.height);
              const ctx = canvas.getContext('2d');
              ctx.drawImage(image, 0, 0);
              return ctx.getImageData(0, 0, image.width, image.height).data;
            }
            const x = await pixels(a),
              y = await pixels(b);
            let changedPixels = 0,
              maxChannelError = 0;
            for (let i = 0; i < x.length; i += 4) {
              let changed = false;
              for (let j = 0; j < 4; j++) {
                const d = Math.abs(x[i + j] - y[i + j]);
                if (d) changed = true;
                maxChannelError = Math.max(maxChannelError, d);
              }
              if (changed) changedPixels++;
            }
            return { changedPixels, maxChannelError };
          },
          [end, repeated].map((bytes) => 'data:image/png;base64,' + bytes.toString('base64')),
        );
        assert.ok(
          delta.changedPixels <= (plan.schema === 1 ? 16 : 2048) &&
            delta.maxChannelError <= (plan.schema === 1 ? 8 : 1),
          'Repeated-frame raster drift ' + id + ': ' + JSON.stringify(delta),
        );
        row.rasterQuantization = delta;
      }
      row.locales.push(locale);
    }
    // IDs may change while explicit operation fields retain the rendered meaning.
    if (['multiscale-v1', 'topology-v1', 'correspondence-v1'].includes(plan.recipe)) {
      const renamed = structuredClone(plan);
      renamed.id = 'renamed-explicit-story';
      renamed.beats.forEach((beat, index) => {
        beat.id = `renamed-${index}`;
      });
      const renamedFile = path.join(out, 'renamed.html');
      fs.writeFileSync(
        renamedFile,
        fs
          .readFileSync(path.join(out, 'index.html'), 'utf8')
          .replace(
            /(<script id="story-plan" type="application\/json">)[\s\S]*?(<\/script>)/,
            (_match, start, end) =>
              start + JSON.stringify(renamed).replaceAll('<', '\\u003c') + end,
          ),
      );
      const semanticFrames = plan.beats.map((beat) => beat.endFrame - 1);
      await page.goto(url + '?capture=1&lang=en');
      const originals = [];
      for (const frame of semanticFrames) {
        await captureComposedFrame(page, { frame, fps: plan.fps, width: 1280, height: 720 });
        originals.push(
          await page.locator('.scene-player').evaluate((element) => ({
            caption: element.querySelector('[data-scene-title]')?.textContent,
            legend: element.querySelector('.scene-legend')?.textContent,
            // Ignore data attributes and identity; compare the actual composition and geometry.
            svg: [...element.querySelectorAll('svg')].map((svg) => svg.outerHTML),
            output: element.querySelector('[class*="storyOutput"]')?.innerHTML,
          })),
        );
      }
      await page.goto(pathToFileURL(renamedFile).href + '?capture=1&lang=en');
      for (const [index, frame] of semanticFrames.entries()) {
        await captureComposedFrame(page, { frame, fps: plan.fps, width: 1280, height: 720 });
        const renamedView = await page.locator('.scene-player').evaluate((element) => ({
          caption: element.querySelector('[data-scene-title]')?.textContent,
          legend: element.querySelector('.scene-legend')?.textContent,
          svg: [...element.querySelectorAll('svg')].map((svg) => svg.outerHTML),
          output: element.querySelector('[class*="storyOutput"]')?.innerHTML,
        }));
        assert.deepEqual(renamedView, originals[index], `${id} explicit rename at frame ${frame}`);
      }
      row.renameInvariant = semanticFrames;
    }
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(url + '?lang=zh-CN');
    await page.locator('.scene-player[data-rendered="true"]').waitFor();
    assert.equal(
      await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
      true,
      'mobile overflow ' + id,
    );
    await page.locator('.scene-player').screenshot({ path: path.join(out, 'mobile.png') });
    await reviewCardiacInteractions(page, plan, out, 'mobile');
    if (plan.recipe === 'imaging101-eht-original-v1') {
      for (let step = 1; step < plan.beats.length; step++) {
        await page.locator(`[data-story-step="${step}"]`).click();
        await page.waitForFunction(
          (f) =>
            document.querySelector('.scene-player')?.getAttribute('data-committed-frame') ===
            String(f),
          plan.beats[step].startFrame,
        );
        assert.ok(
          await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
          'Static closure mobile overflow',
        );
        await page
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `mobile-chapter-${step}.png`) });
      }
      await page.locator('[data-story-step="5"]').click();
      assert.equal(await page.locator('[data-original-reference]').count(), 0);
      await page.locator('.scene-play').click();
      await page.locator('[data-original-reference]').first().waitFor({ timeout: 20000 });
      await page.locator('.scene-play').click();
      assert.equal(await page.locator('[data-original-reference]').count(), 1);
      assert.ok(
        await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
        'Static closure mobile reference overflow',
      );
      await page
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'mobile-reference-revealed.png') });
      await page.locator('.scene-reset').click();
      assert.equal(await page.locator('[data-original-reference]').count(), 0);
    }
    if (plan.recipe === 'imaging101-eht-features-dynamic-v1') {
      for (let step = 1; step < plan.beats.length; step++) {
        await page.locator(`[data-story-step="${step}"]`).click();
        await page.waitForFunction(
          (f) =>
            document.querySelector('.scene-player')?.getAttribute('data-committed-frame') ===
            String(f),
          plan.beats[step].startFrame,
        );
        assert.ok(
          await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
          'Dynamic features mobile overflow',
        );
        await page
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `mobile-chapter-${step}.png`) });
      }
      await page.locator('[data-story-step="4"]').click();
      assert.equal(await page.locator('[data-features-reference]').count(), 0);
      await page.locator('.scene-play').click();
      await page.locator('[data-features-reference]').first().waitFor({ timeout: 20000 });
      await page.locator('.scene-play').click();
      assert.equal(await page.locator('[data-features-reference]').count(), 1);
      assert.ok(
        await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
        'Dynamic features mobile reference overflow',
      );
      await page
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'mobile-reference-revealed.png') });
      await page.locator('.scene-reset').click();
      assert.equal(await page.locator('[data-features-reference]').count(), 0);
    }
    if (plan.recipe === 'imaging101-eht-dynamic-v1') {
      for (let step = 1; step < plan.beats.length; step++) {
        await page.locator(`[data-story-step="${step}"]`).click();
        await page.waitForFunction(
          (f) =>
            document.querySelector('.scene-player')?.getAttribute('data-committed-frame') ===
            String(f),
          plan.beats[step].startFrame,
        );
        assert.ok(
          await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
          'Dynamic EHT mobile overflow',
        );
        await page
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `mobile-chapter-${step}.png`) });
      }
      await page.locator('[data-story-step="4"]').click();
      assert.equal(await page.locator('[data-dynamic-reference]').count(), 0);
      await page.locator('.scene-play').click();
      await page.locator('[data-dynamic-reference]').first().waitFor({ timeout: 20000 });
      await page.locator('.scene-play').click();
      assert.equal(await page.locator('[data-dynamic-reference]').count(), 1);
      assert.ok(
        await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
        'Dynamic EHT mobile reference overflow',
      );
      await page
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'mobile-reference-revealed.png') });
      await page.locator('.scene-reset').click();
      assert.equal(await page.locator('[data-dynamic-reference]').count(), 0);
    }
    if (plan.recipe === 'imaging101-eht-uq-v1') {
      for (let step = 1; step < plan.beats.length; step++) {
        await page.locator(`[data-story-step="${step}"]`).click();
        await page.waitForFunction(
          (f) =>
            document.querySelector('.scene-player')?.getAttribute('data-committed-frame') ===
            String(f),
          plan.beats[step].startFrame,
        );
        assert.ok(
          await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
          'EHT mobile overflow',
        );
        await page
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `mobile-chapter-${step}.png`) });
      }
      await page.locator('[data-story-step="5"]').click();
      assert.equal(await page.locator('[data-eht-reference]').count(), 0);
      await page.locator('.scene-play').click();
      await page.locator('[data-eht-reference]').first().waitFor({ timeout: 20000 });
      await page.locator('.scene-play').click();
      assert.equal(await page.locator('[data-eht-reference]').count(), 1);
      assert.ok(
        await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
        'EHT mobile reference overflow',
      );
      await page
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'mobile-reference-revealed.png') });
      await page.locator('.scene-reset').click();
      assert.equal(await page.locator('[data-eht-reference]').count(), 0);
    }
    if (plan.recipe === 'imaging101-dti-v1') {
      for (let step = 1; step < plan.beats.length; step++) {
        await page.locator(`[data-story-step="${step}"]`).click();
        await page.waitForFunction(
          (f) =>
            document.querySelector('.scene-player')?.getAttribute('data-committed-frame') ===
            String(f),
          plan.beats[step].startFrame,
        );
        assert.ok(
          await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
          'DTI mobile overflow',
        );
        await page
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `mobile-chapter-${step}.png`) });
      }
      await page.locator('[data-story-step="5"]').click();
      assert.equal(await page.locator('[data-dti-reference]').count(), 0);
      await page.locator('.scene-play').click();
      await page.locator('[data-dti-reference]').first().waitFor({ timeout: 20000 });
      await page.locator('.scene-play').click();
      assert.equal(await page.locator('[data-dti-reference]').count(), 1);
      assert.ok(
        await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
        'DTI mobile reference overflow',
      );
      await page
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'mobile-reference-revealed.png') });
      await page.locator('.scene-reset').click();
      assert.equal(await page.locator('[data-dti-reference]').count(), 0);
    }
    if (plan.recipe === 'imaging101-deflectometry-v1') {
      for (let step = 1; step < plan.beats.length; step++) {
        await page.locator(`[data-story-step="${step}"]`).click();
        await page.waitForFunction(
          (f) =>
            document.querySelector('.scene-player')?.getAttribute('data-committed-frame') ===
            String(f),
          plan.beats[step].startFrame,
        );
        assert.ok(
          await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
          'Deflectometry mobile overflow',
        );
        await page
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `mobile-chapter-${step}.png`) });
      }
      await page.locator('[data-story-step="5"]').click();
      assert.equal(await page.locator('[data-deflectometry-reference]').count(), 0);
      await page.locator('.scene-play').click();
      await page.locator('[data-deflectometry-reference]').first().waitFor({ timeout: 20000 });
      await page.locator('.scene-play').click();
      assert.equal(await page.locator('[data-deflectometry-reference]').count(), 2);
      assert.ok(
        await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
        'Deflectometry mobile reference overflow',
      );
      await page
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'mobile-reference-revealed.png') });
      await page.locator('.scene-reset').click();
      assert.equal(await page.locator('[data-deflectometry-reference]').count(), 0);
    }
    if (plan.recipe === 'imaging101-fan-beam-v1') {
      for (let step = 1; step < plan.beats.length; step++) {
        await page.locator(`[data-story-step="${step}"]`).click();
        await page.waitForFunction(
          (f) =>
            document.querySelector('.scene-player')?.getAttribute('data-committed-frame') ===
            String(f),
          plan.beats[step].startFrame,
        );
        assert.ok(
          await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
          'Fan-beam mobile overflow',
        );
        await page
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `mobile-chapter-${step}.png`) });
      }
      await page.locator('[data-story-step="4"]').click();
      assert.equal(await page.locator('[data-fan-beam-reference]').count(), 0);
      await page.locator('.scene-play').click();
      await page.locator('[data-fan-beam-reference]').first().waitFor({ timeout: 20000 });
      await page.locator('.scene-play').click();
      assert.equal(await page.locator('[data-fan-beam-reference]').count(), 1);
      assert.ok(
        await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
        'Fan-beam mobile reference overflow',
      );
      await page
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'mobile-reference-revealed.png') });
      await page.locator('.scene-reset').click();
      assert.equal(await page.locator('[data-fan-beam-reference]').count(), 0);
    }
    if (plan.recipe === 'imaging101-dual-energy-v1') {
      for (let step = 1; step < plan.beats.length; step++) {
        await page.locator(`[data-story-step="${step}"]`).click();
        await page.waitForFunction(
          (f) =>
            document.querySelector('.scene-player')?.getAttribute('data-committed-frame') ===
            String(f),
          plan.beats[step].startFrame,
        );
        assert.ok(
          await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
          'Dual-energy mobile overflow',
        );
        await page
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `mobile-chapter-${step}.png`) });
      }
      await page.locator('[data-story-step="4"]').click();
      assert.equal(await page.locator('[data-dual-energy-reference]').count(), 0);
      await page.locator('.scene-play').click();
      await page.locator('[data-dual-energy-reference]').first().waitFor({ timeout: 20000 });
      await page.locator('.scene-play').click();
      assert.equal(await page.locator('[data-dual-energy-reference]').count(), 1);
      assert.ok(
        await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
        'Dual-energy mobile reference overflow',
      );
      await page
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'mobile-reference-revealed.png') });
      await page.locator('.scene-reset').click();
      assert.equal(await page.locator('[data-dual-energy-reference]').count(), 0);
    }
    if (plan.recipe === 'imaging101-ptychography-v1') {
      for (let step = 1; step < plan.beats.length; step++) {
        await page.locator(`[data-story-step="${step}"]`).click();
        await page.waitForFunction(
          (f) =>
            document.querySelector('.scene-player')?.getAttribute('data-committed-frame') ===
            String(f),
          plan.beats[step].startFrame,
        );
        assert.ok(
          await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
          'Ptychography mobile overflow',
        );
        await page
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `mobile-chapter-${step}.png`) });
      }
      await page.locator('[data-story-step="4"]').click();
      assert.equal(await page.locator('[data-ptychography-reference]').count(), 0);
      await page.locator('.scene-play').click();
      await page.locator('[data-ptychography-reference]').waitFor({ timeout: 20000 });
      await page.locator('.scene-play').click();
      assert.equal(await page.locator('[data-ptychography-reference]').count(), 1);
      assert.ok(
        await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
        'Ptychography mobile reference overflow',
      );
      await page
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'mobile-reference-revealed.png') });
      await page.locator('.scene-reset').click();
      assert.equal(await page.locator('[data-ptychography-reference]').count(), 0);
    }
    if (plan.recipe === 'imaging101-nlos-v1') {
      for (let step = 1; step < plan.beats.length; step++) {
        await page.locator(`[data-story-step="${step}"]`).click();
        await page.waitForFunction(
          (f) =>
            document.querySelector('.scene-player')?.getAttribute('data-committed-frame') ===
            String(f),
          plan.beats[step].startFrame,
        );
        assert.ok(
          await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
          'NLOS mobile overflow',
        );
        await page
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `mobile-chapter-${step}.png`) });
      }
      await page.locator('[data-story-step="4"]').click();
      assert.equal(await page.locator('[data-nlos-reference]').count(), 0);
      await page.locator('.scene-play').click();
      await page.locator('[data-nlos-reference]').waitFor({ timeout: 20000 });
      await page.locator('.scene-play').click();
      assert.equal(await page.locator('[data-nlos-reference]').count(), 1);
      assert.ok(
        await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
        'NLOS mobile reference overflow',
      );
      await page
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'mobile-reference-revealed.png') });
      await page.locator('.scene-reset').click();
      assert.equal(await page.locator('[data-nlos-reference],[data-nlos-reference]').count(), 0);
    }
    if (plan.recipe === 'imaging101-cars-v1') {
      for (let step = 1; step < plan.beats.length; step++) {
        await page.locator(`[data-story-step="${step}"]`).click();
        await page.waitForFunction(
          (f) =>
            document.querySelector('.scene-player')?.getAttribute('data-committed-frame') ===
            String(f),
          plan.beats[step].startFrame,
        );
        assert.ok(
          await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
          'CARS mobile overflow',
        );
        await page
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `mobile-chapter-${step}.png`) });
      }
      await page.locator('[data-story-step="4"]').click();
      assert.equal(await page.locator('[data-cars-reference]').count(), 0);
      await page.locator('.scene-play').click();
      await page.locator('[data-cars-reference]').waitFor({ timeout: 20000 });
      await page.locator('.scene-play').click();
      assert.equal(await page.locator('[data-cars-reference]').count(), 1);
      assert.ok(
        await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
        'CARS mobile reference overflow',
      );
      await page
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'mobile-reference-revealed.png') });
      await page.locator('.scene-reset').click();
      assert.equal(await page.locator('[data-cars-reference],[data-cars-reference]').count(), 0);
    }
    if (plan.recipe === 'rex-topcow-v1') {
      for (let step = 1; step < plan.beats.length; step++) {
        await page.locator(`[data-story-step="${step}"]`).click();
        await page.waitForFunction(
          (f) =>
            document.querySelector('.scene-player')?.getAttribute('data-committed-frame') ===
            String(f),
          plan.beats[step].startFrame,
        );
        assert.ok(
          await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
          'Rex mobile overflow',
        );
        await page
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `mobile-chapter-${step}.png`) });
      }
      await page.locator('[data-story-step="4"]').click();
      assert.equal(await page.locator('[data-rex-crop]').count(), 0);
      await page.locator('.scene-play').click();
      await page.locator('[data-rex-crop]').waitFor({ timeout: 20000 });
      await page.locator('.scene-play').click();
      assert.equal(await page.locator('[data-rex-reference]').count(), 2);
      assert.ok(
        await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
        'Rex mobile reference overflow',
      );
      await page
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'mobile-reference-revealed.png') });
      await page.locator('.scene-reset').click();
      assert.equal(await page.locator('[data-rex-crop],[data-rex-reference]').count(), 0);
    }
    if (plan.recipe === 'automed-multiorgan-v1') {
      for (let step = 1; step < plan.beats.length; step++) {
        await page.locator(`[data-story-step="${step}"]`).click();
        await page.waitForFunction(
          (f) =>
            document.querySelector('.scene-player')?.getAttribute('data-committed-frame') ===
            String(f),
          plan.beats[step].startFrame,
        );
        assert.ok(
          await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
          'Automed mobile overflow',
        );
        await page
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `mobile-chapter-${step}.png`) });
      }
    }
    if (plan.recipe === 'bcer-workflow-v1') {
      for (let step = 1; step < plan.beats.length; step++) {
        await page.locator(`[data-story-step="${step}"]`).click();
        await page.waitForFunction(
          (f) =>
            document.querySelector('.scene-player')?.getAttribute('data-committed-frame') ===
            String(f),
          plan.beats[step].startFrame,
        );
        assert.ok(
          await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
          'BCER mobile overflow',
        );
        if (plan.beats[step].scene === 'dependencies') {
          const optional = page.locator('[data-bcer-scene] li[data-required="false"]');
          assert.equal(await optional.count(), 2);
          assert.ok(
            await optional.evaluateAll((nodes) =>
              nodes.every((e) => getComputedStyle(e).borderTopStyle === 'dashed'),
            ),
          );
        }
        await page
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `mobile-chapter-${step}.png`) });
      }
    }
    if (plan.recipe === 'abra-annotation-v1') {
      for (let step = 1; step < plan.beats.length; step++) {
        await page.locator(`[data-story-step="${step}"]`).click();
        await page.waitForFunction(
          (f) =>
            document.querySelector('.scene-player')?.getAttribute('data-committed-frame') ===
            String(f),
          plan.beats[step].startFrame,
        );
        assert.ok(
          await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
          'ABRA mobile overflow',
        );
        await page
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `mobile-chapter-${step}.png`) });
        if (['reference', 'oracle'].includes(plan.beats[step].scene)) {
          await page.locator('.scene-play').click();
          await page
            .locator(
              plan.beats[step].scene === 'reference'
                ? '[data-abra-reference-info]'
                : '[data-abra-output]',
            )
            .first()
            .waitFor();
          await page.locator('.scene-play').click();
          assert.ok(
            await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
            'ABRA mobile reveal overflow',
          );
          await page
            .locator('.scene-player')
            .screenshot({ path: path.join(out, `mobile-${plan.beats[step].scene}.png`) });
        }
      }
    }
    if (plan.recipe === 'ct-context-v1') {
      for (let step = 1; step < plan.beats.length; step++) {
        await page.locator(`[data-story-step="${step}"]`).click();
        await page.waitForFunction(
          (f) =>
            document.querySelector('.scene-player')?.getAttribute('data-committed-frame') ===
            String(f),
          plan.beats[step].startFrame,
        );
        assert.ok(
          await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
          'Context mobile overflow',
        );
        await page
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `mobile-chapter-${step}.png`) });
        if (plan.beats[step].scene === 'reference') {
          await page.locator('.scene-play').click();
          await page.locator('[data-context-private]').first().waitFor();
          await page.locator('.scene-play').click();
          assert.ok(
            await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
            'Context mobile reveal overflow',
          );
          await page
            .locator('.scene-player')
            .screenshot({ path: path.join(out, 'mobile-reference.png') });
        }
      }
    }

    if (plan.recipe === 'history-sourcing-v1') {
      for (let step = 1; step < plan.beats.length; step++) {
        await page.locator(`[data-story-step="${step}"]`).click();
        await page.waitForFunction(
          (f) =>
            document.querySelector('.scene-player')?.getAttribute('data-committed-frame') ===
            String(f),
          plan.beats[step].startFrame,
        );
        assert.ok(
          await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
          'History mobile overflow',
        );
        await page
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `mobile-chapter-${step}.png`) });
        if (plan.beats[step].scene === 'reference') {
          await page.locator('.scene-play').click();
          await page.locator('[data-history-private]').first().waitFor();
          await page.locator('.scene-play').click();
          assert.ok(
            await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
            'History mobile reveal overflow',
          );
          await page
            .locator('.scene-player')
            .screenshot({ path: path.join(out, 'mobile-reference.png') });
        }
      }
    }

    if (plan.recipe === 'mri-importer-v1') {
      for (let step = 1; step < plan.beats.length; step++) {
        await page.locator(`[data-story-step="${step}"]`).click();
        await page.waitForFunction(
          (f) =>
            document.querySelector('.scene-player')?.getAttribute('data-committed-frame') ===
            String(f),
          plan.beats[step].startFrame,
        );
        assert.ok(
          await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
          'MR mobile overflow',
        );
        await page
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `mobile-chapter-${step}.png`) });
        if (step === 7) {
          assert.ok(
            await page.locator('[data-mri-controls] tbody td:nth-child(2)').evaluateAll((cells) =>
              cells.every((cell) => {
                const r = document.createRange();
                r.selectNodeContents(cell);
                return (
                  r.getBoundingClientRect().height <=
                  parseFloat(getComputedStyle(cell).lineHeight) + 1
                );
              }),
            ),
            'MR score denominator wraps across lines',
          );
        }
        if (step === 6) {
          await page.locator('.scene-play').click();
          await page.locator('[data-mri-private]').first().waitFor();
          await page.locator('.scene-play').click();
          assert.ok(
            await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
            'MR mobile reference overflow',
          );
          await page
            .locator('.scene-player')
            .screenshot({ path: path.join(out, 'mobile-reference.png') });
        }
      }
    }
    if (plan.recipe === 'localized-ct-v1') {
      for (let step = 1; step < plan.beats.length; step++) {
        await page.locator(`[data-story-step="${step}"]`).click();
        await page.waitForFunction(
          (f) =>
            document.querySelector('.scene-player')?.getAttribute('data-committed-frame') ===
            String(f),
          plan.beats[step].startFrame,
        );
        assert.ok(
          await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
          'Localized mobile overflow',
        );
        await page
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `mobile-chapter-${step}.png`) });
      }
    }
    if (plan.recipe === 'aneurysm-localization-v1') {
      for (const step of [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]) {
        await page.locator(`[data-story-step="${step}"]`).click();
        await page.waitForFunction(
          (f) =>
            document.querySelector('.scene-player')?.getAttribute('data-committed-frame') ===
            String(f),
          plan.beats[step].startFrame,
        );
        assert.ok(
          await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
          'Aneurysm mobile overflow',
        );
        await page
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `mobile-chapter-${step}.png`) });
      }
    }
    if (plan.recipe === 'segmentation-calibration-v1') {
      for (const step of [1, 2, 3, 5, 6, 7, 8, 9, 10, 11]) {
        await page.locator(`[data-story-step="${step}"]`).click();
        await page.waitForFunction(
          (f) =>
            document.querySelector('.scene-player')?.getAttribute('data-committed-frame') ===
            String(f),
          plan.beats[step].startFrame,
        );
        assert.ok(
          await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
          'Calibration mobile overflow',
        );
        await page
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `mobile-chapter-${step}.png`) });
      }
    }
    if (plan.recipe === 'dental-v3-v1') {
      for (const step of [2, 3, 5, 6, 7, 8, 9, 10, 11]) {
        await page.locator(`[data-story-step="${step}"]`).click();
        await page.waitForFunction(
          (f) =>
            document.querySelector('.scene-player')?.getAttribute('data-committed-frame') ===
            String(f),
          plan.beats[step].startFrame,
        );
        assert.ok(
          await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
          'Dental v3 mobile overflow',
        );
        if (step === 5)
          assert.equal(await page.locator('[data-scene-inline-narration]').count(), 0);
        await page
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `mobile-chapter-${step}.png`) });
      }
    }
    if (plan.recipe === 'dental-v2-v1') {
      for (const step of [2, 3, 5, 6, 7, 8, 9, 10, 11]) {
        await page.locator(`[data-story-step="${step}"]`).click();
        await page.waitForFunction(
          (f) =>
            document.querySelector('.scene-player')?.getAttribute('data-committed-frame') ===
            String(f),
          plan.beats[step].startFrame,
        );
        assert.ok(
          await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
          'Dental v2 mobile overflow',
        );
        if (step === 5)
          assert.equal(await page.locator('[data-scene-inline-narration]').count(), 0);
        await page
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `mobile-chapter-${step}.png`) });
      }
    }
    if (plan.recipe === 'dental-original-v1') {
      for (const step of [4, 5, 6, 8, 9, 10]) {
        await page.locator(`[data-story-step="${step}"]`).click();
        await page.waitForFunction(
          (f) =>
            document.querySelector('.scene-player')?.getAttribute('data-committed-frame') ===
            String(f),
          plan.beats[step].startFrame,
        );
        assert.ok(
          await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
          'Dental mobile overflow',
        );
        await page
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `mobile-chapter-${step}.png`) });
      }
    }
    if (plan.recipe === 'ct-organ-v1') {
      for (const step of [2, 3, 6, 8, 9]) {
        await page.locator(`[data-story-step="${step}"]`).click();
        await page.waitForFunction(
          (f) =>
            document.querySelector('.scene-player')?.getAttribute('data-committed-frame') ===
            String(f),
          plan.beats[step].startFrame,
        );
        assert.ok(
          await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
          'CT mobile overflow',
        );
        await page
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `mobile-chapter-${step}.png`) });
      }
    }
    if (plan.recipe === 'named-landmarks-v1') {
      for (const step of [4, 5, 8, 9, 10]) {
        await page.locator(`[data-story-step="${step}"]`).click();
        assert.equal(
          await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
          true,
          'Landmark mobile overflow',
        );
        await page
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `mobile-chapter-${step}.png`) });
      }
    }
    if (plan.recipe === 'clinical-cavity-v1') {
      for (const step of [4, 5, 6, 7, 8, 9, 10]) {
        await page.locator(`[data-story-step="${step}"]`).click();
        await page.waitForFunction(
          (frame) =>
            document.querySelector('.scene-player')?.getAttribute('data-committed-frame') ===
            String(frame),
          plan.beats[step].startFrame,
        );
        assert.ok(
          await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
          'Cavity mobile chapter overflows',
        );
        const panel = await page.locator('[data-cavity-output]').boundingBox();
        assert.ok(
          panel && panel.x >= 0 && panel.x + panel.width <= 390,
          'Cavity mobile panel clipped',
        );
        if ([4, 9, 10].includes(step))
          await page
            .locator('.scene-player')
            .screenshot({ path: path.join(out, `mobile-chapter-${step}.png`) });
      }
    }
    if (plan.recipe === 'tiger-context-v1') {
      const labels = await page.locator('[data-tiger-scene]').evaluate((svg) => {
        const box = svg.getBoundingClientRect();
        return [...svg.querySelectorAll('text')].every((text) => {
          const b = text.getBoundingClientRect();
          return b.width > 0 && b.height > 0 && b.left >= box.left - 1 && b.right <= box.right + 1;
        });
      });
      assert.ok(
        labels,
        'TIGER mobile scale and source labels must remain visible and inside the figure',
      );
    }
    if (plan.recipe === 'mixed-tissue-v1') {
      assert.equal(await page.locator('[data-mixed-orientation]').isVisible(), true);
      assert.match(await page.locator('[data-mixed-orientation]').innerText(), /LPS mm/);
    }
    await page.setViewportSize({ width: 1280, height: 900 });
    const noGpu = await browser.newContext({
      viewport: { width: 1280, height: 900 },
      reducedMotion: 'reduce',
    });
    await noGpu.route(/^https?:/, (route) => {
      report.remote_requests.push(route.request().url());
      return route.abort();
    });
    await noGpu.addInitScript(() => {
      const original = HTMLCanvasElement.prototype.getContext;
      HTMLCanvasElement.prototype.getContext = function (type, ...args) {
        return type === 'webgl2' || type === 'webgl' ? null : original.call(this, type, ...args);
      };
    });
    const fallback = await noGpu.newPage();
    await fallback.goto(url + '?lang=en');
    await fallback.locator('.scene-player[data-rendered="true"]').waitFor();
    const renderer = await fallback.locator('.scene-player').getAttribute('data-surface-renderer');
    const planar = [
      'automed-brain-cls-v1',
      'rex-ldct-iqa-v1',
      'radagent-vqa-v1',
      'abra-birads-v1',
      'abra-vision-probe-v1',
      'abra-metadata-qa-v1',
      'abra-viewer-control-v1',
      'bcer-brain-full-v1',
      'bcer-cardiac-full-v1',
      'bcer-brain-grade-v1',
      'healthagentbench-cxr-correction-v1',
      'healthagentbench-tumor-tiles-v1',
      'radagent-report-v1',
      'healthagentbench-ct-findings-v1',
      'automed-full-tsg-multiorgan-v1',
      'automed-full-spleen-v1',
      'automed-full-prostate-seg-v1',
      'automed-full-panther-t2-seg-v1',
      'automed-full-panther-t1-seg-v1',
      'automed-full-pancreas-seg-v1',
      'automed-full-pancreas-oar-v1',
      'automed-full-liver-v1',
      'automed-full-kidney-v1',
      'automed-full-hepaticvessel-v1',
      'imaging101-eht-original-v1',
      'imaging101-eht-features-dynamic-v1',
      'imaging101-eht-dynamic-v1',
      'imaging101-eht-uq-v1',
      'imaging101-dti-v1',
      'imaging101-deflectometry-v1',
      'imaging101-fan-beam-v1',
      'imaging101-dual-energy-v1',
      'imaging101-ptychography-v1',
      'imaging101-nlos-v1',
      'imaging101-cars-v1',
      'rex-topcow-v1',
      'automed-multiorgan-v1',
      'bcer-workflow-v1',
      'abra-annotation-v1',
      'ct-context-v1',
      'history-sourcing-v1',
      'mri-importer-v1',
      'localized-ct-v1',
      'aneurysm-localization-v1',
      'segmentation-calibration-v1',
      'dental-v3-v1',
      'dental-v2-v1',
      'dental-original-v1',
      'ct-organ-v1',
      'multiscale-v1',
      'local-edit-v1',
      'longitudinal-v1',
      'inverse-v1',
      'anatomy-identity-v1',
      'prototype-identity-v1',
      'mask-screen-v1',
      'anatomy-curation-v1',
      'named-landmarks-v1',
      'cardiac-contour-v1',
      'cardiac-anchor-v1',
      'cardiac-material-v1',
      'automed-full-heart-seg-v1',
      'automed-full-feta-seg-v1',
      'automed-full-colon-seg-v1',
      'automed-full-aeropath-seg-v1',
      'automed-full-vindr-cxr-detection-v1',
      'automed-full-grazpedwri-detection-v1',
      'automed-full-dentex-detection-v1',
      'automed-full-bccd-detection-v1',
      'rex-topcow-mr-edges-v1',
      'rex-topcow-ct-edges-v1',
      'rex-topcow-mr-box-v1',
      'rex-topcow-ct-box-v1',
      'rex-topcow-mr-seg-v1',
      'rex-topbrain-mr-v1',
      'rex-topbrain-ct-v1',
      'rex-seg-a-v1',
      'rexmle-puma-track2-task2-v1',
      'rexmle-puma-track1-task2-v1',
      'rexmle-puma-track1-task1-v1',
      'rex-panther-task2-v1',
      'rex-panther-task1-v1',
      'rexmle-neurips-cellseg-v1',
      'rex-isles22-v1',
      'rexmle-dentex-v1',
      'abra-longitudinal-v1',
      'bcer-prostate-registration-v1',
      'bcer-brain-v1',
      'automed-kidney-v1',
      'report-reading-v1',
      'cardiac-mask-mechanics-v1',
      'cardiac-real-echo-v1',
      'clinical-cavity-v1',
      'respiratory-v1',
      'registration-analysis-v1',
      'resect-correspondence-v1',
      'resect-pilot-v1',
      'vessel-source-v1',
      'airway-repair-v1',
      'topbrain-screen-v1',
      'hubmap-inventory-v1',
      'tiger-context-v1',
      'longitudinal-mri-v1',
      'longitudinal-ct-original-v1',
      'longitudinal-ct-revised-v1',
      'mixed-tissue-v1',
    ].includes(plan.recipe);
    assert.equal(renderer, planar ? 'planar' : 'poster');
    await reviewCardiacInteractions(fallback, plan, out, 'no-gpu');
    if (plan.recipe === 'imaging101-eht-original-v1') {
      for (const step of [1, 3, 6]) {
        await fallback.locator(`[data-story-step="${step}"]`).click();
        await fallback.locator(`[data-original-scene="${plan.beats[step].scene}"]`).waitFor();
        await fallback
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `no-gpu-${plan.beats[step].scene}.png`) });
      }
      await fallback.locator('.scene-reset').click();
      await fallback.locator('[data-original-scene="inputs"]').waitFor();
    }
    if (plan.recipe === 'imaging101-eht-features-dynamic-v1') {
      for (const step of [1, 3, 6]) {
        await fallback.locator(`[data-story-step="${step}"]`).click();
        await fallback.locator(`[data-features-scene="${plan.beats[step].scene}"]`).waitFor();
        await fallback
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `no-gpu-${plan.beats[step].scene}.png`) });
      }
      await fallback.locator('.scene-reset').click();
      await fallback.locator('[data-features-scene="inputs"]').waitFor();
    }
    if (plan.recipe === 'imaging101-eht-dynamic-v1') {
      for (const step of [1, 3, 6]) {
        await fallback.locator(`[data-story-step="${step}"]`).click();
        await fallback.locator(`[data-dynamic-scene="${plan.beats[step].scene}"]`).waitFor();
        await fallback
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `no-gpu-${plan.beats[step].scene}.png`) });
      }
      await fallback.locator('.scene-reset').click();
      await fallback.locator('[data-dynamic-scene="inputs"]').waitFor();
    }
    if (plan.recipe === 'imaging101-eht-uq-v1') {
      for (const step of [1, 3, 6]) {
        await fallback.locator(`[data-story-step="${step}"]`).click();
        await fallback.locator(`[data-eht-scene="${plan.beats[step].scene}"]`).waitFor();
        await fallback
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `no-gpu-${plan.beats[step].scene}.png`) });
      }
      await fallback.locator('.scene-reset').click();
      await fallback.locator('[data-eht-scene="inputs"]').waitFor();
    }
    if (plan.recipe === 'imaging101-dti-v1') {
      for (const step of [1, 3, 6]) {
        await fallback.locator(`[data-story-step="${step}"]`).click();
        await fallback.locator(`[data-dti-scene="${plan.beats[step].scene}"]`).waitFor();
        await fallback
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `no-gpu-${plan.beats[step].scene}.png`) });
      }
      await fallback.locator('.scene-reset').click();
      await fallback.locator('[data-dti-scene="inputs"]').waitFor();
    }
    if (plan.recipe === 'imaging101-deflectometry-v1') {
      for (const step of [2, 3, 6]) {
        await fallback.locator(`[data-story-step="${step}"]`).click();
        await fallback.locator(`[data-deflectometry-scene="${plan.beats[step].scene}"]`).waitFor();
        await fallback
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `no-gpu-${plan.beats[step].scene}.png`) });
      }
      await fallback.locator('.scene-reset').click();
      await fallback.locator('[data-deflectometry-scene="inputs"]').waitFor();
    }
    if (plan.recipe === 'imaging101-fan-beam-v1') {
      for (const step of [1, 2, 5]) {
        await fallback.locator(`[data-story-step="${step}"]`).click();
        await fallback.locator(`[data-fan-beam-scene="${plan.beats[step].scene}"]`).waitFor();
        await fallback
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `no-gpu-${plan.beats[step].scene}.png`) });
      }
      await fallback.locator('.scene-reset').click();
      await fallback.locator('[data-fan-beam-scene="inputs"]').waitFor();
    }
    if (plan.recipe === 'imaging101-dual-energy-v1') {
      for (const step of [2, 5, 6]) {
        await fallback.locator(`[data-story-step="${step}"]`).click();
        await fallback.locator(`[data-dual-energy-scene="${plan.beats[step].scene}"]`).waitFor();
        await fallback
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `no-gpu-${plan.beats[step].scene}.png`) });
      }
      await fallback.locator('.scene-reset').click();
      await fallback.locator('[data-dual-energy-scene="inputs"]').waitFor();
    }
    if (plan.recipe === 'imaging101-ptychography-v1') {
      for (const step of [2, 5, 6]) {
        await fallback.locator(`[data-story-step="${step}"]`).click();
        await fallback.locator(`[data-ptychography-scene="${plan.beats[step].scene}"]`).waitFor();
        await fallback
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `no-gpu-${plan.beats[step].scene}.png`) });
      }
      await fallback.locator('.scene-reset').click();
      await fallback.locator('[data-ptychography-scene="inputs"]').waitFor();
    }
    if (plan.recipe === 'imaging101-nlos-v1') {
      for (const step of [2, 5, 6]) {
        await fallback.locator(`[data-story-step="${step}"]`).click();
        await fallback.locator(`[data-nlos-scene="${plan.beats[step].scene}"]`).waitFor();
        await fallback
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `no-gpu-${plan.beats[step].scene}.png`) });
      }
      await fallback.locator('.scene-reset').click();
      await fallback.locator('[data-nlos-scene="inputs"]').waitFor();
    }
    if (plan.recipe === 'imaging101-cars-v1') {
      for (const step of [2, 5, 6]) {
        await fallback.locator(`[data-story-step="${step}"]`).click();
        await fallback.locator(`[data-cars-scene="${plan.beats[step].scene}"]`).waitFor();
        await fallback
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `no-gpu-${plan.beats[step].scene}.png`) });
      }
      await fallback.locator('.scene-reset').click();
      await fallback.locator('[data-cars-scene="inputs"]').waitFor();
    }
    if (plan.recipe === 'rex-topcow-v1') {
      for (const step of [2, 5, 6]) {
        await fallback.locator(`[data-story-step="${step}"]`).click();
        await fallback.locator(`[data-rex-scene="${plan.beats[step].scene}"]`).waitFor();
        await fallback
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `no-gpu-${plan.beats[step].scene}.png`) });
      }
      await fallback.locator('.scene-reset').click();
      await fallback.locator('[data-rex-scene="inputs"]').waitFor();
    }
    if (plan.recipe === 'automed-multiorgan-v1') {
      for (const step of [2, 6]) {
        await fallback.locator(`[data-story-step="${step}"]`).click();
        await fallback.locator(`[data-automed-scene="${plan.beats[step].scene}"]`).waitFor();
        await fallback
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `no-gpu-${plan.beats[step].scene}.png`) });
      }
      await fallback.locator('.scene-reset').click();
      await fallback.locator('[data-automed-scene="inputs"]').waitFor();
    }
    if (plan.recipe === 'bcer-workflow-v1') {
      for (const step of [2, 3, 5]) {
        await fallback.locator(`[data-story-step="${step}"]`).click();
        await fallback.locator(`[data-bcer-scene="${plan.beats[step].scene}"]`).waitFor();
        await fallback
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `no-gpu-${plan.beats[step].scene}.png`) });
      }
      await fallback.locator('.scene-reset').click();
      await fallback.locator('[data-bcer-scene="inputs"]').waitFor();
    }
    if (plan.recipe === 'abra-annotation-v1') {
      assert.equal(
        await fallback
          .locator('[data-abra-reference],[data-abra-oracle],[data-abra-output]')
          .count(),
        0,
      );
      for (const [step, selector, name] of [
        [3, '[data-abra-reference-info]', 'reference'],
        [5, '[data-abra-output]', 'oracle'],
      ]) {
        await fallback.locator(`[data-story-step="${step}"]`).click();
        await fallback.locator('.scene-play').click();
        await fallback.locator(selector).first().waitFor();
        await fallback.locator('.scene-play').click();
        await fallback
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `no-gpu-${name}.png`) });
      }
      await fallback.locator('.scene-reset').click();
      await fallback.locator('[data-abra-scene="inputs"]').waitFor();
      assert.equal(
        await fallback
          .locator('[data-abra-reference],[data-abra-oracle],[data-abra-output]')
          .count(),
        0,
      );
    }
    if (plan.recipe === 'ct-context-v1') {
      assert.equal(await fallback.locator('[data-context-private]').count(), 0);
      await fallback.locator('[data-story-step="2"]').click();
      await fallback.locator('[data-context-point]').first().waitFor();
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-liver.png') });
      await fallback.locator('[data-story-step="5"]').click();
      await fallback.locator('.scene-play').click();
      await fallback.locator('[data-context-private]').first().waitFor();
      await fallback.locator('.scene-play').click();
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-reference.png') });
      await fallback.locator('.scene-reset').click();
      await fallback.waitForFunction(
        () =>
          document
            .querySelector('[data-context-reference]')
            ?.getAttribute('data-context-reference') === 'hidden',
      );
      assert.equal(await fallback.locator('[data-context-private]').count(), 0);
    }
    if (plan.recipe === 'history-sourcing-v1') {
      assert.equal(await fallback.locator('[data-history-private]').count(), 0);
      await fallback.locator('[data-story-step="1"]').click();
      await fallback.locator('[data-history-excerpt]').waitFor();
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-excerpts.png') });
      await fallback.locator('[data-story-step="5"]').click();
      await fallback.locator('.scene-play').click();
      await fallback.locator('[data-history-private]').first().waitFor();
      await fallback.locator('.scene-play').click();
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-reference.png') });
      await fallback.locator('.scene-reset').click();
      await fallback.waitForFunction(
        () =>
          document
            .querySelector('[data-history-reference]')
            ?.getAttribute('data-history-reference') === 'hidden',
      );
      assert.equal(await fallback.locator('[data-history-private]').count(), 0);
    }
    if (plan.recipe === 'mri-importer-v1') {
      assert.equal(await fallback.locator('[data-mri-private]').count(), 0);
      await fallback.locator('[data-story-step="2"]').click();
      assert.equal(
        await fallback.locator('[data-mri-grid] article[data-selected="true"]').count(),
        2,
      );
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-association.png') });
      await fallback.locator('[data-story-step="6"]').click();
      await fallback.locator('.scene-play').click();
      await fallback.locator('[data-mri-private]').first().waitFor();
      await fallback.locator('.scene-play').click();
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-reference.png') });
      await fallback.locator('.scene-reset').click();
      await fallback.waitForFunction(
        () =>
          document.querySelector('[data-mri-reference]')?.getAttribute('data-mri-reference') ===
          'hidden',
      );
      assert.equal(await fallback.locator('[data-mri-private]').count(), 0);
    }
    if (plan.recipe === 'localized-ct-v1') {
      assert.equal(await fallback.locator('[data-localized-private]').count(), 0);
      assert.equal(await fallback.locator('[data-localized-point]').count(), 2);
      await fallback.locator('[data-story-step="7"]').click();
      await fallback.locator('.scene-play').click();
      await fallback.locator('path[data-localized-private]').first().waitFor();
      await fallback.locator('.scene-play').click();
      assert.equal(await fallback.locator('path[data-localized-private]').count(), 2);
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-reference.png') });
      await fallback.locator('.scene-reset').click();
      await fallback.waitForFunction(
        () =>
          document
            .querySelector('[data-localized-reference]')
            ?.getAttribute('data-localized-reference') === 'hidden',
      );
      assert.equal(await fallback.locator('[data-localized-private]').count(), 0);
    }
    if (plan.recipe === 'aneurysm-localization-v1') {
      assert.equal(
        await fallback.locator('[data-aneurysm-point], [data-aneurysm-private]').count(),
        0,
      );
      await fallback.locator('[data-story-step="7"]').click();
      await fallback.waitForFunction(
        () =>
          document
            .querySelector('[data-aneurysm-reference]')
            ?.getAttribute('data-aneurysm-reference') === 'visible',
      );
      assert.ok((await fallback.locator('[data-aneurysm-private]').count()) > 0);
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-reference.png') });
      await fallback.locator('.scene-reset').click();
      await fallback.waitForFunction(
        () =>
          document
            .querySelector('[data-aneurysm-reference]')
            ?.getAttribute('data-aneurysm-reference') === 'hidden',
      );
      assert.equal(
        await fallback.locator('[data-aneurysm-point], [data-aneurysm-private]').count(),
        0,
      );
    }
    if (plan.recipe === 'segmentation-calibration-v1') {
      assert.equal(await fallback.locator('[data-calibration-layer]').count(), 0);
      await fallback.locator('[data-story-step="7"]').click();
      await fallback.waitForFunction(
        () =>
          document
            .querySelector('[data-calibration-reference]')
            ?.getAttribute('data-calibration-reference') === 'visible',
      );
      assert.ok((await fallback.locator('[data-calibration-layer="reference"]').count()) > 0);
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-reference.png') });
      await fallback.locator('.scene-reset').click();
      await fallback.waitForFunction(
        () =>
          document
            .querySelector('[data-calibration-reference]')
            ?.getAttribute('data-calibration-reference') === 'hidden',
      );
      assert.equal(await fallback.locator('[data-calibration-layer]').count(), 0);
    }
    if (plan.recipe === 'dental-v3-v1') {
      assert.equal(await fallback.locator('[data-dental-v3-layer]').count(), 0);
      await fallback.locator('[data-story-step="9"]').click();
      await fallback.waitForFunction(
        () =>
          document
            .querySelector('[data-dental-v3-reference]')
            ?.getAttribute('data-dental-v3-reference') === 'visible',
      );
      assert.ok((await fallback.locator('[data-dental-v3-layer="reference"]').count()) > 0);
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-reference.png') });
      await fallback.locator('.scene-reset').click();
      await fallback.waitForFunction(
        () =>
          document
            .querySelector('[data-dental-v3-reference]')
            ?.getAttribute('data-dental-v3-reference') === 'hidden',
      );
      assert.equal(await fallback.locator('[data-dental-v3-layer]').count(), 0);
    }

    if (plan.recipe === 'dental-v2-v1') {
      assert.equal(await fallback.locator('[data-dental-v2-layer]').count(), 0);
      await fallback.locator('[data-story-step="9"]').click();
      await fallback.waitForFunction(
        () =>
          document
            .querySelector('[data-dental-v2-reference]')
            ?.getAttribute('data-dental-v2-reference') === 'visible',
      );
      assert.ok((await fallback.locator('[data-dental-v2-layer="reference"]').count()) > 0);
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-reference.png') });
      await fallback.locator('.scene-reset').click();
      await fallback.waitForFunction(
        () =>
          document
            .querySelector('[data-dental-v2-reference]')
            ?.getAttribute('data-dental-v2-reference') === 'hidden',
      );
      assert.equal(await fallback.locator('[data-dental-v2-layer]').count(), 0);
    }

    if (plan.recipe === 'dental-original-v1') {
      assert.equal(await fallback.locator('[data-dental-layer]').count(), 0);
      await fallback.locator('[data-story-step="5"]').click();
      await fallback.waitForFunction(
        () =>
          document
            .querySelector('[data-dental-reference]')
            ?.getAttribute('data-dental-reference') === 'visible',
      );
      assert.ok((await fallback.locator('[data-dental-layer="reference"]').count()) > 0);
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-reference.png') });
      await fallback.locator('.scene-reset').click();
      await fallback.waitForFunction(
        () =>
          document
            .querySelector('[data-dental-reference]')
            ?.getAttribute('data-dental-reference') === 'hidden',
      );
      assert.equal(await fallback.locator('[data-dental-layer]').count(), 0);
    }
    if (plan.recipe === 'ct-organ-v1') {
      assert.equal(await fallback.locator('[data-ct-layer]').count(), 0);
      await fallback.locator('[data-story-step="6"]').click();
      await fallback.waitForFunction(
        () =>
          document.querySelector('[data-ct-reference]')?.getAttribute('data-ct-reference') ===
          'visible',
      );
      assert.equal(await fallback.locator('[data-ct-layer="reference"]').count(), 2);
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-reference.png') });
      await fallback.locator('.scene-reset').click();
      await fallback.waitForFunction(
        () =>
          document.querySelector('[data-ct-reference]')?.getAttribute('data-ct-reference') ===
          'hidden',
      );
      assert.equal(await fallback.locator('[data-ct-layer]').count(), 0);
    }
    if (plan.recipe === 'named-landmarks-v1') {
      assert.equal(await fallback.locator('[data-landmark-mark]').count(), 0);
      await fallback.locator('[data-story-step="5"]').click();
      await fallback.waitForFunction(
        () =>
          document
            .querySelector('[data-landmark-reference]')
            ?.getAttribute('data-landmark-reference') === 'visible',
      );
      assert.equal(await fallback.locator('[data-landmark-mark="reference"]').count(), 3);
      assert.equal(await fallback.locator('[data-landmark-mark="sol"]').count(), 0);
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-reference.png') });
      await fallback.locator('.scene-reset').click();
      await fallback.waitForFunction(
        () =>
          document
            .querySelector('[data-landmark-reference]')
            ?.getAttribute('data-landmark-reference') === 'hidden',
      );
      assert.equal(await fallback.locator('[data-landmark-mark]').count(), 0);
    }
    if (plan.recipe === 'clinical-cavity-v1') {
      assert.equal(await fallback.locator('[data-cavity-projection]').count(), 1);
      assert.equal(await fallback.locator('[data-cavity-reference-section]').count(), 0);
      await fallback.locator('[data-story-step="4"]').click();
      await fallback.waitForFunction(
        () =>
          document.querySelector('[data-cavity-output]')?.getAttribute('data-cavity-reference') ===
          'revealed',
      );
      assert.equal(await fallback.locator('[data-cavity-reference-section]').count(), 6);
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-reference.png') });
      await fallback.locator('.scene-reset').click();
      await fallback.waitForFunction(
        () =>
          document.querySelector('[data-cavity-output]')?.getAttribute('data-cavity-reference') ===
          'hidden',
      );
      assert.equal(await fallback.locator('[data-cavity-reference-section]').count(), 0);
    }
    if (plan.recipe === 'longitudinal-ct-revised-v1') {
      assert.equal(await fallback.locator('[data-ct-reference], [data-ct-output]').count(), 0);
      await fallback.locator('[data-story-step="2"]').click();
      assert.equal(await fallback.locator('image[data-ct-reference]').count(), 2);
      await fallback.locator('.scene-reset').click();
      assert.equal(await fallback.locator('[data-ct-reference], [data-ct-output]').count(), 0);
    }
    if (plan.recipe === 'longitudinal-ct-original-v1') {
      assert.equal(await fallback.locator('[data-ct-reference], [data-ct-output]').count(), 0);
      await fallback.locator('[data-story-step="2"]').click();
      assert.equal(await fallback.locator('image[data-ct-reference]').count(), 1);
      await fallback.locator('.scene-reset').click();
      assert.equal(await fallback.locator('[data-ct-reference], [data-ct-output]').count(), 0);
    }
    if (plan.recipe === 'longitudinal-mri-v1') {
      assert.equal(await fallback.locator('[data-mri-reference], [data-mri-output]').count(), 0);
      await fallback.locator('[data-story-step="2"]').click();
      assert.equal(await fallback.locator('[data-mri-reference] [data-mri-input]').count(), 2);
      await fallback.locator('.scene-reset').click();
      assert.equal(await fallback.locator('[data-mri-reference], [data-mri-output]').count(), 0);
    }
    if (plan.recipe === 'airway-repair-v1') {
      // Check rendered pixels, not only nonempty paths: opposite mesh-face winding
      // can silently cancel a complete silhouette inside a compound SVG path.
      const bluePixels = await fallback.locator('.scene-stage svg').evaluate(async (svg) => {
        const image = new Image();
        const url = URL.createObjectURL(
          new Blob([new XMLSerializer().serializeToString(svg)], { type: 'image/svg+xml' }),
        );
        try {
          await new Promise((resolve, reject) => {
            image.onload = resolve;
            image.onerror = reject;
            image.src = url;
          });
          const canvas = document.createElement('canvas');
          canvas.width = 600;
          canvas.height = 420;
          const context = canvas.getContext('2d');
          context.drawImage(image, 0, 0, 600, 420);
          const pixels = context.getImageData(0, 0, 600, 420).data;
          let count = 0;
          for (let i = 0; i < pixels.length; i += 4)
            if (
              pixels[i + 3] > 100 &&
              pixels[i + 2] > pixels[i] + 20 &&
              pixels[i + 1] > pixels[i] + 15
            )
              count++;
          return count;
        } finally {
          URL.revokeObjectURL(url);
        }
      });
      assert.ok(bluePixels > 1000, 'Fallback must visibly render the supplied airway mask');
      row.fallbackMaskPixels = bluePixels;
      assert.equal(await fallback.locator('[data-airway-reference-geometry]').count(), 0);
      assert.equal(await fallback.locator('[data-airway-result]').count(), 0);
      await fallback.locator('[data-story-step="5"]').click();
      await fallback.waitForFunction(
        () => document.querySelector('[data-airway-reference-state]')?.textContent === 'hidden',
      );
      await fallback.locator('.scene-play').click();
      await fallback.locator('[data-airway-reference-geometry]').waitFor();
      await fallback.locator('.scene-play').click();
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-reference.png') });
      await fallback.locator('.scene-reset').click();
      await fallback.waitForFunction(
        () =>
          document.querySelector('[data-airway-output]')?.getAttribute('data-airway-output') ===
          'inputs',
      );
      assert.equal(await fallback.locator('[data-airway-reference-geometry]').count(), 0);
      assert.equal(await fallback.locator('[data-airway-result]').count(), 0);
    }
    if (plan.recipe === 'tiger-context-v1') {
      assert.equal(await fallback.locator('[data-tiger-reference]').count(), 0);
      await fallback.locator('[data-story-step="2"]').click();
      assert.equal(await fallback.locator('[data-tiger-reference]').count(), 0);
      await fallback.locator('.scene-play').click();
      await fallback.locator('.scene-stage').scrollIntoViewIfNeeded();
      await fallback.locator('[data-tiger-reference]').first().waitFor();
      await fallback.locator('.scene-play').click();
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-reference.png') });
      await fallback.locator('.scene-reset').click();
      await fallback.waitForFunction(
        () =>
          document.querySelector('[data-tiger-scene]')?.getAttribute('data-tiger-scene') ===
          'inputs',
      );
      assert.equal(await fallback.locator('[data-tiger-reference]').count(), 0);
      assert.equal(await fallback.locator('[data-tiger-measurement]').count(), 0);
    }
    if (plan.recipe === 'hubmap-inventory-v1') {
      assert.equal(await fallback.locator('[data-hubmap-reference]').count(), 0);
      await fallback.locator('[data-story-step="3"]').click();
      assert.equal(await fallback.locator('[data-hubmap-reference]').count(), 0);
      await fallback.locator('.scene-play').click();
      await fallback.locator('.scene-stage').scrollIntoViewIfNeeded();
      await fallback.locator('[data-hubmap-reference]').waitFor();
      await fallback.locator('.scene-play').click();
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-reference.png') });
      await fallback.locator('.scene-reset').click();
      await fallback.waitForFunction(
        () =>
          document.querySelector('[data-hubmap-scene]')?.getAttribute('data-hubmap-scene') ===
          'inputs',
      );
      assert.equal(await fallback.locator('[data-hubmap-reference]').count(), 0);
      assert.equal(await fallback.locator('[data-hubmap-measurement]').count(), 0);
    }
    if (plan.recipe === 'topbrain-screen-v1') {
      assert.equal(await fallback.locator('[data-brain-reference-image]').count(), 0);
      await fallback.locator('[data-story-step="6"]').click();
      await fallback.waitForFunction(
        () => document.querySelector('[data-brain-reference-state]')?.textContent === 'hidden',
      );
      await fallback.locator('.scene-play').click();
      await fallback.locator('.scene-stage').scrollIntoViewIfNeeded();
      await fallback.locator('[data-brain-reference-image]').first().waitFor();
      await fallback.locator('.scene-play').click();
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-reference.png') });
      await fallback.locator('.scene-reset').click();
      await fallback.waitForFunction(
        () =>
          document.querySelector('[data-brain-output]')?.getAttribute('data-brain-output') ===
          'inputs',
      );
      assert.equal(await fallback.locator('[data-brain-reference-image]').count(), 0);
      assert.equal(await fallback.locator('[data-brain-answer]').count(), 0);
    }
    if (plan.recipe === 'vessel-source-v1') {
      assert.equal(await fallback.locator('[data-vessel-reference-image]').count(), 0);
      await fallback.locator('[data-story-step="1"]').click();
      await fallback.waitForFunction(
        () => document.querySelector('[data-vessel-reference]')?.textContent === 'hidden',
      );
      await fallback.locator('.scene-play').click();
      await fallback.locator('[data-vessel-reference-image]').first().waitFor();
      await fallback.locator('.scene-play').click();
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-reference.png') });
      await fallback.locator('.scene-reset').click();
      await fallback.waitForFunction(
        () =>
          document.querySelector('[data-vessel-output]')?.getAttribute('data-vessel-output') ===
          'sources',
      );
      assert.equal(await fallback.locator('[data-vessel-reference-image]').count(), 0);
      assert.equal(await fallback.locator('[data-vessel-answer]').count(), 0);
    }
    if (plan.recipe === 'resect-pilot-v1') {
      await fallback.locator('[data-story-step="5"]').click();
      await fallback.waitForFunction(
        () => document.querySelector('[data-pilot-reference]')?.textContent === 'hidden',
      );
      assert.equal(await fallback.locator('[data-pilot-point="reference"]').count(), 0);
      await fallback.locator('.scene-play').click();
      await fallback.locator('[data-pilot-point="reference"]').first().waitFor();
      await fallback.locator('.scene-play').click();
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-reference.png') });
      await fallback.locator('[data-story-step="0"]').click();
      await fallback.waitForFunction(
        () =>
          document.querySelector('[data-pilot-output]')?.getAttribute('data-pilot-output') ===
          'inputs',
      );
      assert.equal(await fallback.locator('[data-pilot-point="reference"]').count(), 0);
      assert.equal(await fallback.locator('[data-pilot-answer]').count(), 0);
    }
    if (plan.recipe === 'resect-correspondence-v1') {
      await fallback.locator('[data-story-step="5"]').click();
      await fallback.waitForFunction(
        () => document.querySelector('[data-resect-reference]')?.textContent === 'hidden',
      );
      await fallback.locator('[data-story-step="6"]').click();
      await fallback.waitForFunction(() =>
        document.querySelector('[data-resect-output]')?.textContent.includes('9.58'),
      );
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-cases.png') });
      await fallback.locator('[data-story-step="0"]').click();
      await fallback.waitForFunction(
        () =>
          document.querySelector('[data-resect-output]')?.getAttribute('data-resect-output') ===
          'inputs',
      );
      assert.equal(await fallback.locator('[data-resect-target]').count(), 0);
    }
    if (plan.recipe === 'registration-analysis-v1') {
      await fallback.locator('[data-story-step="1"]').click();
      await fallback.waitForFunction(
        () => document.querySelector('[data-analysis-reference]')?.textContent === 'hidden',
      );
      await fallback.locator('[data-story-step="3"]').click();
      await fallback.waitForFunction(() =>
        document
          .querySelector('[data-registration-analysis-output]')
          ?.textContent.includes('18.994'),
      );
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-support.png') });
      await fallback.locator('[data-story-step="0"]').click();
      await fallback.waitForFunction(() =>
        document
          .querySelector('[data-registration-analysis-output]')
          ?.textContent.includes('A postmortem of one selected failure'),
      );
      assert.equal(await fallback.locator('[data-analysis-reference]').count(), 0);
    }
    if (plan.recipe === 'respiratory-v1') {
      await fallback.locator('[data-story-step="4"]').click();
      await fallback.waitForFunction(
        () => document.querySelector('[data-respiratory-reference]')?.textContent === 'hidden',
      );
      await fallback.locator('[data-story-step="5"]').click();
      await fallback.waitForFunction(() =>
        document
          .querySelector('[data-respiratory-output]')
          ?.textContent.includes('User visual judgment'),
      );
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-reference.png') });
      await fallback.locator('[data-story-step="0"]').click();
      await fallback.waitForFunction(() =>
        document
          .querySelector('[data-respiratory-output]')
          ?.textContent.includes('Eight source queries'),
      );
      assert.equal(await fallback.locator('[data-respiratory-reference]').count(), 0);
    }
    if (plan.recipe === 'anatomy-curation-v1') {
      assert.deepEqual(await fallback.locator('[data-curation-reference]').allTextContents(), [
        'hidden',
        'hidden',
      ]);
      await fallback.locator('[data-story-step="2"]').click();
      await fallback.waitForFunction(() =>
        document.querySelector('[data-curation-output]')?.textContent.includes('37.49'),
      );
      assert.deepEqual(await fallback.locator('[data-curation-reference]').allTextContents(), [
        'T9',
        'T10',
        'T11',
      ]);
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-preservation.png') });
      await fallback.locator('[data-story-step="0"]').click();
      await fallback.waitForFunction(
        () => document.querySelector('[data-curation-reference]')?.textContent === 'hidden',
      );
      assert.deepEqual(await fallback.locator('[data-curation-reference]').allTextContents(), [
        'hidden',
        'hidden',
      ]);
    }
    if (plan.recipe === 'mask-screen-v1') {
      await fallback.locator('[data-story-step="4"]').click();
      await fallback.waitForFunction(
        () => document.querySelectorAll('[data-screen-wrong="true"]').length === 2,
      );
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-exception.png') });
      await fallback.locator('[data-story-step="1"]').click();
      assert.ok(
        (await fallback.locator('[data-screen-reference]').allTextContents()).every(
          (t) => t === '—',
        ),
      );
      assert.equal(await fallback.locator('[data-screen-wrong="true"]').count(), 0);
    }

    if (plan.recipe === 'prototype-identity-v1') {
      assert.ok(
        (await fallback.locator('[data-prototype-label]').allTextContents()).every(
          (s) => s === 'unassigned',
        ),
      );
      await fallback.locator('[data-story-step="4"]').click();
      await fallback.waitForFunction(() =>
        [...document.querySelectorAll('[data-prototype-label]')].every(
          (e) => e.textContent !== 'unassigned',
        ),
      );
      await fallback.locator('[data-story-step="0"]').click();
      await fallback.waitForFunction(() =>
        [...document.querySelectorAll('[data-prototype-label]')].every(
          (e) => e.textContent === 'unassigned',
        ),
      );
    }
    if (plan.recipe === 'mixed-tissue-v1') {
      assert.equal(await fallback.locator('[data-mixed-reference]').count(), 0);
      assert.equal(await fallback.locator('[data-mixed-answer]').count(), 0);
      await fallback.locator('[data-story-step="5"]').click();
      await fallback.locator('[data-mixed-answer]').waitFor();
      await fallback.locator('[data-story-step="0"]').click();
      await fallback.locator('[data-mixed-pending]').waitFor();
      assert.equal(await fallback.locator('[data-mixed-reference]').count(), 0);
    }
    if (plan.recipe === 'anatomy-identity-v1') {
      assert.equal(
        await fallback.locator('.scene-player').getAttribute('data-committed-frame'),
        '0',
      );
      assert.ok(
        (await fallback.locator('[data-identity-label]').allTextContents()).every(
          (label) => label === 'unassigned',
        ),
      );
      await fallback.locator('[data-story-step="4"]').click();
      await fallback.waitForFunction(() =>
        [...document.querySelectorAll('[data-identity-label]')].every(
          (e) => e.textContent !== 'unassigned',
        ),
      );
      await fallback.locator('[data-story-step="0"]').click();
      await fallback.waitForFunction(() =>
        [...document.querySelectorAll('[data-identity-label]')].every(
          (e) => e.textContent === 'unassigned',
        ),
      );
    }
    if (!planar && plan.schema === 2)
      assert.equal(
        await fallback.locator('.scene-player').getAttribute('data-committed-frame'),
        String(plan.durationFrames - 1),
      );
    if (plan.schema === 2)
      assert.equal(await fallback.getByText('Route-conditioned image', { exact: true }).count(), 0);
    await fallback.locator('.scene-player').screenshot({ path: path.join(out, 'no-gpu.png') });
    row.fallback = true;
    await noGpu.close();
    report.stories.push(row);
    console.log('Reviewed matrix: ' + id);
  }
  if (!entryOnly) {
    await page.goto(
      pathToFileURL(explorer).href + '?lang=en#tb3-named-coronary/0/overview?view=repository',
    );
    await page.locator('.scene-player[data-rendered="true"]').waitFor();
    assert.equal(await page.evaluate(() => typeof window.__tb3ExplainerCapture), 'undefined');
    for (let pass = 0; pass < 3; pass++)
      for (const id of [
        'tb3-named-coronary',
        'wsi-hiesd-patches',
        'tb3-oblique-pose',
        'tb3-label-audit',
        'tb3-supplied-object-identity',
        'tb3-mixed-tissue-audit',
        'tb3-unlabeled-anatomy-prototype',
        'tb3-mask-reasoning-study',
        'tb3-anatomy-curation',
        'tb3-respiratory-correspondence',
        'tb3-registration-analysis',
        'tb3-clinical-cavity-adaptation',
      ]) {
        await page.evaluate((id) => {
          location.hash = `${id}/0/overview?view=repository`;
        }, id);
        await page.waitForFunction(
          (id) => document.querySelector('.task-detail')?.dataset.brief === id,
          id,
        );
        await page.locator('.scene-player[data-rendered="true"]').waitFor();
        const state = await page.locator('.scene-player').evaluate(
          (e, id) => ({
            id,
            renderer: e.dataset.surfaceRenderer,
            roots: e.dataset.nativeRoots,
            canvases: e.querySelectorAll('canvas').length,
          }),
          id,
        );
        assert.equal(state.canvases, 1);
        if (state.renderer === 'webgl') assert.equal(state.roots, '1');
        if (id === 'tb3-clinical-cavity-adaptation') {
          assert.equal(
            await page.locator('.scene-player').getAttribute('data-recipe'),
            'clinical-cavity-v1',
          );
          assert.equal(
            await page.locator('[data-cavity-output]').getAttribute('data-cavity-reference'),
            'hidden',
          );
          if (pass === 0) {
            await page.locator('[data-story-step="4"]').click();
            await page.waitForFunction(
              () =>
                document
                  .querySelector('[data-cavity-output]')
                  ?.getAttribute('data-cavity-reference') === 'revealed',
            );
            assert.match(await page.locator('[data-cavity-output]').innerText(), /45.31%/);
            const playerBox = await page.locator('.scene-player').boundingBox();
            const stageBox = await page.locator('.scene-stage').boundingBox();
            const outputBox = await page.locator('[data-cavity-output]').boundingBox();
            if (playerBox.width <= 900)
              assert.ok(
                outputBox.y >= stageBox.y + stageBox.height - 1,
                'Narrow Explorer must stack the cavity measurements beneath the stage',
              );

            await page
              .locator('.scene-player')
              .screenshot({ path: path.join(folder, 'explorer-clinical-reference.png') });
            await page.locator('.scene-reset').click();
            await page.waitForFunction(
              () =>
                document
                  .querySelector('[data-cavity-output]')
                  ?.getAttribute('data-cavity-reference') === 'hidden',
            );
          }
        }
        report.navigation.push(state);
      }
    await page.evaluate(() => {
      location.hash = 'tb3-named-landmarks/0/overview?view=repository';
    });
    await page.waitForFunction(
      () =>
        document.querySelector('.scene-player')?.getAttribute('data-recipe') ===
        'named-landmarks-v1',
    );
    assert.equal(await page.locator('[data-landmark-mark]').count(), 0);
    await page.locator('[data-story-step="5"]').click();
    await page.waitForFunction(
      () =>
        document
          .querySelector('[data-landmark-reference]')
          ?.getAttribute('data-landmark-reference') === 'visible',
    );
    assert.match(await page.locator('[data-landmark-output]').innerText(), /visible miss/);
    assert.equal(await page.locator('[data-landmark-mark="sol"]').count(), 0);
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(folder, 'integrated-landmarks.png') });
    await page.locator('.scene-reset').click();
    await page.waitForFunction(
      () =>
        document
          .querySelector('[data-landmark-reference]')
          ?.getAttribute('data-landmark-reference') === 'hidden',
    );
    report.navigation.push({ id: 'tb3-named-landmarks', revealAndReset: true });
    await page.evaluate(() => {
      location.hash = 'tb3-ct-organ-segmentation/0/overview?view=repository';
    });
    await page.waitForFunction(
      () => document.querySelector('.scene-player')?.getAttribute('data-recipe') === 'ct-organ-v1',
    );
    assert.equal(await page.locator('[data-ct-layer]').count(), 0);
    await page.locator('[data-story-step="6"]').click();
    await page.waitForFunction(
      () =>
        document.querySelector('[data-ct-reference]')?.getAttribute('data-ct-reference') ===
        'visible',
    );
    assert.equal(await page.locator('[data-ct-layer="reference"]').count(), 2);
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(folder, 'integrated-ct-organ.png') });
    await page.locator('.scene-reset').click();
    await page.waitForFunction(
      () =>
        document.querySelector('[data-ct-reference]')?.getAttribute('data-ct-reference') ===
        'hidden',
    );
    assert.equal(await page.locator('[data-ct-layer]').count(), 0);
    report.navigation.push({ id: 'tb3-ct-organ-segmentation', revealAndReset: true });
    await page.evaluate(() => {
      location.hash = 'tb3-dental-original/0/overview?view=repository';
    });
    await page.waitForFunction(
      () =>
        document.querySelector('.scene-player')?.getAttribute('data-recipe') ===
        'dental-original-v1',
    );
    assert.equal(await page.locator('[data-dental-layer]').count(), 0);
    await page.locator('[data-story-step="5"]').click();
    await page.waitForFunction(
      () =>
        document.querySelector('[data-dental-reference]')?.getAttribute('data-dental-reference') ===
        'visible',
    );
    assert.ok((await page.locator('[data-dental-layer="reference"]').count()) > 0);
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(folder, 'integrated-dental-original.png') });
    await page.locator('.scene-reset').click();
    await page.waitForFunction(
      () =>
        document.querySelector('[data-dental-reference]')?.getAttribute('data-dental-reference') ===
        'hidden',
    );
    assert.equal(await page.locator('[data-dental-layer]').count(), 0);
    report.navigation.push({ id: 'tb3-dental-original', revealAndReset: true });
    await page.evaluate(() => {
      location.hash = 'tb3-dental-v2/0/overview?view=repository';
    });
    await page.waitForFunction(
      () => document.querySelector('.scene-player')?.getAttribute('data-recipe') === 'dental-v2-v1',
    );
    assert.equal(await page.locator('[data-dental-v2-layer]').count(), 0);
    await page.locator('[data-story-step="9"]').click();
    await page.waitForFunction(
      () =>
        document
          .querySelector('[data-dental-v2-reference]')
          ?.getAttribute('data-dental-v2-reference') === 'visible',
    );
    assert.ok((await page.locator('[data-dental-v2-layer="reference"]').count()) > 0);
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(folder, 'integrated-dental-v2.png') });
    await page.locator('.scene-reset').click();
    await page.waitForFunction(
      () =>
        document
          .querySelector('[data-dental-v2-reference]')
          ?.getAttribute('data-dental-v2-reference') === 'hidden',
    );
    assert.equal(await page.locator('[data-dental-v2-layer]').count(), 0);
    report.navigation.push({ id: 'tb3-dental-v2', revealAndReset: true });

    await page.evaluate(() => {
      location.hash = 'tb3-dental-v3/0/overview?view=repository';
    });
    await page.waitForFunction(
      () => document.querySelector('.scene-player')?.getAttribute('data-recipe') === 'dental-v3-v1',
    );
    assert.equal(await page.locator('[data-dental-v3-layer]').count(), 0);
    await page.locator('[data-story-step="9"]').click();
    await page.waitForFunction(
      () =>
        document
          .querySelector('[data-dental-v3-reference]')
          ?.getAttribute('data-dental-v3-reference') === 'visible',
    );
    assert.ok((await page.locator('[data-dental-v3-layer="reference"]').count()) > 0);
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(folder, 'integrated-dental-v3.png') });
    await page.locator('.scene-reset').click();
    await page.waitForFunction(
      () =>
        document
          .querySelector('[data-dental-v3-reference]')
          ?.getAttribute('data-dental-v3-reference') === 'hidden',
    );
    assert.equal(await page.locator('[data-dental-v3-layer]').count(), 0);
    report.navigation.push({ id: 'tb3-dental-v3', revealAndReset: true });
    await page.evaluate(() => {
      location.hash = 'tb3-segmentation-calibration/0/overview?view=repository';
    });
    await page.waitForFunction(
      () =>
        document.querySelector('.scene-player')?.getAttribute('data-recipe') ===
        'segmentation-calibration-v1',
    );
    assert.equal(await page.locator('[data-calibration-layer]').count(), 0);
    await page.locator('[data-story-step="7"]').click();
    await page.waitForFunction(
      () =>
        document
          .querySelector('[data-calibration-reference]')
          ?.getAttribute('data-calibration-reference') === 'visible',
    );
    assert.ok((await page.locator('[data-calibration-layer="reference"]').count()) > 0);
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(folder, 'integrated-calibration.png') });
    await page.locator('.scene-reset').click();
    await page.waitForFunction(
      () =>
        document
          .querySelector('[data-calibration-reference]')
          ?.getAttribute('data-calibration-reference') === 'hidden',
    );
    assert.equal(await page.locator('[data-calibration-layer]').count(), 0);
    report.navigation.push({ id: 'tb3-segmentation-calibration', revealAndReset: true });
    await page.evaluate(() => {
      location.hash = 'tb3-aneurysm-localization/0/overview?view=repository';
    });
    await page.waitForFunction(
      () =>
        document.querySelector('.scene-player')?.getAttribute('data-recipe') ===
        'aneurysm-localization-v1',
    );
    assert.equal(await page.locator('[data-aneurysm-point], [data-aneurysm-private]').count(), 0);
    await page.locator('[data-story-step="7"]').click();
    await page.waitForFunction(
      () =>
        document
          .querySelector('[data-aneurysm-reference]')
          ?.getAttribute('data-aneurysm-reference') === 'visible',
    );
    assert.ok((await page.locator('[data-aneurysm-private]').count()) > 0);
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(folder, 'integrated-aneurysm.png') });
    await page.locator('.scene-reset').click();
    await page.waitForFunction(
      () =>
        document
          .querySelector('[data-aneurysm-reference]')
          ?.getAttribute('data-aneurysm-reference') === 'hidden',
    );
    assert.equal(await page.locator('[data-aneurysm-point], [data-aneurysm-private]').count(), 0);
    report.navigation.push({ id: 'tb3-aneurysm-localization', revealAndReset: true });

    await page.evaluate(() => {
      location.hash = 'tb3-localized-candidate-recognition/0/overview?view=repository';
    });
    await page.waitForFunction(
      () =>
        document.querySelector('.scene-player')?.getAttribute('data-recipe') === 'localized-ct-v1',
    );
    assert.equal(
      await page.locator('[data-localized-private], [data-localized-output]').count(),
      0,
    );
    assert.equal(await page.locator('[data-localized-point]').count(), 2);
    await page.locator('[data-story-step="8"]').click();
    await page.locator('[data-localized-private]').first().waitFor();
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(folder, 'integrated-localized-ct.png') });
    await page.locator('.scene-reset').click();
    await page.waitForFunction(
      () =>
        document
          .querySelector('[data-localized-reference]')
          ?.getAttribute('data-localized-reference') === 'hidden',
    );
    assert.equal(
      await page.locator('[data-localized-private], [data-localized-output]').count(),
      0,
    );
    report.navigation.push({ id: 'tb3-localized-candidate-recognition', revealAndReset: true });
    await page.evaluate(() => {
      location.hash = 'tb3-mri-importer/0/overview?view=repository';
    });
    await page.waitForFunction(
      () =>
        document.querySelector('.scene-player')?.getAttribute('data-recipe') === 'mri-importer-v1',
    );
    assert.equal(await page.locator('[data-mri-private], [data-mri-output]').count(), 0);
    await page.locator('[data-story-step="2"]').click();
    assert.equal(await page.locator('[data-mri-grid] article[data-selected="true"]').count(), 2);
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(folder, 'integrated-mri-importer.png') });
    await page.locator('[data-story-step="7"]').click();
    await page.locator('[data-mri-private]').first().waitFor();
    await page.locator('.scene-reset').click();
    await page.waitForFunction(
      () =>
        document.querySelector('[data-mri-reference]')?.getAttribute('data-mri-reference') ===
        'hidden',
    );
    assert.equal(await page.locator('[data-mri-private], [data-mri-output]').count(), 0);
    report.navigation.push({ id: 'tb3-mri-importer', revealAndReset: true });

    await page.evaluate(() => {
      location.hash = 'tb3-history-sourcing/0/overview?view=repository';
    });
    await page.waitForFunction(
      () =>
        document.querySelector('.scene-player')?.getAttribute('data-recipe') ===
        'history-sourcing-v1',
    );
    assert.equal(await page.locator('[data-history-private]').count(), 0);
    await page.locator('[data-story-step="1"]').click();
    await page.locator('[data-history-excerpt]').waitFor();
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(folder, 'integrated-history-sourcing.png') });
    await page.locator('[data-story-step="5"]').click();
    await page.locator('.scene-play').click();
    await page.locator('[data-history-private]').first().waitFor();
    await page.locator('.scene-play').click();
    await page.locator('.scene-reset').click();
    await page.waitForFunction(
      () =>
        document
          .querySelector('[data-history-reference]')
          ?.getAttribute('data-history-reference') === 'hidden',
    );
    assert.equal(await page.locator('[data-history-private]').count(), 0);
    report.navigation.push({ id: 'tb3-history-sourcing', revealAndReset: true });
    await page.evaluate(() => {
      location.hash = 'tb3-ct-context-inference/0/overview?view=repository';
    });
    await page.waitForFunction(
      () =>
        document.querySelector('.scene-player')?.getAttribute('data-recipe') === 'ct-context-v1',
    );
    assert.equal(await page.locator('[data-context-private]').count(), 0);
    await page.locator('[data-story-step="2"]').click();
    await page.locator('[data-context-point]').first().waitFor();
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(folder, 'integrated-ct-context.png') });
    await page.locator('[data-story-step="5"]').click();
    await page.locator('.scene-play').click();
    await page.locator('[data-context-private]').first().waitFor();
    await page.locator('.scene-play').click();
    await page.locator('.scene-reset').click();
    await page.waitForFunction(
      () =>
        document
          .querySelector('[data-context-reference]')
          ?.getAttribute('data-context-reference') === 'hidden',
    );
    assert.equal(await page.locator('[data-context-private]').count(), 0);
    report.navigation.push({ id: 'tb3-ct-context-inference', revealAndReset: true });
    await page.evaluate(() => {
      location.hash = 'abra/0/overview?view=repository';
    });
    await page.waitForFunction(
      () =>
        document.querySelector('.scene-player')?.getAttribute('data-recipe') ===
        'abra-annotation-v1',
    );
    assert.equal(
      await page.locator('[data-abra-reference],[data-abra-oracle],[data-abra-output]').count(),
      0,
    );
    await page.locator('[data-story-step="2"]').click();
    await page.locator('[data-abra-witness]').waitFor();
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(folder, 'integrated-abra.png') });
    await page.locator('[data-story-step="3"]').click();
    await page.locator('.scene-play').click();
    await page.locator('[data-abra-reference-info]').waitFor();
    await page.locator('.scene-play').click();
    await page.locator('.scene-reset').click();
    await page.locator('[data-abra-scene="inputs"]').waitFor();
    assert.equal(
      await page.locator('[data-abra-reference],[data-abra-oracle],[data-abra-output]').count(),
      0,
    );
    report.navigation.push({ id: 'abra', revealAndReset: true });
    await page.evaluate(() => {
      location.hash = 'bcer/0/overview?view=repository';
    });
    await page.waitForFunction(
      () =>
        document.querySelector('.scene-player')?.getAttribute('data-recipe') === 'bcer-workflow-v1',
    );
    await page.locator('[data-story-step="2"]').click();
    await page.locator('[data-bcer-witness]').first().waitFor();
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(folder, 'integrated-bcer.png') });
    await page.locator('[data-story-step="5"]').click();
    assert.equal(await page.locator('[data-bcer-metrics] tbody tr').count(), 5);
    await page.locator('.scene-reset').click();
    await page.locator('[data-bcer-scene="inputs"]').waitFor();
    report.navigation.push({ id: 'bcer', contractsAndReset: true });
    await page.evaluate(() => {
      location.hash = 'automedbench-tsg/0/overview?view=repository';
    });
    await page.waitForFunction(
      () =>
        document.querySelector('.scene-player')?.getAttribute('data-recipe') ===
        'automed-multiorgan-v1',
    );
    await page.locator('[data-story-step="2"]').click();
    await page.locator('[data-automed-remap]').waitFor();
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(folder, 'integrated-automed.png') });
    await page.locator('[data-story-step="6"]').click();
    assert.equal(await page.locator('[data-automed-fixtures] tbody tr').count(), 7);
    await page.locator('.scene-reset').click();
    assert.equal(await page.locator('[data-automed-reference]').count(), 0);
    report.navigation.push({ id: 'automedbench-tsg', remapAndReset: true });
    await page.evaluate(() => {
      location.hash = 'rexmle/0/overview?view=repository';
    });
    await page.waitForFunction(
      () =>
        document.querySelector('.scene-player')?.getAttribute('data-recipe') === 'rex-topcow-v1',
    );
    await page.locator('[data-story-step="5"]').click();
    assert.equal(await page.locator('[data-rex-fixtures] tbody tr').count(), 5);
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(folder, 'integrated-rex.png') });
    await page.locator('[data-story-step="4"]').click();
    assert.equal(await page.locator('[data-rex-reference],[data-rex-crop]').count(), 0);
    await page.locator('.scene-reset').click();
    await page.locator('[data-rex-scene="inputs"]').waitFor();
    assert.equal(await page.locator('[data-rex-reference],[data-rex-crop]').count(), 0);
    report.navigation.push({ id: 'rexmle', fixturesAndReset: true });
    await page.evaluate(() => {
      location.hash = 'imaging101-cars-spectroscopy/0/overview?view=repository';
    });
    await page.waitForFunction(
      () =>
        document.querySelector('.scene-player')?.getAttribute('data-recipe') ===
        'imaging101-cars-v1',
    );
    await page.locator('[data-story-step="3"]').click();
    await page.locator('[data-cars-residual]').waitFor({ state: 'attached' });
    await page.locator('[data-cars-scene="fit"] svg').waitFor();
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(folder, 'integrated-cars.png') });
    await page.locator('.scene-reset').click();
    await page.locator('[data-cars-scene="inputs"]').waitFor();
    assert.equal(await page.locator('[data-cars-reference],[data-cars-fit]').count(), 0);
    report.navigation.push({ id: 'imaging101-cars-spectroscopy', residualAndReset: true });
    await page.evaluate(() => {
      location.hash = 'imaging101-confocal-nlos-fk/0/overview?view=repository';
    });
    await page.waitForFunction(
      () =>
        document.querySelector('.scene-player')?.getAttribute('data-recipe') ===
        'imaging101-nlos-v1',
    );
    await page.locator('[data-story-step="2"]').click();
    await page.locator('[data-nlos-stolt-probe]').waitFor();
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(folder, 'integrated-nlos.png') });
    await page.locator('.scene-reset').click();
    await page.locator('[data-nlos-scene="inputs"]').waitFor();
    assert.equal(await page.locator('[data-nlos-reference]').count(), 0);
    report.navigation.push({ id: 'imaging101-confocal-nlos-fk', stoltAndReset: true });
    await page.evaluate(() => {
      location.hash = 'imaging101-conventional-ptychography/0/overview?view=repository';
    });
    await page.waitForFunction(
      () =>
        document.querySelector('.scene-player')?.getAttribute('data-recipe') ===
        'imaging101-ptychography-v1',
    );
    await page.locator('[data-story-step="2"]').click();
    await page.locator('[data-ptychography-scene="projection"]').waitFor();
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(folder, 'integrated-ptychography.png') });
    await page.locator('.scene-reset').click();
    await page.locator('[data-ptychography-scene="inputs"]').waitFor();
    assert.equal(await page.locator('[data-ptychography-reference]').count(), 0);
    report.navigation.push({
      id: 'imaging101-conventional-ptychography',
      projectionAndReset: true,
    });
    await page.evaluate(() => {
      location.hash = 'imaging101-ct-dual-energy/0/overview?view=repository';
    });
    await page.waitForFunction(
      () =>
        document.querySelector('.scene-player')?.getAttribute('data-recipe') ===
        'imaging101-dual-energy-v1',
    );
    await page.locator('[data-story-step="2"]').click();
    await page.locator('[data-dual-energy-scene="forward"]').waitFor();
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(folder, 'integrated-dual-energy.png') });
    await page.locator('.scene-reset').click();
    await page.locator('[data-dual-energy-scene="inputs"]').waitFor();
    assert.equal(await page.locator('[data-dual-energy-reference]').count(), 0);
    report.navigation.push({ id: 'imaging101-ct-dual-energy', forwardAndReset: true });
    await page.evaluate(() => {
      location.hash = 'imaging101-ct-fan-beam/0/overview?view=repository';
    });
    await page.waitForFunction(
      () =>
        document.querySelector('.scene-player')?.getAttribute('data-recipe') ===
        'imaging101-fan-beam-v1',
    );
    await page.locator('[data-story-step="1"]').click();
    await page.locator('[data-fan-beam-scene="geometry"]').waitFor();
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(folder, 'integrated-fan-beam.png') });
    await page.locator('.scene-reset').click();
    await page.locator('[data-fan-beam-scene="inputs"]').waitFor();
    assert.equal(await page.locator('[data-fan-beam-reference]').count(), 0);
    report.navigation.push({ id: 'imaging101-ct-fan-beam', geometryAndReset: true });
    await page.evaluate(() => {
      location.hash = 'imaging101-differentiable-deflectometry/0/overview?view=repository';
    });
    await page.waitForFunction(
      () =>
        document.querySelector('.scene-player')?.getAttribute('data-recipe') ===
        'imaging101-deflectometry-v1',
    );
    await page.locator('[data-story-step="3"]').click();
    await page.locator('[data-deflectometry-scene="geometry"]').waitFor();
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(folder, 'integrated-deflectometry.png') });
    await page.locator('.scene-reset').click();
    await page.locator('[data-deflectometry-scene="inputs"]').waitFor();
    assert.equal(await page.locator('[data-deflectometry-reference]').count(), 0);
    report.navigation.push({
      id: 'imaging101-differentiable-deflectometry',
      geometryAndReset: true,
    });
    await page.evaluate(() => {
      location.hash = 'imaging101-diffusion-mri-dti/0/overview?view=repository';
    });
    await page.waitForFunction(
      () =>
        document.querySelector('.scene-player')?.getAttribute('data-recipe') ===
        'imaging101-dti-v1',
    );
    await page.locator('[data-story-step="3"]').click();
    await page.locator('[data-dti-scene="tensor"]').waitFor();
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(folder, 'integrated-dti.png') });
    await page.locator('.scene-reset').click();
    await page.locator('[data-dti-scene="inputs"]').waitFor();
    assert.equal(await page.locator('[data-dti-reference]').count(), 0);
    report.navigation.push({ id: 'imaging101-diffusion-mri-dti', tensorAndReset: true });
    await page.evaluate(() => {
      location.hash = 'imaging101-eht-black-hole-uq/0/overview?view=repository';
    });
    await page.waitForFunction(
      () =>
        document.querySelector('.scene-player')?.getAttribute('data-recipe') ===
        'imaging101-eht-uq-v1',
    );
    await page.locator('[data-story-step="1"]').click();
    await page.locator('[data-eht-scene="closures"]').waitFor();
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(folder, 'integrated-eht-uq.png') });
    await page.locator('.scene-reset').click();
    await page.locator('[data-eht-scene="inputs"]').waitFor();
    assert.equal(await page.locator('[data-eht-reference]').count(), 0);
    report.navigation.push({ id: 'imaging101-eht-black-hole-uq', closureAndReset: true });
    await page.evaluate(() => {
      location.hash = 'imaging101-eht-black-hole-dynamic/0/overview?view=repository';
    });
    await page.waitForFunction(
      () =>
        document.querySelector('.scene-player')?.getAttribute('data-recipe') ===
        'imaging101-eht-dynamic-v1',
    );
    await page.locator('[data-story-step="2"]').click();
    await page.locator('[data-dynamic-scene="temporal"]').waitFor();
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(folder, 'integrated-eht-dynamic.png') });
    await page.locator('.scene-reset').click();
    await page.locator('[data-dynamic-scene="inputs"]').waitFor();
    assert.equal(await page.locator('[data-dynamic-reference]').count(), 0);
    report.navigation.push({ id: 'imaging101-eht-black-hole-dynamic', temporalAndReset: true });
    await page.evaluate(() => {
      location.hash =
        'imaging101-eht-black-hole-feature-extraction-dynamic/0/overview?view=repository';
    });
    await page.waitForFunction(
      () =>
        document.querySelector('.scene-player')?.getAttribute('data-recipe') ===
        'imaging101-eht-features-dynamic-v1',
    );
    await page.locator('[data-story-step="2"]').click();
    await page.locator('[data-features-scene="model"]').waitFor();
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(folder, 'integrated-eht-features-dynamic.png') });
    await page.locator('.scene-reset').click();
    await page.locator('[data-features-scene="inputs"]').waitFor();
    assert.equal(await page.locator('[data-features-reference]').count(), 0);
    report.navigation.push({
      id: 'imaging101-eht-black-hole-feature-extraction-dynamic',
      modelAndReset: true,
    });
    await page.evaluate(() => {
      location.hash = 'imaging101-eht-black-hole-original/0/overview?view=repository';
    });
    await page.waitForFunction(
      () =>
        document.querySelector('.scene-player')?.getAttribute('data-recipe') ===
        'imaging101-eht-original-v1',
    );
    await page.locator('[data-story-step="1"]').click();
    await page.locator('[data-original-scene="closures"]').waitFor();
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(folder, 'integrated-eht-original.png') });
    await page.locator('.scene-reset').click();
    await page.locator('[data-original-scene="inputs"]').waitFor();
    assert.equal(await page.locator('[data-original-reference]').count(), 0);
    report.navigation.push({ id: 'imaging101-eht-black-hole-original', closuresAndReset: true });
  }
  for (const entry of currentBatch.entries.filter((e) => cardiacRecipes.has(e.recipe))) {
    const plan = JSON.parse(fs.readFileSync(path.join(folder, entry.story_id, 'plan.json')));
    await page.setViewportSize({ width: 1280, height: 900 });
    await page.goto(
      pathToFileURL(explorer).href + `?lang=en#${entry.entry_id}/0/overview?view=repository`,
    );
    await page.waitForFunction(
      (recipe) => document.querySelector('.scene-player')?.getAttribute('data-recipe') === recipe,
      entry.recipe,
    );
    assert.equal(await page.evaluate(() => typeof window.__tb3ExplainerCapture), 'undefined');
    await reviewCardiacInteractions(page, plan, folder, `explorer-${entry.story_id}`);
    await page.setViewportSize({ width: 390, height: 844 });
    await reviewCardiacInteractions(page, plan, folder, `explorer-mobile-${entry.story_id}`);
    report.navigation.push({ id: entry.entry_id, chaptersAndReferenceReset: true, mobile: true });
  }
  await context.close();
  assert.deepEqual(report.errors, []);
  assert.deepEqual(report.remote_requests, []);
})
  .then(() => {
    fs.writeFileSync(
      path.join(folder, 'browser-matrix.json'),
      JSON.stringify(report, null, 2) + '\n',
    );
    console.log(
      'PASS: integrated locale/seek/mobile/no-GPU/navigation matrix; zero remote requests',
    );
  })
  .catch((error) => {
    report.errors.push(error.stack);
    fs.writeFileSync(
      path.join(folder, 'browser-matrix.json'),
      JSON.stringify(report, null, 2) + '\n',
    );
    console.error(error);
    process.exitCode = 1;
  });
