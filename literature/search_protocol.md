# 第一、二章文献检索协议

> 检索启动日期：2026-07-27  
> 检索截止日期：每次正式检索的执行日期  
> 目标：建立85篇真实、去重、可查询的有效文献库，并支撑第一章和第二章。工作库须包含5篇2022—2025年中文硕士/博士学位论文和不少于5篇2023—2025年中文期刊论文；按既定“2021年至检索日”口径统计，近年文献占比不低于60%。

## 1. 研究问题

1. φ-OTDR/DAS的技术演进、关键架构和性能约束是什么？
2. LD–SOA在脉冲产生、光放大、增益动态、ASE和瞬态频率变化方面有哪些已知规律？
3. AOM移频、射频门控、平衡探测和偏振分集如何影响外差式DAS？
4. DAS收发模块、小型化询问器和模块级光电集成有哪些已有工作？
5. 数字下变频、差分相位、偏振衰落抑制和参数配置的理论依据是什么？

## 2. 数据库

- Crossref、OpenAlex：候选发现与元数据核验；
- Optica Publishing Group、IEEE Xplore、SPIE Digital Library：光纤传感和光电系统原始论文；
- Web of Science、Scopus：引文追踪（用户学校权限可用时）；
- CNKI、万方、期刊官网：中文研究；
- Google Scholar、Semantic Scholar：前向/后向引文和相似论文发现；
- 出版社或DOI落地页：最终元数据核验。

## 3. 主题检索式

### T1：φ-OTDR/DAS

```text
("phase-sensitive optical time-domain reflectometry" OR "phase-OTDR"
 OR "phi-OTDR" OR "distributed acoustic sensing")
AND (review OR coherent OR heterodyne OR phase)
```

### T2：LD–SOA与发射链路

```text
("semiconductor optical amplifier" OR SOA OR "LD-SOA")
AND (pulse OR modulation OR gating OR "gain saturation"
 OR ASE OR chirp OR "carrier dynamics")
```

### T3：AOM、接收和同步

```text
("phase-OTDR" OR "distributed acoustic sensing")
AND ("acousto-optic modulator" OR heterodyne OR
 "balanced detection" OR synchronization)
```

### T4：偏振与数字解调

```text
("phase-OTDR" OR "distributed acoustic sensing")
AND ("polarization fading" OR "polarization diversity"
 OR "phase demodulation" OR "digital down conversion")
```

### T5：收发模组与小型化

```text
("distributed acoustic sensing" OR "phase-OTDR")
AND (interrogator OR module OR integrated OR compact
 OR miniaturized OR transceiver)
```

### 中文检索

```text
(相位敏感光时域反射 OR 分布式声学传感 OR 分布式振动传感)
AND (相干探测 OR 外差 OR 相位解调 OR 偏振分集)
```

```text
(半导体光放大器 OR SOA OR LD-SOA)
AND (脉冲调制 OR 增益饱和 OR ASE OR 瞬态啁啾 OR 载流子动态)
```

## 4. 纳入标准

- 直接支撑第一章研究现状或第二章理论/公式；
- 同行评议期刊、重要会议或高质量综述优先；
- 题名、作者、年份、来源和DOI/稳定链接可核验；
- 奠基工作不限年份，近期进展覆盖至检索执行日；
- 关键论断尽量回到原始论文；
- 预印本仅补充特别新的进展，并检查正式出版版本。

## 5. 排除标准

- 与光纤传感无关的DAS或SOA缩写结果；
- 只有营销性描述、无稳定元数据的网页；
- 题名、作者、来源或用途无法核验；
- 预印本、会议版和期刊扩展版重复计数；
- 只涉及应用场景，不能支撑技术论证；
- 无法追溯原始证据的二手转述；
- 撤稿、明显可疑或为凑数量保留的弱相关文献。

## 6. 核验要求

- DOI优先去重，题名和作者作为补充；
- 每条记录保存至少一个权威元数据来源；
- 实际引用文献必须阅读摘要或正文相关段落；
- 具体数值、首创性、优缺点和因果判断必须记录证据位置；
- 未核验条目不得进入正式BibTeX库。
