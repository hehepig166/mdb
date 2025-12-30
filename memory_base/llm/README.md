# llm

LLM 抽象层：把不同厂商（OpenAI/Anthropic/本地）统一到同一个接口上，方便：
- 业务逻辑（extract/summarize/retrieve）不绑定具体厂商 SDK
- 统一做重试、限流、超时、日志、成本统计（后续可加）

当前对外接口刻意保持极简，只提供两种能力：
- **单次调用**：`llm.respond(message) -> response`
- **持续对话**：`session = llm.start_chat(...); session.send(message) -> response`

增量建议：
1) 先实现 `MockLLM` 用于本地测试  
2) 再补一个真实 provider（OpenAI 或 Anthropic 任选其一）  
3) 逐步把 enrich/summarization 迁移到这个抽象层


