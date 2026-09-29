import {
  topcowLocalImage,
  topcowLocalRecord,
  topcowLocalRevealed,
  topcowLocalSample,
  type RexTopcowLocalState,
  type TopcowBoxReference,
  type TopcowEdgeReference,
  type TopcowLocalRecord,
} from './rex-topcow-localization';
import shared from './task-visual.module.css';
import css from './rex-topcow-localization.module.css';

const fmt = (n: number) => n.toFixed(1);
const spacing = (n: number) => Number(n.toFixed(6)).toString();
type Candidate = {
  name: string;
  group: 'anterior' | 'posterior';
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  lx: number;
  ly: number;
};
const CANDIDATES: Candidate[] = [
  { name: 'L-A1', group: 'anterior', x1: 24, y1: 70, x2: 96, y2: 70, lx: 42, ly: 61 },
  { name: 'Acom', group: 'anterior', x1: 101, y1: 70, x2: 199, y2: 70, lx: 131, ly: 61 },
  { name: '3rd-A2', group: 'anterior', x1: 150, y1: 67, x2: 150, y2: 20, lx: 158, ly: 42 },
  { name: 'R-A1', group: 'anterior', x1: 204, y1: 70, x2: 276, y2: 70, lx: 221, ly: 61 },
  { name: 'L-Pcom', group: 'posterior', x1: 74, y1: 186, x2: 105, y2: 127, lx: 10, ly: 148 },
  { name: 'L-P1', group: 'posterior', x1: 22, y1: 186, x2: 74, y2: 186, lx: 25, ly: 177 },
  { name: 'R-P1', group: 'posterior', x1: 226, y1: 186, x2: 278, y2: 186, lx: 231, ly: 177 },
  { name: 'R-Pcom', group: 'posterior', x1: 195, y1: 127, x2: 226, y2: 186, lx: 230, ly: 148 },
];

