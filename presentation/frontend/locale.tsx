import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import type { ExplorerData } from './types';

export type Locale = 'en' | 'zh-CN';
const STORAGE_KEY = 'tb3-presentation-language';
const valid = (value: string | null): value is Locale => value === 'en' || value === 'zh-CN';

function preferredLocale(): Locale {
  const query = new URLSearchParams(location.search).get('lang');
  if (valid(query)) return query;
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (valid(stored)) return stored;
  } catch {
    // Local file copies can disable storage; browser language still works.
  }
  return navigator.language.toLowerCase().startsWith('zh') ? 'zh-CN' : 'en';
}

const zh: Record<string, string> = {
  'Research workbench': '研究工作台',
  'Primary navigation': '主导航',
  Overview: '总览',
  Tasks: '任务',
  Datasets: '数据集',
  Language: '语言',
  'Skip to content': '跳到正文',
  Close: '关闭',
  'Source repository': '来源仓库',
  'Explore a capability': '按能力探索',
  'No results': '没有结果',
  'No tasks match these filters': '没有符合筛选条件的任务',
  'Reset filters': '清除筛选',
  'Coverage & source revisions': '覆盖范围与来源版本',
  'Brief guide': '阅读指南',
  'Browse tasks': '浏览任务',
  'Task catalogue': '任务目录',
  'Search tasks': '搜索任务',
  'Task, image type, case…': '任务、图像类型或案例…',
  'Browse by': '浏览方式',
  Capability: '能力',
  Repository: '仓库',
  'Refine the collection': '筛选目录',
  'Research role': '研究角色',
  'Agent tasks': '智能体任务',
  'Supporting research': '支撑研究',
  'All research': '全部研究',
  'Imaging / data modality': '影像／数据类型',
  'All modalities': '全部类型',
  'Agent work': '智能体工作',
  'All agent work': '全部工作类型',
  'Why it matters': '任务价值',
  Input: '输入',
  'Supplied help': '提供的帮助',
  Deliverable: '交付物',
  'Assistance condition': '帮助条件',
  Given: '已提供',
  'Remaining work': '仍需完成',
  'What makes it difficult': '难点',
  'Task rules': '任务要求',
  'Environment & callable tools': '环境与可调用工具',
  'How success is checked': '如何评价',
  'Reference-only material': '仅供参考的材料',
  'Animated task illustration': '任务示意动画',
  'Illustrative model · not case-specific': '示意模型 · 非本例结果',
  'Source-derived example': '来源图像示例',
  'Inspect example →': '查看示例 →',
  'Inspect example and reference →': '查看示例与参考标注 →',
  'Reveal reference / output': '揭示参考／输出',
  'Supplied helpers': '提供的帮助',
  'Source reference': '来源参考',
  Examples: '示例',
  Requirements: '要求',
  Sources: '来源',
  'Source files': '来源文件',
  'English source text': '此条目尚无中文译文，以下保留英文原文。',
  Dataset: '数据集',
  'How to read this dataset': '如何阅读此数据集',
  'Conceptual structure': '概念结构',
  'Original data': '原始数据',
  'Annotations / reference': '标注／参考',
  'One sample:': '一个样本：',
  'Frozen source snapshot': '保留的来源快照',
  'Sample + reference': '样本与参考标注',
  'Sample available · paired GT unavailable': '样本可用 · 配对参考不可用',
  'Reference available · image unavailable': '参考可用 · 图像不可用',
  'Source screen · imaging not acquired': '仅有来源调查 · 未获取图像',
  'Enlarge snapshot ↗': '放大图像 ↗',
  'Reveal ground truth / source reference': '揭示参考标注',
  'Snapshot provenance and exact source files': '快照来源与原始文件',
  'Understand the data structure': '了解数据结构',
  'What the reference can establish': '参考标注能支持什么',
  'Selected samples & their use': '所选样本及用途',
  'Selection provenance': '选样来源',
  'Tasks using or explaining this source': '使用或说明此来源的任务',
  'Release, access & recovery': '发布、访问与恢复',
  'Open documentation or reference gaps': '文档或参考标注的缺口',
  'Copy full metadata': '复制完整元数据',
  'Metadata copied': '已复制元数据',
  'Copy failed': '复制失败',
  'Page caveat': '阅读边界',
  'Full provenance': '完整来源信息',
  'Show source image first': '先看来源图像',
  'Native example': '原生示例',
  ' in this collection': '（本目录）',
  ' match your search': '项匹配',
  'A mask marks voxels; a landmark marks a point; a correspondence links observations. Each has its own limits.':
    '掩膜标体素，标志点标位置，对应关系连接不同观察；各自都有适用边界。',
  'A reference can be hidden for scoring or supplied as help. The task condition decides which.':
    '参考标注可以留给评估，也可以作为帮助提供；由具体任务条件决定。',
  'All datasets →': '全部数据集 →',
  Annotation: '标注',
  'Back to Tasks': '返回任务',
  'Back to references': '返回来源列表',
  'Browse and filter tasks': '浏览与筛选任务',
  'Browse evidence': '浏览证据',
  'Choose a source from the dataset list, or return to the full collection.':
    '请从列表选择数据来源，或返回完整目录。',
  'Choose a task': '选择任务',
  'Clear search': '清除搜索',
  'Dataset not found': '未找到数据集',
  'Definition references': '任务定义来源',
  'Download full metadata': '下载完整元数据',
  'Download original': '下载原文',
  'Entries in this selection': '当前选择的条目',
  'Evidence & remaining gaps': '证据与剩余缺口',
  'Exact paths and checksums are included in full metadata below.':
    '完整路径与校验值可通过下方元数据获取。',
  Example: '示例',
  'Explore samples and reference availability': '查看样本与参考标注的可用情况',
  'Explore source': '查看来源',
  'Explore tasks': '探索任务',
  'Explore the images, annotations and selected samples behind the work.':
    '查看研究所依据的图像、标注与所选样本。',
  'Explore the tasks, follow the research and trace each conclusion back to its evidence.':
    '从任务出发，阅读研究过程，并追溯每项结论的证据。',
  'Explore the workbench': '探索工作台',
  'Find a dataset': '查找数据集',
  'Find your way': '从这里开始',
  'Frozen image unavailable in this build:': '此版本未包含保留图像：',
  'Ground-truth availability:': '参考标注可用情况：',
  'How to read a dataset': '如何阅读数据集',
  'How to read the research record': '如何阅读研究记录',
  Image: '图像',
  'Image attribution, terms and derivation': '图像归属、许可与生成方式',
  'Image example': '图像示例',
  'Inspect source-derived example': '查看来源图像示例',
  'Learn about the data': '了解数据',
  'Learn the data before the task': '先了解数据，再看任务',
  'Matching entries': '匹配的条目',
  'Medical imaging research, with a record you can inspect.': '可追溯的医学影像智能体研究。',
  'Medical imaging · Agent research': '医学影像 · 智能体研究',
  'Name, modality, sample ID…': '名称、图像类型或样本 ID…',
  'No frozen sample has been documented for this source.': '此来源尚无保留样本记录。',
  'No matching dataset or sample. Try a broader term.':
    '没有匹配的数据集或样本，请尝试更宽泛的词。',
  'No matching datasets': '没有匹配的数据集',
  'No matching entries. Try a broader term or reset the filters.':
    '没有匹配条目，请尝试更宽泛的词或清除筛选。',
  'No matching tasks': '没有匹配的任务',
  'No tasks match this search in this repository.': '此仓库内没有匹配的任务。',
  'Open selected source ↗': '打开所选来源 ↗',
  Proposed: '拟议',
  'Read illustrated story →': '阅读图文故事 →',
  'Read-only workbench · Packaging, evidence validity and submission qualification are separate.':
    '只读工作台 · 打包、证据有效性与提交资格分别处理。',
  'Recover the pinned snapshot; this is not an empty scan.': '需恢复固定快照；这不表示空白扫描。',
  'Repeated views and conditions may reuse that sample.': '不同视图和条件可能复用同一样本。',
  'Research owner:': '研究归属：',
  Reset: '重置',
  'Search datasets': '搜索数据集',
  'Selections can overlap. These are documented source selections, not a count of independent patients or successful trials.':
    '所选样本可能重叠；这里记录的是来源选样，不代表独立患者数或成功试验数。',
  'Shared definition sources': '共享任务定义的来源',
  'Source documentation': '来源文档',
  'Source library': '来源资料库',
  'Source record': '来源记录',
  'Source records, cases and attempts are separate counts.': '来源记录、案例与执行次数分别计数。',
  'Source repositories': '来源仓库',
  'Source review only; no task brief is linked.': '仅有来源调查，尚未关联任务简述。',
  'Status definitions': '状态说明',
  'Successes, partial attempts and corrections stay in the same record.':
    '成功、部分尝试与修正都保留在同一记录中。',
  'Task capabilities': '任务能力',
  'Task sections': '任务章节',
  'Task use': '任务用途',
  'Technical identifiers': '技术标识',
  'The acquired scan or generated input. Geometry and coordinates are part of the data.':
    '获取的扫描或生成的输入；几何与坐标也是数据的一部分。',
  'The source image was not retained. Available annotations can be inspected below.':
    '未保留来源图像；下方可查看已有标注。',
  'These frozen views preserve the selection and reference limits. Opening the page does not run a model or change task inputs.':
    '这些固定视图保留了选样和参考边界；打开页面不会运行模型或改变任务输入。',
  'Try a broader term, a different research role, or clear the filters to explore the collection.':
    '请尝试更宽泛的词、其他研究角色，或清除筛选。',
  'Try a dataset name, image type, or sample ID.': '请尝试数据集名称、图像类型或样本 ID。',
  'Unavailable in this copy:': '此副本中不可用：',
  'View all datasets': '查看全部数据集',
  'What can an agent learn from medical images?': '智能体能从医学图像中学到什么？',
  'definitions/revisions': '个定义／修订',
  'linked experiment records': '条相关实验记录',
  'linked medical experiment records': '条相关医学实验记录',
  'research entries': '条研究',
  'source snapshot': '来源快照',
  sources: '个来源',
  'supporting studies': '项支撑研究',
  'task entries': '条任务',
  variants: '个变体',
  case: '个案例',
  cases: '个案例',
  Cases: '案例',
  'Shared task; different inputs': '同一任务，不同输入',
  'Pool manifest ↗': '样本池清单 ↗',
  'Open source ↗': '打开来源 ↗',
  'Experiments and conditions': '实验与条件',
  'Grouped for navigation. Each protocol retains its contract, cases, assistance, model and runtime. Grouping does not pool scores or count an index as an execution.':
    '此处按导航分组；各协议保留各自的任务约定、案例、帮助条件、模型与运行环境，分组不会合并分数或算作一次执行。',
  'Recorded task/case IDs:': '记录的任务／案例标识：',
  'Read exact protocol': '阅读完整协议',
  'Protocol not embedded in this copy.': '此副本未包含协议。',
  Experiment: '实验',
  'Visual reveal': '视觉揭示',
  entry: '条目',
  entries: '条目',
  source: '个来源',
  'Find and localize': '寻找与定位',
  'Segment images': '图像分割',
  'Microscopy / histopathology': '显微病理图像',
  'Solve a case': '解决案例',
  'Agent task': '智能体任务',
  'Follow a research question': '追踪研究问题',
  'Read the story across experiments.': '阅读跨实验的研究脉络。',
  'Inspect the evidence': '检查证据',
  'Find results, decisions and open issues.': '查看结果、决策与待解决问题。',
  'Understand the status': '理解状态',
  'See what each assessment means.': '了解每种评估状态的含义。',
  curated: '教学选样',
  'Selected example': '所选示例',
  'Selected sample': '所选样本',
  'Search for a target and return its location or absence.': '搜索目标并报告其位置或不存在。',
  'Produce spatial labels for image elements or instances.': '为图像区域或对象生成空间标注。',
  'Accepted convention · 21 Sep 2026': '已确定的写作约定 · 2026 年 9 月 21 日',
  'A Task Brief, inside a Task Explorer': '任务目录中的任务简述',
  'A short explanation of a task, useful before a run and alongside a results story. Aim for a 60–90 second first read.':
    '任务简述在运行前和结果故事旁解释任务；初读目标约为 60–90 秒。',
  'Question + value.': '问题与价值。',
  'One concrete action and where it fits in a clinical or scientific workflow.':
    '说明一个具体动作及其在临床或科学流程中的位置。',
  'What is given.': '已提供什么。',
  'Raw data, supplied helpers and callable tools shown separately. Mark reference-only material explicitly.':
    '分开呈现原始数据、提供的帮助和可调用工具；明确标出仅供参考的材料。',
  'Task contract.': '任务约定。',
  'Required action, constraints, output shape and how success is checked.':
    '说明动作、限制、输出形态与评价方式。',
  'Visual explanation.': '视觉说明。',
  'Show input → assistance → output. Use native slices/overlays when available; label conceptual diagrams.':
    '展示输入 → 帮助 → 输出；有原生图像时优先使用，并标明概念示意图。',
  'What remains difficult.': '剩余难点。',
  'Explain the work left after assistance, backed by evidence when available.':
    '说明得到帮助后仍需完成的工作；有证据时引用证据。',
  'Sources + state.': '来源与状态。',
  'Pin the task/condition, distinguish drafts from published definitions, and state missing evidence.':
    '固定任务条件，区分草案与已发布定义，并指出缺少的证据。',
  'Catalogue structure:': '目录结构：',
  'Capability or repository → task family → definition/revision → conditions and cases. Research ownership and supporting-study roles are separate axes. Repeated cases share a brief; every case should still be reachable.':
    '能力或仓库 → 任务家族 → 定义／修订 → 条件与案例。研究归属和支撑研究是独立维度；重复案例共享简述，但每个案例仍可访问。',
  'Reuse:': '复用：',
  'One repository rulebook and small template; a thin authoring skill follows them. Existing tours stay task-specific visual modules.':
    '仓库规则与简短模板定义写作，写作技能遵循它们；现有导览保留为具体任务的视觉模块。',
  'The existing experiment protocol/scorer remains authoritative. A reader-facing brief is not automatically a runnable solver prompt. Source coverage remains explicitly scoped.':
    '实验协议与评分器仍是执行依据。面向读者的简述不会自动成为可运行的求解提示；来源覆盖范围必须明确。',
};

