import {
  vesselCases as cases,
  vesselReference as refs,
  vesselReveal,
  vesselOutput,
  vesselSliceIndex,
  vesselNodePixel,
  vesselVisibleNodes,
  vesselColors as colors,
  type VesselPlane,
  type VesselSourceState,
} from './vessel-source';
import styles from './task-visual.module.css';
function Plane({
  plane,
  overlay,
  x,
  y,
  width,
}: {
  plane: VesselPlane;
  overlay?: string;
  x: number;
  y: number;
  width: number;
}) {
  const height = (width * plane.height) / plane.width;
  return (
    <g>
      <rect x={x} y={y} width={width} height={height} fill="#101713" />
      <image href={plane.png} x={x} y={y} width={width} height={height} />
      {overlay && (
        <image
          data-vessel-reference-image
          href={overlay}
          x={x}
          y={y}
          width={width}
          height={height}
        />
      )}
    </g>
  );
}
const short = (id: string) => id.slice(-3);
export function VesselSourceScene({ state }: { state: VesselSourceState }) {
  const reveal = vesselReveal(state),
    result = vesselOutput(state),
    index = vesselSliceIndex(state.scan),
    c = cases[1],
    ref = refs[1];
  return (
    <svg
      className={styles.operationCanvas}
      viewBox="0 0 600 420"
      role="img"
      aria-label="Actual TopCoW MRA source projections and native sections with separately revealed annotations"
    >
      {['sources', 'states'].includes(state.scene) ? (
        <g>
          {cases.map((row, i) => {
            const x = 40 + (i % 2) * 300,
              y = 50 + Math.floor(i / 2) * 200;
            return (
              <g key={row.id}>
                <text data-vessel-state-label={reveal ? true : undefined} x={x} y={y - 15}>
                  {short(row.id)}
                  {reveal
                    ? ` · L${refs[i].edges['L-Pcom'] ? '+' : '−'} / R${refs[i].edges['R-Pcom'] ? '+' : '−'}`
                    : ' · MRA'}
                </text>
                <Plane
                  plane={row.mip}
                  overlay={reveal ? refs[i].mip_overlay : undefined}
                  x={x}
                  y={y}
                  width={185}
                />
              </g>
            );
          })}
        </g>
      ) : state.scene === 'inspect' ? (
        <g>
          <text x="25" y="32">
            007 · native slice k = {c.native[index].k}
          </text>
          <text x="25" y="78">
            MRA
          </text>
          <text x="325" y="78">
            {reveal ? 'Reference overlay' : 'Reference hidden'}
          </text>
          <Plane plane={c.native[index]} x={25} y={95} width={250} />
          <Plane
            plane={c.native[index]}
            overlay={reveal ? ref.native_overlays[index] : undefined}
            x={325}
            y={95}
            width={250}
          />
          <text x="25" y="320" fontSize="17">
            Same grid · fixed window · 0.6 mm steps
          </text>
          <text x="25" y="357" fontSize="16">
            Native oblique sections · no resampling
          </text>
          <text x="25" y="394" fontSize="16">
            Author view selected from annotation extent
          </text>
        </g>
      ) : state.scene === 'contacts' ? (
        <g>
          <text x="25" y="32">
            007 · source mask contact check
          </text>
          <Plane
            plane={c.mip}
            overlay={reveal ? ref.mip_overlay : undefined}
            x={25}
            y={58}
            width={260}
          />
          <text x="315" y="94">
            26-neighbour
          </text>
          <text x="315" y="125">
            label contact
          </text>
          {reveal &&
            (['right', 'left'] as const).map((side, i) => (
              <g key={side}>
                <rect x="315" y={156 + i * 61} width="16" height="16" fill={colors[side]} />
                <text x="344" y={171 + i * 61}>
                  {side === 'right' ? 'R' : 'L'}: ICA ↔ PCA
                </text>
              </g>
            ))}
          <text x="25" y="313" fontSize="17">
            Measured on the 3D mask, not this MIP.
          </text>
          <text x="25" y="353" fontSize="16">
            A label contact is not an adjudicated vessel.
          </text>
          <text x="25" y="393" fontSize="16">
            Binary union can hide class-label mistakes.
          </text>
        </g>
      ) : state.scene === 'nodes' ? (
        <g>
          <text x="25" y="32">
            007 · mask-derived graph nodes
          </text>
          <Plane plane={c.mip} x={75} y={58} width={430} />
          {reveal &&
            vesselVisibleNodes(1).map((n) => {
              const p = vesselNodePixel(c, n),
                scale = 430 / c.mip.width;
              return (
                <circle
                  data-vessel-node
                  key={n.id}
                  cx={75 + (p.u + 0.5) * scale}
                  cy={58 + (p.v + 0.5) * scale}
                  r="4"
                  fill="none"
                  stroke={colors.node}
                  strokeWidth="1.6"
                />
              );
            })}
          <text x="25" y="382" fontSize="16">
            Same native affine · projected through depth
          </text>
          <text x="25" y="414" fontSize="15">
            Circles: nodes inside the source box only
          </text>
        </g>
      ) : state.scene === 'contract' ? (
        <g>
          <text x="25" y="35">
            Proposed future solver packet
          </text>
          {['MRA region', 'Proposed binary mask', 'Broad editable region'].map((t, i) => (
            <g key={t}>
              <rect x="25" y={58 + i * 60} width="550" height="49" rx="7" fill="#e7ebe3" />
              <text x="43" y={89 + i * 60}>
                {t}
              </text>
            </g>
          ))}
          <text x="25" y="274">
            ↓ corrected_mask.nii.gz
          </text>
          <text x="25" y="317">
            Same grid · preserve outside region
          </text>
          <text x="25" y="362" fontSize="17">
            Reconnect / disconnect / leave unchanged
          </text>
          <text x="25" y="406" fontSize="16">
            No natural faulty prediction admitted yet
          </text>
        </g>
      ) : state.scene === 'admission' ? (
        <g>
          <text x="25" y="35">
            BR-025 · curation output
          </text>
          {result ? (
            <g data-vessel-result>
              {result.source_candidates.map((r, i) => (
                <g key={r.id}>
                  <rect x="25" y={60 + i * 55} width="550" height="44" rx="6" fill="#e7ebe3" />
                  <text x="43" y={90 + i * 55}>
                    {short(r.id)} · source_candidate_only
                  </text>
                </g>
              ))}
              <text x="25" y="324">
                {result.admitted_defect_fixtures} admitted defects · {result.local_model_trials}{' '}
                model trials
              </text>
            </g>
          ) : (
            <text x="25" y="145">
              Curation records withheld until reveal
            </text>
          )}
          <text x="25" y="371" fontSize="17">
            Prediction, adjudication and controls pending
          </text>
          <text x="25" y="406" fontSize="16">
            Later synthetic feasibility is a separate study
          </text>
        </g>
      ) : (
        <g>
          <text x="25" y="35">
            What this source screen establishes
          </text>
          {[
            'Pinned public sources',
            'Matching image / mask grids',
            'Annotation configurations',
            'Explicit task-admission gaps',
          ].map((t, i) => (
            <g key={t}>
              <rect x="25" y={61 + i * 65} width="550" height="50" rx="6" fill="#e7ebe3" />
              <text x="43" y={94 + i * 65}>
                {t}
              </text>
            </g>
          ))}
          <text x="25" y="366" fontSize="17">
            No clinical absence or model difficulty claim
          </text>
          <text x="25" y="407" fontSize="16">
            Graph edges and anatomy remain unadjudicated
          </text>
        </g>
      )}
    </svg>
  );
}
export function VesselSourceOutput({ state }: { state: VesselSourceState }) {
  const reveal = vesselReveal(state),
    result = vesselOutput(state);
  return (
    <aside className={styles.storyOutput} data-vessel-output={state.scene}>
      {state.scene === 'sources' ? (
        <>
          <h4>Source study, before a repair task</h4>
          <p>
            Four complete public training MRA volumes selected after screening 12 edge-label files.
            Shown: maximum-intensity projections through the supplied Circle of Willis boxes.
          </p>
          <p>
            The author also has masks, boxes, edge labels and mask-derived graphs. These are
            curation inputs, not a frozen solver packet.
          </p>
          <small>
            Each projection is fitted independently and collapses depth. CTA labels were checked;
            CTA images were not reviewed.
          </small>
        </>
      ) : state.scene === 'states' ? (
        <>
          <h4>Reveal source annotation states</h4>
          <span data-vessel-reference>{reveal ? 'revealed' : 'hidden'}</span>
          {reveal ? (
            <table>
              <thead>
                <tr>
                  <th>Case</th>
                  <th>Candidate role</th>
                </tr>
              </thead>
              <tbody>
                {[
                  'Unchanged right-only',
                  'Possible broken connection',
                  'Possible false bridge',
                  'Unchanged left-only',
                ].map((v, i) => (
                  <tr key={v}>
                    <th>{short(cases[i].id)}</th>
                    <td>{v}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p>Labels and candidate roles remain hidden until the reader reveal.</p>
          )}
          <p>
            Pcom means posterior communicating artery. Plus means present; minus means absent in the
            source label. Neither is a new diagnosis.
          </p>
          <small>
            Orange: right Pcom. Teal: left Pcom. Blue: other vessel annotations. No defective
            prediction is shown.
          </small>
        </>
      ) : state.scene === 'inspect' ? (
        <>
          <h4>Inspect the source in depth</h4>
          <p>
            Case 007, native slices 104–117. Both panels use the same crop, scale and fixed
            intensity window. Only the viewed section changes.
          </p>
          <p>
            Extent comes from both annotated Pcoms plus one slice on each side. This privileged
            author view is not a fair search packet.
          </p>
          <small>
            Oblique native axes have L/P/S orientation codes. Pixel coordinates and the full NIfTI
            affine are retained in RAS+ millimetres.
          </small>
        </>
      ) : state.scene === 'contacts' ? (
        <>
          <h4>Topology checked on source labels</h4>
          {reveal && (
            <table>
              <thead>
                <tr>
                  <th>007 label</th>
                  <th>Voxels</th>
                  <th>Components</th>
                </tr>
              </thead>
              <tbody>
                {(['right', 'left'] as const).map((s) => (
                  <tr key={s}>
                    <th>{s} Pcom</th>
                    <td>{refs[1].pcoms[s].voxel_count}</td>
                    <td>{refs[1].pcoms[s].components_26}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          <p>
            Each present Pcom label in all four cases is one 26-connected component and touches its
            expected internal carotid (ICA) and posterior cerebral (PCA) labels.
          </p>
          <small>
            Corner contact counts under this neighbourhood. Neither a projected crossing nor a
            connected binary union proves the intended local anatomical attachment.
          </small>
        </>
      ) : state.scene === 'nodes' ? (
        <>
          <h4>Coordinates corroborate alignment</h4>
          {reveal && (
            <p data-vessel-node-summary>
              <b>007:</b> {refs[1].node_entries.length} node entries; largest distance to a
              foreground voxel centre <b>{refs[1].node_distances_mm.max.toFixed(3)} mm</b>.
            </p>
          )}
          <p>
            All 146 entries across four cases reproduce the retained alignment screen. Shared
            boundary nodes recur under different labels; the drawing deduplicates IDs and clips to
            the source box.
          </p>
          <p>
            Stored node coordinates use the same NIfTI RAS+ frame. No extra x/y flip or independent
            fitting is applied.
          </p>
          <small>
            Graphs derive from the masks. These distances do not validate all VTP edges or provide
            independent anatomical truth.
          </small>
        </>
      ) : state.scene === 'contract' ? (
        <>
          <h4>Three legitimate outcomes</h4>
          <p>
            The proposed repair may reconnect a broken vessel, remove a false bridge, or preserve a
            valid absence. Connecting everything must fail.
          </p>
          <p>
            Keep exact defect coordinates, answer labels, graphs and ground-truth-shaped corridors
            out of solver inputs.
          </p>
          <small>
            Evaluate local attachment, physical geometry, collateral edits and unchanged regions
            separately. Global Dice alone can conceal a missing small connection.
          </small>
        </>
      ) : state.scene === 'admission' ? (
        <>
          <h4>Source candidates, not accepted defects</h4>
          {result ? (
            <div data-vessel-answer>
              <p>
                <b>
                  {result.source_candidates.length} source candidates ·{' '}
                  {result.admitted_defect_fixtures} defect fixtures · {result.local_model_trials}{' '}
                  trials
                </b>
              </p>
              <p>Natural faulty prediction: absent. Numeric verifier thresholds: not frozen.</p>
            </div>
          ) : (
            <p>Actual curation outcome appears at the output reveal.</p>
          )}
          <p>
            Admission needs reproducible prediction provenance, native-image review, adjudication
            and oracle, unchanged and wrong-bridge controls.
          </p>
          <small>
            No inference or defect injection was run for this explanation. BR-026 synthetic
            feasibility has a separate contract.
          </small>
        </>
      ) : (
        <>
          <h4>Keep the evidence boundary</h4>
          <p>
            Thirty selected files: size, SHA-256 and ZIP CRC verified. Twelve MRA edge files and
            four image/mask grids checked.
          </p>
          <p>
            Unresolved: natural prediction errors, annotation ambiguity, unseen-data exposure,
            numeric tolerances and anatomical adjudication.
          </p>
          <small>
            TopCoW permits noncommercial use with attribution; commercial use needs permission.
            Graphs are CC BY-NC, version unspecified. Local review does not clear commercial
            redistribution.
          </small>
        </>
      )}
    </aside>
  );
}
