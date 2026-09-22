import { Component, Fragment, useEffect, useMemo, useRef, useState } from 'react';
import type { ErrorInfo, ReactNode } from 'react';
import { createRoot } from 'react-dom/client';
import {
  filterRecords,
  initialRoute,
  overviewUrl,
  parseOverviewData,
  readOverviewRoute,
  recordKinds,
  recordText,
} from './overview-data';
import type {
  OverviewData,
  OverviewRoute,
  OverviewVocabulary,
  ResearchRecord,
  VocabularyTerm,
} from './overview-data';

function Badge({ term }: { term: VocabularyTerm | undefined }) {
  return term ? (
    <span className="badge" title={term.definition}>
      {term.label}
    </span>
  ) : null;
}

function RecordBadges({
  row,
  vocabulary,
}: {
  row: ResearchRecord;
  vocabulary: OverviewVocabulary;
}) {
  const rule = vocabulary.display_rules[`${row.kind}_primary`];
  const axes = Array.isArray(rule) ? rule : [];
  return (
    <span className="badges">
      {axes.map((axis) => (
        <Badge key={axis} term={vocabulary.axes[axis]?.values[recordText(row.current[axis])]} />
      ))}
      {row.kind === 'evaluation' && (
        <Badge term={vocabulary.axes.outcome?.values[recordText(row.outcome)]} />
      )}
      {row.kind === 'export' && (
        <Badge
          term={vocabulary.axes.submission_status?.values[recordText(row.submission_status)]}
        />
      )}
    </span>
  );
}

function RecordDetails({ row, data }: { row: ResearchRecord; data: OverviewData }) {
  const { vocabulary } = data;
  const observed = row.current.observed_at || row.observed_at || row.collected_at;
  const decisions = data.records
    .filter((record) => record.kind === 'decision' && record.target_id === row.id)
    .sort((a, b) => recordText(a.created_at).localeCompare(recordText(b.created_at)));
  const control =
    ['oracle', 'nop'].includes(recordText(row.agent)) &&
    ['pass', 'fail'].includes(recordText(row.outcome))
      ? row.outcome === (row.agent === 'oracle' ? 'pass' : 'fail')
        ? 'control_expected'
        : 'control_unexpected'
      : undefined;
  return (
    <div className="detail">
      <p className="meta">
        {row.id} · {recordText(row.group_id) || 'shared'}
      </p>
      {['historical', 'diagnostic'].map((key) =>
        row[key] ? <Badge key={key} term={vocabulary.context_badges[key]} /> : null,
      )}
      {Boolean(row.partial || row.current.partial) && (
        <Badge term={vocabulary.context_badges.partial} />
      )}
      {Boolean(observed) && <p className="meta">Observed: {recordText(observed)}</p>}
      {['question', 'claim', 'reason', 'scope', 'body', 'insight', 'notes'].map((key) =>
        row[key] ? <p key={key}>{recordText(row[key])}</p> : null,
      )}
      {Boolean(row.current.assessment_reason) && <p>{recordText(row.current.assessment_reason)}</p>}
      {Boolean(row.current.assessment_scope) && (
        <p>Assessed scope: {recordText(row.current.assessment_scope)}</p>
      )}
      {row.kind === 'evaluation' && (
        <>
          <p>
            Scorer reward: {recordText(row.reward ?? 'not recorded')} ·{' '}
            {recordText(row.model || row.agent || 'role not recorded')}
          </p>
          {control && <Badge term={vocabulary.context_badges[control]} />}
        </>
      )}
      {(row.current.review_flags ?? []).map((flag, index) => (
        <p className="unavailable" key={`${flag.experiment_id}-${index}`}>
          {flag.experiment_id}:{' '}
          {vocabulary.axes.assessment?.values[flag.assessment]?.label ?? flag.assessment} —{' '}
          {flag.reason}
        </p>
      ))}
      {decisions.map((decision) => (
        <p key={decision.id}>
          {decision.accepted ? 'Accepted decision' : 'Recommendation'} ·{' '}
          {recordText(decision.actor)}:{' '}
          {vocabulary.axes.idea_state?.values[recordText(decision.idea_state)]?.label ??
            recordText(decision.idea_state)}{' '}
          — {recordText(decision.reason)}
        </p>
      ))}
      {(row.portable_links ?? []).map((link, index) =>
        link.url ? (
          <p key={`${link.url}-${index}`}>
            <a href={link.url}>{link.label}</a>
          </p>
        ) : null,
      )}
      {(row.experiment_ids ?? []).map((id) => (
        <p key={id}>
          <a href={`?kind=experiment&q=${encodeURIComponent(id)}`}>Experiment: {id}</a>
        </p>
      ))}
      <details>
        <summary>Record and evidence locators</summary>
        <pre>{JSON.stringify(row, null, 2)}</pre>
      </details>
    </div>
  );
}