type LocaleContextValue = { locale: Locale; setLocale: (value: Locale) => void };
const Context = createContext<LocaleContextValue | null>(null);

export function LocaleProvider({ children }: { children: ReactNode }) {
  const [locale, setState] = useState<Locale>(preferredLocale);
  useEffect(() => {
    document.documentElement.lang = locale;
    try {
      localStorage.setItem(STORAGE_KEY, locale);
    } catch {
      // URL and current page still carry the explicit choice.
    }
  }, [locale]);
  const setLocale = (value: Locale) => {
    const url = new URL(location.href);
    url.searchParams.set('lang', value);
    history.replaceState(history.state, '', url.href);
    setState(value);
  };
  return <Context.Provider value={{ locale, setLocale }}>{children}</Context.Provider>;
}

export function useLocale() {
  const context = useContext(Context);
  if (!context) throw new Error('Language context is missing');
  return {
    ...context,
    t: (english: string) => (context.locale === 'zh-CN' ? zh[english] || english : english),
  };
}

export function LanguageSwitch() {
  const { locale, setLocale, t } = useLocale();
  return (
    <label className="language-switch">
      <span>{t('Language')}</span>
      <select
        aria-label={t('Language')}
        value={locale}
        onChange={(event) => setLocale(event.target.value as Locale)}
      >
        <option value="en">English</option>
        <option value="zh-CN">中文</option>
      </select>
    </label>
  );
}

