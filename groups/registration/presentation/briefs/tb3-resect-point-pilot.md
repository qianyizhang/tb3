# 修正两组 MRI 到超声的对应点

修正偏离的点，同时保留已接近正确位置的初始点。

## Value

检验局部对应点修正能否改善较大偏差，且不损害原本接近的初始位置。

## Given

### Original data

两组完整的 FLAIR MRI／切除前超声配对，每组有一个 MRI 查询点。

### Supplied helpers

初始超声候选点复制 MRI 的世界坐标，并提供通用正交视图工具。本试点未提供肿瘤掩膜。

### Callable tools

各关联协议分别规定允许调用的工具与执行环境。

### Reference-only material

参考答案及可用范围以各冻结契约为准。供读者查看的来源或示意图不会自动提供给求解器。

## Task specification

对每个查询点返回保留或修正后的超声体素点，并附置信度与图像依据。遵守各协议的坐标、标识符和访问契约。

## Expected output

每个查询点对应的超声体素点、置信度与图像依据；允许保留原候选点。

## Evaluation

以毫米计算目标配准误差 TRE，并与复制坐标的无操作基线比较；保留有害的过度修正。两个选定查询点不能验证人群表现。

## Difficulty

MRI 与超声的外观不同。复制共同坐标有时已是强基线，不必要的移动反而会使结果变差。

## Coverage

实验索引保留病例、契约、帮助条件和执行边界。实验记录不等于执行次数；分组不会合并分数。

## Sources

- [RESECT 标准／挑战点复核：Astra medium](../../experiments/resect-point-audit-astra-medium/protocol.md)
