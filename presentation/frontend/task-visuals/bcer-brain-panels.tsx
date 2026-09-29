import { brainContract, brainDiagram, type BcerBrainState } from './bcer-brain';
import shared from './task-visual.module.css';
import css from './bcer-brain.module.css';

function AbstractGrid({ tone, name }: { tone: string; name: string }) {
  return (
    <svg viewBox="0 0 120 98" role="img" aria-label={`${name}: symbolic unit grid, no MRI pixels`}>
      <rect
        x="20"
        y="8"
        width="76"
        height="76"
        rx="3"
        fill="#142b39"
        stroke={tone}
        strokeWidth="2"
      />
      {[1, 2, 3, 4, 5].map((n) => (
        <g key={n} stroke={tone} strokeOpacity=".35" strokeWidth=".75">
          <path d={`M${20 + (n * 76) / 6} 8V84`} />
          <path d={`M20 ${8 + (n * 76) / 6}H96`} />
        </g>
      ))}
      <path d="M96 8l11 8v76l-11-8M20 84l11 8h76" fill="none" stroke={tone} strokeOpacity=".55" />
      <text x="60" y="48" textAnchor="middle" fill={tone} fontSize="13" fontWeight="700">
        {name}
      </text>
    </svg>
  );
}

function Inputs({ view }: { view: number }) {
  const active = Math.min(3, Math.floor(view * 4));
  return (
    <div className={css.modalityGrid} data-bcer-brain-symbolic-inputs>
      {brainDiagram.modalities.map((m, i) => (
        <article className={css.modality} data-current={i === active} key={m.name}>
          <AbstractGrid name={m.name} tone={m.tone} />
          <b>{m.name}</b>
          <small>{m.alias}</small>
        </article>
      ))}
      <p className={css.gridNote}>
        Abstract aligned slots in a unit grid. No native voxel dimensions, affine, intensity, or
        patient image is asserted.
      </p>
    </div>
  );
}

function Identify({ view }: { view: number }) {
  const swap = view > 0.54;
  const names = brainDiagram.modalities;
  return (
    <div className={css.flow} data-bcer-brain-identify data-semantic-swap={swap}>
      <div className={css.flowTitle}>
        <b>Case manifest</b>
        <span>identify_sequences → typed paths</span>
      </div>
      <div className={css.pathRows}>
        {names.map((m, i) => {
          const target =
            swap && i === 1
              ? 'flair_path'
              : swap && i === 3
                ? 't1c_path'
                : `${m.name.toLowerCase()}_path`;
          return (
            <div className={css.pathRow} data-fault={swap && (i === 1 || i === 3)} key={m.name}>
              <span className={css.chip} style={{ borderColor: m.tone }}>
                {m.name}
              </span>
              <span className={css.arrow}>→</span>
              <code>{target}</code>
              <span className={css.rowStatus}>
                {swap && (i === 1 || i === 3) ? 'WRONG MODALITY' : 'typed mapping'}
              </span>
            </div>
          );
        })}
      </div>
      <p className={css.smallNote}>
        A valid path is insufficient when T1c and FLAIR identities are swapped. This is a
        source-defined fault, not an observed run.
      </p>
    </div>
  );
}

function Segment({ view }: { view: number }) {
  return (
    <div className={css.segment} data-bcer-brain-segment>
      <div className={css.segmentInputs}>
        {['T1c', 'T1', 'T2', 'FLAIR'].map((m) => (
          <span key={m}>{m}</span>
        ))}
      </div>
      <div className={css.downArrow}>↓ four typed paths</div>
      <div className={css.tool}>
        brats_mri_segmentation<span>specialist tool · not run here</span>
      </div>
      <div className={css.branches}>
        <article data-current={view <= 0.5}>
          <b>Normal code path</b>
          <span>MONAI BraTS bundle</span>
        </article>
        <article data-current={view > 0.5}>
          <b>Dependency failure path</b>
          <span>T1c + FLAIR heuristic fallback</span>
        </article>
      </div>
      <p className={css.smallNote}>
        Source behavior only. No bundle inference, fallback segmentation, or model-performance
        observation was generated.
      </p>
    </div>
  );
}

