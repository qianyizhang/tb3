import type { ReactNode } from 'react';
import {
  brainCases,
  brainRefs,
  brainResult,
  brainReveal,
  brainOutput,
  brainSelection,
  brainPlaneFit,
  brainPixel,
  type BrainPlane,
  type TopbrainState,
} from './topbrain-screen';
import styles from './task-visual.module.css';

function Plane({
  p,
  overlay,
  extra,
  x,
  y,
  width,
  height,
  reference = false,
  children,
}: {
  p: BrainPlane;
  overlay?: string;
  extra?: string;
  x: number;
  y: number;
  width: number;
  height: number;
  reference?: boolean;
  children?: ReactNode;
}) {
  const fit = brainPlaneFit(p, width, height);
  return (
    <g transform={`translate(${x + (width - fit.width) / 2} ${y})`}>
      <rect width={fit.width} height={fit.height} fill="#111b19" />
      <image
        data-brain-source-image
        href={p.image}
        width={fit.width}
        height={fit.height}
        preserveAspectRatio="none"
        style={{ imageRendering: 'pixelated' }}
      />
      {overlay && (
        <image
          data-brain-reference-image={reference ? true : undefined}
          data-brain-prediction-image={!reference ? true : undefined}
          href={overlay}
          width={fit.width}
          height={fit.height}
          preserveAspectRatio="none"
          style={{ imageRendering: 'pixelated' }}
        />
      )}
      {extra && (
        <image
          data-brain-extra-image
          href={extra}
          width={fit.width}
          height={fit.height}
          preserveAspectRatio="none"
          style={{ imageRendering: 'pixelated' }}
        />
      )}
      <g transform={`scale(${fit.width / p.width} ${fit.height / p.height})`}>{children}</g>
    </g>
  );
}
function Pair({
  p,
  ref,
  reveal,
  extra,
  title = 'Prediction',
}: {
  p: BrainPlane;
  ref?: string;
  reveal: boolean;
  extra?: string;
  title?: string;
}) {
  return (
    <g>
      <text x="24" y="66">
        {title}
      </text>
      <text x="322" y="66">
        {reveal ? 'Reference' : 'MRA · reference hidden'}
      </text>
      <Plane p={p} overlay={p.prediction} x={24} y={83} width={254} height={254} />
      <Plane
        p={p}
        overlay={reveal ? ref : undefined}
        extra={reveal ? extra : undefined}
        reference
        x={322}
        y={83}
        width={254}
        height={254}
      />
    </g>
  );
}
export function TopbrainScene({ state }: { state: TopbrainState }) {
  const selected = brainSelection(state),
    c = selected.case,
    ref = brainRefs[c.id],
    reveal = brainReveal(state),
    returned = brainOutput(state);
  const cal = brainCases[0].calibration!;
  return (
    <svg
      className={styles.operationCanvas}
      viewBox="0 0 600 420"
      role="img"
      aria-label="Actual TopBrain MRA prediction screening with separate reference and calibration reveals"
      data-brain-scene={state.scene}
      data-brain-case={c.id}
      data-brain-plane={selected.plane}
    >
      {state.scene === 'inputs' ? (
        <g>
          <text x="24" y="32">
            {c.id} · public development MRA
          </text>
          <Plane p={c.overview} x={24} y={57} width={552} height={288} />
          <text x="24" y="374" fontSize="17">
            Full-volume prediction was retained unchanged.
          </text>
          <text x="24" y="405" fontSize="16">
            Shown: author-selected native-axis projection
          </text>
        </g>
      ) : state.scene === 'cohort' ? (
        <g>
          <text x="24" y="32">
            {c.id} · selected source and segmentation
          </text>
          <Pair p={c.overview} ref={ref.overview} reveal={reveal} />
          <text x="24" y="374" fontSize="17">
            Blue: vessel union · class scores use 3D labels
          </text>
          <text x="24" y="405" fontSize="16">
            Depth is collapsed; this is not a contact test.
          </text>
        </g>
      ) : state.scene === 'variants' ? (
        <g>
          <text x="24" y="32">
            {c.id} · third-A2 / third-A3 variant
          </text>
          <Pair p={c.variant!} ref={ref.variant} reveal={reveal} />
          <text x="24" y="366" fontSize="17" fill="#ac7024">
            Orange: third-A2
          </text>
          <text x="314" y="366" fontSize="17" fill="#187d74">
            Teal: third-A3
          </text>
          <text x="24" y="405" fontSize="16">
            Blue: R-ICA / R-A1A2 · full 3D chain checked
          </text>
        </g>
      ) : state.scene === 'contacts' ? (
        <g>
          <text x="24" y="32">
            {c.id} · {c.id === '007' ? 'right' : 'left'} PCA–SCA candidate
          </text>
          <Pair
            p={c.contacts![selected.plane]}
            ref={ref.contacts![selected.plane]}
            reveal={reveal}
          />
          <text x="24" y="364" fontSize="17">
            Native {'ijk'[selected.plane]} = {c.contacts![selected.plane].index}
          </text>
          <text x="24" y="394" fontSize="16">
            Orange: PCA · teal: SCA · physical pixel aspect
          </text>
        </g>
      ) : state.scene === 'parent' ? (
        <g>
          <text x="24" y="32">
            007 · left MCA parent-chain audit
          </text>
          <Pair p={c.parent!} ref={ref.parent} extra={ref.parent_detached} reveal={reveal} />
          <text x="24" y="374" fontSize="17">
            Pink: reference voxels outside parent component
          </text>
          <text x="24" y="405" fontSize="16">
            A reference gap is not automatically a model error.
          </text>
        </g>
      ) : state.scene === 'calibration' ? (
        <g>
          <text x="24" y="32">
            004 · R-SCA gap · native k = {cal.gap_sections[selected.plane].index}
          </text>
          <text x="24" y="66">
            Unchanged prediction
          </text>
          <text x="322" y="66">
            {reveal
              ? 'Reference at additions'
              : returned
                ? 'Saved two-voxel bridge'
                : 'Saved output hidden'}
          </text>
          <Plane
            p={cal.gap_sections[selected.plane]}
            overlay={cal.gap_sections[selected.plane].prediction}
            x={24}
            y={83}
            width={254}
            height={240}
          />
          <Plane
            p={cal.gap_sections[selected.plane]}
            overlay={
              reveal
                ? ref.calibration!.gap_sections[selected.plane]
                : cal.gap_sections[selected.plane].prediction
            }
            reference={reveal}
            extra={returned && !reveal ? cal.gap_sections[selected.plane].added : undefined}
            x={322}
            y={83}
            width={254}
            height={240}
          >
            {returned &&
              reveal &&
              cal.changes_native_ijk
                .filter((v) => v[2] === cal.gap_sections[selected.plane].index)
                .map((v) => {
                  const p = brainPixel(cal.gap_sections[selected.plane], v);
                  return (
                    <rect
                      data-brain-addition-reference
                      key={v.join(',')}
                      x={p[0]}
                      y={p[1]}
                      width="1"
                      height="1"
                      fill="none"
                      stroke="#e7519f"
                      strokeWidth="0.18"
                    />
                  );
                })}
          </Plane>
          <text x="24" y="360" fontSize="17">
            {reveal
              ? 'Right: reference labels; outlined additions'
              : 'Pink: saved additions · no removals'}
          </text>
          <text x="24" y="393" fontSize="16">
            Geometry-only calibration · reference-assisted selection
          </text>
        </g>
      ) : state.scene === 'cpr' ? (
        <g>
          <text x="24" y="32">
            004 · retained BA → R-SCA output
          </text>
          {returned ? (
            <g data-brain-calibration-output>
              <Plane
                p={cal.overview}
                overlay={cal.overview.prediction}
                x={24}
                y={72}
                width={254}
                height={234}
              >
                <polyline
                  points={cal.overview.route_native_ijk
                    .map((v) =>
                      brainPixel(cal.overview, v)
                        .map((n) => n + 0.5)
                        .join(','),
                    )
                    .join(' ')}
                  fill="none"
                  stroke="#e7519f"
                  strokeWidth="1.6"
                />
                {cal.overview.anchors_native_ijk.map((v, i) => {
                  const p = brainPixel(cal.overview, v);
                  return <circle key={i} cx={p[0] + 0.5} cy={p[1] + 0.5} r="2.4" fill="#f4aa3d" />;
                })}
              </Plane>
              <text x="310" y="81" fontSize="17">
                CPR rotation {cal.cpr[selected.plane].angle}°
              </text>
              <image
                data-brain-cpr-image
                href={cal.cpr[selected.plane].png}
                x="310"
                y="143"
                width="265"
                height={(265 * cal.cpr_display_extent_mm[1]) / cal.cpr_display_extent_mm[0]}
                preserveAspectRatio="none"
              />
              <text x="310" y="204" fontSize="15">
                0 → 85.57 mm arc
              </text>
              <text x="310" y="232" fontSize="15">
                Offsets −5 → +5 mm
              </text>
              <text x="24" y="347" fontSize="17">
                Saved route · eight MRA-sampled ribbons
              </text>
            </g>
          ) : (
            <text x="24" y="176">
              Saved calibration outputs remain hidden.
            </text>
          )}
          <text x="24" y="382" fontSize="16">
            A valid export does not establish anatomical difficulty.
          </text>
        </g>
      ) : state.scene === 'admission' ? (
        <g>
          <text x="24" y="32">
            Curation decision
          </text>
          {returned ? (
            <g data-brain-decision>
              {[
                ['Small R-SCA gap', 'Geometry calibration'],
                ['Three PCA–SCA contacts', 'Reference convention unresolved'],
                ['Two preserved variants', 'Potential preservation controls'],
                ['Admitted brain tasks / trials', '0 / 0'],
              ].map(([a, b], i) => (
                <g key={a}>
                  <rect x="24" y={57 + i * 75} width="552" height="64" rx="7" fill="#e5ebe2" />
                  <text x="40" y={81 + i * 75} fontSize="17">
                    {a}
                  </text>
                  <text x="40" y={106 + i * 75} fontSize="18" fontWeight="600">
                    {b}
                  </text>
                </g>
              ))}
            </g>
          ) : (
            <text x="24" y="156">
              Admission output remains hidden.
            </text>
          )}
          <text x="24" y="395" fontSize="16">
            The named-branch repair hypothesis remains untested.
          </text>
        </g>
      ) : (
        <g>
          <text x="24" y="32">
            What would allow a future task?
          </text>
          {[
            'A substantial, reference-supported natural error',
            'Correct parent and named-target identity',
            'Intact or adjudicated absence controls',
            'Frozen task and independent verifier',
          ].map((t, i) => (
            <g key={t}>
              <rect x="24" y={62 + i * 65} width="552" height="50" rx="7" fill="#e5ebe2" />
              <text x="40" y={93 + i * 65} fontSize="18">
                {t}
              </text>
            </g>
          ))}
          <text x="24" y="371" fontSize="17">
            Five selected training scans · no expert adjudication
          </text>
          <text x="24" y="405" fontSize="16">
            No new inference or medical trial in this explanation.
          </text>
        </g>
      )}
    </svg>
  );
}

