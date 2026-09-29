import {
  realEchoColors as color,
  realEchoFrame,
  realEchoOutput as saved,
  realEchoRevealed,
  realEchoReview as withheld,
  realEchoSource as source,
  type CardiacRealEchoState,
} from './cardiac-real-echo';
import css from './cardiac-real-echo.module.css';
import shared from './task-visual.module.css';

const dot = (a: number[], b: number[]) => a.reduce((sum, x, i) => sum + x * b[i], 0);
const center = [100.2724, -20.043, 75.8716]; // Fixed centre from all retained primary and alternative points.

function Scan({
  name,
  image,
  section,
  sectionColor = color.output,
  review = false,
  geometry = false,
}: {
  name: string;
  image: string;
  section?: string;
  sectionColor?: string;
  review?: boolean;
  geometry?: boolean;
}) {
  return (
    <figure className={css.scan} data-real-echo-review={review ? 'image-only' : undefined}>
      <svg
        viewBox="0 0 256 256"
        role="img"
        aria-label={`${name} native grayscale ultrasound${section ? ' with saved mesh section' : ''}`}
      >
        <image href={image} width="256" height="256" />
        {geometry && (
          <g className={css.axes}>
            <path d="M127.5 14V242M14 127.5H242" />
            <circle cx="127.5" cy="127.5" r="3" />
            <text x="139" y="25">
              v · row
            </text>
            <text x="174" y="120">
              u · column
            </text>
          </g>
        )}
        {section && (
          <path
            data-real-echo-section
            d={section}
            fill="none"
            stroke={sectionColor}
            strokeWidth="2.5"
            vectorEffect="non-scaling-stroke"
          />
        )}
      </svg>
      <figcaption>
        {name}
        {review ? ' · withheld image, no truth contour' : ' · solver-visible'}
      </figcaption>
    </figure>
  );
}

function Mesh({
  frame,
  alternative = false,
  label,
}: {
  frame: number;
  alternative?: boolean;
  label: string;
}) {
  const rings = (alternative ? saved.basal_alternative_rings_mm : saved.primary_rings_mm)[frame];
  const axes = source.task_axes;
  const project = (point: number[]) => {
    const q = point.map((v, i) => v - center[i]);
    const t1 = dot(q, axes.transverse_1),
      t2 = dot(q, axes.transverse_2),
      depth = dot(q, axes.depth);
    return { x: 180 + 2.2 * (t1 + 0.3 * t2), y: 110 - 2.2 * (depth - 0.2 * t2), z: t2 };
  };
  const cells: { points: string; depth: number; shade: number }[] = [];
  for (let r = 0; r < rings.length - 1; r++)
    for (let a = 0; a < rings[r].length; a++) {
      const b = (a + 1) % rings[r].length;
      const p = [rings[r][a], rings[r][b], rings[r + 1][b], rings[r + 1][a]].map(project);
      cells.push({
        points: p.map((v) => `${v.x.toFixed(1)},${v.y.toFixed(1)}`).join(' '),
        depth: p.reduce((sum, v) => sum + v.z, 0) / 4,
        shade: Math.max(0.3, Math.min(0.8, 0.55 + p[0].z / 100)),
      });
    }
  cells.sort((a, b) => a.depth - b.depth);
  return (
    <figure
      className={css.mesh}
      data-real-echo-saved-output
      data-real-echo-mesh={alternative ? 'basal-alternative' : 'primary'}
    >
      <svg
        viewBox="0 0 360 220"
        role="img"
        aria-label={`${label}, frame ${frame + 1}, fixed millimetre projection of sampled saved vertices`}
      >
        <path d="M20 195H64M20 195V151" className={css.meshAxes} />
        <text x="69" y="198">
          20 mm
        </text>
        {cells.map((cell, i) => (
          <polygon
            key={i}
            points={cell.points}
            fill={alternative ? color.alternative : color.output}
            fillOpacity={cell.shade}
            stroke="#17313b"
            strokeWidth="0.35"
          />
        ))}
        {[0, 6, 12].map((r) => (
          <polyline
            key={r}
            points={rings[r]
              .map(project)
              .map((p) => `${p.x.toFixed(1)},${p.y.toFixed(1)}`)
              .join(' ')}
            fill="none"
            stroke="#163f4b"
            strokeWidth="0.9"
          />
        ))}
      </svg>
      <figcaption>{label} · saved points sampled for display · task mm</figcaption>
    </figure>
  );
}

