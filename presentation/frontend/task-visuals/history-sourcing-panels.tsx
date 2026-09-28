import {
  historySource as src,
  historyReference as ref,
  historySelection,
  type HistorySourcingState,
} from './history-sourcing';
import styles from './task-visual.module.css';
function CandidateStrip({ selected, count = 5 }: { selected: number; count?: number }) {
  return (
    <div className={styles.historyStrip}>
      {src.candidates.slice(0, count).map((c, i) => (
        <div
          key={c.id}
          data-history-candidate={c.id}
          data-selected={selected === i}
          data-untested={!c.task}
        >
          <b>{c.id}</b>
          <span>{c.label}</span>
        </div>
      ))}
    </div>
  );
}
function Results() {
  return (
    <div data-history-private>
      <table className={styles.historyTable}>
        <thead>
          <tr>
            <th>Frozen condition</th>
            <th>Terra/high · one attempt each</th>
            <th>Agent time</th>
          </tr>
        </thead>
        <tbody>
          {ref.tasks.map((t, i) => (
            <tr key={t.task}>
              <td>
                {src.candidates[i].id} · {src.candidates[i].label}
              </td>
              <td>
                {src.candidates[i].endpoint}
                {i === 3 && <small> All 72 Dice values = 1.0</small>}
              </td>
              <td>{t.trials.find((t) => t.agent === 'codex')!.agent_seconds.toFixed(1)} s</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className={styles.historyCallout}>
        All four original rewards = 1; zero model exceptions. Each frozen task has a separate oracle
        = 1 and no-op = 0.
      </p>
      <p>
        Eight controls are separate executions. These four endpoints cannot be pooled into accuracy.
        QA packets are correlated; H03 and H04 share one CT.
      </p>
    </div>
  );
}
export function HistorySourcingScene({ state }: { state: HistorySourcingState }) {
  const sel = historySelection(state),
    e = src.excerpts[sel.excerpt],
    c = src.candidates[sel.candidate],
    t = ref.tasks[sel.task],
    counts = src.counts;
  let title = '',
    body;
  switch (state.scene) {
    case 'retrieval':
      title = 'A bounded selection from retained history';
      body = (
        <>
          <div className={styles.historyCounts}>
            {[
              [395, 'indexed records'],
              [237, 'navigable records'],
              [9, 'selected exports'],
              [8, 'verified excerpts'],
            ].map(([n, label]) => (
              <article key={label}>
                <strong>{n}</strong>
                <span>{label}</span>
              </article>
            ))}
          </div>
          <div
            className={styles.historyPartition}
            role="img"
            aria-label="395 indexed records partitioned into 142 automatic reviews, 16 other long titles, and 237 navigable records"
          >
            <div style={{ flex: counts.automatic_reviews }}>142</div>
            <div style={{ flex: counts.other_long_titles }}>16</div>
            <div style={{ flex: counts.navigable_records }}>237</div>
          </div>
          <p>Gray: automatic reviews · amber: other long titles · green: navigable records.</p>
          <p className={styles.historyCallout}>
            395 − 142 − 16 = 237. Nine conversations were selected; eight quoted records come from
            six of them.
          </p>
          <p>
            This recount verifies the retained selection. It does not recover every incident or
            establish 237 independent attempts.
          </p>
        </>
      );
      break;
    case 'excerpts':
      title = 'Read the record before making a claim';
      body = (
        <>
          <div className={styles.historyExcerptStrip}>
            {src.excerpts.map((r, i) => (
              <span key={r.id} data-selected={sel.excerpt === i}>
                {r.id}
              </span>
            ))}
          </div>
          <article className={styles.historyQuote} data-history-excerpt={e.id}>
            <b>
              {e.id} · {e.evidence_class}
            </b>
            <blockquote lang={e.id === 'E07' ? 'zh-CN' : 'en'}>{e.excerpt}</blockquote>
            <small>
              Role: {e.role} · original JSONL line {e.line}
            </small>
            <code>Session {e.session_id}</code>
            <code>Record SHA-256 {e.raw_record_sha256}</code>
          </article>
          <p>
            The original record bytes, role and literal excerpt match the receipt. This
            authenticates the quotation, not its diagnosis or a benchmark failure.
          </p>
        </>
      );
      break;
    case 'classification':
      title = 'Different source claims need different evidence';
      body = (
        <>
          <div className={styles.historyCards}>
            <article>
              <b>Recovered reports</b>
              <p>E01–E03: PDF crop complaints and an assistant diagnosis.</p>
              <p>E04–E08: resident lifecycle, queued work and stale-ledger reports.</p>
            </article>
            <article>
              <b>New proposal</b>
              <p>H03: coverage-aware anatomical annotation QA.</p>
              <p>An explicit user question, not a recovered failed trial.</p>
            </article>
            <article>
              <b>Incomplete recollection</b>
              <p>H04: SVG difficulty recalled by the user.</p>
              <p>
                The original SVG incident and exact timeout/reroute incident were not recovered.
              </p>
            </article>
          </div>
          <p className={styles.historyCallout}>
            All eight excerpts are historical source evidence. None is a BR-003 model trial.
          </p>
        </>
      );
      break;
    case 'candidates':
      title = 'Translate a lead into an explicit contract';
      body = (
        <>
          <CandidateStrip selected={sel.candidate} />
          <article className={styles.historyContract} data-history-contract={c.id}>
            <b>
              {c.id} · {c.source_strength}
            </b>
            <dl>
              <dt>Given</dt>
              <dd>{c.input}</dd>
              <dt>Return</dt>
              <dd>{c.output}</dd>
              <dt>Private reference</dt>
              <dd>{c.reference}</dd>
            </dl>
            <p className={styles.historyCallout}>{c.limit}</p>
          </article>
        </>
      );
      break;
    case 'lineage':
      title = 'Tie every recorded result to frozen task bytes';
      body = (
        <>
          <CandidateStrip selected={sel.task} count={4} />
          <div className={styles.historyLineage} data-history-lineage={src.candidates[sel.task].id}>
            <article>
              <strong>{t.source_files}</strong>
              <b>source files</b>
              <small>{t.freeze.split('/').at(-1)}</small>
            </article>
            <span aria-hidden="true">→</span>
            <article>
              <strong>1</strong>
              <b>retained archive</b>
              <small>Exact snapshot checked in memory</small>
            </article>
            <span aria-hidden="true">→</span>
            <article>
              <strong>3</strong>
              <b>result records</b>
              <small>Oracle · no-op · model</small>
            </article>
          </div>
          <code className={styles.historyHash} data-history-checksum={t.task_checksum}>
            Matching task SHA-256: {t.task_checksum}
          </code>
          <p>
            Across four tasks: 76 frozen files, four archives and twelve raw result records. Hashes
            match the retained receipts.
          </p>
          <p className={styles.historyCallout}>
            Arrows show documented provenance. Byte verification is not a fresh execution or proof
            of container recovery.
          </p>
        </>
      );
      break;
    case 'reference':
      title = sel.reference
        ? 'Reveal four distinct retained outcomes'
        : 'Keep recorded outcomes separate from source claims';
      body = sel.reference ? (
        <Results />
      ) : (
        <>
          <div className={styles.historyLock}>
            <b>Reader reference reveal</b>
            <p>
              The four frozen contracts and eight history excerpts are already visible. The original
              model grades appear halfway through this chapter.
            </p>
          </div>
          <p>
            No source complaint has been converted into a trial failure. H05 has no trial to reveal.
          </p>
        </>
      );
      break;
    case 'controls': {
      const control = ref.controls[sel.task];
      title = 'Ask which specific mistake the grader rejects';
      body = (
        <>
          <CandidateStrip selected={sel.task} count={4} />
          <article
            className={styles.historyContract}
            data-history-control={control.id}
            data-history-private
          >
            <b>Counterexample: {control.error}</b>
            <p>{control.evidence}</p>
            <p className={styles.historyCallout}>{control.meaning}</p>
          </article>
          <p>
            Targeted author diagnostics complement the oracle/no-op runs. They demonstrate
            discrimination on specified errors, not model difficulty.
          </p>
        </>
      );
      break;
    }
    case 'gap':
      title = 'The original vector-crop ownership question remains open';
      body = (
        <>
          <div className={styles.historyBranches}>
            <article>
              <b>Recovered PDF crop reports</b>
              <p>E01–E03 · incomplete crops or unrelated prose</p>
            </article>
            <div className={styles.historyCards}>
              <article>
                <b>H01: table lineage</b>
                <p>New synthetic PDF; manual transcription permitted.</p>
                <p data-history-private>Recorded pass: 4/4 table checks.</p>
              </article>
              <article data-untested="true" data-history-untested>
                <b>H05: vector crop ownership</b>
                <p>Authentic compact figure + independent boundary truth still needed.</p>
                <p>No executable task. No attempt. No score.</p>
              </article>
            </div>
          </div>
          <p className={styles.historyCallout}>
            H01’s pass does not answer H05. The dashed branch is a documented gap, not a failed
            trial.
          </p>
        </>
      );
      break;
    case 'limits':
      title = 'Preserve the pass and the unresolved source gap';
      body = (
        <>
          <div className={styles.historyCards}>
            <article>
              <b>Established here</b>
              <p>
                Eight exact source quotations; frozen identities; four original passing
                calibrations.
              </p>
            </article>
            <article>
              <b>Still bounded</b>
              <p>
                Selected history, different endpoints, one attempt per task, shared medical source
                and correlated packets.
              </p>
            </article>
            <article>
              <b>Not established</b>
              <p>
                Population accuracy, model rankings, original vector-crop difficulty, or clinical
                reliability.
              </p>
            </article>
          </div>
          <p className={styles.historyCallout}>
            The historical round remains closed. This explanation changes no score and launches no
            model trial.
          </p>
          <p>
            182 source pins verify retained records. No saved-code replay or fresh runtime recovery
            is claimed.
          </p>
        </>
      );
      break;
  }
  return (
    <section
      className={styles.historyScene}
      data-history-scene={state.scene}
      data-history-reference={sel.reference ? 'visible' : 'hidden'}
    >
      <h4>{title}</h4>
      {body}
    </section>
  );
}
export function HistorySourcingOutput({ state }: { state: HistorySourcingState }) {
  const sel = historySelection(state),
    candidate =
      src.candidates[
        state.scene === 'gap'
          ? 4
          : state.scene === 'lineage' || state.scene === 'controls'
            ? sel.task
            : sel.candidate
      ];
  return (
    <aside className={styles.historyAside}>
      <b>Source-study operation</b>
      <p>Retrieve → classify → specify → freeze → compare → retain limits.</p>
      {state.scene === 'excerpts' ? (
        <>
          <b>Selected source</b>
          <p>
            {src.excerpts[sel.excerpt].id} · {src.excerpts[sel.excerpt].role}
            <br />
            Line {src.excerpts[sel.excerpt].line}
          </p>
        </>
      ) : (
        <>
          <b>
            {candidate.id} · {candidate.label}
          </b>
          <p>{candidate.lead}</p>
          <p>
            Source excerpts: {candidate.source_ids.join(', ') || 'User proposal or recollection'}
          </p>
        </>
      )}
      <b>Evidence boundary</b>
      <p>Historical reports do not carry model grades. Private outcomes are revealed separately.</p>
      {sel.reference && (
        <p data-history-private>
          <b>Original outcomes</b>
          <br />
          Four Terra/high passes; one attempt per frozen task. H05 untested.
        </p>
      )}
      <small>
        Record indices, not physical coordinates. Amber selects; green marks verified provenance.
        Dashed amber marks an untested branch.
      </small>
    </aside>
  );
}
