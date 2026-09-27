import {
  pilotGeometry as cases,
  pilotTrace as trace,
  pilotReference as refs,
  pilotColors as c,
  pilotSlabIndex,
  pilotReveal,
  pilotOutput,
  type PilotState,
} from './resect-pilot';
import { resectProjection, type ResectPlane } from './resect';
import styles from './task-visual.module.css';
const n = (v: number) => v.toFixed(3),
  triplet = (v: number[]) => v.map(n).join(', ');
function Point({
  plane,
  point,
  x,
  y,
  size,
  color,
  shape,
}: {
  plane: ResectPlane;
  point: number[];
  x: number;
  y: number;
  size: number;
  color: string;
  shape: string;
}) {
  const p = resectProjection(plane, point),
    scale = size / Math.max(plane.width, plane.height);
  const sx = x + (p.u + 0.5) * scale,
    sy = y + (p.v + 0.5) * scale;
  return (
    <g
      transform={`translate(${sx} ${sy})`}
      fill="none"
      stroke={color}
      strokeWidth="2.5"
      data-pilot-point={shape}
    >
      {shape === 'initial' ? (
        <circle r="6" />
      ) : shape === 'cue' ? (
        <path d="M0 -8L8 0L0 8L-8 0Z" />
      ) : shape === 'returned' ? (
        <rect x="-4" y="-4" width="8" height="8" />
      ) : (
        <path d="M-7 0H7M0 -7V7" />
      )}
    </g>
  );
}
function ImagePlane({
  plane,
  x,
  y,
  size,
  label,
}: {
  plane: ResectPlane;
  x: number;
  y: number;
  size: number;
  label: string;
}) {
  const scale = size / Math.max(plane.width, plane.height);
  return (
    <g>
      <text x={x} y={y - 12} fontSize="16">
        {label}
      </text>
      <rect x={x} y={y} width={plane.width * scale} height={plane.height * scale} fill="#202825" />
      <image
        href={plane.png}
        x={x}
        y={y}
        width={plane.width * scale}
        height={plane.height * scale}
      />
    </g>
  );
}
function TracePair({ state }: { state: PilotState }) {
  const cue = state.scene === 'cue',
    index = pilotSlabIndex(state.view),
    views = cue ? trace.cue_views : trace.slabs[index];
  return (
    <g>
      <text x="25" y="30">
        {cue
          ? 'Prompt candidate · displayed at step 19'
          : `Final candidate slabs · offset ${trace.slab_offsets_mm[index]} mm`}
      </text>
      {views.map((p, i) => (
        <g key={i}>
          <text x={30 + i * 290} y="75" fontSize="17">
            {i ? 'US candidate' : 'MRI query'}
          </text>
          <image href={p.png} x={30 + i * 290} y="95" width="245" height="245" />
        </g>
      ))}
      <text x="25" y="370" fontSize="16">
        {cue ? '30 mm field · independently centred' : '20 mm field · five retained sections'}
      </text>
      <text x="25" y="400" fontSize="15">
        Gold crosses: centres · +R right / +A up
      </text>
    </g>
  );
}
export function ResectPilotScene({ state }: { state: PilotState }) {
  const reveal = pilotReveal(state),
    answer = pilotOutput(state);
  return (
    <svg
      className={styles.operationCanvas}
      viewBox="0 0 600 420"
      role="img"
      aria-label="Retained RESECT pilot inputs, prompt cue, trace and manual-reference reveal"
    >
      {state.scene === 'inputs' ? (
        <g>
          {cases.map((row, i) =>
            (['mri', 'us'] as const).map((key, j) => (
              <g key={row.case_id + key}>
                <ImagePlane
                  plane={row.modalities[key].native}
                  x={45 + j * 290}
                  y={65 + i * 185}
                  size={155}
                  label={`${i ? 'B' : 'A'} · ${key === 'mri' ? 'FLAIR' : 'US'}`}
                />
                <Point
                  plane={row.modalities[key].native}
                  point={row.mri_world_mm}
                  x={45 + j * 290}
                  y={65 + i * 185}
                  size={155}
                  color={c.initial}
                  shape="initial"
                />
              </g>
            )),
          )}
        </g>
      ) : ['cue', 'inspect', 'output'].includes(state.scene) ? (
        <TracePair state={state} />
      ) : state.scene === 'search' ? (
        <g>
          <text x="25" y="35">
            Retained correlation peaks · step 21
          </text>
          <text x="25" y="76" fontSize="17">
            B: patch radius → top world point
          </text>
          {trace.peaks
            .filter((p) => p.case_id === 'case_b')
            .map((p, i) => (
              <g key={p.radius_mm}>
                <rect x="25" y={95 + i * 73} width="550" height="63" rx="6" fill="#e9ede5" />
                <text x="40" y={120 + i * 73} fontSize="17">
                  {p.radius_mm} mm · NCC {p.score_rounded}
                </text>
                <text x="40" y={144 + i * 73} fontSize="16">
                  [{p.top_world_mm_rounded.join(', ')}]
                </text>
              </g>
            ))}
          <text x="25" y="348" fontSize="17">
            A: correlation alternatives were rejected.
          </text>
          <text x="25" y="381" fontSize="16">
            Search centred on original MRI query.
          </text>
          <text x="25" y="409" fontSize="15">
            Rounded trace values · no search rerun
          </text>
        </g>
      ) : state.scene === 'reference' ? (
        <g>
          <text x="25" y="32">
            Case B · fixed initial-centred US sections
          </text>
          {cases[1].modalities.us.ras.map((plane, i) => (
            <g key={plane.name}>
              <ImagePlane plane={plane} x={25 + i * 195} y={92} size={160} label={plane.name} />
              <Point
                plane={plane}
                point={cases[1].initial_us_world_mm}
                x={25 + i * 195}
                y={92}
                size={160}
                color={c.initial}
                shape="initial"
              />
              <Point
                plane={plane}
                point={trace.cue_world_mm}
                x={25 + i * 195}
                y={92}
                size={160}
                color={c.cue}
                shape="cue"
              />
              {answer && (
                <Point
                  plane={plane}
                  point={answer[1].us_world_mm}
                  x={25 + i * 195}
                  y={92}
                  size={160}
                  color={c.returned}
                  shape="returned"
                />
              )}
              {reveal && (
                <Point
                  plane={plane}
                  point={refs.cases[1].reference_world_mm}
                  x={25 + i * 195}
                  y={92}
                  size={160}
                  color={c.reference}
                  shape="reference"
                />
              )}
              <text x={25 + i * 195} y="281" fontSize="15">
                Ref off-plane:
              </text>
              <text x={25 + i * 195} y="307" fontSize="15">
                {reveal
                  ? `${resectProjection(plane, refs.cases[1].reference_world_mm).normal_mm.toFixed(2)} mm`
                  : 'hidden'}
              </text>
            </g>
          ))}
          <text x="25" y="343" fontSize="16">
            {reveal ? 'Cue: 0.505 mm · returned: 1.130 mm' : 'Manual reference and errors hidden'}
          </text>
          <text x="25" y="376" fontSize="15">
            Projected markers · no reference recentering
          </text>
          <text x="25" y="407" fontSize="14">
            XY +R/+A · XZ +R/+S · YZ +A/+S (right/down)
          </text>
        </g>
      ) : state.scene === 'controls' ? (
        <g>
          <text x="25" y="34">
            Artifact pass does not mean physical success
          </text>
          {[
            ['Original oracle', 'Reference artifact · reward 1'],
            ['Original nop', 'No result.json · reward 0'],
            [
              'Post-hoc unchanged copy',
              reveal ? 'Mean 5.305 mm · reward 1' : 'Reference errors hidden',
            ],
            [
              'Post-hoc A + B cue copy',
              reveal ? 'Mean 0.771 mm · reward 1' : 'Reference errors hidden',
            ],
          ].map((r, i) => (
            <g key={r[0]}>
              <rect x="25" y={57 + i * 83} width="550" height="71" rx="8" fill="#e9ede5" />
              <text x="40" y={84 + i * 83} fontSize="18">
                {r[0]}
              </text>
              <text x="40" y={112 + i * 83} fontSize="16">
                {r[1]}
              </text>
            </g>
          ))}
          <text x="25" y="410" fontSize="15">
            Diagnostics are synthetic artifacts, not model runs.
          </text>
        </g>
      ) : (
        <g>
          {[
            ['Retain', 'Exact outcomes in a cue-present task'],
            ['Exclude', 'Unaided or unseen-case capability claim'],
            ['Unresolved', 'Cue origin and causal contribution'],
            ['Reopen', 'Authorized neutral prompt + held-out plan'],
          ].map((r, i) => (
            <g key={r[0]}>
              <rect x="25" y={25 + i * 94} width="550" height="79" rx="8" fill="#e9ede5" />
              <text x="40" y={55 + i * 94} fontSize="19">
                {r[0]}
              </text>
              <text x="40" y={85 + i * 94} fontSize="16">
                {r[1]}
              </text>
            </g>
          ))}
        </g>
      )}
    </svg>
  );
}
export function ResectPilotOutput({ state }: { state: PilotState }) {
  const reveal = pilotReveal(state),
    answer = pilotOutput(state);
  return (
    <aside className={styles.storyOutput} data-pilot-output={state.scene}>
      {state.scene === 'inputs' ? (
        <>
          <h4>One attempt, two selected queries</h4>
          <p>
            Four complete native volumes. Circles locate supplied MRI queries and identical initial
            US world points.
          </p>
          <p>
            <b>A:</b> source Case 1, tag index 1. <b>B:</b> Case 3, index 12. Complete native XY
            sections are previews; axes differ.
          </p>
          <p>
            Selection used paired tags and mask centroids before inference. Public training data;
            not blinded.
          </p>
          <small>
            No masks or tag files supplied. A helpful B coordinate example is supplied; inspect it
            next.
          </small>
        </>
      ) : state.scene === 'cue' ? (
        <>
          <h4>A coordinate inside the prompt</h4>
          <pre>--case case_b{'\n'}--us-center -30 15 15</pre>
          <p>
            Frozen instruction lines 21–22. Delivered at trace step 5; rendered at step 18;
            displayed at step 19.
          </p>
          <p>
            MRI is centred on the query; US on the example candidate. Matching centres on screen do
            not prove registration.
          </p>
          <small>
            Actual delivered axial panels, cropped and reduced. Gold crosses are viewer centres.
            Manual destination and error remain hidden.
          </small>
        </>
      ) : state.scene === 'inspect' ? (
        <>
          <h4>Inspect neighbouring slices</h4>
          <p>
            Five axial slabs from the actual final-candidate views displayed at step 25. Offset −2
            to +2 mm from each volume's own centre.
          </p>
          <p>
            MRI centre: supplied query. US centre: returned candidate. The images share orientation
            and scale, not world centre.
          </p>
          <p>
            Only the middle plane contains its centre point. Crosses on other slices are
            projections.
          </p>
          <small>
            This animation changes the viewed slice. It neither moves anatomy nor establishes
            homologous tissue.
          </small>
        </>
      ) : state.scene === 'search' ? (
        <>
          <h4>Image analysis with the cue present</h4>
          <p>
            Inverted FLAIR / US local correlation: 0.6 mm grid, smoothing, ±12 mm translation
            search, three patch sizes.
          </p>
          <p>
            Small-patch B peak is near the returned point. Other patch sizes differ. For A, the
            agent keeps the initial point despite alternatives.
          </p>
          <p>
            The search starts at the MRI query, not the cue. This is counterevidence to assuming the
            cue was necessary.
          </p>
          <small>
            NCC is not confidence or reference agreement. No optimizer is executed for this
            explanation.
          </small>
        </>
      ) : state.scene === 'output' ? (
        <>
          <h4>Actual output: US world millimetres</h4>
          {answer ? (
            <div data-pilot-answer>
              <table>
                <thead>
                  <tr>
                    <th>Case</th>
                    <th>us_world_mm</th>
                    <th>Conf.</th>
                  </tr>
                </thead>
                <tbody>
                  {answer.map((a, i) => (
                    <tr key={a.case_id}>
                      <th>{i ? 'B' : 'A'}</th>
                      <td>{triplet(a.us_world_mm)}</td>
                      <td>{a.confidence}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <p>
                Ordered entries, nonempty evidence and report. Confidence is subjective, not
                calibrated.
              </p>
            </div>
          ) : (
            <p>Saved answer withheld until the output reveal.</p>
          )}
          <small>
            Shown: slabs displayed at step 25. A separate final PNG was generated at step 27 without
            a recorded display. This is not the proposed voxel-output task.
          </small>
        </>
      ) : state.scene === 'reference' ? (
        <>
          <h4>Reveal the manual paired target</h4>
          <span data-pilot-reference>{reveal ? 'revealed' : 'hidden'}</span>
          {reveal ? (
            <>
              <table>
                <thead>
                  <tr>
                    <th>TRE mm</th>
                    <th>A</th>
                    <th>B</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <th>Initial</th>
                    {refs.cases.map((r, i) => (
                      <td key={i}>{n(r.initial_error_mm)}</td>
                    ))}
                  </tr>
                  <tr>
                    <th>Returned</th>
                    {refs.cases.map((r, i) => (
                      <td key={i}>{n(r.final_error_mm)}</td>
                    ))}
                  </tr>
                  <tr>
                    <th>Prompt cue</th>
                    <td>—</td>
                    <td>{n(refs.cue_error_mm)}</td>
                  </tr>
                </tbody>
              </table>
              <p>
                <b>The supplied cue is closer.</b> B moved 10.640 mm. Original final error remains
                unchanged.
              </p>
            </>
          ) : (
            <p>Paired target and physical errors remain hidden.</p>
          )}
          <p>
            Circle: initial. Diamond: cue. Square: returned. Pink cross: manual target. All are
            projections onto fixed planes.
          </p>
          <small>
            48 mm fields; 3D Euclidean error, no physical pass threshold or clinical adjudication.
          </small>
        </>
      ) : state.scene === 'controls' ? (
        <>
          <h4>Separate runs from diagnostics</h4>
          <p>
            <b>Eligible:</b> one normal completion. <b>Excluded:</b> empty-credential HTTP 401
            before task work.
          </p>
          <p>Original no-op produced no answer. It is not an unchanged-coordinate prediction.</p>
          <p>
            Later zero-confidence copy artifacts pass too. These test the scorer, not model
            capability.
          </p>
          <small>
            Saved-output replay is byte-identical. It is not fresh execution, and reward checks no
            distance threshold.
          </small>
        </>
      ) : (
        <>
          <h4>Qualified descriptive evidence</h4>
          <p>
            Keep exact coordinates, scores, movement, valid artifacts and observed image-analysis
            actions.
          </p>
          <p>
            Withhold unaided recovery, superiority to all supplied cues, pure visual-only reasoning
            and generalization claims.
          </p>
          <p>
            Cue origin and causal effect remain unresolved. Two selected public points do not
            establish clinical accuracy.
          </p>
          <small>
            Original evidence is preserved. A scoped assistant review records the limitation. No new
            trial or publication.
          </small>
        </>
      )}
    </aside>
  );
}
