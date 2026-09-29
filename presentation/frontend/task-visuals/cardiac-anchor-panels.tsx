import {
  anchorCondition,
  anchorFrame,
  anchorOutput,
  anchorReference,
  anchorSource,
  type CardiacAnchorState,
  type Condition,
} from './cardiac-anchor';
import sharedStyles from './task-visual.module.css';
import styles from './cardiac-anchor.module.css';

function Panel({
  image,
  helper,
  output,
  reference,
  label,
  referenceVisible,
}: {
  image: string;
  helper?: string;
  output?: string;
  reference?: string;
  label: string;
  referenceVisible: boolean;
}) {
  return (
    <figure className={styles.panel}>
      <div className={styles.image}>
        <img src={image} alt="FeEcho4D teaching panel at half native display size" />
        {helper && <img className={styles.overlay} src={helper} alt="Supplied anchor boundary" />}
        {output && (
          <img
            className={styles.overlay}
            src={output}
            alt="Saved prediction boundary"
            data-cardiac-anchor-output-boundary
          />
        )}
        {referenceVisible && reference && (
          <img
            className={styles.overlay}
            src={reference}
            alt="Reader-only source boundary"
            data-cardiac-anchor-reference-boundary
          />
        )}
      </div>
      <figcaption>{label}</figcaption>
    </figure>
  );
}

function Curve({
  condition,
  frame,
  reveal,
}: {
  condition: Condition;
  frame: number;
  reveal: boolean;
}) {
  const selected = anchorOutput.conditions[condition].volume_ml;
  const dense = anchorReference.dense_volume_ml;
  const left = 44,
    right = 360,
    top = 18,
    bottom = 124;
  const max = 1.2; // Fixed mL scale across one/two conditions and dense comparator.
  const x = (i: number) => left + ((right - left) * i) / 29;
  const y = (v: number) => bottom - ((bottom - top) * v) / max;
  const path = (values: number[]) =>
    values.map((v, i) => `${i ? 'L' : 'M'}${x(i)},${y(v)}`).join(' ');
  return (
    <svg
      className={styles.curve}
      viewBox="0 0 380 150"
      role="img"
      aria-label={`Saved ${condition === 'one' ? 'one-anchor' : 'two-anchor'} cavity volume over 30 frames. ${reveal ? 'Dense annotation-derived comparator revealed.' : 'Dense comparator hidden.'}`}
      data-cardiac-anchor-volume
    >
      <path d={`M${left} ${top}V${bottom}H${right}`} className={styles.axis} />
      {[0, 0.4, 0.8, 1.2].map((v) => (
        <g key={v}>
          <path d={`M${left - 3} ${y(v)}H${right}`} className={styles.gridline} />
          <text x="38" y={y(v) + 3} textAnchor="end">
            {v.toFixed(1)}
          </text>
        </g>
      ))}
      <text x="5" y="17">
        mL
      </text>
      <text x="44" y="146">
        1
      </text>
      <text x="360" y="146" textAnchor="end">
        30
      </text>
      <path d={path(selected)} fill="none" stroke="#22d7e0" strokeWidth="2.5" />
      {reveal && (
        <path
          d={path(dense)}
          fill="none"
          stroke="#ffbe4b"
          strokeWidth="2.5"
          strokeDasharray="5 3"
          data-cardiac-anchor-reference-curve
        />
      )}
      <path d={`M${x(frame)} ${top}V${bottom}`} stroke="#d5e4e5" strokeWidth="1" />
      <circle cx={x(frame)} cy={y(selected[frame])} r="4" fill="#22d7e0" />
      <text x="215" y="145" textAnchor="middle">
        Filename frame
      </text>
    </svg>
  );
}

