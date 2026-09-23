# CAMELYON16 · 从全片找转移灶

搜索整张淋巴结切片，定位转移灶。

## Value

低倍搜索 → 高倍核查 → 返回全片坐标。

## Given

### Original data

- **样本：** tumor_091，阳性淋巴结，H&E。
- **文件：** 金字塔 TIFF，546.4 MB。
- **尺寸：** 61,440 × 53,760 px；0.227273 µm/px。

### Supplied helpers

- **任务输入：** 原始 TIFF、标尺、通用切图工具。
- **教学裁图：** 按参考标注选定位置，已移除搜索工作。
- **选样限制：** 文件较小、阳性区域较大；不代表微小灶难度。

### Callable tools

- 缩略图、指定坐标/倍率读图。
- 点与轮廓标记、坐标导出。
- 当前仅浏览保留图像，未运行检测器。

### Reference-only material

- **XML：** 6 个 Tumor 多边形 + 1 个 Exclusion。
- **红色：** 肿瘤；**青色：** 需排除的内部区域。
- **边界：** 多边形数 ≠ 独立病灶数；不直接给临床分期。
- **用途：** 评估与教学揭示，默认不提供给智能体。

## Task specification

- 自主搜索全片，核查所有候选区域。
- 输出位置、置信度及可选轮廓；允许报告阴性。
- 先确定多边形合并与 Exclusion 规则。

## Expected output

- **文件：** `lesions.json`。
- **结构：** `slide_id`、`detections[]`。
- **每个发现：** `x_px, y_px, confidence`；可加 `polygon_px`。
- **坐标：** 第 0 层，左上角原点；x 向右，y 向下。

## Evaluation

- **定位：** 病灶召回 + 每片假阳性（FROC）。
- **轮廓：** IoU / Dice，单独报告。
- **待补：** 阴性片、病灶合并规则、匹配容差。
- 单个阳性教学片不足以排名。

## Visual explanation

### Workflow

- 原始全片 + 标尺
- 自主搜索并高倍核查
- 导出全片坐标、轮廓与置信度。

### Input

![CAMELYON16 原图：全片缩略图，未显示参考标注](../../../../.local/wsi-ground-truth/explainer/assets/camelyon-overview-input.jpg)

### Supplied helpers

- **位置：** (47739, 31340)，1600 × 1600 原生 px。
- **选择：** 最小 Tumor 多边形；属于按参考标注选定的教学裁图。

### Reference or output

![CAMELYON16 XML 参考：红色肿瘤、青色 exclusion，无模型输出](../../../../.local/wsi-ground-truth/explainer/assets/camelyon-overview-reference.png)

## Conditions

| Condition | Supplied help | Work remaining |
| --- | --- | --- |
| 拟议全片搜索 | 原图与尺度 | 搜索、确认、定位 |
| 课堂局部检查 | 按参考标注选择的裁图 | 观察形态；不能评价搜索能力 |

## Difficulty

- 搜索覆盖、倍率切换、假阳性控制。
- 当前未实测任务难度。

## Sources

- [官方 AWS 发布 / CC0](https://registry.opendata.aws/camelyon/)。
- [文件说明](https://camelyon-dataset.s3.us-west-2.amazonaws.com/CAMELYON16/README.md) · [数据论文](https://pmc.ncbi.nlm.nih.gov/articles/PMC6007545/)。
- **归属：** Radboudumc / UMC Utrecht；图像与同名 XML 配对。
- **条款范围：** 本次 AWS 发布物；旧站文字有差异。

## Coverage

- **配对样本：** 1 张阳性 WSI + XML。
- **选样附件：** tumor_084 / tumor_075 的 XML；未下载对应 WSI。

## Gaps

- 无阴性片、冻结评分器或逐灶临床复核。
- 金字塔含填充；必须按 64× 倍率映射坐标。
- 拟议任务，未运行模型。
