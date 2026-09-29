import {
  abraImage,
  abraOutput,
  abraReference,
  abraRevealed,
  abraSample,
  abraSource,
  type AbraLongitudinalState,
  type AbraVisit,
} from './abra-longitudinal';
import shared from './task-visual.module.css';
import css from './abra-longitudinal.module.css';

const visits = abraSource.visits;
const showDate = (raw: string) => `${raw.slice(0, 4)}-${raw.slice(4, 6)}-${raw.slice(6, 8)}`;

function Scan({
  visit,
  position,
  compact = false,
}: {
  visit: AbraVisit;
  position: number;
  compact?: boolean;
}) {
  const sample = abraSample(visit, position);
  const ordinal = sample.sample_order_zero_based + 1;
  return (
    <figure className={css.scan} data-abra-source-ct={visit.role}>
      <div className={css.scanHeader}>
        <b>{visit.role === 'baseline' ? 'Baseline' : 'Follow-up'}</b>
        <span>
          {showDate(visit.study_date_yyyymmdd)} · {visit.kernel}
        </span>
      </div>
      <img
        src={abraImage(sample.image)}
        width="512"
        height="512"
        alt={`${visit.role} native NLST CT; sampled InstanceNumber ${sample.instance_number}, LPS z ${sample.image_position_lps_mm[2]} mm; no annotation or lesion claim`}
      />
      <figcaption>
        <b>Source sample {ordinal}/16</b>
        <span>
          DICOM InstanceNumber {sample.instance_number}/{visit.native_instance_count} · z{' '}
          {sample.image_position_lps_mm[2].toFixed(1)} mm
        </span>
        {!compact && (
          <small>
            512 × 512 px · {sample.pixel_spacing_row_col_mm[0].toFixed(4)} mm/px · native visit
            frame
          </small>
        )}
      </figcaption>
    </figure>
  );
}

function SampleRail({ visit, position }: { visit: AbraVisit; position: number }) {
  const selected = abraSample(visit, position).sample_order_zero_based;
  return (
    <div className={css.rail} aria-label={`${visit.role} independent source sample navigator`}>
      {visit.samples.map((sample, i) => (
        <span
          key={sample.sop_uid}
          data-current={selected === i}
          title={`${visit.role} sample ${i + 1}: native InstanceNumber ${sample.instance_number}, z ${sample.image_position_lps_mm[2]} mm`}
        />
      ))}
    </div>
  );
}

function Inputs(state: AbraLongitudinalState) {
  return (
    <div className={css.inputScene}>
      <div className={css.scans}>
        <Scan visit={visits[0]} position={state.baseline} compact />
        <Scan visit={visits[1]} position={state.followup} compact />
      </div>
      <p className={css.note}>
        These are independent source samples, selected by DICOM InstanceNumber. Matching sample
        positions do not match anatomy or viewer slice indices. Full native series remain retained
        locally.
      </p>
    </div>
  );
}

function Metadata() {
  return (
    <div className={css.operation} data-abra-metadata-operation>
      <div className={css.step}>
        <strong>1 · get_study_metadata</strong>
        <span>Baseline StudyDate</span>
        <b>{showDate(visits[0].study_date_yyyymmdd)}</b>
      </div>
      <div className={css.step}>
        <strong>2 · get_study_metadata</strong>
        <span>Follow-up StudyDate</span>
        <b>{showDate(visits[1].study_date_yyyymmdd)}</b>
      </div>
      <div className={css.formula}>
        <b>Absolute calendar-day interval</b>
        <span>Compute from the two dates, then submit one integer in days.</span>
        <code>answer: ____ days</code>
      </div>
      <p className={css.note}>
        Dates are source input metadata. The benchmark's expected integer stays in a separate
        reader-only reference until explicit reveal.
      </p>
    </div>
  );
}

