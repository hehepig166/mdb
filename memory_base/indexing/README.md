# indexing

索引层：embedding 与混合检索。

增量化建议：
- **更简单的 MVP（推荐优先）**：先不做向量索引，直接用“图 + BFS”在 L1/L2/L3 上做遍历检索（配合少量关键词过滤）。
- **需要加速/泛化时再上**：做 `VectorStore` interface + 本地实现（例如内存/FAISS/SQLite 向量扩展）。
- 同时维护关键词/结构槽位过滤（artifact、source_type、label、时间窗）。
- 支持“多字段/多视角索引”：`situation/goal/attempt/reflection` 分开建索引。

备注：从更抽象的角度看，embedding 向量检索只是“相似度度量的一种实现”（例如 cosine 相似度），用于自动生成“相似边”或用于召回候选节点。


