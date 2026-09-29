import type { ReactNode } from 'react';
import styles from './automed-kidney.module.css';
import shared from './task-visual.module.css';
import {
  kidneySource as src,
  kidneyOutput as out,
  kidneyReference as ref,
  kidneyIndex,
  kidneyRevealed,
  type AutomedKidneyState,
} from './automed-kidney';

function Native({ slice = 1, reveal = false }: { slice?: number; reveal?: boolean }) {
  const v = src.views[slice];
  const label = reveal ? ref.views[slice] : null;
  return (
    <figure className={styles.native} data-kidney-ct data-kidney-slice={v.index}>
      <div className={styles.scan}>
        <svg
          viewBox="0 0 512 512"
          role="img"
          aria-label={`KiTS19 native axial CT slice ${v.index}; columns increase left, rows increase posterior${reveal ? '; source annotation revealed' : ''}`}
        >
          <image href={v.ct_png} width="512" height="512" />
          {label && (
            <image
              data-kidney-private-reference
              href={label.overlay_png}
              width="512"
              height="512"
            />
          )}
          <g className={styles.axes}>
            <text x="8" y="260">
              R
            </text>
            <text x="486" y="260">
              L
            </text>
            <text x="252" y="20">
              A
            </text>
            <text x="252" y="503">
              P
            </text>
          </g>
        </svg>
      </div>
      <figcaption>
        case_00000 · native axial index {v.index} · WL 40 / WW 400 HU
        <br />
        512 × 512 pixels · 0.919921875 mm/pixel · no resampling
      </figcaption>
    </figure>
  );
}

function MiniGrid({ shifted = false }: { shifted?: boolean }) {
  if (shifted)
    return (
      <svg
        className={styles.grid}
        viewBox="0 0 206 112"
        role="img"
        aria-label="Independent toy geometry counterexample: equal mask arrays at different physical origins; schematic grid"
      >
        {[0, 1].map((n) => (
          <g key={n} transform={`translate(${n * 105},0)`}>
            <rect
              x="13"
              y="2"
              width="70"
              height="62"
              fill="#fff"
              stroke={n ? '#eaa83d' : '#8fa4b1'}
              strokeWidth="2"
            />
            <path d="M30 2v62M48 2v62M65 2v62M13 18h70M13 34h70M13 50h70" stroke="#c6d6df" />
            <rect x="31" y="19" width="16" height="14" fill="#1fbbc5" />
            <text x="48" y="82" textAnchor="middle">
              {n ? 'same array' : 'reference'}
            </text>
            <text x="48" y="100" textAnchor="middle">
              {n ? 'origin +100 mm' : 'origin 0 mm'}
            </text>
          </g>
        ))}
      </svg>
    );
  return (
    <svg
      className={styles.grid}
      viewBox="0 0 206 112"
      role="img"
      aria-label={
        shifted
          ? 'Toy array with identical values but origin shifted 100 millimeters'
          : 'Native CT and two empty output grids share dimensions and affine'
      }
    >
      {[0, 1, 2].map((n) => (
        <g key={n} transform={`translate(${n * 69},0)`}>
          <rect
            x="2"
            y="2"
            width="62"
            height="62"
            rx="4"
            fill={n === 0 ? '#314d60' : '#fff'}
            stroke={shifted && n === 2 ? '#eaa83d' : '#8fa4b1'}
            strokeWidth="2"
          />
          <path
            d="M17 2v62M32 2v62M47 2v62M2 17h62M2 32h62M2 47h62"
            stroke={n === 0 ? '#627e90' : '#d4e0e5'}
          />
          <text x="32" y="83" textAnchor="middle">
            {['CT', 'organ', 'lesion'][n]}
          </text>
          <text x="32" y="99" textAnchor="middle">
            {shifted && n === 2 ? '+100 mm' : n === 0 ? 'input' : 'empty'}
          </text>
        </g>
      ))}
    </svg>
  );
}

