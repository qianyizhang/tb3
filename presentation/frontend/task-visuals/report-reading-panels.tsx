import {
  reportColors,
  reportOutput,
  reportReference,
  reportReveal,
  reportSource,
  type ReportReadingState,
} from './report-reading';
import sharedStyles from './task-visual.module.css';
import styles from './report-reading.module.css';

function AbstractViewer({ phase }: { phase: number }) {
  const shift = Math.max(0, Math.min(1, phase)) * 72;
  return (
    <svg
      className={styles.viewer}
      viewBox="0 0 360 235"
      role="img"
      aria-label="Symbolic orientation-aware volume viewer with three orthogonal planes; no patient image or numeric geometry"
      data-report-reading-viewer
    >
      <text x="13" y="19">
        ABSTRACT VIEWER · no patient voxels
      </text>
      <path
        className={styles.cube}
        d="M84 57L225 57L283 100L142 100ZM84 57V176L142 219V100M225 57V176L283 219V100M84 176L225 176L283 219L142 219"
      />
      <path
        className={styles.plane}
        d={`M84 ${78 + shift}L225 ${78 + shift}L283 ${121 + shift}L142 ${121 + shift}Z`}
      />
      <path className={styles.plane} d="M150 57L208 100V219L150 176Z" />
      <path className={styles.plane} d="M84 91L142 134L283 134L225 91Z" />
      <path className={styles.cursor} d="M172 112h26m-13-13v26" />
      <text x="10" y="68">
        axial
      </text>
      <text x="10" y="87">
        coronal
      </text>
      <text x="10" y="106">
        sagittal
      </text>
      <text x="235" y="186">
        RAS convention
      </text>
      <text x="235" y="204">
        if geometry verified
      </text>
    </svg>
  );
}

function InputRoles() {
  return (
    <div className={styles.grid}>
      <div className={`${styles.card} ${styles.input}`} data-report-reading-solver-input>
        <h4>Proposed solver-visible input</h4>
        <div className={styles.slot}>
          <strong>Native examination</strong>Full scan if a case is admitted; no image loaded here.
        </div>
        <div className={styles.slot}>
          <strong>Verified pre-exam context slots</strong>
          {reportSource.context_slots.join(' · ')}. Omit unknown values.
        </div>
        <p>No target diagnosis, label, original report or expected finding enters this lane.</p>
      </div>
      <div className={styles.card}>
        <h4>Admission status</h4>
        <div className={styles.slot}>
          <strong>0 admitted CT/report pairs</strong>No case ID or pairing key exists for BR-018.
        </div>
        <div className={styles.slot}>
          <strong>0 model trials</strong>No saved answer or clinical grader result exists.
        </div>
      </div>
    </div>
  );
}

function ViewerOperation({ phase }: { phase: number }) {
  return (
    <div className={styles.grid}>
      <div className={styles.card}>
        <h4>Proposed full-volume search</h4>
        <AbstractViewer phase={phase} />
      </div>
      <div className={styles.card} data-report-reading-evidence-map>
        <h4>Link each answer to image evidence</h4>
        <div className={styles.slot}>
          <strong>Viewer action</strong>Choose orientation and slice; adjust window/level; inspect
          the whole volume.
        </div>
        <div className={styles.arrow}>↓</div>
        <div className={styles.slot}>
          <strong>Evidence location slot</strong>Image filename plus view/slice, or physical RAS-mm
          location after geometry is verified.
        </div>
        <p>
          No slice index, measurement or RAS-mm coordinate is asserted without an admitted image.
        </p>
      </div>
    </div>
  );
}

function Schema({ visible }: { visible: boolean }) {
  if (!visible)
    return (
      <div className={styles.card}>
        <h4>Proposed answer withheld</h4>
        <p>
          No answer fields are shown until the output chapter. There is no retained model response.
        </p>
      </div>
    );
  return (
    <div className={`${styles.card} ${styles.answer}`} data-report-reading-answer-schema>
      <h4>Proposed answer.json · empty schema</h4>
      <div className={styles.slot}>
        <strong>findings [ ]</strong>Observation · location · certainty · evidence
      </div>
      <div className={styles.slot}>
        <strong>impression [ ]</strong>Prioritized synthesis with uncertainty
      </div>
      <div className={styles.slot}>
        <strong>limitations [ ]</strong>Unavailable priors or incomplete evidence
      </div>
      <div className={styles.slot}>
        <strong>evidence_summary [ ]</strong>Links from assertions to inspected image locations
      </div>
      <p>
        Certainty vocabulary: {reportOutput.certainty_vocabulary.join(' / ')}. Every bracket is
        empty.
      </p>
    </div>
  );
}

function PrivateLedger({ reveal }: { reveal: boolean }) {
  if (!reveal)
    return (
      <div className={styles.card}>
        <h4>Private report remains sealed</h4>
        <p>
          Use the reader reference reveal to inspect only the proposed evaluator schema. No report
          or patient claim exists here.
        </p>
      </div>
    );
  return (
    <div className={`${styles.card} ${styles.private}`} data-report-reading-reference>
      <h4>Reader-only proposed report claim ledger · empty</h4>
      {reportReference.claim_slots.map((slot) => (
        <div key={slot} className={styles.slot}>
          {slot}: [no admitted claim]
        </div>
      ))}
      <p>
        The original clinical report would be a fallible report-concordance reference, never a
        solver hint or independent pathology truth.
      </p>
    </div>
  );
}

