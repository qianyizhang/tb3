import {
  contourColors as color,
  contourCondition,
  contourFrame,
  contourOutput,
  contourReference,
  contourReveal,
  contourSource,
  type CardiacContourState,
  type ContourCondition,
} from './cardiac-contour';
import css from './cardiac-contour.module.css';
import shared from './task-visual.module.css';

function Scan({
  title,
  image,
  helper,
  output,
  reference,
  withheld = false,
  rays,
}: {
  title: string;
  image: string;
  helper?: string;
  output?: string;
  reference?: string;
  withheld?: boolean;
  rays?: { polar_index: number[]; positive_radius_px: number[]; negative_radius_px: number[] };
}) {
  return (
    <figure className={css.scan} data-contour-heldout={withheld ? 'true' : undefined}>
      <figcaption>{title}</figcaption>
      <svg viewBox="0 0 485 464" role="img" aria-label={title}>
        <image href={image} width="485" height="464" />
        {helper && <image data-contour-supplied href={helper} width="485" height="464" />}
        {rays &&
          rays.polar_index.map((polar, j) => {
            const phi = (polar * Math.PI) / 64;
            const r = rays.positive_radius_px[j];
            return (
              <g key={polar} data-contour-radial-sample>
                <line
                  x1="242"
                  y1="172"
                  x2={242 + r * Math.sin(phi)}
                  y2={172 + r * Math.cos(phi)}
                  stroke="#f8e09b"
                  strokeWidth="1.4"
                  opacity=".72"
                />
                <circle
                  cx={242 + r * Math.sin(phi)}
                  cy={172 + r * Math.cos(phi)}
                  r="2.3"
                  fill="#f8e09b"
                />
              </g>
            );
          })}
        {output && <image data-contour-output href={output} width="485" height="464" />}
        {reference && <image data-contour-reference href={reference} width="485" height="464" />}
      </svg>
      <small>Native rows/columns · 0.089950 mm/pixel</small>
    </figure>
  );
}

function Curve({ state }: { state: CardiacContourState }) {
  const frame = contourFrame(state);
  const curves = contourOutput.curves_ml;
  const showReference = contourReveal(state);
  const x = (i: number) => 46 + (i / 29) * 312;
  const y = (value: number) => 154 - (value / 1.05) * 120;
  const line = (values: number[]) =>
    values.map((v, i) => `${i ? 'L' : 'M'}${x(i)},${y(v)}`).join(' ');
  return (
    <div className={css.curveWrap}>
      <svg
        className={css.curve}
        viewBox="0 0 378 190"
        role="img"
        aria-label="Saved cavity volumes for one, four and eight supplied-view conditions; dense curve is revealed separately"
      >
        {[0, 0.5, 1].map((v) => (
          <g key={v}>
            <path d={`M46 ${y(v)}H358`} stroke="#cad5d8" />
            <text x="37" y={y(v) + 4} textAnchor="end">
              {v.toFixed(1)}
            </text>
          </g>
        ))}
        <text x="8" y="17">
          mL
        </text>
        <path d={line(curves.one)} stroke="#799ca5" strokeWidth="2" fill="none" />
        <path d={line(curves.two)} stroke="#9d769d" strokeWidth="2" fill="none" />
        <path d={line(curves.four)} stroke={color.output} strokeWidth="3" fill="none" />
        <path d={line(curves.eight)} stroke="#537b9b" strokeWidth="2" fill="none" />
        {showReference && (
          <path
            data-contour-reference
            d={line(contourReference.dense_curve_ml)}
            stroke={color.reference}
            strokeWidth="2.5"
            strokeDasharray="5 3"
            fill="none"
          />
        )}
        <path d={`M${x(frame)} 26V154`} stroke="#35464c" strokeWidth="1" />
        <text x="46" y="177">
          1
        </text>
        <text x="358" y="177" textAnchor="end">
          30
        </text>
        <text x="202" y="188" textAnchor="middle">
          Native source frame
        </text>
      </svg>
      <div className={css.key}>
        <span>
          <i style={{ background: '#799ca5' }} />1 view
        </span>
        <span>
          <i style={{ background: '#9d769d' }} />2 views
        </span>
        <span>
          <i style={{ background: color.output }} />4 views
        </span>
        <span>
          <i style={{ background: '#537b9b' }} />8 views
        </span>
        {showReference && (
          <span data-contour-reference>
            <i
              style={{
                background: color.reference,
                backgroundImage:
                  'repeating-linear-gradient(90deg, #f4bc49 0 4px, transparent 4px 7px)',
              }}
            />
            Dense source fit · dashed
          </span>
        )}
      </div>
    </div>
  );
}

