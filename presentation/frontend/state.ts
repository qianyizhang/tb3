import { groupId, hasExample, inScope, navKey, supporting, type ExplorerModel } from './model';
import type { BrowseView, ResearchLane, TaskEntry, TaskTab, VisualRole } from './types';
export interface ExplorerState {
  selected: string;
  selectedItem: string;
  condition: number;
  tab: TaskTab;
  visual: VisualRole;
  source: string;
  view: BrowseView;
  lane: ResearchLane;
  work: string;
  modality: string;
  query: string;
  dataset: string | null;
}
export type ExplorerAction =
  | { type: 'route'; hash: string }
  | { type: 'definition' | 'variant' | 'item'; id: string }
  | { type: 'tab'; tab: TaskTab }
  | { type: 'source'; source: string }
  | { type: 'condition'; condition: number }
  | { type: 'visual'; visual: VisualRole }
  | { type: 'search'; query: string }
  | { type: 'filters'; view: BrowseView; lane: ResearchLane; work: string; modality: string }
  | { type: 'reset' };
const canonicalTab = (value = ''): TaskTab =>
  (({ brief: 'overview', catalogue: 'overview', contract: 'requirements' })[value] ||
    value ||
    'overview') as TaskTab;
export function initialState(model: ExplorerModel): ExplorerState {
  return {
    selected: model.data.entries[0]!.id,
    selectedItem: '',
    condition: 0,
    tab: 'overview',
    visual: 'input',
    source: '',
    view: 'capability',
    lane: 'tasks',
    work: '',
    modality: '',
    query: '',
    dataset: null,
  };
}
export function taskRoute(state: ExplorerState, model: ExplorerModel) {
  const entry = model.get(state.selected),
    item = model.items(entry).find((row) => row.id === state.selectedItem);
  const path = item
    ? `${groupId(entry)}/task/${encodeURIComponent(item.id)}/${state.condition}/${state.tab}`
    : `${entry.id}/${state.condition}/${state.tab}`;
  const params = new URLSearchParams({ view: state.view, lane: state.lane });
  if (state.work) params.set('work', state.work);
  if (state.modality) params.set('modality', state.modality);
  if (state.source && state.tab === 'sources') params.set('source', state.source);
  return '#' + path + '?' + params;
}
export function explorerReducer(
  model: ExplorerModel,
  state: ExplorerState,
  action: ExplorerAction,
): ExplorerState {
  const choose = (id: string): ExplorerState => ({
    ...state,
    selected: id,
    selectedItem: '',
    source: '',
    condition: 0,
    tab: 'overview',
    visual: 'input',
    dataset: null,
  });
  const withItem = (base: ExplorerState, id: string) => {
    const item = model.repository(model.get(base.selected))?.items.find((row) => row.id === id);
    return item?.brief_id
      ? {
          ...base,
          selected: item.brief_id,
          selectedItem: item.id,
          source: '',
          condition: item.condition_index || 0,
          visual: 'input' as const,
        }
      : base;
  };
  switch (action.type) {
    case 'route': {
      if (/^#datasets(?:\/|$)/.test(action.hash)) {
        let id = '';
        try {
          id = decodeURIComponent(action.hash.slice(1).split('?')[0]!.split('/')[1] || '');
        } catch {
          id = 'invalid-route';
        }
        return { ...state, dataset: id };
      }
      const [path = '', query = ''] = action.hash.slice(1).split('?'),
        parts = path.split('/'),
        params = new URLSearchParams(query);
      let next = {
        ...state,
        ...choose(model.byId.has(parts[0] || '') ? parts[0]! : model.data.entries[0]!.id),
      };
      let requested: string | undefined;
      if (parts[1] === 'task' || parts[1] === 'catalogue') {
        try {
          next = withItem(next, decodeURIComponent(parts[2] || ''));
        } catch {
          /* Keep a valid task for malformed legacy links. */
        }
        requested = parts[1] === 'task' ? parts[3] : undefined;
        next.tab = canonicalTab(parts[1] === 'task' ? parts[4] : 'overview');
      } else {
        requested = parts[1];
        next.tab = canonicalTab(parts[2]);
      }
      const entry = model.get(next.selected),
        lane = params.get('lane'),
        work = params.get('work') || '';
      next.view = params.get('view') === 'repository' ? 'repository' : 'capability';
      next.lane =
        lane === 'tasks' || lane === 'supporting' || lane === 'all'
          ? lane
          : supporting(entry)
            ? 'supporting'
            : 'tasks';
      next.work = model.data.taxonomy.agent_work?.[work] ? work : '';
      const requestedModality = params.get('modality') || '';
      const modality = model.data.taxonomy.modalities?.[requestedModality] ? requestedModality : '';
      // An empty filtered collection still has a stable return task in its URL.
      // Preserve all valid filters on reload/back; an ordinary incompatible task
      // link clears filters only when the requested collection has matching tasks.
      const emptySelection =
        !!modality &&
        !model.data.entries.some((row) => inScope(row, next.lane, next.work, modality));
      next.modality = emptySelection || entry.modalities.includes(modality) ? modality : '';
      if (!emptySelection && !inScope(entry, next.lane, next.work)) {
        next.lane = supporting(entry) ? 'supporting' : 'tasks';
        next.work = '';
      }
      if (!model.match(entry, next.query.trim().toLowerCase())) next.query = '';
      const condition = Number(requested);
      if (requested !== undefined && Number.isInteger(condition))
        next.condition = Math.max(0, Math.min(condition, entry.variants.length - 1));
      if (
        !['overview', 'requirements', 'examples', 'sources'].includes(next.tab) ||
        (next.tab === 'examples' && !hasExample(entry))
      )
        next.tab = 'overview';
      const source = params.get('source');
      next.source =
        next.tab === 'sources' &&
        source &&
        entry.sources.some(([, path]) => model.data.local_sources[path]?.sha256 === source)
          ? source
          : '';
      return next;
    }
    case 'definition':
      return choose(action.id);
    case 'variant': {
      const entry = model.get(action.id),
        previous = model.get(state.selected);
      return {
        ...state,
        selected: action.id,
        selectedItem: '',
        source: '',
        visual: 'input',
        condition: Math.max(
          0,
          entry.variants.findIndex(
            (variant) => variant.name === previous.variants[state.condition]!.name,
          ),
        ),
        tab: state.tab === 'examples' && !hasExample(entry) ? 'overview' : state.tab,
        query: model.match(entry, state.query.trim().toLowerCase()) ? state.query : '',
        modality: entry.modalities.includes(state.modality) ? state.modality : '',
      };
    }
    case 'item':
      return action.id
        ? withItem(state, action.id)
        : { ...state, selectedItem: '', condition: 0, visual: 'input' };
    case 'tab':
      return { ...state, tab: action.tab, source: '' };
    case 'source':
      return { ...state, source: action.source, tab: 'sources' };
    case 'visual':
      return { ...state, visual: action.visual };
    case 'condition': {
      const items = model.items(model.get(state.selected)),
        current = items.find((item) => item.id === state.selectedItem),
        linked = items.filter((item) => (item.condition_index || 0) === action.condition);
      return {
        ...state,
        condition: action.condition,
        visual: 'input',
        selectedItem:
          current && (current.condition_index || 0) !== action.condition
            ? linked.length === 1
              ? linked[0]!.id
              : ''
            : state.selectedItem,
      };
    }
    case 'search': {
      const next = { ...state, query: action.query };
      if (model.match(model.get(state.selected), action.query.trim().toLowerCase())) return next;
      const first = model.data.entries.find(
        (entry) =>
          inScope(entry, state.lane, state.work, state.modality) &&
          model.match(entry, action.query.trim().toLowerCase()),
      );
      return first ? { ...choose(first.id), query: action.query } : next;
    }
    case 'filters': {
      const next = {
        ...state,
        view: action.view,
        lane: action.lane,
        query: '',
        work: action.lane === 'supporting' ? '' : action.work,
        modality: action.modality,
      };
      if (inScope(model.get(state.selected), next.lane, next.work, next.modality)) return next;
      const entry = model.get(state.selected),
        matches = model.data.entries.filter((row) =>
          inScope(row, next.lane, next.work, next.modality),
        );
      let first: TaskEntry | undefined =
        matches.find((row) => navKey(row, next.view) === navKey(entry, next.view)) || matches[0];
      if (!first && next.modality) return next;
      if (!first) {
        next.work = '';
        first = model.data.entries.find((row) => inScope(row, next.lane, ''));
      }
      return {
        ...choose(first?.id || model.data.entries[0]!.id),
        view: next.view,
        lane: next.lane,
        work: next.work,
        modality: next.modality,
        query: '',
      };
    }
    case 'reset':
      return {
        ...(supporting(model.get(state.selected))
          ? choose(model.data.entries.find((entry) => !supporting(entry))!.id)
          : state),
        lane: 'tasks',
        work: '',
        modality: '',
        query: '',
      };
  }
}
export type Dispatch = (action: ExplorerAction, focus?: string) => void;
