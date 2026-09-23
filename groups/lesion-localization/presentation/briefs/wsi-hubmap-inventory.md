# HuBMAP · 清点与测量肾小球

清点全片肾小球，逐个标出轮廓并测量面积。

## Value

- 肾小球：肾脏的微小滤过单位。
- PAS 下常呈近圆形毛细血管团，需与肾小管区分。
- 对象清单便于分别检查漏检、重复和边界误差。

## Given

### Original data

- **样本：** aaa6a05cc，PAS 肾脏训练图像。
- **文件：** TIFF，82.3 MB。
- **尺寸：** 13,013 × 18,484 px；0.65 µm/px。

### Supplied helpers

- **默认输入：** 原图 + 物理标尺。
- **可选上下文：** 已下载的解剖区 JSON。
- **教学裁图：** 围绕首个参考对象，已移除搜索。

### Callable tools

- 多尺度切图、轮廓编辑。
- 对象去重、几何面积计算。
- 当前未运行自动分割模型。

### Reference-only material

- **参考标注：** 99 个肾小球多边形，与图像同坐标。
- **流程：** 机器辅助起草、专家修正；仍可能有误差。
- **来源：** 发布包 `gt_masks`，未使用模型预测目录。

## Task specification

- 遍历全片，生成完整、无重复的对象清单。
- 每个对象记录中心、轮廓、面积。
- 相邻候选需区分对象身份；不推断未提供的病理分级。

## Expected output

- **轮廓：** `glomeruli.geojson`。
- **清单：** `inventory.csv`，字段 `id, center_x_px, center_y_px, area_um2`。
- **面积：** 多边形像素面积 × 0.65² → µm²。

## Evaluation

- **对象：** 一对一匹配；统计漏检、重复、误检。
- **轮廓：** 匹配对象的 Dice / IoU。
- **测量：** 面积误差。
- 匹配阈值待定；全局 Dice 可能掩盖小对象漏检。

## Visual explanation

### Workflow

- 原始 PAS 全片 + 标尺
- 逐对象搜索、核查与去重
- 导出对象清单及物理面积。

### Input

![HuBMAP PAS 肾脏原图缩略图，未显示参考标注](../../../../.local/wsi-ground-truth/explainer/assets/hubmap-overview-input.jpg)

### Supplied helpers

- **位置：** (2016, 6706)，1600 × 1600 原生 px。
- **宽度：** 1.04 mm。
- **选择：** 首条参考标注轮廓，仅供教学。

### Reference or output

![HuBMAP 参考肾小球轮廓，青绿色；不是模型输出](../../../../.local/wsi-ground-truth/explainer/assets/hubmap-overview-reference.png)

## Conditions

| Condition | Supplied help | Work remaining |
| --- | --- | --- |
| 全片清单 | 原图与物理尺度 | 搜索、对象识别、分割、测量 |
| 课堂局部 | 按参考标注选出的裁图 | 观察结构和轮廓，不能证明完整清点 |

## Difficulty

- 全片覆盖、相似结构区分、对象去重。
- 数量和面积易审计，适合先做小规模任务。

## Sources

- [作者 Zenodo v1 / CC BY 4.0](https://zenodo.org/records/7729610)。
- [配套网站](https://cns-iu.github.io/ccf-research-kaggle-2021/) · [数据论文](https://pmc.ncbi.nlm.nih.gov/articles/PMC10356924/)。
- **归属：** HuBMAP / Jain 等。
- **提取：** HTTP range 下载 3 个成员；已校验成员 CRC32、记录 SHA-256。
- **范围：** 未下载或校验整个 33.6 GB 压缩包。

## Coverage

- 1 张 TIFF + 肾小球 JSON + 解剖区 JSON。
- 99 是参考对象数，非模型成绩。

## Gaps

- 无病理分级参考标注、正式评分器或临床复核。
- 公共训练样本不支持无数据暴露的泛化结论。
- 拟议任务，未运行模型。
