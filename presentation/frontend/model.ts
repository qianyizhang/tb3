import type { BrowseView, ExplorerData, InventoryItem, ResearchLane, TaskEntry } from './types';
export const groupId = (entry: TaskEntry) => entry.repository_id || entry.id;
export const supporting = (entry: TaskEntry) => (entry.role || 'task') !== 'task';
export const hasExample = (entry: TaskEntry) =>
  Object.values(entry.visuals).some((value) => /<img\b/.test(value));
export const edition = (entry: TaskEntry) =>
  entry.id.startsWith('automedbench-full-')
    ? 'Full release'
    : entry.id === 'automedbench-tsg'
      ? 'Lite release'
      : entry.id === 'automedbench'
        ? 'Domain branch'
        : '';
export const inScope = (entry: TaskEntry, lane: ResearchLane, work: string, modality = '') =>
  (lane === 'all' || supporting(entry) === (lane === 'supporting')) &&
  (!work || entry.agent_work === work) &&
  (!modality || entry.modalities.includes(modality));
export const navKey = (entry: TaskEntry, view: BrowseView) =>
  view === 'repository' ? groupId(entry) : entry.category;
export const listGroup = (entry: TaskEntry, view: BrowseView) =>
  view === 'capability' ? entry.repo : entry.nav_group || '';
export const familyKey = (entry: TaskEntry, view: BrowseView) =>
  view + '/' + navKey(entry, view) + '/' + listGroup(entry, view);
export interface TaskUnit {
  id: string;
  entry: TaskEntry;
  members: TaskEntry[];
  title: string;
}
export function createModel(data: ExplorerData) {
  const byId = new Map(data.entries.map((entry) => [entry.id, entry]));
  const get = (id: string) => byId.get(id) || data.entries[0]!;
  const repository = (entry: TaskEntry) =>
    data.inventory.repositories?.find((repo) => repo.id === groupId(entry));
  const items = (entry: TaskEntry) =>
    (repository(entry)?.items || []).filter((item) => item.brief_id === entry.id);
  const family = (entry: TaskEntry) =>
    entry.task_family ? data.task_families?.[entry.task_family] : undefined;
  const members = (entry: TaskEntry) =>
    entry.task_family
      ? data.entries.filter(
          (other) => groupId(other) === groupId(entry) && other.task_family === entry.task_family,
        )
      : [entry];
  const category = (id: string) => data.taxonomy.categories?.[id] || { title: id, description: '' };
  const match = (entry: TaskEntry, query: string) =>
    JSON.stringify([
      entry.category,
      category(entry.category).title,
      entry.modalities,
      entry.modalities.map((modality) => data.taxonomy.modalities?.[modality]),
      entry.operations,
      entry.owner_group,
      entry.studies,
      entry.title,
      entry.nav_group,
      entry.nav_label,
      family(entry)?.title,
      entry.goal,
      entry.raw,
      entry.helpers,
      entry.output,
      entry.repo,
    ])
      .toLowerCase()
      .includes(query) ||
    items(entry).some((item) =>
      JSON.stringify([
        item.id,
        item.title,
        item.family,
        item.definition,
        item.condition,
        item.case_context?.label,
        item.case_context?.facts,
      ])
        .toLowerCase()
        .includes(query),
    );
  const units = (entries: TaskEntry[], selected = '') => {
    const groups = new Map<string, TaskUnit>();
    for (const entry of entries) {
      const key = groupId(entry) + '/' + (entry.task_family || entry.id);
      if (!groups.has(key))
        groups.set(key, {
          id: entry.task_family || entry.id,
          entry,
          members: [],
          title: family(entry)?.title || entry.nav_label || entry.title,
        });
      const unit = groups.get(key)!;
      unit.members.push(entry);
      if (entry.id === selected) unit.entry = entry;
    }
    return [...groups.values()];
  };
  const label = (item: InventoryItem, entry: TaskEntry) => {
    if (item.case_context?.label) return item.case_context.label;
    if (item.id.startsWith('clinical_trial_matching_task_'))
      return 'Case ' + item.id.split('_').at(-1);
    if (item.id.startsWith('ct_abnormality_')) return item.id.replace('ct_abnormality_', '');
    if (item.id.startsWith('tumor_area_selection_'))
      return 'Slide ' + Number(item.id.split('_').at(-1));
    if (item.id.startsWith('xray_report_correction_case_'))
      return 'Case ' + Number(item.id.split('_').at(-1));
    if (item.id.startsWith('lite-case-')) return item.id.slice(10);
    if (item.kind === 'gallery entry') return 'Gallery';
    if (item.kind === 'code package') return 'Domain branch';
    if (item.id.startsWith('full-release-')) return 'Full release';
    if (item.id.startsWith('lite-release-')) return 'Lite release';
    if (
      items(entry).length > 1 &&
      new Set(items(entry).map((row) => row.condition_index || 0)).size > 1
    )
      return entry.variants[item.condition_index || 0]!.name;
    return item.title;
  };
  return { data, byId, get, repository, items, family, members, category, match, units, label };
}
export type ExplorerModel = ReturnType<typeof createModel>;
