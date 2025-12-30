# 通用经验数据库（EMB）技术方案细节（Tech Notes）

## 1. 设计取向
本文件讨论“如何实现”而非“系统是什么”。形式化规格见 `experience_memory_system_spec.md`。

核心目标：
- **来源无关**：写数学证明、写 Lean、长程现实任务、对话日志等均可接入。
- **多级经验**：L1 事实 → L2 模式 → L3 原则，并保持证据链可回溯。
- **可增量演化**：持续摄入、周期聚合、用户反馈、遗忘机制。

## 2. 推荐的整体实现形态：分层图（Layered DAG）
把“聚类/总结结果”物化为图节点与边，天然支持：
- 多视角（goal/situation/attempt/failure_mode…）并行存在
- 同一事件多归属（一个 L1 同时属于多个 L2）
- 证据链与冲突边的可解释输出
- 增量更新（局部更新节点与摘要，而非频繁全量重算）

### 2.1 节点与边（建议）
- **Nodes**
  - `L1Event`
  - `L2Pattern`（cluster node, 带 view 与 cluster_info）
  - `L3Principle`
  - `Artifact`（lemma / file / error type / concept）

- **Edges**
  - `member_of(L1 -> L2)`：成员边（带 membership weight）
  - `supports(L2 -> L3)`：支撑边（带 support weight）
  - `about(* -> Artifact)`：对象关联
  - `contradicts(* <-> *)`：冲突/反例（带证据与强度）
  - `refines(* -> *)`：细化覆盖（更窄条件、更强结论）

### 2.2 统一抽象：用相似度度量建边（Similarity-Metric-Driven Edges）
你提到“总之要抽象成以某个相似度度量为依据建边”——这是一个非常好的统一视角：无论是“embedding 聚类/近邻”、还是“结构化规则相似”，都可以视为在某个空间里定义了一个相似度函数，然后用它来生成图边。

形式化：
- 对任意两个节点 \(u, v\)，定义相似度度量 \(sim(u, v)\in\mathbb{R}\)（通常归一到 \([0,1]\) 或 \([-1,1]\)）。
- 建边策略（常用两种）：
  - **阈值建边**：若 \(sim(u, v)\ge \tau\)，则添加边 \(u\leftrightarrow v\)
  - **Top‑K 建边**：对每个节点 \(u\)，连接其相似度最高的 \(k\) 个邻居

重要的是：**“聚类”只是建边策略的一种**（例如同簇内全连接/与簇中心连边），底层仍然依赖某个 \(sim(\cdot,\cdot)\) 或距离度量。

在工程实现上建议把边的生成拆成两个可替换部件：
- **SimilarityMetric**：负责计算 \(sim(u,v)\)（embedding cosine、Jaccard、编辑距离、共享 artifact 等）
- **EdgeBuilder**：负责把相似度变成边（阈值/Top‑K/聚类‑to‑edges）

这样你可以随时替换/叠加度量，而不需要重写 BFS/检索逻辑。

## 3. L1 结构化与信号提取（Adapter Strategy）
建议采用“规则 + LLM”的混合结构化：
- **强结构**：可从日志/状态机/编辑记录直接抽取（例如 Lean 的错误栈、proof state 摘要、耗时）
- **弱结构**：goal/situation/reflection 常来自文本，需要 LLM 抽取，但应标注 `human/machine` 来源

### 3.1 Lean adapter（示例）
可观测信号（observations）建议包括：
- build/compile pass-fail + error
- goal 数、未解决目标复杂度 proxy（例如目标表达式长度）
- tactic/lemma 使用序列（可用于 attempt embedding）
- time/memory

典型 failure pattern 可聚类的维度：
- “改动引入新 subgoal 爆炸”
- “simp 重写方向错误导致循环/无效”
- “依赖 lemma 缺失/命名空间引用错误”

### 3.2 数学证明 adapter（示例）
建议将 attempt 表示为“证明策略 token 序列”（例如 induction/contradiction/construction/case split/normalization…），再结合自然语言摘要。

## 4. 多视角 embedding 与聚类（L1→L2）
你提出的按字段分别 embedding 并聚类，是实践上很有效的路线。

### 4.1 多视角集合（推荐）
- `E_s`：situation embedding
- `E_g`：goal embedding
- `E_a`：attempt embedding
- `E_r`：result 信号（更多结构化，embedding 可选）
- `E_ρ`：reflection embedding

### 4.2 聚类策略（可组合）
- **单视角聚类**：得到 view-specific patterns（更清晰）
- **多视角交叉**：例如 situation 簇 ∩ attempt 簇，用于高精度模式
- **失败优先**：对 failure/unknown 单独建簇，优先抽取 failure modes（缩小探索空间）

