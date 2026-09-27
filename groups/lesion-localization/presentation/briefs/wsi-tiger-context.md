# TIGER · 在组织区室中计数免疫细胞

识别组织区室，定位免疫细胞，按区室计数。

## Value

将「有几个细胞」与「细胞属于什么组织」关联。

## Given

### Original data

- **样本：** 114S，乳腺 H&E 全片，425.0 MB。
- **尺寸：** 61,504 × 43,392 px；0.456694 µm/px。
- **配套：** 3 个 ROI、组织掩膜、全片 XML、细胞 COCO JSON。

### Supplied helpers

- **首轮输入：** 官方 ROI + 标尺，移除全片搜索。
- **对照条件：** 额外提供组织参考标注，只保留细胞检测与关联计数。
- 两种帮助条件分开评价。

### Callable tools

- 图像缩放、细胞中心标记。
- 组织轮廓、区室汇总。
- 本页叠加来自公开参考标注；既有诊断试验另有冻结记录，本次不运行模型。

### Reference-only material

- **组织参考标注：** 区域类别掩膜。
- **细胞参考标注：** 试验 roi1 = COCO 942（20），roi2 = COCO 940（175），roi3 = COCO 941（323）。旧教学图按 COCO ID 排序。
- **合并类别：** 淋巴细胞 + 浆细胞；无法分别评分。
- **范围：** 框是位置提示；ROI 外不能当负例。

## Task specification

- 标出组织区室与免疫细胞中心。
- 将每个细胞关联到所在区室。
- 汇总数量、面积、密度；排除 mask 0。
- 预先确定 class 2 与 6 是否合并。

## Expected output

- **细胞：** `cells.csv` → `x_px, y_px, class, compartment`。
- **组织：** `regions.geojson` → 区室轮廓。
- **汇总：** `summary.csv` → `compartment, n_cells, area_mm2, density_per_mm2`。
- **全片坐标：** ROI 坐标 + 裁图左上角。

## Evaluation

- 联合组织/面积/密度任务仍为提案。[原试验](../../experiments/wsi-tiger-context-astra-medium/protocol.md)与[修订试验](../../experiments/wsi-tiger-context-v2-sol6-xhigh/protocol.md)仅提交 ROI 局部坐标的 `points.json` 与区室代码。
- 修订评分在 20 px 内一对一配对，分别读取源细胞中心与提交中心处的组织类别；这不等于轮廓或密度评价。

- 分开评价：组织分区、细胞检测、区室关联、计数误差。
- 密度分母：同一受标注支持的区室面积。
- **细胞数/mm² ≠ 临床 sTIL 面积百分比。**

## Visual explanation

[规范故事](../stories/tiger-context.story.md)展示原始 ROI、单独揭示的组织/细胞参考、坐标回映及密度分母。[来源审计](../sources/tiger-context-audit.json)核验 9 个源文件与 4 个冻结条件中的 70 个文件。动态图的颜色与许可见[教学包说明](../../../../presentation/task-explorer/tiger-context/NOTICE.md)；以下旧静态图沿用自身图例。

### Workflow

- 官方 ROI + 标尺
- 识别组织与细胞并关联
- 导出区室内数量、面积和密度。

### Input

![TIGER 原始全片，无密集的全片参考标注](../../../../.local/wsi-ground-truth/explainer/assets/tiger-overview-input.jpg)

### Supplied helpers

- 3 个官方 ROI，位置已知。
- ROI PNG 与原生 TIFF 裁图逐像素一致：RGB MAE = 0。

### Reference or output

![COCO 940 / 试验 roi2（旧教学 ROI1）参考：彩色组织区域和黄色细胞框，颜色图例见课堂](../../../../.local/wsi-ground-truth/explainer/assets/tiger-roi1-reference.png)

| 颜色 | 含义 |
| --- | --- |
| 红 #e6425e | 浸润性肿瘤 |
| 蓝 #28a8c7 | 肿瘤相关基质 |
| 橙 #f08c38 | 健康腺体 |
| 绿 #88b929 | 高淋巴细胞密度的肿瘤相关炎症基质（code 6） |
| 灰 #8792a7 | 其他 |
| 黄框 #ffe600 | 淋巴细胞 + 浆细胞 |
| 全片橙框 #f59e0b | ROI 位置 |

## Conditions

| Condition | Supplied help | Work remaining |
| --- | --- | --- |
| 联合任务 | ROI 与尺度 | 组织分区、细胞检测、关联计数 |
| 已知组织条件 | 再给组织参考标注 | 细胞检测与条件计数 |

## Difficulty

- 小对象识别 + 组织上下文关联。
- 用「给 / 不给组织参考标注」对照拆解误差。

## Sources

- [官方数据说明](https://tiger.grand-challenge.org/Data/) · [AWS 发布](https://registry.opendata.aws/tiger/)。
- [类别编码](https://grand-challenge.org/algorithms/tiger-algorithm-example/) · [CC BY-NC 4.0 许可](https://tiger-training.s3.us-west-2.amazonaws.com/license.txt)。
- **归属：** TIGER / Radboudumc 及合作机构；本例来自 JB。
- **第四路线：** 本次只取 TIGER，未下载 PanopTILs。

## Coverage

- 1 张 WSI、3 个配对 ROI、518 个源细胞框。
- COCO 中其他 ROI 的标签不计为已配对样本。

## Gaps

- 无全片穷尽细胞的参考标注。
- 无淋巴细胞/浆细胞独立类别或精确核边界。
- 页内计数由参考标注衍生，仅供演示；非模型或临床评分。
- 已有点任务冻结及诊断试验；联合轮廓/面积/密度评价尚待冻结，需明确边界归属、纳入规则及 2/6 合并策略。

## Worked reference example

COCO 940 / 试验 roi2：class 2 为 45 个细胞 / 0.06760694 mm²；class 6 为 129 / 0.01730459 mm²。合并时将计数与面积分别相加，得到 **2,049.19 个/mm²**，不能平均两个密度。mask 0 排除，零面积报告不可计算。固定 8×8 µm 标记框不代表细胞核面积。

源中心按 COCO 框计算，掩膜按冻结评分器的四舍五入索引读取；旧教学收据向下取整。此处 518 个中心均为整数，核验结果一致。COCO 941 的 (465,870) 人工平移 (+2,+3) 像素后由 code 1 变成 2，仅演示边界规则，不是模型输出。
