# HuBMAP · 清点与测量肾小球

**拟议轮廓任务：** 找出各肾小球截面，描边并测量面积。已有诊断试验只提交**点坐标**，不能据此认定完整轮廓与面积任务已经完成。

## Value

肾小球是肾脏的滤过结构。逐对象记录可分别检查漏标、重复和边界误差；合并掩膜可能掩盖这些差异。

## Given

### Original data

PAS 肾脏训练 TIFF `aaa6a05cc`：**13,013 × 18,484 原生像素**；OME 标尺两轴均为 **0.65 µm/px**。左上角为原点，x 向右，y 向下。

### Supplied helpers

默认给图像和标尺。可选皮质/髓质多边形是粗略区域上下文，不是肾小球答案或经裁定的阴性区域；已有点试验未提供这些区域多边形。

### Callable tools

切图、描绘轮廓、重叠视野去重与几何计算。点试验提供无参考概览与切图工具，也允许直接读取 TIFF。

### Reference-only material

源 `gt_masks` 文件有 **99 个肾小球多边形**，由自动分割初始化、专家校正。参考揭示与参考选出的教学裁图不是默认求解器输入。

## Task specification

遍历全片，各截面保留一个稳定对象记录，把裁图内坐标映射回原生坐标。导出中心、轮廓与物理面积；不推断疾病分级、三维体积或整颗肾脏的肾小球总数。

## Expected output

`glomeruli.geojson` 与 `inventory.csv`，字段为 `id, center_x_px, center_y_px, area_um2`。统一使用多边形面积质心；**像素面积 × 0.65²** 得到 µm²。展示的格式示例来自源参考，不是模型提交。

## Evaluation

轮廓方案仍需冻结一对一匹配、边缘截面规则、有效标注范围、逐对象重叠和面积误差。额外候选须经裁定才能作临床假阳性判断。点任务只检查点在多边形内或距边界 **50 µm** 以内的一对一匹配；修订版报告参考召回，将额外候选列入复核。Harbor 奖励检查提交格式，不代表轮廓准确性。

## Visual explanation

### Workflow

全片输入 → 可选区域上下文 → 教学裁图 → 参考轮廓 → 原生坐标 → 重复记录合并 → 物理面积 → 清单示例。

### Input

![HuBMAP PAS 原图缩略图，未显示肾小球参考](../../../../.local/wsi-ground-truth/explainer/assets/hubmap-overview-input.jpg)

### Supplied helpers

教学裁图起点 **(2016,6706)**，大小 **1600 × 1600 原生像素，宽 1.04 mm**；按首个参考多边形选取。两个重叠视野重复显示同一对象，是构造的去重示例，不是已观察到的模型错误。

### Reference or output

![青绿色为源肾小球参考轮廓，不是模型输出](../../../../.local/wsi-ground-truth/explainer/assets/hubmap-overview-reference.png)

## Conditions

| Condition | Supplied help | Work remaining |
| --- | --- | --- |
| 拟议轮廓清单 | 图像与标尺 | 搜索、描边、去重、测量 |
| 可选解剖上下文 | 粗略皮质/髓质区域 | 定位并描绘各截面 |
| 教学裁图 | 参考选出的位置 | 观察几何；全片搜索已移除 |
| 原始点试验 | 无参考概览与切图工具 | 返回原生中心点；无轮廓 |
| 修订参考召回试验 | 相同图像；明确报告不确定截面 | 返回点与备注；额外候选待复核 |

## Difficulty

覆盖全片、相邻对象身份与轮廓精度是不同工作。点结果不能证明轮廓或面积表现；公共训练数据的预先暴露仍不明。

## Sources

- [作者 v1 / CC BY 4.0](https://zenodo.org/records/7729610) · [标注方法](https://pmc.ncbi.nlm.nih.gov/articles/PMC10356924/)。
- [来源凭据](../../../../datasets/receipts/wsi-teaching-samples.json) · [显示派生说明](../../../../presentation/task-explorer/hubmap-inventory/NOTICE.md)。
- [原始点试验](../../experiments/wsi-hubmap-inventory-astra-medium/protocol.md) · [修订点试验](../../experiments/wsi-hubmap-inventory-v2-sol6-xhigh/protocol.md)。

## Coverage

1 张 TIFF 与 2 个标注 JSON 成员经 CRC32/SHA-256 校验。**未下载或校验完整 33.6 GB 压缩包。** 99 是源多边形数，不是经独立裁定的全部对象数。

## Cases

所有视图均为 `aaa6a05cc`。源对象 ID 重复，因此示例 `ref-NNN` 按源数组从 1 开始编号。裁图不构成独立病例。

## Gaps

轮廓/面积方案尚无冻结评分器或经评估的轮廓输出；已有点试验属于各自协议。参考纳入范围、局部截面与疾病分级仍待澄清；本解释不构成临床裁定或新试验授权。