function Comparison({ reveal, phase }: { reveal: boolean; phase: number }) {
  if (!reveal)
    return (
      <div className={styles.card}>
        <h4>Bidirectional comparison waits for reader reveal</h4>
        <p>
          A proposed answer and a private report claim ledger would be compared in two directions.
          Neither exists for this case-free protocol.
        </p>
      </div>
    );
  const sourceIndex = Math.min(3, Math.floor(Math.max(0, Math.min(phase, 0.999)) * 4));
  const additionIndex = Math.min(2, Math.floor(Math.max(0, Math.min(phase, 0.999)) * 3));
  return (
    <div className={styles.card} data-report-reading-reference data-report-reading-comparison>
      <h4>Proposed bidirectional claim review · no case claims</h4>
      <div className={styles.route}>
        <div data-report-reading-direction="source-to-answer">
          <strong>Private report claim → answer</strong>
          <ol>
            {reportReference.source_claim_routes.map((route, i) => (
              <li
                key={route}
                className={i === sourceIndex ? styles.active : undefined}
                data-report-reading-claim-route={route}
              >
                {route}
              </li>
            ))}
          </ol>
        </div>
        <div data-report-reading-direction="answer-to-source">
          <strong>Answer addition → report / image review</strong>
          <ol>
            {reportReference.solver_addition_routes.map((route, i) => (
              <li
                key={route}
                className={i === additionIndex ? styles.active : undefined}
                data-report-reading-claim-route={route}
              >
                {route}
              </li>
            ))}
          </ol>
        </div>
      </div>
      <p className={styles.note}>
        {reportReference.rule} Highlighting cycles through categories only; it does not score an
        actual finding.
      </p>
    </div>
  );
}

export function ReportReadingScene({ state }: { state: ReportReadingState }) {
  const reveal = reportReveal(state);
  const output =
    state.output > 0.5 && ['answer', 'reference', 'comparison', 'limits'].includes(state.scene);
  const titles: Record<ReportReadingState['scene'], string> = {
    availability: 'Proposed BR-018 reading task · source unavailable',
    input: 'What a solver would receive',
    viewer: 'How complete-volume evidence would be located',
    answer: 'An editable answer schema, still empty',
    reference: 'The original report belongs to a private evaluator',
    comparison: 'Compare omissions and unsupported additions separately',
    limits: 'What remains proposed, and what would reopen the task',
  };
  return (
    <div
      className={styles.scene}
      data-report-reading-scene={state.scene}
      data-report-reading-reference-state={reveal ? 'revealed' : 'hidden'}
      data-report-reading-basis="symbolic-proposed"
    >
      <div className={styles.head}>
        <h3>{titles[state.scene]}</h3>
        <span>BR-018 · 0 admitted pairs · 0 trials</span>
      </div>
      {state.scene === 'availability' && <InputRoles />}
      {state.scene === 'input' && <InputRoles />}
      {state.scene === 'viewer' && <ViewerOperation phase={state.phase} />}
      {state.scene === 'answer' && (
        <div className={styles.grid}>
          <div className={styles.card} data-report-reading-evidence-map>
            <h4>Symbolic image evidence → answer</h4>
            <AbstractViewer phase={state.phase} />
            <p>Evidence locations would be linked after a real case and geometry are verified.</p>
          </div>
          <Schema visible={output} />
        </div>
      )}
      {state.scene === 'reference' && (
        <div className={styles.grid}>
          <Schema visible={output} />
          <PrivateLedger reveal={reveal} />
        </div>
      )}
      {state.scene === 'comparison' && (
        <div className={styles.grid}>
          <Schema visible={output} />
          <Comparison reveal={reveal} phase={state.phase} />
        </div>
      )}
      {state.scene === 'limits' && (
        <div className={styles.grid}>
          <div className={styles.card}>
            <h4>Proposed controls · no results</h4>
            {reportReference.proposed_controls.map((control) => (
              <div key={control} className={styles.slot}>
                {control}
              </div>
            ))}
            <p>These were planned evaluator checks, never executed on an admitted patient pair.</p>
          </div>
          <div className={styles.card}>
            <h4>Reopen with an admitted pair</h4>
            <p>
              Obtain authorized access, verify exact image/report pairing, native geometry and
              correction status, then freeze a private claim ledger and enforce solver/reference
              isolation.
            </p>
            {reveal && (
              <p className={styles.boundary} data-report-reading-reference>
                Reference reveal explains roles only. No report text or case claim is present.
              </p>
            )}
          </div>
        </div>
      )}
      <p className={styles.note}>
        Every drawing is an abstract protocol diagram. No patient voxels, diagnostic claims, model
        findings, report excerpts or performance values are depicted.
      </p>
    </div>
  );
}

export function ReportReadingOutput({ state }: { state: ReportReadingState }) {
  const visible =
    state.output > 0.5 && ['answer', 'reference', 'comparison', 'limits'].includes(state.scene);
  return (
    <aside
      className={`${sharedStyles.storyOutput} ${styles.output}`}
      data-report-reading-output={visible ? 'empty-schema' : 'hidden'}
    >
      <h3>{visible ? 'Proposed output schema' : 'No model answer'}</h3>
      {visible ? (
        <>
          <div className={styles.code} data-report-reading-answer-schema>
            {
              '{\n  "findings": [],\n  "impression": [],\n  "limitations": [],\n  "evidence_summary": []\n}'
            }
          </div>
          <p>
            <strong>Empty by design.</strong> No patient record, saved response, diagnosis or score
            exists.
          </p>
        </>
      ) : (
        <p>
          BR-018 has zero admitted CT/report pairs and zero model trials. The output lane opens only
          as an empty proposed schema.
        </p>
      )}
    </aside>
  );
}
