# graph

分层图（Layered DAG）层：把 L1/L2/L3 与它们的关系物化为图结构，支持：
- `member_of`：L1 属于某个 view 的 L2 cluster
- `supports`：L2 支撑 L3（证据链）
- `about`：绑定 Artifact（lemma/file/error type/concept）
- `contradicts/refines`：冲突与细化关系

增量化建议：
- MVP 可用“边表（edge table）”模拟图：`(src_id, dst_id, edge_type, weight, meta)`。
- 稳定后再接图数据库实现 `GraphStore`。

## 统一抽象：基于相似度度量生成边
建议把“边从何而来”统一抽象为：
- 选择一个相似度度量 `sim(u, v)`（embedding cosine / 共享 artifact / 结构相似等）
- 选择一个建边策略（阈值 / top-k / 聚类转边）

也就是说：embedding/聚类只是其中一种度量/策略组合，不影响上层 BFS 检索与证据链回溯。