function MeshProjection({ condition, frame }: { condition: Condition; frame: number }) {
  const rings = anchorOutput.conditions[condition].mesh_rings_mm[frame];
  const project = (p: number[]) => [150 + 9 * (p[0] + 0.55 * p[2]), 110 - 9 * (p[1] - 0.18 * p[2])];
  const line = (points: number[][], close = false) =>
    points
      .map((p, i) => {
        const [x, y] = project(p);
        return `${i ? 'L' : 'M'}${x.toFixed(1)},${y.toFixed(1)}`;
      })
      .join(' ') + (close ? ' Z' : '');
  const cells: { path: string; depth: number; opacity: number }[] = [];
  for (let ring = 0; ring < rings.length - 1; ring++) {
    for (let az = 0; az < rings[ring].length; az++) {
      const next = (az + 1) % rings[ring].length;
      const vertices = [
        rings[ring][az],
        rings[ring][next],
        rings[ring + 1][next],
        rings[ring + 1][az],
      ];
      const depth = vertices.reduce((sum, p) => sum + p[2], 0) / 4;
      cells.push({
        path: line(vertices, true),
        depth,
        opacity: Math.max(0.24, Math.min(0.78, 0.5 + depth / 23)),
      });
    }
  }
  cells.sort((a, b) => a.depth - b.depth);
  return (
    <figure className={styles.meshFigure}>
      <svg
        viewBox="0 0 300 220"
        role="img"
        aria-label={`Native millimetre cavity mesh, frame ${frame + 1}; fixed projection of sampled retained vertices`}
        data-cardiac-anchor-mesh
      >
        {cells.map((cell, i) => (
          <path
            key={i}
            d={cell.path}
            fill="#22d7e0"
            fillOpacity={cell.opacity}
            stroke="#205a68"
            strokeOpacity="0.08"
            strokeWidth="0.3"
          />
        ))}
        {[0, 3, 6, 9, 10].map((ring) => (
          <path
            key={ring}
            d={line(rings[ring], true)}
            fill="none"
            stroke="#276473"
            strokeWidth="0.7"
            opacity="0.7"
          />
        ))}
        <text x="8" y="19">
          Saved mesh vertices · mm
        </text>
        <text x="8" y="208">
          Fixed oblique display projection
        </text>
      </svg>
      <figcaption>
        Sampled retained surface rings, frame {frame + 1}; fixed scale and orientation.
      </figcaption>
    </figure>
  );
}

export function CardiacAnchorScene({ state }: { state: CardiacAnchorState }) {
  const frame = anchorFrame(state.phase);
  const one = anchorOutput.conditions.one,
    two = anchorOutput.conditions.two;
  const condition = anchorCondition(state.scene);
  const reveal =
    state.reference > 0.5 && ['reference', 'comparison', 'limits'].includes(state.scene);
  const selected = anchorReference.selected;
  if (state.scene === 'surface' || state.scene === 'reference' || state.scene === 'limits') {
    const fixed = state.scene === 'reference' || state.scene === 'limits' ? 16 : frame;
    const ref = selected['withheld-8-17'];
    const neutral =
      'data:image/svg+xml,' +
      encodeURIComponent(
        '<svg xmlns="http://www.w3.org/2000/svg" width="243" height="232" viewBox="0 0 243 232"><rect width="243" height="232" fill="#10232d"/><text x="121" y="114" fill="#c5d5d8" font-size="11" text-anchor="middle">Saved mesh section</text><text x="121" y="130" fill="#c5d5d8" font-size="9" text-anchor="middle">withheld image hidden</text></svg>',
      );
    return (
      <div
        className={styles.root}
        data-cardiac-anchor-scene={state.scene}
        data-cardiac-anchor-frame={fixed + 1}
        data-cardiac-anchor-condition="one"
        data-cardiac-anchor-reference={reveal ? 'revealed' : 'hidden'}
      >
        <p className={styles.tag}>
          Withheld source plane 8 · {state.scene === 'surface' ? `frame ${fixed + 1}` : 'frame 17'}
        </p>
        <div className={styles.grid}>
          <Panel
            image={reveal ? ref.image : neutral}
            output={state.output > 0.5 ? one.withheld_plane8_mesh_sections[fixed] : undefined}
            reference={ref.boundary}
            referenceVisible={reveal}
            label="Saved mesh section on an unprovided direction"
          />
          <MeshProjection condition="one" frame={fixed} />
        </div>
        <div className={styles.explain}>
          <strong>Four measured directions → interpolated cavity surface</strong>
          <p>
            Planes 1, 10, 19 and 28 are input; plane 8 is withheld. The saved mesh has 4,538
            vertices and 9,072 faces at each frame. Shared indices do not track myocardial tissue.
          </p>
          {reveal && (
            <p>
              Gold is reader-only source annotation. The dense curve fits source views, including
              withheld directions.
            </p>
          )}
        </div>
      </div>
    );
  }
  if (state.scene === 'comparison') {
    const a = selected['input-28-17'],
      b = selected['input-28-25'];
    return (
      <div
        className={styles.root}
        data-cardiac-anchor-scene={state.scene}
        data-cardiac-anchor-frame="17,25"
        data-cardiac-anchor-condition="one,two"
        data-cardiac-anchor-reference={reveal ? 'revealed' : 'hidden'}
      >
        <p className={styles.tag}>Native input plane 28 · selected frames</p>
        <div className={styles.grid}>
          <Panel
            image={anchorSource.views[3].frames[16]}
            output={one.input_mask_boundaries[3][16]}
            reference={a.boundary}
            referenceVisible={reveal}
            label="Frame 17 · one anchor · tracked"
          />
          <Panel
            image={anchorSource.views[3].frames[16]}
            output={two.input_mask_boundaries[3][16]}
            reference={a.boundary}
            referenceVisible={reveal}
            label="Frame 17 · two anchors · supplied exact mask"
          />
          <Panel
            image={anchorSource.views[3].frames[24]}
            output={one.input_mask_boundaries[3][24]}
            reference={b.boundary}
            referenceVisible={reveal}
            label="Frame 25 · one anchor · tracked"
          />
          <Panel
            image={anchorSource.views[3].frames[24]}
            output={two.input_mask_boundaries[3][24]}
            reference={b.boundary}
            referenceVisible={reveal}
            label="Frame 25 · two anchors · tracked"
          />
        </div>
      </div>
    );
  }
  return (
    <div
      className={styles.root}
      data-cardiac-anchor-scene={state.scene}
      data-cardiac-anchor-frame={frame + 1}
      data-cardiac-anchor-condition={condition}
      data-cardiac-anchor-reference="hidden"
    >
      <p className={styles.tag}>
        FeEcho4D Patient001 · native radial views · filename frame {frame + 1}/30
      </p>
      <div className={styles.grid}>
        {anchorSource.views.map((view, i) => {
          const showAnchor =
            state.helper > 0.5 && (frame === 1 || (condition === 'two' && frame === 16));
          const helper = showAnchor
            ? anchorSource.anchors[condition][`${i}-${frame + 1}`]
            : undefined;
          const output =
            state.output > 0.5
              ? (condition === 'one' ? one : two).input_mask_boundaries[i][frame]
              : undefined;
          return (
            <Panel
              key={i}
              image={view.frames[frame]}
              helper={helper}
              output={output}
              referenceVisible={false}
              label={`Source plane ${view.source_plane_1based} · assumed ${view.assumed_degrees}°`}
            />
          );
        })}
      </div>
    </div>
  );
}