function Labels() {
  return (
    <div className={css.labels} data-bcer-brain-label-semantics>
      <div className={css.labelTiles}>
        {brainDiagram.label_key.map((item) => (
          <article key={item.value} style={{ borderTopColor: item.color }}>
            <strong style={{ color: item.color }}>{item.value}</strong>
            <span>
              {
                (
                  {
                    0: 'background',
                    1: 'necrotic core',
                    2: 'edema / invaded tissue',
                    4: 'enhancing tumor',
                  } as Record<number, string>
                )[item.value]
              }
            </span>
          </article>
        ))}
      </div>
      <div className={css.equation}>
        <b>WT = (label 1) ∪ (label 2) ∪ (label 4)</b>
        <small>Source-defined binary whole-tumor mask</small>
      </div>
      <div className={css.sockets}>
        <span>
          <code>seg_path</code> — expected label-map file
        </span>
        <span>
          <code>wt_mask_path</code> — expected binary-mask file
        </span>
      </div>
      <p className={css.smallNote}>
        Color tiles are a key, not a spatial mask. Both case-specific output files are missing.
      </p>
    </div>
  );
}

function Checks() {
  const c = brainContract.contract;
  return (
    <div className={css.checks} data-bcer-brain-checks>
      <article>
        <b>2 stages</b>
        {c.required_stage_success.map((x) => (
          <span key={x}>{x}</span>
        ))}
      </article>
      <article>
        <b>2 paths</b>
        {c.required_artifacts.map((x) => (
          <span key={x}>{x}</span>
        ))}
      </article>
      <article>
        <b>3 invariants</b>
        {c.invariants.map((x) => (
          <span key={x}>{x}</span>
        ))}
      </article>
      <p className={css.smallNote}>
        A NIfTI read failure can fall back to positive file size. These checks do not test
        anatomical accuracy.
      </p>
    </div>
  );
}

function Limits() {
  return (
    <div className={css.limits} data-bcer-brain-limits>
      <article>
        <b>Available</b>
        <span>Pinned BCER contract, evaluator and tool source</span>
      </article>
      <article>
        <b>Missing case data</b>
        <span>Four matching BraTS MRI volumes</span>
      </article>
      <article>
        <b>Missing answer</b>
        <span>No BCER segmentation or WT mask</span>
      </article>
      <article>
        <b>Missing reference</b>
        <span>No case-matched annotation or accuracy comparison</span>
      </article>
      <p>
        Future BraTS annotations are reader-only reference material. They are not solver inputs, and
        none is embedded in this pack.
      </p>
    </div>
  );
}

const titles: Record<BcerBrainState['scene'], string> = {
  inputs: 'Four required contrasts',
  identify: 'Identify each sequence',
  segment: 'Call the specialist tool',
  labels: 'Interpret the expected files',
  checks: 'Inspect structural checks',
  limits: 'Evidence boundary',
};

export function BcerBrainScene({ state }: { state: BcerBrainState }) {
  return (
    <section className={css.scene} data-bcer-brain-scene={state.scene}>
      <h3>{titles[state.scene]}</h3>
      {state.scene === 'inputs' && <Inputs view={state.view} />}
      {state.scene === 'identify' && <Identify view={state.view} />}
      {state.scene === 'segment' && <Segment view={state.view} />}
      {state.scene === 'labels' && <Labels />}
      {state.scene === 'checks' && <Checks />}
      {state.scene === 'limits' && <Limits />}
    </section>
  );
}

export function BcerBrainOutput({ state }: { state: BcerBrainState }) {
  const late = ['labels', 'checks', 'limits'].includes(state.scene);
  return (
    <aside className={`${shared.storyOutput} ${css.output}`} data-bcer-brain-output>
      <b>Source status</b>
      <p>Symbolic contract · no patient case</p>
      <b>{late ? 'Expected artifacts' : 'Input and helper'}</b>
      <p>
        {late
          ? 'seg_path: label map; wt_mask_path: binary whole tumor. Neither file is retained.'
          : 'Four MRI modalities required; manifest, runtime and tools are supplied workflow help.'}
      </p>
      <b>Boundary</b>
      <p>
        {state.scene === 'checks'
          ? 'Stage, path and nonzero checks cannot establish anatomical accuracy.'
          : 'No observed segmentation, reference annotation, or performance score.'}
      </p>
      <small>BCER d108167 · source-derived symbolic teaching</small>
    </aside>
  );
}
