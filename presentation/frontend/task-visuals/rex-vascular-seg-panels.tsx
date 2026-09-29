import {
  vascularImage,
  vascularRecord,
  vascularRevealed,
  vascularSample,
  type RexVascularSegState,
  type VascularRecord,
} from './rex-vascular-seg';
import shared from './task-visual.module.css';
import css from './rex-vascular-seg.module.css';

const fmt = (n: number) => n.toFixed(1);
const spacing = (n: number) => Number(n.toFixed(6)).toString();
function Scan({
  record,
  slice,
  showSupport = false,
}: {
  record: VascularRecord;
  slice: number;
  showSupport?: boolean;
}) {
  const sample = vascularSample(record.source, slice);
  const index = record.source.samples.indexOf(sample);
  const support = record.support.samples[index];
  const basis = record.source.geometry.orientation.includes('LPS') ? 'LPS' : 'RAS';
  return (
    <figure className={css.scan} data-vascular-input={record.source.entry_id}>
      <div className={css.scanHead}>
        <b>
          {record.source.modality} · {record.source.case_id}
        </b>
        <span>native {record.source.geometry.shape_ijk.join('×')}</span>
      </div>
      <div className={css.scanFrame}>
        <img
          src={vascularImage(record.pack, sample.file)}
          alt={`Actual ${record.source.modality} source image, native k=${sample.native_k_zero_based}; no prediction`}
        />
        {showSupport && support && (
          <img
            className={css.overlay}
            src={vascularImage(record.pack, support.file)}
            alt={`${record.privateReference ? 'Reader-only test reference' : 'Public training helper'} vessel labels at native k=${sample.native_k_zero_based}`}
            {...(record.privateReference
              ? { 'data-vascular-reference': '' }
              : { 'data-vascular-helper': '' })}
          />
        )}
      </div>
      <figcaption>
        <b>
          native k={sample.native_k_zero_based} · {basis} center z={fmt(sample.center_world_mm[2])}{' '}
          mm
        </b>
        <span>{record.source.geometry.spacing_ijk_mm.map(spacing).join(' × ')} mm / voxel</span>
      </figcaption>
    </figure>
  );
}

function Rail({ record, slice }: { record: VascularRecord; slice: number }) {
  const selected = record.source.samples.indexOf(vascularSample(record.source, slice));
  return (
    <div className={css.rail} aria-label="Nine fixed native-slice samples">
      {record.source.samples.map((s, i) => (
        <span
          key={s.native_k_zero_based}
          data-current={i === selected}
          title={`native k=${s.native_k_zero_based}`}
        />
      ))}
    </div>
  );
}

function Inputs({ record, state }: { record: VascularRecord; state: RexVascularSegState }) {
  return (
    <div className={css.twoCol}>
      <div>
        <Scan record={record} slice={state.slice} />
        <Rail record={record} slice={state.slice} />
      </div>
      <div className={css.facts} data-vascular-input-facts>
        <b>One verified native {record.source.modality} volume</b>
        <span>{record.source.source_role}. Nine fixed native slices from its full 3D array.</span>
        <b>Physical grid</b>
        <span>
          {record.source.geometry.shape_ijk.join(' × ')} voxels at{' '}
          {record.source.geometry.spacing_ijk_mm.map(spacing).join(' × ')} mm.
        </span>
        <b>Answer requested</b>
        <span>{record.taskType}; no mask produced in this retained record.</span>
        <small>Input image only at opening. Labels appear in a separate explicit chapter.</small>
      </div>
    </div>
  );
}

function Geometry({ record, state }: { record: VascularRecord; state: RexVascularSegState }) {
  const s = vascularSample(record.source, state.slice);
  const basis = record.source.geometry.orientation.includes('LPS') ? 'LPS' : 'RAS';
  return (
    <div className={css.twoCol} data-vascular-geometry>
      <div>
        <Scan record={record} slice={state.slice} />
        <Rail record={record} slice={state.slice} />
      </div>
      <div className={css.facts}>
        <b>Voxel index → world millimeters</b>
        <span>
          Native voxel (i, j, k) follows the source {basis} affine/direction, not a generic screen
          coordinate.
        </span>
        <div className={css.equation}>
          [i, j, {s.native_k_zero_based}, 1] → {basis} z {fmt(s.center_world_mm[2])} mm at volume
          center
        </div>
        <b>Display resampling</b>
        <span>
          PNG x=i and y reverses native j; the longest axis is capped at 384 pixels using
          nearest-neighbor sampling. The original 3D array and physical map remain pinned.
        </span>
        <small>Matching screen pixels in another scan are not registered physical points.</small>
      </div>
    </div>
  );
}

function Operation({ record, state }: { record: VascularRecord; state: RexVascularSegState }) {
  return (
    <div className={css.operation} data-vascular-operation>
      <div>
        <Scan record={record} slice={state.slice} />
        <Rail record={record} slice={state.slice} />
      </div>
      <div className={css.flow}>
        <article>
          <b>1 · Read native volume</b>
          <span>
            {record.source.modality} voxels and their{' '}
            {record.source.geometry.orientation.includes('LPS') ? 'LPS' : 'RAS'} mm map.
          </span>
        </article>
        <article>
          <b>2 · Assign labels</b>
          <span>
            {record.taskType} on the required source grid. Training helper or test reference is
            separate from the participant answer.
          </span>
        </article>
        <article className={css.empty}>
          <b>3 · Prediction socket empty</b>
          <span>
            No mask file was retained. This outline is an output requirement, not colored patient
            prediction pixels.
          </span>
        </article>
      </div>
    </div>
  );
}