function RecordCard({
  row,
  data,
  groupLabel,
  open,
  toggle,
}: {
  row: ResearchRecord;
  data: OverviewData;
  groupLabel: string | undefined;
  open: boolean;
  toggle: () => void;
}) {
  return (
    <details className="record" id={row.id} open={open}>
      <summary
        className={row.current.attention ? 'alert' : undefined}
        onClick={(event) => {
          event.preventDefault();
          toggle();
        }}
      >
        <span className="type">{row.kind}</span>
        <span className="record-heading">
          <span className="record-title">{recordText(row.title) || row.id}</span>
          {groupLabel && <span className="record-subtitle">{groupLabel}</span>}
        </span>
        <RecordBadges row={row} vocabulary={data.vocabulary} />
        <span className="disclosure" aria-hidden="true">
          ›
        </span>
      </summary>
      {open && <RecordDetails row={row} data={data} />}
    </details>
  );
}

function ResearchAreas({ data }: { data: OverviewData | undefined }) {
  const groups = data?.records.filter((row) => row.kind === 'group') ?? [];
  return (
    <section id="research-areas" className="research-areas" aria-labelledby="areas-title">
      <SectionTitle
        eyebrow="The questions behind the work"
        id="areas-title"
        title="Research areas"
        description="Current findings, open questions and the path between them."
      />
      <div id="groups" className="groups" aria-busy={!data}>
        {groups.map((group, index) => {
          const experiments = data?.records.filter(
            (row) => row.kind === 'experiment' && row.group_id === group.id,
          ).length;
          const ideas = data?.records.filter(
            (row) => row.kind === 'idea' && row.group_id === group.id,
          ).length;
          return (
            <a className="group-card" href={recordText(group.story_url)} key={group.id}>
              <span className="number">{String(index + 1).padStart(2, '0')}</span>
              <h3>{recordText(group.title)}</h3>
              <p>{recordText(group.question)}</p>
              <p className="counts">
                <span>
                  {experiments} experiment{experiments === 1 ? '' : 's'} · {ideas} idea
                  {ideas === 1 ? '' : 's'}
                </span>
                <span className="card-arrow" aria-hidden="true">
                  →
                </span>
              </p>
            </a>
          );
        })}
      </div>
    </section>
  );
}

function SectionTitle({
  eyebrow,
  id,
  title,
  description,
}: {
  eyebrow: string;
  id: string;
  title: string;
  description: string;
}) {
  return (
    <div className="section-title">
      <div>
        <p className="eyebrow">{eyebrow}</p>
        <h2 id={id}>{title}</h2>
      </div>
      <p>{description}</p>
    </div>
  );
}

