import { useLayoutEffect, useRef, useState } from 'react';
import {
  edition,
  familyKey,
  hasExample,
  inScope,
  listGroup,
  navKey,
  type ExplorerModel,
  type TaskUnit,
} from './model';
import type { Dispatch, ExplorerState } from './state';
import type { BrowseView, ResearchLane } from './types';
import { useLocale } from './locale';
interface Props {
  model: ExplorerModel;
  state: ExplorerState;
  dispatch: Dispatch;
}
export function TaskBrowser({
  model,
  state,
  dispatch,
  hidden,
  compact,
}: Props & { hidden: boolean; compact: boolean }) {
  const { t } = useLocale();
  const query = state.query.trim().toLowerCase(),
    entry = model.get(state.selected),
    active = navKey(entry, state.view),
    buckets = new Map<string, typeof model.data.entries>();
  for (const row of model.data.entries.filter((row) =>
    inScope(row, state.lane, state.work, state.modality),
  )) {
    const key = navKey(row, state.view);
    if (!buckets.has(key)) buckets.set(key, []);
    buckets.get(key)!.push(row);
  }
  const count = model.units(
    model.data.entries.filter(
      (row) => inScope(row, state.lane, state.work, state.modality) && model.match(row, query),
    ),
  ).length;
  const filter = (
    change: Partial<{ view: BrowseView; lane: ResearchLane; work: string; modality: string }>,
  ) =>
    dispatch({
      type: 'filters',
      view: state.view,
      lane: state.lane,
      work: state.work,
      modality: state.modality,
      ...change,
    });
  const reset = () => dispatch({ type: 'reset' }, hidden ? '#main' : '#search');
  return (
    <aside id="task-browser" aria-label={t('Browse and filter tasks')} hidden={hidden}>
      <div className="browser-heading">
        <span className="eyebrow">{t('Task catalogue')}</span>
        <button
          className="text-button"
          id="reset-filters"
          hidden={!query && state.lane === 'tasks' && !state.work && !state.modality}
          onClick={reset}
        >
          {t('Reset')}
        </button>
      </div>
      <label htmlFor="search">{t('Search tasks')}</label>
      <input
        id="search"
        type="search"
        placeholder={t('Task, image type, case…')}
        autoComplete="off"
        value={state.query}
        onChange={(event) => dispatch({ type: 'search', query: event.target.value })}
      />
      <p id="search-count" className="search-count" role="status" aria-live="polite">
        {count} {state.lane === 'tasks' ? t('task entries') : t('research entries')}
        {query ? t(' match your search') : t(' in this collection')}
      </p>
      <label htmlFor="browse">{t('Browse by')}</label>
      <select
        id="browse"
        value={state.view}
        onChange={(event) => filter({ view: event.target.value as BrowseView })}
      >
        <option value="capability">{t('Capability')}</option>
        <option value="repository">{t('Repository')}</option>
      </select>
      <details
        className="advanced-filters"
        id="advanced-filters"
        open={!compact || state.lane !== 'tasks' || !!state.work || !!state.modality}
      >
        <summary>{t('Refine the collection')}</summary>
        <div className="filter-fields">
          <label htmlFor="lane">{t('Research role')}</label>
          <select
            id="lane"
            value={state.lane}
            onChange={(event) => filter({ lane: event.target.value as ResearchLane })}
          >
            <option value="tasks">{t('Agent tasks')}</option>
            <option value="supporting">{t('Supporting research')}</option>
            <option value="all">{t('All research')}</option>
          </select>
          <label htmlFor="modality">{t('Imaging / data modality')}</label>
          <select
            id="modality"
            value={state.modality}
            onChange={(event) => filter({ modality: event.target.value })}
          >
            <option value="">{t('All modalities')}</option>
            {Object.entries(model.data.taxonomy.modalities || {}).map(([id, label]) => (
              <option value={id} key={id}>
                {t(label)}
              </option>
            ))}
          </select>
          <label htmlFor="agent-work">{t('Agent work')}</label>
          <select
            id="agent-work"
            value={state.work}
            onChange={(event) => filter({ work: event.target.value })}
          >
            <option value="">{t('All agent work')}</option>
            {Object.entries(model.data.taxonomy.agent_work || {})
              .filter(([key]) => key !== 'none')
              .map(([key, label]) => (
                <option value={key} key={key}>
                  {t(label)}
                </option>
              ))}
          </select>
        </div>
      </details>
      <nav
        id="nav"
        aria-label={state.view === 'capability' ? t('Task capabilities') : t('Source repositories')}
      >
        {[...buckets]
          .filter(([, rows]) => rows.some((row) => model.match(row, query)))
          .map(([key, rows]) => {
            const first = rows.find((row) => model.match(row, query))!,
              count = model.units(rows.filter((row) => model.match(row, query))).length;
            return (
              <button
                className="navitem"
                data-group={first.id}
                aria-current={active === key}
                key={key}
                onClick={() =>
                  dispatch(
                    { type: 'definition', id: first.id },
                    `[data-group="${CSS.escape(first.id)}"]`,
                  )
                }
              >
                <strong>
                  {state.view === 'repository' ? first.repo : t(model.category(key).title)}
                </strong>
                <small>
                  {count} {state.lane === 'tasks' ? t('task entries') : t('research entries')}
                </small>
              </button>
            );
          })}
        {!count && (
          <p className="empty">
            {t('No matching entries. Try a broader term or reset the filters.')}
          </p>
        )}
      </nav>
    </aside>
  );
}
export function TaskList({ model, state, dispatch }: Props) {
  const { t } = useLocale();
  const entry = model.get(state.selected),
    key = navKey(entry, state.view),
    query = state.query.trim().toLowerCase(),
    searching = !!query;
  const all = model.data.entries.filter(
    (row) =>
      navKey(row, state.view) === key && inScope(row, state.lane, state.work, state.modality),
  );
  const units = model.units(
      all.filter((row) => model.match(row, query)),
      state.selected,
    ),
    allUnits = model.units(all, state.selected);
  const [openGroups, setOpenGroups] = useState<Record<string, boolean>>({});
  useLayoutEffect(() => {
    const family = familyKey(entry, state.view);
    if (listGroup(entry, state.view)) {
      setOpenGroups((current) =>
        current[family] === true ? current : { ...current, [family]: true },
      );
    }
  }, [state.selected, state.view]);
  const list = useRef<HTMLElement>(null),
    scroll = useRef(new Map<string, number>()),
    scrollKey = state.view + '/' + key;
  useLayoutEffect(() => {
    const element = list.current;
    if (!element) return;
    element.scrollTop = scroll.current.get(scrollKey) || 0;
    const selected = element.querySelector<HTMLElement>('[aria-pressed="true"]');
    if (selected?.getClientRects().length) {
      const bounds = element.getBoundingClientRect(),
        row = selected.getBoundingClientRect();
      if (row.top < bounds.top) element.scrollTop += row.top - bounds.top;
      else if (row.bottom > bounds.bottom) element.scrollTop += row.bottom - bounds.bottom;
    }
    return () => {
      scroll.current.set(scrollKey, element.scrollTop);
    };
  }, [scrollKey, state.selected]);
  const choose = (id: string, mobile = false) =>
    dispatch(
      { type: 'definition', id },
      mobile ? '#mobile-task-picker' : `[data-definition="${CSS.escape(id)}"]`,
    );
  const item = (unit: TaskUnit) => {
    const row = unit.entry,
      count = model.members(row).length,
      cases = model.items(row).filter((item) => item.kind === 'case'),
      tags: string[] = [];
    if (count > 1) tags.push(count + ' ' + t('variants'));
    else {
      if (edition(row)) tags.push(edition(row));
      if (cases.length) tags.push(cases.length + ' ' + t(cases.length === 1 ? 'case' : 'cases'));
    }
    if (unit.members.some(hasExample)) tags.push(t('Image example'));
    return (
      <button
        className="task-item"
        data-definition={row.id}
        data-task={unit.id}
        aria-pressed={unit.members.some((row) => row.id === state.selected)}
        key={unit.id}
        onClick={() => choose(row.id)}
      >
        <strong>{unit.title}</strong>
        {!!tags.length && <small>{tags.join(' · ')}</small>}
      </button>
    );
  };
  const groups = new Map<string, TaskUnit[]>();
  for (const unit of units) {
    const group = listGroup(unit.entry, state.view) || unit.entry.repo;
    if (!groups.has(group)) groups.set(group, []);
    groups.get(group)!.push(unit);
  }
  const seen = new Set<string>();
  return (
    <>
      <div className="mobile-task-selection">
        <label htmlFor="mobile-task-picker">
          {t('Choose a task')}{' '}
          <span>
            {units.length} {t(units.length === 1 ? 'entry' : 'entries')}
          </span>
        </label>
        <select
          id="mobile-task-picker"
          disabled={!units.length}
          value={
            units.find((unit) => unit.members.some((row) => row.id === state.selected))?.entry.id ||
            ''
          }
          onChange={(event) => choose(event.target.value, true)}
        >
          {[...groups].map(([label, group]) => (
            <optgroup label={label} key={label}>
              {group.map((unit) => (
                <option value={unit.entry.id} key={unit.id}>
                  {unit.title}
                </option>
              ))}
            </optgroup>
          ))}
          {!units.length && <option value="">{t('No matching tasks')}</option>}
        </select>
      </div>
      <nav
        ref={list}
        className="task-list"
        data-repository={scrollKey}
        aria-label={t('Entries in this selection')}
      >
        <div className="list-heading">
          {searching
            ? t('Matching entries')
            : state.lane === 'supporting'
              ? t('Supporting research')
              : t('Tasks')}{' '}
          <span>{units.length}</span>
        </div>
        {units.map((unit) => {
          const name = listGroup(unit.entry, state.view);
          if (
            !name ||
            allUnits.filter((other) => listGroup(other.entry, state.view) === name).length < 2
          )
            return item(unit);
          if (seen.has(name)) return null;
          seen.add(name);
          const children = units.filter((other) => listGroup(other.entry, state.view) === name),
            family = familyKey(unit.entry, state.view),
            active = children.some((other) =>
              other.members.some((row) => row.id === state.selected),
            ),
            open = searching || (openGroups[family] ?? active);
          return (
            <details
              className="task-family"
              data-family={family}
              key={family}
              open={open}
              onToggle={(event) => {
                const next = event.currentTarget.open;
                if (!searching && next !== open)
                  setOpenGroups((current) => ({ ...current, [family]: next }));
              }}
            >
              <summary>
                <span>{name}</span>
                <small>{children.length}</small>
              </summary>
              <div className="family-tasks">{children.map(item)}</div>
            </details>
          );
        })}
        {!units.length && (
          <p className="empty">{t('No tasks match this search in this repository.')}</p>
        )}
      </nav>
    </>
  );
}