### 4.3 L2 总结（LLM Summarization）
建议输出固定字段（便于检索与排序）：
- `summary`：共性描述
- `signature`：适用条件/关键特征槽位
- `recommendation`：建议做法/避免做法
- `counterexamples`：已知反例（若有）

## 5. L2→L3 抽象（Pattern→Principle）
建议用模板驱动抽象，避免“空泛”：
- **If**（适用信号/条件）**then**（行动）**because**（证据链）**watch out**（反例/代价）

L3 的更新频率建议低于 L2：强调稳定、少打脸、强证据链。

## 6. 查询与排序（多级检索 + 证据输出）
推荐检索 pipeline：
- 先检索 L1（向量+关键词+结构槽位）得到证据候选
- 通过图边向上找对应 L2/L3，再向下补充最能解释的 L1
- 组织输出：优先“可追溯证据”，再给模式与原则

### 6.0 最简单可用实现：图上限定深度/广度 BFS（推荐先做）
如果你的目标是“能查到 L1/L2/L3 相关记录”，可以先不引入 embedding/向量库，直接把经验库维护成一个分层图，然后做 BFS：

- **节点层级**：L1 / L2 / L3
- **边类型**（你提的简化版很合理）：
  - **跨层边（inter-layer）**：L1↔L2、L2↔L3（member/support）
  - **层内边（intra-layer）**：L1↔L1、L2↔L2、L3↔L3（similar/contradict/refine/related）

检索做法（示意）：
- 先根据关键词/结构槽位（artifact/label/source_type/time window）选出起始节点集合（seed）
- 在图上做 **限定深度/限定宽度的 BFS** 扩展邻居
- 输出时按“是否同层/是否跨层、边权重、时间/反馈权重”等做一个简单排序

这样 MVP 复杂度最低、可解释性最好；等 BFS 命中率/语义能力不够再引入 embedding。

### 6.1 是否可以用 embedding 做索引？（可以，且推荐）
可以把“索引”理解为：为不同检索意图选择不同的向量空间与召回策略。EMB 建议做**多字段/多视角 embedding 索引**，并与关键词/结构槽位检索混合：

- **L1 的 embedding 索引（证据层）**：
  - `situation` 向量索引：适合“我现在卡在什么状态/错误”
  - `goal` 向量索引：适合“我想达成什么”
  - `attempt` 向量索引：适合“我打算怎么做/有没有类似策略”
  - `reflection` 向量索引：适合“失败模式/经验教训”

- **L2/L3 的 embedding 索引（模式/原则层）**：
  - `L2.summary + signature` 向量索引：快速命中共性模式（成功/失败模式）
  - `L3.principle + when_applicable` 向量索引：快速命中高层策略（再用证据链回溯到 L1）

- **混合检索（强烈建议）**：
  - embedding 对自然语言相似性很强，但对专有名词/符号/路径/lemma 名称可能不稳
  - 因此建议同时做关键词/结构槽位过滤：`Artifact`（lemma/file/error type）、标签（success/failure/unknown）、时间窗、来源类型等

- **证据链约束（避免“命中但不可用”）**：
  - 允许先命中 L2/L3（模式/原则），但输出时必须回溯到支撑的 L1（带 `source_ref`）作为证据
  - 若无法回溯，需标注为 hypothesis/needs validation

排序信号建议：
- 相似度（主视角匹配度）
- `confidence/usefulness` 权重（受反馈影响）
- 新鲜度（时间衰减）
- 反证惩罚（被强反例打脸则降权）

## 7. 反馈闭环（Online Learning Lite）
反馈类型：
- useful / not useful
- correct / incorrect（纠错）
- label override（success/failure/unknown）
- merge/split（对 L2 簇结构反馈）

落地策略：
- 以“权重更新”为主（避免频繁结构大改）
- 结构性反馈（merge/split）延迟到离线重聚类处理

## 8. 遗忘机制（Forgetting）
建议优先“降权与归档”而非硬删除，以保留可追溯性：
- 时间衰减
- 低使用淘汰
- 反证惩罚
- 来源可信度（human > machine）

## 9. 存储建议（逻辑，不绑定具体产品）
常见组合：
- **对象存储/关系库**：存 L1/L2/L3 的结构化字段与来源引用
- **向量索引**：按多视角字段索引（situation/goal/attempt/reflection）
- **图存储（可选）**：存 member_of/supports/about/contradicts/refines 等边

MVP 可先用“关系库 + 向量索引”，图关系先以表/边表模拟；稳定后再引入图数据库。


