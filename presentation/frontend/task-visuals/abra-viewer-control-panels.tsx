import { useId, useState } from 'react';
import { abraViewerPack as pack, type AbraViewerState } from './abra-viewer-control';
import shared from './task-visual.module.css';
import css from './abra-viewer-control.module.css';

const titles = {
  input: 'Inspect fixed source CT',
  route: 'Derive the requested state',
  operation: 'Stage a symbolic slice request',
  output: 'Separate requested and observed state',
  limits: 'Inspect the scoring boundary',
} as const;
function SourcePreview() {
  const p = pack.source.preview;
  return (
    <figure className={css.preview} data-abra-source-preview>
      <img src={p.data_uri} alt="Fixed windowed CT source member; OHIF index unverified" />
      <figcaption>
        {p.archive_member} · DICOM instance {p.dicom_instance_number} · OHIF index unverified.{' '}
        Window {p.window_center_hu}/{p.window_width_hu} HU; spacing {p.pixel_spacing_mm[0]} mm.{' '}
        <a href={pack.source.notice.url}>LIDC-IDRI / TCIA</a> ·{' '}
        <a href="https://creativecommons.org/licenses/by/3.0/">CC BY 3.0</a>.
      </figcaption>
    </figure>
  );
}
function StateSockets() {
  return (
    <div className={css.sockets} data-abra-state-sockets>
      <div className={css.requested}>
        <span>Prompt-visible request</span>
        <strong>sliceIndex {pack.operation.target_slice_index}</strong>
      </div>
      <div className={css.absent} data-abra-observed-state="absent">
        <span>Observed OHIF final state</span>
        <strong>Absent</strong>
        <small>No action trace or score</small>
      </div>
    </div>
  );
}
function Input() {
  return (
    <div className={css.columns} data-abra-input>
      <SourcePreview />
      <div className={css.card}>
        <b>Matched native source</b>
        <p>
          {pack.source.title}: {pack.source.instance_count} DICOM instances share the manifest
          Study/Series UIDs.
        </p>
        <p>
          This is a fixed source image. No loaded OHIF viewport or viewer ordering was retained.
        </p>
        <StateSockets />
      </div>
    </div>
  );
}
function Route({ state }: { state: AbraViewerState }) {
  const active = Math.min(2, Math.floor(Math.max(0, Math.min(1, state.progress)) * 3));
  const steps = [
    ['Manifest count', String(pack.source.instance_count), 'Public CT metadata'],
    ['Generator rule', '140 // 2 = 70', 'Static integer division'],
    ['Prompt request', 'Navigate to slice 70', 'Zero-based tool index'],
  ];
  return (
    <div data-abra-route>
      <div className={css.steps}>
        {steps.map(([label, value, note], i) => (
          <div key={label} className={i === active ? css.active : ''}>
            <span>{label}</span>
            <strong>{value}</strong>
            <small>{note}</small>
          </div>
        ))}
      </div>
      <div className={css.card}>
        <b>Requested state is already given</b>
        <p>
          The YAML expected_outcome repeats 70 for grading. It is a state target, not hidden
          clinical truth. Initial requested state is index 0.
        </p>
      </div>
      <p className={css.caution}>
        DICOM instance number, archive order and OHIF sliceIndex are different coordinates.
      </p>
    </div>
  );
}
function MockControl({ state }: { state: AbraViewerState }) {
  const id = useId();
  const [override, setOverride] = useState<number | null>(null);
  const candidate =
    override ??
    Math.round(Math.max(0, Math.min(1, state.progress)) * pack.operation.target_slice_index);
  return (
    <div className={css.columns} data-abra-mock-control>
      <SourcePreview />
      <div className={css.card}>
        <b>Local teaching control</b>
        <label htmlFor={id}>
          Symbolic candidate index: <output data-abra-mock-index>{candidate}</output>
        </label>
        <input
          id={id}
          type="range"
          min={pack.operation.candidate_min}
          max={pack.operation.candidate_max}
          value={candidate}
          onChange={(event) => setOverride(Number(event.target.value))}
        />
        <div className={css.buttons}>
          <button type="button" onClick={() => setOverride(pack.operation.target_slice_index)}>
            Stage 70 locally
          </button>
          <button type="button" onClick={() => setOverride(null)}>
            Follow story
          </button>
        </div>
        <code className={css.request}>set_viewport_slice(slice_index={candidate})</code>
        <p>
          No tool call occurs. This control never changes the fixed CT image or records OHIF state.
        </p>
        <p data-abra-observed-state="absent">
          Observed OHIF state absent · no action trace or score.
        </p>
      </div>
    </div>
  );
}
function Output() {
  return (
    <div data-abra-output-schema>
      <StateSockets />
      <div className={css.card}>
        <b>Required API field: sliceIndex</b>
        <p>
          The final OHIF API state would need to contain the requested value 70. No such final
          state, viewport screenshot or executed trajectory exists in this pack. A mock index of 70
          does not establish task success.
        </p>
      </div>
    </div>
  );
}
function Limits() {
  return (
    <div className={css.columns} data-abra-limits>
      <div className={css.card}>
        <b>State-difference rule</b>
        <dl className={css.rules}>
          <dt>YAML → API</dt>
          <dd>slice_index → sliceIndex</dd>
          <dt>Numeric default</dt>
          <dd>Absolute difference ≤ 0.01</dd>
          <dt>Window variants</dt>
          <dd>Tolerance 1.0; distinct target fields</dd>
          <dt>Strings</dt>
          <dd>Exact string equality</dd>
          <dt>Partial credit</dt>
          <dd>Passed fields / specified fields</dd>
        </dl>
        <p>A missing final-state field fails its check. No scorer ran here.</p>
      </div>
      <div className={css.card}>
        <b>Unresolved boundaries</b>
        <p>
          The scorer does not validate anatomy or DICOM-to-viewer ordering. Loaded viewport,
          performed action and runtime filesystem isolation are unaudited.
        </p>
        <p>
          Archive member 00000001 has instance number 80. Neither value supplies a verified OHIF
          sliceIndex.
        </p>
        <strong>No private reference · no prediction · no score</strong>
      </div>
    </div>
  );
}
export function AbraViewerScene({ state }: { state: AbraViewerState }) {
  return (
    <section className={css.scene} data-abra-viewer-scene={state.scene} data-abra-basis="mixed">
      <h3>{titles[state.scene]}</h3>
      {state.scene === 'input' && <Input />}
      {state.scene === 'route' && <Route state={state} />}
      {state.scene === 'operation' && <MockControl state={state} />}
      {state.scene === 'output' && <Output />}
      {state.scene === 'limits' && <Limits />}
    </section>
  );
}
export function AbraViewerOutput({ state }: { state: AbraViewerState }) {
  return (
    <aside className={`${shared.storyOutput} ${css.aside}`} data-abra-aside>
      <b>{state.scene === 'input' ? 'Source input boundary' : 'State output boundary'}</b>
      <p>
        {state.scene === 'input'
          ? 'Fixed native CT; no verified OHIF index.'
          : 'Requested sliceIndex 70; observed state absent.'}
      </p>
      <small>Mixed illustration · no viewer action or score</small>
    </aside>
  );
}