function RecordBrowser({ data, failed }: { data: OverviewData | undefined; failed: boolean }) {
  const [route, setRoute] = useState<OverviewRoute>(initialRoute);
  const [openRecords, setOpenRecords] = useState<Set<string>>(() => new Set());
  const searchInput = useRef<HTMLInputElement>(null);
  const groups = useMemo(() => data?.records.filter((row) => row.kind === 'group') ?? [], [data]);
  const groupLabels = useMemo(
    () => new Map(groups.map((row) => [row.id, recordText(row.title)])),
    [groups],
  );
  const rows = useMemo(() => (data ? filterRecords(data.records, route) : []), [data, route]);

  useEffect(() => {
    if (!data) return;
    const restore = () => {
      const next = readOverviewRoute(location.search, data);
      setRoute(next);
      setOpenRecords(new Set(next.record ? [next.record] : []));
    };
    restore();
    window.addEventListener('popstate', restore);
    return () => window.removeEventListener('popstate', restore);
  }, [data]);

  function navigate(next: OverviewRoute, push = true) {
    setRoute(next);
    const url = overviewUrl(location.href, next);
    if (url.href !== location.href) history[push ? 'pushState' : 'replaceState'](null, '', url);
  }

  function updateFilter(key: 'search' | 'group' | 'kind' | 'status', value: string) {
    navigate({ ...route, [key]: value, record: '' }, key !== 'search');
    setOpenRecords(new Set());
  }

  function resetFilters() {
    navigate(initialRoute);
    setOpenRecords(new Set());
    searchInput.current?.focus({ preventScroll: true });
  }

  function toggleRecord(id: string) {
    const open = !openRecords.has(id);
    setOpenRecords((previous) => {
      const next = new Set(previous);
      if (open) next.add(id);
      else next.delete(id);
      return next;
    });
    navigate({ ...route, record: open ? id : route.record === id ? '' : route.record });
  }

  return (
    <section id="research-record" className="catalog" aria-labelledby="evidence-title">
      <SectionTitle
        eyebrow="Trace a conclusion to its source"
        id="evidence-title"
        title="Evidence & decisions"
        description="Search the record. Open an entry to inspect the details."
      />
      <form
        id="filters"
        role="search"
        aria-label="Filter research records"
        onSubmit={(event) => event.preventDefault()}
        onReset={(event) => {
          event.preventDefault();
          resetFilters();
        }}
      >
        <label htmlFor="search">
          Search the record
          <input
            ref={searchInput}
            id="search"
            type="search"
            placeholder="Question, model, source…"
            autoComplete="off"
            disabled={!data}
            value={route.search}
            onChange={(event) => updateFilter('search', event.target.value)}
          />
        </label>
        <label htmlFor="group">
          Research area
          <select
            id="group"
            disabled={!data}
            value={route.group}
            onChange={(event) => updateFilter('group', event.target.value)}
          >
            <option value="">All research areas</option>
            {groups.map((group) => (
              <option value={group.id} key={group.id}>
                {recordText(group.title)}
              </option>
            ))}
          </select>
        </label>
        <label htmlFor="kind">
          Record type
          <select
            id="kind"
            disabled={!data}
            value={route.kind}
            onChange={(event) => updateFilter('kind', event.target.value)}
          >
            {recordKinds.map(([kind, label]) => (
              <option value={kind} key={kind}>
                {label}
              </option>
            ))}
          </select>
        </label>
        <label htmlFor="status">
          Status
          <select
            id="status"
            disabled={!data}
            value={route.status}
            onChange={(event) => updateFilter('status', event.target.value)}
          >
            <option value="">All statuses</option>
            <option value="attention">Experiments needing action</option>
            {Object.entries(data?.vocabulary.axes ?? {}).map(([axis, definition]) => (
              <optgroup label={axis.replaceAll('_', ' ')} key={axis}>
                {Object.entries(definition.values).map(([code, term]) => (
                  <option value={`${axis}:${code}`} key={code}>
                    {term.label}
                  </option>
                ))}
              </optgroup>
            ))}
          </select>
        </label>
      </form>
      <div className="result-toolbar">
        <p id="count" role="status" aria-live="polite">
          {failed
            ? 'Research record unavailable'
            : data
              ? `${rows.length} of ${data.records.length} records`
              : 'Loading the research record…'}
        </p>
        <button
          id="reset-filters"
          className="reset-button"
          type="reset"
          form="filters"
          disabled={!data}
        >
          Reset filters
        </button>
      </div>
      <div id="records" className="records" aria-busy={!data && !failed}>
        {failed && <LoadError />}
        {data &&
          rows.map((row) => (
            <RecordCard
              key={row.id}
              row={row}
              data={data}
              groupLabel={groupLabels.get(recordText(row.group_id))}
              open={openRecords.has(row.id)}
              toggle={() => toggleRecord(row.id)}
            />
          ))}
      </div>
      <div id="empty" className="empty-state" hidden={!data || rows.length > 0}>
        <h3>No matching records</h3>
        <p>Try a broader search, choose another research area or include all record types.</p>
        <button className="button button-secondary" type="reset" form="filters">
          Reset filters
        </button>
      </div>
    </section>
  );
}

function LoadError() {
  return (
    <div className="empty-state" role="alert">
      <h3>The research record could not be loaded</h3>
      <p>Reload the page to try again.</p>
      <button className="button button-secondary" type="button" onClick={() => location.reload()}>
        Reload workbench
      </button>
    </div>
  );
}

