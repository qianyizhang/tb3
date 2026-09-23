# 跨访视追踪 CT 病灶：修订后的纳入与实例规则

按修订规则在两次 CT 中发现病灶、划分实例并建立关联。

## Value

在明确通用纳入规则及相接病灶的实例规则后，检验纵向病灶追踪。

## Given

### Original data

不同访视的两套完整原生 CT 体数据。

### Supplied helpers

修订后的相接病灶与纳入规则；“提供广泛背景”的条件另附宽泛临床先验信息。

### Callable tools

各关联协议分别规定允许调用的工具与执行环境。

### Reference-only material

参考答案及可用范围以各冻结契约为准。供读者查看的来源或示意图不会自动提供给求解器。

## Task specification

为每次访视输出实例掩膜、跨访视对应／事件及不确定候选的判断。遵守各协议的坐标、标识符和访问契约。

## Expected output

逐访视实例掩膜、跨访视对应关系与事件，以及不确定候选的处理决定。

## Evaluation

分别评分检测、区域重叠、实例关联和事件。保留所有参考实例与原科学终点；契约修订本身不构成配对因果比较。

## Conditions

| Condition | Supplied help | Work remaining |
| --- | --- | --- |
| 仅图像 | 完整 CT 配对与修订后的通用说明 | 发现病灶，判断纳入、实例与事件 |
| 提供广泛背景 | 第二位患者的相同 CT 配对，另有已发布的宽泛临床背景 | 利用背景，但没有给出位置或实例身份 |

## Difficulty

措辞修订不会直接给出位置。宽泛临床背景改变先验，而更换患者也更换了病例；两种影响不可混为一谈。

## Coverage

实验索引保留病例、契约、帮助条件和执行边界。实验记录不等于执行次数；分组不会合并分数。

## Sources

- [修订后的纯图像 CT 说明：Astra medium](../../experiments/longitudinal-ct-v2-astra-medium/protocol.md)
- [第二个纯图像 CT 病例：持续与新发病灶，Astra medium](../../experiments/longitudinal-ct-case02-astra-medium/protocol.md)
- [提供已核实宽泛临床背景的 CT 配对：Astra medium](../../experiments/longitudinal-ct-context-supplied-astra-medium/protocol.md)