export function CardiacAnchorOutput({ state }: { state: CardiacAnchorState }) {
  const frame = ['reference', 'comparison', 'limits'].includes(state.scene)
      ? 16
      : anchorFrame(state.phase),
    condition = anchorCondition(state.scene);
  const reveal =
    state.reference > 0.5 && ['reference', 'comparison', 'limits'].includes(state.scene);
  const showCurve = state.output > 0.5 && state.scene !== 'comparison';
  return (
    <aside className={`${sharedStyles.storyOutput} ${styles.output}`} data-cardiac-anchor-output>
      <strong>
        {
          {
            inputs: 'Input: four videos + contour anchors',
            anchors: 'One or two supplied contour times',
            'tracking-one': 'One-anchor saved tracking',
            'tracking-two': 'Two-anchor saved tracking',
            surface: 'Saved mesh fills unseen directions',
            reference: 'Withheld source section revealed',
            comparison: 'Matched one- and two-anchor masks',
            limits: 'Development result and limits',
          }[state.scene]
        }
      </strong>
      {state.scene === 'inputs' && (
        <p>
          Four synchronized native radial videos, 30 frames each. Frame 2 contours are supplied;
          frame 17 is added only for the two-anchor variant.
        </p>
      )}
      {state.scene === 'anchors' && (
        <p>
          Blue-grey outlines are supplied frame-2 masks in all four views. No target-time mask or
          mesh is supplied.
        </p>
      )}
      {state.scene === 'tracking-one' && (
        <p>
          Cyan contours and the cavity-volume curve replay the saved DIS output. Evaluator masks
          remain hidden.
        </p>
      )}
      {state.scene === 'tracking-two' && (
        <p>
          The second supplied time is frame 17 in each view. Cyan is the saved two-anchor output;
          evaluator masks remain hidden.
        </p>
      )}
      {state.scene === 'surface' && (
        <p>
          The cyan section and sampled surface come from the same saved one-anchor mesh in native
          millimetres.
        </p>
      )}
      {state.scene === 'reference' && (
        <p>
          Gold is the reader-only source boundary on withheld plane 8, frame 17. The dashed gold
          volume curve is a dense annotation-derived fit, not independent 3D truth.
        </p>
      )}
      {state.scene === 'comparison' && (
        <p>
          First two panels: frame 17, where only the two-anchor mask was supplied. Last two panels:
          frame 25, unsupplied to both. Gold source boundaries are reader-only.
        </p>
      )}
      {showCurve && <Curve condition={condition} frame={frame} reveal={reveal} />}
      {reveal && state.scene === 'limits' && (
        <p>
          On 240 withheld frame/plane pairs per condition, one-anchor DIS: Dice 0.887, volume MAPE
          29.16%, EF error 21.60 pp. Two-anchor DIS: Dice 0.920, MAPE 7.82%, EF error 0.82 pp.
        </p>
      )}
      {state.scene === 'limits' && (
        <small>
          One previously inspected patient; no independent model attempt. Dense fit is
          annotation-derived, not clinical truth.
        </small>
      )}
    </aside>
  );
}