function Volume({
  frame,
  alternative = false,
  control = false,
}: {
  frame: number;
  alternative?: boolean;
  control?: boolean;
}) {
  const x = (i: number) => 45 + i * 17;
  const y = (v: number) => 143 - (v / 240) * 116;
  const path = (v: number[]) => v.map((n, i) => `${i ? 'L' : 'M'}${x(i)},${y(n)}`).join(' ');
  return (
    <svg
      className={css.curve}
      viewBox="0 0 360 178"
      role="img"
      aria-label="Saved mesh-derived volume in mL, fixed 0 to 240 mL axis over 18 original frames"
    >
      {[0, 80, 160, 240].map((v) => (
        <g key={v}>
          <path d={`M45 ${y(v)}H334`} className={css.gridLine} />
          <text x="38" y={y(v) + 3} textAnchor="end">
            {v}
          </text>
        </g>
      ))}
      <text x="5" y="18">
        mL
      </text>
      <path d={path(saved.volume_ml)} stroke={color.output} strokeWidth="2.6" fill="none" />
      {alternative && (
        <path
          d={path(saved.alternative_volume_ml[2])}
          stroke={color.alternative}
          strokeWidth="2"
          strokeDasharray="5 3"
          fill="none"
        />
      )}
      {control && (
        <path
          d={path(saved.static_control_volume_ml)}
          stroke={color.control}
          strokeWidth="2"
          strokeDasharray="3 4"
          fill="none"
        />
      )}
      <path d={`M${x(frame)} 25V143`} stroke="#e3eceb" strokeWidth="1" />
      <circle cx={x(frame)} cy={y(saved.volume_ml[frame])} r="3.5" fill={color.output} />
      <text x="45" y="166">
        1
      </text>
      <text x="334" y="166" textAnchor="end">
        18
      </text>
      <text x="194" y="174" textAnchor="middle">
        original frame
      </text>
    </svg>
  );
}

export function CardiacRealEchoScene({ state }: { state: CardiacRealEchoState }) {
  const frame = realEchoFrame(state.phase);
  const reveal = realEchoRevealed(state);
  const showOutput =
    state.output > 0.5 && !['inputs', 'geometry', 'interpretation'].includes(state.scene);
  if (state.scene === 'review' || state.scene === 'limits') {
    return (
      <div
        className={css.root}
        data-real-echo-scene={state.scene}
        data-real-echo-frame={frame + 1}
        data-real-echo-review-state={reveal ? 'revealed' : 'hidden'}
      >
        <p className={css.tag}>Withheld directions · image-only review · frame {frame + 1}/18</p>
        {reveal ? (
          <div className={css.grid}>
            {[0, 1, 2, 3].map((i) => (
              <Scan
                key={i}
                name={withheld.views[i].name.replaceAll('_', ' ')}
                image={withheld.views[i].frames[frame]}
                section={showOutput ? withheld.primary_sections_px[i][frame] : undefined}
                review
              />
            ))}
          </div>
        ) : (
          <div className={css.hidden}>Reader-only planes hidden until explicit reveal.</div>
        )}
        {reveal && (
          <p className={css.stageNote}>
            Cyan is the saved surface intersection; a missing cyan section means the retained mesh
            does not cross that calibrated plane. Grayscale is ultrasound, not an anatomy label.
          </p>
        )}
      </div>
    );
  }
  if (
    state.scene === 'reconstruction' ||
    state.scene === 'alternatives' ||
    state.scene === 'controls'
  ) {
    return (
      <div
        className={css.root}
        data-real-echo-scene={state.scene}
        data-real-echo-frame={frame + 1}
        data-real-echo-review-state="hidden"
      >
        <p className={css.tag}>
          One acquisition · saved reconstruction · frame {frame + 1}/18 ·{' '}
          {source.times_seconds[frame].toFixed(2)} s
        </p>
        <div className={css.operation}>
          <Scan
            name="Long axis 0°"
            image={source.views[0].frames[frame]}
            section={
              showOutput
                ? state.scene === 'alternatives'
                  ? saved.basal_alternative_plane0_sections_px[frame]
                  : saved.primary_sections_px[0][frame]
                : undefined
            }
            sectionColor={state.scene === 'alternatives' ? color.alternative : color.output}
          />
          {state.scene === 'alternatives' ? (
            <Mesh frame={frame} alternative label="Basal assumption alternative" />
          ) : (
            <Mesh frame={frame} label="Primary cavity surface" />
          )}
          <Volume
            frame={frame}
            alternative={state.scene === 'alternatives'}
            control={state.scene === 'controls'}
          />
        </div>
        <p className={css.stageNote}>
          Fixed pixel scale 0.75 mm/pixel · fixed mesh projection and 0–240 mL curve scale.{' '}
          {state.scene === 'alternatives'
            ? 'Orange is the saved basal variant section and mesh.'
            : 'Cyan is saved output, not a supplied contour.'}
        </p>
      </div>
    );
  }
  return (
    <div
      className={css.root}
      data-real-echo-scene={state.scene}
      data-real-echo-frame={frame + 1}
      data-real-echo-review-state="hidden"
    >
      <p className={css.tag}>
        Four synchronized reslices of one 3D ultrasound acquisition · frame {frame + 1}/18 ·{' '}
        {source.times_seconds[frame].toFixed(2)} s
      </p>
      <div className={css.grid}>
        {source.views.map((view, i) => (
          <Scan
            key={i}
            name={['Long axis 0°', 'Long axis 90°', 'Short axis 65 mm', 'Short axis 105 mm'][i]}
            image={view.frames[frame]}
            geometry={state.scene === 'geometry'}
          />
        ))}
      </div>
      {state.scene === 'geometry' && (
        <p className={css.stageNote}>
          World point = plane origin + 0.75 mm × [(column − 127.5)u + (row − 127.5)v]. The axes are
          supplied calibration, not a cavity label.
        </p>
      )}
      {state.scene === 'interpretation' && (
        <p className={css.stageNote}>
          The original agent inspected these pixels and then recorded radii, centroids, apex and
          basal extents in fixed tables. No contour, seed or initial mesh was supplied.
        </p>
      )}
    </div>
  );
}

