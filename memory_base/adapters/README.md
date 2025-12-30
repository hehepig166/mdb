# adapters

来源适配层：把任意来源的原始输入 `raw` 转成统一的 **NEI（NormalizedExperienceInput）**。

## 设计原则
- **只做规范化**：`raw -> NEI`（把来源差异收口到 `source_type/source_ref/payload/observations/hints`）
- **保持“薄”**：默认不在 adapter 里做 embedding/聚类/LLM 抽取（除非你明确要 source-specific 的抽取）
- **可追溯**：务必把可回放的引用放进 `source_ref`

## 如何新增一个来源
1. 新建一个文件（例如 `lean.py`）
2. 实现 `Adapter.ingest(raw) -> NormalizedExperienceInput`
3. 在 `__init__.py` 里导出（可选）

## 已有实现
- `ManualAdapter`（`manual.py`）：用于手工/调试输入，先跑通全链路