function Counts() {
  return (
    <div className={css.operation} data-abra-count-operation>
      <div className={css.step}>
        <strong>1 · get_study_series</strong>
        <span>Baseline CT images</span>
        <b>{visits[0].native_instance_count}</b>
      </div>
      <div className={css.step}>
        <strong>2 · get_study_series</strong>
        <span>Follow-up CT images</span>
        <b>{visits[1].native_instance_count}</b>
      </div>
      <div className={css.formula}>
        <b>Signed follow-up − baseline</b>
        <span>
          Order matters. The contract asks for one signed integer, not an unsigned change.
        </span>
        <code>answer: ____ images</code>
      </div>
      <p className={css.note}>
        These are all native CT instances, not the 16 display samples per visit. Source counts are
        available to the solver; the expected answer remains reader-only.
      </p>
    </div>
  );
}

function Browse(state: AbraLongitudinalState) {
  return (
    <div className={css.browse} data-abra-independent-navigation>
      <div className={css.scans}>
        {visits.map((visit, i) => (
          <div key={visit.role} className={css.browseColumn}>
            <Scan visit={visit} position={i ? state.followup : state.baseline} compact />
            <SampleRail visit={visit} position={i ? state.followup : state.baseline} />
          </div>
        ))}
      </div>
      <p className={css.note}>
        Each rail moves through its own 16 evenly spaced native InstanceNumbers. Positions and LPS z
        are per visit; no synchronized anatomy, registration or lesion point is supplied.
      </p>
    </div>
  );
}

function Submit({ multi }: { multi: boolean }) {
  return (
    <div className={css.submit} data-abra-empty-output-schema>
      <div className={css.schemaTitle}>
        ABRA {multi ? 'multiple-new-lesion' : 'single-new-lesion'} submission
      </div>
      <div className={css.schemaRows}>
        <div>
          <span>finding_type</span>
          <code>new_lesion</code>
        </div>
        <div>
          <span>follow-up slice_index</span>
          <code>
            ____ <small>0-based viewer index</small>
          </code>
        </div>
        <div>
          <span>follow-up pixel x, y</span>
          <code>
            ____ , ____ <small>image pixels</small>
          </code>
        </div>
        {multi && (
          <div>
            <span>completion</span>
            <code>submit_longitudinal_complete</code>
          </div>
        )}
      </div>
      <div className={css.empty}>
        <b>Answer-owned output: empty</b>
        <span>
          No agent finding, submission or score was retained. Source CT is input, not a prediction.
        </span>
      </div>
      <p className={css.note}>
        The source scorer checks location near a stored point. It cannot, by itself, establish
        clinical newness across unregistered visits.
      </p>
    </div>
  );
}

function AbstractReference() {
  const point = abraReference.single_lesion;
  const x = 22 + (point.pixel_x / 512) * 204;
  const y = 14 + (point.pixel_y / 512) * 204;
  return (
    <div className={css.referenceGrid} data-abra-private-reference>
      <svg
        viewBox="0 0 260 245"
        role="img"
        aria-label="Abstract 512 by 512 pixel coordinate grid with source reference point, not a patient image"
      >
        <rect
          x="22"
          y="14"
          width="204"
          height="204"
          fill="#e5eef0"
          stroke="#426475"
          strokeWidth="1.5"
        />
        <path d="M22 116H226M124 14V218" stroke="#9bb1b9" strokeDasharray="3 4" />
        <circle cx={x} cy={y} r="8" fill="none" stroke="#d66d46" strokeWidth="2" />
        <circle cx={x} cy={y} r="3" fill="#d66d46" />
        <text x="22" y="235">
          0
        </text>
        <text x="226" y="235" textAnchor="end">
          512 x
        </text>
        <text x="231" y="20">
          y↓
        </text>
      </svg>
      <div>
        <b>Private source point</b>
        <span>
          Viewer index {point.viewer_slice_index_zero_based} · pixel ({point.pixel_x},{' '}
          {point.pixel_y})
        </span>
        <small>
          Abstract grid only. SOP mapping and display orientation are unverified; no CT overlay is
          authorized by this evidence.
        </small>
      </div>
    </div>
  );
}

