# adapters

来源适配层：把任意来源的原始输入 `raw` 转成统一的 **NEI（NormalizedExperienceInput）**。

## 设计原则
- **只做规范化**：`raw -> NEI`，其中 NEI 以 `situation/goal/attempt/result/reflection/label` 为核心，同时保留 `source_type/source_ref`（可追溯）
- **保持“薄”**：默认不在 adapter 里做 embedding/聚类；LLM 抽取属于可选策略（当 raw 本身不结构化时很有用）
- **可追溯**：`source_ref` 必填，且应能回放/定位到原始来源

## 派生/分类建议（不要过度约束，但要有惯例）
建议优先按 **来源/输入形态（source_type / raw shape）** 来拆 adapter：
- `commit_*`：commit message/diff/log -> NEI
- `lean_*`：Lean 编译/证明日志 -> NEI
- `text_*`：自由文本描述 -> NEI（通常会用 LLM）

而“处理方式”（规则/LLM/混合）作为 adapter 内部实现细节即可，不必单独作为模块分类的第一维度。

## 如何新增一个来源
1. 新建一个文件（例如 `lean.py`）
2. 实现 `Adapter.ingest(raw) -> NormalizedExperienceInput`
3. 在 `__init__.py` 里导出（可选）

## 已有实现
- `ManualAdapter`（`manual.py`）：用于手工/调试输入，先跑通全链路


