import styles from './task-detail.module.css';
import { Fragment, useState } from 'react';
import { Box, Field, Markup, SourceLink, TaskScene } from './content';
import { copyText, useLocale, wsiBoundary } from './locale';
import { edition, hasExample, type ExplorerModel } from './model';
import type { Dispatch, ExplorerState } from './state';
import type { TaskEntry, TaskTab, VisualRole } from './types';
interface DetailProps {
  model: ExplorerModel;
  state: ExplorerState;
  dispatch: Dispatch;
}
function ImageNotice({
  model,
  entry,
  dispatch,
}: {
  model: ExplorerModel;
  entry: TaskEntry;
  dispatch: Dispatch;
}) {
  const { t } = useLocale();
  const notice = entry.sources.find(([label]) => label === 'Preview image notices'),
    source = notice && model.data.local_sources[notice[1]];
  return source?.sha256 ? (
    <p className="fine">
      <button
        className="text-button"
        data-notice={source.sha256}
        onClick={() => dispatch({ type: 'source', source: source.sha256! }, '#source-heading')}
      >
        {t('Image attribution, terms and derivation')}
      </button>
    </p>
  ) : null;
}
function TaskPicture({ model, state, dispatch }: DetailProps) {
  const { t } = useLocale();
  const entry = model.get(state.selected),
    illustrated = entry.example_case_id
      ? model.items(entry).find((item) => item.id === entry.example_case_id)
      : undefined;
  const exampleLabel = illustrated ? ' · ' + model.label(illustrated, entry) : '',
    native = /<img\b/.test(entry.visuals.input);
  const open = () => dispatch({ type: 'tab', tab: 'examples' }, '#tab-examples');
  const notice = <ImageNotice model={model} entry={entry} dispatch={dispatch} />;
  return (
    <>
      {native && (
        <figure className="task-picture native-preview">
          <figcaption>
            <span className="drawing-label">
              {t('Source-derived example')}
              {exampleLabel}
            </span>
            <button className="text-button" data-example-open onClick={open}>
              {t('Inspect example →')}
            </button>
          </figcaption>
          <Markup className="native-input" html={entry.visuals.input} />
          {notice}
        </figure>
      )}
      {entry.illustration ? (
        <figure className="task-picture conceptual" data-illustration={entry.illustration.kind}>
          <figcaption>
            <span className="drawing-label">{t('Animated task illustration')}</span>
            <span>{t('Illustrative model · not case-specific')}</span>
          </figcaption>
          <TaskScene entry={entry} />
        </figure>
      ) : null}
      {!!entry.missing_media?.length && (
        <div className="preview-unavailable">
          <Markup html={entry.visuals.input} />
          {notice}
        </div>
      )}
    </>
  );
}
function CaseSelector({ model, state, dispatch }: DetailProps) {
  const { t } = useLocale();
  const entry = model.get(state.selected),
    cases = model
      .items(entry)
      .filter((item) => item.kind === 'case')
      .sort((a, b) => a.id.localeCompare(b.id, undefined, { numeric: true })),
    item = model.items(entry).find((row) => row.id === state.selectedItem),
    facts = item?.case_context?.facts || [];
  if (!cases.length) return null;
  return (
    <section className="case-selector" aria-label={t('Cases')}>
      <div className="case-heading">
        <h3>
          {cases.length} {t('cases')}
        </h3>
        <span>{t('Shared task; different inputs')}</span>
      </div>
      <div className="case-buttons">
        {cases.map((row) => (
          <button
            key={row.id}
            className="case-button"
            data-entry={row.id}
            aria-pressed={row.id === state.selectedItem}
            onClick={() => dispatch({ type: 'item', id: row.id })}
          >
            {model.label(row, entry)}
          </button>
        ))}
      </div>
      {!!facts.length && (
        <p className="case-facts">
          {facts.map((fact, index) => (
            <Fragment key={index}>
              {index > 0 && ' · '}
              <strong>{fact.value}</strong> {fact.label.toLowerCase()}
            </Fragment>
          ))}{' '}
          {item?.case_context?.source && (
            <SourceLink url={item.case_context.source}>{t('Pool manifest ↗')}</SourceLink>
          )}
        </p>
      )}
      {entry.case_note !== 'Not yet specified.' && (
        <div className="case-note">
          <Field entry={entry} name="case_note" />
        </div>
      )}
      {item && (
        <div className="case-source">
          <SourceLink url={item.url}>
            {t('Open source ↗')} {model.label(item, entry)}
          </SourceLink>
        </div>
      )}
    </section>
  );
}
function StudyIndex({ model, state, dispatch }: DetailProps) {
  const { locale, t } = useLocale();
  const entry = model.get(state.selected);
  if (!entry.studies?.length) return null;
  return (
    <section className="study-index">
      <h3>{t('Experiments and conditions')}</h3>
      {!entry.id.startsWith('wsi-') && (
        <p className="fine">
          {t(
            'Grouped for navigation. Each protocol retains its contract, cases, assistance, model and runtime. Grouping does not pool scores or count an index as an execution.',
          )}
        </p>
      )}
      {entry.studies.map((study) => {
        const source = model.data.local_sources[study.protocol];
        return (
          <details className="study" data-experiment={study.id} key={study.id}>
            <summary>{study.title}</summary>
            {locale === 'zh-CN' && entry.id.startsWith('wsi-') && (
              <p className="translation-notice">{t('English source text')}</p>
            )}
            <p>{study.scope}</p>
            {!!study.tasks.length && (
              <p className="fine">
                {t('Recorded task/case IDs:')}{' '}
                {study.tasks.map((id, index) => (
                  <Fragment key={id}>
                    {index > 0 && ' · '}
                    <code>{id}</code>
                  </Fragment>
                ))}
              </p>
            )}
            <p>
              {source?.sha256 ? (
                <button
                  className="text-button"
                  data-source={source.sha256}
                  onClick={() =>
                    dispatch({ type: 'source', source: source.sha256! }, '#source-heading')
                  }
                >
                  {t('Read exact protocol')}
                </button>
              ) : (
                t('Protocol not embedded in this copy.')
              )}
            </p>
            <p className="fine">
              {t('Experiment')} <code>{study.id}</code>
              <br />
              {study.record_path}
            </p>
          </details>
        );
      })}
    </section>
  );
}
function Overview(props: DetailProps) {
  const { t } = useLocale();
  const { model, state, dispatch } = props,
    entry = model.get(state.selected),
    condition = entry.variants[state.condition]!;
  return (
    <>
      <div className="task-context">
        <h3>{t('Why it matters')}</h3>
        <Field entry={entry} name="value" />
      </div>
      <TaskPicture {...props} />
      <div className="overview-contract">
        <Box title={t('Input')}>
          <Field entry={entry} name="raw" />
        </Box>
        {entry.variants.length < 2 && (
          <Box title={t('Supplied help')} className="helper">
            <Field entry={entry} name="helpers" />
          </Box>
        )}
        <Box title={t('Deliverable')} className="deliverable">
          <Field entry={entry} name="output" />
        </Box>
      </div>
      {entry.variants.length > 1 && (
        <section className="assistance">
          <h3>{t('Assistance condition')}</h3>
          <div className="variants">
            {entry.variants.map((variant, index) => (
              <button
                className="variant"
                data-condition={index}
                aria-pressed={index === state.condition}
                key={variant.name}
                onClick={() => dispatch({ type: 'condition', condition: index })}
              >
                {variant.name}
              </button>
            ))}
          </div>
          <div className="condition">
            <p>
              <strong>{t('Given')}</strong>
              {condition.helper}
            </p>
            <p>
              <strong>{t('Remaining work')}</strong>
              {condition.remaining}
            </p>
          </div>
        </section>
      )}
      <section className="difficulty">
        <h3>{t('What makes it difficult')}</h3>
        <Field entry={entry} name="challenge" />
      </section>
      <CaseSelector {...props} />
      <StudyIndex {...props} />
    </>
  );
}
function Requirements({ entry }: { entry: TaskEntry }) {
  const { t } = useLocale();
  return (
    <div className="requirements">
      <Box title={t('Task rules')}>
        <Field entry={entry} name="spec" />
      </Box>
      <Box title={t('Environment & callable tools')}>
        <Field entry={entry} name="tools" />
      </Box>
      <Box title={t('How success is checked')}>
        <Field entry={entry} name="score" />
      </Box>
      <Box title={t('Reference-only material')}>
        <Field entry={entry} name="reference" />
      </Box>
    </div>
  );
}
function Examples({ model, state, dispatch }: DetailProps) {
  const { t } = useLocale();
  const entry = model.get(state.selected),
    illustrated = model.items(entry).find((item) => item.id === entry.example_case_id);
  const roles: [VisualRole, string][] = [
    ['input', t('Input')],
    ['helpers', t('Supplied helpers')],
    ['answer', t('Reveal reference / output')],
  ];
  return (
    <>
      {entry.example_case_id &&
        state.selectedItem &&
        state.selectedItem !== entry.example_case_id && (
          <p className="scope-note">
            Illustrated example:{' '}
            {illustrated ? model.label(illustrated, entry) : entry.example_case_id}. The selected
            case has no local image preview.
          </p>
        )}
      <div className="variants" aria-label={t('Visual reveal')}>
        {roles.map(([role, label]) => (
          <button
            key={role}
            className="variant"
            data-visual={role}
            aria-pressed={state.visual === role}
            onClick={() => dispatch({ type: 'visual', visual: role })}
          >
            {label}
          </button>
        ))}
      </div>
      <div className="visual-content" data-visible-role={state.visual}>
        <Markup html={entry.visuals[state.visual]} />
      </div>
      <ImageNotice model={model} entry={entry} dispatch={dispatch} />
    </>
  );
}
function Sources({ model, state, dispatch }: DetailProps) {
  const { t } = useLocale();
  const [copyStatus, setCopyStatus] = useState('');
  const entry = model.get(state.selected),
    items = model.items(entry),
    active =
      items.find((item) => item.id === state.selectedItem) ||
      (items.length === 1 ? items[0] : undefined);
  const sourceEntry = entry.sources.find(
      ([, path]) => model.data.local_sources[path]?.sha256 === state.source,
    ),
    source = sourceEntry && model.data.local_sources[sourceEntry[1]];
  return (
    <>
      {sourceEntry && source && (
        <section className="source-reader" aria-labelledby="source-heading">
          <div className="source-actions">
            <button
              className="quiet"
              id="source-close"
              onClick={() =>
                dispatch({ type: 'source', source: '' }, `[data-source="${state.source}"]`)
              }
            >
              {t('Back to references')}
            </button>
            <a
              id="source-download"
              href={'data:application/octet-stream;base64,' + source.base64}
              download={sourceEntry[1].split('/').at(-1)}
            >
              {t('Download original')}
            </a>
          </div>
          <h3 id="source-heading" tabIndex={-1}>
            {sourceEntry[0]}
          </h3>
          <pre id="source-content" tabIndex={0}>
            {source.content}
          </pre>
        </section>
      )}
      {items.length > 1 && (
        <label className="source-picker">
          {t('Source record')}
          <select
            id="source-picker"
            value={state.selectedItem}
            onChange={(event) =>
              dispatch({ type: 'item', id: event.target.value }, '#source-picker')
            }
          >
            <option value="">{t('Shared definition sources')}</option>
            {items.map((item) => (
              <option value={item.id} key={item.id}>
                {model.label(item, entry)}
              </option>
            ))}
          </select>
        </label>
      )}
      {active && (
        <div className="selected-source">
          <SourceLink url={active.url}>{t('Open selected source ↗')}</SourceLink>
          {active.brief_scope_note && <p className="fine">{active.brief_scope_note}</p>}
          <details className="provenance">
            <summary>{t('Technical identifiers')}</summary>
            <dl>
              <dt>Source ID</dt>
              <dd>
                <code>{active.id}</code>
              </dd>
              <dt>Definition ID</dt>
              <dd>
                <code>{active.definition}</code>
              </dd>
              <dt>Source condition</dt>
              <dd>{active.condition}</dd>
            </dl>
          </details>
        </div>
      )}
      <h3>{t('Definition references')}</h3>
      {entry.sources.map(([label, path], index) => {
        const reference = model.data.local_sources[path],
          story = model.data.presentation_context?.story_urls?.[path];
        return (
          <div className="source" key={index}>
            {/^https?:/.test(path) ? (
              <SourceLink url={path}>{label} ↗</SourceLink>
            ) : (
              <>
                {reference?.sha256 ? (
                  <button
                    className="text-button"
                    data-source={reference.sha256}
                    onClick={() =>
                      dispatch({ type: 'source', source: reference.sha256! }, '#source-heading')
                    }
                  >
                    {label}
                  </button>
                ) : (
                  label
                )}
                {story && (
                  <>
                    {' '}
                    · <a href={story}>{t('Read illustrated story →')}</a>
                  </>
                )}
                {!reference?.sha256 && (
                  <small>
                    {t('Unavailable in this copy:')}{' '}
                    {reference?.unavailable || 'This source is not included.'}
                  </small>
                )}
              </>
            )}
          </div>
        );
      })}
      <div className="metadata-actions">
        <button
          className="quiet"
          onClick={async () => {
            const metadata = entry.sources.map(([label, path]) => ({
              label,
              path,
              sha256: model.data.local_sources[path]?.sha256,
              bytes: model.data.local_sources[path]?.bytes,
              unavailable: model.data.local_sources[path]?.unavailable,
            }));
            setCopyStatus(
              (await copyText(
                JSON.stringify(
                  {
                    task_id: entry.id,
                    owner_group: entry.owner_group,
                    category: entry.category,
                    role: entry.role,
                    agent_work: entry.agent_work,
                    modalities: entry.modalities,
                    studies: entry.studies?.map((study) => study.id),
                    sources: metadata,
                  },
                  null,
                  2,
                ) + '\n',
              ))
                ? t('Metadata copied')
                : t('Copy failed'),
            );
          }}
        >
          {t('Copy full metadata')}
        </button>
        <span role="status" aria-live="polite">
          {copyStatus}
        </span>
      </div>
      <details className="source-limits">
        <summary>{t('Evidence & remaining gaps')}</summary>
        <Field entry={entry} name="families" />
        <Field entry={entry} name="gap" />
      </details>
    </>
  );
}
export function TaskDetail(props: DetailProps) {
  const { locale, t } = useLocale();
  const { model, state, dispatch } = props,
    entry = model.get(state.selected),
    members = model.members(entry),
    family = model.family(entry),
    item = model.items(entry).find((row) => row.id === state.selectedItem);
  const tabs: [TaskTab, string][] = [
    ['overview', t('Overview')],
    ['requirements', t('Requirements')],
  ];
  if (hasExample(entry)) tabs.push(['examples', t('Example')]);
  tabs.push(['sources', t('Sources')]);
  const normalized = (value: string) =>
    value
      .toLowerCase()
      .replace(
        /^(build and run a pipeline to |develop and apply a prediction method to |implement a computational method to )/,
        '',
      )
      .replace(/[.]+$/, '');
  const datasets =
    model.data.datasets?.records.filter((dataset) => dataset.task_ids.includes(entry.id)) || [];
  return (
    <article className="task-detail" data-brief={entry.id}>
      <div className="detail-heading">
        {!entry.id.startsWith('wsi-') && (
          <p className="task-provenance">
            {entry.repo}
            {entry.owner_group && ' · ' + t('Research owner:') + ' ' + entry.owner_group}
            <br />
            {t(model.category(entry.category).title)} ·{' '}
            {t(model.data.taxonomy.roles?.[entry.role || 'task'] || 'Agent task')} ·{' '}
            {t(model.data.taxonomy.agent_work?.[entry.agent_work] || '')}
            {!!entry.operations?.length &&
              ' · Also: ' +
                entry.operations.map((operation) => t(model.category(operation).title)).join(', ')}
          </p>
        )}
        {!entry.id.startsWith('wsi-') && (
          <div className={styles.modalities} aria-label="Imaging and data modalities">
            {entry.modalities.map((modality) => (
              <span className={styles.modality} data-modality={modality} key={modality}>
                {t(model.data.taxonomy.modalities?.[modality] || modality)}
              </span>
            ))}
          </div>
        )}
        {entry.proposed && <span className="draft">{t('Proposed')}</span>}
        <h2>{members.length > 1 ? family?.title : entry.title}</h2>
        {members.length > 1 && (
          <label className="task-variant-picker" htmlFor="task-variant">
            {family?.selector}
            <select
              id="task-variant"
              value={entry.id}
              onChange={(event) =>
                dispatch({ type: 'variant', id: event.target.value }, '#task-variant')
              }
            >
              {members.map((member) => (
                <option key={member.id} value={member.id}>
                  {member.nav_label || member.title}
                </option>
              ))}
            </select>
          </label>
        )}
        {edition(entry) && <span className="edition">{edition(entry)}</span>}
        {normalized(entry.goal) !== normalized(entry.title) && (
          <div className="task-goal">
            <Field entry={entry} name="goal" />
          </div>
        )}
        {wsiBoundary(entry.id, locale) && (
          <aside className="reading-boundary">
            <strong>{t('Page caveat')}</strong>
            <p>{wsiBoundary(entry.id, locale)}</p>
          </aside>
        )}
        {locale === 'zh-CN' && !entry.locales?.['zh-CN'] && (
          <p className="translation-notice" lang="zh-CN">
            {t('English source text')}
          </p>
        )}
      </div>
      {item?.brief_scope_note && (
        <p className="scope-note">
          Selected source: {model.label(item, entry)}. This overview describes the{' '}
          {edition(entry) || 'shared task'}; exact data and recipes can differ.{' '}
          <button
            className="text-button"
            data-tab="sources"
            onClick={() => dispatch({ type: 'tab', tab: 'sources' }, '#tab-sources')}
          >
            Source details
          </button>
        </p>
      )}
      {!!datasets.length && (
        <div className="dataset-links">
          <span>{t('Learn about the data')}</span>
          {datasets.map((dataset) => (
            <a key={dataset.id} href={'#datasets/' + encodeURIComponent(dataset.id)}>
              {dataset.title} →
            </a>
          ))}
        </div>
      )}
      <div className="tabs" role="tablist" aria-label={t('Task sections')}>
        {tabs.map(([tab, label], index) => (
          <button
            id={'tab-' + tab}
            data-tab={tab}
            key={tab}
            role="tab"
            tabIndex={state.tab === tab ? 0 : -1}
            aria-selected={state.tab === tab}
            aria-controls="task-panel"
            onClick={() => dispatch({ type: 'tab', tab }, '#tab-' + tab)}
            onKeyDown={(event) => {
              const target = {
                ArrowRight: (index + 1) % tabs.length,
                ArrowLeft: (index + tabs.length - 1) % tabs.length,
                Home: 0,
                End: tabs.length - 1,
              }[event.key];
              if (target !== undefined) {
                event.preventDefault();
                const next = tabs[target]![0];
                dispatch({ type: 'tab', tab: next }, '#tab-' + next);
              }
            }}
          >
            {label}
          </button>
        ))}
      </div>
      <section id="task-panel" role="tabpanel" tabIndex={0} aria-labelledby={'tab-' + state.tab}>
        {state.tab === 'overview' ? (
          <Overview {...props} />
        ) : state.tab === 'requirements' ? (
          <Requirements entry={entry} />
        ) : state.tab === 'examples' ? (
          <Examples {...props} />
        ) : (
          <Sources {...props} />
        )}
      </section>
    </article>
  );
}