/** Fixed camera and scale across source-derived saved meshes and the retained z-scale control. */
function Surface({
  points,
  depthScale = 1,
  label,
}: {
  points: number[][];
  depthScale?: number;
  label: string;
}) {
  const rings = contourOutput.mesh_sample_grid.rings;
  const azimuths = contourOutput.mesh_sample_grid.azimuths;
  const project = (p: number[]) => [
    116 + 9 * p[0] + 4 * p[2] * depthScale,
    94 - 8 * p[1] + 2 * p[2] * depthScale,
  ];
  const cells = [];
  for (let ring = 0; ring < rings - 1; ring++)
    for (let az = 0; az < azimuths; az++) {
      const next = (az + 1) % azimuths;
      const vertices = [
        points[ring * azimuths + az],
        points[ring * azimuths + next],
        points[(ring + 1) * azimuths + next],
        points[(ring + 1) * azimuths + az],
      ];
      const depth = vertices.reduce((sum, p) => sum + p[2] * depthScale, 0) / 4;
      cells.push({
        depth,
        path: vertices.map((p, i) => `${i ? 'L' : 'M'}${project(p).join(',')}`).join('') + 'Z',
        tone: Math.max(0.18, Math.min(0.75, 0.46 + depth / 20)),
      });
    }
  cells.sort((a, b) => a.depth - b.depth);
  const ringLine = (ring: number) =>
    Array.from({ length: azimuths + 1 }, (_, i) => {
      const p = project(points[ring * azimuths + (i % azimuths)]);
      return `${i ? 'L' : 'M'}${p.join(',')}`;
    }).join('');
  return (
    <figure className={css.surface} data-contour-surface={label}>
      <figcaption>{label}</figcaption>
      <svg
        viewBox="0 0 232 188"
        role="img"
        aria-label={`${label}; fixed camera, sampled saved cavity mesh`}
      >
        {cells.map((cell, i) => (
          <path
            key={i}
            d={cell.path}
            fill={color.output}
            fillOpacity={cell.tone}
            stroke="#205a68"
            strokeOpacity=".1"
            strokeWidth=".3"
          />
        ))}
        {[0, 3, 6, 9, 11].map((ring) => (
          <path
            key={ring}
            d={ringLine(ring)}
            fill="none"
            stroke="#276473"
            strokeWidth=".65"
            opacity=".65"
          />
        ))}
      </svg>
      <small>Saved mesh display sample · fixed millimeter camera</small>
    </figure>
  );
}

export function CardiacContourScene({ state }: { state: CardiacContourState }) {
  const frame = contourFrame(state);
  const item = contourSource.frames[frame];
  const condition = contourCondition(state);
  const helper = state.helper > 0.5;
  const output = state.output > 0.5;
  const reveal = contourReveal(state);
  const showFour = state.scene === 'views';
  const showOperation = state.scene === 'reconstruct';
  const points = contourOutput.mesh_samples_mm[condition][frame];
  const depthScale = 1 + 0.25 * Math.cos((2 * Math.PI * (frame - 1)) / 30);
  return (
    <section
      className={css.scene}
      data-cardiac-contour-scene={state.scene}
      data-contour-frame={item.frame_1based}
    >
      <div className={css.mast}>
        <strong>Patient001 · frame {item.frame_1based}/30</strong>
        <span>Fetal radial ultrasound · one case</span>
      </div>
      {showOperation ? (
        <div className={css.operation} data-contour-operation>
          <Scan
            title="1 · Sample the supplied boundary"
            image={item.supplied_image}
            helper={item.supplied_contour}
            rays={contourOutput.radial_samples[frame]}
          />
          <div className={css.method}>
            <strong>2 · Fill unobserved directions</strong>
            <p>
              Nine of 65 polar samples shown. Interpolate across four supplied planes onto 72
              azimuths; close the poles.
            </p>
            <p>
              Each source frame is fit independently. This star-shaped prior supplies unseen
              geometry.
            </p>
            <span className={css.arrow}>→</span>
          </div>
          <Surface points={points} label="3 · Saved four-view cavity" />
        </div>
      ) : state.scene === 'depth' ? (
        <div className={css.depthPair} data-contour-depth-control>
          <Scan
            title="Same observed z = 0 plane"
            image={item.supplied_image}
            helper={item.supplied_contour}
          />
          <Surface points={points} label="Saved one-view completion" />
          <Surface
            points={points}
            depthScale={depthScale}
            label={`Unseen z ×${depthScale.toFixed(2)} · retained control`}
          />
          <p>
            Both surfaces preserve z = 0 exactly. A fixed camera and millimeter scale show the
            changed unseen depth.
          </p>
        </div>
      ) : (
        <div className={showFour ? css.four : css.pair}>
          <Scan
            title="Plane 1 · supplied image and cavity boundary"
            image={item.supplied_image}
            helper={helper ? item.supplied_contour : undefined}
          />
          {showFour ? (
            item.additional_inputs.map((view) => (
              <Scan
                key={view.plane_1based}
                title={`Plane ${view.plane_1based} · supplied boundary`}
                image={view.image}
                helper={helper ? view.contour : undefined}
              />
            ))
          ) : (
            <Scan
              title="Plane 8 · withheld evaluation view"
              withheld
              image={item.withheld_image}
              output={output ? contourOutput.frames[frame][condition] : undefined}
              reference={reveal ? contourReference.frames[frame].withheld_contour : undefined}
            />
          )}
        </div>
      )}
      {['curves', 'limits'].includes(state.scene) && <ScoreTable reveal={reveal} />}
    </section>
  );
}