function Overview() {
  const [data, setData] = useState<OverviewData>();
  const [failed, setFailed] = useState(false);
  const [guideOpen, setGuideOpen] = useState(location.hash === '#status-guide');
  const main = useRef<HTMLElement>(null);
  const taskUrl = data?.task_explorer_url ?? undefined;

  useEffect(() => {
    const controller = new AbortController();
    async function load() {
      try {
        const response = await fetch('records.json', { signal: controller.signal });
        if (!response.ok) throw new Error(`Research record response: ${response.status}`);
        const payload: unknown = await response.json();
        setData(parseOverviewData(payload));
      } catch {
        if (!controller.signal.aborted) setFailed(true);
      }
    }
    void load();
    return () => controller.abort();
  }, []);

  useEffect(() => {
    const reveal = () => {
      if (location.hash === '#status-guide') setGuideOpen(true);
    };
    window.addEventListener('hashchange', reveal);
    return () => window.removeEventListener('hashchange', reveal);
  }, []);

  return (
    <>
      <a
        className="skip-link"
        href="#main"
        onClick={(event) => {
          event.preventDefault();
          main.current?.focus();
        }}
      >
        Skip to content
      </a>
      <header className="site-header">
        <a className="site-brand" href="index.html">
          TB3 / MEDICAL<span className="site-brand-caption">Research workbench</span>
        </a>
        <nav className="site-nav" aria-label="Primary navigation">
          <a href="index.html" aria-current="page">
            Overview
          </a>
          <a id="tasks-nav-link" href={taskUrl} hidden={!taskUrl}>
            Tasks
          </a>
          <a
            id="datasets-nav-link"
            href={taskUrl ? `${taskUrl}#datasets` : undefined}
            hidden={!taskUrl}
          >
            Datasets
          </a>
        </nav>
      </header>
      <main id="main" ref={main} tabIndex={-1}>
        <section className="intro" aria-labelledby="intro-title">
          <div className="intro-copy">
            <p className="eyebrow">Medical imaging · Agent research</p>
            <h1 id="intro-title">What can an agent learn from medical images?</h1>
            <p className="lede">
              Explore the tasks, follow the research and trace each conclusion back to its evidence.
            </p>
            <div className="intro-actions">
              <span id="task-explorer-entry" hidden={!taskUrl}>
                <a id="task-explorer-link" className="button button-primary" href={taskUrl}>
                  Explore tasks <span aria-hidden="true">→</span>
                </a>
              </span>
              <a className="button button-secondary" href="#research-record">
                Browse evidence
              </a>
            </div>
            <p className="intro-note">
              Successes, partial attempts and corrections stay in the same record.
            </p>
          </div>
          <aside className="wayfinding" aria-label="Explore the workbench">
            <p className="eyebrow">Find your way</p>
            {[
              [
                'research-areas',
                'Follow a research question',
                'Read the story across experiments.',
              ],
              [
                'research-record',
                'Inspect the evidence',
                'Find results, decisions and open issues.',
              ],
              ['status-guide', 'Understand the status', 'See what each assessment means.'],
            ].map(([id, title, description], index) => (
              <a
                href={`#${id}`}
                key={id}
                onClick={id === 'status-guide' ? () => setGuideOpen(true) : undefined}
              >
                <span className="wayfinding-number" aria-hidden="true">
                  {String(index + 1).padStart(2, '0')}
                </span>
                <span>
                  <strong>{title}</strong>
                  <span>{description}</span>
                </span>
                <span className="wayfinding-arrow" aria-hidden="true">
                  ↓
                </span>
              </a>
            ))}
          </aside>
        </section>
        <ResearchAreas data={data} />
        <RecordBrowser data={data} failed={failed} />
        <details
          id="status-guide"
          className="status-guide"
          open={guideOpen}
          onToggle={(event) => setGuideOpen(event.currentTarget.open)}
        >
          <summary>
            <span>Status definitions</span>
            <span className="guide-hint">How to read the research record</span>
          </summary>
          <dl id="legend">
            {Object.entries(data?.vocabulary.axes ?? {}).flatMap(([axis, definition]) =>
              Object.entries(definition.values).map(([code, term]) => (
                <Fragment key={`${axis}:${code}`}>
                  <dt>{term.label}</dt>
                  <dd>{term.definition}</dd>
                </Fragment>
              )),
            )}
          </dl>
        </details>
        <footer>
          <p>Medical imaging research, with a record you can inspect.</p>
          <p>
            Read-only workbench · Packaging, evidence validity and submission qualification are
            separate.
          </p>
        </footer>
      </main>
    </>
  );
}

class OverviewBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };

  static getDerivedStateFromError() {
    return { failed: true };
  }

  componentDidCatch(error: Error, information: ErrorInfo) {
    console.error('Unable to display the research workbench', error, information.componentStack);
  }

  render() {
    return this.state.failed ? (
      <main>
        <LoadError />
      </main>
    ) : (
      this.props.children
    );
  }
}

const root = document.getElementById('overview-root');
if (!root) throw new Error('The workbench root is missing');
createRoot(root).render(
  <OverviewBoundary>
    <Overview />
  </OverviewBoundary>,
);
