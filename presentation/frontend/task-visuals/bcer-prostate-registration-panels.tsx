import type { ReactNode } from 'react';
import styles from './bcer-prostate-registration.module.css';
import shared from './task-visual.module.css';
import {
  bcerSource as src,
  bcerOperation as op,
  bcerIndex,
  type BcerProstateState,
} from './bcer-prostate-registration';

const short = (n: number) => Number(n.toFixed(2));

function Scan({ index, cross = false, role }: { index: number; cross?: boolean; role?: string }) {
  const s = src.sequences[index];
  // SVG image coordinates address pixel edges; continuous voxel indices address centers.
  const [x, y] = s.witness_ijk.map((v) => v + 0.5);
  return (
    <figure className={styles.scan} data-bcer-prostate-input={s.name}>
      <div className={styles.scanFrame}>
        <svg
          viewBox={`0 0 ${s.size_xyz[0]} ${s.size_xyz[1]}`}
          role="img"
          aria-label={`${s.name} native axial slice ${s.slice_k}; ${s.size_xyz[0]} by ${s.size_xyz[1]} voxel image${cross ? '; header-coordinate witness' : ''}`}
        >
          <image href={s.png} width={s.size_xyz[0]} height={s.size_xyz[1]} />
          {cross && (
            <g
              data-bcer-prostate-witness
              stroke="#f4c54e"
              strokeWidth={Math.max(1, s.size_xyz[0] / 220)}
            >
              <circle cx={x} cy={y} r={s.size_xyz[0] / 45} fill="none" />
              <path
                d={`M${x - s.size_xyz[0] / 25} ${y}h${s.size_xyz[0] / 12.5}M${x} ${y - s.size_xyz[0] / 25}v${s.size_xyz[0] / 12.5}`}
              />
            </g>
          )}
        </svg>
      </div>
      <figcaption>
        <b>
          {role ? `${role} · ` : ''}
          {s.name} · native LPS k={s.slice_k}
        </b>
        <span>
          {s.size_xyz.join(' × ')} voxels · {short(s.spacing_xyz_mm[0])} ×{' '}
          {short(s.spacing_xyz_mm[1])} × {short(s.spacing_xyz_mm[2])} mm
        </span>
      </figcaption>
    </figure>
  );
}

function SymbolicGrid({ moving, swap = false }: { moving: string; swap?: boolean }) {
  return (
    <svg
      className={styles.diagram}
      viewBox="0 0 570 215"
      role="img"
      aria-label="Symbolic physical-space mapping from dense T2w target grid through LPS millimeters to coarse moving diffusion grid, without a patient resample"
    >
      <defs>
        <pattern id="bcerFine" width="13" height="13" patternUnits="userSpaceOnUse">
          <path d="M13 0H0V13" fill="none" stroke="#7296a9" strokeWidth=".7" />
        </pattern>
        <pattern id="bcerCoarse" width="34" height="34" patternUnits="userSpaceOnUse">
          <path d="M34 0H0V34" fill="none" stroke="#7296a9" strokeWidth="1" />
        </pattern>
      </defs>
      <rect
        x="8"
        y="25"
        width="172"
        height="140"
        fill={swap ? 'url(#bcerCoarse)' : 'url(#bcerFine)'}
        stroke="#60a9b9"
        strokeWidth="2"
      />
      <rect
        x="390"
        y="25"
        width="172"
        height="140"
        fill={swap ? 'url(#bcerFine)' : 'url(#bcerCoarse)'}
        stroke="#e5ae48"
        strokeWidth="2"
      />
      <circle cx="94" cy="95" r="7" fill="#f5cf62" stroke="#213742" />
      <circle cx="476" cy="95" r="7" fill="#f5cf62" stroke="#213742" />
      <path d="M190 95h190" stroke="#3f768a" strokeWidth="3" markerEnd="none" />
      <path d="M375 89l8 6-8 6" fill="none" stroke="#3f768a" strokeWidth="3" />
      <text x="94" y="187" textAnchor="middle">
        {swap ? moving : 'T2w'} · {swap ? 'wrong fixed' : 'fixed output'}
      </text>
      <text x="476" y="187" textAnchor="middle">
        {swap ? 'T2w · wrong moving' : `${moving} · moving input`}
      </text>
      <text x="285" y="74" textAnchor="middle">
        LPS mm
      </text>
      <text x="285" y="120" textAnchor="middle">
        T = identity
      </text>
      <text x="285" y="204" textAnchor="middle">
        symbolic grids · no patient pixels resampled
      </text>
    </svg>
  );
}

