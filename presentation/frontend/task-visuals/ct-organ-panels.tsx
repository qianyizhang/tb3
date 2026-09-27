import { useId } from 'react';
import {
  ctOrganSource as src,
  ctOrganOutputs as out,
  ctOrganReference as refs,
  ctOrganColors as color,
  ctOrganSelection,
  ctPath,
  type CtPlane,
  type CtPaths,
  type CtOrganState,
} from './ct-organ';
import styles from './task-visual.module.css';
const name = (s: string) => s.replaceAll('_', ' ');
const f = (n: number) => n.toFixed(3);
function Plane({
  plane: p,
  layers = [],
  box,
}: {
  plane: CtPlane;
  layers?: { paths: CtPaths; color: string; dash?: boolean; role: string }[];
  box?: number[];
}) {
  const clip = useId();
  return (
    <svg
      className={styles.ctNative}
      viewBox={`0 0 ${p.width} ${p.height}`}
      role="img"
      aria-label={`Native CT section ${p.index}`}
      data-ct-plane={p.index}
    >
      <defs>
        <clipPath id={clip}>
          <rect width={p.width} height={p.height} />
        </clipPath>
      </defs>
      <image href={p.png} width={p.width} height={p.height} />
      <g clipPath={`url(#${clip})`}>
        {layers.map((l) => (
          <path
            key={l.role}
            data-ct-layer={l.role}
            d={ctPath(l.paths)}
            fill="none"
            stroke={l.color}
            strokeWidth="2"
            vectorEffect="non-scaling-stroke"
            strokeDasharray={l.dash ? '4 3' : undefined}
          />
        ))}
        {box && (
          <rect
            data-ct-layer="box"
            x={box[0]}
            y={box[1]}
            width={box[2]}
            height={box[3]}
            fill="none"
            stroke={color.method}
            strokeWidth="2"
            vectorEffect="non-scaling-stroke"
            strokeDasharray="4 3"
          />
        )}
      </g>
    </svg>
  );
}
function Compare({ state }: { state: CtOrganState }) {
  const v = ctOrganSelection(state);
  return (
    <>
      <h4>
        {String(v.id).padStart(2, '0')} · {name(v.label.name)} · k={v.plane.index}
      </h4>
      <div className={styles.ctCards}>
        {(['medium', 'tool'] as const).map((key) => (
          <article key={key}>
            <b>{key === 'medium' ? 'Astra / medium' : '+ LiteMedSAM'}</b>
            <Plane
              plane={v.plane}
              layers={[
                ...(v.output
                  ? [{ paths: out.masks[String(v.id)][key], color: color[key], role: key }]
                  : []),
                ...(v.reveal
                  ? [
                      {
                        paths: refs.masks[String(v.id)],
                        color: color.reference,
                        dash: true,
                        role: 'reference',
                      },
                    ]
                  : []),
              ]}
            />
            {v.reveal && (
              <strong data-ct-private>
                Whole 3D Dice {f(refs.metrics[key].per_label[v.id - 1].dice)}
              </strong>
            )}
          </article>
        ))}
      </div>
      <p>Same native crop · R → / A ↑ · 1.5 mm/pixel · window −160 to 240 HU</p>
      <p>
        Reader selection: largest reference section; crop includes both outputs.{' '}
        {v.reveal ? 'Private reference revealed.' : 'Private contours and scores hidden.'}
      </p>
    </>
  );
}
function Method({ state }: { state: CtOrganState }) {
  const { method: m } = ctOrganSelection(state),
    tool = state.scene === 'tool';
  const p = src.views[`method-${m.k}`];
  return (
    <>
      <h4>
        Stomach · native k={m.k} ·{' '}
        {tool
          ? m.box_explicit
            ? 'explicit box'
            : 'interpolated box'
          : m.polygon_explicit
            ? 'authored anchor'
            : 'between anchors'}
      </h4>
      <div className={styles.ctCards}>
        <article>
          <b>{tool ? 'Saved prompt + candidate' : 'Raw polygon construction'}</b>
          <Plane
            plane={p}
            box={tool ? m.box : undefined}
            layers={[
              {
                paths: tool ? m.tool_candidate : m.raw_polygon,
                color: tool ? color.tool : color.method,
                dash: !tool,
                role: tool ? 'candidate' : 'raw',
              },
            ]}
          />
        </article>
        <article>
          <b>{tool ? 'After union + cleanup' : 'Final submitted mask'}</b>
          <Plane
            plane={p}
            layers={[
              {
                paths: tool ? m.tool_final : m.baseline_final,
                color: tool ? color.tool : color.medium,
                role: tool ? 'tool' : 'medium',
              },
            ]}
          />
        </article>
      </div>
      <div className={styles.ctSteps}>
        {[235, 236, 237, 238, 239, 240].map((k) => (
          <span key={k} data-active={k === m.k}>
            {k}
            <small>{k === 235 || k === 240 ? 'anchor' : 'between'}</small>
          </span>
        ))}
      </div>
      <p>Six actual CT planes · R → / A ↑ · reader-selected crop · reference hidden</p>
    </>
  );
}
export function CtOrganScene({ state }: { state: CtOrganState }) {
  const v = ctOrganSelection(state);
  return (
    <div
      className={styles.ctScene}
      data-ct-scene={state.scene}
      data-ct-reference={v.reveal ? 'visible' : 'hidden'}
    >
      {['inputs', 'contract'].includes(state.scene) ? (
        <>
          <h4>
            {state.scene === 'inputs'
              ? 'Full CT + ten definitions'
              : 'Ten independent binary masks'}
          </h4>
          <div className={styles.ctInput}>
            <article>
              <Plane plane={src.views.input} />
              <p>
                j=132 · R → / S ↑<br />
                Centre section; full scan supplied
              </p>
            </article>
            <ol>
              {src.labels.map((l) => (
                <li key={l.id}>
                  <code>{l.file}</code> {name(l.name)}
                </li>
              ))}
            </ol>
          </div>
          <p>265 × 265 × 401 native voxels · 1.5 mm isotropic · source RAS affine</p>
        </>
      ) : ['polygon', 'tool'].includes(state.scene) ? (
        <Method state={state} />
      ) : state.scene === 'comparison' ? (
        <>
          <h4>One attempt in each condition · same CT and reference</h4>
          <table className={styles.ctTable} data-ct-private>
            <thead>
              <tr>
                <th>Condition</th>
                <th>Semantic Dice</th>
                <th>Matched Dice</th>
              </tr>
            </thead>
            <tbody>
              {(['xhigh', 'medium', 'sol', 'tool'] as const).map((key) => (
                <tr key={key}>
                  <td>
                    {
                      {
                        xhigh: 'Astra/xhigh',
                        medium: 'Astra/medium',
                        sol: 'Sol/xhigh',
                        tool: 'Medium + tool',
                      }[key]
                    }
                  </td>
                  <td>{f(refs.metrics[key].semantic_macro_dice)}</td>
                  <td>{f(refs.metrics[key].matched_macro_dice)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p>
            Each mean weights all ten organs equally. Matched Dice permits optimal one-to-one
            relabelling.
          </p>
          <p>
            Sol: 0.329 → 0.349 after matching. Relabelling alone does not repair the contours or
            locations.
          </p>
          <p>
            Tool arm changes skill + instruction + runtime. These are descriptive single-case
            endpoints.
          </p>
        </>
      ) : state.scene === 'slices' ? (
        <>
          <h4>Compare unchanged outputs on identical baseline planes</h4>
          <table className={styles.ctTable} data-ct-private>
            <thead>
              <tr>
                <th>Baseline-defined set</th>
                <th>Pairs</th>
                <th>Medium</th>
                <th>+ Tool</th>
              </tr>
            </thead>
            <tbody>
              {(['authored_polygon', 'interpolated_shape'] as const).map((key) => (
                <tr key={key}>
                  <td>{key === 'authored_polygon' ? 'Authored anchors' : 'Between anchors'}</td>
                  <td>{refs.matched_macro[key].n}</td>
                  <td>{f(refs.matched_macro[key].baseline)}</td>
                  <td>{f(refs.matched_macro[key].tool)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p>
            Organ-balanced conditional Dice; GT-present planes only. Nine outside-extent pairs are
            separate.
          </p>
          <p>
            Own-anchor scores are not uniformly better. Plane selection and cleanup complicate the
            comparison.
          </p>
          <p>Display ≠ authoring ≠ repeat inference ≠ corrected contour.</p>
        </>
      ) : state.scene === 'limits' ? (
        <>
          <h4>Localize · delineate · name · complete · review</h4>
          <dl className={styles.ctLimits}>
            <div>
              <dt>Useful result</dt>
              <dd>
                The tool condition improves 7/10 organs; three regress. Ten matched identities
                remain correct for both Astra/medium outputs.
              </dd>
            </div>
            <div>
              <dt>Reference boundary</dt>
              <dd>
                Human-reviewed research masks, with residual source uncertainty. No new clinical
                adjudication.
              </dd>
            </div>
            <div>
              <dt>Scope</dt>
              <dd>
                One selected public case; one attempt per condition. Training overlap unknown. No
                population ranking or causal tool benefit.
              </dd>
            </div>
            <div>
              <dt>Evidence</dt>
              <dd>
                8 saved model/control scores replayed; 40 organ values independently reproduced. No
                new inference.
              </dd>
            </div>
          </dl>
        </>
      ) : (
        <Compare state={state} />
      )}
    </div>
  );
}
export function CtOrganOutput({ state }: { state: CtOrganState }) {
  const v = ctOrganSelection(state);
  return (
    <div className={styles.operationOutput} data-ct-output={state.scene}>
      <strong>
        {
          {
            inputs: 'Locations and contours must be found',
            contract: 'Preserve separate masks',
            polygon: 'Mask geometry is interpolated',
            tool: 'Boxes are interpolated; masks are inferred',
            output: 'Submitted geometry and name',
            reference: 'Compare to the private research reference',
            regressions: 'A mean gain hides local regressions',
            inventory: 'All ten organs remain visible',
            comparison: 'Geometry and naming are separate',
            slices: 'Fix the plane set before comparing',
            limits: 'Supported conclusions and limits',
          }[state.scene]
        }
      </strong>
      {state.scene === 'inputs' ? (
        <>
          <p>The solver receives CT, target definitions and native-grid conventions.</p>
          <p>No supplied masks, organ locations, source identity or reference scores.</p>
          <p>
            Standalone conditions use ordinary scientific libraries. The separate tool condition
            adds a skill and segmenter.
          </p>
        </>
      ) : state.scene === 'contract' ? (
        <>
          <p>01.nii.gz … 10.nii.gz plus method.md.</p>
          <p>Binary values; unchanged shape and affine; anatomical right/left from RAS.</p>
          <p>
            Independent masks may overlap. Stomach, gallbladder and duodenum include their contents.
          </p>
          <p>Reference overlaps motivate this format; no exclusive label fusion.</p>
        </>
      ) : state.scene === 'polygon' ? (
        <>
          <p>Saved stomach polygons at k235 and k240 define signed-distance fields.</p>
          <p>
            Four interior planes interpolate those fields. The displayed raw contours are
            reconstructed from exact saved coordinates.
          </p>
          <p>
            Final masks also use image thresholds, smoothing and morphology. This is a numerical
            stage comparison.
          </p>
        </>
      ) : state.scene === 'tool' ? (
        <>
          <p>The agent assigns organ IDs and chooses boxes from CT.</p>
          <p>
            Each actual slice is windowed, cropped and resized for LiteMedSAM. Explicit and
            interpolated boxes both trigger image-conditioned inference.
          </p>
          <p>
            The saved candidate is then united with other batches and cleaned up. No inference is
            run for this animation.
          </p>
        </>
      ) : ['output', 'reference', 'regressions', 'inventory'].includes(state.scene) ? (
        <>
          <p>
            <code>{v.label.file}</code> · {name(v.label.name)}
          </p>
          <p>{v.label.convention}.</p>
          {v.reveal ? (
            <>
              <p data-ct-private>
                Medium {f(refs.metrics.medium.per_label[v.id - 1].dice)} → tool{' '}
                {f(refs.metrics.tool.per_label[v.id - 1].dice)}.
              </p>
              <p>Full 3D organ Dice; this selected 2D view illustrates the retained result.</p>
              {v.id === 8 ? (
                <p>
                  Post-hoc prompts cover only 23.7% of reference voxels. A box is not a hard output
                  constraint or score ceiling.
                </p>
              ) : v.id === 4 ? (
                <p>
                  Post-hoc prompt coverage is 65.7%; localization remains an upstream limitation.
                </p>
              ) : (
                <p>Contours and whole-organ scores answer different levels of the comparison.</p>
              )}
            </>
          ) : (
            <p>
              Only saved predictions are shown. The private reference and all scores remain hidden.
            </p>
          )}
        </>
      ) : state.scene === 'comparison' ? (
        <>
          <p>Semantic Dice pairs each output with its named organ.</p>
          <p>Matched Dice asks how much overlap is recoverable by renaming the ten masks.</p>
          <p>Astra medium → tool: 0.73419 → 0.75697; +0.02278, seven gains and three losses.</p>
          <p>Single attempts do not establish a model ranking or causal benefit.</p>
        </>
      ) : state.scene === 'slices' ? (
        <>
          <p>One organ–slice pair means one organ on one native axial plane.</p>
          <p>
            The same baseline-defined 119 anchor and 372 between-anchor pairs are scored in both
            outputs.
          </p>
          <p>
            These conditional scores weight organs equally. They do not replace frozen whole-volume
            scores.
          </p>
          <p>Correlated planes are not independent patients.</p>
        </>
      ) : (
        <>
          <p>Saved evidence, not a fresh experiment.</p>
          <p>
            Localization, contouring, identity, interpolation and tool orchestration need separate
            evidence.
          </p>
          <p>Further cohort expansion would require its own protocol.</p>
        </>
      )}
    </div>
  );
}
