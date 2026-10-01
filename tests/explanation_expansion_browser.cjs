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
  'imaging101-usct-fwi-v1',
  'imaging-ultrasound-sos-v1',
  'imaging101-pnp-mri-reconstruction-v1',
  'imaging101-plane-wave-ultrasound-v1',
  'imaging101-photoacoustic-tomography-v1',
  'imaging101-pet-mlem-v1',
  'imaging101-varnet-v1',
  'imaging101-t2-mapping-v1',
  'imaging101-sense-v1',
  'imaging101-pnp-admm-v1',
  'imaging101-noncartesian-v1',
  'imaging101-wavelet-v1',
  'imaging-grappa-v1',
  'imaging-dynamic-mri-v1',
  'imaging-eit-v1',
  'imaging101-poisson-v1',
  'bcer-grappa-v1',
  'bcer-superres-v1',
  'bcer-denoise-v1',
  'automed-slake-v1',
  'automed-pathvqa-v1',
  'automed-vqa-rad-v1',
  'automed-omni-v1',
  'automed-kvasir-v1',
  'automed-medxpert-mm-v1',
  'automed-medframeqa-v1',
  'automed-pathology-caption-500-v1',
  'automed-pathology-caption-100-v1',
  'automed-mimic-report-v1',
  'automed-iu-xray-report-v1',
  'automed-chexpert-report-v1',
  'automed-skin-lesion-cls-v1',
  'automed-pcam-cls-v1',
  'automed-crc-cls-v1',
  'automed-pneumonia-cls-v1',
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
  if (plan.recipe === 'imaging101-usct-fwi-v1') return {scene:'data-imaging-usct-fwi-scene',reference:'[data-imaging-usct-fwi-reference-revealed]',referenceChannel:null,referencePolicy:'reader-reference-reveal',readerControlled:true,output:'[data-imaging-usct-fwi-output-schema]',aside:'[data-imaging-usct-fwi-output]'};
  if (plan.recipe === 'imaging-ultrasound-sos-v1')
    return {
      scene: 'data-sos-scene',
      reference: '[data-sos-source-truth], [data-sos-metric-boundary], [data-sos-format]',
      referenceChannel: null,
      referencePolicy: 'no-reference-assets',
      readerControlled: true,
      output: '[data-sos-output-schema]',
      aside: '[data-sos-output]',
    };
  if (plan.recipe === 'imaging101-pnp-mri-reconstruction-v1')
    return {
      scene: 'data-imaging-pnp-mri-scene',
      reference: '[data-imaging-pnp-mri-reference-revealed]',
      referenceChannel: null,
      readerControlled: true,
      output: '[data-imaging-pnp-mri-scene="output"] code',
      aside: '[data-imaging-pnp-mri-output]',
    };
  if (plan.recipe === 'imaging101-plane-wave-ultrasound-v1')
    return {
      scene: 'data-imaging-plane-wave-scene',
      reference: '[data-imaging-plane-wave-reference-revealed]',
      referenceChannel: null,
      readerControlled: true,
      output: '[data-imaging-plane-wave-scene="output"] code',
      aside: '[data-imaging-plane-wave-output]',
    };
  if (plan.recipe === 'imaging101-photoacoustic-tomography-v1')
    return {
      scene: 'data-imaging-photoacoustic-scene',
      reference: '[data-imaging-photoacoustic-reference-revealed]',
      referenceChannel: null,
      readerControlled: true,
      output: '[data-imaging-photoacoustic-scene="output"] code',
      aside: '[data-imaging-photoacoustic-output]',
    };
  if (plan.recipe === 'imaging101-pet-mlem-v1')
    return {
      scene: 'data-imaging-pet-mlem-scene',
      reference: '[data-imaging-pet-mlem-reference-revealed]',
      referenceChannel: null,
      readerControlled: true,
      output: '[data-imaging-pet-mlem-scene="output"] code',
      aside: '[data-imaging-pet-mlem-output]',
    };
  if (plan.recipe === 'imaging101-varnet-v1')
    return {
      scene: 'data-imaging-varnet-scene',
      reference: '[data-imaging-varnet-reference-revealed]',
      referenceChannel: null,
      readerControlled: true,
      output: '[data-imaging-varnet-scene="output"] code',
      aside: '[data-imaging-varnet-output]',
    };
  if (plan.recipe === 'imaging101-t2-mapping-v1')
    return {
      scene: 'data-imaging-t2-mapping-scene',
      reference: '[data-imaging-t2-mapping-reference-revealed]',
      referenceChannel: null,
      readerControlled: true,
      output: '[data-imaging-t2-mapping-scene="output"] code',
      aside: '[data-imaging-t2-mapping-output]',
    };
  if (plan.recipe === 'imaging101-sense-v1')
    return {
      scene: 'data-imaging-sense-scene',
      reference: '[data-imaging-sense-reference-revealed]',
      referenceChannel: null,
      readerControlled: true,
      output: '[data-imaging-sense-scene="output"] code',
      aside: '[data-imaging-sense-output]',
    };
  if (plan.recipe === 'imaging101-pnp-admm-v1')
    return {
      scene: 'data-imaging-pnp-admm-scene',
      reference: '[data-imaging-pnp-admm-reference-revealed]',
      referenceChannel: null,
      readerControlled: true,
      output: '[data-imaging-pnp-admm-scene="output"] code',
      aside: '[data-imaging-pnp-admm-output]',
    };

  if (plan.recipe === 'imaging101-noncartesian-v1')
    return {
      scene: 'data-imaging-noncartesian-scene',
      reference: '[data-imaging-noncartesian-reference-revealed]',
      referenceChannel: null,
      readerControlled: true,
      output: '[data-imaging-noncartesian-scene="output"] code',
      aside: '[data-imaging-noncartesian-output]',
    };
  if (plan.recipe === 'imaging101-wavelet-v1')
    return {
      scene: 'data-imaging-wavelet-scene',
      reference: '[data-imaging-wavelet-reference-revealed]',
      referenceChannel: null,
      readerControlled: true,
      output: '[data-imaging-wavelet-scene="output"] code',
      aside: '[data-imaging-wavelet-output]',
    };

  if (plan.recipe === 'imaging-grappa-v1')
    return {
      scene: 'data-grappa-scene',
      reference: '[data-grappa-full-target], [data-grappa-ssim]',
      referenceChannel: null,
      readerControlled: true,
      referencePolicy: 'no-reference-assets',
      output: '[data-grappa-output-schema]',
      aside: '[data-grappa-output]',
    };
  if (plan.recipe === 'imaging-dynamic-mri-v1')
    return {
      scene: 'data-dynamic-mri-scene',
      reference: '[data-dynamic-mri-source-series], [data-dynamic-mri-acquisition]',
      referenceChannel: null,
      readerControlled: true,
      referencePolicy: 'no-reference-assets',
      output: '[data-dynamic-mri-output-schema]',
      aside: '[data-dynamic-mri-output]',
    };
  if (plan.recipe === 'imaging-eit-v1')
    return {
      scene: 'data-eit-scene',
      reference: '[data-eit-source-truth], [data-eit-task-metric]',
      referenceChannel: null,
      referencePolicy: 'no-reference-assets',
      readerControlled: true,
      output: '[data-eit-output-schema]',
      aside: '[data-eit-output]',
    };
  if (plan.recipe === 'imaging101-poisson-v1')
    return {
      scene: 'data-imaging-poisson-scene',
      reference: '[data-imaging-poisson-reference-revealed]',
      referenceChannel: null,
      readerControlled: true,
      output: '[data-imaging-poisson-scene="output"] code',
      aside: '[data-imaging-poisson-output]',
    };
  if (plan.recipe === 'bcer-grappa-v1')
    return {
      scene: 'data-bcer-grappa-scene',
      reference: '[data-bcer-grappa-reference-revealed]',
      referenceChannel: null,
      readerControlled: true,
      output: '[data-bcer-grappa-output-schema]',
      aside: '[data-bcer-grappa-output]',
    };
  if (plan.recipe === 'bcer-superres-v1')
    return {
      scene: 'data-bcer-superres-scene',
      reference: '[data-bcer-superres-reference-revealed]',
      referenceChannel: null,
      readerControlled: true,
      output: '[data-bcer-superres-scene="output"] pre',
      aside: '[data-bcer-superres-output]',
    };
  if (plan.recipe === 'bcer-denoise-v1')
    return {
      scene: 'data-bcer-denoise-scene',
      reference: '[data-bcer-denoise-reference-revealed]',
      referenceChannel: null,
      readerControlled: true,
      output: '[data-bcer-denoise-output-schema]',
      aside: '[data-bcer-denoise-output]',
    };
  if (plan.recipe === 'automed-slake-v1')
    return {
      scene: 'data-slake-scene',
      reference: '[data-slake-public-annotation]',
      referenceChannel: null,
      readerControlled: true,
      output: '[data-slake-output-schema]',
      aside: '[data-slake-output]',
    };
  if (plan.recipe === 'automed-pathvqa-v1')
    return {
      scene: 'data-pathvqa-scene',
      reference: '[data-pathvqa-reference-revealed]',
      referenceChannel: null,
      readerControlled: true,
      output: '[data-pathvqa-scene="output"] pre',
      aside: '[data-pathvqa-output]',
    };
  if (plan.recipe === 'automed-vqa-rad-v1')
    return {
      scene: 'data-vqa-rad-scene',
      reference: '[data-vqa-rad-public-annotation]',
      referenceChannel: null,
      readerControlled: true,
      referencePolicy: 'no-reference-assets',
      output: '[data-vqa-rad-output-schema]',
      aside: '[data-vqa-rad-output]',
    };
  if (plan.recipe === 'automed-omni-v1')
    return {
      scene: 'data-omni-scene',
      reference: '[data-omni-reference-revealed]',
      referenceChannel: null,
      readerControlled: true,
      output: '[data-omni-scene="output"] pre',
      aside: '[data-omni-output]',
    };
  if (plan.recipe === 'automed-kvasir-v1')
    return {
      scene: 'data-kvasir-scene',
      reference: '[data-kvasir-reference-revealed]',
      referenceChannel: null,
      readerControlled: true,
      output: '[data-kvasir-scene="output"] pre',
      aside: '[data-kvasir-output]',
    };
  if (plan.recipe === 'automed-medxpert-mm-v1')
    return {
      scene: 'data-medxpert-scene',
      reference: '[data-medxpert-reference-revealed]',
      referenceChannel: null,
      readerControlled: true,
      output: '[data-medxpert-output-schema]',
      aside: '[data-medxpert-output]',
    };
  if (plan.recipe === 'automed-medframeqa-v1')
    return {
      scene: 'data-medframeqa-scene',
      reference: '[data-medframeqa-reference]',
      referenceChannel: null,
      output: '[data-medframeqa-output-schema]',
      aside: '[data-medframeqa-output]',
    };
  if (plan.recipe === 'automed-pathology-caption-500-v1')
    return {
      scene: 'data-pathology500-scene',
      reference: '[data-pathology500-reference-revealed]',
      referenceChannel: null,
      output: '[data-pathology500-output-schema]',
      aside: '[data-pathology500-output]',
    };
  if (plan.recipe === 'automed-pathology-caption-100-v1')
    return {
      scene: 'data-pathology100-scene',
      reference: '[data-pathology100-reference-revealed]',
      referenceChannel: null,
      output: '[data-pathology100-output-schema]',
      aside: '[data-pathology100-output]',
    };
  if (plan.recipe === 'automed-mimic-report-v1')
    return {
      scene: 'data-mimic-scene',
      reference: '[data-mimic-private-reference]',
      referenceChannel: null,
      output: '[data-mimic-output-schema]',
      aside: '[data-mimic-output]',
    };
  if (plan.recipe === 'automed-iu-xray-report-v1')
    return {
      scene: 'data-iu-report-scene',
      reference: '[data-iu-report-reference-revealed]',
      output: '[data-iu-report-output-schema]',
      aside: '[data-iu-report-output]',
    };
  if (plan.recipe === 'automed-chexpert-report-v1')
    return {
      scene: 'data-chexpert-scene',
      reference: '[data-chexpert-private-reference]',
      referenceChannel: null,
      output: '[data-chexpert-output-schema]',
      aside: '[data-chexpert-output]',
    };
  if (plan.recipe === 'automed-skin-lesion-cls-v1')
    return {
      scene: 'data-skin-lesion-scene',
      reference: '[data-skin-lesion-reference-revealed]',
      output: '[data-skin-lesion-fields]',
      aside: '[data-skin-lesion-output]',
    };
  if (plan.recipe === 'automed-pcam-cls-v1')
    return {
      scene: 'data-pcam-cls-scene',
      reference: '[data-pcam-cls-private-reference]',
      referenceChannel: null,
      output: '[data-pcam-cls-output-schema]',
      aside: '[data-pcam-cls-output]',
    };
  if (plan.recipe === 'automed-crc-cls-v1')
    return {
      scene: 'data-crc-cls-scene',
      reference: '[data-crc-cls-private-reference]',
      referenceChannel: null,
      output: '[data-crc-cls-output-schema]',
      aside: '[data-crc-cls-output]',
    };
  if (plan.recipe === 'automed-pneumonia-cls-v1')
    return {
      scene: 'data-pneumonia-scene',
      reference: '[data-pneumonia-reference-revealed]',
      output: '[data-pneumonia-output-schema]',
      aside: '[data-pneumonia-output]',
    };
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
    'imaging101-usct-fwi-v1': [/Numerical phantom observations; true speed, calibrated pressure and participant output absent./s,'https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/usct_FWI','data-imaging-usct-fwi-scene',false],
    'imaging-ultrasound-sos-v1': [
      /Native synthetic parallel-beam sums omit pixel-length scaling; calibrated seconds and ring paths are unestablished. Source truth is solver-visible; no participant reconstruction or score./s,
      'https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/ultrasound_sos_tomography',
      'data-sos-scene',
      false,
    ],
    'imaging101-pnp-mri-reconstruction-v1': [
      /Source image equals visible truth; acquired k-space and participant PnP result absent./s,
      'https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/pnp_mri_reconstruction',
      'data-imaging-pnp-mri-scene',
      false,
    ],
    'imaging101-plane-wave-ultrasound-v1': [
      /Phantom RF only; no participant B-mode. Baseline and generic binding unresolved./s,
      'https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/plane_wave_ultrasound',
      'data-imaging-plane-wave-scene',
      false,
    ],
    'imaging101-photoacoustic-tomography-v1': [
      /Synthetic pressure signals only; no tissue scan, participant reconstruction or score./s,
      'https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/photoacoustic_tomography',
      'data-imaging-photoacoustic-scene',
      false,
    ],
    'imaging101-pet-mlem-v1': [
      /Synthetic scaled-count sinogram only; no patient study, participant activity image or score./s,
      'https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/pet_mlem',
      'data-imaging-pet-mlem-scene',
      false,
    ],
    'imaging101-varnet-v1': [
      /Actual fastMRI-derived k-space; promised checkpoint absent, no participant reconstruction.*Local research use only/s,
      'https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/mri_varnet',
      'data-imaging-varnet-scene',
      false,
    ],
    'imaging101-t2-mapping-v1': [
      /Synthetic echoes only; generic reference may select M0 rather than T2.*No participant fit or clinical result/s,
      'https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/mri_t2_mapping',
      'data-imaging-t2-mapping-scene',
      false,
    ],
    'imaging101-sense-v1': [
      /Synthetic source only; loader requires absent full-kspace keys and main R4 differs from native R3.*No participant reconstruction/s,
      'https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/mri_sense',
      'data-imaging-sense-scene',
      false,
    ],
    'imaging101-pnp-admm-v1': [
      /No measured k-space or participant result; pinned metadata omits required noise_scale.*Actual masks only/s,
      'https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/mri_pnp_admm',
      'data-imaging-pnp-admm-scene',
      false,
    ],
    'imaging101-noncartesian-v1': [
      /Synthetic source-visible phantom; no participant reconstruction or calibrated FOV\/time.*README coordinate units differ from source NUFFT grid scaling/s,
      'https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/mri_noncartesian_cs',
      'data-imaging-noncartesian-scene',
      false,
    ],
    'imaging101-wavelet-v1': [
      /Released R4 knee k-space differs from README R8 synthetic case.*loader truth key also differs.*No participant output/s,
      'https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/mri_l1_wavelet',
      'data-imaging-wavelet-scene',
      false,
    ],
    'imaging-grappa-v1': [
      /Native full eight-coil k-space and phantom truth are solver-visible.*supplied rule.*not raw missing data.*No participant reconstruction or performance/s,
      'https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/mri_grappa',
      'data-grappa-scene',
      false,
    ],
    'imaging-dynamic-mri-v1': [
      /Native synthetic input; source truth is solver-visible and generator defaults differ.*No reconstruction or perfusion result/s,
      'https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/mri_dynamic_dce',
      'data-dynamic-mri-scene',
      false,
    ],
    'imaging-eit-v1': [
      /Native synthetic input; source truth is solver-visible and output\/reference scale unresolved.*No participant reconstruction/s,
      'https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/eit_conductivity_reconstruction',
      'data-eit-scene',
      false,
    ],
    'imaging101-poisson-v1': [
      /Matching 300-photon noisy input\/truth missing; retained raw data uses 1000.*Symbolic counts.*expectation only/s,
      'https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/ct_poisson_lowdose/data',
      'data-imaging-poisson-scene',
      false,
    ],
    'bcer-grappa-v1': [
      /Matching cardiac H5, reconstruction and clean GT absent; mask and modes are symbolic/s,
      'https://cmrxrecon.github.io/2025/Join-the-Challenge.html',
      'data-bcer-grappa-scene',
      false,
    ],
    'bcer-superres-v1': [
      /Representative PI-CAI helper only; no matched BCER resampled output or independent high-resolution truth/s,
      'https://zenodo.org/records/6624726',
      'data-bcer-superres-scene',
      false,
    ],
    'bcer-denoise-v1': [
      /Representative PI-CAI helper only; matched BM3D input\/output and clean GT absent/s,
      'https://zenodo.org/records/6624726',
      'data-bcer-denoise-scene',
      false,
    ],
    'automed-slake-v1': [
      /Public train example only; Full test selection\/private gold absent/s,
      'https://huggingface.co/datasets/BoKelvin/SLAKE',
      'data-slake-scene',
      false,
    ],
    'automed-pathvqa-v1': [
      /Public PathVQA train example only.*Full split\/private answer absent/s,
      'https://huggingface.co/datasets/flaviagiammarino/path-vqa',
      'data-pathvqa-scene',
      false,
    ],
    'automed-vqa-rad-v1': [
      /Public train example only.*exact Full case and private answer absent/s,
      'https://osf.io/89kps/',
      'data-vqa-rad-scene',
      false,
    ],
    'automed-omni-v1': [
      /Matching image and Full selection\/private gold absent.*per-source rights unresolved/s,
      'https://huggingface.co/datasets/foreverbeliever/OmniMedVQA',
      'data-omni-scene',
      false,
    ],
    'automed-kvasir-v1': [
      /Public raw example only.*Full IDs\/benchmark permission\/private answers absent/s,
      'https://huggingface.co/datasets/SimulaMet-HOST/Kvasir-VQA',
      'data-kvasir-scene',
      false,
    ],
    'automed-medxpert-mm-v1': [
      /Public dev example only; Full selection\/private gold absent/s,
      'https://huggingface.co/datasets/TsinghuaC3I/MedXpertQA',
      'data-medxpert-scene',
      false,
    ],
    'automed-medframeqa-v1': [
      /Two native public upstream test frames acquired.*exact Full question\/image\/option mapping absent.*No source gold\/reasoning, private reference, submitted answer or score/s,
      'https://huggingface.co/datasets/SuhaoYu1020/MedFrameQA',
      'data-medframeqa-scene',
      false,
    ],
    'automed-pathology-caption-500-v1': [
      /Native image\/caption and selected\s*500 IDs absent.*symbolic protocol/s,
      'https://huggingface.co/datasets/jamessyx/PathCap',
      'data-pathology500-scene',
      true,
    ],
    'automed-pathology-caption-100-v1': [
      /Native image\/caption and selected100 IDs absent.*symbolic protocol/s,
      'https://huggingface.co/datasets/jamessyx/PathCap',
      'data-pathology100-scene',
      true,
    ],
    'automed-mimic-report-v1': [
      /Credentialed MIMIC source images and exact Full study\/view manifest absent.*returned403.*No generated report, private reference or score/s,
      'https://physionet.org/content/mimic-cxr/2.1.0/',
      'data-mimic-scene',
      true,
    ],
    'automed-iu-xray-report-v1': [
      /Symbolic IU study.*matching images\/reports and Full staging absent/s,
      'https://openi.nlm.nih.gov/faq',
      'data-iu-report-scene',
      true,
    ],
    'automed-chexpert-report-v1': [
      /Exact Full frontal JPEG, staged case\/patient join, reference report and submitted report absent.*metadata GET200.*no access denial is inferred/s,
      'https://aimi.stanford.edu/datasets/chexpert-plus',
      'data-chexpert-scene',
      true,
    ],
    'automed-skin-lesion-cls-v1': [
      /Source HAM10000 example only.*Full case split, private labels and results absent/s,
      'https://api.isic-archive.com/collections/212/',
      'data-skin-lesion-scene',
      false,
    ],
    'automed-pcam-cls-v1': [
      /No matched 96x96 training row or frozen Full 100-case tile is recovered.*official annotated README collage.*private labels, checkpoint, predictions and scores absent/s,
      'https://github.com/basveeling/pcam',
      'data-pcam-cls-scene',
      false,
    ],
    'automed-crc-cls-v1': [
      /One official training patch is retained; frozen Full 100-case IDs, private labels, checkpoint, predictions and scores are absent/s,
      'https://zenodo.org/records/1214456',
      'data-crc-cls-scene',
      false,
    ],
    'automed-pneumonia-cls-v1': [
      /Training-source example only.*frozen Full evaluation IDs, test labels and results absent/s,
      'https://data.mendeley.com/datasets/rscbjbr9sj/2',
      'data-pneumonia-scene',
      false,
    ],
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
  await page.bringToFront();
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
  if (plan.recipe === 'automed-slake-v1') {
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    const beat = (name) => plan.beats.findIndex((b) => b.id === name);
    const scene = page.locator('[data-slake-scene]');
    const capture = async (name) =>
      page.locator('.scene-player').screenshot({ path: path.join(output, `${label}-${name}.png`) });
    const absent = async () =>
      assert.equal(await page.locator('[data-slake-public-annotation]').count(), 0);
    await page.locator('[data-story-step="0"]').click();
    const img = scene.locator('[data-slake-native]');
    const src = await img.getAttribute('src');
    assert.ok(src.startsWith('data:image/jpeg;base64,'), 'native JPEG embedded offline');
    assert.equal(
      crypto
        .createHash('sha256')
        .update(Buffer.from(src.split(',')[1], 'base64'))
        .digest('hex'),
      '4e591a1ace76cbf3e539069b73e848f9fde485879a24b95f212bbe0ac1d84609',
    );
    assert.equal(await img.evaluate((el) => el.naturalWidth), 256);
    assert.equal(await img.evaluate((el) => el.naturalHeight), 256);
    assert.match(await scene.innerText(), /What modality is used to take this image/);
    await absent();
    await page.locator(`[data-story-step="${beat('helper')}"]`).click();
    await absent();
    const reveal = scene.getByRole('button', {
      name: 'Reveal public training annotation',
      exact: true,
    });
    await reveal.click();
    assert.match(
      await page.locator('[data-slake-public-annotation]').innerText(),
      /MRI.*Public train annotation.*not Full gold.*model output/s,
    );
    await capture('annotation-revealed');
    await scene
      .getByRole('button', { name: 'Hide public training annotation', exact: true })
      .click();
    await absent();
    await reveal.click();
    await page.locator(`[data-story-step="${beat('bind')}"]`).click();
    await absent();
    await page.locator(`[data-story-step="${beat('helper')}"]`).click();
    await absent();
    await reveal.click();
    await page.locator('.scene-reset').click();
    await absent();
    await page.locator(`[data-story-step="${beat('helper')}"]`).click();
    await absent();
    await reveal.click();
    await page.locator('[data-story-step="0"]').click();
    await absent();
    await page.locator(`[data-story-step="${beat('helper')}"]`).click();
    await absent();
    await page.locator(`[data-story-step="${beat('bind')}"]`).click();
    const assistance = scene.getByRole('group', { name: 'SLAKE assistance' });
    await assistance.getByRole('button', { name: 'standard', exact: true }).click();
    assert.match(
      await page.locator('[data-slake-tier]').innerText(),
      /six candidates.*five.*PathVQA.*unresolved/s,
    );
    await capture('tier-standard');
    await page.locator('.scene-reset').click();
    await page.locator(`[data-story-step="${beat('bind')}"]`).click();
    assert.equal(
      await assistance
        .getByRole('button', { name: 'lite', exact: true })
        .getAttribute('aria-pressed'),
      'true',
    );
    for (let j = 0; j < 4; j++) {
      const b = plan.beats.find(
        (b) =>
          b.scene === 'operation' &&
          Math.abs(b.channels.progress[0] - j / 3) < 1e-8 &&
          b.channels.progress[0] === b.channels.progress[1],
      );
      await page.locator(`[data-slake-operation-step="${j}"]`).click();
      assert.equal(
        Number(await page.locator('.scene-player').getAttribute('data-frame')),
        b.startFrame,
      );
      assert.equal(
        await page.locator('[data-slake-currentstage]').getAttribute('data-slake-currentstage'),
        String(j),
      );
      await capture(`contract-${j}`);
      await absent();
    }
    await page.locator(`[data-story-step="${beat('output')}"]`).click();
    assert.equal(await page.locator('[data-slake-format]').count(), 0);
    await scene.getByRole('button', { name: 'Inspect format checks', exact: true }).click();
    assert.match(
      await page.locator('[data-slake-format]').innerText(),
      /Six keys.*No five-word.*nonfinite.*guard/s,
    );
    await capture('format-revealed');
    await page.locator(`[data-story-step="${beat('limits')}"]`).click();
    assert.equal(await page.locator('[data-slake-format]').count(), 0);
    const metrics = scene.getByRole('group', { name: 'SLAKE scoring boundary' });
    for (const m of ['accuracy', 'judge', 'format gate']) {
      await metrics.getByRole('button', { name: m, exact: true }).click();
      assert.ok((await page.locator('[data-slake-metric]').innerText()).length > 40);
      await capture(`metric-${m.replace(' ', '-')}`);
      await absent();
    }
    await page.locator('[data-story-step="0"]').click();
    await page.locator(`[data-story-step="${beat('limits')}"]`).click();
    assert.equal(
      await metrics
        .getByRole('button', { name: 'accuracy', exact: true })
        .getAttribute('aria-pressed'),
      'true',
    );
    await page.locator(`[data-story-step="${beat('output')}"]`).click();
    assert.equal(await page.locator('[data-slake-format]').count(), 0);
    assert.match(
      await scene.innerText(),
      /No answer was generated.*Private reference, score and participant output absent/s,
    );
    await page.locator('[data-story-step="0"]').click();
    await absent();
  }
  if (plan.recipe === 'automed-pathvqa-v1') {
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    const beat = (name) => plan.beats.findIndex((b) => b.id === name);
    const scene = page.locator('[data-pathvqa-scene]');
    const capture = async (name) =>
      page.locator('.scene-player').screenshot({ path: path.join(output, `${label}-${name}.png`) });
    const absent = async () =>
      assert.equal(await page.locator('[data-pathvqa-reference-revealed]').count(), 0);
    await page.locator('[data-story-step="0"]').click();
    const img = scene.locator('img');
    const src = await img.getAttribute('src');
    assert.ok(src.startsWith('data:image/jpeg;base64,'), 'native JPEG embedded offline');
    assert.equal(
      crypto
        .createHash('sha256')
        .update(Buffer.from(src.split(',')[1], 'base64'))
        .digest('hex'),
      '5dc180279e32d753a79e17dd8df06075b7867aeb8385dc8b15632ddef3a20e87',
    );
    assert.equal(await img.evaluate((el) => el.naturalWidth), 309);
    assert.equal(await img.evaluate((el) => el.naturalHeight), 272);
    assert.match(await scene.innerText(), /where are liver stem cells.*oval cells.*located/s);
    await absent();
    const expected = (j, o = 0) => {
      const b = plan.beats.find(
        (b) => b.scene === 'operation' && Math.abs(b.channels.progress[0] - j / 2) < 1e-6,
      );
      if (j !== 1) return b.startFrame;
      let best = 0,
        d = Infinity;
      for (let k = 0; k < b.frames; k++) {
        const u = k / b.frames,
          z = u * u * (3 - 2 * u),
          v = Math.abs(z - o / 2);
        if (v < d) {
          d = v;
          best = k;
        }
      }
      return b.startFrame + best;
    };
    await page.locator(`[data-story-step="${beat('bind')}"]`).click();
    for (let j = 0; j < 3; j++) {
      await page.locator(`[data-pathvqa-step="${j}"]`).click();
      assert.equal(
        Number(await page.locator('.scene-player').getAttribute('data-frame')),
        expected(j),
      );
      assert.equal(await scene.getAttribute('data-pathvqa-currentstep'), String(j));
      await capture(`contract-${j}`);
      await absent();
    }
    await page.locator('[data-pathvqa-step="0"]').click();
    await scene.getByRole('button', { name: 'standard', exact: true }).click();
    assert.match(
      await page.locator('[data-pathvqa-tier]').innerText(),
      /exactly six.*five.*open-ended/s,
    );
    await capture('tier-standard');
    await scene
      .getByRole('button', { name: 'Inspect public calibration rule', exact: true })
      .click();
    assert.match(
      await page.locator('#pathvqa-calibration-rule').innerText(),
      /first 15.*top.up.*not implement.*≥10.*gold optional.*eight-word/s,
    );
    await capture('calibration-revealed');
    await page.locator('.scene-reset').click();
    await page.locator(`[data-story-step="${beat('bind')}"]`).click();
    assert.equal(
      await scene.getByRole('button', { name: 'lite', exact: true }).getAttribute('aria-pressed'),
      'true',
    );
    assert.equal(await page.locator('#pathvqa-calibration-rule').count(), 0);
    await page.locator('[data-pathvqa-step="1"]').click();
    for (let o = 0; o < 3; o++) {
      await page.locator(`[data-pathvqa-branch="${o}"]`).click();
      assert.equal(
        Number(await page.locator('.scene-player').getAttribute('data-frame')),
        expected(1, o),
      );
      assert.equal(
        await page.locator(`[data-pathvqa-branch="${o}"]`).getAttribute('aria-pressed'),
        'true',
      );
      await capture(`branch-${o}`);
      await absent();
    }
    await page.locator(`[data-story-step="${beat('output')}"]`).click();
    assert.match(await scene.innerText(), /All actual fields null.*no source train answer copied/s);
    assert.equal(await page.locator('#pathvqa-format-rule').count(), 0);
    await scene.getByRole('button', { name: 'Inspect format boundary', exact: true }).click();
    assert.match(
      await page.locator('#pathvqa-format-rule').innerText(),
      /Six required keys.*finite-runtime.*≥50%.*all-ID denominator/s,
    );
    await capture('format-revealed');
    await page.locator(`[data-story-step="${beat('reference')}"]`).click();
    await absent();
    assert.equal(await page.locator('#pathvqa-format-rule').count(), 0);
    const reveal = scene.getByRole('button', {
      name: 'Reveal public train annotation',
      exact: true,
    });
    await reveal.click();
    assert.match(
      await page.locator('[data-pathvqa-reference-revealed]').innerText(),
      /in the canals of hering.*Not model evidence.*independent clinical/s,
    );
    await capture('reference-revealed');
    await page.locator(`[data-story-step="${beat('limits')}"]`).click();
    await absent();
    await page.locator(`[data-story-step="${beat('reference')}"]`).click();
    await absent();
    await reveal.click();
    await page.locator('.scene-reset').click();
    await absent();
    await page.locator(`[data-story-step="${beat('reference')}"]`).click();
    await absent();
    await reveal.click();
    await page.locator('[data-story-step="0"]').click();
    await absent();
    await page.locator(`[data-story-step="${beat('reference')}"]`).click();
    await absent();
    await page.locator('[data-story-step="0"]').click();
    await absent();
  }
  if (plan.recipe === 'imaging101-varnet-v1') {
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    const scene = page.locator('[data-imaging-varnet-scene]');
    const absent = async () =>
      assert.equal(await scene.locator('[data-imaging-varnet-reference-revealed]').count(), 0);
    const capture = async (n) =>
      page.locator('.scene-player').screenshot({ path: path.join(output, `${label}-${n}.png`) });
    const advance = async (f) => {
      await page.bringToFront();
      await page.locator('.scene-play').click();
      await page.locator('.scene-stage').scrollIntoViewIfNeeded();
      await page.waitForFunction(
        (x) => Number(document.querySelector('.scene-player').getAttribute('data-frame')) > x,
        f + 4,
      );
      await page.locator('.scene-play').click();
    };
    const image = async (m) => {
      const img = scene.locator('img');
      assert.equal(await img.count(), 1);
      const d = await img.evaluate((e) => ({
        src: e.src,
        w: e.naturalWidth,
        h: e.naturalHeight,
        alt: e.alt,
      }));
      assert.equal(d.w, 92);
      assert.equal(d.h, 160);
      assert.match(
        d.alt,
        new RegExp(
          `Native k-space magnitude samples, Coil ${[0, 7, 14][m]}; no spatial reconstruction`,
        ),
      );
      assert.ok(d.src.startsWith('data:image/png;base64,'));
      assert.equal(
        sha(Buffer.from(d.src.split(',')[1], 'base64')),
        sha(
          fs.readFileSync(
            `presentation/task-explorer/imaging101-mri-varnet/kspace-${[0, 7, 14][m]}.png`,
          ),
        ),
      );
      assert.match(
        await scene.locator('figcaption').first().innerText(),
        /Gray: log-display \|k\|.*fixed\s*\.006 ceiling; phase lost.*Every fourth row\/column.*160\s*×\s*92\s*cells/s,
      );
    };
    const mask = async () => {
      const rows = await scene.locator('svg rect').evaluateAll((es) =>
        es.map((e) => ({
          x: Number(e.getAttribute('x')),
          w: Number(e.getAttribute('width')),
          h: Number(e.getAttribute('height')),
          fill: e.getAttribute('fill'),
        })),
      );
      assert.equal(rows.length, 368);
      rows.forEach((v, j) =>
        assert.deepEqual(v, {
          x: j,
          w: 1,
          h: 8,
          fill: j % 4 === 2 || (j >= 170 && j < 199) ? '#57d1cc' : '#122939',
        }),
      );
      assert.match(
        await scene.locator('figcaption').last().innerText(),
        /Teal: saved sampled columns; dark: missing.*113\s*\/\s*368; ACS\s*29/s,
      );
    };
    await page.locator('[data-story-step="0"]').click();
    await image(0);
    await absent();
    assert.match(
      await scene.innerText(),
      /1\s*slice.*15\s*coils.*640\s*×\s*368 complex grid.*fastMRI-derived source.*CORPD_FBK.*Frequency-array indices.*no anatomical or clinical image.*Promised checkpoint absent.*local research only.*No FFT.*model forward or reconstruction/is,
    );
    await capture('native-input');
    await advance(0);
    await page.locator('[data-story-step="0"]').click();
    const steps = ['Complex encoding', 'Native samples + mask', 'Model boundary'],
      branches = ['Coil 0', 'Coil 7', 'Coil 14'],
      bf = [336, 419, 503];
    for (let i = 0; i < 3; i++)
      for (let m = 0; m < 3; m++) {
        await page.locator('[data-story-step="2"]').click();
        await scene.getByRole('button', { name: branches[m], exact: true }).click();
        assert.equal(Number(await page.locator('.scene-player').getAttribute('data-frame')), bf[m]);
        await image(m);
        await mask();
        await scene.getByRole('button', { name: steps[i], exact: true }).click();
        assert.equal(
          Number(await page.locator('.scene-player').getAttribute('data-frame')),
          i === 1 ? bf[m] : [168, 0, 504][i],
        );
        assert.equal(await scene.getAttribute('data-imaging-varnet-operation-step'), String(i));
        assert.equal(
          await scene
            .getByRole('button', { name: steps[i], exact: true })
            .getAttribute('aria-pressed'),
          'true',
        );
        const text = await scene.innerText();
        if (i === 0) {
          assert.match(
            text,
            /y_c=M F\(S_c x\).*centered orthonormal FFT.*Complex-pair model input.*1\s*×\s*15\s*×\s*640\s*×\s*368\s*×\s*2.*Sensitivity maps estimated by external model.*not supplied or computed here.*Authored hard-consistency example\s*\[3,4\]→\[2,4\].*teaching arithmetic.*not VarNet's learned\/soft update/is,
          );
          assert.equal(await scene.locator('img,canvas,image').count(), 0);
        } else if (i === 1) {
          await image(m);
          await mask();
          assert.match(
            text,
            /Equispaced columns with random offset.*Saved offset\s*2.*nominal R4 plus\s*29\s*ACS lines.*effective\s*368\s*\/\s*113≈3\.257.*not a Bernoulli mask or a fresh model tensor/is,
          );
        } else {
          assert.match(
            text,
            /12-cascade constructor; checkpoint absent.*Regularizer pools\s*4\s*\/\s*channels\s*18.*sensitivity pools\s*4\s*\/\s*channels\s*8.*External fastMRI lower bound.*not pin exact blocks or calibration schedule.*CPU\s*\/\s*eval\s*\/\s*no_grad.*no forward.*320\s*×\s*320.*\(160,24\).*no resize or image computed/is,
          );
          assert.equal(await scene.locator('img,canvas,image').count(), 0);
        }
        await absent();
        await capture(`contract-${i}-${m}`);
      }
    await page.locator('[data-story-step="2"]').click();
    await advance(336);
    await page.locator('[data-story-step="2"]').click();
    await image(0);
    await absent();
    const oi = plan.beats.findIndex((b) => b.scene === 'output');
    await page.locator(`[data-story-step="${oi}"]`).click();
    assert.match(
      await scene.innerText(),
      /reconstruction\.npy.*320\s*×\s*320 magnitude.*Participant image\s*\/\s*score empty.*Saved source VarNet output.*no recovered checkpoint or new execution lineage/is,
    );
    assert.equal(await scene.locator('img,canvas,image').count(), 0);
    await absent();
    await capture('empty-output');
    const ri = plan.beats.findIndex((b) => b.scene === 'reference');
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    const reveal = () => scene.getByRole('button', { name: 'Reveal source rules', exact: true });
    await reveal().click();
    assert.equal(
      await scene
        .getByRole('button', { name: 'Hide source rules', exact: true })
        .getAttribute('aria-expanded'),
      'true',
    );
    assert.match(
      await scene.locator('[data-imaging-varnet-reference-revealed]').innerText(),
      /Source RSS image is solver-visible.*no private clinical truth.*No source or participant image shown.*Generic magnitude comparison.*102,?400\s*pixels.*no scale normalization.*Phase information is lost.*NCC differs from range error.*windowed SSIM differs from generic global SSIM.*source averages lack pass boundary fields.*Saved metrics are not current model evidence/is,
    );
    assert.equal(await scene.locator('img,canvas,image').count(), 0);
    await capture('rules-revealed');
    await scene.getByRole('button', { name: 'Hide source rules', exact: true }).click();
    await absent();
    await advance(plan.beats[ri].startFrame);
    await reveal().click();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    await reveal().click();
    await page.locator('.scene-reset').click();
    await absent();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    await reveal().click();
    await page.locator('[data-story-step="1"]').click();
    await absent();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    const li = plan.beats.findIndex((b) => b.scene === 'limits');
    await page.locator(`[data-story-step="${li}"]`).click();
    assert.match(
      await scene.innerText(),
      /Pinned data tree lacks varnet_knee_state_dict\.pt.*Saved source output cannot establish checkpoint replay or participant\/model outcome.*Exact external fastMRI runtime implementation and source-case identity not established.*retain local-use rights boundary.*Native k-space previews are input evidence only.*No reconstructed finding.*learned outcome.*performance or clinical inference/is,
    );
    await capture('limits-contract');
    await absent();
    await page.locator('.scene-reset').click();
    await absent();
  }

  if (plan.recipe === 'imaging101-pet-mlem-v1') {
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    const scene = page.locator('[data-imaging-pet-mlem-scene]');
    const absent = async () =>
      assert.equal(await scene.locator('[data-imaging-pet-mlem-reference-revealed]').count(), 0);
    const capture = async (n) =>
      page.locator('.scene-player').screenshot({ path: path.join(output, `${label}-${n}.png`) });
    const advance = async (f) => {
      await page.bringToFront();
      await page.locator('.scene-play').click();
      await page.locator('.scene-stage').scrollIntoViewIfNeeded();
      await page.waitForFunction(
        (x) => Number(document.querySelector('.scene-player').getAttribute('data-frame')) > x,
        f + 4,
      );
      await page.locator('.scene-play').click();
    };
    const image = async () => {
      const img = scene.locator('img');
      assert.equal(await img.count(), 1);
      const d = await img.evaluate((e) => ({
        src: e.src,
        w: e.naturalWidth,
        h: e.naturalHeight,
        alt: e.alt,
      }));
      assert.equal(d.w, 120);
      assert.equal(d.h, 128);
      assert.match(
        d.alt,
        /Native synthetic sinogram: radial rows, angle columns; grayscale scaled counts, no activity reconstruction/,
      );
      assert.ok(d.src.startsWith('data:image/png;base64,'));
      assert.equal(
        sha(Buffer.from(d.src.split(',')[1], 'base64')),
        sha(fs.readFileSync('presentation/task-explorer/imaging101-pet-mlem/sinogram.png')),
      );
      assert.match(
        await scene.locator('figcaption').innerText(),
        /Black\s*0\s*→\s*white\s*220.*y=C\s*\/\s*1000.*128 radial rows\s*×\s*120 angle columns.*0°…178\.5°/s,
      );
    };
    const source = JSON.parse(
      fs.readFileSync('presentation/task-explorer/imaging101-pet-mlem/source.json', 'utf8'),
    ).native_profiles;
    const profile = async (m) => {
      const svg = scene.locator('svg');
      assert.equal(await svg.count(), 1);
      assert.match(
        await svg.getAttribute('aria-label'),
        new RegExp(
          `Native scaled-count radial profile at ${[0, 90, 178.5][m]} degrees; no reconstructed activity`,
        ),
      );
      const poly = svg.locator('polyline');
      assert.equal(await poly.getAttribute('stroke'), '#57d1cc');
      const points = (await poly.getAttribute('points'))
        .split(' ')
        .map((s) => s.split(',').map(Number));
      assert.equal(points.length, 128);
      points.forEach((p, j) => {
        assert.ok(Math.abs(p[0] - (14 + (j * 244) / 127)) < 1e-9);
        assert.ok(Math.abs(p[1] - (148 - (source.values[m][j] * 140) / 220)) < 1e-9);
      });
      const line = svg.locator('line');
      assert.equal(await line.getAttribute('stroke'), '#b2c2ce');
      assert.ok(
        Math.abs(Number(await line.getAttribute('y1')) - (148 - (source.background * 140) / 220)) <
          1e-9,
      );
      assert.match(
        await scene.locator('figcaption').innerText(),
        /Teal: native observed y; gray: r=10\.928.*128 radial bins/s,
      );
      assert.equal(await scene.locator('img,canvas,image').count(), 0);
    };
    await page.locator('[data-story-step="0"]').click();
    await image();
    await absent();
    assert.match(
      await scene.innerText(),
      /15,?360 measurement bins.*relative units.*Poisson draws divided by\s*1,?000.*Background is additive in the mean.*no patient scan or calibrated uptake.*No projection.*backprojection.*reconstruction or score computed/is,
    );
    await capture('native-input');
    await advance(0);
    await page.locator('[data-story-step="0"]').click();
    const steps = ['Poisson + background', 'Native profiles', 'MLEM + OSEM'],
      branches = ['Angle 0°', 'Angle 90°', 'Angle 178.5°'],
      bf = [336, 419, 503];
    for (let i = 0; i < 3; i++)
      for (let m = 0; m < 3; m++) {
        await page.locator('[data-story-step="2"]').click();
        await scene.getByRole('button', { name: branches[m], exact: true }).click();
        assert.equal(Number(await page.locator('.scene-player').getAttribute('data-frame')), bf[m]);
        await profile(m);
        await scene.getByRole('button', { name: steps[i], exact: true }).click();
        assert.equal(
          Number(await page.locator('.scene-player').getAttribute('data-frame')),
          i === 1 ? bf[m] : [168, 0, 504][i],
        );
        assert.equal(await scene.getAttribute('data-imaging-pet-mlem-operation-step'), String(i));
        assert.equal(
          await scene
            .getByRole('button', { name: steps[i], exact: true })
            .getAttribute('aria-pressed'),
          'true',
        );
        const text = await scene.innerText();
        if (i === 0) {
          assert.match(
            text,
            /C\s*~\s*Poisson\(1000\s*×\s*\(A x\s*\+\s*r\)\).*y=C\s*\/\s*1000.*Uniform source background.*10\.928.*not subtracted before the fit.*No attenuation.*separate scatter or detector normalization.*Authored A=3.*x=2.*r=2.*y=8.*x_new=2.*scalar rule only.*no native activity image/is,
          );
          assert.equal(await scene.locator('img,canvas,image,svg').count(), 0);
        } else if (i === 1) {
          await profile(m);
          assert.match(
            text,
            /Background and observations share one scale.*Angles\s*0°\s*\/\s*90°\s*\/\s*178\.5°.*native values only.*Some bins can be below background.*no clipping\/subtraction here.*Display choice never changes acquisition.*draws noise or runs a solver.*Radial index is not mm/is,
          );
        } else {
          assert.match(
            text,
            /x←x\s*\/\s*\(B1\)\s*×\s*B\(y\s*\/\s*\(Ax\+r\)\).*MLEM:\s*50 updates.*OSEM:\s*10 cycles\s*×\s*6 interleaved subsets\s*=\s*60 updates.*20 angles per subset.*B is unfiltered iradon.*not verified exact transpose or FBP.*Floors\s*1e−10.*no explicit prior.*MLEM history is pre-update.*OSEM post-cycle.*no convergence claim/is,
          );
          assert.equal(await scene.locator('img,canvas,image,svg').count(), 0);
        }
        await absent();
        await capture(`contract-${i}-${m}`);
      }
    await page.locator('[data-story-step="2"]').click();
    await advance(336);
    await page.locator('[data-story-step="2"]').click();
    await profile(0);
    await absent();
    const oi = plan.beats.findIndex((b) => b.scene === 'output');
    await page.locator(`[data-story-step="${oi}"]`).click();
    assert.match(
      await scene.innerText(),
      /reconstruction\.npy.*128\s*×\s*128 relative activity.*Participant image\s*\/\s*score empty.*Saved source MLEM\/OSEM artifacts are separate from fresh execution or clinical uptake/is,
    );
    assert.equal(await scene.locator('img,canvas,image,svg').count(), 0);
    await absent();
    await capture('empty-output');
    const ri = plan.beats.findIndex((b) => b.scene === 'reference');
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    const reveal = () => scene.getByRole('button', { name: 'Reveal source rules', exact: true });
    await reveal().click();
    assert.equal(
      await scene
        .getByRole('button', { name: 'Hide source rules', exact: true })
        .getAttribute('aria-expanded'),
      'true',
    );
    assert.match(
      await scene.locator('[data-imaging-pet-mlem-reference-revealed]').innerText(),
      /Source mask:\s*7,?379 positive pixels.*range\s*5\.5.*Generic:\s*16,?384 pixels.*range\s*6.*no source mask or scale normalization.*Source baseline thresholds select best NCC and NRMSE independently.*matched live comparison unverified.*No activity or truth image.*likelihood run.*uptake value or score displayed.*Exit\s*\/\s*backward\s*\/\s*reset covers rules/is,
    );
    assert.equal(await scene.locator('img,canvas,image,svg').count(), 0);
    await capture('rules-revealed');
    await scene.getByRole('button', { name: 'Hide source rules', exact: true }).click();
    await absent();
    await advance(plan.beats[ri].startFrame);
    await reveal().click();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    await reveal().click();
    await page.locator('.scene-reset').click();
    await absent();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    await reveal().click();
    await page.locator('[data-story-step="1"]').click();
    await absent();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    const li = plan.beats.findIndex((b) => b.scene === 'limits');
    await page.locator(`[data-story-step="${li}"]`).click();
    assert.match(
      await scene.innerText(),
      /Native synthetic sinogram\/background retained.*no participant reconstruction or calibrated patient uptake.*Simplified Radon model lacks attenuation.*detector normalization.*separate scatter.*timing and scanner-unit calibration.*exact discrete adjoint\/runtime not established.*Native measurements are input evidence only.*No reconstructed finding.*likelihood monotonicity.*clinical uptake or numerical performance/is,
    );
    await capture('limits-contract');
    await absent();
    await page.locator('.scene-reset').click();
    await absent();
  }

  if (plan.recipe === 'imaging101-photoacoustic-tomography-v1') {
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    const scene = page.locator('[data-imaging-photoacoustic-scene]');
    const absent = async () =>
      assert.equal(
        await scene.locator('[data-imaging-photoacoustic-reference-revealed]').count(),
        0,
      );
    const capture = async (n) =>
      page.locator('.scene-player').screenshot({ path: path.join(output, `${label}-${n}.png`) });
    const advance = async (f) => {
      await page.bringToFront();
      await page.locator('.scene-play').click();
      await page.locator('.scene-stage').scrollIntoViewIfNeeded();
      await page.waitForFunction(
        (x) => Number(document.querySelector('.scene-player').getAttribute('data-frame')) > x,
        f + 4,
      );
      await page.locator('.scene-play').click();
    };
    const image = async () => {
      const img = scene.locator('img');
      assert.equal(await img.count(), 1);
      const d = await img.evaluate((e) => ({
        src: e.src,
        w: e.naturalWidth,
        h: e.naturalHeight,
        alt: e.alt,
      }));
      assert.equal(d.w, 1301);
      assert.equal(d.h, 31);
      assert.match(
        d.alt,
        /Native center-y pressure slice: time columns, detector-x rows; red positive, blue negative, white zero/,
      );
      assert.ok(d.src.startsWith('data:image/png;base64,'));
      assert.equal(
        sha(Buffer.from(d.src.split(',')[1], 'base64')),
        sha(
          fs.readFileSync(
            'presentation/task-explorer/imaging101-photoacoustic-tomography/signals.png',
          ),
        ),
      );
      assert.match(
        await scene.locator('figcaption').innerText(),
        /31 detector-x rows\s*×\s*1,?301 time columns.*center-y index\s*15.*Blue\s*\/\s*red: negative\s*\/\s*positive pressure.*fixed\s*±0\.1\s*a\.u\..*white zero/s,
      );
    };
    const source = JSON.parse(
      fs.readFileSync(
        'presentation/task-explorer/imaging101-photoacoustic-tomography/source.json',
        'utf8',
      ),
    ).native_profiles;
    const branches = ['Center (15, 15)', 'Edge x (0, 15)', 'Edge y (15, 0)'];
    const trace = async (m) => {
      const svg = scene.locator('svg');
      assert.equal(await svg.count(), 1);
      assert.equal(
        await svg.getAttribute('aria-label'),
        `Native pressure time trace detector ${branches[m]}; no reconstructed image`,
      );
      const poly = svg.locator('polyline');
      assert.equal(await poly.getAttribute('stroke'), '#57d1cc');
      const points = (await poly.getAttribute('points'))
        .split(' ')
        .map((s) => s.split(',').map(Number));
      assert.equal(points.length, 1301);
      points.forEach((p, j) => {
        assert.ok(Math.abs(p[0] - (14 + (j * 244) / 1300)) < 1e-9);
        assert.ok(Math.abs(p[1] - (78 - source.values[m][j] * 650)) < 1e-9);
      });
      const line = svg.locator('line');
      assert.equal(await line.getAttribute('stroke'), '#b2c2ce');
      assert.equal(Number(await line.getAttribute('y1')), 78);
      assert.deepEqual(
        (await svg.locator('text').allTextContents()).map((x) => x.trim()),
        ['signed pressure (a.u.)', 'time 0–65 µs →'],
      );
      assert.match(
        await scene.locator('figcaption').innerText(),
        /Teal: all\s*1,?301 source samples; gray: zero.*Detector/s,
      );
      assert.equal(await scene.locator('img,canvas,image').count(), 0);
    };
    await page.locator('[data-story-step="0"]').click();
    await image();
    await absent();
    assert.match(
      await scene.innerText(),
      /961 detectors.*20 MHz.*65\s*µs.*Native signed signals from four simulated spheres.*no tissue scan or calibrated pressure/is,
    );
    await capture('native-input');
    await advance(0);
    await page.locator('[data-story-step="0"]').click();
    const steps = ['Geometry + time', 'Native traces', 'Backprojection rules'],
      bf = [336, 419, 503];
    for (let i = 0; i < 3; i++)
      for (let m = 0; m < 3; m++) {
        await page.locator('[data-story-step="2"]').click();
        await scene.getByRole('button', { name: branches[m], exact: true }).click();
        assert.equal(Number(await page.locator('.scene-player').getAttribute('data-frame')), bf[m]);
        await trace(m);
        await scene.getByRole('button', { name: steps[i], exact: true }).click();
        assert.equal(
          Number(await page.locator('.scene-player').getAttribute('data-frame')),
          i === 1 ? bf[m] : [168, 0, 504][i],
        );
        assert.equal(
          await scene.getAttribute('data-imaging-photoacoustic-operation-step'),
          String(i),
        );
        assert.equal(
          await scene
            .getByRole('button', { name: steps[i], exact: true })
            .getAttribute('aria-pressed'),
          'true',
        );
        const text = await scene.innerText();
        if (i === 0) {
          assert.match(
            text,
            /t\s*=\s*distance\s*\/\s*c.*sample\s*=\s*round\(distance\s*×\s*fs\s*\/\s*c\).*c\s*=\s*1,?484 m\/s.*sampling\s*20 MHz.*detectors z\s*=\s*0.*target plane z\s*=\s*15 mm.*Coordinates metres.*time seconds.*Authored distance\s*15 mm\s*→\s*10\.108\s*µs\s*→\s*index\s*202.*Units fixture only.*no reconstructed pixel or native target claim/is,
          );
          assert.equal(await scene.locator('img,canvas,image,svg').count(), 0);
        } else if (i === 1) {
          await trace(m);
        } else {
          assert.match(
            text,
            /b\s*=\s*2p\s*−\s*2tc\s*IFFT\(−ik FFT\(p\)\).*k\s*=\s*2πf\s*\/\s*c.*Nearest arrival sample.*solid-angle weights.*weight-sum and complex peak normalization.*Grid\s*41\s*×\s*41.*0\.5 mm spacing.*Signed derivative.*no FFT or backprojection run.*No optical fluence model.*iterative solver.*positivity guarantee or calibrated absorption/is,
          );
          assert.equal(await scene.locator('img,canvas,image,svg').count(), 0);
        }
        await absent();
        await capture(`contract-${i}-${m}`);
      }
    await page.locator('[data-story-step="2"]').click();
    await advance(336);
    await page.locator('[data-story-step="2"]').click();
    await trace(0);
    await absent();
    const oi = plan.beats.findIndex((b) => b.scene === 'output');
    await page.locator(`[data-story-step="${oi}"]`).click();
    assert.match(
      await scene.innerText(),
      /reconstruction\.npy.*41\s*×\s*41 target plane.*Participant image\s*\/\s*score empty.*Saved source artifacts are historical examples.*no tissue finding or recovered pressure here/is,
    );
    assert.equal(await scene.locator('img,canvas,image,svg').count(), 0);
    await absent();
    await capture('empty-output');
    const ri = plan.beats.findIndex((b) => b.scene === 'reference');
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    const reveal = () => scene.getByRole('button', { name: 'Reveal source rules', exact: true });
    await reveal().click();
    assert.equal(
      await scene
        .getByRole('button', { name: 'Hide source rules', exact: true })
        .getAttribute('aria-expanded'),
      'true',
    );
    assert.match(
      await scene.locator('[data-imaging-photoacoustic-reference-revealed]').innerText(),
      /Binary geometric support is solver-visible.*not calibrated pressure.*Source crop:\s*33\s*×\s*33\s*=\s*1,?089 pixels.*generic full image:\s*1,?681 pixels.*Both include\s*101 positive support pixels.*Reference\s*\/\s*reconstruction images and metric absent.*exit\s*\/\s*backward\s*\/\s*reset covers rules/is,
    );
    assert.equal(await scene.locator('img,canvas,image,svg').count(), 0);
    await capture('rules-revealed');
    await scene.getByRole('button', { name: 'Hide source rules', exact: true }).click();
    await absent();
    await advance(plan.beats[ri].startFrame);
    await reveal().click();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    await reveal().click();
    await page.locator('.scene-reset').click();
    await absent();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    await reveal().click();
    await page.locator('[data-story-step="1"]').click();
    await absent();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    const li = plan.beats.findIndex((b) => b.scene === 'limits');
    await page.locator(`[data-story-step="${li}"]`).click();
    assert.match(
      await scene.innerText(),
      /No reconstructed finding.*fluence\s*\/\s*absorption inference or numerical performance/is,
    );
    await capture('limits-contract');
    await absent();
    await page.locator('.scene-reset').click();
    await absent();
  }

  if (plan.recipe === 'imaging101-plane-wave-ultrasound-v1') {
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    const scene = page.locator('[data-imaging-plane-wave-scene]');
    const absent = async () =>
      assert.equal(await scene.locator('[data-imaging-plane-wave-reference-revealed]').count(), 0);
    const capture = async (n) =>
      page.locator('.scene-player').screenshot({ path: path.join(output, `${label}-${n}.png`) });
    const advance = async (f) => {
      await page.bringToFront();
      await page.locator('.scene-play').click();
      await page.locator('.scene-stage').scrollIntoViewIfNeeded();
      await page.waitForFunction(
        (x) => Number(document.querySelector('.scene-player').getAttribute('data-frame')) > x,
        f + 4,
      );
      await page.locator('.scene-play').click();
    };
    const images = async () => {
      const imgs = scene.locator('img');
      assert.equal(await imgs.count(), 2);
      for (let i = 0; i < 2; i++) {
        const phantom = ['fibers', 'cysts'][i];
        const d = await imgs
          .nth(i)
          .evaluate((e) => ({ src: e.src, w: e.naturalWidth, h: e.naturalHeight, alt: e.alt }));
        assert.equal(d.w, 128);
        assert.equal(d.h, [336, 192][i]);
        assert.match(d.alt, /raw ADC time\/element sheet, not B-mode/);
        assert.ok(d.src.startsWith('data:image/png;base64,'));
        assert.equal(
          sha(Buffer.from(d.src.split(',')[1], 'base64')),
          sha(
            fs.readFileSync(
              `presentation/task-explorer/imaging101-plane-wave-ultrasound/rf-${phantom}.png`,
            ),
          ),
        );
        const caption = await scene.locator('figcaption').nth(i).innerText();
        assert.match(
          caption,
          /128 element columns, 0°; every eighth native time sample.*Black 0 → white\s*255: raw ADC code/s,
        );
        assert.match(
          caption,
          i === 0
            ? /Fibers:\s*336 time rows, t₀\s*=\s*0\s*µs/
            : /Cysts:\s*192 time rows, t₀\s*=\s*50\s*µs/,
        );
      }
    };
    const source = JSON.parse(
      fs.readFileSync(
        'presentation/task-explorer/imaging101-plane-wave-ultrasound/source.json',
        'utf8',
      ),
    ).native_profiles;
    const branches = ['Fibers −1.5°', 'Fibers 0°', 'Cysts 0°'];
    const trace = async (m) => {
      const p = source.profiles[m],
        n = p.values.length,
        svg = scene.locator('svg');
      assert.equal(await svg.count(), 1);
      assert.equal(
        await svg.getAttribute('aria-label'),
        `Native raw ADC trace ${branches[m]}; no envelope or B-mode`,
      );
      const poly = svg.locator('polyline');
      assert.equal(await poly.getAttribute('stroke'), '#57d1cc');
      const points = (await poly.getAttribute('points'))
        .split(' ')
        .map((s) => s.split(',').map(Number));
      assert.equal(points.length, n);
      points.forEach((v, j) => {
        assert.ok(Math.abs(v[0] - (14 + (j * 244) / (n - 1))) < 1e-9);
        assert.ok(Math.abs(v[1] - (148 - (p.values[j] * 140) / 255)) < 1e-9);
      });
      const line = svg.locator('line');
      assert.equal(await line.getAttribute('stroke'), '#b2c2ce');
      assert.ok(
        Math.abs(Number(await line.getAttribute('y1')) - (148 - (p.global_mean * 140) / 255)) <
          1e-9,
      );
      assert.equal(await line.getAttribute('y1'), await line.getAttribute('y2'));
      const last = (p.t0_seconds + (n - 1) * source.dt_seconds) * 1e6;
      assert.deepEqual(
        (await svg.locator('text').allTextContents()).map((x) => x.trim()),
        ['ADC 0–255', `${(p.t0_seconds * 1e6).toFixed(0)}–${last.toFixed(2)} µs →`],
      );
      const caption = await scene.locator('figcaption').innerText();
      assert.ok(caption.includes(n.toLocaleString('en-US')));
      assert.ok(caption.includes(branches[m]));
      assert.ok(caption.includes(p.global_mean.toFixed(3)));
      assert.match(caption, /untouched samples, element 63.*Gray: global\s*mean/s);
      assert.equal(await scene.locator('img,canvas,image').count(), 0);
    };
    await page.locator('[data-story-step="0"]').click();
    await images();
    await absent();
    assert.match(
      await scene.innerText(),
      /128 elements.*7 angles.*20 MHz.*Display stride only.*no DC subtraction, envelope or\s*beamforming/is,
    );
    await capture('native-input');
    await advance(0);
    await page.locator('[data-story-step="0"]').click();
    const steps = ['RF + steering', 'Native traces', 'Compound + envelope'],
      bf = [336, 419, 503];
    for (let i = 0; i < 3; i++)
      for (let m = 0; m < 3; m++) {
        await page.locator('[data-story-step="2"]').click();
        await scene.getByRole('button', { name: branches[m], exact: true }).click();
        assert.equal(Number(await page.locator('.scene-player').getAttribute('data-frame')), bf[m]);
        await trace(m);
        await scene.getByRole('button', { name: steps[i], exact: true }).click();
        assert.equal(
          Number(await page.locator('.scene-player').getAttribute('data-frame')),
          i === 1 ? bf[m] : [168, 0, 504][i],
        );
        assert.equal(await scene.getAttribute('data-imaging-plane-wave-operation-step'), String(i));
        assert.equal(
          await scene
            .getByRole('button', { name: steps[i], exact: true })
            .getAttribute('aria-pressed'),
          'true',
        );
        const text = await scene.innerText();
        if (i === 0) {
          assert.match(
            text,
            /Real ADC\s*→\s*global DC removal\s*→\s*per-angle migration.*c\s*=\s*1,?540 m\/s.*298\s*µm pitch.*angles\s*−1\.5°…\+1\.5°.*Fibers t₀\s*=\s*0.*cysts t₀\s*=\s*50\s*µs.*Raw RF is not IQ.*Source depth grid uses c\s*\/\s*\(2fs\).*38\.5\s*µm steps.*relative to acquisition start.*compensation does not add an absolute depth label/is,
          );
          assert.equal(await scene.locator('img,canvas,image,svg').count(), 0);
        } else if (i === 1) {
          await trace(m);
        } else {
          assert.match(
            text,
            /mean\(complex migrated angles\)\s*→\s*envelope\s*→\s*power gamma.*ERM at\s*0° uses\s*c\/√2.*README says\s*c\/2.*Signed steering and linear Stolt\s*interpolation precede compounding.*Hilbert\(real\(compound\)\).*gamma\s*0\.7 fibers\s*\/\s*0\.5\s*cysts.*Authored\s*\+1 and\s*−1 average to\s*0.*mean magnitudes\s*=\s*1.*Phase fixture only.*No FFT, Hilbert, migration or result computed/is,
          );
          assert.equal(await scene.locator('img,canvas,image,svg').count(), 0);
        }
        await absent();
        await capture(`contract-${i}-${m}`);
      }
    await page.locator('[data-story-step="2"]').click();
    await advance(336);
    await page.locator('[data-story-step="2"]').click();
    await trace(0);
    await absent();
    const oi = plan.beats.findIndex((b) => b.scene === 'output');
    await page.locator(`[data-story-step="${oi}"]`).click();
    assert.match(
      await scene.innerText(),
      /reconstruction\.npy.*one phantom shape.*Fibers\s*2,?688\s*×\s*128 or cysts\s*1,?536\s*×\s*128.*No participant B-mode.*aggregate verdict.*FWHM\s*or CNR/is,
    );
    assert.equal(await scene.locator('img,canvas,image,svg').count(), 0);
    await absent();
    await capture('empty-output');
    const ri = plan.beats.findIndex((b) => b.scene === 'reference');
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    const reveal = () => scene.getByRole('button', { name: 'Reveal source rules', exact: true });
    await reveal().click();
    assert.equal(
      await scene
        .getByRole('button', { name: 'Hide source rules', exact: true })
        .getAttribute('aria-expanded'),
      'true',
    );
    assert.match(
      await scene.locator('[data-imaging-plane-wave-reference-revealed]').innerText(),
      /Baselines are solver-visible source arrays.*differ from saved B-mode.*not\s*anatomical truth.*Pixel denominators:\s*344,?064 fibers\s*\/\s*196,?608 cysts.*Source centered NCC differs from generic cosine.*per-phantom threshold names do not\s*bind generic keys.*Baseline\s*\/\s*output images and scores absent.*Exit\s*\/\s*backward\s*\/\s*reset covers rules/is,
    );
    assert.equal(await scene.locator('img,canvas,image,svg').count(), 0);
    await capture('rules-revealed');
    await scene.getByRole('button', { name: 'Hide source rules', exact: true }).click();
    await absent();
    await advance(plan.beats[ri].startFrame);
    await reveal().click();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    await reveal().click();
    await page.locator('.scene-reset').click();
    await absent();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    await reveal().click();
    await page.locator('[data-story-step="1"]').click();
    await absent();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    const li = plan.beats.findIndex((b) => b.scene === 'limits');
    await page.locator(`[data-story-step="${li}"]`).click();
    assert.match(
      await scene.innerText(),
      /Physical phantoms are not patients.*no focused tissue finding or numerical performance/is,
    );
    await capture('limits-contract');
    await absent();
    await page.locator('.scene-reset').click();
    await absent();
  }

  if (plan.recipe === 'imaging-ultrasound-sos-v1') {
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    const scene = page.locator('[data-sos-scene]');
    const absent = async () =>
      assert.equal(
        await scene
          .locator('[data-sos-source-truth], [data-sos-metric-boundary], [data-sos-format]')
          .count(),
        0,
      );
    const capture = async (n) =>
      page.locator('.scene-player').screenshot({ path: path.join(output, `${label}-${n}.png`) });
    const advance = async (f) => {
      await page.bringToFront();
      await page.locator('.scene-play').click();
      await page.locator('.scene-stage').scrollIntoViewIfNeeded();
      await page.waitForFunction(
        (x) => Number(document.querySelector('.scene-player').getAttribute('data-frame')) > x,
        f + 4,
      );
      await page.locator('.scene-play').click();
    };
    assert.equal(plan.reference_policy, 'no-reference-assets');
    assert.ok(plan.beats.every((b) => b.channels.reference.every((x) => x === 0)));
    await page.locator('[data-story-step="0"]').click();
    await absent();
    const native = JSON.parse(
      fs.readFileSync(
        'presentation/task-explorer/imaging101-ultrasound-sos-tomography/measurement.json',
        'utf8',
      ),
    );
    const points = (await scene.locator('polyline').getAttribute('points'))
      .split(' ')
      .map((x) => x.split(',').map(Number));
    const scale = Math.max(...native.native_detector_trace.map(Math.abs));
    assert.equal(points.length, 60);
    for (let i = 0; i < 60; i++) {
      assert.equal(points[i][0], 15 + i * 4);
      assert.ok(
        Math.abs(points[i][1] - (85 - (65 * native.native_detector_trace[i]) / scale)) < 1e-11,
      );
    }
    assert.equal(await scene.locator('polyline').getAttribute('stroke'), '#73c7e6');
    assert.equal(await scene.locator('line').getAttribute('stroke'), '#eeb989');
    assert.equal(await scene.locator('line').getAttribute('stroke-dasharray'), '4 4');
    assert.equal(await scene.locator('circle').getAttribute('fill'), '#92d9ae');
    assert.match(
      await scene.innerText(),
      /Native detector 64.*angle index 0–59.*noisy source trace.*zero baseline.*selected native sample.*No physical time calibration.*parallel-beam radon.*50 mm.*0\.5 mm.*not an implemented physical ring-ray table.*not calibrated seconds/is,
    );
    const slider = scene.locator('#sos-native-angle');
    assert.equal(await slider.getAttribute('max'), '59');
    await slider.fill('59');
    assert.match(await scene.locator('[data-sos-sample]').innerText(), /angle 177°/);
    assert.equal(Number(await scene.locator('circle').getAttribute('cx')), 251);
    await slider.fill('0');
    await capture('native-input');
    await advance(0);
    await slider.fill('59');
    await page.locator('[data-story-step="0"]').click();
    assert.equal(await slider.inputValue(), '0');
    const steps = ['1. Signed slowness', '2. Inverse conventions', '3. Adjoint normalization'],
      methods = ['FBP', 'SART', 'TV'],
      bf = [336, 419, 503];
    for (let i = 0; i < 3; i++)
      for (let j = 0; j < 3; j++) {
        await page.locator('[data-story-step="2"]').click();
        await scene.getByRole('button', { name: methods[j], exact: true }).click();
        assert.equal(Number(await page.locator('.scene-player').getAttribute('data-frame')), bf[j]);
        await scene.getByRole('button', { name: steps[i], exact: true }).click();
        assert.equal(
          Number(await page.locator('.scene-player').getAttribute('data-frame')),
          i === 1 ? bf[j] : [168, 0, 504][i],
        );
        assert.equal(
          await scene
            .getByRole('button', { name: steps[i], exact: true })
            .getAttribute('aria-pressed'),
          'true',
        );
        const text = await scene.innerText();
        if (i === 0) {
          assert.match(
            text,
            /Symbolic baseline algebra.*not a native finding.*delta_s=1\/c-1\/1500.*1e-8.*Main fat-negative comment is inconsistent with formula/is,
          );
          for (const c of [1450, 1500, 2500]) {
            await scene.getByRole('button', { name: `${c} m/s`, exact: true }).click();
            assert.match(
              await scene.locator('[data-sos-sign]').innerText(),
              new RegExp(c < 1500 ? 'positive' : c > 1500 ? 'negative' : 'zero'),
            );
            assert.ok(
              (await scene.locator('[data-sos-sign]').innerText()).includes(
                (1 / c - 1 / 1500).toPrecision(7),
              ),
            );
          }
        } else if (i === 1) {
          assert.equal(
            await scene
              .getByRole('button', { name: methods[j], exact: true })
              .getAttribute('aria-pressed'),
            'true',
          );
          const patterns = [
            /ramp-filtered iradon.*not refracted ring paths.*No FBP executed/is,
            /30 iterations.*relaxation0\.15.*full-sinogram residual backprojection.*textbook equivalence is not verified/is,
            /lambda 1e-6.*300 iterations.*positivity=False.*default lambda 1e-7.*positivity=True.*not a convergence proof/is,
          ];
          assert.match(await scene.locator('[data-sos-method]').innerText(), patterns[j]);
        } else
          assert.match(
            text,
            /unfiltered iradon\*pi\/\(2\*n_angles\).*TV updates use unfiltered iradon without this factor.*Exact discrete adjoint and step scaling unverified.*No forward operator, inverse, reconstruction or convergence trial/is,
          );
        assert.equal(await scene.locator('img,canvas,image,svg').count(), 0);
        await absent();
        await capture(`contract-${i}-${j}`);
      }
    await page.locator('[data-story-step="1"]').click();
    await advance(168);
    await scene.getByRole('button', { name: '2500 m/s', exact: true }).click();
    await page.locator('[data-story-step="1"]').click();
    assert.equal(
      await scene
        .getByRole('button', { name: '1500 m/s', exact: true })
        .getAttribute('aria-pressed'),
      'true',
    );
    const oi = plan.beats.findIndex((b) => b.scene === 'output');
    await page.locator(`[data-story-step="${oi}"]`).click();
    await absent();
    assert.match(
      await scene.innerText(),
      /128×128 real speed map.*m\/s.*UNSUBMITTED.*mathematical ceiling 1e8 m\/s.*not a clinically validated range.*not patient acquisition or tissue diagnosis/is,
    );
    await scene.getByRole('button', { name: 'Inspect artifact format', exact: true }).click();
    assert.match(
      await scene.locator('[data-sos-format]').innerText(),
      /Generic one real speed NPY.*main reconstructions\.npz.*multiple delta_s and sos.*not participant outputs/is,
    );
    await capture('empty-output');
    await advance(plan.beats[oi].startFrame);
    await page.locator(`[data-story-step="${oi}"]`).click();
    await absent();
    const hi = plan.beats.findIndex((b) => b.scene === 'helper');
    await page.locator(`[data-story-step="${hi}"]`).click();
    await absent();
    assert.match(
      await scene.innerText(),
      /Clean\/full projections and phantom truth.*already in supplied data.*does not establish private evaluation/is,
    );
    for (const t of ['L1', 'L2', 'L3']) {
      await scene.getByRole('button', { name: t, exact: true }).click();
      assert.equal(
        await scene.getByRole('button', { name: t, exact: true }).getAttribute('aria-pressed'),
        'true',
      );
      assert.match(
        await scene.locator('[data-sos-tier]').innerText(),
        t === 'L1'
          ? /noisy\/clean\/full raw arrays and phantom truth/
          : t === 'L2'
            ? /plus approach/
            : /plus software design/,
      );
    }
    const reveal = () => scene.getByRole('button', { name: 'Reveal source truth', exact: true });
    await reveal().click();
    assert.equal(
      await scene
        .getByRole('button', { name: 'Hide source truth', exact: true })
        .getAttribute('aria-expanded'),
      'true',
    );
    assert.match(
      await scene.locator('[data-sos-source-truth]').innerText(),
      /Exact source synthetic center.*not a participant reconstruction or private evaluator target.*1540\.000.*-0\.00001731602.*-0\.001195999/is,
    );
    assert.equal(await scene.locator('img,canvas,image,svg').count(), 0);
    await capture('source-revealed');
    await scene.getByRole('button', { name: 'Hide source truth', exact: true }).click();
    await absent();
    await advance(plan.beats[hi].startFrame);
    await reveal().click();
    await page.locator(`[data-story-step="${hi}"]`).click();
    await absent();
    assert.equal(
      await scene.getByRole('button', { name: 'L1', exact: true }).getAttribute('aria-pressed'),
      'true',
    );
    await reveal().click();
    await page.locator('.scene-reset').click();
    await absent();
    await page.locator(`[data-story-step="${hi}"]`).click();
    await absent();
    await reveal().click();
    await page.locator('[data-story-step="1"]').click();
    await absent();
    await page.locator(`[data-story-step="${hi}"]`).click();
    await absent();
    const li = plan.beats.findIndex((b) => b.scene === 'limits');
    await page.locator(`[data-story-step="${li}"]`).click();
    await absent();
    const rules = ['metric', 'reference selection', 'threshold'];
    const patterns = [
      /16384 speed entries.*No flux.*global SSIM.*constant-range NRMSE returns infinity/is,
      /ground_truth\.npz before reconstructions\.npz.*sos_phantom before slowness_perturbation.*full speed.*differs cropped delta_s/is,
      /ncc_boundary=0\.9\*best NCC.*nrmse_boundary=1\.1\*best NRMSE.*No metrics file retained.*no effective threshold or score/is,
    ];
    for (let i = 0; i < 3; i++) {
      await scene.getByRole('button', { name: rules[i], exact: true }).click();
      assert.match(await scene.locator('[data-sos-rule]').innerText(), patterns[i]);
    }
    const boundary = () =>
      scene.getByRole('button', { name: 'Reveal source metric boundary', exact: true });
    await boundary().click();
    assert.match(
      await scene.locator('[data-sos-metric-boundary]').innerText(),
      /13:115.*102x102=10404.*0\.0.*infinity.*zero norm.*local skimage.*zero-range guard.*No score computed/is,
    );
    await capture('rules-revealed');
    await scene.getByRole('button', { name: 'Hide source metric boundary', exact: true }).click();
    await absent();
    await advance(plan.beats[li].startFrame);
    await boundary().click();
    await page.locator(`[data-story-step="${li}"]`).click();
    await absent();
    assert.equal(
      await scene
        .getByRole('button', { name: 'reference selection', exact: true })
        .getAttribute('aria-pressed'),
      'true',
    );
    await boundary().click();
    await page.locator('.scene-reset').click();
    await absent();
    await page.locator(`[data-story-step="${li}"]`).click();
    await boundary().click();
    await page.locator('[data-story-step="1"]').click();
    await absent();
    await page.locator(`[data-story-step="${li}"]`).click();
    await absent();
    await capture('limits-contract');
    await page.locator('.scene-reset').click();
    await absent();
  }

  if (plan.recipe === 'imaging101-usct-fwi-v1') {
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true') await page.locator('.scene-play').click();
    const scene=page.locator('[data-imaging-usct-fwi-scene]');
    const absent=async()=>assert.equal(await scene.locator('[data-imaging-usct-fwi-reference-revealed]').count(),0);
    const capture=async n=>page.locator('.scene-player').screenshot({path:path.join(output,`${label}-${n}.png`)});
    const advance=async f=>{await page.bringToFront();await page.locator('.scene-play').click();await page.locator('.scene-stage').scrollIntoViewIfNeeded();await page.waitForFunction(x=>Number(document.querySelector('.scene-player').getAttribute('data-frame'))>x,f+4);await page.locator('.scene-play').click();};
    const image=async i=>{const imgs=scene.locator('img');assert.equal(await imgs.count(),1);const d=await imgs.evaluate(e=>({src:e.src,w:e.naturalWidth,h:e.naturalHeight,alt:e.alt}));assert.equal(d.w,128);assert.equal(d.h,128);assert.ok(d.src.startsWith('data:image/png;base64,'));assert.equal(sha(Buffer.from(d.src.split(',')[1],'base64')),sha(fs.readFileSync(`presentation/task-explorer/imaging101-usct-fwi/${['observations-03','observations-08','observations-125'][i]}.png`)));assert.match(d.alt,/Native numerical phantom complex observations.*real component, receiver rows and source columns, stride two/);assert.match(await scene.locator('figcaption').innerText(),/receiver rows.*source columns.*every second cell.*Black −.*gray 0.*white \+.*uncalibrated amplitude/is);};
    await page.locator('[data-story-step="0"]').click();await image(0);await absent();assert.match(await scene.innerText(),/20 frequencies.*256 receivers.*256 sources.*1,310,720 complex cells.*No time waveform, calibrated Pa or patient recordings.*No wave simulation, speed reconstruction or metric/is);await capture('native-input');await advance(0);await page.locator('[data-story-step="0"]').click();
    const steps=['Units + muting','Native frequencies','Fit + update rules'],branches=['0.3 MHz','0.8 MHz','1.25 MHz'],bf=[336,419,503];
    for(let i=0;i<3;i++)for(let m=0;m<3;m++){
      await page.locator('[data-story-step="2"]').click();await scene.getByRole('button',{name:branches[m],exact:true}).click();assert.equal(Number(await page.locator('.scene-player').getAttribute('data-frame')),bf[m]);await scene.getByRole('button',{name:steps[i],exact:true}).click();assert.equal(Number(await page.locator('.scene-player').getAttribute('data-frame')),i===1?bf[m]:[168,0,504][i]);assert.equal(await scene.getAttribute('data-imaging-usct-fwi-operation-step'),String(i));assert.equal(await scene.getByRole('button',{name:steps[i],exact:true}).getAttribute('aria-pressed'),'true');const text=await scene.innerText();
      if(i===0){assert.match(text,/480 × 480 cells.*50 µm.*256 ring positions.*24 mm.*2\.4 cm.*metadata says 24 cm.*7,500 µm muted.*zero observations additionally excluded.*No time sampling or density map/is);assert.equal(await scene.locator('img,canvas,image,svg').count(),0);}
      else if(i===1){assert.equal(await scene.getByRole('button',{name:branches[m],exact:true}).getAttribute('aria-pressed'),'true');await image(m);assert.match(text,/128 × 128 direct stride-two receiver\/source cells.*signed real amplitude.*complex profiles retained.*No wave solve, interpolation, amplitude calibration or reconstructed speed/is);await capture(`native-frequency-${m}`);}
      else{assert.match(text,/α = Σ\(conj\(dsrc\) y\) \/ Σ\|dsrc\|².*Authored dsrc = \[1, 2\], y = \[2, 4\] gives α = 2.*Native fitted α and update remain unknown.*1480 m\/s.*max 3 NCG steps per frequency.*9 × 9 gradient smoothing.*No gradient\/adjoint certification or current convergence/is);assert.equal(await scene.locator('img,canvas,image,svg').count(),0);}
      await absent();await capture(`contract-${i}-${m}`);
    }
    await page.locator('[data-story-step="2"]').click();await advance(336);await page.locator('[data-story-step="2"]').click();await image(0);await absent();
    const oi=plan.beats.findIndex(b=>b.scene==='output');await page.locator(`[data-story-step="${oi}"]`).click();assert.match(await scene.innerText(),/Participant speed map absent.*output\/reconstruction\.npy.*480 × 480.*m\/s.*Source main saves to evaluation\/reference_outputs instead.*never participant output or phantom truth/is);assert.equal(await scene.locator('img,canvas,image,svg').count(),0);await absent();await capture('empty-output');
    const ri=plan.beats.findIndex(b=>b.scene==='reference');await page.locator(`[data-story-step="${ri}"]`).click();await absent();const reveal=()=>scene.getByRole('button',{name:'Reveal public reference rules',exact:true});await reveal().click();assert.equal(await scene.getByRole('button',{name:'Cover public reference rules',exact:true}).getAttribute('aria-pressed'),'true');assert.match(await scene.locator('[data-imaging-usct-fwi-reference-revealed]').innerText(),/neither is phantom truth.*Filesystem selects a saved reconstruction, not true speed.*source uses the visible baseline.*230,400 cells.*No-filesystem scorer requires absent ground_truth\.npy.*No participant map, score or private truth/is);assert.equal(await scene.locator('img,canvas,image,svg').count(),0);await capture('rules-revealed');await scene.getByRole('button',{name:'Cover public reference rules',exact:true}).click();await absent();
    await advance(plan.beats[ri].startFrame);await reveal().click();await page.locator(`[data-story-step="${ri}"]`).click();await absent();await reveal().click();await page.locator('.scene-reset').click();await absent();await page.locator(`[data-story-step="${ri}"]`).click();await absent();await reveal().click();await page.locator('[data-story-step="1"]').click();await absent();await page.locator(`[data-story-step="${ri}"]`).click();await absent();
    const li=plan.beats.findIndex(b=>b.scene==='limits');await page.locator(`[data-story-step="${li}"]`).click();assert.match(await scene.innerText(),/No clinical property, reconstruction quality, current CUDA success or convergence claim/is);assert.equal(await scene.locator('img,canvas,image,svg').count(),0);await capture('limits-contract');await absent();await page.locator('.scene-reset').click();await absent();
  }

  if (plan.recipe === 'imaging101-pnp-mri-reconstruction-v1') {
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    const scene = page.locator('[data-imaging-pnp-mri-scene]');
    const absent = async () =>
      assert.equal(await scene.locator('[data-imaging-pnp-mri-reference-revealed]').count(), 0);
    const capture = async (n) =>
      page.locator('.scene-player').screenshot({ path: path.join(output, `${label}-${n}.png`) });
    const advance = async (f) => {
      await page.bringToFront();
      await page.locator('.scene-play').click();
      await page.locator('.scene-stage').scrollIntoViewIfNeeded();
      await page.waitForFunction(
        (x) => Number(document.querySelector('.scene-player').getAttribute('data-frame')) > x,
        f + 4,
      );
      await page.locator('.scene-play').click();
    };
    const image = async (reference) => {
      const imgs = scene.locator('img');
      assert.equal(await imgs.count(), 1);
      const d = await imgs.evaluate((e) => ({
        src: e.src,
        w: e.naturalWidth,
        h: e.naturalHeight,
        alt: e.alt,
      }));
      assert.equal(d.w, reference ? 160 : 320);
      assert.equal(d.h, reference ? 160 : 320);
      assert.ok(d.src.startsWith('data:image/png;base64,'));
      assert.equal(
        sha(Buffer.from(d.src.split(',')[1], 'base64')),
        sha(
          fs.readFileSync(
            `presentation/task-explorer/imaging101-pnp-mri-reconstruction/${reference ? 'source-image' : 'mask'}.png`,
          ),
        ),
      );
      if (reference) {
        assert.match(
          d.alt,
          /Public source image equals solver-visible truth; stride-two minmax display, not reconstruction/,
        );
        assert.match(
          await scene.locator('figcaption').innerText(),
          /Public source input = visible truth.*160 × 160 stride-two display.*no reconstruction/is,
        );
      } else {
        assert.match(
          d.alt,
          /Native source-saved radial mask on a Cartesian 320 by 320 grid; white sampled and black omitted, no measured k-space/,
        );
        assert.match(
          await scene.locator('figcaption').innerText(),
          /White\s*\/\s*black:\s*11,?766 sampled\s*\/\s*90,?634 omitted grid cells.*Saved geometry.*no Fourier\s*samples/is,
        );
      }
    };
    await page.locator('[data-story-step="0"]').click();
    await image(false);
    await absent();
    assert.match(
      await scene.innerText(),
      /Raw image\s*=\s*solver-visible truth.*320\s*×\s*320 source image.*generates noiseless masked Fourier data.*no scanner k-space or coil measurements.*Source image covered.*No FFT, reconstruction, denoiser or\s*score run/is,
    );
    await capture('native-input');
    await advance(0);
    await page.locator('[data-story-step="0"]').click();
    const steps = ['Input boundary', 'Mask + operator', 'PGM + MSSN'],
      branches = ['Saved mask', 'Unitary scale', 'Patch coverage'],
      bf = [336, 419, 503];
    for (let i = 0; i < 3; i++)
      for (let m = 0; m < 3; m++) {
        await page.locator('[data-story-step="2"]').click();
        await scene.getByRole('button', { name: branches[m], exact: true }).click();
        assert.equal(Number(await page.locator('.scene-player').getAttribute('data-frame')), bf[m]);
        await scene.getByRole('button', { name: steps[i], exact: true }).click();
        assert.equal(
          Number(await page.locator('.scene-player').getAttribute('data-frame')),
          i === 1 ? bf[m] : [168, 0, 504][i],
        );
        assert.equal(await scene.getAttribute('data-imaging-pnp-mri-operation-step'), String(i));
        assert.equal(
          await scene
            .getByRole('button', { name: steps[i], exact: true })
            .getAttribute('aria-pressed'),
          'true',
        );
        const text = await scene.innerText();
        if (i === 0) {
          assert.match(
            text,
            /Visible image\s*→\s*minmax\s*→\s*deterministic mask\s*→\s*generated y.*No acquired k-space or added measurement noise.*sigma\s*=\s*5.*unused.*training claim unverified.*L1\s*\/\s*L2\s*\/\s*L3.*No new source measurements generated/is,
          );
          assert.equal(await scene.locator('img,canvas,image,svg').count(), 0);
        } else if (i === 1) {
          assert.equal(
            await scene
              .getByRole('button', { name: branches[m], exact: true })
              .getAttribute('aria-pressed'),
            'true',
          );
          if (m === 0) {
            await image(false);
            assert.match(
              text,
              /36 rasterized radial lines.*11\.490% Cartesian cells sampled.*inverse fraction\s*≈\s*8\.703.*Not acquired.*non-Cartesian trajectories or scan-time acceleration/is,
            );
          } else if (m === 1) {
            assert.match(
              text,
              /A\s*=\s*M fftshift\(FFT2\)\s*\/\s*320.*Aᴴ\s*=\s*320 IFFT2\(ifftshift\(Mz\)\).*real image gradient uses real\(Aᴴ\(Ax−y\)\).*Unitary discrete scaling.*no coil or physical FOV model.*no native FFT, adjoint or reconstructed image computed/is,
            );
            assert.equal(await scene.locator('img,canvas,image,svg').count(), 0);
          } else {
            assert.match(
              text,
              /42\s*×\s*42 patches.*stride\s*7.*final start\s*278.*41 positions per axis\s*=\s*1,?681 patches.*overlap averaged.*Input\s*×\s*255.*residual\s*\+\s*input.*÷\s*255.*Checkpoint shards present.*compatibility and\s*output unknown.*No model loaded/is,
            );
            assert.equal(await scene.locator('img,canvas,image,svg').count(), 0);
          }
        } else {
          assert.match(
            text,
            /x₀\s*=\s*0.*s\s*=\s*max\(x\s*−\s*g,\s*0\).*x_next\s*=\s*D\(s\).*PGM:\s*200 fixed iterations.*step\s*1.*No ADMM dual variable.*positivity before\s*denoiser only.*Authored scalar y\s*=\s*0\.6.*pre-denoise s\s*=\s*0\.6.*D\(s\).*unknown.*no denoised output, convergence or performance/is,
          );
          assert.equal(await scene.locator('img,canvas,image,svg').count(), 0);
        }
        await absent();
        await capture(`contract-${i}-${m}`);
      }
    await page.locator('[data-story-step="2"]').click();
    await advance(336);
    await page.locator('[data-story-step="2"]').click();
    await image(false);
    await absent();
    const oi = plan.beats.findIndex((b) => b.scene === 'output');
    await page.locator(`[data-story-step="${oi}"]`).click();
    assert.match(
      await scene.innerText(),
      /reconstruction\.npy.*320\s*×\s*320 normalized image.*Participant output.*denoiser result.*histories and score empty.*Saved IFFT\s*\/\s*PnP arrays\s*are audit provenance only/is,
    );
    assert.equal(await scene.locator('img,canvas,image,svg').count(), 0);
    await absent();
    await capture('empty-output');
    const ri = plan.beats.findIndex((b) => b.scene === 'reference');
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    assert.equal(await scene.locator('img,canvas,image,svg').count(), 0);
    const reveal = () =>
      scene.getByRole('button', { name: 'Reveal public source image', exact: true });
    await reveal().click();
    assert.equal(
      await scene
        .getByRole('button', { name: 'Cover public source image', exact: true })
        .getAttribute('aria-pressed'),
      'true',
    );
    await image(true);
    assert.match(
      await scene.locator('[data-imaging-pnp-mri-reference-revealed]').innerText(),
      /Later public source image\s*=\s*solver-visible truth;\s*not reconstruction.*Normalized reference.*all\s*102,?400 pixels.*source norm-relative error differs from\s*generic range-normalized error.*Actual participant output and score absent/is,
    );
    await capture('rules-revealed');
    await scene.getByRole('button', { name: 'Cover public source image', exact: true }).click();
    await absent();
    assert.equal(await scene.locator('img').count(), 0);
    await advance(plan.beats[ri].startFrame);
    await reveal().click();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    await reveal().click();
    await page.locator('.scene-reset').click();
    await absent();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    await reveal().click();
    await page.locator('[data-story-step="1"]').click();
    await absent();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    const li = plan.beats.findIndex((b) => b.scene === 'limits');
    await page.locator(`[data-story-step="${li}"]`).click();
    assert.match(
      await scene.innerText(),
      /No blind inverse-problem.*learned proximal.*clinical or model-performance claim/is,
    );
    assert.equal(await scene.locator('img,canvas,image,svg').count(), 0);
    await capture('limits-contract');
    await absent();
    await page.locator('.scene-reset').click();
    await absent();
  }

  if (plan.recipe === 'imaging101-t2-mapping-v1') {
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    const scene = page.locator('[data-imaging-t2-mapping-scene]');
    const capture = async (n) =>
      page.locator('.scene-player').screenshot({ path: path.join(output, `${label}-${n}.png`) });
    const absent = async () =>
      assert.equal(await scene.locator('[data-imaging-t2-mapping-reference-revealed]').count(), 0);
    const advance = async (f) => {
      await page.bringToFront();
      await page.locator('.scene-play').click();
      await page.locator('.scene-stage').scrollIntoViewIfNeeded();
      await page.waitForFunction(
        (x) => Number(document.querySelector('.scene-player').getAttribute('data-frame')) > x,
        f + 4,
      );
      await page.locator('.scene-play').click();
    };
    const image = async (m) => {
      const img = scene.locator('img');
      assert.equal(await img.count(), 1);
      const native = await img.evaluate((e) => ({
        src: e.src,
        w: e.naturalWidth,
        h: e.naturalHeight,
        alt: e.alt,
      }));
      assert.equal(native.w, 256);
      assert.equal(native.h, 256);
      assert.match(
        native.alt,
        new RegExp(`Actual synthetic magnitude image, TE ${[10, 50, 100][m]} ms; no fitted T2 map`),
      );
      assert.ok(native.src.startsWith('data:image/png;base64,'));
      assert.equal(
        sha(Buffer.from(native.src.split(',')[1], 'base64')),
        sha(
          fs.readFileSync(
            `presentation/task-explorer/imaging101-mri-t2-mapping/echo-${[10, 50, 100][m]}.png`,
          ),
        ),
      );
      assert.match(
        await scene.locator('figcaption').innerText(),
        new RegExp(
          `Black→white: magnitude signal a\\.u\\..*fixed\\s*0–1\\s*display.*TE ${[10, 50, 100][m]} ms.*Native 256² cells.*no fit`,
          's',
        ),
      );
    };
    await page.locator('[data-story-step="0"]').click();
    await absent();
    await image(0);
    assert.match(
      await scene.innerText(),
      /10\s*echoes.*TE\s*10…100\s*ms.*256×256.*Magnitude signal a\.u\..*no complex\/coil axis.*Synthetic\s*220\s*mm FOV.*no patient acquisition.*target ranking may choose M0.*T2.*Truth mask solver-visible.*no participant result/is,
    );
    await capture('native-input');
    await advance(0);
    await page.locator('[data-story-step="0"]').click();
    const stepNames = ['Signal + noise', 'Native echoes', 'Log + nonlinear fit'],
      branchNames = ['TE 10 ms', 'TE 50 ms', 'TE 100 ms'],
      branchFrames = [336, 419, 503];
    for (let i = 0; i < 3; i++)
      for (let m = 0; m < 3; m++) {
        await page.locator('[data-story-step="2"]').click();
        await scene.getByRole('button', { name: branchNames[m], exact: true }).click();
        assert.equal(
          Number(await page.locator('.scene-player').getAttribute('data-frame')),
          branchFrames[m],
        );
        await image(m);
        await scene.getByRole('button', { name: stepNames[i], exact: true }).click();
        assert.equal(
          Number(await page.locator('.scene-player').getAttribute('data-frame')),
          i === 1 ? branchFrames[m] : [168, 0, 504][i],
        );
        assert.equal(await scene.getAttribute('data-imaging-t2-mapping-operation-step'), String(i));
        assert.equal(
          await scene
            .getByRole('button', { name: stepNames[i], exact: true })
            .getAttribute('aria-pressed'),
          'true',
        );
        const text = await scene.innerText();
        if (i === 0) {
          assert.match(
            text,
            /S\(TE\)=M₀ exp\(−TE\/T₂\).*TE and T₂ in ms.*Rician magnitude.*σ\s*=\s*(?:0)?\.02 per Gaussian channel.*not zero-mean magnitude noise.*Authored M₀\s*=\s*(?:0)?\.8.*T₂\s*=\s*80\s*ms.*10\/50\/100\s*ms.*0\.706.*0\.428.*0\.229.*no native fit\/noise draw/is,
          );
          assert.equal(await scene.locator('img,canvas,image').count(), 0);
        } else if (i === 1) {
          await image(m);
          assert.match(
            text,
            /Same grayscale scale across echoes.*Indices\s*0\/4\/9.*TE\s*10\/50\/100\s*ms.*no per-echo normalization.*log.*fitted map.*Signal intensity is a\.u\..*T2 output is ms.*background noise remains visible.*truth mask not applied/is,
          );
        } else {
          assert.match(
            text,
            /Log OLS versus signal-domain LM.*log\(max\(S,1e−10\)\).*unweighted OLS.*T₂=−1\/slope.*Unweighted nonlinear LM\s*50.*log fit.*positivity\/clipping.*fallback on failure.*weighted\/unbiased claims not established.*27,?817.*truth-mask pixels.*outside stays\s*0.*No fit\/convergence\/error measured/is,
          );
          assert.equal(await scene.locator('img,canvas,image').count(), 0);
        }
        await absent();
        await capture(`contract-${i}-${m}`);
      }
    await page.locator('[data-story-step="2"]').click();
    await advance(336);
    await page.locator('[data-story-step="2"]').click();
    await image(0);
    await absent();
    const oi = plan.beats.findIndex((b) => b.scene === 'output');
    await page.locator(`[data-story-step="${oi}"]`).click();
    await absent();
    assert.match(
      await scene.innerText(),
      /reconstruction\.npy.*256×256.*intended ms.*Participant map\/score empty.*Saved source T2\/M0 archives.*separate.*generic target ambiguity unresolved/is,
    );
    assert.equal(await scene.locator('img,canvas,image').count(), 0);
    await capture('empty-output');
    const ri = plan.beats.findIndex((b) => b.scene === 'reference');
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    const reveal = () => scene.getByRole('button', { name: 'Reveal source rules', exact: true });
    await reveal().click();
    assert.equal(
      await scene
        .getByRole('button', { name: 'Hide source rules', exact: true })
        .getAttribute('aria-expanded'),
      'true',
    );
    assert.match(
      await scene.locator('[data-imaging-t2-mapping-reference-revealed]').innerText(),
      /Source main T2.*27,?817.*masked pixels.*110\s*ms range.*Generic.*65,?536.*pixels.*no mask.*alphabetical M0_map before T2_map.*thresholds derive from masked T2 baseline.*unmasked M0.*unresolved.*No truth\/fitted image or verdict.*solver-visible.*never private or patient truth/is,
    );
    assert.equal(await scene.locator('img,canvas,image').count(), 0);
    await capture('rules-revealed');
    await scene.getByRole('button', { name: 'Hide source rules', exact: true }).click();
    await absent();
    await advance(plan.beats[ri].startFrame);
    await reveal().click();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    await reveal().click();
    await page.locator('.scene-reset').click();
    await absent();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    await reveal().click();
    await page.locator('[data-story-step="1"]').click();
    await absent();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    const li = plan.beats.findIndex((b) => b.scene === 'limits');
    await page.locator(`[data-story-step="${li}"]`).click();
    await absent();
    assert.match(
      await scene.innerText(),
      /Matching synthetic magnitude echoes.*no patient acquisition or participant fit.*ground_truth.*T2_map.*M0_map.*Live target\/threshold lineage unverified.*Actual synthetic echo contrast is input evidence only.*No fitted T2.*statistical unbiasedness.*model performance.*clinical finding/is,
    );
    await capture('limits-contract');
    await page.locator('.scene-reset').click();
    await absent();
  }

  if (plan.recipe === 'imaging101-sense-v1') {
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    const scene = page.locator('[data-imaging-sense-scene]');
    const capture = async (n) =>
      page.locator('.scene-player').screenshot({ path: path.join(output, `${label}-${n}.png`) });
    const absent = async () =>
      assert.equal(await scene.locator('[data-imaging-sense-reference-revealed]').count(), 0);
    const advance = async (f) => {
      await page.bringToFront();
      await page.locator('.scene-play').click();
      await page.locator('.scene-stage').scrollIntoViewIfNeeded();
      await page.waitForFunction(
        (x) => Number(document.querySelector('.scene-player').getAttribute('data-frame')) > x,
        f + 4,
      );
      await page.locator('.scene-play').click();
    };
    const image = async (m) => {
      const img = scene.locator('img');
      assert.equal(await img.count(), 1);
      const native = await img.evaluate((e) => ({
        src: e.src,
        w: e.naturalWidth,
        h: e.naturalHeight,
        alt: e.alt,
      }));
      assert.equal(native.w, 128);
      assert.equal(native.h, 128);
      assert.match(
        native.alt,
        new RegExp(
          `Actual synthetic sensitivity magnitude, Coil ${[0, 3, 7][m]}; no reconstructed image`,
        ),
      );
      assert.ok(native.src.startsWith('data:image/png;base64,'));
      assert.equal(
        sha(Buffer.from(native.src.split(',')[1], 'base64')),
        sha(
          fs.readFileSync(
            `presentation/task-explorer/imaging101-mri-sense/sensitivity-${[0, 3, 7][m]}.png`,
          ),
        ),
      );
      assert.match(
        await scene.locator('figcaption').first().innerText(),
        /Gray:.*fixed\s*0–\s*\.16\s*display;\s*phase lost.*128²\s*stored indices/s,
      );
    };
    await page.locator('[data-story-step="0"]').click();
    await absent();
    await image(0);
    assert.match(
      await scene.innerText(),
      /8\s*coils.*128×128.*complex source data.*masked keys mismatch full-kspace loader.*main R4 differs from native R3.*54\s*rows\s*×\s*128\s*columns\s*×\s*8\s*coils\s*=\s*55,?296\s*complex values.*no patient\/FOV\/time claim/is,
    );
    const rows = await scene
      .locator('svg rect')
      .evaluateAll((es) =>
        es.map((e) => [
          Number(e.getAttribute('x')),
          Number(e.getAttribute('width')),
          e.getAttribute('fill'),
        ]),
      );
    assert.equal(rows.length, 128);
    for (let i = 0; i < 128; i++)
      assert.deepEqual(rows[i], [i, 1, i % 3 === 0 || (i >= 56 && i < 72) ? '#57d1cc' : '#122939']);
    await capture('native-input');
    await advance(0);
    await page.locator('[data-story-step="0"]').click();
    const stepNames = ['Coil encoding', 'Native maps + mask', 'CG + scaling'];
    const branchNames = ['Coil 0', 'Coil 3', 'Coil 7'];
    const branchFrames = [336, 419, 503];
    for (let i = 0; i < 3; i++)
      for (let m = 0; m < 3; m++) {
        await page.locator('[data-story-step="2"]').click();
        await scene.getByRole('button', { name: branchNames[m], exact: true }).click();
        assert.equal(
          Number(await page.locator('.scene-player').getAttribute('data-frame')),
          branchFrames[m],
        );
        await image(m);
        await scene.getByRole('button', { name: stepNames[i], exact: true }).click();
        assert.equal(
          Number(await page.locator('.scene-player').getAttribute('data-frame')),
          i === 1 ? branchFrames[m] : [168, 0, 504][i],
        );
        assert.equal(await scene.getAttribute('data-imaging-sense-operation-step'), String(i));
        assert.equal(
          await scene
            .getByRole('button', { name: stepNames[i], exact: true })
            .getAttribute('aria-pressed'),
          'true',
        );
        const text = await scene.innerText();
        if (i === 0) {
          assert.match(
            text,
            /y_c=M F\(S_c x\).*spatial axes\s*0\/1.*coil last.*Centered default FFT.*inverse scale\s*1\/16384.*Complex sensitivity phase matters.*Authored matrix.*x=\[1,\s*2\].*y=\[5,\s*5\].*no native solve/is,
          );
          assert.equal(await scene.locator('img,canvas,image').count(), 0);
        } else if (i === 1) {
          await image(m);
          assert.match(
            text,
            /Supplied maps.*no calibration estimation.*float32.*complex128.*Native R3 mask.*ACS\s*16.*main requests absent full data then R4.*Display coil only.*no FFT\/CG.*map power not unity/is,
          );
        } else {
          assert.match(
            text,
            /CG: helper\(Ax\)=helper\(data\).*conj\(S\).*IFFT.*no mask.*scaled inverse.*Euclidean adjoint.*Zero start.*rtol\s*1e−5.*max\s*163,?840.*no explicit λ\/preconditioner.*First-coil nonzero mask can miss sampled zeros.*info discarded.*magnitude\/max.*No iteration\/convergence\/result measured/is,
          );
          assert.equal(await scene.locator('img,canvas,image').count(), 0);
        }
        await absent();
        await capture(`contract-${i}-${m}`);
      }
    await page.locator('[data-story-step="2"]').click();
    await advance(336);
    await page.locator('[data-story-step="2"]').click();
    await image(0);
    await absent();
    const oi = plan.beats.findIndex((b) => b.scene === 'output');
    await page.locator(`[data-story-step="${oi}"]`).click();
    await absent();
    assert.match(
      await scene.innerText(),
      /reconstruction\.npy.*128×128.*Participant image\/score empty.*Saved source SENSE\/RSS.*separate from fresh execution/is,
    );
    assert.equal(await scene.locator('img,canvas,image').count(), 0);
    await capture('empty-output');
    const ri = plan.beats.findIndex((b) => b.scene === 'reference');
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    const reveal = () => scene.getByRole('button', { name: 'Reveal source rules', exact: true });
    await reveal().click();
    assert.equal(
      await scene
        .getByRole('button', { name: 'Hide source rules', exact: true })
        .getAttribute('aria-expanded'),
      'true',
    );
    assert.match(
      await scene.locator('[data-imaging-sense-reference-revealed]').innerText(),
      /phantom key image.*solver-visible.*no private target.*No truth\/reconstruction image.*magnitude comparison.*16,?384\s*pixels.*no scale normalization.*Source main max-normalizes.*selected reference lineage.*windowed SSIM.*generic global SSIM.*range NRMSE.*infinity.*constant reference.*No source SSIM zero-range guard.*(?:no|or) current verdict/is,
    );
    assert.equal(await scene.locator('img,canvas,image').count(), 0);
    await capture('rules-revealed');
    await scene.getByRole('button', { name: 'Hide source rules', exact: true }).click();
    await absent();
    await advance(plan.beats[ri].startFrame);
    await reveal().click();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    await reveal().click();
    await page.locator('.scene-reset').click();
    await absent();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    await reveal().click();
    await page.locator('[data-story-step="1"]').click();
    await absent();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    const li = plan.beats.findIndex((b) => b.scene === 'limits');
    await page.locator(`[data-story-step="${li}"]`).click();
    await absent();
    assert.match(
      await scene.innerText(),
      /masked_kspace.*kspace_full.*R3.*R(?:=|\s*)4.*No matched end-to-end.*participant result.*synthetic map previews.*neither patient truth nor reconstruction.*complex phases.*source R.*selected-reference lineage/is,
    );
    await capture('limits-contract');
    await page.locator('.scene-reset').click();
    await absent();
  }
  if (plan.recipe === 'imaging101-pnp-admm-v1') {
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    const scene = page.locator('[data-imaging-pnp-admm-scene]');
    const capture = async (n) =>
      page.locator('.scene-player').screenshot({ path: path.join(output, `${label}-${n}.png`) });
    const absent = async () =>
      assert.equal(await scene.locator('[data-imaging-pnp-admm-reference-revealed]').count(), 0);
    const advance = async (f) => {
      await page.bringToFront();
      await page.locator('.scene-play').click();
      await page.locator('.scene-stage').scrollIntoViewIfNeeded();
      await page.waitForFunction(
        (x) => Number(document.querySelector('.scene-player').getAttribute('data-frame')) > x,
        f + 4,
      );
      await page.locator('.scene-play').click();
    };
    const image = async (m) => {
      const img = scene.locator('img');
      assert.equal(await img.count(), 1);
      const native = await img.evaluate((e) => ({
        src: e.src,
        w: e.naturalWidth,
        h: e.naturalHeight,
        alt: e.alt,
      }));
      assert.equal(native.w, 256);
      assert.equal(native.h, 256);
      assert.match(
        native.alt,
        new RegExp(
          `Actual ${['Random', 'Radial grid', 'Cartesian'][m]} binary source mask.*stored unshifted Fourier cells`,
        ),
      );
      assert.ok(native.src.startsWith('data:image/png;base64,'));
      assert.equal(
        sha(Buffer.from(native.src.split(',')[1], 'base64')),
        sha(
          fs.readFileSync(
            `presentation/task-explorer/imaging101-mri-pnp-admm/mask-${['random', 'radial', 'cartesian'][m]}.png`,
          ),
        ),
      );
      assert.match(
        await scene.locator('figcaption').innerText(),
        new RegExp(
          `Teal\\s*=\\s*sampled.*dark\\s*=\\s*unsampled.*${[19674, 19249, 19456][m]}/65536.*256² native indices`,
          's',
        ),
      );
    };
    await page.locator('[data-story-step="0"]').click();
    await absent();
    await image(0);
    assert.match(
      await scene.innerText(),
      /Single coil.*256×256.*No measured k-space.*metadata omits required.*noise_scale.*No calibrated FOV\/time/is,
    );
    await capture('native-input');
    await advance(0);
    await page.locator('[data-story-step="0"]').click();
    const stepNames = ['Synthesize + initialize', 'Fourier consistency', 'Denoiser + dual'];
    const branchNames = ['Random', 'Radial grid', 'Cartesian'];
    const branchFrames = [336, 419, 503];
    for (let i = 0; i < 3; i++)
      for (let m = 0; m < 3; m++) {
        await page.locator('[data-story-step="2"]').click();
        await scene.getByRole('button', { name: branchNames[m], exact: true }).click();
        assert.equal(
          Number(await page.locator('.scene-player').getAttribute('data-frame')),
          branchFrames[m],
        );
        await image(m);
        await scene.getByRole('button', { name: stepNames[i], exact: true }).click();
        assert.equal(
          Number(await page.locator('.scene-player').getAttribute('data-frame')),
          i === 1 ? branchFrames[m] : [168, 0, 504][i],
        );
        assert.equal(await scene.getAttribute('data-imaging-pnp-admm-operation-step'), String(i));
        assert.equal(
          await scene
            .getByRole('button', { name: stepNames[i], exact: true })
            .getAttribute('aria-pressed'),
          'true',
        );
        const text = await scene.innerText();
        if (i === 0) {
          assert.match(
            text,
            /y=M FFT2\(image\).*noise_real.*noise_imag.*Unshifted default FFT.*noise added at all bins.*real image iterates.*Missing metadata scale.*Default helper scale=3.*does not resolve main/is,
          );
          assert.equal(await scene.locator('img,canvas,image').count(), 0);
        } else if (i === 1) {
          await image(m);
          assert.match(
            text,
            /α=2.*sampled vf.*\.25vf.*1\.25.*Unsampled vf unchanged.*vf=2.*y=6.*5\.2.*arithmetic only.*never change the pinned random-mask main/is,
          );
        } else {
          assert.match(
            text,
            /xtilde=2v−xold−uold.*Min\/max normalize.*1\+15\/255\/2.*subtract model residual.*u←uold\+xold−v.*100 fixed iterations.*σ=15 training parameter.*not measured noise.*Constant-input normalization unguarded.*No model residual or convergence claim/is,
          );
          assert.equal(await scene.locator('img,canvas,image').count(), 0);
        }
        await absent();
        await capture(`contract-${i}-${m}`);
      }
    await page.locator('[data-story-step="2"]').click();
    await advance(336);
    await page.locator('[data-story-step="2"]').click();
    await image(0);
    await absent();
    const oi = plan.beats.findIndex((b) => b.scene === 'output');
    await page.locator(`[data-story-step="${oi}"]`).click();
    await absent();
    assert.match(
      await scene.innerText(),
      /reconstruction\.npy.*256×256.*Participant image\/score empty.*Saved source PnP examples.*separate from a fresh response/is,
    );
    assert.equal(await scene.locator('img,canvas,image').count(), 0);
    await capture('empty-output');
    const ri = plan.beats.findIndex((b) => b.scene === 'reference');
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    const reveal = () => scene.getByRole('button', { name: 'Reveal source rules', exact: true });
    await reveal().click();
    assert.equal(
      await scene
        .getByRole('button', { name: 'Hide source rules', exact: true })
        .getAttribute('aria-expanded'),
      'true',
    );
    assert.match(
      await scene.locator('[data-imaging-pnp-admm-reference-revealed]').innerText(),
      /solver-visible.*no private target.*No truth image.*squeezes only ndim>2.*magnitude.*float64.*evaluation\/ground_truth\.npy.*priority.*absent\/unverified.*unscaled range NRMSE.*cosine NCC.*No-filesystem fallback.*flux-normalized relative L2.*No current score/is,
    );
    assert.equal(await scene.locator('img,canvas,image').count(), 0);
    await capture('rules-revealed');
    await scene.getByRole('button', { name: 'Hide source rules', exact: true }).click();
    await absent();
    await advance(plan.beats[ri].startFrame);
    await reveal().click();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    await reveal().click();
    await page.locator('.scene-reset').click();
    await absent();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    await reveal().click();
    await page.locator('[data-story-step="1"]').click();
    await absent();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    const li = plan.beats.findIndex((b) => b.scene === 'limits');
    await page.locator(`[data-story-step="${li}"]`).click();
    await absent();
    assert.match(
      await scene.innerText(),
      /noise_scale.*Brain\.jpg.*rights.*No participant.*Mask diagrams.*not brain image evidence.*README convergence claims require conditions.*source inspection.*not a checkpoint or solver test/is,
    );
    await capture('limits-contract');
    await page.locator('.scene-reset').click();
    await absent();
  }

  if (plan.recipe === 'imaging101-noncartesian-v1') {
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    const scene = page.locator('[data-imaging-noncartesian-scene]');
    const capture = async (n) =>
      page.locator('.scene-player').screenshot({ path: path.join(output, `${label}-${n}.png`) });
    const absent = async () =>
      assert.equal(
        await scene.locator('[data-imaging-noncartesian-reference-revealed]').count(),
        0,
      );
    const advance = async (f) => {
      await page.bringToFront();
      await page.locator('.scene-play').click();
      await page.locator('.scene-stage').scrollIntoViewIfNeeded();
      await page.waitForFunction(
        (x) => Number(document.querySelector('.scene-player').getAttribute('data-frame')) > x,
        f + 4,
      );
      await page.locator('.scene-play').click();
    };
    const source = JSON.parse(
      fs.readFileSync(
        'presentation/task-explorer/imaging101-mri-noncartesian-cs/source.json',
        'utf8',
      ),
    );
    const plot = async (m) => {
      const svg = scene.locator('svg');
      assert.match(
        await svg.getAttribute('aria-label'),
        /Actual source radial trajectory subset.*grid coordinates.*not a reconstructed image/,
      );
      assert.equal(await svg.locator('path').getAttribute('stroke'), '#526373');
      const rows = await svg
        .locator('circle')
        .evaluateAll((es) =>
          es.map((e) => [
            Number(e.getAttribute('cx')),
            Number(e.getAttribute('cy')),
            e.getAttribute('r'),
            e.getAttribute('fill'),
          ]),
        );
      const points = source.trajectory.points.slice(0, [1, 16, 64][m] * 8);
      assert.equal(rows.length, points.length);
      points.forEach((p, j) => {
        assert.ok(Math.abs(rows[j][0] - (8 + ((p[1] + 64) * 240) / 128)) < 1e-9);
        assert.ok(Math.abs(rows[j][1] - (8 + ((64 - p[0]) * 240) / 128)) < 1e-9);
        assert.deepEqual(rows[j].slice(2), ['1.3', '#57d1cc']);
      });
      assert.match(
        await scene.locator('figcaption').innerText(),
        /of 8192 points.*of 64 spokes.*1-in-16 display.*acquisition unchanged/s,
      );
    };
    await page.locator('[data-story-step="0"]').click();
    await absent();
    const img = scene.locator('img');
    const native = await img.evaluate((e) => ({
      src: e.src,
      w: e.naturalWidth,
      h: e.naturalHeight,
      alt: e.alt,
    }));
    assert.equal(native.w, 256);
    assert.equal(native.h, 256);
    assert.match(
      native.alt,
      /Pinned synthetic radial coordinates.*512 of 8192.*no image reconstruction/,
    );
    assert.ok(native.src.startsWith('data:image/png;base64,'));
    assert.equal(
      sha(Buffer.from(native.src.split(',')[1], 'base64')),
      '1ea07a047fe848b749d6b98d0dd420cf1f825576a7714c11590024ba37182b98',
    );
    assert.match(
      await scene.innerText(),
      /4 coils.*64 spokes.*128 readout.*8192 samples\/coil.*Source-visible phantom.*no held-out.*physical FOV\/time uncalibrated/is,
    );
    await capture('native-input');
    await advance(0);
    await page.locator('[data-story-step="0"]').click();
    const stepNames = ['Trajectory + coils', 'NUFFT + density', 'Complex wavelet prior'];
    const branchNames = ['Show 1 spoke', 'Show 16 spokes', 'Show 64 spokes'];
    const branchFrames = [336, 419, 503];
    for (let i = 0; i < 3; i++)
      for (let m = 0; m < 3; m++) {
        await page.locator('[data-story-step="2"]').click();
        await scene.getByRole('button', { name: branchNames[m], exact: true }).click();
        assert.equal(
          Number(await page.locator('.scene-player').getAttribute('data-frame')),
          branchFrames[m],
        );
        await plot(m);
        await scene.getByRole('button', { name: stepNames[i], exact: true }).click();
        assert.equal(
          Number(await page.locator('.scene-player').getAttribute('data-frame')),
          i === 1 ? branchFrames[m] : [168, 0, 504][i],
        );
        assert.equal(
          await scene.getAttribute('data-imaging-noncartesian-operation-step'),
          String(i),
        );
        assert.equal(
          await scene
            .getByRole('button', { name: stepNames[i], exact: true })
            .getAttribute('aria-pressed'),
          'true',
        );
        const text = await scene.innerText();
        if (i === 0) {
          assert.match(
            text,
            /coord\s*\(1,\s*8192,\s*2\).*complex kdata\s*\(1,\s*4,\s*8192\).*maps\s*\(1,\s*4,\s*128,\s*128\).*no millisecond time axis.*÷128.*not 50% unique coverage/is,
          );
        } else if (i === 1) {
          await plot(m);
          assert.match(
            text,
            /DCF baseline differs.*30 default iterations.*weighted adjoint.*Actual weights\/image absent.*SigPy runtime defaults not exactly pinned/is,
          );
        } else {
          assert.match(
            text,
            /λ=5e−5.*100 iterations.*solver adjoint sums conjugated coil maps.*no gridding DCF\/normalization.*3 \+ 4i.*2\.4\+3\.2i.*preserves phase.*noise_std=\.005.*declared.*No NUFFT/is,
          );
        }
        assert.equal(await scene.locator('img,canvas,image').count(), 0);
        await absent();
        await capture(`contract-${i}-${m}`);
      }
    await page.locator('[data-story-step="2"]').click();
    await advance(336);
    await page.locator('[data-story-step="2"]').click();
    await plot(0);
    await absent();
    const oi = plan.beats.findIndex((b) => b.scene === 'output');
    await page.locator(`[data-story-step="${oi}"]`).click();
    await absent();
    assert.match(
      await scene.innerText(),
      /reconstruction\.npy.*128×128.*Participant image\/score empty.*saved examples.*never a fresh response/is,
    );
    assert.equal(await scene.locator('img,canvas,image').count(), 0);
    await capture('empty-output');
    const ri = plan.beats.findIndex((b) => b.scene === 'reference');
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    const reveal = () => scene.getByRole('button', { name: 'Reveal source rules', exact: true });
    await reveal().click();
    assert.equal(
      await scene
        .getByRole('button', { name: 'Hide source rules', exact: true })
        .getAttribute('aria-expanded'),
      'true',
    );
    assert.match(
      await scene.locator('[data-imaging-noncartesian-reference-revealed]').innerText(),
      /solver-visible.*truth key phantom.*no private hidden target.*No truth\/reconstruction image.*above two dimensions.*magnitude.*no scale normalization.*flux-normalizes.*relative L2.*16384.*8192.*no native score or pass\/fail/is,
    );
    assert.equal(await scene.locator('img,canvas,image').count(), 0);
    await capture('rules-revealed');
    await scene.getByRole('button', { name: 'Hide source rules', exact: true }).click();
    await absent();
    await advance(plan.beats[ri].startFrame);
    await reveal().click();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    await reveal().click();
    await page.locator('.scene-reset').click();
    await absent();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    await reveal().click();
    await page.locator('[data-story-step="1"]').click();
    await absent();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    const li = plan.beats.findIndex((b) => b.scene === 'limits');
    await page.locator(`[data-story-step="${li}"]`).click();
    await absent();
    assert.match(
      await scene.innerText(),
      /coordinate units.*calibrat|physical FOV|runtime\/evaluator/is,
    );
    await capture('limits-contract');
    await page.locator('.scene-reset').click();
    await absent();
  }
  if (plan.recipe === 'imaging101-wavelet-v1') {
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    const scene = page.locator('[data-imaging-wavelet-scene]');
    const capture = async (n) =>
      page.locator('.scene-player').screenshot({ path: path.join(output, `${label}-${n}.png`) });
    const absent = async () =>
      assert.equal(await page.locator('[data-imaging-wavelet-reference-revealed]').count(), 0);
    const advance = async (f) => {
      await page.bringToFront();
      await page.locator('.scene-play').click();
      await page.locator('.scene-stage').scrollIntoViewIfNeeded();
      await page.waitForFunction(
        (x) => Number(document.querySelector('.scene-player').getAttribute('data-frame')) > x,
        f + 4,
      );
      await page.locator('.scene-play').click();
    };
    const source = JSON.parse(
      fs.readFileSync('presentation/task-explorer/imaging101-mri-l1-wavelet/source.json', 'utf8'),
    );
    const image = async (coil) => {
      const img = scene.locator('img');
      assert.equal(await img.count(), 1);
      const state = await img.evaluate((e) => ({
        src: e.src,
        w: e.naturalWidth,
        h: e.naturalHeight,
        alt: e.alt,
      }));
      assert.equal(state.w, 320);
      assert.equal(state.h, 320);
      assert.match(state.alt, new RegExp(`coil ${coil}.*log-magnitude.*not reconstructed`));
      assert.ok(state.src.startsWith('data:image/png;base64,'));
      assert.equal(
        sha(Buffer.from(state.src.split(',')[1], 'base64')),
        sha(
          fs.readFileSync(`presentation/task-explorer/imaging101-mri-l1-wavelet/coil-${coil}.png`),
        ),
      );
    };
    const mask = async () => {
      assert.deepEqual(
        await scene
          .locator('svg rect')
          .evaluateAll((es) =>
            es.map((e) => [
              e.getAttribute('x'),
              e.getAttribute('width'),
              e.getAttribute('height'),
              e.getAttribute('fill'),
            ]),
          ),
        source.native_mask.map((v, j) => [String(j), '1', '20', v ? '#57d1cc' : '#526373']),
      );
      assert.match(
        await scene.locator('svg').getAttribute('aria-label'),
        /80 of 320 last-axis phase-encode columns/,
      );
    };
    await page.locator('[data-story-step="0"]').click();
    await absent();
    await image(0);
    await mask();
    assert.match(
      await scene.innerText(),
      /1 slice.*15 coils.*320×320.*no physical affine\/spacing.*No reconstructed image/is,
    );
    await capture('native-input');
    await advance(0);
    await page.locator('[data-story-step="0"]').click();
    await absent();
    const stepNames = ['Sampling + coils', 'Complex forward model', 'Wavelet prior'];
    const coilNames = ['Coil 0', 'Coil 7', 'Coil 14'];
    const coilFrames = [336, 419, 503];
    for (let i = 0; i < 3; i++)
      for (let m = 0; m < 3; m++) {
        await page.locator('[data-story-step="2"]').click();
        await scene.getByRole('button', { name: coilNames[m], exact: true }).click();
        assert.equal(
          Number(await page.locator('.scene-player').getAttribute('data-frame')),
          coilFrames[m],
        );
        await image([0, 7, 14][m]);
        await scene.getByRole('button', { name: stepNames[i], exact: true }).click();
        const frame = i === 1 ? coilFrames[m] : [168, 0, 504][i];
        assert.equal(Number(await page.locator('.scene-player').getAttribute('data-frame')), frame);
        assert.equal(await scene.getAttribute('data-imaging-wavelet-operation-step'), String(i));
        assert.equal(
          await scene
            .getByRole('button', { name: stepNames[i], exact: true })
            .getAttribute('aria-pressed'),
          'true',
        );
        if (i === 0) {
          await mask();
          assert.match(
            await scene.innerText(),
            /80\/320.*Complex64\s*\(1,\s*15,\s*320,\s*320\).*Metadata R4.*README\s+8 coils/is,
          );
          assert.equal(await scene.locator('img').count(), 0);
        } else if (i === 1) {
          await image([0, 7, 14][m]);
          assert.match(
            await scene.innerText(),
            /y_c=M F\(S_c x\).*centered orthonormal FFT.*not solver preprocessing.*Separate per-coil log scales/is,
          );
        } else {
          assert.match(
            await scene.innerText(),
            /FISTA uses λ=1e−3.*τ=λα.*3 \+ 4i.*2\.4\+3\.2i.*no native coefficients.*normalized physics helper divides.*distinct operator/is,
          );
          assert.equal(await scene.locator('img').count(), 0);
        }
        await absent();
        await capture(`contract-${i}-${m}`);
      }
    await page.locator('[data-story-step="2"]').click();
    await advance(336);
    await page.locator('[data-story-step="2"]').click();
    assert.equal(Number(await page.locator('.scene-player').getAttribute('data-frame')), 336);
    await image(0);
    await absent();
    const out = plan.beats.findIndex((b) => b.scene === 'output');
    await page.locator(`[data-story-step="${out}"]`).click();
    await absent();
    assert.match(
      await scene.innerText(),
      /reconstruction\.npy.*320×320.*Actual image, score and outcome empty.*not a participant prediction/is,
    );
    assert.equal(await scene.locator('img,canvas,image').count(), 0);
    await capture('empty-output');
    const ri = plan.beats.findIndex((b) => b.scene === 'reference');
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    const reveal = () => scene.getByRole('button', { name: 'Reveal source rules', exact: true });
    await reveal().click();
    assert.equal(
      await scene
        .getByRole('button', { name: 'Hide source rules', exact: true })
        .getAttribute('aria-expanded'),
      'true',
    );
    assert.match(
      await scene.locator('[data-imaging-wavelet-reference-revealed]').innerText(),
      /solver-visible.*mvue.*missing phantom.*No truth image.*phase discarded.*no intensity renormalization.*fallback instead flux-normalizes.*relative L2.*102400.*not 15 coils/is,
    );
    assert.equal(await scene.locator('img,canvas,image').count(), 0);
    await capture('rules-revealed');
    await scene.getByRole('button', { name: 'Hide source rules', exact: true }).click();
    await absent();
    await advance(plan.beats[ri].startFrame);
    await reveal().click();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    await reveal().click();
    await page.locator('.scene-reset').click();
    await absent();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    await reveal().click();
    await page.locator('[data-story-step="1"]').click();
    await absent();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    const li = plan.beats.findIndex((b) => b.scene === 'limits');
    await page.locator(`[data-story-step="${li}"]`).click();
    await absent();
    assert.match(
      await scene.innerText(),
      /README synthetic 8-coil 128-square R8 differs.*15-coil 320-square R4.*phantom.*mvue.*fastMRI rights/is,
    );
    await capture('limits-contract');
    await page.locator('.scene-reset').click();
    await absent();
  }
  if (plan.recipe === 'imaging-grappa-v1') {
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    const scene = page.locator('[data-grappa-scene]');
    const capture = async (name) =>
      page.locator('.scene-player').screenshot({ path: path.join(output, `${label}-${name}.png`) });
    const absent = async () =>
      assert.equal(await page.locator('[data-grappa-full-target], [data-grappa-ssim]').count(), 0);
    const advance = async (frame) => {
      await page.bringToFront();
      await page.locator('.scene-play').click();
      await page.locator('.scene-stage').scrollIntoViewIfNeeded();
      await page.waitForFunction(
        (f) => Number(document.querySelector('.scene-player').getAttribute('data-frame')) > f,
        frame + 4,
      );
      await page.locator('.scene-play').click();
    };
    const native = JSON.parse(
      fs.readFileSync('presentation/task-explorer/imaging101-mri-grappa/measurement.json', 'utf8'),
    );
    const helper = JSON.parse(
      fs.readFileSync('presentation/task-explorer/imaging101-mri-grappa/helper.json', 'utf8'),
    );
    const pair = (v) => `${v[0].toPrecision(7)} + i(${v[1].toPrecision(7)})`;
    await page.locator('[data-story-step="0"]').click();
    await absent();
    assert.equal(await scene.locator('img,canvas,image').count(), 0);
    const slider = scene.locator('input[type="range"]');
    for (const [index, key] of [
      [0, 'Home'],
      [1, 'ArrowRight'],
      [7, 'End'],
    ]) {
      await slider.focus();
      await slider.press(key);
      assert.equal(await slider.inputValue(), String(index));
      const text = await scene.innerText();
      assert.ok(text.includes(`Coil ${index} · native center [64,64]`));
      assert.ok(text.includes(pair(native.native_center_kspace[index]) + ' a.u.'));
      assert.ok(text.includes(pair(native.native_center_sensitivity[index]) + ' a.u.'));
      const expected = native.symbolic_rule_retained_rows.map((y) => [
        '0',
        String(y),
        '128',
        '1',
        y >= 54 && y <= 73 ? '#eeb989' : '#73c7e6',
      ]);
      expected.push(['0', '51', '128', '1', '#92d9ae']);
      assert.deepEqual(
        await scene
          .locator('svg rect')
          .evaluateAll((els) =>
            els
              .slice(1)
              .map((e) => ['x', 'y', 'width', 'height', 'fill'].map((k) => e.getAttribute(k))),
          ),
        expected,
      );
      assert.match(
        await scene.locator('figcaption').innerText(),
        /Illustrated rule.*rows \(dim 0\) down.*columns right/,
      );
      assert.match(
        text,
        /74\/128.*57\.8125%.*nominal R=2.*Rule illustration only.*raw archive is fully sampled/is,
      );
      await capture(`coil-${index}`);
      await absent();
    }
    await advance(0);
    await page.locator('[data-story-step="0"]').click();
    assert.equal(await slider.inputValue(), '0');
    const hi = plan.beats.findIndex((b) => b.scene === 'helper');
    await page.locator(`[data-story-step="${hi}"]`).click();
    await absent();
    const truth = () =>
      scene.getByRole('button', { name: 'Reveal source full-data target', exact: true });
    await truth().click();
    assert.match(
      await scene.locator('[data-grappa-full-target]').innerText(),
      /row 51, col 64.*8 coils.*already solver-visible.*not GRAPPA estimate or private evaluator/is,
    );
    assert.deepEqual(
      await scene.locator('[data-grappa-full-target] span').allTextContents(),
      helper.native_full_target_pairs.map((v, c) => `coil ${c}: ${pair(v)}`),
    );
    await capture('source-target');
    for (const tier of ['L1', 'L2', 'L3']) {
      await scene.getByRole('button', { name: tier, exact: true }).click();
      assert.equal(
        await scene.getByRole('button', { name: tier, exact: true }).getAttribute('aria-pressed'),
        'true',
      );
      assert.equal(await scene.locator('[data-grappa-tier]').innerText(), helper.tiers[tier]);
    }
    await scene.getByRole('button', { name: 'Hide source full-data target', exact: true }).click();
    await absent();
    await advance(plan.beats[hi].startFrame);
    await truth().click();
    await page.locator(`[data-story-step="${hi}"]`).click();
    await absent();
    assert.equal(
      await scene.getByRole('button', { name: 'L1', exact: true }).getAttribute('aria-pressed'),
      'true',
    );
    await truth().click();
    await page.locator('[data-story-step="0"]').click();
    await absent();
    await page.locator(`[data-story-step="${hi}"]`).click();
    await absent();
    await truth().click();
    await page.locator('.scene-reset').click();
    await absent();
    await page.locator(`[data-story-step="${hi}"]`).click();
    await absent();
    const op = plan.beats.findIndex((b) => b.scene === 'operation');
    assert.equal(plan.beats.filter((b) => b.scene === 'operation').length, 1);
    await page.locator(`[data-story-step="${op}"]`).click();
    // Independently solved inverse smoothstep and earliest-tie rule for288-frame canonical beat.
    const nearest = [576, 687, 752, 863];
    assert.equal(plan.beats[op].startFrame, 576);
    assert.equal(plan.beats[op].frames, 288);
    for (let step = 0; step < 4; step++)
      for (let method = 0; method < 3; method++) {
        await scene.locator(`[data-grappa-step="${step}"]`).click();
        const name = ['calibration', 'interpolation', 'combination'][method];
        await scene
          .getByRole('group', { name: 'GRAPPA source mechanism', exact: true })
          .getByRole('button', { name, exact: true })
          .click();
        assert.equal(
          Number(await page.locator('.scene-player').getAttribute('data-frame')),
          nearest[step],
        );
        assert.equal(
          await scene.locator(`[data-grappa-step="${step}"]`).getAttribute('aria-pressed'),
          'true',
        );
        assert.equal(await scene.getAttribute('data-grappa-scene'), 'operation');
        assert.equal(
          await scene
            .locator('[data-grappa-current-step]')
            .getAttribute('data-grappa-current-step'),
          String(step),
        );
        assert.match(
          await scene.locator('[data-grappa-method]').innerText(),
          [
            /λ₀=0\.01.*n_sources.*no weight matrix/is,
            /first-coil.*True acquired zero.*exact zeros=0/is,
            /spatial axes \(0,1\).*forward 1\/128.*coil axis 2 excluded.*sqrt.*bare phantom/is,
          ][method],
        );
        assert.deepEqual(
          await scene
            .locator('[data-kind]')
            .evaluateAll((els) => els.map((e) => [e.getAttribute('data-kind'), e.textContent])),
          Array.from({ length: 25 }, (_, i) => [
            i === 12 ? 'target' : Math.floor(i / 5) % 2 === 1 ? 'source' : 'hole',
            i === 12 ? 'T' : Math.floor(i / 5) % 2 === 1 ? 'S' : '·',
          ]),
        );
        assert.match(
          await scene.innerText(),
          /No calibration solve, missing samples or reconstructed image computed/,
        );
        await capture(`contract-${step}-${method}`);
        await absent();
      }
    await scene.locator('[data-grappa-step="0"]').click();
    await scene.getByRole('button', { name: 'combination', exact: true }).click();
    await advance(nearest[0]);
    await scene.locator('[data-grappa-step="0"]').click();
    assert.equal(
      await scene
        .getByRole('button', { name: 'calibration', exact: true })
        .getAttribute('aria-pressed'),
      'true',
    );
    const oi = plan.beats.findIndex((b) => b.scene === 'output');
    await page.locator(`[data-story-step="${oi}"]`).click();
    await absent();
    assert.match(
      await scene.innerText(),
      /output\/reconstruction\.npy.*128×128 real magnitude image.*UNSUBMITTED.*Synthetic phantom is not an acquired patient brain/is,
    );
    assert.equal(await scene.locator('img,canvas,image').count(), 0);
    assert.equal(await scene.locator('[data-grappa-format]').count(), 0);
    await scene.getByRole('button', { name: 'Inspect artifact format', exact: true }).click();
    assert.match(
      await scene.locator('[data-grappa-format]').innerText(),
      /real 128 x 128 NPY.*grappa_reconstruction\.npz.*1 x 128 x 128 batch.*No participant/is,
    );
    await capture('output-contract');
    const li = plan.beats.findIndex((b) => b.scene === 'limits');
    await page.locator(`[data-story-step="${li}"]`).click();
    await absent();
    for (const rule of ['metric', 'reference selection', 'threshold']) {
      await scene.getByRole('button', { name: rule, exact: true }).click();
      assert.equal(
        await scene.getByRole('button', { name: rule, exact: true }).getAttribute('aria-pressed'),
        'true',
      );
      assert.match(
        await scene.locator('[data-grappa-rule]').innerText(),
        {
          metric: /zero range.*infinity.*16384.*No flux scaling.*1e-12.*1e-30/is,
          'reference selection':
            /ground_truth\.npy.*full-data RSS.*ground_truth\.npz.*bare phantom.*unequal pixel values/is,
          threshold: /nested grappa\/zerofill.*no top-level.*passed=None.*not displayed/is,
        }[rule],
      );
      await capture(`rule-${rule.replaceAll(' ', '-')}`);
    }
    const reveal = () =>
      scene.getByRole('button', { name: 'Reveal SSIM implementation difference', exact: true });
    await reveal().click();
    assert.match(
      await scene.locator('[data-grappa-ssim]').innerText(),
      /also returns infinity.*skimage local.*whole-image.*max\(reference\).*Without a filesystem.*flux-normalizes.*relative L2/is,
    );
    await capture('ssim-revealed');
    await scene
      .getByRole('button', { name: 'Hide SSIM implementation difference', exact: true })
      .click();
    await absent();
    await advance(plan.beats[li].startFrame);
    await reveal().click();
    await page.locator(`[data-story-step="${li}"]`).click();
    await absent();
    assert.equal(
      await scene
        .getByRole('button', { name: 'reference selection', exact: true })
        .getAttribute('aria-pressed'),
      'true',
    );
    await reveal().click();
    await page.locator('.scene-reset').click();
    await absent();
    await page.locator(`[data-story-step="${li}"]`).click();
    await absent();
    await reveal().click();
    await page.locator(`[data-story-step="${oi}"]`).click();
    await absent();
    assert.equal(await scene.locator('[data-grappa-format]').count(), 0);
    await page.locator(`[data-story-step="${li}"]`).click();
    await absent();
    await page.locator('.scene-reset').click();
  }
  if (plan.recipe === 'imaging-dynamic-mri-v1') {
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    const scene = page.locator('[data-dynamic-mri-scene]');
    const capture = async (name) =>
      page.locator('.scene-player').screenshot({ path: path.join(output, `${label}-${name}.png`) });
    const absent = async () =>
      assert.equal(
        await page
          .locator('[data-dynamic-mri-source-series], [data-dynamic-mri-acquisition]')
          .count(),
        0,
      );
    const advance = async (frame) => {
      await page.bringToFront();
      await page.locator('.scene-stage').scrollIntoViewIfNeeded();
      await page.locator('.scene-play').click();
      await page.waitForFunction(
        (f) => Number(document.querySelector('.scene-player').getAttribute('data-frame')) > f,
        frame + 4,
      );
      await page.locator('.scene-play').click();
    };
    const native = JSON.parse(
      fs.readFileSync(
        'presentation/task-explorer/imaging101-mri-dynamic-dce/measurement.json',
        'utf8',
      ),
    );
    const helper = JSON.parse(
      fs.readFileSync('presentation/task-explorer/imaging101-mri-dynamic-dce/helper.json', 'utf8'),
    );
    const bytes = Buffer.from(native.mask_bits_base64, 'base64');
    assert.equal(bytes.length, 40960);
    await page.locator('[data-story-step="0"]').click();
    await absent();
    assert.equal(await scene.locator('img,canvas,image').count(), 0);
    const slider = scene.locator('input[type="range"]');
    for (const [index, key] of [
      [0, 'Home'],
      [1, 'ArrowRight'],
      [19, 'End'],
    ]) {
      await slider.focus();
      await slider.press(key);
      assert.equal(await slider.inputValue(), String(index));
      const text = await scene.innerText();
      assert.ok(
        text.includes(
          `Frame ${index} · ${native.time_seconds[index].toFixed(2)} synthetic seconds`,
        ),
      );
      assert.ok(text.includes('2457/16384'));
      assert.ok(
        text.includes(
          native.native_kspace_center_64_64[index].map((v) => v.toPrecision(5)).join(' + i ') +
            ' a.u.',
        ),
      );
      const expected = [];
      for (let y = 0; y < 128; y++)
        for (let x = 0; x < 128; x++) {
          const i = index * 16384 + y * 128 + x;
          if ((bytes[Math.floor(i / 8)] >>> (i % 8)) & 1)
            expected.push([String(x), String(y), '1', '1', '#73c7e6']);
        }
      assert.equal(expected.length, 2457);
      assert.deepEqual(
        await scene
          .locator('svg rect')
          .evaluateAll((els) =>
            els
              .slice(1)
              .map((e) => ['x', 'y', 'width', 'height', 'fill'].map((k) => e.getAttribute(k))),
          ),
        expected,
      );
      assert.match(
        await scene.locator('figcaption').innerText(),
        /128×128 k-space index grid.*rows down, columns right/,
      );
      assert.match(text, /14\.9963%.*not 25%.*No coil dimension.*physical spacing/is);
      await capture(`frame-${index}`);
      await absent();
    }
    await advance(0);
    await page.locator('[data-story-step="0"]').click();
    assert.equal(await slider.inputValue(), '0');
    const hi = plan.beats.findIndex((b) => b.scene === 'helper');
    await page.locator(`[data-story-step="${hi}"]`).click();
    await absent();
    const truth = () =>
      scene.getByRole('button', { name: 'Reveal synthetic source series', exact: true });
    await truth().click();
    assert.match(
      await scene.locator('[data-dynamic-mri-source-series]').innerText(),
      /\(49,79\).*already solver-visible.*not reconstruction.*ROI average.*perfusion/is,
    );
    assert.deepEqual(
      await scene.locator('[data-dynamic-mri-source-series] span').allTextContents(),
      helper.source_pixel_series.map((v, i) => `t${i}: ${v.toPrecision(4)} a.u.`),
    );
    await capture('source-series');
    for (const tier of ['L1', 'L2', 'L3']) {
      await scene.getByRole('button', { name: tier, exact: true }).click();
      assert.equal(
        await scene.getByRole('button', { name: tier, exact: true }).getAttribute('aria-pressed'),
        'true',
      );
      assert.equal(await scene.locator('[data-dynamic-mri-tier]').innerText(), helper.tiers[tier]);
    }
    await scene.getByRole('button', { name: 'Hide synthetic source series', exact: true }).click();
    await absent();
    await advance(plan.beats[hi].startFrame);
    await truth().click();
    await page.locator(`[data-story-step="${hi}"]`).click();
    await absent();
    assert.equal(
      await scene.getByRole('button', { name: 'L1', exact: true }).getAttribute('aria-pressed'),
      'true',
    );
    await truth().click();
    await page.locator('[data-story-step="0"]').click();
    await absent();
    await page.locator(`[data-story-step="${hi}"]`).click();
    await absent();
    await truth().click();
    await page.locator('.scene-reset').click();
    await absent();
    await page.locator(`[data-story-step="${hi}"]`).click();
    await absent();
    const ops = plan.beats.filter((b) => b.scene === 'operation');
    assert.equal(ops.length, 4);
    await page.locator(`[data-story-step="${plan.beats.indexOf(ops[0])}"]`).click();
    for (let step = 0; step < 4; step++)
      for (let method = 0; method < 3; method++) {
        await scene.locator(`[data-dynamic-mri-operation-step="${step}"]`).click();
        await scene
          .getByRole('group', { name: 'Dynamic MRI source method', exact: true })
          .getByRole('button', {
            name: ['zero filled', 'temporal tv', 'prox'][method],
            exact: true,
          })
          .click();
        assert.equal(
          Number(await page.locator('.scene-player').getAttribute('data-frame')),
          ops[step].startFrame +
            [0, Math.floor((ops[step].frames - 1) / 2), ops[step].frames - 1][method],
        );
        assert.equal(
          await scene
            .locator(`[data-dynamic-mri-operation-step="${step}"]`)
            .getAttribute('aria-pressed'),
          'true',
        );
        assert.match(
          await scene.locator('[data-dynamic-mri-step]').innerText(),
          [
            /Remove batch axis.*time and grid/,
            /y_t=M_t F\(x_t\).*masked complex noise/,
            /19 intervals/,
            /measured data consistency.*temporal TV/,
          ][step],
        );
        assert.match(
          await scene.locator('[data-dynamic-mri-method]').innerText(),
          [
            /abs.*inverseFFT.*no baseline image/is,
            /temporal_tv_pgd.*0\.001.*200.*1e-5.*ADMM conflicts/is,
            /complex temporal differences.*no explicit magnitude-only.*abs\(x\)/is,
          ][method],
        );
        assert.match(
          await scene.innerText(),
          /19 adjacent-index differences.*no division by time.*\[1,3,2\].*\[2,−1\].*not concentration/is,
        );
        await capture(`contract-${step}-${method}`);
        await absent();
      }
    const oi = plan.beats.findIndex((b) => b.scene === 'output');
    await page.locator(`[data-story-step="${oi}"]`).click();
    await absent();
    assert.match(
      await scene.innerText(),
      /output\/reconstruction\.npy.*20×128×128 real magnitude sequence.*UNSUBMITTED.*not contrast concentration/is,
    );
    assert.equal(await scene.locator('img,canvas,image').count(), 0);
    assert.equal(await scene.locator('[data-dynamic-mri-format]').count(), 0);
    await scene.getByRole('button', { name: 'Inspect artifact format', exact: true }).click();
    assert.match(
      await scene.locator('[data-dynamic-mri-format]').innerText(),
      /single real numeric array.*tv_reconstruction\.npz.*not participant/is,
    );
    await capture('output-contract');
    const li = plan.beats.findIndex((b) => b.scene === 'limits');
    await page.locator(`[data-story-step="${li}"]`).click();
    await absent();
    for (const rule of ['metric', 'task metric', 'threshold']) {
      await scene.getByRole('button', { name: rule, exact: true }).click();
      assert.equal(
        await scene.getByRole('button', { name: rule, exact: true }).getAttribute('aria-pressed'),
        'true',
      );
      assert.match(
        await scene.locator('[data-dynamic-mri-rule]').innerText(),
        {
          metric: /327680.*global max.*uncentered cosine.*no flux scaling.*dynamic_images/is,
          'task metric': /16384 pixels.*20 frames.*not 20 patients.*0.*infinity/is,
          threshold: /metrics_detail.*no metrics\.json boundary.*No generic pass\/fail/is,
        }[rule],
      );
      await capture(`rule-${rule.replaceAll(' ', '-')}`);
    }
    const acquisition = () =>
      scene.getByRole('button', { name: 'Reveal acquisition mismatch', exact: true });
    await acquisition().click();
    assert.match(
      await scene.locator('[data-dynamic-mri-acquisition]').innerText(),
      /noise 0\.005.*sampled points.*0\.02 and 25%.*not regenerate/is,
    );
    await capture('acquisition-revealed');
    await scene.getByRole('button', { name: 'Hide acquisition mismatch', exact: true }).click();
    await absent();
    await advance(plan.beats[li].startFrame);
    await acquisition().click();
    await page.locator(`[data-story-step="${li}"]`).click();
    await absent();
    assert.equal(
      await scene.getByRole('button', { name: 'metric', exact: true }).getAttribute('aria-pressed'),
      'true',
    );
    await acquisition().click();
    await page.locator('.scene-reset').click();
    await absent();
    await page.locator(`[data-story-step="${li}"]`).click();
    await absent();
    await acquisition().click();
    await page.locator(`[data-story-step="${oi}"]`).click();
    await absent();
    assert.equal(await scene.locator('[data-dynamic-mri-format]').count(), 0);
    await page.locator(`[data-story-step="${li}"]`).click();
    await absent();
    await page.locator('.scene-reset').click();
  }
  if (plan.recipe === 'imaging-eit-v1') {
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    const scene = page.locator('[data-eit-scene]');
    const capture = async (name) =>
      page.locator('.scene-player').screenshot({ path: path.join(output, `${label}-${name}.png`) });
    const absent = async () =>
      assert.equal(
        await page.locator('[data-eit-source-truth], [data-eit-task-metric]').count(),
        0,
      );
    const advance = async (frame) => {
      await page.locator('.scene-play').click();
      await page.locator('.scene-stage').scrollIntoViewIfNeeded();
      await page.waitForFunction(
        (f) => Number(document.querySelector('.scene-player').getAttribute('data-frame')) > f,
        frame + 4,
      );
      await page.locator('.scene-play').click();
    };
    await page.locator('[data-story-step="0"]').click();
    await absent();
    const native = JSON.parse(
      fs.readFileSync(
        'presentation/task-explorer/imaging101-eit-conductivity-reconstruction/measurement.json',
        'utf8',
      ),
    );
    assert.equal(await scene.locator('svg polygon').count(), 686);
    assert.equal(await scene.locator('svg [data-electrode]').count(), 16);
    assert.equal(await scene.locator('img,canvas,image').count(), 0);
    assert.deepEqual(
      await scene
        .locator('svg polygon')
        .evaluateAll((els) => els.map((e) => e.getAttribute('points'))),
      native.element.map((tri) =>
        tri
          .map((i) => `${160 + native.node[i][0] * 132},${154 - native.node[i][1] * 132}`)
          .join(' '),
      ),
    );
    assert.ok(
      await scene.locator('svg').evaluate((svg) =>
        Array.from(svg.querySelectorAll('text')).every((t) => {
          const b = t.getBBox(),
            v = svg.viewBox.baseVal;
          return (
            b.x >= v.x &&
            b.y >= v.y &&
            b.x + b.width <= v.x + v.width &&
            b.y + b.height <= v.y + v.height
          );
        }),
      ),
    );
    assert.match(
      await scene.innerText(),
      /376 nodes.*686 triangles.*16 electrodes.*x right\/y up.*Point electrode nodes.*no finite contact/is,
    );
    const slider = scene.locator('input[type="range"]');
    for (const [index, key] of [
      [0, 'Home'],
      [1, 'ArrowRight'],
      [207, 'End'],
    ]) {
      await slider.focus();
      await slider.press(key);
      const row = native.meas_mat[index],
        drive = native.ex_mat[row[2]];
      assert.equal(await slider.inputValue(), String(index));
      const text = await scene.innerText();
      assert.ok(
        text.includes(`Row ${index}: drive ${drive.join('→')}; measure ${row[0]}−${row[1]}`),
      );
      assert.ok(text.includes(`${native.v0[index].toPrecision(7)} V*`));
      assert.ok(text.includes(`${native.v1[index].toPrecision(7)} V*`));
      const roles = Array.from({ length: 16 }, (_, e) =>
        e === drive[0]
          ? 'inject'
          : e === drive[1]
            ? 'return'
            : e === row[0] || e === row[1]
              ? 'measure'
              : 'idle',
      );
      assert.deepEqual(
        await scene
          .locator('[data-electrode]')
          .evaluateAll((els) => els.map((e) => e.getAttribute('data-role'))),
        roles,
      );
      const colors = { inject: '#f5b75b', return: '#e087ac', measure: '#73c7e6', idle: '#abbec7' };
      assert.deepEqual(
        await scene
          .locator('[data-electrode] circle')
          .evaluateAll((els) => els.map((e) => e.getAttribute('fill'))),
        roles.map((r) => colors[r]),
      );
      assert.match(
        await scene.locator('figcaption').innerText(),
        /376 nodes.*686 triangles.*16 electrodes/,
      );
      await capture(`row-${index}`);
      await absent();
    }
    await advance(0);
    await page.locator('[data-story-step="0"]').click();
    assert.equal(await slider.inputValue(), '0');
    const hi = plan.beats.findIndex((b) => b.scene === 'helper');
    await page.locator(`[data-story-step="${hi}"]`).click();
    await absent();
    const truth = () =>
      scene.getByRole('button', { name: 'Reveal source conductivity truth', exact: true });
    await truth().click();
    assert.match(
      await page.locator('[data-eit-source-truth]').innerText(),
      /already solver-visible.*not prediction or private.*8\/686 elements.*678.*12 elements.*16 elements.*658.*8 elements.*1000/is,
    );
    await capture('source-truth');
    for (const tier of ['L1', 'L2', 'L3']) {
      await scene.getByRole('button', { name: tier, exact: true }).click();
      assert.equal(
        await scene.getByRole('button', { name: tier, exact: true }).getAttribute('aria-pressed'),
        'true',
      );
      assert.match(
        await scene.locator('[data-eit-tier]').innerText(),
        {
          L1: /README.*data.*source anomaly/i,
          L2: /L1.*plan\/approach/,
          L3: /L1.*complete plan.*software design/,
        }[tier],
      );
    }
    await scene
      .getByRole('button', { name: 'Hide source conductivity truth', exact: true })
      .click();
    await absent();
    await advance(plan.beats[hi].startFrame);
    await truth().click();
    await page.locator(`[data-story-step="${hi}"]`).click();
    await absent();
    assert.equal(
      await scene.getByRole('button', { name: 'L1', exact: true }).getAttribute('aria-pressed'),
      'true',
    );
    await truth().click();
    await page.locator('[data-story-step="0"]').click();
    await absent();
    await page.locator(`[data-story-step="${hi}"]`).click();
    await absent();
    await truth().click();
    await page.locator('.scene-reset').click();
    await absent();
    await page.locator(`[data-story-step="${hi}"]`).click();
    await absent();
    const ops = plan.beats.filter((b) => b.scene === 'operation');
    assert.equal(ops.length, 4);
    await page.locator(`[data-story-step="${plan.beats.indexOf(ops[0])}"]`).click();
    for (let step = 0; step < 4; step++)
      for (let method = 0; method < 3; method++) {
        await scene.locator(`[data-eit-operation-step="${step}"]`).click();
        await scene.locator(`[data-eit-method-branch="${method}"]`).click();
        const local = [0, Math.floor((ops[step].frames - 1) / 2), ops[step].frames - 1][method];
        assert.equal(
          Number(await page.locator('.scene-player').getAttribute('data-frame')),
          ops[step].startFrame + local,
        );
        assert.equal(
          await scene.locator(`[data-eit-operation-step="${step}"]`).getAttribute('aria-pressed'),
          'true',
        );
        assert.equal(
          await scene.locator(`[data-eit-method-branch="${method}"]`).getAttribute('aria-pressed'),
          'true',
        );
        assert.match(
          await scene.locator('[data-eit-method]').innerText(),
          [/BP.*376 mesh nodes/, /JAC.*686 mesh elements/, /GREIT.*32x32 grid/][method],
        );
        const text = await scene.innerText();
        assert.match(
          text,
          [
            /\(v1-v0\)\/sign\(v0.real\).*main multiplies 192/is,
            /\(v1-v0\)\/abs\(v0\).*Kotre.*0\.5.*0\.01/is,
            /\(v1-v0\)\/abs\(v0\).*sigmoid.*0\.5.*0\.01/is,
          ][method],
        );
        if (step === 1) assert.match(text, /3−1 = 2.*13−11 = 2.*Neither.*native patient/is);
        if (step === 2)
          assert.match(text, /δV ≈ J δσ.*local approximation.*not a demonstrated guarantee/is);
        await capture(`contract-${step}-${method}`);
        await absent();
      }
    const oi = plan.beats.findIndex((b) => b.scene === 'output');
    await page.locator(`[data-story-step="${oi}"]`).click();
    await absent();
    assert.match(
      await scene.innerText(),
      /output\/reconstruction\.npy.*UNSUBMITTED.*376 node.*686 element.*32×32.*not this participant/is,
    );
    assert.equal(await scene.locator('[data-eit-format]').count(), 0);
    await scene
      .getByRole('button', { name: 'Inspect generic output contract', exact: true })
      .click();
    assert.match(
      await scene.locator('[data-eit-format]').innerText(),
      /One real numeric array.*shape\/key-ranked.*squeeze dimensions>2/is,
    );
    await capture('output-contract');
    const li = plan.beats.findIndex((b) => b.scene === 'limits');
    await page.locator(`[data-story-step="${li}"]`).click();
    await absent();
    for (const rule of ['metric', 'reference selection', 'threshold']) {
      await scene.getByRole('button', { name: rule, exact: true }).click();
      assert.equal(
        await scene.getByRole('button', { name: rule, exact: true }).getAttribute('aria-pressed'),
        'true',
      );
      assert.match(
        await scene.locator('[data-eit-rule]').innerText(),
        {
          metric: /NRMSE.*zero range.*infinity.*uncentered cosine.*1e-30.*No flux normalization/is,
          'reference selection':
            /\(1,686\).*bp_perm_anomaly.*\(376,\).*ground_truth_bp.*\(686,\).*mismatch/is,
          threshold:
            /nested bp\/jac_dynamic.*no top-level ncc_boundary or nrmse_boundary.*passed=None/is,
        }[rule],
      );
      await capture(`rule-${rule.replaceAll(' ', '-')}`);
    }
    const metric = () =>
      scene.getByRole('button', { name: 'Reveal source method metric rule', exact: true });
    await metric().click();
    assert.match(
      await scene.locator('[data-eit-task-metric]').innerText(),
      /sum\(abs\(gt\)\).*L2 error.*NCC centers.*BP compares node.*JAC element.*GREIT metrics skipped/is,
    );
    await capture('metric-revealed');
    await scene
      .getByRole('button', { name: 'Hide source method metric rule', exact: true })
      .click();
    await absent();
    await advance(plan.beats[li].startFrame);
    await metric().click();
    await page.locator(`[data-story-step="${li}"]`).click();
    await absent();
    assert.equal(
      await scene.getByRole('button', { name: 'metric', exact: true }).getAttribute('aria-pressed'),
      'true',
    );
    await metric().click();
    await page.locator('.scene-reset').click();
    await absent();
    await page.locator(`[data-story-step="${li}"]`).click();
    await absent();
    await metric().click();
    await page.locator(`[data-story-step="${oi}"]`).click();
    await absent();
    assert.equal(await scene.locator('[data-eit-format]').count(), 0);
    await page.locator(`[data-story-step="${li}"]`).click();
    await absent();
    await page.locator('.scene-reset').click();
  }
  if (plan.recipe === 'imaging101-poisson-v1') {
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    const scene = page.locator('[data-imaging-poisson-scene]');
    const capture = async (name) =>
      page.locator('.scene-player').screenshot({ path: path.join(output, `${label}-${name}.png`) });
    const absent = async () =>
      assert.equal(await page.locator('[data-imaging-poisson-reference-revealed]').count(), 0);
    await page.locator('[data-story-step="0"]').click();
    await absent();
    assert.match(
      await scene.innerText(),
      /Matching 300-photon noisy input missing.*256 views × 367 channels.*no patient data.*1000-photon arrays stay separate/is,
    );
    assert.equal(await scene.locator('img').count(), 0);
    assert.deepEqual(
      await scene
        .locator('svg path')
        .evaluateAll((els) => els.map((e) => e.getAttribute('stroke'))),
      ['#88b4e0', '#88b4e0', '#88b4e0'],
    );
    assert.match(
      await scene.locator('figcaption').innerText(),
      /Blue solid lines = symbolic rays.*slate box = attenuation object.*Expected λ differs.*random count Y/is,
    );
    const ops = plan.beats.filter((b) => b.scene === 'operation');
    assert.equal(ops.length, 3);
    await page.locator(`[data-story-step="${plan.beats.indexOf(ops[0])}"]`).click();
    for (let j = 0; j < 3; j++) {
      await scene.locator(`[data-imaging-poisson-step="${j}"]`).click();
      assert.equal(
        Number(await page.locator('.scene-player').getAttribute('data-frame')),
        ops[j].startFrame,
      );
      assert.equal(
        await scene.locator(`[data-imaging-poisson-step="${j}"]`).getAttribute('aria-pressed'),
        'true',
      );
      assert.match(
        await scene.innerText(),
        [
          /λ=300exp.*Y~Poisson.*Variance λ.*cm⁻¹.*mm⁻¹ unresolved/is,
          /Illustrative Y=300.*max\(Y,1\)=300.*−log\(count\/300\)=0\.000000.*weight=300.*authored counts, no random draw.*Zero\/one indistinguishable/is,
          /Toy weights: 1\.000 \/ 0\.333 \/ 0\.003.*max-normalizes.*proximal-gradient TV.*No run\/convergence.*Stored \(1,V,C\).*SVMBIR \(V,1,C\)/is,
        ][j],
      );
      await capture(`contract-${j}`);
      await absent();
    }
    await scene.locator('[data-imaging-poisson-step="1"]').click();
    for (let j = 0; j < 3; j++) {
      await scene.locator(`[data-imaging-poisson-count="${j}"]`).click();
      const local = [0, Math.floor((ops[1].frames - 1) / 2), ops[1].frames - 1][j];
      assert.equal(
        Number(await page.locator('.scene-player').getAttribute('data-frame')),
        ops[1].startFrame + local,
      );
      assert.equal(
        await scene.locator(`[data-imaging-poisson-count="${j}"]`).getAttribute('aria-pressed'),
        'true',
      );
      const counts = [300, 100, 0],
        floored = [300, 100, 1];
      assert.ok(
        (await scene.innerText()).includes(`Illustrative Y=${counts[j]} →max(Y,1)=${floored[j]}`),
      );
      assert.ok(
        (await scene.innerText()).includes(
          `−log(count/300)=${(-Math.log(floored[j] / 300)).toFixed(6)}; weight=${floored[j]}`,
        ),
      );
      await capture(`count-${j}`);
      await absent();
    }
    await scene.locator('[data-imaging-poisson-step="2"]').click();
    for (const mode of ['counts', 'uniform']) {
      const frame = Number(await page.locator('.scene-player').getAttribute('data-frame'));
      await scene.locator(`[data-imaging-poisson-weight="${mode}"]`).click();
      assert.equal(Number(await page.locator('.scene-player').getAttribute('data-frame')), frame);
      assert.match(
        await scene.innerText(),
        mode === 'counts'
          ? /Toy weights: 1\.000 \/ 0\.333 \/ 0\.003/
          : /Toy weights: 1\.000 \/ 1\.000 \/ 1\.000/,
      );
      await capture(`weight-${mode}`);
    }
    await page.locator('.scene-play').click();
    await page.locator('.scene-stage').scrollIntoViewIfNeeded();
    await page.waitForFunction(
      (f) => Number(document.querySelector('.scene-player').getAttribute('data-frame')) > f,
      ops[2].startFrame + 4,
    );
    await page.locator('.scene-play').click();
    await page.locator(`[data-story-step="${plan.beats.indexOf(ops[2])}"]`).click();
    assert.equal(
      await scene.locator('[data-imaging-poisson-weight="counts"]').getAttribute('aria-pressed'),
      'true',
    );
    const oi = plan.beats.findIndex((b) => b.scene === 'output');
    await page.locator(`[data-story-step="${oi}"]`).click();
    await absent();
    assert.match(
      await scene.locator('code').innerText(),
      /output\/reconstruction\.npy.*real 256×256/,
    );
    assert.match(await scene.innerText(), /No reconstructed image, GT, score or model outcome/is);
    const ri = plan.beats.findIndex((b) => b.scene === 'reference');
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    const reveal = () =>
      scene.getByRole('button', { name: 'Reveal fixture and rules', exact: true });
    await reveal().click();
    const ref = page.locator('[data-imaging-poisson-reference-revealed]');
    const native = JSON.parse(
      fs.readFileSync(
        'presentation/task-explorer/imaging101-ct-poisson-lowdose/reference.json',
        'utf8',
      ),
    ).expected_count_subset.values;
    const expected = native.flat().map((v) => {
      const g = Math.round((v / 300) * 255);
      return `rgb(${g},${g},${g})`;
    });
    assert.deepEqual(
      await ref.locator('svg rect').evaluateAll((els) => els.map((e) => e.getAttribute('fill'))),
      expected,
    );
    assert.deepEqual(
      await ref.locator('svg text').evaluateAll((els) =>
        els.map((e) => {
          const b = e.getBBox(),
            v = e.ownerSVGElement.viewBox.baseVal;
          return (
            b.x >= v.x &&
            b.y >= v.y &&
            b.x + b.width <= v.x + v.width &&
            b.y + b.height <= v.y + v.height
          );
        }),
      ),
      [true, true, true, true],
    );
    assert.equal(expected.length, 256);
    assert.equal(await ref.locator('img').count(), 0);
    assert.match(
      await ref.innerText(),
      /Expected photons\/bin.*Black 0 → white 300.*Views 120–135.*detectors 175–190.*native 16×16 subset, no rescale.*Mathematical expectation, never noisy realization/is,
    );
    for (let j = 0; j < 3; j++) {
      await ref.locator(`[data-imaging-poisson-metric="${j}"]`).click();
      assert.equal(
        await ref.locator(`[data-imaging-poisson-metric="${j}"]`).getAttribute('aria-pressed'),
        'true',
      );
      assert.match(
        await ref.innerText(),
        [
          /Filesystem generic: full256².*constant reference gives infinity, no flux normalization/is,
          /Separate task-aware helper: central204² =41616\/65536 pixels.*constant reference gives 0\.0/is,
          /No-filesystem fallback: output flux scaled to \.npy truth, relative L2 NRMSE.*different route/is,
        ][j],
      );
      assert.match(
        await ref.innerText(),
        /No metrics\.json thresholds retained.*no score or pass\/fail.*truth to solver.*educational boundary/is,
      );
      await capture(`scorer-${j}`);
    }
    await capture('fixture-revealed');
    await scene.getByRole('button', { name: 'Cover fixture and rules', exact: true }).click();
    await absent();
    await page.locator('.scene-play').click();
    await page.locator('.scene-stage').scrollIntoViewIfNeeded();
    await page.waitForFunction(
      (f) => Number(document.querySelector('.scene-player').getAttribute('data-frame')) > f,
      plan.beats[ri].startFrame + 4,
    );
    await page.locator('.scene-play').click();
    await reveal().click();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    await reveal().click();
    assert.equal(
      await ref.locator('[data-imaging-poisson-metric="0"]').getAttribute('aria-pressed'),
      'true',
    );
    await page.locator('.scene-reset').click();
    await absent();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    await reveal().click();
    await page
      .locator(`[data-story-step="${plan.beats.findIndex((b) => b.scene === 'limits')}"]`)
      .click();
    await absent();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    await reveal().click();
    await page.locator('[data-story-step="0"]').click();
    await absent();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    await page.locator('.scene-reset').click();
  }
  if (plan.recipe === 'bcer-grappa-v1') {
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    const scene = page.locator('[data-bcer-grappa-scene]');
    const capture = async (name) =>
      page.locator('.scene-player').screenshot({ path: path.join(output, `${label}-${name}.png`) });
    const absent = async () =>
      assert.equal(await page.locator('[data-bcer-grappa-reference-revealed]').count(), 0);
    const mask = async (mode) => {
      const fills = await scene
        .locator('svg rect')
        .evaluateAll((els) => els.map((e) => e.getAttribute('fill')));
      assert.equal(fills.length, 8 * 32);
      const expected = Array.from({ length: 8 }, () =>
        Array.from({ length: 32 }, (_, ky) =>
          ky >= 4 && ky < 28 ? '#57d1cc' : mode === 1 || ky % 2 === 0 ? '#88b4e0' : '#526373',
        ),
      ).flat();
      assert.deepEqual(fills, expected);
      assert.match(
        await scene.locator('figcaption').innerText(),
        /Blue = sampled outside ACS.*teal = central ACS24.*gray = missing.*frequency samples, not missing image pixels/is,
      );
      assert.equal(await scene.locator('img').count(), 0);
    };
    await page.locator('[data-story-step="0"]').click();
    await absent();
    await mask(0);
    assert.match(
      await scene.innerText(),
      /No matching cardiac H5.*8 kx × 32 ky × 2 coils.*No representative prostate image/is,
    );
    const ops = plan.beats.filter((b) => b.scene === 'operation');
    assert.equal(ops.length, 3);
    await page.locator(`[data-story-step="${plan.beats.indexOf(ops[0])}"]`).click();
    for (let j = 0; j < 3; j++) {
      await scene.locator(`[data-bcer-grappa-operation-step="${j}"]`).click();
      assert.equal(
        Number(await page.locator('.scene-player').getAttribute('data-frame')),
        ops[j].startFrame,
      );
      assert.equal(
        await scene
          .locator(`[data-bcer-grappa-operation-step="${j}"]`)
          .getAttribute('aria-pressed'),
        'true',
      );
      assert.match(
        await scene.innerText(),
        [
          /Frame \(kx,ky,coils\).*Last two H5 axes.*last remaining axis ≤64.*placeholder 1 mm is not patient geometry/is,
          /28\/32 ky lines sampled; 0.875.*Below 0.90.*not 2× acquisition acceleration.*ACS24 vs FAQ 16-line\/16×16/is,
          /ifftshift → IFFT2 → ifftshift → RSS magnitude.*sqrt\(sum\|coil image\|²\).*float32.*No measured image output/is,
        ][j],
      );
      await capture(`contract-${j}`);
      await absent();
    }
    await scene.locator('[data-bcer-grappa-operation-step="1"]').click();
    const labels = ['Undersampled', 'Full sampling', 'If GRAPPA fails'];
    for (let j = 0; j < 3; j++) {
      await scene.getByRole('button', { name: labels[j], exact: true }).click();
      const local = [0, Math.floor((ops[1].frames - 1) / 2), ops[1].frames - 1][j];
      assert.equal(
        Number(await page.locator('.scene-player').getAttribute('data-frame')),
        ops[1].startFrame + local,
      );
      assert.equal(
        await scene
          .getByRole('button', { name: labels[j], exact: true })
          .getAttribute('aria-pressed'),
        'true',
      );
      await mask(j);
      assert.match(
        await scene.innerText(),
        [
          /28\/32.*0.875.*Below 0.90.*net 32\/28/is,
          /32\/32.*1.*Fully sampled → skip GRAPPA.*IFFT\+RSS only/is,
          /28\/32.*0.875.*pygrappa raises.*zero-filled frame.*hypothetical rule, no observed failure/is,
        ][j],
      );
      await capture(`mode-${j}`);
      await absent();
    }
    const oi = plan.beats.findIndex((b) => b.scene === 'output');
    await page.locator(`[data-story-step="${oi}"]`).click();
    assert.match(
      await page.locator('[data-bcer-grappa-output-schema]').innerText(),
      /artifacts\/grappa\/reconstructed_<h5stem>\.nii\.gz/,
    );
    assert.match(await scene.innerText(), /Actual mode, image, frame counts and quality null/is);
    await absent();
    const ri = plan.beats.findIndex((b) => b.scene === 'reference');
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    const reveal = () =>
      scene.getByRole('button', { name: 'Reveal public mode rule', exact: true });
    await reveal().click();
    assert.match(
      await page.locator('[data-bcer-grappa-reference-revealed]').innerText(),
      /GRAPPA-applied, sampled-skip, image-passthrough and frame-zero-fill differ.*Stage\/path\/nonempty only.*No applied-kernel, axes\/spacing or PSNR\/SSIM check.*file size/is,
    );
    await capture('mode-rule-revealed');
    await scene.getByRole('button', { name: 'Cover public mode rule', exact: true }).click();
    await absent();
    await page.locator('.scene-play').click();
    await page.locator('.scene-stage').scrollIntoViewIfNeeded();
    await page.waitForFunction(
      (f) => Number(document.querySelector('.scene-player').getAttribute('data-frame')) > f,
      plan.beats[ri].startFrame + 4,
    );
    await page.locator('.scene-play').click();
    await reveal().click();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    await reveal().click();
    await page.locator('.scene-reset').click();
    await absent();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    await reveal().click();
    await page
      .locator(`[data-story-step="${plan.beats.findIndex((b) => b.scene === 'limits')}"]`)
      .click();
    await absent();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    await reveal().click();
    await page.locator('[data-story-step="0"]').click();
    await absent();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    await page.locator('.scene-reset').click();
  }
  if (plan.recipe === 'bcer-superres-v1') {
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    const scene = page.locator('[data-bcer-superres-scene]');
    const capture = async (name) =>
      page.locator('.scene-player').screenshot({ path: path.join(output, `${label}-${name}.png`) });
    const absent = async () =>
      assert.equal(await page.locator('[data-bcer-superres-reference-revealed]').count(), 0);
    await page.locator('[data-story-step="0"]').click();
    await absent();
    const native = await scene
      .locator('img')
      .evaluate((img) => ({ src: img.currentSrc, w: img.naturalWidth, h: img.naturalHeight }));
    assert.deepEqual([native.w, native.h], [320, 320]);
    assert.equal(
      sha(Buffer.from(native.src.split(',')[1], 'base64')),
      'cb76d37da6a4b70a77f865887ab0d44581dbfd5db595ad1e7800a268c295f5c8',
    );
    assert.match(
      await scene.innerText(),
      /Representative MRI input.*640² k10.*320².*15–829.*640×640×21.*LPS.*not a matched BCER input\/output.*No chosen reference grid/is,
    );
    const ops = plan.beats.filter((b) => b.scene === 'operation');
    assert.equal(ops.length, 3);
    await page.locator(`[data-story-step="${plan.beats.indexOf(ops[0])}"]`).click();
    for (let j = 0; j < 3; j++) {
      await scene.locator(`[data-bcer-superres-step="${j}"]`).click();
      assert.equal(
        Number(await page.locator('.scene-player').getAttribute('data-frame')),
        ops[j].startFrame,
      );
      assert.equal(
        await scene.locator(`[data-bcer-superres-step="${j}"]`).getAttribute('aria-pressed'),
        'true',
      );
      const re = [
        /Source size×spacing.*input origin\/direction.*reference wins.*not a clean\/private target/is,
        /640×640×21.*ceil\(N×s\/t\).*641×641×22.*437,782.*5.09%.*not measured output/is,
        /Linear is the source default.*Identity physical transform.*Outside FOV default 0.*input pixel type.*quantize/is,
      ][j];
      assert.match(await scene.innerText(), re);
      await capture(`contract-${j}`);
      await absent();
    }
    await scene.locator('[data-bcer-superres-step="1"]').click();
    for (let j = 0; j < 3; j++) {
      await scene.locator(`[data-bcer-superres-branch="${j}"]`).click();
      // Symmetric monotonic smoothstep has nearest endpoint/midpoint samples;
      // select the earlier sample for the floating-point midpoint tie.
      const expectedLocal = [0, Math.floor((ops[1].frames - 1) / 2), ops[1].frames - 1][j];
      assert.equal(
        Number(await page.locator('.scene-player').getAttribute('data-frame')),
        ops[1].startFrame + expectedLocal,
      );
      assert.equal(
        await scene.locator(`[data-bcer-superres-branch="${j}"]`).getAttribute('aria-pressed'),
        'true',
      );
      assert.match(
        await scene.innerText(),
        new RegExp(
          `Illustrative target: ${['640×640×21', '640×640×42', '1280×1280×42'][j]} voxels.*No resampled image computed`,
          'is',
        ),
      );
      await capture(`grid-${j}`);
      await absent();
    }
    await scene.locator('[data-bcer-superres-step="2"]').click();
    const modes = ['linear', 'nearest', 'bspline'];
    for (let j = 0; j < 3; j++) {
      const before = Number(await page.locator('.scene-player').getAttribute('data-frame'));
      await scene.locator(`[data-bcer-superres-interpolation="${modes[j]}"]`).click();
      assert.equal(Number(await page.locator('.scene-player').getAttribute('data-frame')), before);
      assert.equal(
        await scene
          .locator(`[data-bcer-superres-interpolation="${modes[j]}"]`)
          .getAttribute('aria-pressed'),
        'true',
      );
      assert.match(
        await scene.innerText(),
        [
          /Linear is the source default/is,
          /Nearest selects samples.*does not create detail/is,
          /B-spline interpolates.*no quality result/is,
        ][j],
      );
      await capture(`interpolation-${j}`);
      await absent();
    }
    await page.locator('.scene-play').click();
    await page.locator('.scene-stage').scrollIntoViewIfNeeded();
    await page.waitForFunction(
      (f) => Number(document.querySelector('.scene-player').getAttribute('data-frame')) > f,
      ops[2].startFrame + 4,
    );
    await page.locator('.scene-play').click();
    await scene.locator('[data-bcer-superres-step="2"]').click();
    assert.equal(
      await scene
        .locator('[data-bcer-superres-interpolation="linear"]')
        .getAttribute('aria-pressed'),
      'true',
    );
    const oi = plan.beats.findIndex((b) => b.scene === 'output');
    await page.locator(`[data-story-step="${oi}"]`).click();
    assert.match(
      await scene.locator('pre').innerText(),
      /artifacts\/resample\/resampled_<input_stem>\.nii\.gz/,
    );
    assert.match(
      await scene.innerText(),
      /actual image, target, elapsed time and quality are null/is,
    );
    await absent();
    const ri = plan.beats.findIndex((b) => b.scene === 'reference');
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    const reveal = () => scene.getByRole('button', { name: 'Reveal grader rules', exact: true });
    await reveal().click();
    assert.match(
      await page.locator('[data-bcer-superres-reference-revealed]').innerText(),
      /Stage, path and nonempty checks only.*No target-grid, affine or quality invariant.*file size.*not PSNR\/SSIM/is,
    );
    await capture('grader-revealed');
    await scene.getByRole('button', { name: 'Cover grader rules', exact: true }).click();
    await absent();
    await page.locator('.scene-play').click();
    await page.locator('.scene-stage').scrollIntoViewIfNeeded();
    await page.waitForFunction(
      (f) => Number(document.querySelector('.scene-player').getAttribute('data-frame')) > f,
      plan.beats[ri].startFrame + 4,
    );
    await page.locator('.scene-play').click();
    await reveal().click();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    await reveal().click();
    await page.locator('.scene-reset').click();
    await absent();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    await reveal().click();
    await page
      .locator(`[data-story-step="${plan.beats.findIndex((b) => b.scene === 'limits')}"]`)
      .click();
    await absent();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    await reveal().click();
    await page.locator('[data-story-step="0"]').click();
    await absent();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    await page.locator('.scene-reset').click();
    await page.locator('[data-story-step="3"]').click();
    assert.equal(
      await scene
        .locator('[data-bcer-superres-interpolation="linear"]')
        .getAttribute('aria-pressed'),
      'true',
    );
    await page.locator('.scene-reset').click();
  }
  if (plan.recipe === 'bcer-denoise-v1') {
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    const scene = page.locator('[data-bcer-denoise-scene]');
    const capture = async (name) =>
      page.locator('.scene-player').screenshot({ path: path.join(output, `${label}-${name}.png`) });
    const absent = async () =>
      assert.equal(await page.locator('[data-bcer-denoise-reference-revealed]').count(), 0);
    await page.locator('[data-story-step="0"]').click();
    await absent();
    const native = await scene
      .locator('img')
      .evaluate((img) => ({ src: img.currentSrc, w: img.naturalWidth, h: img.naturalHeight }));
    assert.deepEqual([native.w, native.h], [320, 320]);
    assert.equal(
      sha(Buffer.from(native.src.split(',')[1], 'base64')),
      'cb76d37da6a4b70a77f865887ab0d44581dbfd5db595ad1e7800a268c295f5c8',
    );
    assert.match(
      await scene.innerText(),
      /representative MRI helper.*k = 10.*640².*320².*15–829.*oblique LPS.*No clean target/is,
    );
    const ops = plan.beats.filter((b) => b.scene === 'operation');
    assert.equal(ops.length, 3);
    await page.locator(`[data-story-step="${plan.beats.indexOf(ops[0])}"]`).click();
    for (let j = 0; j < 3; j++) {
      await scene.locator(`[data-bcer-denoise-operation-step="${j}"]`).click();
      assert.equal(
        Number(await page.locator('.scene-player').getAttribute('data-frame')),
        ops[j].startFrame,
      );
      assert.equal(
        await scene
          .locator(`[data-bcer-denoise-operation-step="${j}"]`)
          .getAttribute('aria-pressed'),
        'true',
      );
      const re = [
        /10 \/ 20 \/ 30 \/ 50.*0 \/ 0.25 \/ 0.5 \/ 1.*Nonfinite.*constant range/s,
        /Estimated σ=0.03 normalized units.*Toy range 40.*1.2.*not.*measured MRI noise/s,
        /Independent 2-D BM3D profile=np.*restore range.*floating input dtype.*No BM3D output/s,
      ][j];
      assert.match(await scene.innerText(), re);
      await capture(`contract-${j}`);
      await absent();
    }
    await scene.locator('[data-bcer-denoise-operation-step="1"]').click();
    for (let j = 0; j < 3; j++) {
      await scene
        .getByRole('button', { name: ['0.03', '0.08 default', '0.15'][j], exact: true })
        .click();
      let best = 0,
        d = Infinity;
      for (let k = 0; k < ops[1].frames; k++) {
        const u = k / (ops[1].frames - 1),
          z = u * u * (3 - 2 * u),
          v = Math.abs(z - j / 2);
        if (v < d) {
          d = v;
          best = k;
        }
      }
      assert.equal(
        Number(await page.locator('.scene-player').getAttribute('data-frame')),
        ops[1].startFrame + best,
      );
      assert.match(
        await scene.innerText(),
        new RegExp(
          `Estimated σ=${[0.03, 0.08, 0.15][j]} normalized units.*Toy range 40.*${[1.2, 3.2, 6][j]}`,
          's',
        ),
      );
      assert.equal(
        await scene
          .getByRole('button', { name: ['0.03', '0.08 default', '0.15'][j], exact: true })
          .getAttribute('aria-pressed'),
        'true',
      );
      await capture(`sigma-${j}`);
      await absent();
    }
    const oi = plan.beats.findIndex((b) => b.scene === 'output');
    await page.locator(`[data-story-step="${oi}"]`).click();
    assert.match(
      await page.locator('[data-bcer-denoise-output-schema]').innerText(),
      /artifacts\/denoise\/denoised_<input_stem>\.nii\.gz/,
    );
    assert.match(await scene.innerText(), /actual path\/image\/elapsed\/quality remain null/i);
    await absent();
    const ri = plan.beats.findIndex((b) => b.scene === 'reference');
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    const reveal = () =>
      scene.getByRole('button', { name: 'Reveal public validator rule', exact: true });
    await reveal().click();
    assert.match(
      await page.locator('[data-bcer-denoise-reference-revealed]').innerText(),
      /Stage\/path\/nonempty\/geometry.*file size.*size is exact.*1e-3.*No PSNR\/SSIM\/clean target/s,
    );
    await capture('validator-revealed');
    await scene.getByRole('button', { name: 'Cover validator rule', exact: true }).click();
    await absent();
    await page.locator('.scene-play').click();
    await page.locator('.scene-stage').scrollIntoViewIfNeeded();
    await page.waitForFunction(
      (f) => Number(document.querySelector('.scene-player').getAttribute('data-frame')) > f,
      plan.beats[ri].startFrame + 4,
    );
    await page.locator('.scene-play').click();
    await reveal().click();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    await reveal().click();
    await page.locator('.scene-reset').click();
    await absent();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    await reveal().click();
    await page
      .locator(`[data-story-step="${plan.beats.findIndex((b) => b.scene === 'limits')}"]`)
      .click();
    await absent();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    await reveal().click();
    await page.locator('[data-story-step="0"]').click();
    await absent();
    await page.locator(`[data-story-step="${ri}"]`).click();
    await absent();
    await page.locator('.scene-reset').click();
  }
  if (plan.recipe === 'automed-vqa-rad-v1') {
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    const beat = (name) => plan.beats.findIndex((b) => b.id === name),
      scene = page.locator('[data-vqa-rad-scene]');
    const capture = async (name) =>
      page.locator('.scene-player').screenshot({ path: path.join(output, `${label}-${name}.png`) });
    const absent = async () =>
      assert.equal(await page.locator('[data-vqa-rad-public-annotation]').count(), 0);
    await page.locator('[data-story-step="0"]').click();
    await absent();
    const native = await scene
      .locator('img')
      .evaluate((img) => ({ src: img.currentSrc, w: img.naturalWidth, h: img.naturalHeight }));
    assert.deepEqual([native.w, native.h], [566, 555]);
    assert.equal(
      require('node:crypto')
        .createHash('sha256')
        .update(Buffer.from(native.src.split(',')[1], 'base64'))
        .digest('hex'),
      '379dff334415856e4ee966f9abfcba8d50f2a2a3534d4965bbd6c462baeaada2',
    );
    assert.match(
      await scene.innerText(),
      /are regions of the brain infarcted\?.*no native question ID.*No source answer.*no DICOM geometry/s,
    );
    await page.locator(`[data-story-step="${beat('helper')}"]`).click();
    await absent();
    const reveal = () =>
      scene.getByRole('button', { name: 'Reveal public training annotation', exact: true });
    await reveal().click();
    assert.match(
      await page.locator('[data-vqa-rad-public-annotation]').innerText(),
      /^yes.*Public train annotation.*not Full gold, diagnosis or model output/s,
    );
    await capture('public-annotation-revealed');
    await scene
      .getByRole('button', { name: 'Hide public training annotation', exact: true })
      .click();
    await page.locator('.scene-play').click();
    await page.locator('.scene-stage').scrollIntoViewIfNeeded();
    await page.waitForFunction(
      (f) => Number(document.querySelector('.scene-player').getAttribute('data-frame')) > f,
      plan.beats[beat('helper')].startFrame + 4,
    );
    await page.locator('.scene-play').click();
    await reveal().click();
    await page.locator(`[data-story-step="${beat('helper')}"]`).click();
    await absent();
    await reveal().click();

    await scene
      .getByRole('button', { name: 'Hide public training annotation', exact: true })
      .click();
    await absent();
    await reveal().click();
    await page.locator(`[data-story-step="${beat('operation')}"]`).click();
    await absent();
    await page.locator(`[data-story-step="${beat('helper')}"]`).click();
    await absent();
    await reveal().click();
    await page.locator('.scene-reset').click();
    await absent();
    await page.locator(`[data-story-step="${beat('helper')}"]`).click();
    await absent();
    await reveal().click();
    await page.locator('[data-story-step="0"]').click();
    await absent();
    await page.locator(`[data-story-step="${beat('helper')}"]`).click();
    await absent();
    await page.locator(`[data-story-step="${beat('operation')}"]`).click();
    const op = plan.beats.find((b) => b.scene === 'operation');
    for (let j = 0; j < 4; j++) {
      let best = 0,
        d = Infinity;
      for (let k = 0; k < op.frames; k++) {
        const u = k / op.frames,
          z = u * u * (3 - 2 * u),
          v = Math.abs(z - j / 3);
        if (v < d) {
          d = v;
          best = k;
        }
      }
      await page.locator(`[data-vqa-rad-step="${j}"]`).click();
      assert.equal(
        Number(await page.locator('.scene-player').getAttribute('data-frame')),
        op.startFrame + best,
      );
      assert.equal(
        await page.locator('[data-vqa-rad-currentstep]').getAttribute('data-vqa-rad-currentstep'),
        String(j),
      );
      assert.equal(
        await page.locator(`[data-vqa-rad-step="${j}"]`).getAttribute('aria-pressed'),
        'true',
      );
      await capture(`contract-${j}`);
      await absent();
    }
    await scene.getByRole('button', { name: 'standard', exact: true }).click();
    assert.match(
      await page.locator('[data-vqa-rad-tier]').innerText(),
      /six candidates.*five.*wrongly says multiple-choice.*open-ended.*unverified/s,
    );
    await capture('tier-standard');
    await scene.getByRole('button', { name: 'Inspect calibration rule', exact: true }).click();
    assert.match(
      await page.locator('[data-vqa-rad-calibration]').innerText(),
      /first15.*missing gold dropped.*lacks top-up.*>=10.*optional gold.*smoke1-10.*unaudited/s,
    );
    await capture('calibration-revealed');
    await page.locator('.scene-reset').click();
    await page.locator(`[data-story-step="${beat('operation')}"]`).click();
    assert.equal(
      await scene.getByRole('button', { name: 'lite', exact: true }).getAttribute('aria-pressed'),
      'true',
    );
    assert.equal(await page.locator('[data-vqa-rad-calibration]').count(), 0);
    await page.locator(`[data-story-step="${beat('output')}"]`).click();
    assert.equal(await page.locator('[data-vqa-rad-format]').count(), 0);
    await scene.getByRole('button', { name: 'Inspect format checks', exact: true }).click();
    assert.match(
      await page.locator('[data-vqa-rad-format]').innerText(),
      /Six keys.*label ignored.*No five-word.*bool\/nonfinite/s,
    );
    await capture('format-revealed');
    await absent();
    await page.locator(`[data-story-step="${beat('limits')}"]`).click();
    assert.equal(await page.locator('[data-vqa-rad-format]').count(), 0);
    const branches = [
      [
        'accuracy',
        /strict normalized yes\/no.*0.5EM\+0.5tokenF1.*all discovered.*Missing\/invalid\/placeholder/s,
      ],
      [
        'judge',
        /replaces primary accuracy.*all evaluator-supplied question IDs.*Only parsed records.*fallback/s,
      ],
      ['format gate', /Every file strict-valid.*fraction>=0.5.*max\(expected,1\)/s],
    ];
    for (let j = 0; j < branches.length; j++) {
      const [n, re] = branches[j];
      await scene.getByRole('button', { name: n, exact: true }).click();
      assert.match(await page.locator('[data-vqa-rad-metric]').innerText(), re);
      await capture(`metric-${j}`);
      await absent();
    }
    await page.locator('.scene-reset').click();
    await page.locator(`[data-story-step="${beat('limits')}"]`).click();
    assert.equal(
      await scene
        .getByRole('button', { name: 'accuracy', exact: true })
        .getAttribute('aria-pressed'),
      'true',
    );
    await page.locator('[data-story-step="0"]').click();
    await absent();
  }
  if (plan.recipe === 'automed-omni-v1') {
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    const beat = (name) => plan.beats.findIndex((b) => b.id === name);
    const scene = page.locator('[data-omni-scene]');
    const capture = async (name) =>
      page.locator('.scene-player').screenshot({ path: path.join(output, `${label}-${name}.png`) });
    const absent = async () =>
      assert.equal(await page.locator('[data-omni-reference-revealed]').count(), 0);
    await page.locator('[data-story-step="0"]').click();
    assert.equal(await scene.locator('img').count(), 0, 'no invented patient image');
    assert.match(
      await scene.innerText(),
      /Referenced CT image unavailable.*no recovered patient pixels.*What anatomical area.*Upper arm region.*Chest region.*Leg region.*Shoulder and upper back region.*Covid CT_0082/s,
    );
    await absent();
    const expected = (j, o = 0) => {
      const b = plan.beats.find(
        (b) => b.scene === 'operation' && Math.abs(b.channels.progress[0] - j / 2) < 1e-6,
      );
      if (j !== 1) return b.startFrame;
      let best = 0,
        d = Infinity;
      for (let k = 0; k < b.frames; k++) {
        const u = k / Math.max(1, b.frames - 1),
          z = u * u * (3 - 2 * u),
          v = Math.abs(z - o / 2);
        if (v < d) {
          d = v;
          best = k;
        }
      }
      return b.startFrame + best;
    };
    await page.locator(`[data-story-step="${beat('bind')}"]`).click();
    for (let j = 0; j < 3; j++) {
      await page.locator(`[data-omni-operation-step="${j}"]`).click();
      assert.equal(
        Number(await page.locator('.scene-player').getAttribute('data-frame')),
        expected(j),
      );
      assert.equal(
        await page.locator(`[data-omni-operation-step="${j}"]`).getAttribute('aria-pressed'),
        'true',
      );
      await capture(`contract-${j}`);
      await absent();
    }
    await page.locator('[data-omni-operation-step="0"]').click();
    await scene.getByRole('button', { name: 'standard', exact: true }).click();
    assert.match(
      await page.locator('[data-omni-tier]').innerText(),
      /all six.*modality\/access\/memory\/reproducibility.*no observed comparison/s,
    );
    await capture('tier-standard');
    await page.locator('.scene-reset').click();
    await page.locator(`[data-story-step="${beat('bind')}"]`).click();
    assert.equal(
      await scene.getByRole('button', { name: 'lite', exact: true }).getAttribute('aria-pressed'),
      'true',
    );
    await page.locator('[data-omni-operation-step="1"]').click();
    const names = ['Standalone A', 'Reject E', 'Reject miss'];
    const patterns = [
      /Authored control.*Answer: A.*A.*parser control.*never a real decode/s,
      /Authored control.*E.*reject.*outside task A–D.*Generic schema\/scorer A–E/s,
      /Authored control.*unparsed response.*reject.*do not guess/s,
    ];
    for (let o = 0; o < 3; o++) {
      await scene.getByRole('button', { name: names[o], exact: true }).click();
      assert.equal(
        Number(await page.locator('.scene-player').getAttribute('data-frame')),
        expected(1, o),
      );
      assert.equal(
        await scene
          .getByRole('button', { name: names[o], exact: true })
          .getAttribute('aria-pressed'),
        'true',
      );
      assert.match(await scene.innerText(), patterns[o]);
      await capture(`branch-${o}`);
      await absent();
    }
    await page.locator('[data-omni-operation-step="2"]').click();
    assert.equal(await page.locator('[data-omni-format]').count(), 0);
    await scene
      .getByRole('button', { name: 'Inspect task versus generic checks', exact: true })
      .click();
    assert.match(
      await page.locator('[data-omni-format]').innerText(),
      /Task A–D.*generic A–E.*conditional.*Private gold is exact, unnormalized.*no score/s,
    );
    await capture('format-revealed');
    await page.locator(`[data-story-step="${beat('output')}"]`).click();
    assert.equal(await page.locator('[data-omni-format]').count(), 0);
    assert.match(await scene.innerText(), /No authored control or public source answer copied/s);
    await page.locator(`[data-story-step="${beat('reference')}"]`).click();
    await absent();
    const reveal = scene.getByRole('button', {
      name: 'Reveal public README annotation',
      exact: true,
    });
    await reveal.click();
    assert.match(
      await page.locator('[data-omni-reference-revealed]').innerText(),
      /Chest region.*option B.*not private gold.*all evaluator-supplied IDs.*missing\/invalid.*No open-ended token-F1 or judge promotion/s,
    );
    await capture('reference-revealed');
    await reveal.click();
    await absent();
    await reveal.click();
    await page.locator(`[data-story-step="${beat('limits')}"]`).click();
    await absent();
    await page.locator(`[data-story-step="${beat('reference')}"]`).click();
    await absent();
    await reveal.click();
    await page.locator('.scene-reset').click();
    await absent();
    await page.locator(`[data-story-step="${beat('reference')}"]`).click();
    await absent();
    await reveal.click();
    await page.locator('[data-story-step="0"]').click();
    await absent();
    await page.locator(`[data-story-step="${beat('reference')}"]`).click();
    await absent();
    await page.locator('[data-story-step="0"]').click();
    await absent();
  }
  if (plan.recipe === 'automed-kvasir-v1') {
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    const beat = (name) => plan.beats.findIndex((b) => b.id === name);
    const scene = page.locator('[data-kvasir-scene]');
    const capture = async (name) =>
      page.locator('.scene-player').screenshot({ path: path.join(output, `${label}-${name}.png`) });
    const absent = async () =>
      assert.equal(await page.locator('[data-kvasir-reference-revealed]').count(), 0);
    await page.locator('[data-story-step="0"]').click();
    const img = scene.locator('img');
    const src = await img.getAttribute('src');
    assert.ok(src.startsWith('data:image/jpeg;base64,'), 'native JPEG embedded offline');
    assert.equal(
      crypto
        .createHash('sha256')
        .update(Buffer.from(src.split(',')[1], 'base64'))
        .digest('hex'),
      '1500eb8e766c4eb761518b1c5829316416bcd348d06885e146cbd4d2c8ec0de8',
    );
    assert.equal(await img.evaluate((el) => el.naturalWidth), 720);
    assert.equal(await img.evaluate((el) => el.naturalHeight), 576);
    assert.match(
      await scene.innerText(),
      /Are there any abnormalities in the image.*Check all that are present/s,
    );
    await absent();
    const expected = (j, o = 0) => {
      const b = plan.beats.find(
        (b) => b.scene === 'operation' && Math.abs(b.channels.progress[0] - j / 2) < 1e-6,
      );
      if (j !== 1) return b.startFrame;
      let best = 0,
        d = Infinity;
      for (let k = 0; k < b.frames; k++) {
        const u = k / b.frames,
          z = u * u * (3 - 2 * u),
          v = Math.abs(z - o / 2);
        if (v < d) {
          d = v;
          best = k;
        }
      }
      return b.startFrame + best;
    };
    await page.locator(`[data-story-step="${beat('bind')}"]`).click();
    for (let j = 0; j < 3; j++) {
      await page.locator(`[data-kvasir-step="${j}"]`).click();
      assert.equal(
        Number(await page.locator('.scene-player').getAttribute('data-frame')),
        expected(j),
      );
      assert.equal(await scene.getAttribute('data-kvasir-currentstep'), String(j));
      await capture(`contract-${j}`);
      await absent();
    }
    await page.locator('[data-kvasir-step="0"]').click();
    await scene.getByRole('button', { name: 'standard', exact: true }).click();
    assert.match(
      await page.locator('[data-kvasir-tier]').innerText(),
      /all six.*endoscopy-image.*free-text/s,
    );
    await capture('tier-standard');
    await scene
      .getByRole('button', { name: 'Inspect staged validation rule', exact: true })
      .click();
    assert.match(
      await page.locator('#kvasir-calibration-rule').innerText(),
      /1–10 staged questions.*≥10 public records.*15.*gold optional.*composite prompt unresolved/s,
    );
    await capture('calibration-revealed');
    await page.locator('.scene-reset').click();
    await page.locator(`[data-story-step="${beat('bind')}"]`).click();
    assert.equal(
      await scene.getByRole('button', { name: 'lite', exact: true }).getAttribute('aria-pressed'),
      'true',
    );
    assert.equal(await page.locator('#kvasir-calibration-rule').count(), 0);
    await page.locator('[data-kvasir-step="1"]').click();
    for (let o = 0; o < 3; o++) {
      await page.locator(`[data-kvasir-branch="${o}"]`).click();
      assert.equal(
        Number(await page.locator('.scene-player').getAttribute('data-frame')),
        expected(1, o),
      );
      assert.equal(
        await page.locator(`[data-kvasir-branch="${o}"]`).getAttribute('aria-pressed'),
        'true',
      );
      await capture(`branch-${o}`);
      await absent();
    }
    await page.locator(`[data-story-step="${beat('output')}"]`).click();
    assert.match(
      await scene.innerText(),
      /All actual fields null.*no source raw annotation copied/s,
    );
    assert.equal(await page.locator('#kvasir-format-rule').count(), 0);
    await scene.getByRole('button', { name: 'Inspect format boundary', exact: true }).click();
    assert.match(
      await page.locator('#kvasir-format-rule').innerText(),
      /Six required keys.*finite-runtime.*≥50%.*all-ID denominator/s,
    );
    await capture('format-revealed');
    await page.locator(`[data-story-step="${beat('reference')}"]`).click();
    await absent();
    assert.equal(await page.locator('#kvasir-format-rule').count(), 0);
    const reveal = scene.getByRole('button', { name: 'Reveal public raw annotation', exact: true });
    await reveal.click();
    assert.match(
      await page.locator('[data-kvasir-reference-revealed]').innerText(),
      /ulcerative colitis.*Source category: Ulcerative Colitis.*Not model evidence.*independent clinical/s,
    );
    await capture('reference-revealed');
    await page.locator(`[data-story-step="${beat('limits')}"]`).click();
    await absent();
    await page.locator(`[data-story-step="${beat('reference')}"]`).click();
    await absent();
    await reveal.click();
    await page.locator('.scene-reset').click();
    await absent();
    await page.locator(`[data-story-step="${beat('reference')}"]`).click();
    await absent();
    await reveal.click();
    await page.locator('[data-story-step="0"]').click();
    await absent();
    await page.locator(`[data-story-step="${beat('reference')}"]`).click();
    await absent();
    await page.locator('[data-story-step="0"]').click();
    await absent();
  }
  if (plan.recipe === 'automed-medxpert-mm-v1') {
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    const beat = (name) => plan.beats.findIndex((b) => b.id === name);
    const scene = page.locator('[data-medxpert-scene]');
    const capture = async (name) =>
      page.locator('.scene-player').screenshot({ path: path.join(output, `${label}-${name}.png`) });
    const absent = async () =>
      assert.equal(await page.locator('[data-medxpert-reference-revealed]').count(), 0);
    await page.locator('[data-story-step="0"]').click();
    const img = page.locator('[data-medxpert-native]');
    const src = await img.getAttribute('src');
    assert.ok(src.startsWith('data:image/jpeg;base64,'), 'native JPEG embedded offline');
    assert.equal(
      crypto
        .createHash('sha256')
        .update(Buffer.from(src.split(',')[1], 'base64'))
        .digest('hex'),
      '35082586ba0b7457db2495f651de8729afdb6d2833b25eb5f19904737ff2610d',
    );
    assert.equal(await img.evaluate((el) => el.naturalWidth), 945);
    assert.equal(await img.evaluate((el) => el.naturalHeight), 999);
    await scene.locator('summary').click();
    assert.match(await scene.locator('pre').innerText(), /most appropriate next imaging study/);
    await capture('question-expanded');
    await scene.locator('summary').click();
    await absent();
    await page.locator(`[data-story-step="${beat('bind')}"]`).click();
    const expected = (j, o = 0) => {
      const b = plan.beats.find(
        (b) => b.scene === 'operation' && Math.abs(b.channels.progress[0] - j / 2) < 1e-6,
      );
      if (j !== 1) return b.startFrame;
      let best = 0,
        d = Infinity;
      for (let k = 0; k < b.frames; k++) {
        const u = k / b.frames,
          z = u * u * (3 - 2 * u),
          v = Math.abs(z - o / 4);
        if (v < d) {
          d = v;
          best = k;
        }
      }
      return b.startFrame + best;
    };
    for (let j = 0; j < 3; j++) {
      await page.locator(`[data-medxpert-operation-step="${j}"]`).click();
      assert.equal(
        Number(await page.locator('.scene-player').getAttribute('data-frame')),
        expected(j),
      );
      assert.equal(
        await page
          .locator('[data-medxpert-currentstage]')
          .getAttribute('data-medxpert-currentstage'),
        String(j),
      );
      await capture(`contract-${j}`);
      await absent();
    }
    await page.locator('[data-medxpert-operation-step="0"]').click();
    const assistance = scene.getByRole('navigation', { name: 'MedXpert assistance' });
    await assistance.getByRole('button', { name: 'standard', exact: true }).click();
    assert.match(await page.locator('[data-medxpert-tier]').innerText(), /all five.*unverified/s);
    await capture('tier-standard');
    await page.locator('.scene-reset').click();
    await page.locator(`[data-story-step="${beat('bind')}"]`).click();
    assert.equal(
      await assistance
        .getByRole('button', { name: 'lite', exact: true })
        .getAttribute('aria-pressed'),
      'true',
    );
    await page.locator('[data-medxpert-operation-step="1"]').click();
    for (let o = 0; o < 5; o++) {
      const letter = 'ABCDE'[o];
      await page.locator(`[data-medxpert-option="${letter}"]`).click();
      assert.equal(
        Number(await page.locator('.scene-player').getAttribute('data-frame')),
        expected(1, o),
      );
      assert.equal(
        await page.locator(`[data-medxpert-option="${letter}"]`).getAttribute('aria-pressed'),
        'true',
      );
      await capture(`option-${letter}`);
      await absent();
    }
    await page.locator('[data-medxpert-operation-step="2"]').click();
    assert.equal(await page.locator('[data-medxpert-format]').count(), 0);
    await scene
      .getByRole('button', { name: 'Inspect format/scorer boundary', exact: true })
      .click();
    assert.match(
      await page.locator('[data-medxpert-format]').innerText(),
      /Six keys.*Empty-answer.*fail format.*scores correctly/s,
    );
    await capture('format-revealed');
    await page.locator(`[data-story-step="${beat('reference')}"]`).click();
    await absent();
    const reveal = scene.getByRole('button', { name: 'Reveal public source label', exact: true });
    await reveal.click();
    assert.match(
      await page.locator('[data-medxpert-reference-revealed]').innerText(),
      /Source annotation: D.*Abdominal ultrasound.*Not private Full gold/s,
    );
    await capture('reference-revealed');
    await page.locator(`[data-story-step="${beat('limits')}"]`).click();
    await absent();
    await page.locator(`[data-story-step="${beat('reference')}"]`).click();
    await absent();
    await reveal.click();
    await page.locator('.scene-reset').click();
    await absent();
    await page.locator(`[data-story-step="${beat('reference')}"]`).click();
    await absent();
    await reveal.click();
    await page.locator('[data-story-step="0"]').click();
    await absent();
    await page.locator(`[data-story-step="${beat('reference')}"]`).click();
    await absent();
    await page.locator(`[data-story-step="${beat('schema')}"]`).click();
    assert.equal(await page.locator('[data-medxpert-format]').count(), 0);
    await scene
      .getByRole('button', { name: 'Inspect format/scorer boundary', exact: true })
      .click();
    await page.locator(`[data-story-step="${beat('output')}"]`).click();
    assert.equal(await page.locator('[data-medxpert-format]').count(), 0);
    assert.match(await scene.innerText(), /actual values remain null.*No source correct label/s);
    await page.locator('[data-story-step="0"]').click();
    await absent();
  }
  if (plan.recipe === 'automed-medframeqa-v1') {
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    const beat = (name) => plan.beats.findIndex((b) => b.id === name);
    const scene = page.locator('[data-medframeqa-scene]');
    const capture = async (name) =>
      page.locator('.scene-player').screenshot({ path: path.join(output, `${label}-${name}.png`) });
    const absent = async () => {
      assert.equal(await page.locator('[data-medframeqa-reference]').count(), 0);
      assert.ok(plan.beats.every((b) => b.channels.reference.every((v) => v === 0)));
    };
    await page.locator('[data-story-step="0"]').click();
    assert.match(
      await scene.innerText(),
      /1280×720.*Full question.*absent.*no video time.*no HU.*patient-independent/s,
    );
    const img = scene.locator('img');
    const nativeHash = async () => {
      const src = await scene.locator('img').getAttribute('src');
      assert.ok(src.startsWith('data:image/jpeg;base64,'), 'Native JPEG embedded for offline use');
      return sha(Buffer.from(src.split(',')[1], 'base64'));
    };
    assert.equal(
      await nativeHash(),
      '75fe53e62cd6c48b91ba165311c43d409fe92f5212490404c6897551989d2e4a',
    );
    await scene.getByRole('button', { name: 'Source slot 2', exact: true }).click();
    assert.equal(
      await nativeHash(),
      'bbf298e1ccfd3cc64dd7b2e21905b084c3a09aa4043ead43f9a010eb5928bafd',
    );
    assert.equal(await img.evaluate((el) => el.naturalWidth), 1280);
    assert.equal(await img.evaluate((el) => el.naturalHeight), 720);
    await capture('source-slot-2');
    await absent();
    await page.locator(`[data-story-step="${beat('helper')}"]`).click();
    assert.equal(await page.locator('[data-medframeqa-calibration]').count(), 0);
    assert.match(
      await scene.innerText(),
      /slot 6.*A.*B.*C.*D.*E.*six-option.*No source question, options, gold or reasoning/s,
    );
    await scene.getByRole('button', { name: 'Inspect calibration rule', exact: true }).click();
    assert.match(
      await page.locator('[data-medframeqa-calibration]').innerText(),
      /15.*>=10.*public-gold.*unaudited/s,
    );
    await capture('calibration-revealed');
    await absent();
    await page.locator(`[data-story-step="${beat('operation')}"]`).click();
    const assistance = page.getByRole('group', { name: 'MedFrameQA assistance' });
    await assistance.getByRole('button', { name: 'standard', exact: true }).click();
    assert.match(
      await page.locator('[data-medframeqa-tier]').innerText(),
      /Bounded candidate.*not measured performance/s,
    );
    await capture('tier-standard');
    const expected = plan.beats.find((b) => b.scene === 'operation');
    for (let i = 0; i < 4; i++) {
      const button = page.locator(`[data-medframeqa-step="${i}"]`);
      await button.click();
      assert.equal(await button.getAttribute('aria-pressed'), 'true');
      assert.equal(await scene.getAttribute('data-medframeqa-currentstep'), String(i));
      const frame = Math.round(expected.startFrame + ((expected.frames - 1) * i) / 3);
      assert.equal(Number(await page.locator('.scene-player').getAttribute('data-frame')), frame);
      assert.match(
        await scene.innerText(),
        [
          /Verify question\.json/,
          /method-specific prompt/,
          /Run provisioned method; parse raw text to A\.\.E/,
          /Map label to exact option text/,
        ][i],
      );
      await capture(`contract-${i}`);
      await absent();
    }
    await page.locator('[data-medframeqa-step="0"]').click();
    assert.equal(
      await assistance
        .getByRole('button', { name: 'lite', exact: true })
        .getAttribute('aria-pressed'),
      'true',
    );
    await page.locator(`[data-story-step="${beat('helper')}"]`).click();
    assert.equal(await page.locator('[data-medframeqa-calibration]').count(), 0);
    await page.locator(`[data-story-step="${beat('output')}"]`).click();
    assert.equal(await page.locator('[data-medframeqa-format]').count(), 0);
    assert.match(
      await page.locator('[data-medframeqa-output-schema]').innerText(),
      /model_name.*predicted_label.*question_id.*raw_model_output.*runtime_s.*unset.*Both-empty/s,
    );
    await scene.getByRole('button', { name: 'Inspect format checks', exact: true }).click();
    assert.match(
      await page.locator('[data-medframeqa-format]').innerText(),
      /extra keys accepted.*stripped\/uppercased.*no finite or boolean.*Empty text loophole/s,
    );
    await capture('format-revealed');
    await absent();
    await page.locator(`[data-story-step="${beat('limits')}"]`).click();
    const metric = page.getByRole('group', { name: 'Scoring boundary' });
    for (const name of ['accuracy', 'format gate', 'workflow']) {
      await metric.getByRole('button', { name, exact: true }).click();
      assert.match(
        await page.locator('[data-medframeqa-metric]').innerText(),
        name === 'accuracy'
          ? /all evaluator-selected.*Missing\/invalid\/placeholder/s
          : name === 'format gate'
            ? /every file strict-valid.*fraction>=0.5.*max\(expected,1\)/s
            : /renormaliz.*S4.*S5/s,
      );
      await capture(`metric-${name.replace(' ', '-')}`);
    }
    await page.locator(`[data-story-step="${beat('output')}"]`).click();
    assert.equal(await page.locator('[data-medframeqa-format]').count(), 0);
    await page.locator(`[data-story-step="${beat('limits')}"]`).click();
    assert.equal(
      await metric
        .getByRole('button', { name: 'accuracy', exact: true })
        .getAttribute('aria-pressed'),
      'true',
    );
    await page.locator('[data-story-step="0"]').click();
    assert.equal(
      await nativeHash(),
      '75fe53e62cd6c48b91ba165311c43d409fe92f5212490404c6897551989d2e4a',
    );
    await scene.getByRole('button', { name: 'Source slot 2', exact: true }).click();
    await page.locator('.scene-reset').click();
    assert.equal(
      await nativeHash(),
      '75fe53e62cd6c48b91ba165311c43d409fe92f5212490404c6897551989d2e4a',
    );
    await absent();
  }
  if (plan.recipe === 'automed-pathology-caption-500-v1') {
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    const beat = (name) => plan.beats.findIndex((b) => b.id === name);
    const scene = page.locator('[data-pathology500-scene]');
    await page.locator('[data-story-step="0"]').click();
    assert.equal(await scene.locator('img').count(), 0);
    assert.match(
      await scene.innerText(),
      /0 actual images\/captions.*Tissue, stain, magnification.*unknown.*500 selected case IDs are unstaged.*subset relation is unknown/s,
    );
    assert.match(
      await page.locator('[data-pathology500-output]').innerText(),
      /500 expected image cases.*1 image\/1 caption.*Actual caption empty/s,
    );
    await page.locator(`[data-story-step="${beat('group')}"]`).click();
    const assistance = page.getByRole('navigation', { name: 'PathCap inference guidance' });
    await assistance.getByRole('button', { name: 'standard', exact: true }).click();
    assert.match(
      await page.locator('[data-pathology500-tier]').innerText(),
      /at least three.*inference-only.*training forbidden/s,
    );
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(output, `${label}-tier-standard.png`) });
    const operations = ['One-image unit', 'Caption syntax', 'Pathology metric gap'];
    const contracts = [
      /Exactly one JPEG per case.*one caption file/s,
      /1–8000 raw chars.*≥1 letter.*ASCII printable.*One ASCII letter passes syntax only.*checker does not enforce wrapper structure/s,
      /Default CXR schema does not validate pathology.*Seven|Default CXR schema.*Equal seven.*0–1.*no score/s,
    ];
    for (let i = 0; i < 3; i++) {
      const button = page.locator(`[data-pathology500-step="${i}"]`);
      await button.click();
      assert.equal(await button.getAttribute('aria-pressed'), 'true');
      assert.equal(
        await page
          .locator('[data-pathology500-currentstage]')
          .getAttribute('data-pathology500-currentstage'),
        String(i),
      );
      assert.match(await scene.innerText(), contracts[i]);
      assert.equal(await page.locator('[data-pathology500-reference-revealed]').count(), 0);
      await page
        .locator('.scene-player')
        .screenshot({ path: path.join(output, `${label}-contract-${i}.png`) });
    }
    await page.locator(`[data-story-step="${beat('output')}"]`).click();
    assert.equal(await page.locator('[data-pathology500-format]').count(), 0);
    await page
      .getByRole('button', { name: 'Inspect authored syntax fixture', exact: true })
      .click();
    assert.match(
      await page.locator('[data-pathology500-format]').innerText(),
      /illustrative text.*no patient or medical finding/s,
    );
    assert.match(
      await page.locator('[data-pathology500-output-schema]').innerText(),
      /agent_outputs\/<case_id>\/report.txt/,
    );
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(output, `${label}-format-revealed.png`) });
    await page.locator(`[data-story-step="${beat('reference')}"]`).click();
    assert.equal(await page.locator('[data-pathology500-reference-revealed]').count(), 0);
    await page.getByRole('button', { name: 'Reveal grading mechanics', exact: true }).click();
    assert.match(
      await page.locator('[data-pathology500-reference-revealed]').innerText(),
      /all supplied IDs.*500 not enforced.*forces F.*zero aggregate.*Raw micro.*F1=1.*not evidence.*No private\/public caption/s,
    );
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(output, `${label}-mechanics-revealed.png`) });
    await page.locator(`[data-story-step="${beat('output')}"]`).click();
    assert.equal(await page.locator('[data-pathology500-format]').count(), 0);
    assert.equal(await page.locator('[data-pathology500-reference-revealed]').count(), 0);
    await page.locator(`[data-story-step="${beat('reference')}"]`).click();
    assert.equal(await page.locator('[data-pathology500-reference-revealed]').count(), 0);
    await page.getByRole('button', { name: 'Reveal grading mechanics', exact: true }).click();
    await page.locator(`[data-story-step="${beat('limits')}"]`).click();
    assert.equal(await page.locator('[data-pathology500-reference-revealed]').count(), 0);
    await page.locator(`[data-story-step="${beat('reference')}"]`).click();
    assert.equal(await page.locator('[data-pathology500-reference-revealed]').count(), 0);
    await page.locator('.scene-reset').click();
    await page.locator(`[data-story-step="${beat('group')}"]`).click();
    assert.equal(
      await assistance
        .getByRole('button', { name: 'lite', exact: true })
        .getAttribute('aria-pressed'),
      'true',
    );
    assert.match(
      await page.locator('[data-pathology500-tier]').innerText(),
      /Release-owned BLIP inference-only.*no website checkpoint/s,
    );
    await assistance.getByRole('button', { name: 'standard', exact: true }).click();
    await page.locator('[data-pathology500-step="2"]').click();
    await page.locator('[data-pathology500-step="0"]').click();
    assert.equal(
      await assistance
        .getByRole('button', { name: 'lite', exact: true })
        .getAttribute('aria-pressed'),
      'true',
    );
    await page.locator('[data-story-step="0"]').click();
  }
  if (plan.recipe === 'automed-pathology-caption-100-v1') {
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    const beat = (name) => plan.beats.findIndex((b) => b.id === name);
    const scene = page.locator('[data-pathology100-scene]');
    await page.locator('[data-story-step="0"]').click();
    assert.equal(await scene.locator('img').count(), 0);
    assert.match(
      await scene.innerText(),
      /0 actual images\/captions.*Tissue, stain, magnification.*unknown.*100 selected case IDs are unstaged.*subset relation is unknown/s,
    );
    assert.match(
      await page.locator('[data-pathology100-output]').innerText(),
      /100 expected image cases.*1 image\/1 caption.*Actual caption empty/s,
    );
    await page.locator(`[data-story-step="${beat('group')}"]`).click();
    const assistance = page.getByRole('navigation', { name: 'PathCap inference guidance' });
    await assistance.getByRole('button', { name: 'standard', exact: true }).click();
    assert.match(
      await page.locator('[data-pathology100-tier]').innerText(),
      /at least three.*inference-only.*training forbidden/s,
    );
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(output, `${label}-tier-standard.png`) });
    const operations = ['One-image unit', 'Caption syntax', 'Pathology metric gap'];
    const contracts = [
      /Exactly one JPEG per case.*one caption file/s,
      /1–8000 raw chars.*≥1 letter.*ASCII printable.*One ASCII letter passes syntax only.*checker does not enforce wrapper structure/s,
      /Default CXR schema does not validate pathology.*Seven|Default CXR schema.*Equal seven.*0–1.*no score/s,
    ];
    for (let i = 0; i < 3; i++) {
      const button = page.locator(`[data-pathology100-step="${i}"]`);
      await button.click();
      assert.equal(await button.getAttribute('aria-pressed'), 'true');
      assert.equal(
        await page
          .locator('[data-pathology100-currentstage]')
          .getAttribute('data-pathology100-currentstage'),
        String(i),
      );
      assert.match(await scene.innerText(), contracts[i]);
      assert.equal(await page.locator('[data-pathology100-reference-revealed]').count(), 0);
      await page
        .locator('.scene-player')
        .screenshot({ path: path.join(output, `${label}-contract-${i}.png`) });
    }
    await page.locator(`[data-story-step="${beat('output')}"]`).click();
    assert.equal(await page.locator('[data-pathology100-format]').count(), 0);
    await page
      .getByRole('button', { name: 'Inspect authored syntax fixture', exact: true })
      .click();
    assert.match(
      await page.locator('[data-pathology100-format]').innerText(),
      /illustrative text.*no patient or medical finding/s,
    );
    assert.match(
      await page.locator('[data-pathology100-output-schema]').innerText(),
      /agent_outputs\/<case_id>\/report.txt/,
    );
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(output, `${label}-format-revealed.png`) });
    await page.locator(`[data-story-step="${beat('reference')}"]`).click();
    assert.equal(await page.locator('[data-pathology100-reference-revealed]').count(), 0);
    await page.getByRole('button', { name: 'Reveal grading mechanics', exact: true }).click();
    assert.match(
      await page.locator('[data-pathology100-reference-revealed]').innerText(),
      /all supplied IDs.*100 not enforced.*forces F.*zero aggregate.*Raw micro.*F1=1.*not evidence.*No private\/public caption/s,
    );
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(output, `${label}-mechanics-revealed.png`) });
    await page.locator(`[data-story-step="${beat('output')}"]`).click();
    assert.equal(await page.locator('[data-pathology100-format]').count(), 0);
    assert.equal(await page.locator('[data-pathology100-reference-revealed]').count(), 0);
    await page.locator(`[data-story-step="${beat('reference')}"]`).click();
    assert.equal(await page.locator('[data-pathology100-reference-revealed]').count(), 0);
    await page.getByRole('button', { name: 'Reveal grading mechanics', exact: true }).click();
    await page.locator(`[data-story-step="${beat('limits')}"]`).click();
    assert.equal(await page.locator('[data-pathology100-reference-revealed]').count(), 0);
    await page.locator(`[data-story-step="${beat('reference')}"]`).click();
    assert.equal(await page.locator('[data-pathology100-reference-revealed]').count(), 0);
    await page.locator('.scene-reset').click();
    await page.locator(`[data-story-step="${beat('group')}"]`).click();
    assert.equal(
      await assistance
        .getByRole('button', { name: 'lite', exact: true })
        .getAttribute('aria-pressed'),
      'true',
    );
    assert.match(
      await page.locator('[data-pathology100-tier]').innerText(),
      /Release-owned BLIP inference-only.*no website checkpoint/s,
    );
    await assistance.getByRole('button', { name: 'standard', exact: true }).click();
    await page.locator('[data-pathology100-step="2"]').click();
    await page.locator('[data-pathology100-step="0"]').click();
    assert.equal(
      await assistance
        .getByRole('button', { name: 'lite', exact: true })
        .getAttribute('aria-pressed'),
      'true',
    );
    await page.locator('[data-story-step="0"]').click();
  }
  if (plan.recipe === 'automed-mimic-report-v1') {
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    const beat = (name) => plan.beats.findIndex((b) => b.scene === name);
    await page.locator('[data-story-step="0"]').click();
    assert.equal(await page.locator('[data-mimic-input] img').count(), 0);
    assert.match(
      await page.locator('[data-mimic-input]').innerText(),
      /first_three_underscore_fields.*Unknown views\/count.*no independent-patient, geometry or temporal-order/s,
    );
    assert.match(
      await page.locator('[data-mimic-input]').innerText(),
      /test_mimic_100_v4.*actual discovered case count absent/s,
    );
    assert.match(
      await page.locator('[data-mimic-output]').innerText(),
      /Report text.*unset.*fractions 0–1.*no clinical accuracy/s,
    );
    await page.locator(`[data-story-step="${beat('helper')}"]`).click();
    const classes = [
      'support_devices',
      'no_acute_process',
      'clear_lungs',
      'low_lung_volumes',
      'consolidation',
      'pleural_effusion',
      'pneumothorax',
      'pulmonary_edema',
      'cardiomegaly',
      'adenopathy_or_mass',
      'granuloma_or_calcified_nodule',
      'post_surgical_changes',
    ];
    assert.deepEqual(await page.locator('[data-mimic-helper] code').allTextContents(), classes);
    assert.match(
      await page.locator('[data-mimic-helper]').innerText(),
      /12 binary text regex.*original 14.*no image-derived finding/s,
    );
    assert.match(
      await page.locator('[data-mimic-helper]').innerText(),
      /global negative.*Uncertain wording/s,
    );
    await page.locator(`[data-story-step="${beat('operation')}"]`).click();
    const tiers = page.getByRole('group', { name: 'MIMIC method guidance' });
    assert.match(
      await page.locator('[data-mimic-tier]').innerText(),
      /compares.*no fixed checkpoint/,
    );
    await tiers.getByRole('button', { name: 'standard', exact: true }).click();
    assert.match(
      await page.locator('[data-mimic-tier]').innerText(),
      /at least 3.*MLRG.*CXRMate.*HERGen.*R2-LLM.*No performance measured/s,
    );
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(output, `${label}-tier-standard.png`) });
    const stages = [
      'Verify all manifest views and declared filename grouping',
      'Provision tier method and its preprocessing',
      'Generate report under text constraints',
      'Submit every discovered case without reading private references',
    ];
    for (let i = 0; i < 4; i++) {
      const button = page.locator(`[data-mimic-step="${i}"]`);
      await button.click();
      assert.equal(await button.getAttribute('aria-pressed'), 'true');
      assert.equal(await page.locator('[data-mimic-currentstage]').innerText(), stages[i]);
      assert.equal(await page.locator('[data-mimic-private-reference]').count(), 0);
      await page
        .locator('.scene-player')
        .screenshot({ path: path.join(output, `${label}-stage-${i}.png`) });
    }
    await page.locator(`[data-story-step="${beat('output')}"]`).click();
    const format = page.getByRole('button', { name: 'Inspect format constraints', exact: true });
    assert.equal(await page.locator('[data-mimic-format]').count(), 0);
    await format.click();
    assert.match(
      await page.locator('[data-mimic-format]').innerText(),
      /UTF8.*ASCII.*40\.\.8000.*20 alphabetic/s,
    );
    assert.match(
      await page.locator('[data-mimic-output-schema]').innerText(),
      /agent_outputs\/<case_id>\/report.txt.*No report text.*count>0.*rating F/s,
    );
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(output, `${label}-format-revealed.png`) });
    await page.locator(`[data-story-step="${beat('limits')}"]`).click();
    const metrics = page.getByRole('group', { name: 'Report metric aggregation' });
    await metrics.getByRole('button', { name: 'micro', exact: true }).click();
    assert.match(
      await page.locator('[data-mimic-metric]').innerText(),
      /Pool TP\/FP\/FN.*separate diagnostic.*not configured clinical score/s,
    );
    assert.match(
      await page.locator('[data-mimic-limits]').innerText(),
      /Nonempty Findings.*otherwise entire report.*No separate Impression.*Both positive sets empty.*F1=1.*No scores, ratings or outcomes measured/s,
    );
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(output, `${label}-micro.png`) });
    await page.locator(`[data-story-step="${beat('output')}"]`).click();
    assert.equal(await page.locator('[data-mimic-format]').count(), 0);
    await page.locator(`[data-story-step="${beat('limits')}"]`).click();
    assert.equal(
      await metrics
        .getByRole('button', { name: 'macro', exact: true })
        .getAttribute('aria-pressed'),
      'true',
    );
    assert.match(
      await page.locator('[data-mimic-metric]').innerText(),
      /\.7 mean per-case observation F1.*\.3 mean per-case ROUGE-L F1.*all case_ids/s,
    );
    await page.locator('.scene-reset').click();
    await page.locator(`[data-story-step="${beat('operation')}"]`).click();
    assert.equal(
      await tiers.getByRole('button', { name: 'lite', exact: true }).getAttribute('aria-pressed'),
      'true',
    );
    await page.locator('[data-mimic-step="3"]').click();
    await page.locator('[data-mimic-step="0"]').click();
    assert.equal(
      await tiers.getByRole('button', { name: 'lite', exact: true }).getAttribute('aria-pressed'),
      'true',
    );
    await page.locator('[data-story-step="0"]').click();
  }
  if (plan.recipe === 'automed-iu-xray-report-v1') {
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    const beat = (name) => plan.beats.findIndex((b) => b.id === name);
    const scene = page.locator('[data-iu-report-scene]');
    await page.locator('[data-story-step="0"]').click();
    assert.equal(await scene.locator('img').count(), 0);
    assert.match(
      await scene.innerText(),
      /Two authored image sockets.*Actual image\/report\/case count: 0/s,
    );
    assert.match(
      await page.locator('[data-iu-report-output]').innerText(),
      /1 text file per study.*actual Full output empty/s,
    );
    await page.locator(`[data-story-step="${beat('group')}"]`).click();
    const assistance = page.getByRole('navigation', { name: 'IU method assistance' });
    await assistance.getByRole('button', { name: 'standard', exact: true }).click();
    assert.match(
      await page.locator('[data-iu-assistance]').innerText(),
      /at least three.*unprovisioned/s,
    );
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(output, `${label}-tier-standard.png`) });
    const operations = ['Study grouping', 'Text validity', 'Metric binding'];
    const contracts = [
      /every image.*case list.*image count does not multiply reports/s,
      /40–8000.*20 letters.*ASCII printable.*UTF-8.*Unicode.*does not validate medical/s,
      /Seven equal components.*declared intent/s,
    ];
    const navigation = page.getByRole('navigation', { name: 'IU report contract steps' });
    for (let i = 0; i < 3; i++) {
      const button = navigation.getByRole('button', { name: operations[i], exact: true });
      await button.click();
      assert.equal(await button.getAttribute('aria-pressed'), 'true');
      assert.match(await scene.innerText(), contracts[i]);
      assert.equal(await page.locator('[data-iu-report-reference-revealed]').count(), 0);
      await page
        .locator('.scene-player')
        .screenshot({ path: path.join(output, `${label}-contract-${i}.png`) });
    }
    const bindings = page.getByRole('navigation', {
      name: 'IU declared versus executable metrics',
    });
    await bindings.getByRole('button', { name: 'Executable default', exact: true }).click();
    assert.match(
      await page.locator('[data-iu-binding]').innerText(),
      /Missing clinical_score_backend\/weights.*0.7 observation F1.*0.3 ROUGE-L.*0–1.*not clinical accuracy/s,
    );
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(output, `${label}-executable-default.png`) });
    await page.locator(`[data-story-step="${beat('format')}"]`).click();
    await page.locator(`[data-story-step="${beat('metric')}"]`).click();
    assert.equal(
      await bindings
        .getByRole('button', { name: 'Declared seven', exact: true })
        .getAttribute('aria-pressed'),
      'true',
    );
    assert.match(
      await page.locator('[data-iu-binding]').innerText(),
      /BLEU.*METEOR.*ROUGE-L.*F1RadGraph.*precision.*recall.*F1.*absent/s,
    );
    await page.locator(`[data-story-step="${beat('output')}"]`).click();
    const format = page.getByRole('button', { name: 'Inspect text format', exact: true });
    assert.equal(await page.locator('[data-iu-format]').count(), 0);
    await format.click();
    assert.match(
      await page.locator('[data-iu-format]').innerText(),
      /UTF-8.*40–8000.*20 letters.*ASCII.*No JSON.*factual/s,
    );
    assert.match(
      await scene.locator('pre').innerText(),
      /illustrative text.*no patient or medical finding/s,
    );
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(output, `${label}-format-revealed.png`) });
    await page.locator(`[data-story-step="${beat('reference')}"]`).click();
    assert.match(
      await page.locator('[data-iu-report-reference-revealed]').innerText(),
      /all supplied studies.*missing\/invalid.*forces F.*zeroes.*Raw micro.*no actual score/s,
    );
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(output, `${label}-mechanics-revealed.png`) });
    await page.locator(`[data-story-step="${beat('output')}"]`).click();
    assert.equal(await page.locator('[data-iu-format]').count(), 0);
    assert.equal(await page.locator('[data-iu-report-reference-revealed]').count(), 0);
    await page.locator('.scene-reset').click();
    await page.locator(`[data-story-step="${beat('group')}"]`).click();
    assert.equal(
      await assistance
        .getByRole('button', { name: 'lite', exact: true })
        .getAttribute('aria-pressed'),
      'true',
    );
    assert.match(
      await page.locator('[data-iu-assistance]').innerText(),
      /CheXagent-2-3b.*every JPEG/s,
    );
    await page.locator('[data-story-step="0"]').click();
  }
  if (plan.recipe === 'automed-chexpert-report-v1') {
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    const step = (name) => plan.beats.findIndex((b) => b.scene === name);
    await page.locator('[data-story-step="0"]').click();
    assert.equal(await page.locator('[data-chexpert-input] img').count(), 0);
    assert.match(
      await page.locator('[data-chexpert-input]').innerText(),
      /Study unit.*patient join unknown/s,
    );
    assert.match(await page.locator('[data-chexpert-output]').innerText(), /Report text.*unset/s);
    await page.locator(`[data-story-step="${step('helper')}"]`).click();
    const classes = [
      'support_devices',
      'no_acute_process',
      'clear_lungs',
      'low_lung_volumes',
      'consolidation',
      'pleural_effusion',
      'pneumothorax',
      'pulmonary_edema',
      'cardiomegaly',
      'adenopathy_or_mass',
      'granuloma_or_calcified_nodule',
      'post_surgical_changes',
    ];
    assert.equal(await page.locator('[data-chexpert-helper] code').count(), 12);
    assert.deepEqual(await page.locator('[data-chexpert-helper] code').allTextContents(), classes);
    assert.match(
      await page.locator('[data-chexpert-helper]').innerText(),
      /binary text regex.*original14.*no image-derived finding/s,
    );
    assert.match(await page.locator('[data-chexpert-helper]').innerText(), /global negative match/);
    await page.locator(`[data-story-step="${step('operation')}"]`).click();
    const tiers = page.getByRole('group', { name: 'CheXpert method guidance' });
    await tiers.getByRole('button', { name: 'standard', exact: true }).click();
    assert.match(
      await page.locator('[data-chexpert-operation]').innerText(),
      /CheXagent-2-3b.*CheXagent-8b.*MedVersa.*MAIRA-2.*at least two/s,
    );
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(output, `${label}-tier-standard.png`) });
    const operations = [
      'Verify single frontal view and staged case identity',
      'Provision tier method and its preprocessing',
      'Generate report under text constraints',
      'Submit every discovered case without reading private references',
    ];
    const questions = [
      /S1 plan.md.*model variant.*processor\/tokenizer/s,
      /S2 setup.*CUDA_VISIBLE_DEVICES.*workers.*2/s,
      /S3 example guidance.*40 alphabetic.*60 seconds.*20 alphabetic/s,
      /S4\/S5.*every discovered study.*private reports\/labels outside generation/s,
    ];
    const navigation = page.getByRole('navigation', { name: 'CheXpert canonical operation steps' });
    for (let i = 0; i < 4; i++) {
      const button = navigation.getByRole('button', { name: operations[i], exact: true });
      await button.click();
      assert.equal(await button.getAttribute('aria-pressed'), 'true');
      assert.match(await page.locator('[data-chexpert-stage-question]').innerText(), questions[i]);
      assert.equal(await page.locator('[data-chexpert-operation] li').innerText(), operations[i]);
      assert.equal(await page.locator('[data-chexpert-private-reference]').count(), 0);
      if (i === 2)
        await page
          .locator('.scene-player')
          .screenshot({ path: path.join(output, `${label}-s3-checker-difference.png`) });
    }
    await page.locator(`[data-story-step="${step('output')}"]`).click();
    const format = page.getByRole('button', { name: 'Inspect format constraints', exact: true });
    assert.equal(await page.locator('[data-chexpert-format]').count(), 0);
    await format.click();
    assert.match(
      await page.locator('[data-chexpert-format]').innerText(),
      /UTF8.*ASCII.*40\.\.8000.*20 alphabetic/s,
    );
    assert.match(
      await page.locator('[data-chexpert-output-schema]').innerText(),
      /agent_outputs\/<case_id>\/report.txt.*No report text.*count>0.*rating F/s,
    );
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(output, `${label}-format-revealed.png`) });
    await page.locator(`[data-story-step="${step('limits')}"]`).click();
    const metrics = page.getByRole('group', { name: 'Report metric aggregation' });
    await metrics.getByRole('button', { name: 'micro', exact: true }).click();
    assert.match(
      await page.locator('[data-chexpert-metric]').innerText(),
      /Pool TP\/FP\/FN.*separate diagnostic.*not configured clinical score/s,
    );
    const sections = page.getByRole('group', { name: 'Reference text selector mechanics' });
    await sections.getByRole('button', { name: 'Full-report fallback', exact: true }).click();
    assert.match(
      await page.locator('[data-chexpert-selector]').innerText(),
      /full stripped report.*no separate Impression selector/,
    );
    assert.match(
      await page.locator('[data-chexpert-limits]').innerText(),
      /Both positive sets empty.*F1=1.*No scores, ratings or outcomes measured/s,
    );
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(output, `${label}-micro-fallback.png`) });
    await metrics.getByRole('button', { name: 'macro', exact: true }).click();
    assert.match(
      await page.locator('[data-chexpert-metric]').innerText(),
      /\.7 mean per-case observation F1.*\.3 mean per-case ROUGE-L F1.*all case_ids/s,
    );
    await page.locator(`[data-story-step="${step('output')}"]`).click();
    assert.equal(await page.locator('[data-chexpert-format]').count(), 0);
    await page.locator(`[data-story-step="${step('limits')}"]`).click();
    assert.equal(
      await metrics
        .getByRole('button', { name: 'macro', exact: true })
        .getAttribute('aria-pressed'),
      'true',
    );
    assert.equal(
      await sections
        .getByRole('button', { name: 'Nonempty Findings', exact: true })
        .getAttribute('aria-pressed'),
      'true',
    );
    await page.locator('.scene-reset').click();
    await page.locator(`[data-story-step="${step('operation')}"]`).click();
    assert.equal(
      await tiers.getByRole('button', { name: 'lite', exact: true }).getAttribute('aria-pressed'),
      'true',
    );
    await page.locator('[data-story-step="0"]').click();
  }
  if (plan.recipe === 'automed-skin-lesion-cls-v1') {
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    await page.locator('[data-story-step="0"]').click();
    const native = page.locator('[data-skin-lesion-scene="input"] img');
    assert.deepEqual(await native.evaluate((e) => [e.naturalWidth, e.naturalHeight]), [600, 450]);
    assert.doesNotMatch(
      await page.locator('.scene-player').innerText(),
      /diagnosis_3|Nevus;|serial imaging/,
    );
    assert.match(
      await page.locator('[data-skin-lesion-output]').innerText(),
      /Actual Full prediction.reference absent/,
    );
    const processor = plan.beats.findIndex((b) => b.id === 'processor');
    const mapping = plan.beats.findIndex((b) => b.id === 'mapping');
    const files = plan.beats.findIndex((b) => b.id === 'files');
    const out = plan.beats.findIndex((b) => b.scene === 'output');
    const reference = plan.beats.findIndex((b) => b.scene === 'reference');
    const limits = plan.beats.findIndex((b) => b.scene === 'limits');
    await page.locator(`[data-story-step="${processor}"]`).click();
    const steps = page.getByRole('navigation', { name: 'Classification steps' });
    for (const [name, pattern] of [
      ['RGB processor settings', /224.224.*1\/255.*settings only/],
      ['Seven-class remap', /index 0.*akiec.*actinic_keratoses/s],
      ['Canonical files', /All staged IDs.*one canonical string/s],
    ]) {
      await steps.getByRole('button', { name, exact: true }).click();
      assert.equal(
        await steps.getByRole('button', { name, exact: true }).getAttribute('aria-pressed'),
        'true',
      );
      assert.match(await page.locator('[data-skin-lesion-scene]').innerText(), pattern);
    }
    await page.locator(`[data-story-step="${mapping}"]`).click();
    const map = page.getByRole('navigation', { name: 'Inspect seven checkpoint label mappings' });
    const abbreviations = ['akiec', 'bcc', 'bkl', 'df', 'mel', 'nv', 'vasc'];
    const canonical = [
      'actinic_keratoses',
      'basal_cell_carcinoma',
      'benign_keratosis_like_lesions',
      'dermatofibroma',
      'melanoma',
      'melanocytic_nevi',
      'vascular_lesions',
    ];
    for (let i = 0; i < 7; i++) {
      const button = map.getByRole('button', { name: `${i}:${abbreviations[i]}`, exact: true });
      await button.click();
      assert.equal(await button.getAttribute('aria-pressed'), 'true');
      assert.match(
        await page.locator('[data-skin-lesion-scene]').innerText(),
        new RegExp(`index ${i}.*${abbreviations[i]}.*${canonical[i]}`, 's'),
      );
      assert.match(
        await page.locator('[data-skin-lesion-scene]').innerText(),
        /No argmax, logits or image prediction/,
      );
    }
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(output, `${label}-mapping-seven.png`) });
    await page.locator(`[data-story-step="${processor}"]`).click();
    const views = page.getByRole('navigation', {
      name: 'Native display versus processor contract',
    });
    for (const [name, pattern] of [
      ['Native display', /600.450.*no model tensor/],
      ['Processor settings', /224.224.*1\/255/],
    ]) {
      await views.getByRole('button', { name, exact: true }).click();
      assert.match(await page.locator('[data-skin-lesion-preprocessing]').innerText(), pattern);
    }
    await views.getByRole('button', { name: 'Native display', exact: true }).click();
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(output, `${label}-native-contract.png`) });
    await page.locator(`[data-story-step="${files}"]`).click();
    await page.locator(`[data-story-step="${processor}"]`).click();
    assert.equal(
      await views
        .getByRole('button', { name: 'Processor settings', exact: true })
        .getAttribute('aria-pressed'),
      'true',
    );
    await page.locator(`[data-story-step="${out}"]`).click();
    const formats = page.getByRole('navigation', { name: 'Skin classification submission format' });
    for (const name of ['json', 'csv']) {
      await formats.getByRole('button', { name, exact: true }).click();
      assert.equal(
        await page.locator('[data-skin-lesion-fields]').innerText(),
        name === 'csv' ? 'patient_id,label' : 'label',
      );
      assert.match(
        await page.locator('[data-skin-lesion-scene]').innerText(),
        /Authored toy formatting, unrelated to the source image/,
      );
    }
    await formats.getByRole('button', { name: 'json', exact: true }).click();
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(output, `${label}-format-json.png`) });
    await page.locator(`[data-story-step="${reference}"]`).click();
    assert.equal(await page.locator('[data-skin-lesion-reference-revealed]').count(), 1);
    assert.match(
      await page.locator('[data-skin-lesion-reference-revealed]').innerText(),
      /Absent GT classes omitted.*missing predictions wrong/s,
    );
    await page.locator(`[data-story-step="${limits}"]`).click();
    assert.equal(await page.locator('[data-skin-lesion-reference-revealed]').count(), 0);
    await page.locator(`[data-story-step="${out}"]`).click();
    assert.equal(
      await formats.getByRole('button', { name: 'csv', exact: true }).getAttribute('aria-pressed'),
      'true',
    );
    await page.locator('.scene-reset').click();
    assert.equal(await page.locator('[data-skin-lesion-reference-revealed]').count(), 0);
    await page.locator(`[data-story-step="${mapping}"]`).click();
    assert.equal(
      await map.getByRole('button', { name: '0:akiec', exact: true }).getAttribute('aria-pressed'),
      'true',
    );
    await page.locator('[data-story-step="0"]').click();
  }
  if (plan.recipe === 'automed-pcam-cls-v1') {
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    const step = (scene) => plan.beats.findIndex((b) => b.scene === scene);
    const classes = ['negative', 'positive'];
    await page.locator('[data-story-step="0"]').click();
    assert.equal(await page.locator('[data-pcam-cls-input] img').count(), 0);
    const geometry = page.locator('[data-pcam-cls-input] svg');
    assert.equal(await geometry.count(), 1);
    assert.equal(await geometry.getAttribute('viewBox'), '0 0 112 112');
    const center = geometry.locator('rect').nth(1);
    assert.deepEqual(
      await center.evaluate((e) => ['x', 'y', 'width', 'height'].map((k) => e.getAttribute(k))),
      ['40', '40', '32', '32'],
    );
    const windows = page.getByRole('group', { name: 'PCam label window' });
    for (const name of ['Outer context', 'Label center']) {
      const button = windows.getByRole('button', { name, exact: true });
      await button.click();
      assert.equal(await button.getAttribute('aria-pressed'), 'true');
      assert.match(
        await page.locator('[data-pcam-cls-window]').innerText(),
        name === 'Label center'
          ? /at least one annotated tumor pixel.*center/
          : /Outer tumor alone does not set positive/,
      );
      assert.equal(await center.getAttribute('stroke-dasharray'), '2 2');
      await page.locator('.scene-player').screenshot({
        path: path.join(output, `${label}-window-${name.replaceAll(' ', '-')}.png`),
      });
    }
    assert.doesNotMatch(
      await page.locator('.scene-player').innerText(),
      /1600 x 400 source collage|green boxes source positives/,
    );
    await page.locator(`[data-story-step="${step('helper')}"]`).click();
    assert.equal(await page.locator('[data-pcam-cls-figure-revealed]').count(), 0);
    assert.match(
      await page.locator('[data-pcam-cls-helper]').innerText(),
      /0.*negative.*1.*positive/s,
    );
    assert.equal(await page.locator('[data-pcam-cls-helper] img').count(), 0);
    await page.getByRole('button', { name: 'Reveal annotated source figure', exact: true }).click();
    const figure = page.locator('[data-pcam-cls-figure-revealed]');
    assert.match(
      await figure.innerText(),
      /1600 x 400 source collage.*green boxes source positives.*no row\/Full IDs or partition match/s,
    );
    assert.deepEqual(
      await figure.locator('img').evaluate((e) => [e.naturalWidth, e.naturalHeight]),
      [1600, 400],
    );
    assert.match(
      await page.locator('[data-pcam-cls-output]').innerText(),
      /patient_id\s+unset\s+label\s+unset/s,
    );
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(output, `${label}-figure-revealed.png`) });
    await page.getByRole('button', { name: 'Hide annotated source figure', exact: true }).click();
    assert.equal(await page.locator('[data-pcam-cls-figure-revealed]').count(), 0);
    await page.getByRole('button', { name: 'Reveal annotated source figure', exact: true }).click();
    await page.locator('.scene-play').click();
    await page.waitForFunction(
      (frame) =>
        Number(document.querySelector('.scene-player')?.getAttribute('data-committed-frame')) >
        frame,
      plan.beats[step('helper')].startFrame + 4,
    );
    await page.locator('.scene-play').click();
    await page.locator(`[data-story-step="${step('helper')}"]`).click();
    assert.equal(
      await page.locator('[data-pcam-cls-figure-revealed]').count(),
      0,
      'Backward seek must cover training annotation',
    );
    await page.getByRole('button', { name: 'Reveal annotated source figure', exact: true }).click();
    await page.locator('[data-story-step="0"]').click();
    assert.equal(await page.locator('[data-pcam-cls-figure-revealed]').count(), 0);
    await page.locator(`[data-story-step="${step('operation')}"]`).click();
    const tiers = page.getByRole('group', { name: 'PCam classification assistance' });
    for (const name of ['standard', 'lite']) {
      const button = tiers.getByRole('button', { name, exact: true });
      await button.click();
      assert.equal(await button.getAttribute('aria-pressed'), 'true');
      assert.match(await page.locator('[data-pcam-cls-operation]').innerText(), new RegExp(name));
      await page
        .locator('.scene-player')
        .screenshot({ path: path.join(output, `${label}-tier-${name}.png`) });
    }
    const token = page.getByRole('combobox', { name: 'Hypothetical canonical token' });
    for (const c of classes) {
      await token.selectOption(c);
      assert.equal(
        await page.locator('[data-pcam-cls-map]').innerText(),
        `Canonical spelling: ${c}`,
      );
      assert.match(
        await page.locator('[data-pcam-cls-output]').innerText(),
        /patient_id\s+unset\s+label\s+unset/s,
      );
    }
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(output, `${label}-mapping.png`) });
    await page.locator(`[data-story-step="${step('output')}"]`).click();
    const formats = page.getByRole('group', { name: 'PCam classification submission format' });
    for (const name of ['json', 'csv']) {
      const button = formats.getByRole('button', { name, exact: true });
      await button.click();
      assert.equal(await button.getAttribute('aria-pressed'), 'true');
      assert.match(
        await page.locator('[data-pcam-cls-format]').innerText(),
        name === 'csv' ? /predictions\.csv/ : /prediction\.json/,
      );
      assert.match(
        await page.locator('[data-pcam-cls-output-schema]').innerText(),
        /label\s+unset/s,
      );
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
        await page.locator('[data-pcam-cls-metric]').innerText(),
        name === 'accuracy' ? /all.*IDs/i : /positive|support|present/i,
      );
      assert.match(await page.locator('[data-pcam-cls-limits]').innerText(), /0\.\.1|0–1/);
      await page.locator('.scene-player').screenshot({
        path: path.join(output, `${label}-metric-${name.replaceAll(' ', '-')}.png`),
      });
    }
    await page.locator('.scene-reset').click();
    await page.waitForFunction(
      () => document.querySelector('.scene-player')?.getAttribute('data-committed-frame') === '0',
    );
    await page.locator('[data-story-step="0"]').click();
    assert.equal(
      await windows
        .getByRole('button', { name: 'Label center', exact: true })
        .getAttribute('aria-pressed'),
      'true',
    );
    await page.locator(`[data-story-step="${step('helper')}"]`).click();
    assert.equal(await page.locator('[data-pcam-cls-figure-revealed]').count(), 0);
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
  if (plan.recipe === 'automed-crc-cls-v1') {
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    const step = (scene) => plan.beats.findIndex((b) => b.scene === scene);
    const classes = ['adi', 'back', 'deb', 'lym', 'muc', 'mus', 'norm', 'str', 'tum'];
    await page.locator('[data-story-step="0"]').click();
    assert.deepEqual(
      await page
        .locator('[data-crc-cls-input] img')
        .evaluate((e) => [e.naturalWidth, e.naturalHeight]),
      [224, 224],
    );
    assert.match(
      await page.locator('[data-crc-cls-input]').innerText(),
      /0\.5.*µm.*source description/s,
    );
    assert.doesNotMatch(
      await page.locator('.scene-player').innerText(),
      /ADI-AAAMHQMK|Source folder ADI/,
    );
    await page.locator(`[data-story-step="${step('helper')}"]`).click();
    assert.equal(await page.locator('[data-crc-cls-training-revealed]').count(), 0);
    for (const c of classes)
      assert.match(
        await page.locator('[data-crc-cls-helper]').innerText(),
        new RegExp(`${c.toUpperCase()}.*${c}`),
      );
    await page.getByRole('button', { name: 'Reveal training annotation', exact: true }).click();
    assert.match(
      await page.locator('[data-crc-cls-training-revealed]').innerText(),
      /Source folder ADI.*adi.*Public source annotation only/s,
    );
    assert.match(
      await page.locator('[data-crc-cls-output]').innerText(),
      /patient_id\s+unset\s+label\s+unset/s,
    );
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(output, `${label}-training-revealed.png`) });
    await page.getByRole('button', { name: 'Hide training annotation', exact: true }).click();
    assert.equal(await page.locator('[data-crc-cls-training-revealed]').count(), 0);
    await page.getByRole('button', { name: 'Reveal training annotation', exact: true }).click();
    await page.locator('.scene-play').click();
    await page.waitForFunction(
      (frame) =>
        Number(document.querySelector('.scene-player')?.getAttribute('data-committed-frame')) >
        frame,
      plan.beats[step('helper')].startFrame + 4,
    );
    await page.locator('.scene-play').click();
    await page.locator(`[data-story-step="${step('helper')}"]`).click();
    assert.equal(
      await page.locator('[data-crc-cls-training-revealed]').count(),
      0,
      'Backward seek must cover training annotation',
    );
    await page.getByRole('button', { name: 'Reveal training annotation', exact: true }).click();
    await page.locator('[data-story-step="0"]').click();
    assert.equal(await page.locator('[data-crc-cls-training-revealed]').count(), 0);
    await page.locator(`[data-story-step="${step('operation')}"]`).click();
    const tiers = page.getByRole('group', { name: 'CRC classification assistance' });
    for (const name of ['standard', 'lite']) {
      const button = tiers.getByRole('button', { name, exact: true });
      await button.click();
      assert.equal(await button.getAttribute('aria-pressed'), 'true');
      assert.match(await page.locator('[data-crc-cls-operation]').innerText(), new RegExp(name));
      await page
        .locator('.scene-player')
        .screenshot({ path: path.join(output, `${label}-tier-${name}.png`) });
    }
    const token = page.getByRole('combobox', { name: 'Hypothetical tissue token' });
    for (const c of classes) {
      await token.selectOption(c);
      assert.equal(
        await page.locator('[data-crc-cls-map]').innerText(),
        `Canonical spelling: ${c}`,
      );
      assert.match(
        await page.locator('[data-crc-cls-output]').innerText(),
        /patient_id\s+unset\s+label\s+unset/s,
      );
    }
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(output, `${label}-mapping.png`) });
    await page.locator(`[data-story-step="${step('output')}"]`).click();
    const formats = page.getByRole('group', { name: 'CRC classification submission format' });
    for (const name of ['json', 'csv']) {
      const button = formats.getByRole('button', { name, exact: true });
      await button.click();
      assert.equal(await button.getAttribute('aria-pressed'), 'true');
      assert.match(
        await page.locator('[data-crc-cls-format]').innerText(),
        name === 'csv' ? /predictions\.csv/ : /prediction\.json/,
      );
      assert.match(
        await page.locator('[data-crc-cls-output-schema]').innerText(),
        /label\s+unset/s,
      );
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
        await page.locator('[data-crc-cls-metric]').innerText(),
        name === 'accuracy' ? /all.*IDs/i : /positive|support|present/i,
      );
      assert.match(
        await page.locator('[data-crc-cls-limits]').innerText(),
        /headline accuracy.*balanced accuracy.*discrepancy/s,
      );
      assert.match(await page.locator('[data-crc-cls-limits]').innerText(), /0\.\.1|0–1/);
      await page.locator('.scene-player').screenshot({
        path: path.join(output, `${label}-metric-${name.replaceAll(' ', '-')}.png`),
      });
    }
    await page.locator('.scene-reset').click();
    await page.waitForFunction(
      () => document.querySelector('.scene-player')?.getAttribute('data-committed-frame') === '0',
    );
    await page.locator(`[data-story-step="${step('helper')}"]`).click();
    assert.equal(await page.locator('[data-crc-cls-training-revealed]').count(), 0);
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
  if (plan.recipe === 'automed-pneumonia-cls-v1') {
    if ((await page.locator('.scene-player').getAttribute('data-playing')) === 'true')
      await page.locator('.scene-play').click();
    const inputIndex = plan.beats.findIndex((b) => b.scene === 'input');
    await page.locator(`[data-story-step="${inputIndex}"]`).click();
    const native = page.locator('[data-pneumonia-native]');
    assert.equal(await native.count(), 1);
    assert.deepEqual(await native.evaluate((e) => [e.naturalWidth, e.naturalHeight]), [2090, 1858]);
    assert.match(await page.locator('[data-pneumonia-output]').innerText(), /output absent/);
    assert.equal(await page.locator('[data-pneumonia-training-label]').count(), 0);
    assert.doesNotMatch(
      await page.locator('.scene-player').innerText(),
      /Public training helper: NORMAL/,
    );
    const operationIndex = plan.beats.findIndex((b) => b.scene === 'operation');
    await page.locator(`[data-story-step="${operationIndex}"]`).click();
    const steps = page.getByRole('navigation', { name: 'Classification implementation steps' });
    const names = ['Training-only preprocessing', 'Class index mapping', 'All-case file output'];
    const expected = [
      /preprocessing|normalization/i,
      /0.*normal.*1.*pneumonia/s,
      /exactly one canonical class/,
    ];
    for (const [i, name] of names.entries()) {
      const button = steps.getByRole('button', { name, exact: true });
      await button.click();
      assert.equal(await button.getAttribute('aria-pressed'), 'true');
      assert.equal(
        await page
          .locator('[data-pneumonia-operation-step]')
          .getAttribute('data-pneumonia-operation-step'),
        String(i),
      );
      assert.match(await page.locator('[data-pneumonia-scene]').innerText(), expected[i]);
      assert.equal(await page.locator('[data-pneumonia-reference-revealed]').count(), 0);
      assert.match(await page.locator('[data-pneumonia-output]').innerText(), /output absent/);
      await page
        .locator('.scene-player')
        .screenshot({ path: path.join(output, `${label}-operation-${i}.png`) });
    }
    const outputIndex = plan.beats.findIndex((b) => b.scene === 'output');
    await page.locator(`[data-story-step="${outputIndex}"]`).click();
    assert.match(
      await page.locator('[data-pneumonia-scene]').innerText(),
      /participant_prediction:.*—/s,
    );
    assert.match(
      await page.locator('[data-pneumonia-scene]').innerText(),
      /Authored toy syntax.*not the displayed native image/s,
    );
    const referenceIndex = plan.beats.findIndex((b) => b.scene === 'reference');
    await page.locator(`[data-story-step="${referenceIndex}"]`).click();
    assert.match(
      await page.locator('[data-pneumonia-reference-revealed]').innerText(),
      /n_correct.*len\(patient_ids\).*Missing prediction or reference/s,
    );
    await page
      .locator('.scene-player')
      .screenshot({ path: path.join(output, `${label}-denominator.png`) });
    assert.match(
      await page.locator('[data-pneumonia-training-label]').innerText(),
      /NORMAL.*normal/s,
    );
    const limitsIndex = plan.beats.findIndex((b) => b.scene === 'limits');
    await page.locator(`[data-story-step="${limitsIndex}"]`).click();
    assert.equal(await page.locator('[data-pneumonia-reference-revealed]').count(), 0);
    assert.match(
      await page.locator('[data-pneumonia-scene]').innerText(),
      /Generic S4\/S5.*segmentation masks.*classification/s,
    );
    await page.locator(`[data-story-step="${referenceIndex}"]`).click();
    await page.locator('[data-story-step="0"]').click();
    assert.equal(
      await page.locator('[data-pneumonia-reference-revealed]').count(),
      0,
      'Backward chapter seek must cover scorer rules',
    );
    assert.equal(await page.locator('[data-pneumonia-training-label]').count(), 0);
    await page.locator('.scene-reset').click();
    await page.waitForFunction(
      () => document.querySelector('.scene-player')?.getAttribute('data-committed-frame') === '0',
    );
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
    assert.equal(
      plan.reference_policy,
      selectors.referencePolicy ||
        (selectors.readerControlled ? 'reader-reference-reveal' : 'no-reference-assets'),
    );
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
      'imaging101-usct-fwi-v1',
      'imaging-ultrasound-sos-v1',
      'imaging101-pnp-mri-reconstruction-v1',
      'imaging101-plane-wave-ultrasound-v1',
      'imaging101-photoacoustic-tomography-v1',
      'imaging101-pet-mlem-v1',
      'imaging101-varnet-v1',
      'imaging101-t2-mapping-v1',
      'imaging101-sense-v1',
      'imaging101-pnp-admm-v1',
      'imaging101-noncartesian-v1',
      'imaging101-wavelet-v1',
      'imaging-grappa-v1',
      'imaging-dynamic-mri-v1',
      'imaging-eit-v1',
      'imaging101-poisson-v1',
      'bcer-grappa-v1',
      'bcer-superres-v1',
      'bcer-denoise-v1',
      'automed-slake-v1',
      'automed-pathvqa-v1',
      'automed-vqa-rad-v1',
      'automed-omni-v1',
      'automed-kvasir-v1',
      'automed-medxpert-mm-v1',
      'automed-medframeqa-v1',
      'automed-pathology-caption-500-v1',
      'automed-pathology-caption-100-v1',
      'automed-mimic-report-v1',
      'automed-iu-xray-report-v1',
      'automed-chexpert-report-v1',
      'automed-skin-lesion-cls-v1',
      'automed-pcam-cls-v1',
      'automed-crc-cls-v1',
      'automed-pneumonia-cls-v1',
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