function Scan({
  record,
  slice,
  roi = false,
}: {
  record: TopcowLocalRecord;
  slice: number;
  roi?: boolean;
}) {
  const sample = topcowLocalSample(record.source, slice);
  const sampleIndex = record.source.samples.indexOf(sample);
  const ref = record.kind === 'box' ? (record.reference as TopcowBoxReference) : null;
  return (
    <figure className={css.scan} data-topcow-input={record.source.entry_id}>
      <div className={css.scanHead}>
        <b>
          {record.source.modality} · case {record.source.case_id}
        </b>
        <span>native {record.source.geometry.shape_ijk.join('×')}</span>
      </div>
      <div className={css.scanFrame}>
        <img
          src={topcowLocalImage(record.pack, sample.file)}
          alt={`Actual ${record.source.modality} source image, native k=${sample.native_k_zero_based}; no prediction`}
        />
        {roi && ref && (
          <img
            className={css.overlay}
            data-topcow-reference-roi
            src={topcowLocalImage(record.pack, ref.samples[sampleIndex].file)}
            alt={`Reader-only scorer-interpreted source ROI projection at native k=${sample.native_k_zero_based}`}
          />
        )}
      </div>
      <figcaption>
        <b>
          native k={sample.native_k_zero_based} · RAS center z={fmt(sample.center_ras_mm[2])} mm
        </b>
        <span>{record.source.geometry.spacing_ijk_mm.map(spacing).join(' × ')} mm / voxel</span>
      </figcaption>
    </figure>
  );
}
function Rail({ record, slice }: { record: TopcowLocalRecord; slice: number }) {
  const selected = record.source.samples.indexOf(topcowLocalSample(record.source, slice));
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
function Inputs({ record, state }: { record: TopcowLocalRecord; state: RexTopcowLocalState }) {
  return (
    <div className={css.twoCol} data-topcow-input-facts>
      <div>
        <Scan record={record} slice={state.slice} />
        <Rail record={record} slice={state.slice} />
      </div>
      <div className={css.facts}>
        <b>Input: one exact native {record.source.modality} volume</b>
        <span>
          Case 012 is in the pinned ReX test partition by static split reconstruction. The displayed
          scan is a source image, not a prediction.
        </span>
        <b>What this task asks</b>
        <span>
          {record.kind === 'box'
            ? 'Localize a 3D Circle of Willis ROI in voxel coordinates.'
            : 'Classify eight named Circle of Willis connections as present or absent.'}
        </span>
        <small>
          No target ROI, edge bits, segmentation, output JSON or performance value is mounted in
          this opening scene.
        </small>
      </div>
    </div>
  );
}
function Geometry({ record, state }: { record: TopcowLocalRecord; state: RexTopcowLocalState }) {
  const s = topcowLocalSample(record.source, state.slice);
  return (
    <div className={css.twoCol} data-topcow-geometry>
      <div>
        <Scan record={record} slice={state.slice} />
        <Rail record={record} slice={state.slice} />
      </div>
      <div className={css.facts}>
        <b>Native voxel index → RAS millimeters</b>
        <div className={css.equation}>
          [i, j, {s.native_k_zero_based}, 1] → world z {fmt(s.center_ras_mm[2])} mm at volume center
        </div>
        <span>
          The NIfTI sform sets the physical map. Image PNGs use x=i and reversed j, sampled by
          nearest neighbor with the longest axis capped at 384 pixels.
        </span>
        <b>
          {record.kind === 'box' ? 'Box output is in voxel indices' : 'Graph output is categorical'}
        </b>
        <span>
          {record.kind === 'box'
            ? 'The requested size and location are three native voxel values each, not millimeters or display pixels.'
            : 'Named 0/1 edge decisions are separate from image voxel labels or a traced vessel segmentation.'}
        </span>
      </div>
    </div>
  );
}
function BoxToy({ step }: { step: number }) {
  const active = step < 0.5 ? 'scorer' : 'prose';
  return (
    <div className={css.toy} data-topcow-box-counterexample>
      <svg
        viewBox="0 0 490 230"
        role="img"
        aria-label="Abstract voxel grid comparing minimum-corner versus center meanings for one location and size; no patient geometry"
      >
        {[0, 1].map((side) => {
          const x = 22 + side * 247;
          const boxX = side === 0 ? x + 86 : x + 42;
          const boxY = side === 0 ? 92 : 115.5;
          const selected = (side === 0 ? 'scorer' : 'prose') === active;
          return (
            <g key={side}>
              <rect x={x} y="28" width="207" height="166" fill="#f1f7f8" stroke="#95b9c2" />
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <g key={i} stroke="#d5e5e8" strokeWidth="1">
                  <path d={`M${x + i * 29.5} 28v166`} />
                  <path d={`M${x} ${28 + i * 23.7}h207`} />
                </g>
              ))}
              <rect
                x={boxX}
                y={boxY}
                width="88"
                height="47"
                fill={selected ? '#4dc9d388' : '#95b1bc55'}
                stroke={selected ? '#087c91' : '#678998'}
                strokeWidth="2.5"
              />
              <circle cx={x + 86} cy="139" r="5" fill="#e48944" stroke="#9d4d23" strokeWidth="2" />
              <text
                x={x}
                y="20"
                fill={selected ? '#145e6b' : '#68818a'}
                fontSize="12"
                fontWeight="700"
              >
                {side === 0 ? 'Pinned scorer: location=min' : 'Description prose: location=center'}
              </text>
              <text x={x + 4} y="215" fill="#576d75" fontSize="10">
                same location point · same size values
              </text>
            </g>
          );
        })}
      </svg>
      <span>
        The orange point and blue box are an abstract contract example. Source-case values are
        hidden until reader reveal. The scorer uses the left interpretation.
      </span>
    </div>
  );
}
function EdgeGraph({ step, bits }: { step: number; bits?: TopcowEdgeReference }) {
  const selected = Math.max(0, Math.min(7, Math.round(step * 7)));
  return (
    <div className={css.graph} data-topcow-edge-graph={bits ? 'reference' : 'candidate'}>
      <svg
        viewBox="0 0 300 225"
        role="img"
        aria-label={
          bits
            ? 'Reader-only source graph edge bits on an abstract topology diagram'
            : 'Eight named candidate edges on an abstract topology diagram; patient bits hidden'
        }
      >
        <text x="12" y="14" className={css.svgHeading}>
          Anterior candidates
        </text>
        <text x="12" y="114" className={css.svgHeading}>
          Posterior candidates
        </text>
        {CANDIDATES.map((edge, i) => {
          const bit = bits ? bits[edge.group][edge.name] : undefined;
          const color = bits
            ? bit === 1
              ? '#2aa77f'
              : '#879eaa'
            : i === selected
              ? '#24aec0'
              : '#9db5bf';
          const dash = bits ? (bit === 1 ? undefined : '5 4') : '5 4';
          return (
            <g key={edge.name} data-topcow-edge={edge.name}>
              <line
                x1={edge.x1}
                y1={edge.y1}
                x2={edge.x2}
                y2={edge.y2}
                stroke={color}
                strokeWidth={i === selected || bit === 1 ? 4 : 2.5}
                strokeDasharray={dash}
              />
              <text
                x={edge.lx}
                y={edge.ly}
                fill={bits ? '#2b5865' : i === selected ? '#137184' : '#5e7780'}
                fontSize="10"
                fontWeight="700"
              >
                {edge.name}
                {bits ? ` ${bit}` : ''}
              </text>
            </g>
          );
        })}
        {[
          { x: 24, y: 70 },
          { x: 101, y: 70 },
          { x: 199, y: 70 },
          { x: 276, y: 70 },
          { x: 150, y: 20 },
          { x: 74, y: 186 },
          { x: 105, y: 127 },
          { x: 195, y: 127 },
          { x: 226, y: 186 },
        ].map((n, i) => (
          <circle key={i} cx={n.x} cy={n.y} r="4" fill="#3e7180" />
        ))}
      </svg>
      <div className={css.legend}>
        {!bits && (
          <>
            <span>
              <i className={css.candidate} />
              candidate, status unknown
            </span>
            <span>
              <i className={css.focused} />
              focused question
            </span>
          </>
        )}
        {bits && (
          <>
            <span>
              <i className={css.present} />
              source bit 1
            </span>
            <span>
              <i className={css.absent} />
              source bit 0
            </span>
          </>
        )}
      </div>
    </div>
  );
}
function Operation({ record, state }: { record: TopcowLocalRecord; state: RexTopcowLocalState }) {
  return (
    <div className={css.operation} data-topcow-operation>
      {record.kind === 'box' ? (
        <>
          <BoxToy step={state.step} />
          <div className={css.opText}>
            <b>One `location`, two incompatible meanings</b>
            <span>
              The task description calls location a center. The pinned scorer instead computes
              min=location and max=location+size−1. Both are voxel-index rules; neither is silently
              treated as physical truth here.
            </span>
            <small>
              Move the operation focus between the two symbolic boxes. Source ROI numbers remain
              hidden.
            </small>
          </div>
        </>
      ) : (
        <>
          <EdgeGraph step={state.step} />
          <div className={css.opText}>
            <b>Eight named connection decisions</b>
            <span>
              Four anterior and four posterior candidate edges form two 4-bit variant strings. A
              highlighted dashed edge is the current question, not an observed connection.
            </span>
            <small>
              This graph is an abstract topology key. It is not traced from the patient image or a
              segmentation output.
            </small>
          </div>
        </>
      )}
    </div>
  );
}
function Output({ record }: { record: TopcowLocalRecord }) {
  return (
    <div className={css.schema} data-topcow-output-schema>
      <b>Answer-owned files · empty</b>
      <div>
        <span>submission.csv</span>
        <code>{record.output.columns.join(',')}</code>
      </div>
      <div>
        <span>relative JSON path</span>
        <code>{record.output.relative_prediction_pattern}</code>
      </div>
      <div>
        <span>required JSON</span>
        <code>
          {record.kind === 'box'
            ? '{"size":[?, ?, ?],"location":[?, ?, ?]}'
            : '{"anterior":{"L-A1":?,"Acom":?,"3rd-A2":?,"R-A1":?},"posterior":{"L-Pcom":?,"L-P1":?,"R-P1":?,"R-Pcom":?}}'}
        </code>
      </div>
      <p>
        Question marks mark unfilled participant values. The schema is not a prediction file and no
        score was retained.
      </p>
    </div>
  );
}
function Reference({ record, state }: { record: TopcowLocalRecord; state: RexTopcowLocalState }) {
  if (!topcowLocalRevealed(state))
    return (
      <div className={css.covered} data-topcow-reference-hidden>
        <b>Private source annotation covered</b>
        <span>Reader reveal is required before source ROI coordinates or edge bits mount.</span>
      </div>
    );
  if (record.kind === 'box') {
    const ref = record.reference as TopcowBoxReference;
    const sample = topcowLocalSample(record.source, state.slice);
    const selected = record.source.samples.indexOf(sample);
    return (
      <div className={css.twoCol} data-topcow-reference-panel>
        <div>
          <Scan record={record} slice={state.slice} roi />
          <Rail record={record} slice={state.slice} />
        </div>
        <div className={css.facts}>
          <b>
            <i className={css.roiSwatch} />
            Source ROI · scorer interpretation
          </b>
          <span>
            Size {ref.size_voxels.join(' × ')} voxels; location {ref.location_voxels.join(', ')}{' '}
            voxels.
          </span>
          <span>
            Scorer minimum corner {ref.scorer_interpreted_min_corner_voxels.join(', ')}; inclusive
            maximum {ref.scorer_interpreted_max_corner_inclusive_voxels.join(', ')}.
          </span>
          <b>Selected native k={sample.native_k_zero_based}</b>
          <span>
            {ref.samples[selected].intersects_scorer_box
              ? 'Yellow projection intersects this slice.'
              : 'This slice is outside the scorer-interpreted source box z range.'}
          </span>
          <small>
            Source TXT says “Location (Voxels)”; description calls it center. The yellow box follows
            the scorer formula only. It is not a participant prediction.
          </small>
        </div>
      </div>
    );
  }
  const ref = record.reference as TopcowEdgeReference;
  return (
    <div className={css.twoCol} data-topcow-reference-panel>
      <div>
        <Scan record={record} slice={state.slice} />
        <Rail record={record} slice={state.slice} />
      </div>
      <div className={css.referenceGraph}>
        <b>Reader-only source YML edge bits</b>
        <EdgeGraph step={state.step} bits={ref} />
        <small>
          Bits describe the archived case annotation. The diagram is not traced from the source
          image and supplies no participant answer or score.
        </small>
      </div>
    </div>
  );
}
function Limits({ record }: { record: TopcowLocalRecord }) {
  return (
    <div className={css.limits} data-topcow-limits>
      <article>
        <b>Actual source</b>
        <span>
          One exact TopCoW2024 CTA or MRA case, statically in the pinned test split. Full native
          input and target hashes are retained. No ReX staging was materialized.
        </span>
      </article>
      <article>
        <b>Scorer contract</b>
        <span>{record.scorer}</span>
      </article>
      <article>
        <b>Claim boundary</b>
        <span>
          {record.kind === 'box'
            ? 'The metric named IoU is computed after 50% dilation, not ordinary undilated 3D IoU.'
            : 'A single case gives two source 4-bit variants, not a balanced-accuracy result. Named edge bits are not voxel segmentations.'}
        </span>
      </article>
      <div className={css.limitFooter}>
        No model, participant JSON, grader execution, score, or clinical interpretation is shown.
      </div>
    </div>
  );
}
const titles: Record<RexTopcowLocalState['scene'], string> = {
  inputs: 'Read the exact source image',
  geometry: 'Locate native voxels in physical space',
  operation: 'Understand the answer operation',
  output: 'Specify the empty JSON answer',
  reference: 'Reveal source annotation for reading',
  limits: 'Bound the scorer and this source case',
};
export function RexTopcowLocalScene({ state }: { state: RexTopcowLocalState }) {
  const record = topcowLocalRecord(state.recipe);
  const revealed = topcowLocalRevealed(state);
  return (
    <section
      className={css.scene}
      data-topcow-scene={state.scene}
      data-topcow-recipe={state.recipe}
      data-topcow-reference-state={revealed ? 'revealed' : 'hidden'}
    >
      <h3>{titles[state.scene]}</h3>
      {state.scene === 'inputs' && <Inputs record={record} state={state} />}
      {state.scene === 'geometry' && <Geometry record={record} state={state} />}
      {state.scene === 'operation' && <Operation record={record} state={state} />}
      {state.scene === 'output' && <Output record={record} />}
      {state.scene === 'reference' && <Reference record={record} state={state} />}
      {state.scene === 'limits' && <Limits record={record} />}
    </section>
  );
}
export function RexTopcowLocalOutput({ state }: { state: RexTopcowLocalState }) {
  const record = topcowLocalRecord(state.recipe);
  const status =
    state.scene === 'inputs'
      ? `Input: native ${record.source.modality} image only.`
      : state.scene === 'geometry'
        ? 'Native image grid maps to RAS millimeters.'
        : state.scene === 'operation'
          ? record.kind === 'box'
            ? 'Symbolic voxel-box interpretation; no source ROI yet.'
            : 'Symbolic candidate graph; no source edge bits yet.'
          : state.scene === 'output'
            ? 'Required CSV and JSON remain unfilled.'
            : state.scene === 'reference'
              ? topcowLocalRevealed(state)
                ? 'Reader-only source annotation revealed.'
                : 'Source annotation remains covered.'
              : 'Pinned scorer rules and one-case limits.';
  return (
    <aside className={`${shared.storyOutput} ${css.output}`} data-topcow-output>
      <b>
        {state.scene === 'inputs' ? `Input: native ${record.source.modality} volume` : record.title}
      </b>
      <p>{status}</p>
      {state.scene !== 'inputs' && (
        <>
          <b>Participant output</b>
          <p>No JSON prediction or score was retained.</p>
        </>
      )}
      <small>TopCoW2024 · noncommercial with attribution · one case</small>
    </aside>
  );
}
