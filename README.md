# memory-base

这个目录用于实现 **EMB（Experience Memory Base）经验数据库系统**。

## 文档
- 入口索引：`doc/experience_memory_system_design.md`
- 形式化规格（任务/输入/输出）：`doc/experience_memory_system_spec.md`
- 技术方案细节（实现）：`doc/experience_memory_system_tech.md`

## 推荐代码结构（增量化开发友好）
代码建议放在 `memory_base/` 这个 Python 包中。为了好维护、好增量开发，建议先把结构收敛成“能跑的最小集合”，其它模块等需要时再加。

## 当前代码结构（已落地，尽量精简）
```
memory-base/
  memory_base/
    __init__.py

    adapters/                  # 来源适配：raw -> NEI（规范化输入）
      base.py
      manual.py

    graph/                     # 分层图 + “相似度度量 -> 建边”抽象
      types.py
      metrics.py
      edge_builders.py

  doc/
```

## 可选模块（需要时再引入）
- `llm/`：把各家 LLM API 统一封装到同一个接口下（本仓库已放了 scaffold）
- `indexing/`：embedding/向量索引（FAISS 等）用于候选生成与性能加速（本仓库已放了 scaffold）

## 增量开发顺序（建议）
1. **MVP（最简单）**：先把图模型与“相似度度量->建边”跑通（当前已具备）
2. **可选加速**：需要更强语义/性能时再用 `indexing`（embedding/FAISS）
3. **LLM 重活**：需要抽取/总结时再用 `llm/`