export function AutomedKidneyScene({ state: s }: { state: AutomedKidneyState }) {
  const slice = kidneyIndex(s.view, src.views.length);
  const tier = kidneyIndex(s.helper, out.tiers.length);
  const step = kidneyIndex(s.step, out.steps.length);
  const fixture = kidneyIndex(s.fixture, out.fixtures.length);
  const revealed = kidneyRevealed(s);
  let title = '';
  let body: ReactNode;
  switch (s.scene) {
    case 'inputs':
      title = 'Read the native CT before any labels';
      body = (
        <div className={styles.columns}>
          <Native slice={slice} />
          <article>
            <p className={styles.kicker}>ACTUAL KiTS19 SOURCE · CT INPUT ONLY</p>
            <h4>611 × 512 × 512 voxels</h4>
            <p>Native axes I / P / L; spacing 0.5 × 0.919921875 × 0.919921875 mm.</p>
            <p>
              Scroll across three sampled axial planes. The actual task receives a volume, not these
              post hoc teaching slices.
            </p>
            <p className={styles.note}>
              No model prediction is retained. No source annotation enters this input view.
            </p>
          </article>
        </div>
      );
      break;
    case 'assistance':
      title = 'The two tiers supply different help';
      body = (
        <div className={styles.columns}>
          <Native />
          <article>
            <p className={styles.kicker}>SUPPLIED HELP · NOT A SOURCE LABEL</p>
            <div className={styles.tiers}>
              {out.tiers.map((item, i) => (
                <div key={item.name} data-kidney-tier={item.name} data-current={i === tier}>
                  <b>{item.name}</b>
                  <span>{item.help}</span>
                </div>
              ))}
            </div>
            <p className={styles.note}>
              Both tiers include a one-case S3 validation step. Neither supplies this patient's
              answer mask.
            </p>
          </article>
        </div>
      );
      break;
    case 'workflow':
      title = 'A required pipeline, not a saved agent trace';
      body = (
        <>
          <div className={styles.steps}>
            {out.steps.map((item, i) => (
              <div key={item.id} data-kidney-step={item.id} data-current={i === step}>
                <strong>{item.id}</strong>
                <span>{item.name}</span>
              </div>
            ))}
          </div>
          <div className={styles.detail}>
            <b>{out.steps[step].name}</b>
            <p>{out.steps[step].action}</p>
          </div>
          <p>
            Configured budget: 3,600 seconds. S1–S3 judge scores remain unavailable; no task run is
            replayed.
          </p>
        </>
      );
      break;
    case 'schema':
      title = 'Two binary masks must occupy the CT grid';
      body = (
        <div className={styles.columns}>
          <Native />
          <article data-kidney-empty-output>
            <p className={styles.kicker}>REQUIRED OUTPUT · NO SAVED PREDICTION</p>
            <h4>{out.patient_path}</h4>
            <div className={styles.fileList}>
              {out.empty_artifacts.map((item) => (
                <div key={item.name}>
                  <b>{item.name}</b>
                  <span>empty required target</span>
                </div>
              ))}
            </div>
            <MiniGrid />
            <p>
              Each mask is binary 0/1, 611 × 512 × 512, with the input affine. The organ target
              includes lesion tissue.
            </p>
          </article>
        </div>
      );
      break;
    case 'reference':
      title = 'Reveal the source annotation only to the reader';
      body = (
        <div className={styles.columns}>
          <Native slice={slice} reveal={revealed} />
          <article>
            <p className={styles.kicker}>PRIVATE SOURCE REFERENCE · NOT A PREDICTION</p>
            {!revealed ? (
              <p className={styles.note} data-kidney-reference-closed>
                Source labels remain hidden until the explicit reveal channel opens.
              </p>
            ) : (
              <div data-kidney-reference-revealed>
                <p>Oracle format illustration from the released source annotation:</p>
                <div className={styles.mapping}>
                  {ref.mapping.map((m) => (
                    <div key={m.target}>
                      <i style={{ background: m.color }} />
                      <b>{m.rule}</b>
                      <span>→ {m.target}</span>
                    </div>
                  ))}
                </div>
                <p>
                  On axial index {ref.views[slice].index}:{' '}
                  {ref.views[slice].organ_voxels.toLocaleString()} organ voxels (including lesion);{' '}
                  {ref.views[slice].lesion_voxels.toLocaleString()} lesion voxels.
                </p>
                <p className={styles.note}>
                  The root label map uses 1 = kidney and 2 = lesion. These derived masks illustrate
                  schema only; they are not model output or a scored result.
                </p>
              </div>
            )}
          </article>
        </div>
      );
      break;
    case 'contract': {
      title = 'Format, overlap and geometry answer different questions';
      const f = out.fixtures[fixture];
      body = (
        <div className={styles.columns}>
          <article>
            <p className={styles.kicker}>SIX NONCLINICAL SOURCE-AUDIT FIXTURES · TWO 8³ ARRAYS</p>
            <div className={styles.fixtures}>
              {out.fixtures.map((item, i) => (
                <div key={item.id} data-kidney-fixture={item.id} data-current={i === fixture}>
                  {item.id.replaceAll('-', ' ')}
                </div>
              ))}
            </div>
            <p className={styles.note}>
              Selected: <b>{f.id}</b> · quick-check complete {String(f.quick_check_complete)} ·
              format valid {String(f.format_valid)}.
            </p>
            <p>
              Artificial array means: organ Dice {f.organ_dice.toFixed(2)}; lesion Dice on
              GT-positive cases {f.lesion_dice_positive.toFixed(2)}.
            </p>
          </article>
          <article>
            <h4>Independent geometry counterexample</h4>
            <MiniGrid shifted />
            <p>
              Format and array Dice do not prove physical alignment. A +100 mm origin shift can
              preserve array Dice in a toy fixture.
            </p>
            <p>
              Lesion Dice uses GT-positive cases: {f.lesion_positive_cases} of {f.cases} in this
              toy. No clinical score is implied.
            </p>
            <p className={styles.note}>
              Runner quick check requires both files; the separate format helper can treat a missing
              organ as optional.
            </p>
          </article>
        </div>
      );
      break;
    }
    case 'limits':
      title = 'What these retained bytes establish';
      body = (
        <div className={styles.cards}>
          <article>
            <b>Actual source</b>
            <p>Hash-verified KiTS19 case_00000 CT and released annotation, same native grid.</p>
          </article>
          <article>
            <b>Task contract</b>
            <p>35 pinned AutoMedBench files; six bounded nonclinical source-audit fixtures.</p>
          </article>
          <article>
            <b>Missing run</b>
            <p>No clinical model prediction, agent trace, S1–S3 judge result or patient Dice.</p>
          </article>
          <article>
            <b>Open layout</b>
            <p>
              Root-recipe data/Kidney and task-loader data/CruzAbdomen_Kidney differ; no staging
              execution reconciled them.
            </p>
          </article>
        </div>
      );
      break;
  }
  return (
    <section className={styles.scene} data-kidney-scene={s.scene}>
      <h3>{title}</h3>
      {body}
    </section>
  );
}

export function AutomedKidneyOutput({ state: s }: { state: AutomedKidneyState }) {
  const captions: Record<AutomedKidneyState['scene'], string> = {
    inputs:
      'Input CT only. Sampled views were chosen for teaching; the solver receives the full native volume.',
    assistance:
      'Lite names a checkpoint. Standard offers model-choice guidance. Both still require validation.',
    workflow: 'The five-step requirement is source text, not a completed run.',
    schema: 'Both binary NIfTI masks are required per patient and must preserve the CT affine.',
    reference: kidneyRevealed(s)
      ? 'Source annotation revealed to the reader. Label-derived oracle masks are format examples only.'
      : 'Reader reference is closed.',
    contract: 'Synthetic contract fixtures do not measure patient anatomy or capability.',
    limits: 'Source-backed task explanation, without a model or judge result.',
  };
  return (
    <aside className={`${shared.storyOutput} ${styles.aside}`} data-kidney-output={s.scene}>
      <b>{s.scene === 'inputs' ? 'Native source geometry' : 'Reading boundary'}</b>
      <p>{captions[s.scene]}</p>
      <small>KiTS19 case_00000 · CC-BY-NC-SA-4.0 · local noncommercial teaching</small>
    </aside>
  );
}
