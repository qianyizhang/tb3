# HiESD · 给每条胃组织建立病变地图

按胃组织条，建立粗粒度病变类别地图。

## Value

局部组织识别 → 条内定位 → 逐条汇总。

## Given

### Original data

- **样本：** e4442edf…，胃 ESD，H&E；同片 2 条组织。
- **文件：** SVS，139.3 MB；39,887 × 28,702 px。
- **尺度：** 0.2458 µm/px。
- **配套图：** 623 × 448 px，64× 下采样。

### Supplied helpers

- **可选帮助：** c1/c2 组织条掩膜，仅提供条的归属。
- **教学裁图：** GT 选定位置。
- **追溯：** 完整样本 ID、映射与文件见下载收据。

### Callable tools

- 分倍率读图、组织条标记。
- 区域轮廓与表格导出。
- 默认不提供病变分割模型。

### Reference-only material

- **本例 XML：** 88 个粗区域、6 类。
- **类别：** 胃炎、两类肠化、淋巴滤泡、正常腺体、tub1 腺癌。
- **精度：** 成组腺体区域，非逐腺体精确边界。
- **空白：** 未标注，不自动等于正常。

## Task specification

- 识别每条组织上的粗类别与位置。
- 汇总逐条类别地图，保留未判定区域。
- 覆盖比例仅以已标注区域为分母。

## Expected output

- **文件：** `strip_map.json`。
- **字段：** `strip_id`、`regions[{class, polygon_level0_px, confidence}]`。
- **附表：** 每条组织的类别摘要、未判定区域。
- **坐标：** XML 的 x/y × 64 → 全片原生像素。

## Evaluation

- **主评：** 有参考支持的区域 / patch 类别。
- **次评：** 组织条归属、粗位置。
- **不宜单用：** 精确边界 Dice；参考边界本身较粗。
- **缺少 GT：** 切缘阴阳性、浸润深度。

## Visual explanation

### Workflow

- 全片 + 可选组织条掩膜
- 局部识别与条内定位
- 导出每条组织的粗类别地图。

### Input

![HiESD 官方 64× 下采样缩略图，两条胃组织](../../../../.local/wsi-ground-truth/explainer/assets/hiesd-overview-input.jpg)

### Supplied helpers

- **组织条：** 官方 c1/c2 掩膜，可作为独立帮助条件。
- **局部：** (32192, 2560)，2048 × 2048 原生 px。
- **选择：** 最大 tub1 粗区域，已使用 GT。

### Reference or output

![HiESD XML 类别图：沿用官方类别颜色，粗边界参考](../../../../.local/wsi-ground-truth/explainer/assets/hiesd-overview-reference.png)

| 颜色 | 含义 |
| --- | --- |
| 暗红 #8B0000 | tub1 高分化腺癌 |
| 紫 #8A2BE2 | 正常腺体 |
| 蓝 #0000FF | 慢性胃炎 |
| 亮绿 #00FF00 | 淋巴滤泡 |
| 深绿 #008000 | 完全型肠化 |
| 黄 #FFFF00 | 不完全型肠化 |

## Conditions

| Condition | Supplied help | Work remaining |
| --- | --- | --- |
| 原图起步 | 全片与尺度 | 组织条识别、类别地图、汇总 |
| 提供组织条 | c1/c2 掩膜 | 类别识别与条内定位 |

## Difficulty

- 多尺度形态识别、组织条内定位、汇总。
- 当前仅为任务假设。

## Sources

- [Figshare 原生 SVS / CC BY 4.0](https://doi.org/10.6084/m9.figshare.28919840)。
- [作者配套数据：固定版本](https://huggingface.co/datasets/JSGe-AI/HiESD/tree/f35faff3300342aaa31c87465b264b98fa6b8726)。
- [论文与标注限制](https://www.nature.com/articles/s41597-025-05679-1) · [作者代码](https://github.com/JSGe-AI/HiESD)。
- **归属：** HiESD 作者。

## Coverage

- **配对样本：** 1 张 SVS、缩略图、类别 PNG/XML、2 个组织条掩膜。
- **选样附件：** 0a682165… 的低分辨率预览；未下载第二张 WSI。

## Gaps

- **颜色异常：** 类别 PNG 有 1,569 种 RGB；量化前须审核编码。
- **本页处理：** 采用官方粗网格 XML，不擅自重映射插值颜色。
- 未审计全数据集；无冻结评分器或模型结果。