export function BcerProstateScene({ state: s }: { state: BcerProstateState }) {
  const view = bcerIndex(s.view, 3),
    moving = 1 + bcerIndex(s.moving, 2);
  const movingName = src.sequences[moving].name;
  const swap = s.swap > 0.5;
  let title = '';
  let body: ReactNode;
  switch (s.scene) {
    case 'availability':
      title = 'Real inputs; no retained registration result';
      body = (
        <div className={styles.columns}>
          <Scan index={0} />
          <article>
            <p className={styles.kicker}>PI-CAI 10001_1000001 · REPRESENTATIVE INPUT</p>
            <h4>Actual T2w, ADC and high-b DWI</h4>
            <p>
              These three sequences were retained for a different BCER workflow audit. They are a
              task-matched input example, not proof of admission to the medium task.
            </p>
            <p className={styles.callout}>
              No transform, resampled patient volume, independent correspondence target or
              registration quality measurement is retained.
            </p>
          </article>
        </div>
      );
      break;
    case 'inputs':
      title = 'Inspect three unregistered native contrasts';
      body = (
        <>
          <div className={styles.three}>
            {src.sequences.map((_, i) => (
              <div key={i} data-current={i === view}>
                <Scan index={i} />
              </div>
            ))}
          </div>
          <p>
            Native central k=10 planes have sequence-specific display ranges and different fields of
            view. Panel widths are for inspection, not a common physical scale.
          </p>
        </>
      );
      break;
    case 'select':
      title = 'Keep fixed and moving roles explicit';
      body = (
        <div className={styles.columns}>
          <Scan index={0} role="fixed" />
          <div>
            <Scan index={moving} role="moving" />
            <p className={styles.callout}>
              `identify_sequences` resolves typed paths; `register_to_reference` takes fixed T2w and
              moving {movingName}. The case manifest and runtime state are supplied helpers, not
              image labels.
            </p>
          </div>
        </div>
      );
      break;
    case 'coordinates':
      title = 'The same LPS point has different voxel indices';
      body = (
        <div className={styles.columns}>
          <Scan index={0} cross role="fixed" />
          <div>
            <Scan index={moving} cross role="moving" />
            <p className={styles.coordinate} data-bcer-prostate-coordinates>
              LPS ({op.witness.lps_mm.map(short).join(', ')}) mm
              <br />
              T2w ({op.witness.t2w_ijk.map(short).join(', ')}) → {movingName} (
              {src.sequences[moving].witness_ijk.map(short).join(', ')})
            </p>
          </div>
        </div>
      );
      break;
    case 'resample':
      title = 'Default identity uses header-based resampling';
      body = (
        <div className={styles.columns}>
          <SymbolicGrid moving={movingName} />
          <article data-bcer-prostate-symbolic-operation>
            <p className={styles.kicker}>SYMBOLIC OPERATION · NO PATIENT OUTPUT</p>
            <h4>Target T2w grid → LPS → moving grid</h4>
            <ol>
              {op.mapping.map((m, i) => (
                <li
                  key={m}
                  data-bcer-prostate-operation-step={i}
                  data-current={i === bcerIndex(s.operation, op.mapping.length)}
                >
                  {m}
                </li>
              ))}
            </ol>
            <p>
              <b>Default method:</b> identity physical transform. <b>Interpolation:</b> linear for
              continuous MRI.
            </p>
            <p className={styles.callout}>
              Rigid and affine mutual-information optimization exist in the tool, but neither was
              run here. Header correspondence does not establish anatomical alignment.
            </p>
          </article>
        </div>
      );
      break;
    case 'contract':
      title = 'Files can exist in the wrong output space';
      body = (
        <div className={styles.columns}>
          <div>
            <SymbolicGrid moving={movingName} swap={swap} />
            <p className={styles.callout} data-bcer-prostate-swap={swap}>
              {swap
                ? op.swap_counterexample
                : 'Correct role assignment requests a resampled moving image on the fixed T2w grid.'}
            </p>
          </div>
          <article data-bcer-prostate-empty-output>
            <p className={styles.kicker}>REQUIRED KEYS · BOTH EMPTY HERE</p>
            <div className={styles.sockets}>
              <div>
                <b>transform_path</b>
                <span>no saved file</span>
              </div>
              <div>
                <b>resampled_path</b>
                <span>no saved file</span>
              </div>
            </div>
            <p>
              Evaluator checks both stages, both paths, and resampled existence/nonempty status. It
              has no independent landmark or anatomical quality reference.
            </p>
          </article>
        </div>
      );
      break;
    case 'limits':
      title = 'Structural validity is not registration accuracy';
      body = (
        <div className={styles.cards}>
          <article>
            <b>Actual inputs</b>
            <p>Three hash-verified native PI-CAI images and LPS headers.</p>
          </article>
          <article>
            <b>Symbolic operation</b>
            <p>
              Default identity header mapping and linear resampling are explained, not executed.
            </p>
          </article>
          <article>
            <b>Missing output</b>
            <p>No target-task transform, resampled patient image or BCER medium run.</p>
          </article>
          <article>
            <b>Missing reference</b>
            <p>
              No independent correspondence target; path/nonzero checks do not measure alignment.
            </p>
          </article>
        </div>
      );
      break;
  }
  return (
    <section className={styles.scene} data-bcer-prostate-scene={s.scene}>
      <h3>{title}</h3>
      {body}
    </section>
  );
}

export function BcerProstateOutput({ state: s }: { state: BcerProstateState }) {
  const copy: Record<BcerProstateState['scene'], string> = {
    availability:
      'Only representative source images are retained. The top notice applies throughout.',
    inputs: 'Native T2w uses 0.3 mm in-plane spacing; ADC and high-b DWI use 2 mm.',
    select: 'T2w is the requested fixed output grid; ADC or high-b DWI is moving.',
    coordinates: 'The cross is an author coordinate witness, not an anatomical landmark.',
    resample:
      'Identity in physical LPS is header-based resampling; no optimized registration is demonstrated.',
    contract:
      'Both named target artifacts remain empty; structural checks cannot establish accuracy.',
    limits: 'Mixed-basis teaching explanation, not a BCER medium task result.',
  };
  return (
    <aside className={`${shared.storyOutput} ${styles.aside}`} data-bcer-prostate-output={s.scene}>
      <b>Registration boundary</b>
      <p>{copy[s.scene]}</p>
      <small>PI-CAI input: CC-BY-NC-4.0 · BCER d108167 · no model or registration run</small>
    </aside>
  );
}
