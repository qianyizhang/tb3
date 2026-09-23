import { useRef, useState } from 'react';
import { SourceLink } from './content';
import { copyText, useLocale, wsiBoundary } from './locale';
import type { ExplorerModel } from './model';
import type { DatasetRecord, DatasetSnapshot, SnapshotPanel } from './types';
function DatasetDiagram({ dataset }: { dataset: DatasetRecord }) {
  const { t } = useLocale();
  return (
    <figure className="dataset-diagram">
      <figcaption>
        {t('How to read this dataset')} <span>{t('Conceptual structure')}</span>
      </figcaption>
      <div className="dataset-flow">
        <section>
          <svg viewBox="0 0 160 105" role="img" aria-label="Stack of source image planes">
            <g fill="#e9f3f3" stroke="#347d83" strokeWidth="2">
              <path d="M20 62 86 25 140 55 74 92Z" />
              <path d="M20 48 86 11 140 41 74 78Z" />
              <path d="M20 34 86 0 140 27 74 64Z" />
            </g>
            <path
              d="m44 35 40-21 34 17-42 21Z"
              fill="none"
              stroke="#347d83"
              strokeDasharray="4 3"
            />
          </svg>
          <h3>{t('Original data')}</h3>
          <p>{dataset.image_description}</p>
        </section>
        <div className="dataset-arrow" aria-hidden="true">
          +
        </div>
        <section>
          <svg viewBox="0 0 160 105" role="img" aria-label="Annotations linked to data">
            <g fill="none" stroke="#a66a29" strokeWidth="2">
              <rect x="29" y="8" width="105" height="84" rx="8" />
              <path d="M49 30h65M49 51h65M49 72h65" />
              <circle cx="39" cy="30" r="3" />
              <circle cx="39" cy="51" r="3" />
              <circle cx="39" cy="72" r="3" />
            </g>
          </svg>
          <h3>{t('Annotations / reference')}</h3>
          <p>{dataset.annotation_description}</p>
        </section>
      </div>
      <p className="dataset-unit">
        <strong>{t('One sample:')}</strong> {dataset.sample_unit}.{' '}
        {t('Repeated views and conditions may reuse that sample.')}
      </p>
    </figure>
  );
}
function Snapshot({ snapshot }: { snapshot: DatasetSnapshot | undefined }) {
  const { t } = useLocale();
  const dialog = useRef<HTMLDialogElement>(null),
    [enlarged, setEnlarged] = useState<SnapshotPanel>(),
    [zoom, setZoom] = useState(100);
  if (!snapshot)
    return (
      <p className="dataset-no-example">
        {t('No frozen sample has been documented for this source.')}
      </p>
    );
  const inputs = snapshot.panels.filter((panel) => panel.role === 'input'),
    references = snapshot.panels.filter((panel) => panel.role === 'reference'),
    metadata = snapshot.panels.filter((panel) => panel.role === 'metadata');
  const open = (panel: SnapshotPanel) => {
    setEnlarged(panel);
    setZoom(100);
    dialog.current?.showModal();
  };
  const panel = (row: SnapshotPanel) => (
    <figure
      className="snapshot-panel"
      data-snapshot-role={row.role}
      key={snapshot.panels.indexOf(row)}
    >
      {row.image_url ? (
        <button
          className="snapshot-image"
          data-snapshot-enlarge={snapshot.panels.indexOf(row)}
          aria-label={'Enlarge ' + snapshot.sample_id + ' ' + row.role + ' snapshot'}
          onClick={() => open(row)}
        >
          <img
            loading="lazy"
            src={row.image_url}
            alt={snapshot.sample_id + ' · ' + row.role + ' · ' + row.caption}
          />
          <span>{t('Enlarge snapshot ↗')}</span>
        </button>
      ) : row.text ? (
        <pre className="snapshot-text">{row.text}</pre>
      ) : (
        <p className="snapshot-missing">
          {t('Frozen image unavailable in this build:')} <code>{row.path}</code>.{' '}
          {t('Recover the pinned snapshot; this is not an empty scan.')}
        </p>
      )}
      <figcaption>{row.caption}</figcaption>
    </figure>
  );
  const status = {
    paired: t('Sample + reference'),
    'input-only': t('Sample available · paired GT unavailable'),
    'reference-only': t('Reference available · image unavailable'),
    unavailable: t('Source screen · imaging not acquired'),
  }[snapshot.status];
  return (
    <section className="dataset-snapshot" data-snapshot-status={snapshot.status}>
      <div className="snapshot-heading">
        <div>
          <div className="eyebrow">{t('Frozen source snapshot')}</div>
          <h2>{snapshot.sample_id.length > 20 ? t('Selected example') : snapshot.sample_id}</h2>
        </div>
        <span className="snapshot-state">{status}</span>
      </div>
      <p>{snapshot.summary}</p>
      {inputs.length ? (
        inputs.map(panel)
      ) : metadata.length ? (
        metadata.map(panel)
      ) : (
        <div className="snapshot-missing">
          {t('The source image was not retained. Available annotations can be inspected below.')}
        </div>
      )}
      {references.length ? (
        <details className="dataset-reference">
          <summary>{t('Reveal ground truth / source reference')}</summary>
          <p className="snapshot-reference-note">{snapshot.reference_note}</p>
          {references.map(panel)}
        </details>
      ) : (
        <p className="snapshot-reference-note">
          <strong>{t('Ground-truth availability:')}</strong> {snapshot.reference_note}
        </p>
      )}
      <details className="snapshot-provenance">
        <summary>{t('Snapshot provenance and exact source files')}</summary>
        <p>
          {t(
            'These frozen views preserve the selection and reference limits. Opening the page does not run a model or change task inputs.',
          )}
        </p>
        <p>{t('Exact paths and checksums are included in full metadata below.')}</p>
      </details>
      <dialog
        ref={dialog}
        id="dataset-image-dialog"
        className="snapshot-dialog"
        aria-label="Enlarged source snapshot"
        onClick={(event) => {
          if (event.target === event.currentTarget) dialog.current?.close();
        }}
      >
        <div className="snapshot-dialog-toolbar">
          <label>
            Zoom{' '}
            <input
              id="snapshot-zoom"
              type="range"
              min="100"
              max="250"
              value={zoom}
              step="25"
              onChange={(event) => setZoom(Number(event.target.value))}
            />
          </label>
          <button id="snapshot-close" onClick={() => dialog.current?.close()}>
            Close
          </button>
        </div>
        <div className="snapshot-dialog-image">
          <img
            id="snapshot-large"
            src={enlarged?.image_url}
            alt={enlarged?.caption || ''}
            style={{ width: zoom + '%' }}
          />
        </div>
        <p id="snapshot-large-caption">{enlarged?.caption}</p>
      </dialog>
    </section>
  );
}
function DatasetDetail({ dataset, model }: { dataset: DatasetRecord; model: ExplorerModel }) {
  const { locale, t } = useLocale();
  const [copyStatus, setCopyStatus] = useState('');
  const tasks = dataset.task_ids
      .map((id) => model.byId.get(id))
      .filter((entry) => entry !== undefined),
    links = (dataset.links || []).filter((link) => /^https?:\/\//.test(link.path));
  const snapshot = model.data.datasets?.previews?.[dataset.id];
  const metadata =
    JSON.stringify(
      {
        dataset,
        snapshot: snapshot && {
          ...snapshot,
          panels: snapshot.panels.map(({ image_url: _image, ...panel }) => panel),
        },
      },
      null,
      2,
    ) + '\n';
  return (
    <article className="dataset-detail" data-dataset={dataset.id}>
      <div className="eyebrow">
        {t('Dataset')} · {dataset.modality}
      </div>
      <h1>{dataset.title}</h1>
      <p className="dataset-lead">{dataset.summary}</p>
      {wsiBoundary(dataset.task_ids[0] || '', locale) && (
        <aside className="reading-boundary">
          <strong>{t('Page caveat')}</strong>
          <p>{wsiBoundary(dataset.task_ids[0] || '', locale)}</p>
        </aside>
      )}
      {locale === 'zh-CN' && !dataset.locales?.['zh-CN'] && (
        <p className="translation-notice" lang="zh-CN">
          {t('English source text')}
        </p>
      )}
      <Snapshot key={dataset.id} snapshot={snapshot} />
      <details className="dataset-structure">
        <summary>{t('Understand the data structure')}</summary>
        <DatasetDiagram dataset={dataset} />
      </details>
      <section className="dataset-reference-scope">
        <h2>{t('What the reference can establish')}</h2>
        <p>{dataset.reference_note}</p>
      </section>
      <section>
        <h2>{t('Selected samples & their use')}</h2>
        {!dataset.task_ids[0]?.startsWith('wsi-') ? (
          <p className="fine">
            {t(
              'Selections can overlap. These are documented source selections, not a count of independent patients or successful trials.',
            )}
          </p>
        ) : null}
        {dataset.sample_sets.map((sample, index) => (
          <section className="dataset-sample" key={index}>
            <div>
              <h3>{sample.label}</h3>
              <span className="dataset-role">{t(sample.role)}</span>
            </div>
            {sample.sample_ids.some((id) => id.length <= 20) && (
              <p className="sample-identities">
                {sample.sample_ids
                  .filter((id) => id.length <= 20)
                  .map((id) => (
                    <code key={id}>{id} </code>
                  ))}
              </p>
            )}
            <p>{sample.note}</p>
          </section>
        ))}
      </section>
      <section>
        <h2>{t('Tasks using or explaining this source')}</h2>
        {tasks.length ? (
          <div className="dataset-task-links">
            {tasks.map((entry) => (
              <a href={'#' + entry.id + '/0/overview'} key={entry.id}>
                {entry.title} →
              </a>
            ))}
          </div>
        ) : (
          <p>{t('Source review only; no task brief is linked.')}</p>
        )}
        <details>
          <summary>
            {dataset.experiments.length} {t('linked experiment records')}
          </summary>
          <ul>
            {dataset.experiments.map((experiment) => (
              <li key={experiment.id}>
                {experiment.title} <code>{experiment.id}</code>
              </li>
            ))}
          </ul>
        </details>
      </section>
      <details className="dataset-recovery">
        <summary>{t('Release, access & recovery')}</summary>
        <p>{dataset.version_note}</p>
        <p>{dataset.terms_note}</p>
        {dataset.access_note && <p>{dataset.access_note}</p>}
        {links.map((link) => (
          <p key={link.path}>
            <SourceLink url={link.path}>{link.label} ↗</SourceLink>
          </p>
        ))}
        {!!dataset.documentation_gaps?.length && (
          <>
            <h3>{t('Open documentation or reference gaps')}</h3>
            <ul>
              {dataset.documentation_gaps.map((gap) => (
                <li key={gap}>{gap}</li>
              ))}
            </ul>
          </>
        )}
        <div className="metadata-actions">
          <button
            className="quiet"
            onClick={async () =>
              setCopyStatus((await copyText(metadata)) ? t('Metadata copied') : t('Copy failed'))
            }
          >
            {t('Copy full metadata')}
          </button>
          <a
            id="dataset-download"
            download={dataset.id + '-metadata.json'}
            href={'data:application/json;charset=utf-8,' + encodeURIComponent(metadata)}
          >
            {t('Download full metadata')}
          </a>
          <span role="status" aria-live="polite">
            {copyStatus}
          </span>
        </div>
      </details>
    </article>
  );
}
export function Datasets({
  model,
  id,
  taskRoute,
}: {
  model: ExplorerModel;
  id: string;
  taskRoute: string;
}) {
  const { locale, t } = useLocale();
  const [search, setSearch] = useState(''),
    searchInput = useRef<HTMLInputElement>(null);
  const records = model.data.datasets?.records || [],
    dataset = records.find((record) => record.id === id),
    query = search.trim().toLowerCase();
  const matches = records.filter((record) =>
      JSON.stringify([
        record.title,
        record.modality,
        record.summary,
        record.sample_sets.map((sample) => sample.sample_ids),
      ])
        .toLowerCase()
        .includes(query),
    ),
    ids = new Set(matches.map((record) => record.id));
  const clear = () => {
    setSearch('');
    searchInput.current?.focus();
  };
  return (
    <>
      <div className="dataset-top">
        <a href={taskRoute}>← {t('Back to Tasks')}</a>
        {id ? <a href="#datasets">{t('All datasets →')}</a> : <span>{t('Source library')}</span>}
      </div>
      <div className="dataset-workspace">
        <aside className="dataset-sidebar" aria-label={t('Find a dataset')}>
          <div className="browser-heading">
            <span className="eyebrow">{t('Source library')}</span>
            <button className="text-button" id="dataset-reset" hidden={!query} onClick={clear}>
              {t('Reset')}
            </button>
          </div>
          <label htmlFor="dataset-search">{t('Search datasets')}</label>
          <input
            ref={searchInput}
            id="dataset-search"
            type="search"
            placeholder={t('Name, modality, sample ID…')}
            autoComplete="off"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
          <p id="dataset-count" className="search-count" role="status" aria-live="polite">
            {matches.length} {t(matches.length === 1 ? 'source' : 'sources')}
            {query ? t(' match your search') : t(' in this collection')}
          </p>
          <nav id="dataset-nav" aria-label={t('Datasets')}>
            {matches.map((record) => (
              <a
                key={record.id}
                href={'#datasets/' + encodeURIComponent(record.id)}
                aria-current={record.id === id ? 'page' : undefined}
              >
                {record.title}
                <small>{record.modality}</small>
              </a>
            ))}
            {!matches.length && (
              <p className="empty">{t('No matching dataset or sample. Try a broader term.')}</p>
            )}
          </nav>
        </aside>
        <div id="dataset-content">
          {dataset ? (
            <DatasetDetail model={model} dataset={dataset} />
          ) : id ? (
            <section className="empty-state">
              <div className="eyebrow">{t('Source library')}</div>
              <h1>{t('Dataset not found')}</h1>
              <p>{t('Choose a source from the dataset list, or return to the full collection.')}</p>
              <a className="button button-secondary" href="#datasets">
                {t('View all datasets')}
              </a>
            </section>
          ) : (
            <div className="dataset-intro">
              <div className="eyebrow">{t('Learn the data before the task')}</div>
              <h1>{t('Datasets')}</h1>
              <p className="dataset-lead">
                {t('Explore the images, annotations and selected samples behind the work.')}
              </p>
              {locale === 'zh-CN' && (
                <p className="translation-notice" lang="zh-CN">
                  目录中尚未翻译的来源条目保留英文原文；四条 WSI 路线已有中英双语。
                </p>
              )}
              <p className="dataset-collection-count">
                {records.length} {t('sources')} · {model.data.datasets?.coverage.experiments || 0}{' '}
                {t('linked medical experiment records')}
              </p>
              <div className="dataset-cards">
                {records.map((record) => {
                  const preview = model.data.datasets?.previews?.[record.id]?.panels.find(
                    (panel) => panel.role === 'input' && panel.image_url,
                  );
                  return (
                    <a
                      href={'#datasets/' + encodeURIComponent(record.id)}
                      data-dataset-card={record.id}
                      key={record.id}
                      hidden={!ids.has(record.id)}
                    >
                      {preview ? (
                        <div className="dataset-card-visual">
                          <img
                            loading="lazy"
                            className="dataset-card-preview"
                            src={preview.image_url}
                            alt={record.title + ' · ' + t('source snapshot')}
                          />
                        </div>
                      ) : (
                        <div className="dataset-card-placeholder">
                          <span>{t('Source documentation')}</span>
                          <small>{t('Explore samples and reference availability')}</small>
                        </div>
                      )}
                      <div className="dataset-card-copy">
                        <span>{record.modality}</span>
                        <h2>{record.title}</h2>
                        <p>{record.summary}</p>
                        <div className="dataset-card-action">
                          {t('Explore source')} <span aria-hidden="true">→</span>
                        </div>
                      </div>
                    </a>
                  );
                })}
              </div>
              <section
                className="dataset-empty empty-state"
                id="dataset-empty"
                hidden={!!matches.length}
              >
                <h2>{t('No matching datasets')}</h2>
                <p>{t('Try a dataset name, image type, or sample ID.')}</p>
                <button
                  className="button button-secondary"
                  id="dataset-clear-search"
                  onClick={clear}
                >
                  {t('Clear search')}
                </button>
              </section>
              <details className="dataset-glossary-guide">
                <summary>{t('How to read a dataset')}</summary>
                <div className="dataset-glossary">
                  <section>
                    <h2>{t('Image')}</h2>
                    <p>
                      {t(
                        'The acquired scan or generated input. Geometry and coordinates are part of the data.',
                      )}
                    </p>
                  </section>
                  <section>
                    <h2>{t('Annotation')}</h2>
                    <p>
                      {t(
                        'A mask marks voxels; a landmark marks a point; a correspondence links observations. Each has its own limits.',
                      )}
                    </p>
                  </section>
                  <section>
                    <h2>{t('Task use')}</h2>
                    <p>
                      {t(
                        'A reference can be hidden for scoring or supplied as help. The task condition decides which.',
                      )}
                    </p>
                  </section>
                </div>
              </details>
              <p className="dataset-coverage-note fine">
                {model.data.datasets?.coverage.scope || ''}
              </p>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