function ScoreTable({ reveal }: { reveal: boolean }) {
  const keys = ['one', 'two', 'four', 'eight', 'static'] as const;
  return (
    <table className={css.scores}>
      <thead>
        <tr>
          <th>Supplied</th>
          <th>Withheld Dice</th>
          <th>HD95</th>
          <th>Volume MAPE</th>
          <th>EF error</th>
        </tr>
      </thead>
      <tbody>
        {keys.map((key) => {
          const m = contourReference.stats[key];
          return (
            <tr key={key} data-contour-reference={reveal ? '' : undefined}>
              <th>
                {key === 'static' ? 'Static 4-view' : `${m.input_planes_1based.length} views`}
              </th>
              <td>{reveal ? m.heldout_dice.mean.toFixed(3) : 'Reveal'}</td>
              <td>{reveal ? `${m.heldout_hd95_mm.mean.toFixed(3)} mm` : 'Reveal'}</td>
              <td>{reveal ? `${m.volume_curve_mape_vs_dense_percent.toFixed(2)}%` : 'Reveal'}</td>
              <td>{reveal ? `${m.ef_error_vs_dense_reference_pp.toFixed(2)} pp` : 'Reveal'}</td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}

export function CardiacContourOutput({ state }: { state: CardiacContourState }) {
  const reveal = contourReveal(state);
  const frame = contourFrame(state);
  const condition = contourCondition(state);
  const volume = contourOutput.curves_ml[condition][frame];
  const showSaved = state.output > 0.5;
  return (
    <aside className={`${shared.storyOutput} ${css.output}`} data-cardiac-contour-output>
      <h3>
        {state.scene === 'depth'
          ? 'One plane, two completions'
          : showSaved
            ? 'Saved 3D cavity estimate'
            : 'Input contract'}
      </h3>
      {showSaved ? (
        <>
          <p>
            <strong>{volume.toFixed(3)} mL</strong> at frame {frame + 1} · {condition} supplied
            contour views
          </p>
          <Curve state={state} />
        </>
      ) : state.scene !== 'depth' ? (
        <p>
          Native radial ultrasound and clean label-127 cavity masks at every phase. Reconstruction
          output and withheld evaluation masks are hidden.
        </p>
      ) : null}
      {state.scene === 'depth' && (
        <p className={css.depth}>
          One observed plane admits different unseen depths: the retained control changes derived EF
          from <strong>66.47%</strong> to <strong>79.88%</strong> (13.41 pp). Neither completion is
          validated anatomy.
        </p>
      )}
      <p className={css.note}>
        One patient ·{' '}
        {reveal ? '30 × 8 = 240 frame/plane pairs per sparse condition' : 'withheld masks hidden'} ·
        dense curve includes evaluation planes and is source fit. Static control repeats frame-1
        four-view geometry.
      </p>
    </aside>
  );
}
