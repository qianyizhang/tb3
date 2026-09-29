import {
  islesImage,
  islesOutput,
  islesReference,
  islesRevealed,
  islesSample,
  islesSource,
  type IslesModality,
  type RexIslesState,
} from './rex-isles22';
import shared from './task-visual.module.css';
import css from './rex-isles22.module.css';

const modalities = islesSource.modalities;
const fmt = (n: number) => n.toFixed(1);

function Scan({
  modality,
  progress,
  overlay = false,
}: {
  modality: 'dwi' | 'adc' | 'flair';
  progress: number;
  overlay?: boolean;
}) {
  const source = modalities[modality];
  const sample = islesSample(source, progress);
  const sampleIndex = source.samples.indexOf(sample);
  const refSample = islesReference.samples[sampleIndex];
  return (
    <figure className={css.scan} data-isles-input={modality}>
      <div className={css.scanHead}>
        <b>{modality.toUpperCase()}</b>
        <span>{source.shape_ijk.join('×')} voxels</span>
      </div>
      <div className={css.scanFrame}>
        <img
          src={islesImage(sample.image)}
          alt={`Actual ${modality.toUpperCase()} source MRI, native slice k=${sample.native_k_zero_based}; no prediction`}
        />
        {overlay &&
          modality !== 'flair' &&
          refSample?.native_k_zero_based === sample.native_k_zero_based && (
            <img
              className={css.mask}
              data-isles-reference
              src={islesImage(refSample.image)}
              alt={`Reader-only source lesion mask, native slice k=${sample.native_k_zero_based}`}
            />
          )}
      </div>
      <figcaption>
        <b>
          native k={sample.native_k_zero_based} · RAS z {fmt(sample.center_ras_mm[2])} mm
        </b>
        <span>{source.spacing_ijk_mm.map(fmt).join(' × ')} mm / voxel</span>
      </figcaption>
    </figure>
  );
}
function Rail({ modality, progress }: { modality: IslesModality; progress: number }) {
  const selected = modality.samples.indexOf(islesSample(modality, progress));
  return (
    <div className={css.rail} aria-label="Fixed native-slice samples">
      {modality.samples.map((sample, i) => (
        <span
          key={sample.native_k_zero_based}
          data-current={selected === i}
          title={`native k=${sample.native_k_zero_based}; RAS z ${fmt(sample.center_ras_mm[2])} mm`}
        />
      ))}
    </div>
  );
}
function Inputs(state: RexIslesState) {
  return (
    <div className={css.content}>
      <div className={css.scans}>
        <div>
          <Scan modality="dwi" progress={state.slice} />
          <Rail modality={modalities.dwi} progress={state.slice} />
        </div>
        <div>
          <Scan modality="adc" progress={state.slice} />
          <Rail modality={modalities.adc} progress={state.slice} />
        </div>
        <div>
          <Scan modality="flair" progress={state.flair} />
          <Rail modality={modalities.flair} progress={state.flair} />
        </div>
      </div>
      <p className={css.note}>
        DWI and ADC share native voxels. FLAIR has its own 224×256×24 grid and independent sample
        rail; similar RAS z does not mean the images are registered.
      </p>
    </div>
  );
}
function Geometry(state: RexIslesState) {
  const dwi = islesSample(modalities.dwi, state.slice);
  const flair = islesSample(modalities.flair, state.flair);
  return (
    <div className={css.geometry} data-isles-geometry-audit>
      <div className={css.geometryScans}>
        <Scan modality="dwi" progress={state.slice} />
        <Scan modality="flair" progress={state.flair} />
      </div>
      <div className={css.geometryFacts}>
        <strong>Voxel index → NIfTI RAS world mm</strong>
        <span>
          DWI center (63.5, 63.5, {dwi.native_k_zero_based}) → z {fmt(dwi.center_ras_mm[2])} mm
        </span>
        <span>
          FLAIR center (111.5, 127.5, {flair.native_k_zero_based}) → z {fmt(flair.center_ras_mm[2])}{' '}
          mm
        </span>
        <b>Separate affines. No FLAIR-on-DWI mask overlay or image registration is supplied.</b>
      </div>
    </div>
  );
}
function Output() {
  return (
    <div className={css.schema} data-isles-output-schema>
      <div className={css.schemaTitle}>Answer-owned output · empty</div>
      <div className={css.row}>
        <span>submission/submission.csv</span>
        <code>case_id,predicted_mask_path</code>
      </div>
      <div className={css.row}>
        <span>illustrative case row</span>
        <code>{islesOutput.illustrative_row.join(',')}</code>
      </div>
      <div className={css.row}>
        <span>required referenced file</span>
        <code>binary NIfTI · 128×128×25 DWI/ADC voxel grid</code>
      </div>
      <div className={css.empty}>
        <b>No saved prediction</b>
        <span>
          The row is a path contract, not a produced file. A valid workflow must create a mask for
          every held-out case.
        </span>
      </div>
      <div className={css.pipeline}>
        public DWI + ADC + FLAIR <span>→</span> prediction process <span>→</span> empty binary-mask
        socket
      </div>
    </div>
  );
}
function Reference({ state, reveal }: { state: RexIslesState; reveal: boolean }) {
  if (!reveal)
    return (
      <div className={css.covered} data-isles-reference-hidden>
        <b>Private mask covered</b>
        <span>Reader reveal is required before the selected source label is shown.</span>
      </div>
    );
  const sample = islesSample(modalities.dwi, state.slice);
  const index = modalities.dwi.samples.indexOf(sample);
  return (
    <div className={css.reference} data-isles-reference>
      <div className={css.referenceScans}>
        <Scan modality="dwi" progress={state.slice} overlay />
        <div className={css.referenceFacts}>
          <b>
            <i className={css.swatch} /> Source mask, reader only
          </b>
          <span>
            Yellow overlay is the actual selected-case label on the same native DWI/ADC grid.
          </span>
          <strong>
            {islesReference.positive_voxels} / {islesReference.total_voxels.toLocaleString()}{' '}
            reference-positive voxels
          </strong>
          <span>
            Selected native k={sample.native_k_zero_based}:{' '}
            {islesReference.samples[index].positive_voxels_in_slice} labeled voxels.
          </span>
          <small>
            No agent mask, overlap, Dice, lesion F1 or volume-error result was retained.
          </small>
        </div>
      </div>
      <p className={css.note}>
        The label came from the official source archive and is private in ReX test staging. FLAIR
        remains on its own grid.
      </p>
    </div>
  );
}
function Limits() {
  return (
    <div className={css.limits}>
      <article>
        <b>Actual source</b>
        <span>
          Four native files from one exact official case; nine fixed display slices per modality.
          Original 3D arrays and affine hashes are pinned.
        </span>
      </article>
      <article>
        <b>Different grid</b>
        <span>
          FLAIR's 224×256×24 grid is not the DWI/ADC 128×128×25 prediction grid. A matching slice
          index is not physical alignment.
        </span>
      </article>
      <article>
        <b>Evaluator boundary</b>
        <span>
          Pinned grader resizes shape-mismatched predictions with nearest neighbors, then compares
          arrays. It does not validate affines.
        </span>
      </article>
      <div className={css.toy} data-isles-geometry-counterexample>
        <b>Array-wise score ≠ physical alignment</b>
        <span>
          Two same-shape masks can carry shifted affines; the grader's array comparison would not
          inspect that shift. This is a geometry counterexample, not a scored patient prediction.
        </span>
      </div>
    </div>
  );
}
const titles: Record<RexIslesState['scene'], string> = {
  inputs: 'Three real MRI contrasts, two native grids',
  geometry: 'Follow the physical coordinates',
  output: 'Specify the binary NIfTI output',
  reference: 'Reader-only source lesion mask',
  limits: 'What this case and scorer establish',
};
export function RexIslesScene({ state }: { state: RexIslesState }) {
  const reveal = islesRevealed(state);
  return (
    <section
      className={css.scene}
      data-isles-scene={state.scene}
      data-isles-reference-state={reveal ? 'revealed' : 'hidden'}
    >
      <h3>{titles[state.scene]}</h3>
      {state.scene === 'inputs' && <Inputs {...state} />}
      {state.scene === 'geometry' && <Geometry {...state} />}
      {state.scene === 'output' && <Output />}
      {state.scene === 'reference' && <Reference state={state} reveal={reveal} />}
      {state.scene === 'limits' && <Limits />}
    </section>
  );
}
export function RexIslesOutput({ state }: { state: RexIslesState }) {
  const reveal = islesRevealed(state);
  const line =
    state.scene === 'inputs'
      ? 'Public test inputs: DWI, ADC and FLAIR for the selected case.'
      : state.scene === 'geometry'
        ? 'Physical mm coordinates come from each volume’s own NIfTI affine.'
        : state.scene === 'output'
          ? 'A CSV row must point to a produced binary NIfTI. None is retained.'
          : state.scene === 'reference'
            ? reveal
              ? 'The source mask is reader-only; it is not a model output.'
              : 'Private source mask remains covered.'
            : 'Shape resizing cannot establish affine alignment or clinical validity.';
  return (
    <aside className={`${shared.storyOutput} ${css.output}`} data-isles-output>
      <b>{state.scene === 'inputs' ? 'Input: DWI + ADC + FLAIR' : 'Task state'}</b>
      <p>{line}</p>
      <b>Answer-owned output</b>
      <p>No prediction or score retained. The schema is an unfilled submission contract.</p>
      <b>Reference boundary</b>
      <p>
        {reveal
          ? 'Explicit reader reveal; source label on the DWI/ADC grid.'
          : 'Private ReX test mask hidden.'}
      </p>
      <small>ISLES-2022 v2.3.1 · CC BY 4.0 · single-case teaching</small>
    </aside>
  );
}
