import { useId } from 'react';
import {
  aneurysmCases as cases,
  aneurysmOutputs as outputs,
  aneurysmReference as refs,
  aneurysmColors as colors,
  aneurysmSelection,
  aneurysmPixel,
  aneurysmPath,
  type AneurysmCase,
  type AneurysmState,
} from './aneurysm';
import styles from './task-visual.module.css';
const axes = ['i', 'j', 'k'];
function Plane({
  caseId,
  name,
  reference = false,
  output = false,
}: {
  caseId: AneurysmCase;
  name: string;
  reference?: boolean;
  output?: boolean;
}) {
  const p = cases[caseId].views[name],
    clip = useId(),
    r = refs.views[`${caseId}/${name}`];
  const scale = Math.min(236 / p.extent_mm[0], 200 / p.extent_mm[1]);
  const w = p.extent_mm[0] * scale,
    h = p.extent_mm[1] * scale,
    x = (240 - w) / 2,
    y = (204 - h) / 2;
  return (
    <article data-aneurysm-plane={`${caseId}/${name}`} data-native-index={p.index ?? 'mip'}>
      <b>
        {p.kind === 'mip'
          ? `MIP · ${axes[p.axis]} [${p.bounds[2 * p.axis]},${p.bounds[2 * p.axis + 1]})`
          : `${axes[p.axis]} = ${p.index}`}{' '}
        · {cases[caseId].axes[p.u_axis]} → / {cases[caseId].axes[p.v_axis]} ↑
      </b>
      <svg
        className={styles.aneurysmImage}
        viewBox="0 0 240 204"
        role="img"
        aria-label={`${caseId.toUpperCase()} ${p.kind}, native ${axes[p.axis]} ${p.index ?? 'projection'}; ${p.selection}`}
      >
        <defs>
          <clipPath id={clip}>
            <rect x={x} y={y} width={w} height={h} />
          </clipPath>
        </defs>
        <image href={p.png} x={x} y={y} width={w} height={h} preserveAspectRatio="none" />
        <g clipPath={`url(#${clip})`}>
          <svg
            x={x}
            y={y}
            width={w}
            height={h}
            viewBox={`0 0 ${p.width} ${p.height}`}
            preserveAspectRatio="none"
          >
            {reference && (
              <g data-aneurysm-private>
                <path
                  d={aneurysmPath(r.accepted)}
                  fill="none"
                  stroke={colors.accepted}
                  strokeWidth="1.5"
                  strokeDasharray="2 3"
                  vectorEffect="non-scaling-stroke"
                />
                <path
                  d={aneurysmPath(r.weak)}
                  fill="none"
                  stroke={colors.weak}
                  strokeWidth="1.6"
                  strokeDasharray="6 3"
                  vectorEffect="non-scaling-stroke"
                />
              </g>
            )}
            {output &&
              outputs.cases[caseId].answer.aneurysms.map((q, i) => {
                const pos = aneurysmPixel(p, q, cases[caseId].spacing_mm);
                return (
                  <g
                    key={i}
                    data-aneurysm-point
                    data-depth-offset={pos.offset_mm}
                    transform={`translate(${pos.x} ${pos.y})`}
                  >
                    <path
                      d="M-2.2 0H2.2M0-2.2V2.2"
                      stroke={colors.output}
                      strokeWidth="2"
                      vectorEffect="non-scaling-stroke"
                    />
                  </g>
                );
              })}
          </svg>
        </g>
      </svg>
      <small>{p.bounds.map((n, i) => (i % 2 ? `${n})` : `[${n},`)).join(' ')} · native i/j/k</small>
      <small>
        Window [{p.window[0]},{p.window[1].toFixed(0)}] · {p.volume}
      </small>
    </article>
  );
}
function Planes({
  caseId,
  names,
  reference = false,
  output = false,
}: {
  caseId: AneurysmCase;
  names: string[];
  reference?: boolean;
  output?: boolean;
}) {
  return (
    <div className={styles.aneurysmCards} data-columns={names.length}>
      {names.map((name) => (
        <Plane key={name} caseId={caseId} name={name} reference={reference} output={output} />
      ))}
    </div>
  );
}
function Outcomes() {
  return (
    <table className={styles.aneurysmTable} data-aneurysm-private>
      <thead>
        <tr>
          <th>Case</th>
          <th>TP / FP / FN</th>
          <th>Interpretation</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>N01</td>
          <td>0 / 0 / 1</td>
          <td>Reference miss</td>
        </tr>
        <tr>
          <td>N02</td>
          <td>1 / 0 / 0</td>
          <td>Matching point</td>
        </tr>
        <tr>
          <td>N03</td>
          <td>0 / 0 / 0</td>
          <td>Source-assisted negative</td>
        </tr>
      </tbody>
    </table>
  );
}
export function AneurysmScene({ state: s }: { state: AneurysmState }) {
  const v = aneurysmSelection(s);
  return (
    <section
      className={styles.aneurysmScene}
      data-aneurysm-scene={s.scene}
      data-aneurysm-reference={v.reference ? 'visible' : 'hidden'}
    >
      {s.scene === 'inputs' && (
        <>
          <h4>One complete examination, two image versions</h4>
          <Planes caseId="n02" names={['original', 'overview-2']} />
          <p>
            Original and source skull-stripped MRA · same 512 × 512 × 140 native grid. Full-volume
            projections; no location supplied.
          </p>
        </>
      )}
      {s.scene === 'projections' && (
        <>
          <h4>Three projections collapse three different depth axes</h4>
          <Planes caseId="n02" names={['overview-0', 'overview-1', 'overview-2']} />
          <p>
            Maximum intensity along each full axis. Bright structures at different depths may
            overlap.
          </p>
        </>
      )}
      {s.scene === 'slabs' && (
        <>
          <h4>Fixed slabs cover the entire scan</h4>
          <Planes caseId="n02" names={[`slab-${v.slab}`]} />
          <p>
            Slab {v.slab + 1} / 12 · equal axial partitions · native pixels · supplied whole-scan
            policy.
          </p>
        </>
      )}
      {s.scene === 'candidate' && (
        <>
          <h4>N02: inspect the candidate in three planes</h4>
          <Planes caseId="n02" names={['candidate-0', 'candidate-1', 'candidate-2']} />
          <p>
            Selected sections reconstructed from step 14; generated and displayed at steps 14–15.
            This crop was chosen by the agent.
          </p>
        </>
      )}
      {s.scene === 'depth' && (
        <>
          <h4>A projection candidate must persist across depth</h4>
          <Planes caseId="n02" names={[`depth-${v.depth}`]} />
          <p>
            Native k = {v.depth} · seven selected sections from the original axial montage. Discrete
            slices, no image interpolation.
          </p>
        </>
      )}
      {['outputs', 'reference'].includes(s.scene) && (
        <>
          <h4>
            {v.reference
              ? 'N02: the point matches a coarse region'
              : 'N02: one returned native-grid point'}
          </h4>
          <Planes
            caseId="n02"
            names={['point-0', 'point-1', 'point-2']}
            reference={v.reference}
            output={v.output}
          />
          <p>
            {v.reference
              ? 'Weak enclosing region + frozen 1 mm acceptance. Neither outline is an exact clinical sac boundary.'
              : 'Reader sections through [312,213,94]. Cyan crosses mark the same voxel; reference and scores remain hidden.'}
          </p>
        </>
      )}
      {s.scene === 'miss' && (
        <>
          <h4>N01: an empty answer misses the released region</h4>
          <Planes
            caseId="n01"
            names={['reference-0', 'reference-1', 'reference-2']}
            reference={v.reference}
          />
          <p>
            Post-result reference-centred reader views, not solver inputs. Saved answer:{' '}
            {`{"aneurysms": []}`}.
          </p>
        </>
      )}
      {s.scene === 'coverage' && (
        <>
          <h4>N01: final close-ups focused elsewhere</h4>
          <Planes caseId="n01" names={['final-candidate-0', 'final-candidate-1']} />
          <p>
            Selected step-28 axial sections near [192,248,74] and [166,309,100]; viewed at step 29.
            They do not contain the reference region.
          </p>
        </>
      )}
      {s.scene === 'negative' && (
        <>
          <h4>N03: negative answer after source identification</h4>
          <div className={styles.aneurysmFlow}>
            <article>
              <b>1 · Image review</b>
              <p>Native sections, rotated projections and width checks</p>
            </article>
            <article>
              <b>2 · Public lookup</b>
              <p>
                Step 42: manual-mask inventory
                <br />
                Step 48: source array equality
              </p>
            </article>
            <article>
              <b>3 · Submit</b>
              <code>{'{"aneurysms": []}'}</code>
              <p>No frozen answer before lookup</p>
            </article>
          </div>
          <p>
            Lookup was permitted. The original pass remains; its evidence basis is source-assisted
            exclusion.
          </p>
        </>
      )}
      {s.scene === 'matching' && (
        <>
          <h4>One-to-one region matching; extra points fail</h4>
          <table className={styles.aneurysmTable} data-aneurysm-private>
            <thead>
              <tr>
                <th>Saved or diagnostic answer</th>
                <th>Positive N01/N02</th>
                <th>Negative N03</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Oracle regions</td>
                <td>Pass</td>
                <td>Empty list passes</td>
              </tr>
              <tr>
                <td>Valid empty list</td>
                <td>Miss</td>
                <td>Pass</td>
              </tr>
              <tr>
                <td>Extra corner point</td>
                <td>False positive</td>
                <td>False positive</td>
              </tr>
              <tr>
                <td>{'{}'} no-op</td>
                <td>Invalid schema</td>
                <td>Invalid schema</td>
              </tr>
            </tbody>
          </table>
          <p>
            Round with floor(x + 0.5). Each accepted region can match once; every reference must
            match and no detection may remain unmatched.
          </p>
          <p>V1 failed verifier setup; v2 repaired packaging. No model attempted v1.</p>
        </>
      )}
      {s.scene === 'limits' && (
        <>
          <h4>Three workflow outcomes, three evidence boundaries</h4>
          <Outcomes />
          <div className={styles.aneurysmFlow}>
            <article>
              <b>Supported locally</b>
              <p>Native input fidelity, saved-point matching and observed source exposure</p>
            </article>
            <article>
              <b>Still unresolved</b>
              <p>Clinical visibility/completeness, N01 failure cause and training overlap</p>
            </article>
          </div>
          <p>
            One attempt per selected case. No population accuracy, causal heuristic benefit,
            clinical diagnosis or precise segmentation claim.
          </p>
        </>
      )}
    </section>
  );
}
export function AneurysmOutput({ state: s }: { state: AneurysmState }) {
  const v = aneurysmSelection(s),
    c = cases[v.caseId];
  return (
    <aside className={styles.aneurysmAside} data-aneurysm-output>
      <b>{v.caseId.toUpperCase()} · retained TOF-MRA pilot</b>
      {['candidate', 'depth', 'outputs', 'reference', 'miss', 'coverage', 'negative'].includes(
        s.scene,
      ) && <Plane caseId={v.caseId} name="overview-2" />}
      {s.scene === 'slabs' ? (
        <>
          <p>
            Every native k slice belongs to exactly one supplied slab. A slab still collapses depth.
          </p>
          <p>
            Three full MIPs and twelve slabs are starting views; the full arrays remain available.
          </p>
        </>
      ) : (
        <p>
          {c.shape.join(' × ')} voxels
          <br />
          {c.spacing_mm.map((x) => x.toFixed(5)).join(' / ')} mm
        </p>
      )}
      {v.output && (
        <>
          <b>Saved answer</b>
          <pre data-aneurysm-answer>{JSON.stringify(outputs.cases[v.caseId].answer)}</pre>
        </>
      )}
      {s.scene === 'reference' && v.reference && (
        <div data-aneurysm-private>
          <p>
            <strong>{refs.n02_point_to_centroid_mm.toFixed(4)} mm</strong> from the weak region's
            centroid; the point is inside that region.
          </p>
          <p>Centroid distance is not the scoring endpoint.</p>
        </div>
      )}
      {s.scene === 'coverage' && (
        <p data-aneurysm-private>
          Reference centre [166,273,84]. Earlier generated views intersected it; that does not prove
          attention or recognition.
        </p>
      )}
      {s.scene === 'negative' && (
        <p data-aneurysm-private>
          Public sub-000 identity and annotation inventory were available before the answer. This is
          not an isolated image-only negative.
        </p>
      )}
      {s.scene === 'matching' && (
        <p>
          Fresh replay: nine saved grades match. Positive weak-region expansions independently
          reproduce the frozen scorer.
        </p>
      )}
      <p>
        {v.reference
          ? 'Reference revealed for readers; it was not a solver image input.'
          : 'Weak reference regions and accuracy values are hidden.'}
      </p>
      <small>
        Public OpenNeuro ds003949 · CC0 · direct source pixels. Selected crops are labelled; no
        reconstructed vessel mesh.
      </small>
    </aside>
  );
}
