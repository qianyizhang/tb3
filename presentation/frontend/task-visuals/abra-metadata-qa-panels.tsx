import {
  abraMetadataPack,
  metadataCounts,
  metadataValues,
  metadataReferenceVisible,
  queryFrame,
  queryIndex,
  type AbraMetadataState,
} from './abra-metadata-qa';
import type { StoryPlan } from '../types';
import shared from './task-visual.module.css';
import css from './abra-metadata-qa.module.css';
const { source, fixture } = abraMetadataPack;
const families = [
  {
    label: 'CT instance count',
    tool: 'get_study_series',
    field: 'first CT.instanceCount',
    format: 'integer',
    value: '140',
    derivation: 'Select the first CT series and its 140 instances; exclude 26 SEG/SR instances.',
  },
  {
    label: 'All-series count',
    tool: 'get_study_metadata',
    field: 'seriesCount',
    format: 'integer',
    value: '27',
    derivation: '1 CT + 13 SEG + 13 SR = 27 series, irrespective of modality.',
  },
  {
    label: 'Distinct modalities',
    tool: 'get_study_series',
    field: 'series[].Modality',
    format: 'sorted comma + space list',
    value: 'CT, SEG, SR',
    derivation:
      '27 tags → distinct {SR, CT, SEG} → alphabetically sorted [CT, SEG, SR] → comma + space join.',
  },
  {
    label: 'Study date',
    tool: 'get_study_metadata',
    field: 'StudyDate',
    format: 'YYYYMMDD',
    value: '',
    derivation:
      'Read the eight-digit source StudyDate; do not infer an acquisition time from file order.',
  },
  {
    label: 'First CT series UID',
    tool: 'get_study_series',
    field: 'first CT.SeriesInstanceUID',
    format: 'exact UID string',
    value: '',
    derivation:
      'Use the first CT in source enumeration; do not sort UIDs or use the StudyInstanceUID.',
  },
];
export function AbraMetadataScene({
  state,
  plan,
  onSeekFrame,
}: {
  state: AbraMetadataState;
  plan: StoryPlan;
  onSeekFrame?: (frame: number) => void;
}) {
  const query = queryIndex(state.progress);
  const selected = families[query];
  const reveal = metadataReferenceVisible(state);
  const counts = metadataCounts(source);
  const values = metadataValues(source);
  return (
    <section className={css.scene} data-abra-metadata-scene={state.scene}>
      {(state.scene === 'input' || state.scene === 'operation') && (
        <>
          <h3>
            {counts.study} study → {counts.series} series → {counts.total} instances
          </h3>
          <p>
            <b>Source-manifest teaching record</b>; no observed generated task or tool response.
          </p>
          {state.scene === 'input' && (
            <table>
              <caption>Series and instances are different denominators</caption>
              <thead>
                <tr>
                  <th>Modality</th>
                  <th>Series</th>
                  <th>Instances</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <th>CT</th>
                  <td>1</td>
                  <td>140</td>
                </tr>
                <tr>
                  <th>SEG</th>
                  <td>13</td>
                  <td>13</td>
                </tr>
                <tr>
                  <th>SR</th>
                  <td>13</td>
                  <td>13</td>
                </tr>
                <tr>
                  <th>Total</th>
                  <td>27</td>
                  <td>166</td>
                </tr>
              </tbody>
            </table>
          )}
          <p>Only 140 CT DICOMs are recovered locally. SEG/SR counts are manifest records.</p>
          <div className={css.controls} aria-label="Select metadata query family">
            {families.map((item, index) => (
              <button
                key={item.label}
                type="button"
                aria-pressed={query === index}
                onClick={() => onSeekFrame?.(queryFrame(plan, index))}
                disabled={!onSeekFrame}
              >
                {item.label}
              </button>
            ))}
          </div>
          {state.scene === 'operation' && (
            <>
              <h4>{selected.label}</h4>
              <p>
                <code>{selected.tool}(study_uid)</code> → <code>{selected.field}</code> →{' '}
                {selected.format}
              </p>
              <p>{selected.derivation}</p>
              {state.scene === 'operation' && (
                <p data-abra-metadata-source-value>
                  <b>Source-derived teaching value:</b>{' '}
                  <code style={{ overflowWrap: 'anywhere' }}>{values[query]}</code>. This value is
                  permitted metadata context, not a submitted answer.
                </p>
              )}
              <small>
                get_study_series returns up to three sample instances per series; instanceCount
                represents its stored total. Do not count just the three samples.
              </small>
            </>
          )}
        </>
      )}
      {state.scene === 'output' && (
        <>
          <h3>One terminal answer string</h3>
          <code data-abra-metadata-empty-output>submit_answer.arguments.answer: —</code>
          <p>
            Empty participant field. Integer count, YYYYMMDD date, comma + space sorted modality
            list or exact UID, as requested; no label or explanation.
          </p>
        </>
      )}
      {state.scene === 'reference' && (
        <>
          <h3>Separate evaluator state and illustrative comparison</h3>
          {!reveal ? (
            <p data-abra-metadata-comparison-hidden>
              Comparison covered until explicit reader reveal.
            </p>
          ) : (
            <div data-abra-metadata-comparison-revealed>
              <p>
                Generated <code>expected_outcome.answer</code> is evaluator-owned and absent. No
                reference answer asset exists.
              </p>
              <h4>
                Illustrative formatter control — authored records, no patient/model/reference
                evidence
              </h4>
              <p>
                Authored input: <code>{fixture.input_modalities.join(', ')}</code> → deduplicate →
                alphabetic sort → comma + space join.
              </p>
              <table>
                <caption>
                  Pure source-code synthetic contract check; no participant submission
                </caption>
                <thead>
                  <tr>
                    <th>Illustrative string</th>
                    <th>Contract comparison</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>CT, SEG, SR</td>
                    <td>Matches toy formatted string</td>
                  </tr>
                  <tr>
                    <td>SR, CT, SEG</td>
                    <td>Order mismatch</td>
                  </tr>
                  <tr>
                    <td>CT,SEG,SR</td>
                    <td>Comma-spacing mismatch</td>
                  </tr>
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
      {state.scene === 'limits' && (
        <>
          <h3>Counts are source teaching; observed task result is absent</h3>
          <p>{source.actual_data_gap}</p>
          <p>
            Eight-turn generator limit. Last submit_answer is compared after lowercase/whitespace
            and suffix normalization, or numeric difference strictly below 0.01. No scored
            participant result or image interpretation is represented.
          </p>
        </>
      )}
    </section>
  );
}

export function AbraMetadataOutput({ state }: { state: AbraMetadataState }) {
  return (
    <aside className={`${shared.storyOutput} ${css.aside}`} data-abra-metadata-output>
      <b>Metadata QA</b>
      <p>{families[queryIndex(state.progress)].label}</p>
      <p>Manifest teaching record; permitted source fields may reveal the queried value.</p>
      <small>
        No generated task, live response, participant answer or score. Illustrative comparison{' '}
        {metadataReferenceVisible(state) ? 'revealed' : 'covered'}.
      </small>
    </aside>
  );
}
