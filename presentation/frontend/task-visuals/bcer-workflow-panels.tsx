import {
  bcerInputs as src,
  bcerContract as data,
  bcerSelection,
  bcerPixel,
  type BcerState,
} from './bcer-workflow';
import css from './bcer-workflow.module.css';
const labels = [
  'Identify',
  'Register ADC',
  'Register DWI',
  'Segment',
  'ROI features',
  'Lesion candidates',
  'Package evidence',
  'Generate report',
];
const locations = [
  [75, 145],
  [255, 35],
  [255, 115],
  [255, 215],
  [450, 275],
  [450, 100],
  [650, 100],
  [650, 245],
];
function Native({ witness, selected }: { witness?: number; selected?: number }) {
  return (
    <div className={css.images} data-bcer-native>
      {src.sequences.map((v, i) => {
        const point =
          witness === undefined ? null : bcerPixel(src.witnesses[witness].native_ijk[i]);
        return (
          <figure key={v.name} data-current={selected === i}>
            <svg
              viewBox={`0 0 ${v.size_xyz[0]} ${v.size_xyz[1]}`}
              role="img"
              aria-label={`${v.name} native MRI, k=${v.slice_k}`}
            >
              <image href={v.png} width={v.size_xyz[0]} height={v.size_xyz[1]} />
              {point && (
                <g data-bcer-witness stroke="white" strokeWidth={v.size_xyz[0] / 300}>
                  <path
                    d={`M${point[0] - v.size_xyz[0] / 30},${point[1]}h${v.size_xyz[0] / 15} M${point[0]},${point[1] - v.size_xyz[0] / 30}v${v.size_xyz[0] / 15}`}
                  />
                </g>
              )}
            </svg>
            <figcaption>
              <b>
                {v.name} · k={v.slice_k}
              </b>
              <span>{v.size_xyz.join(' × ')} voxels</span>
              <span>{v.spacing_xyz_mm.map((n) => n.toFixed(1)).join(' × ')} mm</span>
            </figcaption>
          </figure>
        );
      })}
    </div>
  );
}
function DependencyGraph({ selected }: { selected: number }) {
  return (
    <>
      <svg
        className={css.graph}
        viewBox="0 0 740 315"
        role="img"
        aria-label="Eight-node source planning template; selected node and its direct dependencies"
      >
        <defs>
          <marker
            id="bcer-arrow"
            markerWidth="7"
            markerHeight="7"
            refX="6"
            refY="3.5"
            orient="auto"
          >
            <path d="M0 0L7 3.5L0 7" fill="#607e72" />
          </marker>
        </defs>
        {data.template.nodes.flatMap((node, i) =>
          node.depends_on.map((id) => {
            const j = data.template.nodes.findIndex((n) => n.node_id === id),
              a = locations[j],
              b = locations[i];
            return (
              <line
                key={`${j}-${i}`}
                x1={a[0] === b[0] ? a[0] : a[0] + 68}
                y1={a[0] === b[0] ? a[1] + 23 : a[1]}
                x2={a[0] === b[0] ? b[0] : b[0] - 72}
                y2={a[0] === b[0] ? b[1] - 26 : b[1]}
                stroke={i === selected ? '#267f72' : '#ccd6cf'}
                strokeWidth={i === selected ? 3 : 1.4}
                markerEnd="url(#bcer-arrow)"
              />
            );
          }),
        )}
        {data.template.nodes.map((node, i) => (
          <g key={node.node_id} data-bcer-node={i} data-current={i === selected}>
            <rect
              x={locations[i][0] - 69}
              y={locations[i][1] - 23}
              width="138"
              height="46"
              rx="4"
              fill={i === selected ? '#d5ebe2' : '#fff'}
              stroke={i === selected ? '#267f72' : '#859b8f'}
              strokeWidth={i === selected ? 2 : 1}
              strokeDasharray={node.required ? undefined : '5 3'}
            />
            <text
              x={locations[i][0]}
              y={locations[i][1] - 3}
              textAnchor="middle"
              fontSize="13"
              fill="#163d30"
            >
              {labels[i]}
            </text>
            <text
              x={locations[i][0]}
              y={locations[i][1] + 13}
              textAnchor="middle"
              fontSize="10"
              fill="#61756a"
            >
              {node.required ? 'required in template' : 'optional in template'}
            </text>
          </g>
        ))}
      </svg>
      <ol className={css.mobileNodes} aria-label="Template dependency list">
        {data.template.nodes.map((node, i) => (
          <li key={node.node_id} data-current={i === selected} data-required={node.required}>
            <b>{labels[i]}</b> · {node.required ? 'required' : 'optional'} in template
            <small>
              From:{' '}
              {node.depends_on
                .map((id) => labels[data.template.nodes.findIndex((n) => n.node_id === id)])
                .join(', ') || 'case input'}
            </small>
          </li>
        ))}
      </ol>
    </>
  );
}
const fixtureLabels = [
  'Missing outputs',
  'Empty files',
  'One-voxel fixture',
  'Origin shifted 1 mm',
  'Report stage fails',
];
const artifactDescriptions = [
  [
    'NIfTI mask',
    'Nonzero voxels; size, spacing, origin and direction match the declared T2 input.',
  ],
  [
    'Candidate JSON',
    'Nonnegative integer num_candidates and a candidates list. No lesion reference comparison.',
  ],
  [
    'Feature CSV',
    'At least one parsed data row. The invariant does not check a clinical feature schema.',
  ],
  ['Report JSON', 'A truthy parsed JSON value. No independent diagnostic correctness check.'],
];
export function BcerScene({ state: s }: { state: BcerState }) {
  const at = bcerSelection(s);
  let title = '',
    body;
  switch (s.scene) {
    case 'inputs':
      title = 'Three contrasts enter one workflow';
      body = (
        <>
          <Native selected={at} />
          <p className={css.callout}>
            T2w + at least one of ADC / DWI_highb. This retained PI-CAI example has all three.
          </p>
          <p>PI-CAI 10001_1000001 · native acquired planes · sequence-specific grayscale.</p>
          <p className={css.small}>
            Representative input preparation. No official BCER split, model run or generated
            clinical outputs.
          </p>
        </>
      );
      break;
    case 'manifest':
      title = 'Modality names are part of the contract';
      body = (
        <>
          <div className={css.columns}>
            <article>
              <b>Preserved local example</b>
              <pre>{'{ t2w: true,\n  adc: true,\n  dwi: true,\n  t1c: false }'}</pre>
              <p className={css.warn}>Does not satisfy the pinned case-sensitive modality rule.</p>
            </article>
            <article data-bcer-manifest>
              <b>Fresh derived example</b>
              <pre>{'{ T2w: true,\n  ADC: true,\n  DWI_highb: true }'}</pre>
              <p className={css.good}>Matches long_prostate_full in selected rule replay.</p>
            </article>
          </div>
          <p className={css.callout}>Required: T2w AND (ADC OR DWI_highb).</p>
          <p>
            Canonical flags come from prepared filenames. They do not establish scan quality or
            validate DICOM metadata.
          </p>
        </>
      );
      break;
    case 'geometry':
      title = 'Follow physical coordinates across native grids';
      body = (
        <>
          <Native witness={at} />
          <div className={css.coordinate} data-bcer-coordinate>
            <b>White cross: author ruler point {at + 1}/3 · LPS mm</b>
            <code>{src.witnesses[at].lps_mm.map((n) => n.toFixed(2)).join(', ')}</code>
            <span>
              Native (i,j):{' '}
              {src.witnesses[at].native_ijk
                .map((p, i) => `${src.sequences[i].name} (${p[0].toFixed(1)}, ${p[1].toFixed(1)})`)
                .join(' · ')}
            </span>
          </div>
          <p>
            Header mapping only. Panels have different physical fields of view; matching a physical
            point does not prove anatomical registration.
          </p>
        </>
      );
      break;
    case 'dependencies':
      title = 'Resolve the source plan’s artifact dependencies';
      body = (
        <>
          <DependencyGraph selected={at} />
          <div className={css.selected} data-bcer-dependency>
            <b>
              {labels[at]} · {data.template.nodes[at].tool_name}
            </b>
            <code>
              {at === 5
                ? 'adc_nifti ← @node.register_adc_010.resampled_path'
                : at === 4
                  ? 'Optional in template; required by benchmark contract'
                  : at === 7
                    ? 'case_state_path ← @runtime.case_state_path'
                    : `depends on: ${data.template.nodes[at].depends_on.map((id) => labels[data.template.nodes.findIndex((n) => n.node_id === id)]).join(', ') || 'case input'}`}
            </code>
          </div>
          <p className={css.small}>
            Solid node border: required here. Dashed: optional here. Six required tool names in the
            benchmark contract; eight nodes in this planning template. This is not an execution
            trace.
          </p>
        </>
      );
      break;
    case 'artifacts':
      title = 'Return four typed artifact paths';
      body = (
        <>
          <div className={css.artifactList}>
            {data.contract.required_artifacts.map((a, i) => (
              <article key={a.id} data-current={i === at} data-bcer-artifact={i}>
                <b>{artifactDescriptions[i][0]}</b>
                <code>{a.data_key}</code>
                <span>{a.tool}</span>
              </article>
            ))}
          </div>
          <div className={css.selected}>
            <b>{artifactDescriptions[at][0]} · independent invariant</b>
            <p>{artifactDescriptions[at][1]}</p>
          </div>
          <p className={css.callout}>
            A path that exists counts toward TCR. Its content is checked separately.
          </p>
        </>
      );
      break;
    case 'metrics': {
      title = 'Three check results answer different questions';
      const row = data.validator_examples[at];
      body = (
        <>
          <p className={css.kicker}>AUTHOR NONCLINICAL FIXTURES · SELECTED PURE FUNCTIONS</p>
          <table data-bcer-metrics>
            <thead>
              <tr>
                <th>Fixture</th>
                <th>Base success</th>
                <th>TCR</th>
                <th>Invariants</th>
              </tr>
            </thead>
            <tbody>
              {data.validator_examples.map((r, i) => (
                <tr key={r.id} data-current={i === at}>
                  <td>{fixtureLabels[i]}</td>
                  <td>{r.base_success_rule ? 'pass' : 'fail'}</td>
                  <td>{r.tcr.completed}/10</td>
                  <td>{r.invariants_passed}/5</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className={css.metricDetail}>
            <svg
              viewBox="0 0 80 80"
              role="img"
              aria-label="Nonclinical 8 by 8 grid slice; one colored voxel, not anatomy"
            >
              {Array.from({ length: 64 }, (_, i) => (
                <rect
                  key={i}
                  x={(i % 8) * 10}
                  y={Math.floor(i / 8) * 10}
                  width="9"
                  height="9"
                  fill={at >= 2 && i === 27 ? '#267f72' : '#e3e8e1'}
                />
              ))}
            </svg>
            <div>
              <b>
                {fixtureLabels[at]}: {row.invariants_passed}/5 invariants
              </b>
              <p>
                {at === 0
                  ? 'Six ok=true records, no output files.'
                  : at === 1
                    ? 'All four paths exist, but files contain no usable data.'
                    : at === 2
                      ? '8³ grid with one voxel; empty candidate list, one CSV row, trivial JSON.'
                      : at === 3
                        ? 'Only the synthetic mask origin changes. The geometry invariant fails.'
                        : 'Files and invariants pass, but generate_report has ok=false.'}
              </p>
            </div>
          </div>
          <p className={css.small}>
            Base success: six tool-success rules. TCR: six stages + four paths. Five
            content/geometry invariants are separate. This does not replay controller or fault
            handling.
          </p>
        </>
      );
      break;
    }
    case 'provenance':
      title = 'Keep output provenance beside its status';
      body = (
        <>
          <div className={css.columns}>
            <article>
              <b>Inspect degraded_mode</b>
              <p>
                The segmentation source can use a geometric ellipse when its MONAI dependency check
                raises.
              </p>
              <code>degraded_mode: true</code>
              <p>
                That fallback uses image dimensions. No medical fallback was executed for this
                explanation.
              </p>
            </article>
            <article>
              <b>Read the pinned implementation</b>
              <p>
                Metrics documentation describes SR as requiring TCR=1. The selected contract’s base
                success rule checks six tool statuses.
              </p>
              <p>The runner records success, TCR and invariant outcomes separately.</p>
            </article>
          </div>
          <p className={css.callout}>
            Successful status and a nonempty mask do not establish anatomical accuracy. Retain
            warnings, route and source revision.
          </p>
        </>
      );
      break;
    case 'limits':
      title = 'A workflow contract needs several kinds of evidence';
      body = (
        <div className={css.columns}>
          <article>
            <b>Native inputs</b>
            <p>
              Three PI-CAI volumes. Original and prepared arrays match exactly; geometry agrees
              within 0.00001 mm.
            </p>
          </article>
          <article>
            <b>Recovered mechanics</b>
            <p>
              Pinned six-stage contract, eight-node template and five nonclinical validator
              examples.
            </p>
          </article>
          <article>
            <b>Clinical outputs absent</b>
            <p>
              No retained prostate mask, lesion candidates, feature table or report from an actual
              BCER pipeline.
            </p>
          </article>
          <article>
            <b>Accuracy remains open</b>
            <p>
              No independent anatomical reference or model performance claim. Other BCER tasks need
              their own review.
            </p>
          </article>
        </div>
      );
      break;
  }
  return (
    <section className={css.scene} data-bcer-scene={s.scene}>
      <h3>{title}</h3>
      {body}
    </section>
  );
}
export function BcerOutput({ state: s }: { state: BcerState }) {
  return (
    <aside className={css.aside} data-bcer-aside>
      <b>Workflow operation</b>
      <p>Sequences → tool dependencies → typed artifacts → separate checks</p>
      <b>Task contract</b>
      <p>
        long_prostate_full
        <br />6 stage rules · 4 paths
        <br />5 invariants
      </p>
      <b>{s.scene === 'metrics' ? 'Mechanical replay' : 'Source scope'}</b>
      <p>
        {s.scene === 'metrics'
          ? 'Five author fixtures. The small grid is not patient anatomy.'
          : 'One representative MRI case. Public contract; no clinical output or private GT.'}
      </p>
      <small>
        BCER d108167 · PI-CAI CC BY-NC 4.0
        <br />
        No medical tool or model launch.
      </small>
    </aside>
  );
}