export function CardiacRealEchoOutput({ state }: { state: CardiacRealEchoState }) {
  const reveal = realEchoRevealed(state);
  const title: Record<CardiacRealEchoState['scene'], string> = {
    inputs: 'Input: 72 real ultrasound images',
    geometry: 'Supplied: calibrated plane geometry',
    interpretation: 'Operation: interpret sparse image planes',
    reconstruction: 'Output: saved dynamic surface',
    alternatives: 'Assumption sensitivity, not certainty',
    review: 'Withheld images revealed for review',
    controls: 'Artifact validity and input dependence',
    limits: 'One case; no independent cavity truth',
  };
  return (
    <aside className={`${shared.storyOutput} ${css.output}`} data-real-echo-output>
      <strong>{title[state.scene]}</strong>
      {state.scene === 'inputs' && (
        <p>
          Four planes × 18 original frames, 256 × 256 pixels each. These are reslices of one
          simultaneous acquisition, not four probe recordings.
        </p>
      )}
      {state.scene === 'geometry' && (
        <p>
          The 73rd public file gives plane origins and directions in task millimetres. No mask,
          seed, initial mesh or reference is supplied.
        </p>
      )}
      {state.scene === 'interpretation' && (
        <p>
          Original image viewing informed fixed measurements. The basal cap and out-of-plane
          completion remain modeling choices.
        </p>
      )}
      {state.scene === 'reconstruction' && (
        <p>
          The saved primary mesh has 1,202 vertices and 2,400 faces per frame. Its curve spans
          54.08–177.57 mL; these are model geometry, not clinical EF.
        </p>
      )}
      {state.scene === 'alternatives' && (
        <p>
          Orange dashed is one retained basal alternative at the same frame. Three saved
          alternatives change shape assumptions; their spread is not calibrated coverage.
        </p>
      )}
      {state.scene === 'review' && (
        <p>
          {reveal
            ? 'Four more ultrasound planes were withheld from the solver. Cyan mesh sections can be inspected against pixels, but no independent contour is present.'
            : 'Select the review chapter to reveal the image-only withheld planes.'}
        </p>
      )}
      {state.scene === 'controls' && (
        <p>
          Primary and image-ignorant static ellipsoid each earned artifact reward 1; no-output
          earned 0. The static-input replay changed 68/72 PNGs but left the fixed-table meshes
          unchanged.
        </p>
      )}
      {state.scene === 'limits' && (
        <p>
          One selected source sequence and one original agent attempt.{' '}
          {reveal
            ? 'Withheld images support qualitative section review, not a truth score.'
            : 'The withheld review remains hidden.'}{' '}
          No clinical EF, material motion or population claim follows.
        </p>
      )}
      <div className={css.legend}>
        {state.output > 0.5 && (
          <span>
            <i style={{ background: color.output }} />
            Saved primary
          </span>
        )}
        {state.scene === 'alternatives' && (
          <span>
            <i className={css.dashed} style={{ borderColor: color.alternative }} />
            Saved alternative
          </span>
        )}
        {state.scene === 'controls' && (
          <span>
            <i className={css.dashed} style={{ borderColor: color.control }} />
            Static format control
          </span>
        )}
        {reveal && (
          <span data-real-echo-review="image-only">Grayscale withheld image · no GT contour</span>
        )}
      </div>
      {state.scene === 'controls' && (
        <small>
          Reward tests file structure, mesh validity and volume arithmetic; it does not test
          anatomy. Original trace viewed images, while the replayed executable used fixed
          measurements.
        </small>
      )}
      {state.scene === 'limits' && (
        <small>
          18 samples are not an adjudicated heartbeat. Persistent mesh indices do not establish
          tracked tissue.
        </small>
      )}
    </aside>
  );
}