function Output({ record }: { record: VascularRecord }) {
  return (
    <div className={css.schema} data-vascular-output-schema>
      <b>Required submission · no file produced</b>
      <div>
        <span>CSV</span>
        <code>{record.output.columns.join(',')}</code>
      </div>
      <div>
        <span>Relative path pattern</span>
        <code>{record.output.relative_prediction_pattern}</code>
      </div>
      <div>
        <span>Referenced file</span>
        <code>{record.output.required_file}</code>
      </div>
      <p>
        The path describes what a participant must create for held-out images. It is not a saved
        prediction for the illustrated case.
      </p>
    </div>
  );
}

function Support({ record, state }: { record: VascularRecord; state: RexVascularSegState }) {
  const privateVisible = vascularRevealed(state);
  if (record.privateReference && !privateVisible)
    return (
      <div className={css.covered} data-vascular-reference-hidden>
        <b>Held-out test reference covered</b>
        <span>
          Explicit reader reveal is required. No reference image or values are mounted yet.
        </span>
      </div>
    );
  const s = vascularSample(record.source, state.slice);
  const selected = record.source.samples.indexOf(s);
  return (
    <div
      className={css.twoCol}
      {...(record.privateReference
        ? { 'data-vascular-reference-panel': '' }
        : { 'data-vascular-helper-panel': '' })}
    >
      <div>
        <Scan record={record} slice={state.slice} showSupport />
        <Rail record={record} slice={state.slice} />
      </div>
      <div className={css.facts}>
        <b>
          {record.privateReference ? 'Reader-only test reference' : 'Public training label helper'}
        </b>
        <span>
          Colored pixels are exact source label values on the matching native grid, not confidence
          or a participant prediction.
        </span>
        <div className={css.legend} aria-label="Selected source label color key">
          {record.support.samples[selected].visible_label_values.map((value) => (
            <span key={value}>
              <i style={{ background: record.support.class_colors[String(value)] }} />
              class {value}
            </span>
          ))}
        </div>
        <b>Selected native k={s.native_k_zero_based}</b>
        <span>
          {record.support.samples[selected].nonzero_display_pixels.toLocaleString()} nonzero display
          pixels after nearest-neighbor sampling.
        </span>
        <span>
          {record.support.classes_present.length - 1} nonzero values occur in the full source label;
          this is not a score.
        </span>
        <small>
          {record.privateReference
            ? 'The source label is private answer material in ReX staging. It was not supplied to the solver.'
            : 'This source label is permitted training help, not the held-out test answer.'}
        </small>
      </div>
    </div>
  );
}

function Limits({ record }: { record: VascularRecord }) {
  return (
    <div className={css.limits} data-vascular-limits>
      <article>
        <b>One source case</b>
        <span>
          Exact native image and annotation, not a cohort result. The split is statically
          reconstructed from the pinned adapter; preparer not executed.
        </span>
      </article>
      <article>
        <b>What the grader compares</b>
        <span>{record.scorer}</span>
      </article>
      <article>
        <b>Interpretation limit</b>
        <span>{record.caveat}</span>
      </article>
      <div className={css.limitFooter}>
        No ReX submission, grader execution, participant metric, or clinical assessment is
        represented.
      </div>
    </div>
  );
}

const titles: Record<RexVascularSegState['scene'], string> = {
  inputs: 'Read the exact source image',
  geometry: 'Locate voxels in native physical space',
  operation: 'From volume to label grid',
  output: 'Specify the empty answer contract',
  helper: 'Inspect a public training label',
  reference: 'Reveal the held-out source reference',
  limits: 'Bound what the source and scorer establish',
};
export function RexVascularSegScene({ state }: { state: RexVascularSegState }) {
  const record = vascularRecord(state.recipe);
  const reveal = vascularRevealed(state);
  return (
    <section
      className={css.scene}
      data-vascular-scene={state.scene}
      data-vascular-recipe={state.recipe}
      data-vascular-reference-state={reveal ? 'revealed' : 'hidden'}
    >
      <h3>{titles[state.scene]}</h3>
      {state.scene === 'inputs' && <Inputs record={record} state={state} />}
      {state.scene === 'geometry' && <Geometry record={record} state={state} />}
      {state.scene === 'operation' && <Operation record={record} state={state} />}
      {state.scene === 'output' && <Output record={record} />}
      {state.scene === 'helper' && !record.privateReference && (
        <Support record={record} state={state} />
      )}
      {state.scene === 'reference' && record.privateReference && (
        <Support record={record} state={state} />
      )}
      {state.scene === 'limits' && <Limits record={record} />}
    </section>
  );
}
export function RexVascularSegOutput({ state }: { state: RexVascularSegState }) {
  const r = vascularRecord(state.recipe);
  const revealed = vascularRevealed(state);
  const status =
    state.scene === 'inputs'
      ? `Input: one native ${r.source.modality} volume`
      : state.scene === 'geometry'
        ? 'Index-to-world mapping is source-pinned.'
        : state.scene === 'operation'
          ? `Task operation: ${r.taskType}.`
          : state.scene === 'output'
            ? 'Required CSV and mask path; no file exists.'
            : state.scene === 'helper'
              ? 'Public source training label, not test truth.'
              : state.scene === 'reference'
                ? revealed
                  ? 'Reader-only private source label revealed.'
                  : 'Private source label covered.'
                : 'Scorer details and single-case limits.';
  return (
    <aside className={`${shared.storyOutput} ${css.output}`} data-vascular-output>
      <b>{state.scene === 'inputs' ? `Input: native ${r.source.modality} volume` : r.title}</b>
      <p>{status}</p>
      {state.scene !== 'inputs' && (
        <>
          <b>Answer-owned output</b>
          <p>No participant prediction or score is retained.</p>
        </>
      )}
      <small>
        {r.license} · one source case · {r.source.geometry.orientation}
      </small>
    </aside>
  );
}