function Reference({ reveal }: { reveal: boolean }) {
  if (!reveal)
    return (
      <div className={css.covered} data-abra-reference-hidden>
        <b>Reader-only reference is covered</b>
        <span>
          Reveal source expected outcomes only after inspecting inputs, operations and empty output
          schema.
        </span>
      </div>
    );
  return (
    <div className={css.reference} data-abra-private-reference>
      <div className={css.referenceValues}>
        <article>
          <span>Interval reference</span>
          <b>{abraReference.interval_days} days</b>
          <small>metadata arithmetic</small>
        </article>
        <article>
          <span>Count reference</span>
          <b>+{abraReference.slice_count_followup_minus_baseline} image</b>
          <small>follow-up − baseline</small>
        </article>
      </div>
      <AbstractReference />
      <p className={css.note}>
        The point-distance scorer uses a {abraReference.scorer.single_point_threshold_px}-pixel
        threshold; this is a benchmark comparison, not a measured agent result or independent
        clinical truth.
      </p>
    </div>
  );
}

function Limits() {
  return (
    <div className={css.limits} data-abra-limits>
      <article>
        <b>Recovered</b>
        <span>
          Exact 161 + 162 native CT instances; 16 fixed-window samples per visit in this pack.
        </span>
      </article>
      <article>
        <b>Unverified</b>
        <span>
          Cross-visit registration and OHIF viewer index→SOP mapping; equal numeric z visibly showed
          different chest levels.
        </span>
      </article>
      <article>
        <b>Absent</b>
        <span>
          No retained ABRA agent answer, lesion submission, score or independent radiologic
          adjudication.
        </span>
      </article>
      <p>
        Source metadata can support date and count arithmetic. Patient-image lesion comparison needs
        matched anatomy and verified viewer indexing; a private point alone does not prove newness.
      </p>
    </div>
  );
}

const titles: Record<AbraLongitudinalState['scene'], string> = {
  inputs: 'Two actual CT visits',
  metadata: 'Query dates → interval',
  counts: 'Query series → signed count',
  browse: 'Browse each native stack independently',
  submit: 'Specify a finding, with no saved answer',
  reference: 'Reader-only source reference',
  limits: 'What the retained evidence supports',
};

export function AbraLongitudinalScene({ state }: { state: AbraLongitudinalState }) {
  const reveal = abraRevealed(state);
  return (
    <section
      className={css.scene}
      data-abra-scene={state.scene}
      data-abra-reference-state={reveal ? 'revealed' : 'hidden'}
    >
      <h3>{titles[state.scene]}</h3>
      {state.scene === 'inputs' && <Inputs {...state} />}
      {state.scene === 'metadata' && <Metadata />}
      {state.scene === 'counts' && <Counts />}
      {state.scene === 'browse' && <Browse {...state} />}
      {state.scene === 'submit' && <Submit multi={state.task > 0.5} />}
      {state.scene === 'reference' && <Reference reveal={reveal} />}
      {state.scene === 'limits' && <Limits />}
    </section>
  );
}

export function AbraLongitudinalOutput({ state }: { state: AbraLongitudinalState }) {
  const reveal = abraRevealed(state);
  const line =
    state.scene === 'metadata'
      ? 'Two source StudyDate fields → one integer day interval.'
      : state.scene === 'counts'
        ? 'Two native CT counts → signed follow-up minus baseline.'
        : state.scene === 'browse'
          ? 'Independent source slices and per-visit positions; no registration.'
          : state.scene === 'submit'
            ? 'Finding fields are blank; no retained agent submission.'
            : state.scene === 'reference'
              ? reveal
                ? 'Source expected outcomes shown by reader reveal.'
                : 'Source expected outcomes remain covered.'
              : 'Two real native CT stacks; supplied pairing and viewer tools.';
  return (
    <aside className={`${shared.storyOutput} ${css.output}`} data-abra-output>
      <b>{state.scene === 'inputs' ? 'Input: two CT visits' : 'Task state'}</b>
      <p>{line}</p>
      <b>Answer-owned output</b>
      <p>
        {abraOutput.status === 'not-retained'
          ? 'None retained. Blank fields are an output schema, not an observed result.'
          : 'Unexpected status'}
      </p>
      <b>Evidence boundary</b>
      <p>
        {reveal
          ? 'Reference checks source targets, not clinical truth.'
          : 'Private reference hidden; anatomy and viewer index are unverified.'}
      </p>
      <small>ABRA 6888146 · NLST CC BY 4.0 · local source-derived teaching</small>
    </aside>
  );
}
