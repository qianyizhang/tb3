/** Python owns the read-only payload contract; this file owns browser state. */
import type { OverviewData, ResearchRecord, VocabularyTerm } from './contracts.generated';
export type {
  OverviewData,
  OverviewVocabulary,
  ResearchRecord,
  VocabularyTerm,
} from './contracts.generated';

export interface OverviewRoute {
  search: string;
  group: string;
  kind: string;
  status: string;
  record: string;
}

export const initialRoute: OverviewRoute = {
  search: '',
  group: '',
  kind: 'overview',
  status: '',
  record: '',
};

export const recordKinds = [
  ['overview', 'Ideas, experiments & findings'],
  ['', 'Everything'],
  ['idea', 'Ideas'],
  ['decision', 'Decisions'],
  ['experiment', 'Experiments'],
  ['attempt', 'Attempts'],
  ['evaluation', 'Evaluations'],
  ['finding', 'Findings'],
  ['issue', 'Issues'],
  ['review', 'Reviews'],
  ['export', 'Exports'],
  ['plan', 'Plans'],
  ['dataset', 'Datasets'],
] as const;

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function isTerm(value: unknown): value is VocabularyTerm {
  return isObject(value) && typeof value.label === 'string' && typeof value.definition === 'string';
}

function isStringList(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((entry: unknown) => typeof entry === 'string');
}

/** Reject a broken presentation contract instead of showing a partial, misleading record. */
export function parseOverviewData(value: unknown): OverviewData {
  if (
    !isObject(value) ||
    value.schema_version !== 1 ||
    typeof value.local_media !== 'boolean' ||
    !Array.isArray(value.records) ||
    !isObject(value.vocabulary)
  ) {
    throw new Error('Invalid research record payload');
  }
  const vocabulary = value.vocabulary;
  if (
    !isObject(vocabulary.axes) ||
    !Object.values(vocabulary.axes).every(
      (axis) => isObject(axis) && isObject(axis.values) && Object.values(axis.values).every(isTerm),
    ) ||
    !isObject(vocabulary.context_badges) ||
    !Object.values(vocabulary.context_badges).every(isTerm) ||
    !isObject(vocabulary.display_rules) ||
    !Object.values(vocabulary.display_rules).every(
      (rule) => typeof rule === 'string' || isStringList(rule),
    )
  ) {
    throw new Error('Invalid research status vocabulary');
  }
  const identifiers = new Set<string>();
  for (const row of value.records) {
    if (
      !isObject(row) ||
      typeof row.id !== 'string' ||
      typeof row.kind !== 'string' ||
      !isObject(row.current) ||
      identifiers.has(row.id)
    ) {
      throw new Error('Invalid research record');
    }
    identifiers.add(row.id);
    if (
      row.portable_links !== undefined &&
      (!Array.isArray(row.portable_links) ||
        !row.portable_links.every(
          (link: unknown) =>
            isObject(link) &&
            typeof link.label === 'string' &&
            (link.url == null || typeof link.url === 'string'),
        ))
    ) {
      throw new Error('Invalid research record links');
    }
    if (row.experiment_ids !== undefined && !isStringList(row.experiment_ids)) {
      throw new Error('Invalid experiment references');
    }
    if (
      row.current.review_flags !== undefined &&
      (!Array.isArray(row.current.review_flags) ||
        !row.current.review_flags.every(
          (flag: unknown) =>
            isObject(flag) &&
            typeof flag.experiment_id === 'string' &&
            typeof flag.assessment === 'string' &&
            typeof flag.reason === 'string',
        ))
    ) {
      throw new Error('Invalid research review flags');
    }
  }
  if (value.task_explorer_url != null && typeof value.task_explorer_url !== 'string') {
    throw new Error('Invalid Task Explorer link');
  }
  return value as unknown as OverviewData;
}

export function recordText(value: unknown): string {
  if (value === undefined || value === null) return '';
  return typeof value === 'string' ? value : JSON.stringify(value);
}

export function readOverviewRoute(search: string, data: OverviewData): OverviewRoute {
  const parameters = new URLSearchParams(search);
  const route = {
    search: parameters.get('q') ?? '',
    group: parameters.get('group') ?? '',
    kind: parameters.get('kind') ?? 'overview',
    status: parameters.get('status') ?? '',
    record: parameters.get('record') ?? '',
  };
  if (!data.records.some((row) => row.kind === 'group' && row.id === route.group)) route.group = '';
  if (!recordKinds.some(([kind]) => kind === route.kind)) route.kind = 'overview';
  if (route.status && route.status !== 'attention') {
    const [axis, code] = route.status.split(':');
    if (!axis || !code || !data.vocabulary.axes[axis]?.values[code]) route.status = '';
  }
  return route;
}

export function overviewUrl(href: string, route: OverviewRoute): URL {
  const url = new URL(href);
  const fields = { search: 'q', group: 'group', kind: 'kind', status: 'status', record: 'record' };
  for (const [field, parameter] of Object.entries(fields)) {
    const key = field as keyof OverviewRoute;
    if (route[key] !== initialRoute[key]) url.searchParams.set(parameter, route[key]);
    else url.searchParams.delete(parameter);
  }
  return url;
}

export function filterRecords(records: ResearchRecord[], route: OverviewRoute): ResearchRecord[] {
  const words = route.search.toLowerCase().split(/\s+/).filter(Boolean);
  return records.filter((row) => {
    if (route.group && row.group_id !== route.group && row.id !== route.group) return false;
    if (route.status === 'attention' && (row.kind !== 'experiment' || !row.current.attention)) {
      return false;
    }
    if (
      route.status !== 'attention' &&
      route.kind &&
      !(route.kind === 'overview'
        ? ['idea', 'experiment', 'finding'].includes(row.kind)
        : row.kind === route.kind)
    ) {
      return false;
    }
    if (!words.every((word) => JSON.stringify(row).toLowerCase().includes(word))) return false;
    if (route.status && route.status !== 'attention') {
      const [axis, code] = route.status.split(':');
      if (!axis || row.current[axis] !== code) return false;
    }
    return true;
  });
}