const titles = {
  inputs: 'A source-screening study',
  cohort: 'Five predictions, zero agent trials',
  variants: 'Preserve a supported variant',
  contacts: 'A contact depends on its definition',
  parent: 'Audit the reference itself',
  calibration: 'A real gap, a simple geometric bridge',
  cpr: 'Inspect saved outputs separately',
  admission: 'No clean hard task admitted',
  limits: 'Keep the original hypothesis open',
};
export function TopbrainOutput({ state }: { state: TopbrainState }) {
  const { case: c } = brainSelection(state),
    ref = brainRefs[c.id],
    reveal = brainReveal(state),
    returned = brainOutput(state);
  return (
    <aside className={styles.storyOutput} data-brain-output={state.scene} data-brain-case={c.id}>
      <h4>{titles[state.scene]}</h4>
      {state.scene === 'inputs' ? (
        <>
          <p>
            Start with full native MRA, untouched released-model predictions and author-side TA36
            labels. Screen for a defensible named-vessel repair, routing or preservation case.
          </p>
          <p>
            004/007/012 were available first. Reference-identified third-artery variants motivated
            adding 006/011.
          </p>
          <small>
            Author selection uses references. Shown crops and projections are teaching views, not
            solver inputs.
          </small>
        </>
      ) : state.scene === 'cohort' ? (
        <>
          <p>
            One released ResEncM fold-4 component; full-volume inference on MPS. No reference crop,
            synthetic defect, official ensemble or pruning.
          </p>
          {reveal ? (
            <table data-brain-scores>
              <thead>
                <tr>
                  <th>MRA</th>
                  <th>Classes</th>
                  <th>Mean Dice</th>
                </tr>
              </thead>
              <tbody>
                {brainCases.map((r) => (
                  <tr key={r.id}>
                    <th>{r.id}</th>
                    <td>{brainRefs[r.id].metrics.length}</td>
                    <td>{brainRefs[r.id].mean_present_label_dice.toFixed(4)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p>Reference comparisons remain hidden.</p>
          )}
          <small>
            Nonbackground labels present in either mask; equal class weights. These selected
            training scans do not measure held-out performance.
          </small>
        </>
      ) : state.scene === 'variants' ? (
        <>
          <p>
            006 and 011 already preserve third-A2/A3. They are potential unchanged controls, not
            failed repair cases.
          </p>
          {reveal ? (
            <table>
              <thead>
                <tr>
                  <th>{c.id}</th>
                  <th>Prediction</th>
                  <th>Reference</th>
                </tr>
              </thead>
              <tbody>
                {['15', '16'].map((k, i) => (
                  <tr key={k}>
                    <th>Third-A{i + 2}</th>
                    <td>{ref.variant_metrics!.prediction.branches[k].voxels}</td>
                    <td>{ref.variant_metrics!.reference.branches[k].voxels}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p>Reference counts remain hidden.</p>
          )}
          <p>
            All selected variant voxels reach R-ICA in both masks using the R-ICA → R-A1A2 →
            third-A2/A3 chain and 26-neighbour connectivity.
          </p>
          <small>Reference-assisted selection; no clinical absence claim.</small>
        </>
      ) : state.scene === 'contacts' ? (
        <>
          <p>
            Three new PCA–SCA face contacts were considered. Their references also touch through
            edges or corners.
          </p>
          {reveal ? (
            <table>
              <thead>
                <tr>
                  <th>{c.id} PCA voxels</th>
                  <th>6-neighbour</th>
                  <th>26-neighbour</th>
                </tr>
              </thead>
              <tbody>
                {(['prediction', 'reference'] as const).map((k) => (
                  <tr key={k}>
                    <th>{k}</th>
                    <td>{ref.contact_metrics![k].contact_voxels_6}</td>
                    <td>{ref.contact_metrics![k].contact_voxels_26}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p>Reference contact measurements remain hidden.</p>
          )}
          <p>
            Counts measure PCA voxels touching SCA, not adjacency pairs. A new face contact is
            insufficient to declare a false anatomical connection.
          </p>
          <small>
            Three calibrated native sections per candidate; no reslicing or clinical adjudication.
          </small>
        </>
      ) : state.scene === 'parent' ? (
        <>
          <p>
            The reference itself has disconnected left-MCA pieces within the stated parent chain.
          </p>
          {reveal ? (
            <p data-brain-parent-count>
              <b>1,479 / 11,322 L-M2 voxels (13.1%)</b> lie outside the selected L-ICA parent
              component. The chain contains four components.
            </p>
          ) : (
            <p>Reference geometry and counts remain hidden.</p>
          )}
          <p>
            Chain: L-ICA-C6-C7, L-M1, L-M2, L-M3. This numerical gap cannot automatically become a
            prediction failure.
          </p>
          <small>
            Pink marks disconnected reference regions in a depth projection; it does not diagnose
            the missing anatomy.
          </small>
        </>
      ) : state.scene === 'calibration' ? (
        <>
          <p>
            004 has a detached 247-voxel R-SCA fragment. Nearest centres are 0.939 mm apart. The
            saved geometry-only bridge reconnects its BA parent.
          </p>
          {returned ? (
            <p data-brain-answer>
              <b>Two additions; zero other full-volume edits.</b> Native voxel centres: (190,306,79)
              and (191,307,79).
            </p>
          ) : (
            <p>Calibration output remains hidden.</p>
          )}
          {reveal ? (
            <p data-brain-reference-detail>
              <b>One addition is labeled R-SCA; one is reference background.</b> Connectivity
              recovery is not exact annotation recovery.
            </p>
          ) : (
            <p>Reference comparison remains hidden.</p>
          )}
          <small>
            Selection used references; repair used prediction geometry. No new solver execution or
            agent score.
          </small>
        </>
      ) : state.scene === 'cpr' ? (
        <>
          <p>
            Saved full labeled mask, 344-point route, eight 344×51 CPR rasters and a target-chain
            PLY mesh.
          </p>
          {returned && (
            <p data-brain-answer>
              <b>85.57 mm route; one watertight mesh component.</b> The surface covers BA + R-SCA
              only.
            </p>
          )}
          {reveal && (
            <p data-brain-reference-detail>
              Nearest saved reference-route distance: p95 <b>0.298 mm</b>, max <b>0.449 mm</b>. Both
              routes use the same author-selected endpoints.
            </p>
          )}
          <small>
            140,352 original-MRA samples checked; max signal difference 0.000102 within float32
            tolerance. Signal is not HU. Display interpolates saved rows along arc only.
          </small>
        </>
      ) : state.scene === 'admission' ? (
        <>
          {returned ? (
            <p data-brain-answer>
              <b>
                {brainResult.segmentation_predictions} segmentation predictions;{' '}
                {brainResult.hard_cases_admitted} hard tasks; {brainResult.coding_agent_trials}{' '}
                coding-agent trials.
              </b>{' '}
              No brain task or verifier was frozen.
            </p>
          ) : (
            <p>The recorded admission decision remains hidden.</p>
          )}
          <p>
            The easy gap, ambiguous contacts and preserved variants did not supply the intended hard
            error/control set.
          </p>
          <small>
            The earlier download failure was resolved. Source curation stopped at its admission
            gate; this is not an agent failure.
          </small>
        </>
      ) : (
        <>
          <p>
            The bounded screen does not show that TopBrain lacks useful repair cases or that brain
            vessels are intrinsically harder.
          </p>
          <p>
            The 0.5 mm interior-disagreement screen can miss thin vessels. Sixteen retained
            candidate regions were not an exhaustive branch review.
          </p>
          <small>
            Reference questions remain unadjudicated. Future task admission needs new evidence; this
            explainer grants no trial authorization.
          </small>
        </>
      )}
      <small data-brain-boundary>
        Reader reference: <span data-brain-reference-state>{reveal ? 'shown' : 'hidden'}</span> ·
        Saved output: <span data-brain-output-state>{returned ? 'shown' : 'hidden'}</span>
      </small>
    </aside>
  );
}
