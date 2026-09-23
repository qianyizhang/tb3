import { useEffect, useLayoutEffect, useMemo, useReducer, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Datasets } from './datasets';
import { LanguageSwitch, LocaleProvider, localeHref, localizeExplorer, useLocale } from './locale';
import { createModel, groupId, inScope, navKey } from './model';
import {
  explorerReducer,
  initialState,
  taskRoute,
  type Dispatch,
  type ExplorerAction,
} from './state';
import { TaskBrowser, TaskList } from './task-browser';
import { TaskDetail } from './task-detail';
import { parseExplorerData, type ExplorerData } from './types';
function useMedia(query: string) {
  const [matches, setMatches] = useState(() => matchMedia(query).matches);
  useEffect(() => {
    const media = matchMedia(query),
      update = () => setMatches(media.matches);
    media.addEventListener('change', update);
    return () => media.removeEventListener('change', update);
  }, [query]);
  return matches;
}
function BriefGuide({ dialog }: { dialog: React.RefObject<HTMLDialogElement | null> }) {
  const { t } = useLocale();
  return (
    <dialog ref={dialog} id="rules" aria-labelledby="rules-title">
      <button className="quiet close" id="close" onClick={() => dialog.current?.close()}>
        {t('Close')}
      </button>
      <div className="eyebrow">{t('Accepted convention · 21 Sep 2026')}</div>
      <h2 id="rules-title">{t('A Task Brief, inside a Task Explorer')}</h2>
      <p>
        {t(
          'A short explanation of a task, useful before a run and alongside a results story. Aim for a 60–90 second first read.',
        )}
      </p>
      <ol>
        <li>
          <strong>{t('Question + value.')}</strong>{' '}
          {t('One concrete action and where it fits in a clinical or scientific workflow.')}
        </li>
        <li>
          <strong>{t('What is given.')}</strong>{' '}
          {t(
            'Raw data, supplied helpers and callable tools shown separately. Mark reference-only material explicitly.',
          )}
        </li>
        <li>
          <strong>{t('Task contract.')}</strong>{' '}
          {t('Required action, constraints, output shape and how success is checked.')}
        </li>
        <li>
          <strong>{t('Visual explanation.')}</strong>{' '}
          {t(
            'Show input → assistance → output. Use native slices/overlays when available; label conceptual diagrams.',
          )}
        </li>
        <li>
          <strong>{t('What remains difficult.')}</strong>{' '}
          {t('Explain the work left after assistance, backed by evidence when available.')}
        </li>
        <li>
          <strong>{t('Sources + state.')}</strong>{' '}
          {t(
            'Pin the task/condition, distinguish drafts from published definitions, and state missing evidence.',
          )}
        </li>
      </ol>
      <p>
        <strong>{t('Catalogue structure:')}</strong>{' '}
        {t(
          'Capability or repository → task family → definition/revision → conditions and cases. Research ownership and supporting-study roles are separate axes. Repeated cases share a brief; every case should still be reachable.',
        )}
      </p>
      <p>
        <strong>{t('Reuse:')}</strong>{' '}
        {t(
          'One repository rulebook and small template; a thin authoring skill follows them. Existing tours stay task-specific visual modules.',
        )}
      </p>
      <p className="fine">
        {t(
          'The existing experiment protocol/scorer remains authoritative. A reader-facing brief is not automatically a runnable solver prompt. Source coverage remains explicitly scoped.',
        )}
      </p>
    </dialog>
  );
}
export function Explorer({ data: sourceData }: { data: ExplorerData }) {
  const { locale, t } = useLocale();
  const data = useMemo(() => localizeExplorer(sourceData, locale), [sourceData, locale]);
  const model = useMemo(() => createModel(data), [data]);
  const [state, reduce] = useReducer(
    (state: ReturnType<typeof initialState>, action: ExplorerAction) =>
      explorerReducer(model, state, action),
    model,
    (model) => explorerReducer(model, initialState(model), { type: 'route', hash: location.hash }),
  );
  const current = useRef(state);
  current.current = state;
  const focus = useRef<string | null>(state.source ? '#source-heading' : null);
  const focusBrowserOnOpen = useRef(false);
  const [browserExpanded, setBrowserExpanded] = useState(false),
    compact = useMedia('(max-width: 800px)'),
    mobile = useMedia('(max-width: 640px)');
  const dialog = useRef<HTMLDialogElement>(null),
    main = useRef<HTMLElement>(null),
    datasetMode = state.dataset !== null;
  const hidden = datasetMode || (compact && !browserExpanded),
    route = taskRoute(state, model),
    entry = model.get(state.selected);
  const dispatch: Dispatch = (action, selector) => {
    const next = explorerReducer(model, current.current, action);
    focus.current = selector || null;
    if (action.type !== 'visual' && action.type !== 'route')
      history[action.type === 'search' ? 'replaceState' : 'pushState'](
        null,
        '',
        taskRoute(next, model),
      );
    reduce(action);
  };
  useEffect(() => {
    const change = () => {
      const previous = current.current,
        next = explorerReducer(model, previous, { type: 'route', hash: location.hash });
      focus.current = next.source
        ? '#source-heading'
        : previous.source
          ? `[data-source="${previous.source}"], [data-notice="${previous.source}"]`
          : null;
      reduce({ type: 'route', hash: location.hash });
    };
    window.addEventListener('hashchange', change);
    return () => window.removeEventListener('hashchange', change);
  }, [model]);
  useLayoutEffect(() => {
    document.body.classList.toggle('dataset-mode', datasetMode);
    const dataset = data.datasets?.records.find((record) => record.id === state.dataset);
    document.title =
      (datasetMode ? dataset?.title || t('Datasets') : entry.repo) + ' · ' + t('Task catalogue');
    if (focus.current) {
      const element = document.querySelector<HTMLElement>(focus.current);
      const sourceExample = element?.closest<HTMLDetailsElement>('.scene-source');
      if (sourceExample) sourceExample.open = true;
      element?.focus();
      focus.current = null;
    }
  }, [state, datasetMode, data, entry]);
  useLayoutEffect(() => {
    if (focusBrowserOnOpen.current && !hidden) {
      document.getElementById('search')?.focus();
      focusBrowserOnOpen.current = false;
    }
    const active = document.activeElement;
    if (hidden && active?.closest('#task-browser'))
      document.getElementById(datasetMode ? 'main' : 'browse-toggle')?.focus();
    if (mobile && active?.closest('.task-list'))
      document.getElementById('mobile-task-picker')?.focus();
    if (!mobile && active?.id === 'mobile-task-picker')
      document.querySelector<HTMLElement>('.task-item[aria-pressed="true"]')?.focus();
  }, [hidden, mobile, datasetMode, browserExpanded]);
  const toggleBrowser = () => {
    // Focus only after React has committed the sidebar's visible state.
    focusBrowserOnOpen.current = !browserExpanded;
    setBrowserExpanded((expanded) => !expanded);
  };
  const matches = model.data.entries.filter(
    (row) =>
      navKey(row, state.view) === navKey(entry, state.view) &&
      inScope(row, state.lane, state.work, state.modality) &&
      model.match(row, state.query.trim().toLowerCase()),
  );
  const visible = matches.some((row) => row.id === state.selected),
    repository = model.repository(entry),
    intro =
      state.view === 'repository'
        ? data.repository_contexts?.[groupId(entry)]
        : model.category(entry.category).description;
  const heading = state.view === 'repository' ? entry.repo : model.category(entry.category).title;
  return (
    <>
      <a
        className="skip-link"
        href="#main"
        onClick={(event) => {
          event.preventDefault();
          main.current?.focus();
          main.current?.scrollIntoView({ block: 'start' });
        }}
      >
        {t('Skip to content')}
      </a>
      <header className="site-header">
        <a
          className="site-brand"
          id="site-brand"
          href={
            data.presentation_context?.home_url
              ? localeHref(data.presentation_context.home_url, locale)
              : route
          }
        >
          <span>TB3 / MEDICAL</span>
          <span className="site-brand-caption">{t('Research workbench')}</span>
        </a>
        <nav className="site-nav" aria-label={t('Primary navigation')}>
          {data.presentation_context?.home_url && (
            <a id="workbench-home" href={localeHref(data.presentation_context.home_url, locale)}>
              {t('Overview')}
            </a>
          )}
          <a id="tasks-home" href={route} aria-current={!datasetMode ? 'page' : undefined}>
            {t('Tasks')}
          </a>
          <a id="datasets-home" href="#datasets" aria-current={datasetMode ? 'page' : undefined}>
            {t('Datasets')}
          </a>
        </nav>
        <button
          className="button button-secondary brief-guide"
          id="format"
          onClick={() => dialog.current?.showModal()}
        >
          {t('Brief guide')}
        </button>
        <LanguageSwitch />
      </header>
      <div className="browse-toolbar">
        <button
          className="button button-secondary"
          id="browse-toggle"
          aria-controls="task-browser"
          aria-expanded={!hidden}
          onClick={toggleBrowser}
        >
          {t('Browse tasks')} <span aria-hidden="true">⌄</span>
        </button>
        <span id="mobile-selection">{heading}</span>
      </div>
      <div className="shell">
        <TaskBrowser
          model={model}
          state={state}
          dispatch={dispatch}
          hidden={hidden}
          compact={compact}
        />
        <main ref={main} id="main" tabIndex={-1}>
          {datasetMode ? (
            <Datasets key={state.dataset} model={model} id={state.dataset!} taskRoute={route} />
          ) : (
            <>
              <div className="repository-heading">
                <div className="eyebrow">
                  {state.view === 'repository' ? t('Source repository') : t('Explore a capability')}
                </div>
                <h1>{heading}</h1>
                {intro && <p>{intro}</p>}
              </div>
              <div className="catalogue-workspace">
                <TaskList model={model} state={state} dispatch={dispatch} />
                {visible ? (
                  <TaskDetail model={model} state={state} dispatch={dispatch} />
                ) : (
                  <section className="empty-state task-detail">
                    <div className="eyebrow">{t('No results')}</div>
                    <h2>{t('No tasks match these filters')}</h2>
                    <p>
                      {t(
                        'Try a broader term, a different research role, or clear the filters to explore the collection.',
                      )}
                    </p>
                    <button
                      className="button button-secondary"
                      data-reset-filters
                      onClick={() => dispatch({ type: 'reset' }, hidden ? '#main' : '#search')}
                    >
                      {t('Reset filters')}
                    </button>
                  </section>
                )}
              </div>
              {repository && (
                <details className="coverage">
                  <summary>{t('Coverage & source revisions')}</summary>
                  <p>{repository.coverage}</p>
                  <p className="fine">
                    {repository.items.length} indexed source records · observed{' '}
                    {repository.observed_on} · revision <code>{repository.commit}</code>. Records
                    include repeated cases and overlapping releases.
                  </p>
                </details>
              )}
            </>
          )}
        </main>
      </div>
      <BriefGuide dialog={dialog} />
    </>
  );
}
const root = document.getElementById('root');
if (root) {
  try {
    const data = parseExplorerData(document.getElementById('data')?.textContent || '');
    createRoot(root).render(
      <LocaleProvider>
        <Explorer data={data} />
      </LocaleProvider>,
    );
  } catch (error) {
    createRoot(root).render(
      <main className="empty-state" role="alert">
        <h1>This Task Explorer could not open</h1>
        <p>{error instanceof Error ? error.message : 'The embedded collection is unreadable.'}</p>
        <p>Rebuild this copy with the matching frontend and data contract.</p>
      </main>,
    );
  }
}
