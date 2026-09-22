/** Payload contracts are generated from the canonical Python TypedDict module. */
import type { ExplorerData } from './contracts.generated';
export type * from './contracts.generated';
const record = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null && !Array.isArray(value);
function assert(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error('Invalid Task Explorer data: ' + message);
}
/** Reject incompatible or incomplete builds before any interactive UI is mounted. */
export function parseExplorerData(raw: string): ExplorerData {
  const value: unknown = JSON.parse(raw);
  assert(record(value) && value.schema_version === 1, 'expected schema_version 1');
  assert(
    Array.isArray(value.entries) && value.entries.length > 0,
    'entries must be a nonempty array',
  );
  assert(
    record(value.inventory) && record(value.taxonomy) && record(value.local_sources),
    'inventory, taxonomy and local_sources are required',
  );
  const ids = new Set<string>();
  for (const entry of value.entries) {
    assert(record(entry), 'each entry must be an object');
    for (const field of [
      'id',
      'title',
      'repo',
      'category',
      'agent_work',
      'goal',
      'value',
      'raw',
      'helpers',
      'output',
      'challenge',
      'spec',
      'tools',
      'score',
      'reference',
      'families',
      'gap',
      'case_note',
    ])
      assert(typeof entry[field] === 'string', 'entry.' + field + ' must be a string');
    assert(
      Array.isArray(entry.modalities) &&
        entry.modalities.length > 0 &&
        entry.modalities.every((modality) => typeof modality === 'string'),
      'entry.modalities must contain authored IDs',
    );
    const id = entry.id as string;
    assert(!ids.has(id), 'duplicate entry ' + id);
    ids.add(id);
    assert(
      Array.isArray(entry.variants) && entry.variants.length > 0,
      id + ' needs assistance conditions',
    );
    for (const variant of entry.variants)
      assert(
        record(variant) &&
          ['name', 'helper', 'remaining'].every((key) => typeof variant[key] === 'string'),
        id + ' has an invalid condition',
      );
    assert(
      record(entry.visuals) &&
        ['input', 'helpers', 'answer'].every(
          (key) => typeof (entry.visuals as Record<string, unknown>)[key] === 'string',
        ),
      id + ' has invalid visual roles',
    );
    assert(
      Array.isArray(entry.sources) &&
        entry.sources.every(
          (source) =>
            Array.isArray(source) &&
            source.length === 2 &&
            source.every((part) => typeof part === 'string'),
        ),
      id + ' has invalid sources',
    );
  }
  if (value.datasets !== undefined)
    assert(
      record(value.datasets) &&
        Array.isArray(value.datasets.records) &&
        record(value.datasets.coverage),
      'invalid dataset collection',
    );
  return value as unknown as ExplorerData;
}
