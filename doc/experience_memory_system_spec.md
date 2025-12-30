# 通用经验数据库（EMB）形式化规格（Spec）

## 1. 系统目的（Goal）
构建一个通用系统，用于持续沉淀并利用“做事经验”：
- **正向记忆**：成功经验，用于强化可复用策略/技能。
- **反向记忆**：失败经验，用于缩小探索空间、规避失败模式。

本规格仅描述：**任务定义、系统输入、系统输出、可追溯与可解释约束**。实现细节见技术方案文档。

## 2. 核心对象（Data Objects）

### 2.1 L1 经验事件（L1Event）
L1 是最底层、可追溯的经验事实记录。形式化为：
\[
e = \langle s, g, a, r, \rho \rangle
\]
- \(s\)（situation）：情景（上下文与约束）
- \(g\)（goal）：目的/意图（想达成什么）
- \(a\)（attempt）：尝试/行动（做了什么）
- \(r\)（result）：结果（是否推进/是否达成/质量指标/失败原因）
- \(\rho\)（reflection）：反思（为什么会这样、下次怎么做）

结果标签：
- \(label(e) \in \{success, failure, unknown\}\)

必备约束：
- **可追溯**：每个 L1Event 必须包含可回放的来源引用 `source_ref`。

### 2.2 Episode（可选，推荐）
长程任务通常包含多次尝试与中间状态，建议用 Episode 组织：
\[
Episode = \langle goal, context, (e_1, e_2, \dots, e_T) \rangle
\]

### 2.3 L2 共性经验（L2Pattern）
L2 是由多个 L1 聚合形成的模式（pattern），用于复用与提醒：
- 可区分 success pattern 与 failure pattern。
- 必须可回溯到其支撑的 L1 集合（证据链）。

### 2.4 L3 抽象经验（L3Principle）
L3 是从 L2 进一步抽象出的策略/原则（policy-like knowledge）：
- 描述适用条件、推荐行动、代价/风险。
- 必须可回溯到其支撑的 L2（进而到 L1）。

## 3. 系统输入（Input Contract）

### 3.1 规范化输入对象（Normalized Experience Input, NEI）
任何经验来源在进入系统前，需被适配为 NEI。这里我们把 NEI 定义为“**来源无关的经验事件候选**”，其核心字段与 L1Event 对齐：
- `situation`：情景
- `goal`：目标
- `attempt`：尝试（建议必填）
- `result`：结果描述（可为空）
- `reflection`：反思（可为空）
- `label`：`success | failure | unknown`

同时 NEI 必须携带来源信息以保证可追溯：
- `source_type`：`lean | math_proof | chat | log | manual | ...`
- `source_ref`：可追溯引用（文件路径、会话 id、实验 id 等，**必填**）

可选保留原始载荷与观测信号（便于回放/再抽取/再判定）：
- `payload`：原始载荷（建议保留）
- `observations`：可观测信号（proof state、编译结果、时间成本、质量指标等）
- `hints`：人为提示（关键 artifact、约束、是否明确失败等）

### 3.2 摄入输出的最小约束（MVP）
摄入后至少产出一个候选或确定的 L1Event，满足：
- `attempt` 必须存在
- `source_ref` 必须存在
- `result.label` 至少为 `unknown`
- `situation/goal/reflection` 允许为空但建议补全

## 4. 系统任务（Tasks）与形式化 I/O

### 4.1 摄入（Ingestion）
输入：NEI \(x\)  
输出：一组 L1Event 与元信息：
\[
Ingest(x) \rightarrow \{(e_i, meta_i)\}_{i=1}^n
\]
其中 `meta` 包含来源追溯信息、置信度与判定信号等。

### 4.2 聚合（Aggregation: L1 → L2）
输入：L1 事件集合 \(\mathcal{E}_{L1}\)  
输出：L2Pattern 集合与映射（证据链）：
\[
Aggregate(\mathcal{E}_{L1}) \rightarrow (\mathcal{P}_{L2}, M_{1\to2})
\]

### 4.3 抽象（Abstraction: L2 → L3）
输入：L2Pattern 集合 \(\mathcal{P}_{L2}\)  
输出：L3Principle 集合与映射：
\[
Abstract(\mathcal{P}_{L2}) \rightarrow (\mathcal{K}_{L3}, M_{2\to3})
\]

### 4.4 查询（Retrieval & Synthesis）
输入：查询对象：
\[
q = \langle situation, goal, constraints, preferences \rangle
\]
输出：结构化回答 `ans`，至少包含：
- `l1_evidence[]`：相关 L1 证据（必须可追溯）
- `l2_patterns[]`：相关 L2 模式（可选）
- `l3_principles[]`：相关 L3 原则（可选）
- `recommended_attempts[]`：可操作建议（可选）
\[
Query(q) \rightarrow ans
\]

### 4.5 反馈（Feedback）
输入：用户反馈 \(fb\)（useful/incorrect/label override/merge-split 等）  
输出：对对象权重、标签、关联的更新：
\[
Feedback(fb) \rightarrow \Delta(\mathcal{E}_{L1}, \mathcal{P}_{L2}, \mathcal{K}_{L3})
\]

### 4.6 遗忘（Forgetting）
输入：经验库全量 + 时间/使用/反证信号  
输出：降权/归档/删除等变更：
\[
Forget(\cdot) \rightarrow \Delta(w, status)
\]

## 5. 输出的可解释性与一致性约束（Invariants）
- **证据链**：任何 L2/L3 建议必须能回溯到支撑的 L1（或明确标注为 “hypothesis/needs validation”）。
- **可追溯引用**：所有 `l1_evidence` 必须携带 `source_ref`，便于回放。
- **冲突可见**：若存在强反例/冲突经验，输出应提示并给出反例引用。