export function localeHref(href: string, locale: Locale): string {
  if (!href || href.startsWith('#') || /^[a-z]+:\/\//i.test(href)) return href;
  const url = new URL(href, location.href);
  url.searchParams.set('lang', locale);
  return url.href;
}

export function localizeExplorer(data: ExplorerData, locale: Locale): ExplorerData {
  if (locale === 'en') return data;
  const datasetLocales = new Map(
    data.datasets?.records.map((record) => [record.id, record.locales?.[locale]]) || [],
  );
  return {
    ...data,
    entries: data.entries.map((entry) => ({
      ...entry,
      ...(entry.locales?.[locale] || {}),
    })),
    datasets: data.datasets && {
      ...data.datasets,
      records: data.datasets.records.map((record) => {
        const translated = record.locales?.[locale];
        if (!translated) return record;
        const {
          sample_set_notes,
          snapshot_summary: _summary,
          snapshot_reference_note: _reference,
          snapshot_captions: _captions,
          ...fields
        } = translated;
        return {
          ...record,
          ...fields,
          sample_sets: record.sample_sets.map((sample, index) => ({
            ...sample,
            label: '教学样本',
            note: sample_set_notes[index] || sample.note,
          })),
        };
      }),
      previews: Object.fromEntries(
        Object.entries(data.datasets.previews || {}).map(([id, snapshot]) => {
          const translated = datasetLocales.get(id);
          return [
            id,
            translated
              ? {
                  ...snapshot,
                  summary: translated.snapshot_summary,
                  reference_note: translated.snapshot_reference_note,
                  panels: snapshot.panels.map((panel, index) => ({
                    ...panel,
                    caption: translated.snapshot_captions[index] || panel.caption,
                  })),
                }
              : snapshot,
          ];
        }),
      ),
    },
  };
}

const wsiBoundaries: Record<string, { en: string; 'zh-CN': string }> = {
  'wsi-camelyon-search': {
    en: 'One positive teaching slide. The local crop was chosen from the reference, and no model was run.',
    'zh-CN': '仅一张阳性教学片；局部裁图由参考标注选定，未运行模型。',
  },
  'wsi-hiesd-map': {
    en: 'Coarse, partly annotated regions support a tissue map, not exact gland or margin scoring. No model was run.',
    'zh-CN': '粗粒度、部分区域标注适合组织地图，不支持精确腺体或切缘评分；未运行模型。',
  },
  'wsi-hubmap-inventory': {
    en: 'One training slide with 99 source reference objects; no disease grades or model run.',
    'zh-CN': '一张训练切片和 99 个来源参考对象；不含疾病分级，也未运行模型。',
  },
  'wsi-tiger-context': {
    en: 'Dense cell reference covers selected ROIs only. Cell classes are merged, and no model was run.',
    'zh-CN': '密集细胞标注仅覆盖选定 ROI；细胞类别已合并，未运行模型。',
  },
};
export const wsiBoundary = (id: string, locale: Locale) => wsiBoundaries[id]?.[locale];

export async function copyText(value: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(value);
    return true;
  } catch {
    const field = document.createElement('textarea');
    field.value = value;
    document.body.append(field);
    field.select();
    const copied = document.execCommand('copy');
    field.remove();
    return copied;
  }
}
